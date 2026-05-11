from rest_framework import serializers
from .models import DayTradeRecord, DayTradeStats


class DayTradeRecordSerializer(serializers.ModelSerializer):
    """做T记录序列化器"""
    class Meta:
        model = DayTradeRecord
        fields = '__all__'
        read_only_fields = ['profit_rate', 'success', 'created_at']


class DayTradeStatsSerializer(serializers.ModelSerializer):
    """做T统计序列化器"""
    class Meta:
        model = DayTradeStats
        fields = '__all__'
        read_only_fields = ['created_at']
