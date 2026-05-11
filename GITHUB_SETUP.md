# GitHub Actions 快速配置指南

## ✅ 已完成的操作

1. ✓ 代码已推送到 GitHub: `https://github.com/hc1609/trading-system`
2. ✓ 已配置两个GitHub Actions工作流
3. ✓ 首次提交: 155个文件, 15297行代码

---

## 📋 下一步: 验证自动构建

### 1. 查看Actions状态

访问: https://github.com/hc1609/trading-system/actions

您应该能看到:
- **Build and Push Docker Image** 工作流正在运行
- 蓝色/绿色表示成功,红色表示失败

### 2. 等待构建完成 (约5-10分钟)

构建完成后,您将看到:
- ✅ 绿色的勾号表示构建成功
- 镜像已推送到: `ghcr.io/hc1609/trading-system:master`

---

## 🔧 可选配置: Docker Hub推送

默认情况下,镜像只推送到 GitHub Container Registry (ghcr.io)。

如果您还想推送到 Docker Hub,需要配置Secrets:

### 步骤:

1. **创建Docker Hub Access Token**
   - 访问: https://hub.docker.com/settings/security
   - 点击 "New Access Token"
   - 命名: `GitHub Actions`
   - 权限: Read & Write
   - 复制生成的Token

2. **添加到GitHub Secrets**
   - 访问: https://github.com/hc1609/trading-system/settings/secrets/actions
   - 点击 "New repository secret"
   
   添加两个Secrets:
   
   | Secret名称 | 值 |
   |-----------|-----|
   | `DOCKERHUB_USERNAME` | `hc1609` (您的Docker Hub用户名) |
   | `DOCKERHUB_TOKEN` | 刚才创建的Access Token |

3. **验证**
   - 再次推送代码或手动触发Actions
   - 镜像将同时推送到 ghcr.io 和 Docker Hub

---

## 🚀 使用示例

### 场景1: 发布第一个版本

```bash
# 创建版本tag
git tag -a v1.0.0 -m "Release version 1.0.0"

# 推送tag
git push origin v1.0.0
```

这将自动触发:
1. 构建镜像并推送 (标签: `1.0.0`, `1.0`, `1`, `latest`)
2. 更新 `docker-compose.yml` 中的镜像版本

### 场景2: 日常开发

```bash
# 修改代码
git add .
git commit -m "feat: 添加新功能"

# 推送到master
git push
```

这将自动:
- 构建镜像并推送到 `ghcr.io/hc1609/trading-system:master`
- 不会触发版本更新工作流

### 场景3: 手动触发构建

1. 访问: https://github.com/hc1609/trading-system/actions
2. 点击左侧 "Build and Push Docker Image"
3. 点击 "Run workflow" 按钮
4. 选择分支,点击 "Run workflow"

---

## 📦 服务器部署

在CentOS服务器上拉取并使用镜像:

### 方式1: 直接从GitHub拉取 (推荐)

```bash
# 1. 安装Docker和Docker Compose (如果还没有)
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install -y docker-ce docker-ce-cli containerd.io
sudo systemctl start docker
sudo systemctl enable docker

sudo curl -L "https://github.com/docker/compose/releases/download/v2.23.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 2. 登录GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u hc1609 --password-stdin
# 注意: 需要先创建Personal Access Token

# 3. 创建项目目录
mkdir -p /opt/trading-system
cd /opt/trading-system

# 4. 创建配置文件
cat > .env << EOF
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,*

DB_HOST=localhost
DB_PORT=3306
DB_NAME=trading_system
DB_USER=trading
DB_PASSWORD=your-mysql-password

REDIS_HOST=localhost
REDIS_PORT=6379

ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-admin-password
EOF

# 5. 创建docker-compose.yml
cat > docker-compose.yml << EOF
version: '3.8'

services:
  trading-system:
    image: ghcr.io/hc1609/trading-system:latest
    container_name: trading-system
    restart: unless-stopped
    ports:
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - ./logs:/app/logs
      - ./media:/app/media
EOF

# 6. 启动服务
docker-compose up -d

# 7. 查看日志
docker logs -f trading-system
```

