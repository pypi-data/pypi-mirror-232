from aiconsole.gpt.consts import MODEL_DATA
from aiconsole.gpt.count_tokens import count_tokens
from aiconsole.gpt.gpt_types import GPTRequest
from aiconsole.gpt.token_error import TokenError

EXTRA_BUFFER_FOR_ENCODING_OVERHEAD = 50


def get_max_token(
    request: GPTRequest,
    min_tokens: int,
    preferred_tokens: int,
) -> int:
    """
    Checks if the given prompt can fit within a specified range of token lengths for the specified AI model.
    Returns the number of tokens that can be used.
    """
    used_tokens = count_tokens(request) + EXTRA_BUFFER_FOR_ENCODING_OVERHEAD
    available_tokens = MODEL_DATA[request.model].max_tokens - used_tokens

    if available_tokens < min_tokens:
        print(
            "Not enough tokens to perform the modification. Used tokens: ",
            used_tokens,
            "  available tokens: ",
            available_tokens,
            "requested tokens: ",
            request.max_tokens,
        )
        raise TokenError(
            "Combination of file size, selection, and your command is too big for us to handle."
        )

    return min(available_tokens, preferred_tokens)
