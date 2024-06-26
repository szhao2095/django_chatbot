from rest_framework import serializers

class ChatRecordSerializer(serializers.ModelSerializer):
    class Meta:
        from .models import Thread
        model = Thread
        fields = ['unique_id', 'thread_id']

# class ChatHistorySerializer(serializers.ModelSerializer):
#     class Meta:
#         from .models import ChatHistory
#         model = ChatHistory
#         fields = '__all__'
