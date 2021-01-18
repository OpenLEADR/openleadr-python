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
from openleadr.objects import Measurement, PowerAttributes


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
    X_LOAD_CONTROL_PERCENT_OFFSET = "x-loadControlPercentOffset"
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


class SIGNAL_TARGET_MRID(metaclass=Enum):
    THERMOSTAT = "Thermostat"
    STRIP_HEATER = "Strip_Heater"
    BASEBOARD_HEATER = "Baseboard_Heater"
    WATER_HEATER = "Water_Heater"
    POOL_PUMP = "Pool_Pump"
    SAUNA = "Sauna"
    HOT_TUB = "Hot_tub"
    SMART_APPLIANCE = "Smart_Appliance"
    IRRIGATION_PUMP = "Irrigation_Pump"
    MANAGED_COMMERCIAL_AND_INDUSTRIAL_LOADS = "Managed_Commercial_and_Industrial_Loads"
    SIMPLE_RESIDENTIAL_ON_OFF_LOADS = "Simple_Residential_On_Off_Loads"
    EXTERIOR_LIGHTING = "Exterior_Lighting"
    INTERIOR_LIGHTING = "Interior_Lighting"
    ELECTRIC_VEHICLE = "Electric_Vehicle"
    GENERATION_SYSTEMS = "Generation_Systems"
    LOAD_CONTROL_SWITCH = "Load_Control_Switch"
    SMART_INVERTER = "Smart_Inverter"
    EVSE = "EVSE"
    RESU = "RESU"
    ENERGY_MANAGEMENT_SYSTEM = "Energy_Management_System"
    SMART_ENERGY_MODULE = "Smart_Energy_Module"
    STORAGE = "Storage"


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
    DEPLOYMENT_ERROR_OR_OTHER_ERROR = 469


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

_ACCEPTABLE_UNITS = {'currency': _CURRENCIES,
                     'currencyPerKW': _CURRENCIES,
                     'currencyPerKWh': _CURRENCIES,
                     'currencyPerThm': _CURRENCIES,
                     'current': ('A',),
                     'energyApparent': ('VAh',),
                     'energyReactive': ('VARh',),
                     'energyReal': ('Wh',),
                     'frequency': ('Hz',),
                     'powerApparent': ('VA',),
                     'powerReactive': ('VAR',),
                     'powerReal': ('W',),
                     'pulseCount': ('count',),
                     'temperature': ('celsius', 'fahrenheit'),
                     'Therm': ('thm',),
                     'voltage': ('V',)}

_MEASUREMENT_DESCRIPTIONS = {'currency': 'currency',
                             'currencyPerKW': 'currencyPerKW',
                             'currencyPerKWh': 'currencyPerKWh',
                             'currencyPerThm': 'currency',
                             'current': 'Current',
                             'energyApparent': 'ApparentEnergy',
                             'energyReactive': 'ReactiveEnergy',
                             'energyReal': 'RealEnergy',
                             'frequency': 'Frequency',
                             'powerApparent': 'ApparentPower',
                             'powerReactive': 'ReactivePower',
                             'powerReal': 'RealPower',
                             'pulseCount': 'pulse count',
                             'temperature': 'temperature',
                             'Therm': 'Therm',
                             'voltage': 'Voltage'}

_MEASUREMENT_NAMESPACES = {'currency': 'oadr',
                           'currencyPerWK': 'oadr',
                           'currencyPerKWh': 'oadr',
                           'currencyPerThm': 'oadr',
                           'current': 'oadr',
                           'energyApparent': 'power',
                           'energyReactive': 'power',
                           'energyReal': 'power',
                           'frequency': 'oadr',
                           'powerApparent': 'power',
                           'powerReactive': 'power',
                           'powerReal': 'power',
                           'pulseCount': 'oadr',
                           'temperature': 'oadr',
                           'Therm': 'oadr',
                           'voltage': 'power',
                           'customUnit': 'oadr'}


