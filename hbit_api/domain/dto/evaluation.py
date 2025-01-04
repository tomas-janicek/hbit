import datetime
import typing

from pydantic import BaseModel

from hbit_api.domain.dto import vuls as vuls_dto

if typing.TYPE_CHECKING:
    from hbit_api.domain import models


#########
# CAPEC #
#########


class CAPECDto(BaseModel):
    capec_id: int
    description: str
    extended_description: str
    likelihood_of_attack: str
    severity: str
    execution_flow: list[vuls_dto.AttackStepDto]
    prerequisites: list[str]
    skills_required: list[vuls_dto.SkillDto]
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
            execution_flow=capec.execution_flow,  # type: ignore
            prerequisites=capec.prerequisites,
            skills_required=capec.skills_required,  # type: ignore
            resources_required=capec.resources_required,
            consequences=capec.consequences,
        )


#######
# CWE #
#######


class CweDto(BaseModel):
    cwe_id: int
    description: str
    extended_description: str
    background_details: list[str]
    potential_mitigations: list[vuls_dto.MitigationDto]
    detection_methods: list[vuls_dto.DetectionMethodDto]
    capecs: list[CAPECDto]

    @classmethod
    def from_cwe(cls, cwe: "models.CWE") -> typing.Self:
        return cls(
            cwe_id=cwe.cwe_id,
            description=cwe.description,
            extended_description=cwe.extended_description,
            background_details=cwe.background_details,
            potential_mitigations=cwe.potential_mitigations,  # type: ignore
            detection_methods=cwe.detection_methods,  # type: ignore
            capecs=[CAPECDto.from_capec(capec) for capec in cwe.capecs],
        )


#################
# Vulnerability #
#################


class VulnerabilityDto(BaseModel):
    cve_id: str
    description: str
    score: float
    cwes: list[CweDto]

    @classmethod
    def from_cve(cls, cve: "models.CVE") -> typing.Self:
        return cls(
            cve_id=cve.cve_id,
            description=cve.description,
            # TODO: How can I parse cvss immediately to Pydantic using sqlalchemy model?
            score=cve.cvss["score"],
            cwes=[CweDto.from_cwe(cwe) for cwe in cve.cwes],
        )


class PatchEvaluationDto(BaseModel):
    build: str
    os: str
    name: str

    @classmethod
    def from_patch(cls, patch: "models.Patch") -> typing.Self:
        return cls(
            build=patch.build,
            os=patch.os,
            name=patch.name,
        )


class DeviceDto(BaseModel):
    manufacturer: str
    name: str
    identifier: str
    models: list[str]
    released: datetime.date | None
    discontinued: datetime.date | None

    @classmethod
    def from_device(cls, device: "models.Device") -> typing.Self:
        return cls(
            manufacturer=device.manufacturer.name,
            name=device.name,
            identifier=device.identifier,
            models=device.models,
            released=device.released,
            discontinued=device.discontinued,
        )


class EvaluationDto(BaseModel):
    device: DeviceDto
    patch: PatchEvaluationDto
    vulnerabilities: list[VulnerabilityDto]

    @classmethod
    def from_device_and_patch(
        cls, device: "models.Device", patch: "models.Patch"
    ) -> typing.Self:
        return cls(
            device=DeviceDto.from_device(device),
            patch=PatchEvaluationDto.from_patch(patch),
            # include only cves with high score
            vulnerabilities=[
                VulnerabilityDto.from_cve(cve)
                for cve in patch.cves
                if cve.cvss["score"] > 7.0
            ],
        )
