"""
认证相关API
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr

from app.core.database import get_db
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
)
from app.core.config import settings
from app.services import UserService
from loguru import logger

router = APIRouter()


# ========================================
# Pydantic Schemas
# ========================================

class RegisterRequest(BaseModel):
    """注册请求"""
    email: EmailStr
    username: str
    password: str
    full_name: str | None = None


class LoginResponse(BaseModel):
    """登录响应"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict


class TokenRefreshRequest(BaseModel):
    """刷新令牌请求"""
    refresh_token: str


# ========================================
# API Endpoints
# ========================================

@router.post("/register", response_model=LoginResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    用户注册
    
    - **email**: 邮箱地址（必填，唯一）
    - **username**: 用户名（必填，唯一）
    - **password**: 密码（必填，至少8位）
    - **full_name**: 真实姓名（可选）
    """
    logger.info(f"📝 新用户注册: {request.email}")
    
    try:
        # 创建用户
        user = await UserService.create_user(
            db=db,
            email=request.email,
            username=request.username,
            password=request.password,
            full_name=request.full_name
        )
        
        # 生成令牌
        access_token = create_access_token({"sub": str(user.id), "email": user.email})
        refresh_token = create_refresh_token({"sub": str(user.id)})
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "role": user.role.value
            }
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=LoginResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    用户登录
    
    - **username**: 用户名或邮箱
    - **password**: 密码
    """
    logger.info(f"🔐 用户登录尝试: {form_data.username}")
    
    # 验证用户
    user = await UserService.authenticate_user(
        db=db,
        email_or_username=form_data.username,
        password=form_data.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 生成令牌
    access_token = create_access_token({"sub": str(user.id), "email": user.email})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    
    logger.info(f"✅ 用户登录成功: {user.email}")
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "role": user.role.value
        }
    }


@router.post("/refresh", response_model=dict)
async def refresh_token(
    request: TokenRefreshRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    刷新访问令牌
    
    - **refresh_token**: 刷新令牌
    """
    payload = decode_token(request.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的刷新令牌"
        )
    
    user_id = payload.get("sub")
    
    # 生成新的访问令牌
    new_access_token = create_access_token({"sub": user_id})
    
    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """
    用户登出
    
    - 需要认证
    """
    logger.info(f"👋 用户登出: {current_user.get('email')}")
    
    # TODO: 将令牌加入黑名单（Redis）
    
    return {"message": "登出成功"}


@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    获取当前用户信息
    
    - 需要认证
    """
    return {
        "success": True,
        "data": current_user
    }


@router.post("/forgot-password")
async def forgot_password(
    email: EmailStr,
    db: AsyncSession = Depends(get_db)
):
    """
    忘记密码 - 发送重置邮件
    
    - **email**: 注册邮箱
    """
    # TODO: 实现密码重置逻辑
    # 1. 检查用户是否存在
    # 2. 生成重置令牌
    # 3. 发送重置邮件
    
    logger.info(f"📧 密码重置请求: {email}")
    
    return {
        "message": "如果该邮箱存在，我们已发送重置链接"
    }


@router.post("/reset-password")
async def reset_password(
    token: str,
    new_password: str,
    db: AsyncSession = Depends(get_db)
):
    """
    重置密码
    
    - **token**: 重置令牌（从邮件获取）
    - **new_password**: 新密码
    """
    # TODO: 实现密码重置逻辑
    # 1. 验证令牌
    # 2. 更新密码
    
    return {
        "message": "密码重置成功"
    }


@router.post("/verify-email")
async def verify_email(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    验证邮箱
    
    - **token**: 验证令牌（从邮件获取）
    """
    # TODO: 实现邮箱验证逻辑
    
    return {
        "message": "邮箱验证成功"
    }


# ========================================
# OAuth社交登录
# ========================================

@router.get("/oauth/github")
async def github_oauth_login():
    """GitHub OAuth登录"""
    if not settings.FEATURE_SOCIAL_LOGIN:
        raise HTTPException(status_code=403, detail="社交登录功能未启用")
    
    # TODO: 实现GitHub OAuth流程
    return {"message": "GitHub OAuth登录（待实现）"}


@router.get("/oauth/wechat")
async def wechat_oauth_login():
    """微信OAuth登录"""
    if not settings.FEATURE_SOCIAL_LOGIN:
        raise HTTPException(status_code=403, detail="社交登录功能未启用")
    
    # TODO: 实现微信OAuth流程
    return {"message": "微信OAuth登录（待实现）"}
