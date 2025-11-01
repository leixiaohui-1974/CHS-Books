"""
支付服务
处理Stripe和Alipay支付集成
"""

import os
from typing import Optional, Dict, Any
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger

from app.models.payment import Order, OrderStatus, PaymentMethod
from app.models.user import User
from app.models.book import Book


class PaymentService:
    """支付服务类"""
    
    @staticmethod
    async def create_order(
        db: AsyncSession,
        user_id: int,
        book_id: int,
        amount: float,
        payment_method: PaymentMethod = PaymentMethod.STRIPE
    ) -> Order:
        """
        创建订单
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            book_id: 书籍ID
            amount: 金额
            payment_method: 支付方式
        
        Returns:
            Order对象
        """
        # 检查用户
        user = await db.get(User, user_id)
        if not user:
            raise ValueError("用户不存在")
        
        # 检查书籍
        book = await db.get(Book, book_id)
        if not book:
            raise ValueError("书籍不存在")
        
        # 生成订单号
        order_no = PaymentService._generate_order_no()
        
        # 创建订单
        order = Order(
            order_no=order_no,
            user_id=user_id,
            book_id=book_id,
            amount=amount,
            status=OrderStatus.PENDING,
            payment_method=payment_method,
            payment_status=PaymentStatus.PENDING,
            created_at=datetime.now(timezone.utc)
        )
        
        db.add(order)
        await db.commit()
        await db.refresh(order)
        
        logger.info(f"订单创建成功: {order_no}, 用户: {user_id}, 金额: {amount}")
        return order
    
    @staticmethod
    async def process_stripe_payment(
        db: AsyncSession,
        order_id: int,
        stripe_token: str
    ) -> Dict[str, Any]:
        """
        处理Stripe支付
        
        Args:
            db: 数据库会话
            order_id: 订单ID
            stripe_token: Stripe支付令牌
        
        Returns:
            支付结果
        """
        # 获取订单
        order = await db.get(Order, order_id)
        if not order:
            raise ValueError("订单不存在")
        
        if order.status != OrderStatus.PENDING:
            raise ValueError(f"订单状态不正确: {order.status}")
        
        try:
            # TODO: 实际集成Stripe API
            # import stripe
            # stripe.api_key = os.getenv("STRIPE_API_KEY")
            # charge = stripe.Charge.create(
            #     amount=int(order.amount * 100),  # 转换为分
            #     currency="usd",
            #     source=stripe_token,
            #     description=f"Order {order.order_no}"
            # )
            
            # 模拟支付成功
            order.status = OrderStatus.PAID
            order.payment_status = PaymentStatus.SUCCESS
            order.paid_at = datetime.now(timezone.utc)
            order.transaction_id = f"stripe_{stripe_token[:20]}"
            
            await db.commit()
            await db.refresh(order)
            
            logger.info(f"Stripe支付成功: {order.order_no}")
            
            return {
                "success": True,
                "order_no": order.order_no,
                "amount": order.amount,
                "paid_at": order.paid_at.isoformat()
            }
            
        except Exception as e:
            # 支付失败
            order.status = OrderStatus.FAILED
            order.payment_status = PaymentStatus.FAILED
            await db.commit()
            
            logger.error(f"Stripe支付失败: {order.order_no}, 错误: {e}")
            
            return {
                "success": False,
                "order_no": order.order_no,
                "error": str(e)
            }
    
    @staticmethod
    async def process_alipay_payment(
        db: AsyncSession,
        order_id: int,
        alipay_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        处理Alipay支付
        
        Args:
            db: 数据库会话
            order_id: 订单ID
            alipay_data: Alipay支付数据
        
        Returns:
            支付结果
        """
        # 获取订单
        order = await db.get(Order, order_id)
        if not order:
            raise ValueError("订单不存在")
        
        if order.status != OrderStatus.PENDING:
            raise ValueError(f"订单状态不正确: {order.status}")
        
        try:
            # TODO: 实际集成Alipay API
            # from alipay import AliPay
            # alipay = AliPay(...)
            # result = alipay.verify(alipay_data)
            
            # 模拟支付成功
            order.status = OrderStatus.PAID
            order.paid_at = datetime.now(timezone.utc)
            order.transaction_id = f"alipay_{alipay_data.get('trade_no', 'mock')}"
            
            await db.commit()
            await db.refresh(order)
            
            logger.info(f"Alipay支付成功: {order.order_no}")
            
            return {
                "success": True,
                "order_no": order.order_no,
                "amount": order.amount,
                "paid_at": order.paid_at.isoformat()
            }
            
        except Exception as e:
            # 支付失败
            order.status = OrderStatus.FAILED
            await db.commit()
            
            logger.error(f"Alipay支付失败: {order.order_no}, 错误: {e}")
            
            return {
                "success": False,
                "order_no": order.order_no,
                "error": str(e)
            }
    
    @staticmethod
    async def get_user_orders(
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 20
    ) -> list[Order]:
        """
        获取用户订单列表
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            skip: 跳过数量
            limit: 返回数量
        
        Returns:
            订单列表
        """
        result = await db.execute(
            select(Order)
            .where(Order.user_id == user_id)
            .order_by(Order.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_order_by_no(
        db: AsyncSession,
        order_no: str
    ) -> Optional[Order]:
        """
        通过订单号获取订单
        
        Args:
            db: 数据库会话
            order_no: 订单号
        
        Returns:
            Order对象或None
        """
        result = await db.execute(
            select(Order).where(Order.order_no == order_no)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def cancel_order(
        db: AsyncSession,
        order_id: int,
        reason: str = "用户取消"
    ) -> Order:
        """
        取消订单
        
        Args:
            db: 数据库会话
            order_id: 订单ID
            reason: 取消原因
        
        Returns:
            更新后的Order对象
        """
        order = await db.get(Order, order_id)
        if not order:
            raise ValueError("订单不存在")
        
        if order.status not in [OrderStatus.PENDING, OrderStatus.FAILED]:
            raise ValueError(f"订单状态不允许取消: {order.status}")
        
        order.status = OrderStatus.CANCELLED
        order.cancelled_at = datetime.now(timezone.utc)
        
        await db.commit()
        await db.refresh(order)
        
        logger.info(f"订单已取消: {order.order_no}, 原因: {reason}")
        return order
    
    @staticmethod
    async def refund_order(
        db: AsyncSession,
        order_id: int,
        refund_amount: Optional[float] = None,
        reason: str = "用户申请"
    ) -> Dict[str, Any]:
        """
        退款
        
        Args:
            db: 数据库会话
            order_id: 订单ID
            refund_amount: 退款金额（None表示全额退款）
            reason: 退款原因
        
        Returns:
            退款结果
        """
        order = await db.get(Order, order_id)
        if not order:
            raise ValueError("订单不存在")
        
        if order.status != OrderStatus.PAID:
            raise ValueError(f"订单状态不允许退款: {order.status}")
        
        if refund_amount is None:
            refund_amount = order.amount
        
        if refund_amount > order.amount:
            raise ValueError("退款金额不能超过订单金额")
        
        try:
            # TODO: 实际调用支付平台退款API
            # if order.payment_method == PaymentMethod.STRIPE:
            #     stripe.Refund.create(charge=order.transaction_id, amount=...)
            # elif order.payment_method == PaymentMethod.ALIPAY:
            #     alipay.refund(...)
            
            # 模拟退款成功
            order.status = OrderStatus.REFUNDED
            order.refunded_at = datetime.now(timezone.utc)
            order.refund_amount = refund_amount
            
            await db.commit()
            await db.refresh(order)
            
            logger.info(f"退款成功: {order.order_no}, 金额: {refund_amount}, 原因: {reason}")
            
            return {
                "success": True,
                "order_no": order.order_no,
                "refund_amount": refund_amount,
                "refunded_at": order.refunded_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"退款失败: {order.order_no}, 错误: {e}")
            
            return {
                "success": False,
                "order_no": order.order_no,
                "error": str(e)
            }
    
    @staticmethod
    def _generate_order_no() -> str:
        """生成订单号"""
        import random
        import string
        
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_str = ''.join(random.choices(string.digits, k=6))
        return f"ORD{timestamp}{random_str}"


# 便捷函数
async def create_order(
    db: AsyncSession,
    user_id: int,
    book_id: int,
    amount: float,
    payment_method: PaymentMethod = PaymentMethod.STRIPE
) -> Order:
    """创建订单"""
    return await PaymentService.create_order(db, user_id, book_id, amount, payment_method)


async def process_payment(
    db: AsyncSession,
    order_id: int,
    payment_method: PaymentMethod,
    payment_data: Dict[str, Any]
) -> Dict[str, Any]:
    """处理支付"""
    if payment_method == PaymentMethod.STRIPE:
        return await PaymentService.process_stripe_payment(
            db, order_id, payment_data.get("token", "")
        )
    elif payment_method == PaymentMethod.ALIPAY:
        return await PaymentService.process_alipay_payment(
            db, order_id, payment_data
        )
    else:
        raise ValueError(f"不支持的支付方式: {payment_method}")
