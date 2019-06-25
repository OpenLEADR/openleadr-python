from asyncio import iscoroutine
from http import HTTPStatus
import random
import string

from . import api
from .. import config, errors
from ..utils import parse_message, indent_xml

class VTNService:
    """
    This is the default OpenADR handler. You should subclass this with your
    specific services.
    """
    def __init__(self):
        self.handlers = {}
        for method in [getattr(self, attr) for attr in dir(self) if callable(getattr(self, attr))]:
            if hasattr(method, '__message_type__'):
                print(f"Adding {method.__name__} as handler for {method.__message_type__}")
                self.handlers[method.__message_type__] = method

    async def on_request(self, request, response):
        """
        This is the default handler that is used by python-responder. It will
        look for a handler of the message type in one of the subclasses.
        """
        print()
        print()
        print("================================================================================")
        print(f"             NEW REQUEST to {request.url.path}                                 ")
        print("================================================================================")
        content = await request.content
        print(f"Received: {content.decode('utf-8')}")
        message_type, message_payload = parse_message(content)
        print(f"Interpreted message: {message_type}: {message_payload}")
        if message_type in self.handlers:
            handler = self.handlers[message_type]
            result = handler(message_payload)
            if iscoroutine(result):
                response_type, response_payload = await result
            else:
                response_type, response_payload = result
            response.html = indent_xml(api.template(f'{response_type}.xml', **response_payload))
            print(f"Sending {response.html}")
        else:
            response.html = indent_xml(api.template('oadrResponse.xml',
                                status_code=errorcodes.COMPLIANCE_ERROR,
                                status_description=f'A message of type {message_type} should not be sent to this endpoint'))
            print(f"Sending {response.html}")
            response.status_code = HTTPStatus.BAD_REQUEST

