#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一搜索API路由
整合教材、案例和知识库的搜索功能
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import sys
from pathlib import Path
import json

# 添加服务路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'services' / 'textbook'))
sys.path.insert(0, str(Path(__file__).parent.parent / 'services' / 'knowledge'))

router = APIRouter(prefix="/api/search", tags=["Unified Search"])

# ============================================================================
# 数据模型
# ============================================================================

class SearchResult(BaseModel):
    """搜索结果"""
    type: str  # textbook, case, knowledge
    id: str
    title: str
    description: str
    source: str
    relevance_score: float = 1.0
    preview: Optional[str] = None

class SearchStats(BaseModel):
    """搜索统计"""
    textbooks: Dict[str, int]
    cases: Dict[str, int]
    knowledge: Dict[str, int]
    total_items: int

# ============================================================================
# 依赖注入
# ============================================================================

def get_textbook_db():
    """获取教材数据库会话"""
    try:
        from services.textbook.database import SessionLocal
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"教材数据库未就绪: {str(e)}")

def get_knowledge_db():
    """获取知识库数据库会话"""
    try:
        from services.knowledge.database import SessionLocal
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"知识库数据库未就绪: {str(e)}")

# ============================================================================
# 辅助函数
# ============================================================================

CASES_INDEX_FILE = Path(__file__).parent.parent / "cases_index.json"

def load_cases_index():
    """加载案例索引"""
    if not CASES_INDEX_FILE.exists():
        return {"books": [], "total_cases": 0}
    try:
        with open(CASES_INDEX_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"books": [], "total_cases": 0}

# ============================================================================
# API端点
# ============================================================================

