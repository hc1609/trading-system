from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RiskStatusViewSet, RiskLogViewSet, current_risk_status, reset_risk

router = DefaultRouter()
router.register(r'status', RiskStatusViewSet, basename='risk-status')
router.register(r'logs', RiskLogViewSet, basename='risk-log')

urlpatterns = [
    path('', include(router.urls)),
    path('current/', current_risk_status, name='current-risk-status'),
    path('reset/', reset_risk, name='reset-risk'),
]
