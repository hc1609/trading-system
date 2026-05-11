#!/bin/bash
# ============================================================
# 交易策略系统 - 单镜像一键部署脚本
# 
# 架构: 单容器(Django+Vue+Celery) + 外部MySQL + 外部Redis
# 
# 用法: sudo bash deploy.sh [命令]
# 命令: install|start|stop|restart|status|logs|update|backup|clean|help
# ============================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

info() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 项目配置
PROJECT_NAME="trading-system"
PROJECT_DIR="/opt/${PROJECT_NAME}"
ENV_FILE="${PROJECT_DIR}/.env"

# 检查root权限
check_root() {
    if [ "$EUID" -ne 0 ]; then
        error "请使用 sudo 运行此脚本"
        exit 1
    fi
}

# 安装Docker
install_docker() {
    if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
        info "Docker已安装"
        docker --version
        docker-compose --version
        return
    fi

    info "安装Docker..."
    yum install -y yum-utils
    yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
    yum install -y docker-ce docker-ce-cli containerd.io
    systemctl start docker
    systemctl enable docker

    # 安装Docker Compose
    curl -L "https://github.com/docker/compose/releases/download/v2.23.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose

    success "Docker安装完成"
}

# 检查外部依赖
check_dependencies() {
    info "检查外部依赖..."
    
    # 检查MySQL
    if ! command -v mysql &> /dev/null && ! docker ps | grep -q mysql; then
        warning "未检测到MySQL,请先安装并启动MySQL"
        warning "  CentOS安装: yum install -y mysql-server && systemctl start mysqld"
        warning "  Docker安装: docker run -d --name mysql -e MYSQL_ROOT_PASSWORD=xxx -p 3306:3306 mysql:8.0"
    fi
    
    # 检查Redis
    if ! command -v redis-cli &> /dev/null && ! docker ps | grep -q redis; then
        warning "未检测到Redis,请先安装并启动Redis"
        warning "  CentOS安装: yum install -y redis && systemctl start redis"
        warning "  Docker安装: docker run -d --name redis -p 6379:6379 redis:7-alpine"
    fi
    
    success "依赖检查完成"
}

# 初始化数据库
init_database() {
    info "初始化数据库..."
    
    read -p "请输入MySQL root密码: " MYSQL_ROOT_PWD
    
    # 创建数据库和用户
    mysql -h localhost -u root -p${MYSQL_ROOT_PWD} << EOF 2>/dev/null || {
        error "连接MySQL失败,请检查密码和MySQL服务状态"
        exit 1
    }
CREATE DATABASE IF NOT EXISTS trading_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'trading'@'%' IDENTIFIED BY 'trading123';
GRANT ALL PRIVILEGES ON trading_system.* TO 'trading'@'%';
FLUSH PRIVILEGES;
EOF

    success "数据库初始化完成"
    info "数据库: trading_system"
    info "用户: trading / trading123"
}

# 设置项目
setup_project() {
    info "设置项目..."
    
    mkdir -p ${PROJECT_DIR}/{logs,media,backups}
    
    # 复制项目文件
    if [ -f "./Dockerfile" ]; then
        cp -r ./* ${PROJECT_DIR}/
    else
        error "未找到项目文件,请在项目根目录运行脚本"
        exit 1
    fi
    
    # 创建环境配置文件
    if [ ! -f "${ENV_FILE}" ]; then
        SECRET_KEY=$(openssl rand -base64 50 | tr -dc 'a-zA-Z0-9' | cut -c1-50)
        
        cat > ${ENV_FILE} << EOF
SECRET_KEY=${SECRET_KEY}
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,*

# 外部MySQL (请根据实际情况修改)
DB_HOST=localhost
DB_PORT=3306
DB_NAME=trading_system
DB_USER=trading
DB_PASSWORD=trading123

# 外部Redis (请根据实际情况修改)
REDIS_HOST=localhost
REDIS_PORT=6379

# Tushare API (可选)
TUSHARE_TOKEN=

# 管理员账号
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123456
ADMIN_EMAIL=admin@example.com
EOF
        success "配置文件已创建: ${ENV_FILE}"
        warning "请务必修改配置文件中的数据库连接信息!"
    fi
}

# 启动服务
start_services() {
    info "启动服务..."
    cd ${PROJECT_DIR}
    docker-compose up -d --build
    
    # 等待服务就绪
    info "等待服务启动 (约30秒)..."
    sleep 30
    
    success "服务启动完成!"
    echo ""
    info "访问地址:"
    echo "  - 应用: http://localhost:8000"
    echo "  - 管理后台: http://localhost:8000/admin/"
    echo ""
    info "默认账号:"
    echo "  - 用户名: admin"
    echo "  - 密码: admin123456"
    echo ""
    info "查看日志: docker logs -f trading-system"
}

# 停止服务
stop_services() {
    info "停止服务..."
    cd ${PROJECT_DIR}
    docker-compose down
    success "服务已停止"
}

# 重启服务
restart_services() {
    info "重启服务..."
    cd ${PROJECT_DIR}
    docker-compose restart
    success "服务已重启"
}

# 查看状态
show_status() {
    cd ${PROJECT_DIR}
    docker-compose ps
}

# 查看日志
show_logs() {
    cd ${PROJECT_DIR}
    docker logs -f --tail=100 trading-system
}

# 更新项目
update_project() {
    info "更新项目..."
    cd ${PROJECT_DIR}
    docker-compose down
    docker-compose up -d --build
    success "项目更新完成"
}

# 备份数据库
backup_database() {
    info "备份数据库..."
    cd ${PROJECT_DIR}
    
    source .env
    BACKUP_FILE="backups/backup_$(date +%Y%m%d_%H%M%S).sql"
    
    mysqldump -h ${DB_HOST} -u ${DB_USER} -p${DB_PASSWORD} ${DB_NAME} > ${BACKUP_FILE}
    
    # 保留最近30天
    find backups -name "backup_*.sql" -mtime +30 -delete
    
    success "备份完成: ${BACKUP_FILE}"
}

# 清理资源
cleanup() {
    info "清理资源..."
    cd ${PROJECT_DIR}
    docker-compose down
    docker image prune -af
    success "清理完成"
}

# 使用帮助
show_help() {
    cat << EOF
交易策略系统 - 单镜像部署脚本

用法: sudo bash deploy.sh [命令]

命令:
  install     安装Docker并部署项目 (首次使用)
  start       启动服务
  stop        停止服务
  restart     重启服务
  status      查看服务状态
  logs        查看应用日志
  update      更新项目并重建
  backup      备份数据库
  clean       清理Docker资源
  help        显示帮助

快速开始:
  1. 准备MySQL和Redis (可Docker或系统安装)
  2. sudo bash deploy.sh install
  3. 修改 .env 配置数据库连接
  4. sudo bash deploy.sh start
  5. 访问 http://localhost:8000

EOF
}

# 主函数
main() {
    case "$1" in
        install)
            check_root
            install_docker
            check_dependencies
            setup_project
            info "请修改 ${ENV_FILE} 配置文件后, 运行: sudo bash deploy.sh start"
            ;;
        start)
            check_root
            start_services
            ;;
        stop)
            check_root
            stop_services
            ;;
        restart)
            check_root
            restart_services
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs
            ;;
        update)
            check_root
            update_project
            ;;
        backup)
            check_root
            backup_database
            ;;
        clean)
            check_root
            cleanup
            ;;
        help|*)
            show_help
            ;;
    esac
}

main "$@"
