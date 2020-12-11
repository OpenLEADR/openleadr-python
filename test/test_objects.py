from openleadr import objects, enums
from datetime import datetime, timedelta, timezone
from openleadr.utils import ensure_bytes
from openleadr.messaging import create_message, parse_message, validate_xml_schema
from pprint import pprint
import pytest


def test_oadr_event():
    event = objects.Event(
        event_descriptor=objects.EventDescriptor(
            event_id=1,
            modification_number=0,
            market_context='MarketContext1',
            event_status=enums.EVENT_STATUS.NEAR),
        active_period=objects.ActivePeriod(
            dtstart=datetime.now(),
            duration=timedelta(minutes=10)),
        event_signals=[objects.EventSignal(
            intervals=[
                objects.Interval(
                    dtstart=datetime.now(),
                    duration=timedelta(minutes=5),
                    uid=0,
                    signal_payload=1),
                objects.Interval(
                    dtstart=datetime.now(),
                    duration=timedelta(minutes=5),
                    uid=1,
                    signal_payload=2)],
            targets=[objects.Target(
                ven_id='1234'
            )],
            signal_name=enums.SIGNAL_NAME.LOAD_CONTROL,
            signal_type=enums.SIGNAL_TYPE.LEVEL,
            signal_id=1,
            current_value=0
        )],
        targets=[objects.Target(
            ven_id='1234'
        )]
    )

    response = objects.Response(response_code=200,
                                response_description='OK',
                                request_id='1234')
    msg = create_message('oadrDistributeEvent', response=response, events=[event])
    validate_xml_schema(ensure_bytes(msg))
    message_type, message_payload = parse_message(msg)


def test_oadr_event_targets_by_type():
    event = objects.Event(
        event_descriptor=objects.EventDescriptor(
            event_id=1,
            modification_number=0,
            market_context='MarketContext1',
            event_status=enums.EVENT_STATUS.NEAR),
        active_period=objects.ActivePeriod(
            dtstart=datetime.now(),
            duration=timedelta(minutes=10)),
        event_signals=[objects.EventSignal(
            intervals=[
                objects.Interval(
                    dtstart=datetime.now(),
                    duration=timedelta(minutes=5),
                    uid=0,
                    signal_payload=1),
                objects.Interval(
                    dtstart=datetime.now(),
                    duration=timedelta(minutes=5),
                    uid=1,
                    signal_payload=2)],
            targets=[objects.Target(
                ven_id='1234'
            )],
            signal_name=enums.SIGNAL_NAME.LOAD_CONTROL,
            signal_type=enums.SIGNAL_TYPE.LEVEL,
            signal_id=1,
            current_value=0
        )],
        targets_by_type={'ven_id': ['ven123']}
    )

    msg = create_message('oadrDistributeEvent', events=[event])
    validate_xml_schema(ensure_bytes(msg))
    message_type, message_payload = parse_message(msg)


def test_oadr_event_targets_and_targets_by_type():
    event = objects.Event(
        event_descriptor=objects.EventDescriptor(
            event_id=1,
            modification_number=0,
            market_context='MarketContext1',
            event_status=enums.EVENT_STATUS.NEAR),
        active_period=objects.ActivePeriod(
            dtstart=datetime.now(),
            duration=timedelta(minutes=10)),
        event_signals=[objects.EventSignal(
            intervals=[
                objects.Interval(
                    dtstart=datetime.now(),
                    duration=timedelta(minutes=5),
                    uid=0,
                    signal_payload=1),
                objects.Interval(
                    dtstart=datetime.now(),
                    duration=timedelta(minutes=5),
                    uid=1,
                    signal_payload=2)],
            targets=[objects.Target(
                ven_id='1234'
            )],
            signal_name=enums.SIGNAL_NAME.LOAD_CONTROL,
            signal_type=enums.SIGNAL_TYPE.LEVEL,
            signal_id=1,
            current_value=0
        )],
        targets=[{'ven_id': 'ven123'}],
        targets_by_type={'ven_id': ['ven123']}
    )

    msg = create_message('oadrDistributeEvent', events=[event])
    validate_xml_schema(ensure_bytes(msg))
    message_type, message_payload = parse_message(msg)


