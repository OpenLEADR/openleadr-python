from openleadr import OpenADRClient, OpenADRServer, objects, utils
from functools import partial
from dataclasses import asdict
from datetime import datetime, timezone, timedelta
import pytest

def on_create_party_registration(registration_info):
    return 'ven123', 'reg123'

def poll_responder(ven_id, message_type, message_payload):
    return message_type, message_payload


event = objects.Event(event_descriptor=objects.EventDescriptor(event_id='event123',
                                                               event_status='far',
                                                               modification_number='1',
                                                               market_context='http://marketcontext01'),
                      event_signals=[objects.EventSignal(signal_name='simple',
                                                         signal_type='level',
                                                         signal_id=utils.generate_id(),
                                                         intervals=[objects.Interval(dtstart=datetime.now(timezone.utc),
                                                                                     duration=timedelta(minutes=10),
                                                                                     signal_payload=1)])],
                      targets=[{'ven_id': 'ven123'}])

poll_responses = [('oadrResponse', {}),
                  ('oadrDistributeEvent', {'events': [asdict(event)]}),
                  ('oadrCreateReport', {'report_requests': [{'report_request_id': 'req123',
                                                            'report_specifier': {'report_specifier_id': 'rsi123',
                                                                                 'granularity': timedelta(seconds=10),
                                                                                 'report_back_duration': timedelta(seconds=10),
                                                                                 'specifier_payloads': [{'r_id': 'rid123',
                                                                                                         'reading_type': 'Direct Read'}]}}]}),
                  ('oadrCancelReport', {'report_request_id': 'report123',
                                        'report_to_follow': False,
                                        'request_id': 'request123'}),
                  ('oadrRegisterReport', {'ven_id': 'ven123', 'reports': []}),
                  ('oadrUpdateReport', {'ven_id': 'ven123'}),
                  ('oadrCancelPartyRegistration', {'registration_id': 'reg123',
                                                   'ven_id': 'ven123'}),
                  ('oadrRequestReregistration', {'ven_id': 'ven123'})]

@pytest.mark.parametrize('message_type,message_payload', poll_responses)
@pytest.mark.asyncio
async def test_message(message_type, message_payload):
    server = OpenADRServer(vtn_id='myvtn')
    server.add_handler('on_create_party_registration', on_create_party_registration)
    server.add_handler('on_poll', partial(poll_responder, message_type=message_type, message_payload=message_payload))
    client = OpenADRClient(ven_name='myven',
                           vtn_url='http://localhost:8080/OpenADR2/Simple/2.0b')
    await server.run_async()
    await client.create_party_registration()
    response_type, response_payload = await client.poll()
    await server.stop()
    assert response_type == message_type
