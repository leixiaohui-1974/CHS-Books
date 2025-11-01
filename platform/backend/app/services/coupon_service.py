"""
优惠券服务
"""

from typing import Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from loguru import logger

from app.models.coupon import Coupon, UserCoupon, CouponType, CouponStatus
from app.models.user import User


class CouponService:
    """优惠券服务类"""
    
    @staticmethod
    async def validate_coupon(
        db: AsyncSession,
        code: str,
        user_id: int,
        order_amount: float
    ) -> dict:
        """
        验证优惠券
        
        Args:
            db: 数据库会话
            code: 优惠券代码
            user_id: 用户ID
            order_amount: 订单金额
        
        Returns:
            验证结果和折扣信息
        """
        # 查询优惠券
        result = await db.execute(
            select(Coupon).where(Coupon.code == code)
        )
        coupon = result.scalar_one_or_none()
        
        if not coupon:
            return {"valid": False, "error": "优惠券不存在"}
        
        # 检查状态
        if coupon.status != CouponStatus.ACTIVE:
            return {"valid": False, "error": "优惠券未激活"}
        
        # 检查时间
        now = datetime.now(timezone.utc)
        if now < coupon.start_date:
            return {"valid": False, "error": "优惠券未到使用时间"}
        if now > coupon.end_date:
            return {"valid": False, "error": "优惠券已过期"}
        
        # 检查总使用次数
        if coupon.max_uses and coupon.used_count >= coupon.max_uses:
            return {"valid": False, "error": "优惠券已被领完"}
        
        # 检查用户使用次数
        result = await db.execute(
            select(UserCoupon).where(
                and_(
                    UserCoupon.user_id == user_id,
                    UserCoupon.coupon_id == coupon.id,
                    UserCoupon.is_used == True
                )
            )
        )
        user_used_count = len(result.scalars().all())
        
        if user_used_count >= coupon.max_uses_per_user:
            return {"valid": False, "error": f"您已使用过此优惠券（限{coupon.max_uses_per_user}次）"}
        
        # 检查最低消费
        if order_amount < coupon.min_purchase:
            return {
                "valid": False,
                "error": f"订单金额未达到最低消费要求（¥{coupon.min_purchase}）"
            }
        
        # 计算折扣
        discount = CouponService._calculate_discount(coupon, order_amount)
        
        logger.info(f"优惠券验证成功 - 代码: {code}, 用户: {user_id}, 折扣: ¥{discount}")
        
        return {
            "valid": True,
            "coupon_id": coupon.id,
            "discount": discount,
            "final_amount": max(order_amount - discount, 0),
            "coupon_name": coupon.name
        }
    
    @staticmethod
    async def apply_coupon(
        db: AsyncSession,
        user_id: int,
        coupon_id: int,
        order_id: int
    ) -> bool:
        """
        应用优惠券到订单
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            coupon_id: 优惠券ID
            order_id: 订单ID
        
        Returns:
            是否成功
        """
        try:
            # 查找用户优惠券记录
            result = await db.execute(
                select(UserCoupon).where(
                    and_(
                        UserCoupon.user_id == user_id,
                        UserCoupon.coupon_id == coupon_id,
                        UserCoupon.is_used == False
                    )
                )
            )
            user_coupon = result.scalar_one_or_none()
            
            if not user_coupon:
                # 创建新记录
                user_coupon = UserCoupon(
                    user_id=user_id,
                    coupon_id=coupon_id
                )
                db.add(user_coupon)
            
            # 标记为已使用
            user_coupon.is_used = True
            user_coupon.order_id = order_id
            user_coupon.used_at = datetime.now(timezone.utc)
            
            # 更新优惠券使用次数
            coupon = await db.get(Coupon, coupon_id)
            if coupon:
                coupon.used_count += 1
            
            await db.commit()
            
            logger.info(f"优惠券应用成功 - 用户: {user_id}, 订单: {order_id}")
            return True
            
        except Exception as e:
            logger.error(f"应用优惠券失败: {e}")
            await db.rollback()
            return False
    
    @staticmethod
    async def get_user_coupons(
        db: AsyncSession,
        user_id: int,
        unused_only: bool = False
    ) -> list:
        """
        获取用户的优惠券列表
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            unused_only: 是否只返回未使用的
        
        Returns:
            优惠券列表
        """
        query = select(UserCoupon).where(UserCoupon.user_id == user_id)
        
        if unused_only:
            query = query.where(UserCoupon.is_used == False)
        
        result = await db.execute(query)
        user_coupons = result.scalars().all()
        
        # 加载关联的优惠券信息
        coupons_data = []
        for uc in user_coupons:
            coupon = await db.get(Coupon, uc.coupon_id)
            if coupon:
                coupons_data.append({
                    "user_coupon_id": uc.id,
                    "code": coupon.code,
                    "name": coupon.name,
                    "description": coupon.description,
                    "type": coupon.coupon_type.value,
                    "discount_value": coupon.discount_value,
                    "min_purchase": coupon.min_purchase,
                    "is_used": uc.is_used,
                    "received_at": uc.received_at.isoformat(),
                    "used_at": uc.used_at.isoformat() if uc.used_at else None,
                    "start_date": coupon.start_date.isoformat(),
                    "end_date": coupon.end_date.isoformat(),
                    "status": coupon.status.value
                })
        
        return coupons_data
    
    @staticmethod
    def _calculate_discount(coupon: Coupon, order_amount: float) -> float:
        """计算折扣金额"""
        if coupon.coupon_type == CouponType.PERCENTAGE:
            # 百分比折扣
            discount = order_amount * (coupon.discount_value / 100)
            # 检查最大折扣限制
            if coupon.max_discount:
                discount = min(discount, coupon.max_discount)
        else:
            # 固定金额折扣
            discount = min(coupon.discount_value, order_amount)
        
        return round(discount, 2)


# 便捷函数
async def validate_coupon(
    db: AsyncSession,
    code: str,
    user_id: int,
    order_amount: float
) -> dict:
    """验证优惠券"""
    return await CouponService.validate_coupon(db, code, user_id, order_amount)


async def apply_coupon(
    db: AsyncSession,
    user_id: int,
    coupon_id: int,
    order_id: int
) -> bool:
    """应用优惠券"""
    return await CouponService.apply_coupon(db, user_id, coupon_id, order_id)
