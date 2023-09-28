import { useRef } from "react";
import { PaperAirplaneIcon } from "@heroicons/react/24/solid";

import { cn } from "../utils/styles";
import { usePromptStore } from "../store/PromptStore";

interface MessageInputProps {
  onSubmit: (command: string) => void;
  className?: string;
  disabled?: boolean;
}

export const CommandInput = ({ onSubmit, className, disabled }: MessageInputProps) => {
  const prompt = usePromptStore((state) => state.promptHistory[state.promptIndex]);

  const setPrompt = usePromptStore((state) => state.editPrompt);
  const newPrompt = usePromptStore((state) => state.newPrompt);
  const promptUp = usePromptStore((state) => state.historyUp);
  const promptDown = usePromptStore((state) => state.historyDown);

  const textAreaRef = useRef<HTMLTextAreaElement>(null);

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setPrompt(e.target.value);

    if (textAreaRef.current) {
      if (e.target.value.trim() === "") {
        textAreaRef.current.style.height = `${16 + 24 + 2}px`;
      } else {
        textAreaRef.current.style.height = `${textAreaRef.current.scrollHeight + 2}px`;
      }
    }
  };

  const handleKeyDown = async (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (!disabled) await handleSendMessage();
    }

    if (textAreaRef.current) {
      const caretAtStart =
        textAreaRef.current.selectionStart === 0 &&
        textAreaRef.current.selectionEnd === 0;
      const caretAtEnd =
        textAreaRef.current.selectionStart === textAreaRef.current.value.length &&
        textAreaRef.current.selectionEnd === textAreaRef.current.value.length;

      if (e.key === "ArrowUp" && caretAtStart) {
        promptUp();
      } else if (e.key === "ArrowDown" && caretAtEnd) {
        promptDown();
      }
    }
  };

  const handleSendMessage = async () => {
    const trimmed = prompt.trim();
    //if (!trimmed) return;
    onSubmit(trimmed);
    newPrompt();
  };

  return (
    <div className={cn(className, "flex w-full flex-col p-4")}>
      <div className="flex items-center">
        <textarea
          ref={textAreaRef}
          className="border-slate-300 bg-slate-400 text-slate-900 flex-grow resize-none overflow-hidden rounded-md border px-4 py-2 focus:outline-none focus:ring-2"
          value={prompt}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          placeholder="Type a new command here..."
          rows={1}
          style={{ boxSizing: "border-box", transition: "height 0.2s" }}
        />
        <button
          className={cn(
            "focus:ring-primary ml-4 rounded-md px-4 py-2 transition-colors duration-200 ease-in-out focus:outline-none focus:ring-4",
            {
              "bg-slate-500  text-slate-800 cursor-not-allowed": disabled,
              "bg-orange-700 hover:bg-orange-500 text-primary-content": !disabled,
            }
          )}
          type="button"
          onClick={handleSendMessage}
          disabled={disabled}
        >
          <PaperAirplaneIcon className="h-6 w-6 scale-75" />
        </button>
      </div>
    </div>
  );
};
