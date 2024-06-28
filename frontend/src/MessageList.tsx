import React from 'react';
import Message from './Message';

interface MessageType {
  text: string;
  user: string;
  userImage: string;
  type: 'sent' | 'received';
}

const messages: MessageType[] = [
  {
    text: 'yes, I have a mac. I never had issues with root permission as well, but this helped me to solve the problem',
    user: 'Anderson Vanhron',
    userImage: 'https://images.unsplash.com/photo-1590031905470-a1a1feacbb0b?ixlib=rb-1.2.1&amp;ixid=eyJhcHBfaWQiOjEyMDd9&amp;auto=format&amp;fit=facearea&amp;facepad=3&amp;w=144&amp;h=144',
    type: 'sent',
  },
  {
    text: 'I also have this issue, Here is what I was doing until now: #1076',
    user: 'User 2',
    userImage: 'https://images.unsplash.com/photo-1549078642-b2ba4bda0cdb?ixlib=rb-1.2.1&amp;ixid=eyJhcHBfaWQiOjEyMDd9&amp;auto=format&amp;fit=facearea&amp;facepad=3&amp;w=144&amp;h=144',
    type: 'received',
  },
  {
    text: 'even i am facing',
    user: 'User 2',
    userImage: 'https://images.unsplash.com/photo-1549078642-b2ba4bda0cdb?ixlib=rb-1.2.1&amp;ixid=eyJhcHBfaWQiOjEyMDd9&amp;auto=format&amp;fit=facearea&amp;facepad=3&amp;w=144&amp;h=144',
    type: 'received',
  },
];

const MessageList: React.FC = () => {
  return (
    <div id="messages" className="flex flex-col space-y-4 p-3 overflow-y-auto scrollbar-thumb-blue scrollbar-thumb-rounded scrollbar-track-blue-lighter scrollbar-w-2 scrolling-touch">
      {messages.map((msg, index) => (
        <Message key={index} message={msg} />
      ))}
    </div>
  );
};

export default MessageList;
