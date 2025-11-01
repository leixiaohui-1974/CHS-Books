"""
RAG知识库系统测试
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.knowledge import (
    KnowledgeBase, Document, DocumentChunk,
    KnowledgeBaseStatus, DocumentType
)
from app.services.rag_service import rag_service


@pytest.mark.asyncio
async def test_create_knowledge_base(db_session: AsyncSession):
    """测试创建知识库"""
    # 创建测试用户
    user = User(
        username="testuser_kb",
        email="kb@test.com",
        hashed_password="hashed_password",
        full_name="KB Test"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    # 创建知识库
    kb = await rag_service.create_knowledge_base(
        db_session,
        name="Python编程知识库",
        description="Python相关技术文档和教程",
        owner_id=user.id
    )
    
    assert kb is not None
    assert kb.name == "Python编程知识库"
    assert kb.owner_id == user.id
    assert kb.status == KnowledgeBaseStatus.ACTIVE
    assert kb.document_count == 0


@pytest.mark.asyncio
async def test_upload_document(db_session: AsyncSession):
    """测试上传文档"""
    # 创建测试用户
    user = User(
        username="testuser_doc",
        email="doc@test.com",
        hashed_password="hashed_password",
        full_name="Doc Test"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    # 创建知识库
    kb = await rag_service.create_knowledge_base(
        db_session,
        name="测试知识库",
        description="用于测试",
        owner_id=user.id
    )
    
    # 上传文档
    content = "Python是一种高级编程语言。" * 50  # 生成足够长的内容以触发分块
    doc = await rag_service.upload_document(
        db_session,
        kb.id,
        title="Python基础",
        content=content,
        doc_type=DocumentType.TEXT
    )
    
    assert doc is not None
    assert doc.title == "Python基础"
    assert doc.knowledge_base_id == kb.id
    assert doc.chunk_count > 0


@pytest.mark.asyncio
async def test_search_knowledge(db_session: AsyncSession):
    """测试知识搜索"""
    # 创建测试用户和知识库
    user = User(
        username="testuser_search",
        email="search@test.com",
        hashed_password="hashed_password",
        full_name="Search Test"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    kb = await rag_service.create_knowledge_base(
        db_session,
        name="搜索测试库",
        description="测试搜索功能",
        owner_id=user.id
    )
    
    # 上传文档
    content = "Python装饰器是一种特殊的函数，可以修改其他函数的行为。" * 20
    await rag_service.upload_document(
        db_session,
        kb.id,
        title="Python装饰器",
        content=content,
        doc_type=DocumentType.TEXT
    )
    
    # 搜索知识
    results = await rag_service.search_knowledge(
        db_session,
        kb.id,
        query="什么是装饰器",
        top_k=5
    )
    
    assert len(results) > 0
    assert "similarity" in results[0]
    assert "content" in results[0]


@pytest.mark.asyncio
async def test_ask_question(db_session: AsyncSession):
    """测试RAG问答"""
    # 创建测试用户和知识库
    user = User(
        username="testuser_qa",
        email="qa@test.com",
        hashed_password="hashed_password",
        full_name="QA Test"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    kb = await rag_service.create_knowledge_base(
        db_session,
        name="问答测试库",
        description="测试问答功能",
        owner_id=user.id
    )
    
    # 上传文档
    content = """
    Python是一种解释型、面向对象、动态数据类型的高级程序设计语言。
    Python由Guido van Rossum于1989年底发明，第一个公开发行版发行于1991年。
    Python语法简洁清晰，特色之一是强制用空白符作为语句缩进。
    """ * 10
    await rag_service.upload_document(
        db_session,
        kb.id,
        title="Python简介",
        content=content,
        doc_type=DocumentType.TEXT
    )
    
    # 提问
    result = await rag_service.ask_question(
        db_session,
        kb.id,
        question="Python是谁发明的？"
    )
    
    assert "answer" in result
    assert "sources" in result
    assert len(result["sources"]) > 0


@pytest.mark.asyncio
async def test_get_knowledge_bases(db_session: AsyncSession):
    """测试获取知识库列表"""
    # 创建测试用户
    user = User(
        username="testuser_list",
        email="list@test.com",
        hashed_password="hashed_password",
        full_name="List Test"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    # 创建多个知识库
    await rag_service.create_knowledge_base(
        db_session, "知识库1", "描述1", user.id
    )
    await rag_service.create_knowledge_base(
        db_session, "知识库2", "描述2", user.id
    )
    await rag_service.create_knowledge_base(
        db_session, "知识库3", "描述3", user.id
    )
    
    # 获取列表
    kbs = await rag_service.get_knowledge_bases(db_session, owner_id=user.id)
    
    assert len(kbs) >= 3


@pytest.mark.asyncio
async def test_knowledge_base_stats(db_session: AsyncSession):
    """测试知识库统计"""
    # 创建测试用户和知识库
    user = User(
        username="testuser_stats",
        email="stats@test.com",
        hashed_password="hashed_password",
        full_name="Stats Test"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    kb = await rag_service.create_knowledge_base(
        db_session,
        name="统计测试库",
        description="测试统计功能",
        owner_id=user.id
    )
    
    # 上传文档
    await rag_service.upload_document(
        db_session, kb.id, "文档1", "内容1" * 100, DocumentType.TEXT
    )
    await rag_service.upload_document(
        db_session, kb.id, "文档2", "内容2" * 100, DocumentType.TEXT
    )
    
    # 获取统计
    stats = await rag_service.get_knowledge_base_stats(db_session, kb.id)
    
    assert stats["document_count"] == 2
    assert stats["total_chunks"] > 0
    assert "avg_chunks_per_doc" in stats


@pytest.mark.asyncio
async def test_delete_document(db_session: AsyncSession):
    """测试删除文档"""
    # 创建测试用户和知识库
    user = User(
        username="testuser_delete",
        email="delete@test.com",
        hashed_password="hashed_password",
        full_name="Delete Test"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    kb = await rag_service.create_knowledge_base(
        db_session,
        name="删除测试库",
        description="测试删除功能",
        owner_id=user.id
    )
    
    # 上传文档
    doc = await rag_service.upload_document(
        db_session, kb.id, "待删除文档", "内容" * 50, DocumentType.TEXT
    )
    
    # 删除文档
    result = await rag_service.delete_document(db_session, doc.id, kb.id)
    
    assert result is True
    
    # 验证文档已删除
    stats = await rag_service.get_knowledge_base_stats(db_session, kb.id)
    assert stats["document_count"] == 0


@pytest.mark.asyncio
async def test_text_splitting(db_session: AsyncSession):
    """测试文本分块功能"""
    # 创建测试用户和知识库
    user = User(
        username="testuser_split",
        email="split@test.com",
        hashed_password="hashed_password",
        full_name="Split Test"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    kb = await rag_service.create_knowledge_base(
        db_session,
        name="分块测试库",
        description="测试文本分块",
        owner_id=user.id
    )
    
    # 创建长文本（超过默认chunk_size）
    long_text = "这是一段很长的文本。" * 200
    
    doc = await rag_service.upload_document(
        db_session, kb.id, "长文档", long_text, DocumentType.TEXT
    )
    
    # 验证分块
    assert doc.chunk_count > 1


@pytest.mark.asyncio
async def test_document_metadata(db_session: AsyncSession):
    """测试文档元数据"""
    # 创建测试用户和知识库
    user = User(
        username="testuser_meta",
        email="meta@test.com",
        hashed_password="hashed_password",
        full_name="Meta Test"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    kb = await rag_service.create_knowledge_base(
        db_session,
        name="元数据测试库",
        description="测试元数据",
        owner_id=user.id
    )
    
    # 上传文档（RAGService当前不支持meta_data参数，直接测试基本上传）
    doc = await rag_service.upload_document(
        db_session,
        kb.id,
        title="带元数据的文档",
        content="内容" * 50,
        doc_type=DocumentType.TEXT
    )
    
    # 手动设置元数据
    metadata = {
        "author": "张三",
        "category": "编程",
        "tags": ["Python", "教程"]
    }
    doc.meta_data = metadata
    await db_session.commit()
    await db_session.refresh(doc)
    
    assert doc.meta_data == metadata
    assert doc.meta_data["author"] == "张三"


@pytest.mark.asyncio
async def test_multiple_knowledge_bases(db_session: AsyncSession):
    """测试多知识库场景"""
    # 创建两个用户
    user1 = User(
        username="user1_multi",
        email="user1@test.com",
        hashed_password="hashed_password",
        full_name="User 1"
    )
    user2 = User(
        username="user2_multi",
        email="user2@test.com",
        hashed_password="hashed_password",
        full_name="User 2"
    )
    db_session.add_all([user1, user2])
    await db_session.commit()
    await db_session.refresh(user1)
    await db_session.refresh(user2)
    
    # 每个用户创建知识库
    kb1 = await rag_service.create_knowledge_base(
        db_session, "用户1的知识库", "描述1", user1.id
    )
    kb2 = await rag_service.create_knowledge_base(
        db_session, "用户2的知识库", "描述2", user2.id
    )
    
    # 验证隔离性
    user1_kbs = await rag_service.get_knowledge_bases(db_session, owner_id=user1.id)
    user2_kbs = await rag_service.get_knowledge_bases(db_session, owner_id=user2.id)
    
    assert len(user1_kbs) >= 1
    assert len(user2_kbs) >= 1
    assert kb1.owner_id == user1.id
    assert kb2.owner_id == user2.id


@pytest.mark.asyncio
async def test_knowledge_base_update(db_session: AsyncSession):
    """测试知识库更新"""
    # 创建测试用户和知识库
    user = User(
        username="testuser_update",
        email="update@test.com",
        hashed_password="hashed_password",
        full_name="Update Test"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    kb = await rag_service.create_knowledge_base(
        db_session,
        name="原始名称",
        description="原始描述",
        owner_id=user.id
    )
    
    # 更新知识库
    kb.name = "更新后的名称"
    kb.description = "更新后的描述"
    await db_session.commit()
    await db_session.refresh(kb)
    
    assert kb.name == "更新后的名称"
    assert kb.description == "更新后的描述"
