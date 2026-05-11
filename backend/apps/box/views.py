from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from .models import BoxRecord
from .serializers import BoxRecordSerializer


class BoxPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'


class BoxRecordViewSet(viewsets.ModelViewSet):
    """箱体记录视图集"""
    serializer_class = BoxRecordSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = BoxPagination
    
    def get_queryset(self):
        user = self.request.user
        queryset = BoxRecord.objects.filter(user=user)
        
        # 支持过滤
        symbol = self.request.query_params.get('symbol', None)
        status_filter = self.request.query_params.get('status', 'active')
        
        if symbol:
            queryset = queryset.filter(symbol=symbol)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-created_at')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def box_analysis(request, pk):
    """获取箱体分析"""
    from apps.box.services.box_analyzer import BoxAnalyzer
    
    box = BoxRecord.objects.get(pk=pk, user=request.user)
    
    # 获取当前位置(需要当前价格,这里简化处理)
    # 实际应该传入current_price
    
    return Response({
        'box': BoxRecordSerializer(box).data,
        'message': '需要传入当前价格以获取详细分析'
    })
