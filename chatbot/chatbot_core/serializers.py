from rest_framework import serializers

class ChatRecordSerializer(serializers.ModelSerializer):
    class Meta:
        from .models import ChatRecord
        model = ChatRecord
        fields = '__all__'

class ChatHistorySerializer(serializers.ModelSerializer):
    class Meta:
        from .models import ChatHistory
        model = ChatHistory
        fields = '__all__'
