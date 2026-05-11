from rest_framework import viewsets, status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from datetime import date
from .models import Position, Transaction, KeyPointSignal
from .serializers import (
    PositionSerializer,
    TransactionSerializer,
    KeyPointSignalSerializer,
    OpenPositionSerializer,
    ClosePositionSerializer
)


class PositionPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'


class PositionViewSet(viewsets.ModelViewSet):
    """持仓视图集"""
    serializer_class = PositionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PositionPagination
    
    def get_queryset(self):
        user = self.request.user
        queryset = Position.objects.filter(user=user)
        
        # 支持过滤
        position_type = self.request.query_params.get('type', None)
        status_filter = self.request.query_params.get('status', 'holding')
        
        if position_type:
            queryset = queryset.filter(type=position_type)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-buy_date')


class TransactionViewSet(viewsets.ModelViewSet):
    """交易记录视图集"""
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PositionPagination
    
    def get_queryset(self):
        user = self.request.user
        queryset = Transaction.objects.filter(user=user)
        
        # 支持过滤
        position_id = self.request.query_params.get('position_id', None)
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        
        if position_id:
            queryset = queryset.filter(position_id=position_id)
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        return queryset.order_by('-date')


class KeyPointSignalViewSet(viewsets.ModelViewSet):
    """关键点信号视图集"""
    serializer_class = KeyPointSignalSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PositionPagination
    
    def get_queryset(self):
        user = self.request.user
        queryset = KeyPointSignal.objects.filter(user=user)
        
        # 支持过滤
        status_filter = self.request.query_params.get('status', 'pending')
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-date')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def open_position(request):
    """开仓"""
    from apps.position.services.open_position_service import OpenPositionChecker
    from apps.risk.services.risk_manager import RiskManager
    from apps.users.models import UserProfile
    
    serializer = OpenPositionSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    user = request.user
    
    try:
        # 获取用户配置
        profile = user.profile
        
        # 检查开仓条件 (这里简化处理)
        # 实际应该传入更多参数进行完整检查
        
        # 计算止损价(如果未提供)
        stop_loss = serializer.validated_data.get('stop_loss')
        if not stop_loss:
            stop_loss = RiskManager.calculate_stop_loss(
                float(serializer.validated_data['buy_price']),
                stop_loss_percentage=5.0
            )
        
        # 创建持仓
        position = Position.objects.create(
            user=user,
            symbol=serializer.validated_data['symbol'],
            name=serializer.validated_data['name'],
            type='individual',
            logic=serializer.validated_data['logic'],
            buy_date=date.today(),
            buy_price=serializer.validated_data['buy_price'],
            quantity=serializer.validated_data['quantity'],
            stop_loss=stop_loss,
            status='holding'
        )
        
        # 创建交易记录
        amount = float(serializer.validated_data['buy_price']) * serializer.validated_data['quantity']
        Transaction.objects.create(
            user=user,
            position=position,
            date=date.today(),
            direction='buy',
            price=serializer.validated_data['buy_price'],
            quantity=serializer.validated_data['quantity'],
            amount=amount,
            logic_type=serializer.validated_data['logic']
        )
        
        return Response({
            'message': '开仓成功',
            'data': PositionSerializer(position).data
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {'error': f'开仓失败: {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def close_position(request, pk):
    """平仓"""
    position = generics.get_object_or_404(Position, pk=pk, user=request.user)
    
    if position.status != 'holding':
        return Response(
            {'error': '该持仓不是持仓中状态'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    serializer = ClosePositionSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    try:
        sell_price = serializer.validated_data['sell_price']
        quantity = serializer.validated_data['quantity']
        
        # 更新持仓状态
        if quantity >= position.quantity:
            # 全部平仓
            position.status = 'sold'
        else:
            # 部分平仓
            position.quantity -= quantity
        
        position.save()
        
        # 创建交易记录
        amount = float(sell_price) * quantity
        Transaction.objects.create(
            user=request.user,
            position=position,
            date=date.today(),
            direction='sell',
            price=sell_price,
            quantity=quantity,
            amount=amount,
            logic_type=serializer.validated_data.get('reason', 'normal')
        )
        
        return Response({
            'message': '平仓成功',
            'data': PositionSerializer(position).data
        })
        
    except Exception as e:
        return Response(
            {'error': f'平仓失败: {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def etf_recommendation(request):
    """获取ETF操作建议"""
    from apps.position.services.etf_service import ETFStrategy
    from apps.strategy.models import MarketState
    
    # 获取最新市场状态
    market_state = MarketState.objects.filter(user=request.user).first()
    
    if not market_state:
        return Response(
            {'error': '暂无市场状态数据'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # 获取ETF建议
    etf_action = ETFStrategy.get_etf_action(
        market_state.final_state or '震荡区',
        market_state.cycle_state or ''
    )
    
    return Response({
        'market_state': market_state.final_state,
        'cycle_state': market_state.cycle_state,
        'recommendation': etf_action
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def position_summary(request):
    """获取持仓汇总"""
    user = request.user
    
    # 统计持仓
    holding_positions = Position.objects.filter(user=user, status='holding')
    
    total_value = sum(p.current_value for p in holding_positions)
    etf_count = holding_positions.filter(type='etf').count()
    individual_count = holding_positions.filter(type='individual').count()
    
    return Response({
        'total_positions': holding_positions.count(),
        'etf_count': etf_count,
        'individual_count': individual_count,
        'total_value': total_value,
        'positions': PositionSerializer(holding_positions, many=True).data
    })
