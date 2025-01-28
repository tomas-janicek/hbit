import logging
import typing

from langchain.prompts import (
    ChatPromptTemplate,
)
from langchain_core.language_models import BaseChatModel
from langchain_core.runnables import RunnableSerializable
from sqlalchemy import text as _text

from hbit import core, dto, utils

from . import base

_log = logging.getLogger(__name__)


class StructurePatchExtractor(base.PatchExtractor):
    examples = (
        "Input Example: 'How secure is my iPhone 13 Pro patch if I have patch 18.1.0 installed identified by build 22B83.'\n"
        f"Output Example: {{{dto.Patch(build='22B83', version='18.1.0').model_dump_json()}}}\n\n"
        "Input Example: 'The latest patch for my device is 17.7.2.'\n"
        f"Output Example: {{{dto.Patch(build=None, version='17.7.2').model_dump_json()}}}\n\n"
        "Input Example: 'What version does my patch with build 22B83 have?'\n"
        f"Output Example: {{{dto.Patch(build='22B83', version=None).model_dump_json()}}}\n\n"
        "Input Example: How secure is an iPhone XS running iOS 17.0.2? Are there any known vulnerabilities or security concerns with this version?\n"
        f"Output Example: {{{dto.Patch(build=None, version='17.0.2').model_dump_json()}}}\n\n"
        "Input Example: What's the latest iOS patch for iPhone 14?\n"
        f"Output Example: {{{dto.Patch(build=None, version=None).model_dump_json()}}}\n\n"
        "Input Example: Is my iPhone 14 Pro on iOS 16.3 safe from known vulnerabilities?\n"
        f"Output Example: {{{dto.Patch(build=None, version='16.3').model_dump_json()}}}\n\n"
    )

    prompt_template = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an expert extraction algorithm. "
                "Only extract relevant information from the text. "
                "Make sure you only extract the values of the attributes mentioned in the question. "
                "If you do not know the value of an attribute asked to extract, "
                "return null for the attribute's value.\n\n"
                "Output Format:\n"
                "After your extraction process, provide the extracted information in JSON format. "
                "The JSON should contain two keys: 'version' and 'build'. If a value is not found, it should be set to null."
                "Example output structure:\n"
                "{\n"
                '    "version": "[extracted version or null]",\n'
                '    "build": "[extracted build or null]"\n'
                "}\n\n"
                "{examples}",
            ),
            ("human", "{input}"),
        ]
    )

    def __init__(self, model: BaseChatModel, db: core.DatabaseService) -> None:
        self.model = model
        self.db = db
        self.extractor_model: RunnableSerializable[dict[str, typing.Any], dto.Patch] = (
            self.prompt_template | self.model.with_structured_output(schema=dto.Patch)
        )  # type: ignore

    def extract_patch_build(self, text: str) -> str | None:
        patch = self.extract_patch_info(text)
        _log.debug(f"Extracted patch: {patch}")
        if utils.are_all_fields_none(patch):
            return None

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
                    "version": f"%{patch.version}%" if patch.version else None,
                },
            )
        return result

    def extract_patch_info(self, text: str) -> dto.Patch:
        patch = self.extractor_model.invoke({"input": text, "examples": self.examples})
        return patch


class SqlPatchExtractor(base.PatchExtractor):
    examples = (
        "Input Example: How secure is my iPhone 13 Pro patch if I have patch 18.0.1 installed identified by build 22B83.\n"
        "Output Example: SELECT build FROM patches WHERE build LIKE '22B83' AND version LIKE '%18.0.1%'\n\n"
        "Input Example: The latest patch for my device is 17.7.2.\n"
        "Output Example: SELECT build FROM patches WHERE version LIKE '%17.7.2%'\n\n"
        "Input Example: What version does my patch with build 22B83 have?\n"
        "Output Example: SELECT build FROM patches WHERE build LIKE '22B83'\n\n"
        "Input Example: How secure is an iPhone XS running iOS 17.0.2? Are there any known vulnerabilities or security concerns with this version?\n"
        "Output Example: SELECT build FROM patches WHERE version LIKE '%17.0.2%'\n\n"
        "Input Example: What's the latest iOS patch for iPhone 14?\n"
        "Output Example: \n\n"
        "Input Example: Is my iPhone 14 Pro on iOS 16.3 safe from known vulnerabilities?\n"
        "Output Example: SELECT build FROM patches WHERE version LIKE '%16.3%'\n\n"
    )

    query_prompt_template = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Your task is to generate a syntactically correct {dialect} query based on the given input question. "
                "The purpose of the query is to extract the `build` column from the `patches` table. If there is no "
                "mention of any patch, return empty string instead of SQL query.\n"
                "Follow these guidelines:\n"
                "1. Only filter by values explicitly mentioned in the input question that are relevant to the patch.\n"
                "2. Avoid querying columns that are not part of the schema or using incorrect example values.\n"
                "3. Prioritize using unique columns that can independently identify a patch.\n"
                "4. Use `LIKE` for string matching to ensure case-insensitive filtering.\n"
                "5. Completely ignore JSON fields.\n"
                "6. Return empty string when there is not data about patch in input.\n\n"
                "The schema of the `patches` table is as follows:\n"
                "{table_info}\n"
                "Examples:"
                "{examples}",
            ),
            ("user", "Question: {input}"),
        ]
    )

    def __init__(self, model: BaseChatModel, db: core.DatabaseService) -> None:
        self.model = model
        self.db = db

        self.structured_llm: RunnableSerializable[
            dict[str, typing.Any], dto.QueryOutput
        ] = self.query_prompt_template | self.model.with_structured_output(
            dto.QueryOutput
        )  # type: ignore

    def extract_patch_build(self, text: str) -> str | None:
        query_output = self.create_extraction_query(text)
        if not query_output.query:
            return None

        _log.debug(f"Query: {query_output.query}")
        response = self.execute_query(query_output.query)
        return response

    def create_extraction_query(self, question: str) -> dto.QueryOutput:
        patches_table_info = self.db.get_table_info(["patches"])

        result: dto.QueryOutput = self.structured_llm.invoke(
            {
                "dialect": self.db.dialect,
                "table_info": patches_table_info,
                "input": question,
                "examples": self.examples,
            }
        )
        return result

    def execute_query(self, query: str) -> str:
        with self.db.connect() as connection:
            result = connection.scalar(_text(query))
        return result
