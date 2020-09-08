import pytest

from pyopenadr import OpenADRClient, OpenADRServer, enums
from pyopenadr.utils import generate_id
from pyopenadr.messaging import create_message, parse_message
from pyopenadr.objects import Event, EventDescriptor, ActivePeriod, EventSignal, Interval
from datetime import datetime, timezone, timedelta

from pprint import pprint
import warnings

from test.fixtures.simple_server import start_server, add_event

@pytest.mark.asyncio
async def test_conformance_021(start_server):
    """
    If venID, vtnID, or eventID value is included in the payload, the receiving
    entity MUST validate that the ID value is as expected and generate an error
    if an unexpected value is received.
    Exception: A VEN MUST NOT generate an error upon receipt of a canceled
    event whose eventID is not previously known.
    """

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
                }]
        }
    add_event(ven_id=client.ven_id,
              event_id = event['event_descriptor']['event_id'],
              event=event)
    message_type, message_payload = await client.poll()
    assert message_type == 'oadrDistributeEvent'
