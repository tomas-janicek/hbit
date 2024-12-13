import datetime
import typing

from pydantic import BaseModel, StringConstraints

from hbit_data import enums, normalizer

StripedStr = typing.Annotated[str, StringConstraints(strip_whitespace=True)]

LoweredString = typing.Annotated[
    str, StringConstraints(strip_whitespace=True, to_lower=True)
]

###################
# Security Update #
###################


class CVSS(BaseModel):
    version: LoweredString
    vector: LoweredString
    score: float
    exploitability_score: float
    impact_score: float


class CVE(BaseModel):
    cve_id: str
    description: StripedStr
    published: datetime.datetime
    last_modified: datetime.datetime
    cvss: CVSS
    cwe_ids: list[int]


class Patch(BaseModel):
    os: enums.Os
    name: LoweredString
    version: normalizer.VersionStr
    major: int
    minor: int
    patch: int
    build: typing.Annotated[
        str, StringConstraints(strip_whitespace=True, to_lower=True)
    ]
    released: datetime.date | None
    affected_devices: list[LoweredString]


class SecurityUpdate(BaseModel):
    patch: Patch
    cves: list[CVE]


#######
# CWE #
#######


class Mitigation(BaseModel):
    description: StripedStr
    effectiveness: LoweredString
    effectiveness_notes: StripedStr


class DetectionMethod(BaseModel):
    method: StripedStr
    description: StripedStr
    effectiveness: LoweredString


class CWE(BaseModel):
    cwe_id: int
    name: StripedStr
    description: StripedStr
    extended_description: StripedStr
    likelihood_of_exploit: LoweredString
    background_details: list[StripedStr]
    potential_mitigations: list[Mitigation]
    detection_methods: list[DetectionMethod]


#########
# CAPEC #
#########


class AttackStep(BaseModel):
    step: int
    phase: LoweredString
    description: StripedStr
    techniques: list[StripedStr]


class Skill(BaseModel):
    level: LoweredString
    description: StripedStr


class CAPEC(BaseModel):
    capec_id: int
    description: StripedStr
    extended_description: StripedStr
    likelihood_of_attack: LoweredString
    severity: StripedStr
    execution_flow: list[AttackStep]
    prerequisites: list[StripedStr]
    skills_required: list[Skill]
    resources_required: list[StripedStr]
    consequences: list[StripedStr]
    cwe_ids: list[int]


##########
# iPhone #
##########


class iPhone(BaseModel): ...
