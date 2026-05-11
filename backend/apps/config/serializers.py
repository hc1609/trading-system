from rest_framework import serializers
from .models import SystemConfig


class SystemConfigSerializer(serializers.ModelSerializer):
    """系统配置序列化器"""
    class Meta:
        model = SystemConfig
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
