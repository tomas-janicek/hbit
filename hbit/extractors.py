from langchain.prompts import (
    ChatPromptTemplate,
    FewShotChatMessagePromptTemplate,
)
from langchain_core.prompt_values import PromptValue
from langchain_core.runnables import Runnable
from langchain_groq import ChatGroq
from pydantic import BaseModel

example_prompt = ChatPromptTemplate.from_messages(
    [
        ("human", "{input}"),
        ("ai", "{output}"),
    ]
)


class Device(BaseModel):
    identifier: str | None
    name: str | None
    manufacturer: str | None
    model: str | None


device_examples = [
    {
        "input": "How secure is my iPhone 13 Pro device if I have patch 18.1.0 installed identified by build 22B83.",
        "output": Device(
            identifier=None, name="iPhone 13 Pro", manufacturer="Apple", model=None
        ),
    },
    {
        "input": "How secure is my device with model A2483.",
        "output": Device(
            identifier=None, name=None, manufacturer="Apple", model="a2483"
        ),
    },
    {
        "input": "Should I buy new phone if I have iphone14,2.",
        "output": Device(
            identifier="iphone14,2", name=None, manufacturer="Apple", model=None
        ),
    },
]


# TODO: Create class that wraps this two return and behavior they provide
def create_device_extractor() -> (
    tuple[Runnable[PromptValue, Device], ChatPromptTemplate]
):
    model = ChatGroq(model="llama3-8b-8192")  # type: ignore
    extractor_model: Runnable[PromptValue, Device] = model.with_structured_output(
        schema=Device
    )  # type: ignore

    few_shot_prompt = FewShotChatMessagePromptTemplate(
        example_prompt=example_prompt,
        examples=device_examples,
    )

    prompt_template = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an expert extraction algorithm. "
                "Only extract relevant information from the text. "
                "If you do not know the value of an attribute asked to extract, "
                "return null for the attribute's value.",
            ),
            few_shot_prompt,
            ("human", "{input}"),
        ]
    )

    return extractor_model, prompt_template
