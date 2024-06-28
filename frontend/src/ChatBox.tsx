import React, { useState, useEffect } from 'react';
import Header from './Header';
import MessageList from './MessageList';
import InputBox from './InputBox';
import { MessageType } from './types';

const ChatBox: React.FC = () => {
  const [messages, setMessages] = useState<MessageType[]>([
    {
      text: 'Hi there! How can I assist you today?',
      user: 'Assistant',
      userImage: 'https://images.unsplash.com/photo-1549078642-b2ba4bda0cdb?ixlib=rb-1.2.1&amp;ixid=eyJhcHBfaWQiOjEyMDd9&amp;auto=format&amp;fit=facearea&amp;facepad=3&amp;w=144&amp;h=144',
      type: 'received',
    },
  ]);

  const addMessage = (message: MessageType) => {
    setMessages(prevMessages => [...prevMessages, message]);
  };

//   useEffect(() => {
//     console.log(messages);
//   }, [messages]);

  return (
    <div className="flex-1 p-2 sm:p-6 justify-between flex flex-col h-screen">
      <Header />
      <MessageList messages={messages} />
      <InputBox addMessage={addMessage} />
    </div>
  );
};

export default ChatBox;
