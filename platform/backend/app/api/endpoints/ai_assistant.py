"""
AI助手API端点
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.ai_assistant_enhanced import ai_assistant_service
from loguru import logger

router = APIRouter()


# ============================================
# Schemas
# ============================================

class CodeExplainRequest(BaseModel):
    """代码讲解请求"""
    code: str = Field(..., description="代码片段")
    context: Optional[str] = Field(None, description="上下文信息")


class ErrorDiagnoseRequest(BaseModel):
    """错误诊断请求"""
    code: str = Field(..., description="出错的代码")
    error_message: str = Field(..., description="错误信息")
    stack_trace: Optional[str] = Field(None, description="堆栈跟踪")


class QuestionRequest(BaseModel):
    """问答请求"""
    session_id: str = Field(..., description="会话ID")
    question: str = Field(..., description="用户问题")
    context: Optional[Dict] = Field(None, description="上下文")


class InsightsRequest(BaseModel):
    """洞察生成请求"""
    result_data: Dict[str, Any] = Field(..., description="结果数据")


# ============================================
# Endpoints
# ============================================

@router.post("/explain-code")
async def explain_code(
    request: CodeExplainRequest,
    current_user: User = Depends(get_current_user)
):
    """
    AI讲解代码
    """
    try:
        explanation = await ai_assistant_service.explain_code(
            code=request.code,
            context=request.context
        )
        
        return {
            "explanation": explanation,
            "model": "gpt-4-demo"
        }
    
    except Exception as e:
        logger.error(f"❌ 代码讲解失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"代码讲解失败: {str(e)}"
        )


@router.post("/diagnose-error")
async def diagnose_error(
    request: ErrorDiagnoseRequest,
    current_user: User = Depends(get_current_user)
):
    """
    AI诊断错误
    """
    try:
        diagnosis = await ai_assistant_service.diagnose_error(
            code=request.code,
            error_message=request.error_message,
            stack_trace=request.stack_trace
        )
        
        return diagnosis
    
    except Exception as e:
        logger.error(f"❌ 错误诊断失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"错误诊断失败: {str(e)}"
        )


@router.post("/ask")
async def ask_question(
    request: QuestionRequest,
    current_user: User = Depends(get_current_user)
):
    """
    向AI助手提问
    """
    try:
        answer = await ai_assistant_service.answer_question(
            session_id=request.session_id,
            question=request.question,
            context=request.context
        )
        
        return {
            "answer": answer,
            "session_id": request.session_id
        }
    
    except Exception as e:
        logger.error(f"❌ 问答失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"问答失败: {str(e)}"
        )


@router.post("/generate-insights")
async def generate_insights(
    request: InsightsRequest,
    current_user: User = Depends(get_current_user)
):
    """
    从结果生成AI洞察
    """
    try:
        insights = await ai_assistant_service.generate_insights(
            result_data=request.result_data
        )
        
        return {
            "insights": insights,
            "count": len(insights)
        }
    
    except Exception as e:
        logger.error(f"❌ 生成洞察失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成洞察失败: {str(e)}"
        )


@router.delete("/conversation/{session_id}")
async def clear_conversation(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    清除会话的对话历史
    """
    ai_assistant_service.clear_conversation(session_id)
    
    return {"message": "对话历史已清除"}
