import logging
from django.shortcuts import HttpResponse, render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# Set up logging
logger = logging.getLogger('chatbot_core')

# Create your views here.
def home(request):
    logger.debug("Home view called")
    return HttpResponse("Hello, world!")