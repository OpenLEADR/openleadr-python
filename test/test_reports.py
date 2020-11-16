from openleadr import OpenADRClient, OpenADRServer, enable_default_logging
import asyncio
import pytest
from datetime import timedelta
from functools import partial
import logging
from random import random

loop = asyncio.get_event_loop()
loop.set_debug(True)

enable_default_logging()

async def collect_data(future=None):
    print("Collect Data")
    value = 100 * random()
    if future:
        future.set_result(value)
    return value

async def lookup_ven(ven_name=None, ven_id=None):
    """
    Look up a ven by its name or ID
    """
    return {'ven_id': '1234'}

async def receive_data(data, future=None):
    if future:
        future.set_result(data)
    pass

async def on_update_report(report, futures=None):
    if futures:
        for future in futures:
            if future.done() is False:
                future.set_result(report)
                break
    pass

async def on_register_report(resource_id, measurement, unit, scale,
                             min_sampling_interval, max_sampling_interval, bundling=1, futures=None, receive_futures=None):
    """
    Deal with this report.
    """
    print(f"Called on register report {resource_id}, {measurement}, {unit}, {scale}, {min_sampling_interval}, {max_sampling_interval}")
    if futures:
        futures.pop(0).set_result(True)
    if receive_futures:
        callback = partial(receive_data, future=receive_futures.pop(0))
    else:
        callback = receive_data
    print(f"Returning from on register report {callback}, {min_sampling_interval}")
    if bundling > 1:
        return callback, min_sampling_interval, bundling * min_sampling_interval
    return callback, min_sampling_interval

async def on_register_report_full(report, futures=None):
    """
    Deal with this report.
    """
    if futures:
        futures.pop().set_result(True)
    granularity = min(*[rd['sampling_rate']['min_period'] for rd in report['report_descriptions']])
    report_requests = [(rd['r_id'], on_update_report, granularity) for rd in report['report_descriptions'] if report['report_name'] == 'METADATA_TELEMETRY_USAGE']
    return report_requests

async def on_create_party_registration(ven_name, future=None):
    if future:
        future.set_result(True)
    ven_id = '1234'
    registration_id = 'abcd'
    return ven_id, registration_id

@pytest.mark.asyncio
async def test_report_registration():
    """
    Test the registration of two reports with two r_ids each.
    """
    # Create a server
    logger = logging.getLogger('openleadr')
    logger.setLevel(logging.DEBUG)
    server = OpenADRServer(vtn_id='testvtn')
    server.add_handler('on_register_report', on_register_report)
    server.add_handler('on_create_party_registration', on_create_party_registration)

    # Create a client
    client = OpenADRClient(ven_name='myven', vtn_url='http://localhost:8080/OpenADR2/Simple/2.0b',)

    # Add 4 reports
    client.add_report(callback=collect_data,
                      report_specifier_id='AmpereReport',
                      resource_id='Device001',
                      measurement='current',
                      unit='A')
    client.add_report(callback=collect_data,
                      report_specifier_id='AmpereReport',
                      resource_id='Device002',
                      measurement='current',
                      unit='A')
    client.add_report(callback=collect_data,
                      report_specifier_id='VoltageReport',
                      resource_id='Device001',
                      measurement='voltage',
                      unit='V')
    client.add_report(callback=collect_data,
                      report_specifier_id='VoltageReport',
                      resource_id='Device002',
                      measurement='voltage',
                      unit='V')


    asyncio.create_task(server.run_async())
    await asyncio.sleep(1)
    # Register the client
    await client.create_party_registration()

    # Register the reports
    await client.register_reports(client.reports)
    assert len(client.report_requests) == 2
    assert len(server.services['report_service'].report_callbacks) == 4
    await client.stop()
    await server.stop()

