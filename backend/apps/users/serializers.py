from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile


class UserRegistrationSerializer(serializers.ModelSerializer):
    """用户注册序列化器"""
    password = serializers.CharField(write_only=True, min_length=6)
    email = serializers.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'password', 'email']
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data.get('email', '')
        )
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """用户配置序列化器"""
    class Meta:
        model = UserProfile
        fields = ['total_capital', 'tushare_token', 'theme']
    
    def update(self, instance, validated_data):
        instance.total_capital = validated_data.get('total_capital', instance.total_capital)
        instance.tushare_token = validated_data.get('tushare_token', instance.tushare_token)
        instance.theme = validated_data.get('theme', instance.theme)
        instance.save()
        return instance


class UserDetailSerializer(serializers.ModelSerializer):
    """用户详情序列化器"""
    profile = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'date_joined', 'profile']
        read_only_fields = ['id', 'username', 'email', 'date_joined']
