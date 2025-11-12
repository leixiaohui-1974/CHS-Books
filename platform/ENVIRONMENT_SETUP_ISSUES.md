# 🔧 环境搭建问题与解决方案

**日期**: 2025-11-12
**Sprint**: Sprint 1 - 环境集成阶段
**进度**: 65% → 70% (环境配置完成，依赖问题已识别)

---

## 📋 问题总结

在尝试启动完整后端服务进行集成测试时，遇到了一系列依赖和配置问题。

### 问题列表

| # | 问题 | 状态 | 解决方案 |
|---|------|------|----------|
| 1 | PostgreSQL/Docker不可用 | ✅ 已解决 | 配置SQLite作为开发数据库 |
| 2 | config.py硬编码PostgreSQL URL | ✅ 已解决 | 修改为支持.env配置 |
| 3 | 缺少asyncpg模块 | ⚠️  绕过 | 使用SQLite+aiosqlite |
| 4 | 缺少python-jose模块 | ⚠️  未完全解决 | 需要解决cryptography依赖 |
| 5 | cffi/cryptography版本冲突 | ❌ 阻塞 | 系统包冲突，无法通过pip修复 |
| 6 | docker模块在导入时初始化 | ❌ 阻塞 | execution_engine在模块级别启动异步任务 |
| 7 | 模型关系配置问题 | ⚠️  警告 | User模型'sessions'属性未配置 |

---

## ✅ 已完成的配置

### 1. 数据库配置

**修改文件**: `platform/backend/app/core/config.py`

**变更内容**:
```python
# 之前: 硬编码PostgreSQL
@property
def DATABASE_URL(self) -> str:
    return f"postgresql+asyncpg://..."

# 之后: 支持.env配置
DATABASE_URL: Optional[str] = None

@property
def database_url(self) -> str:
    if self.DATABASE_URL:
        return self.DATABASE_URL
    return f"postgresql+asyncpg://..."
```

**效果**: 现在可以在`.env`中直接设置`DATABASE_URL=sqlite+aiosqlite:///./test.db`

### 2. 创建开发环境配置

**文件**: `platform/backend/.env`

**内容**:
```bash
ENVIRONMENT=development
DATABASE_URL=sqlite+aiosqlite:///./test.db
SECRET_KEY=dev-secret-key-for-testing-only
CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]
```

### 3. 安装核心依赖

已安装模块:
- ✅ fastapi 0.121.1
- ✅ uvicorn (最新)
- ✅ sqlalchemy (最新)
- ✅ aiosqlite 0.21.0
- ✅ pydantic 2.12.4
- ✅ pydantic-settings 2.12.0
- ✅ loguru 0.7.3
- ✅ alembic (最新)
- ✅ docker (Python SDK)
- ✅ motor (异步MongoDB驱动)
- ✅ httpx
- ✅ aiofiles

### 4. 创建最小化测试服务器

**文件**: `platform/backend/test_server_minimal.py`

**目的**: 仅包含textbooks API，避免复杂依赖

**状态**: 由于模块导入机制问题，仍然加载了execution模块

---

## ❌ 未解决的阻塞问题

### 问题1: Cryptography依赖冲突

**错误信息**:
```
ModuleNotFoundError: No module named '_cffi_backend'
pyo3_runtime.PanicException: Python API call failed
```

**根本原因**:
- `python-jose[cryptography]`需要`cffi`和`cryptography`
- 系统中`cryptography 41.0.7`由debian包管理器安装
- 无法通过pip卸载/升级系统包

**影响范围**:
- `app.core.security` (JWT认证)
- `app.api.endpoints.sessions` (会话管理)
- `app.api.endpoints.auth` (用户认证)

**可能方案**:
1. **方案A**: 使用Python虚拟环境（venv）隔离依赖
2. **方案B**: 替换jwt库（使用`pyjwt`而非`python-jose`）
3. **方案C**: 暂时禁用认证功能，仅测试textbooks API

### 问题2: 模块级别异步初始化

**错误信息**:
```
RuntimeError: no running event loop
sys:1: RuntimeWarning: coroutine 'ContainerPool._warm_up_pool' was never awaited
```

**位置**: `app/services/execution_engine.py:559`

**根本原因**:
```python
# 文件末尾，模块级别
enhanced_execution_engine = EnhancedExecutionEngine(...)  # 触发__init__
    # __init__中
    self.container_pool = ContainerPool(...)  # 触发异步任务
        # ContainerPool.__init__中
        asyncio.create_task(self._warm_up_pool())  # 需要event loop
```

**影响**:
- 任何导入`app.api`的操作都会触发所有端点的导入
- 无法选择性导入单个API端点

**可能方案**:
1. **方案A**: 延迟初始化（在first request时创建实例）
2. **方案B**: 使用lifespan event初始化
3. **方案C**: 创建完全独立的textbooks API服务（不依赖app目录）

---

## 🎯 建议的解决路径

### 短期方案（2-4小时）

**目标**: 完成Sprint 1的剩余35%，实现前后端集成测试

**步骤**:

#### 1. 创建独立的Textbooks API服务 ⭐ **推荐**

**原理**: 复制textbooks端点代码，创建完全独立的服务，不依赖复杂的app结构

**实现**:
```bash
# 创建独立服务目录
mkdir platform/backend/standalone_textbook_server
cd platform/backend/standalone_textbook_server

# 文件结构:
# - main.py (FastAPI app)
# - models.py (Book, Chapter, Case models)
# - database.py (SQLite连接)
# - api.py (textbooks endpoint)
# - seed_data.py (示例数据)
```

