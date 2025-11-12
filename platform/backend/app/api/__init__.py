"""
API路由注册
"""

from fastapi import APIRouter
from app.api.endpoints import (
    sessions,
    execution,
    code,
    ai_assistant,
    textbooks
)
from app.api.v1.endpoints import auth as auth_v1, oauth as oauth_v1, twofa as twofa_v1, learning as learning_v1, questions as questions_v1
from app.api.v2 import books as books_v2

api_router = APIRouter()

# V1 API端点
api_router.include_router(auth_v1.router, prefix="/v1/auth", tags=["认证"])
api_router.include_router(oauth_v1.router, prefix="/v1/oauth", tags=["OAuth"])
api_router.include_router(twofa_v1.router, prefix="/v1/2fa", tags=["双因素认证"])
api_router.include_router(learning_v1.router, prefix="/v1/learning", tags=["学习追踪"])
api_router.include_router(questions_v1.router, prefix="/v1/questions", tags=["题目练习"])

# 其他端点
api_router.include_router(sessions.router, prefix="/sessions", tags=["会话管理"])
api_router.include_router(execution.router, prefix="/execution", tags=["代码执行"])
api_router.include_router(code.router, prefix="/code", tags=["代码管理"])
api_router.include_router(ai_assistant.router, prefix="/ai", tags=["AI助手"])
api_router.include_router(books_v2.router, prefix="/books", tags=["书籍管理"])
api_router.include_router(textbooks.router, prefix="/textbooks", tags=["教材内容"])
