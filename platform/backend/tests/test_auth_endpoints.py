"""
认证端点集成测试
"""

import os
os.environ["TESTING"] = "1"

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from main import app
from app.core.database import Base, get_db
# 导入所有模型
from app.models import (
    User, Book, Chapter, Case, UserProgress, ChapterProgress, CaseProgress,
    Order, Subscription, ToolExecution, Coupon, UserCoupon
)


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
    
    # 创建会话
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


@pytest.mark.asyncio
async def test_register_success(client):
    """测试用户注册成功"""
    response = await client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "password123",
        "full_name": "Test User"
    })
    
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["email"] == "test@example.com"
    assert data["user"]["username"] == "testuser"


@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    """测试注册重复邮箱"""
    # 第一次注册
    await client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "password123"
    })
    
    # 第二次注册（相同邮箱）
    response = await client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "username": "testuser2",
        "password": "password123"
    })
    
    assert response.status_code == 400
    assert "已存在" in response.json()["detail"]  # 匹配"邮箱或用户名已存在"


@pytest.mark.asyncio
async def test_login_success(client):
    """测试登录成功"""
    # 先注册用户
    await client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "password123"
    })
    
    # 登录
    response = await client.post("/api/v1/auth/login", data={
        "username": "test@example.com",
        "password": "password123"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    """测试登录错误密码"""
    # 先注册用户
    await client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "password123"
    })
    
    # 使用错误密码登录
    response = await client.post("/api/v1/auth/login", data={
        "username": "test@example.com",
        "password": "wrongpassword"
    })
    
    assert response.status_code == 401
    assert "用户名或密码错误" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_current_user(client):
    """测试获取当前用户信息"""
    # 注册并登录
    register_response = await client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "password123",
        "full_name": "Test User"
    })
    
    access_token = register_response.json()["access_token"]
    
    # 获取用户信息
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"
    assert data["full_name"] == "Test User"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