@pytest.mark.asyncio
async def test_report_registration_full():
    """
    Test the registration of two reports with two r_ids each.
    """
    # Create a server
    logger = logging.getLogger('openleadr')
    logger.setLevel(logging.DEBUG)
    server = OpenADRServer(vtn_id='testvtn')
    server.add_handler('on_register_report', on_register_report_full)
    server.add_handler('on_create_party_registration', on_create_party_registration)

    # Create a client
    client = OpenADRClient(ven_name='myven', vtn_url='http://localhost:8080/OpenADR2/Simple/2.0b',)

    # Add 4 reports
    client.add_report(callback=collect_data,
                      report_specifier_id='AmpereReport',
                      resource_id='Device001',
                      measurement='current',
                      unit='A')
    client.add_report(callback=collect_data,
                      report_specifier_id='AmpereReport',
                      resource_id='Device002',
                      measurement='current',
                      unit='A')
    client.add_report(callback=collect_data,
                      report_specifier_id='VoltageReport',
                      resource_id='Device001',
                      measurement='voltage',
                      unit='V')
    client.add_report(callback=collect_data,
                      report_specifier_id='VoltageReport',
                      resource_id='Device002',
                      measurement='voltage',
                      unit='V')


    asyncio.create_task(server.run_async())
    await asyncio.sleep(0.1)
    # Register the client
    await client.create_party_registration()

    # Register the reports
    await client.register_reports(client.reports)
    assert len(client.report_requests) == 2
    assert len(server.services['report_service'].report_callbacks) == 4
    await client.stop()
    await server.stop()

@pytest.mark.asyncio
async def test_update_reports():
    """
    Tests the timely delivery of requested reports
    """
    # Create a server
    logger = logging.getLogger('openleadr')
    logger.setLevel(logging.DEBUG)
    loop = asyncio.get_event_loop()
    server = OpenADRServer(vtn_id='testvtn')

    register_report_future_1 = loop.create_future()
    register_report_future_2 = loop.create_future()
    register_report_futures = [register_report_future_1, register_report_future_2]

    receive_report_future_1 = loop.create_future()
    receive_report_future_2 = loop.create_future()
    receive_report_future_3 = loop.create_future()
    receive_report_future_4 = loop.create_future()
    receive_report_futures = [receive_report_future_1, receive_report_future_2, receive_report_future_3, receive_report_future_4]
    server.add_handler('on_register_report', partial(on_register_report, futures=register_report_futures, receive_futures=receive_report_futures))

    party_future = loop.create_future()
    server.add_handler('on_create_party_registration', partial(on_create_party_registration, future=party_future))

    # Create a client
    client = OpenADRClient(ven_name='myven', vtn_url='http://localhost:8080/OpenADR2/Simple/2.0b')

    # Add 4 reports
    future_1 = loop.create_future()
    client.add_report(callback=partial(collect_data, future=future_1),
                      report_specifier_id='AmpereReport',
                      resource_id='Device001',
                      measurement='current',
                      sampling_rate=timedelta(seconds=2),
                      unit='A')
    future_2 = loop.create_future()
    client.add_report(callback=partial(collect_data, future=future_2),
                      report_specifier_id='AmpereReport',
                      resource_id='Device002',
                      measurement='current',
                      sampling_rate=timedelta(seconds=2),
                      unit='A')
    future_3 = loop.create_future()
    client.add_report(callback=partial(collect_data, future=future_3),
                      report_specifier_id='VoltageReport',
                      resource_id='Device001',
                      measurement='voltage',
                      sampling_rate=timedelta(seconds=2),
                      unit='V')
    future_4 = loop.create_future()
    client.add_report(callback=partial(collect_data, future=future_4),
                      report_specifier_id='VoltageReport',
                      resource_id='Device002',
                      measurement='voltage',
                      sampling_rate=timedelta(seconds=2),
                      unit='V')

    assert len(client.reports) == 2
    asyncio.create_task(server.run_async())
    await asyncio.sleep(1)

    # Run the client asynchronously
    print("Running the client")
    asyncio.create_task(client.run())

    print("Awaiting party future")
    await party_future

    print("Awaiting report futures")
    await asyncio.gather(register_report_future_1, register_report_future_2)
    await asyncio.sleep(0.1)
    assert len(server.services['report_service'].report_callbacks) == 4

    print("Awaiting data collection futures")
    await future_1
    await future_2
    await future_3
    await future_4

    print("Awaiting update report futures")
    await asyncio.gather(receive_report_future_1, receive_report_future_2, receive_report_future_3, receive_report_future_4)
    print("Done gathering")

    assert receive_report_future_1.result()[0][1] == future_1.result()
    assert receive_report_future_2.result()[0][1] == future_2.result()
    assert receive_report_future_3.result()[0][1] == future_3.result()
    assert receive_report_future_4.result()[0][1] == future_4.result()

    await client.stop()
    await server.stop()

