"""
Serializers for notifications and reminders.
"""

from rest_framework import serializers
from .models import Notification, TradingReminder, DisciplineLog


class NotificationSerializer(serializers.ModelSerializer):
    """通知序列化器"""
    created_at_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ['created_at', 'read_at']
    
    def get_created_at_formatted(self, obj):
        return obj.created_at.strftime('%Y-%m-%d %H:%M:%S')


class TradingReminderSerializer(serializers.ModelSerializer):
    """交易提醒序列化器"""
    reminder_time_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = TradingReminder
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def get_reminder_time_formatted(self, obj):
        return obj.reminder_time.strftime('%H:%M')


class DisciplineLogSerializer(serializers.ModelSerializer):
    """纪律记录序列化器"""
    status_display = serializers.SerializerMethodField()
    
    class Meta:
        model = DisciplineLog
        fields = '__all__'
        read_only_fields = ['created_at']
    
    def get_status_display(self, obj):
        return '✅ 遵守' if obj.is_followed else '❌ 违反'
