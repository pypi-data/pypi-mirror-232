import { useDebouncedValue } from '@mantine/hooks';
import { create } from 'zustand';

export type GPTMessage = {
  id: string;
  role: string;
  content: string;
  timestamp: string;
  language?: string;
  code?: boolean;
  code_output?: boolean;
};

export type GPTMessageGroup = {
  role: string;
  messages: GPTMessage[];
};

export type Manual = {
  id: string;
  usage: string;
  content: string;
};

export type Strategy = {
  id: string;
  usage: string;
  system: string;
};

export type GPTMode = 'QUALITY' | 'FAST';

function createMessage({
  role,
  content,
  language,
  code,
  code_output,
}: {
  role: string;
  content: string;
  language?: string;
  code?: boolean;
  code_output?: boolean;
}): GPTMessage {
  return {
    id:
      Math.random().toString(36).substring(2, 15) +
      Math.random().toString(36).substring(2, 15),
    role,
    content,
    language,
    code,
    code_output,
    timestamp: new Date().toISOString(),
  };
}

type PromptStore = {
  conversationId: string;
  strategy?: Strategy;
  mode: GPTMode;
  manuals: Manual[];
  messages: GPTMessage[];
  removeMessage: (id: string) => void;
  editMessageContent: (id: string, content: string) => void;

  groupedMessages: () => GPTMessageGroup[];

  usedTokens: number;
  availableTokens: number;

  promptHistory: string[];
  promptIndex: number;

  newConversation: () => void;

  historyUp: () => void;
  historyDown: () => void;
  newPrompt: () => void;
  editPrompt: (prompt: string) => void;
  getPrompt: () => string;
  shouldExecuteWhenReady: boolean;
  cancelGenerating: () => void;

  // analysis
  requestAnalysis: () => void;
  doAnalysis: () => void;
  analysisTimeoutId: number | undefined;
  isAnalysisDirty: boolean;
  isAnalysisRunning: boolean;

  doExecute: () => void;
  isExecuteRunning: boolean;
  submitPrompt: (prompt: string) => void;

  // requests aborts
  analysisAbortController: AbortController;
  executeAbortSignal: AbortController;
};

