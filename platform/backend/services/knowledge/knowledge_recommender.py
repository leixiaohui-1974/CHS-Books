"""
知识推荐系统 - 基于多种策略的智能推荐
"""
import sys
sys.path.insert(0, '.')

from typing import List, Dict, Any, Set
from collections import defaultdict, Counter
import random

from .vector_store import vector_store
from .knowledge_manager import knowledge_manager


class KnowledgeRecommender:
    """知识推荐系统"""
    
    def __init__(self):
        self.user_history = defaultdict(list)  # 用户浏览历史
        self.popular_knowledge = Counter()  # 知识热度
        
    def recommend_similar(self, knowledge_title: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        基于相似度推荐
        
        Args:
            knowledge_title: 当前知识标题
            top_k: 推荐数量
            
        Returns:
            推荐的知识列表
        """
        # 使用向量检索找到相似知识
        results = vector_store.search(knowledge_title, n_results=top_k + 1)
        
        recommendations = []
        
        if results['ids']:
            for i in range(1, len(results['ids'][0])):  # 跳过自己
                metadata = results['metadatas'][0][i]
                distance = results['distances'][0][i]
                
                recommendations.append({
                    'title': metadata.get('title', ''),
                    'category': metadata.get('category', ''),
                    'level': metadata.get('level', ''),
                    'similarity': 1 - distance,
                    'reason': '内容相似',
                    'score': (1 - distance) * 100
                })
        
        return recommendations[:top_k]
    
    def recommend_by_category(self, current_category: str, exclude_title: str = None, 
                            top_k: int = 5) -> List[Dict[str, Any]]:
        """
        基于分类推荐
        
        Args:
            current_category: 当前分类
            exclude_title: 要排除的知识标题
            top_k: 推荐数量
            
        Returns:
            推荐的知识列表
        """
        recommendations = []
        
        # 遍历知识库找到同类知识
        for category_key, items in knowledge_manager.knowledge_data.items():
            for item in items:
                if item['category'] == current_category:
                    if exclude_title and item['title'] == exclude_title:
                        continue
                    
                    recommendations.append({
                        'title': item['title'],
                        'category': item['category'],
                        'level': item.get('level', '通用'),
                        'reason': f'同属{current_category}分类',
                        'score': 70 + random.randint(0, 20)  # 基础分70-90
                    })
        
        # 按分数排序
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        return recommendations[:top_k]
    
    def recommend_by_level(self, current_level: str, exclude_title: str = None,
                          top_k: int = 5) -> List[Dict[str, Any]]:
        """
        基于层级推荐（学习路径）
        
        Args:
            current_level: 当前层级
            exclude_title: 要排除的知识标题
            top_k: 推荐数量
            
        Returns:
            推荐的知识列表
        """
        # 定义学习路径
        level_order = ['本科', '硕士', '博士']
        
        recommendations = []
        target_levels = []
        
        # 确定推荐的层级
        if current_level in level_order:
            current_index = level_order.index(current_level)
            # 推荐当前层级和下一层级
            target_levels.append(current_level)
            if current_index < len(level_order) - 1:
                target_levels.append(level_order[current_index + 1])
        else:
            target_levels = ['本科', '硕士']
        
        # 查找目标层级的知识
        for category_key, items in knowledge_manager.knowledge_data.items():
            for item in items:
                item_level = item.get('level', '通用')
                if item_level in target_levels:
                    if exclude_title and item['title'] == exclude_title:
                        continue
                    
                    # 计算分数
                    score = 60
                    if item_level == current_level:
                        score += 20  # 同级加分
                        reason = f'同为{current_level}级别'
                    else:
                        score += 30  # 进阶加分
                        reason = f'进阶到{item_level}级别'
                    
                    recommendations.append({
                        'title': item['title'],
                        'category': item['category'],
                        'level': item_level,
                        'reason': reason,
                        'score': score + random.randint(0, 10)
                    })
        
        # 按分数排序
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        return recommendations[:top_k]
    
    def recommend_popular(self, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        推荐热门知识
        
        Args:
            top_k: 推荐数量
            
        Returns:
            推荐的知识列表
        """
        # 如果没有热度数据，返回随机推荐
        if not self.popular_knowledge:
            return self.recommend_random(top_k)
        
        recommendations = []
        
        for title, count in self.popular_knowledge.most_common(top_k):
            # 查找完整信息
            for category_key, items in knowledge_manager.knowledge_data.items():
                for item in items:
                    if item['title'] == title:
                        recommendations.append({
                            'title': item['title'],
                            'category': item['category'],
                            'level': item.get('level', '通用'),
                            'views': count,
                            'reason': f'热门知识（{count}次浏览）',
                            'score': 80 + min(count, 20)
                        })
                        break
        
        return recommendations
    
    def recommend_random(self, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        随机推荐（探索发现）
        
        Args:
            top_k: 推荐数量
            
        Returns:
            推荐的知识列表
        """
        all_knowledge = []
        
        for category_key, items in knowledge_manager.knowledge_data.items():
            for item in items:
                all_knowledge.append({
                    'title': item['title'],
                    'category': item['category'],
                    'level': item.get('level', '通用'),
                    'reason': '随机发现',
                    'score': random.randint(50, 70)
                })
        
        # 随机打乱
        random.shuffle(all_knowledge)
        
        return all_knowledge[:top_k]
    
    def recommend_comprehensive(self, context: Dict[str, Any], top_k: int = 10) -> Dict[str, Any]:
        """
        综合推荐（融合多种策略）
        
        Args:
            context: 上下文信息，包含：
                - current_title: 当前知识标题
                - current_category: 当前分类
                - current_level: 当前层级
                - user_id: 用户ID（可选）
            top_k: 推荐数量
            
        Returns:
            推荐结果，包含多种策略的推荐
        """
        current_title = context.get('current_title')
        current_category = context.get('current_category')
        current_level = context.get('current_level')
        
        recommendations = {
            'similar': [],
            'category': [],
            'level': [],
            'popular': [],
            'random': []
        }
        
        # 1. 相似推荐（如果有当前知识）
        if current_title:
            recommendations['similar'] = self.recommend_similar(
                current_title, top_k=5
            )
        
        # 2. 分类推荐
        if current_category:
            recommendations['category'] = self.recommend_by_category(
                current_category, exclude_title=current_title, top_k=5
            )
        
        # 3. 层级推荐
        if current_level:
            recommendations['level'] = self.recommend_by_level(
                current_level, exclude_title=current_title, top_k=5
            )
        
        # 4. 热门推荐
        recommendations['popular'] = self.recommend_popular(top_k=5)
        
        # 5. 随机推荐
        recommendations['random'] = self.recommend_random(top_k=5)
        
        # 综合排序（去重）
        all_recommendations = []
        seen_titles = set()
        
        # 按优先级添加
        for strategy in ['similar', 'category', 'level', 'popular', 'random']:
            for rec in recommendations[strategy]:
                if rec['title'] not in seen_titles:
                    rec['strategy'] = strategy
                    all_recommendations.append(rec)
                    seen_titles.add(rec['title'])
        
        # 按分数排序
        all_recommendations.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        return {
            'recommendations': all_recommendations[:top_k],
            'by_strategy': recommendations,
            'total': len(all_recommendations),
            'context': context
        }
    
    def record_view(self, title: str, user_id: str = 'anonymous'):
        """
        记录浏览历史
        
        Args:
            title: 知识标题
            user_id: 用户ID
        """
        self.user_history[user_id].append(title)
        self.popular_knowledge[title] += 1
    
    def get_user_interests(self, user_id: str = 'anonymous') -> Dict[str, Any]:
        """
        分析用户兴趣
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户兴趣分析
        """
        history = self.user_history.get(user_id, [])
        
        if not history:
            return {
                'views': 0,
                'categories': {},
                'levels': {},
                'recommendations': self.recommend_random(5)
            }
        
        # 统计分类和层级偏好
        category_counter = Counter()
        level_counter = Counter()
        
        for title in history:
            # 查找知识信息
            for category_key, items in knowledge_manager.knowledge_data.items():
                for item in items:
                    if item['title'] == title:
                        category_counter[item['category']] += 1
                        level_counter[item.get('level', '通用')] += 1
                        break
        
        # 基于兴趣推荐
        favorite_category = category_counter.most_common(1)[0][0] if category_counter else None
        recommendations = []
        
        if favorite_category:
            recommendations = self.recommend_by_category(favorite_category, top_k=5)
        
        return {
            'views': len(history),
            'recent': history[-5:],
            'categories': dict(category_counter),
            'levels': dict(level_counter),
            'favorite_category': favorite_category,
            'recommendations': recommendations
        }


# 全局实例
knowledge_recommender = KnowledgeRecommender()


if __name__ == "__main__":
    print("=== 知识推荐系统测试 ===\n")
    
    # 测试相似推荐
    print("1. 相似推荐测试")
    similar = knowledge_recommender.recommend_similar("水力学基本概念", top_k=3)
    print(f"  找到{len(similar)}个相似知识：")
    for rec in similar:
        print(f"    • {rec['title']} - 相似度{rec['similarity']:.2%}")
    
    # 测试分类推荐
    print(f"\n2. 分类推荐测试")
    category = knowledge_recommender.recommend_by_category("水力学", top_k=3)
    print(f"  找到{len(category)}个同类知识：")
    for rec in category:
        print(f"    • {rec['title']} - {rec['reason']}")
    
    # 测试层级推荐
    print(f"\n3. 层级推荐测试")
    level = knowledge_recommender.recommend_by_level("本科", top_k=3)
    print(f"  找到{len(level)}个相关层级知识：")
    for rec in level:
        print(f"    • {rec['title']} ({rec['level']}) - {rec['reason']}")
    
    # 测试综合推荐
    print(f"\n4. 综合推荐测试")
    context = {
        'current_title': '水力学基本概念',
        'current_category': '水力学',
        'current_level': '本科'
    }
    comprehensive = knowledge_recommender.recommend_comprehensive(context, top_k=5)
    print(f"  综合推荐{len(comprehensive['recommendations'])}个知识：")
    for i, rec in enumerate(comprehensive['recommendations'], 1):
        print(f"    {i}. {rec['title']} - {rec['strategy']} (分数:{rec.get('score', 0):.0f})")
