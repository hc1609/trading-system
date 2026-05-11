# App configurations

from django.apps import AppConfig


class MarketConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.market'
    verbose_name = '市场数据'


class StrategyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.strategy'
    verbose_name = '策略计算'


class PositionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.position'
    verbose_name = '持仓管理'


class BoxConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.box'
    verbose_name = '箱体分析'


class DaytradeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.daytrade'
    verbose_name = '做T管理'


class RiskConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.risk'
    verbose_name = '风险管理'


class ConfigConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.config'
    verbose_name = '配置管理'


class SyncConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.sync'
    verbose_name = '数据同步'
