"""
Notification service for trading reminders and discipline alerts.
"""

import logging
from datetime import date, datetime, time
from typing import List, Dict, Optional

from django.contrib.auth.models import User
from apps.sync.models import Notification, TradingReminder, DisciplineLog
from apps.strategy.models import MarketState
from apps.risk.models import RiskStatus
from apps.position.models import Position

logger = logging.getLogger(__name__)


class NotificationService:
    """通知服务"""
    
    @staticmethod
    def create_notification(
        user: User,
        title: str,
        message: str,
        notification_type: str = 'system',
        show_popup: bool = True,
        popup_duration: int = 5
    ) -> Notification:
        """创建通知消息"""
        notification = Notification.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type=notification_type,
            show_popup=show_popup,
            popup_duration=popup_duration
        )
        logger.info(f"Created notification for user {user.id}: {title}")
        return notification
    
    @staticmethod
    def get_unread_notifications(user: User) -> List[Notification]:
        """获取用户未读通知"""
        return Notification.objects.filter(
            user=user,
            is_read=False,
            is_dismissed=False
        ).order_by('-created_at')[:20]
    
    @staticmethod
    def mark_as_read(notification_id: int) -> bool:
        """标记通知为已读"""
        try:
            notification = Notification.objects.get(id=notification_id)
            notification.is_read = True
            notification.read_at = datetime.now()
            notification.save()
            return True
        except Notification.DoesNotExist:
            return False
    
    @staticmethod
    def dismiss_notification(notification_id: int) -> bool:
        """忽略通知"""
        try:
            notification = Notification.objects.get(id=notification_id)
            notification.is_dismissed = True
            notification.save()
            return True
        except Notification.DoesNotExist:
            return False
    
    @staticmethod
    def clear_old_notifications(user: User, days: int = 30) -> int:
        """清理旧通知"""
        from datetime import timedelta
        cutoff_date = datetime.now() - timedelta(days=days)
        
        deleted_count = Notification.objects.filter(
            user=user,
            created_at__lt=cutoff_date
        ).delete()[0]
        
        logger.info(f"Cleared {deleted_count} old notifications for user {user.id}")
        return deleted_count


class TradingReminderService:
    """交易提醒服务"""
    
    # 默认提醒配置
    DEFAULT_REMINDERS = [
        {
            'reminder_type': 'pre_market',
            'reminder_time': time(8, 30),
            'title': '盘前准备',
            'message': '📋 今日交易检查清单:\n1. 查看市场状态\n2. 检查持仓止损位\n3. 确认今日策略',
            'show_popup': True,
            'play_sound': True,
        },
        {
            'reminder_type': 'market_open',
            'reminder_time': time(9, 30),
            'title': '开盘提醒',
            'message': '🔔 市场已开盘!\n请查看今日市场状态和建议仓位。',
            'show_popup': True,
            'play_sound': True,
        },
        {
            'reminder_type': 'noon_review',
            'reminder_time': time(11, 30),
            'title': '午间复盘',
            'message': '📊 上午交易复盘:\n1. 检查持仓盈亏\n2. 关注下午计划\n3. 严格遵守止损',
            'show_popup': True,
            'play_sound': False,
        },
        {
            'reminder_type': 'market_close',
            'reminder_time': time(15, 0),
            'title': '收盘提醒',
            'message': '🔔 市场即将收盘!\n请检查今日交易记录和持仓状态。',
            'show_popup': True,
            'play_sound': True,
        },
        {
            'reminder_type': 'stop_loss_check',
            'reminder_time': time(10, 0),
            'title': '止损检查',
            'message': '⚠️ 止损纪律检查:\n1. 检查所有持仓是否触发止损\n2. 严格执行止损纪律\n3. 不要抱有侥幸心理',
            'show_popup': True,
            'play_sound': True,
        },
    ]
    
    @staticmethod
    def create_default_reminders(user: User) -> List[TradingReminder]:
        """为用户创建默认提醒"""
        reminders = []
        
        for reminder_data in TradingReminderService.DEFAULT_REMINDERS:
            reminder, created = TradingReminder.objects.get_or_create(
                user=user,
                reminder_type=reminder_data['reminder_type'],
                defaults={
                    'reminder_time': reminder_data['reminder_time'],
                    'title': reminder_data['title'],
                    'message': reminder_data['message'],
                    'show_popup': reminder_data['show_popup'],
                    'play_sound': reminder_data['play_sound'],
                }
            )
            
            if created:
                reminders.append(reminder)
                logger.info(f"Created default reminder for user {user.id}: {reminder.title}")
        
        return reminders
    
    @staticmethod
    def get_active_reminders(user: User) -> List[TradingReminder]:
        """获取用户启用的提醒"""
        today = date.today()
        weekday = today.isoweekday()  # 1=Monday, 7=Sunday
        
        return TradingReminder.objects.filter(
            user=user,
            is_enabled=True,
            repeat_days__contains=str(weekday)
        ).order_by('reminder_time')
    
    @staticmethod
    def check_and_send_reminders() -> Dict:
        """检查并发送当前时间应触发的提醒"""
        now = datetime.now()
        current_time = now.time()
        today = now.date()
        weekday = today.isoweekday()
        
        sent_count = 0
        users = User.objects.filter(is_active=True)
        
        for user in users:
            try:
                # Get reminders that should trigger now (within 1 minute window)
                reminders = TradingReminder.objects.filter(
                    user=user,
                    is_enabled=True,
                    repeat_days__contains=str(weekday)
                )
                
                for reminder in reminders:
                    reminder_datetime = datetime.combine(today, reminder.reminder_time)
                    time_diff = abs((datetime.combine(today, current_time) - reminder_datetime).total_seconds())
                    
                    # Check if within 1 minute window and not already sent today
                    if time_diff <= 60:
                        # Check if already sent today
                        existing = Notification.objects.filter(
                            user=user,
                            title=reminder.title,
                            created_at__date=today
                        ).exists()
                        
                        if not existing:
                            # Create notification
                            NotificationService.create_notification(
                                user=user,
                                title=reminder.title,
                                message=reminder.message,
                                notification_type='system',
                                show_popup=reminder.show_popup,
                                popup_duration=5
                            )
                            sent_count += 1
                            
            except Exception as e:
                logger.error(f"Error sending reminders for user {user.id}: {str(e)}")
                continue
        
        logger.info(f"Sent {sent_count} reminders")
        return {"status": "success", "sent_count": sent_count}


