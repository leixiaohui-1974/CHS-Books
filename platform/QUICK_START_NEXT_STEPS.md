# 🚀 下一步操作指南

**当前状态**: 核心代码开发完成 ✅
**下一步**: 环境搭建与集成测试 ⏳

---

## 快速开始（5分钟）

### 1️⃣ 启动数据库（1分钟）

```bash
# 使用Docker启动PostgreSQL
docker run -d \
  --name postgres-elp \
  -e POSTGRES_DB=elp_db \
  -e POSTGRES_USER=elp_user \
  -e POSTGRES_PASSWORD=elp_password \
  -p 5432:5432 \
  postgres:15

# 验证数据库已启动
docker ps | grep postgres-elp
```

### 2️⃣ 启动后端服务（2分钟）

```bash
cd platform/backend

# 安装依赖（首次）
pip install -r requirements.txt
pip install asyncpg psycopg2-binary  # 数据库驱动

# 运行数据库迁移（创建表）
alembic upgrade head

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**验证**: 访问 http://localhost:8000/docs 应该看到API文档

### 3️⃣ 创建示例数据（30秒）

```bash
# 在API文档页面或使用curl
curl -X POST http://localhost:8000/api/v1/textbooks/dev/seed-example
```

**预期输出**:
```json
{
  "message": "示例教材数据已创建",
  "book_slug": "water-system-intro",
  "chapter_slug": "chapter-01",
  "case_slug": "case-water-tank",
  "preview_url": "/api/v1/textbooks/water-system-intro/chapter-01/case-water-tank"
}
```

### 4️⃣ 测试API端点（30秒）

```bash
# 获取教材内容
curl http://localhost:8000/api/v1/textbooks/water-system-intro/chapter-01/case-water-tank | jq
```

**预期输出**: 包含sections、starter_code等完整数据的JSON

### 5️⃣ 启动前端（1分钟）

```bash
cd platform/frontend

# 安装依赖（首次）
npm install

# 启动开发服务器
npm run dev
```

**验证**: 访问 http://localhost:3000/textbook-demo

### 6️⃣ 体验功能 ✨

在浏览器中打开 http://localhost:3000/textbook-demo，你应该看到：

- ✅ 左侧：水箱实验教材内容
- ✅ 右侧：Python代码编辑器
- ✅ 中间：可拖拽的分隔符
- ✅ 滚动教材时，代码自动定位到相应行
- ✅ 点击代码引用链接，代码行高亮

---

## 常见问题解决

### ❌ 数据库连接失败

**错误信息**: `could not connect to server`

**解决方案**:
```bash
# 检查Docker容器状态
docker ps -a | grep postgres

# 如果容器已停止，启动它
docker start postgres-elp

# 查看容器日志
docker logs postgres-elp
```

### ❌ 后端导入错误

**错误信息**: `ModuleNotFoundError: No module named 'asyncpg'`

**解决方案**:
```bash
pip install asyncpg psycopg2-binary aiosqlite pydantic-settings
```

### ❌ 前端API调用失败

**错误信息**: `Failed to fetch textbook` 或 CORS错误

**解决方案**:

1. 检查后端服务是否运行:
   ```bash
   curl http://localhost:8000/health
   ```

2. 检查CORS配置 (`backend/app/main.py`):
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://localhost:3000"],
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

3. 使用浏览器开发者工具检查Network标签

### ❌ 数据库迁移失败

**错误信息**: `Target database is not up to date`

**解决方案**:
```bash
cd platform/backend

# 重置数据库（开发环境）
alembic downgrade base
alembic upgrade head

# 或者删除并重建容器
docker rm -f postgres-elp
# 然后重新运行步骤1
```

---

## 手动测试清单

### 后端API测试

- [ ] API文档可访问: http://localhost:8000/docs
- [ ] 创建示例数据成功
- [ ] GET /api/v1/textbooks/water-system-intro/chapter-01/case-water-tank 返回数据
- [ ] 响应包含4个sections
- [ ] sections包含code_lines映射
- [ ] starter_code字段不为空

### 前端组件测试

- [ ] 页面正常加载
- [ ] 左侧显示教材内容
- [ ] 右侧显示代码编辑器
- [ ] 分隔符可以拖拽
- [ ] 滚动教材，代码面板响应
- [ ] 代码行可以高亮显示
- [ ] 编辑代码不会崩溃
- [ ] 点击"执行代码"按钮有响应

---

## 自动化测试

### 运行后端测试

```bash
cd platform/backend

