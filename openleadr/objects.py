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

from dataclasses import dataclass, field, asdict, is_dataclass
from typing import List, Dict
from datetime import datetime, timezone, timedelta
from openleadr import utils
from openleadr import enums


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

    def __repr__(self):
        targets = {key: value for key, value in asdict(self).items() if value is not None}
        targets_str = ", ".join(f"{key}={value}" for key, value in targets.items())
        return f"Target('{targets_str}')"


@dataclass
class EventDescriptor:
    event_id: str
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
    notification_period: dict = None
    ramp_up_period: dict = None
    recovery_period: dict = None


@dataclass
class Interval:
    dtstart: datetime
    duration: timedelta
    signal_payload: float
    uid: int = None


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
    name: str
    description: str
    unit: str
    acceptable_units: List[str] = field(repr=False, default_factory=list)
    scale: str = None
    power_attributes: PowerAttributes = None
    pulse_factor: int = None
    ns: str = 'power'

    def __post_init__(self):
        if self.name not in enums._MEASUREMENT_NAMESPACES:
            self.name = 'customUnit'
        self.ns = enums._MEASUREMENT_NAMESPACES[self.name]


@dataclass
class EventSignal:
    intervals: List[Interval]
    signal_name: str
    signal_type: str
    signal_id: str
    current_value: float = None
    targets: List[Target] = None
    targets_by_type: Dict = None
    measurement: Measurement = None

    def __post_init__(self):
        if self.signal_type not in enums.SIGNAL_TYPE.values:
            raise ValueError(f"""The signal_type must be one of '{"', '".join(enums.SIGNAL_TYPE.values)}', """
                             f"""you specified: '{self.signal_type}'.""")
        if self.signal_name not in enums.SIGNAL_NAME.values and not self.signal_name.startswith('x-'):
            raise ValueError(f"""The signal_name must be one of '{"', '".join(enums.SIGNAL_TYPE.values)}', """
                             f"""or it must begin with 'x-'. You specified: '{self.signal_name}'""")
        if self.targets is None and self.targets_by_type is None:
            return
        elif self.targets_by_type is None:
            list_of_targets = [asdict(target) if is_dataclass(target) else target for target in self.targets]
            targets_by_type = utils.group_targets_by_type(list_of_targets)
            if len(targets_by_type) > 1:
                raise ValueError("In OpenADR, the EventSignal target may only be of type endDeviceAsset. "
                                 f"You provided types: '{', '.join(targets_by_type)}'")
        elif self.targets is None:
            self.targets = [Target(**target) for target in utils.ungroup_targets_by_type(self.targets_by_type)]
        elif self.targets is not None and self.targets_by_type is not None:
            list_of_targets = [asdict(target) if is_dataclass(target) else target for target in self.targets]
            if utils.group_targets_by_type(list_of_targets) != self.targets_by_type:
                raise ValueError("You assigned both 'targets' and 'targets_by_type' in your event, "
                                 "but the two were not consistent with each other. "
                                 f"You supplied 'targets' = {self.targets} and "
                                 f"'targets_by_type' = {self.targets_by_type}")


@dataclass
class Event:
    event_descriptor: EventDescriptor
    event_signals: List[EventSignal]
    targets: List[Target] = None
    targets_by_type: Dict = None
    active_period: ActivePeriod = None
    response_required: str = 'always'

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
        if self.targets is None and self.targets_by_type is None:
            raise ValueError("You must supply either 'targets' or 'targets_by_type'.")
        elif self.targets_by_type is None:
            list_of_targets = [asdict(target) if is_dataclass(target) else target for target in self.targets]
            self.targets_by_type = utils.group_targets_by_type(list_of_targets)
        elif self.targets is None:
            self.targets = [Target(**target) for target in utils.ungroup_targets_by_type(self.targets_by_type)]
        elif self.targets is not None and self.targets_by_type is not None:
            list_of_targets = [asdict(target) if is_dataclass(target) else target for target in self.targets]
            if utils.group_targets_by_type(list_of_targets) != self.targets_by_type:
                raise ValueError("You assigned both 'targets' and 'targets_by_type' in your event, "
                                 "but the two were not consistent with each other. "
                                 f"You supplied 'targets' = {self.targets} and "
                                 f"'targets_by_type' = {self.targets_by_type}")
        # Set the event status
        self.event_descriptor.event_status = utils.determine_event_status(self.active_period)


@dataclass
class Response:
    response_code: int
    response_description: str
    request_id: str


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
