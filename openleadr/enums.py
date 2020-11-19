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
from openleadr import objects


class Enum(type):
    def __getitem__(self, item):
        return getattr(self, item)

    @property
    def members(self):
        return sorted([item for item in list(set(dir(self)) - set(dir(Enum)))
                       if not item.startswith("_")])

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
    OUT_OF_SEQUENCE = 450
    NOT_ALLOWED = 451
    INVALID_ID = 452
    NOT_RECOGNIZED = 453
    INVALID_DATA = 454
    COMPLIANCE_ERROR = 459
    SIGNAL_NOT_SUPPORTED = 460
    REPORT_NOT_SUPPORTED = 461
    TARGET_MISMATCH = 462
    NOT_REGISTERED_OR_AUTHORIZED = 463
    DEPLOYMENT_ERROR_OTHER = 469


class SECURITY_LEVEL:
    STANDARD = 'STANDARD'
    HIGH = 'HIGH'


_CURRENCIES = ("AFN", "ALL", "AMD", "ANG", "AOA", "ARS", "AUD", "AWG", "AZN", "BAM",
               "BBD", "BDT", "BGN", "BHD", "BIF", "BMD", "BND", "BOB", "BOV", "BRL",
               "BSD", "BTN", "BWP", "BYR", "BZD", "CAD", "CDF", "CHE", "CHF", "CHW",
               "CLF", "CLP", "CNY", "COP", "COU", "CRC", "CUC", "CUP", "CVE", "CZK",
               "DJF", "DKK", "DOP", "DZD", "EEK", "EGP", "ERN", "ETB", "EUR", "FJD",
               "FKP", "GBP", "GEL", "GHS", "GIP", "GMD", "GNF", "GTQ", "GWP", "GYD",
               "HKD", "HNL", "HRK", "HTG", "HUF", "IDR", "ILS", "INR", "IQD", "IRR",
               "ISK", "JMD", "JOD", "JPY", "KES", "KGS", "KHR", "KMF", "KPW", "KRW",
               "KWD", "KYD", "KZT", "LAK", "LBP", "LKR", "LRD", "LSL", "LTL", "LVL",
               "LYD", "MAD", "MAD", "MDL", "MGA", "MKD", "MMK", "MNT", "MOP", "MRO",
               "MUR", "MVR", "MWK", "MXN", "MXV", "MYR", "MZN", "NAD", "NGN", "NIO",
               "NOK", "NPR", "NZD", "OMR", "PAB", "PEN", "PGK", "PHP", "PKR", "PLN",
               "PYG", "QAR", "RON", "RSD", "RUB", "RWF", "SAR", "SBD", "SCR", "SDG",
               "SEK", "SGD", "SHP", "SLL", "SOS", "SRD", "STD", "SVC", "SYP", "SZL",
               "THB", "TJS", "TMT", "TND", "TOP", "TRY", "TTD", "TWD", "TZS", "UAH",
               "UGX", "USD", "USN", "USS", "UYI", "UYU", "UZS", "VEF", "VND", "VUV",
               "WST", "XAF", "XAG", "XAU", "XBA", "XBB", "XBC", "XBD", "XCD", "XDR",
               "XFU", "XOF", "XPD", "XPF", "XPF", "XPF", "XPT", "XTS", "XXX", "YER",
               "ZAR", "ZMK", "ZWL")


