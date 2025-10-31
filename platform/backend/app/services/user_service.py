"""
用户服务 - 业务逻辑层
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models.user import User, UserRole
from app.core.security import get_password_hash, verify_password
from loguru import logger


class UserService:
    """用户服务类"""
    
    @staticmethod
    async def create_user(
        db: AsyncSession,
        email: str,
        username: str,
        password: str,
        full_name: Optional[str] = None
    ) -> User:
        """
        创建新用户
        
        Args:
            db: 数据库会话
            email: 邮箱
            username: 用户名
            password: 密码
            full_name: 真实姓名
            
        Returns:
            创建的用户对象
            
        Raises:
            IntegrityError: 邮箱或用户名已存在
        """
        try:
            # 创建用户对象
            user = User(
                email=email,
                username=username,
                hashed_password=get_password_hash(password),
                full_name=full_name,
                role=UserRole.USER,
                is_active=True,
                is_verified=False
            )
            
            db.add(user)
            await db.commit()
            await db.refresh(user)
            
            logger.info(f"✅ 创建用户成功: {email}")
            return user
            
        except IntegrityError as e:
            await db.rollback()
            logger.error(f"❌ 创建用户失败: {e}")
            raise ValueError("邮箱或用户名已存在")
    
    @staticmethod
    async def get_user_by_email(
        db: AsyncSession,
        email: str
    ) -> Optional[User]:
        """通过邮箱查询用户"""
        result = await db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_username(
        db: AsyncSession,
        username: str
    ) -> Optional[User]:
        """通过用户名查询用户"""
        result = await db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_id(
        db: AsyncSession,
        user_id: int
    ) -> Optional[User]:
        """通过ID查询用户"""
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def authenticate_user(
        db: AsyncSession,
        email_or_username: str,
        password: str
    ) -> Optional[User]:
        """
        验证用户登录
        
        Args:
            db: 数据库会话
            email_or_username: 邮箱或用户名
            password: 密码
            
        Returns:
            验证成功返回用户对象，否则返回None
        """
        # 尝试用邮箱查询
        user = await UserService.get_user_by_email(db, email_or_username)
        
        # 如果邮箱查询失败，尝试用户名查询
        if not user:
            user = await UserService.get_user_by_username(db, email_or_username)
        
        # 验证密码
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        if not user.is_active:
            return None
        
        logger.info(f"✅ 用户认证成功: {user.email}")
        return user
    
    @staticmethod
    async def update_user(
        db: AsyncSession,
        user_id: int,
        **kwargs
    ) -> Optional[User]:
        """
        更新用户信息
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            **kwargs: 要更新的字段
            
        Returns:
            更新后的用户对象
        """
        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            return None
        
        # 更新字段
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        await db.commit()
        await db.refresh(user)
        
        logger.info(f"✅ 更新用户成功: {user.email}")
        return user
    
    @staticmethod
    async def change_password(
        db: AsyncSession,
        user_id: int,
        old_password: str,
        new_password: str
    ) -> bool:
        """
        修改密码
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            old_password: 旧密码
            new_password: 新密码
            
        Returns:
            成功返回True，否则返回False
        """
        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            return False
        
        # 验证旧密码
        if not verify_password(old_password, user.hashed_password):
            logger.warning(f"⚠️  修改密码失败: 旧密码错误 - user_id={user_id}")
            return False
        
        # 更新密码
        user.hashed_password = get_password_hash(new_password)
        await db.commit()
        
        logger.info(f"✅ 修改密码成功: {user.email}")
        return True
    
    @staticmethod
    async def delete_user(
        db: AsyncSession,
        user_id: int
    ) -> bool:
        """
        删除用户（软删除）
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            
        Returns:
            成功返回True
        """
        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            return False
        
        # 软删除
        from datetime import datetime, timezone
        user.deleted_at = datetime.now(timezone.utc)
        user.is_active = False
        
        await db.commit()
        
        logger.info(f"✅ 删除用户成功: {user.email}")
        return True
