import json
import random
from typing import List
from openai_function_call import OpenAISchema
from pydantic import Field
from typing import List
from aiconsole.aic_types import Manual, Strategy
from aiconsole.gpt.ensure_i_can_run_this_in_range import ensure_I_can_run_this_in_range
from aiconsole.gpt.get_model import get_model
from aiconsole.gpt.gpt_executor import GPTExecutor
from aiconsole.gpt.gpt_types import EnforcedFunctionCall, GPTMessage, GPTRequest

DEBUG_PROMPTS = True

class ManualsAndStrategyChooser:
    def __init__(self):
        self.picked_strategy = None
        self.relevant_manuals = []
        self.tokens_used = 0

    def execute(self,
                messages: List[GPTMessage],
                system_description: str,
                available_strategies: List[Strategy],
                available_manuals: List[Manual]):

        new_line = "\n"
        system_content = f"""
{system_description}

1. Establish the strategy to execute the command, it can be one of the following values:

{new_line.join([f"* {c.id} - {c.usage}" for c in random.sample(available_strategies, len(available_strategies))])}

2. Figure out and provide a list of ids of materials that are needed to execute the command.

You have access to the following materials:

{new_line.join([f"* {c.id} - {c.usage}" for c in random.sample(available_manuals, len(available_manuals))]) if available_manuals else ''}
        """.strip()

        # GPTMessage(role="user", content=f"Command from the user: {task_prompt}")
        prompt_with_context = [
            GPTMessage(role="system", content=system_content),
            *messages
        ]

        available_manuals_ids = [k.id for k in available_manuals]
        available_strategy_ids = [s.id for s in available_strategies]

        class OutputSchema(OpenAISchema):
            """
            Choose needed manuals and strategy for the task.
            """
            needed_manuals_ids: List[str] = Field(..., description="Choosen manuals ids needed for the task")
            
            strategy_id: str = Field(..., description="Choosen strategy id for the task",
                                  json_schema_extra={"enum": available_strategy_ids})
            
            class Config:
                schema_extra = {
                    "properties": {
                        "needed_manuals": {
                            "items": {
                                "enum": available_manuals_ids
                            }
                        }
                    }
                }

        request = GPTRequest(
            model = get_model(messages, 0, "QUALITY"),
            messages = prompt_with_context,
            max_tokens = 0,
            functions = [OutputSchema.openai_schema],
            function_call=EnforcedFunctionCall(name="OutputSchema")
        )

        min_tokens = 250
        preferred_tokens = 500; #TODO: Figure out the best value for this

        request.max_tokens = ensure_I_can_run_this_in_range(
            request,
            min_tokens = min_tokens,
            preferred_tokens = preferred_tokens,   
        )

        gpt_executor = GPTExecutor()

        yield from gpt_executor.execute(request)

        if gpt_executor.full_result.function_call == None:
            raise ValueError(f"Could not find function call in the text: {gpt_executor.full_result}")

        x = gpt_executor.full_result.function_call["arguments"]
        raw_arguments = gpt_executor.full_result.function_call["arguments"]
        arguments = json.loads(raw_arguments, strict=False)

        matching_strategies = [
            c for c in available_strategies if arguments["strategy_id"] == c.id]

        if len(matching_strategies) != 1:
            raise ValueError(f"Could not find strategy in the text: {gpt_executor.full_result}")

        picked_strategy = matching_strategies[0]

        relevant_manuals = [
            k for k in available_manuals if k.id in raw_arguments]

        self.picked_strategy = picked_strategy
        self.relevant_manuals = relevant_manuals
        self.tokens_used = gpt_executor.input_tokens + gpt_executor.output_tokens

