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

from pyopenadr import OpenADRClient, OpenADRServer, enums
from pyopenadr.utils import generate_id
from pyopenadr.messaging import create_message, parse_message
from datetime import datetime, timezone, timedelta

import asyncio
import sqlite3
import pytest
from aiohttp import web

SERVER_PORT = 8001
VEN_NAME = 'myven'
VEN_ID = '1234abcd'
VTN_ID = "TestVTN"


async def _on_create_party_registration(payload):
    registration_id = generate_id()
    payload = {'response': {'response_code': 200,
                            'response_description': 'OK',
                            'request_id': payload['request_id']},
               'ven_id': VEN_ID,
               'registration_id': registration_id,
               'profiles': [{'profile_name': '2.0b',
                             'transports': {'transport_name': 'simpleHttp'}}],
               'requested_oadr_poll_freq': timedelta(seconds=10)}
    return 'oadrCreatedPartyRegistration', payload

@pytest.fixture
async def start_server():
    server = OpenADRServer(vtn_id=VTN_ID)
    server.add_handler('on_create_party_registration', _on_create_party_registration)

    runner = web.AppRunner(server.app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', SERVER_PORT)
    await site.start()
    yield
    await runner.cleanup()


@pytest.mark.asyncio
async def test_query_party_registration(start_server):
    client = OpenADRClient(ven_name=VEN_NAME,
                           vtn_url=f"http://localhost:{SERVER_PORT}/OpenADR2/Simple/2.0b")

    response_type, response_payload = await client.query_registration()
    assert response_type == 'oadrCreatedPartyRegistration'
    assert response_payload['vtn_id'] == VTN_ID

@pytest.mark.asyncio
async def test_create_party_registration(start_server):
    client = OpenADRClient(ven_name=VEN_NAME,
                           vtn_url=f"http://localhost:{SERVER_PORT}/OpenADR2/Simple/2.0b")

    response_type, response_payload = await client.create_party_registration()
    assert response_type == 'oadrCreatedPartyRegistration'
    assert response_payload['ven_id'] == VEN_ID


