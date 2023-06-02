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

from openleadr.utils import generate_id, group_targets_by_type
from openleadr.messaging import create_message, parse_message, validate_xml_schema
from openleadr import enums
from pprint import pprint
from termcolor import colored
from datetime import datetime, timezone, timedelta
import pytest
from pprint import pprint, pformat
from lxml import etree
from dataclasses import asdict
import re

DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"



def create_dummy_event(ven_id):
    """
    Creates a dummy event
    """
    now = datetime.now(timezone.utc)
    event_id = generate_id()
    active_period = {"dtstart": (now + timedelta(minutes=1)),
                     "duration": timedelta(minutes=9)}
    event_descriptor = {"event_id": event_id,
                        "modification_number": 1,
                        "modification_date_time": now,
                        "priority": 1,
                        "market_context": "http://MarketContext1",
                        "created_date_time": now,
                        "event_status": "near",
                        "test_event": False,
                        "vtn_comment": "This is an event"}
    event_signals = [{"intervals": [{"duration": timedelta(minutes=1), "uid": 0, "signal_payload": 8.0},
                                    {"duration": timedelta(minutes=1), "uid": 1, "signal_payload": 10.0},
                                    {"duration": timedelta(minutes=1), "uid": 2, "signal_payload": 12.0},
                                    {"duration": timedelta(minutes=1), "uid": 3, "signal_payload": 14.0},
                                    {"duration": timedelta(minutes=1), "uid": 4, "signal_payload": 16.0},
                                    {"duration": timedelta(minutes=1), "uid": 5, "signal_payload": 18.0},
                                    {"duration": timedelta(minutes=1), "uid": 6, "signal_payload": 20.0},
                                    {"duration": timedelta(minutes=1), "uid": 7, "signal_payload": 10.0},
                                    {"duration": timedelta(minutes=1), "uid": 8, "signal_payload": 20.0}],
                    "signal_name": "LOAD_CONTROL",
                    "signal_type": "x-loadControlCapacity",
                    "signal_id": generate_id(),
                    "measurement": {"name": "voltage",
                                    "description": "Voltage",
                                    "unit": "V",
                                    "scale": "none"},
                    "current_value": 0.0}]
    event_targets = [{"ven_id": 'VEN001'}, {"ven_id": 'VEN002'}]
    event = {'active_period': active_period,
             'event_descriptor': event_descriptor,
             'event_signals': event_signals,
             'targets': event_targets,
             'targets_by_type': group_targets_by_type(event_targets),
             'response_required': 'always'}
    return event

reports = [{'duration': timedelta(seconds=3600),
            'report_descriptions': [{'r_id': generate_id(),
                                     'report_subject': {'end_device_asset': {'mrid': 'meter001'}},
                                     'report_data_source': {'resource_id': 'resource001'},
                                     'report_type': 'usage',
                                     'measurement': asdict(measurement),
                                     'reading_type': 'Direct Read',
                                     'market_context': 'http://MarketContext1',
                                     'sampling_rate': {'min_period': timedelta(seconds=10), 'max_period': timedelta(seconds=30), 'on_change': False}} for measurement in enums.MEASUREMENTS.values],
            'report_specifier_id': generate_id(),
            'report_name': 'METADATA_HISTORY_USAGE',
            'report_request_id': 0,
            'created_date_time': datetime.now(timezone.utc)}]

for report in reports:
  for rd in report['report_descriptions']:
    rd['measurement'].pop('acceptable_units')
    rd['measurement'].pop('ns')
    if rd['measurement']['power_attributes'] is None:
      rd['measurement'].pop('power_attributes')
    if rd['measurement']['scale'] is None:
      rd['measurement'].pop('scale')
    if rd['measurement']['pulse_factor'] is None:
      rd['measurement'].pop('pulse_factor')

