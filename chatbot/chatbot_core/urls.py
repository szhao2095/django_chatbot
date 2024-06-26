from django.urls import path
from . import views

urlpatterns = [
    path('create-or-validate-token/', views.CreateOrValidateTokenView.as_view(), name='create-or-validate-token'),
]
