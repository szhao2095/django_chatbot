import json, hashlib
from django.db import models

class AssistantInfo(models.Model):
    hash = models.CharField(max_length=64, unique=True)
    info = models.JSONField()

    @classmethod
    def get_or_create(cls, info):
        info_str = json.dumps(info, sort_keys=True)
        info_hash = hashlib.sha256(info_str.encode('utf-8')).hexdigest()
        assistant_info, created = cls.objects.get_or_create(hash=info_hash, defaults={'info': info})
        return assistant_info


class VectorStoreInfo(models.Model):
    hash = models.CharField(max_length=64, unique=True)
    info = models.JSONField()

    @classmethod
    def get_or_create(cls, info):
        info_str = json.dumps(info, sort_keys=True)
        info_hash = hashlib.sha256(info_str.encode('utf-8')).hexdigest()
        vector_store_info, created = cls.objects.get_or_create(hash=info_hash, defaults={'info': info})
        return vector_store_info


class ChatRecord(models.Model):
    unique_id = models.CharField(max_length=100, unique=True)
    thread_id = models.CharField(max_length=255)
    assistant_id = models.CharField(max_length=255)
    vector_store_id = models.CharField(max_length=255)
    assistant_info_hash = models.CharField(max_length=64)
    vector_store_info_hash = models.CharField(max_length=64)
    timestamp = models.DateTimeField(auto_now_add=True)

    def set_assistant_info(self, info):
        assistant_info = AssistantInfo.get_or_create(info)
        self.assistant_info_hash = assistant_info.hash

    def get_assistant_info(self):
        try:
            assistant_info = AssistantInfo.objects.get(hash=self.assistant_info_hash)
            return assistant_info.info
        except AssistantInfo.DoesNotExist:
            return None

    def set_vector_store_info(self, info):
        vector_store_info = VectorStoreInfo.get_or_create(info)
        self.vector_store_info_hash = vector_store_info.hash

    def get_vector_store_info(self):
        try:
            vector_store_info = VectorStoreInfo.objects.get(hash=self.vector_store_info_hash)
            return vector_store_info.info
        except VectorStoreInfo.DoesNotExist:
            return None
class ChatHistory(models.Model):
    unique_id = models.CharField(max_length=100)
    user_message = models.TextField()
    response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)