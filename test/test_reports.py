from openleadr import OpenADRClient, OpenADRServer, enable_default_logging
import asyncio
import pytest
import aiohttp
from datetime import datetime, timedelta
from functools import partial
import logging
from random import random
import time

from openleadr.messaging import create_message

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
    return {'ven_id': 'ven1234'}

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

async def on_register_report(ven_id, resource_id, measurement, unit, scale,
                             min_sampling_interval, max_sampling_interval, bundling=1, futures=None, receive_futures=None):
    """
    Deal with this report.
    """
    print(f"Called on register report {ven_id}, {resource_id}, {measurement}, {unit}, {scale}, {min_sampling_interval}, {max_sampling_interval}")
    assert resource_id in ('Device001', 'Device002')
    if futures:
        futures.pop(0).set_result(True)
    if receive_futures:
        callback = partial(receive_data, future=receive_futures.pop(0))
    else:
        callback = receive_data
    if bundling > 1:
        print(f"Returning from on register report {callback}, {min_sampling_interval}, {bundling * min_sampling_interval}")
        return callback, min_sampling_interval, bundling * min_sampling_interval
    print(f"Returning from on register report {callback}, {min_sampling_interval}")
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
    ven_id = 'ven123'
    registration_id = 'reg123'
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
                      report_specifier_id='CurrentReport',
                      resource_id='Device001',
                      measurement='current',
                      unit='A')
    client.add_report(callback=collect_data,
                      report_specifier_id='CurrentReport',
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
    #await asyncio.sleep(1)
    # Register the client
    await client.create_party_registration()

    # Register the reports
    await client.register_reports(client.reports)
    assert len(client.report_requests) == 2
    assert len(server.services['report_service'].report_callbacks) == 4
    await client.stop()
    await server.stop()

async def collect_status():
    return 1

@pytest.mark.asyncio
async def test_report_registration_with_status_report():
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
                      report_specifier_id='CurrentReport',
                      resource_id='Device001',
                      measurement='current',
                      unit='A')
    client.add_report(callback=collect_data,
                      report_specifier_id='CurrentReport',
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
    client.add_report(callback=collect_status,
                      report_name='TELEMETRY_STATUS',
                      report_specifier_id='StatusReport',
                      resource_id='Device001')

    asyncio.create_task(server.run_async())
    # await asyncio.sleep(1)
    # Register the client
    await client.create_party_registration()

    # Register the reports
    await client.register_reports(client.reports)
    assert len(client.report_requests) == 3
    assert len(server.services['report_service'].report_callbacks) == 5
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
    client = OpenADRClient(ven_name='myven', vtn_url='http://localhost:8080/OpenADR2/Simple/2.0b')

    # Add 4 reports
    client.add_report(callback=collect_data,
                      report_specifier_id='PowerReport',
                      resource_id='Device001',
                      measurement='power_real',
                      unit='W')
    client.add_report(callback=collect_data,
                      report_specifier_id='PowerReport',
                      resource_id='Device002',
                      measurement='power_real',
                      unit='W')
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


    await server.run_async()
    # await asyncio.sleep(0.1)
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
                      report_specifier_id='PowerReport',
                      resource_id='Device001',
                      measurement='power_real',
                      sampling_rate=timedelta(seconds=2),
                      unit='W')
    future_2 = loop.create_future()
    client.add_report(callback=partial(collect_data, future=future_2),
                      report_specifier_id='PowerReport',
                      resource_id='Device002',
                      measurement='power_real',
                      sampling_rate=timedelta(seconds=2),
                      unit='W')
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
    # await asyncio.sleep(1)

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
                      resource_id='Device001',
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
    # await asyncio.sleep(1)
    await client.run()
    print("Awaiting party future")
    await party_future

    print("Awaiting register report future")
    await register_report_future

    print("Awaiting first data collection future... ", end="")
    await collect_futures[0]
    print("check")

    # await asyncio.sleep(1)
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
    # await asyncio.sleep(0)



