"""
RAG (Retrieval-Augmented Generation) 服务 V2
集成真实的向量存储和嵌入服务
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from loguru import logger
import re

from app.models.knowledge import KnowledgeBase, Document, DocumentChunk, KnowledgeBaseStatus, DocumentType
from app.services.embedding_service import embedding_service
from app.services.vector_store import vector_store
from app.services.openai_service import openai_service


class RAGServiceV2:
    """RAG服务 V2 - 使用真实向量存储"""
    
    def __init__(self):
        self.embedding_service = embedding_service
        self.vector_store = vector_store
        self.openai_service = openai_service
        self.chunk_size = 500  # 每个chunk的字符数
        self.chunk_overlap = 50  # chunk之间的重叠
    
    async def create_knowledge_base(
        self,
        db: AsyncSession,
        name: str,
        description: Optional[str] = None,
        owner_id: Optional[int] = 1  # 默认测试用户
    ) -> KnowledgeBase:
        """
        创建知识库
        
        Args:
            db: 数据库会话
            name: 知识库名称
            description: 知识库描述
            owner_id: 所有者ID
            
        Returns:
            知识库对象
        """
        try:
            kb = KnowledgeBase(
                name=name,
                description=description,
                owner_id=owner_id,
                embedding_model="all-MiniLM-L6-v2",
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                status=KnowledgeBaseStatus.ACTIVE,
                document_count=0,
                total_chunks=0
            )
            
            db.add(kb)
            await db.commit()
            await db.refresh(kb)
            
            # 创建向量集合
            collection_name = f"kb_{kb.id}"
            self.vector_store.create_collection(
                collection_name=collection_name,
                metadata={"knowledge_base_id": kb.id, "name": name}
            )
            
            logger.success(f"Created knowledge base: {name} (id={kb.id})")
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
        doc_type: DocumentType = DocumentType.TEXT
    ) -> Document:
        """
        上传文档到知识库
        
        Args:
            db: 数据库会话
            knowledge_base_id: 知识库ID
            title: 文档标题
            content: 文档内容
            doc_type: 文档类型
            
        Returns:
            文档对象
        """
        try:
            # 验证知识库存在
            kb = await db.get(KnowledgeBase, knowledge_base_id)
            if not kb:
                raise ValueError(f"Knowledge base {knowledge_base_id} not found")
            
            # 创建文档
            doc = Document(
                knowledge_base_id=knowledge_base_id,
                title=title,
                content=content,
                doc_type=doc_type,
                file_size=len(content.encode('utf-8')),
                chunk_count=0
            )
            
            db.add(doc)
            await db.flush()  # 获取doc.id但不提交
            
            # 分割文档为chunks
            chunks = self._split_text(content)
            logger.info(f"Split document into {len(chunks)} chunks")
            
            # 批量生成嵌入向量
            chunk_texts = [chunk for chunk in chunks]
            embeddings = self.embedding_service.generate_embeddings_batch(chunk_texts)
            
            # 保存chunks到数据库和向量存储
            collection_name = f"kb_{knowledge_base_id}"
            chunk_ids = []
            chunk_documents = []
            chunk_embeddings = []
            chunk_metadatas = []
            
            for i, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
                chunk = DocumentChunk(
                    document_id=doc.id,
                    content=chunk_text,
                    chunk_index=i
                )
                db.add(chunk)
                await db.flush()
                
                # 准备向量存储数据
                chunk_ids.append(f"chunk_{chunk.id}")
                chunk_documents.append(chunk_text)
                chunk_embeddings.append(embedding)
                chunk_metadatas.append({
                    "chunk_id": chunk.id,
                    "document_id": doc.id,
                    "document_title": title,
                    "chunk_index": i,
                    "knowledge_base_id": knowledge_base_id
                })
            
            # 批量添加到向量存储
            self.vector_store.add_documents(
                collection_name=collection_name,
                documents=chunk_documents,
                embeddings=chunk_embeddings,
                metadatas=chunk_metadatas,
                ids=chunk_ids
            )
            
            # 更新文档统计
            doc.chunk_count = len(chunks)
            
            # 更新知识库统计
            kb.document_count += 1
            kb.total_chunks += len(chunks)
            
            await db.commit()
            await db.refresh(doc)
            
            logger.success(f"Uploaded document: {title} ({len(chunks)} chunks)")
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
        """
        在知识库中搜索相关内容
        
        Args:
            db: 数据库会话
            knowledge_base_id: 知识库ID
            query: 查询文本
            top_k: 返回结果数量
            
        Returns:
            搜索结果列表
        """
        try:
            # 生成查询向量
            query_embedding = self.embedding_service.generate_embedding(query)
            
            # 在向量存储中搜索
            collection_name = f"kb_{knowledge_base_id}"
            results = self.vector_store.search(
                collection_name=collection_name,
                query_embedding=query_embedding,
                top_k=top_k,
                filter_metadata={"knowledge_base_id": knowledge_base_id}
            )
            
            # 格式化结果
            formatted_results = []
            for result in results:
                metadata = result.get("metadata", {})
                formatted_results.append({
                    "chunk_id": metadata.get("chunk_id"),
                    "document_id": metadata.get("document_id"),
                    "document_title": metadata.get("document_title"),
                    "content": result.get("document"),
                    "similarity": 1 - result.get("distance", 0),  # 转换距离为相似度
                    "chunk_index": metadata.get("chunk_index")
                })
            
            logger.info(f"Found {len(formatted_results)} relevant chunks for query: {query[:50]}...")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Failed to search knowledge: {str(e)}")
            return []
    
    async def ask_question(
        self,
        db: AsyncSession,
        knowledge_base_id: int,
        question: str,
        top_k: int = 3
    ) -> Dict[str, Any]:
        """
        基于知识库回答问题（RAG）
        
        Args:
            db: 数据库会话
            knowledge_base_id: 知识库ID
            question: 问题
            top_k: 使用的上下文数量
            
        Returns:
            回答结果
        """
        try:
            # 搜索相关内容
            search_results = await self.search_knowledge(
                db=db,
                knowledge_base_id=knowledge_base_id,
                query=question,
                top_k=top_k
            )
            
            if not search_results:
                return {
                    "answer": "抱歉，我在知识库中没有找到相关信息。",
                    "sources": [],
                    "confidence": 0.0
                }
            
            # 构建上下文
            context_parts = []
            sources = []
            
            for i, result in enumerate(search_results):
                context_parts.append(f"[文档{i+1}] {result['content']}")
                sources.append({
                    "document_id": result["document_id"],
                    "document_title": result["document_title"],
                    "chunk_index": result["chunk_index"],
                    "similarity": result["similarity"]
                })
            
            context = "\n\n".join(context_parts)
            
            # 使用OpenAI生成回答
            llm_response = await self.openai_service.generate_answer(
                question=question,
                context=context,
                max_tokens=500,
                temperature=0.7
            )
            
            # 计算置信度（基于相似度）
            confidence = sum(s["similarity"] for s in sources) / len(sources) if sources else 0.0
            
            return {
                "answer": llm_response["answer"],
                "sources": sources,
                "confidence": confidence,
                "model": llm_response.get("model", "unknown"),
                "tokens_used": llm_response.get("tokens_used", 0)
            }
            
        except Exception as e:
            logger.error(f"Failed to answer question: {str(e)}")
            return {
                "answer": f"处理问题时出错: {str(e)}",
                "sources": [],
                "confidence": 0.0
            }
    
    def _split_text(self, text: str) -> List[str]:
        """
        将文本分割成chunks
        
        Args:
            text: 输入文本
            
        Returns:
            chunk列表
        """
        # 按段落分割
        paragraphs = re.split(r'\n\s*\n', text)
        
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # 如果当前chunk加上新段落不超过限制，则添加
            if len(current_chunk) + len(para) + 2 <= self.chunk_size:
                if current_chunk:
                    current_chunk += "\n\n" + para
                else:
                    current_chunk = para
            else:
                # 否则保存当前chunk，开始新chunk
                if current_chunk:
                    chunks.append(current_chunk)
                
                # 如果单个段落就超过限制，需要进一步分割
                if len(para) > self.chunk_size:
                    # 按句子分割
                    sentences = re.split(r'[。！？；]', para)
                    temp_chunk = ""
                    
                    for sentence in sentences:
                        sentence = sentence.strip()
                        if not sentence:
                            continue
                        
                        if len(temp_chunk) + len(sentence) + 1 <= self.chunk_size:
                            if temp_chunk:
                                temp_chunk += "。" + sentence
                            else:
                                temp_chunk = sentence
                        else:
                            if temp_chunk:
                                chunks.append(temp_chunk + "。")
                            temp_chunk = sentence
                    
                    current_chunk = temp_chunk
                else:
                    current_chunk = para
        
        # 添加最后一个chunk
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks if chunks else [text]
    
    def _generate_answer_simple(self, question: str, context: str) -> str:
        """
        简单的答案生成（模板方法）
        实际生产中应该调用OpenAI或其他LLM API
        
        Args:
            question: 问题
            context: 上下文
            
        Returns:
            答案
        """
        # 简单的提取式回答
        lines = context.split('\n')
        relevant_lines = [line for line in lines if line.strip() and not line.startswith('[文档')]
        
        if not relevant_lines:
            return "根据知识库内容，我无法直接回答这个问题。"
        
        # 返回前3个最相关的句子
        answer_parts = relevant_lines[:3]
        answer = "\n\n".join(answer_parts)
        
        return f"根据知识库内容：\n\n{answer}\n\n(注：这是基于检索的简单回答，实际部署时会使用AI模型生成更完善的答案)"
    
    async def get_knowledge_bases(self, db: AsyncSession) -> List[KnowledgeBase]:
        """获取所有知识库"""
        result = await db.execute(select(KnowledgeBase))
        return result.scalars().all()
    
    async def get_knowledge_base(self, db: AsyncSession, knowledge_base_id: int) -> Optional[KnowledgeBase]:
        """获取单个知识库"""
        return await db.get(KnowledgeBase, knowledge_base_id)
    
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
            return False


# 全局RAG服务实例
rag_service_v2 = RAGServiceV2()
