"""
Views for notifications and reminders.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Notification, TradingReminder, DisciplineLog
from .serializers import (
    NotificationSerializer,
    TradingReminderSerializer,
    DisciplineLogSerializer
)
from .services.notification_service import (
    NotificationService,
    TradingReminderService,
    DisciplineCheckService
)


class NotificationViewSet(viewsets.ModelViewSet):
    """通知视图集"""
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')
    
    @action(detail=False, methods=['get'])
    def unread(self, request):
        """获取未读通知"""
        notifications = NotificationService.get_unread_notifications(request.user)
        serializer = self.get_serializer(notifications, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """标记为已读"""
        success = NotificationService.mark_as_read(pk)
        return Response({'success': success})
    
    @action(detail=True, methods=['post'])
    def dismiss(self, request, pk=None):
        """忽略通知"""
        success = NotificationService.dismiss_notification(pk)
        return Response({'success': success})


class TradingReminderViewSet(viewsets.ModelViewSet):
    """交易提醒视图集"""
    serializer_class = TradingReminderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return TradingReminder.objects.filter(user=self.request.user).order_by('reminder_time')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def create_defaults(self, request):
        """创建默认提醒"""
        reminders = TradingReminderService.create_default_reminders(request.user)
        serializer = self.get_serializer(reminders, many=True)
        return Response({
            'message': f'创建了 {len(reminders)} 个默认提醒',
            'data': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """获取当前启用的提醒"""
        reminders = TradingReminderService.get_active_reminders(request.user)
        serializer = self.get_serializer(reminders, many=True)
        return Response(serializer.data)


class DisciplineLogViewSet(viewsets.ModelViewSet):
    """纪律记录视图集"""
    serializer_class = DisciplineLogSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return DisciplineLog.objects.filter(user=self.request.user).order_by('-check_date')
    
    @action(detail=False, methods=['post'])
    def run_check(self, request):
        """运行纪律检查"""
        results = DisciplineCheckService.run_daily_discipline_check(request.user)
        return Response({
            'message': '纪律检查完成',
            'results': results
        })
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """获取纪律执行汇总"""
        days = int(request.query_params.get('days', 7))
        summary = DisciplineCheckService.get_discipline_summary(request.user, days)
        return Response(summary)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_notifications_summary(request):
    """获取通知汇总"""
    user = request.user
    
    # 未读通知数
    unread_count = Notification.objects.filter(
        user=user,
        is_read=False,
        is_dismissed=False
    ).count()
    
    # 今日纪律检查结果
    today_violations = DisciplineLog.objects.filter(
        user=user,
        check_date=date.today(),
        is_followed=False
    ).count()
    
    # 今日提醒数
    today_reminders = Notification.objects.filter(
        user=user,
        created_at__date=date.today()
    ).count()
    
    return Response({
        'unread_notifications': unread_count,
        'today_violations': today_violations,
        'today_reminders': today_reminders,
    })


# Import for action decorator
from rest_framework.decorators import action
from datetime import date
