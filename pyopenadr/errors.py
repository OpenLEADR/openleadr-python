OUT_OF_SEQUENCE  = 450
NOT_ALLOWED      = 451
INVALID_ID       = 452
NOT_RECOGNIZED   = 453
INVALID_DATA     = 454
COMPLIANCE_ERROR = 459
SIGNAL_NOT_SUPPORTED = 460
REPORT_NOT_SUPPORTED = 461
TARGET_MISMATCH = 462
NOT_REGISTERED_OR_AUTHORIZED = 463
DEPLOYMENT_ERROR_OTHER = 469

class OpenADRError(Exception):
    status_codes = {450: "OUT_OF_SEQUENCE",
                    451: "NOT_ALLOWED",
                    452: "INVALID_ID",
                    453: "NOT_RECOGNIZED",
                    454: "INVALID_DATA",
                    459: "COMPLIANCE_ERROR",
                    460: "SIGNAL_NOT_SUPPORTED",
                    461: "REPORT_NOT_SUPPORTED",
                    462: "TARGET_MISMATCH",
                    463: "NOT_REGISTERED_OR_AUTHORIZED",
                    469: "DEPLOYMENT_ERROR_OTHER"}

    def __init__(self, status, description):
        assert status in self.status_codes, f"Invalid status code {status} while raising OpenADRError"
        super().__init__()
        self.status = status
        self.description = description

    def __str__(self):
        return f'Error {self.status} {self.status_codes[self.status]}: {self.description}'
