from openleadr.enums import STATUS_CODES


class ProtocolError(Exception):
    pass


class FingerprintMismatch(Exception):
    pass


class HTTPError(Exception):
    def __init__(self, status=500, description=None):
        super().__init__()
        self.response_code = status
        self.response_description = description


class OutOfSequenceError(ProtocolError):
    def __init__(self, description=None):
        super().__init__()
        self.response_code = STATUS_CODES.OUT_OF_SEQUENCE
        self.response_description = description


class NotAllowedError(ProtocolError):
    def __init__(self, description=None):
        super().__init__()
        self.response_code = STATUS_CODES.NOT_ALLOWED
        self.response_description = description


class InvalidIdError(ProtocolError):
    def __init__(self, description=None):
        super().__init__()
        self.response_code = STATUS_CODES.INVALID_ID
        self.response_description = description


class NotRecognizedError(ProtocolError):
    def __init__(self, description=None):
        super().__init__()
        self.response_code = STATUS_CODES.NOT_RECOGNIZED
        self.response_description = description


class InvalidDataError(ProtocolError):
    def __init__(self, description=None):
        super().__init__()
        self.response_code = STATUS_CODES.INVALID_DATA
        self.response_description = description


class ComplianceError(ProtocolError):
    def __init__(self, description=None):
        super().__init__()
        self.response_code = STATUS_CODES.COMPLIANCE_ERROR
        self.response_description = description


class SignalNotSupportedError(ProtocolError):
    def __init__(self, description=None):
        super().__init__()
        self.response_code = STATUS_CODES.SIGNAL_NOT_SUPPORTED
        self.response_description = description


class ReportNotSupportedError(ProtocolError):
    def __init__(self, description=None):
        super().__init__()
        self.response_code = STATUS_CODES.REPORT_NOT_SUPPORTED
        self.response_description = description


class TargetMismatchError(ProtocolError):
    def __init__(self, description=None):
        super().__init__()
        self.response_code = STATUS_CODES.TARGET_MISMATCH
        self.response_description = description


class NotRegisteredOrAuthorizedError(ProtocolError):
    def __init__(self, description=None):
        super().__init__()
        self.response_code = STATUS_CODES.NOT_REGISTERED_OR_AUTHORIZED
        self.response_description = description


class DeploymentError(ProtocolError):
    def __init__(self, description=None):
        super().__init__()
        self.response_code = STATUS_CODES.DEPLOYMENT_ERROR_OTHER
        self.response_description = description
