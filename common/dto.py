import datetime
import logging
import typing

from pydantic import BaseModel

if typing.TYPE_CHECKING:
    from hbit_api.domain import models


_log = logging.getLogger(__name__)


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


class CAPECDto(BaseModel):
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
            execution_flow=capec.execution_flow,  # type: ignore
            prerequisites=capec.prerequisites,
            skills_required=capec.skills_required,  # type: ignore
            resources_required=capec.resources_required,
            consequences=capec.consequences,
        )


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


class CweDto(BaseModel):
    cwe_id: int
    name: str
    description: str
    extended_description: str
    likelihood_of_exploit: str
    background_details: list[str]
    potential_mitigations: list[MitigationDto]
    detection_methods: list[DetectionMethodDto]
    capecs: list[CAPECDto]

    @classmethod
    def from_cwe(cls, cwe: "models.CWE") -> typing.Self:
        return cls(
            cwe_id=cwe.cwe_id,
            name=cwe.name,
            description=cwe.description,
            extended_description=cwe.extended_description,
            likelihood_of_exploit=cwe.likelihood_of_exploit,
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

    @property
    def n_json_tokens(self) -> int:
        json = self.model_dump_json()
        return len(json)

    @classmethod
    def from_cve(cls, cve: "models.CVE") -> typing.Self:
        return cls(
            cve_id=cve.cve_id,
            description=cve.description,
            score=cve.cvss["score"],
            cwes=[CweDto.from_cwe(cwe) for cwe in cve.cwes],
        )


class CVSSDto(BaseModel):
    version: str
    vector: str
    score: float
    exploitability_score: float
    impact_score: float


class CveDto(BaseModel):
    cve_id: str
    description: str
    published: datetime.datetime
    last_modified: datetime.datetime
    cvss: CVSSDto
    cwe_ids: list[int]


class CVEsDto(BaseModel):
    data: list[CveDto]
    count: int


#########
# Patch #
#########


class PatchDto(BaseModel):
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


##########
# Device #
##########


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


###############
# Evaluations #
###############


class DeviceEvaluationDto(BaseModel):
    device: DeviceDto
    patch: PatchDto
    vulnerabilities: list[VulnerabilityDto]

    @classmethod
    def from_device_and_patch(
        cls, device: "models.Device", patch: "models.Patch"
    ) -> typing.Self:
        return cls(
            device=DeviceDto.from_device(device),
            patch=PatchDto.from_patch(patch),
            # include only cves with high score
            vulnerabilities=[VulnerabilityDto.from_cve(cve) for cve in patch.cves],
        )

    def get_chunked_by_n_tokens(
        self, n_max_tokens: int, n_summaries_limit: int
    ) -> typing.Iterator["DeviceEvaluationDto"]:
        n_prepared_tokens = 0
        chunked_vuls: list[VulnerabilityDto] = []
        iterations = 0

        for vul in self.vulnerabilities:
            if iterations >= n_summaries_limit:
                break
            if vul.n_json_tokens > n_max_tokens:
                _log.warning(
                    "Vulnerability with ID %s can't be summarized because it is too big (it has %s tokens).",
                    vul.cve_id,
                    vul.n_json_tokens,
                )
            elif n_prepared_tokens + vul.n_json_tokens > n_max_tokens:
                yield DeviceEvaluationDto(
                    device=self.device,
                    patch=self.patch,
                    vulnerabilities=chunked_vuls,
                )
                n_prepared_tokens = vul.n_json_tokens
                chunked_vuls = [vul]
                iterations += 1
            else:
                n_prepared_tokens += vul.n_json_tokens
                chunked_vuls.append(vul)

        if chunked_vuls:
            yield DeviceEvaluationDto(
                device=self.device,
                patch=self.patch,
                vulnerabilities=chunked_vuls,
            )


class PatchEvaluationDto(BaseModel):
    patch: PatchDto
    vulnerabilities: list[VulnerabilityDto]

    @classmethod
    def from_patch(cls, patch: "models.Patch") -> typing.Self:
        return cls(
            patch=PatchDto.from_patch(patch),
            # include only cves with high score
            vulnerabilities=[VulnerabilityDto.from_cve(cve) for cve in patch.cves],
        )

    def get_chunked_by_n_tokens(
        self, n_max_tokens: int, n_summaries_limit: int
    ) -> typing.Iterator["PatchEvaluationDto"]:
        n_prepared_tokens = 0
        chunked_vuls: list[VulnerabilityDto] = []
        iterations = 0

        for vul in self.vulnerabilities:
            if iterations >= n_summaries_limit:
                break
            if vul.n_json_tokens > n_max_tokens:
                _log.warning(
                    "Vulnerability with ID %s can't be summarized because it is too big (it has %s tokens).",
                    vul.cve_id,
                    vul.n_json_tokens,
                )
            elif n_prepared_tokens + vul.n_json_tokens > n_max_tokens:
                yield PatchEvaluationDto(
                    patch=self.patch,
                    vulnerabilities=chunked_vuls,
                )
                n_prepared_tokens = vul.n_json_tokens
                chunked_vuls = [vul]
                iterations += 1
            else:
                n_prepared_tokens += vul.n_json_tokens
                chunked_vuls.append(vul)


EvaluationDto = DeviceEvaluationDto | PatchEvaluationDto
