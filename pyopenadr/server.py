#!/Users/stan/Development/ElaadNL/pyopenadr/.python/bin/python3
# A simple Python OpenADR VTN Server.

from pyopenadr.service import api
from pyopenadr.service import PollService, EventService, PollService, RegistrationService, ReportService

class OpenADRServer:
    def __init__(self):
        self.api = api
        self.__setattr__ = self.add_handler

    def add_handler(self, name, func):
        """
        Add a handler to the OpenADRServer.
        """
        map = {'on_created_event': EventService,
               'on_request_event': EventService,

               'on_create_report': ReportService,
               'on_created_report': ReportService,
               'on_request_report': ReportService,
               'on_update_report': ReportService,

               'on_poll': PollService,

               'on_query_registration': RegistrationService,
               'on_create_party_registration': RegistrationService,
               'on_cancel_party_registration': RegistrationService}
        if name in map:
            setattr(map[name], name, staticmethod(func))
        else:
            raise NameError(f"Unknown handler {name}. Correct handler names are: {map.keys()}")

