from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from datetime import date
from .models import RiskStatus, RiskLog
from .serializers import RiskStatusSerializer, RiskLogSerializer


class RiskPagination(PageNumberPagination):
    page_size = 30
    page_size_query_param = 'page_size'


class RiskStatusViewSet(viewsets.ModelViewSet):
    """风控状态视图集"""
    serializer_class = RiskStatusSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = RiskPagination
    
    def get_queryset(self):
        user = self.request.user
        return RiskStatus.objects.filter(user=user).order_by('-date')


class RiskLogViewSet(viewsets.ModelViewSet):
    """风控日志视图集"""
    serializer_class = RiskLogSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = RiskPagination
    
    def get_queryset(self):
        user = self.request.user
        return RiskLog.objects.filter(user=user).order_by('-created_at')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_risk_status(request):
    """获取当前风控状态"""
    risk_status = RiskStatus.objects.filter(user=request.user).first()
    
    if not risk_status:
        return Response(
            {'error': '暂无风控状态数据'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    return Response(RiskStatusSerializer(risk_status).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reset_risk(request):
    """重置风控状态"""
    risk_status = RiskStatus.objects.filter(user=request.user).first()
    
    if risk_status:
        risk_status.risk_lock = False
        risk_status.lock_reason = ''
        risk_status.lock_until = None
        risk_status.consecutive_losses = 0
        risk_status.today_trades = 0
        risk_status.save()
    
    return Response({'message': '风控状态已重置'})
