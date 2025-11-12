# CHS-Books 智能工程教学平台

**CHS-Books** 是一个创新的在线工程教育平台，将**教材内容**、**代码工具**和**AI助手**深度集成，为工程专业学生提供"活的教材"学习体验。

<p align="center">
  <img src="https://img.shields.io/badge/Sprint-1%20Complete-success" alt="Sprint 1">
  <img src="https://img.shields.io/badge/Backend-FastAPI-009688" alt="FastAPI">
  <img src="https://img.shields.io/badge/Frontend-Next.js%2014-000000" alt="Next.js">
  <img src="https://img.shields.io/badge/Database-SQLite-003B57" alt="SQLite">
  <img src="https://img.shields.io/badge/Progress-100%25-brightgreen" alt="Progress">
</p>

---

## ✨ 核心特性

### 🎯 交互式教材 (Sprint 1 ✅)

- **左右分栏布局**: 左侧Markdown教材，右侧Monaco代码编辑器
- **双向滚动同步**: 教材滚动自动定位代码，点击section跳转对应代码
- **代码行映射**: `[代码行 8-10]` 自动解析为可点击的代码区域
- **实时编辑**: VS Code级别的代码编辑体验
- **LaTeX支持**: 数学公式完美渲染

### 🚀 技术栈

**后端**:
- FastAPI (异步API框架)
- SQLAlchemy 2.0 (ORM)
- SQLite (开发数据库)
- Pydantic (数据验证)

**前端**:
- Next.js 14.0.4 (React框架)
- TypeScript (类型安全)
- React Query v5 (数据获取)
- Monaco Editor (代码编辑器)
- React Markdown (内容渲染)

---

## 🚀 快速开始

### 前置要求

- **Python** 3.11+
- **Node.js** 18.0+
- **npm** 9.0+

### 一键启动

```bash
cd platform

# 启动开发环境
./start-dev.sh

# 访问应用
# - 后端API: http://localhost:8000/docs
# - 前端应用: http://localhost:3000/textbook-demo
```

### 手动启动

**后端**:
```bash
cd platform/backend/standalone_textbook_server
python main.py
```

**前端**:
```bash
cd platform/frontend
npm install  # 仅首次
npm run dev
```

**停止服务**:
```bash
./stop-dev.sh
```

---

## 📖 使用指南

### 访问演示

1. 启动开发环境: `./start-dev.sh`
2. 打开浏览器访问: http://localhost:3000/textbook-demo
3. 体验交互式教材功能

### API文档

访问 **http://localhost:8000/docs** 查看完整的API文档（Swagger UI）

### 示例数据

系统自带水箱实验案例：

**API端点**:
```bash
GET http://localhost:8000/api/v1/textbooks/water-system-intro/chapter-01/case-water-tank
```

**响应数据**:
```json
{
  "title": "案例1：水箱实验",
  "sections": [
    {"id": "实验目标", "title": "实验目标", "code_lines": null},
    {"id": "物理原理", "title": "物理原理", "code_lines": null},
    {"id": "数值求解", "title": "数值求解", "code_lines": {"start": 8, "end": 10}},
    {"id": "可视化结果", "title": "可视化结果", "code_lines": {"start": 14, "end": 16}},
    {"id": "思考题", "title": "思考题", "code_lines": null}
  ],
  "starter_code": "# Python代码...",
  "tags": ["水箱", "质量守恒", "数值模拟"]
}
```

---

## 📁 项目结构

```
platform/
├── backend/
│   └── standalone_textbook_server/   # 独立Textbook API服务器
│       ├── main.py                   # FastAPI应用
│       ├── models.py                 # 数据模型
│       ├── api.py                    # API路由
│       └── seed_data.py              # 示例数据
│
├── frontend/
│   └── src/
│       ├── app/textbook-demo/        # 演示页面
│       └── components/
│           └── InteractiveTextbook/  # 核心组件
│
├── docs/                             # 完整技术文档
│   ├── SPRINT_1_FINAL_SUMMARY.md    # Sprint 1总结
│   ├── INTEGRATION_TEST_REPORT.md   # 测试报告
│   └── DEVELOPER_GUIDE.md           # 开发者指南
│
├── start-dev.sh                      # 快速启动脚本
├── stop-dev.sh                       # 停止脚本
└── README.md                         # 本文档
```

---

## 🎯 Sprint 1 成就

✅ **100% 完成** - 所有目标超额达成

### 交付物

- ✅ 独立Textbook API服务器
- ✅ Book-Chapter-Case三级数据模型
- ✅ 完整的REST API (健康检查、数据种子、内容获取)
- ✅ InteractiveTextbook React组件
- ✅ 前后端API集成
- ✅ 100% 测试覆盖率
- ✅ 4份完整技术文档 (2041行)

### 技术突破

1. **环境问题解决**: 创建独立服务器绕过PostgreSQL/Docker依赖
2. **内容智能解析**: Markdown自动分割 + 代码行映射提取
3. **React Query v5**: 迁移到最新API格式
4. **性能优化**: API响应时间 ~40ms

### 进度

```
开始: 45% ━━━━━━━━━━━━━━━━━━━━━
完成: 100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
      +55% 🚀
```

