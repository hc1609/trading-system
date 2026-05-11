from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """用户配置模型"""
    THEME_CHOICES = [
        ('light', '浅色主题'),
        ('dark', '深色主题'),
    ]
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='用户'
    )
    total_capital = models.DecimalField(
        '总资金',
        max_digits=15,
        decimal_places=2,
        default=100000.00
    )
    tushare_token = models.CharField(
        'Tushare Token',
        max_length=100,
        blank=True,
        null=True
    )
    theme = models.CharField(
        '主题',
        max_length=20,
        choices=THEME_CHOICES,
        default='light'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '用户配置'
        verbose_name_plural = verbose_name
        db_table = 'users_userprofile'

    def __str__(self):
        return f"{self.user.username}的配置"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    """自动创建用户配置"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    """保存用户配置"""
    instance.profile.save()
