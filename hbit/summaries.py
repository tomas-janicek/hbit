import typing

from langchain.schema import AIMessage
from langchain_core.language_models import BaseChatModel

from common import dto as common_dto
from hbit import prompting, settings


class SummaryService(typing.Protocol):
    def generate_summary(self, evaluation: common_dto.EvaluationDto) -> str: ...


class AiSummaryService(SummaryService):
    def __init__(
        self,
        summary_model: BaseChatModel,
        analysis_model: BaseChatModel,
        prompt_store: prompting.PromptStore,
        n_max_tokens: int = settings.N_TOKEN_GENERATION_LIMIT,
        n_summaries_limit: int = settings.N_SUMMARIES_LIMIT,
    ) -> None:
        self.prompt_store = prompt_store
        self.summary_model = self.prompt_store.evaluation_part_summary | summary_model
        self.analysis_model = self.prompt_store.evaluation_summary | analysis_model
        self.n_max_tokens = n_max_tokens
        self.n_summaries_limit = n_summaries_limit

    def generate_summary(self, evaluation: common_dto.EvaluationDto) -> str:
        if not evaluation.vulnerabilities:
            return self.generate_summary_for_empty_evaluation(evaluation)

        return self.generate_summary_for_vulnerable_evaluation(evaluation)

    def generate_summary_for_vulnerable_evaluation(
        self, evaluation: common_dto.EvaluationDto
    ) -> str:
        summaries: list[str] = []
        for evaluation_chunk in evaluation.get_chunked_by_n_tokens(
            n_max_tokens=self.n_max_tokens, n_summaries_limit=self.n_summaries_limit
        ):
            summary: AIMessage = self.summary_model.invoke(
                {"evaluation_chunk": evaluation_chunk.model_dump_json()}
            )  # type: ignore
            summaries.append(str(summary.content))

        summaries_str = "\n - ".join(summaries)
        analysis: AIMessage = self.analysis_model.invoke(
            {"summaries_str": summaries_str}
        )  # type: ignore

        return str(analysis.content)

    def generate_summary_for_empty_evaluation(
        self, evaluation: common_dto.EvaluationDto
    ) -> str:
        match evaluation:
            case common_dto.PatchEvaluationDto():
                summaries_str = (
                    "Patch defined by JSON object below does not any vulnerabilities making in safe.\n"
                    f"Patch: {evaluation.patch}"
                )
            case common_dto.DeviceEvaluationDto():
                summaries_str = (
                    "Device and patch defined by JSON object below does not any vulnerabilities making in safe.\n"
                    f"Device: {evaluation.device.model_dump_json()}\n"
                    f"Patch: {evaluation.patch.model_dump_json()}"
                )

        analysis: AIMessage = self.analysis_model.invoke(
            {"summaries_str": summaries_str}
        )  # type: ignore

        return str(analysis.content)
