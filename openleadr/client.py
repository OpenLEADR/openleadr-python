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

"""
OpenADR Client for Python
"""

import asyncio
import inspect
import logging
import ssl
from datetime import datetime, timedelta, timezone
from functools import partial
from http import HTTPStatus
from random import randint

import aiohttp
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from openleadr import enums, objects
from openleadr.messaging import create_message, parse_message
from openleadr.utils import generate_id, certificate_fingerprint, find_by, cron_config

logger = logging.getLogger('openleadr')


class OpenADRClient:
    """
    Main client class. Most of these methods will be called automatically, but
    you can always choose to call them manually.
    """
    def __init__(self, ven_name, vtn_url, debug=False, cert=None, key=None,
                 passphrase=None, vtn_fingerprint=None, show_fingerprint=True, ca_file=None):
        """
        Initializes a new OpenADR Client (Virtual End Node)

        :param str ven_name: The name for this VEN
        :param str vtn_url: The URL of the VTN (Server) to connect to
        :param bool debug: Whether or not to print debugging messages
        :param str cert: The path to a PEM-formatted Certificate file to use
                         for signing messages.
        :param str key: The path to a PEM-formatted Private Key file to use
                        for signing messages.
        :param str fingerprint: The fingerprint for the VTN's certificate to
                                verify incomnig messages
        :param str show_fingerprint: Whether to print your own fingerprint
                                     on startup. Defaults to True.
        :param str ca_file: The path to the PEM-formatted CA file for validating the VTN server's
                            certificate.
        """

        self.ven_name = ven_name
        if vtn_url.endswith("/"):
            vtn_url = vtn_url[:-1]
        self.vtn_url = vtn_url
        self.ven_id = None
        self.poll_frequency = None
        self.debug = debug
        self.reports = []
        self.report_callbacks = {}              # Holds the callbacks for each specific report
        self.report_requests = []               # Keep track of the report requests from the VTN
        self.incomplete_reports = {}            # Holds reports that are being populated over time
        self.pending_reports = asyncio.Queue()  # Holds reports that are waiting to be sent
        self.scheduler = AsyncIOScheduler()
        self.client_session = None
        self.report_queue_task = None

        self.cert_path = cert
        self.key_path = key
        self.passphrase = passphrase
        self.ca_file = ca_file

        if cert and key:
            with open(cert, 'rb') as file:
                cert = file.read()
            with open(key, 'rb') as file:
                key = file.read()
            if show_fingerprint:
                print("")
                print("*" * 80)
                print("Your VEN Certificate Fingerprint is ".center(80))
                print(f"{certificate_fingerprint(cert).center(80)}".center(80))
                print("Please deliver this fingerprint to the VTN.".center(80))
                print("You do not need to keep this a secret.".center(80))
                print("*" * 80)
                print("")

        self._create_message = partial(create_message,
                                       cert=cert,
                                       key=key,
                                       passphrase=passphrase)

    async def run(self):
        """
        Run the client in full-auto mode.
        """
        # if not hasattr(self, 'on_event'):
        #     raise NotImplementedError("You must implement on_event.")

        await self.create_party_registration()

        if not self.ven_id:
            logger.error("No VEN ID received from the VTN, aborting.")
            return

        if self.reports:
            await self.register_reports(self.reports)
            loop = asyncio.get_event_loop()
            self.report_queue_task = loop.create_task(self._report_queue_worker())

        await self._poll()

        # Set up automatic polling
        if self.poll_frequency.total_seconds() < 60:
            seconds_offset = randint(0, self.poll_frequency.seconds)
            cron_second = f"{seconds_offset}/{self.poll_frequency.seconds}"
            cron_minute = "*"
            cron_hour = "*"
        elif self.poll_frequency.total_seconds() < 3600:
            cron_second = randint(0, 59)
            cron_minute = f'*/{int(self.poll_frequency.total_seconds() / 60)}'
            cron_hour = "*"
        elif self.poll_frequency.total_seconds() < 86400:
            cron_second = randint(0, 59)
            cron_minute = "0"
            cron_hour = f'*/{int(self.poll_frequency.total_seconds() / 3600)}'
        elif self.poll_frequency.total_seconds() > 86400:
            logger.warning("Polling with intervals of more than 24 hours is not supported. "
                           "Will use 24 hours as the logging interval.")
            cron_second = randint(0, 59)
            cron_minute = "0"
            cron_hour = "0"
            return

        self.scheduler.add_job(self._poll,
                               trigger='cron',
                               second=cron_second,
                               minute=cron_minute,
                               hour=cron_hour)
        self.scheduler.start()

    async def stop(self):
        """
        Cleanly stops the client. Run this coroutine before closing your event loop.
        """
        if self.scheduler.running:
            self.scheduler.shutdown()
        if self.report_queue_task:
            self.report_queue_task.cancel()
        await self.client_session.close()

    def add_handler(self, handler, callback):
        """
        Add a callback for the given situation
        """
        if handler not in ('on_event', 'on_update_event'):
            logger.error("'handler' must be either on_event or on_update_event")
            return

        setattr(self, handler, callback)

    def add_report(self, callback, resource_id, measurement,
                   data_collection_mode='incremental',
                   report_specifier_id=None, r_id=None,
                   report_name=enums.REPORT_NAME.TELEMETRY_USAGE,
                   reading_type=enums.READING_TYPE.DIRECT_READ,
                   report_type=enums.REPORT_TYPE.READING, sampling_rate=None, data_source=None,
                   scale="none", unit=None, power_ac=True, power_hertz=50, power_voltage=230,
                   market_context=None):
        """
        Add a new reporting capability to the client.

        :param callable callback: A callback or coroutine that will fetch the value for a specific
                                  report. This callback will be passed the report_id and the r_id
                                  of the requested value.
        :param str resource_id: A specific name for this resource within this report.
        :param str measurement: The quantity that is being measured (openleadr.enums.MEASUREMENTS).
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

        if data_collection_mode not in ('incremental', 'full'):
            raise ValueError("The data_collection_mode should be 'incremental' or 'full'.")

        if data_collection_mode == 'full':
            args = inspect.signature(callback).parameters
            if not ('date_from' in args and 'date_to' in args and 'sampling_interval' in args):
                raise TypeError("Your callback function must accept the 'date_from', 'date_to' "
                                "and 'sampling_interval' arguments if used "
                                "with data_collection_mode 'full'.")

        # Determine the correct item name, item description and unit
        if isinstance(measurement, objects.Measurement):
            item_base = measurement
        elif measurement.upper() in enums.MEASUREMENTS.members:
            item_base = enums.MEASUREMENTS[measurement.upper()]
        else:
            item_base = objects.Measurement(item_name='customUnit',
                                            item_description=measurement,
                                            item_units=unit,
                                            si_scale_code=scale)

        if scale is not None:
            if scale in enums.SI_SCALE_CODE.values:
                item_base.si_scale_code = scale
            else:
                raise ValueError("The 'scale' argument must be one of '{'. ',join(enums.SI_SCALE_CODE.values)}")

        # Check if unit is compatible
        if unit is not None and unit != item_base.item_units \
                and unit not in item_base.acceptable_units:
            logger.warning(f"The supplied unit {unit} for measurement {measurement} "
                           f"will be ignored, {item_base.item_units} will be used instead."
                           f"Allowed units for this measurement are: "
                           f"{', '.join(item_base.acceptable_units)}")

        # Get or create the relevant Report
        if report_specifier_id:
            report = find_by(self.reports,
                             'report_name', report_name,
                             'report_specifier_id', report_specifier_id)
        else:
            report = find_by(self.reports, 'report_name', report_name)

        if not report:
            report_specifier_id = report_specifier_id or generate_id()
            report = objects.Report(created_date_time=datetime.now(),
                                    report_name=report_name,
                                    report_specifier_id=report_specifier_id,
                                    data_collection_mode=data_collection_mode)
            self.reports.append(report)

        # Add the new report description to the report
        target = objects.Target(resource_id=resource_id)
        r_id = generate_id()
        report_description = objects.ReportDescription(r_id=r_id,
                                                       reading_type=reading_type,
                                                       report_data_source=target,
                                                       report_subject=target,
                                                       report_type=report_type,
                                                       sampling_rate=sampling_rate,
                                                       measurement=item_base,
                                                       market_context='Market01')
        self.report_callbacks[(report.report_specifier_id, r_id)] = callback
        report.report_descriptions.append(report_description)

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
        request_id = generate_id()
        service = 'EiRegisterParty'
        message = self._create_message('oadrQueryRegistration', request_id=request_id)
        response_type, response_payload = await self._perform_request(service, message)
        return response_type, response_payload

    async def create_party_registration(self, http_pull_model=True, xml_signature=False,
                                        report_only=False, profile_name='2.0b',
                                        transport_name='simpleHttp', transport_address=None,
                                        ven_id=None):
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
        request_id = generate_id()
        service = 'EiRegisterParty'
        payload = {'ven_name': self.ven_name,
                   'http_pull_model': http_pull_model,
                   'xml_signature': xml_signature,
                   'report_only': report_only,
                   'profile_name': profile_name,
                   'transport_name': transport_name,
                   'transport_address': transport_address}
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
        self.poll_frequency = response_payload.get('requested_oadr_poll_freq',
                                                   timedelta(seconds=10))
        logger.info(f"VEN is now registered with ID {self.ven_id}")
        logger.info(f"The polling frequency is {self.poll_frequency}")
        return response_type, response_payload

    async def cancel_party_registration(self):
        raise NotImplementedError("Cancel Registration is not yet implemented")

    ###########################################################################
    #                                                                         #
    #                              EVENT METHODS                              #
    #                                                                         #
    ###########################################################################

    async def request_event(self, reply_limit=1):
        """
        Request the next Event from the VTN, if it has any.
        """
        payload = {'request_id': generate_id(),
                   'ven_id': self.ven_id,
                   'reply_limit': reply_limit}
        message = self._create_message('oadrRequestEvent', **payload)
        service = 'EiEvent'
        response_type, response_payload = await self._perform_request(service, message)
        return response_type, response_payload

    async def created_event(self, request_id, event_id, opt_type, modification_number=1):
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

    async def register_reports(self, reports):
        """
        Tell the VTN about our reports. The VTN miht respond with an
        oadrCreateReport message that tells us which reports are to be sent.
        """
        request_id = generate_id()
        payload = {'request_id': request_id,
                   'ven_id': self.ven_id,
                   'reports': reports}

        service = 'EiReport'
        message = self._create_message('oadrRegisterReport', **payload)
        response_type, response_payload = await self._perform_request(service, message)

        # Handle the subscriptions that the VTN is interested in.
        if 'report_requests' in response_payload:
            for report_request in response_payload['report_requests']:
                await self.create_report(report_request)

        message_type = 'oadrCreatedReport'
        message_payload = {}

        return message_type, message_payload

    async def create_report(self, report_request):
        """
        Add the requested reports to the reporting mechanism.
        This is called when the VTN requests reports from us.

        :param report_request dict: The oadrReportRequest dict from the VTN.
        """
        # Get the relevant variables from the report requests
        report_request_id = report_request['report_request_id']
        report_specifier_id = report_request['report_specifier']['report_specifier_id']
        report_back_duration = report_request['report_specifier'].get('report_back_duration')
        granularity = report_request['report_specifier']['granularity']

        # Check if this report actually exists
        report = find_by(self.reports, 'report_specifier_id', report_specifier_id)
        if not report:
            logger.error(f"A non-existant report with report_specifier_id "
                         f"{report_specifier_id} was requested.")
            return False

        # Check and collect the requested r_ids for this report
        requested_r_ids = []
        for specifier_payload in report_request['report_specifier']['specifier_payloads']:
            r_id = specifier_payload['r_id']
            # Check if the requested r_id actually exists
            rd = find_by(report.report_descriptions, 'r_id', r_id)
            if not rd:
                logger.error(f"A non-existant report with r_id {r_id} "
                             f"inside report with report_specifier_id {report_specifier_id} "
                             f"was requested.")
                continue

            # Check if the requested measurement exists and if the correct unit is requested
            if 'measurement' in specifier_payload:
                measurement = specifier_payload['measurement']
                if measurement['item_description'] != rd.measurement.item_description:
                    logger.error(f"A non-matching measurement description for report with "
                                 f"report_request_id {report_request_id} and r_id {r_id} was given "
                                 f"by the VTN. Offered: {rd.measurement.item_description}, "
                                 f"requested: {measurement['item_description']}")
                    continue
                if measurement['item_units'] != rd.measurement.item_units:
                    logger.error(f"A non-matching measurement unit for report with "
                                 f"report_request_id {report_request_id} and r_id {r_id} was given "
                                 f"by the VTN. Offered: {rd.measurement.item_units}, "
                                 f"requested: {measurement['item_units']}")
                    continue

            if granularity is not None:
                if not rd.sampling_rate.min_period <= granularity <= rd.sampling_rate.max_period:
                    logger.error(f"An invalid sampling rate {granularity} was requested for report "
                                 f"with report_specifier_id {report_specifier_id} and r_id {r_id}. "
                                 f"The offered sampling rate was between "
                                 f"{rd.sampling_rate.min_period} and "
                                 f"{rd.sampling_rate.max_period}")
                    continue
            else:
                # If no granularity is specified, set it to the lowest sampling rate.
                granularity = rd.sampling_rate.max_period

            requested_r_ids.append(r_id)

        callback = partial(self.update_report, report_request_id=report_request_id)

        reporting_interval = report_back_duration or granularity
        job = self.scheduler.add_job(func=callback,
                                     trigger='cron',
                                     **cron_config(reporting_interval))

        self.report_requests.append({'report_request_id': report_request_id,
                                     'report_specifier_id': report_specifier_id,
                                     'report_back_duration': report_back_duration,
                                     'r_ids': requested_r_ids,
                                     'granularity': granularity,
                                     'job': job})

    async def update_report(self, report_request_id):
        """
        Call the previously registered report callback and send the result as a message to the VTN.
        """
        logger.debug(f"Running update_report for {report_request_id}")
        report_request = find_by(self.report_requests, 'report_request_id', report_request_id)
        granularity = report_request['granularity']
        report_back_duration = report_request['report_back_duration']
        report_specifier_id = report_request['report_specifier_id']
        report = find_by(self.reports, 'report_specifier_id', report_specifier_id)
        data_collection_mode = report.data_collection_mode

        if report_request_id in self.incomplete_reports:
            logger.debug("We were already compiling this report")
            outgoing_report = self.incomplete_reports[report_request_id]
        else:
            logger.debug("There is no report in progress")
            outgoing_report = objects.Report(report_request_id=report_request_id,
                                             report_specifier_id=report.report_specifier_id,
                                             report_name=report.report_name,
                                             intervals=[])

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
                for dt, value in result:
                    report_payload = objects.ReportPayload(r_id=r_id, value=value)
                    intervals.append(objects.ReportInterval(dtstart=dt,
                                                            report_payload=report_payload))

        else:
            for r_id in report_request['r_ids']:
                report_callback = self.report_callbacks[(report_specifier_id, r_id)]
                result = report_callback()
                if asyncio.iscoroutine(result):
                    result = await result
                if isinstance(result, (int, float)):
                    result = [(datetime.now(timezone.utc), result)]
                for dt, value in result:
                    logger.info(f"Adding {dt}, {value} to report")
                    report_payload = objects.ReportPayload(r_id=r_id, value=value)
                    intervals.append(objects.ReportInterval(dtstart=dt,
                                                            report_payload=report_payload))
        outgoing_report.intervals = intervals
        logger.info(f"The number of intervals in the report is now {len(outgoing_report.intervals)}")

        # Figure out if the report is complete after this sampling
        if data_collection_mode == 'incremental' and report_back_duration is not None\
                and report_back_duration > granularity:
            report_interval = report_back_duration.total_seconds()
            sampling_interval = granularity.total_seconds()
            expected_len = len(report_request['r_ids']) * int(report_interval / sampling_interval)
            if len(outgoing_report.intervals) == expected_len:
                logger.info("The report is now complete with all the values. Will queue for sending.")
                await self.pending_reports.put(self.incomplete_reports.pop(report_request_id))
            else:
                logger.debug("The report is not yet complete, will hold until it is.")
                self.incomplete_reports[report_request_id] = outgoing_report
        else:
            logger.info("Report will be sent now.")
            await self.pending_reports.put(outgoing_report)

    async def cancel_report(self, payload):
        """
        Cancel this report.
        """

    async def _report_queue_worker(self):
        """
        A Queue worker that pushes out the pending reports.
        """

        while True:
            report = await self.pending_reports.get()
            logger.info("Sending report!!!")

            service = 'EiReport'
            message = self._create_message('oadrUpdateReport', reports=[report])

            try:
                response_type, response_payload = await self._perform_request(service, message)
            except Exception as err:
                logger.error(f"Unable to send the report to the VTN. Error: {err}")
            else:
                if 'cancel_report' in response_payload:
                    await self.cancel_report(response_payload['cancel_report'])

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
        return 'optOut'

    ###########################################################################
    #                                                                         #
    #                                  LOW LEVEL                              #
    #                                                                         #
    ###########################################################################

    async def _perform_request(self, service, message):
        await self._ensure_client_session()
        logger.debug(f"Client is sending {message}")
        url = f"{self.vtn_url}/{service}"
        try:
            async with self.client_session.post(url, data=message) as req:
                content = await req.read()
                if req.status != HTTPStatus.OK:
                    logger.warning(f"Non-OK status when performing a request to {url} with data "
                                   f"{message}: {req.status} {content.decode('utf-8')}")
                logger.debug(content.decode('utf-8'))
        except aiohttp.client_exceptions.ClientConnectorError as err:
            # Could not connect to server
            logger.error(f"Could not connect to server with URL {self.vtn_url}:")
            logger.error(f"{err.__class__.__name__}: {str(err)}")
            return None, {}
        except Exception as err:
            logger.error(f"Request error {err.__class__.__name__}:{err}")
            return None, {}
        try:
            message_type, message_payload = parse_message(content)
        except Exception as err:
            logger.error(f"The incoming message could not be parsed or validated: {err}")
            return None, {}
        return message_type, message_payload

    async def _on_event(self, message):
        logger.debug("The VEN received an event")
        try:
            result = self.on_event(message)
            if asyncio.iscoroutine(result):
                result = await result
        except Exception as err:
            logger.error("Your on_event handler encountered an error. Will Opt Out of the event. "
                         f"The error was {err.__class__.__name__}: {str(err)}")
            result = 'optOut'

        if result not in ('optIn', 'optOut'):
            logger.error("Your on_event handler must return 'optIn' or 'optOut'; "
                         f"you supplied {result}. Please fix your on_event handler.")
            result = 'optOut'

        logger.debug(f"Now responding with {result}")
        request_id = message['request_id']
        event_id = message['events'][0]['event_descriptor']['event_id']
        await self.created_event(request_id, event_id, result)
        return

    async def _poll(self):
        logger.debug("Now polling for new messages")
        response_type, response_payload = await self.poll()
        if response_type is None:
            return

        if response_type == 'oadrResponse':
            logger.debug("No events or reports available")
            return

        if response_type == 'oadrRequestReregistration':
            logger.info("The VTN required us to re-register. Calling the registration procedure.")
            await self.create_party_registration()

        if response_type == 'oadrDistributeEvent':
            await self._on_event(response_payload)

        elif response_type == 'oadrUpdateReport':
            await self._on_report(response_payload)

        else:
            logger.warning(f"No handler implemented for incoming message "
                           f"of type {response_type}, ignoring.")

        # Immediately poll again, because there might be more messages
        await self._poll()

    async def _ensure_client_session(self):
        if not self.client_session:
            if self.cert_path:
                ssl_context = ssl.create_default_context(cafile=self.ca_file,
                                                         purpose=ssl.Purpose.CLIENT_AUTH)
                ssl_context.load_cert_chain(self.cert_path, self.key_path, self.passphrase)
                ssl_context.check_hostname = False
                connector = aiohttp.TCPConnector(ssl=ssl_context)
                self.client_session = aiohttp.ClientSession(connector=connector)
                print("Created Client Session")
            else:
                self.client_session = aiohttp.ClientSession()
