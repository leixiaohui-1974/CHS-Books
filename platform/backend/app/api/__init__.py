"""
API路由注册
"""

from fastapi import APIRouter
from app.api.endpoints import (
    sessions,
    execution,
    code,
    ai_assistant
)

api_router = APIRouter()

# 注册所有端点
api_router.include_router(sessions.router, prefix="/sessions", tags=["会话管理"])
api_router.include_router(execution.router, prefix="/execution", tags=["代码执行"])
api_router.include_router(code.router, prefix="/code", tags=["代码管理"])
api_router.include_router(ai_assistant.router, prefix="/ai", tags=["AI助手"])
