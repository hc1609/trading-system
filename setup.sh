#!/bin/bash
# 交易策略系统 - 快速启动脚本

echo "========================================="
echo "交易策略系统 - 初始化脚本"
echo "========================================="
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到Python3,请先安装Python 3.10+"
    exit 1
fi

echo "✅ Python版本: $(python3 --version)"

# 进入backend目录
cd backend

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 创建Python虚拟环境..."
    python3 -m venv venv
    echo "✅ 虚拟环境创建成功"
else
    echo "✅ 虚拟环境已存在"
fi

# 激活虚拟环境
echo ""
echo "🔄 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo ""
echo "📦 安装Python依赖..."
pip install -q -r requirements.txt
echo "✅ 依赖安装完成"

# 检查.env文件
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  未找到.env文件,从.env.example复制..."
    cp .env.example .env
    echo "✅ 已创建.env文件"
    echo "⚠️  请编辑.env文件,填入实际的配置值(特别是数据库配置和Tushare Token)"
else
    echo "✅ .env文件已存在"
fi

# 创建必要目录
echo ""
echo "📁 创建必要目录..."
mkdir -p logs
mkdir -p static
mkdir -p static/dist
mkdir -p media
mkdir -p templates
echo "✅ 目录创建完成"

# 提示数据库配置
echo ""
echo "========================================="
echo "下一步操作:"
echo "========================================="
echo ""
echo "1. 配置MySQL数据库:"
echo "   - 编辑 .env 文件,填入数据库配置"
echo "   - 创建数据库: CREATE DATABASE trading_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
echo ""
echo "2. 运行数据库迁移:"
echo "   python manage.py makemigrations"
echo "   python manage.py migrate"
echo ""
echo "3. 创建管理员账号:"
echo "   python manage.py createsuperuser"
echo ""
echo "4. 启动开发服务器:"
echo "   python manage.py runserver"
echo ""
echo "5. 访问应用:"
echo "   - API: http://localhost:8000/api/"
echo "   - Admin: http://localhost:8000/admin/"
echo ""
echo "========================================="
echo "初始化完成! 🎉"
echo "========================================="
