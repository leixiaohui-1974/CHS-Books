"""
认证服务测试
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.auth_service import AuthService
from app.models.user import User


class TestAuthService:
    """认证服务测试类"""
    
    @pytest.mark.asyncio
    async def test_create_user(
        self,
        test_session: AsyncSession,
        test_user_data: dict
    ):
        """测试创建用户"""
        auth_service = AuthService(test_session)
        
        user = await auth_service.create_user(
            username=test_user_data["username"],
            password=test_user_data["password"],
            email=test_user_data["email"]
        )
        
        assert user.id is not None
        assert user.username == test_user_data["username"]
        assert user.email == test_user_data["email"]
        assert user.hashed_password is not None
        assert user.hashed_password != test_user_data["password"]
    
    @pytest.mark.asyncio
    async def test_verify_password(
        self,
        test_session: AsyncSession,
        test_user_data: dict
    ):
        """测试密码验证"""
        auth_service = AuthService(test_session)
        
        user = await auth_service.create_user(
            username=test_user_data["username"],
            password=test_user_data["password"],
            email=test_user_data["email"]
        )
        
        # 正确密码
        assert auth_service.verify_password(test_user_data["password"], user.hashed_password) == True
        
        # 错误密码
        assert auth_service.verify_password("wrongpassword", user.hashed_password) == False
    
    @pytest.mark.asyncio
    async def test_get_user_by_username(
        self,
        test_session: AsyncSession,
        test_user_data: dict
    ):
        """测试通过用户名获取用户"""
        auth_service = AuthService(test_session)
        
        created_user = await auth_service.create_user(
            username=test_user_data["username"],
            password=test_user_data["password"],
            email=test_user_data["email"]
        )
        
        user = await auth_service.get_user_by_username(test_user_data["username"])
        
        assert user is not None
        assert user.id == created_user.id
        assert user.username == test_user_data["username"]
    
    @pytest.mark.asyncio
    async def test_get_user_by_email(
        self,
        test_session: AsyncSession,
        test_user_data: dict
    ):
        """测试通过邮箱获取用户"""
        auth_service = AuthService(test_session)
        
        created_user = await auth_service.create_user(
            username=test_user_data["username"],
            password=test_user_data["password"],
            email=test_user_data["email"]
        )
        
        user = await auth_service.get_user_by_email(test_user_data["email"])
        
        assert user is not None
        assert user.id == created_user.id
        assert user.email == test_user_data["email"]
    
    @pytest.mark.asyncio
    async def test_check_username_available(
        self,
        test_session: AsyncSession,
        test_user_data: dict
    ):
        """测试检查用户名可用性"""
        auth_service = AuthService(test_session)
        
        # 用户名可用
        available = await auth_service.check_username_available(test_user_data["username"])
        assert available == True
        
        # 创建用户后不可用
        await auth_service.create_user(
            username=test_user_data["username"],
            password=test_user_data["password"],
            email=test_user_data["email"]
        )
        
        available = await auth_service.check_username_available(test_user_data["username"])
        assert available == False
    
    @pytest.mark.asyncio
    async def test_check_password_strength(self, test_session: AsyncSession):
        """测试密码强度检查"""
        auth_service = AuthService(test_session)
        
        # 强密码
        result = auth_service.check_password_strength("StrongPass123")
        assert result["is_valid"] == True
        
        # 弱密码（太短）
        result = auth_service.check_password_strength("Short1")
        assert result["is_valid"] == False
        
        # 弱密码（没有大写字母）
        result = auth_service.check_password_strength("weakpass123")
        assert result["is_valid"] == False
        
        # 弱密码（没有数字）
        result = auth_service.check_password_strength("WeakPassword")
        assert result["is_valid"] == False
    
    @pytest.mark.asyncio
    async def test_create_access_token(
        self,
        test_session: AsyncSession,
        test_user_data: dict
    ):
        """测试创建访问令牌"""
        auth_service = AuthService(test_session)
        
        user = await auth_service.create_user(
            username=test_user_data["username"],
            password=test_user_data["password"],
            email=test_user_data["email"]
        )
        
        token = auth_service.create_access_token(user.id)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    @pytest.mark.asyncio
    async def test_verify_token(
        self,
        test_session: AsyncSession,
        test_user_data: dict
    ):
        """测试验证令牌"""
        auth_service = AuthService(test_session)
        
        user = await auth_service.create_user(
            username=test_user_data["username"],
            password=test_user_data["password"],
            email=test_user_data["email"]
        )
        
        token = auth_service.create_access_token(user.id)
        payload = auth_service.verify_token(token)
        
        assert payload is not None
        assert payload["sub"] == str(user.id)
    
    @pytest.mark.asyncio
    async def test_update_user_password(
        self,
        test_session: AsyncSession,
        test_user_data: dict
    ):
        """测试更新用户密码"""
        auth_service = AuthService(test_session)
        
        user = await auth_service.create_user(
            username=test_user_data["username"],
            password=test_user_data["password"],
            email=test_user_data["email"]
        )
        
        old_password_hash = user.hashed_password
        
        # 更新密码
        new_password = "NewPassword123"
        updated_user = await auth_service.update_user_password(user.id, new_password)
        
        # 验证密码已更改
        assert updated_user.hashed_password != old_password_hash
        assert auth_service.verify_password(new_password, updated_user.hashed_password) == True
        assert auth_service.verify_password(test_user_data["password"], updated_user.hashed_password) == False
