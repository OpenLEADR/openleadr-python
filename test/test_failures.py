from openleadr import OpenADRClient, OpenADRServer
from openleadr.utils import generate_id, certificate_fingerprint
from openleadr import messaging, errors, objects
from datetime import datetime, timezone, timedelta
import pytest
import pytest_asyncio
from aiohttp import web
import os
import logging
import asyncio
from datetime import timedelta
from base64 import b64encode
import re
from lxml import etree

@pytest.mark.asyncio
async def test_http_level_error(start_server):
    client = OpenADRClient(vtn_url="http://this.is.an.error", ven_name=VEN_NAME)
    client.on_event = _client_on_event
    await client.run()
    await client.client_session.close()


@pytest.mark.asyncio
async def test_xml_schema_error(start_server, caplog):
    message = messaging.create_message("oadrQueryRegistration", request_id='req1234')
    message = message.replace('<requestID xmlns="http://docs.oasis-open.org/ns/energyinterop/201110/payloads">req1234</requestID>', '')
    client = OpenADRClient(ven_name='myven', vtn_url=f'http://localhost:{SERVER_PORT}/OpenADR2/Simple/2.0b')
    result = await client._perform_request('EiRegisterParty', message)
    assert result == (None, {})

    logs = [rec.message for rec in caplog.records]
    for log in logs:
        if log.startswith("Non-OK status 400"):
          assert "XML failed validation" in log
          break
    else:
        assert False

@pytest.mark.asyncio
async def test_wrong_endpoint(start_server, caplog):
    message = messaging.create_message("oadrQueryRegistration", request_id='req1234')
    client = OpenADRClient(ven_name='myven', vtn_url=f'http://localhost:{SERVER_PORT}/OpenADR2/Simple/2.0b')
    response_type, response_payload = await client._perform_request('OadrPoll', message)
    assert response_type == 'oadrResponse'
    assert response_payload['response']['response_code'] == 459

@pytest.mark.asyncio
async def test_vtn_no_create_party_registration_handler(caplog):
    caplog.set_level(logging.WARNING)
    server = OpenADRServer(vtn_id='myvtn')
    client = OpenADRClient(ven_name='myven', vtn_url='http://localhost:8080/OpenADR2/Simple/2.0b')
    await server.run_async()
    await client.run()
    #await asyncio.sleep(0.5)
    await server.stop()
    await client.stop()
    #await asyncio.sleep(0)
    assert 'No RegistrationID received from the VTN, aborting.' in caplog.messages
    assert ("You should implement and register your own on_create_party_registration "
            "handler if you want VENs to be able to connect to you. This handler will "
            "receive a registration request and should return either 'False' (if the "
            "registration is denied) or a (ven_id, registration_id) tuple if the "
            "registration is accepted.") in caplog.messages

@pytest.mark.asyncio
async def test_invalid_signature_error(start_server_with_signatures, caplog):
    client = OpenADRClient(ven_name='myven',
                           vtn_url=f'https://localhost:{SERVER_PORT}/OpenADR2/Simple/2.0b',
                           cert=VEN_CERT,
                           key=VEN_KEY,
                           ca_file=CA_FILE,
                           vtn_fingerprint=VTN_FINGERPRINT)
    message = client._create_message('oadrPoll', ven_id='ven123')
    fake_sig = b64encode("HelloThere".encode('utf-8')).decode('utf-8')
    message = re.sub(r'<ds:SignatureValue>.*?</ds:SignatureValue>', f'<ds:SignatureValue>{fake_sig}</ds:SignatureValue>', message)
    result = await client._perform_request('OadrPoll', message)
    assert result == (None, {})

    logs = [rec.message for rec in caplog.records]
    for log in logs:
        if log.startswith("Non-OK status 403 when performing a request"):
          assert "Invalid Signature" in log
          break
    else:
        assert False

def problematic_handler(*args, **kwargs):
    raise Exception("BOOM")

@pytest.mark.asyncio
async def test_server_handler_exception(caplog):
    server = OpenADRServer(vtn_id=VTN_ID,
                           http_port=SERVER_PORT)
    server.add_handler('on_create_party_registration', problematic_handler)
    await server.run_async()
    client = OpenADRClient(ven_name='myven',
                           vtn_url=f'http://localhost:{SERVER_PORT}/OpenADR2/Simple/2.0b')
    await client.run()
    #await asyncio.sleep(0.5)
    await client.stop()
    await server.stop()
    for message in caplog.messages:
        if message.startswith('Non-OK status 500 when performing a request'):
            break
    else:
        assert False

def protocol_error_handler(*args, **kwargs):
    raise errors.OutOfSequenceError()


