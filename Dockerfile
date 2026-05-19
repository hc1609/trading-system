# ============================================================
# 交易策略系统 - 应用镜像
# 包含: Django后端 + Vue前端 + Celery定时任务
# 外部依赖: MySQL + Redis (需外部提供)
# ============================================================

FROM python:3.11-slim as frontend-builder

# 安装Node.js
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# 构建前端
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm install --production=false
COPY frontend/ .
RUN npm run build

# ============================================================
# 最终运行镜像
# ============================================================
FROM python:3.11-slim

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DJANGO_SETTINGS_MODULE=trading_system.settings \
    TZ=Asia/Shanghai

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmariadb3 \
    curl \
    supervisor \
    cron \
    gcc \
    build-essential \
    wget \
    && rm -rf /var/lib/apt/lists/* \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone

# 手动编译安装 TA-Lib C 库 (使用GitHub镜像)
RUN wget -q https://github.com/TA-Lib/ta-lib/releases/download/v0.4.0/ta-lib-0.4.0-src.tar.gz -O ta-lib.tar.gz && \
    tar -xzf ta-lib.tar.gz && \
    cd ta-lib/ && \
    ./configure --prefix=/usr && \
    make -j$(nproc) && \
    make install && \
    cd .. && \
    rm -rf ta-lib ta-lib.tar.gz && \
    ldconfig

# 设置工作目录
WORKDIR /app

# 复制并安装Python依赖
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn supervisor

# 复制后端代码
COPY backend/ .

# 从前端构建阶段复制静态文件
COPY --from=frontend-builder /frontend/dist ./static/dist

# 创建必要的目录
RUN mkdir -p /app/logs /app/media /var/log/supervisor /var/run

# 复制supervisor配置
COPY docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# 复制启动脚本
COPY docker/start.sh /start.sh
RUN chmod +x /start.sh

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["/start.sh"]
