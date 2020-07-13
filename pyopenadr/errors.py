from .enums import STATUS_CODES

class OpenADRError(Exception):
    def __init__(self, status, description):
        assert status in self.status_codes.values, f"Invalid status code {status} while raising OpenADRError"
        super().__init__()
        self.status = status
        self.description = description

    def __str__(self):
        return f'Error {self.status} {self.status_codes[self.status]}: {self.description}'
