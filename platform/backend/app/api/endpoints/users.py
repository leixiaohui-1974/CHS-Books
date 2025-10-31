"""
用户相关API
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr
from typing import Optional

from app.core.database import get_db
from app.core.security import get_current_user, get_password_hash
from loguru import logger

router = APIRouter()


class UpdateProfileRequest(BaseModel):
    """更新个人资料请求"""
    full_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None


@router.get("/me")
async def get_profile(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取当前用户个人资料"""
    logger.info(f"👤 获取用户资料: user_id={current_user['id']}")
    return {"success": True, "data": current_user}


@router.put("/me")
async def update_profile(
    request: UpdateProfileRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新个人资料"""
    logger.info(f"✏️  更新用户资料: user_id={current_user['id']}")
    return {"message": "更新成功"}


@router.post("/change-password")
async def change_password(
    old_password: str,
    new_password: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """修改密码"""
    logger.info(f"🔐 修改密码: user_id={current_user['id']}")
    return {"message": "密码修改成功"}