export const usePromptStore = create<PromptStore>((set, get) => ({
  // declarations
  conversationId:
    Math.random().toString(36).substring(2, 15) +
    Math.random().toString(36).substring(2, 15),
  strategy: undefined,
  mode: 'QUALITY',
  manuals: [],
  messages: [],
  isAnalysisDirty: false,
  isAnalysisRunning: false,
  isExecuteRunning: false,
  analysisAbortController: new AbortController(), // Initialize fetchAbortController as undefined
  executeAbortSignal: new AbortController(),
  analysisTimeoutId: undefined,
  usedTokens: 0,
  availableTokens: 0,
  promptHistory: [''],
  promptIndex: 0,
  shouldExecuteWhenReady: false,

  newConversation: () => {
    set(() => ({
      conversationId:
        Math.random().toString(36).substring(2, 15) +
        Math.random().toString(36).substring(2, 15),
    }));
  },

  groupedMessages: () => {
    const groups: GPTMessageGroup[] = [];
    for (const message of get().messages) {
      if (
        groups.length === 0 ||
        groups[groups.length - 1].role !== message.role
      ) {
        groups.push({
          role: message.role,
          messages: [message],
        });
      } else {
        groups[groups.length - 1].messages.push(message);
      }
    }
    return groups;
  },

  removeMessage: (id: string) =>
    set((state) => ({
      messages: state.messages.filter((message) => message.id !== id),
    })),

  editMessageContent: (id: string, content: string) =>
    set((state) => ({
      messages: state.messages.map((message) =>
        message.id === id ? { ...message, content } : message,
      ),
    })),

  doExecute: async () => {
    set(() => ({
      executeAbortSignal: new AbortController(),
      isExecuteRunning: true,
      shouldExecuteWhenReady: false,
    }));

    try {
      const response = await fetch(
        `http://${window.location.hostname}:8000/execute`,
        {
          method: 'POST',
          body: JSON.stringify({
            conversation_id: get().conversationId,
            messages: get().messages,
            relevant_manuals: get().manuals,
            strategy: get().strategy?.id || '???',
            mode: get().mode,
          }),
          headers: {
            'Content-Type': 'application/json',
          },
          signal: get().executeAbortSignal.signal,
        },
      );

      const reader = response.body?.getReader();
      const decoder = new TextDecoder('utf-8');

      let messageDone = true;
      while (true) {
        // this is temporary
        try {
          const { value, done } = (await reader?.read()) || {
            value: undefined,
            done: true,
          };

          const messages = get().messages;

          const TOKEN_PROCESSORS = [
            ...[
              'python',
              'bash',
              'shell',
              'javascript',
              'html',
              'applescript',
              'r',
            ].map((language) => ({
              token: `<<<< START CODE (${language}) >>>>`,
              processor: () => {
                messages.push(
                  createMessage({
                    role: 'assistant',
                    content: '',
                    language: language,
                    code: true,
                  }),
                );

                messageDone = false;
              },
            })),
            {
              token: '<<<< END CODE >>>>',
              processor: () => {
                if (messageDone) throw new Error('Invalid chunk');
                messageDone = true;
              },
            },
            {
              token: '<<<< START CODE OUTPUT >>>>',
              processor: () => {
                messages.push(
                  createMessage({
                    role: 'assistant',
                    content: '',
                    code_output: true,
                  }),
                );
                messageDone = false;
              },
            },
            {
              token: '<<<< END CODE OUTPUT >>>>',
              processor: () => {
                if (messageDone) throw new Error('Invalid chunk');
                messageDone = true;
              },
            },
            {
              token: '<<<< CLEAR >>>>',
              processor: () => {
                if (!messageDone) {
                  messages.push(
                    createMessage({ role: 'assistant', content: '' }),
                  );
                  messageDone = false;
                }
                messages[messages.length - 1].content = '';
              },
            },
          ];

          const textChunk = decoder.decode(value);

          const escapeRegExp = (string: string) =>
            string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
          const tokens = TOKEN_PROCESSORS.map((processor) => processor.token);
          const regexPattern = new RegExp(
            `(${tokens.map(escapeRegExp).join('|')})`,
            'g',
          );
          const splitText = textChunk
            .split(regexPattern)
            .filter((text) => text !== '');

          for (const text of splitText) {
            let consumed = false;
            TOKEN_PROCESSORS.forEach((tokenProcessor) => {
              if (text === tokenProcessor.token) {
                tokenProcessor.processor();
                consumed = true;
              }
            });

            if (!consumed) {
              if (messageDone) {
                messages.push({
                  id:
                    Math.random().toString(36).substring(2, 15) +
                    Math.random().toString(36).substring(2, 15),
                  role: 'assistant',
                  content: '',
                  timestamp: new Date().toISOString(),
                });
                messageDone = false;
              }
              messages[messages.length - 1].content += text;
            }
          }

          set(() => ({
            messages: messages.slice(),
          }));

          if (done) {
            break;
          }
        } catch (err) {
          if ((err as Error).name === 'AbortError') {
            console.log('Execution operation aborted');
            return;
          } else {
            throw err;
          }
        }
      }
    } finally {
      set(() => ({
        isExecuteRunning: false,
      }));

      get().requestAnalysis();
    }
  },

  cancelGenerating: () => {
    get().executeAbortSignal.abort();
  },

  getPrompt: () => {
    return get().promptHistory[get().promptIndex];
  },

  requestAnalysis: () => {
    if (get().shouldExecuteWhenReady) {
      return;
    }

    set(() => ({
      isAnalysisDirty: true,
    }));

    get().analysisAbortController?.abort(); // Abort existing fetch operation if any

    set(() => ({
      analysisAbortController: new AbortController(),
    }));

    if (get().analysisTimeoutId) {
      clearTimeout(get().analysisTimeoutId);
    }

    const timeoutId = setTimeout(() => {
      set(() => ({
        analysisTimeoutId: undefined,
      }));

      if (get().analysisAbortController.signal.aborted) {
        // If the existing fetch operation has been aborted, stop proceeding
        return;
      }

      get().doAnalysis();
    }, 1000);

    set(() => ({
      analysisTimeoutId: timeoutId,
    }));
  },

  doAnalysis: async () => {
    let shouldAnalysisBeDirtyAfter = false;

    try {
      set(() => ({
        isAnalysisRunning: true,
      }));
      const response = await fetch(
        `http://${window.location.hostname}:8000/analyse`,
        {
          method: 'POST',
          body: JSON.stringify({
            messages: [
              ...get().messages,
              createMessage({ role: 'user', content: get().getPrompt() }),
            ],
            mode: get().mode,
          }),
          headers: {
            'Content-Type': 'application/json',
          },
          signal: get().analysisAbortController.signal, // Passing abort signal to fetch operation
        },
      );

      const data = await response.json();

      if (get().analysisAbortController.signal.aborted) {
        // If existing fetch operation has been aborted, stop proceeding
        return;
      }

      set(() => ({
        strategy: data.strategy,
        manuals: data.manuals,
        usedTokens: data.usedTokens,
        availableTokens: data.availableTokens,
      }));

      if (get().shouldExecuteWhenReady) {
        get().doExecute();
      }
    } catch (err) {
      if ((err as Error).name === 'AbortError') {
        console.log('Analysis aborted');
        shouldAnalysisBeDirtyAfter = true;
        return;
      } else {
        throw err;
      }
    } finally {
      set(() => ({
        isAnalysisDirty: shouldAnalysisBeDirtyAfter,
        isAnalysisRunning: false,
      }));
    }
  },

  historyUp: () =>
    set((state) => ({
      promptIndex: Math.min(
        state.promptHistory.length - 1,
        state.promptIndex + 1,
      ),
    })),

  historyDown: () =>
    set((state) => ({ promptIndex: Math.max(0, state.promptIndex - 1) })),

  editPrompt: (prompt) => {
    set((state) => ({
      promptHistory: [
        ...state.promptHistory.slice(0, state.promptIndex),
        prompt,
        ...state.promptHistory.slice(
          state.promptIndex + 1,
          state.promptHistory.length,
        ),
      ],
    }));
    get().requestAnalysis();
  },

  newPrompt: () =>
    set((state) => ({
      promptHistory: ['', ...state.promptHistory],
      promptIndex: 0,
    })),

  submitPrompt: async (prompt: string) => {
    if (prompt.trim() !== '') {
      set(() => ({
        messages: [
          ...get().messages,
          createMessage({ role: 'user', content: prompt }),
        ],
      }));
    }

    if (get().isAnalysisDirty) {
      set(() => ({
        shouldExecuteWhenReady: true,
      }));
    } else {
      get().doExecute();
    }
  },
}));

export function useDebouncedPrompt() {
  const prompt = usePromptStore(
    (state) => state.promptHistory[state.promptIndex],
  ).trim();
  const [debouncedPrompt] = useDebouncedValue(prompt, 150, { leading: true });

  return debouncedPrompt;
}
