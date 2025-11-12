"""
代码执行API端点
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
import asyncio

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.session_service import SessionService, ExecutionService
from app.services.execution_engine import enhanced_execution_engine
from loguru import logger

router = APIRouter()


# ============================================
# Schemas
# ============================================

class ExecutionRequest(BaseModel):
    """执行请求"""
    session_id: str = Field(..., description="会话ID")
    script_path: str = Field(..., description="脚本路径")
    input_params: Dict[str, Any] = Field(default={}, description="输入参数")
    modified_files: Optional[Dict[str, str]] = Field(None, description="修改的文件")
    dependencies: Optional[list] = Field(None, description="依赖列表")


class ExecutionStartResponse(BaseModel):
    """执行开始响应"""
    execution_id: str
    status: str
    message: str
    ws_url: str


# ============================================
# WebSocket Connection Manager
# ============================================

class WSConnectionManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, execution_id: str, websocket: WebSocket):
        """连接WebSocket"""
        await websocket.accept()
        self.active_connections[execution_id] = websocket
        logger.info(f"🔌 WebSocket连接: {execution_id}")
    
    def disconnect(self, execution_id: str):
        """断开连接"""
        if execution_id in self.active_connections:
            del self.active_connections[execution_id]
            logger.info(f"🔌 WebSocket断开: {execution_id}")
    
    async def send_message(self, execution_id: str, message: dict):
        """发送消息"""
        if execution_id in self.active_connections:
            try:
                ws = self.active_connections[execution_id]
                await ws.send_json(message)
            except Exception as e:
                logger.error(f"❌ 发送WebSocket消息失败: {e}")
                self.disconnect(execution_id)


ws_manager = WSConnectionManager()


# ============================================
# Endpoints
# ============================================

@router.post("/start", response_model=ExecutionStartResponse)
async def start_execution(
    request: ExecutionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    开始执行代码
    
    返回execution_id和WebSocket URL，客户端通过WebSocket接收实时输出
    """
    # 1. 验证会话
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
    
    if not session.can_execute():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="会话无法执行（可能已过期或达到执行次数上限）"
        )
    
    # 2. 创建执行记录
    execution = await ExecutionService.create_execution(
        db=db,
        session_id=request.session_id,
        user_id=current_user.id,
        script_path=request.script_path,
        input_params=request.input_params
    )
    
    # 3. 异步执行（不等待完成）
    asyncio.create_task(
        _execute_async(
            db=db,
            execution=execution,
            request=request
        )
    )
    
    return ExecutionStartResponse(
        execution_id=execution.execution_id,
        status="pending",
        message="执行已开始，请通过WebSocket接收实时输出",
        ws_url=f"/api/v1/execution/ws/{execution.execution_id}"
    )


async def _execute_async(
    db: AsyncSession,
    execution,
    request: ExecutionRequest
):
    """异步执行任务"""
    try:
        # 更新状态为运行中
        await ExecutionService.update_execution_status(
            db=db,
            execution_id=execution.execution_id,
            status="running"
        )
        
        # 执行代码
        result = await enhanced_execution_engine.execute_script(
            execution_id=execution.execution_id,
            script_path=request.script_path,
            input_params=request.input_params,
            code_files=request.modified_files,
            dependencies=request.dependencies
        )
        
        # 更新执行结果
        await ExecutionService.update_execution_status(
            db=db,
            execution_id=execution.execution_id,
            status=result["status"],
            output_data=result.get("output_data"),
            console_output=result.get("console_output"),
            error_message=result.get("error_message"),
            execution_time=int(result.get("execution_time", 0)),
            result_files=result.get("result_files", [])
        )
        
        # 更新会话统计
        await SessionService.increment_execution_count(
            db=db,
            session_id=request.session_id,
            execution_id=execution.execution_id,
            execution_time=int(result.get("execution_time", 0))
        )
        
    except Exception as e:
        logger.error(f"❌ 异步执行失败: {e}")
        await ExecutionService.update_execution_status(
            db=db,
            execution_id=execution.execution_id,
            status="failed",
            error_message=str(e)
        )


@router.get("/{execution_id}/status")
async def get_execution_status(
    execution_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取执行状态
    """
    execution = await ExecutionService.get_execution(db, execution_id)
    
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="执行记录不存在"
        )
    
    # 验证权限
    if execution.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此执行记录"
        )
    
    return execution.to_dict()


@router.get("/{execution_id}/result")
async def get_execution_result(
    execution_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取执行结果（完整）
    """
    execution = await ExecutionService.get_execution(db, execution_id)
    
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="执行记录不存在"
        )
    
    # 验证权限
    if execution.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此执行记录"
        )
    
    if execution.status not in ["completed", "failed", "timeout"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="执行尚未完成"
        )
    
    return execution.to_dict()


@router.websocket("/ws/{execution_id}")
async def websocket_execution(
    websocket: WebSocket,
    execution_id: str
):
    """
    WebSocket端点 - 接收实时执行输出
    
    消息格式:
    {
        "type": "status|output|error|completed|failed|timeout",
        "data": {...},
        "timestamp": "2025-11-03T10:00:00"
    }
    """
    await ws_manager.connect(execution_id, websocket)
    
    # 注册执行引擎回调
    async def ws_callback(message: dict):
        await ws_manager.send_message(execution_id, message)
    
    enhanced_execution_engine.register_ws_callback(execution_id, ws_callback)
    
    try:
        # 保持连接，等待客户端消息（可用于暂停/停止等控制）
        while True:
            data = await websocket.receive_text()
            
            # 处理客户端命令
            try:
                command = eval(data)  # 简单处理，生产环境应用json.loads
                
                if command.get("action") == "ping":
                    await websocket.send_json({"type": "pong"})
                
                # TODO: 实现暂停、停止等控制
                
            except Exception as e:
                logger.error(f"❌ 处理WebSocket命令失败: {e}")
    
    except WebSocketDisconnect:
        ws_manager.disconnect(execution_id)
        enhanced_execution_engine.unregister_ws_callback(execution_id)
        logger.info(f"👋 客户端断开连接: {execution_id}")


@router.get("/pool/stats")
async def get_pool_stats(
    current_user: User = Depends(get_current_user)
):
    """
    获取容器池统计信息（管理员功能）
    """
    # TODO: 添加管理员权限检查
    
    stats = enhanced_execution_engine.get_pool_stats()
    
    return {
        "container_pool": stats,
        "timestamp": asyncio.get_event_loop().time()
    }
