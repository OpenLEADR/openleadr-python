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
from ..enums import STATUS_CODES
from ..messaging import create_message, parse_message, validate_xml_schema, validate_xml_signature, authenticate_message
from ..utils import generate_id, get_cert_fingerprint_from_request, ensure_str, extract_pem_cert, certificate_fingerprint

from dataclasses import is_dataclass, asdict
from lxml import etree

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
        try:
            # Validate the message to the XML Schema
            message_tree = validate_xml_schema(content)

            # Parse the message to a type and payload dict
            message_type, message_payload = parse_message(content)

            # Authenticate the message
            if request.secure and 'ven_id' in message_payload:
                await authenticate_message(request, message_tree, message_payload,
                                           self.fingerprint_lookup)

            # Pass the message off to the handler and get the response type and payload
            response_type, response_payload = await self.handle_message(message_type,
                                                                        message_payload)
            if 'response' not in response_payload:
                response_payload['response'] = {'response_status': 200,
                                                'response_description': 'OK',
                                                'request_id': message_payload['request_id']}
            response_payload['vtn_id'] = self.vtn_id
            if 'ven_id' not in response_payload:
                response_payload['ven_id'] = message_payload.get('ven_id')
        except errors.ProtocolError as err:
            # In case of an OpenADR error, return a valid OpenADR message
            response_type, response_payload = self.error_response(message_type,
                                                                  err.response_status,
                                                                  err.response_description)
            msg = self._create_message(response_type, **response_payload)
            response = web.Response(text=msg,
                                    status=HTTPStatus.OK,
                                    content_type='application/xml')
        except errors.HTTPError as err:
            # If we throw a http-related error, deal with it here
            response = web.Response(text=err.response_description,
                                    status=err.response_status)
        except Exception as err:
            # In case of some other error, return a HTTP 500
            response = web.Response(status=HTTPStatus.INTERNAL_SERVER_ERROR)


        else:
            # We've successfully handled this message
            msg = self._create_message(response_type, **response_payload)
            response = web.Response(text=msg,
                                    status=HTTPStatus.OK,
                                    content_type='application/xml')
        return response

    async def handle_message(self, message_type, message_payload):
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

        else:
            response_type, response_payload = self.error_response(message_type,
                                                                  STATES_CODES.COMPLIANCE_ERROR,
                                                                  "A message of type "
                                                                  f"{message_type} should not be "
                                                                  "sent to this endpoint")
        return response_type, response_payload

    def error_response(self, message_type, error_code, error_description):
        if message_type == 'oadrCreatePartyRegistration':
            response_type = 'oadrCreatedPartyRegistration'
        if message_type == 'oadrRequestEvent':
            response_type = 'oadrDistributeEvent'
        else:
            response_type = 'oadrResponse'
        response_payload = {'response': {'response_code': error_code,
                                         'response_description': 'Certificate fingerprint mismatch'}}
        return response_type, response_payload
