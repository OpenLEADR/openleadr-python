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

from openleadr import OpenADRClient, OpenADRServer, enums
from openleadr.utils import generate_id, certificate_fingerprint
from openleadr.messaging import create_message, parse_message
from datetime import datetime, timezone, timedelta

import asyncio
import sqlite3
import pytest
import pytest_asyncio
from aiohttp import web

import os

SERVER_PORT = 8001
VEN_NAME = 'myven'
VEN_ID = '1234abcd'
VTN_ID = "TestVTN"

CERTFILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'certificates', 'dummy_ven.crt')
KEYFILE =  os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'certificates', 'dummy_ven.key')
CAFILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'certificates', 'dummy_ca.crt')

async def _on_create_party_registration(payload):
    registration_id = generate_id()
    return VEN_ID, registration_id

@pytest_asyncio.fixture
async def start_server():
    server = OpenADRServer(vtn_id=VTN_ID, http_port=SERVER_PORT)
    server.add_handler('on_create_party_registration', _on_create_party_registration)
    await server.run_async()
    yield
    await server.stop()

@pytest_asyncio.fixture
async def start_server_with_signatures():
    server = OpenADRServer(vtn_id=VTN_ID, cert=CERTFILE, key=KEYFILE, fingerprint_lookup=fingerprint_lookup, http_port=SERVER_PORT)
    server.add_handler('on_create_party_registration', _on_create_party_registration)
    await server.run_async()
    yield
    await server.stop()


@pytest.mark.asyncio
async def test_query_party_registration(start_server):
    client = OpenADRClient(ven_name=VEN_NAME,
                           vtn_url=f"http://localhost:{SERVER_PORT}/OpenADR2/Simple/2.0b")

    response_type, response_payload = await client.query_registration()
    assert response_type == 'oadrCreatedPartyRegistration'
    assert response_payload['vtn_id'] == VTN_ID
    await client.stop()

@pytest.mark.asyncio
async def test_create_party_registration(start_server):
    client = OpenADRClient(ven_name=VEN_NAME,
                           vtn_url=f"http://localhost:{SERVER_PORT}/OpenADR2/Simple/2.0b")

    response_type, response_payload = await client.create_party_registration()
    assert response_type == 'oadrCreatedPartyRegistration'
    assert response_payload['ven_id'] == VEN_ID
    await client.stop()

def fingerprint_lookup(ven_id):
    with open(CERTFILE) as file:
        cert = file.read()
    return certificate_fingerprint(cert)

@pytest.mark.asyncio
@pytest.mark.parametrize("disable_signature", [False, True])
async def test_create_party_registration_with_signatures(start_server_with_signatures, disable_signature):
    with open(CERTFILE) as file:
        cert = file.read()
    client = OpenADRClient(ven_name=VEN_NAME,
                           vtn_url=f"http://localhost:{SERVER_PORT}/OpenADR2/Simple/2.0b",
                           cert=CERTFILE, key=KEYFILE, ca_file=CAFILE, vtn_fingerprint=certificate_fingerprint(cert),
                           disable_signature=disable_signature)

    response_type, response_payload = await client.create_party_registration()
    assert response_type == 'oadrCreatedPartyRegistration'
    assert response_payload['ven_id'] == VEN_ID
    await client.stop()
