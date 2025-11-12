"""
认证相关的Pydantic Schema
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import re


# ============================================
# 注册相关
# ============================================

class RegisterRequest(BaseModel):
    """注册请求"""
    username: str = Field(..., min_length=4, max_length=50, description="用户名")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, description="手机号")
    password: str = Field(..., min_length=8, description="密码")
    verification_code: str = Field(..., min_length=4, max_length=10, description="验证码")
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]{4,50}$', v):
            raise ValueError('用户名只能包含字母、数字和下划线')
        return v
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('密码长度至少8位')
        if not re.search(r'[a-z]', v):
            raise ValueError('密码必须包含小写字母')
        if not re.search(r'[A-Z]', v):
            raise ValueError('密码必须包含大写字母')
        if not re.search(r'\d', v):
            raise ValueError('密码必须包含数字')
        return v
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        if v and not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError('手机号格式不正确')
        return v


class RegisterResponse(BaseModel):
    """注册响应"""
    user_id: int
    username: str
    email: Optional[str]
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


# ============================================
# 登录相关
# ============================================

class LoginRequest(BaseModel):
    """登录请求（用户名/邮箱/手机号 + 密码）"""
    identifier: str = Field(..., description="用户名/邮箱/手机号")
    password: str = Field(..., description="密码")
    remember_me: bool = Field(False, description="记住登录状态")
    device_id: Optional[str] = Field(None, description="设备ID")
    device_name: Optional[str] = Field(None, description="设备名称")


class SMSLoginRequest(BaseModel):
    """短信登录请求"""
    phone: str = Field(..., description="手机号")
    code: str = Field(..., min_length=6, max_length=6, description="验证码")
    device_id: Optional[str] = Field(None, description="设备ID")
    device_name: Optional[str] = Field(None, description="设备名称")


class LoginResponse(BaseModel):
    """登录响应"""
    user_id: int
    username: str
    email: Optional[str]
    avatar_url: Optional[str]
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    requires_2fa: bool = False
    temp_token: Optional[str] = None  # 需要2FA时的临时token


class LogoutRequest(BaseModel):
    """登出请求"""
    all_devices: bool = Field(False, description="是否登出所有设备")


# ============================================
# Token相关
# ============================================

class RefreshTokenRequest(BaseModel):
    """刷新Token请求"""
    refresh_token: str


class RefreshTokenResponse(BaseModel):
    """刷新Token响应"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


# ============================================
# 验证码相关
# ============================================

class SendCodeRequest(BaseModel):
    """发送验证码请求"""
    type: str = Field(..., description="验证码类型: register, login, reset_password, change_email, change_phone")
    recipient: str = Field(..., description="接收者（邮箱或手机号）")
    method: str = Field("email", description="发送方式: email, sms")
    
    @field_validator('type')
    @classmethod
    def validate_type(cls, v):
        valid_types = ['register', 'login', 'reset_password', 'change_email', 'change_phone']
        if v not in valid_types:
            raise ValueError(f'type必须是以下之一: {", ".join(valid_types)}')
        return v
    
    @field_validator('method')
    @classmethod
    def validate_method(cls, v):
        if v not in ['email', 'sms']:
            raise ValueError('method必须是email或sms')
        return v


class SendCodeResponse(BaseModel):
    """发送验证码响应"""
    success: bool
    message: str
    expires_in: int  # 有效期（秒）


class VerifyCodeRequest(BaseModel):
    """验证验证码请求"""
    recipient: str
    code: str


# ============================================
# 密码相关
# ============================================

class ChangePasswordRequest(BaseModel):
    """修改密码请求"""
    old_password: str
    new_password: str
    
    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('密码长度至少8位')
        if not re.search(r'[a-z]', v):
            raise ValueError('密码必须包含小写字母')
        if not re.search(r'[A-Z]', v):
            raise ValueError('密码必须包含大写字母')
        if not re.search(r'\d', v):
            raise ValueError('密码必须包含数字')
        return v


