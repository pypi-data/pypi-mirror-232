import asyncio
from typing import AsyncGenerator
from aiconsole.aic_types import ExecutionTaskContext
from aiconsole.gpt.create_full_prompt_from_sections import create_full_prompt_from_sections
from aiconsole.gpt.get_max_token import get_max_token
from aiconsole.gpt.get_model import get_model
from aiconsole.gpt.gpt_executor import GPTExecutor
from aiconsole.gpt.gpt_types import GPTMessage, GPTRequest
from aiconsole.gpt.consts import GPTMode

MIN_TOKENS = 250
PREFERRED_TOKENS = 2000


async def execution_mode_normal(context: ExecutionTaskContext) -> AsyncGenerator[str, None]:
    global interpreter

    print("execution_mode_normal")

    system_content = create_full_prompt_from_sections(
        intro=context.strategy.system,
        sections=context.relevant_manuals,
        outro="\n\n---\n\n"
    )

    prompt_with_context = [
        GPTMessage(role="system", content=system_content),
        *context.messages,
    ]

    request = GPTRequest(
        model=get_model(context.messages, GPTMode.QUALITY),
        messages=prompt_with_context,
    )

    request.max_tokens = get_max_token(
        request,
        min_tokens=MIN_TOKENS,
        preferred_tokens=PREFERRED_TOKENS,
    )

    gpt_executor = GPTExecutor()

    for chunk in gpt_executor.execute(request):
        try:
            yield chunk["choices"][0]["delta"].get("content", "")
            await asyncio.sleep(0)
        except asyncio.CancelledError:
            print("Cancelled")

    tokens_used = gpt_executor.input_tokens + gpt_executor.output_tokens
