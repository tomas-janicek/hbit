from hbit import dto

device_sql_examples = [
    "Input: How secure is my iPhone 13 Pro device if I have patch 18.1.0 installed identified by build 22B83.\n"
    "Output: SELECT identifier FROM devices WHERE name LIKE 'iPhone 13 Pro'",
    "Input: How secure is my device with model Apple device with model A2483.\n"
    "Output: SELECT identifier FROM devices WHERE models LIKE '%A2483%'",
    "Input: Should I buy new phone if I have iphone14,2.\n"
    "Output: SELECT identifier FROM devices WHERE identifier LIKE 'iphone14,2'",
    "Input: Is iPhone 6 and iphone7,2 the same device?\n"
    "Output: SELECT identifier FROM devices WHERE identifier LIKE 'iphone7,2' AND name LIKE 'iPhone 6'",
    "Input: How secure is an iPhone XS running iOS 17.7.2? Are there any known vulnerabilities or security concerns with this version?\n"
    "Output: SELECT identifier FROM devices WHERE name LIKE 'iPhone XS'",
    "Input: Which version is my iPhone running if the patch is labeled with build 24D12?\n"
    "Output: ",
    "Input: Can you tell me the version number for the patch identified by build 23C45?\n"
    "Output: ",
]

device_sql_few_shot_examples = [
    {
        "input": "How secure is my iPhone 13 Pro device if I have patch 18.1.0 installed identified by build 22B83.",
        "output": f"{{{dto.QueryOutput(query="SELECT identifier FROM devices WHERE name LIKE 'iPhone 13 Pro'").model_dump_json()}}}",
    },
    {
        "input": "How secure is my device with model Apple device with model A2483.",
        "output": f"{{{dto.QueryOutput(query="SELECT identifier FROM devices WHERE models LIKE '%A2483%'").model_dump_json()}}}",
    },
    {
        "input": "Should I buy new phone if I have iphone14,2.",
        "output": f"{{{dto.QueryOutput(query="SELECT identifier FROM devices WHERE identifier LIKE 'iphone14,2'").model_dump_json()}}}",
    },
    {
        "input": "Is iPhone 6 and iphone7,2 the same device?",
        "output": f"{{{dto.QueryOutput(query="SELECT identifier FROM devices WHERE identifier LIKE 'iphone7,2' AND name LIKE 'iPhone 6'").model_dump_json()}}}",
    },
    {
        "input": "How secure is an iPhone XS running iOS 17.7.2? Are there any known vulnerabilities or security concerns with this version?",
        "output": f"{{{dto.QueryOutput(query="SELECT identifier FROM devices WHERE name LIKE 'iPhone XS'").model_dump_json()}}}",
    },
    {
        "input": "Which version is my iPhone running if the patch is labeled with build 24D12?",
        "output": f"{{{dto.QueryOutput(query='').model_dump_json()}}}",
    },
    {
        "input": "Can you tell me the version number for the patch identified by build 23C45?",
        "output": f"{{{dto.QueryOutput(query='').model_dump_json()}}}",
    },
]

device_json_examples = [
    "Input: How secure is my iPhone 13 Pro device if I have patch 18.1.0 installed identified by build 22B83.\n"
    f"Output: {{{dto.Device(identifier=None, name='iPhone 13 Pro', manufacturer=None, model=None).model_dump_json()}}}",
    "Input: How secure is my device with model Apple device with model A2483.\n"
    f"Output: {{{dto.Device(identifier=None, name=None, manufacturer='Apple', model='a2483').model_dump_json()}}}",
    "Input: Should I buy new phone if I have iphone14,2.\n"
    f"Output: {{{dto.Device(identifier='iphone14,2', name=None, manufacturer=None, model=None).model_dump_json()}}}",
    "Input: Is iPhone 6 and iphone7,2 the same device?\n"
    f"Output: {{{dto.Device(identifier='iphone7,2', name='iPhone 6', manufacturer=None, model=None).model_dump_json()}}}",
    "Input: How secure is an iPhone XS running iOS 17.7.2? Are there any known vulnerabilities or security concerns with this version?\n"
    f"Output: {{{dto.Device(identifier=None, name='iPhone XS', manufacturer=None, model=None).model_dump_json()}}}",
    "Input: Which version is my iPhone running if the patch is labeled with build 24D12?\n"
    f"Output: {{{dto.Device(identifier=None, name=None, manufacturer=None, model=None).model_dump_json()}}}",
    "Input: Can you tell me the version number for the patch identified by build 23C45?\n"
    f"Output: {{{dto.Device(identifier=None, name=None, manufacturer=None, model=None).model_dump_json()}}}",
]

