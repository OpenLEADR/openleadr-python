from openleadr import errors, enums

def test_protocol_errors():
    for error in dir(errors):
        if isinstance(getattr(errors, error), type):
            err = getattr(errors, error)()
            if isinstance(err, errors.ProtocolError) and not type(err) == errors.ProtocolError:
                err_description = err.response_description
                err_code = err.response_code
                err_enum = err_description.replace(" ", "_")
                assert enums.STATUS_CODES[err_enum] == err_code