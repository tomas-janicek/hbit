from langchain.schema import BaseMessage
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langgraph.prebuilt import create_react_agent  # type: ignore

from hbit import core, dto, prompting, services, types, utils
from hbit.tools import TOOLS


class AgentDeviceEvaluator:
    def __init__(self, registry: services.ServiceContainer) -> None:
        self.registry = registry
        model = self.registry.get_service(types.AgentModel)
        db = self.registry.get_service(core.DatabaseService)
        saver = self.registry.get_service(types.Saver)
        prompt_store = self.registry.get_service(prompting.PromptStore)
        toolkit = SQLDatabaseToolkit(db=db.db_tool, llm=model)
        tools = [*toolkit.get_tools(), *TOOLS]

        self.agent_executor = create_react_agent(
            model=model,
            tools=tools,
            state_schema=dto.AgentStateSchema,
            checkpointer=saver,
            prompt=prompt_store.agent_system_message,
        )

    def get_device_security_answer(
        self, question: str, thread_id: str | None = None, print_steps: bool = False
    ) -> str:
        if not thread_id:
            thread_id = utils.generate_random_string(5)

        response = "Nothing was generated!"
        for event in self.agent_executor.stream(
            {"messages": [{"role": "user", "content": question}]},
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
