from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BoxRecordViewSet, box_analysis

router = DefaultRouter()
router.register(r'', BoxRecordViewSet, basename='box')

urlpatterns = [
    path('', include(router.urls)),
    path('<int:pk>/analysis/', box_analysis, name='box-analysis'),
]
