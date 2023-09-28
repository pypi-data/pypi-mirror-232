import TrashIcon from "@heroicons/react/24/solid/TrashIcon";
import ReactMarkdown from "react-markdown";
import SyntaxHighlighter from "react-syntax-highlighter";
import { darcula } from "react-syntax-highlighter/dist/cjs/styles/hljs";
import { GPTMessage, usePromptStore } from "../store/PromptStore";

export function Message({ message, index }: { message: GPTMessage; index: number }) {
  const removeMessage = usePromptStore((state) => state.removeMessage);

  return (
    <div className="flex justify-between items-center max-w-900px w-full px-5 py-5 rounded-lg bg-slate-700  shadow-lg mb-5 ">
      <div className="prose prose-stone dark:prose-invert">
        <ReactMarkdown
          components={{
            code(props) {
              const {children, className, inline, node, ...rest} = props
              const match = /language-(\w+)/.exec(className || '')
              return !inline && match ? (
                <SyntaxHighlighter
                  {...rest}
                  style={darcula}
                  children={String(children).replace(/\n$/, '')}
                  language={match[1]}
                  PreTag="div"
                />
              ) : (
                <code {...rest} className={className}>
                  {children}
                </code>
              )
            }
          }}
        >
          {message.content}
        </ReactMarkdown>
      </div>
      <button onClick={() => removeMessage(index)} className=" self-start">
        <TrashIcon className="h-5 w-5 text-white" />{" "}
      </button>
    </div>
  );
}
