import React, { useState, useEffect } from 'react';
import Header from './Header';
import MessageList from './MessageList';
import InputBox from './InputBox';
import { MessageType } from './types';
import axios from 'axios';

interface ChatBoxProps {
  token?: string;
  userImage: string;
  assistantImage: string;
}

const ChatBox: React.FC<ChatBoxProps> = ({ token: initialToken, userImage, assistantImage }) => {
  const [messages, setMessages] = useState<MessageType[]>([
    {
      text: 'Hi there! How can I assist you today?',
      user: 'Assistant',
      type: 'received',
    },
  ]);
  const [token, setToken] = useState<string | null>(initialToken ?? null);

  useEffect(() => {
    const fetchToken = async () => {
      try {
        const response = await axios.post('http://localhost:8000/api/v1/chat/create-or-validate-token/');
        setToken(response.data.jwt_token);
      } catch (error) {
        console.error('Error fetching token:', error);
      }
    };

    if (!token) {
      fetchToken();
    }
  }, [token]);


  const addMessage = (message: MessageType) => {
    setMessages(prevMessages => [...prevMessages, message]);
  };

//   useEffect(() => {
//     console.log(messages);
//   }, [messages]);

  return (
    <div className="flex-1 p-2 sm:p-6 justify-between flex flex-col h-screen">
      <Header />
      <MessageList messages={messages} userImage={userImage} assistantImage={assistantImage} />
      {token && <InputBox addMessage={addMessage} token={token} />}
    </div>
  );
};

export default ChatBox;
