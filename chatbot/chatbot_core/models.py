from django.db import models

class ChatRecord(models.Model):
    unique_id = models.CharField(max_length=100, unique=True)
    thread_id = models.CharField(max_length=255)
    assistant_id = models.CharField(max_length=255)
    vector_store_id = models.CharField(max_length=255)


# class ChatHistory(models.Model):
#     user_id = models.CharField(max_length=255)
#     message = models.TextField()
#     response = models.TextField()
#     timestamp = models.DateTimeField(auto_now_add=True)