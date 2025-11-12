#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识库API路由 - 简化版
整合chs-ai知识库系统到CHS-Books平台
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import sys
from pathlib import Path

# 添加知识库服务路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'services' / 'knowledge'))

router = APIRouter(prefix="/api/knowledge", tags=["Knowledge Base"])

# ============================================================================
# 数据模型
# ============================================================================

class SearchRequest(BaseModel):
    """搜索请求"""
    query: str
    limit: int = 5
    category: Optional[str] = None

# ============================================================================
# 依赖注入
# ============================================================================

def get_db():
    """获取数据库会话"""
    try:
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent / 'services' / 'knowledge'))
        
        from services.knowledge.database import SessionLocal
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据库服务未就绪: {str(e)}")

def get_vector_store():
    """获取向量存储实例"""
    try:
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent / 'services' / 'knowledge'))
        
        from services.knowledge.vector_store import VectorStore
        return VectorStore()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"向量存储未就绪: {str(e)}")

# ============================================================================
# API端点
# ============================================================================

@router.get("/")
async def knowledge_info():
    """知识库系统信息"""
    return {
        "name": "CHS水利水电知识库",
        "version": "2.1.0",
        "description": "基于RAG架构的智能知识库系统",
        "features": [
            "智能搜索",
            "向量检索",
            "分类管理",
            "知识推荐"
        ],
        "status": "ready"
    }

