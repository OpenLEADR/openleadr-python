# SPDX-License-Identifier: Apache-2.0

# Copyright 2020 Contributors to OpenLEADR

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest

from openleadr import OpenADRClient, OpenADRServer, enums
from openleadr.utils import generate_id
from openleadr.messaging import create_message, parse_message
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
                                             'targets': [{'ven_id': '123'}]})
    parsed_type, parsed_msg = parse_message(msg)
    assert parsed_msg['created_date_time'].tzinfo == timezone.utc
    assert parsed_msg['created_date_time'] == dt.astimezone(timezone.utc)

