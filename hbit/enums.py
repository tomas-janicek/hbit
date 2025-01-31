import enum


class DeviceExtractorType(enum.StrEnum):
    SQL = "SQL"
    JSON = "JSON"


class PatchExtractorType(enum.StrEnum):
    SQL = "SQL"
    JSON = "JSON"


class DeviceEvaluationType(enum.StrEnum):
    IMPERATIVE = "Imperative"
    AI = "AI"


class PatchEvaluationType(enum.StrEnum):
    IMPERATIVE = "Imperative"
    AI = "AI"


class SummaryServiceType(enum.StrEnum):
    AI = "AI"


class ModelProvider(enum.StrEnum):
    GROQ = "GROQ"
    OPEN_AI = "OpenAI"
    ANTHROPIC = "Anthropic"
    DEEPSEEK = "DeepSeek"
    GOOGLE = "Google"
    MISTRAL = "Mistral"
    TOGETHER_AI = "Together AI"
