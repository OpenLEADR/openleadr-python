import asyncio
import pytest
import os
from functools import partial
from openleadr import OpenADRServer, OpenADRClient, enable_default_logging
from openleadr.utils import certificate_fingerprint
from openleadr import errors
from async_timeout import timeout

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
    if payload['fingerprint'] != ven_fingerprint:
        raise errors.FingerprintMismatch("The fingerprint of your TLS connection does not match the expected fingerprint. Your VEN is not allowed to register.")
    else:
        future.set_result(True)
        return 'ven1234', 'reg5678'

@pytest.mark.asyncio
@pytest.mark.parametrize("disable_signature", [False, True])
async def test_ssl_certificates(disable_signature):
    loop = asyncio.get_event_loop()
    registration_future = loop.create_future()
    server = OpenADRServer(vtn_id='myvtn',
                           http_cert=VTN_CERT,
                           http_key=VTN_KEY,
                           http_ca_file=CA_CERT,
                           cert=VTN_CERT,
                           key=VTN_KEY,
                           fingerprint_lookup=lookup_fingerprint)
    server.add_handler('on_create_party_registration', partial(on_create_party_registration,
                                                               future=registration_future))
    await server.run_async()
    #await asyncio.sleep(1)
    # Run the client
    client = OpenADRClient(ven_name='myven',
                           vtn_url='https://localhost:8080/OpenADR2/Simple/2.0b',
                           cert=VEN_CERT,
                           key=VEN_KEY,
                           ca_file=CA_CERT,
                           vtn_fingerprint=vtn_fingerprint, disable_signature=disable_signature)
    await client.run()

    # Wait for the registration to be triggered
    result = await asyncio.wait_for(registration_future, 1.0)
    assert client.registration_id == 'reg5678'

    await client.stop()
    await server.stop()
    #await asyncio.sleep(0)

@pytest.mark.asyncio
async def test_ssl_certificates_wrong_cert():
    loop = asyncio.get_event_loop()
    registration_future = loop.create_future()
    server = OpenADRServer(vtn_id='myvtn',
                           http_cert=VTN_CERT,
                           http_key=VTN_KEY,
                           http_ca_file=CA_CERT,
                           cert=VTN_CERT,
                           key=VTN_KEY,
                           fingerprint_lookup=lookup_fingerprint)
    server.add_handler('on_create_party_registration', partial(on_create_party_registration,
                                                               future=registration_future))
    await server.run_async()
    #await asyncio.sleep(1)

    # Run the client
    client = OpenADRClient(ven_name='myven',
                           vtn_url='https://localhost:8080/OpenADR2/Simple/2.0b',
                           cert=VTN_CERT,
                           key=VTN_KEY,
                           ca_file=CA_CERT,
                           vtn_fingerprint=vtn_fingerprint)
    await client.run()

    # Wait for the registration to be triggered
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(registration_future, timeout=0.5)
    assert client.registration_id is None

    await client.stop()
    await server.stop()
    await asyncio.sleep(0)

@pytest.mark.asyncio
async def test_ssl_certificates_wrong_fingerprint(caplog):
    loop = asyncio.get_event_loop()
    registration_future = loop.create_future()
    server = OpenADRServer(vtn_id='myvtn',
                           http_cert=VTN_CERT,
                           http_key=VTN_KEY,
                           http_ca_file=CA_CERT,
                           cert=VTN_CERT,
                           key=VTN_KEY,
                           fingerprint_lookup=lookup_fingerprint)
    server.add_handler('on_create_party_registration', partial(on_create_party_registration,
                                                               future=registration_future))
    await server.run_async()
    #await asyncio.sleep(1)
    # Run the client
    client = OpenADRClient(ven_name='myven',
                           vtn_url='https://localhost:8080/OpenADR2/Simple/2.0b',
                           cert=VEN_CERT,
                           key=VEN_KEY,
                           ca_file=CA_CERT,
                           vtn_fingerprint='00:11:22:33:44:55:66:77:88:99')
    await client.run()

    # Wait for the registration to be triggered
    result = await asyncio.wait_for(registration_future, 1.0)

    assert client.registration_id is None
    assert ("The certificate fingerprint was incorrect. Expected: 00:11:22:33:44:55:66:77:88:99; "
            "Received: E6:0C:FE:2F:56:53:64:EA:EC:35. Ignoring message.") in [rec.message for rec in caplog.records]

    await client.stop()
    await server.stop()
