"""
支付相关API端点
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.payment import PaymentMethod, Order
from app.services.payment_service import PaymentService


router = APIRouter()


# ========================================
# Pydantic模型
# ========================================

class CreateOrderRequest(BaseModel):
    """创建订单请求"""
    book_id: int = Field(..., description="书籍ID")
    payment_method: PaymentMethod = Field(
        PaymentMethod.STRIPE,
        description="支付方式"
    )


class OrderResponse(BaseModel):
    """订单响应"""
    id: int
    order_no: str
    user_id: int
    book_id: int
    amount: float
    status: str
    payment_method: str
    # payment_status: str  # 暂时注释，使用status字段
    created_at: str
    paid_at: str | None = None
    
    class Config:
        from_attributes = True


class PaymentRequest(BaseModel):
    """支付请求"""
    order_id: int = Field(..., description="订单ID")
    payment_method: PaymentMethod = Field(..., description="支付方式")
    stripe_token: str | None = Field(None, description="Stripe支付令牌")
    alipay_data: dict | None = Field(None, description="Alipay支付数据")


class RefundRequest(BaseModel):
    """退款请求"""
    order_id: int = Field(..., description="订单ID")
    refund_amount: float | None = Field(None, description="退款金额（null表示全额）")
    reason: str = Field("用户申请", description="退款原因")


# ========================================
# API端点
# ========================================

@router.post("/orders", response_model=OrderResponse, tags=["支付"])
async def create_order(
    request: CreateOrderRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    创建订单
    
    创建购买课程的订单，订单创建后需要调用支付接口完成支付。
    """
    try:
        # 获取书籍价格
        from app.services.book_service import BookService
        book = await BookService.get_book_by_id(db, request.book_id)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="书籍不存在"
            )
        
        if book.is_free:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="免费书籍无需购买"
            )
        
        # 创建订单
        order = await PaymentService.create_order(
            db,
            user_id=current_user.id,
            book_id=request.book_id,
            amount=book.price,
            payment_method=request.payment_method
        )
        
        return OrderResponse(
            id=order.id,
            order_no=order.order_no,
            user_id=order.user_id,
            book_id=order.book_id,
            amount=order.amount,
            status=order.status.value,
            payment_method=order.payment_method.value,
            # payment_status=order.payment_status.value,
            created_at=order.created_at.isoformat(),
            paid_at=order.paid_at.isoformat() if order.paid_at else None
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/pay", tags=["支付"])
async def process_payment(
    request: PaymentRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    处理支付
    
    根据支付方式处理支付请求：
    - Stripe: 需要提供stripe_token
    - Alipay: 需要提供alipay_data
    """
    try:
        if request.payment_method == PaymentMethod.STRIPE:
            if not request.stripe_token:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Stripe支付需要提供token"
                )
            result = await PaymentService.process_stripe_payment(
                db,
                request.order_id,
                request.stripe_token
            )
        elif request.payment_method == PaymentMethod.ALIPAY:
            if not request.alipay_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Alipay支付需要提供数据"
                )
            result = await PaymentService.process_alipay_payment(
                db,
                request.order_id,
                request.alipay_data
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的支付方式: {request.payment_method}"
            )
        
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/orders", response_model=List[OrderResponse], tags=["支付"])
async def get_my_orders(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取我的订单列表
    
    分页获取当前用户的所有订单。
    """
    orders = await PaymentService.get_user_orders(
        db,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
    
    return [
        OrderResponse(
            id=order.id,
            order_no=order.order_no,
            user_id=order.user_id,
            book_id=order.book_id,
            amount=order.amount,
            status=order.status.value,
            payment_method=order.payment_method.value,
            # payment_status=order.payment_status.value,
            created_at=order.created_at.isoformat(),
            paid_at=order.paid_at.isoformat() if order.paid_at else None
        )
        for order in orders
    ]


@router.get("/orders/{order_no}", response_model=OrderResponse, tags=["支付"])
async def get_order(
    order_no: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取订单详情
    
    通过订单号查询订单详情。
    """
    order = await PaymentService.get_order_by_no(db, order_no)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )
    
    # 检查订单所有权
    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此订单"
        )
    
    return OrderResponse(
        id=order.id,
        order_no=order.order_no,
        user_id=order.user_id,
        book_id=order.book_id,
        amount=order.amount,
        status=order.status.value,
        payment_method=order.payment_method.value,
        payment_status=order.payment_status.value,
        created_at=order.created_at.isoformat(),
        paid_at=order.paid_at.isoformat() if order.paid_at else None
    )


@router.post("/orders/{order_id}/cancel", tags=["支付"])
async def cancel_order(
    order_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    取消订单
    
    取消未支付的订单。已支付的订单需要申请退款。
    """
    try:
        order = await db.get(Order, order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="订单不存在"
            )
        
        if order.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权操作此订单"
            )
        
        order = await PaymentService.cancel_order(db, order_id)
        
        return {
            "message": "订单已取消",
            "order_no": order.order_no
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/refund", tags=["支付"])
async def refund_order(
    request: RefundRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    申请退款
    
    对已支付的订单申请全额或部分退款。
    """
    try:
        order = await db.get(Order, request.order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="订单不存在"
            )
        
        if order.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权操作此订单"
            )
        
        result = await PaymentService.refund_order(
            db,
            request.order_id,
            request.refund_amount,
            request.reason
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
