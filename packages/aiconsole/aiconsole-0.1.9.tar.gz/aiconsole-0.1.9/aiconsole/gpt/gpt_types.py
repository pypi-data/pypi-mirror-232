import decimal
from typing import Dict, List, Literal, Optional, Union

from pydantic import BaseModel
from typing_extensions import TypedDict

from aiconsole.gpt.consts import GPTModelLiteral

Role = Literal["user", "assistant", "system"]


class GPTMessage(BaseModel):
    role: Role
    content: str


class EnforcedFunctionCall(TypedDict):
    name: str


class GPTRequest(BaseModel):
    messages: List[GPTMessage]
    model: GPTModelLiteral
    temperature: float = 1
    max_tokens: int = 0
    stream: bool = True
    functions: List[Dict] = []
    function_call: Union[
        Literal["none"], Literal["auto"], EnforcedFunctionCall, None
    ] = None


class GPTFunctionCallInvocation(TypedDict):
    name: str
    arguments: str


class GPTResult(BaseModel):
    content: str
    function_call: Optional[GPTFunctionCallInvocation]
    cost: decimal.Decimal
