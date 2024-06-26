import json
import uuid
from channels.generic.websocket import WebsocketConsumer
from .chatservice import ChatService

import logging
logger = logging.getLogger('chatbot_core')

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.user_id = str(uuid.uuid4())
        self.chat_service = ChatService(user_id=self.user_id)
        self.accept()
        logger.debug(f"WebSocket connection accepted for user: {self.user_id}")

    def disconnect(self, close_code):
        logger.debug(f"WebSocket connection closed for user: {self.user_id}")
        pass

    def receive(self, text_data):
        logger.debug(f"Message received: {text_data}")
        if not text_data:
            logger.error("Received empty message")
            return
        
        try:
            text_data_json = json.loads(text_data)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return
        
        message = text_data_json.get('message', '')
        if not message:
            logger.error("No message field in received JSON")
            return
        
        response = self.chat_service.handle_message(message)

        self.send(text_data=json.dumps({
            'response': response
        }))
        logger.debug(f"Response sent to user {self.user_id}: {response}")
