# CHS-Books 开发者指南

**版本**: Sprint 1
**更新时间**: 2025-11-12
**适用范围**: 独立Textbook API服务器开发环境

---

## 📋 目录

1. [快速开始](#快速开始)
2. [项目结构](#项目结构)
3. [环境配置](#环境配置)
4. [开发工作流](#开发工作流)
5. [API开发指南](#api开发指南)
6. [前端开发指南](#前端开发指南)
7. [测试指南](#测试指南)
8. [调试技巧](#调试技巧)
9. [常见问题](#常见问题)
10. [最佳实践](#最佳实践)

---

## 🚀 快速开始

### 前置要求

- **Python**: 3.11+
- **Node.js**: 18.0+
- **npm**: 9.0+
- **操作系统**: Linux / macOS / WSL2

### 一键启动

```bash
cd /home/user/CHS-Books/platform

# 启动开发环境
./start-dev.sh

# 停止开发环境
./stop-dev.sh
```

### 手动启动

**启动后端**:
```bash
cd platform/backend/standalone_textbook_server
python main.py
# 访问: http://localhost:8000/docs
```

**启动前端**:
```bash
cd platform/frontend
npm install  # 仅首次需要
npm run dev
# 访问: http://localhost:3000/textbook-demo
```

---

## 📁 项目结构

```
platform/
├── backend/
│   ├── standalone_textbook_server/    # 独立Textbook API服务器
│   │   ├── main.py                   # FastAPI应用入口
│   │   ├── models.py                 # SQLAlchemy数据模型
│   │   ├── database.py               # 数据库连接管理
│   │   ├── api.py                    # API路由和业务逻辑
│   │   ├── seed_data.py              # 示例数据生成
│   │   ├── README.md                 # 服务器文档
│   │   └── textbook_test.db          # SQLite数据库文件
│   ├── app/                          # 主服务器（未使用）
│   └── .env                          # 环境变量配置
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   └── textbook-demo/        # 演示页面
│   │   │       └── page.tsx
│   │   └── components/
│   │       └── InteractiveTextbook/  # 交互式教材组件
│   │           └── InteractiveTextbook.tsx
│   ├── package.json                  # 依赖配置
│   └── next.config.js               # Next.js配置
│
├── docs/                            # 技术文档
│   ├── ENVIRONMENT_SETUP_ISSUES.md  # 环境问题分析
│   ├── SPRINT_1_COMPLETION_SUMMARY.md
│   ├── INTEGRATION_TEST_REPORT.md
│   └── SPRINT_1_FINAL_SUMMARY.md
│
├── start-dev.sh                     # 快速启动脚本
├── stop-dev.sh                      # 停止服务脚本
├── DEVELOPER_GUIDE.md              # 开发者指南（本文档）
├── logs/                            # 服务日志
│   ├── backend.log
│   └── frontend.log
└── .pids/                           # 进程PID文件
    ├── backend.pid
    └── frontend.pid
```

---

## ⚙️ 环境配置

### 后端环境变量

创建 `platform/backend/.env` 文件：

```bash
# 环境模式
ENVIRONMENT=development

# 数据库配置（SQLite）
DATABASE_URL=sqlite+aiosqlite:///./test.db

# 安全配置
SECRET_KEY=dev-secret-key-for-testing-only-change-in-production-12345678

# CORS配置
CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]
```

### 前端环境变量

在 `platform/frontend/next.config.js` 中配置：

```javascript
env: {
  NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  NEXT_PUBLIC_WS_URL: process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000',
}
```

或创建 `.env.local` 文件：

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

---

## 🔄 开发工作流

### 典型开发流程

1. **启动开发环境**
   ```bash
   ./start-dev.sh
   ```

2. **修改代码**
   - 后端代码修改后自动重载（uvicorn --reload）
   - 前端代码修改后自动热更新（Next.js HMR）

3. **测试API**
   ```bash
   # 健康检查
   curl http://localhost:8000/health

   # 获取教材内容
   curl http://localhost:8000/api/v1/textbooks/water-system-intro/chapter-01/case-water-tank | jq .
   ```

4. **查看日志**
   ```bash
   # 实时查看后端日志
   tail -f logs/backend.log

   # 实时查看前端日志
   tail -f logs/frontend.log
   ```

5. **提交代码**
   ```bash
   git add .
   git commit -m "描述性提交信息"
   git push origin <分支名>
   ```

### 代码热重载

- **后端**: 修改Python文件后，uvicorn自动重启（~1秒）
- **前端**: 修改React组件后，浏览器自动刷新（~2秒）

---

## 🌐 API开发指南

### 添加新的API端点

1. **在 `api.py` 中定义路由**:

```python
from fastapi import APIRouter

router = APIRouter()

@router.get("/new-endpoint")
async def new_endpoint():
    """新端点描述"""
    return {"message": "Hello World"}
```

2. **在 `main.py` 中注册路由**:

```python
from api import router as my_router

app.include_router(my_router, prefix="/api/v1", tags=["MyTag"])
```

3. **测试端点**:

```bash
curl http://localhost:8000/api/v1/new-endpoint
```

4. **查看API文档**:

访问 http://localhost:8000/docs（Swagger UI）

### 数据库操作

**查询示例**:

```python
from sqlalchemy import select
from database import get_db
from models import Book

async def get_book_by_slug(slug: str, db: AsyncSession):
    """根据slug查询书籍"""
    stmt = select(Book).where(Book.slug == slug)
    result = await db.execute(stmt)
    book = result.scalar_one_or_none()
    return book
```

**创建记录**:

```python
async def create_book(book_data: dict, db: AsyncSession):
    """创建新书籍"""
    book = Book(**book_data)
    db.add(book)
    await db.commit()
    await db.refresh(book)
    return book
```

### 错误处理

```python
from fastapi import HTTPException

@router.get("/books/{slug}")
async def get_book(slug: str, db: AsyncSession = Depends(get_db)):
    book = await get_book_by_slug(slug, db)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book
```

---

## ⚛️ 前端开发指南

### 组件开发

**创建新组件**:

```typescript
// src/components/MyComponent/MyComponent.tsx
'use client'

import React from 'react'

interface MyComponentProps {
  title: string
  onAction: () => void
}

export const MyComponent: React.FC<MyComponentProps> = ({ title, onAction }) => {
  return (
    <div>
      <h1>{title}</h1>
      <button onClick={onAction}>Click Me</button>
    </div>
  )
}
```

### API调用（React Query）

```typescript
'use client'

import { useQuery } from '@tanstack/react-query'

export function MyComponent() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['myData'],
    queryFn: async () => {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await fetch(`${apiUrl}/api/v1/my-endpoint`)
      if (!response.ok) {
        throw new Error('API request failed')
      }
      return response.json()
    }
  })

  if (isLoading) return <div>Loading...</div>
  if (error) return <div>Error: {error.message}</div>

  return <div>{JSON.stringify(data)}</div>
}
```

### 样式管理

**使用CSS Modules**:

```css
/* MyComponent.module.css */
.container {
  padding: 20px;
  background: #f0f0f0;
}

.title {
  font-size: 24px;
  color: #333;
}
```

```typescript
import styles from './MyComponent.module.css'

export function MyComponent() {
  return (
    <div className={styles.container}>
      <h1 className={styles.title}>Title</h1>
    </div>
  )
}
```

---

## 🧪 测试指南

### 后端测试

**手动API测试**:

```bash
# 健康检查
curl http://localhost:8000/health

# 创建示例数据
curl -X POST http://localhost:8000/api/v1/seed

# 获取教材内容
curl "http://localhost:8000/api/v1/textbooks/water-system-intro/chapter-01/case-water-tank" | jq .

# 查看响应头
curl -I http://localhost:8000/health
```

**使用pytest（未来）**:

```python
# tests/test_api.py
import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
```

### 前端测试

**组件测试（未来）**:

```typescript
// __tests__/MyComponent.test.tsx
import { render, screen } from '@testing-library/react'
import { MyComponent } from '../MyComponent'

describe('MyComponent', () => {
  it('renders title correctly', () => {
    render(<MyComponent title="Test Title" onAction={() => {}} />)
    expect(screen.getByText('Test Title')).toBeInTheDocument()
  })
})
```

### 集成测试

参考 `INTEGRATION_TEST_REPORT.md` 获取完整的集成测试案例。

---

## 🐛 调试技巧

### 后端调试

**1. 查看日志**:

```bash
# 实时查看
tail -f logs/backend.log

# 搜索错误
grep -i error logs/backend.log

# 查看最近50行
tail -50 logs/backend.log
```

**2. 使用Python调试器**:

```python
# 在代码中添加断点
import pdb; pdb.set_trace()

# 或使用ipdb（更友好）
import ipdb; ipdb.set_trace()
```

**3. 查看SQLAlchemy查询**:

在 `database.py` 中启用echo：

```python
engine = create_async_engine(
    database_url,
    echo=True,  # 打印所有SQL语句
    ...
)
```

**4. 检查数据库内容**:

```bash
sqlite3 backend/standalone_textbook_server/textbook_test.db

# SQLite命令
.tables                 # 查看所有表
SELECT * FROM books;    # 查询数据
.schema books          # 查看表结构
.exit                  # 退出
```

### 前端调试

**1. 使用浏览器DevTools**:

- **Console**: 查看console.log输出
- **Network**: 查看API请求和响应
- **React DevTools**: 检查组件状态和props

**2. 查看编译错误**:

```bash
# 查看前端日志
tail -f logs/frontend.log

# 或直接在运行npm run dev的终端查看
```

**3. 调试React Query**:

安装React Query DevTools：

```typescript
// app/layout.tsx
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'

export default function RootLayout({ children }) {
  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  )
}
```

**4. 检查环境变量**:

```typescript
console.log('API URL:', process.env.NEXT_PUBLIC_API_URL)
```

---

## ❓ 常见问题

### Q1: 端口被占用

**问题**: `Address already in use`

**解决**:

```bash
# 查找占用进程
lsof -ti:8000  # 或 :3000

# 杀死进程
lsof -ti:8000 | xargs kill -9

# 或使用停止脚本
./stop-dev.sh
```

### Q2: 数据库锁定

**问题**: `database is locked`

**解决**:

```bash
# 关闭所有数据库连接
./stop-dev.sh

# 删除数据库文件重新创建
rm backend/standalone_textbook_server/textbook_test.db
./start-dev.sh
```

### Q3: 前端编译错误

**问题**: `Module not found` 或 `Cannot find module`

**解决**:

```bash
cd frontend
rm -rf node_modules package-lock.json .next
npm install
npm run dev
```

### Q4: CORS错误

**问题**: `CORS policy: No 'Access-Control-Allow-Origin' header`

**解决**:

检查 `main.py` 中的CORS配置：

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Q5: API返回404

**问题**: 前端请求后端API返回404

**解决**:

1. 检查后端是否运行: `curl http://localhost:8000/health`
2. 检查API路径是否正确
3. 检查前端环境变量: `NEXT_PUBLIC_API_URL`

### Q6: React Query错误

**问题**: `Bad argument type. Starting with v5, only the "Object" form is allowed`

**解决**:

使用正确的v5 API格式：

```typescript
// ❌ 错误（v4格式）
const { data } = useQuery(['key'], fetchFn)

// ✅ 正确（v5格式）
const { data } = useQuery({
  queryKey: ['key'],
  queryFn: fetchFn
})
```

---

## ✨ 最佳实践

### 代码风格

**Python (后端)**:

```python
# 使用类型提示
from typing import List, Optional

async def get_books(limit: int = 10) -> List[Book]:
    """获取书籍列表

    Args:
        limit: 返回数量限制

    Returns:
        书籍列表
    """
    pass

# 使用f-string
message = f"Found {len(books)} books"

# 使用Pydantic for validation
from pydantic import BaseModel

class BookCreate(BaseModel):
    title: str
    slug: str
    description: Optional[str] = None
```

**TypeScript (前端)**:

```typescript
// 使用接口定义
interface TextbookData {
  title: string
  sections: Section[]
  starterCode: string
}

// 使用const断言
const API_CONFIG = {
  baseUrl: 'http://localhost:8000',
  timeout: 5000
} as const

// 使用async/await
const fetchData = async (): Promise<TextbookData> => {
  const response = await fetch(`${apiUrl}/api/v1/textbooks/...`)
  return response.json()
}
```

### Git提交规范

```bash
# 格式: <type>: <subject>

# 示例
git commit -m "feat: add new textbook endpoint"
git commit -m "fix: resolve CORS issue in api.py"
git commit -m "docs: update developer guide"
git commit -m "refactor: improve content parsing logic"
git commit -m "test: add integration tests for API"
```

**Type类型**:
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建/工具相关

### 错误处理

**后端**:

```python
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

try:
    result = await some_operation()
except ValueError as e:
    logger.error(f"Invalid value: {e}")
    raise HTTPException(status_code=400, detail=str(e))
except Exception as e:
    logger.exception("Unexpected error")
    raise HTTPException(status_code=500, detail="Internal server error")
```

**前端**:

```typescript
const { data, error, isLoading } = useQuery({
  queryKey: ['textbook'],
  queryFn: fetchTextbook,
  retry: 3,  // 重试3次
  retryDelay: attemptIndex => Math.min(1000 * 2 ** attemptIndex, 30000),
})

if (error) {
  return (
    <div className="error-message">
      <h2>加载失败</h2>
      <p>{error instanceof Error ? error.message : '未知错误'}</p>
      <button onClick={() => refetch()}>重试</button>
    </div>
  )
}
```

### 性能优化

**后端**:

```python
# 使用数据库索引
class Book(Base):
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True)

# 批量查询减少数据库往返
from sqlalchemy.orm import selectinload

stmt = select(Book).options(
    selectinload(Book.chapters).selectinload(Chapter.cases)
)

# 使用缓存（未来）
from functools import lru_cache

@lru_cache(maxsize=128)
async def get_cached_data(key: str):
    pass
```

**前端**:

```typescript
// 使用React.memo避免不必要的重渲染
export const MyComponent = React.memo(({ data }) => {
  return <div>{data}</div>
})

// 使用useCallback缓存函数
const handleClick = useCallback(() => {
  console.log('Clicked')
}, [])

// 使用useMemo缓存计算结果
const expensiveValue = useMemo(() => {
  return computeExpensiveValue(data)
}, [data])
```

---

## 📚 参考资料

### 官方文档

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [Next.js 14 Documentation](https://nextjs.org/docs)
- [React Query v5 Documentation](https://tanstack.com/query/latest)
- [Monaco Editor Documentation](https://microsoft.github.io/monaco-editor/)

### 项目文档

- `ENVIRONMENT_SETUP_ISSUES.md` - 环境配置问题和解决方案
- `INTEGRATION_TEST_REPORT.md` - 集成测试报告
- `SPRINT_1_FINAL_SUMMARY.md` - Sprint 1最终总结

### 有用的命令

```bash
# 查看进程
ps aux | grep python
ps aux | grep node

# 查看端口占用
lsof -i:8000
netstat -tlnp | grep 8000

# 查看磁盘使用
du -sh *
df -h

# 查看内存使用
free -h
top
```

---

## 🤝 贡献指南

### 开发流程

1. Fork项目
2. 创建功能分支: `git checkout -b feature/my-feature`
3. 提交更改: `git commit -m "feat: add my feature"`
4. 推送分支: `git push origin feature/my-feature`
5. 创建Pull Request

### 代码审查清单

- [ ] 代码符合项目风格指南
- [ ] 添加了必要的注释
- [ ] 更新了相关文档
- [ ] 测试通过
- [ ] 没有引入新的警告或错误
- [ ] API变更向后兼容

---

## 📞 获取帮助

- **技术文档**: 查看 `platform/docs/` 目录
- **API文档**: http://localhost:8000/docs
- **问题报告**: 创建GitHub Issue
- **团队协作**: 使用项目Issue tracker

---

**祝开发顺利！** 🚀

*最后更新: 2025-11-12*
*维护者: CHS-Books开发团队*
