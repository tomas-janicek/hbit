import pathlib
import typing

from langchain.schema import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langgraph.func import END, START
from langgraph.graph import StateGraph
from langgraph.graph.state import Command

from hbit import (
    dto,
    enums,
    nodes,
    services,
    types,
    utils,
)


class GraphDeviceEvaluator:
    def __init__(self, registry: services.ServiceContainer) -> None:
        self.registry = registry
        saver = self.registry.get_service(types.Saver)

        graph_builder = StateGraph(dto.GraphStateSchema)
        graph_builder.add_node("reset_max_steps", nodes.reset_max_steps)
        graph_builder.add_node("route_through_graph", self.route_through_graph)
        graph_builder.add_node("get_device_identifier", nodes.get_device_identifier)
        graph_builder.add_node("get_patch_build", nodes.get_patch_build)
        graph_builder.add_node("get_device_evaluation", nodes.get_device_evaluation)
        graph_builder.add_node("get_patch_evaluation", nodes.get_patch_evaluation)
        graph_builder.add_node("respond_to_user", nodes.respond_to_user)

        graph_builder.add_edge(START, "reset_max_steps")
        graph_builder.add_edge("reset_max_steps", "route_through_graph")
        graph_builder.add_edge("get_device_identifier", "route_through_graph")
        graph_builder.add_edge("get_patch_build", "route_through_graph")
        graph_builder.add_edge("get_device_evaluation", "route_through_graph")
        graph_builder.add_edge("get_patch_evaluation", "route_through_graph")
        graph_builder.add_edge("respond_to_user", END)

        self.graph = graph_builder.compile(checkpointer=saver)
        self.model = self.registry.get_service(types.AgentModel)
        self.graph_router = self.model.with_structured_output(dto.GraphRouterResponse)

    def get_device_security_answer(
        self, input: str, thread_id: str | None = None, print_steps: bool = False
    ) -> str:
        if not thread_id:
            thread_id = utils.generate_random_string(5)

        response = "Nothing was generated!"
        for event in self.graph.stream(
            {"messages": [self.get_system_message(), HumanMessage(content=input)]},
            config={
                "configurable": {"registry": self.registry, "thread_id": thread_id}
            },
            stream_mode="values",
        ):
            message: BaseMessage = event["messages"][-1]
            if print_steps:
                message.pretty_print()
            response = str(message.content)

        return response

    def route_through_graph(
        self, state: dto.GraphStateSchema
    ) -> Command[
        typing.Literal[
            "get_device_identifier",
            "get_patch_build",
            "get_device_evaluation",
            "get_patch_evaluation",
            "respond_to_user",
            "route_through_graph",
        ]
    ]:
        """Route the state through the graph."""
        # make sure we do not exceed the maximum number of steps so we do not get stuck in a loop
        if state["current_step"] >= state["max_steps"]:
            return Command(goto="respond_to_user")

        prompt = (
            "Given the conversation below, decide what should be done next to answer fulfill users requests. "
            "You choose what to do by returning JSON schema of with certain data. "
            "Before choosing action make sure you did not call the same action with the same data by checking the conversation. "
            f"If you do not know what to do, call {enums.GraphAction.RESPOND} which will request more information from user. "
            f"If any message contains error (contains 'Error' in message), follow infractions in error message. If action failed and you can not call it with different data, call {enums.GraphAction.RESPOND} asking for more information."
            "If any action successfully finished (contains 'Success' in message), do not call it again with the same data. "
            "\n"
            "You must choose one of these actions:\n"
            # TODO: Add examples and more information about each action
            f"- {enums.GraphAction.RESPOND}: is action that responds to user based on conversation. Use this action if you are not sure what to call or you have nothing else to call. This should be default action if you are not sure.\n"
            f"- {enums.GraphAction.DEVICE_EXTRACTION}: is action that extract device identifier which can be used for device evaluation. Use this action if user asks about his device. You must provide data field of response schema in ExtractionText type. Should be something like {{'text': 'I have iPhone 13 Pro'}}\n"
            f"- {enums.GraphAction.PATCH_EXTRACTION}: is action that extract patch build which can be used for device evaluation or patch evaluation. Use this action if user asks about his patch. You must provide data field of response schema in ExtractionText type. Should be something like {{'text': 'it has iOS 18.2.1 installed.'}}\n"
            f"- {enums.GraphAction.DEVICE_EVALUATION}: is action that evaluate device based on device identifier and patch build. You must provide provide data field of response schema in DeviceEvaluationParameters type. Something like {{'device_identifier': 'iphone14,2', patch_build: '22B83'}}\n"
            f"- {enums.GraphAction.PATCH_EVALUATION}: is action that evaluate patch based on patch build. You must provide data field of response schema in PatchEvaluationParameters type. Something like {{'patch_build': '22B83'}}\n"
        )
        conversation_messages = [*state["messages"]]
        conversation_messages[0] = SystemMessage(prompt)
        # TODO: Add Few Shot Learning to the model
        action: dto.GraphRouterResponse = self.graph_router.invoke(
            conversation_messages
        )  # type: ignore

        try:
            return self.send_action(state, action)
        except Exception as error:
            message = AIMessage(f"Error: {error} Try fixing the error.")
            return Command(
                goto="route_through_graph",
                update={"messages": message, "current_step": state["current_step"] + 1},
            )

    def send_action(
        self, state: dto.GraphStateSchema, action: dto.GraphRouterResponse
    ) -> Command[
        typing.Literal[
            "get_device_identifier",
            "get_patch_build",
            "get_device_evaluation",
            "get_patch_evaluation",
            "respond_to_user",
            "route_through_graph",
        ]
    ]:
        match action.action:
            case enums.GraphAction.DEVICE_EXTRACTION:
                assert isinstance(action.data, dto.ExtractionText), (
                    "Data must be of type ExtractionText"
                )
                return Command(
                    goto="get_device_identifier",
                    update={
                        "text": action.data.text,
                        "current_step": state["current_step"] + 1,
                    },
                )
            case enums.GraphAction.PATCH_EXTRACTION:
                assert isinstance(action.data, dto.ExtractionText), (
                    "Data must be of type ExtractionText"
                )
                return Command(
                    goto="get_patch_build",
                    update={
                        "text": action.data.text,
                        "current_step": state["current_step"] + 1,
                    },
                )
            case enums.GraphAction.DEVICE_EVALUATION:
                assert isinstance(action.data, dto.DeviceEvaluationParameters), (
                    "Data must be of type DeviceEvaluationParameters"
                )
                return Command(
                    goto="get_device_evaluation",
                    update={
                        **action.data.model_dump(),
                        "current_step": state["current_step"] + 1,
                    },
                )
            case enums.GraphAction.PATCH_EVALUATION:
                assert isinstance(action.data, dto.PatchEvaluationParameters), (
                    "Data must be of type PatchEvaluationParameters"
                )
                return Command(
                    goto="get_patch_evaluation",
                    update={
                        **action.data.model_dump(),
                        "current_step": state["current_step"] + 1,
                    },
                )
            case enums.GraphAction.RESPOND:
                return Command(goto="respond_to_user")

    def save_graph_image(self, img_path: pathlib.Path) -> None:
        graph_image = self.graph.get_graph().draw_mermaid_png()
        with open(img_path, "wb") as file:
            file.write(graph_image)

    @staticmethod
    def get_system_message() -> SystemMessage:
        """Generate the system message that provides context for the graph."""
        system_message = (
            "You are an expert cyber-security analyst. "
            "Your purpose is to request relevant information from user about what he wants to analyze "
            "and then use this information to use nodes that retrieve relevant security information "
            "about whatever user requested. We can analyze user's device and patch.\n"
        )
        return SystemMessage(content=system_message)
