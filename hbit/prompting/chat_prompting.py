from langchain.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate

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
                    "return null for the attribute's value."
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
                    "return null for the attribute's value. Return as a JSON object."
                ),
            ),
            patch_json_few_shots,
            ("human", "{input}"),
        ]
    )

    evaluation_part_summary = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                (
                    "Given the following user question, and evaluation, "
                    "answer the user's question, create summary of given evaluation. "
                    "Bare in mind this summary will then be used with other summaries "
                    "generated similar way.\n\n"
                    "Evaluation Part:\n"
                    "{evaluation_chunk}"
                ),
            ),
            ("human", "User's question: {input}"),
        ]
    )

    # TODO: Add structure to this summary, some points that should be returned to every device evaluation
    # TODO: Sections like weaknesses, recommendations, strengths (security features), overall security rating (one number),
    # TODO: most important vuls list, conclusion.
    evaluation_summary = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                (
                    "You are expert cyber-security analyst."
                    "Given the following user's question and summaries for different security "
                    "evaluations generate security analysis to user's question.\n\n"
                    "Evaluation Summaries:\n"
                    "{summaries_str}"
                ),
            ),
            ("human", "User's question: {input}"),
        ]
    )

    device_evaluation_trimming = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                (
                    "You are a cybersecurity expert analyzing a vulnerability report in JSON format. "
                    "Given the following user's question, and summaries for different security evaluations generate analysis to user's question."
                    "Your task is to extract and return only the most critical information while ensuring the JSON structure remains unchanged. "
                    "Prioritize elements that, if exploited, pose the most significant security risks to the user. "
                    "You may trim non-essential details within fields but **must not remove any JSON fields under any circumstances**. "
                    "If a field contains a list, you may reduce its contents by keeping only the most critical items, but the field itself must remain. "
                    'Do not delete fields, set them to null, or alter the structure. Instead, replace non-essential values with an empty string (`""`). '
                    "Ensure that the JSON output retains every original field while containing only the most essential security-related information.\n\n"
                    "Here is the vulnerability data:\n\n"
                    "{vulnerability}"
                ),
            )
        ]
    )

    patch_evaluation_trimming = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                (
                    "You are a cyber-security expert tasked with analyzing a vulnerability data provided in JSON format. "
                    "Given the following user's question, and summaries for different security evaluations generate analysis to user's question."
                    "Your goal is to identify and return only the most critical parts of given vulnerability. "
                    "Focus on parts that, if exploited, could cause significant problems for the user. Ensure the JSON structure "
                    "of the vulnerability remains unchanged. If any field within a vulnerability contains a list of items, you can also "
                    "remove less important items from those lists, while retaining only the most critical information. "
                    "Remove or exclude less important vulnerabilities and details while maintaining the overall format. "
                    "Never remove fields completely or replace their value with null. If you want to remove any information, "
                    "set filed to empty string. Make sure you do not remove any JSON fields!\n\n"
                    "Here is the vulnerability:\n\n"
                    "{vulnerability}"
                ),
            )
        ]
    )

    # TODO: Give agent more context to how he should approach evaluation
    # - ask user
    # - gather data
    # - ...
    agent_system_message = (
        "You are an expert cyber-security analyst. "
        "Your purpose is to request relevant information from user about what he want to analyze "
        "and then use this information to call tools that retrieve relevant security information "
        "about whatever user requested.\n"
        "Follow these guidelines:\n"
        "- Your task is to analyze user's device and patch so if user did not provide any relevant information, "
        "about what device and patch ask him to specify what device he is using and what version or patch "
        "is installed on that device.\n"
        "- If you retrieve any evaluation, create summary and return the response to user.\n"
    )
