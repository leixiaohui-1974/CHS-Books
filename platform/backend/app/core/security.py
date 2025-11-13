"""
安全相关工具和依赖项
"""

from typing import Optional
from datetime import datetime
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import User
from app.services.auth_service import AuthService


# HTTP Bearer认证
security = HTTPBearer()


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    获取当前登录用户
    依赖项：用于需要认证的API端点
    """
    token = credentials.credentials
    
    # 创建认证服务
    auth_service = AuthService(db)
    
    # 检查Token是否被撤销
    if await auth_service.is_token_revoked(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # 验证Token
    user_id = auth_service.verify_token(token, token_type="access")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # 获取用户信息
    user = await auth_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # 检查用户状态
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User account is {user.status}"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    获取当前活跃用户（已验证邮箱）
    """
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Please verify your email first."
        )
    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    获取当前管理员用户
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


async def get_optional_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    获取当前用户（可选）
    用于可选认证的API端点
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        auth_service = AuthService(db)
        
        if await auth_service.is_token_revoked(token):
            return None
        
        user_id = auth_service.verify_token(token, token_type="access")
        if not user_id:
            return None
        
        user = await auth_service.get_user_by_id(user_id)
        if not user or user.status != "active" or not user.is_active:
            return None
        
        return user
    except:
        return None


def require_permission(permission: str):
    """
    权限验证装饰器工厂
    
    使用方式:
    @router.get("/admin/users")
    async def list_users(
        current_user: User = Depends(require_permission("admin.users.list"))
    ):
        ...
    """
    async def permission_checker(
        current_user: User = Depends(get_current_user)
    ) -> User:
        # TODO: 实现基于角色的权限检查
        # 这里简化为检查是否是管理员
        if permission.startswith("admin.") and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission}"
            )
        return current_user
    
    return permission_checker


def get_client_ip(request: Request) -> str:
    """获取客户端IP地址"""
    # 优先从X-Forwarded-For头获取（适用于反向代理）
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    
    # 从X-Real-IP头获取
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # 直接从客户端获取
    return request.client.host if request.client else "unknown"


def get_request_info(request: Request) -> dict:
    """获取请求信息"""
    user_agent = request.headers.get("User-Agent", "")
    
    # 解析User-Agent
    auth_service = AuthService(None)  # 不需要db
    parsed = auth_service.parse_user_agent(user_agent)
    
    return {
        "ip_address": get_client_ip(request),
        "user_agent": user_agent,
        "device_type": parsed["device_type"],
        "browser": parsed["browser"],
        "os": parsed["os"]
    }
