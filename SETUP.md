# 交易策略系统 - 快速启动指南

## 前置要求

- Python 3.10+
- MySQL 8.0+
- Redis 6.0+
- Node.js 18+
- npm 或 yarn

## 后端安装步骤

### 1. 创建虚拟环境
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
# 或
venv\Scripts\activate  # Windows
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

注意: TA-Lib需要先安装C库:
```bash
# Mac
brew install ta-lib

# Ubuntu
sudo apt-get install -y ta-lib

# 或者使用纯Python替代方案
pip install pandas-ta
```

### 3. 配置环境变量
```bash
cp .env.example .env
# 编辑.env文件,填入实际的配置值
```

### 4. 创建数据库
```sql
CREATE DATABASE trading_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 5. 数据库迁移
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. 创建超级用户
```bash
python manage.py createsuperuser
```

### 7. 运行开发服务器
```bash
python manage.py runserver
```

## 前端安装步骤

### 1. 安装依赖
```bash
cd frontend
npm install
```

### 2. 运行开发服务器
```bash
npm run dev
```

### 3. 构建生产版本
```bash
npm run build
# 构建产物将输出到 ../backend/static/dist/
```

## Celery配置

### 启动Celery Worker
```bash
cd backend
celery -A trading_system worker -l info
```

### 启动Celery Beat(定时任务)
```bash
celery -A trading_system beat -l info
```

## 访问地址

- 后端API: http://localhost:8000/api/
- 前端开发: http://localhost:5173
- Django Admin: http://localhost:8000/admin/

## 开发注意事项

1. **数据库**: 确保MySQL服务已启动
2. **Redis**: 确保Redis服务已启动(Celery需要)
3. **Tushare Token**: 需要在配置中设置有效的Tushare Token才能同步数据
4. **时区**: 系统使用Asia/Shanghai时区

## 常见问题

### Q: 数据库连接失败
A: 检查MySQL服务是否启动,.env中的数据库配置是否正确

### Q: Celery无法连接Redis
A: 检查Redis服务是否启动,Celery配置是否正确

### Q: TA-Lib安装失败
A: 先安装TA-Lib的C库,或使用pandas-ta替代

## 下一步

完成基础安装后,系统已经包含:
- ✅ 用户认证模块(注册、登录、JWT)
- ✅ 数据库模型结构
- ✅ API基础框架

接下来需要:
1. 完善其他业务模块的Models和API
2. 实现核心业务逻辑(技术指标计算、策略判断等)
3. 开发前端页面
4. 配置定时任务

详见项目设计文档。
