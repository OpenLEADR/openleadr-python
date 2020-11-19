import asyncio
import pytest
import os
from functools import partial
from openleadr import OpenADRServer, OpenADRClient, enable_default_logging
from openleadr.utils import certificate_fingerprint

enable_default_logging()

CA_CERT = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'certificates', 'dummy_ca.crt')
VTN_CERT = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'certificates', 'dummy_vtn.crt')
VTN_KEY = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'certificates', 'dummy_vtn.key')
VEN_CERT = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'certificates', 'dummy_ven.crt')
VEN_KEY = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'certificates', 'dummy_ven.key')


with open(VEN_CERT) as file:
    ven_fingerprint = certificate_fingerprint(file.read())

with open(VTN_CERT) as file:
    vtn_fingerprint = certificate_fingerprint(file.read())

async def lookup_fingerprint(ven_id):
    return ven_fingerprint

async def on_create_party_registration(payload, future):
    future.set_result(payload)
    return '1234', '5678'

@pytest.mark.asyncio
async def test_ssl_certificates():
    loop = asyncio.get_event_loop()
    registration_future = loop.create_future()
    server = OpenADRServer(vtn_id='myvtn',
                           http_cert=VTN_CERT,
                           http_key=VTN_KEY,
                           http_ca_file=CA_CERT,
                           fingerprint_lookup=lookup_fingerprint)
    server.add_handler('on_create_party_registration', partial(on_create_party_registration,
                                                               future=registration_future))
    await server.run_async()
    await asyncio.sleep(1)
    # Run the client
    client = OpenADRClient(ven_name='myven',
                           vtn_url='https://localhost:8080/OpenADR2/Simple/2.0b',
                           cert=VEN_CERT,
                           key=VEN_KEY,
                           ca_file=CA_CERT,
                           vtn_fingerprint=vtn_fingerprint)
    await client.run()

    # Wait for the registration to be triggered
    await registration_future

    await client.stop()
    await server.stop()
    await asyncio.sleep(0)
