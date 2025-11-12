"""
向量数据库管理
"""
import os
from typing import List, Dict, Optional, Any
import chromadb
from chromadb.config import Settings as ChromaSettings


class VectorStore:
    """向量数据库管理类"""
    
    def __init__(self, persist_dir: str = "./chroma_db", collection_name: str = "chs_knowledge"):
        """初始化向量数据库"""
        # 确保持久化目录存在
        os.makedirs(persist_dir, exist_ok=True)
        
        # 初始化ChromaDB客户端（使用PersistentClient）
        self.client = chromadb.PersistentClient(
            path=persist_dir
        )
        
        # 获取或创建集合
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "水利水电水务知识库"}
        )
    
    def add_documents(
        self,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: List[str]
    ) -> List[str]:
        """
        添加文档到向量库
        
        Args:
            documents: 文档文本列表
            metadatas: 元数据列表
            ids: 文档ID列表
            
        Returns:
            文档ID列表
        """
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        return ids
    
    def search(
        self,
        query: str,
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        搜索相关文档
        
        Args:
            query: 查询文本
            n_results: 返回结果数量
            where: 元数据过滤条件
            where_document: 文档内容过滤条件
            
        Returns:
            搜索结果字典
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where,
            where_document=where_document
        )
        return results
    
    def delete_documents(self, ids: List[str]):
        """
        删除文档
        
        Args:
            ids: 要删除的文档ID列表
        """
        self.collection.delete(ids=ids)
    
    def update_documents(
        self,
        ids: List[str],
        documents: Optional[List[str]] = None,
        metadatas: Optional[List[Dict[str, Any]]] = None
    ):
        """
        更新文档
        
        Args:
            ids: 文档ID列表
            documents: 新的文档文本列表
            metadatas: 新的元数据列表
        """
        self.collection.update(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """获取集合统计信息"""
        count = self.collection.count()
        return {
            "name": self.collection.name,
            "count": count,
            "metadata": self.collection.metadata
        }


# 全局向量存储实例
vector_store = VectorStore()
