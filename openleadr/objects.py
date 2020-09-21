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

class objdict(dict):
    def __getattr__(self, name):
        if name in self:
            return self[name]
        else:
            raise AttributeError("No such attribute: " + name)

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        if name in self:
            del self[name]
        else:
            raise AttributeError("No such attribute: " + name)

@dataclass
class AggregatedPNode(objdict):
    node: str

@dataclass
class EndDeviceAsset(objdict):
    mrid: str

@dataclass
class MeterAsset(objdict):
    mrid: str

@dataclass
class PNode(objdict):
    node: str

@dataclass
class FeatureCollection(objdict):
    id: str
    location: dict

@dataclass
class ServiceArea(objdict):
    feature_collection: FeatureCollection

@dataclass
class ServiceDeliveryPoint(objdict):
    node: str

@dataclass
class ServiceLocation(objdict):
    node: str

@dataclass
class TransportInterface(objdict):
    point_of_receipt: str
    point_of_delivery: str

@dataclass
class Target(objdict):
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
class EventDescriptor(objdict):
    event_id: int
    modification_number: int
    market_context: str
    event_status: str

    created_date_time: datetime = None
    modification_date: datetime = None
    priority: int = 0
    test_event: bool = False
    vtn_comment: str = None

    def __post_init__(self):
        if self.modification_date is None:
            self.modification_date = datetime.now(timezone.utc)
        if self.created_date_time is None:
            self.created_date_time = datetime.now(timezone.utc)
        if self.modification_number is None:
            self.modification_number = 0
        if not isinstance(self.test_event, bool):
            self.test_event = False

@dataclass
class ActivePeriod(objdict):
    dtstart: datetime
    duration: timedelta
    tolerance: dict = None
    notification: dict = None
    ramp_up: dict = None
    recovery: dict = None

@dataclass
class Interval(objdict):
    dtstart: datetime
    duration: timedelta
    signal_payload: float
    uid: int = None

@dataclass
class EventSignal(objdict):
    intervals: List[Interval]
    target: Target
    signal_name: str
    signal_type: str
    signal_id: str
    current_value: float

@dataclass
class Event(objdict):
    event_descriptor: EventDescriptor
    active_period: ActivePeriod
    event_signals: EventSignal
    target: Target

@dataclass
class Response(objdict):
    response_code: int
    response_description: str
    request_id: str
