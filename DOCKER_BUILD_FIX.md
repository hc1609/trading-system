# Dockerfile 构建问题排查与修复记录

## 问题总结

### 问题1: `/frontend/dist: not found` (第1次)
**错误信息**: 
```
failed to compute cache key: "/frontend/dist": not found
```

**根本原因**: 
- `COPY frontend/ ./` 路径错误
- 在 `WORKDIR /frontend` 下，`COPY frontend/ ./` 会复制到 `/frontend/frontend/`

**修复方案**:
```dockerfile
# 错误
COPY frontend/ ./

# 正确
COPY frontend/ .
```

---

### 问题2: `/frontend/dist: not found` (第2次)
**错误信息**: 同上

**根本原因**:
- `vite.config.js` 中配置的输出目录是 `outDir: '../backend/static/dist'`
- 在Docker第一阶段构建时，文件输出到了 `/backend/static/dist`
- 但Dockerfile中尝试从 `/frontend/dist` 复制

**修复方案**:
修改 `frontend/vite.config.js`:
```javascript
// 修改前
build: {
  outDir: '../backend/static/dist',  // 本地开发时输出到backend
  ...
}

// 修改后
build: {
  outDir: 'dist',  // Docker构建时输出到dist
  ...
}
```

---

## 正确的构建流程

### 阶段1: frontend-builder
```dockerfile
FROM python:3.11-slim as frontend-builder

# 1. 安装Node.js
RUN apt-get update && apt-get install -y ... nodejs

# 2. 设置工作目录
WORKDIR /frontend

# 3. 复制package.json并安装依赖
COPY frontend/package*.json ./
RUN npm install --production=false

# 4. 复制所有前端文件
COPY frontend/ .

# 5. 构建前端 (输出到 /frontend/dist)
RUN npm run build
```

**结果**: 
- 构建产物在: `/frontend/dist/`
- 包含: index.html, assets/*.js, assets/*.css

### 阶段2: 最终镜像
```dockerfile
FROM python:3.11-slim

# 1. 安装系统依赖 + TA-Lib
RUN apt-get update && ... && \
    wget ta-lib && make && make install

# 2. 设置工作目录
WORKDIR /app

# 3. 安装Python依赖
COPY backend/requirements.txt .
RUN pip install -r requirements.txt

# 4. 复制后端代码
COPY backend/ .

# 5. 复制前端构建产物 (从阶段1)
COPY --from=frontend-builder /frontend/dist ./static/dist

# 6. 配置Supervisor和启动脚本
COPY docker/supervisord.conf ...
COPY docker/start.sh ...

# 7. 启动
CMD ["/start.sh"]
```

**最终结构**:
```
/app/
├── backend/...              # Django代码
├── static/dist/             # 前端构建产物
│   ├── index.html
│   └── assets/
├── logs/
└── media/
```

---

## 验证清单

### 本地验证 (推送前)
```bash
# 1. 运行验证脚本
bash verify-dockerfile.sh

# 2. 检查关键路径
ls frontend/package.json          # ✓ 存在
ls frontend/vite.config.js        # ✓ 存在
ls frontend/src/                  # ✓ 存在
ls backend/manage.py              # ✓ 存在
ls backend/requirements.txt       # ✓ 存在
ls docker/start.sh                # ✓ 存在
ls docker/supervisord.conf        # ✓ 存在

# 3. 检查vite配置
grep "outDir" frontend/vite.config.js
# 应该输出: outDir: 'dist',

# 4. 检查Dockerfile关键行
grep "COPY --from=frontend-builder" Dockerfile
# 应该输出: COPY --from=frontend-builder /frontend/dist ./static/dist
```

### Docker构建验证 (需要Docker Desktop)
```bash
# 1. 构建镜像
docker build -t trading-system:test .

# 2. 检查构建产物
docker run --rm trading-system:test ls -la /app/static/dist/
# 应该看到: index.html, assets/

# 3. 测试运行
docker run -p 8000:8000 trading-system:test

# 4. 访问测试
curl http://localhost:8000/
# 应该返回HTML页面
```

---

## 关键配置对照表

| 配置项 | 本地开发 | Docker构建 |
|--------|---------|-----------|
| Vite输出 | `../backend/static/dist` | `dist` |
| 前端工作目录 | `frontend/` | `/frontend` |
| 后端工作目录 | `backend/` | `/app` |
| 静态文件路径 | `backend/static/dist` | `/app/static/dist` |
| 访问方式 | `localhost:5173` (vite dev) | `localhost:8000` (gunicorn) |

---

## 为什么修改vite配置？

### 本地开发时
```
frontend/
└── (npm run build)
    └── 输出到 ../backend/static/dist/
    
结果: backend/static/dist/ 可以直接被Django开发服务器访问
```

### Docker构建时
```
/frontend/
└── (npm run build)
    └── 输出到 /frontend/dist/
    
然后在阶段2:
COPY --from=frontend-builder /frontend/dist /app/static/dist/

结果: 多阶段构建可以正确复制文件
```

**注意**: 本地开发时可以临时改回 `../backend/static/dist`，但Docker构建需要 `dist`。

---

## 最终解决方案

为了同时支持本地开发和Docker构建，有两个选择:

### 方案A: 统一输出到dist (当前采用)
- 修改vite.config.js: `outDir: 'dist'`
- 本地开发: 手动复制 `frontend/dist` 到 `backend/static/dist`
- Docker构建: 自动从 `/frontend/dist` 复制

### 方案B: 在Dockerfile中使用sed
- 保持vite.config.js: `outDir: '../backend/static/dist'`
- Dockerfile中: `RUN sed -i "s|outDir: '../backend/static/dist'|outDir: 'dist'|" vite.config.js`
- 缺点: 增加构建复杂度

**选择方案A的原因**: 更简单、更清晰、Dockerfile更易维护。

---

## 相关文件

- `Dockerfile` - 镜像构建配置
- `frontend/vite.config.js` - Vite构建配置
- `docker/start.sh` - 容器启动脚本
- `docker/supervisord.conf` - 进程管理配置
- `verify-dockerfile.sh` - 本地验证脚本

---

## 更新日志

- **2024-05-19**: 修复vite输出路径问题，统一使用dist目录
- **2024-05-19**: 优化TA-Lib编译 (并行编译 + ldconfig)
- **2024-05-19**: 添加本地验证脚本