device_json_few_shot_examples = [
    {
        "input": "How secure is my iPhone 13 Pro device if I have patch 18.1.0 installed identified by build 22B83.",
        "output": f"{{{dto.Device(identifier=None, name='iPhone 13 Pro', manufacturer=None, model=None).model_dump_json()}}}",
    },
    {
        "input": "How secure is my device with model Apple device with model A2483.",
        "output": f"{{{dto.Device(identifier=None, name=None, manufacturer='Apple', model='a2483').model_dump_json()}}}",
    },
    {
        "input": "Should I buy new phone if I have iphone14,2.",
        "output": f"{{{dto.Device(identifier='iphone14,2', name=None, manufacturer=None, model=None).model_dump_json()}}}",
    },
    {
        "input": "Is iPhone 6 and iphone7,2 the same device?",
        "output": f"{{{dto.Device(identifier='iphone7,2', name='iPhone 6', manufacturer=None, model=None).model_dump_json()}}}",
    },
    {
        "input": "How secure is an iPhone XS running iOS 17.7.2? Are there any known vulnerabilities or security concerns with this version?",
        "output": f"{{{dto.Device(identifier=None, name='iPhone XS', manufacturer=None, model=None).model_dump_json()}}}",
    },
    {
        "input": "Which version is my iPhone running if the patch is labeled with build 24D12?",
        "output": f"{{{dto.Device(identifier=None, name=None, manufacturer=None, model=None).model_dump_json()}}}",
    },
    {
        "input": "Can you tell me the version number for the patch identified by build 23C45?",
        "output": f"{{{dto.Device(identifier=None, name=None, manufacturer=None, model=None).model_dump_json()}}}",
    },
]

patch_sql_examples = [
    "Input: How secure is my iPhone 13 Pro patch if I have patch 18.0.1 installed identified by build 22B83.\n"
    "Output: SELECT build FROM patches WHERE build LIKE '22B83' AND version LIKE '%18.0.1%'",
    "Input: The latest patch for my device is 17.7.2.\n"
    "Output: SELECT build FROM patches WHERE version LIKE '%17.7.2%'",
    "Input: What version does my patch with build 22B83 have?\n"
    "Output: SELECT build FROM patches WHERE build LIKE '22B83'",
    "Input: How secure is an iPhone XS running iOS 17.0.2? Are there any known vulnerabilities or security concerns with this version?\n"
    "Output: SELECT build FROM patches WHERE version LIKE '%17.0.2%'",
    "Input: What's the latest iOS patch for iPhone 14?\nOutput: ",
    "Input: Is my iPhone 14 Pro on iOS 16.3 safe from known vulnerabilities?\n"
    "Output: SELECT build FROM patches WHERE version LIKE '%16.3%'",
]