@pytest.mark.asyncio
async def test_throw_protocol_error(caplog):
    server = OpenADRServer(vtn_id=VTN_ID,
                           http_port=SERVER_PORT)
    server.add_handler('on_create_party_registration', protocol_error_handler)
    await server.run_async()
    client = OpenADRClient(ven_name='myven',
                           vtn_url=f'http://localhost:{SERVER_PORT}/OpenADR2/Simple/2.0b')
    await client.run()
    #await asyncio.sleep(0.5)
    await client.stop()
    await server.stop()
    assert 'We got a non-OK OpenADR response from the server: 450: OUT OF SEQUENCE' in caplog.messages

@pytest.mark.asyncio
async def test_invalid_signature_error(start_server_with_signatures, caplog):
    client = OpenADRClient(ven_name='myven',
                           vtn_url=f'https://localhost:{SERVER_PORT}/OpenADR2/Simple/2.0b',
                           cert=VEN_CERT,
                           key=VEN_KEY,
                           ca_file=CA_FILE,
                           vtn_fingerprint=VTN_FINGERPRINT)
    message = client._create_message('oadrPoll', ven_id='ven123')
    fake_sig = b64encode("HelloThere".encode('utf-8')).decode('utf-8')
    message = re.sub(r'<ds:SignatureValue>.*?</ds:SignatureValue>', f'<ds:SignatureValue>{fake_sig}</ds:SignatureValue>', message)
    result = await client._perform_request('OadrPoll', message)
    assert result == (None, {})

    logs = [rec.message for rec in caplog.records]
    for log in logs:
        if log.startswith("Non-OK status 403 when performing a request"):
          assert "Invalid Signature" in log
          break
    else:
        assert False

def test_replay_protect_message_too_old(caplog):
    client = OpenADRClient(ven_name='myven',
                           vtn_url=f'https://localhost:{SERVER_PORT}/OpenADR2/Simple/2.0b',
                           cert=VEN_CERT,
                           key=VEN_KEY,
                           ca_file=CA_FILE,
                           vtn_fingerprint=VTN_FINGERPRINT)
    _temp = messaging.REPLAY_PROTECT_MAX_TIME_DELTA
    messaging.REPLAY_PROTECT_MAX_TIME_DELTA = timedelta(seconds=0)
    message = client._create_message('oadrPoll', ven_id='ven123')
    tree = etree.fromstring(message.encode('utf-8'))
    with pytest.raises(ValueError) as err:
        messaging._verify_replay_protect(tree)
    assert str(err.value) == 'The message was signed too long ago.'
    messaging.REPLAY_PROTECT_MAX_TIME_DELTA = _temp

def test_replay_protect_repeated_message(caplog):
    client = OpenADRClient(ven_name='myven',
                           vtn_url=f'https://localhost:{SERVER_PORT}/OpenADR2/Simple/2.0b',
                           cert=VEN_CERT,
                           key=VEN_KEY,
                           ca_file=CA_FILE,
                           vtn_fingerprint=VTN_FINGERPRINT)
    message = client._create_message('oadrPoll', ven_id='ven123')
    tree = etree.fromstring(message.encode('utf-8'))
    messaging._verify_replay_protect(tree)
    with pytest.raises(ValueError) as err:
        messaging._verify_replay_protect(tree)
    assert str(err.value) == 'This combination of timestamp and nonce was already used.'


def test_replay_protect_missing_nonce(caplog):
    client = OpenADRClient(ven_name='myven',
                           vtn_url=f'https://localhost:{SERVER_PORT}/OpenADR2/Simple/2.0b',
                           cert=VEN_CERT,
                           key=VEN_KEY,
                           ca_file=CA_FILE,
                           vtn_fingerprint=VTN_FINGERPRINT)
    message = client._create_message('oadrPoll', ven_id='ven123')
    message = re.sub('<dsp:nonce>.*?</dsp:nonce>', '', message)
    tree = etree.fromstring(message.encode('utf-8'))
    with pytest.raises(ValueError) as err:
        messaging._verify_replay_protect(tree)
    assert str(err.value) == "Missing 'nonce' element in ReplayProtect in incoming message."


def test_replay_protect_malformed_nonce(caplog):
    client = OpenADRClient(ven_name='myven',
                           vtn_url=f'https://localhost:{SERVER_PORT}/OpenADR2/Simple/2.0b',
                           cert=VEN_CERT,
                           key=VEN_KEY,
                           ca_file=CA_FILE,
                           vtn_fingerprint=VTN_FINGERPRINT)
    message = client._create_message('oadrPoll', ven_id='ven123')
    message = re.sub('<dsp:timestamp>.*?</dsp:timestamp>', '', message)
    tree = etree.fromstring(message.encode('utf-8'))
    with pytest.raises(ValueError) as err:
        messaging._verify_replay_protect(tree)
    assert str(err.value) == "Missing or malformed ReplayProtect element in the message signature."

    message = re.sub('<dsp:ReplayProtect>.*?</dsp:ReplayProtect>', '', message)
    tree = etree.fromstring(message.encode('utf-8'))
    with pytest.raises(ValueError) as err:
        messaging._verify_replay_protect(tree)
    assert str(err.value) == "Missing or malformed ReplayProtect element in the message signature."


