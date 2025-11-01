"""
积分系统模型
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Boolean, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class TransactionType(str, enum.Enum):
    """交易类型"""
    EARN = "earn"      # 获得积分
    SPEND = "spend"    # 消费积分
    REFUND = "refund"  # 退款


class PointsReason(str, enum.Enum):
    """积分原因"""
    # 获得原因
    DAILY_LOGIN = "daily_login"           # 每日登录
    CASE_COMPLETE = "case_complete"       # 完成案例
    SHARE_COURSE = "share_course"         # 分享课程
    INVITE_FRIEND = "invite_friend"       # 邀请好友
    WRITE_NOTE = "write_note"             # 写笔记
    REVIEW_COURSE = "review_course"       # 课程评价
    ACHIEVEMENT = "achievement"           # 完成成就
    ADMIN_GRANT = "admin_grant"           # 管理员赠送
    
    # 消费原因
    REDEEM_COUPON = "redeem_coupon"       # 兑换优惠券
    REDEEM_COURSE = "redeem_course"       # 兑换课程
    REDEEM_MEMBERSHIP = "redeem_membership"  # 兑换会员
    REDEEM_GIFT = "redeem_gift"           # 兑换礼品


class ProductType(str, enum.Enum):
    """商品类型"""
    COUPON = "coupon"          # 优惠券
    COURSE = "course"          # 课程
    MEMBERSHIP = "membership"  # 会员天数
    GIFT = "gift"              # 实物礼品


class PointsAccount(Base):
    """积分账户"""
    
    __tablename__ = "points_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # 积分余额
    balance = Column(Integer, default=0, nullable=False)
    
    # 统计
    total_earned = Column(Integer, default=0, nullable=False)   # 总获得积分
    total_spent = Column(Integer, default=0, nullable=False)    # 总消费积分
    
    # 冻结积分（用于处理中的交易）
    frozen = Column(Integer, default=0, nullable=False)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # 关系
    user = relationship("User", backref="points_account")
    transactions = relationship("PointsTransaction", back_populates="account", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<PointsAccount(user_id={self.user_id}, balance={self.balance})>"


class PointsTransaction(Base):
    """积分交易记录"""
    
    __tablename__ = "points_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("points_accounts.id", ondelete="CASCADE"), nullable=False)
    
    # 交易信息
    transaction_type = Column(SQLEnum(TransactionType), nullable=False)
    amount = Column(Integer, nullable=False)  # 积分数量（正数）
    reason = Column(SQLEnum(PointsReason), nullable=False)
    description = Column(String(500), nullable=True)
    
    # 余额快照
    balance_before = Column(Integer, nullable=False)
    balance_after = Column(Integer, nullable=False)
    
    # 相关信息
    related_type = Column(String(50), nullable=True)
    related_id = Column(Integer, nullable=True)
    
    # 元数据
    meta_data = Column(JSON, nullable=True)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # 关系
    account = relationship("PointsAccount", back_populates="transactions")
    
    def __repr__(self):
        return f"<PointsTransaction(account_id={self.account_id}, type={self.transaction_type}, amount={self.amount})>"


class PointsProduct(Base):
    """积分商品"""
    
    __tablename__ = "points_products"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 商品信息
    name = Column(String(200), nullable=False)
    description = Column(String(1000), nullable=True)
    product_type = Column(SQLEnum(ProductType), nullable=False)
    
    # 价格
    points_cost = Column(Integer, nullable=False)
    
    # 商品详情（JSON）
    details = Column(JSON, nullable=True)
    # 格式根据product_type不同：
    # COUPON: {"coupon_code": "xxx", "discount": 0.8}
    # COURSE: {"book_id": 1}
    # MEMBERSHIP: {"days": 30, "level": "gold"}
    # GIFT: {"gift_id": "xxx", "address_required": true}
    
    # 库存
    stock = Column(Integer, nullable=True)  # None表示无限库存
    sold_count = Column(Integer, default=0, nullable=False)
    
    # 限制
    max_per_user = Column(Integer, nullable=True)  # 每人限购数量
    requires_level = Column(String(20), nullable=True)  # 需要的会员等级
    
    # 显示
    image_url = Column(String(500), nullable=True)
    sort_order = Column(Integer, default=0, nullable=False)
    
    # 状态
    is_active = Column(Boolean, default=True, nullable=False)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # 关系
    redemptions = relationship("PointsRedemption", back_populates="product", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<PointsProduct(id={self.id}, name={self.name}, cost={self.points_cost})>"


class PointsRedemption(Base):
    """积分兑换记录"""
    
    __tablename__ = "points_redemptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("points_products.id", ondelete="RESTRICT"), nullable=False)
    transaction_id = Column(Integer, ForeignKey("points_transactions.id", ondelete="SET NULL"), nullable=True)
    
    # 兑换信息
    points_cost = Column(Integer, nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    
    # 状态
    status = Column(String(20), default="pending", nullable=False)  # pending, completed, cancelled
    
    # 收货信息（如果需要）
    shipping_info = Column(JSON, nullable=True)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # 关系
    user = relationship("User")
    product = relationship("PointsProduct", back_populates="redemptions")
    transaction = relationship("PointsTransaction")
    
    def __repr__(self):
        return f"<PointsRedemption(user_id={self.user_id}, product_id={self.product_id}, status={self.status})>"


class PointsRule(Base):
    """积分规则配置"""
    
    __tablename__ = "points_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    reason = Column(SQLEnum(PointsReason), unique=True, nullable=False)
    
    # 积分配置
    points = Column(Integer, nullable=False)
    description = Column(String(500), nullable=True)
    
    # 限制
    daily_limit = Column(Integer, nullable=True)    # 每日限制次数
    total_limit = Column(Integer, nullable=True)    # 总限制次数
    
    # 条件（JSON）
    conditions = Column(JSON, nullable=True)
    # 例如: {"min_score": 80, "min_time": 300}
    
    # 状态
    is_active = Column(Boolean, default=True, nullable=False)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<PointsRule(reason={self.reason}, points={self.points})>"
