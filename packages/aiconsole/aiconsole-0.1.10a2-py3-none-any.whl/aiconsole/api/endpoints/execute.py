from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from aiconsole.aic_types import ExecutionTaskContext
from aiconsole.api.schema import GptHTTPRequest
from aiconsole.strategies import strategies

router = APIRouter()


@router.post("/execute")
async def execute(request: GptHTTPRequest) -> StreamingResponse:
    strategy = strategies.strategies[request.strategy]

    context = ExecutionTaskContext(
        messages=request.messages,
        strategy=strategy,
        relevant_manuals=request.relevant_manuals,
        mode=request.mode,
    )

    return StreamingResponse(
        strategy.execution_mode(context), media_type="text/event-stream"
    )
