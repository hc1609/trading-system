# 交易策略系统 - CentOS Docker单镜像部署文档

## 概述

本文档介绍如何在CentOS服务器上使用**单Docker镜像**部署交易策略系统。

**架构特点**:
- **单容器**: Django后端 + Vue前端 + Celery定时任务
- **外部依赖**: MySQL + Redis (需自行准备)
- **可选**: Nginx反向代理

## 系统要求

### 硬件要求

| 配置 | 最低要求 | 推荐配置 |
|------|----------|----------|
| CPU | 2核 | 4核+ |
| 内存 | 2GB | 4GB+ |
| 磁盘 | 20GB SSD | 50GB+ SSD |
| 网络 | 10Mbps | 100Mbps+ |

### 软件要求

- CentOS 7/8/Stream 或兼容的RHEL系统
- Docker 20.10+
- Docker Compose 2.0+
- MySQL 5.7+ 或 8.0+
- Redis 5.0+

## 快速部署 (三步完成)

### 第一步: 准备MySQL和Redis

选择以下任一方式:

**方式A: 使用Docker快速启动**
```bash
# 启动MySQL
docker run -d --name mysql \
  -e MYSQL_ROOT_PASSWORD=root123 \
  -e MYSQL_DATABASE=trading_system \
  -e MYSQL_USER=trading \
  -e MYSQL_PASSWORD=trading123 \
  -p 3306:3306 \
  mysql:8.0 \
  --character-set-server=utf8mb4 \
  --collation-server=utf8mb4_unicode_ci

# 启动Redis
docker run -d --name redis \
  -p 6379:6379 \
  redis:7-alpine
```

**方式B: 使用系统服务**
```bash
# CentOS安装MySQL
yum install -y mysql-server
systemctl start mysqld
systemctl enable mysqld

# 创建数据库和用户
mysql -u root -p << EOF
CREATE DATABASE trading_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'trading'@'%' IDENTIFIED BY 'trading123';
GRANT ALL PRIVILEGES ON trading_system.* TO 'trading'@'%';
FLUSH PRIVILEGES;
EOF

# CentOS安装Redis
yum install -y redis
systemctl start redis
systemctl enable redis
```

### 第二步: 上传并配置项目

```bash
# 上传项目到服务器
scp -r trading-system root@your-server:/opt/

# 进入项目目录
cd /opt/trading-system

# 创建环境配置文件
cp .env.example .env

# 编辑配置 (必须修改数据库连接信息!)
vim .env
```

`.env` 示例:
```env
SECRET_KEY=your-random-secret-key
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

# 外部MySQL配置
DB_HOST=localhost
DB_PORT=3306
DB_NAME=trading_system
DB_USER=trading
DB_PASSWORD=trading123

# 外部Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379

# 管理员账号
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-admin-password
ADMIN_EMAIL=admin@example.com
```

### 第三步: 启动服务

```bash
# 使用部署脚本一键启动
sudo bash deploy.sh start

# 或直接使用Docker Compose
docker-compose up -d --build
```

访问系统:
- 应用: `http://your-server-ip:8000`
- 管理后台: `http://your-server-ip:8000/admin/`

## 单镜像架构说明

```
┌─────────────────────────────────────────────┐
│           单容器 (trading-system)            │
│  ┌─────────────────────────────────────┐    │
│  │           Supervisor                │    │
│  │  ┌─────────┬──────────┬──────────┐ │    │
│  │  │ Django  │  Celery  │  Celery  │ │    │
│  │  │ Gunicorn│  Worker  │  Beat    │ │    │
│  │  │ :8000   │          │          │ │    │
│  │  └─────────┴──────────┴──────────┘ │    │
│  │                                     │    │
│  │  Vue前端静态文件 (static/dist)      │    │
│  └─────────────────────────────────────┘    │
└──────────────────┬──────────────────────────┘
                   │ 连接
    ┌──────────────┼──────────────┐
    │              │              │
┌───▼───┐   ┌─────▼────┐  ┌──────▼──────┐
│ MySQL │   │  Redis   │  │   Nginx     │
│ 3306  │   │  6379    │  │  (可选)     │
└───────┘   └──────────┘  └─────────────┘
```

## 部署脚本命令

```bash
# 一键安装 (首次部署)
sudo bash deploy.sh install

# 启动服务
sudo bash deploy.sh start

# 停止服务
sudo bash deploy.sh stop

# 重启服务
sudo bash deploy.sh restart

# 查看状态
sudo bash deploy.sh status

# 查看日志
sudo bash deploy.sh logs

# 备份数据库
sudo bash deploy.sh backup

# 更新项目
sudo bash deploy.sh update

# 清理资源
sudo bash deploy.sh clean
```

## 使用Nginx反向代理 (推荐生产环境)

### 安装配置Nginx

