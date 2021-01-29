from openleadr import utils, objects
from dataclasses import dataclass, asdict
import pytest
from datetime import datetime, timezone, timedelta
from collections import deque

@dataclass
class dc:
    a: int = 2

def test_hasmember():
    obj = {'a': 1}
    assert utils.hasmember(obj, 'a') == True
    assert utils.hasmember(obj, 'b') == False

    obj = dc()
    assert utils.hasmember(obj, 'a') == True
    assert utils.hasmember(obj, 'b') == False

def test_getmember():
    obj = {'a': 1}
    assert utils.getmember(obj, 'a') == 1

    obj = dc()
    assert utils.getmember(obj, 'a') == 2

    obj = {'a': {'b': 1}}
    assert utils.getmember(obj, 'a.b') == 1

def test_setmember():
    obj = {'a': 1}
    utils.setmember(obj, 'a', 10)
    assert utils.getmember(obj, 'a') == 10

    obj = dc()
    utils.setmember(obj, 'a', 10)
    assert utils.getmember(obj, 'a') == 10

def test_setmember_nested():
    dc_parent = dc()
    dc_parent.a = dc()

    assert utils.getmember(utils.getmember(dc_parent, 'a'), 'a') == 2
    utils.setmember(utils.getmember(dc_parent, 'a'), 'a', 3)
    assert dc_parent.a.a == 3

def test_determine_event_status_completed():
    active_period = {'dtstart': datetime.now(timezone.utc) - timedelta(seconds=10),
                     'duration': timedelta(seconds=5)}
    assert utils.determine_event_status(active_period) == 'completed'

def test_determine_event_status_active():
    active_period = {'dtstart': datetime.now(timezone.utc) - timedelta(seconds=10),
                     'duration': timedelta(seconds=15)}
    assert utils.determine_event_status(active_period) == 'active'

def test_determine_event_status_near():
    active_period = {'dtstart': datetime.now(timezone.utc) + timedelta(seconds=3),
                     'duration': timedelta(seconds=5),
                     'ramp_up_period': timedelta(seconds=5)}
    assert utils.determine_event_status(active_period) == 'near'

def test_determine_event_status_far():
    active_period = {'dtstart': datetime.now(timezone.utc) + timedelta(seconds=10),
                     'duration': timedelta(seconds=5)}
    assert utils.determine_event_status(active_period) == 'far'

def test_determine_event_status_far_with_ramp_up():
    active_period = {'dtstart': datetime.now(timezone.utc) + timedelta(seconds=10),
                     'duration': timedelta(seconds=5),
                     'ramp_up_period': timedelta(seconds=5)}
    assert utils.determine_event_status(active_period) == 'far'

def test_get_active_period_from_intervals():
    now = datetime.now(timezone.utc)
    intervals=[{'dtstart': now,
                'duration': timedelta(seconds=5)},
                {'dtstart': now + timedelta(seconds=5),
                'duration': timedelta(seconds=5)}]
    assert utils.get_active_period_from_intervals(intervals) == {'dtstart': now,
                                                                       'duration': timedelta(seconds=10)}

    intervals=[objects.Interval(dtstart=now,
                                duration=timedelta(seconds=5),
                                signal_payload=1),
               objects.Interval(dtstart=now + timedelta(seconds=5),
                                duration=timedelta(seconds=5),
                                signal_payload=2)]
    assert utils.get_active_period_from_intervals(intervals) == {'dtstart': now,
                                                                 'duration': timedelta(seconds=10)}

    assert utils.get_active_period_from_intervals(intervals, False) == objects.ActivePeriod(dtstart=now,
                                                                                            duration=timedelta(seconds=10))

def test_cron_config():
    assert utils.cron_config(timedelta(seconds=5)) == {'second': '*/5', 'minute': '*', 'hour': '*'}
    assert utils.cron_config(timedelta(minutes=1)) == {'second': '0', 'minute': '*/1', 'hour': '*'}
    assert utils.cron_config(timedelta(minutes=5)) == {'second': '0', 'minute': '*/5', 'hour': '*'}
    assert utils.cron_config(timedelta(hours=1)) == {'second': '0', 'minute': '0', 'hour': '*/1'}
    assert utils.cron_config(timedelta(hours=2)) == {'second': '0', 'minute': '0', 'hour': '*/2'}
    assert utils.cron_config(timedelta(hours=25)) == {'second': '0', 'minute': '0', 'hour': '0'}
    assert utils.cron_config(timedelta(seconds=10), randomize_seconds=True) == {'second': '*/10',
                                                                                'minute': '*',
                                                                                'hour': '*',
                                                                                'jitter': 1}


