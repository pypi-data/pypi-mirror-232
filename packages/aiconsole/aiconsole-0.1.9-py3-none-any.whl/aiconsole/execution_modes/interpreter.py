import asyncio
from typing import AsyncGenerator
from aiconsole.aic_types import ExecutionTaskContext
from aiconsole.gpt.create_full_prompt_from_sections import (
    create_full_prompt_from_sections,
)
from aiconsole.code_interpreter.core.core import Interpreter
from aiconsole.code_interpreter.llm.setup_llm import setup_llm

interpreter = Interpreter()
interpreter.debug_mode = False
interpreter.model = "gpt-4"


async def execution_mode_interpreter(
    context: ExecutionTaskContext,
) -> AsyncGenerator[str, None]:

    # Setup the LLM
    if not interpreter._llm:
        interpreter._llm = setup_llm(interpreter)

    in_block = ""

    interpreter.system_message = create_full_prompt_from_sections(
        intro=context.strategy.system,
        sections=context.relevant_manuals,
        outro="\n\n---\n\n",
    )

    interpreter.messages = [
        {"role": message.role, "message": message.content}
        for message in context.messages
    ]

    for chunk in interpreter._respond():
        print(chunk)

        try:
            if chunk.get("language", ""):
                if in_block != "code":
                    if in_block != "":
                        yield "\n```\n"
                    yield "\n```" + str(chunk.get("language", "")) + "\n"
                in_block = "code"

            if chunk.get("message", ""):
                if in_block != "":
                    yield "\n```\n"
                in_block = ""
                yield str(chunk.get("message", ""))

            if chunk.get("code", ""):
                if in_block != "code":
                    if in_block != "":
                        yield "\n```txt\n"
                    yield "\n```\n"
                in_block = "code"
                yield str(chunk.get("code", ""))

            if chunk.get("output", ""):
                if in_block != "output":
                    if in_block != "":
                        yield "\n```\n"
                    yield "\n```\n"
                in_block = "output"
                yield str(chunk.get("output", ""))

            await asyncio.sleep(0)
        except asyncio.CancelledError:
            print("Cancelled")
            break
