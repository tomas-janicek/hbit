from langchain.prompts import PromptTemplate

from . import base, examples


class GeneralPromptStore(base.PromptStore):
    device_sql_extraction = PromptTemplate.from_examples(
        examples=examples.device_sql_examples,
        prefix=(
            "Your task is to generate a syntactically correct {dialect} query based on the given input question. "
            "The purpose of the query is to extract the `identifier` column from the `devices` table. "
            "If there is no mention of any device, return empty string instead of SQL query.\n"
            "Follow these guidelines:\n"
            "1. Only filter by values explicitly mentioned in the input question that are relevant to the device.\n"
            "2. Avoid querying columns that are not part of the schema or values do not resamble values in rows.\n"
            "3. Prioritize using unique columns that can independently identify a device by themselves.\n"
            "4. Use `LIKE` for string matching to ensure case-insensitive filtering.\n"
            "5. Completely ignore JSON fields.\n"
            "6. Make sure values you are filtering by resemble the values in the schema."
            "\n\n"
            "The schema of the `devices` table is as follows:\n"
            "{table_info}"
        ),
        suffix=("Input: {input}\nOutput: "),
        input_variables=["dialect", "table_info", "input"],
    )

    device_json_extraction = PromptTemplate.from_examples(
        examples=examples.device_json_examples,
        prefix=(
            "You are an expert extraction algorithm. "
            "Only extract relevant information from the text. "
            "Make sure you only extract the values of the attributes mentioned in the question. "
            "If you do not know the value of an attribute asked to extract, "
            "return null for the attribute's value."
        ),
        suffix=("Input: {input}\nOutput: "),
        input_variables=["input"],
    )

    patch_sql_extraction = PromptTemplate.from_examples(
        examples=examples.patch_sql_examples,
        prefix=(
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
            "{table_info}"
        ),
        suffix=("Input: {input}\nOutput: "),
        input_variables=["dialect", "table_info", "input"],
    )

    patch_json_extraction = PromptTemplate.from_examples(
        examples=examples.patch_json_examples,
        prefix=(
            "You are an expert extraction algorithm. "
            "Only extract relevant information from the text. "
            "Make sure you only extract the values of the attributes mentioned in the question. "
            "If you do not know the value of an attribute asked to extract, "
            "return null for the attribute's value."
        ),
        suffix=("Input: {input}\nOutput: "),
        input_variables=["input"],
    )
