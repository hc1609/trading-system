"""
URL Configuration for trading_system project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

from .health_check import health_check, readiness_check, liveness_check

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Health checks
    path('health/', health_check, name='health-check'),
    path('ready/', readiness_check, name='readiness-check'),
    path('live/', liveness_check, name='liveness-check'),
    
    # API URLs
    path('api/auth/', include('apps.users.urls')),
    path('api/market/', include('apps.market.urls')),
    path('api/strategy/', include('apps.strategy.urls')),
    path('api/position/', include('apps.position.urls')),
    path('api/box/', include('apps.box.urls')),
    path('api/daytrade/', include('apps.daytrade.urls')),
    path('api/risk/', include('apps.risk.urls')),
    path('api/config/', include('apps.config.urls')),
    path('api/sync/', include('apps.sync.urls')),
    
    # Frontend - Serve Vue app
    path('', TemplateView.as_view(template_name='index.html'), name='index'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
