# Engineering Learning Platform (ELP)

**版本**: v1.0.0-MVP  
**状态**: 开发中  
**类型**: 商业化学习平台

## 项目简介

智能工程教学平台 - 集教材学习、交互式工具和AI助手于一体的专业学习平台。

### 核心特性

- 📚 **系统化教材**: 完整的知识体系，从入门到精通
- 🛠️ **交互式工具**: 每个案例都有可运行的在线工具
- 🤖 **AI助手**: 基于RAG的智能学习助手
- 🔄 **自动更新**: 自动扫描项目内容，实时同步
- 💳 **支付集成**: 支持多种支付方式
- 🔒 **权限管理**: 完善的用户权限和内容访问控制

## 技术栈

### 后端
- **框架**: FastAPI 0.104+
- **数据库**: PostgreSQL 15 + MongoDB 6
- **缓存**: Redis 7
- **任务队列**: Celery + Redis
- **ORM**: SQLAlchemy 2.0
- **认证**: JWT + OAuth2

### 前端
- **框架**: React 18 + Next.js 14
- **语言**: TypeScript 5
- **UI库**: Ant Design 5
- **状态管理**: Zustand
- **数据请求**: TanStack Query
- **图表**: Plotly.js + Recharts

### 基础设施
- **容器化**: Docker + Docker Compose
- **脚本执行**: Docker沙箱隔离
- **对象存储**: MinIO (S3兼容)
- **监控**: Prometheus + Grafana
- **日志**: ELK Stack

### AI服务
- **LLM**: OpenAI GPT-4 / Claude / 文心一言
- **向量数据库**: Weaviate / Pinecone
- **Embedding**: text-embedding-3-small

## 项目结构

```
platform/
├── backend/                 # 后端服务
│   ├── app/
│   │   ├── api/            # API路由
│   │   ├── core/           # 核心配置
│   │   ├── models/         # 数据模型
│   │   ├── services/       # 业务逻辑
│   │   ├── schemas/        # Pydantic schemas
│   │   └── utils/          # 工具函数
│   ├── alembic/            # 数据库迁移
│   ├── tests/              # 测试
│   ├── requirements.txt
│   └── main.py
│
├── frontend/               # 前端应用
│   ├── src/
│   │   ├── components/     # React组件
│   │   ├── pages/          # Next.js页面
│   │   ├── services/       # API服务
│   │   ├── stores/         # 状态管理
│   │   ├── styles/         # 样式
│   │   └── utils/          # 工具函数
│   ├── public/             # 静态资源
│   ├── package.json
│   └── next.config.js
│
├── scanner/                # 内容扫描器
│   ├── core/
│   │   ├── book_scanner.py
│   │   ├── case_parser.py
│   │   └── code_analyzer.py
│   ├── config.py
│   └── main.py
│
├── executor/               # 脚本执行引擎
│   ├── docker/
│   │   └── Dockerfile.runner
│   ├── engine.py
│   ├── sandbox.py
│   └── resource_limiter.py
│
├── ai_service/             # AI服务
│   ├── rag/
│   │   ├── embeddings.py
│   │   ├── retriever.py
│   │   └── generator.py
│   ├── agents/
│   │   ├── qa_agent.py
│   │   ├── tool_agent.py
│   │   └── tutor_agent.py
│   └── main.py
│
├── shared/                 # 共享代码
│   ├── config/
│   ├── schemas/
│   └── utils/
│
├── docker/                 # Docker配置
│   ├── docker-compose.yml
│   ├── docker-compose.prod.yml
│   └── nginx/
│       └── nginx.conf
│
├── scripts/                # 运维脚本
│   ├── init_db.py
│   ├── seed_data.py
│   └── backup.sh
│
├── docs/                   # 文档
│   ├── API.md
│   ├── DEPLOYMENT.md
│   └── DEVELOPMENT.md
│
├── .env.example
├── .gitignore
└── README.md
```

## 快速开始

### 环境要求

- Python 3.11+
- Node.js 18+
- Docker 24+
- PostgreSQL 15+
- Redis 7+

### 开发环境设置

```bash
# 1. 克隆项目
git clone <repository-url>
cd platform

# 2. 复制环境配置
cp .env.example .env

# 3. 启动服务（Docker Compose）
docker-compose up -d

# 4. 初始化数据库
python scripts/init_db.py

# 5. 扫描内容
python scanner/main.py --scan-all

# 6. 访问应用
# 前端: http://localhost:3000
# 后端API: http://localhost:8000
# API文档: http://localhost:8000/docs
```

### 手动开发模式

#### 后端

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

#### 前端

```bash
cd frontend
npm install
npm run dev
```

## 开发指南

### 代码规范

- **Python**: PEP 8, Black格式化, MyPy类型检查
- **TypeScript**: ESLint + Prettier
- **Git提交**: Conventional Commits规范

### 测试

```bash
# 后端测试
cd backend
pytest tests/ -v --cov

# 前端测试
cd frontend
npm run test
```

### 数据库迁移

```bash
cd backend
alembic revision --autogenerate -m "描述"
alembic upgrade head
```

## 部署

### 生产环境部署

```bash
# 使用Docker Compose
docker-compose -f docker/docker-compose.prod.yml up -d

# 或使用Kubernetes
kubectl apply -f k8s/
```

详见 [部署文档](docs/DEPLOYMENT.md)

## API文档

启动后端服务后访问:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 安全性

- ✅ JWT认证
- ✅ CORS配置
- ✅ SQL注入防护（ORM参数化查询）
- ✅ XSS防护（前端转义）
- ✅ CSRF防护
- ✅ 速率限制
- ✅ Docker沙箱隔离
- ✅ 敏感数据加密

## 性能优化

- ✅ Redis缓存
- ✅ 数据库索引优化
- ✅ CDN静态资源
- ✅ 图片懒加载
- ✅ API响应压缩
- ✅ 数据库连接池

## 监控与日志

- **性能监控**: Prometheus + Grafana
- **日志聚合**: ELK Stack
- **错误追踪**: Sentry
- **用户行为分析**: Google Analytics / Mixpanel

## 许可证

商业许可证 - 保留所有权利

## 联系方式

- 邮箱: support@example.com
- 官网: https://www.example.com
- 文档: https://docs.example.com

---

**开发者**: AI Engineering Team  
**最后更新**: 2025-10-31
