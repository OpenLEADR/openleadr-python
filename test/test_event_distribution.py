from openleadr import OpenADRClient, OpenADRServer, enable_default_logging, objects, utils
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

async def on_event_opt_in(event, future=None):
    if future and future.done() is False:
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
    #await asyncio.sleep(1)
    await client.run()
    #await asyncio.sleep(1)
    status = await event_callback_future
    assert status == 'optIn'

    message_type, message_payload = await asyncio.wait_for(client.poll(), 0.5)
    assert message_type == 'oadrResponse'

    message_type, message_payload = await asyncio.wait_for(client.poll(), 0.5)
    assert message_type == 'oadrResponse'

    #await asyncio.sleep(1)  # Wait for the event to be completed
    await client.stop()
    await server.stop()

@pytest.mark.asyncio
async def test_request_event():
    loop = asyncio.get_event_loop()
    client = OpenADRClient(ven_name='myven',
                           vtn_url='http://localhost:8080/OpenADR2/Simple/2.0b')

    server = OpenADRServer(vtn_id='myvtn', requested_poll_freq=datetime.timedelta(seconds=1))
    server.add_handler('on_create_party_registration', on_create_party_registration)

    event_id = server.add_event(ven_id='ven123',
                                signal_name='simple',
                                signal_type='level',
                                intervals=[{'dtstart': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=4),
                                            'duration': datetime.timedelta(seconds=2),
                                            'signal_payload': 1}],
                                ramp_up_period=datetime.timedelta(seconds=2),
                                callback=partial(event_callback))

    assert server.events['ven123'][0].event_descriptor.event_status == 'far'
    await server.run_async()
    await client.create_party_registration()
    message_type, message_payload = await client.request_event()
    assert message_type == 'oadrDistributeEvent'
    message_type, message_payload = await client.request_event()
    assert message_type == 'oadrDistributeEvent'
    await client.stop()
    await server.stop()


@pytest.mark.asyncio
async def test_raw_event():
    now = datetime.datetime.now(datetime.timezone.utc)
    server = OpenADRServer(vtn_id='myvtn')
    server.add_handler('on_create_party_registration', on_create_party_registration)
    event = objects.Event(event_descriptor=objects.EventDescriptor(event_id='event001',
                                                                   modification_number=0,
                                                                   event_status='far',
                                                                   market_context='http://marketcontext01'),
                          event_signals=[objects.EventSignal(signal_id='signal001',
                                                             signal_type='level',
                                                             signal_name='simple',
                                                             intervals=[objects.Interval(dtstart=now,
                                                                                         duration=datetime.timedelta(minutes=10),
                                                                                         signal_payload=1)]),
                                        objects.EventSignal(signal_id='signal002',
                                                            signal_type='price',
                                                            signal_name='ELECTRICITY_PRICE',
                                                            intervals=[objects.Interval(dtstart=now,
                                                                                        duration=datetime.timedelta(minutes=10),
                                                                                        signal_payload=1)])],
                          targets=[objects.Target(ven_id='ven123')])
    loop = asyncio.get_event_loop()
    event_callback_future = loop.create_future()
    server.add_raw_event(ven_id='ven123', event=event, callback=partial(event_callback, future=event_callback_future))

    on_event_future = loop.create_future()
    client = OpenADRClient(ven_name='myven',
                           vtn_url='http://localhost:8080/OpenADR2/Simple/2.0b')
    client.add_handler('on_event', partial(on_event_opt_in, future=on_event_future))

    await server.run_async()
    await client.run()
    event = await on_event_future
    assert len(event['event_signals']) == 2

    result = await event_callback_future
    assert result == 'optIn'

    await client.stop()
    await server.stop()