def test_server_add_unknown_handler(caplog):
    server = OpenADRServer(vtn_id='myvtn')
    with pytest.raises(NameError) as err:
        server.add_handler('unknown_name', print)
    assert str(err.value) == ("Unknown handler 'unknown_name'. Correct handler names are: "
                              "'on_created_event', 'on_request_event', 'on_register_report', "
                              "'on_create_report', 'on_created_report', 'on_request_report', "
                              "'on_update_report', 'on_poll', 'on_query_registration', "
                              "'on_create_party_registration', 'on_cancel_party_registration'.")


def test_server_add_event_with_invalid_signal_type():
    server = OpenADRServer(vtn_id='myvtn')
    with pytest.raises(ValueError):
        server.add_event(ven_id='ven123',
                         signal_name='simple',
                         signal_type='x-LoadControlCapacity',
                         intervals=[objects.Interval(dtstart=datetime.now(timezone.utc),
                                             duration=timedelta(seconds=10),
                                             signal_payload=1.0)])


def test_server_add_event_with_invalid_signal_name():
    server = OpenADRServer(vtn_id='myvtn')
    with pytest.raises(ValueError):
        server.add_event(ven_id='ven123',
                         signal_name='invalid',
                         signal_type='x-loadControlCapacity',
                         intervals=[objects.Interval(dtstart=datetime.now(timezone.utc),
                                             duration=timedelta(seconds=10),
                                             signal_payload=1.0)])

def test_server_add_event_with_custom_signal_name():
    server = OpenADRServer(vtn_id='myvtn')
    server.add_event(ven_id='ven123',
                     signal_name='x-invalid',
                     signal_type='x-loadControlCapacity',
                     intervals=[objects.Interval(dtstart=datetime.now(timezone.utc),
                                         duration=timedelta(seconds=10),
                                         signal_payload=1.0)])
    assert len(server.events['ven123']) == 1

def test_server_add_event_with_no_intervals():
    server = OpenADRServer(vtn_id='myvtn')
    with pytest.raises(ValueError):
        server.add_event(ven_id='ven123',
                         signal_name='x-invalid',
                         signal_type='x-loadControlCapacity',
                         intervals=None)
    with pytest.raises(ValueError):
        server.add_event(ven_id='ven123',
                         signal_name='x-invalid',
                         signal_type='x-loadControlCapacity',
                         intervals=[])
    with pytest.raises(ValueError):
        server.add_event(ven_id='ven123',
                         signal_name='x-invalid',
                         signal_type='x-loadControlCapacity',
                         intervals={"dtstart": "2021-01-01"})


##########################################################################################

SERVER_PORT = 8001
VEN_NAME = 'myven'
VEN_ID = '1234abcd'
VTN_ID = "TestVTN"

VEN_CERT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "certificates", "dummy_ven.crt")
VEN_KEY = os.path.join(os.path.dirname(os.path.dirname(__file__)), "certificates", "dummy_ven.key")
VTN_CERT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "certificates", "dummy_vtn.crt")
VTN_KEY = os.path.join(os.path.dirname(os.path.dirname(__file__)), "certificates", "dummy_vtn.key")
CA_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "certificates", "dummy_ca.crt")

with open(VEN_CERT) as file:
    VEN_FINGERPRINT = certificate_fingerprint(file.read())

with open(VTN_CERT) as file:
    VTN_FINGERPRINT = certificate_fingerprint(file.read())

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

def fingerprint_lookup(ven_id):
    return VEN_FINGERPRINT

@pytest_asyncio.fixture
async def start_server():
    server = OpenADRServer(vtn_id=VTN_ID, http_port=SERVER_PORT)
    server.add_handler('on_create_party_registration', _on_create_party_registration)
    await server.run_async()
    yield
    await server.stop()

@pytest_asyncio.fixture
async def start_server_with_signatures():
    server = OpenADRServer(vtn_id=VTN_ID,
                           cert=VTN_CERT,
                           key=VTN_KEY,
                           http_cert=VTN_CERT,
                           http_key=VTN_KEY,
                           http_ca_file=CA_FILE,
                           http_port=SERVER_PORT,
                           fingerprint_lookup=fingerprint_lookup)
    server.add_handler('on_create_party_registration', _on_create_party_registration)

    await server.run_async()
    yield
    await server.stop()
