from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from .models import DayTradeRecord, DayTradeStats
from .serializers import DayTradeRecordSerializer, DayTradeStatsSerializer


class DayTradePagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'


class DayTradeRecordViewSet(viewsets.ModelViewSet):
    """做T记录视图集"""
    serializer_class = DayTradeRecordSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DayTradePagination
    
    def get_queryset(self):
        user = self.request.user
        return DayTradeRecord.objects.filter(user=user).order_by('-created_at')


class DayTradeStatsViewSet(viewsets.ModelViewSet):
    """做T统计视图集"""
    serializer_class = DayTradeStatsSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DayTradePagination
    
    def get_queryset(self):
        user = self.request.user
        return DayTradeStats.objects.filter(user=user).order_by('-date')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def daytrade_status(request):
    """获取做T状态"""
    from apps.daytrade.services.daytrade_manager import DayTradeManager
    from apps.strategy.models import MarketState
    
    # 获取市场状态
    market_state = MarketState.objects.filter(user=request.user).first()
    
    # 获取做T统计
    stats = DayTradeStats.objects.filter(user=request.user).first()
    
    allowed = False
    reason = ''
    
    if market_state and stats:
        check_result = DayTradeManager.check_daytrade_allowed(
            market_state=market_state.final_state or '震荡区',
            risk_status={'risk_lock': False},
            daytrade_stats={
                'is_paused': stats.is_paused,
                'pause_until': stats.pause_until,
                'consecutive_failures': stats.consecutive_failures
            }
        )
        allowed = check_result['allowed']
        reason = check_result['reason']
    
    return Response({
        'allowed': allowed,
        'reason': reason,
        'stats': DayTradeStatsSerializer(stats).data if stats else None
    })
