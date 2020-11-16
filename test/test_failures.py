from openleadr import OpenADRClient, OpenADRServer
from openleadr.utils import generate_id
import pytest
from aiohttp import web
import os
import asyncio
from datetime import timedelta

@pytest.mark.asyncio
async def test_http_level_error(start_server):
    client = OpenADRClient(vtn_url="http://this.is.an.error", ven_name=VEN_NAME)
    client.on_event = _client_on_event
    await client.run()
    await client.client_session.close()

@pytest.mark.asyncio
async def test_openadr_error(start_server):
    client = OpenADRClient(vtn_url=f"http://localhost:{SERVER_PORT}/OpenADR2/Simple/2.0b", ven_name=VEN_NAME)
    client.on_event = _client_on_event
    await client.run()
    await client.client_session.close()

@pytest.mark.asyncio
async def test_signature_error(start_server_with_signatures):
    client = OpenADRClient(vtn_url=f"http://localhost:{SERVER_PORT}/OpenADR2/Simple/2.0b", ven_name=VEN_NAME,
                           vtn_fingerprint="INVALID")
    client.on_event = _client_on_event
    await client.run()
    await asyncio.sleep(0)
    await client.client_session.close()


##########################################################################################

SERVER_PORT = 8001
VEN_NAME = 'myven'
VEN_ID = '1234abcd'
VTN_ID = "TestVTN"

CERTFILE = os.path.join(os.path.dirname(__file__), "cert.pem")
KEYFILE =  os.path.join(os.path.dirname(__file__), "key.pem")


async def _on_create_party_registration(payload):
    registration_id = generate_id()
    payload = {'response': {'response_code': 200,
                            'response_description': 'OK',
                            'request_id': payload['request_id']},
               'ven_id': VEN_ID,
               'registration_id': registration_id,
               'profiles': [{'profile_name': '2.0b',
                             'transports': {'transport_name': 'simpleHttp'}}],
               'requested_oadr_poll_freq': timedelta(seconds=1)}
    return 'oadrCreatedPartyRegistration', payload

async def _client_on_event(event):
    pass

async def _client_on_report(report):
    pass

@pytest.fixture
async def start_server():
    server = OpenADRServer(vtn_id=VTN_ID)
    server.add_handler('on_create_party_registration', _on_create_party_registration)

    runner = web.AppRunner(server.app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', SERVER_PORT)
    await site.start()
    yield
    await runner.cleanup()

@pytest.fixture
async def start_server_with_signatures():
    server = OpenADRServer(vtn_id=VTN_ID, cert=CERTFILE, key=KEYFILE, passphrase='openadr')
    server.add_handler('on_create_party_registration', _on_create_party_registration)

    runner = web.AppRunner(server.app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', SERVER_PORT)
    await site.start()
    yield
    await runner.cleanup()

