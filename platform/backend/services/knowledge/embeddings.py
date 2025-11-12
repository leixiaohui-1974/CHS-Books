"""
文本嵌入服务
"""
import os
from typing import List
from abc import ABC, abstractmethod
try:
    import openai
except ImportError:
    openai = None


class EmbeddingService(ABC):
    """嵌入服务抽象基类"""
    
    @abstractmethod
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """将文本列表转换为向量"""
        pass
    
    @abstractmethod
    def embed_query(self, query: str) -> List[float]:
        """将查询文本转换为向量"""
        pass


class OpenAIEmbedding(EmbeddingService):
    """OpenAI嵌入服务"""
    
    def __init__(self, api_key: str = None):
        """初始化OpenAI客户端"""
        if openai is None:
            raise ImportError("openai package is not installed")
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        openai.api_key = self.api_key
        self.model = "text-embedding-ada-002"
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """将文本列表转换为向量"""
        response = openai.embeddings.create(
            input=texts,
            model=self.model
        )
        return [item.embedding for item in response.data]
    
    def embed_query(self, query: str) -> List[float]:
        """将查询文本转换为向量"""
        return self.embed_texts([query])[0]


class LocalEmbedding(EmbeddingService):
    """本地嵌入服务（使用sentence-transformers）"""
    
    def __init__(self, model_name: str = None):
        """初始化本地模型"""
        from sentence_transformers import SentenceTransformer
        
        # 使用默认的中文模型
        self.model_name = model_name or os.getenv("LOCAL_EMBEDDING_MODEL", "paraphrase-multilingual-MiniLM-L12-v2")
        print(f"Loading local embedding model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """将文本列表转换为向量"""
        embeddings = self.model.encode(texts, show_progress_bar=False)
        return embeddings.tolist()
    
    def embed_query(self, query: str) -> List[float]:
        """将查询文本转换为向量"""
        return self.embed_texts([query])[0]


def get_embedding_service(embedding_type: str = "local") -> EmbeddingService:
    """获取嵌入服务实例"""
    embedding_type = embedding_type or os.getenv("EMBEDDING_MODEL", "local")
    if embedding_type == "openai":
        return OpenAIEmbedding()
    elif embedding_type == "local":
        return LocalEmbedding()
    else:
        raise ValueError(f"Unknown embedding model: {embedding_type}")
