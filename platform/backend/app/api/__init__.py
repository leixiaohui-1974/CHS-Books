"""
API路由汇总
"""

from fastapi import APIRouter
from .endpoints import (
    auth, books, chapters, cases, users, progress, tools, admin,
    payments, analytics, order_stats, logs, ai_assistant, coupons, knowledge,
    membership, points, health
)

api_router = APIRouter()

# 注册健康检查路由（在根路径，不加prefix）
api_router.include_router(health.router, tags=["系统"])

# 注册认证路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])

# 注册书籍相关路由
api_router.include_router(books.router, prefix="/books", tags=["书籍"])
api_router.include_router(chapters.router, prefix="/chapters", tags=["章节"])
api_router.include_router(cases.router, prefix="/cases", tags=["案例"])

# 注册用户和进度路由
api_router.include_router(users.router, prefix="/users", tags=["用户"])
api_router.include_router(progress.router, prefix="/progress", tags=["学习进度"])

# 注册工具执行路由
api_router.include_router(tools.router, prefix="/tools", tags=["工具执行"])

# 注册管理员路由
api_router.include_router(admin.router, prefix="/admin", tags=["管理"])

# 注册支付路由
api_router.include_router(payments.router, prefix="/payments", tags=["支付"])

# 注册数据分析路由
api_router.include_router(analytics.router, prefix="/analytics", tags=["数据分析"])

# 注册订单统计路由
api_router.include_router(order_stats.router, prefix="/order-stats", tags=["订单统计"])

# 注册日志查询路由
api_router.include_router(logs.router, prefix="/logs", tags=["日志"])

# 注册AI助手路由
api_router.include_router(ai_assistant.router, prefix="/ai", tags=["AI助手"])

# 注册优惠券路由
api_router.include_router(coupons.router, prefix="/coupons", tags=["优惠券"])

# 注册RAG知识库路由
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["RAG知识库"])

# 注册会员体系路由
api_router.include_router(membership.router, prefix="/membership", tags=["会员体系"])

# 注册积分系统路由
api_router.include_router(points.router, prefix="/points", tags=["积分系统"])
