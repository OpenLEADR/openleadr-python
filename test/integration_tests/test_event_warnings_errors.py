from openleadr import OpenADRClient, OpenADRServer, enable_default_logging
import pytest
from functools import partial
import asyncio
from datetime import datetime, timedelta
import logging

async def on_create_party_registration(ven_name):
    return 'venid', 'regid'

async def on_event_accepted(ven_id, event_id, opt_type, future):
    future.set_result(opt_type)

async def good_on_event(event):
    return 'optIn'

async def faulty_on_event(event):
    return None

async def broken_on_event(event):
    raise KeyError("BOOM")

@pytest.mark.asyncio
async def test_client_no_event_handler(caplog):
    caplog.set_level(logging.WARNING)
    enable_default_logging()
    logger = logging.getLogger('openleadr')
    logger.setLevel(logging.DEBUG)
    client = OpenADRClient(ven_name='myven',
                           vtn_url='http://localhost:8080/OpenADR2/Simple/2.0b')
    server = OpenADRServer(vtn_id='myvtn', requested_poll_freq=timedelta(seconds=1))
    server.add_handler('on_create_party_registration', on_create_party_registration)
    print("Running server")
    await server.run_async()
    await asyncio.sleep(0.1)
    print("Running client")
    await client.run()

    event_confirm_future = asyncio.get_event_loop().create_future()
    print("Adding event")
    server.add_event(ven_id='venid',
                     signal_name='simple',
                     signal_type='level',
                     intervals=[{'dtstart': datetime.now(),
                                 'duration': timedelta(seconds=10),
                                 'signal_payload': 1.1}],
                     target={'ven_id': 'venid'},
                     callback=partial(on_event_accepted, future=event_confirm_future))

    print("Waiting for a response to the event")
    result = await event_confirm_future
    assert result == 'optOut'
    assert ("You should implement your own on_event handler. This handler receives "
            "an Event dict and should return either 'optIn' or 'optOut' based on your "
            "choice. Will opt out of the event for now.") in [rec.message for rec in caplog.records]
    await client.stop()
    await server.stop()
    await asyncio.sleep(0)

@pytest.mark.asyncio
async def test_client_faulty_event_handler(caplog):
    caplog.set_level(logging.WARNING)
    enable_default_logging()
    logger = logging.getLogger('openleadr')
    logger.setLevel(logging.DEBUG)
    client = OpenADRClient(ven_name='myven',
                           vtn_url='http://localhost:8080/OpenADR2/Simple/2.0b')
    client.add_handler('on_event', faulty_on_event)
    server = OpenADRServer(vtn_id='myvtn', requested_poll_freq=timedelta(seconds=1))
    server.add_handler('on_create_party_registration', on_create_party_registration)
    print("Running server")
    await server.run_async()
    await asyncio.sleep(0.1)
    print("Running client")
    await client.run()

    event_confirm_future = asyncio.get_event_loop().create_future()
    print("Adding event")
    server.add_event(ven_id='venid',
                     signal_name='simple',
                     signal_type='level',
                     intervals=[{'dtstart': datetime.now(),
                                 'duration': timedelta(seconds=10),
                                 'signal_payload': 1.1}],
                     target={'ven_id': 'venid'},
                     callback=partial(on_event_accepted, future=event_confirm_future))

    print("Waiting for a response to the event")
    result = await event_confirm_future
    assert result == 'optOut'
    assert ("Your on_event handler must return 'optIn' or 'optOut'; "
           f"you supplied {None}. Please fix your on_event handler.") in [rec.message for rec in caplog.records]
    await client.stop()
    await server.stop()
    await asyncio.sleep(0)