def test_oadr_event_targets_and_targets_by_type_invalid():
    with pytest.raises(ValueError):
        event = objects.Event(
            event_descriptor=objects.EventDescriptor(
                event_id=1,
                modification_number=0,
                market_context='MarketContext1',
                event_status=enums.EVENT_STATUS.NEAR),
            active_period=objects.ActivePeriod(
                dtstart=datetime.now(),
                duration=timedelta(minutes=10)),
            event_signals=[objects.EventSignal(
                intervals=[
                    objects.Interval(
                        dtstart=datetime.now(),
                        duration=timedelta(minutes=5),
                        uid=0,
                        signal_payload=1),
                    objects.Interval(
                        dtstart=datetime.now(),
                        duration=timedelta(minutes=5),
                        uid=1,
                        signal_payload=2)],
                targets=[objects.Target(
                    ven_id='1234'
                )],
                signal_name=enums.SIGNAL_NAME.LOAD_CONTROL,
                signal_type=enums.SIGNAL_TYPE.LEVEL,
                signal_id=1,
                current_value=0
            )],
            targets=[objects.Target(ven_id='ven456')],
            targets_by_type={'ven_id': ['ven123']}
        )

        msg = create_message('oadrDistributeEvent', events=[event])
        validate_xml_schema(ensure_bytes(msg))
        message_type, message_payload = parse_message(msg)


def test_oadr_event_no_targets():
    with pytest.raises(ValueError):
        event = objects.Event(
            event_descriptor=objects.EventDescriptor(
                event_id=1,
                modification_number=0,
                market_context='MarketContext1',
                event_status=enums.EVENT_STATUS.NEAR),
            active_period=objects.ActivePeriod(
                dtstart=datetime.now(),
                duration=timedelta(minutes=10)),
            event_signals=[objects.EventSignal(
                intervals=[
                    objects.Interval(
                        dtstart=datetime.now(),
                        duration=timedelta(minutes=5),
                        uid=0,
                        signal_payload=1),
                    objects.Interval(
                        dtstart=datetime.now(),
                        duration=timedelta(minutes=5),
                        uid=1,
                        signal_payload=2)],
                targets=[objects.Target(
                    ven_id='1234'
                )],
                signal_name=enums.SIGNAL_NAME.LOAD_CONTROL,
                signal_type=enums.SIGNAL_TYPE.LEVEL,
                signal_id=1,
                current_value=0
            )]
        )

def test_event_signal_with_grouped_targets():
    event_signal = objects.EventSignal(intervals=[objects.Interval(dtstart=datetime.now(timezone.utc),
                                                                  duration=timedelta(minutes=10),
                                                                  signal_payload=1)],
                                       signal_name='simple',
                                       signal_type='level',
                                       signal_id='signal123',
                                       targets_by_type={'ven_id': ['ven123', 'ven456']})
    assert event_signal.targets == [objects.Target(ven_id='ven123'), objects.Target(ven_id='ven456')]

def test_event_signal_with_incongruent_targets():
    with pytest.raises(ValueError):
        event_signal = objects.EventSignal(intervals=[objects.Interval(dtstart=datetime.now(timezone.utc),
                                                                      duration=timedelta(minutes=10),
                                                                      signal_payload=1)],
                                           signal_name='simple',
                                           signal_type='level',
                                           signal_id='signal123',
                                           targets=[objects.Target(ven_id='ven123')],
                                           targets_by_type={'ven_id': ['ven123', 'ven456']})


def test_event_descriptor_modification_number():
    event_descriptor = objects.EventDescriptor(event_id='event123',
                                               modification_number=None,
                                               market_context='http://marketcontext01',
                                               event_status='near')
    assert event_descriptor.modification_number == 0
