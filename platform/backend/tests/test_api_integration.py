"""
API端点集成测试
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from main import app
from app.core.database import Base, get_db
from app.services import UserService, BookService
from app.models.book import BookStatus, DifficultyLevel


# 测试数据库配置
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def db_session():
    """创建测试数据库会话"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    # 创建表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # 创建会话工厂
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    # 创建会话实例
    session = async_session()
    yield session
    
    # 清理
    await session.close()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest_asyncio.fixture
async def client(db_session):
    """创建测试客户端"""
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(db_session):
    """创建测试用户"""
    user = await UserService.create_user(
        db=db_session,
        email="test@example.com",
        username="testuser",
        password="password123",
        full_name="Test User"
    )
    return user


@pytest_asyncio.fixture
async def test_book(db_session):
    """创建测试书籍"""
    book = await BookService.create_book(
        db=db_session,
        slug="test-book",
        title="测试书籍",
        subtitle="测试副标题",
        status=BookStatus.PUBLISHED,
        difficulty=DifficultyLevel.BEGINNER,
        price=299.0
    )
    
    # 创建章节
    chapter = await BookService.create_chapter(
        db=db_session,
        book_id=book.id,
        slug="chapter-1",
        order=1,
        title="第1章"
    )
    
    # 创建案例
    case = await BookService.create_case(
        db=db_session,
        book_id=book.id,
        chapter_id=chapter.id,
        slug="case-1",
        order=1,
        title="案例1",
        difficulty=DifficultyLevel.BEGINNER,
        has_tool=True
    )
    
    return book, chapter, case


@pytest_asyncio.fixture
async def auth_headers(client, test_user):
    """获取认证头"""
    # 登录获取token
    response = await client.post("/api/v1/auth/login", data={
        "username": "test@example.com",
        "password": "password123"
    })
    
    assert response.status_code == 200
    data = response.json()
    token = data["access_token"]
    
    return {"Authorization": f"Bearer {token}"}


# ========================================
# 认证API测试
# ========================================

@pytest.mark.asyncio
async def test_register_and_login(client):
    """测试注册和登录流程"""
    # 注册
    register_response = await client.post("/api/v1/auth/register", json={
        "email": "newuser@example.com",
        "username": "newuser",
        "password": "password123",
        "full_name": "New User"
    })
    
    assert register_response.status_code == 201
    register_data = register_response.json()
    assert "access_token" in register_data
    assert register_data["user"]["email"] == "newuser@example.com"
    
    # 登录
    login_response = await client.post("/api/v1/auth/login", data={
        "username": "newuser@example.com",
        "password": "password123"
    })
    
    assert login_response.status_code == 200
    login_data = login_response.json()
    assert "access_token" in login_data


@pytest.mark.asyncio
async def test_get_current_user(client, auth_headers):
    """测试获取当前用户"""
    response = await client.get("/api/v1/auth/me", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"


# ========================================
# 书籍API测试
# ========================================

@pytest.mark.asyncio
async def test_get_books_list(client, test_book):
    """测试获取书籍列表"""
    response = await client.get("/api/v1/books")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert len(data["items"]) >= 1


@pytest.mark.asyncio
async def test_get_book_detail(client, test_book):
    """测试获取书籍详情"""
    book, _, _ = test_book
    
    response = await client.get(f"/api/v1/books/{book.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "测试书籍"
    assert data["slug"] == "test-book"


@pytest.mark.asyncio
async def test_get_book_chapters(client, test_book):
    """测试获取书籍章节"""
    book, _, _ = test_book
    
    response = await client.get(f"/api/v1/books/{book.id}/chapters")
    
    assert response.status_code == 200
    data = response.json()
    assert data["book_id"] == book.id
    assert data["total_chapters"] >= 1
    assert len(data["chapters"]) >= 1


# ========================================
# 进度API测试
# ========================================

@pytest.mark.asyncio
async def test_enroll_book(client, auth_headers, test_book):
    """测试注册学习"""
    book, _, _ = test_book
    
    response = await client.post(
        f"/api/v1/progress/enroll/{book.id}",
        headers=auth_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "注册学习成功"
    assert data["book_id"] == book.id


@pytest.mark.asyncio
async def test_get_my_progress(client, auth_headers, test_book):
    """测试获取我的进度"""
    book, _, _ = test_book
    
    # 先注册学习
    await client.post(f"/api/v1/progress/enroll/{book.id}", headers=auth_headers)
    
    # 获取进度
    response = await client.get("/api/v1/progress/my-progress", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_update_case_progress(client, auth_headers, test_book):
    """测试更新案例进度"""
    book, _, case = test_book
    
    # 先注册学习
    await client.post(f"/api/v1/progress/enroll/{book.id}", headers=auth_headers)
    
    # 更新案例进度
    response = await client.post(
        f"/api/v1/progress/cases/{case.id}/update",
        headers=auth_headers,
        params={
            "status_value": "completed",
            "score": 95.0,
            "time_spent": 300
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "进度更新成功"


@pytest.mark.asyncio
async def test_get_dashboard(client, auth_headers, test_book):
    """测试获取仪表盘"""
    book, _, _ = test_book
    
    # 先注册学习
    await client.post(f"/api/v1/progress/enroll/{book.id}", headers=auth_headers)
    
    # 获取仪表盘
    response = await client.get("/api/v1/progress/dashboard", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "user_info" in data
    assert "statistics" in data
    assert "enrolled_courses" in data


# ========================================
# 健康检查测试
# ========================================

@pytest.mark.asyncio
async def test_health_check(client):
    """测试健康检查"""
    response = await client.get("/api/v1/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
