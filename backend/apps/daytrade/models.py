from django.db import models
from django.conf import settings


class DayTradeRecord(models.Model):
    """做T记录模型"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='daytrades',
        verbose_name='用户'
    )
    symbol = models.CharField('股票代码', max_length=20)
    buy_price = models.DecimalField('买入价', max_digits=10, decimal_places=4)
    sell_price = models.DecimalField('卖出价', max_digits=10, decimal_places=4)
    profit_rate = models.DecimalField('盈亏率(%)', max_digits=10, decimal_places=4, null=True, blank=True)
    success = models.BooleanField('是否成功', default=False)
    duration_minutes = models.IntegerField('持仓时长(分钟)', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '做T记录'
        verbose_name_plural = verbose_name
        db_table = 'daytrade_daytraderecord'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.symbol} 做T: {self.buy_price} -> {self.sell_price} ({self.profit_rate}%)"
    
    def save(self, *args, **kwargs):
        """自动计算盈亏率"""
        if self.buy_price and self.sell_price and self.buy_price > 0:
            self.profit_rate = ((self.sell_price - self.buy_price) / self.buy_price) * 100
            self.success = self.profit_rate >= 0.5  # 盈利>=0.5%算成功
        super().save(*args, **kwargs)


class DayTradeStats(models.Model):
    """做T统计模型"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='daytrade_stats',
        verbose_name='用户'
    )
    date = models.DateField('统计日期')
    total_count = models.IntegerField('总次数', default=0)
    success_count = models.IntegerField('成功次数', default=0)
    success_rate = models.DecimalField('成功率(%)', max_digits=5, decimal_places=2, default=0)
    consecutive_failures = models.IntegerField('连续失败次数', default=0)
    is_paused = models.BooleanField('是否暂停', default=False)
    pause_reason = models.CharField('暂停原因', max_length=100, null=True, blank=True)
    pause_until = models.DateField('暂停截止日期', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '做T统计'
        verbose_name_plural = verbose_name
        db_table = 'daytrade_daytradestats'
        unique_together = ['user', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.date} 做T统计: {self.success_rate}%"
