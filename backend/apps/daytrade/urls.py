from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DayTradeRecordViewSet, DayTradeStatsViewSet, daytrade_status

router = DefaultRouter()
router.register(r'records', DayTradeRecordViewSet, basename='daytrade-record')
router.register(r'stats', DayTradeStatsViewSet, basename='daytrade-stats')

urlpatterns = [
    path('', include(router.urls)),
    path('status/', daytrade_status, name='daytrade-status'),
]
