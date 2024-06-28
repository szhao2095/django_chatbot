// types.ts
export interface MessageType {
    text: string;
    user: string;
    userImage: string;
    type: 'sent' | 'received';
    isError?: boolean;
  }
  