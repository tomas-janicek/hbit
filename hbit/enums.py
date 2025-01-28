import enum


class DeviceExtractorType(enum.Enum):
    SQL_EXTRACTOR = enum.auto()
    STRUCTURED_EXTRACTOR = enum.auto()


class PatchExtractorType(enum.Enum):
    SQL_EXTRACTOR = enum.auto()
    STRUCTURED_EXTRACTOR = enum.auto()


class DeviceEvaluationType(enum.Enum):
    IMPERATIVE = enum.auto()
    AI = enum.auto()


class PatchEvaluationType(enum.Enum):
    IMPERATIVE = enum.auto()
    AI = enum.auto()


class SummaryServiceType(enum.Enum):
    AI = enum.auto()


class ModelProvider(enum.Enum):
    GROQ = enum.auto()
    OPEN_AI = enum.auto()
    ANTHROPIC = enum.auto()
    DEEPSEEK = enum.auto()
