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
    GOOGLE = "Google"
    MISTRAL = "Mistral"
    TOGETHER_AI = "Together AI"
    NVIDIA = "NVIDIA"


class GraphAction(enum.StrEnum):
    DEVICE_EXTRACTION = "device_extraction"
    PATCH_EXTRACTION = "patch_extraction"
    DEVICE_EVALUATION = "device_evaluation"
    PATCH_EVALUATION = "patch_evaluation"
    RESPOND = "respond_to_user"


class SecurityPaperCategory(enum.StrEnum):
    EPUB = "epub_books"
    PDF = "pdf"
    CVE_DATASET = "cve_dataset"
    POC = "poc"
    SEC_KNOWLEAGE = "sec-knowleage"
    SECON = "secon"
