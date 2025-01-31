# TODO: What prompts does this need to hold?
from langchain.prompts import BasePromptTemplate


class PromptStore:
    device_sql_extraction: BasePromptTemplate[str]
    device_json_extraction: BasePromptTemplate[str]
    patch_sql_extraction: BasePromptTemplate[str]
    patch_json_extraction: BasePromptTemplate[str]
    evaluation_part_summary: BasePromptTemplate[str]
    evaluation_summary: BasePromptTemplate[str]
    evaluation_trimming: BasePromptTemplate[str]
    agent_system_message: str
