import { useDebouncedValue } from '@mantine/hooks';
import { create } from 'zustand';

export type GPTMessage = {
  role: string;
  content: string;
  isStreaming?: boolean;
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

type PromptStore = {
  strategy?: Strategy;
  mode: GPTMode;
  manuals: Manual[];
  messages: GPTMessage[];
  setMessages: (newMessages: GPTMessage[]) => void;
  removeMessage: (index: number) => void;
  editMessageContent: (index: number, content: string) => void;

  usedTokens: number;
  availableTokens: number;

  promptHistory: string[];
  promptIndex: number;

  historyUp: () => void;
  historyDown: () => void;
  newPrompt: () => void;
  editPrompt: (prompt: string) => void;
  getPrompt: () => string;
  waitingPrompt: string | undefined;
  setWaitingPrompt: (prompt: string | undefined) => void;
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

  messagesWithPrompt: () => GPTMessage[];

  // requests aborts
  analysisAbortController: AbortController;
  executeAbortSignal: AbortController;
};

export const usePromptStore = create<PromptStore>((set, get) => ({
  // declarations
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
  waitingPrompt: undefined,
  usedTokens: 0,
  availableTokens: 0,
  promptHistory: [''],
  promptIndex: 0,

  // setters
  setWaitingPrompt: (prompt) =>
    set(() => ({
      waitingPrompt: prompt,
    })),

  setMessages: (newMessages: GPTMessage[]) =>
    set(() => ({
      messages: newMessages,
    })),

  removeMessage: (index: number) =>
    set((state) => ({
      messages: state.messages.filter((_, i) => i !== index),
    })),

  editMessageContent: (index: number, content: string) =>
    set((state) => ({
      messages: state.messages.map((message, i) =>
        i === index ? { ...message, content } : message,
      ),
    })),

  messagesWithPrompt: () => {
    return [...get().messages, { role: 'user', content: get().getPrompt() }];
  },

  doExecute: async () => {
    set(() => ({
      executeAbortSignal: new AbortController(),
      isExecuteRunning: true,
    }));

    try {
      const response = await fetch(
        `http://${window.location.hostname}:8000/execute`,
        {
          method: 'POST',
          body: JSON.stringify({
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

      const newMessages = [
        ...get().messages,
        { role: 'assistant', content: '', isStreaming: true },
      ];

      while (true) {
        // this is temporary
        try {
          const { value, done } = (await reader?.read()) || {
            value: undefined,
            done: true,
          };

          let text = decoder.decode(value);
          if (text.includes('§§§§§CLEAR§§§§§')) {
            newMessages[newMessages.length - 1].content = '';
            //delete everything up to $$$CLEAR$$$ in text
            text = text.substring(text.indexOf('§§§§§CLEAR§§§§§') + 15);
          }

          newMessages[newMessages.length - 1].content += text;
          get().setMessages(newMessages.slice());

          if (done) {
            newMessages[newMessages.length - 1].isStreaming = false;
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
    }
  },

  cancelGenerating: () => {
    get().executeAbortSignal.abort();
  },

  getPrompt: () => {
    return get().promptHistory[get().promptIndex];
  },

  requestAnalysis: () => {
    if (get().waitingPrompt !== undefined) {
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
            messages: get().messagesWithPrompt(),
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

      const waitingPrompt = get().waitingPrompt;
      if (waitingPrompt) {
        get().submitPrompt(waitingPrompt);
        get().setWaitingPrompt(undefined);
      }
    } catch (err) {
      const waitingPrompt = get().waitingPrompt;
      if (waitingPrompt) {
        get().editPrompt(waitingPrompt);
        get().setWaitingPrompt(undefined);
      }

      if ((err as Error).name === 'AbortError') {
        console.log('Analysis aborted');
        shouldAnalysisBeDirtyAfter = true;
        return;
      } else {
        throw err;
      }
    } finally {
      set(() => ({ isAnalysisDirty: shouldAnalysisBeDirtyAfter, isAnalysisRunning: false }));
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
    if (get().isAnalysisDirty && get().waitingPrompt === undefined) {
      get().setWaitingPrompt(prompt);
      return;
    }

    if (prompt.trim() !== '') {
      get().setMessages([...get().messages, { role: 'user', content: prompt }]);
    }

    get().doExecute();
  },
}));

export function useDebouncedPrompt() {
  const prompt = usePromptStore(
    (state) => state.promptHistory[state.promptIndex],
  ).trim();
  const [debouncedPrompt] = useDebouncedValue(prompt, 150, { leading: true });

  return debouncedPrompt;
}
