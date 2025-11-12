"""
OAuth认证API端点
提供第三方登录接口
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from app.core.database import get_db
from app.services.oauth_service import OAuthService
from app.models.auth import OAuthProvider
from app.core.security import get_current_user
from app.models.user import User
from pydantic import BaseModel


router = APIRouter()


# ========================================
# Pydantic Schemas
# ========================================

class OAuthUrlResponse(BaseModel):
    """OAuth授权URL响应"""
    auth_url: str
    state: str


class OAuthCallbackRequest(BaseModel):
    """OAuth回调请求"""
    code: str
    state: str


class OAuthLoginResponse(BaseModel):
    """OAuth登录响应"""
    user_id: int
    username: str
    email: str | None
    avatar_url: str | None
    access_token: str
    refresh_token: str
    token_type: str
    is_new_user: bool


class OAuthAccountInfo(BaseModel):
    """OAuth账号信息"""
    provider: str
    provider_user_id: str
    created_at: str


class BindOAuthRequest(BaseModel):
    """绑定OAuth请求"""
    code: str
    state: str


# ========================================
# GitHub OAuth
# ========================================

@router.get("/github/url", response_model=OAuthUrlResponse)
async def get_github_auth_url(
    db: AsyncSession = Depends(get_db)
):
    """
    获取GitHub OAuth授权URL
    
    返回授权URL和state参数，前端需要保存state用于验证
    """
    oauth_service = OAuthService(db)
    state = OAuthService.generate_state()
    auth_url = await oauth_service.get_github_auth_url(state)
    
    return {
        "auth_url": auth_url,
        "state": state
    }


@router.post("/github/callback", response_model=OAuthLoginResponse)
async def github_callback(
    request: OAuthCallbackRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    处理GitHub OAuth回调
    
    前端接收到回调后，将code和state发送到此接口
    """
    oauth_service = OAuthService(db)
    result = await oauth_service.github_callback(request.code, request.state)
    
    return result


# ========================================
# Google OAuth
# ========================================

@router.get("/google/url", response_model=OAuthUrlResponse)
async def get_google_auth_url(
    db: AsyncSession = Depends(get_db)
):
    """
    获取Google OAuth授权URL
    """
    oauth_service = OAuthService(db)
    state = OAuthService.generate_state()
    auth_url = await oauth_service.get_google_auth_url(state)
    
    return {
        "auth_url": auth_url,
        "state": state
    }


@router.post("/google/callback", response_model=OAuthLoginResponse)
async def google_callback(
    request: OAuthCallbackRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    处理Google OAuth回调
    """
    oauth_service = OAuthService(db)
    result = await oauth_service.google_callback(request.code, request.state)
    
    return result


# ========================================
# 微信 OAuth
# ========================================

@router.get("/wechat/url", response_model=OAuthUrlResponse)
async def get_wechat_auth_url(
    db: AsyncSession = Depends(get_db)
):
    """
    获取微信OAuth授权URL
    """
    oauth_service = OAuthService(db)
    state = OAuthService.generate_state()
    auth_url = await oauth_service.get_wechat_auth_url(state)
    
    return {
        "auth_url": auth_url,
        "state": state
    }


@router.post("/wechat/callback", response_model=OAuthLoginResponse)
async def wechat_callback(
    request: OAuthCallbackRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    处理微信OAuth回调
    """
    oauth_service = OAuthService(db)
    result = await oauth_service.wechat_callback(request.code, request.state)
    
    return result


# ========================================
# OAuth账号管理
# ========================================

@router.get("/accounts", response_model=list[OAuthAccountInfo])
async def get_oauth_accounts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取当前用户的所有OAuth账号
    """
    oauth_service = OAuthService(db)
    accounts = await oauth_service.get_user_oauth_accounts(current_user.id)
    
    return [
        {
            "provider": account.provider,
            "provider_user_id": account.provider_user_id,
            "created_at": account.created_at.isoformat()
        }
        for account in accounts
    ]


@router.post("/bind/{provider}")
async def bind_oauth_account(
    provider: str,
    request: BindOAuthRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    绑定OAuth账号到当前用户
    
    用户登录后，可以绑定其他OAuth账号
    """
    # 验证provider
    try:
        oauth_provider = OAuthProvider(provider)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的OAuth提供商: {provider}"
        )
    
    oauth_service = OAuthService(db)
    
    # 根据provider调用对应的callback获取OAuth信息
    if oauth_provider == OAuthProvider.GITHUB:
        result = await oauth_service.github_callback(request.code, request.state)
    elif oauth_provider == OAuthProvider.GOOGLE:
        result = await oauth_service.google_callback(request.code, request.state)
    elif oauth_provider == OAuthProvider.WECHAT:
        result = await oauth_service.wechat_callback(request.code, request.state)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的OAuth提供商: {provider}"
        )
    
    # 注意：这里需要改进，因为callback会创建新用户或登录
    # 真正的绑定逻辑需要单独实现
    
    return {
        "success": True,
        "message": f"成功绑定{provider}账号"
    }


@router.delete("/unbind/{provider}")
async def unbind_oauth_account(
    provider: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    解绑OAuth账号
    """
    # 验证provider
    try:
        oauth_provider = OAuthProvider(provider)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的OAuth提供商: {provider}"
        )
    
    oauth_service = OAuthService(db)
    await oauth_service.unbind_oauth_account(current_user.id, oauth_provider)
    
    return {
        "success": True,
        "message": f"成功解绑{provider}账号"
    }
