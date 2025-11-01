"""
向量存储服务
使用ChromaDB进行向量存储和检索
"""

from typing import List, Dict, Any, Optional
from loguru import logger
import uuid

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    logger.warning("chromadb not available, using in-memory storage")


class VectorStore:
    """向量存储服务"""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        初始化向量存储
        
        Args:
            persist_directory: 持久化目录
        """
        self.persist_directory = persist_directory
        self.client = None
        self.collections = {}
        
        # 内存存储（后备方案）
        self.memory_store: Dict[str, List[Dict[str, Any]]] = {}
        
        if CHROMADB_AVAILABLE:
            try:
                logger.info(f"Initializing ChromaDB: {persist_directory}")
                self.client = chromadb.Client(Settings(
                    chroma_db_impl="duckdb+parquet",
                    persist_directory=persist_directory,
                    anonymized_telemetry=False
                ))
                logger.success("ChromaDB initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize ChromaDB: {str(e)}")
                self.client = None
        else:
            logger.warning("Using in-memory vector storage (install chromadb for persistence)")
    
    def create_collection(self, collection_name: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        创建向量集合
        
        Args:
            collection_name: 集合名称
            metadata: 元数据
            
        Returns:
            是否成功
        """
        if self.client is not None:
            try:
                # 检查集合是否已存在
                try:
                    collection = self.client.get_collection(collection_name)
                    logger.info(f"Collection already exists: {collection_name}")
                    self.collections[collection_name] = collection
                    return True
                except Exception:
                    # 集合不存在，创建新集合
                    collection = self.client.create_collection(
                        name=collection_name,
                        metadata=metadata or {}
                    )
                    self.collections[collection_name] = collection
                    logger.success(f"Collection created: {collection_name}")
                    return True
            except Exception as e:
                logger.error(f"Failed to create collection: {str(e)}")
                return False
        else:
            # 使用内存存储
            if collection_name not in self.memory_store:
                self.memory_store[collection_name] = []
                logger.info(f"In-memory collection created: {collection_name}")
            return True
    
    def add_documents(
        self,
        collection_name: str,
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> bool:
        """
        添加文档到集合
        
        Args:
            collection_name: 集合名称
            documents: 文档文本列表
            embeddings: 嵌入向量列表
            metadatas: 元数据列表
            ids: 文档ID列表
            
        Returns:
            是否成功
        """
        if len(documents) != len(embeddings):
            logger.error("Documents and embeddings length mismatch")
            return False
        
        # 生成ID（如果未提供）
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in range(len(documents))]
        
        # 准备元数据
        if metadatas is None:
            metadatas = [{} for _ in range(len(documents))]
        
        if self.client is not None:
            try:
                collection = self.collections.get(collection_name)
                if collection is None:
                    logger.error(f"Collection not found: {collection_name}")
                    return False
                
                # 添加到ChromaDB
                collection.add(
                    documents=documents,
                    embeddings=embeddings,
                    metadatas=metadatas,
                    ids=ids
                )
                
                logger.success(f"Added {len(documents)} documents to {collection_name}")
                return True
            except Exception as e:
                logger.error(f"Failed to add documents: {str(e)}")
                return False
        else:
            # 使用内存存储
            if collection_name not in self.memory_store:
                self.memory_store[collection_name] = []
            
            for i in range(len(documents)):
                self.memory_store[collection_name].append({
                    "id": ids[i],
                    "document": documents[i],
                    "embedding": embeddings[i],
                    "metadata": metadatas[i]
                })
            
            logger.info(f"Added {len(documents)} documents to in-memory store")
            return True
    
    def search(
        self,
        collection_name: str,
        query_embedding: List[float],
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        搜索相似文档
        
        Args:
            collection_name: 集合名称
            query_embedding: 查询向量
            top_k: 返回结果数量
            filter_metadata: 元数据过滤条件
            
        Returns:
            搜索结果列表
        """
        if self.client is not None:
            try:
                collection = self.collections.get(collection_name)
                if collection is None:
                    logger.error(f"Collection not found: {collection_name}")
                    return []
                
                # 在ChromaDB中搜索
                results = collection.query(
                    query_embeddings=[query_embedding],
                    n_results=top_k,
                    where=filter_metadata
                )
                
                # 格式化结果
                formatted_results = []
                if results and 'documents' in results and results['documents']:
                    for i in range(len(results['documents'][0])):
                        formatted_results.append({
                            "id": results['ids'][0][i],
                            "document": results['documents'][0][i],
                            "distance": results['distances'][0][i] if 'distances' in results else 0,
                            "metadata": results['metadatas'][0][i] if 'metadatas' in results else {}
                        })
                
                return formatted_results
            except Exception as e:
                logger.error(f"Failed to search: {str(e)}")
                return []
        else:
            # 使用内存存储搜索
            return self._memory_search(collection_name, query_embedding, top_k, filter_metadata)
    
    def _memory_search(
        self,
        collection_name: str,
        query_embedding: List[float],
        top_k: int,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """内存搜索实现"""
        import numpy as np
        
        if collection_name not in self.memory_store:
            return []
        
        documents = self.memory_store[collection_name]
        
        # 应用元数据过滤
        if filter_metadata:
            documents = [
                doc for doc in documents
                if all(doc.get("metadata", {}).get(k) == v for k, v in filter_metadata.items())
            ]
        
        # 计算相似度
        query_vec = np.array(query_embedding)
        similarities = []
        
        for doc in documents:
            doc_vec = np.array(doc["embedding"])
            similarity = np.dot(query_vec, doc_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(doc_vec))
            similarities.append((doc, similarity))
        
        # 排序并返回top_k
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        results = []
        for doc, similarity in similarities[:top_k]:
            results.append({
                "id": doc["id"],
                "document": doc["document"],
                "distance": 1 - similarity,  # 转换为距离
                "metadata": doc["metadata"]
            })
        
        return results
    
    def delete_collection(self, collection_name: str) -> bool:
        """
        删除集合
        
        Args:
            collection_name: 集合名称
            
        Returns:
            是否成功
        """
        if self.client is not None:
            try:
                self.client.delete_collection(collection_name)
                if collection_name in self.collections:
                    del self.collections[collection_name]
                logger.success(f"Collection deleted: {collection_name}")
                return True
            except Exception as e:
                logger.error(f"Failed to delete collection: {str(e)}")
                return False
        else:
            # 删除内存存储
            if collection_name in self.memory_store:
                del self.memory_store[collection_name]
                logger.info(f"In-memory collection deleted: {collection_name}")
            return True
    
    def get_collection_count(self, collection_name: str) -> int:
        """
        获取集合中的文档数量
        
        Args:
            collection_name: 集合名称
            
        Returns:
            文档数量
        """
        if self.client is not None:
            try:
                collection = self.collections.get(collection_name)
                if collection is None:
                    return 0
                return collection.count()
            except Exception as e:
                logger.error(f"Failed to get collection count: {str(e)}")
                return 0
        else:
            return len(self.memory_store.get(collection_name, []))


# 全局向量存储实例
vector_store = VectorStore()
