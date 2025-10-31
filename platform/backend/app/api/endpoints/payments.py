"""支付相关API"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.core.security import get_current_user
from loguru import logger

router = APIRouter()

class CreateOrderRequest(BaseModel):
    product_type: str  # book | subscription
    product_id: int
    payment_method: str

@router.post("/create-order")
async def create_order(request: CreateOrderRequest, current_user: dict = Depends(get_current_user)):
    """创建订单"""
    logger.info(f"💳 创建订单: user_id={current_user['id']}, product={request.product_type}")
    return {"order_no": "ORDER_123456", "amount": 299.0, "qr_code": "https://..."}
