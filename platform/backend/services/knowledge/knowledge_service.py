"""
知识管理服务
"""
import uuid
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from .models import KnowledgeEntry, Category, Standard, AcademicLevel, SourceType
from .vector_store import vector_store
from .text_processor import text_processor
# from .document_parser import  # Optional module document_parser
from .embeddings import get_embedding_service


class KnowledgeService:
    """知识管理服务"""
    
    def __init__(self):
        """初始化"""
        self.embedding_service = None
    
    def _get_embedding_service(self):
        """延迟加载嵌入服务"""
        if self.embedding_service is None:
            self.embedding_service = get_embedding_service()
        return self.embedding_service
    
    def add_knowledge_from_text(
        self,
        db: Session,
        title: str,
        content: str,
        category_id: str,
        level: AcademicLevel = AcademicLevel.GENERAL,
        source_type: SourceType = SourceType.OTHER,
        source_name: str = "",
        author: str = "",
        **kwargs
    ) -> KnowledgeEntry:
        """
        从文本添加知识条目
        
        Args:
            db: 数据库会话
            title: 标题
            content: 内容
            category_id: 分类ID
            level: 学术层级
            source_type: 来源类型
            source_name: 来源名称
            author: 作者
            
        Returns:
            知识条目对象
        """
        # 清理文本
        cleaned_content = text_processor.clean_text(content)
        
        # 生成摘要
        summary = text_processor.generate_summary(cleaned_content)
        
        # 提取关键词
        keywords = text_processor.extract_keywords(cleaned_content)
        
        # 创建知识条目
        knowledge = KnowledgeEntry(
            title=title,
            content=cleaned_content,
            summary=summary,
            category_id=category_id,
            level=level,
            source_type=source_type,
            source_name=source_name,
            author=author,
            keywords=keywords,
            **kwargs
        )
        
        db.add(knowledge)
        db.flush()
        
        # 文本切块
        chunks = text_processor.split_text(cleaned_content)
        
        # 向量化并存储
        vector_ids = self._store_chunks_to_vector(
            knowledge_id=knowledge.id,
            title=title,
            chunks=chunks,
            metadata={
                'category_id': category_id,
                'level': level.value,
                'source_type': source_type.value,
            }
        )
        
        # 保存向量ID
        knowledge.vector_ids = vector_ids
        db.commit()
        db.refresh(knowledge)
        
        return knowledge
    
    def add_knowledge_from_file(
        self,
        db: Session,
        file_path: str,
        category_id: str,
        level: AcademicLevel = AcademicLevel.GENERAL,
        source_type: SourceType = SourceType.OTHER,
        **kwargs
    ) -> KnowledgeEntry:
        """
        从文件添加知识条目
        
        Args:
            db: 数据库会话
            file_path: 文件路径
            category_id: 分类ID
            level: 学术层级
            source_type: 来源类型
            
        Returns:
            知识条目对象
        """
        # 解析文档
        parsed = document_parser.parse(file_path)
        
        # 从元数据中提取信息
        metadata = parsed.get('metadata', {})
        title = metadata.get('title', parsed.get('file_name', 'Untitled'))
        author = metadata.get('author', '')
        
        # 添加知识
        return self.add_knowledge_from_text(
            db=db,
            title=title,
            content=parsed['text'],
            category_id=category_id,
            level=level,
            source_type=source_type,
            source_name=parsed.get('file_name', ''),
            author=author,
            **kwargs
        )
    
    def _store_chunks_to_vector(
        self,
        knowledge_id: str,
        title: str,
        chunks: List[str],
        metadata: Dict[str, Any]
    ) -> List[str]:
        """
        将文本块存储到向量数据库
        
        Args:
            knowledge_id: 知识条目ID
            title: 标题
            chunks: 文本块列表
            metadata: 元数据
            
        Returns:
            向量ID列表
        """
        if not chunks:
            return []
        
        # 生成向量ID
        vector_ids = [f"{knowledge_id}_chunk_{i}" for i in range(len(chunks))]
        
        # 准备元数据
        metadatas = []
        for i, chunk in enumerate(chunks):
            chunk_metadata = {
                **metadata,
                'knowledge_id': knowledge_id,
                'title': title,
                'chunk_index': i,
                'total_chunks': len(chunks),
            }
            metadatas.append(chunk_metadata)
        
        # 添加到向量库
        vector_store.add_documents(
            documents=chunks,
            metadatas=metadatas,
            ids=vector_ids
        )
        
        return vector_ids
    
    def update_knowledge(
        self,
        db: Session,
        knowledge_id: str,
        **update_data
    ) -> Optional[KnowledgeEntry]:
        """
        更新知识条目
        
        Args:
            db: 数据库会话
            knowledge_id: 知识条目ID
            update_data: 更新数据
            
        Returns:
            更新后的知识条目对象
        """
        knowledge = db.query(KnowledgeEntry).filter(
            KnowledgeEntry.id == knowledge_id
        ).first()
        
        if not knowledge:
            return None
        
        # 如果更新了内容，需要重新处理向量
        if 'content' in update_data:
            # 删除旧的向量
            if knowledge.vector_ids:
                vector_store.delete_documents(knowledge.vector_ids)
            
            # 重新切块和向量化
            chunks = text_processor.split_text(update_data['content'])
            vector_ids = self._store_chunks_to_vector(
                knowledge_id=knowledge.id,
                title=update_data.get('title', knowledge.title),
                chunks=chunks,
                metadata={
                    'category_id': knowledge.category_id,
                    'level': knowledge.level.value,
                    'source_type': knowledge.source_type.value,
                }
            )
            update_data['vector_ids'] = vector_ids
            
            # 重新生成摘要和关键词
            if 'summary' not in update_data:
                update_data['summary'] = text_processor.generate_summary(
                    update_data['content']
                )
            if 'keywords' not in update_data:
                update_data['keywords'] = text_processor.extract_keywords(
                    update_data['content']
                )
        
        # 更新字段
        for key, value in update_data.items():
            if hasattr(knowledge, key):
                setattr(knowledge, key, value)
        
        db.commit()
        db.refresh(knowledge)
        
        return knowledge
    
    def delete_knowledge(self, db: Session, knowledge_id: str) -> bool:
        """
        删除知识条目
        
        Args:
            db: 数据库会话
            knowledge_id: 知识条目ID
            
        Returns:
            是否删除成功
        """
        knowledge = db.query(KnowledgeEntry).filter(
            KnowledgeEntry.id == knowledge_id
        ).first()
        
        if not knowledge:
            return False
        
        # 删除向量数据
        if knowledge.vector_ids:
            vector_store.delete_documents(knowledge.vector_ids)
        
        # 删除数据库记录
        db.delete(knowledge)
        db.commit()
        
        return True
    
    def search_knowledge(
        self,
        db: Session,
        query: str,
        category_id: Optional[str] = None,
        level: Optional[AcademicLevel] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        搜索知识
        
        Args:
            db: 数据库会话
            query: 查询文本
            category_id: 分类ID（可选）
            level: 学术层级（可选）
            top_k: 返回结果数量
            
        Returns:
            搜索结果列表
        """
        # 构建过滤条件
        where = {}
        if category_id:
            where['category_id'] = category_id
        if level:
            where['level'] = level.value
        
        # 向量检索
        results = vector_store.search(
            query=query,
            n_results=top_k,
            where=where if where else None
        )
        
        # 整理结果
        search_results = []
        if results['ids'] and results['ids'][0]:
            for i, doc_id in enumerate(results['ids'][0]):
                knowledge_id = results['metadatas'][0][i]['knowledge_id']
                
                # 查询数据库获取完整信息
                knowledge = db.query(KnowledgeEntry).filter(
                    KnowledgeEntry.id == knowledge_id
                ).first()
                
                if knowledge:
                    search_results.append({
                        'knowledge_id': knowledge_id,
                        'title': knowledge.title,
                        'summary': knowledge.summary,
                        'content_snippet': results['documents'][0][i],
                        'distance': results['distances'][0][i] if 'distances' in results else 0,
                        'category': knowledge.category.name if knowledge.category else '',
                        'level': knowledge.level.value,
                        'source_type': knowledge.source_type.value,
                    })
        
        return search_results


# 全局知识服务实例
knowledge_service = KnowledgeService()
