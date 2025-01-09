import typing

from langchain.schema import AIMessage
from langchain_core.language_models import BaseChatModel

from common import dto as common_dto


class SummaryService(typing.Protocol):
    def generate_summary(
        self, question: str, evaluation: common_dto.EvaluationDto
    ) -> str: ...


class AiSummaryService(SummaryService):
    def __init__(self, model: BaseChatModel) -> None:
        self.model = model

    def generate_summary(
        self, question: str, evaluation: common_dto.EvaluationDto
    ) -> str:
        prompt = (
            "Given the following user question, and devices evaluation,"
            "answer the user question.\n\n"
            f"Question: {question}\n"
            f"Evaluation: {evaluation.to_readable_str()}"
        )
        response: AIMessage = self.model.invoke(prompt)  # type: ignore
        return str(response.content)
