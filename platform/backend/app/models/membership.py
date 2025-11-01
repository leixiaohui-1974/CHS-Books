"""
会员体系模型
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Boolean, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class MembershipLevel(str, enum.Enum):
    """会员等级"""
    FREE = "free"          # 免费用户
    BRONZE = "bronze"      # 青铜会员: 0-1000经验
    SILVER = "silver"      # 白银会员: 1001-5000经验
    GOLD = "gold"          # 黄金会员: 5001-10000经验
    PLATINUM = "platinum"  # 铂金会员: 10001-30000经验
    DIAMOND = "diamond"    # 钻石会员: 30001+经验


class BenefitType(str, enum.Enum):
    """权益类型"""
    COURSE_DISCOUNT = "course_discount"      # 课程折扣
    FREE_TOOL_USES = "free_tool_uses"       # 免费工具使用次数
    AI_CHAT_QUOTA = "ai_chat_quota"         # AI对话额度
    STORAGE_SPACE = "storage_space"         # 存储空间
    PRIORITY_SUPPORT = "priority_support"   # 优先客服
    EXCLUSIVE_CONTENT = "exclusive_content" # 专属内容


class UserMembership(Base):
    """用户会员信息"""
    
    __tablename__ = "user_memberships"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # 会员等级
    level = Column(SQLEnum(MembershipLevel), default=MembershipLevel.FREE, nullable=False)
    
    # 经验值
    experience_points = Column(Integer, default=0, nullable=False)
    
    # 会员期限
    is_lifetime = Column(Boolean, default=False, nullable=False)  # 是否终身会员
    expires_at = Column(DateTime(timezone=True), nullable=True)   # 到期时间
    
    # 权益使用情况（JSON存储）
    benefits_usage = Column(JSON, nullable=True, default=dict)
    # 格式: {
    #   "free_tool_uses": {"used": 10, "total": 100},
    #   "ai_chat_quota": {"used": 50, "total": 200}
    # }
    
    # 统计
    total_spent = Column(Float, default=0.0, nullable=False)      # 总消费金额
    upgrade_count = Column(Integer, default=0, nullable=False)    # 升级次数
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_upgrade_at = Column(DateTime(timezone=True), nullable=True)
    
    # 关系
    user = relationship("User", backref="membership")
    exp_history = relationship("ExperienceHistory", back_populates="user_membership", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<UserMembership(user_id={self.user_id}, level={self.level}, exp={self.experience_points})>"
    
    @property
    def level_progress(self) -> float:
        """当前等级进度百分比"""
        level_ranges = {
            MembershipLevel.FREE: (0, 0),
            MembershipLevel.BRONZE: (0, 1000),
            MembershipLevel.SILVER: (1001, 5000),
            MembershipLevel.GOLD: (5001, 10000),
            MembershipLevel.PLATINUM: (10001, 30000),
            MembershipLevel.DIAMOND: (30001, float('inf'))
        }
        
        min_exp, max_exp = level_ranges.get(self.level, (0, 1))
        if max_exp == float('inf'):
            return 100.0
        
        if max_exp == min_exp:
            return 0.0
        
        return ((self.experience_points - min_exp) / (max_exp - min_exp)) * 100


class ExperienceHistory(Base):
    """经验值历史记录"""
    
    __tablename__ = "experience_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_membership_id = Column(Integer, ForeignKey("user_memberships.id", ondelete="CASCADE"), nullable=False)
    
    # 经验变更
    amount = Column(Integer, nullable=False)  # 正数为获得，负数为扣除
    reason = Column(String(200), nullable=False)  # 变更原因
    
    # 相关信息
    related_type = Column(String(50), nullable=True)  # 相关类型：case_complete, daily_login, etc.
    related_id = Column(Integer, nullable=True)       # 相关ID
    
    # 元数据
    meta_data = Column(JSON, nullable=True)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # 关系
    user_membership = relationship("UserMembership", back_populates="exp_history")
    
    def __repr__(self):
        return f"<ExperienceHistory(user_membership_id={self.user_membership_id}, amount={self.amount})>"


class MembershipConfig(Base):
    """会员配置（管理员配置）"""
    
    __tablename__ = "membership_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    level = Column(SQLEnum(MembershipLevel), unique=True, nullable=False)
    
    # 等级要求
    min_experience = Column(Integer, nullable=False)
    max_experience = Column(Integer, nullable=True)  # None表示无上限
    
    # 会员价格
    monthly_price = Column(Float, nullable=True)     # 月度价格
    yearly_price = Column(Float, nullable=True)      # 年度价格
    lifetime_price = Column(Float, nullable=True)    # 终身价格
    
    # 权益配置（JSON）
    benefits = Column(JSON, nullable=True, default=dict)
    # 格式: {
    #   "course_discount": 0.9,  # 9折
    #   "free_tool_uses": 100,
    #   "ai_chat_quota": 200,
    #   "storage_space": 10240,  # MB
    #   "priority_support": true
    # }
    
    # 描述
    name = Column(String(50), nullable=False)
    description = Column(String(500), nullable=True)
    icon = Column(String(200), nullable=True)
    color = Column(String(20), nullable=True)
    
    # 状态
    is_active = Column(Boolean, default=True, nullable=False)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<MembershipConfig(level={self.level}, name={self.name})>"
