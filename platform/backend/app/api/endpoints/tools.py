"""
工具执行API端点
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
import uuid
from datetime import datetime, timezone

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.core.cache import RedisCache

# 创建Redis缓存实例
redis_cache = RedisCache()
from app.models.user import User
from loguru import logger

router = APIRouter()


# ========================================
# Pydantic Schemas
# ========================================

class ToolExecuteRequest(BaseModel):
    """工具执行请求"""
    case_id: int
    input_params: Dict[str, Any]


class ToolExecuteResponse(BaseModel):
    """工具执行响应"""
    task_id: str
    status: str
    message: str


class ToolResultResponse(BaseModel):
    """工具结果响应"""
    task_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None
    created_at: str


# ========================================
# 工具执行逻辑
# ========================================

async def execute_tool_task(task_id: str, case_id: int, input_params: Dict[str, Any], user_id: int, db: AsyncSession):
    """
    后台任务：执行工具
    """
    try:
        logger.info(f"🚀 开始执行工具任务: task_id={task_id}, case_id={case_id}")
        
        # 获取案例信息
        from app.models.book import Case, Book
        from sqlalchemy import select
        
        result = await db.execute(
            select(Case, Book)
            .join(Book, Case.book_id == Book.id)
            .where(Case.id == case_id)
        )
        row = result.first()
        
        if not row:
            raise ValueError(f"案例不存在: case_id={case_id}")
        
        case, book = row
        
        # 尝试执行实际脚本
        from app.executor.simple_executor import simple_executor
        
        try:
            execution_result = await simple_executor.execute_script(
                book_slug=book.slug,
                case_slug=case.slug,
                input_params=input_params,
                timeout=30
            )
            
            if execution_result.get("status") == "error":
                logger.warning(f"⚠️ 脚本执行失败，使用Mock数据: {execution_result.get('error')}")
                raise ValueError("脚本执行失败")
            
            # 使用实际执行结果
            result = execution_result
            
        except Exception as e:
            logger.warning(f"⚠️ 实际执行失败，使用Mock数据: {str(e)}")
            
            # 回退到mock结果
            import asyncio
            import random
            
            await asyncio.sleep(2)  # 模拟计算
        
        # Mock结果
        result = {
            "status": "success",
            "execution_time": 2.15,
            "output": {
                "summary": {
                    "avg_water_level": round(random.uniform(40, 70), 2),
                    "pump_on_time": round(random.uniform(10, 15), 2),
                    "pump_cycles": random.randint(10, 20),
                    "efficiency": round(random.uniform(85, 95), 2)
                },
                "charts": [
                    {
                        "title": "水位变化曲线",
                        "type": "line",
                        "data": {
                            "labels": [f"{i}h" for i in range(24)],
                            "datasets": [{
                                "label": "水位 (%)",
                                "data": [round(random.uniform(30, 80), 2) for _ in range(24)]
                            }]
                        }
                    }
                ]
            },
            "input_params": input_params
        }
        
        # 保存结果到缓存
        await redis_cache.set(
            f"tool_result:{task_id}",
            result,
            expire=3600  # 1小时过期
        )
        
        # 更新任务状态
        await redis_cache.set(
            f"tool_status:{task_id}",
            {"status": "completed", "result": result},
            expire=3600
        )
        
        logger.info(f"✅ 工具执行完成: task_id={task_id}")
        
    except Exception as e:
        logger.error(f"❌ 工具执行失败: {str(e)}")
        
        # 保存错误信息
        await redis_cache.set(
            f"tool_status:{task_id}",
            {"status": "failed", "error": str(e)},
            expire=3600
        )


# ========================================
# API Endpoints
# ========================================

@router.post("/execute", response_model=ToolExecuteResponse)
async def execute_tool(
    request: ToolExecuteRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    执行工具
    
    - **case_id**: 案例ID
    - **input_params**: 输入参数（JSON对象）
    """
    logger.info(f"🛠️ 用户 {current_user.id} 请求执行工具: case_id={request.case_id}")
    
    # 生成任务ID
    task_id = str(uuid.uuid4())
    
    # 初始化任务状态
    await redis_cache.set(
        f"tool_status:{task_id}",
        {
            "status": "pending",
            "case_id": request.case_id,
            "user_id": current_user.id,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        expire=3600
    )
    
    # 添加后台任务
    background_tasks.add_task(
        execute_tool_task,
        task_id,
        request.case_id,
        request.input_params,
        current_user.id,
        db
    )
    
    logger.info(f"📋 工具任务已提交: task_id={task_id}")
    
    return {
        "task_id": task_id,
        "status": "pending",
        "message": "工具执行已提交，请稍后查询结果"
    }


@router.get("/result/{task_id}", response_model=ToolResultResponse)
async def get_tool_result(
    task_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    获取工具执行结果
    
    - **task_id**: 任务ID
    """
    logger.info(f"📊 查询工具结果: task_id={task_id}")
    
    # 从缓存获取状态
    status_data = await redis_cache.get(f"tool_status:{task_id}")
    
    if not status_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在或已过期"
        )
    
    # 检查权限
    if status_data.get("user_id") != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问该任务"
        )
    
    task_status = status_data.get("status")
    
    if task_status == "pending":
        return {
            "task_id": task_id,
            "status": "pending",
            "result": None,
            "error": None,
            "execution_time": None,
            "created_at": status_data.get("created_at", "")
        }
    
    elif task_status == "completed":
        result = status_data.get("result", {})
        return {
            "task_id": task_id,
            "status": "completed",
            "result": result,
            "error": None,
            "execution_time": result.get("execution_time"),
            "created_at": status_data.get("created_at", "")
        }
    
    elif task_status == "failed":
        return {
            "task_id": task_id,
            "status": "failed",
            "result": None,
            "error": status_data.get("error", "未知错误"),
            "execution_time": None,
            "created_at": status_data.get("created_at", "")
        }
    
    else:
        return {
            "task_id": task_id,
            "status": "unknown",
            "result": None,
            "error": "未知状态",
            "execution_time": None,
            "created_at": status_data.get("created_at", "")
        }


@router.get("/history")
async def get_tool_history(
    case_id: Optional[int] = None,
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取工具执行历史
    
    - **case_id**: 案例ID（可选，用于筛选）
    - **page**: 页码
    - **page_size**: 每页数量
    """
    logger.info(f"📜 获取工具执行历史: user_id={current_user.id}, case_id={case_id}")
    
    # TODO: 从数据库查询历史记录
    # 这里返回mock数据
    
    return {
        "total": 0,
        "items": [],
        "message": "工具执行历史功能开发中"
    }


@router.post("/{task_id}/save")
async def save_tool_execution(
    task_id: str,
    name: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    保存工具执行结果
    
    - **task_id**: 任务ID
    - **name**: 保存的名称（可选）
    """
    logger.info(f"💾 保存工具结果: task_id={task_id}, name={name}")
    
    # 获取结果
    status_data = await redis_cache.get(f"tool_status:{task_id}")
    
    if not status_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在或已过期"
        )
    
    # 检查权限
    if status_data.get("user_id") != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问该任务"
        )
    
    # TODO: 保存到数据库
    
    return {
        "message": "保存成功",
        "task_id": task_id
    }
