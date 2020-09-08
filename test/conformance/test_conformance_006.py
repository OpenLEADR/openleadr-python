import pytest

from pyopenadr import OpenADRClient, OpenADRServer, enums
from pyopenadr.utils import generate_id
from pyopenadr.messaging import create_message, parse_message
from datetime import datetime, timezone, timedelta

from pprint import pprint


@pytest.mark.asyncio
async def test_conformance_006():
    """
    The presence of any string except “false” in the oadrDistributeEvent
    testEvent element MUST be treated as a trigger for a test event.
    """

    # Monkey patch our own formatter to prevent an error being raised
    from pyopenadr.messaging import TEMPLATES
    def booleanformat_monkey(value):
        """
        Format a boolean value
        """
        if isinstance(value, bool):
            if value == True:
                return "true"
            elif value == False:
                return "false"
        else:
            return value

    booleanformat_original = TEMPLATES.filters['booleanformat']
    TEMPLATES.filters['booleanformat'] = booleanformat_monkey

    event_id = generate_id()
    event = {'event_descriptor':
                {'event_id': event_id,
                 'modification_number': 0,
                 'modification_date': datetime.now(),
                 'priority': 0,
                 'market_context': 'MarketContext001',
                 'created_date_time': datetime.now(),
                 'event_status': enums.EVENT_STATUS.FAR,
                 'test_event': "HelloThere",
                 'vtn_comment': 'No Comment'},
            'active_period':
                {'dtstart': datetime.now(),
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
                  'signal_id': generate_id()
                }]
        }

    # Create a message with this event
    msg = create_message('oadrDistributeEvent',
                         response={'response_code': 200,
                                   'response_description': 'OK',
                                   'request_id': generate_id()},
                         request_id=generate_id(),
                         vtn_id=generate_id(),
                         events=[event])

    parsed_type, parsed_message = parse_message(msg)
    assert parsed_type == 'oadrDistributeEvent'
    assert parsed_message['events'][0]['event_descriptor']['test_event'] == True

    # Restore the original booleanformat function
    TEMPLATES.filters['booleanformat'] = booleanformat_original
