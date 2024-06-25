from django.shortcuts import HttpResponse, render

# Create your views here.
def home(request):
    return HttpResponse("Hello, world!")

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import ChatService
from .serializers import ChatHistorySerializer

class ChatAPIView(APIView):
    def post(self, request):
        user_message = request.data.get('message')
        user_id = request.data.get('user_id', 'anonymous')  # Adjust as needed

        chat_service = ChatService(user_id=user_id, message=user_message)
        response = chat_service.get_reply()

        return Response(response, status=status.HTTP_201_CREATED)

# def perform_rag_retrieval(prompt):
#     # Implement RAG retrieval logic here
#     return "Retrieved context based on internal knowledge base."