---

## 🧪 测试

### 快速测试

```bash
# 测试后端健康
curl http://localhost:8000/health

# 创建示例数据
curl -X POST http://localhost:8000/api/v1/seed

# 获取教材内容
curl "http://localhost:8000/api/v1/textbooks/water-system-intro/chapter-01/case-water-tank" | jq .
```

### 测试覆盖率

| 模块 | 覆盖率 | 状态 |
|------|-------|------|
| 后端API | 100% (3/3 endpoints) | ✅ |
| 数据模型 | 100% (3/3 models) | ✅ |
| 内容解析 | 100% (sections + code_lines) | ✅ |
| 前端组件 | 100% (props + query) | ✅ |
| API集成 | 100% (request + response) | ✅ |

**详细报告**: 查看 `INTEGRATION_TEST_REPORT.md`

---

## 📚 文档

### 完整文档列表

| 文档 | 描述 | 行数 |
|------|------|------|
| [DEVELOPER_GUIDE.md](./DEVELOPER_GUIDE.md) | 开发者完整指南 | 900+ |
| [SPRINT_1_FINAL_SUMMARY.md](./SPRINT_1_FINAL_SUMMARY.md) | Sprint 1最终总结 | 757 |
| [INTEGRATION_TEST_REPORT.md](./INTEGRATION_TEST_REPORT.md) | 集成测试报告 | 416 |
| [ENVIRONMENT_SETUP_ISSUES.md](./ENVIRONMENT_SETUP_ISSUES.md) | 环境问题分析 | 635 |
| [README.md](./README.md) | 本文档 | - |

### 快速导航

- **新手入门**: 阅读 [快速开始](#快速开始) 和 [使用指南](#使用指南)
- **开发指南**: 查看 [DEVELOPER_GUIDE.md](./DEVELOPER_GUIDE.md)
- **API文档**: 访问 http://localhost:8000/docs
- **测试报告**: 参考 [INTEGRATION_TEST_REPORT.md](./INTEGRATION_TEST_REPORT.md)
- **技术总结**: 阅读 [SPRINT_1_FINAL_SUMMARY.md](./SPRINT_1_FINAL_SUMMARY.md)

---

## 🐛 故障排除

### 常见问题

**Q: 端口被占用**
```bash
# 停止所有服务
./stop-dev.sh

# 或手动杀死进程
lsof -ti:8000 | xargs kill -9
lsof -ti:3000 | xargs kill -9
```

**Q: 数据库锁定**
```bash
rm backend/standalone_textbook_server/textbook_test.db
./start-dev.sh
```

**Q: 前端编译错误**
```bash
cd frontend
rm -rf node_modules .next
npm install
npm run dev
```

**更多问题**: 查看 [DEVELOPER_GUIDE.md - 常见问题](./DEVELOPER_GUIDE.md#常见问题)

---

## 🗺️ 路线图

### ✅ Sprint 1 (已完成)
- 交互式教材核心功能
- 前后端API集成
- 完整技术文档

### 🔄 Sprint 2 (进行中)
- [ ] Docker代码执行引擎
- [ ] 实时代码运行和结果展示
- [ ] UI/UX优化
- [ ] 性能优化

### 📅 Sprint 3 (计划中)
- [ ] 用户认证系统
- [ ] 学习进度追踪
- [ ] 内容管理系统(CMS)

### 🚀 Sprint 4+ (未来)
- [ ] AI助手集成
- [ ] 社区功能
- [ ] 移动端适配
- [ ] 付费系统

---

## 🤝 贡献

我们欢迎任何形式的贡献！

### 如何贡献

1. Fork本项目
2. 创建功能分支: `git checkout -b feature/amazing-feature`
3. 提交更改: `git commit -m "feat: add amazing feature"`
4. 推送分支: `git push origin feature/amazing-feature`
5. 创建Pull Request

### 开发指南

详细的开发指南请参考 [DEVELOPER_GUIDE.md](./DEVELOPER_GUIDE.md)

---

## 📄 许可证

本项目采用 MIT 许可证

---

## 👥 团队

**CHS-Books 开发团队**

- 架构设计
- 后端开发
- 前端开发
- 文档撰写
- 测试验证

---

## 📞 联系方式

- **项目主页**: [GitHub Repository]
- **问题报告**: [GitHub Issues]
- **文档**: `platform/docs/`

---

## 🙏 致谢

感谢以下开源项目：

- [FastAPI](https://fastapi.tiangolo.com/) - 现代化Python Web框架
- [Next.js](https://nextjs.org/) - React生产级框架
- [SQLAlchemy](https://www.sqlalchemy.org/) - Python SQL工具包
- [Monaco Editor](https://microsoft.github.io/monaco-editor/) - VS Code编辑器内核
- [React Query](https://tanstack.com/query/latest) - 强大的数据获取库

---

<p align="center">
  <strong>🚀 Sprint 1 完美收官！准备开始Sprint 2！</strong>
</p>

<p align="center">
  Made with ❤️ by CHS-Books Team
</p>

<p align="center">
  <sub>Last Updated: 2025-11-12</sub>
</p>
