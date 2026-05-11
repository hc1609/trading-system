# 单镜像部署架构说明

## 概述

采用**单Docker镜像**架构,将Django后端、Vue前端、Celery定时任务全部打包到一个容器中,外部仅依赖MySQL和Redis。

## 架构对比

### 旧架构 (多容器)
```
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│  Nginx   │ │  Django  │ │  Celery  │ │ Celery   │ │  MySQL   │ │  Redis   │
│          │ │          │ │  Worker  │ │  Beat    │ │          │ │          │
└──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘
   6个容器
```

### 新架构 (单容器 + 外部依赖)
```
┌─────────────────────────────────────────┐
│          单容器 (trading-system)         │
│  ┌───────────────────────────────────┐  │
│  │           Supervisor              │  │
│  │  ┌────────┬──────────┬─────────┐ │  │
│  │  │Django  │  Celery  │  Celery │ │  │
│  │  │Gunicorn│  Worker  │  Beat   │ │  │
│  │  │:8000   │          │         │ │  │
│  │  └────────┴──────────┴─────────┘ │  │
│  │                                   │  │
│  │  Vue前端静态文件 (static/dist)     │  │
│  └───────────────────────────────────┘  │
└──────────────────┬──────────────────────┘
                   │ 连接
    ┌──────────────┼──────────────┐
    │              │              │
┌───▼───┐   ┌─────▼────┐  ┌──────▼──────┐
│ MySQL │   │  Redis   │  │   Nginx     │
│ 3306  │   │  6379    │  │  (可选)     │
└───────┘   └──────────┘  └─────────────┘
   1个容器       外部服务      外部服务
```

## 优势

1. **部署简单** - 只需启动一个应用容器
2. **资源占用少** - 减少容器间网络开销
3. **维护方便** - 统一管理日志和配置
4. **外部依赖清晰** - MySQL和Redis可复用现有实例
5. **扩展灵活** - 外部服务可独立扩展

## 文件结构

```
trading-system/
├── Dockerfile                 # 单镜像构建文件
├── docker-compose.yml         # 单服务编排
├── .env.example               # 环境变量模板
├── deploy.sh                  # 一键部署脚本
├── docker/
│   ├── supervisord.conf       # 进程管理配置
│   └── start.sh               # 容器启动脚本
├── backend/                   # Django后端代码
│   ├── requirements.txt
│   └── ...
└── frontend/                  # Vue前端代码
    ├── package.json
    └── ...
```

## 部署步骤

### 1. 准备外部依赖

```bash
# 启动MySQL (Docker)
docker run -d --name mysql \
  -e MYSQL_ROOT_PASSWORD=root123 \
  -e MYSQL_DATABASE=trading_system \
  -e MYSQL_USER=trading \
  -e MYSQL_PASSWORD=trading123 \
  -p 3306:3306 mysql:8.0

# 启动Redis (Docker)
docker run -d --name redis -p 6379:6379 redis:7-alpine
```

### 2. 配置并启动

```bash
# 复制配置
cp .env.example .env
vim .env  # 修改数据库连接信息

# 一键启动
sudo bash deploy.sh start

# 或手动启动
docker-compose up -d --build
```

### 3. 访问应用

- 应用: http://localhost:8000
- 管理后台: http://localhost:8000/admin/

## 进程管理 (Supervisor)

容器内使用Supervisor管理3个进程:

| 进程 | 说明 | 日志 |
|------|------|------|
| django | Gunicorn WSGI服务器 | logs/django_*.log |
| celery-worker | 异步任务处理 | logs/celery_worker.log |
| celery-beat | 定时任务调度 | logs/celery_beat.log |

查看进程状态:
```bash
docker exec trading-system supervisorctl status
```

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| DB_HOST | MySQL主机 | localhost |
| DB_PORT | MySQL端口 | 3306 |
| DB_NAME | 数据库名 | trading_system |
| DB_USER | 数据库用户 | trading |
| DB_PASSWORD | 数据库密码 | - |
| REDIS_HOST | Redis主机 | localhost |
| REDIS_PORT | Redis端口 | 6379 |
| SECRET_KEY | Django密钥 | - |
| ADMIN_PASSWORD | 管理员密码 | admin123456 |

## 日志位置

| 日志 | 路径 |
|------|------|
| 应用日志 | /opt/trading-system/logs/ |
| 容器日志 | docker logs trading-system |

## 更新部署

```bash
# 进入项目目录
cd /opt/trading-system

# 拉取最新代码
git pull

# 重建并启动
docker-compose down
docker-compose up -d --build
```
