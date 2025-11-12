# CHS-Books 快速参考指南

**快速索引** | **一页掌握所有信息**

---

## 🚀 5分钟快速开始

```bash
# 1. 进入项目目录
cd /home/user/CHS-Books/platform

# 2. 一键启动开发环境
./start-dev.sh

# 3. 访问应用
open http://localhost:3000/textbook-demo  # 前端演示
open http://localhost:8000/docs            # API文档

# 4. 停止服务
./stop-dev.sh
```

---

## 📋 常用命令速查

### 服务管理

```bash
# 启动所有服务
./start-dev.sh

# 停止所有服务
./stop-dev.sh

# 查看演示
./demo.sh

# 查看日志
tail -f logs/backend.log
tail -f logs/frontend.log
```

### API测试

```bash
# 健康检查
curl http://localhost:8000/health

# 创建示例数据
curl -X POST http://localhost:8000/api/v1/seed

# 获取教材内容
curl http://localhost:8000/api/v1/textbooks/water-system-intro/chapter-01/case-water-tank | jq .

# 查看API文档
open http://localhost:8000/docs
```

### 开发调试

```bash
# 手动启动后端
cd backend/standalone_textbook_server
python main.py

# 手动启动前端
cd frontend
npm run dev

# 清除前端缓存
cd frontend
rm -rf .next node_modules
npm install
```

---

## 📁 项目结构速览

```
platform/
├── backend/standalone_textbook_server/  # 后端API服务器
│   ├── main.py                         # FastAPI入口
│   ├── models.py                       # 数据模型
│   ├── api.py                          # API路由
│   └── textbook_test.db                # SQLite数据库
│
├── frontend/                           # Next.js前端
│   ├── src/app/textbook-demo/         # 演示页面
│   └── src/components/InteractiveTextbook/  # 核心组件
│
├── *.md                                # 技术文档 (5800+行)
├── start-dev.sh                        # 启动脚本
├── stop-dev.sh                         # 停止脚本
└── demo.sh                             # 演示脚本
```

---

## 🌐 服务端点

| 服务 | 地址 | 用途 |
|------|------|------|
| 前端应用 | http://localhost:3000 | Next.js应用首页 |
| 演示页面 | http://localhost:3000/textbook-demo | 交互式教材演示 |
| API文档 | http://localhost:8000/docs | Swagger UI |
| 健康检查 | http://localhost:8000/health | 后端状态 |
| 创建数据 | http://localhost:8000/api/v1/seed | 初始化示例数据 |
| 获取教材 | http://localhost:8000/api/v1/textbooks/{book}/{ch}/{case} | 教材内容API |

---

## 📚 文档索引

| 文档 | 用途 | 行数 |
|------|------|------|
| **README.md** | 项目总览 | 400+ |
| **QUICK_REFERENCE.md** | 快速参考 (本文档) | 300+ |
| **DEVELOPER_GUIDE.md** | 完整开发指南 | 900+ |
| **SPRINT_1_FINAL_SUMMARY.md** | Sprint 1总结 | 757 |
| **SPRINT_2_PLAN.md** | Sprint 2规划 | 2000+ |
| **INTEGRATION_TEST_REPORT.md** | 测试报告 | 416 |
| **ENVIRONMENT_SETUP_ISSUES.md** | 环境问题 | 635 |