def test_validate_report_measurement_dict_missing_items(caplog):
    measurement = {'name': 'rainbows'}
    with pytest.raises(ValueError) as err:
        utils.validate_report_measurement_dict(measurement)
    assert str(err.value) == (f"The measurement dict must contain the following keys: "
                              "'name', 'description', 'unit'. Please correct this.")

def test_validate_report_measurement_dict_invalid_name(caplog):
    measurement = {'name': 'rainbows',
                   'unit': 'B',
                   'description': 'Rainbows'}
    utils.validate_report_measurement_dict(measurement)
    assert measurement['name'] == 'customUnit'
    assert (f"You provided a measurement with an unknown name rainbows. "
            "This was corrected to 'customUnit'. Please correct this in your "
            "report definition.") in caplog.messages


def test_validate_report_measurement_dict_invalid_unit():
    with pytest.raises(ValueError) as err:
        measurement = {'name': 'current',
                       'unit': 'B',
                       'description': 'Current'}
        utils.validate_report_measurement_dict(measurement)
    assert str(err.value) == (f"The unit 'B' is not acceptable for measurement 'current'. Allowed "
                              f"units are: 'A'.")


def test_validate_report_measurement_dict_invalid_description(caplog):
    with pytest.raises(ValueError) as err:
        measurement = {'name': 'current',
                       'unit': 'A',
                       'description': 'something'}
        utils.validate_report_measurement_dict(measurement)

    str(err.value) ==  (f"The measurement's description 'something' "
                        f"did not match the expected description for this type "
                        f" ('Current'). Please correct this, or use "
                        "'customUnit' as the name.")

def test_validate_report_measurement_dict_invalid_description_case(caplog):
    measurement = {'name': 'current',
                   'unit': 'A',
                   'description': 'CURRENT'}
    utils.validate_report_measurement_dict(measurement)
    assert measurement['description'] == 'Current'

    assert (f"The description for the measurement with name 'current' "
            f"was not in the correct case; you provided 'CURRENT' but "
            f"it should be 'Current'. "
            "This was automatically corrected.") in caplog.messages


def test_validate_report_measurement_dict_missing_power_attributes(caplog):
    with pytest.raises(ValueError) as err:
        measurement = {'name': 'powerReal',
                       'description': 'RealPower',
                       'unit': 'W'}
        utils.validate_report_measurement_dict(measurement)
    assert str(err.value) == ("A 'power' related measurement must contain a "
                              "'power_attributes' section that contains the following "
                              "keys: 'voltage' (int), 'ac' (boolean), 'hertz' (int)")


def test_validate_report_measurement_dict_invalid_power_attributes(caplog):
    with pytest.raises(ValueError) as err:
        measurement = {'name': 'powerReal',
                       'description': 'RealPower',
                       'unit': 'W',
                       'power_attributes': {'a': 123}}
        utils.validate_report_measurement_dict(measurement)
    assert str(err.value) == ("The power_attributes of the measurement must contain the "
                              "following keys: 'voltage' (int), 'ac' (bool), 'hertz' (int).")

def test_ungroup_target_by_type_with_single_str():
    targets_by_type = {'ven_id': 'ven123'}
    targets = utils.ungroup_targets_by_type(targets_by_type)
    assert targets == [{'ven_id': 'ven123'}]

def test_find_by_with_dict():
    search_dict = {'one': {'a': 123, 'b': 456},
                   'two': {'a': 321, 'b': 654}}
    result = utils.find_by(search_dict, 'a', 123)
    assert result == {'a': 123, 'b': 456}

def test_find_by_with_missing_member():
    search_list = [{'a': 123, 'b': 456},
                   {'a': 321, 'b': 654, 'c': 1000}]
    result = utils.find_by(search_list, 'c', 1000)
    assert result == {'a': 321, 'b': 654, 'c': 1000}

def test_find_by_nested_dict():
    search_list = [{'dict1': {'a': 123, 'b': 456}},
                   {'dict1': {'a': 321, 'b': 654, 'c': 1000}}]
    result = utils.find_by(search_list, 'dict1.c', 1000)
    assert result == {'dict1': {'a': 321, 'b': 654, 'c': 1000}}

def test_pop_by():
    search_list = [{'dict1': {'a': 123, 'b': 456}},
                   {'dict1': {'a': 321, 'b': 654, 'c': 1000}}]
    result = utils.pop_by(search_list, 'dict1.c', 1000)
    assert result == {'dict1': {'a': 321, 'b': 654, 'c': 1000}}
    assert result not in search_list