patch_sql_few_shot_examples = [
    {
        "input": "How secure is my iPhone 13 Pro patch if I have patch 18.0.1 installed identified by build 22B83.",
        "output": f"{{{dto.QueryOutput(query="SELECT build FROM patches WHERE build LIKE '22B83' AND version LIKE '%18.0.1%'").model_dump_json()}}}",
    },
    {
        "input": "The latest patch for my device is 17.7.2.",
        "output": f"{{{dto.QueryOutput(query="SELECT build FROM patches WHERE version LIKE '%17.7.2%'").model_dump_json()}}}",
    },
    {
        "input": "What version does my patch with build 22B83 have?",
        "output": f"{{{dto.QueryOutput(query="SELECT build FROM patches WHERE build LIKE '22B83'").model_dump_json()}}}",
    },
    {
        "input": "How secure is an iPhone XS running iOS 17.0.2? Are there any known vulnerabilities or security concerns with this version?",
        "output": f"{{{dto.QueryOutput(query="SELECT build FROM patches WHERE version LIKE '%17.0.2%'").model_dump_json()}}}",
    },
    {
        "input": "What's the latest iOS patch for iPhone 14?",
        "output": f"{{{dto.QueryOutput(query='').model_dump_json()}}}",
    },
    {
        "input": "Is my iPhone 14 Pro on iOS 16.3 safe from known vulnerabilities?",
        "output": f"{{{dto.QueryOutput(query="SELECT build FROM patches WHERE version LIKE '%16.3%'").model_dump_json()}}}",
    },
]

patch_json_examples = [
    "Input: How secure is my iPhone 13 Pro patch if I have patch 18.1.0 installed identified by build 22B83."
    f"Output: {{{dto.Patch(build='22B83', version='18.1.0').model_dump_json()}}}",
    "Input: The latest patch for my device is 17.7.2.'\n"
    f"Output: {{{dto.Patch(build=None, version='17.7.2').model_dump_json()}}}",
    "Input: What version does my patch with build 22B83 have?'\n"
    f"Output: {{{dto.Patch(build='22B83', version=None).model_dump_json()}}}",
    "Input: How secure is an iPhone XS running iOS 17.0.2? Are there any known vulnerabilities or security concerns with this version?\n"
    f"Output: {{{dto.Patch(build=None, version='17.0.2').model_dump_json()}}}",
    "Input: What's the latest iOS patch for iPhone 14?\n"
    f"Output: {{{dto.Patch(build=None, version=None).model_dump_json()}}}",
    "Input: Is my iPhone 14 Pro on iOS 16.3 safe from known vulnerabilities?\n"
    f"Output: {{{dto.Patch(build=None, version='16.3').model_dump_json()}}}",
]

patch_json_few_shot_examples = [
    {
        "input": "How secure is my iPhone 13 Pro patch if I have patch 18.1.0 installed identified by build 22B83.",
        "output": f"{{{dto.Patch(build='22B83', version='18.1.0').model_dump_json()}}}",
    },
    {
        "input": "The latest patch for my device is 17.7.2.",
        "output": f"{{{dto.Patch(build=None, version='17.7.2').model_dump_json()}}}",
    },
    {
        "input": "What version does my patch with build 22B83 have?",
        "output": f"{{{dto.Patch(build='22B83', version=None).model_dump_json()}}}",
    },
    {
        "input": "How secure is an iPhone XS running iOS 17.0.2? Are there any known vulnerabilities or security concerns with this version?",
        "output": f"{{{dto.Patch(build=None, version='17.0.2').model_dump_json()}}}",
    },
    {
        "input": "What's the latest iOS patch for iPhone 14?",
        "output": f"{{{dto.Patch(build=None, version=None).model_dump_json()}}}",
    },
    {
        "input": "Is my iPhone 14 Pro on iOS 16.3 safe from known vulnerabilities?",
        "output": f"{{{dto.Patch(build=None, version='16.3').model_dump_json()}}}",
    },
]


