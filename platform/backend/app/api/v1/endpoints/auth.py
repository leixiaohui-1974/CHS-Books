"""
认证相关API端点
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta

from app.core.database import get_db
from app.core.security import (
    get_current_user,
    get_current_active_user,
    get_request_info,
    get_client_ip
)
from app.models import User
from app.schemas.auth import (
    RegisterRequest,
    RegisterResponse,
    LoginRequest,
    SMSLoginRequest,
    LoginResponse,
    LogoutRequest,
    RefreshTokenRequest,
    RefreshTokenResponse,
    SendCodeRequest,
    SendCodeResponse,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    UpdateUserInfoRequest,
    UpdateUserProfileRequest,
    CheckAvailabilityRequest,
    CheckAvailabilityResponse,
    MessageResponse,
    UserInfo,
    UserProfileInfo
)
from app.services.auth_service import AuthService
from app.services.email_service import email_service

router = APIRouter()


# ============================================
# 注册
# ============================================

@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: Request,
    data: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    用户注册
    
    - **username**: 用户名（4-50个字符，只能包含字母、数字、下划线）
    - **email**: 邮箱（可选，但email和phone至少提供一个）
    - **phone**: 手机号（可选）
    - **password**: 密码（至少8位，包含大小写字母和数字）
    - **verification_code**: 验证码
    """
    auth_service = AuthService(db)
    
    # 验证至少提供email或phone之一
    if not data.email and not data.phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or phone is required"
        )
    
    # 检查用户名是否已存在
    if not await auth_service.check_username_available(data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # 检查邮箱是否已存在
    if data.email and not await auth_service.check_email_available(data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
    
    # 检查手机号是否已存在
    if data.phone and not await auth_service.check_phone_available(data.phone):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone already exists"
        )
    
    # 验证验证码
    recipient = data.email or data.phone
    is_valid, message = await auth_service.verify_code(
        recipient=recipient,
        code=data.verification_code,
        code_type="register"
    )
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    # 创建用户
    user = await auth_service.create_user(
        username=data.username,
        email=data.email,
        phone=data.phone,
        password=data.password,
        is_verified=True if data.email else False,  # 邮箱注册默认已验证
        email_verified=True if data.email else False,
        phone_verified=True if data.phone else False
    )
    
    # 生成Token
    access_token = auth_service.create_access_token(user.id)
    refresh_token = auth_service.create_refresh_token(user.id)
    
    # 保存Token
    request_info = get_request_info(request)
    await auth_service.save_token(
        user_id=user.id,
        token=access_token,
        token_type="access",
        device_info=request_info,
        expires_in=3600
    )
    
    # 记录登录历史
    await auth_service.record_login_history(
        user_id=user.id,
        username=user.username,
        success=True,
        login_method="register",
        request_info=request_info
    )
    
    # 发送欢迎邮件
    if data.email:
        await email_service.send_welcome_email(data.email, user.username)
    
    return RegisterResponse(
        user_id=user.id,
        username=user.username,
        email=user.email,
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=3600
    )


# ============================================
# 登录
# ============================================

@router.post("/login", response_model=LoginResponse)
async def login(
    request: Request,
    data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    用户登录
    
    - **identifier**: 用户名/邮箱/手机号
    - **password**: 密码
    - **remember_me**: 是否记住登录状态（影响refresh_token有效期）
    - **device_id**: 设备ID（可选）
    - **device_name**: 设备名称（可选）
    """
    auth_service = AuthService(db)
    request_info = get_request_info(request)
    ip_address = get_client_ip(request)
    
    # 检查登录尝试次数
    if not await auth_service.check_login_attempts(data.identifier, ip_address):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed login attempts. Please try again later."
        )
    
    # 认证用户
    user = await auth_service.authenticate_user(data.identifier, data.password)
    
    if not user:
        # 记录失败的登录历史
        await auth_service.record_login_history(
            user_id=None,
            username=data.identifier,
            success=False,
            login_method="password",
            failure_reason="Invalid credentials",
            request_info=request_info
        )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # 检查用户状态
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User account is {user.status}"
        )
    
    # TODO: 检查是否启用了2FA
    # if user.two_factor_auth and user.two_factor_auth.enabled:
    #     return LoginResponse(..., requires_2fa=True, temp_token=...)
    
    # 生成Token
    access_token = auth_service.create_access_token(user.id)
    
    # refresh_token有效期：记住登录30天，否则7天
    refresh_expires = timedelta(days=30 if data.remember_me else 7)
    refresh_token = auth_service.create_refresh_token(user.id)
    
    # 保存Token
    device_info = {
        **request_info,
        'device_id': data.device_id,
        'device_name': data.device_name
    }
    
    await auth_service.save_token(
        user_id=user.id,
        token=access_token,
        token_type="access",
        device_info=device_info,
        expires_in=3600
    )
    
    await auth_service.save_token(
        user_id=user.id,
        token=refresh_token,
        token_type="refresh",
        device_info=device_info,
        expires_in=int(refresh_expires.total_seconds())
    )
    
    # 更新登录信息
    await auth_service.update_user_login_info(user.id, ip_address)
    
    # 记录登录历史
    await auth_service.record_login_history(
        user_id=user.id,
        username=user.username,
        success=True,
        login_method="password",
        request_info=request_info
    )
    
    return LoginResponse(
        user_id=user.id,
        username=user.username,
        email=user.email,
        avatar_url=user.avatar_url,
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=3600,
        requires_2fa=False
    )


@router.post("/sms-login", response_model=LoginResponse)
async def sms_login(
    request: Request,
    data: SMSLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    短信验证码登录
    
    - **phone**: 手机号
    - **code**: 验证码
    """
    auth_service = AuthService(db)
    
    # 验证验证码
    is_valid, message = await auth_service.verify_code(
        recipient=data.phone,
        code=data.code,
        code_type="login"
    )
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    # 获取用户
    user = await auth_service.get_user_by_phone(data.phone)
    
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
    
    # 生成Token
    access_token = auth_service.create_access_token(user.id)
    refresh_token = auth_service.create_refresh_token(user.id)
    
    # 保存Token
    request_info = get_request_info(request)
    device_info = {
        **request_info,
        'device_id': data.device_id,
        'device_name': data.device_name
    }
    
    await auth_service.save_token(
        user_id=user.id,
        token=access_token,
        token_type="access",
        device_info=device_info,
        expires_in=3600
    )
    
    # 更新登录信息
    await auth_service.update_user_login_info(user.id, get_client_ip(request))
    
    # 记录登录历史
    await auth_service.record_login_history(
        user_id=user.id,
        username=user.username,
        success=True,
        login_method="sms",
        request_info=request_info
    )
    
    return LoginResponse(
        user_id=user.id,
        username=user.username,
        email=user.email,
        avatar_url=user.avatar_url,
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=3600
    )


# ============================================
# 登出
# ============================================

@router.post("/logout", response_model=MessageResponse)
async def logout(
    request: Request,
    data: LogoutRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    用户登出
    
    - **all_devices**: 是否登出所有设备
    """
    auth_service = AuthService(db)
    
    # 获取当前Token
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[7:]
        
        if data.all_devices:
            # 撤销所有Token
            await auth_service.revoke_all_user_tokens(current_user.id)
        else:
            # 只撤销当前Token
            await auth_service.revoke_token(token)
    
    return MessageResponse(
        success=True,
        message="Logged out successfully"
    )


# ============================================
# Token刷新
# ============================================

@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(
    data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    刷新访问Token
    
    - **refresh_token**: 刷新Token
    """
    auth_service = AuthService(db)
    
    # 验证refresh token
    user_id = auth_service.verify_token(data.refresh_token, token_type="refresh")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # 检查Token是否被撤销
    if await auth_service.is_token_revoked(data.refresh_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked"
        )
    
    # 生成新的access token
    access_token = auth_service.create_access_token(user_id)
    
    return RefreshTokenResponse(
        access_token=access_token,
        expires_in=3600
    )


# ============================================
# 验证码
# ============================================

@router.post("/send-code", response_model=SendCodeResponse)
async def send_verification_code(
    data: SendCodeRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    发送验证码
    
    - **type**: 验证码类型（register, login, reset_password, change_email, change_phone）
    - **recipient**: 接收者（邮箱或手机号）
    - **method**: 发送方式（email, sms）
    """
    auth_service = AuthService(db)
    
    # 创建验证码
    verification_code = await auth_service.create_verification_code(
        code_type=data.type,
        recipient=data.recipient,
        expires_in=300  # 5分钟
    )
    
    # 发送验证码
    if data.method == "email":
        success = await email_service.send_verification_code(
            to_email=data.recipient,
            code=verification_code.code,
            expires_in=300
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send verification code"
            )
    elif data.method == "sms":
        # TODO: 实现短信发送
        pass
    
    return SendCodeResponse(
        success=True,
        message="Verification code sent successfully",
        expires_in=300
    )


# ============================================
# 密码管理
# ============================================

@router.put("/change-password", response_model=MessageResponse)
async def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    修改密码
    
    - **old_password**: 旧密码
    - **new_password**: 新密码
    """
    auth_service = AuthService(db)
    
    # 验证旧密码
    if not current_user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change password for OAuth users"
        )
    
    if not auth_service.verify_password(data.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Old password is incorrect"
        )
    
    # 更新密码
    current_user.hashed_password = auth_service.hash_password(data.new_password)
    await db.commit()
    
    # 撤销所有Token（强制重新登录）
    await auth_service.revoke_all_user_tokens(current_user.id)
    
    return MessageResponse(
        success=True,
        message="Password changed successfully. Please login again."
    )


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    data: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    忘记密码 - 发送重置链接
    
    - **email**: 邮箱
    """
    auth_service = AuthService(db)
    
    # 查找用户
    user = await auth_service.get_user_by_email(data.email)
    
    # 为了安全，即使用户不存在也返回成功（防止枚举攻击）
    if not user:
        return MessageResponse(
            success=True,
            message="If the email exists, a password reset link has been sent."
        )
    
    # 生成重置Token
    reset_token = auth_service.create_access_token(
        user.id,
        expires_delta=timedelta(minutes=30)
    )
    
    # 发送重置邮件
    await email_service.send_password_reset_email(data.email, reset_token)
    
    return MessageResponse(
        success=True,
        message="If the email exists, a password reset link has been sent."
    )


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    data: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    重置密码
    
    - **token**: 重置Token（从邮件链接获取）
    - **new_password**: 新密码
    """
    auth_service = AuthService(db)
    
    # 验证Token
    user_id = auth_service.verify_token(data.token)
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # 获取用户
    user = await auth_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # 更新密码
    user.hashed_password = auth_service.hash_password(data.new_password)
    await db.commit()
    
    # 撤销所有Token
    await auth_service.revoke_all_user_tokens(user.id)
    
    return MessageResponse(
        success=True,
        message="Password reset successfully. Please login with your new password."
    )


# ============================================
# 用户信息
# ============================================

@router.get("/me", response_model=UserInfo)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """获取当前用户信息"""
    return UserInfo.from_orm(current_user)


@router.put("/me", response_model=UserInfo)
async def update_current_user_info(
    data: UpdateUserInfoRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    更新当前用户信息
    
    - **full_name**: 全名
    - **avatar_url**: 头像URL
    - **bio**: 个人简介
    """
    # 更新字段
    if data.full_name is not None:
        current_user.full_name = data.full_name
    if data.avatar_url is not None:
        current_user.avatar_url = data.avatar_url
    if data.bio is not None:
        current_user.bio = data.bio
    
    await db.commit()
    await db.refresh(current_user)
    
    return UserInfo.from_orm(current_user)


# ============================================
# 检查可用性
# ============================================

@router.get("/check-availability", response_model=CheckAvailabilityResponse)
async def check_availability(
    field: str,
    value: str,
    db: AsyncSession = Depends(get_db)
):
    """
    检查字段可用性
    
    - **field**: 字段名（username, email, phone）
    - **value**: 要检查的值
    """
    auth_service = AuthService(db)
    
    if field == "username":
        available = await auth_service.check_username_available(value)
        message = "Username is available" if available else "Username already exists"
    elif field == "email":
        available = await auth_service.check_email_available(value)
        message = "Email is available" if available else "Email already exists"
    elif field == "phone":
        available = await auth_service.check_phone_available(value)
        message = "Phone is available" if available else "Phone already exists"
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid field name"
        )
    
    return CheckAvailabilityResponse(
        available=available,
        message=message
    )
