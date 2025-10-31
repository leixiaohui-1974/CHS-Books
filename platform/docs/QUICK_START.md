# 快速启动指南

本指南帮助您在5分钟内启动整个平台。

## 前置要求

- Docker 24+ 和 Docker Compose
- 至少 4GB 可用内存
- 至少 10GB 可用磁盘空间

## 快速启动（推荐）

### 1. 克隆项目

```bash
cd /workspace/platform
```

### 2. 配置环境变量

```bash
# 复制环境配置文件
cp .env.example .env

# 编辑.env文件（可选，默认配置可直接运行）
# 至少需要配置：
# - SECRET_KEY (生产环境必须修改)
# - JWT_SECRET_KEY (生产环境必须修改)
# - 数据库密码（生产环境必须修改）
```

### 3. 启动所有服务

```bash
cd docker
docker-compose up -d
```

这将启动以下服务：
- ✅ PostgreSQL (端口 5432)
- ✅ Redis (端口 6379)
- ✅ MongoDB (端口 27017)
- ✅ MinIO (端口 9000, 9001)
- ✅ 后端API (端口 8000)
- ✅ 前端应用 (端口 3000)
- ✅ Celery Worker
- ✅ Nginx (端口 80)

### 4. 初始化数据库

```bash
# 等待数据库启动（约30秒）
sleep 30

# 运行数据库迁移
docker-compose exec backend alembic upgrade head

# （可选）导入示例数据
docker-compose exec backend python scripts/seed_data.py
```

### 5. 扫描内容

```bash
# 扫描books目录，将内容导入数据库
docker-compose exec backend python /workspace/platform/scanner/main.py
```

### 6. 访问应用

- 🌐 **前端应用**: http://localhost:3000
- 📡 **后端API文档**: http://localhost:8000/docs
- 🗄️ **MinIO控制台**: http://localhost:9001 (用户名/密码: minioadmin/minioadmin)

### 7. 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 8. 停止服务

```bash
# 停止所有服务
docker-compose down

# 停止并删除数据卷（警告：会删除所有数据）
docker-compose down -v
```

---

## 手动开发模式

如果您想手动运行各个服务进行开发：

### 1. 启动基础服务

```bash
cd docker
docker-compose up -d postgres redis mongo minio
```

### 2. 后端开发

```bash
cd /workspace/platform/backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 运行数据库迁移
alembic upgrade head

# 启动开发服务器（支持热重载）
uvicorn main:app --reload --port 8000
```

### 3. 前端开发

```bash
cd /workspace/platform/frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 4. 扫描内容

```bash
cd /workspace/platform/scanner
pip install -r requirements.txt
python main.py
```

---

## 验证安装

### 健康检查

```bash
# 检查后端健康状态
curl http://localhost:8000/health

# 预期输出:
# {"status":"healthy","version":"1.0.0","environment":"development"}
```

### 测试API

```bash
# 获取书籍列表
curl http://localhost:8000/api/v1/books

# 注册用户
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","username":"testuser","password":"password123"}'
```

---

## 常见问题

### 端口冲突

如果端口已被占用，修改 `docker/docker-compose.yml` 中的端口映射：

```yaml
services:
  backend:
    ports:
      - "8001:8000"  # 改为8001
```

### 数据库连接失败

1. 检查PostgreSQL是否启动：
   ```bash
   docker-compose ps postgres
   ```

2. 检查日志：
   ```bash
   docker-compose logs postgres
   ```

3. 手动连接测试：
   ```bash
   docker-compose exec postgres psql -U elp_user -d elp_db
   ```

### 内存不足

如果Docker内存不足，增加Docker Desktop的内存限制（至少4GB）。

### 权限问题

```bash
# Linux/Mac: 给予执行权限
chmod +x scripts/*.sh
chmod +x docker/*.sh
```

---

## 下一步

- 📖 阅读 [开发文档](DEVELOPMENT.md)
- 🚀 查看 [部署指南](DEPLOYMENT.md)
- 📚 查看 [API文档](API.md)
- 🤝 查看 [贡献指南](../CONTRIBUTING.md)

---

## 获取帮助

- 💬 提交Issue: https://github.com/your-repo/issues
- 📧 邮件联系: support@example.com
- 📖 完整文档: https://docs.example.com

---

**祝您使用愉快！** 🎉
