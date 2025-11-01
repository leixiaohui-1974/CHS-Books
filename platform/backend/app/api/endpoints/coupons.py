"""
优惠券API端点
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.services.coupon_service import CouponService


router = APIRouter()


# Pydantic模型
class ValidateCouponRequest(BaseModel):
    """验证优惠券请求"""
    code: str = Field(..., min_length=1, max_length=50, description="优惠券代码")
    order_amount: float = Field(..., gt=0, description="订单金额")


class CouponResponse(BaseModel):
    """优惠券响应"""
    user_coupon_id: int
    code: str
    name: str
    description: str | None
    type: str
    discount_value: float
    min_purchase: float
    is_used: bool
    received_at: str
    used_at: str | None
    start_date: str
    end_date: str
    status: str


# API端点
@router.post("/validate", tags=["优惠券"])
async def validate_coupon(
    request: ValidateCouponRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    验证优惠券
    
    检查优惠券是否有效，并计算折扣金额。
    """
    result = await CouponService.validate_coupon(
        db=db,
        code=request.code,
        user_id=current_user.id,
        order_amount=request.order_amount
    )
    
    if not result.get("valid"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "优惠券无效")
        )
    
    return result


@router.get("/my-coupons", response_model=List[CouponResponse], tags=["优惠券"])
async def get_my_coupons(
    unused_only: bool = Query(False, description="只返回未使用的"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取我的优惠券
    
    返回用户拥有的所有优惠券。
    """
    coupons = await CouponService.get_user_coupons(
        db=db,
        user_id=current_user.id,
        unused_only=unused_only
    )
    
    return coupons


@router.get("/available", tags=["优惠券"])
async def get_available_coupons(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取可用优惠券列表
    
    返回用户未使用且未过期的优惠券。
    """
    from datetime import datetime, timezone
    from sqlalchemy import select, and_
    from app.models.coupon import Coupon, CouponStatus
    
    # 获取所有激活且未过期的优惠券
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(Coupon).where(
            and_(
                Coupon.status == CouponStatus.ACTIVE,
                Coupon.start_date <= now,
                Coupon.end_date >= now
            )
        )
    )
    coupons = result.scalars().all()
    
    available = []
    for coupon in coupons:
        # 检查是否还有使用次数
        if coupon.max_uses and coupon.used_count >= coupon.max_uses:
            continue
        
        available.append({
            "id": coupon.id,
            "code": coupon.code,
            "name": coupon.name,
            "description": coupon.description,
            "type": coupon.coupon_type.value,
            "discount_value": coupon.discount_value,
            "min_purchase": coupon.min_purchase,
            "end_date": coupon.end_date.isoformat(),
            "remaining_uses": (coupon.max_uses - coupon.used_count) if coupon.max_uses else None
        })
    
    return {
        "total": len(available),
        "coupons": available
    }
