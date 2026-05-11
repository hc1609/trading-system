from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from datetime import date
from .models import MarketState, EventCalendar
from .serializers import (
    MarketStateSerializer,
    EventCalendarSerializer,
    ActiveEventSerializer
)


class MarketStatePagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'


class MarketStateViewSet(viewsets.ModelViewSet):
    """市场状态视图集"""
    serializer_class = MarketStateSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = MarketStatePagination
    
    def get_queryset(self):
        user = self.request.user
        queryset = MarketState.objects.filter(user=user)
        
        # 支持过滤
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        return queryset.order_by('-date')


class EventCalendarViewSet(viewsets.ModelViewSet):
    """事件日历视图集"""
    serializer_class = EventCalendarSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = MarketStatePagination
    
    def get_queryset(self):
        queryset = EventCalendar.objects.all()
        
        # 支持过滤
        event_type = self.request.query_params.get('event_type', None)
        year = self.request.query_params.get('year', None)
        
        if event_type:
            queryset = queryset.filter(event_type=event_type)
        if year:
            queryset = queryset.filter(year=year)
        
        return queryset.order_by('start_date')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_market_state(request):
    """获取当前市场状态"""
    user = request.user
    
    # 获取最新的市场状态
    market_state = MarketState.objects.filter(user=user).first()
    
    if not market_state:
        return Response(
            {'error': '暂无市场状态数据,请先计算'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = MarketStateSerializer(market_state)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def active_events(request):
    """获取活跃事件列表"""
    today = date.today()
    
    # 查找当前日期在事件范围内的所有事件
    events = EventCalendar.objects.filter(
        start_date__lte=today,
        end_date__gte=today
    ).order_by('start_date')
    
    serializer = ActiveEventSerializer(events, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def calculate_market_state(request):
    """手动触发市场状态计算"""
    from apps.strategy.services.market_state_calculator import MarketStateCalculator
    from apps.market.models import TechnicalIndicators, MarketData
    from .models import MarketState
    
    user = request.user
    
    try:
        # 获取最新技术指标
        latest_indicator = TechnicalIndicators.objects.select_related('market_data').first()
        
        if not latest_indicator:
            return Response(
                {'error': '暂无技术指标数据,请先同步数据并计算指标'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 计算技术状态
        tech_state = MarketStateCalculator.calculate_tech_state(
            change_20d=float(latest_indicator.change_20d or 0),
            rsi_14=float(latest_indicator.rsi_14 or 50)
        )
        
        # 计算大周期状态
        cycle_state = MarketStateCalculator.calculate_cycle_state(
            change_20d=float(latest_indicator.change_20d or 0),
            rsi_14=float(latest_indicator.rsi_14 or 50),
            has_divergence=latest_indicator.divergence == '顶背离',
            is_above_ma5=bool(latest_indicator.ma_5 and latest_indicator.ma_20),
            is_below_ma60=bool(latest_indicator.ma_60 and latest_indicator.ma_60 > latest_indicator.ma_20)
        )
        
        # 计算事件修正
        from datetime import date
        today = date.today()
        active_events = EventCalendar.objects.filter(
            start_date__lte=today,
            end_date__gte=today
        )
        
        event_list = [{'correction_value': float(e.correction_value), 'priority': 1} for e in active_events]
        event_correction = MarketStateCalculator.calculate_event_correction(event_list)
        
        # 计算最终状态
        final_state = MarketStateCalculator.calculate_final_state(tech_state, event_correction)
        
        # 获取建议仓位
        max_position = MarketStateCalculator.get_max_position(final_state)
        etf_action = MarketStateCalculator.get_etf_action(final_state)
        individual_action = MarketStateCalculator.get_individual_action(final_state)
        
        # 保存或更新市场状态
        market_state, created = MarketState.objects.update_or_create(
            user=user,
            date=today,
            defaults={
                'tech_state': tech_state,
                'major_trend': '牛市',  # 需要实际计算
                'cycle_state': cycle_state,
                'event_correction': str(event_correction),
                'final_state': final_state,
                'max_position': max_position,
                'etf_action': etf_action,
                'individual_action': individual_action,
            }
        )
        
        serializer = MarketStateSerializer(market_state)
        
        return Response({
            'message': '市场状态计算完成',
            'data': serializer.data,
            'created': created
        })
        
    except Exception as e:
        return Response(
            {'error': f'计算失败: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
