"""
双因素认证服务测试
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.twofa_service import TwoFAService
from app.services.auth_service import AuthService
from app.models.auth import TwoFactorMethod


class TestTwoFAService:
    """2FA服务测试类"""
    
    @pytest.mark.asyncio
    async def test_generate_secret(self):
        """测试生成密钥"""
        secret = TwoFAService.generate_secret()
        
        assert secret is not None
        assert isinstance(secret, str)
        assert len(secret) == 32  # Base32编码的密钥长度
    
    @pytest.mark.asyncio
    async def test_get_totp_uri(self):
        """测试生成TOTP URI"""
        secret = TwoFAService.generate_secret()
        username = "testuser"
        
        uri = TwoFAService.get_totp_uri(secret, username)
        
        assert uri is not None
        assert uri.startswith("otpauth://totp/")
        assert username in uri
        assert secret in uri
    
    @pytest.mark.asyncio
    async def test_generate_qr_code(self):
        """测试生成二维码"""
        secret = TwoFAService.generate_secret()
        uri = TwoFAService.get_totp_uri(secret, "testuser")
        
        qr_code = TwoFAService.generate_qr_code(uri)
        
        assert qr_code is not None
        assert qr_code.startswith("data:image/png;base64,")
    
    @pytest.mark.asyncio
    async def test_verify_totp(self):
        """测试验证TOTP代码"""
        import pyotp
        
        secret = TwoFAService.generate_secret()
        totp = pyotp.TOTP(secret)
        code = totp.now()
        
        # 正确的代码
        is_valid = TwoFAService.verify_totp(secret, code)
        assert is_valid == True
        
        # 错误的代码
        is_valid = TwoFAService.verify_totp(secret, "000000")
        assert is_valid == False
    
    @pytest.mark.asyncio
    async def test_generate_backup_codes(self):
        """测试生成备用码"""
        codes = TwoFAService.generate_backup_codes(10)
        
        assert len(codes) == 10
        for code in codes:
            assert isinstance(code, str)
            assert len(code) == 9  # XXXX-XXXX格式
            assert "-" in code
    
    @pytest.mark.asyncio
    async def test_hash_and_verify_backup_code(self):
        """测试备用码哈希和验证"""
        code = "ABCD-1234"
        
        hashed = TwoFAService.hash_backup_code(code)
        assert hashed != code
        
        # 正确的备用码
        is_valid = TwoFAService.verify_backup_code(code, hashed)
        assert is_valid == True
        
        # 错误的备用码
        is_valid = TwoFAService.verify_backup_code("WRONG-CODE", hashed)
        assert is_valid == False
    
    @pytest.mark.asyncio
    async def test_enable_2fa(
        self,
        test_session: AsyncSession,
        test_user_data: dict
    ):
        """测试启用2FA"""
        # 创建用户
        auth_service = AuthService(test_session)
        user = await auth_service.create_user(
            username=test_user_data["username"],
            password=test_user_data["password"],
            email=test_user_data["email"]
        )
        
        # 启用2FA
        twofa_service = TwoFAService(test_session)
        secret = TwoFAService.generate_secret()
        backup_codes = TwoFAService.generate_backup_codes(10)
        
        two_fa = await twofa_service.enable_2fa(
            user_id=user.id,
            method=TwoFactorMethod.TOTP,
            secret=secret,
            backup_codes=backup_codes
        )
        
        assert two_fa.user_id == user.id
        assert two_fa.method == TwoFactorMethod.TOTP
        assert two_fa.secret == secret
        assert two_fa.is_enabled == True
        assert len(two_fa.backup_codes) == 10
    
    @pytest.mark.asyncio
    async def test_disable_2fa(
        self,
        test_session: AsyncSession,
        test_user_data: dict
    ):
        """测试禁用2FA"""
        # 创建用户并启用2FA
        auth_service = AuthService(test_session)
        user = await auth_service.create_user(
            username=test_user_data["username"],
            password=test_user_data["password"],
            email=test_user_data["email"]
        )
        
        twofa_service = TwoFAService(test_session)
        secret = TwoFAService.generate_secret()
        backup_codes = TwoFAService.generate_backup_codes(10)
        
        await twofa_service.enable_2fa(
            user_id=user.id,
            method=TwoFactorMethod.TOTP,
            secret=secret,
            backup_codes=backup_codes
        )
        
        # 禁用2FA
        result = await twofa_service.disable_2fa(user.id)
        assert result == True
        
        # 确认已禁用
        two_fa = await twofa_service.get_2fa(user.id)
        assert two_fa is None
    
    @pytest.mark.asyncio
    async def test_verify_2fa_code_with_totp(
        self,
        test_session: AsyncSession,
        test_user_data: dict
    ):
        """测试验证2FA代码（TOTP）"""
        import pyotp
        
        # 创建用户并启用2FA
        auth_service = AuthService(test_session)
        user = await auth_service.create_user(
            username=test_user_data["username"],
            password=test_user_data["password"],
            email=test_user_data["email"]
        )
        
        twofa_service = TwoFAService(test_session)
        secret = TwoFAService.generate_secret()
        backup_codes = TwoFAService.generate_backup_codes(10)
        
        await twofa_service.enable_2fa(
            user_id=user.id,
            method=TwoFactorMethod.TOTP,
            secret=secret,
            backup_codes=backup_codes
        )
        
        # 生成正确的TOTP代码
        totp = pyotp.TOTP(secret)
        code = totp.now()
        
        # 验证
        is_valid = await twofa_service.verify_2fa_code(
            user_id=user.id,
            code=code,
            use_backup=False
        )
        
        assert is_valid == True
    
    @pytest.mark.asyncio
    async def test_verify_2fa_code_with_backup(
        self,
        test_session: AsyncSession,
        test_user_data: dict
    ):
        """测试验证2FA代码（备用码）"""
        # 创建用户并启用2FA
        auth_service = AuthService(test_session)
        user = await auth_service.create_user(
            username=test_user_data["username"],
            password=test_user_data["password"],
            email=test_user_data["email"]
        )
        
        twofa_service = TwoFAService(test_session)
        secret = TwoFAService.generate_secret()
        backup_codes = TwoFAService.generate_backup_codes(10)
        plain_code = backup_codes[0]
        
        await twofa_service.enable_2fa(
            user_id=user.id,
            method=TwoFactorMethod.TOTP,
            secret=secret,
            backup_codes=backup_codes
        )
        
        # 使用备用码验证
        is_valid = await twofa_service.verify_2fa_code(
            user_id=user.id,
            code=plain_code,
            use_backup=True
        )
        
        assert is_valid == True
        
        # 再次使用同一个备用码应该失败（一次性使用）
        is_valid = await twofa_service.verify_2fa_code(
            user_id=user.id,
            code=plain_code,
            use_backup=True
        )
        
        assert is_valid == False
    
    @pytest.mark.asyncio
    async def test_regenerate_backup_codes(
        self,
        test_session: AsyncSession,
        test_user_data: dict
    ):
        """测试重新生成备用码"""
        # 创建用户并启用2FA
        auth_service = AuthService(test_session)
        user = await auth_service.create_user(
            username=test_user_data["username"],
            password=test_user_data["password"],
            email=test_user_data["email"]
        )
        
        twofa_service = TwoFAService(test_session)
        secret = TwoFAService.generate_secret()
        old_backup_codes = TwoFAService.generate_backup_codes(10)
        
        await twofa_service.enable_2fa(
            user_id=user.id,
            method=TwoFactorMethod.TOTP,
            secret=secret,
            backup_codes=old_backup_codes
        )
        
        # 重新生成备用码
        new_codes = await twofa_service.regenerate_backup_codes(user.id)
        
        assert len(new_codes) == 10
        # 新码应该与旧码不同
        assert new_codes[0] != old_backup_codes[0]
