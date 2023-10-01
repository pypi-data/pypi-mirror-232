import { GPTMessageGroup } from '../store/PromptStore';
import { cn } from '../utils/styles';
import { Message } from './Message';

export function MessageGroup({ group, isStreaming }: { group: GPTMessageGroup; isStreaming: boolean; }) {
  return (
    <div className={cn("flex flex-col gap-4 shadow-md border-t border-gray-900/50", group.role === 'user' ? "bg-transparent" : "bg-[#FFFFFF10]")}>
      {group.messages.map((message, index) => (
        <Message
          key={index}
          message={message}
          isStreaming={isStreaming} />
      ))}
    </div>
  );
}

