import jwt
import uuid
from datetime import datetime, timedelta
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import ChatRecord
from .chatservice import OpenAIChatService
from .env_vars import JWT_SECRET_KEY

import logging
logger = logging.getLogger('chatbot_core')

class CreateOrValidateTokenView(APIView):
    def post(self, request):
        logger.debug("Received request to validate or create token")

        token = request.headers.get('Authorization')
        if token:
            logger.debug("Token provided, attempting to decode")
            try:
                payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
                unique_id = payload.get('unique_id')
                logger.debug(f"Token decoded successfully, unique_id: {unique_id}")

                # Fetch the ChatRecord entry
                chat_record = ChatRecord.objects.get(unique_id=unique_id)
                logger.debug(f"Chat record found for unique_id: {unique_id}")

                # Extend the token's expiration date
                new_payload = {
                    'unique_id': unique_id,
                    'exp': datetime.utcnow() + timedelta(days=30),
                    'iat': datetime.utcnow()
                }
                new_token = jwt.encode(new_payload, JWT_SECRET_KEY, algorithm='HS256')
                logger.debug("Token expiration extended")

                return Response({
                    'new_token': new_token
                }, status=status.HTTP_200_OK)
            
            except jwt.ExpiredSignatureError:
                logger.debug("Token expired")
                return Response({'error': 'Token expired'}, status=status.HTTP_401_UNAUTHORIZED)
            except jwt.InvalidTokenError:
                logger.debug("Invalid token")
                return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
            except ChatRecord.DoesNotExist:
                logger.debug(f"No chat record found for unique_id: {unique_id}")
                return Response({'error': 'Chat record not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            logger.debug("No token provided, creating a new one")
            unique_id = str(uuid.uuid4())
            payload = {
                'unique_id': unique_id,
                'exp': datetime.utcnow() + timedelta(days=30),
                'iat': datetime.utcnow()
            }
            new_token = jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')
            logger.debug(f"New token created with unique_id: {unique_id}")

            # Instantiate the class and let it generate the 3 values
            openAIChatService = OpenAIChatService()
            logger.debug("OpenAIChatService instance created")
            logger.debug(f"assistant_id: {openAIChatService.assistant_id}")
            logger.debug(f"thread_id: {openAIChatService.thread_id}")
            logger.debug(f"vector_store_id: {openAIChatService.vector_store_id}")

            # Create a new ChatRecord entry
            chat_record = ChatRecord.objects.create(
                unique_id=unique_id,
                assistant_id=openAIChatService.assistant_id,
                thread_id=openAIChatService.thread_id,
                vector_store_id=openAIChatService.vector_store_id
            )
            logger.debug("New chat record created")

            return Response({
                'jwt_token': new_token
            }, status=status.HTTP_201_CREATED)
