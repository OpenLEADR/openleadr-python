"""
Utility functions for XML Message Signatures
"""

import hmac
import hashlib
from base64 import b64encode
import re
from datetime import datetime, timedelta, timezone
import xmltodict
from uuid import uuid4
from .utils import datetimeformat, timedeltaformat, booleanformat
from cryptography import x509

from xml.etree.ElementTree import canonicalize
from io import StringIO

from jinja2 import Environment, PackageLoader, select_autoescape

TEMPLATES = Environment(loader=PackageLoader('pyopenadr', 'templates'))

TEMPLATES.filters['datetimeformat'] = datetimeformat
TEMPLATES.filters['timedeltaformat'] = timedeltaformat
TEMPLATES.filters['booleanformat'] = booleanformat

REPLAY_PROTECT_MAX_TIME_DELTA = timedelta(seconds=5)

with open("/home/stan/Ontwikkeling/ElaadNL/pyopenadr/cert.pem", "rb") as file:
    certificate = x509.load_pem_x509_certificate(file.read())
    MODULUS = b64encode(certificate.public_key().public_numbers().n.to_bytes(512, 'big')).decode('ascii')
    EXPONENT = b64encode(certificate.public_key().public_numbers().e.to_bytes(4, 'big')).decode('ascii')

def create_signature(xml_message):
    """
    This creates the signature for the given object. It will return the complete
    Signature section that can be pasted into the XML message.
    """
    # Convert it to its canonical C14n form
    signed_object_canonical = canonicalize(xml_message)

    # Calculate the of this section
    print("Calculating the SHA256 hash of this object")
    print(signed_object_canonical)
    digest_value_signed_object = calculate_digest(signed_object_canonical)

    print()
    print("The signature value is")
    print(digest_value_signed_object)


    # Generate the prop and calculate the digest
    prop = render('signatures/prop.xml', timestamp=datetime.now(timezone.utc), nonce=uuid4().hex)
    digest_value_prop = calculate_digest(prop)

    # Construct the SignedInfo object
    references = [{'id': 'oadrSignedObject',
                   'digest_value': digest_value_signed_object},
                  {'id': 'prop',
                   'digest_value': digest_value_prop}]
    signed_info = render('signatures/SignedInfo.xml', references=references)

    # Construct the KeyInfo object
    key_info = render('signatures/KeyInfo.xml', modulus=MODULUS, exponent=EXPONENT)

    # Calculate the signature for the SignedInfo object
    signature_value = calculate_digest(signed_info)

    # Render the complete Signature section
    signature = render('signatures/Signature.xml',
                       signed_info=signed_info,
                       signature_value=signature_value,
                       prop=prop,
                       key_info=key_info,
                       canonicalize_output=False)
    return signature

def validate_message(xml_message):
    """
    This validates the message.

    1. Verify the digest of the SignedInfo element against the SignatureValue
    2. Verify the digest of the oadrSignedObject against the value in the DigestValue field.
    3. Verify the presence of a ReplayProtect field and that the time is no more different than 5 seconds.
    """

    # Extract the SignedInfo part
    signed_info = extract(xml_message, 'SignedInfo')
    signed_info_canonical = canonicalize(signed_info)
    signed_info_dict = xmltodict.parse(signed_info_canonical)

    # Verify the digest of the SignedInfo element
    signed_info_digest = calculate_digest(signed_info)

    # Verify the digest of the oadrSignedObject
    signed_object = extract(xml_message, 'oadrSignedObject')
    signed_object_canonical = canonicalize(signed_object)
    signed_object_id = re.search(r'id="(.*?)"', signed_object_canonical, flags=re.I).group(1)

    # breakpoint()
    signed_info_reference = re.search(fr'<(.*)?Reference.*? URI="#{signed_object_id}".*?>(.*?)</\1Reference>',
                                      signed_info,
                                      flags=re.S).group(2)

    signed_info_digest_method = re.search(r'<(.*)?DigestMethod.* Algorithm="(.*?)"', signed_info_reference).group(2)
    signed_info_digest_value = re.search(r'<(.*)?DigestValue.*?>(.*?)</\1DigestValue>', signed_info_reference).group(2)

    if signed_info_digest_method != "http://www.w3.org/2001/04/xmlenc#sha256":
        raise ValueError(f"Wrong digest method used: {signed_info_digest_method}")

    signed_object_digest = calculate_digest(signed_object_canonical)
    if signed_object_digest != signed_info_digest_value:
        raise ValueError(f"Digest values do not match for oadrSignedObject identified by #{signed_object_id}\n"
                         f"Provided Digest: {signed_info_digest_value}\n"
                         f"Calculated Digest: {signed_object_digest}")


def calculate_digest(xml_part):
    """
    This calculates the digest for the given XML part
    and returns its base-64 encoded value
    """
    hash = hashlib.sha256()
    hash.update(xml_part.encode('utf-8'))
    return b64encode(hash.digest()).decode('ascii')

def calculate_signature(xml_part):
    """
    This calculates the signature for the entire SignedInfo block.
    """

def get_tag_id(xml_message, tag):
    tag = re.search(fr'<(.*)?{tag}.*?id="(.*?)".*?>',
                    xml_message,
                    flags=re.S|re.I).group(0)

def extract(xml, tag):
    # Extract the first occurence of tag and its contents from the xml message
    section = re.search(fr'<([^:]*:?){tag}[^>]*>.*</\1{tag}>', xml, flags=re.S)
    if section:
        return section.group(0)
    else:
        return None

def render(template, canonicalize_output=True, **data):
    t = TEMPLATES.get_template(template)
    xml = t.render(**data)
    if canonicalize_output:
        return canonicalize(xml)
    else:
        return xml