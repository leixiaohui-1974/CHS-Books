"""AI助手相关API"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.core.security import get_current_user
from loguru import logger

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    context: dict = {}

@router.post("/chat")
async def chat(request: ChatRequest, current_user: dict = Depends(get_current_user)):
    """AI对话"""
    logger.info(f"🤖 AI对话: user_id={current_user['id']}, message={request.message[:50]}")
    return {"reply": "这是AI的回复（功能开发中）", "sources": []}
