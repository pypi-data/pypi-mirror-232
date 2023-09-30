import { ChangeEvent, useMemo, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import TextareaAutosize from 'react-textarea-autosize';
import SyntaxHighlighter from 'react-syntax-highlighter';
import { darcula } from 'react-syntax-highlighter/dist/cjs/styles/hljs';

import { GPTMessage, usePromptStore } from '../store/PromptStore';
import { MessageControls } from './MessageControls';

interface MessageProps {
  message: GPTMessage;
  index: number;
}

export function Message({ message, index }: MessageProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [content, setContent] = useState(message.content);
  const removeMessage = usePromptStore((state) => state.removeMessage);
  const updateMessage = usePromptStore((state) => state.editMessageContent);

  const handleEditClick = () => {
    if (message.isStreaming) {
      return;
    }
    setContent(message.content);
    setIsEditing(true);
  };

  const handleRemoveClick = () => removeMessage(index);

  const handleCancelEditClick = () => setIsEditing(false);

  const handleOnChange = (e: ChangeEvent<HTMLTextAreaElement>) =>
    setContent(e.target.value);

  const handleSaveClick = () => {
    updateMessage(index, content);
    setIsEditing(false);
  };

  const messageContent = useMemo(() => {
    if (isEditing) {
      return (
        <div className="bg-[#00000080] rounded-md w-[660px]">
          <TextareaAutosize
            className="resize-none border-0 bg-transparent w-full outline-none h-96 p-4"
            defaultValue={content}
            onChange={handleOnChange}
          />
        </div>
      );
    }

    return (
      <ReactMarkdown
        components={{
          code(props) {
            // eslint-disable-next-line @typescript-eslint/no-unused-vars
            const { children, className, inline, node, ...rest } = props;
            const match = /language-(\w+)/.exec(className || '');
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
            );
          },
        }}
      >
        {message.content}
      </ReactMarkdown>
    );
  }, [isEditing, content, message.content]);

  return (
    <div className="flex justify-between items-center max-w-900px w-full px-5 py-5 rounded-lg bg-slate-700  shadow-lg mb-5 relative">
      <div className="prose prose-stone dark:prose-invert">
        {messageContent}
      </div>
      <MessageControls
        isEditing={isEditing}
        onCancelClick={handleCancelEditClick}
        onEditClick={handleEditClick}
        onSaveClick={handleSaveClick}
        onRemoveClick={handleRemoveClick}
      />
    </div>
  );
}
