from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MarketStateViewSet,
    EventCalendarViewSet,
    current_market_state,
    active_events,
    calculate_market_state
)

router = DefaultRouter()
router.register(r'states', MarketStateViewSet, basename='marketstate')
router.register(r'events', EventCalendarViewSet, basename='eventcalendar')

urlpatterns = [
    path('', include(router.urls)),
    path('current/', current_market_state, name='current-market-state'),
    path('events/active/', active_events, name='active-events'),
    path('calculate/', calculate_market_state, name='calculate-market-state'),
]
