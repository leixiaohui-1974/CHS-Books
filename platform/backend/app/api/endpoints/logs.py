"""
日志查询API端点
"""

from datetime import datetime, timedelta, timezone
from typing import List, Optional
from pathlib import Path
from fastapi import APIRouter, Depends, Query, HTTPException, status
from pydantic import BaseModel

from app.core.security import get_current_active_user
from app.models.user import User


router = APIRouter()


class LogEntry(BaseModel):
    """日志条目"""
    timestamp: str
    level: str
    message: str
    module: Optional[str] = None
    function: Optional[str] = None
    line: Optional[int] = None


class LogQueryResponse(BaseModel):
    """日志查询响应"""
    total: int
    logs: List[LogEntry]
    log_file: str


@router.get("/recent", response_model=LogQueryResponse, tags=["日志"])
async def get_recent_logs(
    level: str = Query("INFO", regex="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$", description="日志级别"),
    limit: int = Query(100, ge=1, le=1000, description="返回条数"),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取最近的日志
    
    返回指定级别的最近日志条目。
    
    **注意**: 此功能需要管理员权限。
    """
    # TODO: 添加管理员权限检查
    # if not current_user.is_admin:
    #     raise HTTPException(status_code=403, detail="需要管理员权限")
    
    # 获取今天的日志文件
    log_dir = Path("logs")
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = log_dir / f"app_{today}.log"
    
    if not log_file.exists():
        return LogQueryResponse(
            total=0,
            logs=[],
            log_file=str(log_file)
        )
    
    # 读取日志文件
    logs = []
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
            # 从后往前读取，获取最新的日志
            for line in reversed(lines[-limit*2:]):  # 多读一些以过滤级别
                if level in line:
                    try:
                        # 简单解析日志行
                        parts = line.split('|')
                        if len(parts) >= 4:
                            logs.append(LogEntry(
                                timestamp=parts[0].strip(),
                                level=parts[1].strip(),
                                message=parts[3].strip() if len(parts) > 3 else "",
                                module=parts[2].strip().split(':')[0] if len(parts) > 2 else None
                            ))
                    except Exception:
                        continue
                
                if len(logs) >= limit:
                    break
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"读取日志文件失败: {str(e)}"
        )
    
    return LogQueryResponse(
        total=len(logs),
        logs=list(reversed(logs)),  # 返回时按时间正序
        log_file=str(log_file)
    )


@router.get("/errors", response_model=LogQueryResponse, tags=["日志"])
async def get_error_logs(
    limit: int = Query(50, ge=1, le=500, description="返回条数"),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取错误日志
    
    返回最近的错误级别日志。
    
    **注意**: 此功能需要管理员权限。
    """
    # TODO: 添加管理员权限检查
    
    # 获取今天的错误日志文件
    log_dir = Path("logs")
    today = datetime.now().strftime("%Y-%m-%d")
    error_log_file = log_dir / f"error_{today}.log"
    
    if not error_log_file.exists():
        return LogQueryResponse(
            total=0,
            logs=[],
            log_file=str(error_log_file)
        )
    
    # 读取错误日志
    logs = []
    try:
        with open(error_log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
            for line in reversed(lines[-limit*2:]):
                try:
                    parts = line.split('|')
                    if len(parts) >= 4:
                        logs.append(LogEntry(
                            timestamp=parts[0].strip(),
                            level=parts[1].strip(),
                            message=parts[3].strip() if len(parts) > 3 else line.strip(),
                            module=parts[2].strip().split(':')[0] if len(parts) > 2 else None
                        ))
                except Exception:
                    continue
                
                if len(logs) >= limit:
                    break
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"读取错误日志失败: {str(e)}"
        )
    
    return LogQueryResponse(
        total=len(logs),
        logs=list(reversed(logs)),
        log_file=str(error_log_file)
    )


@router.get("/stats", tags=["日志"])
async def get_log_stats(
    current_user: User = Depends(get_current_active_user)
):
    """
    获取日志统计
    
    返回今日各级别日志数量统计。
    
    **注意**: 此功能需要管理员权限。
    """
    # TODO: 添加管理员权限检查
    
    log_dir = Path("logs")
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = log_dir / f"app_{today}.log"
    
    stats = {
        "DEBUG": 0,
        "INFO": 0,
        "WARNING": 0,
        "ERROR": 0,
        "CRITICAL": 0
    }
    
    if log_file.exists():
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    for level in stats.keys():
                        if f"| {level} " in line:
                            stats[level] += 1
                            break
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"统计日志失败: {str(e)}"
            )
    
    return {
        "date": today,
        "log_file": str(log_file),
        "file_exists": log_file.exists(),
        "stats": stats,
        "total": sum(stats.values())
    }