async def collect_data_history(date_from, date_to, sampling_interval, futures):
    data = [(date_from, 1.0), (date_to, 2.0)]
    if futures:
        for future in futures:
            if future.done() is False:
                future.set_result(data)
                break
    return data


@pytest.mark.asyncio
async def test_update_report_data_collection_mode_full():
    loop = asyncio.get_event_loop()

    client = OpenADRClient(ven_name='myven', vtn_url='http://localhost:8080/OpenADR2/Simple/2.0b')
    data_collection_future = loop.create_future()
    client.add_report(callback=partial(collect_data_history, futures=[data_collection_future]),
                      resource_id='Device001',
                      measurement='power_real',
                      data_collection_mode='full',
                      sampling_rate=timedelta(seconds=1),
                      unit='W')

    report_register_future = loop.create_future()
    report_received_future = loop.create_future()
    party_registration_future = loop.create_future()
    server = OpenADRServer(vtn_id='myvtn')
    server.add_handler('on_create_party_registration', partial(on_create_party_registration, future=party_registration_future))
    server.add_handler('on_register_report', partial(on_register_report,
                                                     bundling=2,
                                                     futures=[report_register_future],
                                                     receive_futures=[report_received_future]))

    await server.run_async()
    # await asyncio.sleep(0.1)

    print(f"The time is now {datetime.now()}")
    t = time.time()
    wait_for = int(t/2) * 2 + 2 - t
    # await asyncio.sleep(wait_for)
    print(f"The time is now {datetime.now()}, running client")
    await client.run()

    await party_registration_future
    await report_register_future
    # await asyncio.sleep(1)
    print(f"The time is now {datetime.now()}, checking if report was triggered")
    assert data_collection_future.done() is False

    print("Waiting for the data collection to occur")
    await data_collection_future

    print("Waiting for the report to be received")
    await report_received_future

    print("Done")
    await server.stop()
    await client.stop()


def test_add_report_invalid_unit(caplog):
    client = OpenADRClient(ven_name='myven', vtn_url='http://localhost:8080/OpenADR2/Simple/2.0b')
    client.add_report(callback=print,
                      report_specifier_id='myreport',
                      measurement='voltage',
                      resource_id='Device001',
                      sampling_rate=timedelta(seconds=10),
                      unit='A')
    assert ("openleadr", logging.WARNING, f"The supplied unit A for measurement voltage will be ignored, V will be used instead. Allowed units for this measurement are: V") in caplog.record_tuples

def test_add_report_invalid_scale():
    client = OpenADRClient(ven_name='myven', vtn_url='http://localhost:8080/OpenADR2/Simple/2.0b')
    with pytest.raises(ValueError):
        client.add_report(callback=print,
                          report_specifier_id='myreport',
                          measurement='power_real',
                          resource_id='Device001',
                          sampling_rate=timedelta(seconds=10),
                          unit='W',
                          scale='xxx')

def test_add_report_invalid_description(caplog):
    client = OpenADRClient(ven_name='myven', vtn_url='http://localhost:8080/OpenADR2/Simple/2.0b')
    client.add_report(callback=print,
                      report_specifier_id='myreport',
                      measurement={'name': 'voltage', 'description': 'SomethingWrong', 'unit': 'V'},
                      resource_id='Device001',
                      sampling_rate=timedelta(seconds=10))
    msg = create_message('oadrRegisterReport', reports=client.reports)


def test_add_report_invalid_description(caplog):
    client = OpenADRClient(ven_name='myven', vtn_url='http://localhost:8080/OpenADR2/Simple/2.0b')
    with pytest.raises(ValueError):
        client.add_report(callback=print,
                          report_specifier_id='myreport',
                          measurement={'name': 'voltage', 'description': 'SomethingWrong', 'unit': 'V'},
                          resource_id='Device001',
                          sampling_rate=timedelta(seconds=10))