@pytest.mark.asyncio
async def test_create_event_with_future_as_callback():
    now = datetime.datetime.now(datetime.timezone.utc)
    server = OpenADRServer(vtn_id='myvtn')
    server.add_handler('on_create_party_registration', on_create_party_registration)
    event = objects.Event(event_descriptor=objects.EventDescriptor(event_id='event001',
                                                                   modification_number=0,
                                                                   event_status='far',
                                                                   market_context='http://marketcontext01'),
                          event_signals=[objects.EventSignal(signal_id='signal001',
                                                             signal_type='level',
                                                             signal_name='simple',
                                                             intervals=[objects.Interval(dtstart=now,
                                                                                         duration=datetime.timedelta(minutes=10),
                                                                                         signal_payload=1)]),
                                        objects.EventSignal(signal_id='signal002',
                                                            signal_type='price',
                                                            signal_name='ELECTRICITY_PRICE',
                                                            intervals=[objects.Interval(dtstart=now,
                                                                                        duration=datetime.timedelta(minutes=10),
                                                                                        signal_payload=1)])],
                          targets=[objects.Target(ven_id='ven123')])
    loop = asyncio.get_event_loop()
    event_callback_future = loop.create_future()
    server.add_raw_event(ven_id='ven123', event=event, callback=event_callback_future)

    on_event_future = loop.create_future()
    client = OpenADRClient(ven_name='myven',
                           vtn_url='http://localhost:8080/OpenADR2/Simple/2.0b')
    client.add_handler('on_event', partial(on_event_opt_in, future=on_event_future))

    await server.run_async()
    await client.run()
    event = await on_event_future
    assert len(event['event_signals']) == 2

    result = await event_callback_future
    assert result == 'optIn'
    await client.stop()
    await server.stop()

@pytest.mark.asyncio
async def test_multiple_events_in_queue():
    now = datetime.datetime.now(datetime.timezone.utc)
    server = OpenADRServer(vtn_id='myvtn')
    server.add_handler('on_create_party_registration', on_create_party_registration)

    loop = asyncio.get_event_loop()
    event_1_callback_future = loop.create_future()
    event_2_callback_future = loop.create_future()
    server.add_event(ven_id='ven123',
                     signal_name='simple',
                     signal_type='level',
                     intervals=[objects.Interval(dtstart=now,
                                                 duration=datetime.timedelta(seconds=1),
                                                 signal_payload=1)],
                     callback=event_1_callback_future)

    await server.run()

    on_event_future = loop.create_future()
    client = OpenADRClient(ven_name='ven123',
                           vtn_url='http://localhost:8080/OpenADR2/Simple/2.0b')
    await client.create_party_registration()
    response_type, response_payload = await client.request_event()
    assert response_type == 'oadrDistributeEvent'
    events = response_payload['events']
    assert len(events) == 1
    event_id = events[0]['event_descriptor']['event_id']
    request_id = response_payload['request_id']
    await client.created_event(request_id=request_id,
                               event_id=event_id,
                               opt_type='optIn',
                               modification_number=0)

    server.add_event(ven_id='ven123',
                     signal_name='simple',
                     signal_type='level',
                     intervals=[objects.Interval(dtstart=now + datetime.timedelta(seconds=1),
                                                 duration=datetime.timedelta(seconds=1),
                                                 signal_payload=1)],
                     callback=event_2_callback_future)
    response_type, response_payload = await client.request_event()
    assert response_type == 'oadrDistributeEvent'
    events = response_payload['events']

    # Assert that we still have two events in the response
    assert len(events) == 2

    # Wait one second and retrieve the events again
    await asyncio.sleep(1)
    response_type, response_payload = await client.request_event()
    assert response_type == 'oadrDistributeEvent'
    events = response_payload['events']
    assert len(events) == 2
    assert events[1]['event_descriptor']['event_status'] == 'completed'

    response_type, response_payload = await client.request_event()
    assert response_type == 'oadrDistributeEvent'
    events = response_payload['events']
    assert len(events) == 1
    await asyncio.sleep(1)

    response_type, response_payload = await client.request_event()
    assert response_type == 'oadrDistributeEvent'

    response_type, response_payload = await client.request_event()
    assert response_type == 'oadrResponse'

    await server.stop()

@pytest.mark.asyncio
async def test_client_event_cleanup():
    now = datetime.datetime.now(datetime.timezone.utc)
    server = OpenADRServer(vtn_id='myvtn')
    server.add_handler('on_create_party_registration', on_create_party_registration)

    loop = asyncio.get_event_loop()
    event_1_callback_future = loop.create_future()
    event_2_callback_future = loop.create_future()
    server.add_event(ven_id='ven123',
                     signal_name='simple',
                     signal_type='level',
                     intervals=[objects.Interval(dtstart=now,
                                                 duration=datetime.timedelta(seconds=1),
                                                 signal_payload=1)],
                     callback=event_1_callback_future)
    await server.run()

    client = OpenADRClient(ven_name='ven123',
                           vtn_url='http://localhost:8080/OpenADR2/Simple/2.0b')
    client.add_handler('on_event', on_event_opt_in)
    await client.run()
    await asyncio.sleep(0.5)
    assert len(client.received_events) == 1

    await asyncio.sleep(0.5)
    await client._event_cleanup()
    assert len(client.received_events) == 0

    await server.stop()
    await client.stop()


