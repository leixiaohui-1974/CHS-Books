"""
双因素认证服务
提供TOTP生成、验证、备用码管理等功能
"""

import pyotp
import qrcode
import secrets
import io
import base64
from typing import List, Optional, Tuple
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from fastapi import HTTPException, status

from app.models.auth import TwoFactorAuth, TwoFactorMethod
from app.models.user import User
from app.core.config import settings


class TwoFAService:
    """双因素认证服务类"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # ========================================
    # TOTP 相关
    # ========================================
    
    @staticmethod
    def generate_secret() -> str:
        """
        生成TOTP密钥
        
        Returns:
            Base32编码的密钥
        """
        return pyotp.random_base32()
    
    @staticmethod
    def get_totp_uri(secret: str, username: str, issuer: str = None) -> str:
        """
        生成TOTP URI（用于二维码）
        
        Args:
            secret: TOTP密钥
            username: 用户名
            issuer: 发行者名称（应用名）
            
        Returns:
            TOTP URI
        """
        if issuer is None:
            issuer = settings.APP_NAME
        
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(
            name=username,
            issuer_name=issuer
        )
    
    @staticmethod
    def generate_qr_code(uri: str) -> str:
        """
        生成二维码（Base64编码的图片）
        
        Args:
            uri: TOTP URI
            
        Returns:
            Base64编码的PNG图片
        """
        # 创建二维码
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(uri)
        qr.make(fit=True)
        
        # 生成图片
        img = qr.make_image(fill_color="black", back_color="white")
        
        # 转换为Base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    
    @staticmethod
    def verify_totp(secret: str, code: str) -> bool:
        """
        验证TOTP代码
        
        Args:
            secret: TOTP密钥
            code: 用户输入的6位代码
            
        Returns:
            是否验证成功
        """
        totp = pyotp.TOTP(secret)
        # 允许前后30秒的时间窗口（总共60秒）
        return totp.verify(code, valid_window=1)
    
    # ========================================
    # 备用码相关
    # ========================================
    
    @staticmethod
    def generate_backup_codes(count: int = 10) -> List[str]:
        """
        生成备用码
        
        Args:
            count: 生成数量
            
        Returns:
            备用码列表
        """
        codes = []
        for _ in range(count):
            # 生成8位随机码（格式：XXXX-XXXX）
            code = secrets.token_hex(4).upper()
            formatted_code = f"{code[:4]}-{code[4:]}"
            codes.append(formatted_code)
        return codes
    
    @staticmethod
    def hash_backup_code(code: str) -> str:
        """
        对备用码进行哈希（用于存储）
        
        Args:
            code: 备用码
            
        Returns:
            哈希值
        """
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.hash(code)
    
    @staticmethod
    def verify_backup_code(code: str, hashed_code: str) -> bool:
        """
        验证备用码
        
        Args:
            code: 用户输入的备用码
            hashed_code: 存储的哈希值
            
        Returns:
            是否验证成功
        """
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.verify(code, hashed_code)
    
    # ========================================
    # 数据库操作
    # ========================================
    
    async def enable_2fa(
        self,
        user_id: int,
        method: TwoFactorMethod,
        secret: str,
        backup_codes: List[str]
    ) -> TwoFactorAuth:
        """
        启用双因素认证
        
        Args:
            user_id: 用户ID
            method: 认证方法
            secret: TOTP密钥
            backup_codes: 备用码列表
            
        Returns:
            TwoFactorAuth对象
        """
        # 检查是否已启用
        query = select(TwoFactorAuth).where(TwoFactorAuth.user_id == user_id)
        result = await self.db.execute(query)
        existing = result.scalar_one_or_none()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="双因素认证已启用"
            )
        
        # 哈希备用码
        hashed_codes = [self.hash_backup_code(code) for code in backup_codes]
        
        # 创建2FA记录
        two_fa = TwoFactorAuth(
            user_id=user_id,
            method=method,
            secret=secret,
            backup_codes=hashed_codes,
            is_enabled=True
        )
        
        self.db.add(two_fa)
        await self.db.commit()
        await self.db.refresh(two_fa)
        
        return two_fa
    
    async def disable_2fa(self, user_id: int) -> bool:
        """
        禁用双因素认证
        
        Args:
            user_id: 用户ID
            
        Returns:
            是否成功
        """
        query = delete(TwoFactorAuth).where(TwoFactorAuth.user_id == user_id)
        result = await self.db.execute(query)
        await self.db.commit()
        
        return result.rowcount > 0
    
    async def get_2fa(self, user_id: int) -> Optional[TwoFactorAuth]:
        """
        获取用户的2FA设置
        
        Args:
            user_id: 用户ID
            
        Returns:
            TwoFactorAuth对象或None
        """
        query = select(TwoFactorAuth).where(TwoFactorAuth.user_id == user_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def verify_2fa_code(
        self,
        user_id: int,
        code: str,
        use_backup: bool = False
    ) -> bool:
        """
        验证2FA代码
        
        Args:
            user_id: 用户ID
            code: 验证码
            use_backup: 是否使用备用码
            
        Returns:
            是否验证成功
        """
        # 获取2FA设置
        two_fa = await self.get_2fa(user_id)
        
        if not two_fa or not two_fa.is_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="未启用双因素认证"
            )
        
        if use_backup:
            # 验证备用码
            for i, hashed_code in enumerate(two_fa.backup_codes):
                if self.verify_backup_code(code, hashed_code):
                    # 删除已使用的备用码
                    two_fa.backup_codes.pop(i)
                    await self.db.commit()
                    return True
            return False
        else:
            # 验证TOTP代码
            return self.verify_totp(two_fa.secret, code)
    
    async def regenerate_backup_codes(
        self,
        user_id: int
    ) -> List[str]:
        """
        重新生成备用码
        
        Args:
            user_id: 用户ID
            
        Returns:
            新的备用码列表（明文）
        """
        two_fa = await self.get_2fa(user_id)
        
        if not two_fa:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="未启用双因素认证"
            )
        
        # 生成新备用码
        new_codes = self.generate_backup_codes(10)
        hashed_codes = [self.hash_backup_code(code) for code in new_codes]
        
        # 更新数据库
        two_fa.backup_codes = hashed_codes
        await self.db.commit()
        
        return new_codes
    
    async def get_backup_codes_count(self, user_id: int) -> int:
        """
        获取剩余备用码数量
        
        Args:
            user_id: 用户ID
            
        Returns:
            剩余数量
        """
        two_fa = await self.get_2fa(user_id)
        
        if not two_fa:
            return 0
        
        return len(two_fa.backup_codes)
    
    async def check_2fa_required(self, user_id: int) -> bool:
        """
        检查用户是否需要2FA验证
        
        Args:
            user_id: 用户ID
            
        Returns:
            是否需要2FA
        """
        two_fa = await self.get_2fa(user_id)
        return two_fa is not None and two_fa.is_enabled
    
    # ========================================
    # 完整的启用流程
    # ========================================
    
    async def start_enable_2fa(self, user_id: int) -> Tuple[str, str, List[str]]:
        """
        开始启用2FA流程
        
        Args:
            user_id: 用户ID
            
        Returns:
            (secret, qr_code_base64, backup_codes)
        """
        # 检查是否已启用
        if await self.check_2fa_required(user_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="双因素认证已启用"
            )
        
        # 获取用户信息
        query = select(User).where(User.id == user_id)
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 生成密钥
        secret = self.generate_secret()
        
        # 生成二维码
        uri = self.get_totp_uri(secret, user.username)
        qr_code = self.generate_qr_code(uri)
        
        # 生成备用码
        backup_codes = self.generate_backup_codes(10)
        
        return secret, qr_code, backup_codes
    
    async def confirm_enable_2fa(
        self,
        user_id: int,
        secret: str,
        code: str,
        backup_codes: List[str]
    ) -> TwoFactorAuth:
        """
        确认启用2FA（验证TOTP代码后）
        
        Args:
            user_id: 用户ID
            secret: TOTP密钥
            code: 用户输入的验证码
            backup_codes: 备用码列表
            
        Returns:
            TwoFactorAuth对象
        """
        # 验证TOTP代码
        if not self.verify_totp(secret, code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="验证码错误，请重试"
            )
        
        # 启用2FA
        return await self.enable_2fa(
            user_id=user_id,
            method=TwoFactorMethod.TOTP,
            secret=secret,
            backup_codes=backup_codes
        )