def test_add_report_non_standard_measurement():
    client = OpenADRClient(ven_name='myven', vtn_url='http://localhost:8080/OpenADR2/Simple/2.0b')
    client.add_report(callback=print,
                      report_specifier_id='myreport',
                      measurement='rainbows',
                      resource_id='Device001',
                      sampling_rate=timedelta(seconds=10),
                      unit='A')
    assert len(client.reports) == 1
    assert client.reports[0].report_descriptions[0].measurement.name == 'customUnit'
    assert client.reports[0].report_descriptions[0].measurement.description == 'rainbows'


@pytest.mark.asyncio
async def test_different_on_register_report_handlers(caplog):
    def on_create_party_registration(registration_info):
        return 'ven123', 'reg123'

    def get_value():
        return 123.456

    def report_callback(data):
        pass

    def on_register_report_returning_none(ven_id, resource_id, measurement, unit, scale, min_sampling_interval, max_sampling_interval):
        return None

    def on_register_report_returning_string(ven_id, resource_id, measurement, unit, scale, min_sampling_interval, max_sampling_interval):
        return "Hello There"

    def on_register_report_returning_uncallable_first_element(ven_id, resource_id, measurement, unit, scale, min_sampling_interval, max_sampling_interval):
        return ("Hello", "There")

    def on_register_report_returning_non_datetime_second_element(ven_id, resource_id, measurement, unit, scale, min_sampling_interval, max_sampling_interval):
        return (report_callback, "Hello There")

    def on_register_report_returning_non_datetime_third_element(ven_id, resource_id, measurement, unit, scale, min_sampling_interval, max_sampling_interval):
        return (report_callback, timedelta(minutes=10), "Hello There")

    def on_register_report_returning_too_long_tuple(ven_id, resource_id, measurement, unit, scale, min_sampling_interval, max_sampling_interval):
        return (report_callback, timedelta(minutes=10), timedelta(minutes=10), "Hello")

    def on_register_report_full_returning_string(report):
        return "Hello There"

    def on_register_report_full_returning_list_of_strings(report):
        return ["Hello", "There"]

    def on_register_report_full_returning_list_of_tuples_of_wrong_length(report):
        return [("Hello", "There")]

    def on_register_report_full_returning_list_of_tuples_with_no_callable(report):
        return [("Hello", "There", "World")]

    def on_register_report_full_returning_list_of_tuples_with_no_timedelta(report):
        return [(report_callback, "Hello There")]

    server = OpenADRServer(vtn_id='myvtn')
    server.add_handler('on_create_party_registration', on_create_party_registration)

    client = OpenADRClient(ven_name='myven',
                           vtn_url='http://localhost:8080/OpenADR2/Simple/2.0b')
    client.add_report(resource_id='Device001',
                      measurement='voltage',
                      sampling_rate=timedelta(minutes=10),
                      callback=get_value)

    await server.run()
    await client.create_party_registration()
    assert client.ven_id == 'ven123'
    caplog.clear()

    await client.register_reports(client.reports)
    assert len(client.report_requests) == 0
    messages = [rec.message for rec in caplog.records if rec.levelno == logging.ERROR]
    assert len(messages) == 0
    caplog.clear()

    server.add_handler('on_register_report', on_register_report_returning_none)
    await client.register_reports(client.reports)
    assert len(client.report_requests) == 0
    messages = [rec.message for rec in caplog.records if rec.levelno == logging.ERROR]
    assert len(messages) == 0
    caplog.clear()

    server.add_handler('on_register_report', on_register_report_returning_string)
    await client.register_reports(client.reports)
    assert len(client.report_requests) == 0
    assert "Your on_register_report handler must return a tuple or None; it returned 'Hello There' (str)." in caplog.messages
    caplog.clear()

    server.add_handler('on_register_report', on_register_report_returning_uncallable_first_element)
    await client.register_reports(client.reports)
    assert len(client.report_requests) == 0
    assert(f"Your on_register_report handler did not return the correct tuple. "
           "It should return a (callback, sampling_interval) or "
           "(callback, sampling_interval, reporting_interval) tuple, where "
           "the callback is a callable function or coroutine, and "
           "sampling_interval and reporting_interval are of type datetime.timedelta. "
           "It returned: '('Hello', 'There')'. The first element was not callable.") in caplog.messages
    caplog.clear()

    server.add_handler('on_register_report', on_register_report_returning_non_datetime_second_element)
    await client.register_reports(client.reports)
    assert len(client.report_requests) == 0
    assert (f"Your on_register_report handler did not return the correct tuple. "
            "It should return a (callback, sampling_interval) or "
            "(callback, sampling_interval, reporting_interval) tuple, where "
            "sampling_interval and reporting_interval are of type datetime.timedelta. "
            f"It returned: '{(report_callback, 'Hello There')}'. The second element was not of type timedelta.") in caplog.messages
    caplog.clear()

    server.add_handler('on_register_report', on_register_report_returning_non_datetime_third_element)
    await client.register_reports(client.reports)
    assert len(client.report_requests) == 0
    assert ("Your on_register_report handler did not return the correct tuple. "
            "It should return a (callback, sampling_interval) or "
            "(callback, sampling_interval, reporting_interval) tuple, where "
            "sampling_interval and reporting_interval are of type datetime.timedelta. "
            f"It returned: '{(report_callback, timedelta(minutes=10), 'Hello There')}'. The third element was not of type timedelta.") in caplog.messages
    caplog.clear()

    server.add_handler('on_register_report', on_register_report_returning_too_long_tuple)
    await client.register_reports(client.reports)
    assert len(client.report_requests) == 0
    assert ("Your on_register_report handler returned a tuple of the wrong length. "
            "It should be 2 or 3. "
            f"It returned: '{(report_callback, timedelta(minutes=10), timedelta(minutes=10), 'Hello')}'.") in caplog.messages
    caplog.clear()

    server.add_handler('on_register_report', on_register_report_full_returning_string)
    await client.register_reports(client.reports)
    assert len(client.report_requests) == 0
    assert "Your on_register_report handler must return a list of tuples or None; it returned 'Hello There' (str)." in caplog.messages
    caplog.clear()

    server.add_handler('on_register_report', on_register_report_full_returning_list_of_strings)
    await client.register_reports(client.reports)
    assert len(client.report_requests) == 0
    assert ("Your on_register_report handler must return a list of tuples or None; "
            f"The first item from the list was 'Hello' (str).") in caplog.messages
    caplog.clear()

    server.add_handler('on_register_report', on_register_report_full_returning_list_of_tuples_of_wrong_length)
    await client.register_reports(client.reports)
    assert len(client.report_requests) == 0
    assert ("Your on_register_report handler returned tuples of the wrong length. "
            "It should be 3 or 4. It returned: '('Hello', 'There')'.") in caplog.messages
    caplog.clear()

    server.add_handler('on_register_report', on_register_report_full_returning_list_of_tuples_with_no_callable)
    await client.register_reports(client.reports)
    assert len(client.report_requests) == 0
    assert ("Your on_register_report handler did not return the correct tuple. "
            "It should return a list of (r_id, callback, sampling_interval) or "
            "(r_id, callback, sampling_interval, reporting_interval) tuples, "
            "where the r_id is a string, callback is a callable function or "
            "coroutine, and sampling_interval and reporting_interval are of "
            "type datetime.timedelta. It returned: '('Hello', 'There', 'World')'. "
            "The second element was not callable.") in caplog.messages
    caplog.clear()

    server.add_handler('on_register_report', on_register_report_full_returning_list_of_tuples_with_no_timedelta)
    await client.register_reports(client.reports)
    assert len(client.report_requests) == 0
    assert ("Your on_register_report handler returned tuples of the wrong length. "
            f"It should be 3 or 4. It returned: '({report_callback}, 'Hello There')'.") in caplog.messages

    await server.stop()
    await client.stop()


