"""
用户服务测试
"""

import pytest
from app.services.user_service import UserService


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
    assert user.hashed_password != "password123"  # 应该被加密


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
    
    # 正确密码认证
    user = await UserService.authenticate_user(db_session, "test@example.com", "password123")
    assert user is not None
    
    # 错误密码
    user = await UserService.authenticate_user(db_session, "test@example.com", "wrongpassword")
    assert user is None
    
    # 不存在的用户
    user = await UserService.authenticate_user(db_session, "notexist@example.com", "password123")
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
    success = await UserService.change_password(
        db=db_session,
        user_id=user.id,
        old_password="oldpassword",
        new_password="newpassword"
    )
    assert success is True
    
    # 用新密码认证
    authenticated = await UserService.authenticate_user(db_session, "test@example.com", "newpassword")
    assert authenticated is not None
