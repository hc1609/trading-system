"""
Models for sync and notification system.
"""

from django.db import models
from django.contrib.auth.models import User


class Notification(models.Model):
    """通知消息模型"""
    NOTIFICATION_TYPES = [
        ('market_open', '开盘提醒'),
        ('market_close', '收盘提醒'),
        ('stop_loss', '止损提醒'),
        ('risk_alert', '风控提醒'),
        ('position_alert', '持仓提醒'),
        ('system', '系统通知'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', verbose_name='用户')
    title = models.CharField('标题', max_length=100)
    message = models.TextField('内容')
    notification_type = models.CharField('类型', max_length=20, choices=NOTIFICATION_TYPES)
    
    # 状态
    is_read = models.BooleanField('是否已读', default=False)
    is_dismissed = models.BooleanField('是否已忽略', default=False)
    
    # 弹窗设置
    show_popup = models.BooleanField('是否弹窗', default=True)
    popup_duration = models.IntegerField('弹窗持续时间(秒)', default=5)
    
    # 时间
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    read_at = models.DateTimeField('阅读时间', null=True, blank=True)
    
    class Meta:
        verbose_name = '通知消息'
        verbose_name_plural = '通知消息'
        ordering = ['-created_at']
        db_table = 'sync_notifications'
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"


class TradingReminder(models.Model):
    """交易纪律提醒配置"""
    REMINDER_TYPES = [
        ('pre_market', '盘前提醒'),
        ('market_open', '开盘提醒'),
        ('noon_review', '午间复盘'),
        ('market_close', '收盘提醒'),
        ('stop_loss_check', '止损检查'),
        ('position_review', '持仓复盘'),
        ('weekly_review', '周末复盘'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trading_reminders', verbose_name='用户')
    reminder_type = models.CharField('提醒类型', max_length=20, choices=REMINDER_TYPES)
    
    # 提醒时间
    reminder_time = models.TimeField('提醒时间')
    
    # 提醒内容
    title = models.CharField('标题', max_length=100)
    message = models.TextField('提醒内容')
    
    # 状态
    is_enabled = models.BooleanField('是否启用', default=True)
    
    # 提醒方式
    show_popup = models.BooleanField('弹窗提醒', default=True)
    play_sound = models.BooleanField('声音提醒', default=True)
    
    # 重复设置
    repeat_days = models.CharField('重复日期', max_length=20, default='1,2,3,4,5', 
                                   help_text='1=周一, 2=周二, ..., 7=周日')
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '交易提醒'
        verbose_name_plural = '交易提醒'
        ordering = ['reminder_time']
        db_table = 'sync_trading_reminders'
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"


class DisciplineLog(models.Model):
    """纪律执行记录"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='discipline_logs', verbose_name='用户')
    
    # 检查项
    check_item = models.CharField('检查项', max_length=100)
    description = models.TextField('描述')
    
    # 执行状态
    is_followed = models.BooleanField('是否遵守', default=True)
    violation_reason = models.TextField('违反原因', blank=True)
    
    # 时间
    check_date = models.DateField('检查日期')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '纪律记录'
        verbose_name_plural = '纪律记录'
        ordering = ['-check_date']
        db_table = 'sync_discipline_logs'
    
    def __str__(self):
        return f"{self.user.username} - {self.check_item} - {self.check_date}"
