"""
数据模型包
"""

from .user import User, UserRole, UserStatus
from .auth import (
    OAuthAccount, OAuthProvider,
    TwoFactorAuth, TwoFactorMethod,
    UserToken, TokenType,
    LoginHistory,
    VerificationCode, VerificationType,
    UserProfile
)
from .learning import (
    Subject, Chapter as LearningChapter, KnowledgePoint,
    UserKnowledgeProgress, LearningActivity, StudySession,
    LearningPath, DailyGoal,
    Achievement, UserAchievement, LearningStats,
    DifficultyLevel as LearningDifficultyLevel, MasteryLevel, ActivityType, AchievementType
)
from .exercise import (
    Question, QuestionSet, Exercise, Submission, WrongQuestion,
    LearningResource, ResourceView,
    QuestionType, QuestionDifficulty, ExerciseStatus, SubmissionStatus
)
from .book import Book, Chapter, Case, BookStatus, DifficultyLevel
from .progress import UserProgress, ChapterProgress, CaseProgress, ProgressStatus
from .payment import Order, OrderStatus, PaymentMethod, Subscription, SubscriptionStatus
from .tool import ToolExecution, ToolExecutionStatus
from .coupon import Coupon, UserCoupon, CouponType, CouponStatus
from .knowledge import KnowledgeBase, Document, DocumentChunk, KnowledgeBaseStatus, DocumentType
from .membership import UserMembership, ExperienceHistory, MembershipConfig, MembershipLevel, BenefitType
from .points import PointsAccount, PointsTransaction, PointsProduct, PointsRedemption, PointsRule, TransactionType, PointsReason, ProductType

__all__ = [
    # 用户相关
    "User",
    "UserRole",
    "UserStatus",
    "UserProfile",
    # 认证相关
    "OAuthAccount",
    "OAuthProvider",
    "TwoFactorAuth",
    "TwoFactorMethod",
    "UserToken",
    "TokenType",
    "LoginHistory",
    "VerificationCode",
    "VerificationType",
    # 书籍相关
    "Book",
    "Chapter",
    "Case",
    "BookStatus",
    "DifficultyLevel",
    # 进度相关
    "UserProgress",
    "ChapterProgress",
    "CaseProgress",
    "ProgressStatus",
    # 支付相关
    "Order",
    "OrderStatus",
    "PaymentMethod",
    "Subscription",
    "SubscriptionStatus",
    # 工具相关
    "ToolExecution",
    "ToolExecutionStatus",
    # 优惠券相关
    "Coupon",
    "UserCoupon",
    "CouponType",
    "CouponStatus",
    # 知识库相关
    "KnowledgeBase",
    "Document",
    "DocumentChunk",
    "KnowledgeBaseStatus",
    "DocumentType",
    # 会员相关
    "UserMembership",
    "ExperienceHistory",
    "MembershipConfig",
    "MembershipLevel",
    "BenefitType",
    # 积分相关
    "PointsAccount",
    "PointsTransaction",
    "PointsProduct",
    "PointsRedemption",
    "PointsRule",
    "TransactionType",
    "PointsReason",
    "ProductType",
]
