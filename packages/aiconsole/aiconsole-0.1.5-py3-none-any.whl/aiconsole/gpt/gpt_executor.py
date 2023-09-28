import decimal
import os
import pprint
import litellm
from typing import Any, Dict

from aiconsole.gpt.count_tokens import count_tokens

from .calculate_costs import calculate_costs
from .ensure_i_can_run_this import ensure_i_can_run_this
from .gpt_cache import get_cached_result, report_gpt_call
from .gpt_types import GPTRequest, GPTResult


def convert_str_to_result(result: Dict) -> GPTResult:
    '''convert_result accepts a result str and returns appropriate parsing.'''

    return GPTResult(content=result["content"] or '', function_call=result["arguments"], cost=decimal.Decimal(0))


class GPTExecutor:
    def __init__(self):
        self.result = GPTResult(
            content="", function_call=None, cost=decimal.Decimal(0))
        self.input_tokens = 0
        self.output_tokens = 0
        self.total_cost = decimal.Decimal(0)

    def execute(self, request: GPTRequest):
        full_result = ""

        ensure_i_can_run_this(request)

        openai_api_key = os.environ.get('OPENAI_API_KEY')

        if not openai_api_key:
            raise Exception('OpenAI API key not found. Please set it in the settings.')

        cached_result = get_cached_result(request)

        if cached_result and isinstance(cached_result, str):
            yield cached_result
            self.full_result = convert_str_to_result(cached_result)

        raw_request = request.model_dump()

        print("GPT REQUEST:")
        pprint.pprint(raw_request)
        print()

        for attempt in range(3):
            try:
                response = litellm.completion(**raw_request)

                chunks = []

                for chunk in response:
                    chunks.append(chunk)

                    # Send a "."
                    yield {
                        "choices": [
                          {
                              "delta": {
                                  "role": "assistant",
                                  "content": ".",
                              },
                          }
                        ]
                    }

                rebuilt_response = litellm.stream_chunk_builder(chunks)
                message = rebuilt_response["choices"][0]["message"]

                calculate_cost_result = calculate_costs(
                    request, message["content"] or '', message["function_call"])
                self.full_result = GPTResult(
                    content=message["content"] or '',
                    function_call=message["function_call"],
                    cost=calculate_cost_result.cost
                )

                print("GPT RESPONSE:")
                pprint.pprint(self.full_result.model_dump())
                print()

                report_gpt_call(request, self.full_result)

                self.input_tokens = calculate_cost_result.input_tokens
                self.output_tokens = calculate_cost_result.output_tokens
                self.total_cost += self.full_result.cost
                return
            except Exception as error:
                print(f"Error on attempt {attempt}: {error}")
                report_gpt_call(request, {"error": str(error)})
                if attempt == 3:
                    raise error

        raise Exception("Unable to complete GPT request.")


'''import fetch from 'node-fetch';
import { z } from 'zod';
import zodToJsonSchema from 'zod-to-json-schema';
import { DEBUG_RESPONSES } from '../const';
import { getAnalyticsManager } from '../managers/AnalyticsManager';
import { getOpenAICacheManager } from '../managers/OpenAICacheManager';
import { isZodString } from '../utils/isZodString';
import { calculateCosts } from './calculateCosts';
import { ensureICanRunThis } from './ensureIcanRunThis';
import { processOpenAIResponseStream } from './processOpenAIResponseStream';
import { FAST_MODE_TOKENS, GPTExecuteRequestData, GPTExecuteRequestMessage, GPTExecuteRequestPrompt, GPTMode, GPTModel, MODEL_DATA } from './types';
import { countTokens } from './countTokens';

let openAIApiKey: string | undefined;

export function setOpenAIApiKey(apiKey: string) {
  openAIApiKey = apiKey;
}

export async function gptExecute<OutputTypeSchema extends z.ZodType>({
  fullPrompt,
  onChunk = async () => {},
  isCancelled = () => false,
  maxTokens = 2000,
  mode,
  temperature = 1,
  controller = new AbortController(),
  outputSchema,
  outputName = 'output',
}: {
  fullPrompt: GPTExecuteRequestPrompt;
  onChunk?: (chunk: string) => Promise<void>;
  isCancelled?: () => boolean;
  maxTokens?: number;
  mode: GPTMode;
  temperature?: number;
  controller?: AbortController;
  outputSchema: OutputTypeSchema;
  outputName?: string;
}): Promise<{
  result: z.infer<OutputTypeSchema>;
  cost: number;
}> {
  let model: GPTModel = 'gpt-4-0613';

  const messages: GPTExecuteRequestMessage[] = Array.isArray(fullPrompt) ? fullPrompt : [{ role: 'user', content: fullPrompt }];
  const messagesAsString = JSON.stringify(messages);

  if (mode === GPTMode.FAST) {
    model = 'gpt-3.5-turbo-16k-0613';

    const usedTokens = countTokens(messagesAsString, mode) + maxTokens;

    if (usedTokens < FAST_MODE_TOKENS) {
      model = 'gpt-3.5-turbo-0613';
    }
  }

  ensureICanRunThis({ prompt: fullPrompt, mode, maxTokens });

  const signal = controller.signal;

  if (!openAIApiKey) {
    throw new Error('OpenAI API key not found. Please set it in the settings.');
  }

  const requestData: GPTExecuteRequestData = {
    model,
    messages,
    max_tokens: maxTokens,
    temperature,
    stream: true,
    ...(isZodString(outputSchema)
      ? {}
      : {
          function_call: { name: outputName },
          functions: [
            {
              name: outputName,
              description: outputSchema.description || 'Output',
              parameters: zodToJsonSchema(outputSchema, 'parameters').definitions?.parameters,
            },
          ],
        }),
  };

  if (DEBUG_RESPONSES) {
    // console.log('REQUEST DATA:', requestData);
  }
  const cachedResult = await getOpenAICacheManager().getCachedResult(requestData);

  function convertResult(result: string): z.infer<OutputTypeSchema> {
    if (isZodString(outputSchema)) {
      return result as z.infer<OutputTypeSchema>;
    } else {
      const parseResult = outputSchema.safeParse(JSON.parse(result));
      if (parseResult.success) {
        return parseResult.data;
      } else {
        throw new Error(`Could not parse result: ${result}`);
      }
    }
  }

  if (cachedResult && typeof cachedResult === 'string') {
    await onChunk(cachedResult);
    return {
      result: convertResult(cachedResult),
      cost: 0,
    };
  }

  for (let attempt = 1; attempt <= 3; attempt++) {
    try {
      const response = await fetch('https://api.openai.com/v1/chat/completions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${openAIApiKey}`,
        },
        body: JSON.stringify(requestData),
        signal,
      });

      const result = await processOpenAIResponseStream({
        response,
        onChunk,
        isCancelled,
        controller,
      });

      getAnalyticsManager().reportOpenAICall(requestData, result);
      const cost = calculateCosts(model, requestData, result, mode);

      return {
        result: convertResult(result),
        cost,
      };
    } catch (error) {
      console.error(`Error on attempt ${attempt}: ${error}`);

      getAnalyticsManager().reportOpenAICall(requestData, {
        error: String(error),
      });

      if (attempt === 3) {
        throw error;
      }
    }
  }

  throw new Error('Assertion: Should never get here');
}
'''
