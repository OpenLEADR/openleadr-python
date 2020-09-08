import xmltodict
from jinja2 import Environment, PackageLoader, select_autoescape

from .utils import *
from .signature import *
from .preflight import preflight_message

def parse_message(data):
    """
    Parse a message and distill its usable parts. Returns a message type and payload.
    """
    message_dict = xmltodict.parse(data, process_namespaces=True, namespaces=NAMESPACES)
    message_type, message_payload = message_dict['oadrPayload']['oadrSignedObject'].popitem()
    return message_type, normalize_dict(message_payload)

def create_message(message_type, **message_payload):
    """
    This creates an OpenADR message. This consists
    """
    preflight_message(message_type, message_payload)
    signed_object = indent_xml(TEMPLATES.get_template(f'{message_type}.xml').render(**message_payload))
    signature = create_signature(signed_object)

    envelope = TEMPLATES.get_template('oadrPayload.xml')
    msg = envelope.render(template=f'{message_type}',
                          signature=signature,
                          signed_object=signed_object)
    return msg

# Settings for jinja2
TEMPLATES = Environment(loader=PackageLoader('pyopenadr', 'templates'))
TEMPLATES.filters['datetimeformat'] = datetimeformat
TEMPLATES.filters['timedeltaformat'] = timedeltaformat
TEMPLATES.filters['booleanformat'] = booleanformat

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
