"""
代码管理API端点
"""

from typing import Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.services.session_service import SessionService
from app.services.code_intelligence import code_intelligence_service
from loguru import logger

router = APIRouter()


# ============================================
# Schemas
# ============================================

class CodeLoadRequest(BaseModel):
    """代码加载请求"""
    session_id: str = Field(..., description="会话ID")
    case_path: str = Field(..., description="案例路径")


class CodeEditRequest(BaseModel):
    """代码编辑请求"""
    session_id: str = Field(..., description="会话ID")
    file_path: str = Field(..., description="文件路径")
    content: str = Field(..., description="文件内容")


class CodeValidateRequest(BaseModel):
    """代码验证请求"""
    code: str = Field(..., description="代码内容")


# ============================================
# Endpoints
# ============================================

@router.post("/load")
async def load_code(
    request: CodeLoadRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    加载案例代码到会话
    """
    # 验证会话
    session = await SessionService.get_session(
        db=db,
        session_id=request.session_id,
        user_id=current_user.id
    )
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在"
        )
    
    try:
        # 加载代码
        result = await code_intelligence_service.load_case(request.case_path)
        
        # 更新会话的original_files
        session.original_files = result["files"]
        await db.commit()
        
        return {
            "message": "代码加载成功",
            "file_count": len(result["files"]),
            "file_tree": result["file_tree"],
            "dependencies": result["dependencies"]
        }
    
    except Exception as e:
        logger.error(f"❌ 加载代码失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"加载代码失败: {str(e)}"
        )


@router.get("/{session_id}/files")
async def list_files(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取会话的所有文件
    """
    session = await SessionService.get_session(db, session_id, current_user.id)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在"
        )
    
    # 合并原始文件和修改的文件
    files = dict(session.original_files or {})
    
    if session.modified_files:
        for file_path, file_info in session.modified_files.items():
            files[file_path] = file_info.get("content", "")
    
    return {
        "files": files,
        "original_count": len(session.original_files or {}),
        "modified_count": len(session.modified_files or {})
    }


@router.get("/{session_id}/file/{file_path:path}")
async def get_file(
    session_id: str,
    file_path: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取单个文件内容
    """
    session = await SessionService.get_session(db, session_id, current_user.id)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在"
        )
    
    # 优先返回修改版本
    if session.modified_files and file_path in session.modified_files:
        return {
            "content": session.modified_files[file_path].get("content", ""),
            "is_modified": True,
            "modified_at": session.modified_files[file_path].get("modified_at")
        }
    
    # 返回原始版本
    if session.original_files and file_path in session.original_files:
        return {
            "content": session.original_files[file_path],
            "is_modified": False
        }
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="文件不存在"
    )


@router.put("/{session_id}/edit")
async def edit_file(
    session_id: str,
    request: CodeEditRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    编辑文件
    """
    if request.session_id != session_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="会话ID不匹配"
        )
    
    # 验证代码语法
    is_valid, error_msg = await code_intelligence_service.validate_code(request.content)
    
    if not is_valid:
        return {
            "success": False,
            "error": error_msg
        }
    
    # 更新会话
    session = await SessionService.update_modified_files(
        db=db,
        session_id=session_id,
        file_path=request.file_path,
        content=request.content
    )
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在"
        )
    
    return {
        "success": True,
        "message": "文件已更新"
    }


@router.get("/{session_id}/diff/{file_path:path}")
async def get_file_diff(
    session_id: str,
    file_path: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取文件的修改差异
    """
    session = await SessionService.get_session(db, session_id, current_user.id)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在"
        )
    
    # 获取原始和修改版本
    original = session.original_files.get(file_path, "") if session.original_files else ""
    modified = ""
    
    if session.modified_files and file_path in session.modified_files:
        modified = session.modified_files[file_path].get("content", "")
    else:
        return {
            "has_changes": False,
            "message": "文件未修改"
        }
    
    # 计算差异
    diff = await code_intelligence_service.get_diff(
        original=original,
        modified=modified,
        filename=file_path
    )
    
    return diff


@router.post("/validate")
async def validate_code(
    request: CodeValidateRequest,
    current_user: User = Depends(get_current_user)
):
    """
    验证代码语法
    """
    is_valid, error_msg = await code_intelligence_service.validate_code(request.code)
    
    return {
        "is_valid": is_valid,
        "error": error_msg
    }


@router.post("/format")
async def format_code(
    request: CodeValidateRequest,
    current_user: User = Depends(get_current_user)
):
    """
    格式化代码
    """
    formatted, success = await code_intelligence_service.format_code(request.code)
    
    return {
        "success": success,
        "formatted_code": formatted,
        "message": "代码已格式化" if success else "格式化失败"
    }
