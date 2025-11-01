"""
支付和订单模型
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class OrderStatus(str, enum.Enum):
    """订单状态"""
    PENDING = "pending"        # 待支付
    PAID = "paid"             # 已支付
    CANCELLED = "cancelled"    # 已取消
    REFUNDED = "refunded"      # 已退款
    FAILED = "failed"         # 支付失败


class PaymentMethod(str, enum.Enum):
    """支付方式"""
    WECHAT = "wechat"          # 微信支付
    ALIPAY = "alipay"          # 支付宝
    STRIPE = "stripe"          # Stripe (信用卡)
    BALANCE = "balance"        # 账户余额


class Order(Base):
    """订单模型"""
    
    __tablename__ = "orders"
    
    # 基本信息
    id = Column(Integer, primary_key=True, index=True)
    order_no = Column(String(64), unique=True, index=True, nullable=False)  # 订单号
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # 订单类型
    order_type = Column(String(20), nullable=False)  # book | subscription
    
    # 商品信息
    book_id = Column(Integer, ForeignKey("books.id", ondelete="SET NULL"), nullable=True)
    product_name = Column(String(200), nullable=False)
    product_description = Column(String(500), nullable=True)
    
    # 金额
    original_price = Column(Float, nullable=False)
    discount_amount = Column(Float, default=0.0, nullable=False)
    final_price = Column(Float, nullable=False)
    currency = Column(String(10), default="CNY", nullable=False)
    
    # 支付信息
    payment_method = Column(SQLEnum(PaymentMethod), nullable=True)
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    
    # 第三方支付信息
    transaction_id = Column(String(128), unique=True, nullable=True)  # 第三方交易号
    payment_time = Column(DateTime(timezone=True), nullable=True)
    
    # 退款信息
    refund_reason = Column(String(500), nullable=True)
    refund_time = Column(DateTime(timezone=True), nullable=True)
    refund_amount = Column(Float, nullable=True)
    
    # 发票信息
    need_invoice = Column(Boolean, default=False, nullable=False)
    invoice_info = Column(JSON, nullable=True)
    
    # 备注
    remark = Column(String(500), nullable=True)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)  # 订单过期时间
    
    # 关系
    user = relationship("User", back_populates="orders")
    
    def __repr__(self):
        return f"<Order(id={self.id}, order_no={self.order_no}, status={self.status})>"


class SubscriptionStatus(str, enum.Enum):
    """订阅状态"""
    ACTIVE = "active"          # 激活中
    EXPIRED = "expired"        # 已过期
    CANCELLED = "cancelled"    # 已取消


class Subscription(Base):
    """订阅（会员）模型"""
    
    __tablename__ = "subscriptions"
    
    # 基本信息
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="SET NULL"), nullable=True)
    
    # 订阅类型
    plan_type = Column(String(20), nullable=False)  # monthly | yearly
    plan_name = Column(String(100), nullable=False)
    
    # 状态
    status = Column(SQLEnum(SubscriptionStatus), default=SubscriptionStatus.ACTIVE, nullable=False)
    
    # 时间
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    
    # 自动续费
    auto_renew = Column(Boolean, default=False, nullable=False)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    
    # 关系
    user = relationship("User", back_populates="subscriptions")
    
    def __repr__(self):
        return f"<Subscription(id={self.id}, user_id={self.user_id}, status={self.status})>"
