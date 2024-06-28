// types.ts
export interface MessageType {
    text: string;
    user: string;
    type: 'sent' | 'received';
    isError?: boolean;
  }
  