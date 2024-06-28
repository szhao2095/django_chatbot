import jwt
import uuid
from datetime import datetime, timedelta
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import ChatRecord, ChatHistory
from .chatservice import NewChatInitializer, OpenAIChatService
from .env_vars import JWT_SECRET_KEY

import logging
logger = logging.getLogger('chatbot_core')

class CreateNewChat(APIView):
    def post(self, request):
        new_chat = NewChatInitializer('tax_assistant')
        unique_id = str(uuid.uuid4())
        payload = {
            'unique_id': unique_id,
            'exp': datetime.utcnow() + timedelta(days=30),
            'iat': datetime.utcnow()
        }
        new_token = jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')
        logger.debug(f"New token created with unique_id: {unique_id}")

        # Create a new ChatRecord entry
        new_record = ChatRecord(
            unique_id=unique_id,
            thread_id=new_chat.thread_id,
            assistant_id=new_chat.assistant_id,
            vector_store_id=new_chat.vector_store_id,
        )
        new_record.set_assistant_info(new_chat.assistant_info)
        new_record.set_vector_store_info(new_chat.vector_store_info)
        new_record.save()

        logger.debug("New chat record created")

        return Response({
            'jwt_token': new_token
        }, status=status.HTTP_201_CREATED)


class SendMessageView(APIView):
    def post(self, request):
        logger.debug("Received request to send a message")

        # Extract token from the Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            logger.debug("Authorization header missing")
            return Response({'error': 'Authorization header missing'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            token = auth_header.split(' ')[1]
        except IndexError:
            logger.debug("Token missing in Authorization header")
            return Response({'error': 'Token missing in Authorization header'}, status=status.HTTP_401_UNAUTHORIZED)

        if not token:
            logger.debug("Token missing")
            return Response({'error': 'Token missing'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
            unique_id = payload.get('unique_id')
            logger.debug(f"Token decoded successfully, unique_id: {unique_id}")

            # Fetch the ChatRecord entry
            chat_record = ChatRecord.objects.get(unique_id=unique_id)
            logger.debug(f"Chat record found for unique_id: {unique_id}")

        except jwt.ExpiredSignatureError:
            logger.debug("Token expired")
            return Response({'error': 'Token expired'}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            logger.debug("Invalid token")
            return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
        except ChatRecord.DoesNotExist:
            logger.debug(f"No chat record found for unique_id: {unique_id}")
            return Response({'error': 'Chat record not found'}, status=status.HTTP_404_NOT_FOUND)

        # Extract the message from the request payload
        message_content = request.data.get('message', '')
        if not message_content:
            logger.debug("Message content missing")
            return Response({'error': 'Message content missing'}, status=status.HTTP_400_BAD_REQUEST)

        logger.debug(f"Message received: {message_content}")

        # Further processing of the message goes here
        openAIChatService = OpenAIChatService(
            thread_id=chat_record.thread_id,
            assistant_id=chat_record.assistant_id,
            vector_store_id=chat_record.vector_store_id # Unused, should be set during start up, see assistant_startup.py
        )

        chat_response = openAIChatService.send_message(message_content)
        if not chat_response:
            logger.debug("No chat response received")
            return Response({'error': 'An unexpected error has occured'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        _ = ChatHistory.objects.create(
            unique_id=unique_id,
            user_message=message_content,
            response=chat_response if chat_response else ""
        )

        return Response({
            'response': chat_response
        }, status=status.HTTP_200_OK)