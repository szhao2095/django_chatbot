import logging
from django.shortcuts import HttpResponse, render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import ChatService
from .serializers import ChatHistorySerializer

# Set up logging
logger = logging.getLogger('chatbot_core')

# Create your views here.
def home(request):
    logger.debug("Home view called")
    return HttpResponse("Hello, world!")

class ChatAPIView(APIView):
    def post(self, request):
        user_message = request.data.get('message')
        user_id = request.data.get('user_id', 'anonymous')  # Adjust as needed

        logger.debug(f"Received message from user {user_id}: {user_message}")

        chat_service = ChatService(user_id=user_id, message=user_message)
        try:
            response = chat_service.get_reply()
            logger.debug(f"Response from chat service: {response}")
            return Response(response, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error processing chat request: {e}")
            return Response({"error": "An error occurred while processing your request."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
