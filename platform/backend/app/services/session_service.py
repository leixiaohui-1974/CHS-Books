"""
会话管理服务
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.models.session import UserSession, SessionStatus, CodeExecution
from app.models.user import User


class SessionService:
    """会话管理服务"""
    
    @staticmethod
    async def create_session(
        db: AsyncSession,
        user_id: int,
        book_slug: str,
        case_slug: str,
        chapter_slug: Optional[str] = None
    ) -> UserSession:
        """
        创建新会话
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            book_slug: 书籍slug
            case_slug: 案例slug
            chapter_slug: 章节slug（可选）
            
        Returns:
            创建的会话对象
        """
        # 生成唯一session_id
        session_id = f"sess_{uuid.uuid4().hex[:16]}"
        
        # 创建会话
        session = UserSession(
            session_id=session_id,
            user_id=user_id,
            book_slug=book_slug,
            chapter_slug=chapter_slug,
            case_slug=case_slug,
            status=SessionStatus.ACTIVE
        )
        
        db.add(session)
        await db.commit()
        await db.refresh(session)
        
        logger.info(f"✅ 创建会话: {session_id} (用户: {user_id}, 案例: {book_slug}/{case_slug})")
        
        return session
    
    @staticmethod
    async def get_session(
        db: AsyncSession,
        session_id: str,
        user_id: Optional[int] = None
    ) -> Optional[UserSession]:
        """
        获取会话
        
        Args:
            db: 数据库会话
            session_id: 会话ID
            user_id: 用户ID（可选，用于验证权限）
            
        Returns:
            会话对象或None
        """
        query = select(UserSession).where(UserSession.session_id == session_id)
        
        if user_id is not None:
            query = query.where(UserSession.user_id == user_id)
        
        result = await db.execute(query)
        session = result.scalar_one_or_none()
        
        if session:
            # 更新活跃时间
            session.update_activity()
            await db.commit()
        
        return session
    
    @staticmethod
    async def list_user_sessions(
        db: AsyncSession,
        user_id: int,
        status: Optional[SessionStatus] = None,
        limit: int = 50
    ) -> List[UserSession]:
        """
        获取用户的所有会话
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            status: 状态筛选（可选）
            limit: 返回数量限制
            
        Returns:
            会话列表
        """
        query = select(UserSession).where(UserSession.user_id == user_id)
        
        if status:
            query = query.where(UserSession.status == status)
        
        query = query.order_by(UserSession.last_active_at.desc()).limit(limit)
        
        result = await db.execute(query)
        sessions = result.scalars().all()
        
        return list(sessions)
    
    @staticmethod
    async def update_session_status(
        db: AsyncSession,
        session_id: str,
        status: SessionStatus
    ) -> Optional[UserSession]:
        """
        更新会话状态
        
        Args:
            db: 数据库会话
            session_id: 会话ID
            status: 新状态
            
        Returns:
            更新后的会话对象
        """
        session = await SessionService.get_session(db, session_id)
        
        if not session:
            return None
        
        session.status = status
        session.update_activity()
        
        await db.commit()
        await db.refresh(session)
        
        logger.info(f"🔄 更新会话状态: {session_id} -> {status.value}")
        
        return session
    
    @staticmethod
    async def extend_session(
        db: AsyncSession,
        session_id: str,
        hours: int = 24
    ) -> Optional[UserSession]:
        """
        延长会话有效期
        
        Args:
            db: 数据库会话
            session_id: 会话ID
            hours: 延长小时数
            
        Returns:
            更新后的会话对象
        """
        session = await SessionService.get_session(db, session_id)
        
        if not session:
            return None
        
        session.extend_expiration(hours)
        await db.commit()
        await db.refresh(session)
        
        logger.info(f"⏰ 延长会话: {session_id} (新过期时间: {session.expires_at})")
        
        return session
    
    @staticmethod
    async def terminate_session(
        db: AsyncSession,
        session_id: str
    ) -> bool:
        """
        终止会话
        
        Args:
            db: 数据库会话
            session_id: 会话ID
            
        Returns:
            是否成功
        """
        session = await SessionService.get_session(db, session_id)
        
        if not session:
            return False
        
        session.status = SessionStatus.TERMINATED
        await db.commit()
        
        logger.info(f"🛑 终止会话: {session_id}")
        
        # TODO: 清理会话相关资源（工作区文件、容器等）
        
        return True
    
    @staticmethod
    async def update_modified_files(
        db: AsyncSession,
        session_id: str,
        file_path: str,
        content: str
    ) -> Optional[UserSession]:
        """
        更新会话中修改的文件
        
        Args:
            db: 数据库会话
            session_id: 会话ID
            file_path: 文件路径
            content: 文件内容
            
        Returns:
            更新后的会话对象
        """
        session = await SessionService.get_session(db, session_id)
        
        if not session:
            return None
        
        # 更新modified_files
        if not isinstance(session.modified_files, dict):
            session.modified_files = {}
        
        session.modified_files[file_path] = {
            "content": content,
            "modified_at": datetime.utcnow().isoformat()
        }
        
        session.update_activity()
        await db.commit()
        await db.refresh(session)
        
        logger.info(f"📝 更新文件: {session_id}/{file_path}")
        
        return session
    
    @staticmethod
    async def increment_execution_count(
        db: AsyncSession,
        session_id: str,
        execution_id: str,
        execution_time: int = 0
    ) -> Optional[UserSession]:
        """
        增加执行计数
        
        Args:
            db: 数据库会话
            session_id: 会话ID
            execution_id: 执行ID
            execution_time: 执行时间（秒）
            
        Returns:
            更新后的会话对象
        """
        session = await SessionService.get_session(db, session_id)
        
        if not session:
            return None
        
        session.execution_count += 1
        session.last_execution_id = execution_id
        session.total_execution_time += execution_time
        session.update_activity()
        
        await db.commit()
        await db.refresh(session)
        
        return session
    
    @staticmethod
    async def cleanup_expired_sessions(
        db: AsyncSession,
        batch_size: int = 100
    ) -> int:
        """
        清理过期会话
        
        Args:
            db: 数据库会话
            batch_size: 批次大小
            
        Returns:
            清理的会话数量
        """
        # 查找过期会话
        query = select(UserSession).where(
            and_(
                UserSession.status == SessionStatus.ACTIVE,
                UserSession.expires_at < datetime.utcnow()
            )
        ).limit(batch_size)
        
        result = await db.execute(query)
        expired_sessions = result.scalars().all()
        
        count = 0
        for session in expired_sessions:
            session.status = SessionStatus.EXPIRED
            count += 1
        
        await db.commit()
        
        if count > 0:
            logger.info(f"🧹 清理过期会话: {count} 个")
        
        return count


class ExecutionService:
    """代码执行记录服务"""
    
    @staticmethod
    async def create_execution(
        db: AsyncSession,
        session_id: str,
        user_id: int,
        script_path: str,
        input_params: Dict[str, Any]
    ) -> CodeExecution:
        """
        创建执行记录
        
        Args:
            db: 数据库会话
            session_id: 会话ID
            user_id: 用户ID
            script_path: 脚本路径
            input_params: 输入参数
            
        Returns:
            执行记录对象
        """
        execution_id = f"exec_{uuid.uuid4().hex[:16]}"
        
        execution = CodeExecution(
            execution_id=execution_id,
            session_id=session_id,
            user_id=user_id,
            script_path=script_path,
            input_params=input_params,
            status="pending"
        )
        
        db.add(execution)
        await db.commit()
        await db.refresh(execution)
        
        logger.info(f"📝 创建执行记录: {execution_id}")
        
        return execution
    
    @staticmethod
    async def get_execution(
        db: AsyncSession,
        execution_id: str
    ) -> Optional[CodeExecution]:
        """获取执行记录"""
        query = select(CodeExecution).where(CodeExecution.execution_id == execution_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def update_execution_status(
        db: AsyncSession,
        execution_id: str,
        status: str,
        **kwargs
    ) -> Optional[CodeExecution]:
        """
        更新执行状态
        
        Args:
            db: 数据库会话
            execution_id: 执行ID
            status: 新状态
            **kwargs: 其他要更新的字段
            
        Returns:
            更新后的执行记录
        """
        execution = await ExecutionService.get_execution(db, execution_id)
        
        if not execution:
            return None
        
        execution.status = status
        
        # 更新时间戳
        if status == "running" and not execution.started_at:
            execution.started_at = datetime.utcnow()
        elif status in ["completed", "failed", "timeout"] and not execution.completed_at:
            execution.completed_at = datetime.utcnow()
            if execution.started_at:
                execution.execution_time = int((execution.completed_at - execution.started_at).total_seconds())
        
        # 更新其他字段
        for key, value in kwargs.items():
            if hasattr(execution, key):
                setattr(execution, key, value)
        
        await db.commit()
        await db.refresh(execution)
        
        logger.info(f"🔄 更新执行状态: {execution_id} -> {status}")
        
        return execution
    
    @staticmethod
    async def list_session_executions(
        db: AsyncSession,
        session_id: str,
        limit: int = 50
    ) -> List[CodeExecution]:
        """获取会话的所有执行记录"""
        query = select(CodeExecution).where(
            CodeExecution.session_id == session_id
        ).order_by(CodeExecution.created_at.desc()).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())
