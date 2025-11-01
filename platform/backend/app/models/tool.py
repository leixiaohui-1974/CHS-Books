"""
工具执行模型
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class ToolExecutionStatus(str, enum.Enum):
    """工具执行状态"""
    PENDING = "pending"       # 等待中
    RUNNING = "running"       # 运行中
    COMPLETED = "completed"   # 已完成
    FAILED = "failed"        # 失败
    TIMEOUT = "timeout"      # 超时
    CANCELLED = "cancelled"   # 已取消


class ToolExecution(Base):
    """工具执行记录"""
    
    __tablename__ = "tool_executions"
    
    # 基本信息
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(64), unique=True, index=True, nullable=False)  # 任务ID（UUID）
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    case_id = Column(Integer, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False)
    
    # 执行状态
    status = Column(SQLEnum(ToolExecutionStatus), default=ToolExecutionStatus.PENDING, nullable=False)
    
    # 输入参数
    input_params = Column(JSON, nullable=False)  # 用户输入的参数
    
    # 输出结果
    output_data = Column(JSON, nullable=True)  # 结果数据（图表、表格等）
    console_output = Column(Text, nullable=True)  # 控制台输出
    error_message = Column(Text, nullable=True)  # 错误信息
    
    # 执行信息
    execution_time = Column(Float, nullable=True)  # 执行时长（秒）
    memory_used = Column(Integer, nullable=True)  # 内存使用（MB）
    
    # Docker容器信息
    container_id = Column(String(128), nullable=True)
    docker_image = Column(String(200), nullable=True)
    
    # 代码版本（用于追踪）
    script_version = Column(String(64), nullable=True)  # Git commit hash
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # 关系
    user = relationship("User", back_populates="tool_executions")
    case = relationship("Case", back_populates="executions")
    
    def __repr__(self):
        return f"<ToolExecution(id={self.id}, task_id={self.task_id}, status={self.status})>"
    
    @property
    def is_finished(self) -> bool:
        """是否已结束（成功或失败）"""
        return self.status in [
            ToolExecutionStatus.COMPLETED,
            ToolExecutionStatus.FAILED,
            ToolExecutionStatus.TIMEOUT,
            ToolExecutionStatus.CANCELLED
        ]
