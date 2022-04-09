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
import logging
from pprint import pprint

@pytest.mark.asyncio
async def test_conformance_014_warn(caplog):
    """
    If currentValue is included in the payload, it MUST be set to 0 (normal)
    when the event status is not “active” for the SIMPLE signalName.
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
            'targets': {'ven_id': '123'}
        }

    # Create a message with this event
    msg = create_message('oadrDistributeEvent',
                         response={'response_code': 200,
                                   'response_description': 'OK',
                                   'request_id': generate_id()},
                         request_id=generate_id(),
                         vtn_id=generate_id(),
                         events=[event])

    assert ("openleadr", logging.WARNING, "The current_value for a SIMPLE event that is not yet active must be 0. This will be corrected.") in caplog.record_tuples

