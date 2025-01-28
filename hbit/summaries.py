import typing

from langchain.schema import AIMessage
from langchain_core.language_models import BaseChatModel

from common import dto as common_dto
from hbit import settings


class SummaryService(typing.Protocol):
    def generate_summary(
        self,
        text: str,
        evaluation: common_dto.DeviceEvaluationDto | common_dto.PatchEvaluationDto,
    ) -> str: ...


class AiSummaryService(SummaryService):
    def __init__(
        self,
        summary_model: BaseChatModel,
        analysis_model: BaseChatModel,
        n_max_tokens: int = settings.N_TOKEN_GENERATION_LIMIT,
    ) -> None:
        self.summary_model = summary_model
        self.analysis_model = analysis_model
        self.n_max_tokens = n_max_tokens

    def generate_summary(
        self,
        text: str,
        evaluation: common_dto.DeviceEvaluationDto | common_dto.PatchEvaluationDto,
    ) -> str:
        summaries: list[str] = []
        for evaluation_chunk in evaluation.get_chunked_by_n_tokens(
            n_max_tokens=self.n_max_tokens
        ):
            prompt = (
                "Given the following user question, and devices evaluation, "
                "answer the user question, create summary of given evaluation. "
                "Bare in mind this summary will then be used with other summaries "
                "generated similar way.\n\n"
                f"Question: {text}\n"
                f"{evaluation_chunk}"
            )
            summary: AIMessage = self.summary_model.invoke(prompt)  # type: ignore
            summaries.append(str(summary.content))

        summaries_str = "\n - ".join(summaries)

        # TODO: Add structure to this summary, some points that should be returned to every device evaluation
        # TODO: Sections like weaknesses, recommendations, strengths (security features), overall security rating (one number),
        # TODO: most important vuls list, conclusion.
        prompt = (
            "You are expert cyber-security analyst."
            "Given the following user's question, and summaries for different security "
            "evaluations generate analysis to user's question.\n\n"
            f"Question: {text}\n"
            f"{summaries_str}"
        )
        analysis: AIMessage = self.analysis_model.invoke(prompt)  # type: ignore

        return str(analysis.content)
