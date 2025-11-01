"""
RAG知识库API端点
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.knowledge import KnowledgeBase, Document, DocumentType
from app.services.rag_service import rag_service

router = APIRouter()


# ============ Pydantic模型 ============

class KnowledgeBaseCreate(BaseModel):
    """创建知识库请求"""
    name: str = Field(..., min_length=1, max_length=200, description="知识库名称")
    description: Optional[str] = Field(None, description="知识库描述")


class KnowledgeBaseResponse(BaseModel):
    """知识库响应"""
    id: int
    name: str
    description: Optional[str]
    owner_id: int
    status: str
    document_count: int
    total_chunks: int
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


class DocumentUpload(BaseModel):
    """上传文档请求"""
    title: str = Field(..., min_length=1, max_length=500, description="文档标题")
    content: str = Field(..., min_length=1, description="文档内容")
    doc_type: DocumentType = Field(default=DocumentType.TEXT, description="文档类型")


class DocumentResponse(BaseModel):
    """文档响应"""
    id: int
    knowledge_base_id: int
    title: str
    doc_type: str
    chunk_count: int
    view_count: int
    created_at: str
    
    class Config:
        from_attributes = True


class SearchRequest(BaseModel):
    """搜索请求"""
    query: str = Field(..., min_length=1, max_length=500, description="搜索查询")
    top_k: int = Field(default=5, ge=1, le=20, description="返回结果数量")


class AskRequest(BaseModel):
    """RAG问答请求"""
    question: str = Field(..., min_length=1, max_length=500, description="问题")
    context_size: int = Field(default=3, ge=1, le=10, description="上下文数量")


# ============ API端点 ============

@router.post("/create", response_model=KnowledgeBaseResponse, tags=["RAG知识库"])
async def create_knowledge_base(
    kb_create: KnowledgeBaseCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """创建知识库"""
    try:
        kb = await rag_service.create_knowledge_base(
            db=db,
            name=kb_create.name,
            description=kb_create.description,
            owner_id=current_user.id
        )
        
        return KnowledgeBaseResponse(
            id=kb.id,
            name=kb.name,
            description=kb.description,
            owner_id=kb.owner_id,
            status=kb.status.value,
            document_count=kb.document_count,
            total_chunks=kb.total_chunks,
            created_at=kb.created_at.isoformat(),
            updated_at=kb.updated_at.isoformat()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建知识库失败: {str(e)}"
        )


@router.post("/{kb_id}/upload", response_model=DocumentResponse, tags=["RAG知识库"])
async def upload_document(
    kb_id: int,
    doc: DocumentUpload,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """上传文档到知识库"""
    try:
        # 验证知识库所有权
        kb = await db.get(KnowledgeBase, kb_id)
        if not kb:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="知识库不存在"
            )
        
        if kb.owner_id != current_user.id and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限操作此知识库"
            )
        
        document = await rag_service.upload_document(
            db=db,
            knowledge_base_id=kb_id,
            title=doc.title,
            content=doc.content,
            doc_type=doc.doc_type
        )
        
        return DocumentResponse(
            id=document.id,
            knowledge_base_id=document.knowledge_base_id,
            title=document.title,
            doc_type=document.doc_type.value,
            chunk_count=document.chunk_count,
            view_count=document.view_count,
            created_at=document.created_at.isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"上传文档失败: {str(e)}"
        )


@router.get("/{kb_id}/search", tags=["RAG知识库"])
async def search_knowledge(
    kb_id: int,
    query: str,
    top_k: int = 5,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """搜索知识库"""
    try:
        # 验证知识库访问权限
        kb = await db.get(KnowledgeBase, kb_id)
        if not kb:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="知识库不存在"
            )
        
        results = await rag_service.search_knowledge(
            db=db,
            knowledge_base_id=kb_id,
            query=query,
            top_k=top_k
        )
        
        return {
            "query": query,
            "knowledge_base_id": kb_id,
            "results": results
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"搜索失败: {str(e)}"
        )


@router.post("/ask", tags=["RAG知识库"])
async def ask_question(
    kb_id: int,
    question: str,
    context_size: int = 3,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """RAG问答"""
    try:
        # 验证知识库访问权限
        kb = await db.get(KnowledgeBase, kb_id)
        if not kb:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="知识库不存在"
            )
        
        answer = await rag_service.ask_question(
            db=db,
            knowledge_base_id=kb_id,
            question=question,
            context_size=context_size
        )
        
        return {
            "question": question,
            "knowledge_base_id": kb_id,
            **answer
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"问答失败: {str(e)}"
        )


@router.get("", response_model=List[KnowledgeBaseResponse], tags=["RAG知识库"])
async def list_knowledge_bases(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取知识库列表"""
    try:
        kbs = await rag_service.get_knowledge_bases(
            db=db,
            owner_id=current_user.id,
            skip=skip,
            limit=limit
        )
        
        return [
            KnowledgeBaseResponse(
                id=kb.id,
                name=kb.name,
                description=kb.description,
                owner_id=kb.owner_id,
                status=kb.status.value,
                document_count=kb.document_count,
                total_chunks=kb.total_chunks,
                created_at=kb.created_at.isoformat(),
                updated_at=kb.updated_at.isoformat()
            )
            for kb in kbs
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取知识库列表失败: {str(e)}"
        )


@router.get("/{kb_id}", response_model=KnowledgeBaseResponse, tags=["RAG知识库"])
async def get_knowledge_base(
    kb_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取知识库详情"""
    try:
        kb = await db.get(KnowledgeBase, kb_id)
        if not kb:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="知识库不存在"
            )
        
        return KnowledgeBaseResponse(
            id=kb.id,
            name=kb.name,
            description=kb.description,
            owner_id=kb.owner_id,
            status=kb.status.value,
            document_count=kb.document_count,
            total_chunks=kb.total_chunks,
            created_at=kb.created_at.isoformat(),
            updated_at=kb.updated_at.isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取知识库详情失败: {str(e)}"
        )


@router.delete("/{kb_id}/documents/{doc_id}", tags=["RAG知识库"])
async def delete_document(
    kb_id: int,
    doc_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """删除文档"""
    try:
        # 验证知识库所有权
        kb = await db.get(KnowledgeBase, kb_id)
        if not kb:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="知识库不存在"
            )
        
        if kb.owner_id != current_user.id and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限操作此知识库"
            )
        
        success = await rag_service.delete_document(
            db=db,
            document_id=doc_id,
            knowledge_base_id=kb_id
        )
        
        return {
            "success": success,
            "message": "文档删除成功"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除文档失败: {str(e)}"
        )


@router.get("/stats/{kb_id}", tags=["RAG知识库"])
async def get_knowledge_base_stats(
    kb_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取知识库统计"""
    try:
        # 验证知识库访问权限
        kb = await db.get(KnowledgeBase, kb_id)
        if not kb:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="知识库不存在"
            )
        
        stats = await rag_service.get_knowledge_base_stats(
            db=db,
            knowledge_base_id=kb_id
        )
        
        return stats
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取统计失败: {str(e)}"
        )
