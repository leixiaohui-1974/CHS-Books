"""
RAG系统V2测试
测试增强的RAG功能，包括向量存储和语义搜索
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.knowledge import KnowledgeBase, Document, DocumentChunk
from app.services.rag_service_v2 import rag_service_v2
from app.services.embedding_service import embedding_service
from app.services.vector_store import vector_store


@pytest.mark.asyncio
async def test_create_knowledge_base_v2(db_session: AsyncSession):
    """测试创建知识库V2"""
    kb = await rag_service_v2.create_knowledge_base(
        db=db_session,
        name="测试知识库V2",
        description="用于测试RAG V2系统"
    )
    
    assert kb.id is not None
    assert kb.name == "测试知识库V2"
    assert kb.document_count == 0
    assert kb.total_chunks == 0
    
    print(f"\n✅ 创建知识库: {kb.name} (ID={kb.id})")


@pytest.mark.asyncio
async def test_upload_document_v2(db_session: AsyncSession):
    """测试上传文档V2"""
    # 创建知识库
    kb = await rag_service_v2.create_knowledge_base(
        db=db_session,
        name="测试知识库",
        description="测试"
    )
    
    # 上传文档
    content = """
    明渠水力学是研究明渠流动规律的学科。
    
    明渠是指具有自由水面的渠道，如河流、运河、灌溉渠道等。
    明渠流动的特点是具有自由水面，水深可以变化。
    
    明渠水力学的基本方程包括连续性方程和动量方程。
    连续性方程反映质量守恒定律。
    动量方程反映动量守恒定律。
    """
    
    doc = await rag_service_v2.upload_document(
        db=db_session,
        knowledge_base_id=kb.id,
        title="明渠水力学基础",
        content=content
    )
    
    assert doc.id is not None
    assert doc.title == "明渠水力学基础"
    assert doc.chunk_count > 0
    
    # 刷新知识库
    await db_session.refresh(kb)
    assert kb.document_count == 1
    assert kb.total_chunks == doc.chunk_count
    
    print(f"\n✅ 上传文档: {doc.title}")
    print(f"   文档ID: {doc.id}")
    print(f"   分块数: {doc.chunk_count}")
    print(f"   知识库文档数: {kb.document_count}")


@pytest.mark.asyncio
async def test_semantic_search_v2(db_session: AsyncSession):
    """测试语义搜索V2"""
    # 创建知识库并上传文档
    kb = await rag_service_v2.create_knowledge_base(
        db=db_session,
        name="水力学知识库",
        description="测试"
    )
    
    # 上传多个文档
    docs_content = [
        ("渠道设计", "渠道设计需要考虑流量、坡度、粗糙度等因素。合理的渠道断面可以提高输水效率。"),
        ("水流计算", "水流计算包括水深计算、流速计算和流量计算。这些计算基于水力学基本方程。"),
        ("明渠流态", "明渠流动可以分为急流和缓流两种流态。临界流速是判断流态的关键参数。")
    ]
    
    for title, content in docs_content:
        await rag_service_v2.upload_document(
            db=db_session,
            knowledge_base_id=kb.id,
            title=title,
            content=content
        )
    
    # 执行搜索
    results = await rag_service_v2.search_knowledge(
        db=db_session,
        knowledge_base_id=kb.id,
        query="如何计算水流速度",
        top_k=3
    )
    
    assert len(results) > 0
    assert all("content" in r for r in results)
    assert all("similarity" in r for r in results)
    assert all("document_title" in r for r in results)
    
    print(f"\n✅ 语义搜索: 找到 {len(results)} 个相关结果")
    for i, result in enumerate(results):
        print(f"   结果{i+1}: {result['document_title']}")
        print(f"   相似度: {result['similarity']:.4f}")
        print(f"   内容片段: {result['content'][:50]}...")


@pytest.mark.asyncio
async def test_rag_question_answering_v2(db_session: AsyncSession):
    """测试RAG问答V2"""
    # 创建知识库
    kb = await rag_service_v2.create_knowledge_base(
        db=db_session,
        name="Python教程知识库",
        description="测试"
    )
    
    # 上传教程文档
    content = """
    Python是一种高级编程语言，具有简洁易读的语法。
    
    Python的主要特点：
    1. 语法简洁：Python使用缩进来表示代码块，不需要大括号。
    2. 动态类型：变量不需要声明类型，在运行时自动确定。
    3. 丰富的标准库：Python提供了大量内置模块和函数。
    4. 跨平台：Python可以在Windows、Linux、macOS等系统上运行。
    
    Python的应用领域：
    - Web开发：使用Django、Flask等框架
    - 数据分析：使用Pandas、NumPy等库
    - 机器学习：使用TensorFlow、PyTorch等框架
    - 自动化脚本：自动化日常任务
    """
    
    await rag_service_v2.upload_document(
        db=db_session,
        knowledge_base_id=kb.id,
        title="Python编程入门",
        content=content
    )
    
    # 提问
    result = await rag_service_v2.ask_question(
        db=db_session,
        knowledge_base_id=kb.id,
        question="Python有哪些特点？",
        top_k=2
    )
    
    assert "answer" in result
    assert "sources" in result
    assert "confidence" in result
    assert len(result["sources"]) > 0
    assert result["confidence"] > 0
    
    print(f"\n✅ RAG问答测试")
    print(f"   问题: Python有哪些特点？")
    print(f"   回答: {result['answer'][:100]}...")
    print(f"   置信度: {result['confidence']:.4f}")
    print(f"   引用来源: {len(result['sources'])}个")
    print(f"   使用模型: {result.get('model', 'unknown')}")


@pytest.mark.asyncio
async def test_embedding_service(db_session: AsyncSession):
    """测试嵌入服务"""
    # 单个文本嵌入
    text = "这是一个测试文本"
    embedding = embedding_service.generate_embedding(text)
    
    assert len(embedding) == embedding_service.embedding_dim
    assert all(isinstance(x, float) for x in embedding)
    
    # 批量嵌入
    texts = ["文本1", "文本2", "文本3"]
    embeddings = embedding_service.generate_embeddings_batch(texts)
    
    assert len(embeddings) == 3
    assert all(len(emb) == embedding_service.embedding_dim for emb in embeddings)
    
    # 相似度计算
    emb1 = embedding_service.generate_embedding("明渠水力学")
    emb2 = embedding_service.generate_embedding("明渠水力学")
    emb3 = embedding_service.generate_embedding("完全不同的内容")
    
    similarity_same = embedding_service.calculate_similarity(emb1, emb2)
    similarity_diff = embedding_service.calculate_similarity(emb1, emb3)
    
    # 相同文本的相似度应该高于不同文本
    assert similarity_same > 0.95  # 相同文本相似度接近1
    
    print(f"\n✅ 嵌入服务测试")
    print(f"   嵌入维度: {embedding_service.embedding_dim}")
    print(f"   相同文本相似度: {similarity_same:.4f}")
    print(f"   不同文本相似度: {similarity_diff:.4f}")


@pytest.mark.asyncio
async def test_vector_store(db_session: AsyncSession):
    """测试向量存储"""
    collection_name = "test_collection"
    
    # 创建集合
    success = vector_store.create_collection(
        collection_name=collection_name,
        metadata={"test": "true"}
    )
    assert success
    
    # 添加文档
    documents = ["文档1内容", "文档2内容", "文档3内容"]
    embeddings = embedding_service.generate_embeddings_batch(documents)
    metadatas = [{"index": i} for i in range(len(documents))]
    
    success = vector_store.add_documents(
        collection_name=collection_name,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas
    )
    assert success
    
    # 搜索
    query = "文档内容"
    query_embedding = embedding_service.generate_embedding(query)
    results = vector_store.search(
        collection_name=collection_name,
        query_embedding=query_embedding,
        top_k=2
    )
    
    assert len(results) <= 2
    assert all("document" in r for r in results)
    assert all("distance" in r for r in results)
    
    # 获取文档数量
    count = vector_store.get_collection_count(collection_name)
    assert count == 3
    
    # 删除集合
    success = vector_store.delete_collection(collection_name)
    assert success
    
    print(f"\n✅ 向量存储测试")
    print(f"   添加文档: {len(documents)}个")
    print(f"   搜索结果: {len(results)}个")
    print(f"   文档数量: {count}")


@pytest.mark.asyncio
async def test_document_chunking_v2(db_session: AsyncSession):
    """测试文档分块V2"""
    # 长文档
    long_text = """
    第一段内容。这是关于明渠水力学的介绍。明渠是具有自由水面的渠道。
    
    第二段内容。明渠流动的基本特征是水面压力等于大气压。水深可以自由变化。
    
    第三段内容。明渠水力学研究的核心问题包括水流的连续性、能量和动量。
    
    第四段内容。实际应用中需要考虑渠道的形状、坡度和粗糙度等因素。
    
    第五段内容。计算方法包括均匀流公式和非均匀流数值解法。
    """ * 5  # 重复5次以创建长文本
    
    # 创建知识库并上传
    kb = await rag_service_v2.create_knowledge_base(
        db=db_session,
        name="分块测试",
        description="测试"
    )
    
    doc = await rag_service_v2.upload_document(
        db=db_session,
        knowledge_base_id=kb.id,
        title="长文档",
        content=long_text
    )
    
    # 验证分块
    assert doc.chunk_count > 1
    
    print(f"\n✅ 文档分块测试")
    print(f"   文档长度: {len(long_text)}字符")
    print(f"   分块数量: {doc.chunk_count}")
    print(f"   平均每块: {len(long_text) // doc.chunk_count}字符")


@pytest.mark.asyncio
async def test_multiple_knowledge_bases_v2(db_session: AsyncSession):
    """测试多个知识库V2"""
    # 创建两个知识库
    kb1 = await rag_service_v2.create_knowledge_base(
        db=db_session,
        name="数学知识库",
        description="数学相关"
    )
    
    kb2 = await rag_service_v2.create_knowledge_base(
        db=db_session,
        name="物理知识库",
        description="物理相关"
    )
    
    # 分别上传文档
    await rag_service_v2.upload_document(
        db=db_session,
        knowledge_base_id=kb1.id,
        title="微积分",
        content="微积分是研究函数的微分和积分的数学分支。"
    )
    
    await rag_service_v2.upload_document(
        db=db_session,
        knowledge_base_id=kb2.id,
        title="力学",
        content="力学是研究物体运动规律和受力分析的物理学分支。"
    )
    
    # 在各自知识库中搜索
    results1 = await rag_service_v2.search_knowledge(
        db=db_session,
        knowledge_base_id=kb1.id,
        query="数学函数",
        top_k=5
    )
    
    results2 = await rag_service_v2.search_knowledge(
        db=db_session,
        knowledge_base_id=kb2.id,
        query="物体运动",
        top_k=5
    )
    
    assert len(results1) > 0
    assert len(results2) > 0
    
    print(f"\n✅ 多知识库测试")
    print(f"   知识库1: {kb1.name} ({kb1.document_count}个文档)")
    print(f"   知识库2: {kb2.name} ({kb2.document_count}个文档)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
