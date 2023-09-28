from typing import List
from .token_error import TokenError
from .count_tokens import count_tokens
from .get_model import get_model
from .gpt_types import MODEL_DATA, GPTRequest

def ensure_i_can_run_this(request: GPTRequest):
    """
    Checks if the prompt can be handled by the model
    """
    
    used_tokens = count_tokens(request)
    model_max_tokens = MODEL_DATA[request.model].max_tokens
    
    if used_tokens - model_max_tokens >= request.max_tokens:    
        print("Not enough tokens to perform the modification. Used tokens: ", used_tokens, "  available tokens: ", model_max_tokens, "requested tokens: ", request.max_tokens)
        raise TokenError("Combination of file size, selection, and your command is too big for us to handle.")
