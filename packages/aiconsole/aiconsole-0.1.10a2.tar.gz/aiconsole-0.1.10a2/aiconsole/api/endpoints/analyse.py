import asyncio
import json
from typing import List

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from openai_function_call import OpenAISchema
from pydantic import Field

from aiconsole.aic_types import SYSTEM_IDENTITY, ContentTaskContext
from aiconsole.api.schema import AnalyseHTTPRequest
from aiconsole.gpt.gpt_executor import GPTExecutor
from aiconsole.gpt.gpt_types import EnforcedFunctionCall
from aiconsole.gpt.request import GPTRequest
from aiconsole.manuals import manuals
from aiconsole.strategies import strategies
from aiconsole.utils.get_system_content import get_system_content

MIN_TOKENS = 250
PREFERRED_TOKENS = 500

router = APIRouter()

@router.post("/analyse")
async def analyse(request: AnalyseHTTPRequest) -> JSONResponse:
    messages = request.messages
    mode = request.mode

    available_strategies = strategies.all_strategies()
    available_manuals = manuals.all_manuals()

    system_content = get_system_content(
        system_description=SYSTEM_IDENTITY,
        available_strategies=available_strategies,
        available_manuals=available_manuals,
    )

    class OutputSchema(OpenAISchema):
        """
        Choose needed manuals and strategy for the task.
        """

        needed_manuals_ids: List[str] = Field(
            ...,
            description="Chosen manuals ids needed for the task",
            json_schema_extra={
                "items": {"enum": [k.id for k in available_manuals], "type": "string"}
            },
        )

        strategy_id: str = Field(
            ...,
            description="Chosen strategy id for the task",
            json_schema_extra={"enum": [s.id for s in available_strategies]},
        )

    gpt_request = GPTRequest(
        mode=mode,
        messages=messages,
        functions=[OutputSchema.openai_schema],
        function_call=EnforcedFunctionCall(name="OutputSchema"),
    )
    gpt_request.add_prompt_context(system_content)
    gpt_request.update_max_token(MIN_TOKENS, PREFERRED_TOKENS)

    gpt_executor = GPTExecutor()

    for chunk in gpt_executor.execute(gpt_request):
        if (chunk.get("error", "")):
            raise ValueError(f"Error in GPT: {chunk.get('error', '')}")

        delta = chunk["choices"][0]["delta"]

        if isinstance(delta, str):
            text_chunk = delta
        elif isinstance(delta, dict):
            text_chunk = delta.get("content", "") or delta.get("function_call", {"arguments": ""}).get("arguments", "") or ""
        else:
            raise ValueError(f"Unexpected delta type: {type(delta)}")

        print(text_chunk)
        await asyncio.sleep(0)

    full_result = gpt_executor.full_result
    tokens_used = gpt_executor.tokens_used

    if full_result.function_call is None:
        raise ValueError(f"Could not find function call in the text: {full_result}")

    raw_arguments = full_result.function_call["arguments"]
    arguments = json.loads(raw_arguments, strict=False)

    matching_strategies = [
        c for c in available_strategies if arguments["strategy_id"] == c.id
    ]

    try:
        picked_strategy = matching_strategies[0]
    except IndexError:
        raise ValueError(f"Could not find strategy in the text: {full_result}")
    if picked_strategy is None:
        raise Exception("No strategy picked")

    relevant_manuals = [k for k in available_manuals if k.id in raw_arguments]

    task_context = ContentTaskContext(
        messages=request.messages,
        strategy=picked_strategy,
        relevant_manuals=relevant_manuals,
        mode=request.mode,
    )

    analysis = {
        "strategy": {
            "id": picked_strategy.id,
            "usage": picked_strategy.usage,
            "content": picked_strategy.system,
            "execution_mode": picked_strategy.execution_mode.__name__,  # TODO: Probably we should keep to the original name
        }
        if picked_strategy
        else None,
        "manuals": [
            {
                "id": manual.id,
                "usage": manual.usage,
                "content": manual.content(task_context),
            }
            for manual in relevant_manuals
        ],
        "used_tokens": tokens_used,
        "available_tokens": gpt_request.model,
    }

    print(analysis)

    return JSONResponse(content=analysis)
