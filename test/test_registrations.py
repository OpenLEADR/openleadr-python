from openleadr import OpenADRClient, OpenADRServer, enable_default_logging
import datetime
import pytest
import asyncio

enable_default_logging()


def on_create_party_registration_success(registration_info):
    return 'ven123', 'reg123'

def on_create_party_registration_reject(registration_info):
    return False

def on_event(*args, **kwargs):
    return 'optIn'

def event_callback(ven_id, event_id, opt_type):
    pass

@pytest.mark.asyncio
async def test_successful_registration():
    loop = asyncio.get_event_loop()
    client = OpenADRClient(ven_name='myven',
                           vtn_url='http://localhost:8080/OpenADR2/Simple/2.0b')

    client.add_handler('on_event', on_event)
    server = OpenADRServer(vtn_id='myvtn', requested_poll_freq=datetime.timedelta(seconds=1))
    server.add_handler('on_create_party_registration', on_create_party_registration_success)

    await server.run_async()
    await client.run()

    await asyncio.sleep(0.1)

    assert client.registration_id == 'reg123'
    await client.stop()
    await server.stop()

@pytest.mark.asyncio
async def test_rejected_registration():
    loop = asyncio.get_event_loop()
    client = OpenADRClient(ven_name='myven',
                           vtn_url='http://localhost:8080/OpenADR2/Simple/2.0b')

    client.add_handler('on_event', on_event)
    server = OpenADRServer(vtn_id='myvtn', requested_poll_freq=datetime.timedelta(seconds=1))
    server.add_handler('on_create_party_registration', on_create_party_registration_reject)

    await server.run_async()
    await client.run()

    await asyncio.sleep(0.1)

    assert client.registration_id == None
    await client.stop()
    await server.stop()

@pytest.mark.asyncio
async def test_registration_with_prefilled_ven_id():
    loop = asyncio.get_event_loop()
    client = OpenADRClient(ven_name='myven',
                           vtn_url='http://localhost:8080/OpenADR2/Simple/2.0b',
                           ven_id='ven123')

    client.add_handler('on_event', on_event)
    server = OpenADRServer(vtn_id='myvtn', requested_poll_freq=datetime.timedelta(seconds=1))
    server.add_handler('on_create_party_registration', on_create_party_registration_success)

    await server.run_async()
    await client.run()

    await asyncio.sleep(0.1)

    assert client.registration_id == 'reg123'
    await client.stop()
    await server.stop()

@pytest.mark.asyncio
async def test_rejected_registration_with_prefilled_ven_id():
    loop = asyncio.get_event_loop()
    client = OpenADRClient(ven_name='myven',
                           vtn_url='http://localhost:8080/OpenADR2/Simple/2.0b',
                           ven_id='ven123')

    client.add_handler('on_event', on_event)
    server = OpenADRServer(vtn_id='myvtn', requested_poll_freq=datetime.timedelta(seconds=1))
    server.add_handler('on_create_party_registration', on_create_party_registration_reject)

    await server.run_async()
    await client.run()

    await asyncio.sleep(0.1)

    assert client.registration_id == None
    await client.stop()
    await server.stop()

@pytest.mark.asyncio
async def test_registration_with_different_ven_id():
    loop = asyncio.get_event_loop()
    client = OpenADRClient(ven_name='myven',
                           vtn_url='http://localhost:8080/OpenADR2/Simple/2.0b',
                           ven_id='someven')
    client.add_handler('on_event', on_event)
    server = OpenADRServer(vtn_id='myvtn', requested_poll_freq=datetime.timedelta(seconds=1))
    server.add_handler('on_create_party_registration', on_create_party_registration_success)

    await server.run_async()
    await client.run()

    await asyncio.sleep(0.1)

    assert client.registration_id == 'reg123'
    assert client.ven_id == 'ven123'

    await asyncio.sleep(0.1)

    await client.stop()
    await server.stop()