class MEASUREMENTS(metaclass=Enum):
    VOLTAGE = Measurement(name='voltage',
                          description=_MEASUREMENT_DESCRIPTIONS['voltage'],
                          unit=_ACCEPTABLE_UNITS['voltage'][0],
                          acceptable_units=_ACCEPTABLE_UNITS['voltage'],
                          scale='none')
    CURRENT = Measurement(name='current',
                          description=_MEASUREMENT_DESCRIPTIONS['current'],
                          unit=_ACCEPTABLE_UNITS['current'][0],
                          acceptable_units=_ACCEPTABLE_UNITS['current'],
                          scale='none')
    ENERGY_REAL = Measurement(name='energyReal',
                              description=_MEASUREMENT_DESCRIPTIONS['energyReal'],
                              unit=_ACCEPTABLE_UNITS['energyReal'][0],
                              acceptable_units=_ACCEPTABLE_UNITS['energyReal'],
                              scale='none')
    REAL_ENERGY = Measurement(name='energyReal',
                              description=_MEASUREMENT_DESCRIPTIONS['energyReal'],
                              unit=_ACCEPTABLE_UNITS['energyReal'][0],
                              acceptable_units=_ACCEPTABLE_UNITS['energyReal'],
                              scale='none')
    ACTIVE_ENERGY = Measurement(name='energyReal',
                                description=_MEASUREMENT_DESCRIPTIONS['energyReal'],
                                unit=_ACCEPTABLE_UNITS['energyReal'][0],
                                acceptable_units=_ACCEPTABLE_UNITS['energyReal'],
                                scale='none')
    ENERGY_REACTIVE = Measurement(name='energyReactive',
                                  description=_MEASUREMENT_DESCRIPTIONS['energyReactive'],
                                  unit=_ACCEPTABLE_UNITS['energyReactive'][0],
                                  acceptable_units=_ACCEPTABLE_UNITS['energyReactive'],
                                  scale='none')
    REACTIVE_ENERGY = Measurement(name='energyReactive',
                                  description=_MEASUREMENT_DESCRIPTIONS['energyReactive'],
                                  unit=_ACCEPTABLE_UNITS['energyReactive'][0],
                                  acceptable_units=_ACCEPTABLE_UNITS['energyReactive'],
                                  scale='none')
    ENERGY_APPARENT = Measurement(name='energyApparent',
                                  description=_MEASUREMENT_DESCRIPTIONS['energyApparent'],
                                  unit=_ACCEPTABLE_UNITS['energyApparent'][0],
                                  acceptable_units=_ACCEPTABLE_UNITS['energyApparent'],
                                  scale='none')
    APPARENT_ENERGY = Measurement(name='energyApparent',
                                  description=_MEASUREMENT_DESCRIPTIONS['energyApparent'],
                                  unit=_ACCEPTABLE_UNITS['energyApparent'][0],
                                  acceptable_units=_ACCEPTABLE_UNITS['energyApparent'],
                                  scale='none')
    ACTIVE_POWER = Measurement(name='powerReal',
                               description=_MEASUREMENT_DESCRIPTIONS['powerReal'],
                               unit=_ACCEPTABLE_UNITS['powerReal'][0],
                               acceptable_units=_ACCEPTABLE_UNITS['powerReal'],
                               scale='none',
                               power_attributes=PowerAttributes(hertz=50,
                                                                voltage=230,
                                                                ac=True))
    REAL_POWER = Measurement(name='powerReal',
                             description=_MEASUREMENT_DESCRIPTIONS['powerReal'],
                             unit=_ACCEPTABLE_UNITS['powerReal'][0],
                             acceptable_units=_ACCEPTABLE_UNITS['powerReal'],
                             scale='none',
                             power_attributes=PowerAttributes(hertz=50,
                                                              voltage=230,
                                                              ac=True))
    POWER_REAL = Measurement(name='powerReal',
                             description=_MEASUREMENT_DESCRIPTIONS['powerReal'],
                             unit=_ACCEPTABLE_UNITS['powerReal'][0],
                             acceptable_units=_ACCEPTABLE_UNITS['powerReal'],
                             scale='none',
                             power_attributes=PowerAttributes(hertz=50,
                                                              voltage=230,
                                                              ac=True))
    REACTIVE_POWER = Measurement(name='powerReactive',
                                 description=_MEASUREMENT_DESCRIPTIONS['powerReactive'],
                                 unit=_ACCEPTABLE_UNITS['powerReactive'][0],
                                 acceptable_units=_ACCEPTABLE_UNITS['powerReactive'],
                                 scale='none',
                                 power_attributes=PowerAttributes(hertz=50,
                                                                  voltage=230,
                                                                  ac=True))
    POWER_REACTIVE = Measurement(name='powerReactive',
                                 description=_MEASUREMENT_DESCRIPTIONS['powerReactive'],
                                 unit=_ACCEPTABLE_UNITS['powerReactive'][0],
                                 acceptable_units=_ACCEPTABLE_UNITS['powerReactive'],
                                 scale='none',
                                 power_attributes=PowerAttributes(hertz=50,
                                                                  voltage=230,
                                                                  ac=True))
    APPARENT_POWER = Measurement(name='powerApparent',
                                 description=_MEASUREMENT_DESCRIPTIONS['powerApparent'],
                                 unit=_ACCEPTABLE_UNITS['powerApparent'][0],
                                 acceptable_units=_ACCEPTABLE_UNITS['powerApparent'],
                                 scale='none',
                                 power_attributes=PowerAttributes(hertz=50,
                                                                  voltage=230,
                                                                  ac=True))
    POWER_APPARENT = Measurement(name='powerApparent',
                                 description=_MEASUREMENT_DESCRIPTIONS['powerApparent'],
                                 unit=_ACCEPTABLE_UNITS['powerApparent'][0],
                                 acceptable_units=_ACCEPTABLE_UNITS['powerApparent'],
                                 scale='none',
                                 power_attributes=PowerAttributes(hertz=50,
                                                                  voltage=230,
                                                                  ac=True))
    FREQUENCY = Measurement(name='frequency',
                            description=_MEASUREMENT_DESCRIPTIONS['frequency'],
                            unit=_ACCEPTABLE_UNITS['frequency'][0],
                            acceptable_units=_ACCEPTABLE_UNITS['frequency'],
                            scale='none')
    PULSE_COUNT = Measurement(name='pulseCount',
                              description=_MEASUREMENT_DESCRIPTIONS['pulseCount'],
                              unit=_ACCEPTABLE_UNITS['pulseCount'][0],
                              acceptable_units=_ACCEPTABLE_UNITS['pulseCount'],
                              pulse_factor=1000)
    TEMPERATURE = Measurement(name='temperature',
                              description=_MEASUREMENT_DESCRIPTIONS['temperature'],
                              unit=_ACCEPTABLE_UNITS['temperature'][0],
                              acceptable_units=_ACCEPTABLE_UNITS['temperature'],
                              scale='none')
    THERM = Measurement(name='Therm',
                        description=_MEASUREMENT_DESCRIPTIONS['Therm'],
                        unit=_ACCEPTABLE_UNITS['Therm'][0],
                        acceptable_units=_ACCEPTABLE_UNITS['Therm'],
                        scale='none')
    CURRENCY = Measurement(name='currency',
                           description=_MEASUREMENT_DESCRIPTIONS['currency'],
                           unit=_CURRENCIES[0],
                           acceptable_units=_CURRENCIES,
                           scale='none')
    CURRENCY_PER_KW = Measurement(name='currencyPerKW',
                                  description=_MEASUREMENT_DESCRIPTIONS['currencyPerKW'],
                                  unit=_CURRENCIES[0],
                                  acceptable_units=_CURRENCIES,
                                  scale='none')
    CURRENCY_PER_KWH = Measurement(name='currencyPerKWh',
                                   description=_MEASUREMENT_DESCRIPTIONS['currencyPerKWh'],
                                   unit=_CURRENCIES[0],
                                   acceptable_units=_CURRENCIES,
                                   scale='none')
    CURRENCY_PER_THM = Measurement(name='currencyPerThm',
                                   description=_MEASUREMENT_DESCRIPTIONS['currencyPerThm'],
                                   unit=_CURRENCIES[0],
                                   acceptable_units=_CURRENCIES,
                                   scale='none')
