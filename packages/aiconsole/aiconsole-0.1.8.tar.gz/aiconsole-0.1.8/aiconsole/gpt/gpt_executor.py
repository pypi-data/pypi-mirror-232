import decimal
import pprint

import litellm

from aiconsole.gpt.consts import MODEL_DATA
from aiconsole.gpt.count_tokens import count_tokens
from aiconsole.gpt.token_error import TokenError

from .calculate_costs import calculate_costs
# from .gpt_cache import get_cached_result
from .gpt_types import GPTRequest, GPTResult

CLEAR_STR = "§§§§§CLEAR§§§§§"


class GPTExecutor:
    def __init__(self):
        self.result = GPTResult(content="", function_call=None, cost=decimal.Decimal(0))
        self.input_tokens = 0
        self.output_tokens = 0
        self.total_cost = decimal.Decimal(0)
        self.full_result = None

    @staticmethod
    def validate_request(request: GPTRequest):
        """
        Checks if the prompt can be handled by the model
        """

        used_tokens = count_tokens(request)
        model_max_tokens = MODEL_DATA[request.model].max_tokens

        if used_tokens - model_max_tokens >= request.max_tokens:
            print(
                "Not enough tokens to perform the modification. Used tokens: ",
                used_tokens,
                "  available tokens: ",
                model_max_tokens,
                "requested tokens: ",
                request.max_tokens,
            )
            raise TokenError(
                "Combination of file size, selection, and your command is too big for us to handle."
            )

    def execute(self, request: GPTRequest):
        self.validate_request(request)

        # TODO caching result
        # cached_result = get_cached_result(request)
        #
        # if cached_result and isinstance(cached_result, str):
        #     yield cached_result
        #     self.full_result = GPTResult(
        #         content=cached_result["content"] or "",
        #         function_call=cached_result["arguments"],
        #         cost=decimal.Decimal(0),
        #     )

        raw_request = request.model_dump()

        if "function_call" in raw_request and not raw_request["function_call"]:
            del raw_request["function_call"]

        if "functions" in raw_request and raw_request["functions"] == []:
            del raw_request["functions"]

        print("GPT REQUEST:")
        pprint.pprint(raw_request)
        print()

        for attempt in range(3):
            try:
                response = litellm.completion(**raw_request)

                chunks = []

                for chunk in response:
                    chunks.append(chunk)

                    yield chunk

                rebuilt_response = litellm.stream_chunk_builder(chunks)
                message = rebuilt_response["choices"][0]["message"]

                message_content = message["content"] or ""
                message_function_call = message.get("function_call")
                cost, self.input_tokens, self.output_tokens = calculate_costs(
                    request, message_content, message_function_call
                )
                self.full_result = GPTResult(
                    content=message_content,
                    function_call=message_function_call,
                    cost=cost,
                )

                print("GPT RESPONSE:")
                pprint.pprint(self.full_result.model_dump())
                print()

                print(request, self.full_result)

                self.total_cost += self.full_result.cost
                return
            except Exception as error:
                print(f"Error on attempt {attempt}: {error}")
                print(request, {"error": str(error)})
                if attempt == 3:
                    raise error
            yield CLEAR_STR

        raise Exception("Unable to complete GPT request.")


"""import fetch from 'node-fetch';
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
"""
