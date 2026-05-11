from rest_framework import viewsets, status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from .models import MarketData, TechnicalIndicators
from .serializers import (
    MarketDataSerializer,
    TechnicalIndicatorsSerializer,
    MarketDataWithIndicatorsSerializer
)


class MarketDataPagination(PageNumberPagination):
    page_size = 30
    page_size_query_param = 'page_size'
    max_page_size = 100


class MarketDataViewSet(viewsets.ModelViewSet):
    """市场数据视图集"""
    serializer_class = MarketDataWithIndicatorsSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = MarketDataPagination
    
    def get_queryset(self):
        queryset = MarketData.objects.all()
        
        # 支持过滤
        index_code = self.request.query_params.get('index_code', None)
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        
        if index_code:
            queryset = queryset.filter(index_code=index_code)
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        return queryset.order_by('-date')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return MarketDataSerializer
        return MarketDataWithIndicatorsSerializer


class TechnicalIndicatorsViewSet(viewsets.ModelViewSet):
    """技术指标视图集"""
    serializer_class = TechnicalIndicatorsSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = MarketDataPagination
    
    def get_queryset(self):
        queryset = TechnicalIndicators.objects.select_related('market_data')
        
        # 支持过滤
        index_code = self.request.query_params.get('index_code', None)
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        
        if index_code:
            queryset = queryset.filter(market_data__index_code=index_code)
        if start_date:
            queryset = queryset.filter(market_data__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(market_data__date__lte=end_date)
        
        return queryset.order_by('-market_data__date')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def latest_market_data(request):
    """获取最新市场数据"""
    index_code = request.query_params.get('index_code', '399006.SZ')
    
    market_data = MarketData.objects.filter(index_code=index_code).first()
    
    if not market_data:
        return Response(
            {'error': '未找到市场数据'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = MarketDataWithIndicatorsSerializer(market_data)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def calculate_indicators(request):
    """手动触发指标计算"""
    from apps.market.services.technical_indicator_calculator import TechnicalIndicatorCalculator
    
    # 这里可以实现批量计算逻辑
    return Response({
        'message': '指标计算任务已提交',
        'status': 'processing'
    })
