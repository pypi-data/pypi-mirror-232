from typing import Callable, List
from pydantic import BaseModel
from pydantic import BaseModel
from typing import List
from aiconsole.gpt.gpt_types import GPTMessage, GPTMode

class TaskContext(BaseModel):
    messages: List[GPTMessage]
    strategy: 'Strategy'
    relevant_manuals: List['Manual']
    mode: GPTMode

class Manual(BaseModel):
    id: str
    usage: str
    content: Callable[[TaskContext], str]

class StaticManual(BaseModel):
    id: str
    usage: str
    content: str

class Strategy(BaseModel):
    id: str
    usage: str