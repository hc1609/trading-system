"""
Celery configuration for trading_system project.
"""

import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_system.settings')

app = Celery('trading_system')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery Beat Schedule
app.conf.beat_schedule = {
    'sync_market_data_9am': {
        'task': 'apps.sync.tasks.sync_daily_market_data',
        'schedule': crontab(hour=9, minute=0),
    },
    'sync_market_data_3pm': {
        'task': 'apps.sync.tasks.sync_daily_market_data',
        'schedule': crontab(hour=15, minute=30),
    },
    'calculate_technical_indicators': {
        'task': 'apps.sync.tasks.calculate_all_indicators',
        'schedule': 300.0,  # 每5分钟
    },
    'calculate_market_state': {
        'task': 'apps.sync.tasks.calculate_market_state_for_all_users',
        'schedule': 600.0,  # 每10分钟
    },
    'check_risk_limits': {
        'task': 'apps.sync.tasks.check_risk_limits',
        'schedule': 300.0,  # 每5分钟
    },
    'cleanup_old_data': {
        'task': 'apps.sync.tasks.cleanup_old_data',
        'schedule': crontab(hour=2, minute=0),  # 每天凌晨2点
    },
}


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task to verify Celery is working."""
    print(f'Request: {self.request!r}')
