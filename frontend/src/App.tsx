import React from 'react';
import ChatBox from './ChatBox';
import './App.css';

const App: React.FC = () => {
  const token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1bmlxdWVfaWQiOiJmYTc2MWZkMy1lNTZmLTQ2ODEtYjM1ZS1iYjZmYjkxM2E5ODgiLCJleHAiOjE3MjIwNjgxNTUsImlhdCI6MTcxOTQ3NjE1NX0.qh90MiD3LBEHUy1eTIFmkt2V7iNJE7H23GpZ0a1QfIg';
//   const token = "";
  return (
    <div className="App">
      <ChatBox token={token} />
    </div>
  );
}

export default App;
