from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import SystemConfig
from .serializers import SystemConfigSerializer


class SystemConfigViewSet(viewsets.ModelViewSet):
    """系统配置视图集"""
    serializer_class = SystemConfigSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return SystemConfig.objects.filter(user=user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reset_config(request):
    """重置为默认配置"""
    # 删除用户的所有配置
    SystemConfig.objects.filter(user=request.user).delete()
    
    # 创建默认配置
    default_configs = [
        {'config_key': 'bottom_threshold', 'config_value': '-8', 'description': '底部区跌幅阈值(%)'},
        {'config_key': 'bottom_rsi', 'config_value': '35', 'description': '底部区RSI阈值'},
        {'config_key': 'stop_loss_rate', 'config_value': '5', 'description': '固定止损率(%)'},
        {'config_key': 'per_trade_risk', 'config_value': '2', 'description': '单笔风险限额(%)'},
    ]
    
    for config_data in default_configs:
        SystemConfig.objects.create(user=request.user, **config_data)
    
    return Response({'message': '已重置为默认配置'})
