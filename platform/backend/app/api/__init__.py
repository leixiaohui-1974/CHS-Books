"""
API路由主入口
"""

from fastapi import APIRouter
from .endpoints import (
    auth,
    users,
    books,
    chapters,
    cases,
    tools,
    ai_assistant,
    payments,
    progress,
    admin,
)

# 创建主路由
api_router = APIRouter()

# 注册各模块路由
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["认证"]
)

api_router.include_router(
    users.router,
    prefix="/users",
    tags=["用户"]
)

api_router.include_router(
    books.router,
    prefix="/books",
    tags=["书籍"]
)

api_router.include_router(
    chapters.router,
    prefix="/chapters",
    tags=["章节"]
)

api_router.include_router(
    cases.router,
    prefix="/cases",
    tags=["案例"]
)

api_router.include_router(
    tools.router,
    prefix="/tools",
    tags=["工具"]
)

api_router.include_router(
    ai_assistant.router,
    prefix="/ai",
    tags=["AI助手"]
)

api_router.include_router(
    payments.router,
    prefix="/payments",
    tags=["支付"]
)

api_router.include_router(
    progress.router,
    prefix="/progress",
    tags=["学习进度"]
)

api_router.include_router(
    admin.router,
    prefix="/admin",
    tags=["管理员"]
)
