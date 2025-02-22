import streamlit as st
from langchain.schema import AIMessage, BaseMessage, HumanMessage
from langchain_core.messages import ToolMessage

from hbit import bootstrap, endpoints, enums, utils

############################
# Configure Streamlit Page #
############################


st.set_page_config(page_title="👮‍♂️ Security Agent", page_icon="🚨")
st.title("👮‍♂️ Security Agent: Chat with security expert")

if "messages" not in st.session_state:
    # default initial message to render in message state
    st.session_state["messages"] = [AIMessage(content="How can I help you?")]

if "thread_id" not in st.session_state:
    thread_id = utils.generate_random_string(5)
    st.session_state["thread_id"] = thread_id


################
# Display Chat #
################

# Loop through all messages in the session state and render them as a chat on every st.refresh mech
for msg in st.session_state.messages:
    # https://docs.streamlit.io/develop/api-reference/chat/st.chat_message
    # we store them as AIMessage and HumanMessage as its easier to send to LangGraph
    if isinstance(msg, AIMessage):
        st.chat_message("assistant").write(msg.content)
    if isinstance(msg, HumanMessage):
        st.chat_message("user").write(msg.content)


###################
# Display Sidebar #
###################


# TODO: Add description to the sidebar configurations
def update_configuration() -> None:
    # reset chat on every model change
    st.session_state["messages"] = [AIMessage(content="How can I help you?")]

    registry = bootstrap.create_services(
        device_extractor_type=st.session_state.get("device_extractor_type")
        or enums.DeviceExtractorType.JSON,
        patch_extractor_type=st.session_state.get("patch_extractor_type")
        or enums.PatchExtractorType.JSON,
        summary_service_type=enums.SummaryServiceType.AI,
        model_provider=st.session_state.get("model_provider")
        or enums.ModelProvider.OPEN_AI,
    )
    agent_evaluator = endpoints.AgentDeviceEvaluator(registry)
    agent_graph = agent_evaluator.agent_executor
    st.session_state["registry"] = registry
    st.session_state["agent_graph"] = agent_graph


if "registry" not in st.session_state:
    update_configuration()


with st.sidebar:
    st.header("Mode Configuration", divider="gray")

    model_provider = st.pills(
        "Model Provider",
        list(enums.ModelProvider),
        selection_mode="single",
        key="model_provider",
        default=enums.ModelProvider.OPEN_AI,
        on_change=update_configuration,
    )
    device_extractor = st.pills(
        "Device Extractor",
        list(enums.DeviceExtractorType),
        selection_mode="single",
        key="device_extractor_type",
        default=enums.DeviceExtractorType.JSON,
        on_change=update_configuration,
    )
    patch_extractor = st.pills(
        "Patch Extractor",
        list(enums.PatchExtractorType),
        selection_mode="single",
        key="patch_extractor_type",
        default=enums.PatchExtractorType.JSON,
        on_change=update_configuration,
    )


##############
# Call Agent #
##############


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
