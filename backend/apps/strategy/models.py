from django.db import models
from django.conf import settings


class MarketState(models.Model):
    """市场状态模型"""
    STATE_CHOICES = [
        ('底部区', '底部区'),
        ('震荡区', '震荡区'),
        ('上涨区', '上涨区'),
        ('陷阱区', '陷阱区'),
    ]
    
    TREND_CHOICES = [
        ('牛市', '牛市'),
        ('震荡', '震荡'),
        ('熊市', '熊市'),
    ]
    
    CYCLE_CHOICES = [
        ('主升浪', '主升浪'),
        ('正常趋势', '正常趋势'),
        ('赶顶期', '赶顶期'),
        ('震荡期', '震荡期'),
        ('下跌期', '下跌期'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='market_states',
        verbose_name='用户'
    )
    date = models.DateField('日期')
    tech_state = models.CharField('技术状态', max_length=20, choices=STATE_CHOICES, null=True, blank=True)
    major_trend = models.CharField('主要趋势', max_length=20, choices=TREND_CHOICES, null=True, blank=True)
    cycle_state = models.CharField('大周期状态', max_length=20, choices=CYCLE_CHOICES, null=True, blank=True)
    event_correction = models.CharField('事件修正', max_length=20, null=True, blank=True)
    final_state = models.CharField('最终状态', max_length=20, null=True, blank=True)
    max_position = models.IntegerField('建议仓位上限(%)', null=True, blank=True)
    etf_action = models.CharField('ETF建议动作', max_length=50, null=True, blank=True)
    individual_action = models.CharField('个股建议动作', max_length=50, null=True, blank=True)
    exit_level = models.IntegerField('离场级别(1/2/3)', null=True, blank=True)
    exit_reason = models.CharField('离场原因', max_length=100, null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '市场状态'
        verbose_name_plural = verbose_name
        db_table = 'strategy_marketstate'
        unique_together = ['user', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.date} - {self.final_state or '未计算'}"


class EventCalendar(models.Model):
    """事件日历模型"""
    EVENT_TYPE_CHOICES = [
        ('政策', '政策窗口'),
        ('财报', '财报季'),
        ('长假', '长假'),
        ('美联储', '美联储议息'),
        ('LPR', 'LPR报价'),
    ]
    
    event_name = models.CharField('事件名称', max_length=100)
    event_type = models.CharField('事件类型', max_length=20, choices=EVENT_TYPE_CHOICES)
    start_date = models.DateField('开始日期')
    end_date = models.DateField('结束日期')
    correction_value = models.DecimalField('修正值', max_digits=5, decimal_places=2, default=0)
    year = models.IntegerField('年份')
    description = models.CharField('描述', max_length=200, null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '事件日历'
        verbose_name_plural = verbose_name
        db_table = 'strategy_eventcalendar'
        ordering = ['start_date']

    def __str__(self):
        return f"{self.event_name} ({self.start_date} ~ {self.end_date})"
