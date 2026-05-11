from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserRegistrationView,
    login_view,
    logout_view,
    user_profile_view
)

urlpatterns = [
    # 认证
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # 用户信息
    path('profile/', user_profile_view, name='profile'),
]
