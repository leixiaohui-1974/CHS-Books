"""
认证相关模型
包括：OAuth账号、双因素认证、Token管理、登录历史、验证码
"""

from sqlalchemy import Column, Integer, BigInteger, String, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.core.database import Base


class OAuthProvider(str, enum.Enum):
    """OAuth提供商枚举"""
    WECHAT = "wechat"
    GITHUB = "github"
    GOOGLE = "google"
    QQ = "qq"
    WEIBO = "weibo"


class TwoFactorMethod(str, enum.Enum):
    """双因素认证方法枚举"""
    TOTP = "totp"  # Time-based One-Time Password
    SMS = "sms"    # 短信验证码
    EMAIL = "email"  # 邮箱验证码


class TokenType(str, enum.Enum):
    """Token类型枚举"""
    ACCESS = "access"
    REFRESH = "refresh"
    RESET_PASSWORD = "reset_password"
    EMAIL_VERIFICATION = "email_verification"


class VerificationType(str, enum.Enum):
    """验证码类型枚举"""
    REGISTER = "register"
    LOGIN = "login"
    RESET_PASSWORD = "reset_password"
    CHANGE_EMAIL = "change_email"
    CHANGE_PHONE = "change_phone"
    TWO_FACTOR = "two_factor"


class OAuthAccount(Base):
    """OAuth账号关联表"""
    
    __tablename__ = "oauth_accounts"
    
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # OAuth信息
    provider = Column(String(20), nullable=False, index=True)  # wechat, github, google等
    provider_user_id = Column(String(100), nullable=False)  # 第三方平台的用户ID
    
    # Token信息
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    token_expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # 第三方用户信息（可选）
    provider_username = Column(String(100), nullable=True)
    provider_email = Column(String(255), nullable=True)
    provider_avatar = Column(String(500), nullable=True)
    
    # 额外数据
    extra_data = Column(JSON, nullable=True)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # 关系
    user = relationship("User", back_populates="oauth_accounts")
    
    # 唯一约束
    __table_args__ = (
        # 同一个provider下的provider_user_id必须唯一
        # UniqueConstraint('provider', 'provider_user_id', name='uq_oauth_provider_user'),
    )
    
    def __repr__(self):
        return f"<OAuthAccount(id={self.id}, user_id={self.user_id}, provider={self.provider})>"


class TwoFactorAuth(Base):
    """双因素认证表"""
    
    __tablename__ = "two_factor_auth"
    
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    
    # 认证方法
    method = Column(String(20), nullable=False)  # totp, sms, email
    
    # TOTP密钥（用于Google Authenticator等）
    secret = Column(String(100), nullable=True)
    
    # 备用码（JSON数组）
    backup_codes = Column(JSON, nullable=True)
    
    # 状态
    enabled = Column(Boolean, default=False, nullable=False)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    
    # 关系
    user = relationship("User", back_populates="two_factor_auth", uselist=False)
    
    def __repr__(self):
        return f"<TwoFactorAuth(id={self.id}, user_id={self.user_id}, method={self.method}, enabled={self.enabled})>"


