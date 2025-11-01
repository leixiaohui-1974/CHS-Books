"""
订单统计API端点
"""

from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.payment import Order, OrderStatus, PaymentMethod


router = APIRouter()


@router.get("/my-orders/stats", tags=["订单统计"])
async def get_my_order_stats(
    days: int = Query(30, ge=1, le=365, description="统计天数"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取我的订单统计
    
    返回指定时间段内的订单统计数据。
    """
    start_date = datetime.now(timezone.utc) - timedelta(days=days)
    
    # 总订单数
    result = await db.execute(
        select(func.count(Order.id))
        .where(
            and_(
                Order.user_id == current_user.id,
                Order.created_at >= start_date
            )
        )
    )
    total_orders = result.scalar() or 0
    
    # 已支付订单数
    result = await db.execute(
        select(func.count(Order.id))
        .where(
            and_(
                Order.user_id == current_user.id,
                Order.status == OrderStatus.PAID,
                Order.created_at >= start_date
            )
        )
    )
    paid_orders = result.scalar() or 0
    
    # 总消费金额
    result = await db.execute(
        select(func.sum(Order.final_price))
        .where(
            and_(
                Order.user_id == current_user.id,
                Order.status == OrderStatus.PAID,
                Order.created_at >= start_date
            )
        )
    )
    total_spent = float(result.scalar() or 0)
    
    # 待支付订单数
    result = await db.execute(
        select(func.count(Order.id))
        .where(
            and_(
                Order.user_id == current_user.id,
                Order.status == OrderStatus.PENDING,
                Order.created_at >= start_date
            )
        )
    )
    pending_orders = result.scalar() or 0
    
    # 按支付方式统计
    result = await db.execute(
        select(
            Order.payment_method,
            func.count(Order.id).label("count"),
            func.sum(Order.final_price).label("total")
        )
        .where(
            and_(
                Order.user_id == current_user.id,
                Order.status == OrderStatus.PAID,
                Order.payment_method.isnot(None),
                Order.created_at >= start_date
            )
        )
        .group_by(Order.payment_method)
    )
    payment_methods = []
    for row in result:
        payment_methods.append({
            "method": row.payment_method.value if row.payment_method else "unknown",
            "count": row.count,
            "total": float(row.total or 0)
        })
    
    return {
        "period_days": days,
        "total_orders": total_orders,
        "paid_orders": paid_orders,
        "pending_orders": pending_orders,
        "cancelled_orders": total_orders - paid_orders - pending_orders,
        "total_spent": total_spent,
        "average_order_value": round(total_spent / max(paid_orders, 1), 2),
        "payment_methods": payment_methods
    }


@router.get("/my-orders/trend", tags=["订单统计"])
async def get_my_order_trend(
    days: int = Query(7, ge=1, le=30, description="统计天数"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取我的订单趋势
    
    返回每日订单统计数据。
    """
    trend_data = []
    
    for i in range(days):
        date = datetime.now(timezone.utc) - timedelta(days=i)
        date_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        date_end = date.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # 当日订单数
        result = await db.execute(
            select(func.count(Order.id))
            .where(
                and_(
                    Order.user_id == current_user.id,
                    Order.created_at.between(date_start, date_end)
                )
            )
        )
        order_count = result.scalar() or 0
        
        # 当日消费
        result = await db.execute(
            select(func.sum(Order.final_price))
            .where(
                and_(
                    Order.user_id == current_user.id,
                    Order.status == OrderStatus.PAID,
                    Order.payment_time.between(date_start, date_end)
                )
            )
        )
        spent = float(result.scalar() or 0)
        
        trend_data.append({
            "date": date.strftime("%Y-%m-%d"),
            "orders": order_count,
            "spent": spent
        })
    
    return {
        "days": days,
        "data": list(reversed(trend_data))
    }


@router.get("/admin/orders/stats", tags=["订单统计", "管理"])
async def get_admin_order_stats(
    days: int = Query(30, ge=1, le=365, description="统计天数"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取平台订单统计（管理员）
    
    需要管理员权限。
    """
    # TODO: 添加管理员权限检查
    # if not current_user.is_admin:
    #     raise HTTPException(status_code=403, detail="需要管理员权限")
    
    start_date = datetime.now(timezone.utc) - timedelta(days=days)
    
    # 总订单数
    result = await db.execute(
        select(func.count(Order.id))
        .where(Order.created_at >= start_date)
    )
    total_orders = result.scalar() or 0
    
    # 总收入
    result = await db.execute(
        select(func.sum(Order.final_price))
        .where(
            and_(
                Order.status == OrderStatus.PAID,
                Order.created_at >= start_date
            )
        )
    )
    total_revenue = float(result.scalar() or 0)
    
    # 活跃用户数
    result = await db.execute(
        select(func.count(func.distinct(Order.user_id)))
        .where(
            and_(
                Order.status == OrderStatus.PAID,
                Order.created_at >= start_date
            )
        )
    )
    active_users = result.scalar() or 0
    
    # 按状态统计
    result = await db.execute(
        select(
            Order.status,
            func.count(Order.id).label("count")
        )
        .where(Order.created_at >= start_date)
        .group_by(Order.status)
    )
    status_stats = []
    for row in result:
        status_stats.append({
            "status": row.status.value,
            "count": row.count
        })
    
    # 按支付方式统计
    result = await db.execute(
        select(
            Order.payment_method,
            func.count(Order.id).label("count"),
            func.sum(Order.final_price).label("revenue")
        )
        .where(
            and_(
                Order.status == OrderStatus.PAID,
                Order.payment_method.isnot(None),
                Order.created_at >= start_date
            )
        )
        .group_by(Order.payment_method)
    )
    payment_stats = []
    for row in result:
        payment_stats.append({
            "method": row.payment_method.value if row.payment_method else "unknown",
            "count": row.count,
            "revenue": float(row.revenue or 0)
        })
    
    return {
        "period_days": days,
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "active_users": active_users,
        "average_order_value": round(total_revenue / max(total_orders, 1), 2),
        "status_distribution": status_stats,
        "payment_methods": payment_stats
    }
