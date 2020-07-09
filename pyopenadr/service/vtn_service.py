from asyncio import iscoroutine
from http import HTTPStatus
import os

from aiohttp import web
from jinja2 import Environment, PackageLoader, select_autoescape

from .. import errors
from ..utils import parse_message, indent_xml, datetimeformat, timedeltaformat, booleanformat

class VTNService:
    templates = Environment(loader=PackageLoader('pyopenadr', 'templates'),
                            autoescape=select_autoescape(['html', 'xml']))
    templates.filters['datetimeformat'] = datetimeformat
    templates.filters['timedeltaformat'] = timedeltaformat
    templates.filters['booleanformat'] = booleanformat

    def __init__(self, vtn_id):
        self.vtn_id = vtn_id
        self.handlers = {}
        for method in [getattr(self, attr) for attr in dir(self) if callable(getattr(self, attr))]:
            if hasattr(method, '__message_type__'):
                self.handlers[method.__message_type__] = method

    async def handler(self, request):
        """
        Handle all incoming POST requests.
        """
        content = await request.read()
        print(f"Received: {content.decode('utf-8')}")
        message_type, message_payload = parse_message(content)
        print(f"Interpreted message: {message_type}: {message_payload}")

        if message_type in self.handlers:
            handler = self.handlers[message_type]
            response_type, response_payload = await handler(message_payload)

            # Get the relevant template and create the XML response
            template = self.templates.get_template(f'{response_type}.xml')
            template.render(**response_payload)
            response = web.Response(text=indent_xml(template.render(**response_payload)),
                                    status=200,
                                    content_type='application/xml')

        else:
            template = templates.get_template('oadrResponse.xml')
            response = web.Response(
                text=template.render(status_code=errorcodes.COMPLIANCE_ERROR,
                                     status_description=f'A message of type {message_type} should not be sent to this endpoint'),
                status=HTTPStatus.BAD_REQUEST,
                content_type='application/xml')
        print(f"Sending {response.text}")
        return response