# 单元测试（需要数据库）
python test_textbook_api.py

# 集成测试（需要数据库）
python test_integration.py

# 如果想用内存数据库快速测试
# 修改test文件中的DATABASE_URL为: sqlite+aiosqlite:///:memory:
```

### 运行前端测试（未来）

```bash
cd platform/frontend

# Jest单元测试
npm test

# E2E测试（Playwright）
npm run test:e2e
```

---

## 性能验证

### API响应时间

```bash
# 使用Apache Bench测试
ab -n 100 -c 10 http://localhost:8000/api/v1/textbooks/water-system-intro/chapter-01/case-water-tank
```

**预期**: 平均响应时间 < 100ms

### 前端加载时间

在浏览器开发者工具 → Performance 中：

- **首次加载**: < 3秒
- **后续加载**: < 1秒（React Query缓存）

---

## 部署到生产环境

### 后端部署（Docker）

```bash
cd platform/backend

# 构建镜像
docker build -t elp-backend:latest .

# 运行容器
docker run -d \
  --name elp-backend \
  -p 8000:8000 \
  -e DATABASE_URL="postgresql+asyncpg://user:pass@host:5432/db" \
  elp-backend:latest
```

### 前端部署（Vercel/Netlify）

```bash
cd platform/frontend

# 构建生产版本
npm run build

# 本地预览
npm run start

# 或部署到Vercel
vercel deploy --prod
```

---

## 监控和日志

### 查看后端日志

```bash
# 实时日志
docker logs -f elp-backend

# 最近100行
docker logs --tail 100 elp-backend
```

### 数据库查询

```bash
# 进入PostgreSQL容器
docker exec -it postgres-elp psql -U elp_user -d elp_db

# 查询示例数据
SELECT * FROM books;
SELECT * FROM chapters;
SELECT * FROM cases;
```

---

## 功能演示脚本

### 展示给团队

1. **打开演示页面**: http://localhost:3000/textbook-demo

2. **讲解布局**:
   - "左侧是教材内容，使用Markdown编写，支持数学公式"
   - "右侧是Monaco代码编辑器，和VS Code一样的体验"
   - "中间的分隔符可以拖拽调整比例"

3. **演示滚动同步**:
   - 滚动教材到"物理原理"部分
   - 观察右侧代码自动滚动到对应行并高亮

4. **演示代码编辑**:
   - 修改代码中的参数（如Qin = 15.0）
   - 点击"执行代码"（展示集成点）

5. **展示响应式**:
   - 调整浏览器窗口大小
   - 展示移动端视图（开发者工具 → 设备模拟）

---

## 下一步开发任务

完成当前集成测试后，继续以下功能：

### Sprint 1剩余任务

1. **双向滚动同步** (4小时)
   - 代码滚动 → 教材自动定位
   - 实现IntersectionObserver
   - 性能优化

2. **代码执行集成** (4小时)
   - 连接执行API
   - 结果展示组件
   - 错误处理

3. **用户体验优化** (2小时)
   - 加载骨架屏
   - 平滑过渡动画
   - 快捷键支持

### Sprint 2预览

- AI助手集成（代码解释、智能提示）
- 多语言支持（Python, JavaScript, Java）
- 实时协作功能
- 学习进度追踪

---

## 获取帮助

- 📖 **完整文档**: [TEXTBOOK_FEATURE_GUIDE.md](./TEXTBOOK_FEATURE_GUIDE.md)
- 📊 **进度报告**: [SPRINT_1_PROGRESS.md](./SPRINT_1_PROGRESS.md)
- 🐛 **问题反馈**: GitHub Issues
- 💬 **技术讨论**: 项目Slack频道

---

**最后更新**: 2025-01-XX
**适用版本**: v1.0.0-sprint1
**预计完成时间**: 2天
