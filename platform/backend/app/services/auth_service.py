"""
认证服务
提供用户认证、Token管理、密码处理等核心功能
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
import secrets
import hashlib
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.models import User, UserToken, LoginHistory, VerificationCode, UserProfile
from app.schemas.auth import UserInfo
from app.core.config import settings


# 密码上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """认证服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # ========================================
    # 密码处理
    # ========================================
    
    @staticmethod
    def hash_password(password: str) -> str:
        """哈希密码"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def check_password_strength(password: str) -> Dict[str, Any]:
        """检查密码强度"""
        import re
        
        score = 0
        issues = []
        
        # 长度检查
        if len(password) < 8:
            issues.append("密码长度至少8位")
        elif len(password) >= 12:
            score += 1
        
        if len(password) >= 16:
            score += 1
        
        # 复杂度检查
        if not re.search(r'[a-z]', password):
            issues.append("至少包含一个小写字母")
        else:
            score += 1
        
        if not re.search(r'[A-Z]', password):
            issues.append("至少包含一个大写字母")
        else:
            score += 1
        
        if not re.search(r'\d', password):
            issues.append("至少包含一个数字")
        else:
            score += 1
        
        if re.search(r'[@$!%*?&]', password):
            score += 1
        
        # 常见密码检查
        common_passwords = ['password', '12345678', 'qwerty', 'abc123']
        if password.lower() in common_passwords:
            issues.append("不要使用常见密码")
            score = 0
        
        # 确定强度等级
        if score >= 5:
            strength = 'strong'
        elif score >= 3:
            strength = 'medium'
        else:
            strength = 'weak'
        
        return {
            'strength': strength,
            'score': score,
            'issues': issues,
            'valid': len(issues) == 0
        }
    
    # ========================================
    # Token管理
    # ========================================
    
    def create_access_token(
        self, 
        user_id: int, 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """创建访问Token"""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=1)
        
        to_encode = {
            "sub": str(user_id),
            "type": "access",
            "exp": expire,
            "iat": datetime.utcnow()
        }
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.JWT_SECRET_KEY,
            algorithm="HS256"
        )
        
        return encoded_jwt
    
    def create_refresh_token(self, user_id: int) -> str:
        """创建刷新Token"""
        expire = datetime.utcnow() + timedelta(days=30)
        
        to_encode = {
            "sub": str(user_id),
            "type": "refresh",
            "exp": expire,
            "iat": datetime.utcnow()
        }
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.JWT_SECRET_KEY,
            algorithm="HS256"
        )
        
        return encoded_jwt
    
    def verify_token(self, token: str, token_type: str = "access") -> Optional[int]:
        """验证Token"""
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=["HS256"]
            )
            
            if payload.get("type") != token_type:
                return None
            
            user_id = int(payload.get("sub"))
            return user_id
            
        except JWTError:
            return None
    
    async def save_token(
        self,
        user_id: int,
        token: str,
        token_type: str,
        device_info: Optional[Dict] = None,
        expires_in: int = 3600
    ) -> UserToken:
        """保存Token到数据库"""
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        
        user_token = UserToken(
            user_id=user_id,
            token=token,
            token_type=token_type,
            device_id=device_info.get('device_id') if device_info else None,
            device_name=device_info.get('device_name') if device_info else None,
            device_type=device_info.get('device_type') if device_info else None,
            device_info=device_info,
            ip_address=device_info.get('ip_address') if device_info else None,
            expires_at=expires_at
        )
        
        self.db.add(user_token)
        await self.db.commit()
        await self.db.refresh(user_token)
        
        return user_token
    
    async def revoke_token(self, token: str):
        """撤销Token"""
        result = await self.db.execute(
            select(UserToken).where(UserToken.token == token)
        )
        user_token = result.scalar_one_or_none()
        
        if user_token:
            user_token.revoked = True
            user_token.revoked_at = datetime.utcnow()
            await self.db.commit()
    
    async def revoke_all_user_tokens(self, user_id: int):
        """撤销用户所有Token"""
        result = await self.db.execute(
            select(UserToken).where(
                UserToken.user_id == user_id,
                UserToken.revoked == False
            )
        )
        tokens = result.scalars().all()
        
        for token in tokens:
            token.revoked = True
            token.revoked_at = datetime.utcnow()
        
        await self.db.commit()
    
    async def is_token_revoked(self, token: str) -> bool:
        """检查Token是否被撤销"""
        result = await self.db.execute(
            select(UserToken).where(UserToken.token == token)
        )
        user_token = result.scalar_one_or_none()
        
        return user_token.revoked if user_token else False
    
    # ========================================
    # 用户认证
    # ========================================
    
    async def authenticate_user(
        self, 
        identifier: str, 
        password: str
    ) -> Optional[User]:
        """认证用户（支持用户名/邮箱/手机号）"""
        # 查询用户
        result = await self.db.execute(
            select(User).where(
                or_(
                    User.username == identifier,
                    User.email == identifier,
                    User.phone == identifier
                )
            )
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return None
        
        if not user.hashed_password:
            return None  # OAuth用户没有密码
        
        if not self.verify_password(password, user.hashed_password):
            return None
        
        return user
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_phone(self, phone: str) -> Optional[User]:
        """根据手机号获取用户"""
        result = await self.db.execute(
            select(User).where(User.phone == phone)
        )
        return result.scalar_one_or_none()
    
    async def check_username_available(self, username: str) -> bool:
        """检查用户名是否可用"""
        user = await self.get_user_by_username(username)
        return user is None
    
    async def check_email_available(self, email: str) -> bool:
        """检查邮箱是否可用"""
        user = await self.get_user_by_email(email)
        return user is None
    
    async def check_phone_available(self, phone: str) -> bool:
        """检查手机号是否可用"""
        user = await self.get_user_by_phone(phone)
        return user is None
    
    # ========================================
    # 用户注册
    # ========================================
    
    async def create_user(
        self,
        username: str,
        password: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        **kwargs
    ) -> User:
        """创建用户"""
        hashed_password = self.hash_password(password)
        
        user = User(
            username=username,
            email=email,
            phone=phone,
            hashed_password=hashed_password,
            **kwargs
        )
        
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        
        # 创建用户资料
        profile = UserProfile(user_id=user.id)
        self.db.add(profile)
        await self.db.commit()
        
        return user
    
    # ========================================
    # 登录历史
    # ========================================
    
    async def record_login_history(
        self,
        user_id: Optional[int],
        username: Optional[str],
        success: bool,
        login_method: Optional[str] = None,
        failure_reason: Optional[str] = None,
        request_info: Optional[Dict] = None
    ):
        """记录登录历史"""
        history = LoginHistory(
            user_id=user_id,
            username=username,
            login_method=login_method,
            success=success,
            failure_reason=failure_reason,
            ip_address=request_info.get('ip_address') if request_info else None,
            user_agent=request_info.get('user_agent') if request_info else None,
            device_type=request_info.get('device_type') if request_info else None,
            browser=request_info.get('browser') if request_info else None,
            os=request_info.get('os') if request_info else None
        )
        
        self.db.add(history)
        await self.db.commit()
    
    async def update_user_login_info(
        self,
        user_id: int,
        ip_address: Optional[str] = None
    ):
        """更新用户登录信息"""
        user = await self.get_user_by_id(user_id)
        if user:
            user.login_count += 1
            user.last_login_at = datetime.utcnow()
            if ip_address:
                user.last_login_ip = ip_address
            await self.db.commit()
    
    async def check_login_attempts(
        self, 
        identifier: str, 
        ip_address: str
    ) -> bool:
        """检查登录尝试次数（防暴力破解）"""
        since = datetime.utcnow() - timedelta(minutes=15)
        
        result = await self.db.execute(
            select(LoginHistory).where(
                or_(
                    LoginHistory.username == identifier,
                    LoginHistory.ip_address == ip_address
                ),
                LoginHistory.success == False,
                LoginHistory.created_at >= since
            )
        )
        
        failed_attempts = result.scalars().all()
        
        return len(failed_attempts) < 5
    
    # ========================================
    # 验证码管理
    # ========================================
    
    async def create_verification_code(
        self,
        code_type: str,
        recipient: str,
        user_id: Optional[int] = None,
        expires_in: int = 300
    ) -> VerificationCode:
        """创建验证码"""
        # 生成6位随机数字
        code = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
        
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        
        verification_code = VerificationCode(
            code_type=code_type,
            recipient=recipient,
            code=code,
            user_id=user_id,
            expires_at=expires_at
        )
        
        self.db.add(verification_code)
        await self.db.commit()
        await self.db.refresh(verification_code)
        
        return verification_code
    
    async def verify_code(
        self,
        recipient: str,
        code: str,
        code_type: str
    ) -> Tuple[bool, Optional[str]]:
        """验证验证码"""
        result = await self.db.execute(
            select(VerificationCode).where(
                VerificationCode.recipient == recipient,
                VerificationCode.code_type == code_type,
                VerificationCode.used == False
            ).order_by(VerificationCode.created_at.desc())
        )
        
        verification_code = result.scalar_one_or_none()
        
        if not verification_code:
            return False, "验证码不存在或已使用"
        
        if not verification_code.is_valid:
            if verification_code.used:
                return False, "验证码已使用"
            elif datetime.utcnow() > verification_code.expires_at:
                return False, "验证码已过期"
            elif verification_code.attempts >= verification_code.max_attempts:
                return False, "验证码尝试次数过多"
        
        # 检查验证码是否正确
        if verification_code.code != code:
            verification_code.increment_attempts()
            await self.db.commit()
            return False, f"验证码错误，还可尝试{verification_code.max_attempts - verification_code.attempts}次"
        
        # 标记为已使用
        verification_code.mark_as_used()
        await self.db.commit()
        
        return True, "验证成功"
    
    # ========================================
    # 辅助方法
    # ========================================
    
    def parse_user_agent(self, user_agent: str) -> Dict[str, str]:
        """解析User-Agent"""
        # 简化版解析，实际可以使用user-agents库
        device_type = "desktop"
        if 'mobile' in user_agent.lower():
            device_type = "mobile"
        elif 'tablet' in user_agent.lower():
            device_type = "tablet"
        
        browser = "unknown"
        if 'chrome' in user_agent.lower():
            browser = "Chrome"
        elif 'firefox' in user_agent.lower():
            browser = "Firefox"
        elif 'safari' in user_agent.lower():
            browser = "Safari"
        
        os = "unknown"
        if 'windows' in user_agent.lower():
            os = "Windows"
        elif 'mac' in user_agent.lower():
            os = "macOS"
        elif 'linux' in user_agent.lower():
            os = "Linux"
        elif 'android' in user_agent.lower():
            os = "Android"
        elif 'ios' in user_agent.lower():
            os = "iOS"
        
        return {
            "device_type": device_type,
            "browser": browser,
            "os": os
        }
    
    def user_to_info(self, user: User) -> UserInfo:
        """将User模型转换为UserInfo"""
        return UserInfo.from_orm(user)