def test_ensure_str():
    assert utils.ensure_str("Hello") == "Hello"
    assert utils.ensure_str(b"Hello") == "Hello"
    assert utils.ensure_str(None) is None
    with pytest.raises(TypeError) as err:
        utils.ensure_str(1)
    assert str(err.value) == "Must be bytes or str"

def test_ensure_bytes():
    assert utils.ensure_bytes("Hello") == b"Hello"
    assert utils.ensure_bytes(b"Hello") == b"Hello"
    assert utils.ensure_bytes(None) is None
    with pytest.raises(TypeError) as err:
        utils.ensure_bytes(1)
    assert str(err.value) == "Must be bytes or str"

def test_booleanformat():
    assert utils.booleanformat("true") == "true"
    assert utils.booleanformat("false") == "false"
    assert utils.booleanformat(True) == "true"
    assert utils.booleanformat(False) == "false"
    with pytest.raises(ValueError) as err:
        assert utils.booleanformat(123)
    assert str(err.value) == "A boolean value must be provided, not 123."

def test_parse_duration():
    assert utils.parse_duration("PT1M") == timedelta(minutes=1)
    assert utils.parse_duration("PT1M5S") == timedelta(minutes=1, seconds=5)
    assert utils.parse_duration("PT1H5M10S") == timedelta(hours=1, minutes=5, seconds=10)
    assert utils.parse_duration("P1DT1H5M10S") == timedelta(days=1, hours=1, minutes=5, seconds=10)
    assert utils.parse_duration("P1M") == timedelta(days=30)
    assert utils.parse_duration("-P1M") == timedelta(days=-30)
    assert utils.parse_duration("2W") == timedelta(days=14)
    with pytest.raises(ValueError) as err:
        utils.parse_duration("Hello")
    assert str(err.value) == f"The duration 'Hello' did not match the requested format"

def test_parse_datetime():
    assert utils.parse_datetime("2020-12-15T11:29:34Z") == datetime(2020, 12, 15, 11, 29, 34, tzinfo=timezone.utc)
    assert utils.parse_datetime("2020-12-15T11:29:34.123456Z") == datetime(2020, 12, 15, 11, 29, 34, 123456, tzinfo=timezone.utc)
    assert utils.parse_datetime("2020-12-15T11:29:34.123Z") == datetime(2020, 12, 15, 11, 29, 34, 123000, tzinfo=timezone.utc)
    assert utils.parse_datetime("2020-12-15T11:29:34.123456789Z") == datetime(2020, 12, 15, 11, 29, 34, 123456, tzinfo=timezone.utc)

@pytest.mark.asyncio
async def test_await_if_required():
    def normal_func():
        return 123

    async def coro_func():
        return 456

    result = await utils.await_if_required(normal_func())
    assert result == 123

    result = await utils.await_if_required(coro_func())
    assert result == 456

    result = await utils.await_if_required(None)
    assert result == None

@pytest.mark.asyncio
async def test_gather_if_required():
    def normal_func():
        return 123

    async def coro_func():
        return 456

    raw_results = [normal_func(), normal_func(), normal_func()]
    results = await utils.gather_if_required(raw_results)
    assert results == [123, 123, 123]

    raw_results = [coro_func(), coro_func(), coro_func()]
    results = await utils.gather_if_required(raw_results)
    assert results == [456, 456, 456]

    raw_results = [coro_func(), normal_func(), None]
    results = await utils.gather_if_required(raw_results)
    assert results == [456, 123, None]

    raw_results = []
    results = await utils.gather_if_required(raw_results)
    assert results == []

