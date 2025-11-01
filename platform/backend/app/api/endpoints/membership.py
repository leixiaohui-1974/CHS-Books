"""
会员体系API端点
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.services.membership_service import membership_service

router = APIRouter()

@router.get("/my-info", tags=["会员体系"])
async def get_my_membership(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取我的会员信息"""
    try:
        info = await membership_service.get_membership_info(db, current_user.id)
        return info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/exp-history", tags=["会员体系"])
async def get_experience_history(
    limit: int = 20,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取经验值历史"""
    try:
        history = await membership_service.get_experience_history(db, current_user.id, limit)
        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
