from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .serializers import UserRegistrationSerializer, UserDetailSerializer, UserProfileSerializer


class UserRegistrationView(generics.CreateAPIView):
    """用户注册"""
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # 生成JWT token
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserDetailSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """用户登录"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'error': '请提供用户名和密码'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(username=username, password=password)
    
    if user is None:
        return Response(
            {'error': '用户名或密码错误'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    if not user.is_active:
        return Response(
            {'error': '账户已被禁用'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # 生成JWT token
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'user': UserDetailSerializer(user).data,
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    })


@api_view(['POST'])
def logout_view(request):
    """用户登出"""
    # JWT是无状态的,客户端删除token即可
    return Response({'message': '登出成功'})


@api_view(['GET', 'PUT'])
def user_profile_view(request):
    """获取/更新用户配置"""
    user = request.user
    
    if request.method == 'GET':
        serializer = UserDetailSerializer(user)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        # 更新用户配置
        profile_serializer = UserProfileSerializer(
            user.profile,
            data=request.data.get('profile', {}),
            partial=True
        )
        
        if profile_serializer.is_valid():
            profile_serializer.save()
            return Response(UserDetailSerializer(user).data)
        
        return Response(
            profile_serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
