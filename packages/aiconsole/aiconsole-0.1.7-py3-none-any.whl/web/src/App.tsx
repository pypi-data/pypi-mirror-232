import { useCallback, useState, useRef, useEffect } from "react";
import { CommandInput } from "./components/CommandInput";
import { Pill } from "./components/Pill";
import { usePromptStore } from "./store/PromptStore";
import { Message } from "./components/Message";

function App() {
  const [scrolling, setScrolling] = useState<boolean>(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const strategy = usePromptStore((state) => state.strategy);
  const mode = usePromptStore((state) => state.mode);
  const manuals = usePromptStore((state) => state.manuals);
  const usedTokens = usePromptStore((state) => state.usedTokens);
  const availableTokens = usePromptStore((state) => state.availableTokens);
  const messages = usePromptStore((state) => state.messages);
  const setMessages = usePromptStore((state) => state.setMessages);
  const doGPT = usePromptStore((state) => state.doGPT);
  const loadingAnalysis = usePromptStore(
    (state) => state.analysisAbortController && !state.analysisTimeoutId
  );
  const resettingAnalysis = usePromptStore((state) => state.analysisAbortController);

  const timerIdRef = useRef<number | null>(null);
  useEffect(() => {
    const { current } = messagesEndRef;
    if (!current) return;

    const handleScroll = () => {
      if (timerIdRef.current) {
        clearTimeout(timerIdRef.current);
      }
      setScrolling(true);
      timerIdRef.current = setTimeout(() => setScrolling(false), 1000); // Reset scrolling after 1 second.
    };

    current.addEventListener("scroll", handleScroll);
    return () => {
      current.removeEventListener("scroll", handleScroll);
      // It's important to also clear the timer when the component unmounts.
      if (timerIdRef.current) {
        clearTimeout(timerIdRef.current);
      }
    };
  }, []);

  useEffect(() => {
    const { current } = messagesEndRef;
    if (!current || scrolling) return;

    if (
      Math.abs(current.scrollTop - (current.scrollHeight - current.clientHeight)) < 300
    ) {
      const newValue = Math.max(current.scrollHeight - current.clientHeight, 0);
      current.scrollTop = newValue;
    }
  }, [messages, scrolling]);

  const handleSubmit = useCallback(
    async (prompt: string) => {
      if (prompt.trim() !== "") {
        setMessages([...messages, { role: "user", content: prompt }]);
      }
      doGPT();
    },
    [messages, setMessages, doGPT]
  );

  return (
    <div className="App flex flex-col fixed top-0 left-0 bottom-0 right-0 p-5 justify-between dark:bg-gray-800 dark: text-slate-100">
      <div className="flex-grow overflow-y-auto flex flex-col" ref={messagesEndRef}>
        {messages.length === 0 ? (
          <div>No messages</div>
        ) : (
          <div>
            {messages.map((message, index) => (
              <Message message={message} index={index} key={index} />
            ))}
          </div>
        )}
      </div>
      {!resettingAnalysis && (
        <div className="flex flex-row gap-2">
          {strategy && (
            <div>
              Strategy: <Pill color="red">{strategy.id}</Pill>
            </div>
          )}
          <div>
            Mode: <Pill color="blue">{mode}</Pill>
          </div>
          <div>
            Manuals:
            {manuals.map((manual) => (
              <Pill key={manual.id} color="red">
                {manual.id}
              </Pill>
            ))}
          </div>
          <div>
            Memory:{" "}
            <Pill color="green">
              {((100 * (availableTokens - usedTokens)) / availableTokens).toFixed(1)}%
            </Pill>
          </div>
        </div>
      )}

      {resettingAnalysis && (
        <div className="flex flex-row gap-2">
          <div>
            {loadingAnalysis && (
              <svg
                className=" animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                ></circle>
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
            )}
          </div>
        </div>
      )}
      <div className="">
        <CommandInput onSubmit={handleSubmit} disabled={!!resettingAnalysis} />
      </div>
    </div>
  );
}

export default App;
