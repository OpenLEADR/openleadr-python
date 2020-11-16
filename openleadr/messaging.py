# SPDX-License-Identifier: Apache-2.0

# Copyright 2020 Contributors to OpenLEADR

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from lxml import etree
import xmltodict
from jinja2 import Environment, PackageLoader
from signxml import XMLSigner, XMLVerifier, methods
from uuid import uuid4
from lxml.etree import Element

from .utils import *
from .preflight import preflight_message
from dataclasses import is_dataclass, asdict

import logging
logger = logging.getLogger('openleadr')

SIGNER = XMLSigner(method=methods.detached,
                   c14n_algorithm="http://www.w3.org/2001/10/xml-exc-c14n#")
VERIFIER = XMLVerifier()


def parse_message(data, fingerprint=None, fingerprint_lookup=None):
    """
    Parse a message and distill its usable parts. Returns a message type and payload.
    """
    message_dict = xmltodict.parse(data, process_namespaces=True, namespaces=NAMESPACES)
    message_type, message_payload = message_dict['oadrPayload']['oadrSignedObject'].popitem()
    if 'ven_id' in message_payload:
        _validate_and_authenticate_message(data, message_dict, fingerprint, fingerprint_lookup)

    message_payload = normalize_dict(message_payload)
    logger.debug(message_payload)
    return message_type, message_payload


def create_message(message_type, cert=None, key=None, passphrase=None, **message_payload):
    """
    Create and optionally sign an OpenADR message. Returns an XML string.
    """
    # If we supply the payload as dataclasses, convert them to dicts
    # for k, v in message_payload.items():
    #     if isinstance(v, list):
    #         for i, item in enumerate(v):
    #             if is_dataclass(item):
    #                 v[i] = asdict(item)
    #     elif is_dataclass(v):
    #         message_payload[k] = asdict(v)

    message_payload = preflight_message(message_type, message_payload)
    signed_object = flatten_xml(TEMPLATES.get_template(f'{message_type}.xml')
                                         .render(**message_payload))
    envelope = TEMPLATES.get_template('oadrPayload.xml')
    if cert and key:
        tree = etree.fromstring(signed_object)
        signature_tree = SIGNER.sign(tree,
                                     key=key,
                                     cert=cert,
                                     passphrase=ensure_bytes(passphrase),
                                     reference_uri="#oadrSignedObject",
                                     signature_properties=_create_replay_protect())
        signature = etree.tostring(signature_tree).decode('utf-8')
    else:
        signature = None

    msg = envelope.render(template=f'{message_type}',
                          signature=signature,
                          signed_object=signed_object)
    return msg


def _validate_and_authenticate_message(data, message_dict, fingerprint=None,
                                       fingerprint_lookup=None):
    if not fingerprint and not fingerprint_lookup:
        return
    tree = etree.fromstring(ensure_bytes(data))
    cert = extract_pem_cert(tree)
    ven_id = tree.find('.//{http://docs.oasis-open.org/ns/energyinterop/201110}venID').text
    cert_fingerprint = certificate_fingerprint(cert)
    if not fingerprint:
        fingerprint = fingerprint_lookup(ven_id)

    if fingerprint != certificate_fingerprint(cert):
        raise ValueError("The fingerprint does not match")
    VERIFIER.verify(tree, x509_cert=ensure_bytes(cert), expect_references=2)
    _verify_replay_protect(message_dict)


def _create_replay_protect():
    dt_element = Element("{http://openadr.org/oadr-2.0b/2012/07/xmldsig-properties}timestamp")
    dt_element.text = datetimeformat(datetime.now(timezone.utc))

    nonce_element = Element("{http://openadr.org/oadr-2.0b/2012/07/xmldsig-properties}nonce")
    nonce_element.text = uuid4().hex

    el = Element("{http://openadr.org/oadr-2.0b/2012/07/xmldsig-properties}ReplayProtect",
                 nsmap={'dsp': 'http://openadr.org/oadr-2.0b/2012/07/xmldsig-properties'},
                 attrib={'Id': 'myid', 'Target': '#mytarget'})
    el.append(dt_element)
    el.append(nonce_element)
    return el


def _verify_replay_protect(message_dict):
    try:
        sig_props = message_dict['oadrPayload']['Signature']['Object']['SignatureProperties']
        replay_protect = sign_props['SignatureProperty']['ReplayProtect']
        ts = replay_protect['timestamp']
        nonce = replay_protect['nonce']
    except KeyError:
        raise ValueError("Missing ReplayProtect")
    else:
        timestamp = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S.%f%z")
        if timestamp < datetime.now(timezone.utc) - REPLAY_PROTECT_MAX_TIME_DELTA:
            raise ValueError("Message is too old")
        elif (timestamp, nonce) in NONCE_CACHE:
            raise ValueError("This combination of timestamp and nonce was already used")
    _update_nonce_cache(timestamp, nonce)


def _update_nonce_cache(timestamp, nonce):
    for timestamp, nonce in list(NONCE_CACHE):
        if timestamp < datetime.now(timezone.utc) - REPLAY_PROTECT_MAX_TIME_DELTA:
            NONCE_CACHE.remove((timestamp, nonce))
    NONCE_CACHE.add((timestamp, nonce))


# Replay protect settings
REPLAY_PROTECT_MAX_TIME_DELTA = timedelta(seconds=5)
NONCE_CACHE = set()

# Settings for jinja2
TEMPLATES = Environment(loader=PackageLoader('openleadr', 'templates'))
TEMPLATES.filters['datetimeformat'] = datetimeformat
TEMPLATES.filters['timedeltaformat'] = timedeltaformat
TEMPLATES.filters['booleanformat'] = booleanformat
TEMPLATES.trim_blocks = True
TEMPLATES.lstrip_blocks = True

# Settings for xmltodict
NAMESPACES = {
    'http://docs.oasis-open.org/ns/energyinterop/201110': None,
    'http://openadr.org/oadr-2.0b/2012/07': None,
    'urn:ietf:params:xml:ns:icalendar-2.0': None,
    'http://docs.oasis-open.org/ns/energyinterop/201110/payloads': None,
    'http://docs.oasis-open.org/ns/emix/2011/06': None,
    'urn:ietf:params:xml:ns:icalendar-2.0:stream': None,
    'http://docs.oasis-open.org/ns/emix/2011/06/power': None,
    'http://docs.oasis-open.org/ns/emix/2011/06/siscale': None,
    'http://www.w3.org/2000/09/xmldsig#': None,
    'http://openadr.org/oadr-2.0b/2012/07/xmldsig-properties': None
}
