from rest_framework import serializers

class ChatHistorySerializer(serializers.ModelSerializer):
    class Meta:
        from .models import ChatHistory
        model = ChatHistory
        fields = '__all__'
