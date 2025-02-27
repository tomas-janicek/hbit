from langchain.prompts import (
    ChatPromptTemplate,
    FewShotChatMessagePromptTemplate,
    PromptTemplate,
)

from . import base, examples

example_prompt = ChatPromptTemplate.from_messages(
    [
        ("human", "{input}"),
        ("ai", "{output}"),
    ]
)


class ChatPromptStore(base.PromptStore):
    device_sql_few_shots = FewShotChatMessagePromptTemplate(
        example_prompt=example_prompt, examples=examples.device_sql_few_shot_examples
    )
    device_sql_extraction = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                (
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
            ),
            device_sql_few_shots,
            ("human", "{input}"),
        ]
    )

    device_json_few_shots = FewShotChatMessagePromptTemplate(
        example_prompt=example_prompt, examples=examples.device_json_few_shot_examples
    )
    device_json_extraction = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                (
                    "You are an expert extraction algorithm. "
                    "Only extract relevant information from the text. "
                    "Make sure you only extract the values of the attributes mentioned in the question. "
                    "If you do not know the value of an attribute asked to extract, "
                    "return null for the attribute's value. Return as a JSON object. "
                    "After extracting any information, make sure that "
                    "extracted data are really part of the user input. If not, this data are not valid!"
                ),
            ),
            device_json_few_shots,
            ("human", "{input}"),
        ]
    )

    patch_sql_few_shots = FewShotChatMessagePromptTemplate(
        example_prompt=example_prompt, examples=examples.patch_sql_few_shot_examples
    )
    patch_sql_extraction = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                (
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
            ),
            patch_sql_few_shots,
            ("human", "{input}"),
        ]
    )

    patch_json_few_shots = FewShotChatMessagePromptTemplate(
        example_prompt=example_prompt, examples=examples.patch_json_few_shot_examples
    )
    patch_json_extraction = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                (
                    "You are an expert extraction algorithm. "
                    "Only extract relevant information from the text. "
                    "Make sure you only extract the values of the attributes mentioned in the question. "
                    "If you do not know the value of an attribute asked to extract, "
                    "return null for the attribute's value. Return as a JSON object. "
                    "After extracting any information, make sure that "
                    "extracted data are really part of the user input. If not, this data are not valid!"
                ),
            ),
            patch_json_few_shots,
            ("human", "{input}"),
        ]
    )

    evaluation_part_summary = PromptTemplate.from_template(
        "You are expert cyber-security analyst. Given the evaluation, create summary. "
        "Bare in mind this summary will then be used with other summaries "
        "generated similar way.\n\n"
        "Evaluation Part:\n"
        "{evaluation_chunk}"
    )

    # TODO: Add structure to this summary, some points that should be returned to every device evaluation
    # TODO: Sections like weaknesses, recommendations, strengths (security features), overall security rating (one number),
    # TODO: most important vuls list, conclusion.
    evaluation_summary = PromptTemplate.from_template(
        "You are expert cyber-security analyst. Given the following summaries for different security "
        "evaluations generate security analysis.\n\n"
        "Evaluation Summaries:\n"
        "{summaries_str}"
    )

    evaluation_trimming = PromptTemplate.from_template(
        "You are a cybersecurity expert analyzing a vulnerability report in JSON format. "
        "Your task is to extract and return only the most critical information while ensuring that the JSON structure remains **completely unchanged**. "
        "This means:\n"
        "- **Do not remove any fields** under any circumstances.\n"
        "- If a field contains a list, you may reduce its contents by keeping only the most critical items, but the field itself must always remain.\n"
        '- If a field contains non-essential information, replace its value with an empty string (`""`), but **never set it to null** or delete it.\n'
        "- The final output **must contain every field from the original JSON, even if empty**.\n\n"
        "**Before finalizing your output, carefully compare your result to the original JSON to confirm that all fields are retained.**\n\n"
        "Here is the vulnerability data:\n\n"
        "{vulnerability}"
    )

    # TODO: Give agent more context to how he should approach evaluation
    # TODO: - ask user
    # TODO: - gather data
    # TODO: - ...
    agent_system_message = (
        "You are an expert cyber-security analyst. "
        "Your purpose is to request relevant information from user about what he want to analyze "
        "and then use this information to call tools that retrieve relevant security information "
        "about whatever user requested. If a tool fails due to missing or insufficient information, "
        "ask the user for the necessary details and retry.\n"
        "Other than tools, you can use DB queries to retrieve information. "
        "You have access to the database schema and can use it to retrieve information about devices, patches, CVEs, CWEs, etc."
    )
