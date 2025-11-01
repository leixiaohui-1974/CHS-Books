"""
安全相关功能：密码哈希、JWT令牌生成和验证
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Union, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from .config import settings
from .database import get_db
from loguru import logger


# 密码上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# ========================================
# 密码哈希
# ========================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)


# ========================================
# JWT令牌
# ========================================

def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    创建访问令牌
    
    Args:
        data: 要编码的数据
        expires_delta: 过期时间增量
    
    Returns:
        JWT令牌字符串
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """
    创建刷新令牌
    
    Args:
        data: 要编码的数据
    
    Returns:
        JWT令牌字符串
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """
    解码JWT令牌
    
    Args:
        token: JWT令牌字符串
    
    Returns:
        解码后的数据或None
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError as e:
        logger.error(f"JWT解码错误: {e}")
        return None


# ========================================
# 依赖注入：获取当前用户
# ========================================

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    """
    从JWT令牌获取当前用户
    用于需要认证的路由
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证身份凭证",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    # 从数据库获取用户
    from app.models.user import User
    from sqlalchemy import select
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(
    current_user = Depends(get_current_user)
):
    """
    获取当前活跃用户
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="用户已被禁用")
    return current_user


async def get_current_admin_user(
    current_user: dict = Depends(get_current_user)
):
    """
    获取当前管理员用户
    仅管理员可访问的路由使用此依赖
    """
    # TODO: 检查用户是否为管理员
    # if not current_user.is_admin:
    #     raise HTTPException(
    #         status_code=403,
    #         detail="需要管理员权限"
    #     )
    return current_user


# ========================================
# API密钥验证（用于服务间通信）
# ========================================

async def verify_api_key(api_key: str) -> bool:
    """
    验证API密钥
    用于服务间通信认证
    """
    # TODO: 实现API密钥验证逻辑
    # 可以存储在数据库或环境变量中
    return api_key == settings.SECRET_KEY


# ========================================
# 生成随机令牌
# ========================================

import secrets


def generate_random_token(length: int = 32) -> str:
    """生成随机令牌（用于验证码、重置密码等）"""
    return secrets.token_urlsafe(length)


def generate_verification_code(length: int = 6) -> str:
    """生成数字验证码"""
    return ''.join([str(secrets.randbelow(10)) for _ in range(length)])
