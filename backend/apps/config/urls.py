from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SystemConfigViewSet, reset_config

router = DefaultRouter()
router.register(r'', SystemConfigViewSet, basename='config')

urlpatterns = [
    path('', include(router.urls)),
    path('reset/', reset_config, name='reset-config'),
]
