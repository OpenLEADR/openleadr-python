from openleadr import OpenADRClient, OpenADRServer, enums
import pytest
import asyncio
import datetime

vtn_port = 8080
vtn_url = f"http://localhost:{vtn_port}/OpenADR2/Simple/2.0b"


@pytest.mark.asyncio
async def test_create_opt():
    global vtn_url, vtn_port
    my_ven_id = 'ven123'
    server = OpenADRServer(http_port=vtn_port, vtn_id=my_ven_id, requested_poll_freq=datetime.timedelta(seconds=1))
    try:
        await server.run_async()

        client = OpenADRClient(ven_name='myven', vtn_url=vtn_url)
        client.ven_id = my_ven_id
        opt_id = 'opt123'
        opt_type = enums.OPT.OPT_OUT
        opt_reason = enums.OPT_REASON.EMERGENCY
        availability = {'components': [{'duration': datetime.timedelta(minutes=5), 'dtstart': datetime.datetime.now(datetime.timezone.utc)}]}
        request_id = 'request123'
        market_context = 'oadr://unknown.context'
        event_id = None
        modification_number = None
        targets = [{'ven_id': 'ven123'}]

        assert f"{opt_id}_{my_ven_id}" not in server.services['eiopt_service'].opt_schedules

        message_type, message_payload = await asyncio.wait_for(
            client.create_opt(
                opt_id,
                opt_type,
                opt_reason,
                availability,
                request_id,
                market_context,
                event_id, modification_number,
                targets), 0.5)

        assert f"{opt_id}_{my_ven_id}" in server.services['eiopt_service'].opt_schedules
        assert message_type == 'oadrCreatedOpt'
        assert message_payload['response']['response_code'] == 200
        assert message_payload['opt_id'] == opt_id

    finally:
        await server.stop()


@pytest.mark.asyncio
async def test_cancel_opt():
    global vtn_url, vtn_port
    my_ven_id = 'ven123'
    server = OpenADRServer(http_port=vtn_port, vtn_id=my_ven_id, requested_poll_freq=datetime.timedelta(seconds=1))
    try:
        await server.run_async()

        client = OpenADRClient(ven_name='myven', vtn_url=vtn_url)
        client.ven_id = my_ven_id
        opt_id_1 = 'opt123'
        opt_id_2 = 'opt456'
        opt_type = enums.OPT.OPT_OUT
        opt_reason = enums.OPT_REASON.EMERGENCY
        availability = {'components': [{'duration': datetime.timedelta(minutes=5), 'dtstart': datetime.datetime.now(datetime.timezone.utc)}]}
        request_id = 'request123'
        market_context = 'oadr://unknown.context'
        event_id = None
        modification_number = None
        targets = [{'ven_id': 'ven123'}]

        assert f"{opt_id_1}_{my_ven_id}" not in server.services['eiopt_service'].opt_schedules
        assert f"{opt_id_2}_{my_ven_id}" not in server.services['eiopt_service'].opt_schedules

        # First create the first Opt schedule
        message_type, message_payload = await asyncio.wait_for(
            client.create_opt(
                opt_id_1,
                opt_type,
                opt_reason,
                availability,
                request_id,
                market_context,
                event_id, modification_number,
                targets), 0.5)

        assert f"{opt_id_1}_{my_ven_id}" in server.services['eiopt_service'].opt_schedules
        assert message_type == 'oadrCreatedOpt'
        assert message_payload['response']['response_code'] == 200
        assert message_payload['opt_id'] == opt_id_1

        # First create the second Opt schedule
        message_type, message_payload = await asyncio.wait_for(
            client.create_opt(
                opt_id_2,
                opt_type,
                opt_reason,
                availability,
                request_id,
                market_context,
                event_id, modification_number,
                targets), 0.5)

        assert f"{opt_id_2}_{my_ven_id}" in server.services['eiopt_service'].opt_schedules
        assert message_type == 'oadrCreatedOpt'
        assert message_payload['response']['response_code'] == 200
        assert message_payload['opt_id'] == opt_id_2

        # Now cancel the first Opt schedule
        message_type, message_payload = await asyncio.wait_for(client.cancel_opt(opt_id_1), 0.5)

        # Verify that only the Opt_id in question was removed
        assert f"{opt_id_1}_{my_ven_id}" not in server.services['eiopt_service'].opt_schedules
        assert f"{opt_id_2}_{my_ven_id}" in server.services['eiopt_service'].opt_schedules

        assert message_type == 'oadrCanceledOpt'
        assert message_payload['response']['response_code'] == 200
        assert message_payload['opt_id'] == opt_id_1
    finally:
        await server.stop()
