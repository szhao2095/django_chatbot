import json
from django.db import models

class ChatRecord(models.Model):
    unique_id = models.CharField(max_length=100, unique=True)
    thread_id = models.CharField(max_length=255)
    assistant_id = models.CharField(max_length=255)
    vector_store_id = models.CharField(max_length=255)
    assistant_info = models.JSONField()
    vector_store_info = models.JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def set_assistant_info(self, info):
        self.assistant_info = json.dumps(info)
    
    def get_assistant_info(self):
        return json.loads(self.assistant_info)
    
    def set_vector_store_info(self, info):
        self.vector_store_info = json.dumps(info)
    
    def get_vector_store_info(self):
        return json.loads(self.vector_store_info)

class ChatHistory(models.Model):
    unique_id = models.CharField(max_length=100)
    user_message = models.TextField()
    response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)