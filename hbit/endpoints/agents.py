from langchain.schema import BaseMessage
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langgraph.prebuilt import create_react_agent  # type: ignore

from hbit import core, dto, services, types, utils
from hbit.tools import TOOLS


class AgentDeviceEvaluator:
    # TODO: Give agent more context to how he should approach evaluation
    # - ask user
    # - gather data
    # - ...
    system_message = (
        "You are an expert cyber-security analyst. "
        "Your purpose is to request relevant information from user about what he want to analyze "
        "and then use this information to call tools that retrieve relevant security information "
        "about whatever user requested.\n"
        "Follow these guidelines:\n"
        "- Your task is to analyze user's device and patch so if user did not provide any relevant information, "
        "about what device and patch ask him to specify what device he is using and what version or patch "
        "is installed on that device.\n"
        "- If you retrieve any evaluation, create summary and return the response to user.\n"
    )

    def __init__(self, registry: services.ServiceContainer) -> None:
        self.registry = registry
        model = self.registry.get_service(types.DefaultModel)
        db = self.registry.get_service(core.DatabaseService)
        saver = self.registry.get_service(types.Saver)
        toolkit = SQLDatabaseToolkit(db=db.db_tool, llm=model)
        tools = [*toolkit.get_tools(), *TOOLS]

        self.agent_executor = create_react_agent(
            model=model,
            tools=tools,
            state_schema=dto.AgentStateSchema,
            checkpointer=saver,
            messages_modifier=self.system_message,
        )

    def get_device_security_answer(
        self, question: str, thread_id: str | None = None
    ) -> str:
        if not thread_id:
            thread_id = utils.generate_random_string(5)

        response = "Nothing was generated!"
        for event in self.agent_executor.stream(
            {
                "messages": [{"role": "user", "content": question}],
                "state": {"patch_evaluation": None, "device_evaluation": None},
            },
            config={
                "configurable": {"registry": self.registry, "thread_id": thread_id}
            },
            stream_mode="values",
        ):
            message: BaseMessage = event["messages"][-1]
            message.pretty_print()
            response = str(message.content)

        return response
