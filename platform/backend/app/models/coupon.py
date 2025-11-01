"""
优惠券模型
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class CouponType(str, enum.Enum):
    """优惠券类型"""
    PERCENTAGE = "percentage"  # 百分比折扣
    FIXED = "fixed"           # 固定金额
    
class CouponStatus(str, enum.Enum):
    """优惠券状态"""
    ACTIVE = "active"          # 激活
    INACTIVE = "inactive"      # 未激活
    EXPIRED = "expired"        # 已过期


class Coupon(Base):
    """优惠券模型"""
    
    __tablename__ = "coupons"
    
    # 基本信息
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)  # 优惠码
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    
    # 优惠类型和值
    coupon_type = Column(SQLEnum(CouponType), nullable=False)
    discount_value = Column(Float, nullable=False)  # 百分比或金额
    max_discount = Column(Float, nullable=True)  # 最大折扣金额（百分比券）
    min_purchase = Column(Float, default=0.0, nullable=False)  # 最低消费
    
    # 使用限制
    max_uses = Column(Integer, nullable=True)  # 最大使用次数(null=无限)
    used_count = Column(Integer, default=0, nullable=False)  # 已使用次数
    max_uses_per_user = Column(Integer, default=1, nullable=False)  # 每用户最大使用次数
    
    # 状态和时间
    status = Column(SQLEnum(CouponStatus), default=CouponStatus.ACTIVE, nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # 关系
    user_coupons = relationship("UserCoupon", back_populates="coupon", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Coupon(code={self.code}, type={self.coupon_type}, value={self.discount_value})>"


class UserCoupon(Base):
    """用户优惠券（领取记录）"""
    
    __tablename__ = "user_coupons"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    coupon_id = Column(Integer, ForeignKey("coupons.id", ondelete="CASCADE"), nullable=False)
    
    # 使用状态
    is_used = Column(Boolean, default=False, nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="SET NULL"), nullable=True)
    
    # 时间
    received_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)
    
    # 关系
    user = relationship("User", back_populates="user_coupons")
    coupon = relationship("Coupon", back_populates="user_coupons")
    order = relationship("Order")
    
    def __repr__(self):
        return f"<UserCoupon(user_id={self.user_id}, coupon_id={self.coupon_id}, used={self.is_used})>"
