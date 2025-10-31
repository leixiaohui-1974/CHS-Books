"""
用户服务测试
"""

import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.core.database import Base
from app.services.user_service import UserService
from app.models.user import User


# 测试数据库配置
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def db_session():
    """创建测试数据库会话"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    # 创建表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # 创建会话
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        yield session
    
    # 清理
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.mark.asyncio
async def test_create_user(db_session):
    """测试创建用户"""
    user = await UserService.create_user(
        db=db_session,
        email="test@example.com",
        username="testuser",
        password="password123",
        full_name="Test User"
    )
    
    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.username == "testuser"
    assert user.full_name == "Test User"
    assert user.hashed_password != "password123"  # 密码已加密
    assert user.is_active is True
    assert user.is_verified is False


@pytest.mark.asyncio
async def test_get_user_by_email(db_session):
    """测试通过邮箱查询用户"""
    # 创建用户
    await UserService.create_user(
        db=db_session,
        email="test@example.com",
        username="testuser",
        password="password123"
    )
    
    # 查询用户
    user = await UserService.get_user_by_email(db_session, "test@example.com")
    
    assert user is not None
    assert user.email == "test@example.com"


@pytest.mark.asyncio
async def test_authenticate_user(db_session):
    """测试用户认证"""
    # 创建用户
    await UserService.create_user(
        db=db_session,
        email="test@example.com",
        username="testuser",
        password="password123"
    )
    
    # 正确密码
    user = await UserService.authenticate_user(
        db=db_session,
        email_or_username="test@example.com",
        password="password123"
    )
    assert user is not None
    
    # 错误密码
    user = await UserService.authenticate_user(
        db=db_session,
        email_or_username="test@example.com",
        password="wrongpassword"
    )
    assert user is None


@pytest.mark.asyncio
async def test_change_password(db_session):
    """测试修改密码"""
    # 创建用户
    user = await UserService.create_user(
        db=db_session,
        email="test@example.com",
        username="testuser",
        password="oldpassword"
    )
    
    # 修改密码
    result = await UserService.change_password(
        db=db_session,
        user_id=user.id,
        old_password="oldpassword",
        new_password="newpassword"
    )
    assert result is True
    
    # 验证新密码
    user = await UserService.authenticate_user(
        db=db_session,
        email_or_username="test@example.com",
        password="newpassword"
    )
    assert user is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
