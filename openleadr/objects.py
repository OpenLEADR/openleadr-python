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

from dataclasses import dataclass, field
from typing import List
from datetime import datetime, timezone, timedelta


@dataclass
class AggregatedPNode:
    node: str


@dataclass
class EndDeviceAsset:
    mrid: str


@dataclass
class MeterAsset:
    mrid: str


@dataclass
class PNode:
    node: str


@dataclass
class FeatureCollection:
    id: str
    location: dict


@dataclass
class ServiceArea:
    feature_collection: FeatureCollection


@dataclass
class ServiceDeliveryPoint:
    node: str


@dataclass
class ServiceLocation:
    node: str


@dataclass
class TransportInterface:
    point_of_receipt: str
    point_of_delivery: str


@dataclass
class Target:
    aggregated_p_node: AggregatedPNode = None
    end_device_asset: EndDeviceAsset = None
    meter_asset: MeterAsset = None
    p_node: PNode = None
    service_area: ServiceArea = None
    service_delivery_point: ServiceDeliveryPoint = None
    service_location: ServiceLocation = None
    transport_interface: TransportInterface = None
    group_id: str = None
    group_name: str = None
    resource_id: str = None
    ven_id: str = None
    party_id: str = None


@dataclass
class EventDescriptor:
    event_id: int
    modification_number: int
    market_context: str
    event_status: str

    created_date_time: datetime = None
    modification_date_time: datetime = None
    priority: int = 0
    test_event: bool = False
    vtn_comment: str = None

    def __post_init__(self):
        if self.modification_date_time is None:
            self.modification_date_time = datetime.now(timezone.utc)
        if self.created_date_time is None:
            self.created_date_time = datetime.now(timezone.utc)
        if self.modification_number is None:
            self.modification_number = 0


@dataclass
class ActivePeriod:
    dtstart: datetime
    duration: timedelta
    tolerance: dict = None
    notification: dict = None
    ramp_up: dict = None
    recovery: dict = None


@dataclass
class Interval:
    dtstart: datetime
    duration: timedelta
    signal_payload: float
    uid: int = None


@dataclass
class EventSignal:
    intervals: List[Interval]
    signal_name: str
    signal_type: str
    signal_id: str
    current_value: float = None
    targets: List[Target] = None


@dataclass
class Event:
    event_descriptor: EventDescriptor
    event_signals: List[EventSignal]
    targets: List[Target]
    active_period: ActivePeriod = None

    def __post_init__(self):
        if self.active_period is None:
            dtstart = min([i['dtstart']
                           if isinstance(i, dict) else i.dtstart
                           for s in self.event_signals for i in s.intervals])
            duration = max([i['dtstart'] + i['duration']
                            if isinstance(i, dict) else i.dtstart + i.duration
                            for s in self.event_signals for i in s.intervals]) - dtstart
            self.active_period = ActivePeriod(dtstart=dtstart,
                                              duration=duration)


@dataclass
class Response:
    response_code: int
    response_description: str
    request_id: str


@dataclass
class SamplingRate:
    min_period: timedelta = None
    max_period: timedelta = None
    on_change: bool = False


@dataclass
class PowerAttributes:
    hertz: int = 50
    voltage: int = 230
    ac: bool = True


@dataclass
class Measurement:
    item_name: str
    item_description: str
    item_units: str
    acceptable_units: List[str] = field(repr=False, default_factory=list)
    si_scale_code: str = None
    power_attributes: PowerAttributes = None

    def __post_init__(self):
        if self.item_name not in ('voltage', 'energyReal', 'energyReactive',
                                  'energyApparent', 'powerReal', 'powerApparent',
                                  'powerReactive', 'frequency',  'pulseCount', 'temperature',
                                  'therm', 'currency', 'currencyPerKW', 'currencyPerKWh',
                                  'currencyPerTherm'):
            self.item_name = 'customUnit'


@dataclass
class ReportDescription:
    r_id: str                           # Identifies a specific datapoint in a report
    market_context: str
    reading_type: str
    report_subject: Target
    report_data_source: Target
    report_type: str
    sampling_rate: SamplingRate
    measurement: Measurement = None


@dataclass
class ReportPayload:
    r_id: str
    value: float
    confidence: int = None
    accuracy: int = None


@dataclass
class ReportInterval:
    dtstart: datetime
    report_payload: ReportPayload
    duration: timedelta = None


@dataclass
class Report:
    report_specifier_id: str            # This is what the VEN calls this report
    report_name: str                    # Usually one of the default ones (enums.REPORT_NAME)
    report_request_id: str = None       # Usually empty
    report_descriptions: List[ReportDescription] = None
    created_date_time: datetime = None

    dtstart: datetime = None                # For delivering values
    duration: timedelta = None              # For delivering values
    intervals: List[ReportInterval] = None  # For delivering values
    data_collection_mode: str = 'incremental'

    def __post_init__(self):
        if self.created_date_time is None:
            self.created_date_time = datetime.now(timezone.utc)
        if self.report_descriptions is None:
            self.report_descriptions = []


@dataclass
class SpecifierPayload:
    r_id: str
    reading_type: str
    measurement: Measurement = None


@dataclass
class ReportSpecifier:
    report_specifier_id: str    # This is what the VEN called this report
    granularity: timedelta
    specifier_payloads: List[SpecifierPayload]
    report_interval: Interval = None
    report_back_duration: timedelta = None


@dataclass
class ReportRequest:
    report_request_id: str
    report_specifier: ReportSpecifier
