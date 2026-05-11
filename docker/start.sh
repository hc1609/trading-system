#!/bin/bash
set -e

echo "========================================"
echo "  交易策略系统 - 启动脚本"
echo "========================================"

# 等待数据库就绪
echo "[1/5] 等待数据库连接..."
python -c "
import os
import time
import MySQLdb

host = os.getenv('DB_HOST', 'localhost')
port = int(os.getenv('DB_PORT', 3306))
user = os.getenv('DB_USER', 'trading')
password = os.getenv('DB_PASSWORD', '')

try_count = 0
max_try = 30

while try_count < max_try:
    try:
        conn = MySQLdb.connect(host=host, port=port, user=user, password=password, connect_timeout=5)
        conn.close()
        print('数据库连接成功!')
        break
    except Exception as e:
        try_count += 1
        print(f'等待数据库... ({try_count}/{max_try}): {e}')
        time.sleep(2)
else:
    print('数据库连接超时!')
    exit(1)
"

# 等待Redis就绪
echo "[2/5] 等待Redis连接..."
python -c "
import os
import time
import redis

host = os.getenv('REDIS_HOST', 'localhost')
port = int(os.getenv('REDIS_PORT', 6379))

try_count = 0
max_try = 30

while try_count < max_try:
    try:
        r = redis.Redis(host=host, port=port, socket_connect_timeout=5)
        r.ping()
        print('Redis连接成功!')
        break
    except Exception as e:
        try_count += 1
        print(f'等待Redis... ({try_count}/{max_try}): {e}')
        time.sleep(2)
else:
    print('Redis连接超时!')
    exit(1)
"

# 数据库迁移
echo "[3/5] 执行数据库迁移..."
python manage.py migrate --noinput

# 收集静态文件
echo "[4/5] 收集静态文件..."
python manage.py collectstatic --noinput

# 创建默认超级用户(如果不存在)
echo "[5/5] 检查超级用户..."
python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_system.settings')
import django
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

username = os.getenv('ADMIN_USERNAME', 'admin')
email = os.getenv('ADMIN_EMAIL', 'admin@example.com')
password = os.getenv('ADMIN_PASSWORD', 'admin123456')

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f'超级用户创建成功: {username} / {password}')
else:
    print(f'超级用户已存在: {username}')
"

echo ""
echo "========================================"
echo "  启动所有服务 (Django + Celery)"
echo "========================================"
echo ""

# 启动supervisor管理所有进程
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
