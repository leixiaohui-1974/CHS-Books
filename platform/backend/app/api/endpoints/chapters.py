"""章节相关API""" 

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from loguru import logger

router = APIRouter()

@router.get("/{chapter_id}")
async def get_chapter(chapter_id: int, db: AsyncSession = Depends(get_db)):
    """获取章节详情"""
    logger.info(f"📖 获取章节: chapter_id={chapter_id}")
    return {"chapter_id": chapter_id, "title": "第1章", "content": "章节内容..."}
