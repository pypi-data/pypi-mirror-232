import decimal
from typing import Dict, Optional

from aiconsole.gpt.gpt_types import GPTRequest
from aiconsole.gpt.count_tokens import count_tokens, count_tokens_output
from aiconsole.gpt.consts import MODEL_DATA


def calculate_costs(
    request: GPTRequest, content: str, function_call: Optional[Dict]
) -> tuple[decimal.Decimal, int, int]:

    input_tokens = count_tokens(request)
    output_tokens = count_tokens_output(
        content=content, function_call=function_call, model=request.model
    )

    request_model = MODEL_DATA[request.model]
    input_cost = (input_tokens * decimal.Decimal(0.001)) * request_model.input_cost_per_1K
    output_cost = (output_tokens * decimal.Decimal(0.001)) * request_model.output_cost_per_1K

    total_cost = input_cost + output_cost

    return total_cost, input_tokens, output_tokens
