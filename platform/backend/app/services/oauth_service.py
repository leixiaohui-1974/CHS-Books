"""
OAuth服务
处理第三方登录认证
"""

import httpx
import secrets
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models.auth import OAuthAccount, OAuthProvider
from app.models.user import User, UserRole
from app.core.config import settings
from app.services.auth_service import AuthService


class OAuthService:
    """OAuth服务类"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.auth_service = AuthService(db)
    
    # ========================================
    # GitHub OAuth
    # ========================================
    
    async def get_github_auth_url(self, state: str) -> str:
        """
        获取GitHub OAuth授权URL
        
        Args:
            state: 状态码（防CSRF攻击）
            
        Returns:
            授权URL
        """
        if not settings.GITHUB_CLIENT_ID:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="GitHub登录未配置"
            )
        
        params = {
            'client_id': settings.GITHUB_CLIENT_ID,
            'redirect_uri': settings.GITHUB_REDIRECT_URI,
            'scope': 'user:email',
            'state': state
        }
        
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"https://github.com/login/oauth/authorize?{query_string}"
    
    async def github_callback(self, code: str, state: str) -> Dict[str, Any]:
        """
        处理GitHub OAuth回调
        
        Args:
            code: 授权码
            state: 状态码
            
        Returns:
            用户信息和token
        """
        if not settings.GITHUB_CLIENT_ID or not settings.GITHUB_CLIENT_SECRET:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="GitHub登录未配置"
            )
        
        # 1. 交换access_token
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                'https://github.com/login/oauth/access_token',
                data={
                    'client_id': settings.GITHUB_CLIENT_ID,
                    'client_secret': settings.GITHUB_CLIENT_SECRET,
                    'code': code,
                    'redirect_uri': settings.GITHUB_REDIRECT_URI
                },
                headers={'Accept': 'application/json'}
            )
            
            if token_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="GitHub授权失败"
                )
            
            token_data = token_response.json()
            access_token = token_data.get('access_token')
            
            if not access_token:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="未获取到访问令牌"
                )
            
            # 2. 获取用户信息
            user_response = await client.get(
                'https://api.github.com/user',
                headers={
                    'Authorization': f'Bearer {access_token}',
                    'Accept': 'application/json'
                }
            )
            
            if user_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="获取GitHub用户信息失败"
                )
            
            github_user = user_response.json()
            
            # 3. 获取用户邮箱
            email_response = await client.get(
                'https://api.github.com/user/emails',
                headers={
                    'Authorization': f'Bearer {access_token}',
                    'Accept': 'application/json'
                }
            )
            
            emails = email_response.json() if email_response.status_code == 200 else []
            primary_email = next(
                (e['email'] for e in emails if e.get('primary') and e.get('verified')),
                github_user.get('email')
            )
        
        # 4. 创建或获取用户
        user, is_new = await self._get_or_create_oauth_user(
            provider=OAuthProvider.GITHUB,
            provider_user_id=str(github_user['id']),
            username=github_user['login'],
            email=primary_email,
            avatar_url=github_user.get('avatar_url'),
            full_name=github_user.get('name'),
            access_token=access_token,
            refresh_token=token_data.get('refresh_token')
        )
        
        # 5. 生成JWT token
        tokens = await self.auth_service.create_tokens(user.id)
        
        return {
            'user': self.auth_service.get_user_info_dict(user),
            'access_token': tokens['access_token'],
            'refresh_token': tokens['refresh_token'],
            'token_type': 'bearer',
            'is_new_user': is_new
        }
    
    # ========================================
    # Google OAuth
    # ========================================
    
    async def get_google_auth_url(self, state: str) -> str:
        """
        获取Google OAuth授权URL
        
        Args:
            state: 状态码
            
        Returns:
            授权URL
        """
        if not settings.GOOGLE_CLIENT_ID:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Google登录未配置"
            )
        
        params = {
            'client_id': settings.GOOGLE_CLIENT_ID,
            'redirect_uri': settings.GOOGLE_REDIRECT_URI,
            'response_type': 'code',
            'scope': 'openid email profile',
            'state': state
        }
        
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"https://accounts.google.com/o/oauth2/v2/auth?{query_string}"
    
    async def google_callback(self, code: str, state: str) -> Dict[str, Any]:
        """
        处理Google OAuth回调
        
        Args:
            code: 授权码
            state: 状态码
            
        Returns:
            用户信息和token
        """
        if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Google登录未配置"
            )
        
        # 1. 交换access_token
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                'https://oauth2.googleapis.com/token',
                data={
                    'client_id': settings.GOOGLE_CLIENT_ID,
                    'client_secret': settings.GOOGLE_CLIENT_SECRET,
                    'code': code,
                    'redirect_uri': settings.GOOGLE_REDIRECT_URI,
                    'grant_type': 'authorization_code'
                }
            )
            
            if token_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Google授权失败"
                )
            
            token_data = token_response.json()
            access_token = token_data.get('access_token')
            
            if not access_token:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="未获取到访问令牌"
                )
            
            # 2. 获取用户信息
            user_response = await client.get(
                'https://www.googleapis.com/oauth2/v2/userinfo',
                headers={'Authorization': f'Bearer {access_token}'}
            )
            
            if user_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="获取Google用户信息失败"
                )
            
            google_user = user_response.json()
        
        # 3. 创建或获取用户
        user, is_new = await self._get_or_create_oauth_user(
            provider=OAuthProvider.GOOGLE,
            provider_user_id=google_user['id'],
            username=google_user.get('email', '').split('@')[0],
            email=google_user.get('email'),
            avatar_url=google_user.get('picture'),
            full_name=google_user.get('name'),
            access_token=access_token,
            refresh_token=token_data.get('refresh_token'),
            email_verified=google_user.get('verified_email', False)
        )
        
        # 4. 生成JWT token
        tokens = await self.auth_service.create_tokens(user.id)
        
        return {
            'user': self.auth_service.get_user_info_dict(user),
            'access_token': tokens['access_token'],
            'refresh_token': tokens['refresh_token'],
            'token_type': 'bearer',
            'is_new_user': is_new
        }
    
    # ========================================
    # 微信 OAuth
    # ========================================
    
    async def get_wechat_auth_url(self, state: str) -> str:
        """
        获取微信OAuth授权URL
        
        Args:
            state: 状态码
            
        Returns:
            授权URL
        """
        if not settings.WECHAT_APP_ID:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="微信登录未配置"
            )
        
        params = {
            'appid': settings.WECHAT_APP_ID,
            'redirect_uri': settings.WECHAT_REDIRECT_URI,
            'response_type': 'code',
            'scope': 'snsapi_userinfo',
            'state': state
        }
        
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"https://open.weixin.qq.com/connect/oauth2/authorize?{query_string}#wechat_redirect"
    
    async def wechat_callback(self, code: str, state: str) -> Dict[str, Any]:
        """
        处理微信OAuth回调
        
        Args:
            code: 授权码
            state: 状态码
            
        Returns:
            用户信息和token
        """
        if not settings.WECHAT_APP_ID or not settings.WECHAT_APP_SECRET:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="微信登录未配置"
            )
        
        # 1. 交换access_token
        async with httpx.AsyncClient() as client:
            token_response = await client.get(
                'https://api.weixin.qq.com/sns/oauth2/access_token',
                params={
                    'appid': settings.WECHAT_APP_ID,
                    'secret': settings.WECHAT_APP_SECRET,
                    'code': code,
                    'grant_type': 'authorization_code'
                }
            )
            
            if token_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="微信授权失败"
                )
            
            token_data = token_response.json()
            
            if 'errcode' in token_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"微信授权错误: {token_data.get('errmsg')}"
                )
            
            access_token = token_data.get('access_token')
            openid = token_data.get('openid')
            
            # 2. 获取用户信息
            user_response = await client.get(
                'https://api.weixin.qq.com/sns/userinfo',
                params={
                    'access_token': access_token,
                    'openid': openid,
                    'lang': 'zh_CN'
                }
            )
            
            if user_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="获取微信用户信息失败"
                )
            
            wechat_user = user_response.json()
            
            if 'errcode' in wechat_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"获取用户信息错误: {wechat_user.get('errmsg')}"
                )
        
        # 3. 创建或获取用户
        user, is_new = await self._get_or_create_oauth_user(
            provider=OAuthProvider.WECHAT,
            provider_user_id=openid,
            username=f"wx_{openid[:16]}",
            email=None,  # 微信不提供邮箱
            avatar_url=wechat_user.get('headimgurl'),
            full_name=wechat_user.get('nickname'),
            access_token=access_token,
            refresh_token=token_data.get('refresh_token')
        )
        
        # 4. 生成JWT token
        tokens = await self.auth_service.create_tokens(user.id)
        
        return {
            'user': self.auth_service.get_user_info_dict(user),
            'access_token': tokens['access_token'],
            'refresh_token': tokens['refresh_token'],
            'token_type': 'bearer',
            'is_new_user': is_new
        }
    
    # ========================================
    # 通用方法
    # ========================================
    
    async def _get_or_create_oauth_user(
        self,
        provider: OAuthProvider,
        provider_user_id: str,
        username: str,
        email: Optional[str],
        avatar_url: Optional[str],
        full_name: Optional[str],
        access_token: str,
        refresh_token: Optional[str],
        email_verified: bool = False
    ) -> Tuple[User, bool]:
        """
        获取或创建OAuth用户
        
        Args:
            provider: OAuth提供商
            provider_user_id: 提供商的用户ID
            username: 用户名
            email: 邮箱
            avatar_url: 头像URL
            full_name: 全名
            access_token: OAuth访问令牌
            refresh_token: OAuth刷新令牌
            email_verified: 邮箱是否已验证
            
        Returns:
            (用户对象, 是否为新用户)
        """
        # 1. 查找已存在的OAuth账号
        query = select(OAuthAccount).where(
            OAuthAccount.provider == provider,
            OAuthAccount.provider_user_id == provider_user_id
        )
        result = await self.db.execute(query)
        oauth_account = result.scalar_one_or_none()
        
        if oauth_account:
            # 更新OAuth token
            oauth_account.access_token = access_token
            oauth_account.refresh_token = refresh_token
            oauth_account.expires_at = datetime.utcnow() + timedelta(days=60)
            oauth_account.updated_at = datetime.utcnow()
            
            await self.db.commit()
            await self.db.refresh(oauth_account)
            await self.db.refresh(oauth_account.user)
            
            return oauth_account.user, False
        
        # 2. 如果有邮箱，尝试查找已存在的用户
        user = None
        if email:
            query = select(User).where(User.email == email)
            result = await self.db.execute(query)
            user = result.scalar_one_or_none()
        
        # 3. 创建新用户
        if not user:
            # 确保用户名唯一
            base_username = username
            counter = 1
            while True:
                query = select(User).where(User.username == username)
                result = await self.db.execute(query)
                if not result.scalar_one_or_none():
                    break
                username = f"{base_username}{counter}"
                counter += 1
            
            user = User(
                username=username,
                email=email,
                full_name=full_name,
                avatar_url=avatar_url,
                role=UserRole.USER,
                status="active",
                email_verified=email_verified if email else False,
                hashed_password=None  # OAuth用户不需要密码
            )
            self.db.add(user)
            await self.db.flush()
        
        # 4. 创建OAuth关联
        oauth_account = OAuthAccount(
            user_id=user.id,
            provider=provider,
            provider_user_id=provider_user_id,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=datetime.utcnow() + timedelta(days=60)
        )
        self.db.add(oauth_account)
        
        await self.db.commit()
        await self.db.refresh(user)
        
        return user, True
    
    async def bind_oauth_account(
        self,
        user_id: int,
        provider: OAuthProvider,
        provider_user_id: str,
        access_token: str,
        refresh_token: Optional[str]
    ) -> OAuthAccount:
        """
        绑定OAuth账号到已存在的用户
        
        Args:
            user_id: 用户ID
            provider: OAuth提供商
            provider_user_id: 提供商的用户ID
            access_token: OAuth访问令牌
            refresh_token: OAuth刷新令牌
            
        Returns:
            OAuth账号对象
        """
        # 检查是否已绑定
        query = select(OAuthAccount).where(
            OAuthAccount.user_id == user_id,
            OAuthAccount.provider == provider
        )
        result = await self.db.execute(query)
        existing = result.scalar_one_or_none()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"已绑定{provider}账号"
            )
        
        # 检查provider_user_id是否已被其他用户绑定
        query = select(OAuthAccount).where(
            OAuthAccount.provider == provider,
            OAuthAccount.provider_user_id == provider_user_id
        )
        result = await self.db.execute(query)
        existing = result.scalar_one_or_none()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"该{provider}账号已被其他用户绑定"
            )
        
        # 创建绑定
        oauth_account = OAuthAccount(
            user_id=user_id,
            provider=provider,
            provider_user_id=provider_user_id,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=datetime.utcnow() + timedelta(days=60)
        )
        self.db.add(oauth_account)
        await self.db.commit()
        await self.db.refresh(oauth_account)
        
        return oauth_account
    
    async def unbind_oauth_account(
        self,
        user_id: int,
        provider: OAuthProvider
    ) -> bool:
        """
        解绑OAuth账号
        
        Args:
            user_id: 用户ID
            provider: OAuth提供商
            
        Returns:
            是否成功
        """
        query = select(OAuthAccount).where(
            OAuthAccount.user_id == user_id,
            OAuthAccount.provider == provider
        )
        result = await self.db.execute(query)
        oauth_account = result.scalar_one_or_none()
        
        if not oauth_account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"未绑定{provider}账号"
            )
        
        # 检查用户是否有密码（如果没有密码且只有一个OAuth账号，不允许解绑）
        query = select(User).where(User.id == user_id)
        result = await self.db.execute(query)
        user = result.scalar_one()
        
        if not user.hashed_password:
            # 检查OAuth账号数量
            query = select(OAuthAccount).where(OAuthAccount.user_id == user_id)
            result = await self.db.execute(query)
            oauth_accounts = result.scalars().all()
            
            if len(oauth_accounts) <= 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="无法解绑唯一的登录方式，请先设置密码"
                )
        
        await self.db.delete(oauth_account)
        await self.db.commit()
        
        return True
    
    async def get_user_oauth_accounts(self, user_id: int) -> list[OAuthAccount]:
        """
        获取用户的所有OAuth账号
        
        Args:
            user_id: 用户ID
            
        Returns:
            OAuth账号列表
        """
        query = select(OAuthAccount).where(OAuthAccount.user_id == user_id)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    def generate_state() -> str:
        """生成OAuth state参数"""
        return secrets.token_urlsafe(32)
