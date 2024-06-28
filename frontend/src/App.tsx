import React from 'react';
import ChatBox from './ChatBox';
import './App.css';

const App: React.FC = () => {
  const token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1bmlxdWVfaWQiOiJmYTc2MWZkMy1lNTZmLTQ2ODEtYjM1ZS1iYjZmYjkxM2E5ODgiLCJleHAiOjE3MjIwNjgxNTUsImlhdCI6MTcxOTQ3NjE1NX0.qh90MiD3LBEHUy1eTIFmkt2V7iNJE7H23GpZ0a1QfIg';
  const userImage = 'https://images.unsplash.com/photo-1590031905470-a1a1feacbb0b?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=facearea&facepad=3&w=144&h=144';
  const assistantImage = 'https://images.unsplash.com/photo-1549078642-b2ba4bda0cdb?ixlib=rb-1.2.1&amp;ixid=eyJhcHBfaWQiOjEyMDd9&amp;auto=format&amp;fit=facearea&amp;facepad=3&amp;w=144&amp;h=144'
  return (
    <div className="App">
      <ChatBox token={token} userImage={userImage} assistantImage={assistantImage} />
    </div>
  );
}

export default App;