@pytest.mark.asyncio
async def test_report_registration_broken_handlers_raw_message(caplog):
    msg = """<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
<p1:oadrPayload xmlns:p1="http://openadr.org/oadr-2.0b/2012/07">
  <p1:oadrSignedObject>
    <p1:oadrRegisterReport xmlns:p3="http://docs.oasis-open.org/ns/energyinterop/201110" p3:schemaVersion="2.0b" xmlns:p2="http://docs.oasis-open.org/ns/energyinterop/201110/payloads">
      <p2:requestID>B8A6E0D2D4</p2:requestID>
      <p1:oadrReport xmlns:p3="urn:ietf:params:xml:ns:icalendar-2.0" xmlns:p4="http://docs.oasis-open.org/ns/energyinterop/201110">
        <p3:duration>
          <p3:duration>PT120M</p3:duration>
        </p3:duration>
        <p1:oadrReportDescription xmlns:p4="http://docs.oasis-open.org/ns/energyinterop/201110" xmlns:p5="http://docs.oasis-open.org/ns/emix/2011/06/power" xmlns:p6="http://docs.oasis-open.org/ns/emix/2011/06">
          <p4:rID>rid_energy_4184bb93</p4:rID>
          <p4:reportDataSource>
            <p4:resourceID>DEVICE1</p4:resourceID>
          </p4:reportDataSource>
          <p4:reportType>reading</p4:reportType>
          <p5:energyReal xmlns:p6="http://docs.oasis-open.org/ns/emix/2011/06/siscale">
            <p5:itemDescription/>
            <p5:itemUnits>Wh</p5:itemUnits>
            <p6:siScaleCode>none</p6:siScaleCode>
          </p5:energyReal>
          <p4:readingType>Direct Read</p4:readingType>
          <p6:marketContext/>
          <p1:oadrSamplingRate>
            <p1:oadrMinPeriod>PT1M</p1:oadrMinPeriod>
            <p1:oadrMaxPeriod>PT1M</p1:oadrMaxPeriod>
            <p1:oadrOnChange>false</p1:oadrOnChange>
          </p1:oadrSamplingRate>
        </p1:oadrReportDescription>
        <p1:oadrReportDescription xmlns:p4="http://docs.oasis-open.org/ns/energyinterop/201110" xmlns:p5="http://docs.oasis-open.org/ns/emix/2011/06/power" xmlns:p6="http://docs.oasis-open.org/ns/emix/2011/06">
          <p4:rID>rid_power_4184bb93</p4:rID>
          <p4:reportDataSource>
            <p4:resourceID>DEVICE1</p4:resourceID>
          </p4:reportDataSource>
          <p4:reportType>reading</p4:reportType>
          <p5:powerReal xmlns:p6="http://docs.oasis-open.org/ns/emix/2011/06/siscale">
            <p5:itemDescription/>
            <p5:itemUnits>W</p5:itemUnits>
            <p6:siScaleCode>none</p6:siScaleCode>
            <p5:powerAttributes>
              <p5:hertz>60</p5:hertz>
              <p5:voltage>120</p5:voltage>
              <p5:ac>true</p5:ac>
            </p5:powerAttributes>
          </p5:powerReal>
          <p4:readingType>Direct Read</p4:readingType>
          <p6:marketContext/>
          <p1:oadrSamplingRate>
            <p1:oadrMinPeriod>PT1M</p1:oadrMinPeriod>
            <p1:oadrMaxPeriod>PT1M</p1:oadrMaxPeriod>
            <p1:oadrOnChange>false</p1:oadrOnChange>
          </p1:oadrSamplingRate>
        </p1:oadrReportDescription>
        <p4:reportRequestID>0</p4:reportRequestID>
        <p4:reportSpecifierID>DEMO_TELEMETRY_USAGE</p4:reportSpecifierID>
        <p4:reportName>METADATA_TELEMETRY_USAGE</p4:reportName>
        <p4:createdDateTime>2020-12-15T14:10:32Z</p4:createdDateTime>
      </p1:oadrReport>
      <p3:venID>ven_id</p3:venID>
    </p1:oadrRegisterReport>
  </p1:oadrSignedObject>
</p1:oadrPayload>"""
    server = OpenADRServer(vtn_id='myvtn')
    await server.run()


    # Test with no configured callbacks

    from aiohttp import ClientSession
    async with ClientSession() as session:
        async with session.post("http://localhost:8080/OpenADR2/Simple/2.0b/EiReport",
                                  headers={'content-type': 'Application/XML'},
                                  data=msg.encode('utf-8')) as resp:
            assert resp.status == 200


    # Test with a working callback

    def report_callback(data):
        print(data)

    def working_on_register_report(ven_id, resource_id, measurement, unit, scale, min_sampling_interval, max_sampling_interval):
        return report_callback, min_sampling_interval

    server.add_handler('on_register_report', working_on_register_report)
    async with ClientSession() as session:
        async with session.post("http://localhost:8080/OpenADR2/Simple/2.0b/EiReport",
                                  headers={'content-type': 'Application/XML'},
                                  data=msg.encode('utf-8')) as resp:
            assert resp.status == 200


    # Test with a broken callback

    def broken_on_register_report(ven_id, resource_id, measurement, unit, scale, min_sampling_interval, max_sampling_interval):
        return "Hello There"

    server.add_handler('on_register_report', broken_on_register_report)
    async with ClientSession() as session:
        async with session.post("http://localhost:8080/OpenADR2/Simple/2.0b/EiReport",
                                  headers={'content-type': 'Application/XML'},
                                  data=msg.encode('utf-8')) as resp:
            assert resp.status == 200

    # assert "Your on_register_report handler must return a tuple; it returned 'Hello There' (str)." in caplog.messages


    # Test with a broken full callback

    def broken_on_register_report_full(report):
        return "Hello There Again"

    server.add_handler('on_register_report', broken_on_register_report_full)
    async with ClientSession() as session:
        async with session.post("http://localhost:8080/OpenADR2/Simple/2.0b/EiReport",
                                  headers={'content-type': 'Application/XML'},
                                  data=msg.encode('utf-8')) as resp:
            assert resp.status == 200

    assert f"Your on_register_report handler must return a list of tuples or None; it returned 'Hello There Again' (str)." in caplog.messages

    await server.stop()