@router.get("/stats")
async def get_search_stats(
    textbook_db = Depends(get_textbook_db),
    knowledge_db = Depends(get_knowledge_db)
):
    """获取搜索统计信息"""
    try:
        from services.textbook.models import Textbook, TextbookChapter
        from services.knowledge.models import KnowledgeEntry, Category
        from sqlalchemy import func
        
        # 教材统计
        textbook_count = textbook_db.query(Textbook).count()
        chapter_count = textbook_db.query(TextbookChapter).count()
        total_words = textbook_db.query(func.sum(TextbookChapter.word_count)).scalar() or 0
        
        # 案例统计
        cases_index = load_cases_index()
        case_count = cases_index.get("total_cases", 0)
        
        # 知识库统计
        knowledge_count = knowledge_db.query(KnowledgeEntry).count()
        category_count = knowledge_db.query(Category).count()
        
        return {
            "success": True,
            "textbooks": {
                "total": textbook_count,
                "chapters": chapter_count,
                "total_words": total_words
            },
            "cases": {
                "total": case_count,
                "books": len(cases_index.get("books", []))
            },
            "knowledge": {
                "total": knowledge_count,
                "categories": category_count
            },
            "total_items": textbook_count + case_count + knowledge_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def unified_search(
    query: str = Query(..., min_length=1, description="搜索查询词"),
    types: str = Query("textbook,case,knowledge", description="搜索类型，逗号分隔"),
    limit: int = Query(10, ge=1, le=50, description="每种类型返回结果数量"),
    textbook_db = Depends(get_textbook_db),
    knowledge_db = Depends(get_knowledge_db)
):
    """统一搜索API"""
    try:
        from services.textbook.models import TextbookChapter, Textbook
        from services.knowledge.models import KnowledgeEntry, Category
        from sqlalchemy import or_
        
        results = []
        type_list = [t.strip() for t in types.split(',')]
        
        # 1. 搜索教材
        if 'textbook' in type_list:
            chapters = textbook_db.query(TextbookChapter).filter(
                or_(
                    TextbookChapter.title.contains(query),
                    TextbookChapter.content.contains(query)
                )
            ).limit(limit).all()
            
            for chapter in chapters:
                textbook = textbook_db.query(Textbook).filter(Textbook.id == chapter.textbook_id).first()
                textbook_title = textbook.title if textbook else "未知教材"
                
                # 生成预览
                content = chapter.content or ""
                preview = ""
                if query in content:
                    idx = content.find(query)
                    start = max(0, idx - 50)
                    end = min(len(content), idx + len(query) + 50)
                    preview = "..." + content[start:end] + "..."
                
                results.append(SearchResult(
                    type="textbook",
                    id=chapter.id,
                    title=f"[{chapter.chapter_number}] {chapter.title}",
                    description=chapter.summary or f"章节字数: {chapter.word_count}",
                    source=textbook_title,
                    relevance_score=0.9 if query in chapter.title else 0.7,
                    preview=preview
                ))
        
        # 2. 搜索案例
        if 'case' in type_list:
            cases_index = load_cases_index()
            for book_data in cases_index.get("books", []):
                book_slug = book_data.get("slug", "")
                book_title = book_data.get("title", "")
                for case in book_data.get("cases", []):
                    if query.lower() in case.get("title", "").lower() or \
                       query.lower() in case.get("description", "").lower():
                        results.append(SearchResult(
                            type="case",
                            id=case["id"],
                            title=case["title"],
                            description=case.get("description", "")[:200],
                            source=book_title,
                            relevance_score=0.9 if query.lower() in case.get("title", "").lower() else 0.7,
                            preview=None
                        ))
                        if len([r for r in results if r.type == 'case']) >= limit:
                            break
        
        # 3. 搜索知识库
        if 'knowledge' in type_list:
            entries = knowledge_db.query(KnowledgeEntry).filter(
                or_(
                    KnowledgeEntry.title.contains(query),
                    KnowledgeEntry.content.contains(query)
                )
            ).limit(limit).all()
            
            for entry in entries:
                category = knowledge_db.query(Category).filter(Category.id == entry.category_id).first()
                category_name = category.name if category else "未分类"
                
                # 生成预览
                content = entry.content or ""
                preview = ""
                if query in content:
                    idx = content.find(query)
                    start = max(0, idx - 50)
                    end = min(len(content), idx + len(query) + 50)
                    preview = "..." + content[start:end] + "..."
                
                results.append(SearchResult(
                    type="knowledge",
                    id=str(entry.id),
                    title=entry.title,
                    description=entry.summary or content[:200],
                    source=category_name,
                    relevance_score=0.9 if query in entry.title else 0.7,
                    preview=preview
                ))
        
        # 按相关度排序
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        
        # 统计各类型数量
        results_by_type = {
            "textbook": len([r for r in results if r.type == 'textbook']),
            "case": len([r for r in results if r.type == 'case']),
            "knowledge": len([r for r in results if r.type == 'knowledge'])
        }
        
        return {
            "success": True,
            "query": query,
            "total_results": len(results),
            "results_by_type": results_by_type,
            "results": [r.dict() for r in results],
            "suggestions": []  # 可以后续添加建议功能
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/suggestions")
async def get_search_suggestions(
    query: str = Query(..., min_length=1, description="搜索查询词"),
    limit: int = Query(5, ge=1, le=10, description="返回建议数量"),
    textbook_db = Depends(get_textbook_db),
    knowledge_db = Depends(get_knowledge_db)
):
    """获取搜索建议"""
    try:
        from services.textbook.models import TextbookChapter
        from services.knowledge.models import KnowledgeEntry
        
        suggestions = set()
        
        # 从教材标题获取建议
        chapters = textbook_db.query(TextbookChapter.title).filter(
            TextbookChapter.title.contains(query)
        ).limit(limit).all()
        for title, in chapters:
            suggestions.add(title)
        
        # 从知识库标题获取建议
        entries = knowledge_db.query(KnowledgeEntry.title).filter(
            KnowledgeEntry.title.contains(query)
        ).limit(limit).all()
        for title, in entries:
            suggestions.add(title)
        
        return {
            "success": True,
            "query": query,
            "suggestions": sorted(list(suggestions))[:limit]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

