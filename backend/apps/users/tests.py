"""
Tests for user authentication and profile.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status


class UserRegistrationTestCase(APITestCase):
    """用户注册测试"""
    
    def test_register_success(self):
        """测试成功注册"""
        data = {
            'username': 'testuser',
            'password': 'test123456',
            'email': 'test@example.com'
        }
        
        response = self.client.post('/api/auth/register/', data)
        
        # 检查响应状态码
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 检查用户是否创建
        user = User.objects.filter(username='testuser').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'test@example.com')
    
    def test_register_duplicate_username(self):
        """测试重复用户名注册"""
        # 先创建一个用户
        User.objects.create_user(
            username='testuser',
            password='test123456'
        )
        
        # 尝试重复注册
        data = {
            'username': 'testuser',
            'password': 'test123456',
            'email': 'test2@example.com'
        }
        
        response = self.client.post('/api/auth/register/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_register_invalid_data(self):
        """测试无效数据注册"""
        data = {
            'username': '',  # 空用户名
            'password': '123',  # 密码太短
        }
        
        response = self.client.post('/api/auth/register/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserLoginTestCase(APITestCase):
    """用户登录测试"""
    
    def setUp(self):
        """创建测试用户"""
        self.user = User.objects.create_user(
            username='testuser',
            password='test123456',
            email='test@example.com'
        )
    
    def test_login_success(self):
        """测试成功登录"""
        data = {
            'username': 'testuser',
            'password': 'test123456'
        }
        
        response = self.client.post('/api/auth/login/', data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
    
    def test_login_invalid_password(self):
        """测试密码错误"""
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        
        response = self.client.post('/api/auth/login/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_login_nonexistent_user(self):
        """测试用户不存在"""
        data = {
            'username': 'nonexistent',
            'password': 'test123456'
        }
        
        response = self.client.post('/api/auth/login/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserProfileTestCase(APITestCase):
    """用户资料测试"""
    
    def setUp(self):
        """创建测试用户并登录"""
        self.user = User.objects.create_user(
            username='testuser',
            password='test123456',
            email='test@example.com'
        )
        
        # 登录获取Token
        response = self.client.post('/api/auth/login/', {
            'username': 'testuser',
            'password': 'test123456'
        })
        
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
    
    def test_get_profile(self):
        """测试获取用户信息"""
        response = self.client.get('/api/auth/profile/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
    
    def test_get_profile_unauthorized(self):
        """测试未认证获取用户信息"""
        self.client.credentials()  # 清除认证
        
        response = self.client.get('/api/auth/profile/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_update_profile(self):
        """测试更新用户配置"""
        data = {
            'profile': {
                'total_capital': 200000,
                'risk_preference': 'conservative'
            }
        }
        
        response = self.client.put('/api/auth/profile/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UserModelTestCase(TestCase):
    """用户模型测试"""
    
    def test_user_creation(self):
        """测试用户创建"""
        user = User.objects.create_user(
            username='testuser',
            password='test123456',
            email='test@example.com'
        )
        
        self.assertIsNotNone(user.id)
        self.assertEqual(user.username, 'testuser')
        self.assertTrue(user.check_password('test123456'))
        self.assertFalse(user.is_staff)
        self.assertTrue(user.is_active)
    
    def test_superuser_creation(self):
        """测试超级用户创建"""
        admin = User.objects.create_superuser(
            username='admin',
            password='admin123',
            email='admin@example.com'
        )
        
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
