from django.db import models

# Create your models here.
class ChatHistory(models.Model):
    user_id = models.CharField(max_length=255)  # If no login, use session ID or IP address
    message = models.TextField()
    response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)