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


from pyopenadr.utils import generate_id
from pyopenadr.messaging import create_message, parse_message
from hashlib import sha256
from base64 import b64encode
from datetime import datetime, timedelta, timezone
import os

with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'cert.pem'), 'rb') as file:
    TEST_CERT = file.read()
with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'key.pem'), 'rb') as file:
    TEST_KEY = file.read()
TEST_KEY_PASSWORD = 'openadr'

def test_message_validation():
    msg = create_message('oadrPoll', ven_id='123', cert=TEST_CERT, key=TEST_KEY, passphrase='openadr')
    parsed_type, parsed_message = parse_message(msg, cert=TEST_CERT)
    assert parsed_type == 'oadrPoll'


def test_message_validation_complex():
    now = datetime.now(timezone.utc)
    event_id = generate_id()
    active_period = {"dtstart": now + timedelta(minutes=1),
                     "duration": timedelta(minutes=9)}

    event_descriptor = {"event_id": event_id,
                        "modification_number": 1,
                        "modification_date_time": now,
                        "priority": 1,
                        "market_context": "http://MarketContext1",
                        "created_date_time": now,
                        "event_status": "near",
                        "test_event": "false",
                        "vtn_comment": "This is an event"}

    event_signals = [{"intervals": [{"duration": timedelta(minutes=1), "uid": 1, "signal_payload": 8},
                                    {"duration": timedelta(minutes=1), "uid": 2, "signal_payload": 10},
                                    {"duration": timedelta(minutes=1), "uid": 3, "signal_payload": 12},
                                    {"duration": timedelta(minutes=1), "uid": 4, "signal_payload": 14},
                                    {"duration": timedelta(minutes=1), "uid": 5, "signal_payload": 16},
                                    {"duration": timedelta(minutes=1), "uid": 6, "signal_payload": 18},
                                    {"duration": timedelta(minutes=1), "uid": 7, "signal_payload": 20},
                                    {"duration": timedelta(minutes=1), "uid": 8, "signal_payload": 10},
                                    {"duration": timedelta(minutes=1), "uid": 9, "signal_payload": 20}],
                    "signal_name": "LOAD_CONTROL",
                    #"signal_name": "simple",
                    #"signal_type": "level",
                    "signal_type": "x-loadControlCapacity",
                    "signal_id": generate_id(),
                    "current_value": 9.99}]

    event_targets = [{"ven_id": 'VEN001'}, {"ven_id": 'VEN002'}]
    event = {'active_period': active_period,
             'event_descriptor': event_descriptor,
             'event_signals': event_signals,
             'targets': event_targets,
             'response_required': 'always'}

    msg = create_message('oadrDistributeEvent',
                         request_id=generate_id(),
                         response={'request_id': 123, 'response_code': 200, 'response_description': 'OK'},
                         events=[event],
                         cert=TEST_CERT,
                         key=TEST_KEY,
                         passphrase='openadr')
    parsed_type, parsed_msg = parse_message(msg, cert=TEST_CERT)

if __name__ == "__main__":
    msg = create_message('oadrPoll', ven_id='123', signing_certificate=TEST_CERT, signing_key=TEST_KEY, signing_key_passphrase=b'openadr')
    parsed_type, parsed_message = parse_message(msg)
    validate_message(msg, public_key=TEST_CERT)
    print(msg)