from pyopenadr.utils import create_message, parse_message, generate_id
from pprint import pprint
from termcolor import colored
from datetime import datetime, timezone, timedelta

DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

def create_dummy_event(ven_id):
    """
    Creates a dummy event
    """
    now = datetime.now(timezone.utc)
    event_id = generate_id()
    active_period = {"dtstart": (now + timedelta(minutes=1)),
                     "duration": timedelta(minutes=10)}
    event_descriptor = {"event_id": event_id,
                        "modification_number": 1,
                        "modification_date_time": now,
                        "priority": 1,
                        "market_context": "http://MarketContext1",
                        "created_date_time": now,
                        "event_status": "near",
                        "test_event": False,
                        "vtn_comment": "This is an event"}
    event_signals = [{"intervals": [{"duration": timedelta(minutes=1), "uid": 1, "signal_payload": 8},
                                    {"duration": timedelta(minutes=1), "uid": 2, "signal_payload": 10},
                                    {"duration": timedelta(minutes=1), "uid": 3, "signal_payload": 12},
                                    {"duration": timedelta(minutes=1), "uid": 4, "signal_payload": 14},
                                    {"duration": timedelta(minutes=1), "uid": 5, "signal_payload": 16},
                                    {"duration": timedelta(minutes=1), "uid": 6, "signal_payload": 18},
                                    {"duration": timedelta(minutes=1), "uid": 7, "signal_payload": 20},
                                    {"duration": timedelta(minutes=1), "uid": 8, "signal_payload": 10},
                                    {"duration": timedelta(minutes=1), "uid": 9, "signal_payload": 20}],
                    "signal_name": "LOAD_CONTROL",
                    #"signal_name": "simple",
                    #"signal_type": "level",
                    "signal_type": "x-loadControlCapacity",
                    "signal_id": generate_id(),
                    "current_value": 12.34}]
    event_targets = [{"ven_id": 'VEN001'}, {"ven_id": 'VEN002'}]
    event = {'active_period': active_period,
             'event_descriptor': event_descriptor,
             'event_signals': event_signals,
             'targets': event_targets,
             'response_required': 'always'}
    return event

def test_message(message_type, **data):
    message = create_message(message_type, **data)
    #print(message)
    parsed = parse_message(message)[1]

    if parsed == data:
        print(colored(f"pass {message_type}", "green"))
    else:
        pprint(data)
        print(message)
        pprint(parsed)
        print(colored(f"fail {message_type}", "red"))

test_message('oadrCanceledOpt', response={'response_code': 200, 'response_description': 'OK', 'request_id': generate_id()}, opt_id=generate_id())
test_message('oadrCanceledPartyRegistration', response={'response_code': 200, 'response_description': 'OK', 'request_id': generate_id()}, registration_id=generate_id(), ven_id='123ABC')
test_message('oadrCanceledReport', response={'response_code': 200, 'response_description': 'OK', 'request_id': generate_id()}, pending_reports=[{'request_id': generate_id()}, {'request_id': generate_id()}])
test_message('oadrCanceledReport', response={'response_code': 200, 'response_description': 'OK', 'request_id': generate_id()}, pending_reports=[{'request_id': generate_id()}, {'request_id': generate_id()}], ven_id='123ABC')
test_message('oadrCancelOpt', request_id=generate_id(), ven_id='123ABC', opt_id=generate_id())
test_message('oadrCancelPartyRegistration', request_id=generate_id(), ven_id='123ABC', registration_id=generate_id())
test_message('oadrCancelReport', request_id=generate_id(), ven_id='123ABC', report_request_id=generate_id(), report_to_follow=True)
test_message('oadrCreatedEvent', response={'response_code': 200, 'response_description': 'OK', 'request_id': generate_id()},
                                 event_responses=[{'response_code': 200, 'response_description': 'OK', 'request_id': generate_id(), 'event_id': generate_id(), 'modification_number': 1, 'opt_type': 'optIn'},
                                                  {'response_code': 200, 'response_description': 'OK', 'request_id': generate_id(), 'event_id': generate_id(), 'modification_number': 1, 'opt_type': 'optIn'},
                                                  {'response_code': 200, 'response_description': 'OK', 'request_id': generate_id(), 'event_id': generate_id(), 'modification_number': 1, 'opt_type': 'optIn'}],
                                 ven_id='123ABC')
test_message('oadrCreatedReport', response={'response_code': 200, 'response_description': 'OK', 'request_id': generate_id()}, pending_reports=[{'request_id': generate_id()}, {'request_id': generate_id()}], ven_id='123ABC')
test_message('oadrCreatedEvent', response={'response_code': 200, 'response_description': 'OK', 'request_id': generate_id()},
                                 event_responses=[{'response_code': 200, 'response_description': 'OK', 'request_id': generate_id(),
                                                    'event_id': generate_id(),
                                                    'modification_number': 1,
                                                    'opt_type': 'optIn'},
                                                    {'response_code': 200, 'response_description': 'OK', 'request_id': generate_id(),
                                                    'event_id': generate_id(),
                                                    'modification_number': 1,
                                                    'opt_type': 'optOut'}],
                                 ven_id='123ABC')
