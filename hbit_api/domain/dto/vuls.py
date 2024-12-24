import datetime
import typing

from pydantic import BaseModel

if typing.TYPE_CHECKING:
    from hbit_api.domain import models

###################
# Security Update #
###################


class CVSSDto(BaseModel):
    version: str
    vector: str
    score: float
    exploitability_score: float
    impact_score: float


class CVEDto(BaseModel):
    cve_id: str
    description: str
    published: datetime.datetime
    last_modified: datetime.datetime
    cvss: CVSSDto
    cwe_ids: list[int]


class PatchDto(BaseModel):
    os: str
    name: str
    version: str
    major: int
    minor: int
    patch: int
    build: str
    released: datetime.date | None
    affected_devices: list[str]


#######
# CWE #
#######


class MitigationDto(BaseModel):
    description: str
    effectiveness: str
    effectiveness_notes: str


class DetectionMethodDto(BaseModel):
    method: str
    description: str
    effectiveness: str


class CWEDto(BaseModel):
    cwe_id: int
    name: str
    description: str
    extended_description: str
    likelihood_of_exploit: str
    background_details: list[str]
    potential_mitigations: list[MitigationDto]
    detection_methods: list[DetectionMethodDto]

    @classmethod
    def from_cwe(cls, cwe: "models.CWE") -> typing.Self:
        return cls(
            cwe_id=cwe.cwe_id,
            name=cwe.name,
            description=cwe.description,
            extended_description=cwe.extended_description,
            likelihood_of_exploit=cwe.likelihood_of_exploit,
            background_details=cwe.background_details,
            potential_mitigations=cwe.potential_mitigations,
            detection_methods=cwe.detection_methods,
        )


class CWEsDto(BaseModel):
    data: list[CWEDto]
    count: int


#########
# CAPEC #
#########


class AttackStepDto(BaseModel):
    step: int
    phase: str
    description: str
    techniques: list[str]


class SkillDto(BaseModel):
    level: str
    description: str


class CAPECInDto(BaseModel):
    capec_id: int
    description: str
    extended_description: str
    likelihood_of_attack: str
    severity: str
    execution_flow: list[AttackStepDto]
    prerequisites: list[str]
    skills_required: list[SkillDto]
    resources_required: list[str]
    consequences: list[str]
    cwe_ids: list[int]


class CAPECOutDto(BaseModel):
    capec_id: int
    description: str
    extended_description: str
    likelihood_of_attack: str
    severity: str
    execution_flow: list[AttackStepDto]
    prerequisites: list[str]
    skills_required: list[SkillDto]
    resources_required: list[str]
    consequences: list[str]

    @classmethod
    def from_capec(cls, capec: "models.CAPEC") -> typing.Self:
        return cls(
            capec_id=capec.capec_id,
            description=capec.description,
            extended_description=capec.extended_description,
            likelihood_of_attack=capec.likelihood_of_attack,
            severity=capec.severity,
            execution_flow=capec.execution_flow,
            prerequisites=capec.prerequisites,
            skills_required=capec.skills_required,
            resources_required=capec.resources_required,
            consequences=capec.consequences,
        )
