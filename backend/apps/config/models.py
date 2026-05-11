from django.db import models
from django.conf import settings


class SystemConfig(models.Model):
    """系统配置模型"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='configs',
        verbose_name='用户'
    )
    config_key = models.CharField('配置键', max_length=50)
    config_value = models.CharField('配置值', max_length=200)
    description = models.CharField('描述', max_length=200, null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '系统配置'
        verbose_name_plural = verbose_name
        db_table = 'config_systemconfig'
        unique_together = ['user', 'config_key']

    def __str__(self):
        return f"{self.config_key} = {self.config_value}"
