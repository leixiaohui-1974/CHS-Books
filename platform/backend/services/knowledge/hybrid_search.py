"""
混合检索 - 结合关键词检索和语义检索
"""
from typing import List, Dict, Any, Optional
import re

from .vector_store import vector_store
from .knowledge_manager import knowledge_manager


class HybridSearch:
    """混合检索引擎"""
    
    def __init__(self):
        """初始化混合检索"""
        self.vector_store = vector_store
        self.knowledge_manager = knowledge_manager
    
    def _keyword_search(
        self,
        query: str,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        关键词检索
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            
        Returns:
            检索结果列表
        """
        # 使用知识管理器的搜索功能
        results = self.knowledge_manager.search_knowledge(query)
        
        # 格式化结果
        formatted = []
        for i, entry in enumerate(results[:top_k]):
            formatted.append({
                'title': entry['title'],
                'content': entry.get('content', ''),
                'category': entry.get('category', ''),
                'level': entry.get('level', ''),
                'source': 'keyword',
                'score': entry.get('match_score', 0),
                'rank': i + 1
            })
        
        return formatted
    
    def _semantic_search(
        self,
        query: str,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        语义检索
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            
        Returns:
            检索结果列表
        """
        results = self.vector_store.search(query, n_results=top_k)
        
        # 格式化结果
        formatted = []
        if results['ids'] and len(results['ids'][0]) > 0:
            for i, (doc_id, metadata, distance) in enumerate(
                zip(results['ids'][0], results['metadatas'][0], results['distances'][0])
            ):
                relevance = 1 - distance
                formatted.append({
                    'id': doc_id,
                    'title': metadata.get('title', ''),
                    'category': metadata.get('category', ''),
                    'level': metadata.get('level', ''),
                    'source': 'semantic',
                    'score': relevance,
                    'rank': i + 1
                })
        
        return formatted
    
    def _merge_results(
        self,
        keyword_results: List[Dict[str, Any]],
        semantic_results: List[Dict[str, Any]],
        alpha: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        合并检索结果
        
        Args:
            keyword_results: 关键词检索结果
            semantic_results: 语义检索结果
            alpha: 关键词权重（0-1），语义权重为1-alpha
            
        Returns:
            合并后的结果列表
        """
        # 创建标题到结果的映射
        merged = {}
        
        # 处理关键词检索结果
        for result in keyword_results:
            title = result['title']
            # 归一化分数（基于排名）
            normalized_score = 1.0 / (result['rank'] + 1)
            
            merged[title] = {
                'title': title,
                'category': result['category'],
                'level': result['level'],
                'keyword_score': result['score'],
                'semantic_score': 0,
                'keyword_rank': result['rank'],
                'semantic_rank': None,
                'sources': ['keyword'],
                'combined_score': alpha * normalized_score
            }
        
        # 处理语义检索结果
        for result in semantic_results:
            title = result['title']
            normalized_score = 1.0 / (result['rank'] + 1)
            
            if title in merged:
                # 已存在，更新分数
                merged[title]['semantic_score'] = result['score']
                merged[title]['semantic_rank'] = result['rank']
                merged[title]['sources'].append('semantic')
                merged[title]['combined_score'] += (1 - alpha) * normalized_score
            else:
                # 新结果
                merged[title] = {
                    'title': title,
                    'category': result['category'],
                    'level': result['level'],
                    'keyword_score': 0,
                    'semantic_score': result['score'],
                    'keyword_rank': None,
                    'semantic_rank': result['rank'],
                    'sources': ['semantic'],
                    'combined_score': (1 - alpha) * normalized_score
                }
        
        # 转换为列表并排序
        merged_list = list(merged.values())
        merged_list.sort(key=lambda x: x['combined_score'], reverse=True)
        
        return merged_list
    
    def search(
        self,
        query: str,
        top_k: int = 10,
        mode: str = 'hybrid',
        alpha: float = 0.5
    ) -> Dict[str, Any]:
        """
        混合检索
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            mode: 检索模式 ('keyword', 'semantic', 'hybrid')
            alpha: 关键词权重（仅hybrid模式）
            
        Returns:
            检索结果
        """
        if mode == 'keyword':
            # 仅关键词检索
            results = self._keyword_search(query, top_k)
            return {
                'query': query,
                'mode': 'keyword',
                'results': results,
                'total': len(results)
            }
        
        elif mode == 'semantic':
            # 仅语义检索
            results = self._semantic_search(query, top_k)
            return {
                'query': query,
                'mode': 'semantic',
                'results': results,
                'total': len(results)
            }
        
        else:  # hybrid
            # 混合检索
            keyword_results = self._keyword_search(query, top_k * 2)
            semantic_results = self._semantic_search(query, top_k * 2)
            
            merged_results = self._merge_results(
                keyword_results,
                semantic_results,
                alpha
            )
            
            # 取前top_k个
            final_results = merged_results[:top_k]
            
            return {
                'query': query,
                'mode': 'hybrid',
                'alpha': alpha,
                'results': final_results,
                'total': len(final_results),
                'stats': {
                    'keyword_only': len([r for r in final_results if r['sources'] == ['keyword']]),
                    'semantic_only': len([r for r in final_results if r['sources'] == ['semantic']]),
                    'both': len([r for r in final_results if len(r['sources']) == 2])
                }
            }
    
    def advanced_search(
        self,
        query: str,
        category: Optional[str] = None,
        level: Optional[str] = None,
        top_k: int = 10,
        mode: str = 'hybrid',
        alpha: float = 0.5
    ) -> Dict[str, Any]:
        """
        高级检索（带过滤）
        
        Args:
            query: 查询文本
            category: 分类过滤
            level: 层级过滤
            top_k: 返回结果数量
            mode: 检索模式
            alpha: 关键词权重
            
        Returns:
            检索结果
        """
        # 先进行普通检索
        results = self.search(query, top_k * 3, mode, alpha)
        
        # 应用过滤
        filtered = []
        for result in results['results']:
            # 分类过滤
            if category and category not in result.get('category', ''):
                continue
            
            # 层级过滤
            if level and level != result.get('level', ''):
                continue
            
            filtered.append(result)
            
            # 达到top_k就停止
            if len(filtered) >= top_k:
                break
        
        results['results'] = filtered
        results['total'] = len(filtered)
        results['filters'] = {
            'category': category,
            'level': level
        }
        
        return results
    
    def multi_query_search(
        self,
        queries: List[str],
        top_k: int = 10,
        mode: str = 'hybrid'
    ) -> Dict[str, Any]:
        """
        多查询检索（查询扩展）
        
        Args:
            queries: 多个查询文本
            top_k: 返回结果数量
            mode: 检索模式
            
        Returns:
            合并后的检索结果
        """
        all_results = []
        
        # 对每个查询进行检索
        for query in queries:
            result = self.search(query, top_k, mode)
            all_results.extend(result['results'])
        
        # 去重并合并分数
        merged = {}
        for result in all_results:
            title = result['title']
            if title in merged:
                # 合并分数（取最大值）
                if result.get('combined_score', 0) > merged[title].get('combined_score', 0):
                    merged[title] = result
            else:
                merged[title] = result
        
        # 排序
        merged_list = list(merged.values())
        merged_list.sort(key=lambda x: x.get('combined_score', 0), reverse=True)
        
        return {
            'queries': queries,
            'mode': mode,
            'results': merged_list[:top_k],
            'total': len(merged_list[:top_k])
        }
    
    def explain_ranking(
        self,
        query: str,
        title: str,
        mode: str = 'hybrid',
        alpha: float = 0.5
    ) -> Dict[str, Any]:
        """
        解释排名原因
        
        Args:
            query: 查询文本
            title: 知识标题
            mode: 检索模式
            alpha: 关键词权重
            
        Returns:
            排名解释
        """
        results = self.search(query, 20, mode, alpha)
        
        # 查找目标结果
        target = None
        for i, result in enumerate(results['results'], 1):
            if result['title'] == title:
                target = result
                target['final_rank'] = i
                break
        
        if not target:
            return {
                'found': False,
                'message': f'未在前20个结果中找到"{title}"'
            }
        
        explanation = {
            'found': True,
            'title': title,
            'final_rank': target['final_rank'],
            'combined_score': target.get('combined_score', 0),
            'breakdown': {}
        }
        
        if mode == 'hybrid' or mode == 'keyword':
            explanation['breakdown']['keyword'] = {
                'rank': target.get('keyword_rank'),
                'score': target.get('keyword_score', 0),
                'weight': alpha if mode == 'hybrid' else 1.0
            }
        
        if mode == 'hybrid' or mode == 'semantic':
            explanation['breakdown']['semantic'] = {
                'rank': target.get('semantic_rank'),
                'score': target.get('semantic_score', 0),
                'weight': 1 - alpha if mode == 'hybrid' else 1.0
            }
        
        explanation['sources'] = target.get('sources', [])
        explanation['category'] = target.get('category', '')
        explanation['level'] = target.get('level', '')
        
        return explanation


# 全局实例
hybrid_search = HybridSearch()
