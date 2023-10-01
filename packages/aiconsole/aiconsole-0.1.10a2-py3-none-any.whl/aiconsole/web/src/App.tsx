import { useState, useRef, useEffect } from "react";
import { CommandInput } from "./components/CommandInput";
import { Pill } from "./components/Pill";
import { usePromptStore } from "./store/PromptStore";
import { MessageGroup } from "./components/MessageGroup";

function App() {

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [scrolling, setScrolling] = useState<boolean>(false);
  const timerIdRef = useRef<number | null>(null);
  const {
      groupedMessages,
      isAnalysisDirty,
      isAnalysisRunning,
      isExecuteRunning,
      messages,
      availableTokens,
      usedTokens,
      manuals,
      mode,
      strategy,
  } = usePromptStore(
      (state) => state
  );

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
    if (!current || scrolling || !isExecuteRunning) return;

    if (
      Math.abs(current.scrollTop - (current.scrollHeight - current.clientHeight)) < 250
    ) {
      const newValue = Math.max(current.scrollHeight - current.clientHeight, 0);
      current.scrollTop = newValue;
    }
  }, [messages, scrolling, isExecuteRunning]);

  return (
    <div className="App flex flex-col fixed top-0 left-0 bottom-0 right-0 justify-between bg-gray-800 dark: text-slate-200">
      <div className="flex-grow overflow-y-auto flex flex-col" ref={messagesEndRef}>
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-2xl text-gray-400">Welcome to AI-Console</div>
        ) : (
          <div>
            {groupedMessages().map((group, index) => (
              <MessageGroup group={group} key={index} isStreaming={isExecuteRunning && index === messages.length - 1} />
            ))}
          </div>
        )}
      </div>
      {/* for now, let's assume that we need to have strategy from the backend */}
      {!isAnalysisDirty && (
        <div className="flex flex-row gap-2 mt-5 ml-5 mr-5">
          {strategy && (
            <div>
              Strategy: <Pill color="red" title={`id: ${strategy.id}\nusage: ${strategy.usage}\nsystem: ${strategy.system}`}>{strategy.id}</Pill>
            </div>
          )}
          <div>
            Mode: <Pill color="blue" title={mode}>{mode}</Pill>
          </div>
          {manuals.length > 0 && <div>
            Manuals:
            {manuals.map((manual) => (
              <Pill key={manual.id} color="red" title={`id: ${manual.id}\nusage: ${manual.usage}\ncontent: ${manual.content.length > 100 ? manual.content.substring(0, 100) + "..." : manual.content}`}>
                {manual.id}
              </Pill>
            ))}
          </div> }
          {availableTokens > 0 && <div>
            Memory:
            <Pill color="green" title={`Analysis:\nMax tokens: ${availableTokens}\nUsed tokens: ${usedTokens}\n\nExecution:\nMax tokens: ?\nUsed tokens: ? `}>
              {((100 * (availableTokens - usedTokens)) / availableTokens).toFixed(1)}%
            </Pill>
          </div> }
        </div>
      )}

      {isAnalysisRunning && (
        <div className="flex flex-row gap-2">
          <div className="mt-5 ml-5 mr-5">
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
          </div>
        </div>
      )}
      <div className="">
        <CommandInput />
      </div>
    </div>
  );
}

export default App;
