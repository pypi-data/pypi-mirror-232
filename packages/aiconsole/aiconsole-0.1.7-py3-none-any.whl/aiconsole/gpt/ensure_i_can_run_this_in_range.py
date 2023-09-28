import math


from aiconsole.gpt.token_error import TokenError
from aiconsole.gpt.count_tokens import count_tokens
from aiconsole.gpt.gpt_types import  MODEL_DATA, GPTRequest

def ensure_I_can_run_this_in_range(request: GPTRequest, min_tokens: int, preferred_tokens: int) -> int:
    """
    Checks if the given prompt can fit within a specified range of token lengths for the specified AI model. Returns the number of tokens that can be used.
    """
    EXTRA_BUFFER_FOR_ENCODING_OVERHEAD = 50

    min_tokens = math.ceil(min_tokens)
    preferred_tokens = math.ceil(preferred_tokens)

    used_tokens = count_tokens(request) + EXTRA_BUFFER_FOR_ENCODING_OVERHEAD
    available_tokens = MODEL_DATA[request.model].max_tokens - used_tokens

    if available_tokens < min_tokens:
        print("Not enough tokens to perform the modification. Used tokens: ", used_tokens, "  available tokens: ", available_tokens, "requested tokens: ", request.max_tokens)
        raise TokenError(
            "Combination of file size, selection, and your command is too big for us to handle.")

    return min(available_tokens, preferred_tokens)

