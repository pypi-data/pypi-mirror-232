import asyncio
import json
from typing import List

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from openai_function_call import OpenAISchema
from pydantic import Field

from aiconsole.aic_types import SYSTEM_IDENTITY, ContentTaskContext
from aiconsole.api.schema import AnalyseHTTPRequest
from aiconsole.gpt.get_max_token import get_max_token
from aiconsole.gpt.get_model import get_model
from aiconsole.gpt.gpt_executor import GPTExecutor
from aiconsole.gpt.gpt_types import EnforcedFunctionCall, GPTMessage, GPTRequest
from aiconsole.gpt.consts import MODEL_DATA
from aiconsole.manuals import manuals
from aiconsole.strategies import strategies
from aiconsole.gpt.get_system_content import get_system_content

MIN_TOKENS = 250
PREFERRED_TOKENS = 500

router = APIRouter()

@router.post("/analyse")
async def analyse(request: AnalyseHTTPRequest):
    messages = request.messages
    mode = request.mode

    available_strategies = strategies.all_strategies()
    available_manuals = manuals.all_manuals()

    system_content = get_system_content(
        system_description=SYSTEM_IDENTITY,
        available_strategies=available_strategies,
        available_manuals=available_manuals,
    )

    # GPTMessage(role="user", content=f"Command from the user: {task_prompt}")
    prompt_with_context = [
        GPTMessage(role="system", content=system_content),
        *messages,
    ]

    class OutputSchema(OpenAISchema):
        """
        Choose needed manuals and strategy for the task.
        """

        needed_manuals_ids: List[str] = Field(
            ..., description="Chosen manuals ids needed for the task",
            json_schema_extra={"items": {"enum": [k.id for k in available_manuals], "type": "string"}},
        )

        strategy_id: str = Field(
            ...,
            description="Chosen strategy id for the task",
            json_schema_extra={"enum": [s.id for s in available_strategies]},
        )

    gpt_request = GPTRequest(
        model=get_model(messages, mode),
        messages=prompt_with_context,
        functions=[OutputSchema.openai_schema],
        function_call=EnforcedFunctionCall(name="OutputSchema"),
    )

    gpt_request.max_tokens = get_max_token(
        request=gpt_request,
        min_tokens=MIN_TOKENS,
        preferred_tokens=PREFERRED_TOKENS,
    )

    gpt_executor = GPTExecutor()

    for chunk in gpt_executor.execute(gpt_request):
        text_chunk = (
            chunk["choices"][0]["delta"].get("content", "")
            or chunk["choices"][0]["delta"]
            .get("function_call", {"arguments": ""})
            .get("arguments", "")
            or ""
        )
        print(text_chunk)
        await asyncio.sleep(0)

    if gpt_executor.full_result.function_call is None:
        raise ValueError(
            f"Could not find function call in the text: {gpt_executor.full_result}"
        )

    raw_arguments = gpt_executor.full_result.function_call["arguments"]
    arguments = json.loads(raw_arguments, strict=False)

    matching_strategies = [
        c for c in available_strategies if arguments["strategy_id"] == c.id
    ]

    try:
        picked_strategy = matching_strategies[0]
    except IndexError:
        raise ValueError(
            f"Could not find strategy in the text: {gpt_executor.full_result}"
        )
    if picked_strategy is None:
        raise Exception("No strategy picked")

    relevant_manuals = [k for k in available_manuals if k.id in raw_arguments]
    tokens_used = gpt_executor.input_tokens + gpt_executor.output_tokens


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
        "usedTokens": tokens_used,
        "availableTokens": MODEL_DATA[
            get_model(request.messages, request.mode)
        ].max_tokens,
    }

    print(analysis)

    return JSONResponse(content=analysis)
