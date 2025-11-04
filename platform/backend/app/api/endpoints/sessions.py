"""
会话管理API端点
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.session import SessionStatus
from app.services.session_service import SessionService, ExecutionService

router = APIRouter()


# ============================================
# Schemas
# ============================================

class SessionCreateRequest(BaseModel):
    """创建会话请求"""
    book_slug: str = Field(..., description="书籍slug")
    chapter_slug: Optional[str] = Field(None, description="章节slug")
    case_slug: str = Field(..., description="案例slug")


class SessionResponse(BaseModel):
    """会话响应"""
    session_id: str
    user_id: int
    book_slug: str
    chapter_slug: Optional[str]
    case_slug: str
    status: str
    execution_count: int
    last_execution_id: Optional[str]
    conversation_count: int
    created_at: str
    last_active_at: str
    expires_at: str
    is_expired: bool
    is_active: bool
    resource_quota: dict
    statistics: dict


class SessionListResponse(BaseModel):
    """会话列表响应"""
    total: int
    sessions: List[SessionResponse]


class ExecutionResponse(BaseModel):
    """执行记录响应"""
    execution_id: str
    session_id: str
    user_id: int
    status: str
    script_path: str
    input_params: dict
    output_data: Optional[dict]
    console_output: Optional[str]
    error_message: Optional[str]
    execution_time: int
    resource_usage: dict
    result_files: list
    created_at: Optional[str]
    started_at: Optional[str]
    completed_at: Optional[str]


# ============================================
# Endpoints
# ============================================

@router.post("/create", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    request: SessionCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    创建新的学习会话
    
    用户开始学习一个案例时，创建会话来跟踪整个学习过程
    """
    try:
        session = await SessionService.create_session(
            db=db,
            user_id=current_user.id,
            book_slug=request.book_slug,
            case_slug=request.case_slug,
            chapter_slug=request.chapter_slug
        )
        
        return session.to_dict()
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建会话失败: {str(e)}"
        )


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取会话详情
    """
    session = await SessionService.get_session(
        db=db,
        session_id=session_id,
        user_id=current_user.id
    )
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在"
        )
    
    return session.to_dict()


@router.get("/", response_model=SessionListResponse)
async def list_sessions(
    status_filter: Optional[str] = None,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取当前用户的所有会话
    """
    # 验证状态参数
    session_status = None
    if status_filter:
        try:
            session_status = SessionStatus(status_filter)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的状态: {status_filter}"
            )
    
    sessions = await SessionService.list_user_sessions(
        db=db,
        user_id=current_user.id,
        status=session_status,
        limit=limit
    )
    
    return {
        "total": len(sessions),
        "sessions": [s.to_dict() for s in sessions]
    }


@router.put("/{session_id}/pause")
async def pause_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    暂停会话
    """
    session = await SessionService.get_session(db, session_id, current_user.id)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在"
        )
    
    updated_session = await SessionService.update_session_status(
        db=db,
        session_id=session_id,
        status=SessionStatus.PAUSED
    )
    
    return {"message": "会话已暂停", "session": updated_session.to_dict()}


@router.put("/{session_id}/resume")
async def resume_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    恢复会话
    """
    session = await SessionService.get_session(db, session_id, current_user.id)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在"
        )
    
    updated_session = await SessionService.update_session_status(
        db=db,
        session_id=session_id,
        status=SessionStatus.ACTIVE
    )
    
    return {"message": "会话已恢复", "session": updated_session.to_dict()}


@router.put("/{session_id}/extend")
async def extend_session(
    session_id: str,
    hours: int = 24,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    延长会话有效期
    """
    session = await SessionService.get_session(db, session_id, current_user.id)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在"
        )
    
    updated_session = await SessionService.extend_session(
        db=db,
        session_id=session_id,
        hours=hours
    )
    
    return {"message": f"会话已延长{hours}小时", "session": updated_session.to_dict()}


@router.delete("/{session_id}")
async def terminate_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    终止会话
    """
    session = await SessionService.get_session(db, session_id, current_user.id)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在"
        )
    
    success = await SessionService.terminate_session(db, session_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="终止会话失败"
        )
    
    return {"message": "会话已终止"}


@router.get("/{session_id}/executions", response_model=List[ExecutionResponse])
async def list_session_executions(
    session_id: str,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取会话的所有执行记录
    """
    # 验证会话权限
    session = await SessionService.get_session(db, session_id, current_user.id)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在"
        )
    
    executions = await ExecutionService.list_session_executions(
        db=db,
        session_id=session_id,
        limit=limit
    )
    
    return [e.to_dict() for e in executions]
