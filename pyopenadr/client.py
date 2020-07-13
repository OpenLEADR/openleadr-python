#!/Users/stan/Development/ElaadNL/pyopenadr/.python/bin/python3

import xmltodict
import random
import aiohttp
from jinja2 import Environment, PackageLoader, select_autoescape
from pyopenadr.utils import parse_message, create_message, new_request_id, peek, generate_id
from pyopenadr import enums
from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
from asyncio import iscoroutine

MEASURANDS = {'power_real': 'power_quantity',
              'power_reactive': 'power_quantity',
              'power_apparent': 'power_quantity',
              'energy_real': 'energy_quantity',
              'energy_reactive': 'energy_quantity',
              'energy_active': 'energy_quantity'}

class OpenADRClient:
    def __init__(self, ven_name, vtn_url, debug=False):
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

    async def run(self):
        """
        Run the client in full-auto mode.
        """
        if not hasattr(self, 'on_event') or not hasattr(self, 'on_report'):
            raise NotImplementedError("You must implement both the on_event and and_report functions or coroutines.")

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
        :param str report_name: An OpenADR name for this report (one of pyopenadr.enums.REPORT_NAME)
        :param str reading_type: An OpenADR reading type (found in pyopenadr.enums.READING_TYPE)
        :param str report_type: An OpenADR report type (found in pyopenadr.enums.REPORT_TYPE)
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
        request_id = new_request_id()
        service = 'EiRegisterParty'
        message = create_message('oadrQueryRegistration', request_id=request_id)
        response_type, response_payload = await self._perform_request(service, message)
        return response_type, response_payload

    async def create_party_registration(self, http_pull_model=True, xml_signature=False,
                                  report_only=False, profile_name='2.0b',
                                  transport_name='simpleHttp', transport_address=None, ven_id=None):
        request_id = new_request_id()
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
        message = create_message('oadrCreatePartyRegistration', request_id=new_request_id(), **payload)
        response_type, response_payload = await self._perform_request(service, message)
        if response_payload['response']['response_code'] != 200:
            status_code = response_payload['response']['response_code']
            status_description = response_payload['response']['response_description']
            print(f"Got error on Create Party Registration: {status_code} {status_description}")
            return
        self.ven_id = response_payload['ven_id']
        self.poll_frequency = response_payload['requested_oadr_poll_freq']
        print(f"VEN is now registered with ID {self.ven_id}")
        print(f"The polling frequency is {self.poll_frequency}")
        return response_type, response_payload

    async def cancel_party_registration(self):
        raise NotImplementedError("Cancel Registration is not yet implemented")

    async def request_event(self, reply_limit=1):
        """
        Request the next Event from the VTN, if it has any.
        """
        payload = {'request_id': new_request_id(),
                   'ven_id': self.ven_id,
                   'reply_limit': reply_limit}
        message = create_message('oadrRequestEvent', **payload)
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
        message = create_message('oadrCreatedEvent', **payload)
        response_type, response_payload = await self._perform_request(service, message)
        return response_type, response_payload

    async def register_report(self):
        """
        Tell the VTN about our reporting capabilities.
        """
        request_id = generate_id()

        payload = {'request_id': generate_id(),
                   'ven_id': self.ven_id,
                   'reports': self.reports}

        service = 'EiReport'
        message = create_message('oadrRegisterReport', **payload)
        response_type, response_payload = await self._perform_request(service, message)

        # Remember which reports the VTN is interested in

        return response_type, response_payload

    async def created_report(self):
        pass

    async def poll(self):
        service = 'OadrPoll'
        message = create_message('oadrPoll', ven_id=self.ven_id)
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
        message = create_message('oadrUpdateReport', report)
        response_type, response_payload = self._perform_request(service, message)

        # We might get a oadrCancelReport message in this thing:
        if 'cancel_report' in response.payload:
            print("TODO: cancel this report")


    async def _perform_request(self, service, message):
        if self.debug:
            print(f"Sending {message}")
        url = f"{self.vtn_url}/{service}"
        async with self.client_session.post(url, data=message) as req:
            if req.status != HTTPStatus.OK:
                raise Exception(f"Received non-OK status in request: {req.status}")
            content = await req.read()
            if self.debug:
                print(content.decode('utf-8'))
        return parse_message(content)

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

    async def _on_report(self, message):
        result = self.on_report(message)
        if iscoroutine(result):
            result = await result
        return result

    async def _poll(self):
        response_type, response_payload = await self.poll()
        if response_type == 'oadrResponse':
            print("No events or reports available")
            return

        if response_type == 'oadrRequestReregistration':
            result = await self.create_party_registration()

        if response_type == 'oadrDistributeEvent':
            result = await self._on_event(response_payload)

        elif response_type == 'oadrUpdateReport':
            result = await self._on_report(response_payload)

        else:
            print(f"No handler implemented for message type {response_type}, ignoring.")
        await self._poll()

