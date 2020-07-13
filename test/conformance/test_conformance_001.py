import pytest

from pyopenadr import OpenADRClient, OpenADRServer, enums
from pyopenadr.utils import generate_id, create_message, parse_message
from datetime import datetime, timezone, timedelta



@pytest.mark.asyncio
async def test_conformance_001():
    dt = datetime(2020,1,1,12,0,0,tzinfo=timezone(offset=timedelta(hours=4)))
    msg = create_message('oadrCreateOpt', **{'opt_id': generate_id(),
                                             'opt_type': enums.OPT.OPT_IN,
                                             'opt_reason': enums.OPT_REASON.ECONOMIC,
                                             'ven_id': generate_id(),
                                             'created_date_time': dt,
                                             'request_id': generate_id(),
                                             'event_id': generate_id(),
                                             'modification_number': 1,
                                             'targets': []})
    parsed_type, parsed_msg = parse_message(msg)
    assert parsed_msg['created_date_time'].tzinfo == timezone.utc
    assert parsed_msg['created_date_time'] == dt.astimezone(timezone.utc)

