import streamlit as st
from langchain.schema import AIMessage, BaseMessage, HumanMessage
from langchain_core.messages import ToolMessage

from hbit import bootstrap, endpoints, enums, utils

st.set_page_config(page_title="👮‍♂️ Security Agent", page_icon="🚨")
st.title("👮‍♂️ Security Agent: Chat with security expert")

if "messages" not in st.session_state:
    registry = bootstrap.create_services(
        device_extractor_type=enums.DeviceExtractorType.STRUCTURED_EXTRACTOR,
        patch_extractor_type=enums.PatchExtractorType.STRUCTURED_EXTRACTOR,
        device_evaluation_type=enums.DeviceEvaluationType.AI,
        patch_evaluation_type=enums.PatchEvaluationType.AI,
        summary_service_type=enums.SummaryServiceType.AI,
        model_provider=enums.ModelProvider.ANTHROPIC,
    )
    agent_evaluator = endpoints.AgentDeviceEvaluator(registry)
    agent_graph = agent_evaluator.agent_executor
    st.session_state["registry"] = registry
    st.session_state["agent_graph"] = agent_graph

if "messages" not in st.session_state:
    # default initial message to render in message state
    st.session_state["messages"] = [AIMessage(content="How can I help you?")]

if "thread_id" not in st.session_state:
    thread_id = utils.generate_random_string(5)
    st.session_state["thread_id"] = thread_id

# Loop through all messages in the session state and render them as a chat on every st.refresh mech
for msg in st.session_state.messages:
    # https://docs.streamlit.io/develop/api-reference/chat/st.chat_message
    # we store them as AIMessage and HumanMessage as its easier to send to LangGraph
    if isinstance(msg, AIMessage):
        st.chat_message("assistant").write(msg.content)
    if isinstance(msg, HumanMessage):
        st.chat_message("user").write(msg.content)


def call_agent(input: str) -> str:
    with st.status("🤔 Thinking") as status:
        thread_id = st.session_state.thread_id
        response = "Nothing was generated!"
        try:
            for event in st.session_state.agent_graph.stream(
                {"messages": [{"role": "user", "content": input}]},
                config={
                    "configurable": {
                        "registry": st.session_state.registry,
                        "thread_id": thread_id,
                    }
                },
                stream_mode="values",
            ):
                message: BaseMessage = event["messages"][-1]
                match message:
                    case ToolMessage():
                        st.write(f"Using: {message.name}")
                    case _:
                        pass

                response = str(message.content)
        except Exception:
            st.write("Something went wrong when calling agent.")
            status.update(label="⁉️ Error", state="error", expanded=False)
        else:
            status.update(label="✅ Completed", state="complete", expanded=False)

    return response


if input := st.chat_input():
    st.session_state.messages.append(HumanMessage(content=input))
    st.chat_message("user").write(input)

    with st.chat_message("assistant"):
        response = call_agent(input)

        # add that last message to the st_message_state
        st.session_state.messages.append(AIMessage(content=response))

        # visually refresh the complete response after the callback container
        st.write(response)
