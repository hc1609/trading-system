from rest_framework import serializers
from .models import BoxRecord


class BoxRecordSerializer(serializers.ModelSerializer):
    """箱体记录序列化器"""
    class Meta:
        model = BoxRecord
        fields = '__all__'
        read_only_fields = ['height', 'height_rate', 'created_at', 'updated_at']
