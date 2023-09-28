from typing import List
from .count_tokens import count_tokens
from .gpt_types import MODEL_DATA, GPTMessage, GPTMode, GPTModel, GPTRequest

def get_model(messages: List[GPTMessage], max_tokens: int, mode: GPTMode) -> GPTModel:
    model = 'gpt-4-0613'
    if mode == 'FAST':
        model = 'gpt-3.5-turbo-16k-0613'
        used_tokens = count_tokens(GPTRequest(messages = messages, model = model, max_tokens = max_tokens)) + max_tokens

        if used_tokens < MODEL_DATA["gpt-3.5-turbo-0613"].max_tokens:
            model = 'gpt-3.5-turbo-0613'
    
    return model