@router.get("/stats")
async def get_statistics(db = Depends(get_db)):
    """获取知识库统计信息"""
    try:
        from services.knowledge.models import Category, KnowledgeEntry
        
        total_categories = db.query(Category).count()
        total_knowledge = db.query(KnowledgeEntry).count()
        
        # 按分类统计
        from sqlalchemy import func
        category_stats = db.query(
            Category.name,
            func.count(KnowledgeEntry.id).label('count')
        ).join(
            KnowledgeEntry, Category.id == KnowledgeEntry.category_id
        ).group_by(Category.name).all()
        
        return {
            "success": True,
            "stats": {
                "total_categories": total_categories,
                "total_knowledge": total_knowledge,
                "by_category": {name: count for name, count in category_stats}
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/categories")
async def get_categories(db = Depends(get_db)):
    """获取所有分类"""
    try:
        from services.knowledge.models import Category
        
        # 获取顶级分类
        top_categories = db.query(Category).filter(Category.level == 0).order_by(Category.order_num).all()
        
        result = []
        for cat in top_categories:
            # 获取子分类
            children = db.query(Category).filter(
                Category.parent_id == cat.id
            ).order_by(Category.order_num).all()
            
            result.append({
                "id": cat.id,
                "name": cat.name,
                "description": cat.description,
                "children": [
                    {
                        "id": child.id,
                        "name": child.name,
                        "description": child.description
                    }
                    for child in children
                ]
            })
        
        return {
            "success": True,
            "categories": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search")
async def search_knowledge(
    request: SearchRequest,
    db = Depends(get_db)
):
    """搜索知识库"""
    try:
        from services.knowledge.models import KnowledgeEntry, Category
        
        # 首先尝试向量搜索
        try:
            vector_store = get_vector_store()
            
            # 向量搜索
            search_results = vector_store.search(
                query=request.query,
                limit=request.limit
            )
            
            # 获取对应的知识条目
            results = []
            for result in search_results:
                # 从metadata中获取knowledge_id
                knowledge_id = result.get('metadata', {}).get('knowledge_id')
                if knowledge_id:
                    knowledge = db.query(KnowledgeEntry).filter(
                        KnowledgeEntry.id == knowledge_id
                    ).first()
                    
                    if knowledge:
                        category = db.query(Category).filter(
                            Category.id == knowledge.category_id
                        ).first()
                        
                        results.append({
                            "id": knowledge.id,
                            "title": knowledge.title,
                            "content": knowledge.content[:300] + "..." if len(knowledge.content) > 300 else knowledge.content,
                            "category": category.name if category else "未分类",
                            "level": knowledge.level.value if hasattr(knowledge.level, 'value') else str(knowledge.level),
                            "source": knowledge.source_name,
                            "score": result.get('score', 0.0)
                        })
            
            return {
                "success": True,
                "query": request.query,
                "results": results,
                "total": len(results),
                "method": "vector_search"
            }
            
        except Exception as vector_error:
            # 向量搜索失败,使用关键词搜索
            print(f"[WARN] Vector search failed: {vector_error}, falling back to keyword search")
            
            query = db.query(KnowledgeEntry)
            
            # 关键词过滤
            keywords = request.query.split()
            for keyword in keywords:
                query = query.filter(
                    (KnowledgeEntry.title.contains(keyword)) |
                    (KnowledgeEntry.content.contains(keyword))
                )
            
            # 分类过滤
            if request.category:
                query = query.join(Category).filter(Category.name == request.category)
            
            knowledge_list = query.limit(request.limit).all()
            
            results = []
            for knowledge in knowledge_list:
                category = db.query(Category).filter(
                    Category.id == knowledge.category_id
                ).first()
                
                results.append({
                    "id": knowledge.id,
                    "title": knowledge.title,
                    "content": knowledge.content[:300] + "..." if len(knowledge.content) > 300 else knowledge.content,
                    "category": category.name if category else "未分类",
                    "level": knowledge.level.value if hasattr(knowledge.level, 'value') else str(knowledge.level),
                    "source": knowledge.source_name,
                    "score": 0.5  # 默认分数
                })
            
            return {
                "success": True,
                "query": request.query,
                "results": results,
                "total": len(results),
                "method": "keyword_search"
            }
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/knowledge/{knowledge_id}")
async def get_knowledge_detail(knowledge_id: str, db = Depends(get_db)):
    """获取知识详情"""
    try:
        from services.knowledge.models import KnowledgeEntry, Category
        
        knowledge = db.query(KnowledgeEntry).filter(
            KnowledgeEntry.id == knowledge_id
        ).first()
        
        if not knowledge:
            raise HTTPException(status_code=404, detail="Knowledge not found")
        
        category = db.query(Category).filter(
            Category.id == knowledge.category_id
        ).first()
        
        # 更新浏览次数
        knowledge.view_count += 1
        db.commit()
        
        return {
            "success": True,
            "knowledge": {
                "id": knowledge.id,
                "title": knowledge.title,
                "content": knowledge.content,
                "summary": knowledge.summary,
                "category": category.name if category else "未分类",
                "level": knowledge.level.value if hasattr(knowledge.level, 'value') else str(knowledge.level),
                "source_type": knowledge.source_type.value if hasattr(knowledge.source_type, 'value') else str(knowledge.source_type),
                "source_name": knowledge.source_name,
                "author": knowledge.author,
                "keywords": knowledge.keywords,
                "tags": knowledge.tags,
                "view_count": knowledge.view_count,
                "created_at": knowledge.created_at.isoformat() if knowledge.created_at else None,
                "updated_at": knowledge.updated_at.isoformat() if knowledge.updated_at else None
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """健康检查"""
    try:
        from services.knowledge.database import SessionLocal
        from services.knowledge.vector_store import VectorStore
        
        # 测试数据库连接
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        
        # 测试向量存储
        vector_store = VectorStore()
        
        return {
            "status": "healthy",
            "database": "connected",
            "vector_store": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

@router.get("/recommend")
async def recommend_knowledge(
    knowledge_id: Optional[str] = None,
    limit: int = 5,
    db = Depends(get_db)
):
    """
    推荐相关知识
    如果提供knowledge_id，推荐相似知识；否则推荐热门知识
    """
    try:
        from services.knowledge.models import KnowledgeEntry, Category
        from sqlalchemy import func, desc
        
        if knowledge_id:
            # 基于特定知识推荐相似内容
            current_knowledge = db.query(KnowledgeEntry).filter(
                KnowledgeEntry.id == knowledge_id
            ).first()
            
            if not current_knowledge:
                raise HTTPException(status_code=404, detail="Knowledge not found")
            
            # 推荐同分类的其他知识
            recommendations = db.query(KnowledgeEntry).filter(
                KnowledgeEntry.category_id == current_knowledge.category_id,
                KnowledgeEntry.id != knowledge_id
            ).order_by(desc(KnowledgeEntry.view_count)).limit(limit).all()
            
            # 如果同分类知识不足，添加其他分类的热门知识
            if len(recommendations) < limit:
                additional = db.query(KnowledgeEntry).filter(
                    KnowledgeEntry.id != knowledge_id,
                    KnowledgeEntry.category_id != current_knowledge.category_id
                ).order_by(desc(KnowledgeEntry.view_count)).limit(
                    limit - len(recommendations)
                ).all()
                recommendations.extend(additional)
        else:
            # 推荐热门知识（按浏览次数）
            recommendations = db.query(KnowledgeEntry).order_by(
                desc(KnowledgeEntry.view_count)
            ).limit(limit).all()
        
        # 构建返回结果
        results = []
        for knowledge in recommendations:
            category = db.query(Category).filter(
                Category.id == knowledge.category_id
            ).first()
            
            results.append({
                "id": knowledge.id,
                "title": knowledge.title,
                "content": knowledge.content[:200] + "..." if len(knowledge.content) > 200 else knowledge.content,
                "category": category.name if category else "未分类",
                "level": knowledge.level.value if hasattr(knowledge.level, 'value') else str(knowledge.level),
                "view_count": knowledge.view_count,
                "source": knowledge.source_name
            })
        
        return {
            "success": True,
            "recommendations": results,
            "total": len(results),
            "based_on": knowledge_id if knowledge_id else "popularity"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/popular")
async def get_popular_knowledge(limit: int = 10, db = Depends(get_db)):
    """获取热门知识（按浏览次数排序）"""
    try:
        from services.knowledge.models import KnowledgeEntry, Category
        from sqlalchemy import desc
        
        popular = db.query(KnowledgeEntry).order_by(
            desc(KnowledgeEntry.view_count)
        ).limit(limit).all()
        
        results = []
        for knowledge in popular:
            category = db.query(Category).filter(
                Category.id == knowledge.category_id
            ).first()
            
            results.append({
                "id": knowledge.id,
                "title": knowledge.title,
                "category": category.name if category else "未分类",
                "level": knowledge.level.value if hasattr(knowledge.level, 'value') else str(knowledge.level),
                "view_count": knowledge.view_count
            })
        
        return {
            "success": True,
            "popular": results,
            "total": len(results)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recent")
async def get_recent_knowledge(limit: int = 10, db = Depends(get_db)):
    """获取最新知识（按创建时间排序）"""
    try:
        from services.knowledge.models import KnowledgeEntry, Category
        from sqlalchemy import desc
        
        recent = db.query(KnowledgeEntry).order_by(
            desc(KnowledgeEntry.created_at)
        ).limit(limit).all()
        
        results = []
        for knowledge in recent:
            category = db.query(Category).filter(
                Category.id == knowledge.category_id
            ).first()
            
            results.append({
                "id": knowledge.id,
                "title": knowledge.title,
                "category": category.name if category else "未分类",
                "level": knowledge.level.value if hasattr(knowledge.level, 'value') else str(knowledge.level),
                "created_at": knowledge.created_at.isoformat() if knowledge.created_at else None
            })
        
        return {
            "success": True,
            "recent": results,
            "total": len(results)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/graph")
async def get_knowledge_graph(db = Depends(get_db)):
    """获取知识图谱数据用于可视化"""
    try:
        from services.knowledge.models import KnowledgeEntry, Category
        from collections import defaultdict
        
        # 获取所有知识条目
        all_knowledge = db.query(KnowledgeEntry).all()
        categories = db.query(Category).all()
        
        # 构建分类映射
        category_map = {cat.id: cat.name for cat in categories}
        
        # 构建节点
        nodes = []
        category_groups = defaultdict(list)
        
        for knowledge in all_knowledge:
            category_name = category_map.get(knowledge.category_id, "未分类")
            node = {
                "id": knowledge.id,
                "name": knowledge.title,
                "group": category_name,
                "level": knowledge.level.value if hasattr(knowledge.level, 'value') else str(knowledge.level),
                "view_count": knowledge.view_count
            }
            nodes.append(node)
            category_groups[category_name].append(knowledge.id)
        
        # 构建边（基于分类关系）
        links = []
        for category_name, knowledge_ids in category_groups.items():
            # 同一分类内的知识相互连接
            for i, source_id in enumerate(knowledge_ids):
                # 每个节点连接到下一个节点，形成链式结构
                if i < len(knowledge_ids) - 1:
                    links.append({
                        "source": source_id,
                        "target": knowledge_ids[i + 1],
                        "value": 0.6,
                        "type": "category"
                    })
        
        # 基于关键词构建额外的相似性连接
        keyword_groups = defaultdict(list)
        for knowledge in all_knowledge:
            if knowledge.keywords:
                for keyword in knowledge.keywords:
                    keyword_groups[keyword].append(knowledge.id)
        
        # 为共享关键词的知识添加连接
        for keyword, knowledge_ids in keyword_groups.items():
            if len(knowledge_ids) >= 2:
                for i in range(min(len(knowledge_ids), 3)):  # 限制连接数
                    for j in range(i + 1, min(len(knowledge_ids), i + 3)):
                        # 检查连接是否已存在
                        link_exists = any(
                            (l["source"] == knowledge_ids[i] and l["target"] == knowledge_ids[j]) or
                            (l["source"] == knowledge_ids[j] and l["target"] == knowledge_ids[i])
                            for l in links
                        )
                        if not link_exists:
                            links.append({
                                "source": knowledge_ids[i],
                                "target": knowledge_ids[j],
                                "value": 0.8,
                                "type": "keyword"
                            })
        
        return {
            "success": True,
            "nodes": nodes,
            "links": links,
            "stats": {
                "node_count": len(nodes),
                "edge_count": len(links),
                "categories": list(category_groups.keys()),
                "avg_degree": (len(links) * 2 / len(nodes)) if len(nodes) > 0 else 0
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
