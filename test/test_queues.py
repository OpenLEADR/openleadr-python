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

async def on_event_opt_in(event, future):
    if future.done() is False:
        future.set_result(event)
    return 'optIn'

async def on_update_event(event, futures):
    for future in futures:
        if future.done() is False:
            future.set_result(event)
            break
    return 'optIn'

async def on_event_opt_out(event, futures):
    for future in futures:
        if future.done() is False:
            future.set_result(event)
            break
    return 'optOut'

async def event_callback(ven_id, event_id, opt_type, future):
    if future.done() is False:
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
                     intervals=[{'dtstart': datetime.datetime.now(datetime.timezone.utc),
                                 'duration': datetime.timedelta(seconds=3),
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

    await asyncio.sleep(1)  # Wait for the event to be completed
    await client.stop()
    await server.stop()


@pytest.mark.asyncio
async def test_event_status_opt_in():
    loop = asyncio.get_event_loop()
    client = OpenADRClient(ven_name='myven',
                           vtn_url='http://localhost:8080/OpenADR2/Simple/2.0b')
    distribute_event_future = loop.create_future()
    event_update_futures = [loop.create_future() for i in range(2)]
    client.add_handler('on_event', partial(on_event_opt_in, future=distribute_event_future))
    client.add_handler('on_update_event', partial(on_update_event, futures=event_update_futures))

    server = OpenADRServer(vtn_id='myvtn', requested_poll_freq=datetime.timedelta(seconds=1))
    server.add_handler('on_create_party_registration', on_create_party_registration)

    event_callback_future = loop.create_future()
    event_id = server.add_event(ven_id='ven123',
                                signal_name='simple',
                                signal_type='level',
                                intervals=[{'dtstart': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=2),
                                            'duration': datetime.timedelta(seconds=2),
                                            'signal_payload': 1}],
                                callback=partial(event_callback, future=event_callback_future))

    assert server.services['event_service'].pending_events[event_id][0].event_descriptor.event_status == 'far'
    await server.run_async()
    await asyncio.sleep(0.5)
    await client.run()

    await event_callback_future

    print("Waiting for event future 1")
    result = await distribute_event_future
    assert result['event_descriptor']['event_status'] == 'far'
    assert len(client.responded_events) == 1

    print("Watiting for event future 2")
    result = await event_update_futures[0]
    assert result['event_descriptor']['event_status'] == 'active'
    assert len(client.responded_events) == 1

    print("Watiting for event future 3")
    result = await event_update_futures[1]
    assert result['event_descriptor']['event_status'] == 'completed'
    assert len(client.responded_events) == 0

    await client.stop()
    await server.stop()
    await asyncio.sleep(0)

@pytest.mark.asyncio
async def test_event_status_opt_in_with_ramp_up():
    loop = asyncio.get_event_loop()
    client = OpenADRClient(ven_name='myven',
                           vtn_url='http://localhost:8080/OpenADR2/Simple/2.0b')
    distribute_event_future = loop.create_future()
    event_update_futures = [loop.create_future() for i in range(3)]
    client.add_handler('on_event', partial(on_event_opt_in, future=distribute_event_future))
    client.add_handler('on_update_event', partial(on_update_event, futures=event_update_futures))

    server = OpenADRServer(vtn_id='myvtn', requested_poll_freq=datetime.timedelta(seconds=1))
    server.add_handler('on_create_party_registration', on_create_party_registration)

    event_callback_future = loop.create_future()
    event_id = server.add_event(ven_id='ven123',
                                signal_name='simple',
                                signal_type='level',
                                intervals=[{'dtstart': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=4),
                                            'duration': datetime.timedelta(seconds=2),
                                            'signal_payload': 1}],
                                ramp_up_period=datetime.timedelta(seconds=2),
                                callback=partial(event_callback, future=event_callback_future))

    assert server.services['event_service'].pending_events[event_id][0].event_descriptor.event_status == 'far'
    await server.run_async()
    await asyncio.sleep(0.5)
    await client.run()

    await event_callback_future

    print("Waiting for event future 1")
    result = await distribute_event_future
    assert result['event_descriptor']['event_status'] == 'far'

    print("Watiting for event future 2")
    result = await event_update_futures[0]
    assert result['event_descriptor']['event_status'] == 'near'

    print("Watiting for event future 3")
    result = await event_update_futures[1]
    assert result['event_descriptor']['event_status'] == 'active'

    print("Watiting for event future 4")
    result = await event_update_futures[2]
    assert result['event_descriptor']['event_status'] == 'completed'
    await asyncio.sleep(0.5)

    await client.stop()
    await server.stop()
    await asyncio.sleep(1)
