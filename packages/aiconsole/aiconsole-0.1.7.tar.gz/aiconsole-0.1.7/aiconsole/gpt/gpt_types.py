import decimal
from typing import Dict, List, Literal, Optional, Union
from typing_extensions import TypedDict
from pydantic import BaseModel

GPTMode = Literal['FAST', 'QUALITY']
GPTModel = Literal['gpt-4-0613', 'gpt-3.5-turbo-0613', 'gpt-3.5-turbo-16k-0613']

class GPTMessage(BaseModel):
    role: Literal['user', 'assistant', 'system']
    content: str

class EnforcedFunctionCall(TypedDict):
    name: str

class GPTRequest(BaseModel):
    messages: List[GPTMessage]
    model: GPTModel
    temperature: float = 1
    max_tokens: int = 2000
    stream: bool = True
    functions: List[Dict] = []
    function_call: Union[Literal["none"], Literal["auto"], EnforcedFunctionCall] = "auto"

class GPTFunctionCallInvocation(TypedDict):
    name: str
    arguments: str

class GPTResult(BaseModel):
    content: str
    function_call: Optional[GPTFunctionCallInvocation]
    cost: decimal.Decimal
    
class GPTModelData(BaseModel):
    encoding: str
    max_tokens: int
    input_cost_per_1K: decimal.Decimal
    output_cost_per_1K: decimal.Decimal

MODEL_DATA: Dict[GPTModel, GPTModelData] = {
    'gpt-4-0613': GPTModelData(max_tokens = 8192, encoding = "gpt-4", input_cost_per_1K = decimal.Decimal(0.03), output_cost_per_1K = decimal.Decimal(0.06)),
    'gpt-3.5-turbo-0613': GPTModelData(max_tokens = 4096, encoding = "gpt-3.5-turbo", input_cost_per_1K = decimal.Decimal(0.0015), output_cost_per_1K = decimal.Decimal(0.002)),
    'gpt-3.5-turbo-16k-0613': GPTModelData(max_tokens = 16384, encoding = "gpt-3.5-turbo", input_cost_per_1K = decimal.Decimal(0.003), output_cost_per_1K = decimal.Decimal(0.004))
}