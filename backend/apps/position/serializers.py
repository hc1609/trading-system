from rest_framework import serializers
from .models import Position, Transaction, KeyPointSignal


class PositionSerializer(serializers.ModelSerializer):
    """持仓序列化器"""
    current_value = serializers.ReadOnlyField()
    profit_loss = serializers.SerializerMethodField()
    profit_loss_percent = serializers.SerializerMethodField()
    
    class Meta:
        model = Position
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def get_profit_loss(self, obj):
        """计算盈亏"""
        # 这里需要获取当前价格,暂时返回0
        return 0
    
    def get_profit_loss_percent(self, obj):
        """计算盈亏百分比"""
        return 0


class TransactionSerializer(serializers.ModelSerializer):
    """交易记录序列化器"""
    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = ['created_at']


class KeyPointSignalSerializer(serializers.ModelSerializer):
    """关键点信号序列化器"""
    class Meta:
        model = KeyPointSignal
        fields = '__all__'
        read_only_fields = ['created_at']


class OpenPositionSerializer(serializers.Serializer):
    """开仓请求序列化器"""
    symbol = serializers.CharField(max_length=20)
    name = serializers.CharField(max_length=50)
    buy_price = serializers.DecimalField(max_digits=10, decimal_places=4)
    quantity = serializers.IntegerField()
    stop_loss = serializers.DecimalField(max_digits=10, decimal_places=4, required=False)
    logic = serializers.ChoiceField(choices=['trend', 'box', 'short_term'])
    keypoint_type = serializers.CharField(max_length=30, required=False)


class ClosePositionSerializer(serializers.Serializer):
    """平仓请求序列化器"""
    sell_price = serializers.DecimalField(max_digits=10, decimal_places=4)
    quantity = serializers.IntegerField()
    reason = serializers.CharField(max_length=200, required=False)
