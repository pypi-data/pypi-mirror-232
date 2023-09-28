import json
from typing import List
from aiconsole.gpt.gpt_types import GPTMessage

def messages_to_string(messages: List[GPTMessage]):
    return json.dumps([{"role": m.role, "content": m.content} for m in messages])