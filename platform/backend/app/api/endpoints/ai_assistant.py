"""
AI助手API端点
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.services.ai_service import ai_service


router = APIRouter()


# ========================================
# Pydantic模型
# ========================================

class ChatRequest(BaseModel):
    """聊天请求"""
    message: str = Field(..., min_length=1, max_length=2000, description="用户消息")
    context: Optional[Dict[str, Any]] = Field(None, description="上下文信息")


class ChatResponse(BaseModel):
    """聊天响应"""
    success: bool
    message: str
    model: Optional[str] = None
    timestamp: Optional[str] = None
    error: Optional[str] = None


class ConceptRequest(BaseModel):
    """概念解释请求"""
    concept: str = Field(..., min_length=1, max_length=100, description="概念名称")
    context: Optional[Dict[str, Any]] = Field(None, description="上下文")


class RecommendationResponse(BaseModel):
    """推荐响应"""
    case_id: int
    title: str
    difficulty: str
    estimated_minutes: int
    reason: str


# ========================================
# API端点
# ========================================

@router.post("/chat", response_model=ChatResponse, tags=["AI助手"])
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    AI聊天
    
    与AI助手进行对话，获取学习帮助和建议。
    
    支持的功能：
    - 回答技术问题
    - 解释概念
    - 学习建议
    - 案例推荐
    """
    result = await ai_service.chat(
        message=request.message,
        user_id=current_user.id,
        context=request.context,
        db=db
    )
    
    return ChatResponse(**result)


@router.post("/explain", tags=["AI助手"])
async def explain(
    request: ConceptRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    解释概念
    
    获取工程概念的详细解释，包括定义、原理、应用等。
    """
    result = await ai_service.explain_concept(
        concept=request.concept,
        context=request.context
    )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error", "概念解释失败")
        )
    
    return result


@router.get("/recommend", response_model=list[RecommendationResponse], tags=["AI助手"])
async def recommend(
    limit: int = 5,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    推荐案例
    
    基于用户学习历史，智能推荐相关案例。
    """
    recommendations = await ai_service.recommend_cases(
        db=db,
        user_id=current_user.id,
        limit=limit
    )
    
    return [RecommendationResponse(**rec) for rec in recommendations]


@router.get("/learning-path", tags=["AI助手"])
async def get_learning_path(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取学习路径分析
    
    AI分析您的学习进度，提供个性化学习建议。
    """
    result = await ai_service.analyze_learning_path(
        db=db,
        user_id=current_user.id
    )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error", "学习路径分析失败")
        )
    
    return result


@router.get("/help", tags=["AI助手"])
async def get_help():
    """
    获取AI助手使用帮助
    
    返回AI助手的功能说明和使用示例。
    """
    return {
        "name": "工程学习AI助手",
        "version": "1.0.0",
        "capabilities": [
            "回答技术问题",
            "解释工程概念",
            "推荐学习案例",
            "分析学习路径",
            "提供学习建议"
        ],
        "usage_tips": [
            "尽量提供具体的问题描述",
            "可以提供当前学习的章节或案例作为上下文",
            "善用'解释概念'功能快速理解术语",
            "定期查看学习路径分析获取建议"
        ],
        "examples": [
            {
                "question": "什么是明渠均匀流？",
                "endpoint": "/api/v1/ai/explain",
                "method": "POST"
            },
            {
                "question": "我应该学习哪些案例？",
                "endpoint": "/api/v1/ai/recommend",
                "method": "GET"
            },
            {
                "question": "如何提高学习效率？",
                "endpoint": "/api/v1/ai/chat",
                "method": "POST"
            }
        ]
    }
