from django.urls import path
from . import views

urlpatterns = [
    path('create-new-chat/', views.CreateNewChat.as_view(), name='create-new-chat'),
    path('send-message/', views.SendMessageView.as_view(), name='send-message'),
]
