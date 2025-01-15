import typing

from langchain import hub
from langchain.schema import BaseMessage
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_core.language_models import BaseChatModel
from langgraph.func import START  # type: ignore
from langgraph.graph import StateGraph  # type: ignore
from langgraph.prebuilt import create_react_agent  # type: ignore

from hbit import (
    core,
    dto,
    evaluations,
    extractors,
    summaries,
)
from hbit.tools import TOOLS

# TODO: Create module for ML related files


class AgentDeviceEvaluator:
    def __init__(self, model: BaseChatModel, db: core.DatabaseService) -> None:
        self.db = db
        self.model = model
        toolkit = SQLDatabaseToolkit(db=self.db.db_tool, llm=self.model)
        tools = [*toolkit.get_tools(), *TOOLS]

        self.agent_executor = create_react_agent(
            model=self.model,
            tools=tools,
            state_schema=dto.AgentStateSchema,
        )

    def get_device_security_answer(self, question: str) -> str:
        response = "Nothing was generated!"
        for event in self.agent_executor.stream(
            {"messages": [{"role": "user", "content": question}]},
            stream_mode="values",
        ):
            message: BaseMessage = event["messages"][-1]
            message.pretty_print()
            response = str(message.content)
        return response


class ChainDeviceEvaluator:
    def __init__(
        self,
        model: BaseChatModel,
        summary_service: summaries.SummaryService,
        device_extractor: extractors.DeviceExtractor,
        patch_extractor: extractors.PatchExtractor,
        evaluation_service: evaluations.EvaluationService,
    ) -> None:
        self.model = model
        self.query_prompt_template = hub.pull("langchain-ai/sql-query-system-prompt")
        self.summary_service = summary_service
        self.device_extractor = device_extractor
        self.patch_extractor = patch_extractor
        self.evaluation_service = evaluation_service

        # TODO: Add more sequnces to StateGraph
        graph_builder = StateGraph(dto.ChainStateSchema).add_sequence(
            [
                self.get_device_identifier,
                self.get_patch_build,
                self.get_device_evaluation,
                self.generate_evaluation_summary,
            ]
        )
        graph_builder.add_edge(START, "get_device_identifier")
        self.graph = graph_builder.compile()

    def get_device_security_answer(self, question: str) -> str:
        response = "Nothing was generated!"
        step: dict[str, typing.Any] = {}
        for step in self.graph.stream({"question": question}, stream_mode="updates"):
            for key, values in step.items():
                name = key.replace("_", " ")
                print(
                    f"================================== {name.capitalize()} ==================================\n"
                )
                for value in values.values():
                    print(value)
                    response = value

        return response

    def generate_evaluation_summary(
        self, state: dto.ChainStateSchema
    ) -> dict[str, typing.Any]:
        """Generate summary from evaluation. It is strongly recommended to use this tool as last
        if evaluation was retrieved."""
        summary = self.summary_service.generate_summary(
            question=state["question"], evaluation=state["device_evaluation"]
        )
        return {"device_summary": summary}

    def get_device_evaluation(
        self, state: dto.ChainStateSchema
    ) -> dict[str, typing.Any]:
        """Get the evaluation of a device."""
        evaluation = self.evaluation_service.get_trimmed_evaluation(
            device_identifier=state["device_identifier"],
            patch_build=state["patch_build"],
        )
        return {"device_evaluation": evaluation}

    def get_device_identifier(
        self, state: dto.ChainStateSchema
    ) -> dict[str, typing.Any]:
        """Get device identifier from any text. Return None if no device was found."""
        device_identifier = self.device_extractor.extract_device_identifier(
            text=state["question"]
        )
        return {"device_identifier": device_identifier}

    def get_patch_build(self, state: dto.ChainStateSchema) -> dict[str, typing.Any]:
        """Get patch build from any text. Return None if no patch was found."""
        patch_build = self.patch_extractor.extract_patch_build(text=state["question"])
        return {"patch_build": patch_build}


class SummarizationEvaluator:
    def __init__(
        self,
        model: BaseChatModel,
        summary_service: summaries.SummaryService,
        device_extractor: extractors.DeviceExtractor,
        patch_extractor: extractors.PatchExtractor,
        evaluation_service: evaluations.EvaluationService,
    ) -> None:
        self.model = model
        self.summary_service = summary_service
        self.device_extractor = device_extractor
        self.patch_extractor = patch_extractor
        self.evaluation_service = evaluation_service

    def get_device_security_answer(self, question: str) -> str:
        device_identifier = self.device_extractor.extract_device_identifier(question)
        if not device_identifier:
            raise ValueError(
                "Could not figure out what device the user is asking about."
            )
        patch_build = self.patch_extractor.extract_patch_build(question)
        if not patch_build:
            raise ValueError(
                "Could not figure out what patch the user is asking about."
            )
        evaluation = self.evaluation_service.get_trimmed_evaluation(
            device_identifier, patch_build
        )
        summary = self.summary_service.generate_summary(question, evaluation)

        return summary
