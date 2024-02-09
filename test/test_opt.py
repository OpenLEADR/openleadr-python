from openleadr import OpenADRClient, OpenADRServer, enable_default_logging, objects, utils, enums
import pytest
import asyncio
import datetime
from functools import partial

@pytest.mark.asyncio
async def test_create_opt():
    loop = asyncio.get_event_loop()
    my_ven_id='ven123'
    server = OpenADRServer(vtn_id=my_ven_id, requested_poll_freq=datetime.timedelta(seconds=1))
    await server.run_async()

    client = OpenADRClient(ven_name='myven',
                           vtn_url='http://localhost:8080/OpenADR2/Simple/2.0b')
    client.ven_id = my_ven_id
    opt_id = 'opt123'
    opt_type = enums.OPT.OPT_OUT
    opt_reason = enums.OPT_REASON.EMERGENCY
    availability = {'components': [{'duration': datetime.timedelta(minutes=5),'dtstart': datetime.datetime.now(datetime.timezone.utc)}]}
    request_id = 'request123'
    market_context = 'oadr://unknown.context'
    event_id = None
    modification_number = None
    targets = [{'ven_id': 'ven123'}]
    message_type, message_payload = await asyncio.wait_for(
        client.create_opt( 
            opt_id,
            opt_type, 
            opt_reason,
            availability,
            request_id, 
            market_context,
            event_id, modification_number,
            targets)
    , 0.5)    

    assert message_type == 'oadrCreatedOpt'

    # TODO: Remove this later
    file = open('create_opt.txt', 'a')
    print(f"{message_type}", file=file)
    print(f"{message_payload}", file=file)

    await server.stop()
    

@pytest.mark.asyncio
async def test_cancel_opt():
    loop = asyncio.get_event_loop()
    my_ven_id='ven123'
    server = OpenADRServer(vtn_id=my_ven_id, requested_poll_freq=datetime.timedelta(seconds=1))
    await server.run_async()

    client = OpenADRClient(ven_name='myven',
                           vtn_url='http://localhost:8080/OpenADR2/Simple/2.0b')
    client.ven_id = my_ven_id
    opt_id = 'opt123'
    opt_type = enums.OPT.OPT_OUT
    opt_reason = enums.OPT_REASON.EMERGENCY
    availability = {'components': [{'duration': datetime.timedelta(minutes=5),'dtstart': datetime.datetime.now(datetime.timezone.utc)}]}
    request_id = 'request123'
    market_context = 'oadr://unknown.context'
    event_id = None
    modification_number = None
    targets = [{'ven_id': 'ven123'}]

    # First create the Opt schedule
    message_type, message_payload = await asyncio.wait_for(
        client.create_opt( 
            opt_id,
            opt_type, 
            opt_reason,
            availability,
            request_id, 
            market_context,
            event_id, modification_number,
            targets)
    , 0.5)    

    assert message_type == 'oadrCreatedOpt'

    # Now cancel it
    message_type, message_payload = await asyncio.wait_for(client.cancel_opt(opt_id), 0.5)    

    assert message_type == 'oadrCanceledOpt'

    # TODO: Remove this later
    file = open('cancel_opt_test.txt', 'a')
    print(f"{message_type}", file=file)
    print(f"{message_payload}", file=file)

    await server.stop()
        