```bash
# CentOS安装Nginx
yum install -y nginx
systemctl start nginx
systemctl enable nginx

# 编辑配置文件
vim /etc/nginx/conf.d/trading-system.conf
```

### Nginx配置

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # 前端静态文件
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # API和Admin
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    
    location /admin/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # 静态文件缓存
    location /static/ {
        proxy_pass http://127.0.0.1:8000;
        expires 7d;
        add_header Cache-Control "public";
    }
    
    # Gzip压缩
    gzip on;
    gzip_types text/plain text/css application/json application/javascript;
}
```

### 重启Nginx

```bash
nginx -t
systemctl restart nginx
```

## SSL/HTTPS配置 (Let's Encrypt)

```bash
# 安装Certbot
yum install -y certbot python3-certbot-nginx

# 申请证书
certbot --nginx -d your-domain.com

# 自动续期
certbot renew --dry-run
```

## 日志管理

### 查看应用日志

```bash
# 实时查看日志
docker logs -f trading-system

# 查看最新100行
docker logs --tail=100 trading-system

# 查看日志文件
tail -f /opt/trading-system/logs/*.log
```

### 日志文件说明

| 日志文件 | 说明 |
|----------|------|
| `logs/django_out.log` | Django标准输出 |
| `logs/django_err.log` | Django错误日志 |
| `logs/gunicorn_access.log` | Gunicorn访问日志 |
| `logs/gunicorn_error.log` | Gunicorn错误日志 |
| `logs/celery_worker.log` | Celery Worker日志 |
| `logs/celery_beat.log` | Celery Beat日志 |

## 数据备份与恢复

### 自动备份

可以配置crontab定时备份:
```bash
# 编辑crontab
crontab -e

# 每天凌晨2点备份
0 2 * * * cd /opt/trading-system && bash deploy.sh backup
```

### 手动备份

```bash
# 使用脚本备份
bash deploy.sh backup

# 或手动备份
mysqldump -h localhost -u trading -p trading_system > backup_$(date +%Y%m%d).sql
```

### 恢复数据

```bash
# 恢复数据库
mysql -h localhost -u trading -p trading_system < backup_20240101.sql
```

## 性能优化

### Gunicorn调优

编辑 `docker/supervisord.conf`:
```ini
[program:django]
command=gunicorn trading_system.wsgi:application 
    --bind 0.0.0.0:8000 
    --workers 4              # CPU核心数 x 2 + 1
    --worker-class sync
    --timeout 120
    --max-requests 1000      # 防止内存泄漏
    --max-requests-jitter 50
```

### MySQL调优

```ini
[mysqld]
innodb_buffer_pool_size = 1G
max_connections = 200
query_cache_size = 64M
```

## 常见问题

### 1. 数据库连接失败

```bash
# 检查MySQL状态
systemctl status mysqld

# 检查端口
telnet localhost 3306

# 检查用户权限
mysql -u root -p -e "SHOW GRANTS FOR 'trading'@'%';"
```

### 2. Redis连接失败

```bash
# 检查Redis状态
systemctl status redis

# 测试连接
redis-cli ping
```

### 3. 端口被占用

```bash
# 检查端口占用
netstat -tlnp | grep 8000

# 修改端口映射 (docker-compose.yml)
ports:
  - "8080:8000"
```

### 4. 内存不足

```bash
# 添加Swap分区
dd if=/dev/zero of=/swapfile bs=1G count=2
mkswap /swapfile
swapon /swapfile
```

### 5. 静态文件404

```bash
# 重新收集静态文件
docker exec trading-system python manage.py collectstatic --noinput

# 重启容器
docker restart trading-system
```

## 系统服务配置

### 设置为systemd服务

```bash
# 创建服务文件
cat > /etc/systemd/system/trading-system.service << 'EOF'
[Unit]
Description=Trading System
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/trading-system
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
ExecReload=/usr/local/bin/docker-compose restart

[Install]
WantedBy=multi-user.target
EOF

# 启用服务
systemctl daemon-reload
systemctl enable trading-system
systemctl start trading-system
```

## 更新项目

```bash
# 进入项目目录
cd /opt/trading-system

# 拉取最新代码
git pull

# 重建并启动
docker-compose down
docker-compose up -d --build
```

## 安全建议

1. **修改默认密码**: 立即修改admin密码
2. **配置防火墙**: 只开放80/443端口
3. **使用HTTPS**: 生产环境必须启用SSL
4. **定期备份**: 数据库定时备份到远程
5. **更新系统**: 及时更新Docker镜像和系统补丁

## 联系支持

如有问题,请查看:
- [项目文档](./README.md)
- [API文档](./API_DOCUMENTATION.md)

---

**单镜像部署完成!** 🎉

现在您的交易策略系统已经打包为单个Docker镜像,可以轻松部署到任何支持Docker的环境。