anthropic_patch_json_examples = (
    "<examples>\n"
    "<example>\n"
    "<input>\n"
    "How secure is my iPhone 13 Pro patch if I have patch 18.1.0 installed identified by build 22B83.\n"
    "</input>\n"
    "<ideal_output>\n"
    "<analysis>\n"
    "1. Potential build numbers found:\n"
    "   - 22B83\n"
    "2. Validity of potential build numbers:\n"
    "   - 22B83: This is a valid build number. It follows the typical format of two digits followed by a letter and two more digits.\n"
    "3. Potential version numbers found:\n"
    "   - 18.1.0\n"
    "4. Validity of potential version numbers:\n"
    "   - 18.1.0: This is a valid version number. It follows the standard format of XX.X.X where X is a digit.\n"
    "5. Final decision:\n"
    "   Based on the analysis, we will extract the build number 22B83 and the version number 18.1.0.\n"
    "</analysis>\n"
    '{{"build":"22B83","version":"18.1.0"}}\n'
    "</ideal_output>\n"
    "</example>\n\n"
    "<example>\n"
    "<input>\n"
    "The latest patch for my device is 17.7.2.\n"
    "</input>\n"
    "<ideal_output>\n"
    "<analysis>\n"
    "1. Potential build numbers found:\n"
    "   - None\n"
    "2. Validity of potential build numbers:\n"
    "   - N/A (No potential build numbers found)\n"
    "3. Potential version numbers found:\n"
    "   - 17.7.2\n"
    "4. Validity of potential version numbers:\n"
    "   - 17.7.2: This is a valid version number. It follows the standard format of XX.X.X where X is a digit.\n"
    "5. Final decision:\n"
    "   Based on the analysis, we will extract the version number 17.7.2. There is no build number present in the input, so it will be set to null.\n"
    "</analysis>\n"
    '{{"build":null,"version":"17.7.2"}}\n'
    "</ideal_output>\n"
    "</example>\n\n"
    "<example>\n"
    "<input>\n"
    "What version does my patch with build 22B83 have?\n"
    "</input>\n"
    "<ideal_output>\n"
    "<analysis>\n"
    "1. Potential build numbers found:\n"
    "   - 22B83\n"
    "2. Validity of potential build numbers:\n"
    "   - 22B83: This is a valid build number. It follows the typical format of two digits followed by a letter and two more digits.\n"
    "3. Potential version numbers found:\n"
    "   - None\n"
    "4. Validity of potential version numbers:\n"
    "   - N/A (No potential version numbers found)\n"
    "5. Final decision:\n"
    "   Based on the analysis, we will extract the build number 22B83. There is no version number present in the input, so it will be set to null.\n"
    "</analysis>\n"
    '{{"build":"22B83","version":null}}\n'
    "</ideal_output>\n"
    "</example>\n\n"
    "<example>\n"
    "<input>\n"
    "How secure is an iPhone XS running iOS 17.0.2? Are there any known vulnerabilities or security concerns with this version?\n"
    "</input>\n"
    "<ideal_output>\n"
    "<analysis>\n"
    "1. Potential build numbers found:\n"
    "   - None\n"
    "2. Validity of potential build numbers:\n"
    "   - N/A (No potential build numbers found)\n"
    "3. Potential version numbers found:\n"
    "   - 17.0.2\n"
    "4. Validity of potential version numbers:\n"
    "   - 17.0.2: This is a valid version number. It follows the standard format of XX.X.X where X is a digit.\n"
    "5. Final decision:\n"
    "   Based on the analysis, we will extract the version number 17.0.2. There is no build number present in the input, so it will be set to null.\n"
    "</analysis>\n"
    '{{"build":null,"version":"17.0.2"}}\n'
    "</ideal_output>\n"
    "</example>\n\n"
    "<example>\n"
    "<input>\n"
    "What's the latest iOS patch for iPhone 14?\n"
    "</input>\n"
    "<ideal_output>\n"
    "<analysis>\n"
    "1. Potential build numbers found:\n"
    "   - None\n"
    "2. Validity of potential build numbers:\n"
    "   - N/A (No potential build numbers found)\n"
    "3. Potential version numbers found:\n"
    "   - None\n"
    "4. Validity of potential version numbers:\n"
    "   - N/A (No potential version numbers found)\n"
    "5. Final decision:\n"
    "   Based on the analysis, there are no valid build numbers or version numbers present in the input. Both will be set to null in the output.\n"
    "</analysis>\n"
    '{{"build":null,"version":null}}\n'
    "</ideal_output>\n"
    "</example>\n\n"
    "<example>\n"
    "<input>\n"
    "Is my iPhone 14 Pro on iOS 16.3 safe from known vulnerabilities?\n"
    "</input>\n"
    "<ideal_output>\n"
    "<analysis>\n"
    "1. Potential build numbers found:\n"
    "   - None\n"
    "2. Validity of potential build numbers:\n"
    "   - N/A (No potential build numbers found)\n"
    "3. Potential version numbers found:\n"
    "   - 16.3\n"
    "4. Validity of potential version numbers:\n"
    "   - 16.3: This is a valid version number. Although it doesn't have a third decimal place, it still follows a valid format of XX.X where X is a digit.\n\n"
    "5. Final decision:\n"
    "   Based on the analysis, we will extract the version number 16.3. There is no build number present in the input, so it will be set to null.\n\n"
    "</analysis>\n"
    '{{"build":null,"version":"16.3"}}\n'
    "</ideal_output>\n"
    "</example>\n\n"
    "</examples>\n\n"
)

