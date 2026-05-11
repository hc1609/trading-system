from rest_framework import serializers
from .models import MarketData, TechnicalIndicators


class MarketDataSerializer(serializers.ModelSerializer):
    """市场数据序列化器"""
    class Meta:
        model = MarketData
        fields = '__all__'
        read_only_fields = ['created_at']


class TechnicalIndicatorsSerializer(serializers.ModelSerializer):
    """技术指标序列化器"""
    class Meta:
        model = TechnicalIndicators
        fields = '__all__'
        read_only_fields = ['created_at']


class MarketDataWithIndicatorsSerializer(serializers.ModelSerializer):
    """市场数据带技术指标"""
    indicators = TechnicalIndicatorsSerializer(read_only=True)
    
    class Meta:
        model = MarketData
        fields = '__all__'
