from openleadr import utils, objects
from dataclasses import dataclass
import pytest
from datetime import datetime, timezone, timedelta

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

def test_setmember():
    obj = {'a': 1}
    utils.setmember(obj, 'a', 10)
    assert utils.getmember(obj, 'a') == 10

    obj = dc()
    utils.setmember(obj, 'a', 10)
    assert utils.getmember(obj, 'a') == 10

@pytest.mark.asyncio
async def test_delayed_call_with_func():
    async def myfunc():
        pass
    await utils.delayed_call(myfunc, delay=0.1)

@pytest.mark.asyncio
async def test_delayed_call_with_coro():
    async def mycoro():
        pass
    await utils.delayed_call(mycoro(), delay=0.1)

@pytest.mark.asyncio
async def test_delayed_call_with_coro_func():
    async def mycoro():
        pass
    await utils.delayed_call(mycoro, delay=0.1)

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
                     'ramp_up_duration': timedelta(seconds=5)}
    assert utils.determine_event_status(active_period) == 'near'

def test_determine_event_status_far():
    active_period = {'dtstart': datetime.now(timezone.utc) + timedelta(seconds=10),
                     'duration': timedelta(seconds=5)}
    assert utils.determine_event_status(active_period) == 'far'

def test_determine_event_status_far_with_ramp_up():
    active_period = {'dtstart': datetime.now(timezone.utc) + timedelta(seconds=10),
                     'duration': timedelta(seconds=5),
                     'ramp_up_duration': timedelta(seconds=5)}
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

