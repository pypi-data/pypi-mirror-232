import { useDebouncedValue } from "@mantine/hooks";
import { create } from "zustand";

export type GPTMessage = {
  role: string;
  content: string;
};

export type Manual = {
  id: string;
  usage: string;
  content: string;
};

export type Strategy = {
  id: string;
  usage: string;
  content: string;
};

export type GPTMode = "QUALITY" | "FAST";

type PromptStore = {
  strategy?: Strategy;
  mode: GPTMode;
  manuals: Manual[];
  messages: GPTMessage[];
  setMessages: (newMessages: GPTMessage[]) => void;
  removeMessage: (index: number) => void;

  usedTokens: number;
  availableTokens: number;

  promptHistory: string[];
  promptIndex: number;

  historyUp: () => void;
  historyDown: () => void;
  newPrompt: () => void;
  editPrompt: (prompt: string) => void;
  getPrompt: () => string;

  requestAnalysis: () => void;
  doAnalysis: () => void;
  analysisTimeoutId: number | undefined;

  doGPT: () => void;

  messagesWithPrompt: () => GPTMessage[];

  analysisAbortController: AbortController | undefined; // New property to handle fetch operation cancellation
};

export const usePromptStore = create<PromptStore>((set, get) => ({
  strategy: undefined,
  mode: "QUALITY",
  manuals: [],
  messages: [],
  setMessages: (newMessages: GPTMessage[]) =>
    set(() => ({
      messages: newMessages,
    })),
  removeMessage: (index: number) =>
    set((state) => ({
      messages: state.messages.filter((_, i) => i !== index),
    })),

  messagesWithPrompt: () => {
    return [...get().messages, { role: "user", content: get().getPrompt() }];
  },

  analysisAbortController: undefined, // Initialize fetchAbortController as undefined

  doGPT: async () => {
    const response = await fetch(`http://${window.location.hostname}:8000/gpt`, {
      method: "POST",
      body: JSON.stringify({
        messages: get().messages,
        relevant_manuals: get().manuals,
        strategy: get().strategy?.id || "???",
        mode: get().mode,
      }),
      headers: {
        "Content-Type": "application/json",
      },
    });

    const reader = response.body?.getReader();
    const decoder = new TextDecoder("utf-8");

    const newMessages = [...get().messages, { role: "assistant", content: "" }];

    while (true) {
      const { value, done } = (await reader?.read()) || { value: undefined, done: true };

      let text = decoder.decode(value);
      if (text.includes("§§§§§CLEAR§§§§§")) {
        newMessages[newMessages.length - 1].content = "";
        //delete everything up to $$$CLEAR$$$ in text
        text = text.substring(text.indexOf("§§§§§CLEAR§§§§§") + 15);
      }

      newMessages[newMessages.length - 1].content += text;
      get().setMessages(newMessages.slice());
      //console.log(newMessages);

      if (done) {
        break;
      }
    }
  },

  getPrompt: () => {
    return get().promptHistory[get().promptIndex];
  },

  analysisTimeoutId: undefined,

  requestAnalysis: () => {
    // Create new AbortController instance for every new analysis request

    get().analysisAbortController?.abort(); // Abort existing fetch operation if any
    const abortController = new AbortController();

    set(() => ({
      analysisAbortController: abortController,
    }));

    if (get().analysisTimeoutId) {
      clearTimeout(get().analysisTimeoutId);
    }

    const timeoutId = setTimeout(() => {
      get().doAnalysis();
    }, 1000);

    set(() => ({
      analysisTimeoutId: timeoutId,
    }));
  },

  doAnalysis: async () => {
    set(() => ({
      analysisTimeoutId: undefined,
    }));

    if (get().analysisAbortController?.signal.aborted) {
      // If existing fetch operation has been aborted, stop proceeding
      return;
    }

    let response;
    try {
      response = await fetch(`http://${window.location.hostname}:8000/analyse`, {
        method: "POST",
        body: JSON.stringify({
          messages: get().messagesWithPrompt(),
          mode: get().mode,
        }),
        headers: {
          "Content-Type": "application/json",
        },
        signal: get().analysisAbortController?.signal, // Passing abort signal to fetch operation
      });
    } catch (err) {
      if ((err as any).name === "AbortError") {
        console.log("Fetch operation aborted");
        return;
      } else {
        throw err;
      }
    }

    if (get().analysisAbortController?.signal.aborted) {
      // If existing fetch operation has been aborted, stop proceeding
      return;
    }

    const data = await response.json();

    if (get().analysisAbortController?.signal.aborted) {
      // If existing fetch operation has been aborted, stop proceeding
      return;
    }

    set(() => ({
      strategy: data.strategy,
      manuals: data.manuals,
      usedTokens: data.usedTokens,
      availableTokens: data.availableTokens,
    }));

    set(() => ({
      analysisAbortController: undefined,
    }));
  },

  usedTokens: 0,
  availableTokens: 0,
  promptHistory: [""],
  promptIndex: 0,
  historyUp: () =>
    set((state) => ({
      promptIndex: Math.min(state.promptHistory.length - 1, state.promptIndex + 1),
    })),
  historyDown: () =>
    set((state) => ({ promptIndex: Math.max(0, state.promptIndex - 1) })),
  editPrompt: (prompt) => {
    set((state) => ({
      promptHistory: [
        ...state.promptHistory.slice(0, state.promptIndex),
        prompt,
        ...state.promptHistory.slice(state.promptIndex + 1, state.promptHistory.length),
      ],
    }));
    get().requestAnalysis();
  },
  newPrompt: () =>
    set((state) => ({
      promptHistory: ["", ...state.promptHistory],
      promptIndex: 0,
    })),
}));

export function useDebouncedPrompt() {
  const prompt = usePromptStore((state) => state.promptHistory[state.promptIndex]).trim();
  const [debouncedPrompt] = useDebouncedValue(prompt, 150, { leading: true });

  return debouncedPrompt;
}
