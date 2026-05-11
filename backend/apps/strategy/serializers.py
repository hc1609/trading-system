from rest_framework import serializers
from .models import MarketState, EventCalendar


class MarketStateSerializer(serializers.ModelSerializer):
    """市场状态序列化器"""
    class Meta:
        model = MarketState
        fields = '__all__'
        read_only_fields = ['created_at']


class EventCalendarSerializer(serializers.ModelSerializer):
    """事件日历序列化器"""
    class Meta:
        model = EventCalendar
        fields = '__all__'
        read_only_fields = ['created_at']


class ActiveEventSerializer(serializers.ModelSerializer):
    """活跃事件序列化器"""
    days_remaining = serializers.SerializerMethodField()
    
    class Meta:
        model = EventCalendar
        fields = ['id', 'event_name', 'event_type', 'start_date', 'end_date', 
                 'correction_value', 'description', 'days_remaining']
    
    def get_days_remaining(self, obj):
        from datetime import date
        if obj.end_date >= date.today():
            return (obj.end_date - date.today()).days
        return 0
