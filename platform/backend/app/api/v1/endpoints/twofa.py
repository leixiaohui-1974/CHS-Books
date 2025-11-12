"""
双因素认证API端点
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from typing import List

from app.core.database import get_db
from app.services.twofa_service import TwoFAService
from app.core.security import get_current_user
from app.models.user import User


router = APIRouter()


# ========================================
# Pydantic Schemas
# ========================================

class Enable2FAStartResponse(BaseModel):
    """开始启用2FA响应"""
    secret: str
    qr_code: str  # Base64编码的二维码图片
    backup_codes: List[str]
    message: str


class Enable2FAConfirmRequest(BaseModel):
    """确认启用2FA请求"""
    secret: str = Field(..., description="TOTP密钥")
    code: str = Field(..., min_length=6, max_length=6, description="6位验证码")
    backup_codes: List[str] = Field(..., description="备用码列表")


class Verify2FARequest(BaseModel):
    """验证2FA请求"""
    code: str = Field(..., min_length=6, max_length=8, description="验证码或备用码")
    use_backup: bool = Field(default=False, description="是否使用备用码")


class TwoFAStatusResponse(BaseModel):
    """2FA状态响应"""
    enabled: bool
    method: str | None
    backup_codes_count: int


class RegenerateBackupCodesResponse(BaseModel):
    """重新生成备用码响应"""
    backup_codes: List[str]
    message: str


# ========================================
# API端点
# ========================================

@router.get("/status", response_model=TwoFAStatusResponse)
async def get_2fa_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取2FA状态
    """
    twofa_service = TwoFAService(db)
    two_fa = await twofa_service.get_2fa(current_user.id)
    
    if two_fa and two_fa.is_enabled:
        backup_count = await twofa_service.get_backup_codes_count(current_user.id)
        return {
            "enabled": True,
            "method": two_fa.method,
            "backup_codes_count": backup_count
        }
    else:
        return {
            "enabled": False,
            "method": None,
            "backup_codes_count": 0
        }


@router.post("/enable/start", response_model=Enable2FAStartResponse)
async def start_enable_2fa(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    开始启用2FA流程
    
    返回TOTP密钥、二维码和备用码
    用户需要：
    1. 使用认证器应用扫描二维码或手动输入密钥
    2. 保存备用码
    3. 输入认证器生成的6位代码进行确认
    """
    twofa_service = TwoFAService(db)
    
    secret, qr_code, backup_codes = await twofa_service.start_enable_2fa(current_user.id)
    
    return {
        "secret": secret,
        "qr_code": qr_code,
        "backup_codes": backup_codes,
        "message": "请使用认证器应用（如Google Authenticator、Microsoft Authenticator）扫描二维码，然后输入6位验证码进行确认"
    }


@router.post("/enable/confirm")
async def confirm_enable_2fa(
    request: Enable2FAConfirmRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    确认启用2FA
    
    用户需要输入认证器应用显示的6位验证码
    """
    twofa_service = TwoFAService(db)
    
    await twofa_service.confirm_enable_2fa(
        user_id=current_user.id,
        secret=request.secret,
        code=request.code,
        backup_codes=request.backup_codes
    )
    
    return {
        "success": True,
        "message": "双因素认证已成功启用"
    }


@router.post("/disable")
async def disable_2fa(
    request: Verify2FARequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    禁用2FA
    
    需要验证当前的2FA代码
    """
    twofa_service = TwoFAService(db)
    
    # 验证2FA代码
    is_valid = await twofa_service.verify_2fa_code(
        user_id=current_user.id,
        code=request.code,
        use_backup=request.use_backup
    )
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证码错误"
        )
    
    # 禁用2FA
    await twofa_service.disable_2fa(current_user.id)
    
    return {
        "success": True,
        "message": "双因素认证已禁用"
    }


@router.post("/verify")
async def verify_2fa_code(
    request: Verify2FARequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    验证2FA代码
    
    用于测试验证码是否正确
    """
    twofa_service = TwoFAService(db)
    
    is_valid = await twofa_service.verify_2fa_code(
        user_id=current_user.id,
        code=request.code,
        use_backup=request.use_backup
    )
    
    if not is_valid:
        return {
            "valid": False,
            "message": "验证码错误"
        }
    
    return {
        "valid": True,
        "message": "验证成功"
    }


@router.post("/backup-codes/regenerate", response_model=RegenerateBackupCodesResponse)
async def regenerate_backup_codes(
    request: Verify2FARequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    重新生成备用码
    
    需要验证当前的2FA代码
    旧的备用码将失效
    """
    twofa_service = TwoFAService(db)
    
    # 验证2FA代码
    is_valid = await twofa_service.verify_2fa_code(
        user_id=current_user.id,
        code=request.code,
        use_backup=False  # 不允许使用备用码来重新生成备用码
    )
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证码错误"
        )
    
    # 重新生成备用码
    new_codes = await twofa_service.regenerate_backup_codes(current_user.id)
    
    return {
        "backup_codes": new_codes,
        "message": "备用码已重新生成，请妥善保存"
    }


@router.get("/backup-codes/count")
async def get_backup_codes_count(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取剩余备用码数量
    """
    twofa_service = TwoFAService(db)
    count = await twofa_service.get_backup_codes_count(current_user.id)
    
    return {
        "count": count,
        "warning": count < 3
    }
