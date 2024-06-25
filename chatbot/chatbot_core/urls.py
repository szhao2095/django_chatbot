from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('chat/', views.ChatAPIView.as_view(), name='chat'),
]
