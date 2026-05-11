from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PositionViewSet,
    TransactionViewSet,
    KeyPointSignalViewSet,
    open_position,
    close_position,
    etf_recommendation,
    position_summary
)

router = DefaultRouter()
router.register(r'positions', PositionViewSet, basename='position')
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'keypoints', KeyPointSignalViewSet, basename='keypoint')

urlpatterns = [
    path('', include(router.urls)),
    path('open/', open_position, name='open-position'),
    path('<int:pk>/close/', close_position, name='close-position'),
    path('etf/recommendation/', etf_recommendation, name='etf-recommendation'),
    path('summary/', position_summary, name='position-summary'),
]