**阅读顺序建议**:
1. 新手: README.md → QUICK_REFERENCE.md → DEVELOPER_GUIDE.md
2. 开发: DEVELOPER_GUIDE.md → API文档 (http://localhost:8000/docs)
3. 规划: SPRINT_1_FINAL_SUMMARY.md → SPRINT_2_PLAN.md

---

## 🐛 常见问题快速解决

### 问题1: 端口被占用

```bash
# 错误: Address already in use
./stop-dev.sh

# 或手动清理
lsof -ti:8000 | xargs kill -9
lsof -ti:3000 | xargs kill -9
```

### 问题2: 数据库锁定

```bash
# 错误: database is locked
./stop-dev.sh
rm backend/standalone_textbook_server/textbook_test.db
./start-dev.sh
```

### 问题3: 前端编译错误

```bash
cd frontend
rm -rf node_modules .next
npm install
npm run dev
```

### 问题4: API返回404

```bash
# 检查后端是否运行
curl http://localhost:8000/health

# 检查环境变量
echo $NEXT_PUBLIC_API_URL

# 检查示例数据是否创建
curl -X POST http://localhost:8000/api/v1/seed
```

### 问题5: 前端显示Loading不消失

```bash
# 检查浏览器控制台错误
# 检查API是否可访问
curl http://localhost:8000/api/v1/textbooks/water-system-intro/chapter-01/case-water-tank

# 清除浏览器缓存
# Cmd/Ctrl + Shift + R (硬刷新)
```

---

## ⚡ 性能基准

| 指标 | 实际值 | 目标值 | 状态 |
|------|--------|--------|------|
| API响应 | ~40ms | <100ms | ✅ |
| DB查询 | 3次 | <5次 | ✅ |
| 前端编译 | 39.4s | <60s | ✅ |
| 热更新 | ~2s | <5s | ✅ |

---

## 🧪 测试命令

```bash
# 后端健康检查
curl http://localhost:8000/health

# 创建测试数据
curl -X POST http://localhost:8000/api/v1/seed

# 测试教材API
curl http://localhost:8000/api/v1/textbooks/water-system-intro/chapter-01/case-water-tank | jq '.sections | length'
# 应该返回: 5

# 检查sections有code_lines
curl -s http://localhost:8000/api/v1/textbooks/water-system-intro/chapter-01/case-water-tank | jq '.sections[] | select(.code_lines != null) | {id, code_lines}'

# 前端页面测试
curl -s http://localhost:3000/textbook-demo | grep "加载教材中"
```

---

## 🔧 开发工作流

### 典型开发流程

```bash
# 1. 启动环境
./start-dev.sh

# 2. 修改代码
# 后端: backend/standalone_textbook_server/*.py
# 前端: frontend/src/**/*.tsx

# 3. 自动重载
# 后端: uvicorn自动重启 (~1秒)
# 前端: Next.js热更新 (~2秒)

# 4. 测试
curl http://localhost:8000/api/endpoint
open http://localhost:3000/page

# 5. 提交
git add .
git commit -m "feat: add new feature"
git push
```

### Git提交规范

```bash
git commit -m "feat: 新功能"
git commit -m "fix: 修复bug"
git commit -m "docs: 更新文档"
git commit -m "refactor: 重构代码"
git commit -m "test: 添加测试"
git commit -m "chore: 工具更新"
```

---

## 📊 项目状态

### Sprint 1 (已完成 ✅)

- ✅ 独立Textbook API服务器
- ✅ Book-Chapter-Case数据模型
- ✅ 完整REST API (3个端点)
- ✅ InteractiveTextbook组件
- ✅ 前后端集成
- ✅ 100%测试覆盖
- ✅ 5800+行技术文档

### Sprint 2 (规划完成 📋)

**时间**: 2025-11-13 ~ 2025-11-26

**目标**:
- 🐳 Docker代码执行引擎
- 💻 Monaco Editor增强
- 🎨 UI/UX优化
- ⚡ 性能优化

**详细规划**: 查看 `SPRINT_2_PLAN.md`

---

## 🔑 关键技术

### 后端技术栈

```
FastAPI         异步Web框架
SQLAlchemy 2.0  ORM (Mapped[]语法)
SQLite          开发数据库
Pydantic        数据验证
uvicorn         ASGI服务器
```

### 前端技术栈

```
Next.js 14.0.4  React框架
TypeScript      类型安全
React Query v5  数据获取
Monaco Editor   代码编辑器
React Markdown  内容渲染
```

---

## 💡 快速提示

### 查看实时日志

```bash
# 后端日志
tail -f logs/backend.log | grep -i error

# 前端日志
tail -f logs/frontend.log | grep -i compiled

# 同时查看
tail -f logs/*.log
```

### 数据库操作

```bash
# 进入SQLite
sqlite3 backend/standalone_textbook_server/textbook_test.db

# 常用SQL命令
.tables                    # 查看所有表
SELECT * FROM books;       # 查询书籍
SELECT * FROM chapters;    # 查询章节
SELECT * FROM cases;       # 查询案例
.schema books             # 查看表结构
.exit                     # 退出
```

### 环境变量

```bash
# 后端 (.env)
ENVIRONMENT=development
DATABASE_URL=sqlite+aiosqlite:///./test.db
SECRET_KEY=dev-key
CORS_ORIGINS=["http://localhost:3000"]

# 前端 (next.config.js)
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

---

## 🎯 核心API

### GET /health

```bash
curl http://localhost:8000/health
```

**响应**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "sqlite"
}
```

### POST /api/v1/seed

```bash
curl -X POST http://localhost:8000/api/v1/seed
```

**响应**:
```json
{
  "message": "示例数据已创建",
  "book_slug": "water-system-intro",
  "chapter_slug": "chapter-01",
  "case_slug": "case-water-tank"
}
```

### GET /api/v1/textbooks/{book}/{chapter}/{case}

```bash
curl http://localhost:8000/api/v1/textbooks/water-system-intro/chapter-01/case-water-tank
```

**响应结构**:
```json
{
  "book_slug": "water-system-intro",
  "chapter_slug": "chapter-01",
  "case_slug": "case-water-tank",
  "title": "案例1：水箱实验",
  "sections": [
    {
      "id": "实验目标",
      "title": "实验目标",
      "content": "...",
      "code_lines": null,
      "order": 0
    }
  ],
  "starter_code": "# Python代码",
  "tags": ["水箱", "质量守恒"]
}
```

---

## 🔍 调试技巧

### 后端调试

```python
# 添加断点
import pdb; pdb.set_trace()

# 查看SQL
# database.py中设置 echo=True
engine = create_async_engine(..., echo=True)

# 日志级别
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 前端调试

```typescript
// Console调试
console.log('API URL:', process.env.NEXT_PUBLIC_API_URL)

// React Query DevTools
// 安装: npm install @tanstack/react-query-devtools
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'

// Network调试
// Chrome DevTools → Network → XHR
```

---

## 📞 获取帮助

### 文档资源

- 快速开始: README.md
- 开发指南: DEVELOPER_GUIDE.md
- API文档: http://localhost:8000/docs
- Sprint规划: SPRINT_2_PLAN.md

### 命令帮助

```bash
# 查看脚本帮助
./start-dev.sh --help  # (如果实现了)

# 查看Python帮助
python backend/standalone_textbook_server/main.py --help

# 查看npm脚本
cd frontend && npm run
```

### 常用资源

- FastAPI文档: https://fastapi.tiangolo.com/
- Next.js文档: https://nextjs.org/docs
- React Query文档: https://tanstack.com/query/latest
- Monaco Editor文档: https://microsoft.github.io/monaco-editor/

---

## ✅ 检查清单

### 开发环境就绪

- [ ] Python 3.11+ 已安装
- [ ] Node.js 18.0+ 已安装
- [ ] npm 9.0+ 已安装
- [ ] 端口8000和3000空闲
- [ ] 已克隆项目代码

### 首次启动

- [ ] 运行 `./start-dev.sh`
- [ ] 访问 http://localhost:8000/docs
- [ ] 访问 http://localhost:3000/textbook-demo
- [ ] 测试API: `curl http://localhost:8000/health`
- [ ] 创建数据: `curl -X POST http://localhost:8000/api/v1/seed`

### 开发准备

- [ ] 阅读 README.md
- [ ] 阅读 DEVELOPER_GUIDE.md
- [ ] 了解项目结构
- [ ] 熟悉API端点
- [ ] 配置编辑器 (VS Code推荐)

---

## 🎉 快速成功体验

**5分钟体验完整功能**:

```bash
# 1. 启动 (30秒)
cd /home/user/CHS-Books/platform
./start-dev.sh

# 2. 创建数据 (1秒)
curl -X POST http://localhost:8000/api/v1/seed

# 3. 测试API (1秒)
curl http://localhost:8000/api/v1/textbooks/water-system-intro/chapter-01/case-water-tank | jq '.sections | length'

# 4. 访问演示 (浏览器)
open http://localhost:3000/textbook-demo

# 5. 查看API文档 (浏览器)
open http://localhost:8000/docs

# ✅ 成功！所有功能正常运行
```

---

**最后更新**: 2025-11-12
**维护者**: CHS-Books开发团队
**状态**: ✅ Sprint 1完成，Sprint 2就绪