testcases = [
('oadrCanceledOpt', dict(response={'response_code': 200, 'response_description': 'OK', 'request_id': generate_id()}, opt_id=generate_id())),
('oadrCanceledPartyRegistration', dict(response={'response_code': 200, 'response_description': 'OK', 'request_id': generate_id()}, registration_id=generate_id(), ven_id='123ABC')),
('oadrCanceledReport', dict(response={'response_code': 200, 'response_description': 'OK', 'request_id': generate_id()}, pending_reports=[{'report_request_id': generate_id()}, {'report_request_id': generate_id()}], ven_id='123ABC')),
('oadrCancelOpt', dict(request_id=generate_id(), ven_id='123ABC', opt_id=generate_id())),
('oadrCancelPartyRegistration', dict(request_id=generate_id(), ven_id='123ABC', registration_id=generate_id())),
('oadrCancelReport', dict(request_id=generate_id(), ven_id='123ABC', report_request_id=generate_id(), report_to_follow=True)),
('oadrCreatedEvent', dict(response={'response_code': 200, 'response_description': 'OK', 'request_id': None},
                                 event_responses=[{'response_code': 200, 'response_description': 'OK', 'request_id': generate_id(), 'event_id': generate_id(), 'modification_number': 1, 'opt_type': 'optIn'},
                                                  {'response_code': 200, 'response_description': 'OK', 'request_id': generate_id(), 'event_id': generate_id(), 'modification_number': 1, 'opt_type': 'optIn'},
                                                  {'response_code': 200, 'response_description': 'OK', 'request_id': generate_id(), 'event_id': generate_id(), 'modification_number': 1, 'opt_type': 'optIn'}],
                                 ven_id='123ABC')),
('oadrCreatedReport', dict(response={'response_code': 200, 'response_description': 'OK', 'request_id': generate_id()}, pending_reports=[{'report_request_id': generate_id()}], ven_id='123ABC')),
('oadrCreatedReport', dict(response={'response_code': 200, 'response_description': 'OK', 'request_id': generate_id()}, pending_reports=[], ven_id='123ABC')),
('oadrCreatedReport', dict(response={'response_code': 200, 'response_description': 'OK', 'request_id': generate_id()}, pending_reports=[{'report_request_id': '123'}], ven_id='123ABC')),
('oadrCreatedReport', dict(response={'response_code': 200, 'response_description': 'OK', 'request_id': generate_id()}, pending_reports=[{'report_request_id': generate_id()}, {'report_request_id': generate_id()}], ven_id='123ABC')),
('oadrCreatedEvent', dict(response={'response_code': 200, 'response_description': 'OK', 'request_id': None},
                                 event_responses=[{'response_code': 200, 'response_description': 'OK', 'request_id': generate_id(),
                                                    'event_id': generate_id(),
                                                    'modification_number': 1,
                                                    'opt_type': 'optIn'},
                                                    {'response_code': 200, 'response_description': 'OK', 'request_id': generate_id(),
                                                    'event_id': generate_id(),
                                                    'modification_number': 1,
                                                    'opt_type': 'optOut'}],
                                 ven_id='123ABC')),
('oadrCreatedPartyRegistration', dict(response={'response_code': 200, 'response_description': 'OK', 'request_id': generate_id()},
                                             registration_id=generate_id(),
                                             ven_id='123ABC',
                                             profiles=[{'profile_name': '2.0b',
                                                        'transports': [{'transport_name': 'simpleHttp'}]}],
                                             vtn_id='VTN123')),
('oadrCreatedReport', dict(response={'response_code': 200, 'response_description': 'OK', 'request_id': generate_id()}, pending_reports=[{'report_request_id': generate_id()}, {'report_request_id': generate_id()}])),
('oadrCreateOpt', dict(opt_id=generate_id(),
                              opt_type='optIn',
                              opt_reason='participating',
                              created_date_time=datetime.now(timezone.utc),
                              request_id=generate_id(),
                              event_id=generate_id(),
                              modification_number=1,
                              targets=[{'ven_id': '123ABC'}],
                              targets_by_type=group_targets_by_type([{'ven_id': '123ABC'}]),
                              ven_id='VEN123')),
('oadrCreatePartyRegistration', dict(request_id=generate_id(), ven_id='123ABC', profile_name='2.0b', transport_name='simpleHttp', transport_address='http://localhost', report_only=False, xml_signature=False, ven_name='test', http_pull_model=True)),
('oadrCreateReport', dict(request_id=generate_id(),
                                 ven_id='123ABC',
                                 report_requests=[{'report_request_id': 'd2b7bade5f',
                                                  'report_specifier': {'granularity': timedelta(seconds=900),
                                                                       'report_back_duration': timedelta(seconds=900),
                                                                       'report_interval': {'dtstart': datetime(2019, 11, 19, 11, 0, 18, 672768, tzinfo=timezone.utc),
                                                                                           'duration': timedelta(seconds=7200)},
                                                                       'report_specifier_id': '9c8bdc00e7',
                                                                       'specifier_payloads': [{'r_id': 'd6e2e07485',
                                                                                             'reading_type': 'Direct Read'}]}}])),
('oadrDistributeEvent', dict(request_id=generate_id(), response={'request_id': 123, 'response_code': 200, 'response_description': 'OK'}, events=[create_dummy_event(ven_id='123ABC')], vtn_id='VTN123')),
('oadrDistributeEvent', dict(request_id=generate_id(), response={'request_id': 123, 'response_code': 200, 'response_description': 'OK'}, events=[create_dummy_event(ven_id='123ABC'), create_dummy_event(ven_id='123ABC')], vtn_id='VTN123')),
('oadrPoll', dict(ven_id='123ABC')),
('oadrQueryRegistration', dict(request_id=generate_id())),
('oadrRegisteredReport', dict(ven_id='VEN123', response={'response_code': 200, 'response_description': 'OK', 'request_id': generate_id()},
                                     report_requests=[{'report_request_id': generate_id(),
                                                       'report_specifier': {'report_specifier_id': generate_id(),
                                                                            'granularity': timedelta(minutes=15),
                                                                            'report_back_duration': timedelta(minutes=15),
                                                                            'report_interval': {'dtstart': datetime.now(timezone.utc),
                                                                                                'duration': timedelta(hours=2)},
                                                                            'specifier_payloads': [{'r_id': generate_id(),
                                                                                                    'reading_type': 'Direct Read'}]}},
                                                      {'report_request_id': generate_id(),
                                                       'report_specifier': {'report_specifier_id': generate_id(),
                                                                            'granularity': timedelta(minutes=15),
                                                                            'report_back_duration': timedelta(minutes=15),
                                                                            'report_interval': {'dtstart': datetime.now(timezone.utc),
                                                                                                'duration': timedelta(hours=2)},
                                                                            'specifier_payloads': [{'r_id': generate_id(),
                                                                                                    'reading_type': 'Direct Read'}]}}])),
('oadrRequestEvent', dict(request_id=generate_id(), ven_id='123ABC')),
('oadrRequestReregistration', dict(ven_id='123ABC')),
('oadrRegisterReport', dict(request_id=generate_id(), reports=[{'report_descriptions': [{
                                                                     'r_id': generate_id(),
                                                                     'report_subject': {'end_device_asset': {'mrid': 'meter001'}},
                                                                     'report_data_source': {'resource_id': '123ABC'},
                                                                     'report_type': 'reading',
                                                                     'reading_type': 'Direct Read',
                                                                     'market_context': 'http://localhost',
                                                                     'sampling_rate': {'min_period': timedelta(minutes=1), 'max_period': timedelta(minutes=1), 'on_change': True}}],
                                                                'report_request_id': generate_id(),
                                                                'report_specifier_id': generate_id(),
                                                                'report_name': 'HISTORY_USAGE',
                                                                'created_date_time': datetime.now(timezone.utc)}],
                                                        ven_id='123ABC',
                                                        report_request_id=None)),
('oadrRegisterReport', {'request_id': '8a4f859883', 'reports': [{'duration': timedelta(seconds=7200),
                                                                 'report_descriptions': [{'r_id': generate_id(),
                                                                                          'report_data_source': {'resource_id': 'resource1'},
                                                                                          'report_type': 'x-resourceStatus',
                                                                                          'reading_type': 'x-notApplicable',
                                                                                          'market_context': 'http://MarketContext1',
                                                                                          'sampling_rate': {'min_period': timedelta(seconds=60), 'max_period': timedelta(seconds=60), 'on_change': False}}],
                                                                  'report_request_id': 0,
                                                                  'report_specifier_id': '789ed6cd4e_telemetry_status',
                                                                  'report_name': 'METADATA_TELEMETRY_STATUS',
                                                                  'created_date_time': datetime(2019, 11, 20, 15, 4, 52, 638621, tzinfo=timezone.utc)},
                                                                 {'duration': timedelta(seconds=7200),
                                                                  'report_descriptions': [{'r_id': 'resource1_energy',
                                                                                           'report_data_source': {'resource_id': 'resource1'},
                                                                                           'report_type': 'usage',
                                                                                           'measurement': {'name': 'energyReal',
                                                                                                           'description': 'RealEnergy',
                                                                                                           'ns': 'power',
                                                                                                           'unit': 'Wh',
                                                                                                           'scale': 'n'},
                                                                                           'reading_type': 'Direct Read',
                                                                                           'market_context': 'http://MarketContext1',
                                                                                           'sampling_rate': {'min_period': timedelta(seconds=60), 'max_period': timedelta(seconds=60), 'on_change': False}},
                                                                                          {'r_id': 'resource1_power',
                                                                                           'report_data_source': {'resource_id': 'resource1'},
                                                                                           'report_type': 'usage',
                                                                                           'measurement': {'name': 'powerReal',
                                                                                                           'description': 'RealPower',
                                                                                                           'ns': 'power',
                                                                                                           'unit': 'W',
                                                                                                           'scale': 'n',
                                                                                                           'power_attributes': {'hertz': 50, 'voltage': 230, 'ac': True}},
                                                                                            'reading_type': 'Direct Read',
                                                                                            'market_context': 'http://MarketContext1',
                                                                                            'sampling_rate': {'min_period': timedelta(seconds=60), 'max_period': timedelta(seconds=60), 'on_change': False}}],
                                                                  'report_request_id': 0,
                                                                  'report_specifier_id': '789ed6cd4e_telemetry_usage',
                                                                  'report_name': 'METADATA_TELEMETRY_USAGE',
                                                                  'created_date_time': datetime(2019, 11, 20, 15, 4, 52, 638621, tzinfo=timezone.utc)},
                                                                 {'duration': timedelta(seconds=7200),
                                                                  'report_descriptions': [{'r_id': 'resource1_energy',
                                                                                           'report_data_source': {'resource_id': 'resource1'},
                                                                                           'report_type': 'usage',
                                                                                           'measurement': {'name': 'energyReal',
                                                                                                           'description': 'RealEnergy',
                                                                                                           'ns': 'power',
                                                                                                           'unit': 'Wh',
                                                                                                           'scale': 'n'},
                                                                                           'reading_type': 'Direct Read',
                                                                                           'market_context': 'http://MarketContext1',
                                                                                           'sampling_rate': {'min_period': timedelta(seconds=60), 'max_period': timedelta(seconds=60), 'on_change': False}},
                                                                                          {'r_id': 'resource1_power',
                                                                                           'report_data_source': {'resource_id': 'resource1'},
                                                                                           'report_type': 'usage',
                                                                                           'measurement': {'name': 'powerReal',
                                                                                                           'description': 'RealPower',
                                                                                                           'ns': 'power',
                                                                                                           'unit': 'W',
                                                                                                           'scale': 'n',
                                                                                                           'power_attributes': {'hertz': 50, 'voltage': 230, 'ac': True}},
                                                                                            'reading_type': 'Direct Read',
                                                                                            'market_context': 'http://MarketContext1',
                                                                                            'sampling_rate': {'min_period': timedelta(seconds=60), 'max_period': timedelta(seconds=60), 'on_change': False}}],
                                                                  'report_request_id': 0,
                                                                  'report_specifier_id': '789ed6cd4e_history_usage',
                                                                  'report_name': 'METADATA_HISTORY_USAGE',
                                                                  'created_date_time': datetime(2019, 11, 20, 15, 4, 52, 638621, tzinfo=timezone.utc)}], 'ven_id': 's3cc244ee6', 'report_request_id': None}),
('oadrRegisterReport', {'ven_id': 'ven123', 'request_id': generate_id(), 'reports': reports, 'report_request_id': None}),
('oadrResponse', dict(response={'response_code': 200, 'response_description': 'OK', 'request_id': generate_id()}, ven_id='123ABC')),
('oadrResponse', dict(response={'response_code': 200, 'response_description': 'OK', 'request_id': None}, ven_id='123ABC')),
('oadrUpdatedReport', dict(response={'response_code': 200, 'response_description': 'OK', 'request_id': generate_id()}, ven_id='123ABC', cancel_report={'request_id': generate_id(), 'report_request_id': [generate_id(), generate_id(), generate_id()], 'report_to_follow': False, 'ven_id': '123ABC'})),
('oadrUpdateReport', dict(request_id=generate_id(), reports=[{'report_id': generate_id(),
                                                              'report_name': enums.REPORT_NAME.values[0],
                                                              'created_date_time': datetime.now(timezone.utc),
                                                              'report_request_id': generate_id(),
                                                              'report_specifier_id': generate_id(),
                                                              'report_descriptions': [{'r_id': generate_id(),
                                                                                       'report_subject': {'end_device_asset': {'mrid': 'meter001'}},
                                                                                       'report_data_source': {'resource_id': '123ABC'},
                                                                                       'report_type': enums.REPORT_TYPE.values[0],
                                                                                       'reading_type': enums.READING_TYPE.values[0],
                                                                                       'market_context': 'http://localhost',
                                                                                       'sampling_rate': {'min_period': timedelta(minutes=1),
                                                                                                         'max_period': timedelta(minutes=2),
                                                                                                         'on_change': False}}
                                                                                        ]}], ven_id='123ABC')),
]

