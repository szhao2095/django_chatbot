import React from 'react';
import Header from './Header';
import MessageList from './MessageList';
import InputBox from './InputBox';

const ChatBox: React.FC = () => {
  return (
    <div className="flex-1 p-2 sm:p-6 justify-between flex flex-col h-screen">
      <Header />
      <MessageList />
      <InputBox />
    </div>
  );
};

export default ChatBox;