test_message('oadrCreatedPartyRegistration', response={'response_code': 200, 'response_description': 'OK', 'request_id': generate_id()},
                                             registration_id=generate_id(),
                                             ven_id='123ABC',
                                             profiles=[{'profile_name': '2.0b',
                                                        'transports': [{'transport_name': 'simpleHttp'}]}],
                                             vtn_id='VTN123')
test_message('oadrCreatedReport', response={'response_code': 200, 'response_description': 'OK', 'request_id': generate_id()}, pending_reports=[{'request_id': generate_id()}, {'request_id': generate_id()}])
test_message('oadrCreateOpt', opt_id=generate_id(),
                              opt_type='optIn',
                              opt_reason='participating',
                              created_date_time=datetime.now(timezone.utc),
                              request_id=generate_id(),
                              event_id=generate_id(),
                              modification_number=1,
                              targets=[{'ven_id': '123ABC'}],
                              ven_id='VEN123')
test_message('oadrCreatePartyRegistration', request_id=generate_id(), ven_id='123ABC', profile_name='2.0b', transport_name='simpleHttp', transport_address='http://localhost', report_only=False, xml_signature=False, ven_name='test', http_pull_model=True)
test_message('oadrCreateReport', request_id=generate_id(),
                                 ven_id='123ABC',
                                 report_requests=[{'report_request_id': 'd2b7bade5f',
                                                  'report_specifier': {'granularity': timedelta(seconds=900),
                                                                       'report_back_duration': timedelta(seconds=900),
                                                                       'report_interval': {'dtstart': datetime(2019, 11, 19, 11, 0, 18, 672768, tzinfo=timezone.utc),
                                                                                           'duration': timedelta(seconds=7200),
                                                                                           'tolerance': {'tolerate': {'startafter': timedelta(seconds=300)}}},
                                                                       'report_specifier_id': '9c8bdc00e7',
                                                                       'specifier_payload': {'r_id': 'd6e2e07485',
                                                                                             'reading_type': 'Direct Read'}}}])
test_message('oadrDistributeEvent', request_id=generate_id(), response={'request_id': 123, 'response_code': 200, 'response_description': 'OK'}, events=[create_dummy_event(ven_id='123ABC')], vtn_id='VTN123')
test_message('oadrPoll', ven_id='123ABC')
test_message('oadrQueryRegistration', request_id=generate_id())
test_message('oadrRegisteredReport', ven_id='VEN123', response={'response_code': 200, 'response_description': 'OK', 'request_id': generate_id()},
                                     report_requests=[{'report_request_id': generate_id(),
                                                       'report_specifier': {'report_specifier_id': generate_id(),
                                                                            'granularity': timedelta(minutes=15),
                                                                            'report_back_duration': timedelta(minutes=15),
                                                                            'report_interval': {'dtstart': datetime.now(timezone.utc),
                                                                                                'duration': timedelta(hours=2),
                                                                                                'tolerance': {'tolerate': {'startafter': timedelta(minutes=5)}},
                                                                                                'notification': timedelta(minutes=30),
                                                                                                'ramp_up': timedelta(minutes=15),
                                                                                                'recovery': timedelta(minutes=5)},
                                                                            'specifier_payload': {'r_id': generate_id(),
                                                                                                  'reading_type': 'Direct Read'}}},
                                                      {'report_request_id': generate_id(),
                                                       'report_specifier': {'report_specifier_id': generate_id(),
                                                                            'granularity': timedelta(minutes=15),
                                                                            'report_back_duration': timedelta(minutes=15),
                                                                            'report_interval': {'dtstart': datetime.now(timezone.utc),
                                                                                                'duration': timedelta(hours=2),
                                                                                                'tolerance': {'tolerate': {'startafter': timedelta(minutes=5)}},
                                                                                                'notification': timedelta(minutes=30),
                                                                                                'ramp_up': timedelta(minutes=15),
                                                                                                'recovery': timedelta(minutes=5)},
                                                                            'specifier_payload': {'r_id': generate_id(),
                                                                                                  'reading_type': 'Direct Read'}}}])
test_message('oadrRequestEvent', request_id=generate_id(), ven_id='123ABC')
test_message('oadrRequestReregistration', ven_id='123ABC')
test_message('oadrRegisterReport', request_id=generate_id(), reports=[{'report_id': generate_id(),
                                                                       'report_descriptions': [{
                                                                            'r_id': generate_id(),
                                                                            'report_subject': {'ven_id': '123ABC'},
                                                                            'report_data_source': {'ven_id': '123ABC'},
                                                                            'report_type': 'reading',
                                                                            'reading_type': 'Direct Read',
                                                                            'market_context': 'http://localhost',
                                                                            'sampling_rate': {'min_period': timedelta(minutes=1), 'max_period': timedelta(minutes=1), 'on_change': True}}],
                                                                       'report_request_id': generate_id(),
                                                                       'report_specifier_id': generate_id(),
                                                                       'report_name': 'HISTORY_USAGE',
                                                                       'created_date_time': datetime.now(timezone.utc)}],
                                                        ven_id='123ABC',
                                                        report_request_id=generate_id())
test_message('oadrResponse', response={'response_code': 200, 'response_description': 'OK', 'request_id': generate_id()}, ven_id='123ABC')
test_message('oadrResponse', response={'response_code': 200, 'response_description': 'OK', 'request_id': None}, ven_id='123ABC')
#test_message('oadrUpdatedReport')
#test_message('oadrUpdateReport')