@pytest.mark.asyncio
async def test_register_historic_report():
    client = OpenADRClient(ven_name='myven',
                           vtn_url='http://localhost:8080/OpenADR2/Simple/2.0b')
    client.add_report(report_name='HISTORY_USAGE',
                      callback=get_historic_data,
                      measurement='voltage',
                      resource_id='Device001',
                      sampling_rate=timedelta(seconds=1))
    server = OpenADRServer(vtn_id='myvtn')
    server.add_handler('on_create_party_registration', on_create_party_registration)
    # server.add_handler('on_register_report', on_register_report_historic)
    await server.run()
    await client.run()
    assert len(server.registered_reports) == 1
    await client.stop()
    await server.stop()


async def on_register_report_none(report):
    return None


@pytest.mark.asyncio
async def test_register_report_handler_returns_none():
    server = OpenADRServer(vtn_id='myvtn')
    server.add_handler('on_create_party_registration', on_create_party_registration)
    server.add_handler('on_register_report', on_register_report_none)

    client = OpenADRClient(ven_name='myven',
                           vtn_url='http://localhost:8080/OpenADR2/Simple/2.0b')

    client.add_report(callback=collect_data,
                      report_specifier_id='CurrentReport',
                      resource_id='Device001',
                      measurement='current',
                      unit='A')

    await server.run_async()
    await client.run()

    # Check that the report was offered to the VTN
    assert len(server.services['report_service'].registered_reports.get('ven123', [])) == 1

    # Check that the VTN did not request the report for which the handler returned None
    assert len(server.services['report_service'].requested_reports.get('ven123', [])) == 0

    # Client-side check that the report was not requested by the VTN
    assert len(client.report_requests) == 0

    await client.stop()
    await server.stop()
