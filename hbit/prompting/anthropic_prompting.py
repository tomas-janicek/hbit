from langchain.prompts import PromptTemplate

from . import base, examples


class AnthropicPromptingStore(base.PromptStore):
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

    device_json_extraction = PromptTemplate.from_template(
        template=(
            "You are an expert extraction algorithm designed to extract specific device information from user queries. Your task is to analyze the given input and extract relevant information about devices, particularly focusing on Apple products like iPhones.\n\n"
            "Here's the input text you need to analyze:\n\n"
            "<input>\n"
            "{{input}}\n"
            "</input>\n\n"
            "Instructions:\n"
            "1. Carefully read the input text.\n"
            "2. Extract the following information if present:\n"
            '   - identifier: A specific device identifier (e.g., "iphone14,2")\n'
            '   - name: The name of the device (e.g., "iPhone 13 Pro")\n'
            '   - manufacturer: The company that made the device (e.g., "Apple")\n'
            '   - model: The model number or name (e.g., "A2483")\n'
            "3. If any of these pieces of information are not present in the input, set their value to null.\n"
            '4. Be case-insensitive in your extraction (e.g., "iphone" and "iPhone" should be treated the same).\n'
            "5. Extract information even if it's not explicitly asked for in the query.\n\n"
            "Before providing the final output, wrap your analysis inside <extraction_process> tags:\n"
            "- List all potential device-related information found in the input, even if it doesn't fit into the four specific categories.\n"
            "- Categorize each piece of information into one of the four categories (identifier, name, manufacturer, model) or mark it as not fitting any category.\n"
            "- Explain your reasoning for each categorization.\n"
            "It's OK for this section to be quite long.\n\n"
            "Output Format:\n"
            "Provide your output as a JSON object with the following structure:\n"
            "{{\n"
            '  "identifier": [extracted value or null],\n'
            '  "name": [extracted value or null],\n'
            '  "manufacturer": [extracted value or null],\n'
            '  "model": [extracted value or null]\n'
            "}}\n\n"
            "Ensure that all four keys are present in your output, even if their values are null.\n\n"
            f"{examples.anthropic_device_json_examples}"
        )
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

    patch_json_extraction = PromptTemplate.from_template(
        template=(
            "You are an expert extraction algorithm designed to extract specific information from user inputs related to iPhone software updates. Your task is to extract only the build number and version number from the given input, ignoring all other information.\n\n"
            "Here's how you should approach this task:\n\n"
            "1. Carefully read the user input provided.\n"
            '2. Look for any mention of a build number (usually in the format "XXXXX" where X is a digit or letter) or a version number (usually in the format "XX.X.X" where X is a digit).\n'
            "3. If you find a build number, extract it. If not, set it to null.\n"
            "4. If you find a version number, extract it. If not, set it to null.\n"
            '5. Format your output as a JSON object with "build" and "version" keys.\n\n'
            "Important rules:\n"
            "- Only extract the build number and version number. Do not provide any additional information or answer any questions in the input.\n"
            "- If either the build number or version number is not present in the input, use null for that value in your output.\n"
            "- Always provide your output in the specified JSON format, even if both values are null.\n\n"
            "Here's the user input you need to analyze:\n\n"
            "<user_input>\n"
            "{input}\n"
            "</user_input>\n\n"
            "Before providing your final output, wrap your analysis in <analysis> tags. In this analysis:\n"
            "1. List all potential build numbers found in the input, even if they don't match the exact format.\n"
            "2. Explain why each potential build number is or isn't valid.\n"
            "3. List all potential version numbers found in the input, even if they don't match the exact format.\n"
            "4. Explain why each potential version number is or isn't valid.\n"
            "5. State your final decision on which build number and version number (if any) to extract.\n\n"
            "Then, provide your JSON output."
            f"{examples.anthropic_patch_json_examples}"
        ),
    )
