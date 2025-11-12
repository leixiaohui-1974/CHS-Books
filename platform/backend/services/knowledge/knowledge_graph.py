"""
知识图谱模块 - 构建和分析知识关系网络
"""
import json
from typing import Dict, List, Set, Tuple, Any
from collections import defaultdict
import sys
sys.path.insert(0, '.')

from .vector_store import vector_store
from .knowledge_manager import knowledge_manager


class KnowledgeGraph:
    """知识图谱类 - 分析和可视化知识之间的关系"""
    
    def __init__(self):
        self.graph = defaultdict(list)  # 邻接表表示图
        self.nodes = {}  # 节点信息
        self.edges = []  # 边信息
        self.categories = set()
        self.levels = set()
        
    def build_graph(self) -> Dict[str, Any]:
        """
        构建知识图谱
        
        基于以下关系构建：
        1. 同一分类的知识之间有关联
        2. 同一层级的知识之间有关联
        3. 内容相似度高的知识之间有关联
        """
        print("开始构建知识图谱...")
        
        # 获取所有知识
        all_knowledge = []
        stats = knowledge_manager.get_statistics()
        
        for category_key, items in knowledge_manager.knowledge_data.items():
            for item in items:
                all_knowledge.append({
                    'id': f"{category_key}_{items.index(item)}",
                    'title': item['title'],
                    'category': item['category'],
                    'category_key': category_key,
                    'level': item.get('level', '通用'),
                    'content': item['content'][:200]  # 截取前200字符
                })
                
                # 添加节点
                node_id = f"{category_key}_{items.index(item)}"
                self.nodes[node_id] = {
                    'id': node_id,
                    'title': item['title'],
                    'category': item['category'],
                    'level': item.get('level', '通用'),
                    'type': 'knowledge'
                }
                
                self.categories.add(item['category'])
                self.levels.add(item.get('level', '通用'))
        
        # 构建关系
        self._build_category_relations(all_knowledge)
        self._build_level_relations(all_knowledge)
        self._build_similarity_relations(all_knowledge)
        
        print(f"✓ 知识图谱构建完成")
        print(f"  节点数：{len(self.nodes)}")
        print(f"  边数：{len(self.edges)}")
        print(f"  分类数：{len(self.categories)}")
        print(f"  层级数：{len(self.levels)}")
        
        return self.get_graph_data()
    
    def _build_category_relations(self, knowledge_list: List[Dict]):
        """构建基于分类的关系"""
        category_groups = defaultdict(list)
        for k in knowledge_list:
            category_groups[k['category']].append(k['id'])
        
        # 同一分类内的知识相互关联
        for category, ids in category_groups.items():
            for i, id1 in enumerate(ids):
                for id2 in ids[i+1:i+4]:  # 每个节点最多连接3个同类节点
                    self._add_edge(id1, id2, 'category', category, 0.6)
    
    def _build_level_relations(self, knowledge_list: List[Dict]):
        """构建基于层级的关系"""
        level_groups = defaultdict(list)
        for k in knowledge_list:
            level_groups[k['level']].append(k['id'])
        
        # 同一层级内的知识相互关联（弱关系）
        for level, ids in level_groups.items():
            for i, id1 in enumerate(ids):
                for id2 in ids[i+1:i+3]:  # 每个节点最多连接2个同级节点
                    if not self._edge_exists(id1, id2):
                        self._add_edge(id1, id2, 'level', level, 0.3)
    
    def _build_similarity_relations(self, knowledge_list: List[Dict]):
        """构建基于内容相似度的关系"""
        # 对于每个知识点，找到最相似的3个
        for k in knowledge_list:
            try:
                # 使用向量搜索找到相似知识
                similar = vector_store.search(k['title'], n_results=4)
                
                if similar['ids']:
                    for i, similar_id in enumerate(similar['ids'][0][1:]):  # 跳过自己
                        distance = similar['distances'][0][i+1]
                        if distance < 0.8:  # 相似度阈值
                            # 提取ID
                            metadata = similar['metadatas'][0][i+1]
                            similar_node_id = f"{metadata.get('category_key', 'unknown')}_{metadata.get('index', 0)}"
                            
                            if not self._edge_exists(k['id'], similar_node_id):
                                self._add_edge(
                                    k['id'], 
                                    similar_node_id, 
                                    'similarity', 
                                    f"{(1-distance)*100:.0f}%",
                                    1 - distance
                                )
            except Exception as e:
                continue
    
    def _add_edge(self, source: str, target: str, relation_type: str, label: str, weight: float):
        """添加边"""
        edge = {
            'source': source,
            'target': target,
            'type': relation_type,
            'label': label,
            'weight': weight
        }
        self.edges.append(edge)
        self.graph[source].append(target)
        self.graph[target].append(source)
    
    def _edge_exists(self, node1: str, node2: str) -> bool:
        """检查边是否已存在"""
        for edge in self.edges:
            if (edge['source'] == node1 and edge['target'] == node2) or \
               (edge['source'] == node2 and edge['target'] == node1):
                return True
        return False
    
    def get_graph_data(self) -> Dict[str, Any]:
        """获取图数据（用于可视化）"""
        return {
            'nodes': list(self.nodes.values()),
            'edges': self.edges,
            'stats': {
                'node_count': len(self.nodes),
                'edge_count': len(self.edges),
                'categories': list(self.categories),
                'levels': list(self.levels),
                'avg_degree': len(self.edges) * 2 / len(self.nodes) if self.nodes else 0
            }
        }
    
    def find_knowledge_path(self, start_title: str, end_title: str, max_depth: int = 3) -> List[str]:
        """
        查找两个知识点之间的路径（BFS）
        
        Args:
            start_title: 起始知识标题
            end_title: 目标知识标题
            max_depth: 最大搜索深度
            
        Returns:
            路径列表（节点ID）
        """
        # 查找节点ID
        start_id = None
        end_id = None
        
        for node_id, node in self.nodes.items():
            if node['title'] == start_title:
                start_id = node_id
            if node['title'] == end_title:
                end_id = node_id
        
        if not start_id or not end_id:
            return []
        
        # BFS搜索
        from collections import deque
        
        queue = deque([(start_id, [start_id])])
        visited = {start_id}
        
        while queue:
            current, path = queue.popleft()
            
            if len(path) > max_depth:
                continue
            
            if current == end_id:
                return path
            
            for neighbor in self.graph[current]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return []
    
    def get_related_knowledge(self, title: str, depth: int = 1) -> List[Dict[str, Any]]:
        """
        获取相关知识（指定深度的邻居）
        
        Args:
            title: 知识标题
            depth: 搜索深度
            
        Returns:
            相关知识列表
        """
        # 查找节点ID
        node_id = None
        for nid, node in self.nodes.items():
            if node.get('title') == title:
                node_id = nid
                break
        
        if not node_id or node_id not in self.graph:
            return []
        
        # BFS收集邻居
        from collections import deque
        
        related = []
        queue = deque([(node_id, 0)])
        visited = {node_id}
        
        while queue:
            current, current_depth = queue.popleft()
            
            if current_depth >= depth:
                continue
            
            for neighbor in self.graph[current]:
                if neighbor not in visited and neighbor in self.nodes:
                    visited.add(neighbor)
                    related.append(self.nodes[neighbor])
                    queue.append((neighbor, current_depth + 1))
        
        return related
    
    def get_central_knowledge(self, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        获取中心知识点（度数最高的节点）
        
        Args:
            top_k: 返回前k个
            
        Returns:
            中心知识点列表
        """
        degree_map = {}
        
        for node_id in self.nodes:
            degree_map[node_id] = len(self.graph[node_id])
        
        # 按度数排序
        sorted_nodes = sorted(degree_map.items(), key=lambda x: x[1], reverse=True)
        
        central_knowledge = []
        for node_id, degree in sorted_nodes[:top_k]:
            node_info = self.nodes[node_id].copy()
            node_info['degree'] = degree
            node_info['connections'] = len(self.graph[node_id])
            central_knowledge.append(node_info)
        
        return central_knowledge
    
    def get_category_statistics(self) -> Dict[str, Any]:
        """获取分类统计信息"""
        category_stats = defaultdict(lambda: {'count': 0, 'connections': 0})
        
        for node_id, node in self.nodes.items():
            category = node['category']
            category_stats[category]['count'] += 1
            category_stats[category]['connections'] += len(self.graph[node_id])
        
        # 计算平均连接数
        for category in category_stats:
            count = category_stats[category]['count']
            if count > 0:
                category_stats[category]['avg_connections'] = \
                    category_stats[category]['connections'] / count
        
        return dict(category_stats)
    
    def export_for_visualization(self, format: str = 'json') -> str:
        """
        导出图数据用于可视化
        
        Args:
            format: 'json' 或 'cytoscape' 或 'd3'
            
        Returns:
            格式化的图数据
        """
        if format == 'json':
            return json.dumps(self.get_graph_data(), ensure_ascii=False, indent=2)
        
        elif format == 'cytoscape':
            # Cytoscape.js格式
            elements = []
            
            # 添加节点
            for node_id, node in self.nodes.items():
                elements.append({
                    'data': {
                        'id': node_id,
                        'label': node['title'],
                        'category': node['category'],
                        'level': node['level']
                    }
                })
            
            # 添加边
            for edge in self.edges:
                elements.append({
                    'data': {
                        'source': edge['source'],
                        'target': edge['target'],
                        'label': edge['label'],
                        'weight': edge['weight']
                    }
                })
            
            return json.dumps({'elements': elements}, ensure_ascii=False, indent=2)
        
        elif format == 'd3':
            # D3.js力导向图格式
            d3_data = {
                'nodes': [
                    {
                        'id': node_id,
                        'name': node['title'],
                        'group': node['category'],
                        'level': node['level']
                    }
                    for node_id, node in self.nodes.items()
                ],
                'links': [
                    {
                        'source': edge['source'],
                        'target': edge['target'],
                        'value': edge['weight'],
                        'type': edge['type']
                    }
                    for edge in self.edges
                ]
            }
            return json.dumps(d3_data, ensure_ascii=False, indent=2)
        
        return "{}"


# 全局实例
knowledge_graph = KnowledgeGraph()


if __name__ == "__main__":
    print("=== 知识图谱模块测试 ===\n")
    
    # 构建图谱
    graph_data = knowledge_graph.build_graph()
    
    print(f"\n图谱统计：")
    print(f"  节点：{graph_data['stats']['node_count']}")
    print(f"  边：{graph_data['stats']['edge_count']}")
    print(f"  平均度数：{graph_data['stats']['avg_degree']:.2f}")
    
    # 获取中心知识点
    print(f"\n前5个中心知识点：")
    central = knowledge_graph.get_central_knowledge(top_k=5)
    for i, node in enumerate(central, 1):
        print(f"  {i}. {node['title']} - {node['connections']}个连接")
    
    # 分类统计
    print(f"\n分类连接统计：")
    cat_stats = knowledge_graph.get_category_statistics()
    for category, stats in list(cat_stats.items())[:5]:
        print(f"  {category}: {stats['count']}个知识，平均{stats['avg_connections']:.1f}个连接")
