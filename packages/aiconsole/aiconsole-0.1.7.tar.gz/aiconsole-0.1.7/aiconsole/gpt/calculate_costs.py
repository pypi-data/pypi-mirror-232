import decimal
from typing import Dict, Optional

from pydantic import BaseModel

from aiconsole.gpt.gpt_types import MODEL_DATA, GPTRequest
from aiconsole.gpt.count_tokens import count_tokens, count_tokens_output

class CalculateCostsResult(BaseModel):
  input_tokens: int
  output_tokens: int
  cost: decimal.Decimal
  
def calculate_costs(request: GPTRequest, content: str, function_call: Optional[Dict]) -> CalculateCostsResult:
  input_tokens = count_tokens(request)

  output_tokens = count_tokens_output(content = content, function_call = function_call, model = request.model)

  input_cost = (input_tokens * decimal.Decimal(0.001)) * MODEL_DATA[request.model].input_cost_per_1K
  output_cost = (output_tokens * decimal.Decimal(0.001)) * MODEL_DATA[request.model].output_cost_per_1K

  total_cost = input_cost + output_cost

  return CalculateCostsResult(
    input_tokens = input_tokens,
    output_tokens = output_tokens,
    cost = total_cost
  )