def test_order_events():
    now = datetime.now(timezone.utc)
    event_1_active_high_prio = objects.Event(event_descriptor=objects.EventDescriptor(event_id='event001',
                                                                     modification_number=0,
                                                                     created_date_time=now,
                                                                     event_status='far',
                                                                     priority=1,
                                                                     market_context='http://context01'),
                                             active_period=objects.ActivePeriod(dtstart=now - timedelta(minutes=5),
                                                                                duration=timedelta(minutes=10)),
                                             event_signals=[objects.EventSignal(intervals=[objects.Interval(dtstart=now,
                                                                                                            duration=timedelta(minutes=10),
                                                                                                            signal_payload=1)],
                                                                                signal_name='simple',
                                                                                signal_type='level',
                                                                                signal_id='signal001')],
                                             targets=[{'ven_id': 'ven001'}])

    event_2_active_low_prio = objects.Event(event_descriptor=objects.EventDescriptor(event_id='event001',
                                                                     modification_number=0,
                                                                     created_date_time=now,
                                                                     event_status='far',
                                                                     priority=2,
                                                                     market_context='http://context01'),
                                            active_period=objects.ActivePeriod(dtstart=now - timedelta(minutes=5),
                                                                               duration=timedelta(minutes=10)),
                                            event_signals=[objects.EventSignal(intervals=[objects.Interval(dtstart=now,
                                                                                                           duration=timedelta(minutes=10),
                                                                                                           signal_payload=1)],
                                                                               signal_name='simple',
                                                                               signal_type='level',
                                                                               signal_id='signal001')],
                                            targets=[{'ven_id': 'ven001'}])

    event_3_active_no_prio = objects.Event(event_descriptor=objects.EventDescriptor(event_id='event001',
                                                                     modification_number=0,
                                                                     created_date_time=now,
                                                                     event_status='far',
                                                                     market_context='http://context01'),
                                            active_period=objects.ActivePeriod(dtstart=now - timedelta(minutes=5),
                                                                               duration=timedelta(minutes=10)),
                                            event_signals=[objects.EventSignal(intervals=[objects.Interval(dtstart=now,
                                                                                                           duration=timedelta(minutes=10),
                                                                                                           signal_payload=1)],
                                                                               signal_name='simple',
                                                                               signal_type='level',
                                                                               signal_id='signal001')],
                                            targets=[{'ven_id': 'ven001'}])

    event_4_far_early = objects.Event(event_descriptor=objects.EventDescriptor(event_id='event001',
                                                                     modification_number=0,
                                                                     created_date_time=now,
                                                                     event_status='far',
                                                                     market_context='http://context01'),
                                     active_period=objects.ActivePeriod(dtstart=now + timedelta(minutes=5),
                                                                        duration=timedelta(minutes=10)),
                                     event_signals=[objects.EventSignal(intervals=[objects.Interval(dtstart=now,
                                                                                                    duration=timedelta(minutes=10),
                                                                                                    signal_payload=1)],
                                                                        signal_name='simple',
                                                                        signal_type='level',
                                                                        signal_id='signal001')],
                                     targets=[{'ven_id': 'ven001'}])

    event_5_far_later = objects.Event(event_descriptor=objects.EventDescriptor(event_id='event001',
                                                                     modification_number=0,
                                                                     created_date_time=now,
                                                                     event_status='far',
                                                                     market_context='http://context01'),
                                     active_period=objects.ActivePeriod(dtstart=now + timedelta(minutes=10),
                                                                        duration=timedelta(minutes=10)),
                                     event_signals=[objects.EventSignal(intervals=[objects.Interval(dtstart=now,
                                                                                                    duration=timedelta(minutes=10),
                                                                                                    signal_payload=1)],
                                                                        signal_name='simple',
                                                                        signal_type='level',
                                                                        signal_id='signal001')],
                                     targets=[{'ven_id': 'ven001'}])

    events = [event_5_far_later, event_4_far_early, event_3_active_no_prio, event_2_active_low_prio, event_1_active_high_prio]
    ordered_events = utils.order_events(events)
    assert ordered_events == [event_1_active_high_prio, event_2_active_low_prio, event_3_active_no_prio, event_4_far_early, event_5_far_later]

    ordered_events = utils.order_events(event_1_active_high_prio)
    assert ordered_events == [event_1_active_high_prio]

    event_1_as_dict = asdict(event_1_active_high_prio)
    ordered_events = utils.order_events(event_1_as_dict)
    assert ordered_events == [event_1_as_dict]

def test_increment_modification_number():
    now = datetime.now(timezone.utc)
    event = objects.Event(event_descriptor=objects.EventDescriptor(event_id='event001',
                                                                   modification_number=0,
                                                                   created_date_time=now,
                                                                   event_status='far',
                                                                   priority=1,
                                                                   market_context='http://context01'),
                                           active_period=objects.ActivePeriod(dtstart=now - timedelta(minutes=5),
                                                                              duration=timedelta(minutes=10)),
                                           event_signals=[objects.EventSignal(intervals=[objects.Interval(dtstart=now,
                                                                                                          duration=timedelta(minutes=10),
                                                                                                          signal_payload=1)],
                                                                              signal_name='simple',
                                                                              signal_type='level',
                                                                              signal_id='signal001')],
                                           targets=[{'ven_id': 'ven001'}])

    utils.increment_event_modification_number(event)
    assert utils.getmember(event, 'event_descriptor.modification_number') == 1
    utils.increment_event_modification_number(event)
    assert utils.getmember(event, 'event_descriptor.modification_number') == 2