class UserToken(Base):
    """用户Token表"""
    
    __tablename__ = "user_tokens"
    
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Token信息
    token = Column(String(500), unique=True, nullable=False, index=True)
    token_type = Column(String(20), nullable=False)  # access, refresh, reset_password等
    
    # 设备信息
    device_id = Column(String(100), nullable=True)
    device_name = Column(String(100), nullable=True)
    device_type = Column(String(20), nullable=True)  # desktop, mobile, tablet
    device_info = Column(JSON, nullable=True)  # 详细设备信息（OS、浏览器等）
    
    # IP信息
    ip_address = Column(String(45), nullable=True)
    
    # 过期时间
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    
    # 是否已撤销
    revoked = Column(Boolean, default=False, nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    
    # 关系
    user = relationship("User", back_populates="tokens")
    
    def __repr__(self):
        return f"<UserToken(id={self.id}, user_id={self.user_id}, type={self.token_type})>"
    
    @property
    def is_valid(self) -> bool:
        """Token是否有效"""
        if self.revoked:
            return False
        if self.expires_at and datetime.now() > self.expires_at:
            return False
        return True


class LoginHistory(Base):
    """登录历史表"""
    
    __tablename__ = "login_history"
    
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    username = Column(String(50), nullable=True)  # 保留用户名，即使用户被删除
    
    # 登录信息
    login_method = Column(String(20), nullable=True)  # password, sms, oauth
    success = Column(Boolean, nullable=False, index=True)
    failure_reason = Column(String(100), nullable=True)
    
    # IP和设备信息
    ip_address = Column(String(45), nullable=True, index=True)
    user_agent = Column(Text, nullable=True)
    device_type = Column(String(20), nullable=True)  # desktop, mobile, tablet
    browser = Column(String(50), nullable=True)
    os = Column(String(50), nullable=True)
    
    # 地理位置（可选）
    country = Column(String(50), nullable=True)
    city = Column(String(100), nullable=True)
    location = Column(String(100), nullable=True)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # 关系
    user = relationship("User", back_populates="login_history")
    
    def __repr__(self):
        status = "成功" if self.success else "失败"
        return f"<LoginHistory(id={self.id}, username={self.username}, status={status})>"


class VerificationCode(Base):
    """验证码表"""
    
    __tablename__ = "verification_codes"
    
    id = Column(BigInteger, primary_key=True, index=True)
    
    # 验证码信息
    code_type = Column(String(20), nullable=False, index=True)  # register, login, reset_password等
    recipient = Column(String(100), nullable=False, index=True)  # 邮箱或手机号
    code = Column(String(10), nullable=False)
    
    # 关联信息（可选）
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    
    # 状态
    used = Column(Boolean, default=False, nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)
    
    # 过期时间
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # 验证尝试次数
    attempts = Column(Integer, default=0, nullable=False)
    max_attempts = Column(Integer, default=5, nullable=False)
    
    # IP信息（用于安全）
    ip_address = Column(String(45), nullable=True)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # 关系
    user = relationship("User", back_populates="verification_codes")
    
    def __repr__(self):
        return f"<VerificationCode(id={self.id}, type={self.code_type}, recipient={self.recipient})>"
    
    @property
    def is_valid(self) -> bool:
        """验证码是否有效"""
        if self.used:
            return False
        if datetime.now() > self.expires_at:
            return False
        if self.attempts >= self.max_attempts:
            return False
        return True
    
    def increment_attempts(self):
        """增加验证尝试次数"""
        self.attempts += 1
    
    def mark_as_used(self):
        """标记为已使用"""
        self.used = True
        self.used_at = datetime.now()


class UserProfile(Base):
    """用户资料表"""
    
    __tablename__ = "user_profiles"
    
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    
    # 个人信息
    real_name = Column(String(50), nullable=True)
    gender = Column(String(10), nullable=True)  # male, female, other
    birthday = Column(DateTime(timezone=True), nullable=True)
    
    # 教育信息
    school = Column(String(100), nullable=True)
    major = Column(String(100), nullable=True)
    grade = Column(String(20), nullable=True)
    student_id = Column(String(50), nullable=True)
    
    # 联系方式
    wechat = Column(String(50), nullable=True)
    qq = Column(String(20), nullable=True)
    
    # 个人简介
    bio = Column(Text, nullable=True)
    signature = Column(String(200), nullable=True)
    
    # 地址信息
    country = Column(String(50), nullable=True)
    province = Column(String(50), nullable=True)
    city = Column(String(50), nullable=True)
    address = Column(String(200), nullable=True)
    
    # 个性化设置（JSON）
    preferences = Column(JSON, nullable=True)  # {"theme": "dark", "language": "zh-CN", ...}
    
    # 隐私设置（JSON）
    privacy_settings = Column(JSON, nullable=True)  # {"show_email": false, ...}
    
    # 社交链接（JSON）
    social_links = Column(JSON, nullable=True)  # {"github": "...", "blog": "...", ...}
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # 关系
    user = relationship("User", back_populates="profile", uselist=False)
    
    def __repr__(self):
        return f"<UserProfile(id={self.id}, user_id={self.user_id}, real_name={self.real_name})>"
