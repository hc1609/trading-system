from django.db import models
from django.conf import settings


class RiskStatus(models.Model):
    """风控状态模型"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='risk_status',
        verbose_name='用户'
    )
    date = models.DateField('日期')
    total_capital = models.DecimalField('总资金', max_digits=15, decimal_places=2)
    total_value = models.DecimalField('总市值', max_digits=15, decimal_places=2, null=True, blank=True)
    daily_return = models.DecimalField('当日回撤(%)', max_digits=10, decimal_places=4, null=True, blank=True)
    weekly_return = models.DecimalField('周回撤(%)', max_digits=10, decimal_places=4, null=True, blank=True)
    consecutive_losses = models.IntegerField('连续亏损次数', default=0)
    today_trades = models.IntegerField('今日交易次数', default=0)
    risk_lock = models.BooleanField('风控锁定', default=False)
    lock_reason = models.CharField('锁定原因', max_length=200, null=True, blank=True)
    lock_until = models.DateField('锁定截止日期', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '风控状态'
        verbose_name_plural = verbose_name
        db_table = 'risk_riskstatus'
        unique_together = ['user', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.date} 风控状态 (锁定: {self.risk_lock})"


class RiskLog(models.Model):
    """风控日志模型"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='risk_logs',
        verbose_name='用户'
    )
    date = models.DateField('日期')
    risk_type = models.CharField('风险类型', max_length=30)
    trigger_value = models.DecimalField('触发值', max_digits=10, decimal_places=4, null=True, blank=True)
    action = models.CharField('执行动作', max_length=100)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '风控日志'
        verbose_name_plural = verbose_name
        db_table = 'risk_risklog'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.date} {self.risk_type} - {self.action}"
