#!/bin/bash
# Dockerfile 本地验证脚本

set -e

echo "========================================="
echo "  Dockerfile 本地验证"
echo "========================================="

# 1. 检查必需文件是否存在
echo ""
echo "[1/5] 检查必需文件..."

files=(
    "Dockerfile"
    "docker-compose.yml"
    "docker/start.sh"
    "docker/supervisord.conf"
    "backend/requirements.txt"
    "backend/manage.py"
    "backend/trading_system/settings.py"
    "frontend/package.json"
    "frontend/vite.config.js"
    "frontend/index.html"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ✗ $file (缺失)"
        exit 1
    fi
done

# 2. 检查Dockerfile语法
echo ""
echo "[2/5] 检查Dockerfile语法..."

if grep -q "FROM python:3.11-slim as frontend-builder" Dockerfile; then
    echo "  ✓ 多阶段构建配置正确"
else
    echo "  ✗ 多阶段构建配置错误"
    exit 1
fi

if grep -q "COPY --from=frontend-builder" Dockerfile; then
    echo "  ✓ 前端构建产物复制配置正确"
else
    echo "  ✗ 前端构建产物复制配置错误"
    exit 1
fi

# 3. 检查COPY路径
echo ""
echo "[3/5] 检查COPY路径..."

# 检查backend目录
if [ -d "backend" ]; then
    echo "  ✓ backend/ 目录存在"
    file_count=$(find backend -type f | wc -l)
    echo "    包含 $file_count 个文件"
else
    echo "  ✗ backend/ 目录缺失"
    exit 1
fi

# 检查frontend目录
if [ -d "frontend" ]; then
    echo "  ✓ frontend/ 目录存在"
    file_count=$(find frontend -type f -not -path "*/node_modules/*" | wc -l)
    echo "    包含 $file_count 个文件 (不含node_modules)"
else
    echo "  ✗ frontend/ 目录缺失"
    exit 1
fi

# 检查docker目录
if [ -d "docker" ]; then
    echo "  ✓ docker/ 目录存在"
else
    echo "  ✗ docker/ 目录缺失"
    exit 1
fi

# 4. 检查.gitignore
echo ""
echo "[4/5] 检查.gitignore配置..."

if [ -f ".gitignore" ]; then
    if grep -q "node_modules" .gitignore; then
        echo "  ✓ node_modules 已忽略"
    fi
    if grep -q "dist/" .gitignore; then
        echo "  ✓ frontend/dist/ 已忽略"
    fi
    if grep -q ".env" .gitignore; then
        echo "  ✓ .env 已忽略"
    fi
else
    echo "  ⚠ .gitignore 文件缺失"
fi

# 5. 检查Dockerfile中的潜在问题
echo ""
echo "[5/5] 检查Dockerfile潜在问题..."

# 检查TA-Lib安装
if grep -q "ta-lib" Dockerfile; then
    echo "  ✓ TA-Lib 编译安装配置"
else
    echo "  ⚠ TA-Lib 配置缺失 (requirements.txt中有TA-Lib依赖)"
fi

# 检查healthcheck
if grep -q "HEALTHCHECK" Dockerfile; then
    echo "  ✓ Health check 配置"
else
    echo "  ⚠ Health check 配置缺失"
fi

# 检查EXPOSE
if grep -q "EXPOSE 8000" Dockerfile; then
    echo "  ✓ 端口暴露配置"
else
    echo "  ⚠ 端口暴露配置缺失"
fi

# 总结
echo ""
echo "========================================="
echo "  验证完成!"
echo "========================================="
echo ""
echo "Dockerfile 构建流程:"
echo "  1. [frontend-builder] 安装Node.js → npm install → npm run build"
echo "  2. [main] 安装系统依赖 → 编译TA-Lib → 安装Python依赖"
echo "  3. [main] 复制后端代码 → 复制前端dist → 配置Supervisor"
echo "  4. [main] 启动容器 → start.sh → Supervisor → Django+Celery"
echo ""
echo "下一步:"
echo "  - 启动Docker Desktop"
echo "  - 运行: docker build -t trading-system:test ."
echo "  - 测试运行: docker run -p 8000:8000 trading-system:test"
echo ""
