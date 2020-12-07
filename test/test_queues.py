from openleadr import OpenADRClient, OpenADRServer, enable_default_logging
import pytest
import asyncio
import datetime
from functools import partial

enable_default_logging()

def on_create_party_registration(registration_info):
    print("Registered party")
    return 'ven123', 'reg123'

async def on_event(event):
    return 'optIn'

async def event_callback(ven_id, event_id, opt_type, future):
    future.set_result(opt_type)

@pytest.mark.asyncio
async def test_internal_message_queue():
    loop = asyncio.get_event_loop()
    client = OpenADRClient(ven_name='myven',
                           vtn_url='http://localhost:8080/OpenADR2/Simple/2.0b')
    client.add_handler('on_event', on_event)
    server = OpenADRServer(vtn_id='myvtn', requested_poll_freq=datetime.timedelta(seconds=1))
    server.add_handler('on_create_party_registration', on_create_party_registration)
    event_callback_future = loop.create_future()
    server.add_event(ven_id='ven123',
                     signal_name='simple',
                     signal_type='level',
                     intervals=[{'dtstart': datetime.datetime.now(),
                                 'duration': datetime.timedelta(minutes=5),
                                 'signal_payload': 1}],
                     callback=partial(event_callback, future=event_callback_future))

    await server.run_async()
    await asyncio.sleep(1)
    await client.run()
    await asyncio.sleep(1)
    status = await event_callback_future
    assert status == 'optIn'

    message_type, message_payload = await asyncio.wait_for(client.poll(), 0.5)
    assert message_type == 'oadrResponse'

    message_type, message_payload = await asyncio.wait_for(client.poll(), 0.5)
    assert message_type == 'oadrResponse'

    await client.stop()
    await server.stop()