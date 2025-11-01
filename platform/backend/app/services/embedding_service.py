"""
向量嵌入服务
提供文档向量化和相似度搜索功能
"""

from typing import List, Optional
import hashlib
from loguru import logger

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.warning("sentence-transformers not available, using mock embeddings")


class EmbeddingService:
    """向量嵌入服务"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        初始化嵌入服务
        
        Args:
            model_name: 嵌入模型名称
        """
        self.model_name = model_name
        self.model = None
        self.embedding_dim = 384  # all-MiniLM-L6-v2 的维度
        
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                logger.info(f"Loading embedding model: {model_name}")
                self.model = SentenceTransformer(model_name)
                self.embedding_dim = self.model.get_sentence_embedding_dimension()
                logger.success(f"Embedding model loaded: {model_name} (dim={self.embedding_dim})")
            except Exception as e:
                logger.error(f"Failed to load embedding model: {str(e)}")
                self.model = None
        else:
            logger.warning("Using mock embeddings (install sentence-transformers for real embeddings)")
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        生成文本的嵌入向量
        
        Args:
            text: 输入文本
            
        Returns:
            嵌入向量
        """
        if self.model is not None:
            try:
                # 使用真实模型生成嵌入
                embedding = self.model.encode(text, convert_to_tensor=False)
                return embedding.tolist()
            except Exception as e:
                logger.error(f"Failed to generate embedding: {str(e)}")
                return self._generate_mock_embedding(text)
        else:
            # 使用mock嵌入
            return self._generate_mock_embedding(text)
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        批量生成文本的嵌入向量
        
        Args:
            texts: 文本列表
            
        Returns:
            嵌入向量列表
        """
        if self.model is not None:
            try:
                # 使用真实模型批量生成嵌入
                embeddings = self.model.encode(texts, convert_to_tensor=False, show_progress_bar=True)
                return [emb.tolist() for emb in embeddings]
            except Exception as e:
                logger.error(f"Failed to generate batch embeddings: {str(e)}")
                return [self._generate_mock_embedding(text) for text in texts]
        else:
            # 使用mock嵌入
            return [self._generate_mock_embedding(text) for text in texts]
    
    def _generate_mock_embedding(self, text: str) -> List[float]:
        """
        生成模拟的嵌入向量（用于测试）
        
        Args:
            text: 输入文本
            
        Returns:
            模拟的嵌入向量
        """
        # 使用文本的哈希值生成伪随机但确定性的向量
        hash_bytes = hashlib.md5(text.encode()).digest()
        
        # 将哈希值转换为浮点数向量
        vector = []
        for i in range(0, len(hash_bytes), 2):
            # 将两个字节组合成一个浮点数 (-1 到 1)
            val = (int.from_bytes(hash_bytes[i:i+2], 'little') / 65535.0) * 2 - 1
            vector.append(val)
        
        # 扩展到目标维度
        while len(vector) < self.embedding_dim:
            vector.extend(vector[:self.embedding_dim - len(vector)])
        
        return vector[:self.embedding_dim]
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        计算两个嵌入向量的余弦相似度
        
        Args:
            embedding1: 第一个嵌入向量
            embedding2: 第二个嵌入向量
            
        Returns:
            余弦相似度 (0-1)
        """
        import numpy as np
        
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        # 计算余弦相似度
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        
        # 将结果归一化到 [0, 1]
        return (similarity + 1) / 2


# 全局嵌入服务实例
embedding_service = EmbeddingService()
