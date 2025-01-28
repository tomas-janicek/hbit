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
    techniques: list[str] = []

    def to_readable_str(self) -> str:
        techniques = ", ".join(self.techniques)
        parts = [
            f"######### Step {self.step}. ({self.phase})",
            f"Techniques: {techniques}" if techniques else "",
            f"Description: {self.description}" if self.description else "",
        ]
        return "\n".join(part for part in parts if part)


class SkillDto(BaseModel):
    level: str
    description: str

    def to_readable_str(self) -> str:
        return f"{self.level.capitalize()} Skill: {self.description}"


class CAPECDto(BaseModel):
    capec_id: int
    description: str
    extended_description: str
    likelihood_of_attack: str
    severity: str
    execution_flow: list[AttackStepDto] = []
    prerequisites: list[str] = []
    skills_required: list[SkillDto] = []
    resources_required: list[str] = []
    consequences: list[str] = []

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

    def to_readable_str(self) -> str:
        execution_flow_str = "\n".join(
            [step.to_readable_str() for step in self.execution_flow]
        )
        skills_required_str = "\n".join(
            [skill.to_readable_str() for skill in self.skills_required]
        )
        prerequisites_str = "\n".join(self.prerequisites)
        resources_required_str = "\n".join(self.resources_required)
        consequences_str = "\n".join(self.consequences)

        parts = [
            "####### CAPEC",
            f"CAPEC ID: {self.capec_id}",
            f"Description: {self.description}",
            f"Extended Description: {self.extended_description}"
            if self.extended_description
            else "",
            f"Likelihood of Attack: {self.likelihood_of_attack}"
            if self.likelihood_of_attack
            else "",
            f"Severity: {self.severity}" if self.severity else "",
            f"######## Execution Flow\n{execution_flow_str}"
            if execution_flow_str
            else "",
            f"######## Prerequisites\n{prerequisites_str}" if prerequisites_str else "",
            f"######## Skills Required\n{skills_required_str}"
            if skills_required_str
            else "",
            f"######## Resources Required\n{resources_required_str}"
            if resources_required_str
            else "",
            f"######## Consequences\n{consequences_str}" if consequences_str else "",
        ]
        return "\n".join(part for part in parts if part)


#######
# CWE #
#######


class MitigationDto(BaseModel):
    description: str
    effectiveness: str
    effectiveness_notes: str

    def to_readable_str(self) -> str:
        parts = [
            "####### Attack Mitigation Strategies",
            f"Effectiveness: {self.effectiveness}" if self.effectiveness else "",
            f"Description: {self.description}" if self.description else "",
        ]
        return "\n".join(part for part in parts if part)


class DetectionMethodDto(BaseModel):
    method: str
    description: str
    effectiveness: str

    def to_readable_str(self) -> str:
        parts = [
            "####### Vulnerability Detection Method",
            f"Method: {self.method}" if self.method else "",
            f"Effectiveness: {self.effectiveness}" if self.effectiveness else "",
            f"Description: {self.description}" if self.description else "",
        ]
        return "\n".join(part for part in parts if part)


class CweDto(BaseModel):
    cwe_id: int
    name: str
    description: str
    extended_description: str
    likelihood_of_exploit: str
    background_details: list[str] = []
    potential_mitigations: list[MitigationDto] = []
    detection_methods: list[DetectionMethodDto] = []
    capecs: list[CAPECDto] = []

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

    def to_readable_str(self) -> str:
        potential_mitigations_str = "\n".join(
            [mitigation.to_readable_str() for mitigation in self.potential_mitigations]
        )
        background_details = "\n".join(self.background_details)
        detection_methods_str = "\n".join(
            [method.to_readable_str() for method in self.detection_methods]
        )
        capecs_str = "\n".join([capec.to_readable_str() for capec in self.capecs])

        parts = [
            "##### CWE",
            f"CWE ID: {self.cwe_id}",
            f"Name: {self.name}",
            f"Description: {self.description}",
            f"Extended Description: {self.extended_description}"
            if self.extended_description
            else "",
            f"Likelihood of Exploit: {self.likelihood_of_exploit}"
            if self.likelihood_of_exploit
            else "",
            f"###### Background Details\n{background_details}"
            if background_details
            else "",
            f"###### Potential Mitigations\n{potential_mitigations_str}"
            if potential_mitigations_str
            else "",
            f"###### Detection Methods\n{detection_methods_str}"
            if detection_methods_str
            else "",
            f"###### CAPECs\n{capecs_str}" if capecs_str else "",
        ]
        return "\n".join(part for part in parts if part)


