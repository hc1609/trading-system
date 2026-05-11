from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    NotificationViewSet,
    TradingReminderViewSet,
    DisciplineLogViewSet,
    get_notifications_summary
)

router = DefaultRouter()
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'reminders', TradingReminderViewSet, basename='tradingreminder')
router.register(r'discipline', DisciplineLogViewSet, basename='disciplinelog')

urlpatterns = [
    path('', include(router.urls)),
    path('summary/', get_notifications_summary, name='notifications-summary'),
]
