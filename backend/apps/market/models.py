from django.db import models


class MarketData(models.Model):
    """市场数据模型 - 存储指数日线数据"""
    date = models.DateField('交易日期')
    index_code = models.CharField('指数代码', max_length=20)
    open = models.DecimalField('开盘价', max_digits=10, decimal_places=4, null=True, blank=True)
    high = models.DecimalField('最高价', max_digits=10, decimal_places=4, null=True, blank=True)
    low = models.DecimalField('最低价', max_digits=10, decimal_places=4, null=True, blank=True)
    close = models.DecimalField('收盘价', max_digits=10, decimal_places=4)
    volume = models.BigIntegerField('成交量', null=True, blank=True)
    amount = models.BigIntegerField('成交额', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '市场数据'
        verbose_name_plural = verbose_name
        db_table = 'market_marketdata'
        unique_together = ['date', 'index_code']
        ordering = ['-date']

    def __str__(self):
        return f"{self.index_code} - {self.date}"


class TechnicalIndicators(models.Model):
    """技术指标模型"""
    market_data = models.OneToOneField(
        MarketData,
        on_delete=models.CASCADE,
        related_name='indicators',
        verbose_name='市场数据'
    )
    change_20d = models.DecimalField('20日涨跌幅(%)', max_digits=10, decimal_places=4, null=True, blank=True)
    rsi_14 = models.DecimalField('14日RSI', max_digits=10, decimal_places=4, null=True, blank=True)
    ma_5 = models.DecimalField('5日均线', max_digits=10, decimal_places=4, null=True, blank=True)
    ma_20 = models.DecimalField('20日均线', max_digits=10, decimal_places=4, null=True, blank=True)
    ma_60 = models.DecimalField('60日均线', max_digits=10, decimal_places=4, null=True, blank=True)
    obv = models.BigIntegerField('OBV值', null=True, blank=True)
    obv_trend = models.CharField('OBV趋势', max_length=20, null=True, blank=True)
    volume_ratio = models.DecimalField('量比', max_digits=10, decimal_places=4, null=True, blank=True)
    divergence = models.CharField('背离状态', max_length=20, default='无')
    macd_dif = models.DecimalField('MACD DIF', max_digits=10, decimal_places=4, null=True, blank=True)
    macd_dea = models.DecimalField('MACD DEA', max_digits=10, decimal_places=4, null=True, blank=True)
    macd_bar = models.DecimalField('MACD柱', max_digits=10, decimal_places=4, null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '技术指标'
        verbose_name_plural = verbose_name
        db_table = 'market_technicalindicators'

    def __str__(self):
        return f"{self.market_data.index_code} - {self.market_data.date} 指标"
