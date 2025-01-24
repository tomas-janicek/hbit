import enum


class DeviceExtractorType(enum.Enum):
    SQL_EXTRACTOR = enum.auto()
    STRUCTURED_EXTRACTOR = enum.auto()


class PatchExtractorType(enum.Enum):
    SQL_EXTRACTOR = enum.auto()
    STRUCTURED_EXTRACTOR = enum.auto()


class EvaluationServiceType(enum.Enum):
    IMPERATIVE = enum.auto()
    AI = enum.auto()


class SummaryServiceType(enum.Enum):
    AI = enum.auto()
