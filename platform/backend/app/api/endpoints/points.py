"""
积分系统API端点
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.points import ProductType
from app.services.points_service import points_service

router = APIRouter()

@router.get("/my-account", tags=["积分系统"])
async def get_my_points_account(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取我的积分账户"""
    try:
        info = await points_service.get_account_info(db, current_user.id)
        return info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/transactions", tags=["积分系统"])
async def get_my_transactions(
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取积分明细"""
    try:
        transactions = await points_service.get_transactions(db, current_user.id, limit=limit, offset=offset)
        return {"transactions": transactions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/shop", tags=["积分系统"])
async def get_points_shop(
    product_type: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取积分商城"""
    try:
        ptype = ProductType(product_type) if product_type else None
        products = await points_service.get_products(db, product_type=ptype)
        return {"products": products}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