#################
# Vulnerability #
#################


class VulnerabilityDto(BaseModel):
    cve_id: str
    description: str
    score: float
    cwes: list[CweDto] = []

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

    def to_readable_str(self) -> str:
        parts = [
            "### Vulnerability",
            f"CVE ID: {self.cve_id}" if self.cve_id else "",
            f"Description: {self.description}" if self.description else "",
            f"Score: {self.score}" if self.score else "",
            f"#### CWEs\n{''.join(cwe.to_readable_str() for cwe in self.cwes)}"
            if self.cwes
            else "",
        ]
        return "\n".join(part for part in parts if part)


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

    def to_readable_str(self) -> str:
        parts = [
            "## Patch Info",
            f"Version: {self.name}",
            f"Build: {self.build}",
            f"OS: {self.os}",
        ]
        return "\n".join(part for part in parts if part)


class DeviceDto(BaseModel):
    manufacturer: str
    name: str
    identifier: str
    models: list[str] = []
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

    def to_readable_str(self) -> str:
        models = ", ".join(self.models)
        parts = [
            "## Device Info",
            f"Device: {self.manufacturer.capitalize()} {self.name}"
            if self.manufacturer and self.name
            else "",
            f"Identifier: {self.identifier}" if self.identifier else "",
            f"Models: {models}" if self.models else "",
            f"Released: {self.released}" if self.released else "",
            f"Discontinued: {self.discontinued}" if self.discontinued else "",
        ]
        return "\n".join(part for part in parts if part)


class DeviceEvaluationDto(BaseModel):
    device: DeviceDto
    patch: PatchDto
    vulnerabilities: list[VulnerabilityDto] = []

    @classmethod
    def from_device_and_patch(
        cls, device: "models.Device", patch: "models.Patch"
    ) -> typing.Self:
        return cls(
            device=DeviceDto.from_device(device),
            patch=PatchDto.from_patch(patch),
            # include only cves with high score
            vulnerabilities=[
                VulnerabilityDto.from_cve(cve)
                for cve in patch.cves
                if cve.cvss["score"] > 7.0
            ],
        )

    def to_readable_str(self) -> str:
        device_str = self.device.to_readable_str()
        patch_str = self.patch.to_readable_str()
        vulnerabilities_str = "\n".join(
            [v.to_readable_str() for v in self.vulnerabilities]
        )

        parts = [
            "# Evaluation",
            f"{device_str}",
            f"{patch_str}",
            f"## Vulnerabilities\n{vulnerabilities_str}",
        ]
        return "\n".join(part for part in parts if part)

    def get_chunked_by_n_tokens(
        self, n_max_tokens: int
    ) -> typing.Iterator["DeviceEvaluationDto"]:
        n_prepared_tokens = 0
        chunked_vuls: list[VulnerabilityDto] = []
        for vul in self.vulnerabilities:
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
            else:
                n_prepared_tokens += vul.n_json_tokens
                chunked_vuls.append(vul)


class PatchEvaluationDto(BaseModel):
    patch: PatchDto
    vulnerabilities: list[VulnerabilityDto] = []

    @classmethod
    def from_patch(cls, patch: "models.Patch") -> typing.Self:
        return cls(
            patch=PatchDto.from_patch(patch),
            # include only cves with high score
            vulnerabilities=[
                VulnerabilityDto.from_cve(cve)
                for cve in patch.cves
                if cve.cvss["score"] > 7.0
            ],
        )

    def to_readable_str(self) -> str:
        patch_str = self.patch.to_readable_str()
        vulnerabilities_str = "\n".join(
            [v.to_readable_str() for v in self.vulnerabilities]
        )

        parts = [
            "# Evaluation",
            f"{patch_str}",
            f"## Vulnerabilities\n{vulnerabilities_str}",
        ]
        return "\n".join(part for part in parts if part)

    def get_chunked_by_n_tokens(
        self, n_max_tokens: int
    ) -> typing.Iterator["PatchEvaluationDto"]:
        n_prepared_tokens = 0
        chunked_vuls: list[VulnerabilityDto] = []
        for vul in self.vulnerabilities:
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
            else:
                n_prepared_tokens += vul.n_json_tokens
                chunked_vuls.append(vul)
