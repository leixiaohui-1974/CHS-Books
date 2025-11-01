"""
API路由入口
"""

from fastapi import APIRouter

# 导入所有端点路由
from app.api.endpoints import (
    auth,
    books,
    chapters,
    cases,
    tools,
    users,
    ai_assistant,
    payments,
    analytics,
    admin,
    order_stats,
    logs
)

# 单独导入progress以避免命名冲突
from app.api.endpoints import progress as progress_endpoints

# 创建主路由
api_router = APIRouter()

# 注册各个模块的路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(books.router, prefix="/books", tags=["书籍"])
api_router.include_router(chapters.router, prefix="/chapters", tags=["章节"])
api_router.include_router(cases.router, prefix="/cases", tags=["案例"])
api_router.include_router(tools.router, prefix="/tools", tags=["工具"])
api_router.include_router(users.router, prefix="/users", tags=["用户"])
api_router.include_router(ai_assistant.router, prefix="/ai", tags=["AI助手"])
api_router.include_router(payments.router, prefix="/payments", tags=["支付"])
api_router.include_router(order_stats.router, prefix="/orders", tags=["订单统计"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["分析"])
api_router.include_router(logs.router, prefix="/logs", tags=["日志"])
api_router.include_router(progress_endpoints.router, prefix="/progress", tags=["学习进度"])
api_router.include_router(admin.router, prefix="/admin", tags=["管理"])


# 健康检查端点
@api_router.get("/health", tags=["系统"])
async def health_check():
    """健康检查"""
    return {"status": "ok", "message": "API is running"}
