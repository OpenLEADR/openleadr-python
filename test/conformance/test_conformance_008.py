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
from openleadr.utils import generate_id
from openleadr.messaging import create_message, parse_message
from datetime import datetime, timezone, timedelta

from pprint import pprint
import logging


@pytest.mark.asyncio
async def test_conformance_008_autocorrect(caplog):
    """
    oadrDistributeEvent eventSignal interval durations for a given event MUST
    add up to eiEvent eiActivePeriod duration.
    """
    event_id = generate_id()
    event = {'event_descriptor':
                {'event_id': event_id,
                 'modification_number': 0,
                 'modification_date': datetime.now(),
                 'priority': 0,
                 'market_context': 'MarketContext001',
                 'created_date_time': datetime.now(),
                 'event_status': enums.EVENT_STATUS.FAR,
                 'test_event': False,
                 'vtn_comment': 'No Comment'},
            'active_period':
                {'dtstart': datetime.now(),
                 'duration': timedelta(minutes=5)},
            'event_signals':
                [{'intervals': [{'duration': timedelta(minutes=10),
                                 'signal_payload': 1},
                                {'duration': timedelta(minutes=10),
                                 'signal_payload': 2},
                                {'duration': timedelta(minutes=10),
                                 'signal_payload': 3}],
                  'signal_name': enums.SIGNAL_NAME.SIMPLE,
                  'signal_type': enums.SIGNAL_TYPE.DELTA,
                  'signal_id': generate_id()
                }],
            'targets': [{'ven_id': '123'}]
        }

    # Create a message with this event
    msg = create_message('oadrDistributeEvent',
                         response={'response_code': 200,
                                   'response_description': 'OK',
                                   'request_id': generate_id()},
                         request_id=generate_id(),
                         vtn_id=generate_id(),
                         events=[event])

    assert ("openleadr", logging.WARNING, f"The active_period duration for event {event_id} (0:05:00) differs from the sum of the interval's durations (0:30:00). The active_period duration has been adjusted to (0:30:00).") in caplog.record_tuples

    parsed_type, parsed_msg = parse_message(msg)
    assert parsed_type == 'oadrDistributeEvent'
    total_time = sum([i['duration'] for i in parsed_msg['events'][0]['event_signals'][0]['intervals']],
                     timedelta(seconds=0))
    assert parsed_msg['events'][0]['active_period']['duration'] == total_time

@pytest.mark.asyncio
async def test_conformance_008_raise():
    """
    oadrDistributeEvent eventSignal interval durations for a given event MUST
    add up to eiEvent eiActivePeriod duration.
    """
    event_id = generate_id()
    event = {'event_descriptor':
                {'event_id': event_id,
                 'modification_number': 0,
                 'modification_date': datetime.now(),
                 'priority': 0,
                 'market_context': 'MarketContext001',
                 'created_date_time': datetime.now(),
                 'event_status': enums.EVENT_STATUS.FAR,
                 'test_event': False,
                 'vtn_comment': 'No Comment'},
            'active_period':
                {'dtstart': datetime.now(),
                 'duration': timedelta(minutes=5)},
            'event_signals':
                [{'intervals': [{'duration': timedelta(minutes=10),
                                 'signal_payload': 1},
                                {'duration': timedelta(minutes=10),
                                 'signal_payload': 2},
                                {'duration': timedelta(minutes=10),
                                 'signal_payload': 3}],
                  'signal_name': enums.SIGNAL_NAME.SIMPLE,
                  'signal_type': enums.SIGNAL_TYPE.DELTA,
                  'signal_id': generate_id()
                },
                {'intervals': [{'duration': timedelta(minutes=1),
                                 'signal_payload': 1},
                                {'duration': timedelta(minutes=2),
                                 'signal_payload': 2},
                                {'duration': timedelta(minutes=2),
                                 'signal_payload': 3}],
                  'signal_name': enums.SIGNAL_NAME.SIMPLE,
                  'signal_type': enums.SIGNAL_TYPE.DELTA,
                  'signal_id': generate_id()
                }]
        }

    with pytest.raises(ValueError):
        msg = create_message('oadrDistributeEvent',
                             response={'response_code': 200,
                                       'response_description': 'OK',
                                       'request_id': generate_id()},
                             request_id=generate_id(),
                             vtn_id=generate_id(),
                             events=[event])