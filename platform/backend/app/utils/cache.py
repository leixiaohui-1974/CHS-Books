"""
Redis缓存工具类
提供缓存装饰器和缓存管理功能
"""

import json
import hashlib
from typing import Any, Optional, Callable
from functools import wraps
from loguru import logger
import asyncio

# 简化版缓存实现（内存缓存）
# 在实际生产环境中应该使用Redis


class SimpleCache:
    """简单内存缓存（用于开发/测试）"""
    
    def __init__(self):
        self._cache = {}
        self._ttl = {}
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        if key in self._cache:
            # 检查是否过期
            if key in self._ttl:
                import time
                if time.time() > self._ttl[key]:
                    del self._cache[key]
                    del self._ttl[key]
                    return None
            return self._cache[key]
        return None
    
    async def set(self, key: str, value: Any, ttl: int = 300):
        """设置缓存"""
        self._cache[key] = value
        if ttl > 0:
            import time
            self._ttl[key] = time.time() + ttl
    
    async def delete(self, key: str):
        """删除缓存"""
        if key in self._cache:
            del self._cache[key]
        if key in self._ttl:
            del self._ttl[key]
    
    async def clear(self):
        """清空缓存"""
        self._cache.clear()
        self._ttl.clear()
    
    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        value = await self.get(key)
        return value is not None


# 全局缓存实例
cache = SimpleCache()


def cache_key(*args, **kwargs) -> str:
    """生成缓存键"""
    key_str = f"{args}_{kwargs}"
    return hashlib.md5(key_str.encode()).hexdigest()


def cached(ttl: int = 300, key_prefix: str = ""):
    """
    缓存装饰器
    
    Args:
        ttl: 缓存时间（秒）
        key_prefix: 缓存键前缀
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            func_name = f"{key_prefix}{func.__module__}.{func.__name__}"
            key = f"{func_name}:{cache_key(*args, **kwargs)}"
            
            # 尝试从缓存获取
            cached_value = await cache.get(key)
            if cached_value is not None:
                logger.debug(f"Cache hit: {key}")
                return cached_value
            
            # 缓存未命中，执行函数
            logger.debug(f"Cache miss: {key}")
            result = await func(*args, **kwargs)
            
            # 存入缓存
            await cache.set(key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


async def invalidate_cache_pattern(pattern: str):
    """
    使缓存失效（按模式）
    
    Args:
        pattern: 缓存键模式
    """
    # 简化实现：清空所有缓存
    # 在实际Redis实现中应该使用SCAN命令匹配模式
    await cache.clear()
    logger.info(f"Invalidated cache pattern: {pattern}")


class CacheManager:
    """缓存管理器"""
    
    def __init__(self):
        self.cache = cache
    
    async def get_or_set(
        self,
        key: str,
        factory: Callable,
        ttl: int = 300
    ) -> Any:
        """
        获取缓存，如果不存在则调用factory函数生成
        
        Args:
            key: 缓存键
            factory: 工厂函数（用于生成值）
            ttl: 缓存时间
        """
        value = await self.cache.get(key)
        
        if value is None:
            value = await factory() if asyncio.iscoroutinefunction(factory) else factory()
            await self.cache.set(key, value, ttl)
        
        return value
    
    async def clear_user_cache(self, user_id: int):
        """清除用户相关缓存"""
        # 简化实现
        await self.cache.clear()
        logger.info(f"Cleared cache for user {user_id}")
    
    async def clear_book_cache(self, book_id: int):
        """清除书籍相关缓存"""
        await self.cache.clear()
        logger.info(f"Cleared cache for book {book_id}")


# 全局缓存管理器
cache_manager = CacheManager()