async def get_historic_data(date_from, date_to):
    pass

async def collect_data_multi(futures=None):
    print("Data Collected")
    if futures:
        for i, future in enumerate(futures):
            if future.done() is False:
                print(f"Marking future {i} as done")
                future.set_result(True)
                break
    return 3.14

@pytest.mark.asyncio
async def test_incremental_reports():
    loop = asyncio.get_event_loop()
    client = OpenADRClient(ven_name='myven', vtn_url='http://localhost:8080/OpenADR2/Simple/2.0b')
    collect_futures = [loop.create_future() for i in range(2)]
    client.add_report(callback=partial(collect_data_multi, futures=collect_futures),
                      report_specifier_id='myhistory',
                      measurement='voltage',
                      resource_id='mydevice',
                      sampling_rate=timedelta(seconds=2))

    server = OpenADRServer(vtn_id='myvtn')

    register_report_future = loop.create_future()
    update_report_future = loop.create_future()
    server.add_handler('on_register_report', partial(on_register_report,
                                                     bundling=2,
                                                     futures=[register_report_future],
                                                     receive_futures=[update_report_future]))

    party_future = loop.create_future()
    server.add_handler('on_create_party_registration',
                       partial(on_create_party_registration, future=party_future))

    loop.create_task(server.run_async())
    await asyncio.sleep(1)
    await client.run()
    print("Awaiting party future")
    await party_future

    print("Awaiting register report future")
    await register_report_future

    print("Awaiting first data collection future... ", end="")
    await collect_futures[0]
    print("check")

    await asyncio.sleep(1)
    print("Checking that the report was not yet sent... ", end="")
    assert update_report_future.done() is False
    print("check")
    print("Awaiting data collection second future... ", end="")
    await collect_futures[1]
    print("check")

    print("Awaiting report update future")
    result = await update_report_future
    assert len(result) == 2

    await server.stop()
    await client.stop()
    await asyncio.sleep(0)


def test_add_report_invalid_unit(caplog):
    client = OpenADRClient(ven_name='myven', vtn_url='http://localhost:8080/OpenADR2/Simple/2.0b')
    client.add_report(callback=print,
                      report_specifier_id='myreport',
                      measurement='voltage',
                      resource_id='mydevice',
                      sampling_rate=timedelta(seconds=10),
                      unit='A')
    assert caplog.record_tuples == [("openleadr", logging.WARNING, f"The supplied unit A for measurement voltage will be ignored, V will be used instead.Allowed units for this measurement are: V")]

def test_add_report_invalid_scale():
    client = OpenADRClient(ven_name='myven', vtn_url='http://localhost:8080/OpenADR2/Simple/2.0b')
    with pytest.raises(ValueError):
        client.add_report(callback=print,
                          report_specifier_id='myreport',
                          measurement='current',
                          resource_id='mydevice',
                          sampling_rate=timedelta(seconds=10),
                          unit='A',
                          scale='xxx')

def test_add_report_non_standard_measurement():
    client = OpenADRClient(ven_name='myven', vtn_url='http://localhost:8080/OpenADR2/Simple/2.0b')
    client.add_report(callback=print,
                      report_specifier_id='myreport',
                      measurement='rainbows',
                      resource_id='mydevice',
                      sampling_rate=timedelta(seconds=10),
                      unit='A')

    assert client.reports[0].report_descriptions[0].measurement.item_name == 'customUnit'
    assert client.reports[0].report_descriptions[0].measurement.item_description == 'rainbows'

if __name__ == "__main__":
    asyncio.run(test_update_reports())
