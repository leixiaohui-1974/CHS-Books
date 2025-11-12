"""
优化的检索服务 - 集成缓存
"""
from typing import Dict, Any, Optional
import time

from .hybrid_search import HybridSearch
from .cache_manager import cache_manager


class OptimizedSearch:
    """优化的检索服务"""
    
    def __init__(self):
        """初始化优化检索"""
        self.hybrid_search = HybridSearch()
        self.cache = cache_manager
    
    def search(
        self,
        query: str,
        top_k: int = 10,
        mode: str = 'hybrid',
        alpha: float = 0.5,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        检索（带缓存）
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            mode: 检索模式
            alpha: 关键词权重
            use_cache: 是否使用缓存
            
        Returns:
            检索结果
        """
        start_time = time.time()
        
        # 尝试从缓存获取
        if use_cache:
            cached = self.cache.get_cached_query(query, mode, top_k)
            if cached is not None:
                cache_time = time.time() - start_time
                cached['from_cache'] = True
                cached['cache_hit'] = True
                cached['timing'] = {
                    'total_ms': cache_time * 1000,
                    'cache_ms': cache_time * 1000
                }
                return cached
        
        # 执行检索
        results = self.hybrid_search.search(query, top_k, mode, alpha)
        
        # 添加时间统计
        elapsed = time.time() - start_time
        results['from_cache'] = False
        results['cache_hit'] = False
        results['timing'] = {
            'total_ms': elapsed * 1000,
            'search_ms': elapsed * 1000
        }
        
        # 缓存结果
        if use_cache:
            self.cache.cache_query(query, mode, top_k, results)
        
        return results
    
    def advanced_search(
        self,
        query: str,
        category: Optional[str] = None,
        level: Optional[str] = None,
        top_k: int = 10,
        mode: str = 'hybrid',
        alpha: float = 0.5,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        高级检索（带缓存）
        
        Args:
            query: 查询文本
            category: 分类过滤
            level: 层级过滤
            top_k: 返回结果数量
            mode: 检索模式
            alpha: 关键词权重
            use_cache: 是否使用缓存
            
        Returns:
            检索结果
        """
        start_time = time.time()
        
        # 生成缓存键（包含过滤条件）
        cache_key_parts = [query, mode, top_k, category or '', level or '']
        
        # 尝试从缓存获取
        if use_cache:
            from .cache_manager import CacheManager
            key = CacheManager._make_key('advanced', *cache_key_parts)
            cached = cache_manager.query_cache.get(key)
            if cached is not None:
                cache_time = time.time() - start_time
                cached['from_cache'] = True
                cached['cache_hit'] = True
                cached['timing'] = {
                    'total_ms': cache_time * 1000,
                    'cache_ms': cache_time * 1000
                }
                return cached
        
        # 执行检索
        results = self.hybrid_search.advanced_search(
            query, category, level, top_k, mode, alpha
        )
        
        # 添加时间统计
        elapsed = time.time() - start_time
        results['from_cache'] = False
        results['cache_hit'] = False
        results['timing'] = {
            'total_ms': elapsed * 1000,
            'search_ms': elapsed * 1000
        }
        
        # 缓存结果
        if use_cache:
            from .cache_manager import CacheManager
            key = CacheManager._make_key('advanced', *cache_key_parts)
            cache_manager.query_cache.put(key, results, ttl=3600)
        
        return results
    
    def batch_search(
        self,
        queries: list,
        top_k: int = 10,
        mode: str = 'hybrid',
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        批量检索
        
        Args:
            queries: 查询列表
            top_k: 每个查询返回结果数量
            mode: 检索模式
            use_cache: 是否使用缓存
            
        Returns:
            批量检索结果
        """
        start_time = time.time()
        
        results = []
        cache_hits = 0
        
        for query in queries:
            result = self.search(query, top_k, mode, use_cache=use_cache)
            results.append(result)
            if result.get('cache_hit'):
                cache_hits += 1
        
        total_time = time.time() - start_time
        
        return {
            'queries': queries,
            'results': results,
            'total_queries': len(queries),
            'cache_hits': cache_hits,
            'cache_hit_rate': cache_hits / len(queries) if queries else 0,
            'timing': {
                'total_ms': total_time * 1000,
                'avg_per_query_ms': total_time * 1000 / len(queries) if queries else 0
            }
        }
    
    def warmup_cache(
        self,
        common_queries: list,
        top_k: int = 10,
        mode: str = 'hybrid'
    ) -> Dict[str, Any]:
        """
        预热缓存
        
        Args:
            common_queries: 常见查询列表
            top_k: 结果数量
            mode: 检索模式
            
        Returns:
            预热统计
        """
        start_time = time.time()
        
        warmed = 0
        for query in common_queries:
            # 执行检索并缓存
            self.search(query, top_k, mode, use_cache=True)
            warmed += 1
        
        elapsed = time.time() - start_time
        
        return {
            'warmed_queries': warmed,
            'timing': {
                'total_ms': elapsed * 1000,
                'avg_per_query_ms': elapsed * 1000 / warmed if warmed else 0
            },
            'cache_stats': self.cache.get_stats()
        }
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计
        
        Returns:
            统计信息
        """
        return self.cache.get_stats()
    
    def clear_cache(self):
        """清空缓存"""
        self.cache.clear_all()


# 全局实例
optimized_search = OptimizedSearch()
