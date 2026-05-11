# GitHub Actions 配置说明

## 工作流程概览

本项目配置了两个GitHub Actions工作流:

### 1. Docker镜像自动构建 (`docker-build.yml`)

**触发条件**:
- Push到 `main` 或 `master` 分支
- 创建版本tag (如 `v1.0.0`)
- Pull Request到主分支
- 手动触发

**功能**:
- 自动构建Docker镜像
- 推送到 GitHub Container Registry (ghcr.io)
- 可选推送到 Docker Hub
- 支持多平台构建 (amd64/arm64)
- 智能缓存加速构建

**镜像标签策略**:
- `main`分支: `latest`, `main`, `sha-xxxxx`
- 版本tag: `1.0.0`, `1.0`, `1`, `latest`
- PR: `pr-123`

### 2. 版本自动更新 (`update-version.yml`)

**触发条件**:
- 创建版本tag (如 `v1.0.0`)
- 手动触发 (需输入版本号)

**功能**:
- 自动更新 `docker-compose.yml` 中的镜像版本
- 提交并推送更新

---

## 首次配置步骤

### 第一步: 推送代码到GitHub

```bash
# 进入项目目录
cd /path/to/trading-system

# 初始化Git仓库
git init

# 添加远程仓库
git remote add origin git@github.com:hc1609/trading-system.git

# 添加所有文件
git add .

# 首次提交
git commit -m "Initial commit: 交易策略系统"

# 推送到GitHub
git push -u origin main
```

### 第二步: 配置GitHub Secrets (可选)

如果要推送到Docker Hub,需要配置以下Secrets:

1. 进入GitHub仓库 → Settings → Secrets and variables → Actions
2. 点击 "New repository secret"
3. 添加以下Secrets:

| Secret名称 | 值 | 说明 |
|-----------|-----|------|
| `DOCKERHUB_USERNAME` | 你的Docker Hub用户名 | 例如: hc1609 |
| `DOCKERHUB_TOKEN` | Docker Hub Access Token | 在Docker Hub → Account Settings → Security中创建 |

> **注意**: 推送GitHub Container Registry不需要额外配置,默认使用 `GITHUB_TOKEN`

### 第三步: 验证Actions

推送代码后,进入GitHub仓库 → Actions 标签,可以看到:
- 正在运行的构建工作流
- 构建日志
- 推送结果

---

## 使用示例

### 场景1: 日常开发推送

```bash
# 开发完成后提交代码
git add .
git commit -m "feat: 添加新功能"
git push

# 自动触发: 构建镜像并推送到 ghcr.io, 标签为 main 和 latest
```

### 场景2: 发布正式版本

```bash
# 创建版本tag
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# 自动触发: 
# 1. 构建镜像并推送, 标签为 1.0.0, 1.0, 1, latest
# 2. 自动更新docker-compose.yml中的镜像版本
```

### 场景3: 手动触发构建

1. 进入GitHub仓库 → Actions
2. 选择 "Build and Push Docker Image"
3. 点击 "Run workflow"
4. 选择分支,点击运行

### 场景4: 手动更新版本

1. 进入GitHub仓库 → Actions
2. 选择 "Update Docker Image Version"
3. 点击 "Run workflow"
4. 输入版本号 (例如: 1.0.0)
5. 点击运行

---

## 服务器部署

在CentOS服务器上拉取并运行镜像:

### 方式1: 使用构建的镜像

```bash
# 拉取最新镜像
docker pull ghcr.io/hc1609/trading-system:latest

# 创建配置文件
cp .env.example .env
vim .env  # 修改配置

# 运行 (需要先手动编写docker-compose.yml)
docker-compose up -d
```

### 方式2: 使用项目docker-compose.yml

```bash
# 拉取最新代码
git clone https://github.com/hc1609/trading-system.git
cd trading-system

# 修改配置
cp .env.example .env
vim .env

# 使用指定版本 (需要先触发版本tag)
# docker-compose.yml 会自动更新为最新版本
docker-compose up -d
```

---

## 镜像地址

构建成功后,可以在以下位置找到镜像:

### GitHub Container Registry
- 地址: `https://github.com/hc1609/trading-system/pkgs/container/trading-system`
- 拉取命令: `docker pull ghcr.io/hc1609/trading-system:latest`

### Docker Hub (如果配置)
- 地址: `https://hub.docker.com/r/hc1609/trading-system`
- 拉取命令: `docker pull hc1609/trading-system:latest`

---

## 故障排查

### 问题1: Actions未触发

**检查项**:
- 确认 `.github/workflows/*.yml` 文件存在
- 确认push到正确的分支 (main或master)
- 检查Actions是否被禁用 (Settings → Actions → General)

### 问题2: 构建失败

**查看日志**:
- 进入Actions → 点击失败的工作流 → 查看日志

**常见原因**:
- Dockerfile语法错误
- 依赖安装失败
- 磁盘空间不足

### 问题3: 推送失败

**检查**:
```bash
# 确认远程仓库
git remote -v

# 确认权限
# 需要 package write 权限 (默认GITHUB_TOKEN已有)
```

### 问题4: 镜像拉取失败

**检查**:
```bash
# 登录GitHub Container Registry
echo $CR_PAT | docker login ghcr.io -u USERNAME --password-stdin

# 或使用Personal Access Token
docker login ghcr.io -u hc1609 -p YOUR_TOKEN
```

---

## 优化建议

### 加速构建

1. **使用缓存**: 工作流已配置GitHub Actions缓存
2. **多阶段构建**: Dockerfile已使用多阶段构建
3. **按需推送**: 减少不必要的push,合并后再推送

### 安全建议

1. **保护分支**: 设置main分支保护,需要PR才能合并
2. **版本tag**: 使用语义化版本 (SemVer)
3. **定期更新**: 及时更新基础镜像版本
4. **扫描漏洞**: 启用GitHub Advanced Security

### 成本控制

1. **构建频率**: 非main分支的push不推送镜像,仅测试
2. **存储清理**: 定期清理旧的镜像版本
3. **并行构建**: 使用缓存减少构建时间

---

## 高级配置

### 添加通知

在 `.github/workflows/docker-build.yml` 末尾添加:

```yaml
  notify:
    needs: build-and-push
    runs-on: ubuntu-latest
    if: success()
    steps:
    - name: Send notification
      uses: slackapi/slack-github-action@v1
      with:
        channel-id: 'deployments'
        slack-message: "✅ 交易策略系统镜像构建成功!\n版本: ${{ github.ref_name }}"
      env:
        SLACK_BOT_TOKEN: ${{ secrets.SLACK_BOT_TOKEN }}
```

### 添加测试

```yaml
  test:
    runs-on: ubuntu-latest
    steps:
    - name: Run tests
      run: |
        docker build -t trading-system:test .
        docker run --rm trading-system:test python manage.py test
```

---

## 相关资源

- [GitHub Actions文档](https://docs.github.com/en/actions)
- [Docker Buildx文档](https://docs.docker.com/build/buildx/)
- [GitHub Container Registry文档](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Docker Hub文档](https://docs.docker.com/docker-hub/)