class DisciplineCheckService:
    """纪律检查服务"""
    
    DISCIPLINE_ITEMS = [
        {
            'check_item': '止损纪律',
            'description': '所有持仓都设置了止损位,且严格执行止损',
        },
        {
            'check_item': '仓位控制',
            'description': '总仓位不超过建议仓位上限',
        },
        {
            'check_item': '不做T规则',
            'description': '非震荡区不做T,连续2次失败暂停做T',
        },
        {
            'check_item': '金字塔加仓',
            'description': '加仓时严格遵守金字塔比例(2:1.5:1)',
        },
        {
            'check_item': '趋势判断',
            'description': '只做上升趋势中的个股,不碰下降趋势',
        },
        {
            'check_item': '信息关注',
            'description': '关注宏观信息和持仓个股公告',
        },
    ]
    
    @staticmethod
    def check_position_discipline(user: User) -> List[Dict]:
        """检查持仓纪律"""
        results = []
        
        # Check stop losses
        positions = Position.objects.filter(user=user, status='holding')
        
        for position in positions:
            has_stop_loss = position.stop_loss is not None and position.stop_loss > 0
            
            results.append({
                'check_item': f'{position.name} 止损设置',
                'description': f'持仓 {position.name} {"已" if has_stop_loss else "未"}设置止损',
                'is_followed': has_stop_loss,
                'position_id': position.id,
            })
        
        return results
    
    @staticmethod
    def check_risk_discipline(user: User) -> List[Dict]:
        """检查风控纪律"""
        results = []
        
        # Get today's risk status
        risk_status = RiskStatus.objects.filter(user=user, date=date.today()).first()
        
        if risk_status:
            # Check daily return
            if risk_status.daily_return is not None:
                is_safe = risk_status.daily_return > -3
                results.append({
                    'check_item': '日回撤控制',
                    'description': f'日回撤 {risk_status.daily_return}%, {"未" if not is_safe else ""}超过3%限制',
                    'is_followed': is_safe,
                })
            
            # Check consecutive losses
            if risk_status.consecutive_losses is not None:
                is_safe = risk_status.consecutive_losses < 3
                results.append({
                    'check_item': '连续亏损控制',
                    'description': f'连续亏损 {risk_status.consecutive_losses} 次, {"未" if not is_safe else ""}超过3次限制',
                    'is_followed': is_safe,
                })
        
        return results
    
    @staticmethod
    def run_daily_discipline_check(user: User) -> List[Dict]:
        """运行每日纪律检查"""
        all_results = []
        
        # Check position discipline
        position_results = DisciplineCheckService.check_position_discipline(user)
        all_results.extend(position_results)
        
        # Check risk discipline
        risk_results = DisciplineCheckService.check_risk_discipline(user)
        all_results.extend(risk_results)
        
        # Log results
        today = date.today()
        for result in all_results:
            DisciplineLog.objects.create(
                user=user,
                check_item=result['check_item'],
                description=result['description'],
                is_followed=result['is_followed'],
                check_date=today
            )
            
            # Send notification for violations
            if not result['is_followed']:
                NotificationService.create_notification(
                    user=user,
                    title=f'⚠️ 纪律警告: {result["check_item"]}',
                    message=result['description'],
                    notification_type='risk_alert',
                    show_popup=True,
                    popup_duration=10
                )
        
        logger.info(f"Completed discipline check for user {user.id}: {len(all_results)} items")
        return all_results
    
    @staticmethod
    def get_discipline_summary(user: User, days: int = 7) -> Dict:
        """获取纪律执行汇总"""
        from datetime import timedelta
        
        start_date = date.today() - timedelta(days=days)
        
        logs = DisciplineLog.objects.filter(
            user=user,
            check_date__gte=start_date
        )
        
        total_checks = logs.count()
        followed_count = logs.filter(is_followed=True).count()
        violation_count = logs.filter(is_followed=False).count()
        
        follow_rate = (followed_count / total_checks * 100) if total_checks > 0 else 100
        
        return {
            'total_checks': total_checks,
            'followed_count': followed_count,
            'violation_count': violation_count,
            'follow_rate': round(follow_rate, 2),
            'period_days': days,
        }
