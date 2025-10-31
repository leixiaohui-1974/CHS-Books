"""学习进度相关API"""

from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from loguru import logger

router = APIRouter()

@router.get("/books/{book_id}")
async def get_book_progress(book_id: int, current_user: dict = Depends(get_current_user)):
    """获取书籍学习进度"""
    logger.info(f"📊 获取学习进度: user_id={current_user['id']}, book_id={book_id}")
    return {"book_id": book_id, "percentage": 35.5, "chapters_completed": 2}
