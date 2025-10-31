"""案例相关API"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from loguru import logger

router = APIRouter()

@router.get("/{case_id}")
async def get_case(case_id: int, db: AsyncSession = Depends(get_db)):
    """获取案例详情"""
    logger.info(f"📋 获取案例: case_id={case_id}")
    return {"case_id": case_id, "title": "案例1", "description": "案例描述..."}
