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
from aiohttp import web
from openleadr.service import EventService, PollService, RegistrationService, ReportService, \
                              OptService, VTNService
from openleadr.messaging import create_message
from openleadr.utils import certificate_fingerprint, generate_id
from openleadr import objects
from functools import partial
from datetime import datetime, timedelta, timezone
import logging
import ssl
logger = logging.getLogger('openleadr')


class OpenADRServer:
    _MAP = {'on_created_event': 'event_service',
            'on_request_event': 'event_service',

            'on_register_report': 'report_service',
            'on_create_report': 'report_service',
            'on_created_report': 'report_service',
            'on_request_report': 'report_service',
            'on_update_report': 'report_service',

            'on_poll': 'poll_service',

            'on_query_registration': 'registration_service',
            'on_create_party_registration': 'registration_service',
            'on_cancel_party_registration': 'registration_service'}

    def __init__(self, vtn_id, cert=None, key=None, passphrase=None, fingerprint_lookup=None,
                 show_fingerprint=True, http_port=8080, http_host='127.0.0.1', http_cert=None,
                 http_key=None, http_key_passphrase=None, http_path_prefix='/OpenADR2/Simple/2.0b',
                 requested_poll_freq=timedelta(seconds=10), http_ca_file=None):
        """
        Create a new OpenADR VTN (Server).

        :param vtn_id string: An identifier string for this VTN. This is how you identify yourself
                              to the VENs that talk to you.
        :param cert string: Path to the PEM-formatted certificate file that is used to sign outgoing
                            messages
        :param key string: Path to the PEM-formatted private key file that is used to sign outgoing
                           messages
        :param passphrase string: The passphrase used to decrypt the private key file
        :param fingerprint_lookup callable: A callable that receives a ven_id and should return the
                                            registered fingerprint for that VEN. You should receive
                                            these fingerprints outside of OpenADR and configure them
                                            manually.
        :param show_fingerprint boolean: Whether to print the fingerprint to your stdout on startup.
                                         Defaults to True.
        :param http_port integer: The port that the web server is exposed on (default: 8080)
        :param http_host str: The host or IP address to bind the server to (default: 127.0.0.1).
        :param http_cert str: The path to the PEM certificate for securing HTTP traffic.
        :param http_key str: The path to the PEM private key for securing HTTP traffic.
        :param http_ca_file str: The path to the CA-file that client certificates are checked against.
        :param http_key_passphrase str: The passphrase for the HTTP private key.
        """
        # Set up the message queues
        self.message_queues = {}

        self.app = web.Application()
        self.services = {'event_service': EventService(vtn_id, message_queues=self.message_queues),
                         'report_service': ReportService(vtn_id, message_queues=self.message_queues),
                         'poll_service': PollService(vtn_id, message_queues=self.message_queues),
                         'opt_service': OptService(vtn_id),
                         'registration_service': RegistrationService(vtn_id,
                                                                     poll_freq=requested_poll_freq)}
        if http_path_prefix[-1] == "/":
            http_path_prefix = http_path_prefix[:-1]
        self.app.add_routes([web.post(f"{http_path_prefix}/{s.__service_name__}", s.handler)
                             for s in self.services.values()])
        self.http_port = http_port
        self.http_host = http_host
        self.http_path_prefix = http_path_prefix

        # Create SSL context for running the server
        if http_cert and http_key:
            self.ssl_context = ssl.create_default_context(cafile=http_ca_file,
                                                          purpose=ssl.Purpose.CLIENT_AUTH)
            self.ssl_context.verify_mode = ssl.CERT_REQUIRED
            self.ssl_context.load_cert_chain(http_cert, http_key, http_key_passphrase)
        else:
            self.ssl_context = None

        # Configure message signing
        if cert and key:
            with open(cert, "rb") as file:
                cert = file.read()
            with open(key, "rb") as file:
                key = file.read()
            if show_fingerprint:
                print("")
                print("*" * 80)
                print("Your VTN Certificate Fingerprint is "
                      f"{certificate_fingerprint(cert)}".center(80))
                print("Please deliver this fingerprint to the VENs that connect to you.".center(80))
                print("You do not need to keep this a secret.".center(80))
                print("*" * 80)
                print("")
        VTNService._create_message = partial(create_message, cert=cert, key=key,
                                             passphrase=passphrase)
        VTNService.fingerprint_lookup = staticmethod(fingerprint_lookup)
        self.__setattr__ = self.add_handler

    def run(self):
        """
        Starts the asyncio-loop and runs the server in it. This function is
        blocking. For other ways to run the server in a more flexible context,
        please refer to the `aiohttp documentation
        <https://docs.aiohttp.org/en/stable/web_advanced.html#aiohttp-web-app-runners>`_.
        """
        web.run_app(self.app)

    async def run_async(self):
        """
        Starts the server in an already-running asyncio loop.
        """
        self.app_runner = web.AppRunner(self.app)
        await self.app_runner.setup()
        site = web.TCPSite(self.app_runner,
                           port=self.http_port,
                           host=self.http_host,
                           ssl_context=self.ssl_context)
        await site.start()
        protocol = 'https' if self.ssl_context else 'http'
        print("")
        print("*" * 80)
        print("Your VTN Server is now running at ".center(80))
        print(f"{protocol}://{self.http_host}:{self.http_port}{self.http_path_prefix}".center(80))
        print("*" * 80)
        print("")

    async def stop(self):
        await self.app_runner.cleanup()

    def add_event(self, ven_id, signal_name, signal_type, intervals, target, callback):
        """
        Convenience method to add an event with a single signal.
        :param str ven_id: The ven_id to whom this event must be delivered.
        :param str signal_name: The OpenADR name of the signal; one of openleadr.objects.SIGNAL_NAME
        :param str signal_type: The OpenADR type of the signal; one of openleadr.objects.SIGNAL_TYPE
        :param str intervals: A list of intervals with a dtstart, duration and payload member.
        :param str callback: A callback function for when your event has been accepted (optIn) or refused (optOut).
        """
        if self.services['event_service'].polling_method == 'external':
            logger.error("You cannot use the add_event method after you assign your own on_poll "
                         "handler. If you use your own on_poll handler, you are responsible for "
                         "delivering events from that handler. If you want to use OpenLEADRs "
                         "message queuing system, you should not assign an on_poll handler. "
                         "Your Event will NOT be added.")
            return
        event_id = generate_id()
        if not isinstance(target, list):
            target = [target]
        event_descriptor = objects.EventDescriptor(event_id=event_id,
                                                   modification_number=0,
                                                   market_context="None",
                                                   event_status="near",
                                                   created_date_time=datetime.now(timezone.utc))
        event_signal = objects.EventSignal(intervals=intervals,
                                           signal_name=signal_name,
                                           signal_type=signal_type,
                                           signal_id=generate_id(),
                                           targets=target)
        event = objects.Event(event_descriptor=event_descriptor,
                              event_signals=[event_signal],
                              targets=target)
        if ven_id not in self.message_queues:
            self.message_queues[ven_id] = asyncio.Queue()
        self.message_queues[ven_id].put_nowait(event)
        self.services['event_service'].pending_events[event_id] = callback

    async def add_raw_event(self, ven_id, event):
        """
        Add a new event to the queue for a specific VEN.
        """
        self.message_queues[ven_id].put(event)

    async def request_report(self):
        """
        Request a report from the client.
        """

    def add_handler(self, name, func):
        """
        Add a handler to the OpenADRServer.

        :param name string: The name for this handler. Should be one of: on_created_event,
                            on_request_event, on_register_report, on_create_report,
                            on_created_report, on_request_report, on_update_report, on_poll,
                            on_query_registration, on_create_party_registration,
                            on_cancel_party_registration.
        :param func coroutine: A coroutine that handles this event. It receives the message, and
                               should return the contents of a response.
        """
        logger.debug(f"Adding handler: {name} {func}")
        if name in self._MAP:
            setattr(self.services[self._MAP[name]], name, func)
            if name == 'on_poll':
                self.services['poll_service'].polling_method = 'external'
                self.services['event_service'].polling_method = 'external'
        else:
            raise NameError(f"Unknown handler {name}. "
                            f"Correct handler names are: {self._MAP.keys()}")
