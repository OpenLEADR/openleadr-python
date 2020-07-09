from aiohttp import web
from pyopenadr.service import EventService, PollService, RegistrationService, ReportService, OptService

class OpenADRServer:
    map = {'on_created_event': EventService,
           'on_request_event': EventService,

           'on_register_report': ReportService,
           'on_create_report': ReportService,
           'on_created_report': ReportService,
           'on_request_report': ReportService,
           'on_update_report': ReportService,

           'on_poll': PollService,

           'on_query_registration': RegistrationService,
           'on_create_party_registration': RegistrationService,
           'on_cancel_party_registration': RegistrationService}

    def __init__(self, vtn_id):
        self.app = web.Application()
        self.services = {'event_service': EventService(vtn_id),
                         'report_service': ReportService(vtn_id),
                         'poll_service': PollService(vtn_id),
                         'opt_service': OptService(vtn_id),
                         'registration_service': RegistrationService(vtn_id)}
        self.app.add_routes([web.post(f"/OpenADR2/Simple/2.0b/{s.__service_name__}", s.handler) for s in self.services.values()])
        self.__setattr__ = self.add_handler

    def run(self):
        web.run_app(self.app)

    def add_handler(self, name, func):
        """
        Add a handler to the OpenADRServer.
        """
        print("Called add_handler", name, func)
        if name in self.map:
            setattr(self.map[name], name, staticmethod(func))
        else:
            raise NameError(f"Unknown handler {name}. Correct handler names are: {self.map.keys()}")
