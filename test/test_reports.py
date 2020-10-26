from openleadr import OpenADRClient, OpenADRServer
import asyncio
import pytest
from datetime import timedelta
from functools import partial
import logging

async def collect_data(future=None):
    # print("Collect Data")
    if future:
        future.set_result(True)
    return 3.14


async def lookup_ven(ven_name=None, ven_id=None):
    """
    Look up a ven by its name or ID
    """
    return {'ven_id': '1234'}

async def on_update_report(report, futures=None):
    if futures:
        futures.pop().set_result(True)
    pass

async def on_register_report(report, futures=None):
    """
    Deal with this report.
    """
    if futures:
        futures.pop().set_result(True)
    granularity = min(*[rd['sampling_rate']['min_period'] for rd in report['report_descriptions']])
    return (on_update_report, granularity, [rd['r_id'] for rd in report['report_descriptions'] if report['report_name'] == 'METADATA_TELEMETRY_USAGE'])

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
    client.add_report(callable=collect_data,
                      report_specifier_id='AmpereReport',
                      resource_id='Device001',
                      measurement='current',
                      unit='A')
    client.add_report(callable=collect_data,
                      report_specifier_id='AmpereReport',
                      resource_id='Device002',
                      measurement='current',
                      unit='A')
    client.add_report(callable=collect_data,
                      report_specifier_id='VoltageReport',
                      resource_id='Device001',
                      measurement='voltage',
                      unit='V')
    client.add_report(callable=collect_data,
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

    register_report_futures = [loop.create_future() for i in range(2)]
    server.add_handler('on_register_report', partial(on_register_report, futures=register_report_futures))

    party_future = loop.create_future()
    server.add_handler('on_create_party_registration', partial(on_create_party_registration, future=party_future))

    update_report_futures = [loop.create_future() for i in range(2)]
    server.add_handler('on_update_report', partial(on_update_report, futures=update_report_futures))

    # Create a client
    client = OpenADRClient(ven_name='myven', vtn_url='http://localhost:8080/OpenADR2/Simple/2.0b')

    # Add 4 reports
    future_1 = loop.create_future()
    client.add_report(callable=partial(collect_data, future=future_1),
                      report_specifier_id='AmpereReport',
                      resource_id='Device001',
                      measurement='current',
                      sampling_rate=timedelta(seconds=2),
                      unit='A')
    future_2 = loop.create_future()
    client.add_report(callable=partial(collect_data, future=future_2),
                      report_specifier_id='AmpereReport',
                      resource_id='Device002',
                      measurement='current',
                      sampling_rate=timedelta(seconds=2),
                      unit='A')
    future_3 = loop.create_future()
    client.add_report(callable=partial(collect_data, future=future_3),
                      report_specifier_id='VoltageReport',
                      resource_id='Device001',
                      measurement='voltage',
                      sampling_rate=timedelta(seconds=2),
                      unit='V')
    future_4 = loop.create_future()
    client.add_report(callable=partial(collect_data, future=future_4),
                      report_specifier_id='VoltageReport',
                      resource_id='Device002',
                      measurement='voltage',
                      sampling_rate=timedelta(seconds=2),
                      unit='V')


    assert len(client.reports) == 2
    asyncio.create_task(server.run_async())
    await asyncio.sleep(1)

    # Run the client asynchronously
    # print("Running the client")
    asyncio.create_task(client.run())

    # print("Awaiting party future")
    await party_future

    # print("Awaiting report futures")
    await asyncio.gather(*register_report_futures)

    # breakpoint()

    # print("Awaiting data collection futures")
    await future_1
    await future_2
    await future_3
    await future_4

    await asyncio.gather(*update_report_futures)
    await client.stop()
    await server.stop()

def test_add_report_invalid_unit(caplog):
    client = OpenADRClient(ven_name='myven', vtn_url='http://localhost:8080/OpenADR2/Simple/2.0b')
    client.add_report(callable=print,
                      report_specifier_id='myreport',
                      measurement='voltage',
                      resource_id='mydevice',
                      sampling_rate=timedelta(seconds=10),
                      unit='A')
    assert caplog.record_tuples == [("openleadr", logging.WARNING, f"The supplied unit A for measurement voltage will be ignored, V will be used instead.Allowed units for this measurement are: V")]

def test_add_report_invalid_scale():
    client = OpenADRClient(ven_name='myven', vtn_url='http://localhost:8080/OpenADR2/Simple/2.0b')
    with pytest.raises(ValueError):
        client.add_report(callable=print,
                          report_specifier_id='myreport',
                          measurement='current',
                          resource_id='mydevice',
                          sampling_rate=timedelta(seconds=10),
                          unit='A',
                          scale='xxx')

def test_add_report_non_standard_measurement():
    client = OpenADRClient(ven_name='myven', vtn_url='http://localhost:8080/OpenADR2/Simple/2.0b')
    client.add_report(callable=print,
                      report_specifier_id='myreport',
                      measurement='rainbows',
                      resource_id='mydevice',
                      sampling_rate=timedelta(seconds=10),
                      unit='A')

    assert client.reports[0].report_descriptions[0].measurement.item_name == 'customUnit'
    assert client.reports[0].report_descriptions[0].measurement.item_description == 'rainbows'

if __name__ == "__main__":
    asyncio.run(test_update_reports())
