from typing import List

from aiconsole.gpt.consts import MODEL_DATA, GPTMode, GPTModel, GPTModeLiteral

from .count_tokens import count_tokens
from .gpt_types import GPTMessage, GPTRequest


def get_model(
    messages: List[GPTMessage], mode: GPTModeLiteral, max_tokens: int = 0
) -> str:
    model = GPTModel.GPT_4_0613
    if mode == GPTMode.FAST:
        model = GPTModel.GPT_35_TURBO_16k_0613
        gpt_request = GPTRequest(messages=messages, model=model, max_tokens=max_tokens)
        used_tokens = count_tokens(gpt_request) + max_tokens

        if used_tokens < MODEL_DATA[GPTModel.GPT_35_TURBO_0613].max_tokens:
            model = GPTModel.GPT_35_TURBO_0613

    return model