anthropic_device_json_examples = (
    "<examples>\n"
    "<example>\n"
    "<input>\n"
    "How secure is my iPhone 13 Pro device if I have patch 18.1.0 installed identified by build 22B83.\n"
    "</input>\n"
    "<ideal_output>\n"
    "<extraction_process>\n"
    "Potential device-related information found:\n"
    "- iPhone 13 Pro\n"
    "- patch 18.1.0\n"
    "- build 22B83\n"
    "Categorization:\n"
    '1. "iPhone 13 Pro":\n'
    "   - Category: name\n"
    "   - Reasoning: This is the specific name of an Apple iPhone model.\n"
    '2. "patch 18.1.0":\n'
    "   - Category: None of the four\n"
    "   - Reasoning: This refers to a software update version, not a device identifier, name, manufacturer, or model.\n"
    '3. "build 22B83":\n'
    "   - Category: None of the four\n"
    "   - Reasoning: This is a build number for a software version, not related to the device hardware information we're extracting.\n"
    "The manufacturer (Apple) is implied by the iPhone name but not explicitly stated, so we'll keep it as null.\n"
    "</extraction_process>\n"
    '{{"identifier":null,"name":"iPhone 13 Pro","manufacturer":null,"model":null}}\n'
    "</ideal_output>\n"
    "</example>\n"
    "<example>\n"
    "<input>\n"
    "How secure is my device with model Apple device with model A2483.\n"
    "</input>\n"
    "<ideal_output>\n"
    "<extraction_process>\n"
    "Potential device-related information found:\n"
    "- Apple\n"
    "- A2483\n"
    "Categorization:\n"
    '1. "Apple":\n'
    "   - Category: manufacturer\n"
    "   - Reasoning: Apple is explicitly mentioned as the device manufacturer.\n"
    ""
    '2. "A2483":\n'
    "   - Category: model\n"
    "   - Reasoning: This alphanumeric code is in the format typically used for Apple device model numbers.\n"
    ""
    "No specific device name or identifier is provided in the input.\n"
    "</extraction_process>\n"
    '{{"identifier":null,"name":null,"manufacturer":"Apple","model":"a2483"}}\n'
    "</ideal_output>\n"
    "</example>\n"
    "<example>\n"
    "<input>\n"
    "Should I buy new phone if I have iphone14,2.\n"
    "</input>\n"
    "<ideal_output>\n"
    "<extraction_process>\n"
    "Potential device-related information found:\n"
    "- iphone14,2\n"
    "Categorization:\n"
    '1. "iphone14,2":\n'
    "   - Category: identifier\n"
    '   - Reasoning: This format (lowercase "iphone" followed by numbers and a comma) is consistent with Apple\'s internal device identifiers.\n'
    ""
    'No specific device name, manufacturer, or model number is provided in the input. While "iPhone" is implied by the identifier, we don\'t have enough information to determine the specific name of the device.\n'
    "</extraction_process>\n"
    '{{"identifier":"iphone14,2","name":null,"manufacturer":null,"model":null}}\n'
    "</ideal_output>\n"
    "</example>\n"
    "<example>\n"
    "<input>\n"
    "Is iPhone 6 and iphone7,2 the same device?\n"
    "</input>\n"
    "<ideal_output>\n"
    "<extraction_process>\n"
    "Potential device-related information found:\n"
    "- iPhone 6\n"
    "- iphone7,2\n"
    "Categorization:\n"
    '1. "iPhone 6":\n'
    "   - Category: name\n"
    "   - Reasoning: This is the marketing name for a specific iPhone model.\n"
    '2. "iphone7,2":\n'
    "   - Category: identifier\n"
    '   - Reasoning: This format (lowercase "iphone" followed by numbers and a comma) is consistent with Apple\'s internal device identifiers.\n'
    "The manufacturer (Apple) is implied by the iPhone name but not explicitly stated, so we'll keep it as null. No specific model number is provided.\n"
    'Interestingly, "iPhone 6" and "iphone7,2" actually refer to the same device. The "iphone7,2" is the internal identifier for the iPhone 6. However, we\'ll list them separately as name and identifier in our output as per the instructions.\n'
    "</extraction_process>\n"
    '{{"identifier":"iphone7,2","name":"iPhone 6","manufacturer":null,"model":null}}\n'
    "</ideal_output>\n"
    "</example>\n"
    "<example>\n"
    "<input>\n"
    "How secure is an iPhone XS running iOS 17.7.2? Are there any known vulnerabilities or security concerns with this version?\n"
    "</input>\n"
    "<ideal_output>\n"
    "<extraction_process>\n"
    "Potential device-related information found:\n"
    "- iPhone XS\n"
    "- iOS 17.7.2\n"
    "Categorization:\n"
    '1. "iPhone XS":\n'
    "   - Category: name\n"
    "   - Reasoning: This is the marketing name for a specific iPhone model.\n"
    ""
    '2. "iOS 17.7.2":\n'
    "   - Category: None of the four\n"
    "   - Reasoning: This refers to the operating system version, not a device identifier, name, manufacturer, or model.\n"
    "The manufacturer (Apple) is implied by the iPhone name but not explicitly stated, so we'll keep it as null. No specific identifier or model number is provided in the input.\n"
    "</extraction_process>\n"
    '{{"identifier":null,"name":"iPhone XS","manufacturer":null,"model":null}}\n'
    "</ideal_output>\n"
    "</example>\n"
    "<example>\n"
    "<input>\n"
    "Which version is my iPhone running if the patch is labeled with build 24D12?\n"
    "</input>\n"
    "<ideal_output>\n"
    "<extraction_process>\n"
    "Potential device-related information found:\n"
    "- iPhone\n"
    "- build 24D12\n"
    "Categorization:\n"
    '1. "iPhone":\n'
    "   - Category: None of the four\n"
    "   - Reasoning: While this indicates the device is an iPhone, it doesn't provide a specific name, identifier, or model. It's too general to be categorized.\n"
    '2. "build 24D12":\n'
    "   - Category: None of the four\n"
    "   - Reasoning: This is a build number for a software version, not related to the device hardware information we're extracting.\n"
    "No specific device name, identifier, manufacturer, or model number is provided in the input. While we know it's an iPhone, we don't have enough information to fill in any of the four required fields.\n"
    "</extraction_process>\n"
    '{{"identifier":null,"name":null,"manufacturer":null,"model":null}}\n'
    "</ideal_output>\n"
    "</example>\n"
    "<example>\n"
    "<input>\n"
    "Can you tell me the version number for the patch identified by build 23C45?\n"
    "</input>\n"
    "<ideal_output>\n"
    "<extraction_process>\n"
    "Potential device-related information found:\n"
    "- build 23C45\n"
    "Categorization:\n"
    '1. "build 23C45":\n'
    "   - Category: None of the four\n"
    "   - Reasoning: This is a build number for a software version, not related to the device hardware information we're extracting.\n"
    "No specific device name, identifier, manufacturer, or model number is provided in the input. The query is asking about a software version rather than providing any device-specific information.\n"
    "</extraction_process>\n"
    '{{"identifier":null,"name":null,"manufacturer":null,"model":null}}\n'
    "</ideal_output>\n"
    "</example>\n"
    "</examples>\n"
)
