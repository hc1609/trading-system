from django.db import models
from django.conf import settings


class BoxRecord(models.Model):
    """箱体记录模型"""
    STATUS_CHOICES = [
        ('active', '活跃'),
        ('broken_up', '向上突破'),
        ('broken_down', '向下突破'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='boxes',
        verbose_name='用户'
    )
    symbol = models.CharField('股票代码', max_length=20)
    name = models.CharField('股票名称', max_length=50, null=True, blank=True)
    top = models.DecimalField('箱体上沿', max_digits=10, decimal_places=4)
    bottom = models.DecimalField('箱体下沿', max_digits=10, decimal_places=4)
    height = models.DecimalField('箱体高度', max_digits=10, decimal_places=4, null=True, blank=True)
    height_rate = models.DecimalField('箱体高度率(%)', max_digits=10, decimal_places=4, null=True, blank=True)
    bottom_confirm_count = models.IntegerField('底部确认次数', default=1)
    top_confirm_count = models.IntegerField('顶部确认次数', default=1)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '箱体记录'
        verbose_name_plural = verbose_name
        db_table = 'box_boxrecord'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.symbol} 箱体: {self.bottom} - {self.top}"
    
    def save(self, *args, **kwargs):
        """自动计算箱体高度"""
        if self.top and self.bottom:
            self.height = self.top - self.bottom
            if self.bottom > 0:
                self.height_rate = (self.height / self.bottom) * 100
        super().save(*args, **kwargs)