### 方式2: 克隆项目 (包含完整代码)

```bash
# 1. 克隆项目
git clone https://github.com/hc1609/trading-system.git /opt/trading-system
cd /opt/trading-system

# 2. 配置环境变量
cp .env.example .env
vim .env  # 修改配置

# 3. 启动服务
docker-compose up -d
```

---

## 🔍 镜像管理

### 查看已构建的镜像

访问: https://github.com/hc1609/trading-system/pkgs/container/trading-system

### 拉取指定版本

```bash
# 拉取master分支
docker pull ghcr.io/hc1609/trading-system:master

# 拉取最新版本
docker pull ghcr.io/hc1609/trading-system:latest

# 拉取指定版本 (例如1.0.0)
docker pull ghcr.io/hc1609/trading-system:1.0.0
```

### 查看本地镜像

```bash
docker images | grep trading-system
```

---

## 📊 工作流说明

### docker-build.yml

**触发条件**:
- ✅ Push到master分支
- ✅ 创建版本tag (v1.0.0)
- ✅ Pull Request
- ✅ 手动触发

**输出镜像**:
- `ghcr.io/hc1609/trading-system:master` (master分支)
- `ghcr.io/hc1609/trading-system:1.0.0` (版本tag)
- `ghcr.io/hc1609/trading-system:latest` (最新版本)
- `hc1609/trading-system:*` (如果配置了Docker Hub)

### update-version.yml

**触发条件**:
- ✅ 创建版本tag (v1.0.0)
- ✅ 手动触发 (需输入版本号)

**功能**:
- 自动更新 `docker-compose.yml` 中的镜像版本
- 提交并推送到仓库

---

## 🔐 创建Personal Access Token (用于服务器拉取镜像)

1. 访问: https://github.com/settings/tokens
2. 点击 "Generate new token" → "Generate new token (classic)"
3. 配置:
   - Note: `Server Pull`
   - Expiration: 根据需要选择
   - Scopes: 勾选 `read:packages`
4. 点击 "Generate token"
5. **重要**: 立即复制Token,它只会显示一次

在服务器上使用:
```bash
echo YOUR_TOKEN | docker login ghcr.io -u hc1609 --password-stdin
```

---

## 🎯 验证清单

完成后,您应该能够:

- [ ] 在GitHub Actions中看到成功的构建记录
- [ ] 在Packages中看到已构建的Docker镜像
- [ ] 从服务器成功拉取镜像
- [ ] 成功运行容器并访问应用
- [ ] (可选) 在Docker Hub中看到镜像 (如果已配置)

---

## 📚 相关文档

- [GitHub Actions详细配置](./GITHUB_ACTIONS.md)
- [Docker部署指南](./DEPLOY.md)
- [单镜像架构说明](./DOCKER_SINGLE_IMAGE.md)

---

## ❓ 常见问题

### Q: Actions没有触发?

**A**: 检查:
1. `.github/workflows/` 目录是否存在
2. 工作流文件语法是否正确
3. Actions是否被禁用 (Settings → Actions → General)

### Q: 构建失败怎么办?

**A**: 
1. 点击失败的workflow查看日志
2. 检查Dockerfile是否有错误
3. 确认依赖安装正常

### Q: 如何重新触发构建?

**A**: 
```bash
# 方式1: 创建一个空提交
git commit --allow-empty -m "chore: trigger rebuild"
git push

# 方式2: 在GitHub上手动触发
# Actions → Build and Push Docker Image → Run workflow
```

### Q: 镜像拉取失败?

**A**: 
1. 确认已登录: `docker login ghcr.io`
2. 确认Token权限: `read:packages`
3. 确认镜像名称和标签正确

---

## 🎉 完成!

现在您拥有:
- ✅ 完整的交易策略系统代码
- ✅ 自动构建的GitHub Actions
- ✅ 随时可用的Docker镜像
- ✅ 一键部署能力

祝您使用愉快! 🚀
