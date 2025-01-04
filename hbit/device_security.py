import typing
from typing import Annotated

from groq import BaseModel
from langchain import hub
from langchain.schema import BaseMessage
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_community.utilities import SQLDatabase
from langchain_core.language_models import BaseChatModel
from langgraph.func import START  # type: ignore
from langgraph.graph import StateGraph  # type: ignore
from langgraph.prebuilt import create_react_agent  # type: ignore
from typing_extensions import TypedDict

db = SQLDatabase.from_uri("sqlite:///app.db")


class QueryOutput(BaseModel):
    """Generated SQL query."""

    query: Annotated[str, ..., "Syntactically valid SQL query."]


class State(TypedDict):
    question: str
    query: str
    result: str
    answer: str


class AgentDeviceEvaluator:
    def __init__(self, model: BaseChatModel) -> None:
        self.model = model
        self.toolkit = SQLDatabaseToolkit(db=db, llm=self.model)
        tools = self.toolkit.get_tools()
        prompt_template = hub.pull("langchain-ai/sql-agent-system-prompt")
        system_message = prompt_template.format(dialect="SQLite", top_k=5)
        self.agent_executor = create_react_agent(
            model=self.model,
            tools=tools,
            state_modifier=system_message,
        )

    def get_device_security_answer(self, question: str) -> str:
        response = "Nothing was generated!"
        for step in self.agent_executor.stream(
            {"messages": [{"role": "user", "content": question}]},
            stream_mode="values",
        ):
            message: BaseMessage = step["messages"][-1]
            message.pretty_print()
            response = str(message.content)
        return response


class ChainDeviceEvaluator:
    def __init__(self, model: BaseChatModel) -> None:
        self.model = model
        self.query_prompt_template = hub.pull("langchain-ai/sql-query-system-prompt")
        graph_builder = StateGraph(State).add_sequence(
            [self.write_query, self.execute_query, self.generate_answer]
        )
        graph_builder.add_edge(START, "write_query")
        self.graph = graph_builder.compile()

    def write_query(self, state: State) -> dict[str, typing.Any]:
        """Generate SQL query to fetch information."""
        prompt = self.query_prompt_template.invoke(
            {
                "dialect": db.dialect,
                "top_k": 10,
                "table_info": db.get_table_info(),
                "input": state["question"],
            }
        )
        structured_llm = self.model.with_structured_output(QueryOutput)  # type: ignore
        result: QueryOutput = structured_llm.invoke(prompt)  # type: ignore
        return {"query": result.query}

    def execute_query(self, state: State):
        """Execute SQL query."""
        execute_query_tool = QuerySQLDataBaseTool(db=db)
        return {"result": execute_query_tool.invoke(state["query"])}

    def generate_answer(self, state: State) -> dict[str, typing.Any]:
        """Answer question using retrieved information as `context."""
        prompt = (
            "Given the following user question, corresponding SQL query, "
            "and SQL result, answer the user question.\n\n"
            f'Question: {state["question"]}\n'
            f'SQL Query: {state["query"]}\n'
            f'SQL Result: {state["result"]}'
        )
        response = self.model.invoke(prompt)
        return {"answer": response.content}

    def get_device_security_answer(self, question: str) -> str:
        step: dict[str, typing.Any] = {}
        for step in self.graph.stream({"question": question}, stream_mode="updates"):
            print(step)

        return step["generate_answer"]["answer"]
