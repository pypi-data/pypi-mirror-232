import json
from typing import Dict, Optional

import tiktoken

from aiconsole.gpt.consts import MODEL_DATA
from aiconsole.gpt.gpt_types import GPTRequest


def count_tokens(request: GPTRequest):
    encoding = tiktoken.encoding_for_model(MODEL_DATA[request.model].encoding)

    if request.functions:
        functions_tokens = len(
            encoding.encode(",".join(json.dumps(f) for f in request.functions))
        )
    else:
        functions_tokens = 0

    messages_str = json.dumps([m.model_dump() for m in request.messages])
    messages_tokens = len(encoding.encode(messages_str))

    return messages_tokens + functions_tokens


def count_tokens_output(content: str, function_call: Optional[Dict], model: str):
    encoding = tiktoken.encoding_for_model(MODEL_DATA[model].encoding)

    return len(encoding.encode(content)) + (
        len(encoding.encode(json.dumps(function_call))) if function_call else 0
    )
