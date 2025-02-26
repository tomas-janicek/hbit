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
    {
        "input": "Hello!",
        "output": f"{{{dto.QueryOutput(query='').model_dump_json()}}}",
    },
    {
        # NOTE: Anthropic model fails on message with jus white-spaces
        "input": ".",
        "output": f"{{{dto.QueryOutput(query='').model_dump_json()}}}",
    },
    {
        "input": "version",
        "output": f"{{{dto.QueryOutput(query='').model_dump_json()}}}",
    },
    {
        "input": "device",
        "output": f"{{{dto.QueryOutput(query='').model_dump_json()}}}",
    },
    {
        "input": "iphone 13 pro",
        "output": f"{{{dto.QueryOutput(query="SELECT identifier FROM devices WHERE name LIKE 'iphone 13 pro'").model_dump_json()}}}",
    },
    {
        "input": "iphone XR",
        "output": f"{{{dto.QueryOutput(query="SELECT identifier FROM devices WHERE name LIKE 'iphone XR'").model_dump_json()}}}",
    },
    {
        "input": "What is the most recent iOS update for the iPhone 14, and does it fix any critical security vulnerabilities?",
        "output": f"{{{dto.QueryOutput(query="SELECT identifier FROM devices WHERE name LIKE 'iPhone 14'").model_dump_json()}}}",
    },
    {
        "input": "How secure is my iPhone 13 Pro with patch 18.1.0 (build 22B83) installed?",
        "output": f"{{{dto.QueryOutput(query="SELECT identifier FROM devices WHERE name LIKE 'iPhone 13 Pro'").model_dump_json()}}}",
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
    {
        "input": "Hello!",
        "output": f"{{{dto.Device(identifier=None, name=None, manufacturer=None, model=None).model_dump_json()}}}",
    },
    {
        # NOTE: Anthropic model fails on message with jus white-spaces
        "input": ".",
        "output": f"{{{dto.Device(identifier=None, name=None, manufacturer=None, model=None).model_dump_json()}}}",
    },
    {
        "input": "version",
        "output": f"{{{dto.Device(identifier=None, name=None, manufacturer=None, model=None).model_dump_json()}}}",
    },
    {
        "input": "device",
        "output": f"{{{dto.Device(identifier=None, name=None, manufacturer=None, model=None).model_dump_json()}}}",
    },
    {
        "input": "iphone 13 pro",
        "output": f"{{{dto.Device(identifier=None, name='iphone 13 pro', manufacturer=None, model=None).model_dump_json()}}}",
    },
    {
        "input": "iphone XR",
        "output": f"{{{dto.Device(identifier=None, name='iphone XR', manufacturer=None, model=None).model_dump_json()}}}",
    },
    {
        "input": "What is the most recent iOS update for the iPhone 14, and does it fix any critical security vulnerabilities?",
        "output": f"{{{dto.Device(identifier=None, name='iPhone 14', manufacturer=None, model=None).model_dump_json()}}}",
    },
    {
        "input": "How secure is my iPhone 13 Pro with patch 18.1.0 (build 22B83) installed?",
        "output": f"{{{dto.Device(identifier=None, name='iPhone 13 Pro', manufacturer=None, model=None).model_dump_json()}}}",
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
    {
        "input": "Hello!",
        "output": f"{{{dto.QueryOutput(query='').model_dump_json()}}}",
    },
    {
        "input": "device",
        "output": f"{{{dto.QueryOutput(query='').model_dump_json()}}}",
    },
    {
        "input": "iPhone",
        "output": f"{{{dto.QueryOutput(query='').model_dump_json()}}}",
    },
    {
        # NOTE: Anthropic model fails on message with jus white-spaces
        "input": ".",
        "output": f"{{{dto.QueryOutput(query='').model_dump_json()}}}",
    },
    {
        "input": "18",
        "output": f"{{{dto.QueryOutput(query="SELECT build FROM patches WHERE version LIKE '%18%'").model_dump_json()}}}",
    },
    {
        "input": "22B83",
        "output": f"{{{dto.QueryOutput(query="SELECT build FROM patches WHERE build LIKE '22B83'").model_dump_json()}}}",
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
    {
        "input": "Hello!",
        "output": f"{{{dto.Patch(build=None, version=None).model_dump_json()}}}",
    },
    {
        "input": "device",
        "output": f"{{{dto.Patch(build=None, version=None).model_dump_json()}}}",
    },
    {
        "input": "iPhone",
        "output": f"{{{dto.Patch(build=None, version=None).model_dump_json()}}}",
    },
    {
        # NOTE: Anthropic model fails on message with jus white-spaces
        "input": ".",
        "output": f"{{{dto.Patch(build=None, version=None).model_dump_json()}}}",
    },
    {
        "input": "18",
        "output": f"{{{dto.Patch(build=None, version='18').model_dump_json()}}}",
    },
    {
        "input": "22B83",
        "output": f"{{{dto.Patch(build='22B83', version=None).model_dump_json()}}}",
    },
]
