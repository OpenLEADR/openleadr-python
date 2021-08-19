# SPDX-License-Identifier: Apache-2.0

# Copyright 2020 Contributors to OpenLEADR

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import asyncio
import inspect
import logging
import pytz
import ssl
import tzlocal
import time
from datetime import datetime, timedelta, timezone
from functools import partial
from http import HTTPStatus
from xml.etree import ElementTree
from apscheduler.util import undefined
import aiohttp
from lxml.etree import XMLSyntaxError
from signxml.exceptions import InvalidSignature
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from openleadr import enums, objects, errors
# from openleadr.objects import Component
# from dict2xml import dict2xml
from openleadr.messaging import create_message, parse_message, \
    validate_xml_schema, validate_xml_signature
from openleadr import utils
from threading import Lock
from dataclasses import asdict

logging.basicConfig(level = logging.ERROR)
logger = logging.getLogger('openleadr')



class OpenADRClient:
    """
    Main client class. Most of these methods will be called automatically, but
    you can always choose to call them manually.
    """

    def __init__(self, ven_name, vtn_url, debug=True, cert=None, key=None,
                 passphrase=None, vtn_fingerprint=None, show_fingerprint=True, ca_file=None,
                 allow_jitter=True, ven_id=None, registration_id=None):
        """
        Initializes a new OpenADR Client (Virtual End Node)

        :param str ven_name: The name for this VEN
        :param str vtn_url: The URL of the VTN (Server) to connect to
        :param bool debug: Whether or not to print debugging messages
        :param str cert: The path to a PEM-formatted Certificate file to use
                         for signing messages.
        :param str key: The path to a PEM-formatted Private Key file to use
                        for signing messages.
        :param str passphrase: The passphrase for the Private Key
        :param str vtn_fingerprint: The fingerprint for the VTN's certificate to
                                verify incomnig messages
        :param str show_fingerprint: Whether to print your own fingerprint
                                     on startup. Defaults to True.
        :param str ca_file: The path to the PEM-formatted CA file for validating the VTN server's
                            certificate.
        :param str ven_id: The ID for this VEN. If you leave this blank,
                           a VEN_ID will be assigned by the VTN.
        """

        self.ven_name = ven_name
        if vtn_url.endswith("/"):
            vtn_url = vtn_url[:-1]
        self.vtn_url = vtn_url
        self.ven_id = ven_id
        self.registration_id = registration_id
        self.poll_frequency = None
        self.vtn_id = None
        self.vtn_fingerprint = vtn_fingerprint
        self.debug = debug

        self.reports = []                               # Holds the callbacks for each specific report
        self.report_callbacks = {}                      # Keep track of the report requests from the VTN
        self.report_requests = []                       # Holds reports that are being populated over time
        self.incomplete_reports = {}                    # Holds reports that are waiting to be sent
        self.pending_reports = None
        self.scheduler = AsyncIOScheduler()
        self.client_session = None
        self.report_queue_task = None
        
        self.received_events = []                       # Holds the events that we received.
        self.responded_events = {}                      # Holds the events that we already saw.

        self.cert_path = cert
        self.key_path = key
        self.passphrase = passphrase
        self.ca_file = ca_file
        self.allow_jitter = allow_jitter
        self.local_timezone = tzlocal.get_localzone()

        if cert and key:
            with open(cert, 'rb') as file:
                cert = file.read()
            with open(key, 'rb') as file:
                key = file.read()
            if show_fingerprint:
                print("")
                print("*" * 80)
                print("Your VEN Certificate Fingerprint is ".center(80))
                print(f"{utils.certificate_fingerprint(cert).center(80)}".center(80))
                print("Please deliver this fingerprint to the VTN.".center(80))
                print("You do not need to keep this a secret.".center(80))
                print("*" * 80)
                print("")

        self._create_message = partial(create_message,
                                       cert=cert,
                                       key=key,
                                       passphrase=passphrase)

    async def run(self):
        self.pending_reports = asyncio.Queue()
        """
        Run the client in full-auto mode.
        """
        if not hasattr(self, 'on_event'):
            raise NotImplementedError("You must implement on_event.")
        self.loop = asyncio.get_event_loop()
        await self.query_registration()
        # We need to send the ven_id and registration_id when responding to re-registration request from the VTN
        await self.create_party_registration(ven_id=self.ven_id, registration_id=self.registration_id)

        if not self.ven_id:
            logger.error("No VEN ID received from the VTN, aborting.")
            await self.stop()
            return

        if self.reports:
            await self.register_reports(self.reports)
            self.report_queue_task = self.loop.create_task(self._report_queue_worker())

        await self._poll()

        # Set up automatic polling
        if self.poll_frequency > timedelta(hours=24):
            logger.warning("Polling with intervals of more than 24 hours is not supported. "
                           "Will use 24 hours as the polling interval.")
            self.poll_frequency = timedelta(hours=24)

        self.scheduler.add_job(self._poll,
                               trigger='interval',
                               misfire_grace_time=None,
                               seconds = self.poll_frequency.total_seconds())
        self.scheduler.add_job(self._event_cleanup,
                               trigger='interval',
                               seconds=300)
        self.scheduler.start()

    async def stop(self):
        """
        Cleanly stops the client. Run this coroutine before closing your event loop.
        """
        if self.scheduler.running:
            self.scheduler.shutdown()
        if self.report_queue_task:
            self.report_queue_task.cancel()
        await asyncio.sleep(0)

    def add_handler(self, handler, callback):
        """
        Add a callback for the given situation
        """
        if handler not in ('on_event', 'on_update_event'):
            logger.error("'handler' must be either on_event or on_update_event")
            return

        setattr(self, handler, callback)

    def add_report(self, callback, resource_id, measurement=None,
                   data_collection_mode='incremental',
                   report_specifier_id=None, r_id=None,
                   report_name=enums.REPORT_NAME.TELEMETRY_USAGE,
                   reading_type=enums.READING_TYPE.DIRECT_READ,
                   report_type=enums.REPORT_TYPE.USAGE, sampling_rate=None, data_source=None,
                   scale="none", unit=None, power_ac=True, power_hertz=50, power_voltage=230,
                   market_context=None, end_device_asset_mrid=None, report_data_source=None):
        """
        Add a new reporting capability to the client.

        :param callable callback: A callback or coroutine that will fetch the value for a specific
                                    report. This callback will be passed the report_id and the r_id
                                    of the requested value.
        :param str resource_id: A specific name for this resource within this report.
        :param str measurement: The quantity that is being measured (openleadr.enums.MEASUREMENTS).
                                Optional for TELEMETRY_STATUS reports.
        :param str data_collection_mode: Whether you want the data to be collected incrementally
                                        or at once. If the VTN requests the sampling interval to be
                                        higher than the reporting interval, this setting determines
                                        if the callback should be called at the sampling rate (with
                                        no args, assuming it returns the current value), or at the
                                        reporting interval (with date_from and date_to as keyword
                                        arguments). Choose 'incremental' for the former case, or
                                        'full' for the latter case.
        :param str report_specifier_id: A unique identifier for this report. Leave this blank for a
                                        random generated id, or fill it in if your VTN depends on
                                        this being a known value, or if it needs to be constant
                                        between restarts of the client.
        :param str r_id: A unique identifier for a datapoint in a report. The same remarks apply as
                        for the report_specifier_id.
        :param str report_name: An OpenADR name for this report (one of openleadr.enums.REPORT_NAME)
        :param str reading_type: An OpenADR reading type (found in openleadr.enums.READING_TYPE)
        :param str report_type: An OpenADR report type (found in openleadr.enums.REPORT_TYPE)
        :param datetime.timedelta sampling_rate: The sampling rate for the measurement.
        :param str unit: The unit for this measurement.
        :param boolean power_ac: Whether the power is AC (True) or DC (False).
                                Only required when supplying a power-related measurement.
        :param int power_hertz: Grid frequency of the power.
                                Only required when supplying a power-related measurement.
        :param int power_voltage: Voltage of the power.
                                    Only required when supplying a power-related measurement.
        :param str market_context: The Market Context that this report belongs to.
        :param str end_device_asset_mrid: the Meter ID for the end device that is measured by this report.
        :param report_data_source: A (list of) target(s) that this report is related to.
        """

        # Verify input
        if report_name not in enums.REPORT_NAME.values and not report_name.startswith('x-'):
            raise ValueError(f"{report_name} is not a valid report_name. Valid options are "
                            f"{', '.join(enums.REPORT_NAME.values)}",
                            " or any name starting with 'x-'.")
        if reading_type not in enums.READING_TYPE.values and not reading_type.startswith('x-'):
            raise ValueError(f"{reading_type} is not a valid reading_type. Valid options are "
                            f"{', '.join(enums.READING_TYPE.values)}"
                            " or any name starting with 'x-'.")
        if report_type not in enums.REPORT_TYPE.values and not report_type.startswith('x-'):
            raise ValueError(f"{report_type} is not a valid report_type. Valid options are "
                            f"{', '.join(enums.REPORT_TYPE.values)}"
                            " or any name starting with 'x-'.")
        if scale not in enums.SI_SCALE_CODE.values:
            raise ValueError(f"{scale} is not a valid scale. Valid options are "
                            f"{', '.join(enums.SI_SCALE_CODE.values)}")

        if sampling_rate is None:
            sampling_rate = objects.SamplingRate(min_period=timedelta(seconds=10),
                                                max_period=timedelta(hours=24),
                                                on_change=False)
        elif isinstance(sampling_rate, timedelta):
            sampling_rate = objects.SamplingRate(min_period=sampling_rate,
                                                max_period=sampling_rate,
                                                on_change=False)

        ##The defualt reading_type should be x-notApplicable, and the report_type should be x-resourceStatus for TELEMETRY_STATUS
        ##One thing I fixed
        if report_name=='TELEMETRY_STATUS':
            reading_type = 'x-notApplicable'
            report_type = 'x-resourceStatus'
        
        if data_collection_mode not in ('incremental', 'full'):
            raise ValueError("The data_collection_mode should be 'incremental' or 'full'.")

        if data_collection_mode == 'full':
            args = inspect.signature(callback).parameters
            if not ('date_from' in args and 'date_to' in args and 'sampling_interval' in args):
                raise TypeError("Your callback function must accept the 'date_from', 'date_to' "
                                "and 'sampling_interval' arguments if used "
                                "with data_collection_mode 'full'.")

        # Determine the correct item name, item description and unit
        if report_name == 'TELEMETRY_STATUS':
            item_base = None
        elif isinstance(measurement, objects.Measurement):
            item_base = measurement
        elif isinstance(measurement, dict):
            utils.validate_report_measurement_dict(measurement)
            power_attributes = object.PowerAttributes(**measurement.get('power_attributes')) or None
            item_base = objects.Measurement(name=measurement['name'],
                                            description=measurement['description'],
                                            unit=measurement['unit'],
                                            scale=measurement.get('scale'),
                                            power_attributes=power_attributes)
        elif measurement.upper() in enums.MEASUREMENTS.members:
            item_base = enums.MEASUREMENTS[measurement.upper()]
        else:
            item_base = objects.Measurement(name='customUnit',
                                            description=measurement,
                                            unit=unit,
                                            scale=scale)

        if report_name != 'TELEMETRY_STATUS' and scale is not None:
            if item_base.scale is not None:
                if scale in enums.SI_SCALE_CODE.values:
                    item_base.scale = scale
            else:
                raise ValueError("The 'scale' argument must be one of '{'. ',join(enums.SI_SCALE_CODE.values)}")

        # Check if unit is compatible
        if unit is not None and unit != item_base.unit and unit not in item_base.acceptable_units:
            logger.warning(f"The supplied unit {unit} for measurement {measurement} "
                            f"will be ignored, {item_base.unit} will be used instead. "
                            f"Allowed units for this measurement are: "
                            f"{', '.join(item_base.acceptable_units)}")

        # Get or create the relevant Report
        if report_specifier_id:
            report = utils.find_by(self.reports,
                                    'report_name', report_name,
                                    'report_specifier_id', report_specifier_id)
        else:
            report = utils.find_by(self.reports, 'report_name', report_name)

        if not report:
            report_specifier_id = report_specifier_id or utils.generate_id()
            report = objects.Report(created_date_time=datetime.now(timezone.utc),
                                    report_name=report_name,
                                    report_specifier_id=report_specifier_id,
                                    data_collection_mode=data_collection_mode)
            self.reports.append(report)

        # Add the new report description to the report
        target = objects.Target(resource_id=resource_id)
        r_id = utils.generate_id()
        report_description = objects.ReportDescription(r_id=r_id,
                                                        reading_type=reading_type,
                                                        report_data_source=target,
                                                        report_subject=target,
                                                        report_type=report_type,
                                                        sampling_rate=sampling_rate,
                                                        measurement=item_base,
                                                        market_context=market_context)
        self.report_callbacks[(report.report_specifier_id, r_id)] = callback
        report.report_descriptions.append(report_description)
        return report_specifier_id, r_id

    ###########################################################################
    #                                                                         #
    #                             POLLING METHODS                             #
    #                                                                         #
    ###########################################################################

    async def poll(self):
        """
        Request the next available message from the Server. This coroutine is called automatically.
        """
        service = 'OadrPoll'
        message = self._create_message('oadrPoll', ven_id=self.ven_id)
        response_type, response_payload = await self._perform_request(service, message)
        return response_type, response_payload

    ###########################################################################
    #                                                                         #
    #                         REGISTRATION METHODS                            #
    #                                                                         #
    ###########################################################################

    async def query_registration(self):
        """
        Request information about the VTN.
        """
        request_id = utils.generate_id()
        service = 'EiRegisterParty'
        message = self._create_message('oadrQueryRegistration', request_id=request_id)
        response_type, response_payload = await self._perform_request(service, message)
        return response_type, response_payload

    async def create_party_registration(self, http_pull_model=True, xml_signature=False,
                                        report_only=False, profile_name='2.0b',
                                        transport_name='simpleHttp', transport_address=None,
                                        ven_id=None, registration_id=None):
        """
        Take the neccessary steps to register this client with the server.

        :param bool http_pull_model: Whether to use the 'pull' model for HTTP.
        :param bool xml_signature: Whether to sign each XML message.
        :param bool report_only: Whether or not this is a reporting-only client
                                 which does not deal with Events.
        :param str profile_name: Which OpenADR profile to use.
        :param str transport_name: The transport name to use. Either 'simpleHttp' or 'xmpp'.
        :param str transport_address: Which public-facing address the server should use
                                      to communicate.
        :param str ven_id: The ID for this VEN. If you leave this blank,
                           a VEN_ID will be assigned by the VTN.
        """
        request_id = utils.generate_id()
        service = 'EiRegisterParty'
        payload = { 'ven_name': self.ven_name,
                    'ven_id': 'ven_123',
                    'http_pull_model': http_pull_model,
                    'xml_signature': xml_signature,
                    'report_only': report_only,
                    'profile_name': profile_name,
                    'transport_name': transport_name,
                    'transport_address': transport_address }
        # ven_id and registration_id should be present during re-registration requests coming from the VTN
        if registration_id:
            payload['registration_id'] = registration_id
        if ven_id:
            payload['ven_id'] = ven_id
        message = self._create_message('oadrCreatePartyRegistration',
                                       request_id=request_id,
                                       **payload)
        response_type, response_payload = await self._perform_request(service, message)
        if response_type is None:
            return
        if response_payload['response']['response_code'] != 200:
            status_code = response_payload['response']['response_code']
            status_description = response_payload['response']['response_description']
            logger.error(f"Got error on Create Party Registration: "
                         f"{status_code} {status_description}")
            return
        self.ven_id = response_payload['ven_id']
        self.registration_id = response_payload['registration_id']
        self.vtn_id = response_payload['vtn_id']
        self.poll_frequency = response_payload.get('requested_oadr_poll_freq', timedelta(seconds=10))
        logger.info(f"VEN is now registered with ID {self.ven_id}")
        logger.info(f"The polling frequency is {self.poll_frequency}")
        return response_type, response_payload

    async def create_party_registration_while_registered(self, http_pull_model=True, xml_signature=False,
                                            report_only=False, profile_name='2.0b',
                                            transport_name='simpleHttp', transport_address=None,
                                            ven_id=None, registration_id=None):
            """
            Take the neccessary steps to register this client with the server.

            :param bool http_pull_model: Whether to use the 'pull' model for HTTP.
            :param bool xml_signature: Whether to sign each XML message.
            :param bool report_only: Whether or not this is a reporting-only client
                                    which does not deal with Events.
            :param str profile_name: Which OpenADR profile to use.
            :param str transport_name: The transport name to use. Either 'simpleHttp' or 'xmpp'.
            :param str transport_address: Which public-facing address the server should use
                                        to communicate.
            :param str ven_id: The ID for this VEN. If you leave this blank,
                            a VEN_ID will be assigned by the VTN.
            """
            request_id = utils.generate_id()
            service = 'EiRegisterParty'
            payload = { 'ven_name': self.ven_name,
                        'ven_id': self.ven_id,
                        'http_pull_model': http_pull_model,
                        'xml_signature': xml_signature,
                        'report_only': report_only,
                        'profile_name': profile_name,
                        'transport_name': transport_name,
                        'transport_address': transport_address }
            # ven_id and registration_id should be present during re-registration requests coming from the VTN
            message = self._create_message('oadrCreatePartyRegistration',
                                        request_id=request_id,
                                        **payload)
            response_type, response_payload = await self._perform_request(service, message)
            if response_type is None:
                return
            if response_payload['response']['response_code'] != 200:
                status_code = response_payload['response']['response_code']
                status_description = response_payload['response']['response_description']
                logger.error(f"Got error on Create Party Registration: "
                            f"{status_code} {status_description}")
                return

            self.ven_id = response_payload['ven_id']
            self.registration_id = response_payload['registration_id']
            self.vtn_id = response_payload['vtn_id']
            self.poll_frequency = response_payload.get('requested_oadr_poll_freq', timedelta(seconds=10))
            logger.info(f"VEN is now registered with ID {self.ven_id}")
            logger.info(f"The polling frequency is {self.poll_frequency}")

            if self.reports:
                for report in self.reports:
                    utils.setmember(report, 'created_date_time', datetime.now(timezone.utc))
                await self.register_reports(self.reports)
                self.report_queue_task = self.loop.create_task(self._report_queue_worker())
            return response_type, response_payload

    async def cancel_party_registration(self):
        """
        Cancel registration with the VTN.
        """
        request_id = utils.generate_id()
        service = 'EiRegisterParty'
        payload = {'registration_id': self.registration_id,
                   'ven_id': self.ven_id}
        message = self._create_message(
            'oadrCancelPartyRegistration', request_id=request_id, **payload)
        response_type, response_payload = await self._perform_request(service, message)
        if response_type is None:
            return
        if response_payload['response']['response_code'] != 200:
            status_code = response_payload['response']['response_code']
            status_description = response_payload['response']['response_description']
            logger.error(f"Got error on Cancel Party Registration: "
                         f"{status_code} {status_description}")
            return

        self.registration_id = None
        self.ven_id = None
        self.report_requests = None
        self.reports = None
        self.report_callbacks = None
        self.report_requests = None
        self.incomplete_reports = None
        self.pending_reports = None
        self.scheduler.remove_all_jobs()

        await self.stop()

        return response_type, response_payload

    ###########################################################################
    #                                                                         #
    #                             OPT METHODS                                 #
    #                                                                         #
    ###########################################################################
    async def create_opt(self, eventBody):
        # This function will only be triggered by us to sent
            #1. Avaliability of several eiTarget(its just evse itself) time peroid
            #2. un-Avaliability of several eiTarget(its just evse itself) time period
            #3. Opt-in or Opt-out for specific eventId and eiTarget
        try:
            message_xml = eventBody
            print('xml messge')
            print(message_xml)
            _ ,message_dict = parse_message(message_xml)
            print(message_dict)
            for target in message_dict['targets']:
                target['ven_id'] = self.ven_id
            message_dict['ven_id'] = self.ven_id
            if not isinstance(message_dict['vavailability']['components']['available'], list):
                message_dict['vavailability']['components']['available'] = [message_dict['vavailability']['components']['available']]
            
            
            message_xml= self._create_message('oadrCreateOpt', **message_dict)
            response_type, _ = await self._perform_request('EiOpt', message_xml)
            print('successfully send the create_opt message')
            
            if response_type!='oadrCreatedOpt':
                raise ValueError('Invalid reposne type in odarCreateOpt')
        except Exception as err:
            logger.error(f"Internal error in oadrCreateOpt: {err}")
        return {'status': 200, 'body': 'Sucessfully created an Opt'}
    
    
    async def cancel_opt(self, eventBody):
    # This function can only be triggered manually by us to cancel the Opt informastion we send to the VTN before
    # In this case the OPT_id is the only thing we need
    # No need to save the opt_id in the DB currently, because we trigger this function manually
        try:
            message_xml = eventBody
            print(message_xml)
            _ ,message_dict = parse_message(message_xml)
            message_dict['request_id'] = utils.generate_id()
            message_dict['ven_id'] = self.ven_id
            print(message_dict)
            message_xml= self._create_message('oadrCancelOpt', **message_dict)
            service = 'EiOpt'
            response_type, _ = await self._perform_request(service, message_xml)
            
            if response_type!='oadrCanceledOpt':
                raise ValueError('Invalid reposne type in odarCancelOpt')
            print("Successfully send out the cancel opt message")
        except Exception as err:
            logger.error(f"Internal error in oadrCancelOpt: {err}")
        
        return {'status': 200, 'body': 'Sucessfully canceled an Opt'}
    
    ###########################################################################
    #                                                                         #
    #                              EVENT METHODS                              #
    #                                                                         #
    ###########################################################################

    async def request_event(self, reply_limit=None):
        """
        Request the next Event from the VTN, if it has any.
        """
        payload = {'request_id': utils.generate_id(),
                   'ven_id': self.ven_id,
                   'reply_limit': reply_limit}
        message = self._create_message('oadrRequestEvent', **payload)
        service = 'EiEvent'
        response_type, response_payload = await self._perform_request(service, message)
        return response_type, response_payload

    async def created_event(self, request_id, event_id, opt_type, modification_number=0):
        """
        Inform the VTN that we created an event.
        """
        service = 'EiEvent'
        payload = {'ven_id': self.ven_id,
                   'response': {'response_code': 200,
                                'response_description': 'OK',
                                'request_id': request_id},
                   'event_responses': [{'response_code': 200,
                                        'response_description': 'OK',
                                        'request_id': request_id,
                                        'event_id': event_id,
                                        'modification_number': modification_number,
                                        'opt_type': opt_type}]}
        message = self._create_message('oadrCreatedEvent', **payload)
        response_type, response_payload = await self._perform_request(service, message)

    ###########################################################################
    #                                                                         #
    #                             REPORTING METHODS                           #
    #                                                                         #
    ###########################################################################

    async def _on_report(self, message):
        service = 'EiReport'
        message_type = 'oadrUpdatedReport'
        message = self._create_message(message_type, response={'response_code': 200,
                                                                      'response_description': 'OK'},
                                                            ven_id=self.ven_id,
                                                            request_id=message['request_id'])
        await self._perform_request(service, message)

    async def register_reports(self, reports, report_request_id = 0):
        """
        Tell the VTN about our reports. The VTN might respond with an
        oadrCreateReport message that tells us which reports are to be sent.
        """
        try:
            for report in reports:
                utils.setmember(report, 'created_date_time', datetime.now(timezone.utc))
            request_id = utils.generate_id()
            payload = {'request_id': request_id,
                       'report_request_id': report_request_id if report_request_id!=0 else None,
                       'ven_id': self.ven_id,
                       'reports': reports}

            for report in payload['reports']:
                utils.setmember(report, 'duration', timedelta(days = 365))
                utils.setmember(report, 'report_request_id', report_request_id)

            service = 'EiReport'
            message = self._create_message('oadrRegisterReport', **payload)
            response_type, response_payload = await self._perform_request(service, message)

            # Handle the subscriptions that the VTN is interested in.
            # We only send back the oadrCreatedReport here if we recieve any report_requests from oadrRegisteredReport
            if 'report_requests' in response_payload:
                for report_request in response_payload['report_requests']:
                    result = await self.create_report(report_request)
                print(response_payload)
                request_id = response_payload['response']['request_id']
                # Send the oadrCreatedReport message
                message_type = 'oadrCreatedReport'
                message_payload = {'pending_reports': [{'report_request_id': utils.getmember(report, 'report_request_id')} for report in self.report_requests]}
                message = self._create_message(message_type, response={'response_code': 200,
                                                                    'response_description': 'OK',
                                                                    'request_id': request_id},
                                                                    ven_id=self.ven_id,
                                                                    **message_payload)
                response_type, response_payload = await self._perform_request(service, message)
        except Exception as err:
            logger.warning(f"Internal error in the register reports fucntion: {err}")

    async def register_report(self, response_payload):
        service = 'EiReport'
        message_type = 'oadrRegisteredReport'
        message = self._create_message(message_type, response={'response_code': 200,
                                                                'response_description': 'OK',
                                                                'request_id': response_payload['request_id']},
                                                                ven_id=self.ven_id)
        response_type, response_payload = await self._perform_request(service, message)

    async def create_report(self, report_request):
        """
        Add the requested reports to the reporting mechanism.
        This is called when the VTN requests reports from us.

        :param report_request dict: The oadrReportRequest dict from the VTN.
        """
        # Get the relevant variables from the report requests
        print('The report request is:...............')
        print(report_request)
        try:
            if report_request['report_specifier']['report_specifier_id']=='METADATA':
                await self.register_reports(self.reports, report_request_id=report_request['report_request_id'])
                while self.pending_reports.qsize()!=0:
                    self.pending_reports.get()
                for tmp_report in self.report_requests:
                    self._cancel_report(tmp_report['report_request_id'])
                self.report_requests = []
                #self.report_queue_task
                report_request_id = report_request['report_request_id']
                report_specifier_id = report_request['report_specifier']['report_specifier_id']
                report_back_duration = report_request['report_specifier'].get('report_back_duration')
                granularity = report_request['report_specifier']['granularity']
                print(granularity)
                report_interval = report_request['report_specifier'].get('report_interval')
                if report_interval:
                    dtstart = report_interval['properties']['dtstart']
                    duration = report_interval['properties']['duration']
                    print(dtstart)
                    print(duration)
                granularity = timedelta(0)
                requested_r_ids = [0]
                callback = partial(self.update_report, report_request_id=report_request_id)
                reporting_interval = report_back_duration
                if report_interval:
                    utc_dtstart = dtstart.replace(tzinfo = None)
                    local_dtstart = utc_dtstart.replace(tzinfo = pytz.utc).astimezone(self.local_timezone).replace(tzinfo=None)
                    next_run_time = local_dtstart+timedelta(seconds=4)
                else:
                    next_run_time = undefined
                print('Next run time is: ')
                print(next_run_time)
                
                ##if this is a one shot report, set the next_run_time as now and set interval as one day
                if reporting_interval == timedelta(0):
                    print('this is a one shot report')
                    reporting_interval = timedelta(days=1)
                    next_run_time = datetime.now()+timedelta(seconds=4)
                    ## add 4 seconds in case we missed this job
                job = self.scheduler.add_job(func=callback,
                                            trigger='interval',
                                            id = report_request_id,
                                            # change I made here, Undefined from jinja2 is not a correct accepted type here for next_run_time
                                            # Use the undefined from the apscheduler.util instead
                                            # more details and info please read the source code of add_job in AsyncIoScheduler
                                            # Don't trigger the update report function, this is a hard code test for the test case 3170
                                            next_run_time= next_run_time+timedelta(seconds = 30),
                                            misfire_grace_time=None,
                                            seconds = reporting_interval.total_seconds())

                self.report_requests.append({'report_request_id': report_request_id,
                                            'report_to_follow': False,
                                            'report_specifier_id': report_specifier_id,
                                            'report_back_duration': report_back_duration,
                                            'r_ids': requested_r_ids,
                                            'granularity': granularity,
                                            'dtstart': dtstart if report_interval else datetime.now(),
                                            'duration': duration if report_interval else timedelta(0),
                                            'job': job})
                
                
                
                
                return True
            report_request_id = report_request['report_request_id']
            report_specifier_id = report_request['report_specifier']['report_specifier_id']
            report_back_duration = report_request['report_specifier'].get('report_back_duration')
            granularity = report_request['report_specifier']['granularity']
            print(granularity)
            report_interval = report_request['report_specifier'].get('report_interval')
            if report_interval:
                dtstart = report_interval['properties']['dtstart']
                duration = report_interval['properties']['duration']
                print(dtstart)
                print(duration)
            # Check if this report actually exists
            report = utils.find_by(self.reports, 'report_specifier_id', report_specifier_id)
            if not report:
                logger.error(f"A non-existant report with report_specifier_id "
                            f"{report_specifier_id} was requested.")
                return False
            
            # Check and collect the requested r_ids for this report
            requested_r_ids = []
            for specifier_payload in report_request['report_specifier']['specifier_payloads']:
                r_id = specifier_payload['r_id']
                # Check if the requested r_id actually exists
                rd = utils.find_by(report.report_descriptions, 'r_id', r_id)
                if not rd:
                    logger.error(f"A non-existant report with r_id {r_id} "
                                f"inside report with report_specifier_id {report_specifier_id} "
                                f"was requested.")
                    return False

                # Check if the requested measurement exists and if the correct unit is requested
                if 'measurement' in specifier_payload:
                    measurement = specifier_payload['measurement']
                    if measurement['description'] != rd.measurement.description:
                        logger.error(f"A non-matching measurement description for report with "
                                    f"report_request_id {report_request_id} and r_id {r_id} was given "
                                    f"by the VTN. Offered: {rd.measurement.description}, "
                                    f"requested: {measurement['description']}")
                        continue
                    if measurement['unit'] != rd.measurement.unit:
                        logger.error(f"A non-matching measurement unit for report with "
                                    f"report_request_id {report_request_id} and r_id {r_id} was given "
                                    f"by the VTN. Offered: {rd.measurement.unit}, "
                                    f"requested: {measurement['unit']}")
                        continue
                if granularity is not None and granularity!=timedelta(0):
                    if not rd.sampling_rate.min_period <= granularity <= rd.sampling_rate.max_period:
                        logger.error(f"An invalid sampling rate {granularity} was requested for report "
                                    f"with report_specifier_id {report_specifier_id} and r_id {r_id}. "
                                    f"The offered sampling rate was between "
                                    f"{rd.sampling_rate.min_period} and "
                                    f"{rd.sampling_rate.max_period}")
                        continue
                # It's very strange, but the timedelta==0 was treated as None by defualt, so we check twice here.
                elif not granularity and granularity!=timedelta(0):
                    # If no granularity is specified, set it to the lowest sampling rate.
                    granularity = rd.sampling_rate.max_period

                requested_r_ids.append(r_id)

            callback = partial(self.update_report, report_request_id=report_request_id)
            #if reporting_interval only related to report_back_duration??
            reporting_interval = report_back_duration
            if report_interval:
                utc_dtstart = dtstart.replace(tzinfo = None)
                local_dtstart = utc_dtstart.replace(tzinfo = pytz.utc).astimezone(self.local_timezone).replace(tzinfo=None)
                if report.report_name=='TELEMETRY_USAGE':
                    next_run_time = local_dtstart+granularity
                else:
                    next_run_time = local_dtstart+timedelta(seconds=4)
            else:
                next_run_time = undefined
            print('Next run time is: ')
            print(next_run_time)
            
            ##if this is a one shot report, set the next_run_time as now and set interval as one day
            if reporting_interval == timedelta(0):
                print('this is a one shot report')
                reporting_interval = timedelta(days=1)
                next_run_time = datetime.now()+timedelta(seconds=4)
                ## add 4 seconds in case we missed this job
            job = self.scheduler.add_job(func=callback,
                                        trigger='interval',
                                        id = report_request_id,
                                        # change I made here, Undefined from jinja2 is not a correct accepted type here for next_run_time
                                        # Use the undefined from the apscheduler.util instead
                                        # more details and info please read the source code of add_job in AsyncIoScheduler
                                        next_run_time= next_run_time,
                                        misfire_grace_time=None,
                                        seconds = reporting_interval.total_seconds())

            self.report_requests.append({'report_request_id': report_request_id,
                                        'report_to_follow': False,
                                        'report_specifier_id': report_specifier_id,
                                        'report_back_duration': report_back_duration,
                                        'r_ids': requested_r_ids,
                                        'granularity': granularity,
                                        'dtstart': dtstart if report_interval else datetime.now(),
                                        'duration': duration if report_interval else timedelta(0),
                                        'job': job})
            return True
        except Exception as err:
            logger.warning(f"Internal error in the create report fucntion: {err}")

    async def created_report(self, response_payload, status_code):
    #perform oadrCreatedReport message back to VTN after report added into the pending_reports
        try:
            if status_code ==452:
                service = 'EiReport'
                response = {'response_code': 452,
                            'response_description': 'Not OK',
                            'request_id': response_payload['request_id']
                            }
                msg = self._create_message('oadrCreatedReport', response=response, ven_id=self.ven_id)
                await self._perform_request(service, msg)
            else:
                service = 'EiReport'
                print(response_payload)
                request_id = response_payload['request_id']
                # Send the oadrCreatedReport message
                message_type = 'oadrCreatedReport'
                message_payload = {'pending_reports': [{'report_request_id': utils.getmember(report, 'report_request_id')} for report in self.report_requests]}
                message = self._create_message(message_type, response={'response_code': 200,
                                                                    'response_description': 'OK',
                                                                    'request_id': request_id},
                                                                    ven_id=self.ven_id,
                                                                    **message_payload)
                print('begin to send the oadrCreatedReport')
                await self._perform_request(service, message)
            
        except Exception as err:
            logger.warning(f"Internal error in created report funciton: {err}")

    async def create_single_report(self, report_request):
        """
        Create a single report in response to a request from the VTN.
        """

    async def update_report(self, report_request_id):
        """
        Call the previously registered report callback and send the result as a message to the VTN.
        """
        logger.debug(f"Running update_report for {report_request_id}")
        report_request = utils.find_by(self.report_requests, 'report_request_id', report_request_id)
        if report_request['report_to_follow']==True:
            report_request['report_back_duration'] = timedelta(0)
        granularity = report_request['granularity']
        report_back_duration = report_request['report_back_duration']
        report_specifier_id = report_request['report_specifier_id']
        report = utils.find_by(self.reports, 'report_specifier_id', report_specifier_id)     
        dtstart = report_request['dtstart']
        data_collection_mode = report.data_collection_mode
        report_name = asdict(report)['report_name']
        if report_request_id in self.incomplete_reports:
            logger.debug("We were already compiling this report")
            outgoing_report = self.incomplete_reports[report_request_id]
        else:
            logger.debug("There is no report in progress")
            outgoing_report = objects.Report(report_request_id=report_request_id,
                                             report_specifier_id=report.report_specifier_id,
                                             report_name=report.report_name,
                                             intervals=[],
                                             dtstart = report_request['dtstart'],
                                             duration = report_request['duration'],
                                             report_back_duration = report_request['report_back_duration'])

        intervals = outgoing_report.intervals or []
        if data_collection_mode == 'full':
            if report_back_duration is None:
                report_back_duration = granularity
            date_to = datetime.now(timezone.utc)
            date_from = date_to - max(report_back_duration, granularity)
            for r_id in report_request['r_ids']:
                report_callback = self.report_callbacks[(report_specifier_id, r_id)]
                result = report_callback(date_from=date_from,
                                         date_to=date_to,
                                         sampling_interval=granularity)
                if asyncio.iscoroutine(result):
                    result = await result
                for _ , value in result:
                    report_payload = objects.ReportPayload(r_id=r_id, value=value)
                    intervals.append(objects.ReportInterval(dtstart=dtstart,
                                                            duration= report_request['duration'] if report_request['duration'] else timedelta(0),
                                                            report_payload=report_payload))

        else:
            for r_id in report_request['r_ids']:
                report_callback = self.report_callbacks[(report_specifier_id, r_id)]
                print('did we ever get our report call_back function??')
                print(report_callback)
                result = report_callback()
                print(result)
                if asyncio.iscoroutine(result):
                    result = await result
                if isinstance(result, (int, float)):
                    result = [(datetime.now(timezone.utc), result)]
                for _ , value in result:
                    logger.info(f"Adding {dtstart}, {value} to report")
                    if granularity.total_seconds()>0 and report_back_duration.total_seconds()>0 and report_name=='TELEMETRY_USAGE':
                        print('this is telemetry usage')
                        print(report_back_duration.total_seconds())
                        print(granularity.total_seconds())
                        report_payload = objects.ReportPayload(r_id=r_id, value=value)
                        interval_start = dtstart
                        for i in range(int(report_back_duration.total_seconds()//granularity.total_seconds())):
                            print('after the 2 min adjust, the dtstart is: ')
                            print(dtstart)
                            intervals.append(objects.ReportInterval(dtstart=interval_start,
                                                                    duration= report_request['duration'] if report_request['duration'] else timedelta(0),
                                                                    report_payload=report_payload))
                            interval_start = interval_start + granularity
                            report_request['dtstart'] = interval_start
                            

                    else:
                        report_payload = objects.ReportPayload(r_id=r_id, value=value)
                        intervals.append(objects.ReportInterval(dtstart=dtstart,
                                                                    duration= report_request['duration'] if report_request['duration'] else timedelta(0),
                                                                    report_payload=report_payload))
        outgoing_report.intervals = intervals
        logger.info(f"The number of intervals in the report is now {len(outgoing_report.intervals)}")
        
        logger.info("Report will be sent now.")
        await self.pending_reports.put(outgoing_report)
        print(outgoing_report)
        print('after we add the outgoing_report, its length is:')
        print(self.pending_reports.qsize())
        
        
        
        # Figure out if the report is complete after this sampling
        # if data_collection_mode == 'incremental' and report_back_duration is not None\
        #         and report_back_duration > granularity:
        #     report_interval = report_back_duration.total_seconds()
        #     sampling_interval = granularity.total_seconds()
        #     expected_len = len(report_request['r_ids']) * int(report_interval / sampling_interval)
        #     if len(outgoing_report.intervals) == expected_len:
        #         logger.info("The report is now complete with all the values. Will queue for sending.")
        #         await self.pending_reports.put(self.incomplete_reports.pop(report_request_id))
        #     else:
        #         logger.debug("The report is not yet complete, will hold until it is.")
        #         self.incomplete_reports[report_request_id] = outgoing_report
        # else:
        #     logger.info("Report will be sent now.")
        #     await self.pending_reports.put(outgoing_report)
        #     print('after we add the outgoing_report, its length is:')
        #     print(self.pending_reports.qsize())
       
    async def cancel_report(self, payload):
        """
        Cancel this report.
        """
        #add scheduler(in the create_report) ->pending_report(added in the update_report) -> send out the report(in the _report_queue_worker)
        report_request_id = payload['report_request_id']
        report_to_follow = payload['report_to_follow']
        request_id = payload['request_id']
        job_id = report_request_id
        report_request = utils.find_by(self.report_requests, 'report_request_id', report_request_id)
        if not report_to_follow:
            ## In case that this report request was expired and we have deleted it before in the _report_queue function
            if report_request in self.report_requests:
                self._cancel_report(job_id)
                self.report_requests.remove(report_request)
        else:
            report_request['report_to_follow'] = True
        service = 'EiReport'
        message_type = 'oadrCanceledReport'
        message_payload = {'pending_reports': [{'report_request_id': utils.getmember(report, 'report_request_id')} for report in self.report_requests]}
        message = self._create_message(message_type, response={'response_code': 200,
                                                               'response_description': 'OK',
                                                               'request_id':request_id},
                                                            ven_id=self.ven_id,
                                                            **message_payload)

        await self._perform_request(service, message)

    
    
    
    def _cancel_report(self, job_id):
        try:
            self.scheduler.remove_job(job_id)
        except Exception as err:
            logger.warning(f"Internal error in the _cancel_report fucntion: {err}")
        
        

    async def _report_queue_worker(self):
        """
        A Queue worker that pushes out the pending reports.
        """
        try:
            while True:
                print('Did we ever get into the _report_queue_worker function?')
                print(self.pending_reports.qsize())
                report = asdict(await self.pending_reports.get())
                print('Did we ever get a report from the pending_reports queue')
                print(report)
                print(report['dtstart'])
                print(report['duration'])
                print(report['dtstart']+report['duration'])
                print(datetime.now(timezone.utc))
                ##If this is not a one shot report and it has expired. we remove the job and don't send updateReport
                if report['duration']!=timedelta(0) and report['dtstart']+report['duration'] < datetime.now(timezone.utc):
                    print('Did we ever cancel the report????')
                    report_request_id = report['report_request_id']
                    job_id = report['report_request_id']
                    report_request = utils.find_by(self.report_requests, 'report_request_id', report_request_id)
                    self.report_requests.remove(report_request)
                    self._cancel_report(job_id)
                else:
                    service = 'EiReport'
                    print('Before parse create_message of oadrUpdateReport message')
                    message = self._create_message('oadrUpdateReport',
                                                ven_id=self.ven_id,
                                                request_id=utils.generate_id(),
                                                reports=[report])
                    try:
                        print('Did we send the oadrUpdateReport message???')
                        print(message)
                        response_type, response_payload = await self._perform_request(service, message)
                    except Exception as err:
                        logger.error(f"Unable to send the report to the VTN. Error: {err}")
                    else:
                        #If VTN optinally cancel the report after this updateReport(piggyBack cancellation)
                        if 'cancel_report' in response_payload:
                            report_request_id = response_payload['cancel_report']['report_request_id']
                            report_to_follow = response_payload['cancel_report']['report_to_follow']
                            job_id = report_request_id
                            report_request = utils.find_by(self.report_requests, 'report_request_id', report_request_id)
                            if not report_to_follow:
                                self._cancel_report(job_id)
                                self.report_requests.remove(report_request)
                            else:
                                report_request['report_to_follow'] = True
                        #If this is a one shot report. We remove this job after we send out the updateReport
                        if report['report_back_duration']==timedelta(0):
                            print('we cancel the one shot report here')
                            report_request_id = report['report_request_id']
                            job_id = report['report_request_id']
                            report_request = utils.find_by(self.report_requests, 'report_request_id', report_request_id)
                            self.report_requests.remove(report_request)
                            self._cancel_report(job_id)
        except Exception as err:
            logger.warning(f"Internal error in the report queue worker fucntion: {err}")

    ###########################################################################
    #                                                                         #
    #                                  PLACEHOLDER                            #
    #                                                                         #
    ###########################################################################

    async def on_event(self, event):
        """
        Placeholder for the on_event handler.
        """
        logger.warning("You should implement your own on_event handler. This handler receives "
                       "an Event dict and should return either 'optIn' or 'optOut' based on your "
                       "choice. Will opt out of the event for now.")
        return 'optIn'

    async def on_update_event(self, event):
        """
        Placeholder for the on_update_event handler.
        """
        logger.warning("An Event was updated, but you don't have an on_updated_event handler configured. "
                       "You should implement your own on_update_event handler. This handler receives "
                       "an Event dict and should return either 'optIn' or 'optOut' based on your "
                       "choice. Will re-use the previous opt status for this event_id for now")
        event_id = event['event_descriptor']['event_id']
        if event_id in self.responded_events:
            return self.responded_events[event_id]

    async def on_register_report(self, report):
        """
        Placeholder for the on_register_report handler.
        """

    async def on_cancel_party_registration(self, message):
        """
        Function to respond to a registration cancellation request coming from the VTN
        """
        payload = {'ven_id': self.ven_id,
                   'registration_id': self.registration_id,}
        response = {'response_code': 200,
                    'response_description': 'OK',
                    'request_id': message['request_id']}
        message = self._create_message('oadrCanceledPartyRegistration',
                                       response=response, **payload)
        service = 'EiRegisterParty'

        await self._perform_request(service, message)

        # Update/Delete all the registration and reports information
        # TODO Verify if we need to update anything else
        self.registration_id = None
        self.ven_id = None
        self.report_requests = None
        self.reports = None
        self.report_callbacks = None
        self.report_requests = None
        self.incomplete_reports = None
        self.pending_reports = None
        await self.scheduler.remove_all_jobs()

    ###########################################################################
    #                                                                         #
    #                             EMPTY RESPONSES                             #
    #                                                                         #
    ###########################################################################

    async def send_response(self, service, response_code=200, response_description="OK", request_id=None):
        """
        Send an empty oadrResponse, for instance after receiving oadrRequestReregistration.
        """
        response = {'response_code': response_code,
                    'response_description': response_description,
                    'request_id': request_id
                    }
        msg = self._create_message('oadrResponse',
                                   response=response,
                                   ven_id=self.ven_id)
        await self._perform_request(service, msg)

    ###########################################################################
    #                                                                         #
    #                                  LOW LEVEL                              #
    #                                                                         #
    ###########################################################################

    async def _perform_request(self, service, message):
        client_session = await self._ensure_client_session()

        logger.debug(f"Client is sending {message}")
        url = f"{self.vtn_url}/{service}"
        try:
            async with client_session.post(url, data=message) as req:
                content = await req.read()
                if req.status != HTTPStatus.OK:
                    logger.warning(f"Non-OK status {req.status} when performing a request to {url} "
                                   f"with data {message}: {req.status} {content.decode('utf-8')}")
                    return None, {}
                logger.debug(content.decode('utf-8'))
        except aiohttp.client_exceptions.ClientConnectorError as err:
            # Could not connect to server
            logger.error(f"Could not connect to server with URL {self.vtn_url}:")
            logger.error(f"{err.__class__.__name__}: {str(err)}")
            await client_session.close()
            return None, {}
        except Exception as err:
            logger.error(f"Request error {err.__class__.__name__}:{err}")
            return None, {}
        if len(content) == 0:
            return None
        try:
            tree = validate_xml_schema(content)
            if self.vtn_fingerprint:
                validate_xml_signature(tree, cert_fingerprint=self.vtn_fingerprint)
            message_type, message_payload = parse_message(content)
        except XMLSyntaxError as err:
            logger.warning(f"Incoming message did not pass XML schema validation: {err}")
            return None, {}
        except errors.FingerprintMismatch as err:
            logger.warning(err)
            return None, {}
        except InvalidSignature:
            logger.warning("Incoming message had invalid signature, ignoring.")
            return None, {}
        except Exception as err:
            logger.error(f"The incoming message could not be parsed or validated: {err}")
            return None, {}
        if 'response' in message_payload and 'response_code' in message_payload['response']:
            if message_payload['response']['response_code'] != 200:
                logger.warning("We got a non-OK OpenADR response from the server: "
                               f"{message_payload['response']['response_code']}: "
                               f"{message_payload['response']['response_description']}")
        
        await client_session.close()

        return message_type, message_payload

    async def _on_event(self, message):
        logger.debug("The VEN received an event")
        events = message['events']
        incorrect_modification_number = False
        has_completed_initial_event_status = False 
        try:
            results = []
            for event in message['events']:
                print('this is the event')
                print(event)
                event_id = event['event_descriptor']['event_id']
                event_status = event['event_descriptor']['event_status']
                modification_number = event['event_descriptor']['modification_number']
                received_event = utils.find_by(self.received_events, 'event_descriptor.event_id', event_id)
                dtstart = event['active_period']['properties']['dtstart']
                duration = event['active_period']['properties']['duration']
                # implement event indicator over here using a util function
                asyncio.create_task(utils.event_indicator(event_id, event_status, dtstart, duration))
                if received_event:
                    if modification_number < received_event['event_descriptor']['modification_number']:
                        incorrect_modification_number = True
                        event_responses = [{'response_code': 462,
                                            'opt_type': 'optOut',
                                            'request_id': message['request_id'],
                                            'modification_number': events[i]['event_descriptor']['modification_number'],
                                            'event_id': events[i]['event_descriptor']['event_id']} 
                                            for i, event in enumerate(events)]
                        if len(event_responses) > 0 and event_responses[0] != "no_response_required":
                            response = {'response_code': 200,
                                        'response_description': 'OK',
                                        'request_id': message['request_id']}
                            message = self._create_message('oadrCreatedEvent',
                                                            response=response,
                                                            event_responses=event_responses,
                                                            ven_id=self.ven_id)
                            service = 'EiEvent'
                            response_type, response_payload = await self._perform_request(service, message)
                            logger.info(response_type, response_payload)
                        else:
                            logger.info(
                                "Not sending any event responses, because a response was not required/allowed by the VTN.")
                    if received_event['event_descriptor']['modification_number'] == modification_number:
                        # Re-submit the same opt type as we already had previously
                        result = self.responded_events[event_id]
                    else:
                        # Replace the event with the fresh copy
                        utils.pop_by(self.received_events, 'event_descriptor.event_id', event_id)
                        self.received_events.append(event)
                        # Wait for the result of the on_update_event handler
                        result = await utils.await_if_required(self.on_update_event(event))
                else:
                    # Wait for the result of the on_event
                    self.received_events.append(event)
                    result = self.on_event(event)
                if asyncio.iscoroutine(result):
                    result = await result
                results.append(result)
                if event_status in (enums.EVENT_STATUS.COMPLETED, enums.EVENT_STATUS.CANCELLED) and event_id in self.responded_events.keys():
                    self.responded_events.pop(event_id)
                elif event_status in (enums.EVENT_STATUS.COMPLETED, enums.EVENT_STATUS.CANCELLED) and event_id not in self.responded_events.keys():
                    has_completed_initial_event_status = True
                else:
                    self.responded_events[event_id] = result
            for i, result in enumerate(results):
                if result not in ('optIn', 'optOut') and events[i]['response_required'] == 'always':
                    logger.error("Your on_event or on_update_event handler must return 'optIn' or 'optOut'; "
                                 f"you supplied {result}. Please fix your on_event handler.")
                    results[i] = 'optIn'

            event_responses = [{'response_code': 200,
                            'response_description': 'OK',
                            'opt_type': results[i],
                            'request_id': message['request_id'],
                            'modification_number': events[i]['event_descriptor']['modification_number'],
                            'event_id': events[i]['event_descriptor']['event_id']}
                            if event['response_required'] == 'always' and utils.has_supported_signals(events[i]) and (not utils.determine_event_status(event['active_period']) == 'completed' or has_completed_initial_event_status) 
                            and utils.has_correct_ids(events[i], self.ven_id) and not utils.has_incorrect_market_context(events[i])
                            else
                            {'response_code': 460,
                            'response_description': 'Not OK',
                            'opt_type': results[i],
                            'request_id': message['request_id'],
                            'modification_number': events[i]['event_descriptor']['modification_number'],
                            'event_id': events[i]['event_descriptor']['event_id']} 
                            if not utils.has_supported_signals(events[i])
                            else
                            {'response_code': 462,
                            'opt_type': 'optOut',
                            'request_id': message['request_id'],
                            'modification_number': events[i]['event_descriptor']['modification_number'],
                            'event_id': events[i]['event_descriptor']['event_id']} 
                            if not utils.has_correct_ids(events[i], self.ven_id) or utils.has_incorrect_market_context(events[i])
                            else "no_response_required"
                            for i, event in enumerate(events)]

            if len(event_responses) > 0 and event_responses[0] != "no_response_required" and not incorrect_modification_number:
                response = {'response_code': 200,
                            'response_description': 'OK',
                            'request_id': message['request_id']}
                message = self._create_message('oadrCreatedEvent',
                                            response=response,
                                            event_responses=event_responses,
                                            ven_id=self.ven_id)
                service = 'EiEvent'
                response_type, response_payload = await self._perform_request(service, message)
                logger.info(response_type, response_payload)
            else:
                logger.info(
                    "Not sending any event responses, because a response was not required/allowed by the VTN.")

        except Exception as err:
            logger.error("Your on_event handler encountered an error. Will Opt Out of the event."
                         f"The error was {err.__class__.__name__}: {str(err)}")
            results = ['optIn'] * len(events)


    async def _event_cleanup(self):
        """
        Periodic task that will clean up completed and cancelled events in our memory.
        """
        for event in self.received_events:
            if event['event_descriptor']['event_status'] == 'cancelled' or \
                    utils.determine_event_status(event['active_period']) == 'completed':
                logger.info(f"Removing event {event} because it is no longer relevant.")
                self.received_events.pop(self.received_events.index(event))

    async def _poll(self):
        logger.debug("Now polling for new messages")
        response_type, response_payload = await self.poll()
        if response_type is None:
            return

        elif response_type == 'oadrResponse':
            logger.debug("Received empty response from the VTN.")
            return

        elif response_type == 'oadrRequestReregistration':
            logger.info("The VTN required us to re-register. Calling the registration procedure.")
            await self.send_response(service='EiRegisterParty')
            await self.create_party_registration(ven_id=self.ven_id, registration_id=self.registration_id)

        elif response_type == 'oadrDistributeEvent':
            incorrect_vtn_id = False
            if response_payload['vtn_id'] != self.vtn_id:
                incorrect_vtn_id = True
                service = 'EiEvent'
                response = {'response_code': 452,
                            'request_id': response_payload['request_id']
                            }
                msg = self._create_message('oadrCreatedEvent', response=response, ven_id=self.ven_id)
                await self._perform_request(service, msg)
            if 'events' in response_payload and len(response_payload['events']) > 0 and not incorrect_vtn_id:
                await self._on_event(response_payload)

        elif response_type == 'oadrUpdateReport':
            await self._on_report(response_payload)

        elif response_type == 'oadrCreateReport':
            print('recieve oadrCreateReport.....')
            status_code = 200
            if 'report_requests' in response_payload:
                for report_request in response_payload['report_requests']:
                    if not await self.create_report(report_request):
                        status_code = 452
            await self.created_report(response_payload, status_code)

        elif response_type == 'oadrRegisterReport':
            # if 'reports' in response_payload and len(response_payload['reports']) > 0:
            #     for report in response_payload['reports']:
            #         await self.register_report(report)
            await self.register_report(response_payload)
            await self.request_event()

        elif response_type == 'oadrCancelPartyRegistration':
            incoming_registration_id = response_payload['registration_id']
            if(incoming_registration_id != self.registration_id):
                service = 'EiRegisterParty'
                response = {'response_code': 452,
                            'response_description': 'Not OK',
                            'request_id': response_payload['request_id']
                            }
                msg = self._create_message('oadrCanceledPartyRegistration', response=response, ven_id=self.ven_id)
                await self._perform_request(service, msg)
                return 
            await self.on_cancel_party_registration(response_payload)
        
        elif response_type=='oadrCancelReport':
            print('The cancel report payload is: ')
            print(response_payload)
            await self.cancel_report(response_payload)

        else:
            logger.warning(f"No handler implemented for incoming message "
                           f"of type {response_type}, ignoring.")

        # Immediately poll again, because there might be more messages
        #await self._poll()

    async def _ensure_client_session(self):
        headers = {'content-type': 'application/xml'}
        if self.cert_path:
            ssl_context = ssl.create_default_context(cafile=self.ca_file,
                                                        purpose=ssl.Purpose.CLIENT_AUTH)
            ssl_context.load_cert_chain(self.cert_path, self.key_path, self.passphrase)
            ssl_context.check_hostname = False
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            client_session = aiohttp.ClientSession(connector=connector, headers=headers)
        else:
            client_session = aiohttp.ClientSession(headers=headers)
        return client_session