@pytest.mark.parametrize('message_type,data', testcases)
def test_message(message_type, data):
    # file = open('representations.rst', 'a')
    # print(f".. _{message_type}:", file=file)
    # print("", file=file)
    # print(message_type, file=file)
    # print("="*len(message_type), file=file)
    # print("", file=file)
    # print("OpenADR payload:", file=file)
    # print("", file=file)
    # print(".. code-block:: xml", file=file)
    # print("    ", file=file)
    message = create_message(message_type, **data)
    # message = re.sub(r"\s\s+","",message)
    # message = message.replace("\n","")
    # xml_lines = etree.tostring(etree.fromstring(message.replace('\n', '').encode('utf-8')), pretty_print=True).decode('utf-8').splitlines()
    # for line in xml_lines:
    #      print("    " + line, file=file)
    # print("", file=file)
    # print("OpenLEADR representation:", file=file)
    # print("    ", file=file)
    # print(".. code-block:: python3", file=file)
    # print("    ", file=file)
    validate_xml_schema(message)
    parsed = parse_message(message)[1]
    # dict_lines = pformat(parsed).splitlines()
    # for line in dict_lines:
    #     print("    " + line, file=file)
    # print("", file=file)
    # print("", file=file)
    if message_type == 'oadrRegisterReport':
        data.pop('report_request_id')
        for report in data['reports']:
            for rd in report['report_descriptions']:
                if 'measurement' in rd:
                    rd['measurement'].pop('ns')
    if message_type == 'oadrDistributeEvent':
        for event in data['events']:
            for signal in event['event_signals']:
                if 'measurement' in signal:
                    signal['measurement'].pop('ns')
    assert parsed == data