'''
import { z } from 'zod';
import { Knowledge } from './Knowledge';
import { DEBUG_PROMPTS } from '../../oldconsole/10minions-engine/src/const';
import { getModel } from '../../gpt/getModel';
import { GPTExecuteRequestMessage, GPTMode, MODEL_DATA } from '../../gpt/types';
import { shuffleArray } from '../../utils/random/shuffleArray';
import { formatPrompt } from '../../utils/string/formatPrompt';
import { Strategy } from './Strategy';
import { TaskContext } from '../../oldconsole/10minions-engine/src/tasks/TaskContext';
import { mutateAppendSectionToLog } from '../../oldconsole/10minions-engine/src/tasks/logs/mutators/mutateAppendSectionToLog';
import { mutateAppendToLog } from '../../oldconsole/10minions-engine/src/tasks/logs/mutators/mutateAppendToLog';
import { taskGPTExecute } from '../../oldconsole/10minions-engine/src/tasks/mutators/taskGPTExecute';
import { countTokens } from '../../gpt/countTokens';
import { ensureIRunThisInRange } from '../../gpt/ensureIRunThisInRange';

export async function taskChooseKnowledgeAndStrategy<TC extends TaskContext>({
  task,
  originalCommand,
  originalResult,
  systemDescription = 'AI command center',
  availableStrategies,
  availableKnowledge,
  taskToPrompt,
}: {
  task: TC;
  originalCommand?: TC;
  originalResult?: string;
  systemDescription: string;
  availableStrategies: Strategy[];
  availableKnowledge: Knowledge[];
  taskToPrompt: (task: TC) => Promise<string>;
}) {
  const taskPrompt = await taskToPrompt(originalCommand ?? task);
  const mode = GPTMode.FAST;
  const isKnowledge = Boolean(availableKnowledge.length);

  const promptWithContext: GPTExecuteRequestMessage[] = [
    {
      role: 'system',
      content: formatPrompt(`
        ${systemDescription}

        1. Establish the strategy to execute the command, it can be one of the following values:

        ${shuffleArray(availableStrategies.map((c) => `* ${c.id} - ${c.description}`)).join('\n        ')}

        2. Figure out and provide a list of materials that are needed to execute the command, and output the sum of tokens for it.

        You may not exceed ${MODEL_DATA[getModel(mode)].maxTokens - 2000} tokens in total.

        Prioritize the most important materials first, as the latter might not fit into the context window.

        Do not add materials if they are not needed.
       
        You have access to the following materials:

        ${isKnowledge ? shuffleArray(availableKnowledge.map((c) => `* ${c.id} - ${c.description} `)).join('\n        ') : ''}

        Do not perform the actual command, revise the result or generate any code.
      `),
    },
    ...(originalCommand
      ? ([
          { role: 'user', content: `Original command:\n""" ${taskPrompt} """` },
          { role: 'user', content: `Result that will be revised:\n""" ${originalResult} """` },
          { role: 'user', content: `Request for revision: """ ${taskPrompt} """` },
        ] as GPTExecuteRequestMessage[])
      : ([{ role: 'user', content: `Command from the user: """ ${taskPrompt} """` }] as GPTExecuteRequestMessage[])),
  ];

  if (DEBUG_PROMPTS) {
    mutateAppendSectionToLog(task, task.executionStage);
    mutateAppendToLog(task, '<<<< PROMPT >>>>');
    mutateAppendToLog(task, '');
    mutateAppendToLog(task, promptWithContext.map((m) => m.content).join(','));
    mutateAppendToLog(task, '');
    mutateAppendToLog(task, '<<<< EXECUTION >>>>');
    mutateAppendToLog(task, '');
  }
  const prompt = JSON.stringify(promptWithContext);
  const minTokens = countTokens(taskPrompt, mode) + 500;
  const fullPromptTokens = countTokens(prompt, mode) + 500;

  const maxTokens = ensureIRunThisInRange({
    prompt,
    mode: mode,
    preferedTokens: fullPromptTokens,
    minTokens: minTokens,
  });

  const result = await taskGPTExecute(task, {
    fullPrompt: promptWithContext,
    mode,
    maxTokens,
    outputName: 'choose',
    outputSchema: z
      .object({
        neededKnowledge: z.array(z.enum([availableKnowledge[0].id, ...availableKnowledge.slice(1).map((s) => s.id)])),
        strategy: z.enum([availableStrategies[0].id, ...availableStrategies.slice(1).map((s) => s.id)]),
      })
      .describe('Choose needed knowledge and strategy for the task'),
  });

  mutateAppendToLog(task, '\n');

  //find classification in text
  const matchingStrategies = availableStrategies.filter((c) => result.strategy === c.id);

  if (matchingStrategies.length !== 1) {
    throw new Error(`Could not find strategy in the text: ${result}`);
  }

  const pickedStrategy = matchingStrategies[0];

  if (DEBUG_PROMPTS) {
    mutateAppendToLog(task, `Strategy: ${pickedStrategy.id}\n`);
  }

  const relevantKnowledge = (result.neededKnowledge || [])
    .map((knowledgeId) => availableKnowledge.find((k) => k.id === knowledgeId))
    .filter((k) => k !== undefined) as Knowledge[]; //TODO: Error checking

  return {
    strategy: matchingStrategies[0],
    relevantKnowledge,
  };
}











import { z } from 'zod';
import { DEBUG_PROMPTS } from '../../oldconsole/10minions-engine/src/const';
import { GPTMode, MODEL_NAMES } from '../../gpt/types';
import { TaskContext } from '../../oldconsole/10minions-engine/src/tasks/TaskContext';
import { mutateAppendSectionToLog } from '../../oldconsole/10minions-engine/src/tasks/logs/mutators/mutateAppendSectionToLog';
import { mutateAppendToLog } from '../../oldconsole/10minions-engine/src/tasks/logs/mutators/mutateAppendToLog';
import { taskGPTExecute } from '../../oldconsole/10minions-engine/src/tasks/mutators/taskGPTExecute';
import { shuffleArray } from '../../utils/random/shuffleArray';
import { Strategy } from './Strategy';
import { countTokens } from '../../gpt/countTokens';

export async function taskChooseStrategy<TC extends TaskContext>(task: TC, strategies: Strategy[], taskToPrompt: (task: TC) => Promise<string>) {
  const promptWithContext = `
${await taskToPrompt(task)}

Possible strategies:
${shuffleArray(strategies.map((c) => `* ${c.id} - ${c.description}`)).join('\n')}

Now choose strategy for the task.
`.trim();

  if (DEBUG_PROMPTS) {
    mutateAppendSectionToLog(task, task.executionStage);
    mutateAppendToLog(task, '<<<< PROMPT >>>>');
    mutateAppendToLog(task, '');
    mutateAppendToLog(task, promptWithContext);
    mutateAppendToLog(task, '');
    mutateAppendToLog(task, '<<<< EXECUTION >>>>');
    mutateAppendToLog(task, '');
  }
  const mode = GPTMode.FAST;
  const maxTokens = countTokens(promptWithContext, mode) + 100;
  const result = await taskGPTExecute(task, {
    fullPrompt: promptWithContext,
    mode,
    maxTokens,
    outputName: 'chooseStrategy',
    outputSchema: z
      .object({
        relevantKnowledge: z.array(z.string()),
        strategy: z.enum([strategies[0].id, ...strategies.slice(1).map((s) => s.id)]),
        model: z.enum([MODEL_NAMES[0], ...MODEL_NAMES.slice(1)]),
      })
      .describe('Choose appropriate strategy'),
  });

  mutateAppendToLog(task, '');
  mutateAppendToLog(task, '');

  //find classification in text
  const matchingStrategies = strategies.filter((c) => result.strategy === c.id);

  if (matchingStrategies.length !== 1) {
    throw new Error(`Could not find strategy in the text: ${result}`);
  }

  if (DEBUG_PROMPTS) {
    mutateAppendToLog(task, `Strategy: ${matchingStrategies[0].id}`);
    mutateAppendToLog(task, '');
  }

  return {
    strategy: matchingStrategies[0],
  };
}





import { z } from 'zod';
import { createFullPromptFromSections } from '../../gpt/createFullPromptFromSections';
import { GPTMode } from '../../gpt/types';
import { TaskContext } from '../../tasks/TaskContext';
import { mutateAppendSectionToLog } from '../../tasks/logs/mutators/mutateAppendSectionToLog';
import { mutateAppendToLogNoNewline } from '../../tasks/logs/mutators/mutateAppendToLogNoNewline';
import { taskGPTExecute } from '../../tasks/mutators/taskGPTExecute';
import { Knowledge } from '../Knowledge';

export async function mutateCreateSimpleAnswer<TC extends TaskContext>({
  task,
  prePrompt,
  input,
  relevantKnowledge,
}: {
  task: TC;
  prePrompt: string;
  input: string;
  relevantKnowledge: Knowledge[];
}): Promise<string> {
  //TODO: Trimming the less relevant knowledge so it still fits into the context window, even if there is too much knowledge selected.

  const fullPrompt = createFullPromptFromSections({
    intro: `${preaPrompt}: "${input}"`,
    sections: Object.fromEntries(relevantKnowledge.map((k) => [k.id, k.content])),
  });

  const answer = await taskGPTExecute(task, {
    fullPrompt: fullPrompt,
    mode: GPTMode.QUALITY,
    maxTokens: 400,
    outputSchema: z.string(),
  });

  mutateAppendSectionToLog(task, 'Answer');
  mutateAppendToLogNoNewline(task, answer);

  return answer;
}

'''