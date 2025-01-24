from langchain.schema import BaseMessage
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langgraph.prebuilt import create_react_agent  # type: ignore

from hbit import core, dto, services, types
from hbit.tools import TOOLS


class AgentDeviceEvaluator:
    def __init__(self, registry: services.ServiceContainer) -> None:
        self.registry = registry
        model = self.registry.get_service(types.DefaultModel)
        db = self.registry.get_service(core.DatabaseService)
        toolkit = SQLDatabaseToolkit(db=db.db_tool, llm=model)
        tools = [*toolkit.get_tools(), *TOOLS]

        self.config = {"registry": self.registry}
        self.agent_executor = create_react_agent(
            model=model, tools=tools, state_schema=dto.AgentStateSchema
        )

    def get_device_security_answer(self, question: str) -> str:
        response = "Nothing was generated!"
        for event in self.agent_executor.stream(
            {"messages": [{"role": "user", "content": question}]},
            config={"configurable": self.config},
            stream_mode="values",
        ):
            message: BaseMessage = event["messages"][-1]
            message.pretty_print()
            response = str(message.content)

        return response
