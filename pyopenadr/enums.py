# Some handy enums to use in your messages

class Enum(type):
    def __getitem__(self, item):
        return getattr(self, item)

    @property
    def members(self):
        return sorted([item for item in list(set(dir(self)) - set(dir(Enum))) if not item.startswith("_")])

    @property
    def values(self):
        return [self[item] for item in self.members]

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
    HISTORY_USAGE = "METADATA_HISTORY_USAGE"
    METADATA_HISTORY_GREENBUTTON = "METADATA_HISTORY_GREENBUTTON"
    HISTORY_GREENBUTTON = "HISTORY_GREENBUTTON"
    METADATA_TELEMETRY_USAGE = "METADATA_TELEMETRY_USAGE"
    TELEMETRY_USAGE = "TELEMETRY_USAGE"
    METADATA_TELEMETRY_STATUS = "METADATA_TELEMETRY_STATUS"
    TELEMETRY_STATUS = "TELEMETRY_STATUS"