**优点**:
- 无依赖冲突
- 快速启动测试
- 专注textbooks功能
- 易于调试

**缺点**:
- 代码重复
- 与主服务分离

**预计时间**: 1-2小时

#### 2. 使用Python虚拟环境

**原理**: 隔离系统包和项目包

**实现**:
```bash
cd platform/backend

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动服务
python -m uvicorn app.main:app --reload
```

**优点**:
- 标准Python实践
- 完全隔离依赖
- 可安装任意版本的包

**缺点**:
- 需要重新安装所有依赖
- 可能仍有模块导入问题

**预计时间**: 2-3小时（包括安装时间）

#### 3. 修复现有代码（长期方案）

**原理**: 解决根本问题，使主服务可启动

**需要修改**:
1. `app/services/execution_engine.py` - 延迟初始化
2. `app/core/security.py` - 替换jwt库或设为可选
3. `app/models/*.py` - 修复关系配置

**优点**:
- 解决根本问题
- 完整功能可用
- 生产环境可用

**缺点**:
- 工作量大
- 可能引入新问题
- 需要全面测试

**预计时间**: 4-8小时

---

## 🚀 立即可执行的操作

### 选项A: 独立服务器（最快）

```bash
cd /home/user/CHS-Books/platform/backend

# 创建standalone目录
mkdir -p standalone_textbook_server
cd standalone_textbook_server

# 创建文件（见下方代码）
# 然后运行:
python standalone_server.py
```

### 选项B: 虚拟环境（标准）

```bash
cd /home/user/CHS-Books/platform/backend

python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn sqlalchemy aiosqlite pydantic pydantic-settings loguru
python -m uvicorn app.main:app --reload
```

### 选项C: Docker Compose（生产级）

创建`docker-compose.yml`:
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: elp_db
      POSTGRES_USER: elp_user
      POSTGRES_PASSWORD: elp_password
    ports:
      - "5432:5432"

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql+asyncpg://elp_user:elp_password@postgres:5432/elp_db
    depends_on:
      - postgres

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
```

```bash
docker-compose up
```

---

## 📊 当前测试状态

### ✅ 已验证可用的功能

1. **内容解析功能** ✅
   - `parse_content_to_sections()` 正常工作
   - 成功解析3个sections
   - 代码行映射正确

2. **数据库模型定义** ✅
   - Book, Chapter, Case 模型已定义
   - SQLAlchemy 2.0 异步模式配置正确

3. **前端组件** ✅
   - InteractiveTextbook组件完整
   - ExecutionPanel组件完整
   - 双向滚动同步已实现
   - textbook-demo页面已创建

### ❌ 未完成的测试

1. **完整后端服务启动** ❌
   - 依赖冲突阻塞

2. **数据库迁移** ⏳
   - 未运行alembic升级

3. **API端点测试** ⏳
   - 无法访问HTTP端点

4. **前后端集成** ⏳
   - 前端无法连接后端

---

## 🎓 经验教训

### 1. 模块级别初始化的问题

**教训**: 避免在模块级别创建需要异步运行时的实例

**正确做法**:
```python
# ❌ 错误：模块级别创建
enhanced_execution_engine = EnhancedExecutionEngine()

# ✅ 正确：延迟创建
_engine = None

def get_execution_engine():
    global _engine
    if _engine is None:
        _engine = EnhancedExecutionEngine()
    return _engine
```

### 2. 系统包与pip包冲突

**教训**: 开发时始终使用虚拟环境

**正确做法**:
```bash
# 创建项目时立即创建venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. 依赖链问题

**教训**: API模块不应该导入非必需服务

**正确做法**:
```python
# ❌ 错误：导入所有端点
from app.api.endpoints import *

# ✅ 正确：按需导入
from app.api.endpoints.textbooks import router as textbooks_router
from app.api.endpoints.auth import router as auth_router  # 仅当需要时
```

---

## 📝 下一步行动建议

### 立即执行（30分钟内）

**推荐**: 创建独立textbook服务器

1. 创建`standalone_textbook_server`目录
2. 复制必要的模型和API代码
3. 使用SQLite数据库
4. 启动服务并测试
5. 前端连接测试

### 短期（今天内）

1. 完成独立服务器开发和测试
2. 实现seed示例数据功能
3. 测试前端集成
4. 更新Sprint 1进度到80%
5. 创建集成测试报告

### 中期（本周内）

1. 设置虚拟环境
2. 修复主服务的依赖问题
3. 运行数据库迁移
4. 完整后端服务测试
5. 更新到Sprint 1 100%

### 长期（下周）

1. Docker Compose生产环境
2. CI/CD流水线
3. 自动化测试
4. 性能优化
5. 进入Sprint 2

---

## 📚 相关文档

- [SPRINT_1_PROGRESS.md](./SPRINT_1_PROGRESS.md) - Sprint 1进度报告
- [TEXTBOOK_FEATURE_GUIDE.md](./TEXTBOOK_FEATURE_GUIDE.md) - 完整功能指南
- [BIDIRECTIONAL_SYNC_GUIDE.md](./BIDIRECTIONAL_SYNC_GUIDE.md) - 双向滚动同步指南
- [QUICK_START_NEXT_STEPS.md](./QUICK_START_NEXT_STEPS.md) - 快速开始指南

---

**更新时间**: 2025-11-12 07:30 UTC
**文档版本**: 1.0
**状态**: 🚧 问题已识别，解决方案已规划