@pytest.mark.asyncio
async def test_client_exception_event_handler(caplog):
    caplog.set_level(logging.WARNING)
    enable_default_logging()
    logger = logging.getLogger('openleadr')
    logger.setLevel(logging.DEBUG)
    client = OpenADRClient(ven_name='myven',
                           vtn_url='http://localhost:8080/OpenADR2/Simple/2.0b')
    client.add_handler('on_event', broken_on_event)
    server = OpenADRServer(vtn_id='myvtn', requested_poll_freq=timedelta(seconds=1))
    server.add_handler('on_create_party_registration', on_create_party_registration)
    print("Running server")
    await server.run_async()
    await asyncio.sleep(0.1)
    print("Running client")
    await client.run()

    event_confirm_future = asyncio.get_event_loop().create_future()
    print("Adding event")
    server.add_event(ven_id='venid',
                     signal_name='simple',
                     signal_type='level',
                     intervals=[{'dtstart': datetime.now(),
                                 'duration': timedelta(seconds=10),
                                 'signal_payload': 1.1}],
                     target={'ven_id': 'venid'},
                     callback=partial(on_event_accepted, future=event_confirm_future))

    print("Waiting for a response to the event")
    result = await event_confirm_future
    assert result == 'optOut'

    err = KeyError("BOOM")
    assert ("Your on_event handler encountered an error. Will Opt Out of the event. "
           f"The error was {err.__class__.__name__}: {str(err)}") in [rec.message for rec in caplog.records]
    await client.stop()
    await server.stop()
    await asyncio.sleep(0)

@pytest.mark.asyncio
async def test_client_good_event_handler(caplog):
    caplog.set_level(logging.WARNING)
    enable_default_logging()
    logger = logging.getLogger('openleadr')
    logger.setLevel(logging.DEBUG)
    client = OpenADRClient(ven_name='myven',
                           vtn_url='http://localhost:8080/OpenADR2/Simple/2.0b')
    client.add_handler('on_event', good_on_event)
    server = OpenADRServer(vtn_id='myvtn', requested_poll_freq=timedelta(seconds=1))
    server.add_handler('on_create_party_registration', on_create_party_registration)
    print("Running server")
    await server.run_async()
    await asyncio.sleep(0.1)
    print("Running client")
    await client.run()

    event_confirm_future = asyncio.get_event_loop().create_future()
    print("Adding event")
    server.add_event(ven_id='venid',
                     signal_name='simple',
                     signal_type='level',
                     intervals=[{'dtstart': datetime.now(),
                                 'duration': timedelta(seconds=10),
                                 'signal_payload': 1.1}],
                     target={'ven_id': 'venid'},
                     callback=partial(on_event_accepted, future=event_confirm_future))

    print("Waiting for a response to the event")
    result = await event_confirm_future
    assert result == 'optIn'
    assert len(caplog.records) == 0
    await asyncio.sleep(1)
    await client.stop()
    await server.stop()
    await asyncio.sleep(1)

@pytest.mark.asyncio
async def test_server_warning_conflicting_poll_methods(caplog):
    caplog.set_level(logging.WARNING)
    enable_default_logging()
    logger = logging.getLogger('openleadr')
    logger.setLevel(logging.DEBUG)
    server = OpenADRServer(vtn_id='myvtn', requested_poll_freq=timedelta(seconds=1))
    server.add_handler('on_poll', print)
    print("Running server")
    await server.run_async()
    await asyncio.sleep(0.1)
    server.add_event(ven_id='venid',
                     signal_name='simple',
                     signal_type='level',
                     intervals=[{'dtstart': datetime.now(),
                                 'duration': timedelta(seconds=10),
                                 'signal_payload': 1.1}],
                     target={'ven_id': 'venid'},
                     callback=print)
    assert ("You cannot use the add_event method after you assign your own on_poll "
            "handler. If you use your own on_poll handler, you are responsible for "
            "delivering events from that handler. If you want to use OpenLEADRs "
            "message queuing system, you should not assign an on_poll handler. "
            "Your Event will NOT be added.") in [record.msg for record in caplog.records]
    await server.stop()
    await asyncio.sleep(0)
