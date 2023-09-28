import json
from typing import Dict, Optional

import tiktoken

from aiconsole.gpt.gpt_types import MODEL_DATA, GPTModel, GPTRequest
from .messages_to_string import messages_to_string

def count_tokens(request: GPTRequest):
    encoding = tiktoken.encoding_for_model(MODEL_DATA[request.model].encoding)

    if request.functions:
        functions_tokens = len(encoding.encode(",".join(json.dumps(f) for f in request.functions)))
    else:
        functions_tokens = 0

    return len(encoding.encode(messages_to_string(request.messages))) + functions_tokens

def count_tokens_output(content: str, function_call: Optional[Dict], model: GPTModel):
    encoding = tiktoken.encoding_for_model(MODEL_DATA[model].encoding)

    return len(encoding.encode(content)) + (len(encoding.encode(json.dumps(function_call))) if function_call else 0)