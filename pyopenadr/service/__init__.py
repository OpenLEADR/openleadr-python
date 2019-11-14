import responder
from .. import config
from ..utils import datetimeformat, timedeltaformat, booleanformat

api = responder.API(templates_dir=config.TEMPLATE_DIR)
api.templates._env.filters['datetimeformat'] = datetimeformat
api.templates._env.filters['timedeltaformat'] = timedeltaformat
api.templates._env.filters['booleanformat'] = booleanformat

def handler(message_type):
    """
    Decorator to mark a method as the handler for a specific message type.
    """
    def _actual_decorator(decorated_function):
        decorated_function.__message_type__ = message_type
        return decorated_function
    return _actual_decorator

# The classes below all register to the api
from .vtn_service import VTNService
from .event_service import EventService
from .poll_service import PollService
from .registration_service import RegistrationService
from .report_service import ReportService

# from .opt_service import OptService
