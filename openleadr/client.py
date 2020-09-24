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

import xmltodict
import random
import aiohttp
from openleadr.utils import peek, generate_id, certificate_fingerprint
from openleadr.messaging import create_message, parse_message
from openleadr import enums
from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
from asyncio import iscoroutine
from functools import partial
import warnings

MEASURANDS = {'power_real': 'power_quantity',
              'power_reactive': 'power_quantity',
              'power_apparent': 'power_quantity',
              'energy_real': 'energy_quantity',
              'energy_reactive': 'energy_quantity',
              'energy_active': 'energy_quantity'}

class OpenADRClient:
    """
    Main client class. Most of these methods will be called automatically, but
    you can always choose to call them manually.
    """
    def __init__(self, ven_name, vtn_url, debug=False, cert=None, key=None, passphrase=None, vtn_fingerprint=None):
        """
        Initializes a new OpenADR Client (Virtual End Node)

        :param str ven_name: The name for this VEN
        :param str vtn_url: The URL of the VTN (Server) to connect to
        :param bool debug: Whether or not to print debugging messages
        :param str cert: The path to a PEM-formatted Certificate file to use for signing messages
        :param str key: The path to a PEM-formatted Private Key file to use for signing messages
        :param str fingerprint: The fingerprint for the VTN's certificate to verify incomnig messages
        """

        self.ven_name = ven_name
        self.vtn_url = vtn_url
        self.ven_id = None
        self.poll_frequency = None
        self.debug = debug
        self.reports = {}           # Mapping of all available reports from the VEN
        self.report_requests = {}   # Mapping of the reports requested by the VTN
        self.report_schedulers = {} # Mapping between reportRequestIDs and our internal report schedulers
        self.scheduler = AsyncIOScheduler()
        self.client_session = aiohttp.ClientSession()

        if cert and key:
            with open(cert, 'rb') as file:
                cert = file.read()
            with open(key, 'rb') as file:
                key = file.read()
            print("*" * 80)
            print("Your VEN Certificate Fingerprint is", certificate_fingerprint(cert))
            print("Please deliver this fingerprint to the VTN you are connecting to.")
            print("You do not need to keep this a secret.")
            print("*" * 80)

        self._create_message = partial(create_message,
                                       cert=cert,
                                       key=key,
                                       passphrase=passphrase)
        self._parse_message = partial(parse_message,
                                      fingerprint=vtn_fingerprint)


    async def run(self):
        """
        Run the client in full-auto mode.
        """
        if not hasattr(self, 'on_event'):
            raise NotImplementedError("You must implement an on_event function or coroutine.")

        await self.create_party_registration()

        if not self.ven_id:
            print("No VEN ID received from the VTN, aborting registration.")
            return

        if self.reports:
            await self.register_report()

        # Set up automatic polling
        if self.poll_frequency.total_seconds() < 60:
            cron_second = f"*/{self.poll_frequency.seconds}"
            cron_minute = "*"
            cron_hour = "*"
        elif self.poll_frequency.total_seconds() < 3600:
            cron_second = "0"
            cron_minute = f'*/{int(self.poll_frequency.total_seconds() / 60)}'
            cron_hour = "*"
        elif self.poll_frequency.total_seconds() < 86400:
            cron_second = "0"
            cron_minute = "0"
            cron_hour = f'*/{int(self.poll_frequency.total_seconds() / 3600)}'
        elif self.poll_frequency.total_seconds() > 86400:
            print("Polling with intervals of more than 24 hours is not supported.")
            return

        self.scheduler.add_job(self._poll, trigger='cron', second=cron_second, minute=cron_minute, hour=cron_hour)
        self.scheduler.start()

    def add_report(self, callable, report_id, report_name, reading_type, report_type,
                         sampling_rate, resource_id, measurand, unit, scale="none",
                         power_ac=True, power_hertz=50, power_voltage=230, market_context=None):
        """
        Add a new reporting capability to the client.

        :param callable callable: A callable or coroutine that will fetch the value for a specific report. This callable will be passed the report_id and the r_id of the requested value.
        :param str report_id: A unique identifier for this report.
        :param str report_name: An OpenADR name for this report (one of openleadr.enums.REPORT_NAME)
        :param str reading_type: An OpenADR reading type (found in openleadr.enums.READING_TYPE)
        :param str report_type: An OpenADR report type (found in openleadr.enums.REPORT_TYPE)
        :param datetime.timedelta sampling_rate: The sampling rate for the measurement.
        :param resource_id: A specific name for this resource within this report.
        :param str unit: The unit for this measurement.

        """

        if report_name not in enums.REPORT_NAME.values:
            raise ValueError(f"{report_name} is not a valid report_name. Valid options are {', '.join(enums.REPORT_NAME.values)}.")
        if reading_type not in enums.READING_TYPE.values:
            raise ValueError(f"{reading_type} is not a valid reading_type. Valid options are {', '.join(enums.READING_TYPE.values)}.")
        if report_type not in enums.REPORT_TYPE.values:
            raise ValueError(f"{report_type} is not a valid report_type. Valid options are {', '.join(enums.REPORT_TYPE.values)}.")
        if measurand not in MEASURANDS:
            raise ValueError(f"{measurand} is not a valid measurand. Valid options are 'power_real', 'power_reactive', 'power_apparent', 'energy_real', 'energy_reactive', 'energy_active', 'energy_quantity', 'voltage'")
        if scale not in enums.SI_SCALE_CODE.values:
            raise ValueError(f"{scale} is not a valid scale. Valid options are {', '.join(enums.SI_SCALE_CODE.values)}")

        report_description = {'market_context': market_context,
                              'r_id': resource_id,
                              'reading_type': reading_type,
                              'report_type': report_type,
                              'sampling_rate': {'max_period': sampling_rate,
                                                'min_period': sampling_rate,
                                                'on_change': False},
                               measurand: {'item_description': measurand,
                                           'item_units': unit,
                                           'si_scale_code': scale}}
        if 'power' in measurand:
            report_description[measurand]['power_attributes'] = {'ac': power_ac, 'hertz': power_hertz, 'voltage': power_voltage}

        if report_id in self.reports:
            report = self.reports[report_id]['report_descriptions'].append(report_description)
        else:
            report = {'callable': callable,
                      'created_date_time': datetime.now(timezone.utc),
                      'report_id': report_id,
                      'report_name': report_name,
                      'report_request_id': generate_id(),
                      'report_specifier_id': report_id + "_" + report_name.lower(),
                      'report_descriptions': [report_description]}
        self.reports[report_id] = report
        self.report_ids[resource_id] = {'item_base': measurand}

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
                                  transport_name='simpleHttp', transport_address=None, ven_id=None):
        """
        Take the neccessary steps to register this client with the server.

        :param bool http_pull_model: Whether to use the 'pull' model for HTTP.
        :param bool xml_signature: Whether to sign each XML message.
        :param bool report_only: Whether or not this is a reporting-only client which does not deal with Events.
        :param str profile_name: Which OpenADR profile to use.
        :param str transport_name: The transport name to use. Either 'simpleHttp' or 'xmpp'.
        :param str transport_address: Which public-facing address the server should use to communicate.
        :param str ven_id: The ID for this VEN. If you leave this blank, a VEN_ID will be assigned by the VTN.
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
        message = self._create_message('oadrCreatePartyRegistration', request_id=generate_id(), **payload)
        response_type, response_payload = await self._perform_request(service, message)
        if response_type is None:
            return
        if response_payload['response']['response_code'] != 200:
            status_code = response_payload['response']['response_code']
            status_description = response_payload['response']['response_description']
            print(f"Got error on Create Party Registration: {status_code} {status_description}")
            return
        self.ven_id = response_payload['ven_id']
        self.poll_frequency = response_payload.get('requested_oadr_poll_freq', timedelta(seconds=10))
        print(f"VEN is now registered with ID {self.ven_id}")
        print(f"The polling frequency is {self.poll_frequency}")
        return response_type, response_payload

    async def cancel_party_registration(self):
        raise NotImplementedError("Cancel Registration is not yet implemented")

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

    async def register_report(self):
        """
        Tell the VTN about our reporting capabilities.
        """
        request_id = generate_id()

        payload = {'request_id': generate_id(),
                   'ven_id': self.ven_id,
                   'reports': self.reports}

        service = 'EiReport'
        message = self._create_message('oadrRegisterReport', **payload)
        response_type, response_payload = await self._perform_request(service, message)

        # Remember which reports the VTN is interested in

        return response_type, response_payload

    async def created_report(self):
        pass

    async def poll(self):
        """
        Request the next available message from the Server. This coroutine is called automatically.
        """
        service = 'OadrPoll'
        message = self._create_message('oadrPoll', ven_id=self.ven_id)
        response_type, response_payload = await self._perform_request(service, message)
        return response_type, response_payload

    async def update_report(self, report_id, resource_id=None):
        """
        Calls the previously registered report callable, and send the result as a message to the VTN.
        """
        if not resource_id:
            resource_ids = self.reports[report_id]['report_descriptions'].keys()
        elif isinstance(resource_id, str):
            resource_ids = [resource_id]
        else:
            resource_ids = resource_id
        value = self.reports[report_id]['callable'](resource_id)
        if iscoroutine(value):
            value = await value

        report_type = self.reports[report_id][resource_id]['report_type']
        for measurand in MEASURAND:
            if measurand in self.reports[report_id][resource_id]:
                item_base = measurand
                break
        report = {'report_id': report_id,
                  'report_descriptions': {resource_id: {MEASURANDS[measurand]: {'quantity': value,
                                                                         measurand: self.reports[report_id][resource_id][measurand]},
                                          'report_type': self.reports[report_id][resource_id]['report_type'],
                                          'reading_type': self.reports[report_id][resource_id]['reading_type']}},
                  'report_name': self.report['report_id']['report_name'],
                  'report_request_id': self.reports['report_id']['report_request_id'],
                  'report_specifier_id': self.report['report_id']['report_specifier_id'],
                  'created_date_time': datetime.now(timezone.utc)}

        service = 'EiReport'
        message = self._create_message('oadrUpdateReport', report)
        response_type, response_payload = self._perform_request(service, message)
        if response_type is not None:
            # We might get a oadrCancelReport message in this thing:
            if 'cancel_report' in response_payload:
                print("TODO: cancel this report")


    async def _perform_request(self, service, message):
        if self.debug:
            print(f"Client is sending {message}")
        url = f"{self.vtn_url}/{service}"
        try:
            async with self.client_session.post(url, data=message) as req:
                if req.status != HTTPStatus.OK:
                    warnings.warn(f"Non-OK status when performing a request to {url} with data {message}: {req.status}")
                    return None, {}
                content = await req.read()
                if self.debug:
                    print(content.decode('utf-8'))
        except:
            # Could not connect to server
            warnings.warn(f"Could not connect to server with URL {self.vtn_url}")
            return None, {}
        try:
            message_type, message_payload = self._parse_message(content)
        except Exception as err:
            warnings.warn(f"The incoming message could not be parsed or validated: {content}.")
            raise err
            return None, {}
        return message_type, message_payload

    async def _on_event(self, message):
        if self.debug:
            print("ON_EVENT")
        result = self.on_event(message)
        if iscoroutine(result):
            result = await result

        if self.debug:
            print(f"Now responding with {result}")
        request_id = message['request_id']
        event_id = message['events'][0]['event_descriptor']['event_id']
        await self.created_event(request_id, event_id, result)
        return

    async def _poll(self):
        print("Now polling")
        response_type, response_payload = await self.poll()
        if response_type is None:
            return

        if response_type == 'oadrResponse':
            print("No events or reports available")
            return

        if response_type == 'oadrRequestReregistration':
            await self.create_party_registration()

        if response_type == 'oadrDistributeEvent':
            await self._on_event(response_payload)

        elif response_type == 'oadrUpdateReport':
            await self._on_report(response_payload)

        else:
            print(f"No handler implemented for message type {response_type}, ignoring.")

        # Immediately poll again, because there might be more messages
        await self._poll()