class MEASUREMENTS(metaclass=Enum):
    VOLTAGE = objects.Measurement(item_name='voltage',
                                  item_description='Voltage',
                                  item_units='V',
                                  acceptable_units=('V',),
                                  si_scale_code='none')
    # CURRENT = objects.Measurement(item_name='current',
    #                               item_description='Current',
    #                               item_units='A',
    #                               acceptable_units=('A',),
    #                               si_scale_code='none')
    ENERGY_REAL = objects.Measurement(item_name='energyReal',
                                      item_description='RealEnergy',
                                      item_units='Wh',
                                      acceptable_units=('Wh',),
                                      si_scale_code='none')
    REAL_ENERGY = objects.Measurement(item_name='energyReal',
                                      item_description='RealEnergy',
                                      item_units='Wh',
                                      acceptable_units=('Wh',),
                                      si_scale_code='none')
    ACTIVE_ENERGY = objects.Measurement(item_name='energyReal',
                                        item_description='RealEnergy',
                                        item_units='Wh',
                                        acceptable_units=('Wh',),
                                        si_scale_code='none')
    ENERGY_REACTIVE = objects.Measurement(item_name='energyReal',
                                          item_description='RealEnergy',
                                          item_units='VArh',
                                          acceptable_units=('VArh',),
                                          si_scale_code='none')
    REACTIVE_ENERGY = objects.Measurement(item_name='energyReal',
                                          item_description='RealEnergy',
                                          item_units='VArh',
                                          acceptable_units=('VArh',),
                                          si_scale_code='none')
    ENERGY_APPARENT = objects.Measurement(item_name='energyReal',
                                          item_description='ApparentEnergy',
                                          item_units='VAh',
                                          acceptable_units=('VAh',),
                                          si_scale_code='none')
    APPARENT_ENERGY = objects.Measurement(item_name='energyReal',
                                          item_description='ApparentEnergy',
                                          item_units='VAh',
                                          acceptable_units=('VAh',),
                                          si_scale_code='none')
    ACTIVE_POWER = objects.Measurement(item_name='powerReal',
                                       item_description='RealPower',
                                       item_units='W',
                                       acceptable_units=('W',),
                                       si_scale_code='none',
                                       power_attributes=objects.PowerAttributes(hertz=50,
                                                                                voltage=230,
                                                                                ac=True))
    REAL_POWER = objects.Measurement(item_name='powerReal',
                                     item_description='RealPower',
                                     item_units='W',
                                     acceptable_units=('W',),
                                     si_scale_code='none',
                                     power_attributes=objects.PowerAttributes(hertz=50,
                                                                              voltage=230,
                                                                              ac=True))
    POWER_REAL = objects.Measurement(item_name='powerReal',
                                     item_description='RealPower',
                                     item_units='W',
                                     acceptable_units=('W',),
                                     si_scale_code='none',
                                     power_attributes=objects.PowerAttributes(hertz=50,
                                                                              voltage=230,
                                                                              ac=True))
    REACTIVE_POWER = objects.Measurement(item_name='powerReactive',
                                         item_description='ReactivePower',
                                         item_units='VAr',
                                         acceptable_units=('VAr',),
                                         si_scale_code='none',
                                         power_attributes=objects.PowerAttributes(hertz=50,
                                                                                  voltage=230,
                                                                                  ac=True))
    POWER_REACTIVE = objects.Measurement(item_name='powerReactive',
                                         item_description='ReactivePower',
                                         item_units='VAr',
                                         acceptable_units=('VAr',),
                                         si_scale_code='none',
                                         power_attributes=objects.PowerAttributes(hertz=50,
                                                                                  voltage=230,
                                                                                  ac=True))
    APPARENT_POWER = objects.Measurement(item_name='powerApparent',
                                         item_description='ApparentPower',
                                         item_units='VA',
                                         acceptable_units=('VA',),
                                         si_scale_code='none',
                                         power_attributes=objects.PowerAttributes(hertz=50,
                                                                                  voltage=230,
                                                                                  ac=True))
    POWER_APPARENT = objects.Measurement(item_name='powerApparent',
                                         item_description='ApparentPower',
                                         item_units='VA',
                                         acceptable_units=('VA',),
                                         si_scale_code='none',
                                         power_attributes=objects.PowerAttributes(hertz=50,
                                                                                  voltage=230,
                                                                                  ac=True))
    FREQUENCY = objects.Measurement(item_name='frequency',
                                    item_description='Frequency',
                                    item_units='Hz',
                                    acceptable_units=('Hz',),
                                    si_scale_code='none')
    PULSE_COUNT = objects.Measurement(item_name='pulseCount',
                                      item_description='pulse count',
                                      item_units='count',
                                      acceptable_units=('count',),
                                      si_scale_code='none')
    TEMPERATURE = objects.Measurement(item_name='temperature',
                                      item_description='temperature',
                                      item_units='celsius',
                                      acceptable_units=('celsius', 'fahrenheit'),
                                      si_scale_code='none')
    THERM = objects.Measurement(item_name='therm',
                                item_description='Therm',
                                item_units='thm',
                                acceptable_units=('thm',),
                                si_scale_code='none')
    CURRENCY = objects.Measurement(item_name='currency',
                                   item_description='Currency',
                                   item_units='USD',
                                   acceptable_units=_CURRENCIES,
                                   si_scale_code='none')
    CURRENCY_PER_KW = objects.Measurement(item_name='currencyPerKW',
                                          item_description='CurrencyPerKW',
                                          item_units='USD',
                                          acceptable_units=_CURRENCIES,
                                          si_scale_code='none')
    CURRENCY_PER_KWH = objects.Measurement(item_name='currencyPerKWh',
                                           item_description='CurrencyPerKWh',
                                           item_units='USD',
                                           acceptable_units=_CURRENCIES,
                                           si_scale_code='none')
    CURRENCY_PER_THERM = objects.Measurement(item_name='currencyPerTherm',
                                             item_description='CurrencyPerTherm',
                                             item_units='USD',
                                             acceptable_units=_CURRENCIES,
                                             si_scale_code='none')
