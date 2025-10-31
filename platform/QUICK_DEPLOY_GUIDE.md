# 🚀 快速部署指南

**5分钟快速部署工程学习平台**

---

## 📋 部署前检查

### ✅ 必备条件
- [ ] Docker 20.10+ 已安装
- [ ] Docker Compose 2.0+ 已安装
- [ ] 有8GB+可用内存
- [ ] 有10GB+可用磁盘空间

### 🔧 检查命令
```bash
# 检查Docker
docker --version
docker-compose --version

# 检查资源
free -h  # Linux/Mac
```

---

## 🎯 方式一：一键部署（推荐）

### 步骤1: 下载代码
```bash
cd /workspace/platform
```

### 步骤2: 配置环境
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量（可选，使用默认配置也可以）
nano .env  # 或使用其他编辑器
```

### 步骤3: 一键部署
```bash
# 运行部署脚本
./deploy.sh

# 选择开发环境（输入1）或生产环境（输入2）
```

### 步骤4: 等待完成
```
🚀 工程学习平台 - 一键部署脚本
=================================

📦 检查Docker环境...
✅ Docker环境检查通过

📝 检查环境变量配置...
✅ .env文件已存在

🎯 选择部署模式:
1) 开发环境 (development)
2) 生产环境 (production)
请选择 [1/2, 默认1]: 1

🏗️  构建Docker镜像...
✅ 镜像构建完成

🚀 启动服务...
✅ 服务启动成功

⏳ 等待服务就绪...
✅ 后端服务健康

=================================
✅ 部署完成！
=================================

🌐 访问地址:
  前端应用:     http://localhost:3000
  后端API:      http://localhost:8000
  API文档:      http://localhost:8000/docs

🎉 祝您使用愉快！
```

---

## 🔨 方式二：手动部署

### 步骤1: 环境配置
```bash
cd /workspace/platform
cp .env.example .env
```

### 步骤2: 构建镜像
```bash
docker-compose build --no-cache
```

### 步骤3: 启动服务
```bash
docker-compose up -d
```

### 步骤4: 查看状态
```bash
docker-compose ps
```

应该看到以下服务运行中：
```
NAME                COMMAND                  STATUS
platform-backend    "uvicorn app.main:ap…"   Up
platform-frontend   "docker-entrypoint.s…"   Up
platform-postgres   "docker-entrypoint.s…"   Up
platform-redis      "redis-server"           Up
platform-mongodb    "docker-entrypoint.s…"   Up
platform-nginx      "nginx -g 'daemon of…"   Up
```

---

## 🌐 访问应用

部署完成后，在浏览器中访问：

### 前端应用
```
http://localhost:3000
```

### 后端API
```
http://localhost:8000
```

### API文档
```
Swagger UI:  http://localhost:8000/docs
ReDoc:       http://localhost:8000/redoc
```

### 健康检查
```bash
curl http://localhost:8000/api/v1/health
```

---

## 🗄️ 初始化数据

### 初始化数据库表
```bash
docker-compose exec backend python scripts/init_db.py
```

### 填充示例数据（可选）
```bash
docker-compose exec backend python scripts/seed_data.py
```

示例数据包括：
- 3本示例书籍
- 20+章节
- 50+案例
- 测试用户账号

---

## 🧪 验证部署

### 测试后端API
```bash
# 健康检查
curl http://localhost:8000/api/v1/health

# 获取书籍列表
curl http://localhost:8000/api/v1/books
```

### 测试前端
在浏览器中访问 http://localhost:3000，应该看到：
- ✅ 首页正常显示
- ✅ 可以浏览书籍列表
- ✅ 可以注册登录

### 测试数据库
```bash
# 连接PostgreSQL
docker-compose exec postgres psql -U postgres -d engineering_platform

# 查看表
\dt

# 退出
\q
```

---

## 🔧 常用命令

### 查看日志
```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 重启服务
```bash
# 重启所有服务
docker-compose restart

# 重启特定服务
docker-compose restart backend
```

### 停止服务
```bash
# 停止但保留数据
docker-compose stop

# 停止并删除容器（保留数据卷）
docker-compose down

# 停止并删除所有（包括数据）
docker-compose down -v
```

### 进入容器
```bash
# 进入后端容器
docker-compose exec backend bash

# 进入前端容器
docker-compose exec frontend sh

# 进入数据库
docker-compose exec postgres psql -U postgres -d engineering_platform
```

