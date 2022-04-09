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
from openleadr import errors
from datetime import datetime, timezone, timedelta
import os

from openleadr import utils
from .preflight import preflight_message

import logging
logger = logging.getLogger('openleadr')

SIGNER = XMLSigner(method=methods.detached,
                   c14n_algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315")
SIGNER.namespaces['oadr'] = "http://openadr.org/oadr-2.0b/2012/07"
VERIFIER = XMLVerifier()

XML_SCHEMA_LOCATION = os.path.join(os.path.dirname(__file__), 'schema', 'oadr_20b.xsd')

with open(XML_SCHEMA_LOCATION) as file:
    XML_SCHEMA = etree.XMLSchema(etree.parse(file))
XML_PARSER = etree.XMLParser(schema=XML_SCHEMA)


def parse_message(data):
    """
    Parse a message and distill its usable parts. Returns a message type and payload.
    :param data str: The XML string that is received

    Returns a message type (str) and a message payload (dict)
    """
    try:
        if isinstance(data, bytes):
            logger.debug(f"Parsing message: {data.decode('utf-8')}")
        else:
            logger.debug(f"Parsing message: {data}")
    except UnicodeDecodeError:
        logger.warning(f"Could not decode incoming message as UTF-8: {str(data)}")
    message_dict = xmltodict.parse(data, process_namespaces=True, namespaces=NAMESPACES)
    message_type, message_payload = message_dict['oadrPayload']['oadrSignedObject'].popitem()
    message_payload = utils.normalize_dict(message_payload)
    return message_type, message_payload


def create_message(message_type, cert=None, key=None, passphrase=None, disable_signature=False, **message_payload):
    """
    Create and optionally sign an OpenADR message. Returns an XML string.
    """
    message_payload = preflight_message(message_type, message_payload)
    template = TEMPLATES.get_template(f'{message_type}.xml')
    signed_object = utils.flatten_xml(template.render(**message_payload))
    envelope = TEMPLATES.get_template('oadrPayload.xml')
    if cert and key and not disable_signature:
        tree = etree.fromstring(signed_object)
        signature_tree = SIGNER.sign(tree,
                                     key=key,
                                     cert=cert,
                                     passphrase=utils.ensure_bytes(passphrase),
                                     reference_uri="#oadrSignedObject",
                                     signature_properties=_create_replay_protect())
        signature = etree.tostring(signature_tree).decode('utf-8')
    else:
        signature = None
    msg = envelope.render(template=f'{message_type}',
                          signature=signature,
                          signed_object=signed_object)
    logger.debug(f"Created message: {msg}")
    return msg


def validate_xml_schema(content):
    """
    Validates the XML tree against the schema. Return the XML tree.
    """
    if isinstance(content, str):
        content = content.encode('utf-8')
    tree = etree.fromstring(content, XML_PARSER)
    return tree


def validate_xml_signature(xml_tree, cert_fingerprint=None):
    """
    Validate the XMLDSIG signature and the ReplayProtect element.
    """
    cert = utils.extract_pem_cert(xml_tree)
    if cert_fingerprint:
        fingerprint = utils.certificate_fingerprint(cert)
        if fingerprint != cert_fingerprint:
            raise errors.FingerprintMismatch("The certificate fingerprint was incorrect. "
                                             f"Expected: {cert_fingerprint}; "
                                             f"Received: {fingerprint}. Ignoring message.")
    VERIFIER.verify(xml_tree, x509_cert=utils.ensure_bytes(cert), expect_references=2)
    _verify_replay_protect(xml_tree)


def validate_xml_signature_none(xml_tree):
    assert xml_tree.find('.//{http://www.w3.org/2000/09/xmldsig#}X509Certificate') is None


async def authenticate_message(request, message_tree, message_payload, fingerprint_lookup=None, ven_lookup=None):
    if request.secure and 'ven_id' in message_payload:
        connection_fingerprint = utils.get_cert_fingerprint_from_request(request)
        if connection_fingerprint is None:
            msg = ("Your request must use a client side SSL certificate, of which the "
                   "fingerprint must match the fingerprint that you have given to this VTN.")
            raise errors.NotRegisteredOrAuthorizedError(msg)

        try:
            ven_id = message_payload.get('ven_id')
            if fingerprint_lookup:
                expected_fingerprint = await utils.await_if_required(fingerprint_lookup(ven_id))
                if not expected_fingerprint:
                    raise ValueError
            elif ven_lookup:
                ven_info = await utils.await_if_required(ven_lookup(ven_id))
                if not ven_info:
                    raise ValueError
                expected_fingerprint = ven_info.get('fingerprint')
        except ValueError:
            msg = (f"Your venID {ven_id} is not known to this VTN. Make sure you use the venID "
                   "that you receive from this VTN during the registration step")
            raise errors.NotRegisteredOrAuthorizedError(msg)

        if expected_fingerprint is None:
            msg = ("This VTN server does not know what your certificate fingerprint is. Please "
                   "deliver your fingerprint to the VTN (outside of OpenADR). You used the "
                   "following fingerprint to make this request:")
            raise errors.NotRegisteredOrAuthorizedError(msg)

        if connection_fingerprint != expected_fingerprint:
            msg = (f"The fingerprint of your HTTPS certificate '{connection_fingerprint}' "
                   f"does not match the expected fingerprint '{expected_fingerprint}'")
            raise errors.NotRegisteredOrAuthorizedError(msg)

        message_cert = utils.extract_pem_cert(message_tree)
        message_fingerprint = utils.certificate_fingerprint(message_cert)
        if message_fingerprint != expected_fingerprint:
            msg = (f"The fingerprint of the certificate used to sign the message "
                   f"{message_fingerprint} did not match the fingerprint that this "
                   f"VTN has for you {expected_fingerprint}. Make sure you use the correct "
                   "certificate to sign your messages.")
            raise errors.NotRegisteredOrAuthorizedError(msg)

        try:
            validate_xml_signature(message_tree)
        except ValueError:
            msg = ("The message signature did not match the message contents. Please make sure "
                   "you are using the correct XMLDSig algorithm and C14n canonicalization.")
            raise errors.NotRegisteredOrAuthorizedError(msg)


def _create_replay_protect():
    dt_element = Element("{http://openadr.org/oadr-2.0b/2012/07/xmldsig-properties}timestamp")
    dt_element.text = utils.datetimeformat(datetime.now(timezone.utc))

    nonce_element = Element("{http://openadr.org/oadr-2.0b/2012/07/xmldsig-properties}nonce")
    nonce_element.text = uuid4().hex

    el = Element("{http://openadr.org/oadr-2.0b/2012/07/xmldsig-properties}ReplayProtect",
                 nsmap={'dsp': 'http://openadr.org/oadr-2.0b/2012/07/xmldsig-properties'},
                 attrib={'Id': 'myid', 'Target': '#mytarget'})
    el.append(dt_element)
    el.append(nonce_element)
    return el


def _verify_replay_protect(xml_tree):
    try:
        ns = "{http://openadr.org/oadr-2.0b/2012/07/xmldsig-properties}"
        timestamp = utils.parse_datetime(xml_tree.findtext(f".//{ns}timestamp"))
        nonce = xml_tree.findtext(f".//{ns}nonce")
    except Exception:
        raise ValueError("Missing or malformed ReplayProtect element in the message signature.")
    else:
        if nonce is None:
            raise ValueError("Missing 'nonce' element in ReplayProtect in incoming message.")
        if timestamp < datetime.now(timezone.utc) - REPLAY_PROTECT_MAX_TIME_DELTA:
            raise ValueError("The message was signed too long ago.")
        elif (timestamp, nonce) in NONCE_CACHE:
            raise ValueError("This combination of timestamp and nonce was already used.")
    _update_nonce_cache(timestamp, nonce)


def _update_nonce_cache(timestamp, nonce):
    NONCE_CACHE.add((timestamp, nonce))
    for timestamp, nonce in list(NONCE_CACHE):
        if timestamp < datetime.now(timezone.utc) - REPLAY_PROTECT_MAX_TIME_DELTA:
            NONCE_CACHE.remove((timestamp, nonce))


# Replay protect settings
REPLAY_PROTECT_MAX_TIME_DELTA = timedelta(seconds=5)
NONCE_CACHE = set()

# Settings for jinja2
TEMPLATES = Environment(loader=PackageLoader('openleadr', 'templates'))
TEMPLATES.filters['datetimeformat'] = utils.datetimeformat
TEMPLATES.filters['timedeltaformat'] = utils.timedeltaformat
TEMPLATES.filters['booleanformat'] = utils.booleanformat
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
