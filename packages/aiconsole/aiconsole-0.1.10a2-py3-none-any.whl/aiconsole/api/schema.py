from typing import List

from pydantic import BaseModel

from aiconsole.aic_types import StaticManual
from aiconsole.gpt.gpt_types import GPTMessage
from aiconsole.gpt.consts import GPTModeLiteral


class GptHTTPRequest(BaseModel):
    messages: List[GPTMessage]
    strategy: str
    relevant_manuals: List[StaticManual]
    mode: GPTModeLiteral


class AnalyseHTTPRequest(BaseModel):
    messages: List[GPTMessage]
    mode: GPTModeLiteral
