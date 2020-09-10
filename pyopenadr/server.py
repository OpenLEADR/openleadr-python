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

from aiohttp import web
from pyopenadr.service import EventService, PollService, RegistrationService, ReportService, OptService, VTNService
from pyopenadr.messaging import create_message, parse_message
from functools import partial

class OpenADRServer:
    _MAP = {'on_created_event': EventService,
           'on_request_event': EventService,

           'on_register_report': ReportService,
           'on_create_report': ReportService,
           'on_created_report': ReportService,
           'on_request_report': ReportService,
           'on_update_report': ReportService,

           'on_poll': PollService,

           'on_query_registration': RegistrationService,
           'on_create_party_registration': RegistrationService,
           'on_cancel_party_registration': RegistrationService}

    def __init__(self, vtn_id, cert=None, key=None, passphrase=None, verification_cert=None):
        self.app = web.Application()
        self.services = {'event_service': EventService(vtn_id),
                         'report_service': ReportService(vtn_id),
                         'poll_service': PollService(vtn_id),
                         'opt_service': OptService(vtn_id),
                         'registration_service': RegistrationService(vtn_id)}
        self.app.add_routes([web.post(f"/OpenADR2/Simple/2.0b/{s.__service_name__}", s.handler) for s in self.services.values()])

        # Configure message signing
        if cert and key:
            with open(cert, "rb") as file:
                cert = file.read()
            with open(key, "rb") as file:
                key = file.read()
        if verification_cert:
            with open(verification_cert, "rb") as file:
                verification_cert = file.read()
        VTNService._create_message = partial(create_message, cert=cert, key=key, passphrase=passphrase)
        VTNService._parse_message = partial(parse_message, cert=verification_cert)

        self.__setattr__ = self.add_handler

    def run(self):
        """
        Starts the asyncio-loop and runs the server in it. This function is
        blocking. For other ways to run the server in a more flexible context,
        please refer to the `aiohttp documentation
        <https://docs.aiohttp.org/en/stable/web_advanced.html#aiohttp-web-app-runners>`_.
        """
        web.run_app(self.app)

    def add_handler(self, name, func):
        """
        Add a handler to the OpenADRServer.
        """
        print("Called add_handler", name, func)
        if name in self._MAP:
            setattr(self._MAP[name], name, staticmethod(func))
        else:
            raise NameError(f"Unknown handler {name}. Correct handler names are: {self._MAP.keys()}")
