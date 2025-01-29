import typing

from langchain.schema import AIMessage
from langchain_core.language_models import BaseChatModel

from common import dto as common_dto
from hbit import prompting, settings


class SummaryService(typing.Protocol):
    def generate_summary(
        self,
        text: str,
        evaluation: common_dto.EvaluationDto,
    ) -> str: ...


class AiSummaryService(SummaryService):
    def __init__(
        self,
        summary_model: BaseChatModel,
        analysis_model: BaseChatModel,
        prompt_store: prompting.PromptStore,
        n_max_tokens: int = settings.N_TOKEN_GENERATION_LIMIT,
    ) -> None:
        self.prompt_store = prompt_store
        self.summary_model = self.prompt_store.evaluation_part_summary | summary_model
        self.analysis_model = self.prompt_store.evaluation_summary | analysis_model
        self.n_max_tokens = n_max_tokens

    def generate_summary(
        self,
        text: str,
        evaluation: common_dto.EvaluationDto,
    ) -> str:
        summaries: list[str] = []
        for evaluation_chunk in evaluation.get_chunked_by_n_tokens(
            n_max_tokens=self.n_max_tokens
        ):
            summary: AIMessage = self.summary_model.invoke(
                {"input": text, "evaluation_chunk": evaluation_chunk}
            )  # type: ignore
            summaries.append(str(summary.content))

        summaries_str = "\n - ".join(summaries)
        analysis: AIMessage = self.analysis_model.invoke(
            {"input": text, "summaries_str": summaries_str}
        )  # type: ignore

        return str(analysis.content)