@pytest.mark.asyncio
async def test_cancel_event():
    async def opt_in_to_event(event, future=None):
        if future:
            future.set_result(True)
        return 'optIn'

    async def on_update_event(event, future=None):
        if future:
            future.set_result(event)
        return 'optIn'

    now = datetime.datetime.now(datetime.timezone.utc)
    server = OpenADRServer(vtn_id='myvtn', requested_poll_freq=datetime.timedelta(seconds=1))
    server.add_handler('on_create_party_registration', on_create_party_registration)

    loop = asyncio.get_event_loop()
    event_1_callback_future = loop.create_future()
    event_id = server.add_event(ven_id='ven123',
                                signal_name='simple',
                                signal_type='level',
                                intervals=[objects.Interval(dtstart=now,
                                                            duration=datetime.timedelta(seconds=60),
                                                            signal_payload=1)],
                                callback=event_1_callback_future,
                                response_required='always')
    await server.run()

    client = OpenADRClient(ven_name='ven123',
                           vtn_url='http://localhost:8080/OpenADR2/Simple/2.0b')
    client.add_handler('on_event', opt_in_to_event)
    cancel_future = loop.create_future()
    client.add_handler('on_update_event', partial(on_update_event, future=cancel_future))
    await client.run()
    await event_1_callback_future
    server.cancel_event('ven123', event_id)

    result = await cancel_future
    assert utils.getmember(result, 'event_descriptor.event_status') == 'cancelled'

    response_type, response_payload = await client.request_event()
    assert response_type == 'oadrResponse'

    await client._event_cleanup()

    assert len(client.responded_events) == 0
    assert len(client.received_events) == 0

    await server.stop()
    await client.stop()


@pytest.mark.asyncio
async def test_event_external_polling_function():
    async def opt_in_to_event(event, future=None):
        if future:
            future.set_result(True)
        return 'optIn'

    async def on_update_event(event, future=None):
        if future:
            future.set_result(event)
        return 'optIn'

    async def on_poll(ven_id, future=None):
        if future and not future.done():
            future.set_result(True)
            return objects.Event(event_descriptor=objects.EventDescriptor(event_id='event001',
                                                                       modification_number=0,
                                                                       event_status='far',
                                                                       market_context='http://marketcontext01'),
                              event_signals=[objects.EventSignal(signal_id='signal001',
                                                                 signal_type='level',
                                                                 signal_name='simple',
                                                                 intervals=[objects.Interval(dtstart=now,
                                                                                             duration=datetime.timedelta(minutes=10),
                                                                                             signal_payload=1)]),
                                            objects.EventSignal(signal_id='signal002',
                                                                signal_type='price',
                                                                signal_name='ELECTRICITY_PRICE',
                                                                intervals=[objects.Interval(dtstart=now,
                                                                                            duration=datetime.timedelta(minutes=10),
                                                                                            signal_payload=1)])],
                              targets=[objects.Target(ven_id=ven_id)])
        else:
            print("Returning None")
            return None

    loop = asyncio.get_event_loop()
    now = datetime.datetime.now(datetime.timezone.utc)
    server = OpenADRServer(vtn_id='myvtn', requested_poll_freq=datetime.timedelta(seconds=1))
    server.add_handler('on_create_party_registration', on_create_party_registration)
    poll_fut = loop.create_future()
    server.add_handler('on_poll', partial(on_poll, future=poll_fut))
    await server.run()

    client = OpenADRClient(ven_name='ven123',
                           vtn_url='http://localhost:8080/OpenADR2/Simple/2.0b')
    fut = loop.create_future()
    client.add_handler('on_event', partial(opt_in_to_event, future=fut))
    await client.run()
    await fut

    assert len(client.responded_events) == 1
    assert len(client.received_events) == 1

    await server.stop()
    await client.stop()
