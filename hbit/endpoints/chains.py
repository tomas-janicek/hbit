import pathlib
import typing

from langgraph.func import START  # type: ignore
from langgraph.graph import StateGraph  # type: ignore

from hbit import clients, dto, extractors, services, summaries, types


class ChainDeviceEvaluator:
    def __init__(self, registry: services.ServiceContainer) -> None:
        self.registry = registry

        saver = self.registry.get_service(types.MemorySaver)
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
        self.graph = graph_builder.compile(checkpointer=saver)

    # TODO: Add Memory Savers
    def get_device_security_answer(
        self, question: str, print_steps: bool = False
    ) -> str:
        response = "Nothing was generated!"
        step: dict[str, typing.Any] = {}
        for step in self.graph.stream({"question": question}, stream_mode="updates"):
            for key, values in step.items():
                name = key.replace("_", " ")
                if print_steps:
                    print(
                        f"================================== {name.capitalize()} ==================================\n"
                    )
                for value in values.values():
                    if print_steps:
                        print(value)
                    response = value

        return response

    def generate_evaluation_summary(
        self, state: dto.ChainStateSchema
    ) -> dict[str, typing.Any]:
        """Generate summary from evaluation. It is strongly recommended to use this tool as last
        if evaluation was retrieved."""
        summary_service = self.registry.get_service(summaries.SummaryService)
        summary = summary_service.generate_summary(
            evaluation=state["device_evaluation"]
        )
        return {"device_summary": summary}

    def get_device_evaluation(
        self, state: dto.ChainStateSchema
    ) -> dict[str, typing.Any]:
        """Get the evaluation of a device."""
        client = self.registry.get_service(clients.HBITClient)
        evaluation = client.get_device_evaluation(
            device_identifier=state["device_identifier"],
            patch_build=state["patch_build"],
        )
        return {"device_evaluation": evaluation}

    def get_device_identifier(
        self, state: dto.ChainStateSchema
    ) -> dict[str, typing.Any]:
        """Get device identifier from any text. Return None if no device was found."""
        device_extractor = self.registry.get_service(extractors.DeviceExtractor)
        device_identifier = device_extractor.extract_device_identifier(
            text=state["question"]
        )
        return {"device_identifier": device_identifier}

    def get_patch_build(self, state: dto.ChainStateSchema) -> dict[str, typing.Any]:
        """Get patch build from any text. Return None if no patch was found."""
        patch_extractor = self.registry.get_service(extractors.PatchExtractor)
        patch_build = patch_extractor.extract_patch_build(text=state["question"])
        return {"patch_build": patch_build}

    def save_graph_image(self, img_path: pathlib.Path) -> None:
        graph_image = self.graph.get_graph().draw_mermaid_png()
        with open(img_path, "wb") as file:
            file.write(graph_image)
