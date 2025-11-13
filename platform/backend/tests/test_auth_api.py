"""
认证API测试
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.services.auth_service import AuthService


class TestAuthAPI:
    """认证API测试类"""
    
    # ========================================
    # 注册测试
    # ========================================
    
    @pytest.mark.asyncio
    async def test_register_with_email_success(
        self,
        client: AsyncClient,
        test_session: AsyncSession,
        test_user_data: dict
    ):
        """测试邮箱注册成功"""
        # 1. 发送验证码
        send_code_response = await client.post(
            "/api/v1/auth/send-code",
            json={
                "type": "register",
                "recipient": test_user_data["email"],
                "method": "email"
            }
        )
        assert send_code_response.status_code == 200
        
        # 2. 注册（使用模拟验证码）
        auth_service = AuthService(test_session)
        from app.models.auth import VerificationCode
        from sqlalchemy import select
        result = await test_session.execute(
            select(VerificationCode).order_by(VerificationCode.created_at.desc()).limit(1)
        )
        verification = result.scalar_one()
        code = verification.code
        
        # 3. 执行注册
        register_response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": test_user_data["username"],
                "email": test_user_data["email"],
                "password": test_user_data["password"],
                "verification_code": code
            }
        )
        
        assert register_response.status_code == 200
        data = register_response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["username"] == test_user_data["username"]
    
    @pytest.mark.asyncio
    async def test_register_with_duplicate_username(
        self,
        client: AsyncClient,
        test_session: AsyncSession,
        test_user_data: dict
    ):
        """测试重复用户名注册失败"""
        # 1. 先创建一个用户
        auth_service = AuthService(test_session)
        await auth_service.create_user(
            username=test_user_data["username"],
            password=test_user_data["password"],
            email="other@example.com"
        )
        
        # 2. 尝试用相同用户名注册
        send_code_response = await client.post(
            "/api/v1/auth/send-code",
            json={
                "type": "register",
                "recipient": test_user_data["email"],
                "method": "email"
            }
        )
        
        from app.models.auth import VerificationCode
        from sqlalchemy import select
        result = await test_session.execute(
            select(VerificationCode).order_by(VerificationCode.created_at.desc()).limit(1)
        )
        verification = result.scalar_one()
        code = verification.code
        
        register_response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": test_user_data["username"],
                "email": test_user_data["email"],
                "password": test_user_data["password"],
                "verification_code": code
            }
        )
        
        assert register_response.status_code == 400
        assert "already exists" in register_response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_register_with_weak_password(
        self,
        client: AsyncClient,
        test_user_data: dict
    ):
        """测试弱密码注册失败"""
        response = await client.post(
            "/api/v1/auth/send-code",
            json={
                "type": "register",
                "recipient": test_user_data["email"],
                "method": "email"
            }
        )
        
        # 尝试使用弱密码注册
        register_response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": test_user_data["username"],
                "email": test_user_data["email"],
                "password": "123456",  # 弱密码
                "verification_code": "123456"
            }
        )
        
        # 应该返回422（验证错误）
        assert register_response.status_code == 422
    
    # ========================================
    # 登录测试
    # ========================================
    
    @pytest.mark.asyncio
    async def test_login_success(
        self,
        client: AsyncClient,
        test_session: AsyncSession,
        test_user_data: dict
    ):
        """测试登录成功"""
        # 1. 先创建用户
        auth_service = AuthService(test_session)
        user = await auth_service.create_user(
            username=test_user_data["username"],
            password=test_user_data["password"],
            email=test_user_data["email"]
        )
        
        # 2. 登录
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "identifier": test_user_data["username"],
                "password": test_user_data["password"]
            }
        )
        
        assert login_response.status_code == 200
        data = login_response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["username"] == test_user_data["username"]
    
    @pytest.mark.asyncio
    async def test_login_with_wrong_password(
        self,
        client: AsyncClient,
        test_session: AsyncSession,
        test_user_data: dict
    ):
        """测试错误密码登录失败"""
        # 1. 先创建用户
        auth_service = AuthService(test_session)
        await auth_service.create_user(
            username=test_user_data["username"],
            password=test_user_data["password"],
            email=test_user_data["email"]
        )
        
        # 2. 使用错误密码登录
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "identifier": test_user_data["username"],
                "password": "WrongPassword123"
            }
        )
        
        assert login_response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_login_with_email(
        self,
        client: AsyncClient,
        test_session: AsyncSession,
        test_user_data: dict
    ):
        """测试使用邮箱登录"""
        # 1. 创建用户
        auth_service = AuthService(test_session)
        await auth_service.create_user(
            username=test_user_data["username"],
            password=test_user_data["password"],
            email=test_user_data["email"]
        )
        
        # 2. 使用邮箱登录
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "identifier": test_user_data["email"],
                "password": test_user_data["password"]
            }
        )
        
        assert login_response.status_code == 200
        assert login_response.json()["username"] == test_user_data["username"]
    
    # ========================================
    # Token测试
    # ========================================
    
    @pytest.mark.asyncio
    async def test_refresh_token(
        self,
        client: AsyncClient,
        test_session: AsyncSession,
        test_user_data: dict
    ):
        """测试Token刷新"""
        # 1. 登录获取token
        auth_service = AuthService(test_session)
        await auth_service.create_user(
            username=test_user_data["username"],
            password=test_user_data["password"],
            email=test_user_data["email"]
        )
        
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "identifier": test_user_data["username"],
                "password": test_user_data["password"]
            }
        )
        
        refresh_token = login_response.json()["refresh_token"]
        
        # 2. 刷新token
        refresh_response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        assert refresh_response.status_code == 200
        assert "access_token" in refresh_response.json()
    
    @pytest.mark.asyncio
    async def test_get_current_user(
        self,
        client: AsyncClient,
        test_session: AsyncSession,
        test_user_data: dict
    ):
        """测试获取当前用户信息"""
        # 1. 登录
        auth_service = AuthService(test_session)
        await auth_service.create_user(
            username=test_user_data["username"],
            password=test_user_data["password"],
            email=test_user_data["email"]
        )
        
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "identifier": test_user_data["username"],
                "password": test_user_data["password"]
            }
        )
        
        access_token = login_response.json()["access_token"]
        
        # 2. 获取用户信息
        user_response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert user_response.status_code == 200
        data = user_response.json()
        assert data["username"] == test_user_data["username"]
        assert data["email"] == test_user_data["email"]
    
    @pytest.mark.asyncio
    async def test_logout(
        self,
        client: AsyncClient,
        test_session: AsyncSession,
        test_user_data: dict
    ):
        """测试登出"""
        # 1. 登录
        auth_service = AuthService(test_session)
        await auth_service.create_user(
            username=test_user_data["username"],
            password=test_user_data["password"],
            email=test_user_data["email"]
        )
        
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "identifier": test_user_data["username"],
                "password": test_user_data["password"]
            }
        )
        
        access_token = login_response.json()["access_token"]
        
        # 2. 登出
        logout_response = await client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"all_devices": False}
        )
        
        assert logout_response.status_code == 200
    
    # ========================================
    # 密码管理测试
    # ========================================
    
    @pytest.mark.asyncio
    async def test_change_password(
        self,
        client: AsyncClient,
        test_session: AsyncSession,
        test_user_data: dict
    ):
        """测试修改密码"""
        # 1. 创建用户并登录
        auth_service = AuthService(test_session)
        await auth_service.create_user(
            username=test_user_data["username"],
            password=test_user_data["password"],
            email=test_user_data["email"]
        )
        
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "identifier": test_user_data["username"],
                "password": test_user_data["password"]
            }
        )
        
        access_token = login_response.json()["access_token"]
        
        # 2. 修改密码
        change_password_response = await client.put(
            "/api/v1/auth/change-password",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "old_password": test_user_data["password"],
                "new_password": "NewPassword123"
            }
        )
        
        assert change_password_response.status_code == 200
        
        # 3. 验证新密码可以登录
        new_login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "identifier": test_user_data["username"],
                "password": "NewPassword123"
            }
        )
        
        assert new_login_response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_check_availability(
        self,
        client: AsyncClient,
        test_session: AsyncSession,
        test_user_data: dict
    ):
        """测试检查可用性"""
        # 1. 创建用户
        auth_service = AuthService(test_session)
        await auth_service.create_user(
            username=test_user_data["username"],
            password=test_user_data["password"],
            email=test_user_data["email"]
        )
        
        # 2. 检查已存在的用户名
        response1 = await client.get(
            "/api/v1/auth/check-availability",
            params={"field": "username", "value": test_user_data["username"]}
        )
        assert response1.status_code == 200
        assert response1.json()["available"] == False
        
        # 3. 检查不存在的用户名
        response2 = await client.get(
            "/api/v1/auth/check-availability",
            params={"field": "username", "value": "newuser123"}
        )
        assert response2.status_code == 200
        assert response2.json()["available"] == True
