"""管理员相关API"""

from fastapi import APIRouter, Depends
from app.core.security import get_current_admin_user
from loguru import logger

router = APIRouter()

@router.post("/scan-content")
async def scan_content(current_user: dict = Depends(get_current_admin_user)):
    """触发内容扫描（管理员）"""
    logger.info(f"🔍 管理员触发内容扫描: user_id={current_user['id']}")
    return {"message": "扫描任务已启动"}

@router.get("/stats")
async def get_stats(current_user: dict = Depends(get_current_admin_user)):
    """获取平台统计数据"""
    return {"total_users": 1523, "total_books": 3, "total_revenue": 456789.0}
