import React from 'react';
import Message from './Message';
import { MessageType } from './types';

interface MessageListProps {
  messages: MessageType[];
  userImage: string;
  assistantImage: string;
}

const MessageList: React.FC<MessageListProps> = ({ messages, userImage, assistantImage }) => {
  const groupedMessages: MessageType[][] = [];

  let currentGroup: MessageType[] = [];

  messages.forEach((message, index) => {
    if (currentGroup.length === 0 || currentGroup[currentGroup.length - 1].type === message.type) {
      currentGroup.push(message);
    } else {
      groupedMessages.push(currentGroup);
      currentGroup = [message];
    }
  });

  if (currentGroup.length > 0) {
    groupedMessages.push(currentGroup);
  }

  return (
    <div id="messages" className="flex flex-col space-y-4 p-3 overflow-y-auto scrollbar-thumb-blue scrollbar-thumb-rounded scrollbar-track-blue-lighter scrollbar-w-2 scrolling-touch flex-grow items-start justify-start">
      {groupedMessages.map((group, index) => {
        const imageUrl = group[0].type === 'sent' ? userImage : assistantImage;
        return <Message key={index} messages={group} imageUrl={imageUrl} />;
      })}
    </div>
  );
};

export default MessageList;