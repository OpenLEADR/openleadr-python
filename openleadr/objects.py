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

from dataclasses import dataclass
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
        print("Calling Post Init")
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
    current_value: float
    targets: List[Target] = None

@dataclass
class Event:
    event_descriptor: EventDescriptor
    active_period: ActivePeriod
    event_signals: EventSignal
    targets: List[Target]

@dataclass
class Response:
    response_code: int
    response_description: str
    request_id: str
