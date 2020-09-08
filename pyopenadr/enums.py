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

"""
A collection of useful enumerations that you can use to construct or
interpret OpenADR messages. Can also be useful during testing.
"""

class Enum(type):
    def __getitem__(self, item):
        return getattr(self, item)

    @property
    def members(self):
        return sorted([item for item in list(set(dir(self)) - set(dir(Enum))) if not item.startswith("_")])

    @property
    def values(self):
        return [self[item] for item in self.members]

class EVENT_STATUS(metaclass=Enum):
    NONE = "none"
    FAR = "far"
    NEAR = "near"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class SIGNAL_TYPE(metaclass=Enum):
    DELTA = "delta"
    LEVEL = "level"
    MULTIPLIER = "multiplier"
    PRICE = "price"
    PRICE_MULTIPLIER = "priceMultiplier"
    PRICE_RELATIVE = "priceRelative"
    SETPOINT = "setpoint"
    X_LOAD_CONTROL_CAPACITY = "x-loadControlCapacity"
    X_LOAD_CONTROL_LEVEL_OFFSET = "x-loadControlLevelOffset"
    X_LOAD_CONTROL_PERCENT_OFFSET = "x-loadControlPorcentOffset"
    X_LOAD_CONTROL_SETPOINT = "x-loadControlSetpoint"

class SIGNAL_NAME(metaclass=Enum):
    SIMPLE = "SIMPLE"
    simple = "simple"
    ELECTRICITY_PRICE = "ELECTRICITY_PRICE"
    ENERGY_PRICE = "ENERGY_PRICE"
    DEMAND_CHARGE = "DEMAND_CHARGE"
    BID_PRICE = "BID_PRICE"
    BID_LOAD = "BID_LOAD"
    BID_ENERGY = "BID_ENERGY"
    CHARGE_STATE = "CHARGE_STATE"
    LOAD_DISPATCH = "LOAD_DISPATCH"
    LOAD_CONTROL = "LOAD_CONTROL"

class SI_SCALE_CODE(metaclass=Enum):
    p = "p"
    n = "n"
    micro = "micro"
    m = "m"
    c = "c"
    d = "d"
    k = "k"
    M = "M"
    G = "G"
    T = "T"
    none = "none"

class OPT(metaclass=Enum):
    OPT_IN = "optIn"
    OPT_OUT = "optOut"

class OPT_REASON(metaclass=Enum):
    ECONOMIC = "economic"
    EMERGENCY = "emergency"
    MUST_RUN = "mustRun"
    NOT_PARTICIPATING = "notParticipating"
    OUTAGE_RUN_STATUS = "outageRunStatus"
    OVERRIDE_STATUS = "overrideStatus"
    PARTICIPATING = "participating"
    X_SCHEDULE = "x-schedule"

class READING_TYPE(metaclass=Enum):
    DIRECT_READ = "Direct Read"
    NET = "Net"
    ALLOCATED = "Allocated"
    ESTIMATED = "Estimated"
    SUMMED = "Summed"
    DERIVED = "Derived"
    MEAN = "Mean"
    PEAK = "Peak"
    HYBRID = "Hybrid"
    CONTRACT = "Contract"
    PROJECTED = "Projected"
    X_RMS = "x-RMS"
    X_NOT_APPLICABLE = "x-notApplicable"

class REPORT_TYPE(metaclass=Enum):
    READING = "reading"
    USAGE = "usage"
    DEMAND = "demand"
    SET_POINT = "setPoint"
    DELTA_USAGE = "deltaUsage"
    DELTA_SET_POINT = "deltaSetPoint"
    DELTA_DEMAND = "deltaDemand"
    BASELINE = "baseline"
    DEVIATION = "deviation"
    AVG_USAGE = "avgUsage"
    AVG_DEMAND = "avgDemand"
    OPERATING_STATE = "operatingState"
    UP_REGULATION_CAPACITY_AVAILABLE = "upRegulationCapacityAvailable"
    DOWN_REGULATION_CAPACITY_AVAILABLE = "downRegulationCapacityAvailable"
    REGULATION_SETPOINT = "regulationSetpoint"
    STORED_ENERGY = "storedEnergy"
    TARGET_ENERGY_STORAGE = "targetEnergyStorage"
    AVAILABLE_ENERGY_STORAGE = "availableEnergyStorage"
    PRICE = "price"
    LEVEL = "level"
    POWER_FACTOR = "powerFactor"
    PERCENT_USAGE = "percentUsage"
    PERCENT_DEMAND = "percentDemand"
    X_RESOURCE_STATUS = "x-resourceStatus"

class REPORT_NAME(metaclass=Enum):
    METADATA_HISTORY_USAGE = "METADATA_HISTORY_USAGE"
    HISTORY_USAGE = "HISTORY_USAGE"
    METADATA_HISTORY_GREENBUTTON = "METADATA_HISTORY_GREENBUTTON"
    HISTORY_GREENBUTTON = "HISTORY_GREENBUTTON"
    METADATA_TELEMETRY_USAGE = "METADATA_TELEMETRY_USAGE"
    TELEMETRY_USAGE = "TELEMETRY_USAGE"
    METADATA_TELEMETRY_STATUS = "METADATA_TELEMETRY_STATUS"
    TELEMETRY_STATUS = "TELEMETRY_STATUS"

class STATUS_CODES(metaclass=Enum):
    OUT_OF_SEQUENCE  = 450
    NOT_ALLOWED      = 451
    INVALID_ID       = 452
    NOT_RECOGNIZED   = 453
    INVALID_DATA     = 454
    COMPLIANCE_ERROR = 459
    SIGNAL_NOT_SUPPORTED = 460
    REPORT_NOT_SUPPORTED = 461
    TARGET_MISMATCH = 462
    NOT_REGISTERED_OR_AUTHORIZED = 463
    DEPLOYMENT_ERROR_OTHER = 469

class SECURITY_LEVEL:
    STANDARD: 'STANDARD'
    HIGH: 'HIGH'