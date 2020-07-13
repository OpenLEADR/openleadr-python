import pytest

from pyopenadr import OpenADRClient, OpenADRServer, enums
from pyopenadr.utils import generate_id, create_message, parse_message
from datetime import datetime, timezone, timedelta

from pprint import pprint
import warnings


@pytest.mark.asyncio
async def test_conformance_009_pass():
    """
    oadrDistributeEvent eiEventSignal’s with a signalName of “SIMPLE” MUST
    use signalPayload values of 0=normal; 1=moderate; 2=high; 3=special.
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

@pytest.mark.asyncio
async def test_conformance_009_raise():
    """
    oadrDistributeEvent eiEventSignal’s with a signalName of “SIMPLE” MUST
    use signalPayload values of 0=normal; 1=moderate; 2=high; 3=special.
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
                 'duration': timedelta(minutes=30)},
            'event_signals':
                [{'intervals': [{'duration': timedelta(minutes=10),
                                 'signal_payload': 10},
                                {'duration': timedelta(minutes=10),
                                 'signal_payload': 20},
                                {'duration': timedelta(minutes=10),
                                 'signal_payload': 30}],
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