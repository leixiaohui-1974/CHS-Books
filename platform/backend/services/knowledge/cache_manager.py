"""
缓存管理器 - 提升系统性能
"""
import json
import hashlib
import time
from typing import Any, Optional, Dict
from collections import OrderedDict
import threading


class LRUCache:
    """LRU（最近最少使用）缓存"""
    
    def __init__(self, capacity: int = 100):
        """
        初始化LRU缓存
        
        Args:
            capacity: 缓存容量
        """
        self.cache = OrderedDict()
        self.capacity = capacity
        self.hits = 0
        self.misses = 0
        self.lock = threading.Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存值
        
        Args:
            key: 缓存键
            
        Returns:
            缓存值，不存在返回None
        """
        with self.lock:
            if key in self.cache:
                # 移到末尾（最近使用）
                self.cache.move_to_end(key)
                self.hits += 1
                
                # 检查是否过期
                entry = self.cache[key]
                if entry['expire_time'] and time.time() > entry['expire_time']:
                    del self.cache[key]
                    self.misses += 1
                    return None
                
                return entry['value']
            
            self.misses += 1
            return None
    
    def put(self, key: str, value: Any, ttl: Optional[int] = None):
        """
        设置缓存值
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 生存时间（秒），None表示永不过期
        """
        with self.lock:
            if key in self.cache:
                # 更新值并移到末尾
                self.cache.move_to_end(key)
            elif len(self.cache) >= self.capacity:
                # 删除最旧的项
                self.cache.popitem(last=False)
            
            expire_time = time.time() + ttl if ttl else None
            self.cache[key] = {
                'value': value,
                'expire_time': expire_time,
                'created_at': time.time()
            }
    
    def delete(self, key: str):
        """
        删除缓存
        
        Args:
            key: 缓存键
        """
        with self.lock:
            if key in self.cache:
                del self.cache[key]
    
    def clear(self):
        """清空缓存"""
        with self.lock:
            self.cache.clear()
            self.hits = 0
            self.misses = 0
    
    def size(self) -> int:
        """获取缓存大小"""
        with self.lock:
            return len(self.cache)
    
    def stats(self) -> Dict[str, Any]:
        """
        获取缓存统计
        
        Returns:
            统计信息
        """
        with self.lock:
            total = self.hits + self.misses
            hit_rate = self.hits / total if total > 0 else 0
            
            return {
                'size': len(self.cache),
                'capacity': self.capacity,
                'hits': self.hits,
                'misses': self.misses,
                'hit_rate': hit_rate
            }


class CacheManager:
    """缓存管理器"""
    
    def __init__(self):
        """初始化缓存管理器"""
        # 查询结果缓存
        self.query_cache = LRUCache(capacity=200)
        
        # 向量检索缓存
        self.vector_cache = LRUCache(capacity=100)
        
        # 知识内容缓存
        self.knowledge_cache = LRUCache(capacity=50)
    
    @staticmethod
    def _make_key(*args, **kwargs) -> str:
        """
        生成缓存键
        
        Args:
            *args: 位置参数
            **kwargs: 关键字参数
            
        Returns:
            缓存键
        """
        # 将参数序列化为字符串
        key_data = {
            'args': args,
            'kwargs': kwargs
        }
        key_str = json.dumps(key_data, sort_keys=True)
        
        # 生成hash
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def cache_query(
        self,
        query: str,
        mode: str,
        top_k: int,
        result: Any,
        ttl: int = 3600
    ):
        """
        缓存查询结果
        
        Args:
            query: 查询文本
            mode: 检索模式
            top_k: 结果数量
            result: 查询结果
            ttl: 生存时间（秒）
        """
        key = self._make_key('query', query, mode, top_k)
        self.query_cache.put(key, result, ttl)
    
    def get_cached_query(
        self,
        query: str,
        mode: str,
        top_k: int
    ) -> Optional[Any]:
        """
        获取缓存的查询结果
        
        Args:
            query: 查询文本
            mode: 检索模式
            top_k: 结果数量
            
        Returns:
            缓存的结果，不存在返回None
        """
        key = self._make_key('query', query, mode, top_k)
        return self.query_cache.get(key)
    
    def cache_vector_search(
        self,
        query: str,
        n_results: int,
        result: Any,
        ttl: int = 7200
    ):
        """
        缓存向量检索结果
        
        Args:
            query: 查询文本
            n_results: 结果数量
            result: 检索结果
            ttl: 生存时间（秒）
        """
        key = self._make_key('vector', query, n_results)
        self.vector_cache.put(key, result, ttl)
    
    def get_cached_vector_search(
        self,
        query: str,
        n_results: int
    ) -> Optional[Any]:
        """
        获取缓存的向量检索结果
        
        Args:
            query: 查询文本
            n_results: 结果数量
            
        Returns:
            缓存的结果，不存在返回None
        """
        key = self._make_key('vector', query, n_results)
        return self.vector_cache.get(key)
    
    def cache_knowledge(
        self,
        knowledge_id: str,
        content: Any,
        ttl: int = 86400
    ):
        """
        缓存知识内容
        
        Args:
            knowledge_id: 知识ID
            content: 知识内容
            ttl: 生存时间（秒）
        """
        key = f"knowledge_{knowledge_id}"
        self.knowledge_cache.put(key, content, ttl)
    
    def get_cached_knowledge(
        self,
        knowledge_id: str
    ) -> Optional[Any]:
        """
        获取缓存的知识内容
        
        Args:
            knowledge_id: 知识ID
            
        Returns:
            缓存的内容，不存在返回None
        """
        key = f"knowledge_{knowledge_id}"
        return self.knowledge_cache.get(key)
    
    def clear_all(self):
        """清空所有缓存"""
        self.query_cache.clear()
        self.vector_cache.clear()
        self.knowledge_cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取所有缓存统计
        
        Returns:
            统计信息
        """
        return {
            'query_cache': self.query_cache.stats(),
            'vector_cache': self.vector_cache.stats(),
            'knowledge_cache': self.knowledge_cache.stats(),
            'total_size': (
                self.query_cache.size() +
                self.vector_cache.size() +
                self.knowledge_cache.size()
            )
        }


# 全局缓存管理器实例
cache_manager = CacheManager()
