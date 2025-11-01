# 快速测试指南

## 🚀 快速开始

### 1. 安装依赖

```bash
cd /workspace/platform/backend
pip3 install -r requirements.txt
pip3 install asyncpg aiosqlite
```

### 2. 运行所有测试

```bash
cd /workspace/platform/backend
TESTING=1 python3 -m pytest tests/ -v
```

### 3. 运行特定测试

```bash
# 只测试用户服务
TESTING=1 python3 -m pytest tests/test_user_service.py -v

# 只测试书籍服务
TESTING=1 python3 -m pytest tests/test_book_service.py -v

# 测试单个功能
TESTING=1 python3 -m pytest tests/test_user_service.py::test_create_user -v
```

### 4. 查看测试覆盖率

```bash
TESTING=1 python3 -m pytest tests/ --cov=app --cov-report=html
```

## 📊 当前测试状态

```
✅ 用户服务测试: 4/4 passed
✅ 书籍服务测试: 5/5 passed
✅ 总计: 9/9 passed (100%)
```

## 🔍 测试详情

### 用户服务测试 (test_user_service.py)

```python
✅ test_create_user           # 创建用户
✅ test_get_user_by_email     # 邮箱查询
✅ test_authenticate_user     # 认证功能
✅ test_change_password       # 修改密码
```

### 书籍服务测试 (test_book_service.py)

```python
✅ test_create_book                # 创建书籍
✅ test_get_books_pagination       # 分页查询
✅ test_get_book_by_slug           # slug查询
✅ test_create_chapter_and_case    # 章节案例
✅ test_get_book_chapters          # 章节树
```

## 🛠️ 测试环境

- **Python:** 3.12.3
- **数据库:** SQLite (内存)
- **测试框架:** pytest 7.4.3
- **异步支持:** pytest-asyncio 0.21.1

## 📝 添加新测试

### 1. 创建测试文件

```python
# tests/test_xxx.py
import pytest

@pytest.mark.asyncio
async def test_example(db_session):
    """测试描述"""
    # 测试代码
    assert True
```

### 2. 运行新测试

```bash
TESTING=1 python3 -m pytest tests/test_xxx.py -v
```

## 🐛 常见问题

### Q: ModuleNotFoundError: No module named 'xxx'
**A:** 安装缺失的依赖
```bash
pip3 install xxx
```

### Q: 测试数据库连接失败
**A:** 确保设置了TESTING环境变量
```bash
TESTING=1 pytest tests/
```

### Q: 异步fixture报错
**A:** 使用pytest_asyncio.fixture装饰器
```python
import pytest_asyncio

@pytest_asyncio.fixture
async def my_fixture():
    ...
```

## ⚡ 性能提示

- 使用 `-n auto` 并行运行测试（需要pytest-xdist）
- 使用 `--tb=short` 简化错误输出
- 使用 `-x` 在第一个失败时停止

```bash
TESTING=1 python3 -m pytest tests/ -v -x --tb=short
```

## 📈 测试指标

- **测试覆盖率目标:** >80%
- **测试执行时间:** <5秒
- **测试通过率:** 100%

## 🎯 下一步

1. 添加API端点集成测试
2. 添加前端单元测试
3. 添加E2E测试
4. 设置CI/CD自动测试
