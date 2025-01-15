import typing

import pydantic
from langchain_core.language_models import BaseChatModel

from common import dto as common_dto
from hbit import clients, dto, settings


class EvaluationService(typing.Protocol):
    def get_full_evaluation(
        self, device_identifier: str, patch_build: str
    ) -> common_dto.EvaluationDto: ...

    def get_trimmed_evaluation(
        self, device_identifier: str, patch_build: str
    ) -> common_dto.EvaluationDto: ...


class AiEvaluationService(EvaluationService):
    def __init__(
        self,
        model: BaseChatModel,
        client: clients.HBITClient,
        n_vulnerabilities: int = settings.N_VULNERABILITIES,
    ) -> None:
        self.vulnerability_summarizer = model.with_structured_output(
            dto.VulnerabilitiesDto
        )
        self.client = client
        self.n_vulnerabilities = n_vulnerabilities

    def get_full_evaluation(
        self, device_identifier: str, patch_build: str
    ) -> common_dto.EvaluationDto:
        return self.client.get_device_evaluation(device_identifier, patch_build)

    def get_trimmed_evaluation(
        self, device_identifier: str, patch_build: str
    ) -> common_dto.EvaluationDto:
        evaluation = self.get_full_evaluation(device_identifier, patch_build)

        # TODO: First, pick x vuls and create AI summaries for them. Make sure they have max pre-defined number of tokens.
        # TODO: If one vulnerability can be bigger than context,trim data inside vulnerability.
        # TODO: Then use this summaries to create one big summary.

        vuls_type_adapter = pydantic.TypeAdapter(list[common_dto.VulnerabilityDto])
        vuls_str = vuls_type_adapter.dump_json(evaluation.vulnerabilities)
        prompt = (
            "You are a cyber-security expert tasked with analyzing a list of vulnerabilities provided in JSON format. "
            f"Your goal is to identify and return only the {self.n_vulnerabilities} most critical vulnerabilities. "
            "Focus on vulnerabilities that, if exploited, could cause significant problems for the user. Ensure the JSON structure "
            "of the vulnerabilities remains unchanged. If any field within a vulnerability contains a list of items, you can also "
            "remove less important items from those lists, while retaining only the most critical information. "
            "Remove or exclude less important vulnerabilities and details while maintaining the overall format.\n\n"
            "Here is the list of vulnerabilities:\n\n"
            f"{vuls_str.decode('utf-8')}"
        )
        trimmed_vulnerabilities: dto.VulnerabilitiesDto = (
            self.vulnerability_summarizer.invoke(prompt)
        )  # type: ignore
        evaluation.vulnerabilities = trimmed_vulnerabilities.vulnerabilities
        return evaluation


class IterativeEvaluationService(EvaluationService):
    def __init__(
        self,
        client: clients.HBITClient,
        n_vulnerabilities: int = settings.N_VULNERABILITIES,
    ) -> None:
        self.client = client
        self.n_vulnerabilities = n_vulnerabilities

    def get_full_evaluation(
        self, device_identifier: str, patch_build: str
    ) -> common_dto.EvaluationDto:
        return self.client.get_device_evaluation(device_identifier, patch_build)

    def get_trimmed_evaluation(
        self, device_identifier: str, patch_build: str
    ) -> common_dto.EvaluationDto:
        evaluation = self.get_full_evaluation(device_identifier, patch_build)
        vulnerabilities = self._trim_vulnerabilities(evaluation.vulnerabilities)
        vulnerabilities.sort(key=lambda v: v.score, reverse=True)
        vulnerabilities = vulnerabilities[: self.n_vulnerabilities]
        evaluation.vulnerabilities = vulnerabilities
        return evaluation

    def _trim_vulnerabilities(
        self, vulnerabilities: list[common_dto.VulnerabilityDto]
    ) -> list[common_dto.VulnerabilityDto]:
        trimmed_vulnerabilities: list[common_dto.VulnerabilityDto] = []
        for v in vulnerabilities:
            if v.score > 7.0:
                v.cwes = self._trim_cwes(v.cwes)
                trimmed_vulnerabilities.append(v)
        return trimmed_vulnerabilities

    def _trim_cwes(self, cwes: list[common_dto.CweDto]) -> list[common_dto.CweDto]:
        trimmed_cwes: list[common_dto.CweDto] = []
        for cwe in cwes:
            if cwe.likelihood_of_exploit.lower() in ["high", "medium"]:
                cwe.detection_methods = self._trim_detection_methods(
                    cwe.detection_methods
                )
                cwe.capecs = self._trim_capecs(cwe.capecs)
                trimmed_cwes.append(cwe)
        return trimmed_cwes

    def _trim_detection_methods(
        self, detection_methods: list[common_dto.DetectionMethodDto]
    ) -> list[common_dto.DetectionMethodDto]:
        trimmed_detection_methods = [
            m for m in detection_methods if m.effectiveness.lower() == "high"
        ]
        return trimmed_detection_methods

    def _trim_capecs(
        self, capecs: list[common_dto.CAPECDto]
    ) -> list[common_dto.CAPECDto]:
        trimmed_capecs = [m for m in capecs if m.likelihood_of_attack.lower() == "high"]
        return trimmed_capecs
