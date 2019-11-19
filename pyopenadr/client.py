#!/Users/stan/Development/ElaadNL/pyopenadr/.python/bin/python3

import xmltodict
import random
import requests
from jinja2 import Environment, PackageLoader, select_autoescape
from pyopenadr.utils import parse_message, create_message, new_request_id, peek
from http import HTTPStatus
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
from asyncio import iscoroutine

class OpenADRClient:
    def __init__(self, ven_name, vtn_url, debug=False):
        self.ven_name = ven_name
        self.vtn_url = vtn_url
        self.ven_id = None
        self.poll_frequency = None
        self.debug = debug

    def run(self):
        """
        Run the client in full-auto mode.
        """
        if not hasattr(self, 'on_event') or not hasattr(self, 'on_report'):
            raise NotImplementedError("You must implement both the on_event and and_report functions or coroutines.")

        self.create_party_registration()

        if not self.ven_id:
            print("No VEN ID received from the VTN, aborting registration.")
            return

        # Set up automatic polling
        self.scheduler = AsyncIOScheduler()
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


    def query_registration(self):
        """
        Request information about the VTN.
        """
        request_id = new_request_id()
        service = 'EiRegisterParty'
        message = create_message('oadrQueryRegistration', request_id=request_id)
        response_type, response_payload = self._perform_request(service, message)
        return response_type, response_payload

    def create_party_registration(self, http_pull_model=True, xml_signature=False,
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
        response_type, response_payload = self._perform_request(service, message)
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

    def cancel_party_registration(self):
        raise NotImplementedError("Cancel Registration is not yet implemented")

    def request_event(self, reply_limit=1):
        """
        Request the next Event from the VTN, if it has any.
        """
        payload = {'request_id': new_request_id(),
                   'ven_id': self.ven_id,
                   'reply_limit': reply_limit}
        message = create_message('oadrRequestEvent', **payload)
        service = 'EiEvent'
        response_type, response_payload = self._perform_request(service, message)
        return response_type, response_payload


    def created_event(self, request_id, event_id, opt_type, modification_number=1):
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
        response_type, response_payload = self._perform_request(service, message)
        return response_type, response_payload

    def register_report(self):
        """
        Tell the VTN about our reporting capabilities.
        """
        raise NotImplementedError("Reporting is not yet implemented")

    def poll(self):
        service = 'OadrPoll'
        message = create_message('oadrPoll', ven_id=self.ven_id)
        response_type, response_payload = self._perform_request(service, message)
        return response_type, response_payload

    def _perform_request(self, service, message):
        if self.debug:
            print(f"Sending {message}")
        url = f"{self.vtn_url}/{service}"
        r = requests.post(url,
                          data=message)
        if r.status_code != HTTPStatus.OK:
            raise Exception(f"Received non-OK status in request: {r.status_code}")
        if self.debug:
            print(r.content.decode('utf-8'))
        return parse_message(r.content)

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
        self.created_event(request_id, event_id, result)
        return

    async def _on_report(self, message):
        result = self.on_report(message)
        if iscoroutine(result):
            result = await result
        return result

    async def _poll(self):
        response_type, response_payload = self.poll()
        if response_type == 'oadrResponse':
            print("No events or reports available")
            return

        if response_type == 'oadrRequestReregistration':
            result = self.create_party_registration()

        if response_type == 'oadrDistributeEvent':
            result = await self._on_event(response_payload)

        elif response_type == 'oadrUpdateReport':
            result = await self._on_report(response_payload)

        else:
            print(f"No handler implemented for message type {response_type}, ignoring.")
        await self._poll()

