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

from asyncio import iscoroutine
from http import HTTPStatus
import os
import logging

from aiohttp import web
from jinja2 import Environment, PackageLoader, select_autoescape

from .. import errors
from ..messaging import create_message, parse_message
from ..utils import generate_id

from dataclasses import is_dataclass, asdict

logger = logging.getLogger('openleadr')


class VTNService:
    def __init__(self, vtn_id):
        self.vtn_id = vtn_id
        self.handlers = {}
        for method in [getattr(self, attr) for attr in dir(self) if callable(getattr(self, attr))]:
            if hasattr(method, '__message_type__'):
                self.handlers[method.__message_type__] = method

    async def handler(self, request):
        """
        Handle all incoming POST requests.
        """
        content = await request.read()
        message_type, message_payload = self._parse_message(content)

        if message_type in self.handlers:
            handler = self.handlers[message_type]
            result = handler(message_payload)
            if iscoroutine(result):
                result = await result
            if result is not None:
                response_type, response_payload = result
                if is_dataclass(response_payload):
                    response_payload = asdict(response_payload)
            else:
                response_type, response_payload = 'oadrResponse', {}

            response_payload['vtn_id'] = self.vtn_id
            if 'ven_id' in message_payload:
                response_payload['ven_id'] = message_payload['ven_id']

            response_payload['response'] = {'request_id': message_payload.get('request_id', None),
                                            'response_code': 200,
                                            'response_description': 'OK'}
            response_payload['request_id'] = generate_id()

            # Create the XML response
            msg = self._create_message(response_type, **response_payload)
            logger.debug(f"Server is sending {msg}")
            response = web.Response(text=msg,
                                    status=HTTPStatus.OK,
                                    content_type='application/xml')

        else:
            msg = self._create_message('oadrResponse',
                                       ven_id=message_payload.get('ven_id'),
                                       status_code=errorcodes.COMPLIANCE_ERROR,
                                       status_description=f"A message of type {message_type} "
                                       "should not be sent to this endpoint")
            logger.debug(f"Server is sending {msg}")
            response = web.Response(
                text=msg,
                status=HTTPStatus.BAD_REQUEST,
                content_type='application/xml')
        logger.info(f"Sending {response_type} to ven_id {response_payload.get('ven_id')}")
        return response
