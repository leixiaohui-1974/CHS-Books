"""
RAG (Retrieval-Augmented Generation) 服务
知识库检索增强生成系统
"""

import os
import hashlib
import random
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from loguru import logger

from app.models.knowledge import KnowledgeBase, Document, DocumentChunk, KnowledgeBaseStatus, DocumentType


class RAGService:
    """RAG服务 - 知识库检索增强生成"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
        self.chunk_size = int(os.getenv("CHUNK_SIZE", "1000"))
        self.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "200"))
    
    async def create_knowledge_base(
        self,
        db: AsyncSession,
        name: str,
        description: Optional[str],
        owner_id: int
    ) -> KnowledgeBase:
        """创建知识库"""
        try:
            kb = KnowledgeBase(
                name=name,
                description=description,
                owner_id=owner_id,
                embedding_model=self.embedding_model,
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                status=KnowledgeBaseStatus.ACTIVE
            )
            
            db.add(kb)
            await db.commit()
            await db.refresh(kb)
            
            logger.info(f"Created knowledge base: {kb.id} - {kb.name}")
            return kb
            
        except Exception as e:
            logger.error(f"Failed to create knowledge base: {str(e)}")
            await db.rollback()
            raise
    
    async def upload_document(
        self,
        db: AsyncSession,
        knowledge_base_id: int,
        title: str,
        content: str,
        doc_type: DocumentType = DocumentType.TEXT,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Document:
        """上传文档到知识库"""
        try:
            # 检查知识库是否存在
            kb = await db.get(KnowledgeBase, knowledge_base_id)
            if not kb:
                raise ValueError(f"Knowledge base {knowledge_base_id} not found")
            
            # 计算文件哈希
            file_hash = hashlib.sha256(content.encode()).hexdigest()
            
            # 创建文档
            doc = Document(
                knowledge_base_id=knowledge_base_id,
                title=title,
                content=content,
                doc_type=doc_type,
                file_size=len(content.encode()),
                file_hash=file_hash,
                metadata=metadata or {}
            )
            
            db.add(doc)
            await db.flush()  # 获取doc.id但不提交
            
            # 分块处理
            chunks = self._split_text(content)
            for i, chunk_text in enumerate(chunks):
                # 生成向量（这里使用模拟）
                vector_id = f"{doc.id}_chunk_{i}"
                embedding = self._generate_mock_embedding(chunk_text)
                
                chunk = DocumentChunk(
                    document_id=doc.id,
                    chunk_index=i,
                    content=chunk_text,
                    vector_id=vector_id,
                    embedding=embedding,
                    metadata={"length": len(chunk_text)}
                )
                db.add(chunk)
            
            # 更新文档和知识库统计
            doc.chunk_count = len(chunks)
            kb.document_count += 1
            kb.total_chunks += len(chunks)
            
            await db.commit()
            await db.refresh(doc)
            
            logger.info(f"Uploaded document: {doc.id} - {doc.title} ({len(chunks)} chunks)")
            return doc
            
        except Exception as e:
            logger.error(f"Failed to upload document: {str(e)}")
            await db.rollback()
            raise
    
    async def search_knowledge(
        self,
        db: AsyncSession,
        knowledge_base_id: int,
        query: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """搜索知识库"""
        try:
            # 生成查询向量（模拟）
            query_embedding = self._generate_mock_embedding(query)
            
            # 获取所有块（在实际应用中应该使用向量数据库）
            result = await db.execute(
                select(DocumentChunk, Document)
                .join(Document, Document.id == DocumentChunk.document_id)
                .where(Document.knowledge_base_id == knowledge_base_id)
            )
            chunks = result.all()
            
            # 计算相似度（模拟）
            scored_chunks = []
            for chunk, doc in chunks:
                similarity = self._calculate_similarity(query_embedding, chunk.embedding or [])
                scored_chunks.append({
                    "chunk_id": chunk.id,
                    "document_id": doc.id,
                    "document_title": doc.title,
                    "content": chunk.content,
                    "similarity": similarity,
                    "metadata": chunk.metadata
                })
            
            # 按相似度排序并返回top_k
            scored_chunks.sort(key=lambda x: x["similarity"], reverse=True)
            results = scored_chunks[:top_k]
            
            logger.info(f"Searched knowledge base {knowledge_base_id} with query: {query[:50]}...")
            return results
            
        except Exception as e:
            logger.error(f"Failed to search knowledge: {str(e)}")
            raise
    
    async def ask_question(
        self,
        db: AsyncSession,
        knowledge_base_id: int,
        question: str,
        context_size: int = 3
    ) -> Dict[str, Any]:
        """RAG问答 - 结合检索和生成"""
        try:
            # 1. 检索相关知识
            relevant_chunks = await self.search_knowledge(
                db, knowledge_base_id, question, top_k=context_size
            )
            
            if not relevant_chunks:
                return {
                    "answer": "抱歉，我在知识库中没有找到相关信息。",
                    "sources": [],
                    "confidence": 0.0
                }
            
            # 2. 构建上下文
            context = "\n\n".join([
                f"文档：{chunk['document_title']}\n内容：{chunk['content']}"
                for chunk in relevant_chunks
            ])
            
            # 3. 生成回答（这里使用模拟）
            answer = self._generate_mock_answer(question, context)
            
            # 4. 返回结果
            return {
                "answer": answer,
                "sources": [
                    {
                        "document_id": chunk["document_id"],
                        "document_title": chunk["document_title"],
                        "similarity": chunk["similarity"]
                    }
                    for chunk in relevant_chunks
                ],
                "confidence": relevant_chunks[0]["similarity"] if relevant_chunks else 0.0
            }
            
        except Exception as e:
            logger.error(f"Failed to answer question: {str(e)}")
            raise
    
    async def get_knowledge_bases(
        self,
        db: AsyncSession,
        owner_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 10
    ) -> List[KnowledgeBase]:
        """获取知识库列表"""
        try:
            query = select(KnowledgeBase)
            
            if owner_id:
                query = query.where(KnowledgeBase.owner_id == owner_id)
            
            query = query.offset(skip).limit(limit).order_by(KnowledgeBase.created_at.desc())
            
            result = await db.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Failed to get knowledge bases: {str(e)}")
            raise
    
    async def get_knowledge_base_stats(
        self,
        db: AsyncSession,
        knowledge_base_id: int
    ) -> Dict[str, Any]:
        """获取知识库统计"""
        try:
            kb = await db.get(KnowledgeBase, knowledge_base_id)
            if not kb:
                raise ValueError(f"Knowledge base {knowledge_base_id} not found")
            
            # 获取文档统计
            doc_result = await db.execute(
                select(
                    func.count(Document.id).label("total_docs"),
                    func.sum(Document.file_size).label("total_size"),
                    func.avg(Document.view_count).label("avg_views")
                )
                .where(Document.knowledge_base_id == knowledge_base_id)
            )
            doc_stats = doc_result.first()
            
            return {
                "knowledge_base_id": kb.id,
                "name": kb.name,
                "status": kb.status,
                "document_count": kb.document_count,
                "total_chunks": kb.total_chunks,
                "total_size": doc_stats.total_size or 0,
                "average_views": round(doc_stats.avg_views or 0, 2),
                "created_at": kb.created_at,
                "updated_at": kb.updated_at
            }
            
        except Exception as e:
            logger.error(f"Failed to get knowledge base stats: {str(e)}")
            raise
    
    async def delete_document(
        self,
        db: AsyncSession,
        document_id: int,
        knowledge_base_id: int
    ) -> bool:
        """删除文档"""
        try:
            doc = await db.get(Document, document_id)
            if not doc or doc.knowledge_base_id != knowledge_base_id:
                raise ValueError(f"Document {document_id} not found in knowledge base {knowledge_base_id}")
            
            # 更新知识库统计
            kb = await db.get(KnowledgeBase, knowledge_base_id)
            if kb:
                kb.document_count = max(0, kb.document_count - 1)
                kb.total_chunks = max(0, kb.total_chunks - doc.chunk_count)
            
            # 删除文档（级联删除chunks）
            await db.delete(doc)
            await db.commit()
            
            logger.info(f"Deleted document: {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete document: {str(e)}")
            await db.rollback()
            raise
    
    def _split_text(self, text: str) -> List[str]:
        """分割文本为块"""
        chunks = []
        text_length = len(text)
        
        for i in range(0, text_length, self.chunk_size - self.chunk_overlap):
            chunk = text[i:i + self.chunk_size]
            if chunk:
                chunks.append(chunk)
        
        return chunks
    
    def _generate_mock_embedding(self, text: str) -> List[float]:
        """生成模拟向量"""
        # 实际应用中应该调用OpenAI API生成真实向量
        random.seed(hash(text) % 2**32)
        return [random.random() for _ in range(64)]  # 使用64维简化版本
    
    def _calculate_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """计算余弦相似度"""
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return random.random() * 0.5  # 模拟低相似度
        
        # 简单的点积相似度
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = sum(a * a for a in vec1) ** 0.5
        norm2 = sum(b * b for b in vec2) ** 0.5
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def _generate_mock_answer(self, question: str, context: str) -> str:
        """生成模拟回答"""
        # 实际应用中应该调用LLM API生成真实回答
        return f"""基于知识库中的内容，针对您的问题"{question}"，我找到了以下相关信息：

{context[:500]}...

这是一个模拟回答。在实际应用中，这里会使用GPT等大语言模型根据检索到的知识生成精准的答案。

要启用真实的AI回答功能，请配置OPENAI_API_KEY环境变量。"""


# 创建全局实例
rag_service = RAGService()
