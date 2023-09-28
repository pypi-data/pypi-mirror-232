from aiconsole.aic_types import TaskContext
from aiconsole.gpt.get_model import get_model
from aiconsole.gpt.gpt_types import MODEL_DATA, GPTMessage
from aiconsole.interpreter import base_system_message, manuals
from aiconsole.strategy_and_manuals.manuals_and_strategy_chooser import ManualsAndStrategyChooser, Strategy

import asyncio
from typing import List

async def analyse(messages: List[GPTMessage], mode: str):
    chooser = ManualsAndStrategyChooser()

    available_strategies=[Strategy(id = "Strat1", usage = "Use it for easy tasks"), Strategy(id = "Strat2", usage = "Use it for hard tasks")]
    available_manuals=manuals.all_manuals()

    for chunk in chooser.execute(messages, system_description = base_system_message, available_strategies=available_strategies, available_manuals=available_manuals):
        text_chunk = chunk["choices"][0]["delta"].get("content",'') or chunk["choices"][0]["delta"].get("function_call", {"arguments": ""})["arguments"] or ''
        print(text_chunk)
        await asyncio.sleep(0)

    if chooser.picked_strategy is None:
        raise Exception("No strategy picked")

    task_context = TaskContext(messages=messages, strategy=chooser.picked_strategy, relevant_manuals=chooser.relevant_manuals, mode=mode)

    return {
        "strategy": chooser.picked_strategy.model_dump() if chooser.picked_strategy else None,
        "manuals": [{
            "id": manual.id,
            "usage": manual.usage,
            "content": manual.content(task_context),
        } for manual in chooser.relevant_manuals],
        "usedTokens": chooser.tokens_used,
        "availableTokens": MODEL_DATA[get_model(messages, 0, 'QUALITY' if mode == 'QUALITY' else 'FAST')].max_tokens,
    }