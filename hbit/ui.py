import chainlit as cl
from langchain.schema import AIMessage, BaseMessage, HumanMessage
from langchain_core.messages import ToolMessage

from hbit import bootstrap, endpoints, enums

registry = bootstrap.create_services(
    device_extractor_type=enums.DeviceExtractorType.STRUCTURED_EXTRACTOR,
    patch_extractor_type=enums.PatchExtractorType.STRUCTURED_EXTRACTOR,
    device_evaluation_type=enums.DeviceEvaluationType.IMPERATIVE,
    patch_evaluation_type=enums.PatchEvaluationType.IMPERATIVE,
    summary_service_type=enums.SummaryServiceType.AI,
    model_provider=enums.ModelProvider.OPEN_AI,
)
agent_evaluator = endpoints.AgentDeviceEvaluator(registry)
agent_graph = agent_evaluator.agent_executor


# @cl.on_message
# async def call_agent_without_context(input: cl.Message) -> None:
#     response = agent_evaluator.get_device_security_answer(
#         question=input.content, thread_id=cl.context.session.id
#     )
#     await cl.Message(content=response).send()


# @cl.on_message
# async def call_agent_with_callback(input: cl.Message) -> None:
#     response = "Nothing was generated!"
#     for event in agent_graph.stream(
#         {
#             "messages": [{"role": "user", "content": input.content}],
#             "state": {"patch_evaluation": None, "device_evaluation": None},
#         },
#         config={
#             "configurable": {"registry": registry, "thread_id": cl.context.session.id},
#             "callbacks": [cl.AsyncLangchainCallbackHandler()],
#         },
#         stream_mode="values",
#     ):
#         message: BaseMessage = event["messages"][-1]
#         response = str(message.content)

#     await cl.Message(content=response).send()


@cl.on_message
async def call_agent(input: cl.Message) -> None:
    cl.LangchainCallbackHandler()

    response = "Nothing was generated!"
    last_ai_message: AIMessage | None = None
    for event in agent_graph.stream(
        {
            "messages": [{"role": "user", "content": input.content}],
            "state": {"patch_evaluation": None, "device_evaluation": None},
        },
        config={
            "configurable": {"registry": registry, "thread_id": cl.context.session.id},
            "callbacks": [cl.LangchainCallbackHandler()],
        },
        stream_mode="values",
    ):
        message: BaseMessage = event["messages"][-1]
        response = str(message.content)

        match message:
            case HumanMessage():
                pass
            case AIMessage():
                last_ai_message = message
            case ToolMessage():
                async with cl.Step(name=message.name, type=message.type) as step:
                    step.input = str(last_ai_message.content) if last_ai_message else ""
                    step.output = str(message.content)
            case _:
                pass

    await cl.Message(content=response).send()
