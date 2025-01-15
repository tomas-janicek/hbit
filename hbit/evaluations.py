import logging
import typing

from langchain_core.language_models import BaseChatModel
from langchain_core.runnables import Runnable

from common import dto as common_dto
from hbit import clients, settings

_log = logging.getLogger(__name__)


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
        n_max_tokens: int = settings.N_TOKEN_GENERATION_LIMIT,
    ) -> None:
        self.vulnerability_summarizer: Runnable[str, common_dto.VulnerabilityDto] = (
            model.with_structured_output(common_dto.VulnerabilityDto)
        )  # type: ignore
        self.client = client
        self.n_vulnerabilities = n_vulnerabilities
        self.n_max_tokens = n_max_tokens

    def get_full_evaluation(
        self, device_identifier: str, patch_build: str
    ) -> common_dto.EvaluationDto:
        return self.client.get_device_evaluation(device_identifier, patch_build)

    def get_trimmed_evaluation(
        self, device_identifier: str, patch_build: str
    ) -> common_dto.EvaluationDto:
        evaluation = self.get_full_evaluation(device_identifier, patch_build)
        evaluation.vulnerabilities.sort(key=lambda v: v.score, reverse=True)
        evaluation.vulnerabilities = evaluation.vulnerabilities[
            : self.n_vulnerabilities
        ]

        trimmed_vulnerabilities: list[common_dto.VulnerabilityDto] = []
        for vul in evaluation.vulnerabilities:
            if vul.n_json_tokens > self.n_max_tokens:
                _log.warning(
                    "Vulnerability with ID %s can't be summarized because it is too big (it has %s tokens).",
                    vul.cve_id,
                    vul.n_json_tokens,
                )
                continue
            prompt = (
                "You are a cyber-security expert tasked with analyzing a vulnerability data provided in JSON format. "
                "Your goal is to identify and return only the most critical parts of given vulnerability. "
                "Focus on parts that, if exploited, could cause significant problems for the user. Ensure the JSON structure "
                "of the vulnerability remains unchanged. If any field within a vulnerability contains a list of items, you can also "
                "remove less important items from those lists, while retaining only the most critical information. "
                "Remove or exclude less important vulnerabilities and details while maintaining the overall format.\n\n"
                "Here is the vulnerability:\n\n"
                f"{vul.model_dump_json()}"
            )
            trimmed_vul: common_dto.VulnerabilityDto = (
                self.vulnerability_summarizer.invoke(prompt)
            )
            trimmed_vulnerabilities.append(trimmed_vul)

        evaluation.vulnerabilities = trimmed_vulnerabilities
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
        evaluation.vulnerabilities.sort(key=lambda v: v.score, reverse=True)
        evaluation.vulnerabilities = evaluation.vulnerabilities[
            : self.n_vulnerabilities
        ]
        evaluation.vulnerabilities = self._trim_vulnerabilities(
            evaluation.vulnerabilities
        )
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