class ForgotPasswordRequest(BaseModel):
    """忘记密码请求"""
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """重置密码请求"""
    token: str
    new_password: str
    
    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('密码长度至少8位')
        if not re.search(r'[a-z]', v):
            raise ValueError('密码必须包含小写字母')
        if not re.search(r'[A-Z]', v):
            raise ValueError('密码必须包含大写字母')
        if not re.search(r'\d', v):
            raise ValueError('密码必须包含数字')
        return v


# ============================================
# 双因素认证相关
# ============================================

class Enable2FARequest(BaseModel):
    """启用2FA请求"""
    method: str = Field("totp", description="认证方式: totp, sms, email")
    
    @field_validator('method')
    @classmethod
    def validate_method(cls, v):
        if v not in ['totp', 'sms', 'email']:
            raise ValueError('method必须是totp、sms或email')
        return v


class Enable2FAResponse(BaseModel):
    """启用2FA响应"""
    secret: str  # TOTP密钥
    qr_code: str  # 二维码图片（base64）
    backup_codes: List[str]  # 备用码


class Verify2FARequest(BaseModel):
    """验证2FA请求"""
    user_id: int
    code: str
    temp_token: str  # 登录时获得的临时token


class Disable2FARequest(BaseModel):
    """禁用2FA请求"""
    password: str
    code: str  # 当前的2FA代码


# ============================================
# OAuth相关
# ============================================

class OAuthLoginRequest(BaseModel):
    """OAuth登录请求"""
    provider: str = Field(..., description="OAuth提供商: wechat, github, google")
    code: str = Field(..., description="OAuth授权码")
    state: Optional[str] = Field(None, description="状态码")


class OAuthCallbackRequest(BaseModel):
    """OAuth回调请求"""
    code: str
    state: Optional[str] = None


# ============================================
# 用户信息相关
# ============================================

class UserInfo(BaseModel):
    """用户信息"""
    id: int
    username: str
    email: Optional[str]
    phone: Optional[str]
    full_name: Optional[str]
    avatar_url: Optional[str]
    bio: Optional[str]
    role: str
    status: str
    is_verified: bool
    email_verified: bool
    phone_verified: bool
    is_premium: bool
    premium_expires_at: Optional[datetime]
    total_learning_time: int
    login_count: int
    last_login_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class UpdateUserInfoRequest(BaseModel):
    """更新用户信息请求"""
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None


class UserProfileInfo(BaseModel):
    """用户资料信息"""
    id: int
    user_id: int
    real_name: Optional[str]
    gender: Optional[str]
    birthday: Optional[datetime]
    school: Optional[str]
    major: Optional[str]
    grade: Optional[str]
    wechat: Optional[str]
    qq: Optional[str]
    bio: Optional[str]
    signature: Optional[str]
    country: Optional[str]
    province: Optional[str]
    city: Optional[str]
    preferences: Optional[Dict[str, Any]]
    privacy_settings: Optional[Dict[str, Any]]
    social_links: Optional[Dict[str, Any]]
    
    class Config:
        from_attributes = True


class UpdateUserProfileRequest(BaseModel):
    """更新用户资料请求"""
    real_name: Optional[str] = None
    gender: Optional[str] = None
    birthday: Optional[datetime] = None
    school: Optional[str] = None
    major: Optional[str] = None
    grade: Optional[str] = None
    wechat: Optional[str] = None
    qq: Optional[str] = None
    bio: Optional[str] = None
    signature: Optional[str] = None
    country: Optional[str] = None
    province: Optional[str] = None
    city: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None
    privacy_settings: Optional[Dict[str, Any]] = None
    social_links: Optional[Dict[str, Any]] = None


# ============================================
# 检查可用性
# ============================================

class CheckAvailabilityRequest(BaseModel):
    """检查可用性请求"""
    field: str = Field(..., description="字段名: username, email, phone")
    value: str = Field(..., description="要检查的值")


class CheckAvailabilityResponse(BaseModel):
    """检查可用性响应"""
    available: bool
    message: Optional[str] = None


# ============================================
# 通用响应
# ============================================

class MessageResponse(BaseModel):
    """通用消息响应"""
    success: bool
    message: str


class TokenBlacklistRequest(BaseModel):
    """Token黑名单请求"""
    token: str
