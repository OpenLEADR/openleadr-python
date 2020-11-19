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

import pytest

from openleadr import OpenADRClient, OpenADRServer, enums
from openleadr.utils import generate_id, datetimeformat, timedeltaformat, booleanformat
from openleadr.messaging import create_message, parse_message
from openleadr.objects import Event, EventDescriptor, ActivePeriod, EventSignal, Interval
from datetime import datetime, timezone, timedelta

import json
import sqlite3
from pprint import pprint
import warnings

VEN_NAME = 'myven'
VTN_ID = "TestVTN"

async def lookup_ven(ven_name=None, ven_id=None):
    """
    Look up a ven by its name or ID
    """
    return {'ven_id': '1234'}

async def on_update_report(report, futures=None):
    if futures:
        futures.pop().set_result(True)
    pass

async def on_register_report(report, futures=None):
    """
    Deal with this report.
    """
    if futures:
        futures.pop().set_result(True)
    granularity = min(*[rd['sampling_rate']['min_period'] for rd in report['report_descriptions']])
    return (on_update_report, granularity, [rd['r_id'] for rd in report['report_descriptions']])

async def on_create_party_registration(ven_name, future=None):
    if future:
        future.set_result(True)
    ven_id = '1234'
    registration_id = 'abcd'
    return ven_id, registration_id

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

@pytest.mark.asyncio
async def test_conformance_021():
    """
    If venID, vtnID, or eventID value is included in the payload, the receiving
    entity MUST validate that the ID value is as expected and generate an error
    if an unexpected value is received.
    Exception: A VEN MUST NOT generate an error upon receipt of a canceled
    event whose eventID is not previously known.
    """
    server = OpenADRServer(vtn_id='TestVTN', http_port=8001)
    server.add_handler('on_create_party_registration', on_create_party_registration)
    server.add_handler('on_poll', _on_poll)
    await server.run_async()

    client = OpenADRClient(ven_name="TestVEN",
                           vtn_url="http://localhost:8001/OpenADR2/Simple/2.0b")
    await client.create_party_registration()
    event = {'event_descriptor':
                {'event_id': generate_id(),
                 'modification_number': 0,
                 'modification_date': datetime.now(),
                 'priority': 0,
                 'market_context': 'MarketContext001',
                 'created_date_time': datetime.now(),
                 'event_status': enums.EVENT_STATUS.FAR,
                 'test_event': False,
                 'vtn_comment': 'No Comment'},
            'active_period':
                {'dtstart': datetime.now() + timedelta(minutes=30),
                 'duration': timedelta(minutes=30)},
            'event_signals':
                [{'intervals': [{'duration': timedelta(minutes=10),
                                 'signal_payload': 1},
                                {'duration': timedelta(minutes=10),
                                 'signal_payload': 2},
                                {'duration': timedelta(minutes=10),
                                 'signal_payload': 3}],
                  'signal_name': enums.SIGNAL_NAME.SIMPLE,
                  'signal_type': enums.SIGNAL_TYPE.DELTA,
                  'signal_id': generate_id(),
                  'current_value': 123
                }],
            'targets': [{'ven_id': '123'}]
        }
    add_event(ven_id=client.ven_id,
              event_id = event['event_descriptor']['event_id'],
              event=event)
    message_type, message_payload = await client.poll()
    assert message_type == 'oadrDistributeEvent'
    await client.stop()
    await server.stop()

