import React from 'react';
import { MessageType } from './types';

interface MessageProps {
  message: MessageType;
}

const Message: React.FC<MessageProps> = ({ message }) => {
  return (
    <div className={`chat-message w-full`}>
      <div className={`flex items-end ${message.type === 'sent' ? 'justify-end' : ''}`}>
        <div className={`flex flex-col space-y-2 text-xs max-w-xs mx-2 ${message.type === 'sent' ? 'items-end order-1' : 'items-start order-2'}`}>
          <div>
            <span className={`px-4 py-2 rounded-lg inline-block ${message.type === 'sent' ? 'rounded-br-none bg-blue-600 text-white' : 'rounded-bl-none bg-gray-300 text-gray-600'} ${message.isError ? 'bg-red-500 text-white' : ''}`}>
              {message.text}
            </span>
          </div>
        </div>
        <img src={message.userImage} alt={message.user} className={`w-6 h-6 rounded-full ${message.type === 'sent' ? 'order-2' : 'order-1'}`} />
      </div>
    </div>
  );
};

export default Message;
