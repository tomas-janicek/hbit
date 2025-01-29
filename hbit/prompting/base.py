# TODO: What prompts does this need to hold?
from langchain.prompts import BasePromptTemplate


class PromptStore:
    device_sql_extraction: BasePromptTemplate[str]
    device_json_extraction: BasePromptTemplate[str]
    patch_sql_extraction: BasePromptTemplate[str]
    patch_json_extraction: BasePromptTemplate[str]
