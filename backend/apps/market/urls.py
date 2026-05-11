from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MarketDataViewSet,
    TechnicalIndicatorsViewSet,
    latest_market_data,
    calculate_indicators
)

router = DefaultRouter()
router.register(r'data', MarketDataViewSet, basename='marketdata')
router.register(r'indicators', TechnicalIndicatorsViewSet, basename='indicators')

urlpatterns = [
    path('', include(router.urls)),
    path('latest/', latest_market_data, name='latest-market-data'),
    path('calculate/', calculate_indicators, name='calculate-indicators'),
]
