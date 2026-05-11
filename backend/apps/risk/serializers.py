from rest_framework import serializers
from .models import RiskStatus, RiskLog


class RiskStatusSerializer(serializers.ModelSerializer):
    """风控状态序列化器"""
    class Meta:
        model = RiskStatus
        fields = '__all__'
        read_only_fields = ['created_at']


class RiskLogSerializer(serializers.ModelSerializer):
    """风控日志序列化器"""
    class Meta:
        model = RiskLog
        fields = '__all__'
        read_only_fields = ['created_at']
