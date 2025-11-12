"""
知识管理器 - 实现知识的CRUD操作
"""
import json
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime

from .vector_store import vector_store


class KnowledgeManager:
    """知识管理器"""
    
    def __init__(self, knowledge_file: str = "data/knowledge_base.json"):
        """初始化知识管理器"""
        self.knowledge_file = knowledge_file
        self.knowledge_data = self._load_knowledge()
    
    def _load_knowledge(self) -> Dict[str, Any]:
        """加载知识库"""
        try:
            with open(self.knowledge_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载知识库失败：{e}")
            return {}
    
    def _save_knowledge(self) -> bool:
        """保存知识库"""
        try:
            with open(self.knowledge_file, 'w', encoding='utf-8') as f:
                json.dump(self.knowledge_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存知识库失败：{e}")
            return False
    
    def _flatten_knowledge(self) -> List[Dict[str, Any]]:
        """展平知识数据"""
        entries = []
        for category_key, items in self.knowledge_data.items():
            if isinstance(items, list):
                for item in items:
                    item['category_key'] = category_key
                    entries.append(item)
        return entries
    
    def _sync_to_vector_db(self, entry: Dict[str, Any], doc_id: str) -> bool:
        """同步单条知识到向量数据库"""
        try:
            document = f"{entry['title']}\n\n{entry['content']}"
            metadata = {
                "title": entry['title'],
                "category": entry.get('category', 'unknown'),
                "category_key": entry.get('category_key', 'unknown'),
                "level": entry.get('level', 'general'),
                "source_type": entry.get('source_type', 'unknown'),
                "source_name": entry.get('source_name', 'unknown')
            }
            
            vector_store.add_documents(
                documents=[document],
                metadatas=[metadata],
                ids=[doc_id]
            )
            return True
        except Exception as e:
            print(f"同步到向量数据库失败：{e}")
            return False
    
    def add_knowledge(
        self,
        title: str,
        content: str,
        category: str,
        category_key: str,
        level: str = "通用",
        source_type: str = "其他",
        source_name: str = ""
    ) -> Optional[Dict[str, Any]]:
        """
        添加知识
        
        Args:
            title: 知识标题
            content: 知识内容
            category: 分类名称
            category_key: 分类键
            level: 学术层级
            source_type: 来源类型
            source_name: 来源名称
            
        Returns:
            添加的知识条目，失败返回None
        """
        # 创建新知识条目
        new_entry = {
            "title": title,
            "content": content,
            "category": category,
            "category_key": category_key,
            "level": level,
            "source_type": source_type,
            "source_name": source_name,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # 添加到数据结构
        if category_key not in self.knowledge_data:
            self.knowledge_data[category_key] = []
        
        self.knowledge_data[category_key].append(new_entry)
        
        # 保存到文件
        if not self._save_knowledge():
            return None
        
        # 同步到向量数据库
        doc_id = f"kb_{uuid.uuid4().hex[:8]}"
        if not self._sync_to_vector_db(new_entry, doc_id):
            print("警告：向量数据库同步失败")
        
        return new_entry
    
    def update_knowledge(
        self,
        category_key: str,
        index: int,
        **updates
    ) -> Optional[Dict[str, Any]]:
        """
        更新知识
        
        Args:
            category_key: 分类键
            index: 在分类中的索引
            **updates: 要更新的字段
            
        Returns:
            更新后的知识条目，失败返回None
        """
        if category_key not in self.knowledge_data:
            print(f"分类 {category_key} 不存在")
            return None
        
        items = self.knowledge_data[category_key]
        if not isinstance(items, list) or index >= len(items):
            print(f"索引 {index} 超出范围")
            return None
        
        # 更新字段
        entry = items[index]
        for key, value in updates.items():
            if key in ['title', 'content', 'category', 'level', 'source_type', 'source_name']:
                entry[key] = value
        
        entry['updated_at'] = datetime.now().isoformat()
        
        # 保存到文件
        if not self._save_knowledge():
            return None
        
        # 重新同步到向量数据库（简化：删除旧的，添加新的）
        print("提示：向量数据库更新需要重新导入")
        
        return entry
    
    def delete_knowledge(
        self,
        category_key: str,
        index: int
    ) -> bool:
        """
        删除知识
        
        Args:
            category_key: 分类键
            index: 在分类中的索引
            
        Returns:
            是否成功删除
        """
        if category_key not in self.knowledge_data:
            print(f"分类 {category_key} 不存在")
            return False
        
        items = self.knowledge_data[category_key]
        if not isinstance(items, list) or index >= len(items):
            print(f"索引 {index} 超出范围")
            return False
        
        # 删除条目
        deleted = items.pop(index)
        
        # 保存到文件
        if not self._save_knowledge():
            # 回滚
            items.insert(index, deleted)
            return False
        
        print(f"已删除：{deleted['title']}")
        print("提示：向量数据库更新需要重新导入")
        
        return True
    
    def get_knowledge(
        self,
        category_key: str,
        index: int
    ) -> Optional[Dict[str, Any]]:
        """
        获取知识详情
        
        Args:
            category_key: 分类键
            index: 在分类中的索引
            
        Returns:
            知识条目，不存在返回None
        """
        if category_key not in self.knowledge_data:
            return None
        
        items = self.knowledge_data[category_key]
        if not isinstance(items, list) or index >= len(items):
            return None
        
        return items[index]
    
    def list_knowledge(
        self,
        category_key: Optional[str] = None,
        level: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        列出知识
        
        Args:
            category_key: 分类键（可选）
            level: 学术层级（可选）
            
        Returns:
            知识列表
        """
        entries = self._flatten_knowledge()
        
        # 过滤
        if category_key:
            entries = [e for e in entries if e.get('category_key') == category_key]
        
        if level:
            entries = [e for e in entries if e.get('level') == level]
        
        return entries
    
    def search_knowledge(
        self,
        keyword: str,
        category_key: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        关键词搜索知识
        
        Args:
            keyword: 搜索关键词
            category_key: 分类键（可选）
            
        Returns:
            匹配的知识列表
        """
        entries = self._flatten_knowledge()
        
        # 过滤分类
        if category_key:
            entries = [e for e in entries if e.get('category_key') == category_key]
        
        # 关键词匹配
        keyword_lower = keyword.lower()
        results = []
        
        for entry in entries:
            title = entry.get('title', '').lower()
            content = entry.get('content', '').lower()
            
            if keyword_lower in title or keyword_lower in content:
                # 计算匹配度
                score = 0
                if keyword_lower in title:
                    score += 10
                if keyword_lower in content:
                    score += content.count(keyword_lower)
                
                entry_with_score = entry.copy()
                entry_with_score['match_score'] = score
                results.append(entry_with_score)
        
        # 按匹配度排序
        results.sort(key=lambda x: x['match_score'], reverse=True)
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取统计信息
        
        Returns:
            统计数据
        """
        entries = self._flatten_knowledge()
        
        # 总数统计
        total = len(entries)
        
        # 分类统计
        category_stats = {}
        for entry in entries:
            cat = entry.get('category', '未分类')
            category_stats[cat] = category_stats.get(cat, 0) + 1
        
        # 层级统计
        level_stats = {}
        for entry in entries:
            level = entry.get('level', '通用')
            level_stats[level] = level_stats.get(level, 0) + 1
        
        # 来源统计
        source_stats = {}
        for entry in entries:
            source = entry.get('source_type', '其他')
            source_stats[source] = source_stats.get(source, 0) + 1
        
        return {
            'total': total,
            'by_category': category_stats,
            'by_level': level_stats,
            'by_source': source_stats
        }
    
    def import_from_dict(
        self,
        data: Dict[str, List[Dict[str, Any]]]
    ) -> bool:
        """
        从字典导入知识
        
        Args:
            data: 知识数据字典
            
        Returns:
            是否成功
        """
        try:
            self.knowledge_data = data
            return self._save_knowledge()
        except Exception as e:
            print(f"导入失败：{e}")
            return False
    
    def export_to_dict(self) -> Dict[str, Any]:
        """
        导出知识为字典
        
        Returns:
            知识数据字典
        """
        return self.knowledge_data.copy()
    
    def backup(self, backup_file: str) -> bool:
        """
        备份知识库
        
        Args:
            backup_file: 备份文件路径
            
        Returns:
            是否成功
        """
        try:
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(self.knowledge_data, f, ensure_ascii=False, indent=2)
            print(f"备份成功：{backup_file}")
            return True
        except Exception as e:
            print(f"备份失败：{e}")
            return False
    
    def restore(self, backup_file: str) -> bool:
        """
        从备份恢复
        
        Args:
            backup_file: 备份文件路径
            
        Returns:
            是否成功
        """
        try:
            with open(backup_file, 'r', encoding='utf-8') as f:
                self.knowledge_data = json.load(f)
            
            if self._save_knowledge():
                print(f"恢复成功：{backup_file}")
                return True
            return False
        except Exception as e:
            print(f"恢复失败：{e}")
            return False


# 全局实例
knowledge_manager = KnowledgeManager()
