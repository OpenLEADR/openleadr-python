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
from openleadr.utils import generate_id, normalize_dict, timedeltaformat, datetimeformat, booleanformat
from openleadr.messaging import create_message, parse_message
from datetime import datetime, timezone, timedelta

import asyncio
import sqlite3
import pytest
import pytest_asyncio
from aiohttp import web
import json

SERVER_PORT = 8001
VEN_NAME = 'myven'
VTN_ID = "TestVTN"

class EventFormatter(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, timedelta):
            return timedeltaformat(obj)
        if isinstance(obj, datetime):
            return datetimeformat(obj)
        if isinstance(obj, bool):
            return booleanformat(obj)
        return json.JSONEncoder.default(self, obj)

DB = sqlite3.connect(":memory:")
with DB:
    DB.execute("CREATE TABLE vens (ven_id STRING, ven_name STRING, online BOOLEAN, last_seen DATETIME, registration_id STRING)")
    DB.execute("CREATE TABLE events (event_id STRING, ven_id STRING, request_id STRING, status STRING, event JSON, created_at DATETIME, updated_at DATETIME)")

def lookup_ven(ven_name):
    with DB:
        DB.execute("SELECT * FROM vens WHERE ven_name = ?", (ven_name,))
        ven = DB.fetchone()
    return ven

def add_ven(ven_name, ven_id, registration_id):
    with DB:
        DB.execute("""INSERT INTO vens (ven_id, ven_name, online, last_seen, registration_id)
                           VALUES (?, ?, ?, ?, ?)""", (ven_id, ven_name, True, datetime.now().replace(microsecond=0), registration_id))

def add_event(ven_id, event_id, event):
    serialized_event = json.dumps(event, cls=EventFormatter)
    with DB:
        DB.execute("""INSERT INTO events (ven_id, event_id, request_id, status, event)
                           VALUES (?, ?, ?, ?, ?)""", (ven_id, event_id, None, 'new', serialized_event))

async def _on_poll(ven_id, request_id=None):
    cur = DB.cursor()
    cur.execute("""SELECT event_id, event FROM events WHERE ven_id = ? AND status = 'new' LIMIT 1""", (ven_id,))
    result = cur.fetchone()
    if result:
        event_id, event = result
        event_request_id = generate_id()
        with DB:
            DB.execute("""UPDATE events SET request_id = ? WHERE event_id = ?""", (event_request_id, event_id))
        response_type = 'oadrDistributeEvent'
        response_payload = {'response': {'request_id': request_id,
                                         'response_code': 200,
                                         'response_description': 'OK'},
                            'request_id': event_request_id,
                            'vtn_id': VTN_ID,
                            'events': [json.loads(event)]}
    else:
        response_type = 'oadrResponse'
        response_payload = {'response': {'request_id': request_id,
                                         'response_code': 200,
                                         'response_description': 'OK'},
                            'ven_id': ven_id}
    return response_type, response_payload

async def _on_create_party_registration(payload):
    registration_id = generate_id()
    ven_id = generate_id()
    add_ven(payload['ven_name'], ven_id, registration_id)
    payload = {'response': {'response_code': 200,
                            'response_description': 'OK',
                            'request_id': payload['request_id']},
               'ven_id': ven_id,
               'registration_id': registration_id,
               'profiles': [{'profile_name': '2.0b',
                             'transports': {'transport_name': 'simpleHttp'}}],
               'requested_oadr_poll_freq': timedelta(seconds=10)}
    return 'oadrCreatedPartyRegistration', payload


server = OpenADRServer(vtn_id=VTN_ID, http_port=SERVER_PORT)
server.add_handler('on_create_party_registration', _on_create_party_registration)
server.add_handler('on_poll', _on_poll)

@pytest_asyncio.fixture
async def start_server():
    await server.run_async()
    yield
    await server.stop()
