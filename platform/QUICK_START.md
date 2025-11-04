# 🚀 智能知识平台 V2.0 - 5分钟快速开始

欢迎使用智能知识平台V2.0！本指南将帮助您在5分钟内启动并运行平台。

---

## 📋 前置要求

确保您的系统已安装：
- Docker 20.10+ 
- Docker Compose 2.0+
- Python 3.11+ (仅本地开发需要)

---

## 🎯 方式一：Docker 一键启动（推荐）

### 1. 克隆项目

```bash
cd /workspace/platform
```

### 2. 启动服务

```bash
# 方式A: 使用管理工具
cd backend
./manage.py docker up

# 方式B: 直接使用docker-compose
docker-compose -f docker-compose.v2.yml up -d
```

### 3. 验证服务

```bash
# 检查服务状态
./manage.py docker ps

# 或
docker-compose -f docker-compose.v2.yml ps
```

### 4. 访问平台

打开浏览器访问：
- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health
- **系统信息**: http://localhost:8000/api/v1/system/info

---

## 💻 方式二：本地开发启动

### 1. 安装依赖

```bash
cd /workspace/platform/backend
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑配置（可选）
nano .env
```

### 3. 初始化数据库

```bash
./manage.py db init
```

### 4. 启动服务器

```bash
./manage.py server start --reload
```

### 5. 访问平台

- **API文档**: http://localhost:8000/docs

---

## ✅ 快速验证

### 运行健康检查

```bash
python3 health_check.py
```

期望输出：
```
============================================================
 智能知识平台 V2.0 - 健康检查
============================================================

检查 文件结构... ✅ 文件结构完整 (7 个核心文件)
检查 核心服务... ✅ 所有服务正常
检查 数据库连接... ✅ 数据库连接正常
检查 Redis连接... ✅ Redis配置正常

============================================================
✅ 所有检查通过 (4/4)
系统运行正常！
============================================================
```

### 运行演示工作流

```bash
python3 demo_workflow.py
```

这将展示完整的9步工作流演示。

---

## 🧪 快速测试

### 运行测试套件

```bash
# 快速测试
./manage.py test quick

# E2E测试
./manage.py test e2e

# 所有测试
./manage.py test all
```

---

## 📊 查看系统信息

```bash
./manage.py info
```

输出示例：
```
============================================================
 智能知识平台 V2.0 - 系统信息
============================================================

📦 项目信息:
  版本: 2.0.0
  状态: ✅ 完全交付

📊 代码统计:
  后端代码: 3,730行
  前端组件: 1,250行
  测试代码: 1,250行
  API端点: 26个

🔧 核心功能:
  ✅ 会话管理
  ✅ 代码智能
  ✅ 执行引擎
  ✅ AI助手
  ✅ 结果解析
```

---

## 🎮 使用示例

### 1. 创建学习会话

```bash
curl -X POST "http://localhost:8000/api/v2/sessions/create" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001",
    "book_slug": "water-environment-simulation",
    "case_slug": "case_01_diffusion"
  }'
```

### 2. 加载案例代码

```bash
curl -X POST "http://localhost:8000/api/v2/code/load" \
  -H "Content-Type: application/json" \
  -d '{
    "book_slug": "water-environment-simulation",
    "case_slug": "case_01_diffusion"
  }'
```

### 3. 查看API文档

访问 http://localhost:8000/docs 查看完整的交互式API文档。

---

## 🛠️ 常用命令

### Docker管理

```bash
# 启动
./manage.py docker up

# 停止
./manage.py docker down

# 查看日志
./manage.py docker logs

# 查看状态
./manage.py docker ps
```

### 数据库管理

```bash
# 初始化
./manage.py db init

# 检查
./manage.py db check

# 重置（危险！）
./manage.py db reset
```

### 开发工具

```bash
# 性能监控
python3 performance_monitor.py

# 代码质量检查
python3 code_quality.py

# 备份数据
python3 backup_restore.py
```

---

## 🐛 故障排查

### 问题1: 端口被占用

```bash
# 检查端口占用
lsof -i :8000

# 停止服务
./manage.py server stop

# 或指定其他端口
./manage.py server start --port 8080
```

### 问题2: Docker启动失败

```bash
# 查看详细日志
docker-compose -f docker-compose.v2.yml logs backend

# 重新构建
docker-compose -f docker-compose.v2.yml build --no-cache
docker-compose -f docker-compose.v2.yml up -d
```

### 问题3: 依赖安装失败

```bash
# 清理pip缓存
pip cache purge

# 重新安装
pip install -r requirements.txt --no-cache-dir
```

### 问题4: 数据库连接失败

```bash
# 检查PostgreSQL状态
docker-compose -f docker-compose.v2.yml ps postgres

# 重启PostgreSQL
docker-compose -f docker-compose.v2.yml restart postgres

# 等待30秒后重新初始化
./manage.py db init
```

---

## 📚 下一步

现在平台已经运行，您可以：

1. **阅读完整文档**
   - [README_V2.md](README_V2.md) - 项目总览
   - [智能知识平台增强方案-V2.0.md](智能知识平台增强方案-V2.0.md) - 设计方案
   - [API_USAGE_EXAMPLES.md](API_USAGE_EXAMPLES.md) - API示例
   - [TOOLS_DOCUMENTATION.md](TOOLS_DOCUMENTATION.md) - 工具文档

2. **探索API**
   - 访问 http://localhost:8000/docs 交互式文档
   - 尝试不同的API端点
   - 查看请求/响应示例

3. **运行演示**
   ```bash
   python3 demo_workflow.py
   ```

4. **开发新功能**
   - 参考现有代码结构
   - 使用 `./manage.py` 工具
   - 运行测试验证

---

## 💡 提示

- 使用 `./manage.py --help` 查看所有可用命令
- 运行 `./manage.py info` 查看系统信息
- 使用 `./manage.py docs` 查看文档列表
- 定期运行 `python3 health_check.py` 检查系统健康

---

## 📞 获取帮助

遇到问题？

1. 查看 [TOOLS_DOCUMENTATION.md](TOOLS_DOCUMENTATION.md) 故障排查部分
2. 运行 `python3 health_check.py` 诊断系统
3. 查看日志: `./manage.py docker logs`
4. 阅读 [启动指南.md](启动指南.md) 详细说明

---

## 🎉 开始使用

恭喜！您已经成功启动智能知识平台V2.0！

现在可以：
- 🎓 开始学习水利工程课程
- 💻 执行案例脚本
- 🤖 与AI助手交互
- 📊 查看标准化结果

**祝学习愉快！** 🚀

---

**版本**: V2.0.0  
**更新日期**: 2025-11-04  
**状态**: ✅ 生产就绪