---

## ⚠️ 常见问题

### 问题1: 端口已被占用
```
Error: bind: address already in use
```

**解决方案:**
```bash
# 检查端口占用
lsof -i :3000  # 前端端口
lsof -i :8000  # 后端端口

# 修改端口（编辑docker-compose.yml）
# 或停止占用端口的服务
```

### 问题2: 内存不足
```
Error: Cannot allocate memory
```

**解决方案:**
```bash
# 增加Docker内存限制
# Docker Desktop -> Settings -> Resources -> Memory

# 或减少服务数量（编辑docker-compose.yml）
```

### 问题3: 数据库连接失败
```
Error: could not connect to server
```

**解决方案:**
```bash
# 等待PostgreSQL启动完成
docker-compose logs postgres

# 重启backend服务
docker-compose restart backend
```

### 问题4: 前端无法连接后端
```
Error: Network Error
```

**解决方案:**
```bash
# 检查后端健康
curl http://localhost:8000/api/v1/health

# 检查前端环境变量
docker-compose exec frontend env | grep API

# 重启nginx
docker-compose restart nginx
```

---

## 🔐 安全配置

### 生产环境必须修改
在 `.env` 文件中修改以下配置：

```bash
# JWT密钥（必改！）
JWT_SECRET_KEY=your-secure-random-key-here

# 数据库密码（必改！）
POSTGRES_PASSWORD=your-secure-password

# Redis密码（建议改）
REDIS_PASSWORD=your-redis-password

# 允许的域名
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

### 生成安全密钥
```bash
# 生成JWT密钥
openssl rand -hex 32

# 生成数据库密码
openssl rand -base64 24
```

---

## 📊 性能优化

### 开发环境
```yaml
# docker-compose.yml
services:
  backend:
    environment:
      - DEBUG=True
      - LOG_LEVEL=DEBUG
```

### 生产环境
```yaml
# docker-compose.prod.yml
services:
  backend:
    environment:
      - DEBUG=False
      - LOG_LEVEL=INFO
      - WORKERS=4  # 根据CPU核心数调整
```

---

## 🔄 更新部署

### 更新代码
```bash
# 拉取最新代码
git pull origin main

# 重新构建
docker-compose build --no-cache

# 重启服务
docker-compose up -d
```

### 数据库迁移
```bash
# 运行迁移脚本
docker-compose exec backend alembic upgrade head
```

---

## 🌍 生产环境部署

### 额外配置

#### 1. 配置HTTPS
```bash
# 使用Let's Encrypt
docker-compose exec nginx certbot --nginx -d yourdomain.com
```

#### 2. 配置域名
修改 `docker/nginx/nginx.conf`:
```nginx
server_name yourdomain.com www.yourdomain.com;
```

#### 3. 配置CDN
- 将前端静态资源上传到CDN
- 修改 `NEXT_PUBLIC_CDN_URL` 环境变量

#### 4. 配置监控
```bash
# 访问Prometheus
http://localhost:9090

# 配置Grafana
http://localhost:3001
```

---

## 📞 获取帮助

### 查看文档
- [完整开发报告](FINAL_DEVELOPMENT_REPORT.md)
- [项目状态](PROJECT_STATUS.md)
- [测试指南](QUICK_TEST_GUIDE.md)

### 查看日志
```bash
docker-compose logs -f
```

### 健康检查
```bash
curl http://localhost:8000/api/v1/health
```

### 联系支持
- GitHub Issues: [提交问题](https://github.com/yourusername/repo/issues)
- Email: support@example.com

---

## ✅ 部署检查清单

部署前：
- [ ] 安装Docker和Docker Compose
- [ ] 复制.env.example到.env
- [ ] 修改安全配置（生产环境）
- [ ] 检查端口占用

部署后：
- [ ] 所有服务运行中（docker-compose ps）
- [ ] 后端健康检查通过
- [ ] 前端可以访问
- [ ] API文档可以访问
- [ ] 数据库已初始化

功能测试：
- [ ] 用户注册功能
- [ ] 用户登录功能
- [ ] 书籍列表加载
- [ ] 工具执行功能

---

## 🎉 完成！

恭喜！您已成功部署工程学习平台！

**下一步:**
1. 访问 http://localhost:3000 体验应用
2. 阅读 [用户手册](docs/USER_GUIDE.md)
3. 查看 [API文档](http://localhost:8000/docs)

**祝您使用愉快！** 🚀
