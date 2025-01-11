import logging
import typing

from langchain.prompts import (
    ChatPromptTemplate,
    FewShotChatMessagePromptTemplate,
)
from langchain_core.language_models import BaseChatModel
from langchain_core.prompt_values import PromptValue
from langchain_core.runnables import Runnable
from sqlalchemy import text as _text

from hbit import core, dto

from . import base

_log = logging.getLogger(__name__)

example_prompt = ChatPromptTemplate.from_messages(
    [
        ("human", "{input}"),
        ("ai", "{output}"),
    ]
)


class StructurePatchExtractor(base.PatchExtractor):
    patch_examples: typing.ClassVar[list[dict[str, str]]] = [
        {
            "input": "How secure is my iPhone 13 Pro patch if I have patch 18.1.0 installed identified by build 22B83.",
            "output": dto.Patch(build="22B83", version="18.1.0").model_dump_json(),
        },
        {
            "input": "The latest patch for my device is 17.7.2.",
            "output": dto.Patch(build=None, version="17.7.2").model_dump_json(),
        },
        {
            "input": "What version does my patch with build 22B83 have?",
            "output": dto.Patch(build="22B83", version=None).model_dump_json(),
        },
    ]
    few_shot_prompt = FewShotChatMessagePromptTemplate(
        example_prompt=example_prompt,
        examples=patch_examples,
    )
    prompt_template = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an expert extraction algorithm. "
                "Only extract relevant information from the text. "
                "Make sure you only extract the values of the attributes mentioned in the question. "
                "If you do not know the value of an attribute asked to extract, "
                "return null for the attribute's value.",
            ),
            few_shot_prompt,
            ("human", "{input}"),
        ]
    )

    def __init__(self, model: BaseChatModel, db: core.DatabaseService) -> None:
        self.model = model
        self.db = db
        self.extractor_model: Runnable[PromptValue, dto.Patch] = (
            self.model.with_structured_output(schema=dto.Patch)
        )  # type: ignore

    def extract_patch_build(self, text: str) -> str | None:
        patch = self.extract_patch_info(text)
        _log.debug(f"Extracted patch: {patch}")
        with self.db.connect() as connection:
            raw_sql = (
                "SELECT patches.build "
                "FROM patches as patches "
                "WHERE (:build is null OR patches.build like :build) "
                "AND (:version is null OR patches.version like :version);"
            )
            result = connection.scalar(
                _text(raw_sql),
                parameters={
                    "build": patch.build,
                    "version": patch.version,
                },
            )
        return result

    def extract_patch_info(self, text: str) -> dto.Patch:
        prompt = self.prompt_template.invoke({"input": text})
        patch = self.extractor_model.invoke(prompt)
        return patch


class SqlPatchExtractor(base.PatchExtractor):
    patch_examples: typing.ClassVar[list[dict[str, str]]] = [
        {
            "input": "How secure is my iPhone 13 Pro patch if I have patch 18.0.1 installed identified by build 22B83.",
            "output": "SELECT build FROM patches WHERE build LIKE '22B83' AND version LIKE '18.0.1'",
        },
        {
            "input": "The latest patch for my device is 17.7.2.",
            "output": "SELECT build FROM patches WHERE version LIKE '17.7.2'",
        },
        {
            "input": "What version does my patch with build 22B83 have?",
            "output": "SELECT build FROM patches WHERE build LIKE '22B83'",
        },
        {
            "input": "How secure is an iPhone XS running iOS 17.0.2? Are there any known vulnerabilities or security concerns with this version?",
            "output": "SELECT build FROM patches WHERE version LIKE '17.0.2'",
        },
    ]
    few_shot_prompt = FewShotChatMessagePromptTemplate(
        example_prompt=example_prompt,
        examples=patch_examples,
    )
    query_prompt_template = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Your task is to generate a syntactically correct {dialect} query based on the given input question. "
                "The purpose of the query is to extract the `build` column from the `patches` table. "
                "Follow these guidelines:\n"
                "1. Only filter by values explicitly mentioned in the input question that are relevant to the patch.\n"
                "2. Avoid querying columns that are not part of the schema or using incorrect example values.\n"
                "3. Prioritize using unique columns that can independently identify a patch.\n"
                "4. Use `LIKE` for string matching to ensure case-insensitive filtering.\n"
                "5. Completely ignore JSON fields.\n\n"
                "The schema of the `patches` table is as follows:\n"
                "{table_info}\n",
            ),
            few_shot_prompt,
            ("user", "Question: {input}"),
        ]
    )

    def __init__(self, model: BaseChatModel, db: core.DatabaseService) -> None:
        self.model = model
        self.db = db

    def extract_patch_build(self, text: str) -> str:
        query_output = self.create_extraction_query(text)
        _log.debug(f"Query: {query_output.query}")

        response = self.execute_query(query_output.query)
        return response

    def create_extraction_query(self, question: str) -> dto.QueryOutput:
        patches_table_info = self.db.get_table_info(["patches"])

        prompt = self.query_prompt_template.invoke(
            {
                "dialect": self.db.dialect,
                "table_info": patches_table_info,
                "input": question,
            }
        )

        structured_llm = self.model.with_structured_output(dto.QueryOutput)  # type: ignore
        result: dto.QueryOutput = structured_llm.invoke(prompt)  # type: ignore
        return result

    def execute_query(self, query: str) -> str:
        with self.db.connect() as connection:
            result = connection.scalar(_text(query))
        return result
