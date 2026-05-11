from django.db import models
from django.conf import settings


class Position(models.Model):
    """持仓模型"""
    TYPE_CHOICES = [
        ('etf', 'ETF'),
        ('individual', '个股'),
    ]
    
    LOGIC_CHOICES = [
        ('trend', '趋势'),
        ('box', '箱体'),
        ('short_term', '短线'),
    ]
    
    STATUS_CHOICES = [
        ('holding', '持仓中'),
        ('selling', '卖出中'),
        ('sold', '已平仓'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='positions',
        verbose_name='用户'
    )
    symbol = models.CharField('代码', max_length=20)
    name = models.CharField('名称', max_length=50)
    type = models.CharField('类型', max_length=20, choices=TYPE_CHOICES, default='individual')
    logic = models.CharField('逻辑', max_length=20, choices=LOGIC_CHOICES, default='trend')
    buy_date = models.DateField('买入日期')
    buy_price = models.DecimalField('买入价', max_digits=10, decimal_places=4)
    quantity = models.IntegerField('数量')
    stop_loss = models.DecimalField('止损价', max_digits=10, decimal_places=4, null=True, blank=True)
    target_price = models.DecimalField('目标价', max_digits=10, decimal_places=4, null=True, blank=True)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='holding')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '持仓'
        verbose_name_plural = verbose_name
        db_table = 'position_position'
        ordering = ['-buy_date']

    def __str__(self):
        return f"{self.symbol} - {self.name} ({self.type})"
    
    @property
    def current_value(self):
        """当前市值(需要实时价格,这里返回买入价值)"""
        return self.buy_price * self.quantity


class Transaction(models.Model):
    """交易记录模型"""
    DIRECTION_CHOICES = [
        ('buy', '买入'),
        ('sell', '卖出'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='transactions',
        verbose_name='用户'
    )
    position = models.ForeignKey(
        Position,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transactions',
        verbose_name='关联持仓'
    )
    date = models.DateField('交易日期')
    direction = models.CharField('方向', max_length=10, choices=DIRECTION_CHOICES)
    price = models.DecimalField('成交价', max_digits=10, decimal_places=4)
    quantity = models.IntegerField('数量')
    amount = models.DecimalField('金额', max_digits=15, decimal_places=2)
    fee = models.DecimalField('手续费', max_digits=10, decimal_places=4, default=0)
    logic_type = models.CharField('逻辑类型', max_length=50, null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '交易记录'
        verbose_name_plural = verbose_name
        db_table = 'position_transaction'
        ordering = ['-date']

    def __str__(self):
        return f"{self.position.symbol} {self.direction} {self.quantity}股 @ {self.price}"


class KeyPointSignal(models.Model):
    """关键点信号模型"""
    KEYPOINT_TYPE_CHOICES = [
        ('突破关键点', '突破关键点'),
        ('自然回撤关键点', '自然回撤关键点'),
        ('连续关键点', '连续关键点'),
        ('反转关键点', '反转关键点'),
    ]
    
    STRENGTH_CHOICES = [
        ('强', '强'),
        ('中', '中'),
        ('弱', '弱'),
    ]
    
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('acted', '已处理'),
        ('expired', '已过期'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='keypoint_signals',
        verbose_name='用户'
    )
    symbol = models.CharField('股票代码', max_length=20)
    date = models.DateField('信号日期')
    keypoint_type = models.CharField('关键点类型', max_length=30, choices=KEYPOINT_TYPE_CHOICES)
    strength = models.CharField('强度', max_length=10, choices=STRENGTH_CHOICES)
    price = models.DecimalField('信号价格', max_digits=10, decimal_places=4)
    volume_ratio = models.DecimalField('量比', max_digits=10, decimal_places=4, null=True, blank=True)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '关键点信号'
        verbose_name_plural = verbose_name
        db_table = 'position_keypoint_signal'
        ordering = ['-date']

    def __str__(self):
        return f"{self.symbol} - {self.keypoint_type} ({self.strength})"
