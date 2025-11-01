"""
Redis缓存配置
"""

import redis.asyncio as redis
from typing import Optional, Any
import json
from .config import settings
from loguru import logger


class RedisCache:
    """Redis缓存管理类"""
    
    def __init__(self):
        self.redis: Optional[redis.Redis] = None
    
    async def connect(self):
        """连接Redis"""
        try:
            self.redis = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                max_connections=50
            )
            await self.redis.ping()
            logger.info("✅ Redis连接成功")
        except Exception as e:
            logger.error(f"❌ Redis连接失败: {e}")
            raise
    
    async def close(self):
        """关闭Redis连接"""
        if self.redis:
            await self.redis.close()
            logger.info("👋 Redis连接已关闭")
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        if not self.redis:
            await self.connect()
        
        try:
            value = await self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"❌ Redis GET错误: {e}")
            return None
    
    async def set(
        self,
        key: str,
        value: Any,
        expire: Optional[int] = None
    ) -> bool:
        """设置缓存值"""
        if not self.redis:
            await self.connect()
        
        try:
            serialized = json.dumps(value, ensure_ascii=False, default=str)
            if expire:
                await self.redis.setex(key, expire, serialized)
            else:
                await self.redis.set(key, serialized)
            return True
        except Exception as e:
            logger.error(f"❌ Redis SET错误: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """删除缓存"""
        if not self.redis:
            await self.connect()
        
        try:
            await self.redis.delete(key)
            return True
        except Exception as e:
            logger.error(f"❌ Redis DELETE错误: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        if not self.redis:
            await self.connect()
        
        try:
            return await self.redis.exists(key) > 0
        except Exception as e:
            logger.error(f"❌ Redis EXISTS错误: {e}")
            return False
    
    async def expire(self, key: str, seconds: int) -> bool:
        """设置过期时间"""
        if not self.redis:
            await self.connect()
        
        try:
            return await self.redis.expire(key, seconds)
        except Exception as e:
            logger.error(f"❌ Redis EXPIRE错误: {e}")
            return False
    
    async def ping(self) -> bool:
        """测试连接"""
        if not self.redis:
            await self.connect()
        
        try:
            return await self.redis.ping()
        except Exception as e:
            logger.error(f"❌ Redis PING错误: {e}")
            return False
    
    async def increment(self, key: str, amount: int = 1) -> int:
        """递增计数器"""
        if not self.redis:
            await self.connect()
        
        try:
            return await self.redis.incrby(key, amount)
        except Exception as e:
            logger.error(f"❌ Redis INCR错误: {e}")
            return 0
    
    async def decrement(self, key: str, amount: int = 1) -> int:
        """递减计数器"""
        if not self.redis:
            await self.connect()
        
        try:
            return await self.redis.decrby(key, amount)
        except Exception as e:
            logger.error(f"❌ Redis DECR错误: {e}")
            return 0


# 创建全局Redis客户端实例
redis_client = RedisCache()


# 缓存装饰器
def cache(expire: int = 300, key_prefix: str = ""):
    """
    缓存装饰器
    
    Args:
        expire: 过期时间（秒）
        key_prefix: 键前缀
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{key_prefix}:{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # 尝试从缓存获取
            cached_value = await redis_client.get(cache_key)
            if cached_value is not None:
                logger.debug(f"🎯 缓存命中: {cache_key}")
                return cached_value
            
            # 执行函数
            result = await func(*args, **kwargs)
            
            # 缓存结果
            await redis_client.set(cache_key, result, expire)
            logger.debug(f"💾 缓存保存: {cache_key}")
            
            return result
        
        return wrapper
    return decorator
