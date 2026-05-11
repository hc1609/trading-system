# 快速启动指南

## 环境要求

- Python 3.8+
- Node.js 16+
- MySQL 8.0+
- Redis 6.0+ (可选,用于Celery)

---

## 一、后端启动

### 1. 安装 Python 依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置数据库

创建 MySQL 数据库:
```sql
CREATE DATABASE trading_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'trading'@'localhost' IDENTIFIED BY 'trading123';
GRANT ALL PRIVILEGES ON trading_system.* TO 'trading'@'localhost';
FLUSH PRIVILEGES;
```

编辑 `.env` 文件:
```bash
cp .env.example .env
# 编辑 .env 文件,配置数据库连接
```

### 3. 数据库迁移

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. 创建超级用户

```bash
python manage.py createsuperuser
# 输入用户名、邮箱、密码
```

### 5. 启动后端服务

```bash
python manage.py runserver
```

访问: http://localhost:8000/admin (Django Admin)

---

## 二、前端启动 (开发模式)

### 1. 安装 Node 依赖

```bash
cd frontend
npm install
```

### 2. 启动开发服务器

```bash
npm run dev
```

访问: http://localhost:5173

**注意**: 开发模式下,前端会自动代理 API 请求到后端 (http://localhost:8000)

---

## 三、生产部署

### 1. 构建前端

```bash
cd frontend
npm run build
```

构建产物将输出到 `backend/static/dist` 目录。

### 2. 配置 Django 静态文件

确保 `settings.py` 中配置了:
```python
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
```

### 3. 收集静态文件

```bash
cd backend
python manage.py collectstatic
```

### 4. 启动 Django (提供前端+API)

```bash
python manage.py runserver
```

访问: http://localhost:8000

---

## 四、测试流程

### 1. 注册/登录

1. 访问 http://localhost:5173 (开发) 或 http://localhost:8000 (生产)
2. 点击"立即注册"
3. 填写用户名、邮箱、密码
4. 注册成功后自动登录

### 2. 查看市场状态

1. 登录后进入看板页面
2. 点击"市场状态"卡片的"计算"按钮
3. 查看市场状态、建议仓位、操作建议

### 3. 开仓操作

1. 点击"持仓列表"右上角的"开仓"按钮
2. 填写股票代码、名称、价格、数量
3. 选择交易逻辑 (趋势/箱体/短线)
4. 点击"确认开仓"

### 4. 查看持仓

1. 持仓列表显示所有持仓中股票
2. 查看成本价、数量、止损价
3. 点击"平仓"按钮进行平仓操作

### 5. 刷新数据

点击右上角"刷新数据"按钮,刷新所有数据。

---

## 五、常见问题

### Q1: 前端无法连接后端?

**A**: 检查:
1. 后端是否正常运行 (http://localhost:8000)
2. 前端代理配置是否正确 (`vite.config.js`)
3. CORS 配置是否添加 (`settings.py`)

### Q2: 数据库迁移失败?

**A**: 
```bash
# 删除迁移文件后重新生成
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
python manage.py makemigrations
python manage.py migrate
```

### Q3: npm install 失败?

**A**: 
```bash
# 清除缓存后重新安装
npm cache clean --force
npm install
```

### Q4: 前端构建失败?

**A**: 检查 Node.js 版本 (需要 16+):
```bash
node --version
```

---

## 六、开发工作流

### 后端开发

```bash
# 1. 修改代码
# 2. Django 自动重载
python manage.py runserver
```

### 前端开发

```bash
# 1. 启动开发服务器
npm run dev

# 2. 修改代码,Vite 热更新
# 3. 浏览器自动刷新
```

### 前后端联调

```bash
# 终端1: 启动后端
cd backend
python manage.py runserver

# 终端2: 启动前端
cd frontend
npm run dev

# 访问: http://localhost:5173
```

---

## 七、项目结构概览

```
trading-system/
├── backend/                 # Django 后端
│   ├── apps/               # 业务模块 (9个)
│   │   ├── users/          # 用户认证
│   │   ├── market/         # 市场数据
│   │   ├── strategy/       # 策略状态
│   │   ├── position/       # 持仓管理
│   │   ├── box/            # 箱体分析
│   │   ├── daytrade/       # 做T管理
│   │   ├── risk/           # 风险管理
│   │   ├── config/         # 配置管理
│   │   └── data_sync/      # 数据同步
│   ├── trading_system/     # Django 配置
│   └── manage.py
├── frontend/               # Vue 3 前端
│   ├── src/
│   │   ├── views/          # 页面 (5个)
│   │   ├── components/     # 组件 (4个)
│   │   ├── store/          # 状态管理 (3个)
│   │   └── router/         # 路由配置
│   └── package.json
└── 文档/
    ├── API_DOCUMENTATION.md
    ├── FRONTEND_COMPLETE.md
    └── DELIVERY.md
```

---

## 八、下一步

完成快速启动后,你可以:

1. **测试 API** - 使用 Postman 或 curl 测试 API 接口
2. **完善前端** - 添加更多页面和组件
3. **配置 Celery** - 设置定时任务自动同步数据
4. **编写测试** - 单元测试和集成测试
5. **部署上线** - 使用 Nginx + Gunicorn 部署

---

## 九、相关文档

- [API 文档](./API_DOCUMENTATION.md) - 47个 API 端点详细说明
- [前端文档](./frontend/README.md) - 前端开发指南
- [交付文档](./DELIVERY.md) - 项目完整交付清单
- [核心逻辑](./CORE_LOGICS_COMPLETE.md) - 业务逻辑详解

---

**祝使用愉快!** 🚀
