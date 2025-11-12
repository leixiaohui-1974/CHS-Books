#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一搜索API - 跨教材、案例、知识库的全局搜索
"""

from fastapi import APIRouter, Query, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
from pathlib import Path
import json
import re
import sys

# 添加服务路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'services' / 'textbook'))
sys.path.insert(0, str(Path(__file__).parent.parent / 'services' / 'knowledge'))

from services.textbook.database import SessionLocal as TextbookSession
from services.textbook.models import Textbook, TextbookChapter, ChapterCaseMapping
from services.knowledge.database import SessionLocal as KnowledgeSession
from services.knowledge.models import KnowledgeEntry, Category

router = APIRouter(prefix="/api/search", tags=["Unified Search"])

# 案例元数据文件
ENHANCED_CASES_FILE = Path(__file__).parent.parent / "enhanced_cases_metadata.json"


class SearchResult(BaseModel):
    """搜索结果项"""
    type: str  # textbook/case/knowledge
    id: str
    title: str
    description: str
    relevance_score: float
    source: str
    url: str
    preview: Optional[str] = None
    metadata: Dict[str, Any] = {}


class UnifiedSearchResponse(BaseModel):
    """统一搜索响应"""
    query: str
    total_results: int
    results_by_type: Dict[str, int]
    results: List[SearchResult]
    suggestions: List[str] = []


def get_textbook_db():
    """教材数据库依赖"""
    db = TextbookSession()
    try:
        yield db
    finally:
        db.close()


def get_knowledge_db():
    """知识库数据库依赖"""
    db = KnowledgeSession()
    try:
        yield db
    finally:
        db.close()


def load_enhanced_cases() -> List[Dict]:
    """加载增强的案例元数据"""
    if not ENHANCED_CASES_FILE.exists():
        return []
    
    try:
        with open(ENHANCED_CASES_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('cases', [])
    except Exception as e:
        print(f"[WARN] 加载案例元数据失败: {e}")
        return []


def calculate_text_relevance(query: str, text: str) -> float:
    """计算文本相关度（简单的关键词匹配）"""
    if not text:
        return 0.0
    
    query_lower = query.lower()
    text_lower = text.lower()
    
    # 精确匹配
    if query_lower in text_lower:
        return 1.0
    
    # 关键词匹配
    query_words = set(re.findall(r'[\w\u4e00-\u9fa5]+', query_lower))
    text_words = set(re.findall(r'[\w\u4e00-\u9fa5]+', text_lower))
    
    if not query_words:
        return 0.0
    
    intersection = query_words & text_words
    if not intersection:
        return 0.0
    
    # Jaccard相似度
    union = query_words | text_words
    return len(intersection) / len(union)


def search_textbooks(query: str, limit: int, db: Session) -> List[SearchResult]:
    """搜索教材章节"""
    results = []
    
    # 搜索章节标题和内容
    chapters = db.query(TextbookChapter).filter(
        TextbookChapter.title.ilike(f"%{query}%") | 
        TextbookChapter.content.ilike(f"%{query}%")
    ).limit(limit * 2).all()
    
    for chapter in chapters:
        textbook = db.query(Textbook).filter(Textbook.id == chapter.textbook_id).first()
        
        # 计算相关度
        title_relevance = calculate_text_relevance(query, chapter.title)
        content_relevance = calculate_text_relevance(query, chapter.content or "")
        relevance_score = max(title_relevance, content_relevance * 0.8)
        
        # 提取预览文本
        preview = ""
        if chapter.content:
            # 查找包含查询词的段落
            paragraphs = chapter.content.split('\n\n')
            for para in paragraphs:
                if query in para:
                    preview = para[:200] + "..." if len(para) > 200 else para
                    break
            
            if not preview:
                preview = chapter.content[:200] + "..." if len(chapter.content) > 200 else chapter.content
        
        results.append(SearchResult(
            type="textbook",
            id=chapter.id,
            title=f"[{chapter.chapter_number}] {chapter.title}",
            description=textbook.title if textbook else "未知教材",
            relevance_score=relevance_score,
            source=f"{textbook.title} / {chapter.chapter_number}" if textbook else chapter.chapter_number,
            url=f"/textbooks/{chapter.textbook_id}/chapters/{chapter.id}",
            preview=preview,
            metadata={
                "textbook_id": chapter.textbook_id,
                "chapter_number": chapter.chapter_number,
                "level": chapter.level,
                "difficulty": chapter.difficulty.value if chapter.difficulty else None,
                "word_count": chapter.word_count
            }
        ))
    
    # 按相关度排序
    results.sort(key=lambda x: x.relevance_score, reverse=True)
    return results[:limit]


def search_cases(query: str, limit: int) -> List[SearchResult]:
    """搜索案例"""
    results = []
    enhanced_cases = load_enhanced_cases()
    
    for case in enhanced_cases:
        case_id = case.get('id', '')
        title = case.get('title', '')
        
        # 计算相关度
        title_relevance = calculate_text_relevance(query, title)
        
        # 检查控制方法
        control_methods = case.get('control_methods', [])
        methods_text = ' '.join(control_methods)
        methods_relevance = calculate_text_relevance(query, methods_text)
        
        # 检查标签
        tags = case.get('tags', [])
        tags_text = ' '.join(tags)
        tags_relevance = calculate_text_relevance(query, tags_text)
        
        relevance_score = max(title_relevance, methods_relevance * 0.9, tags_relevance * 0.7)
        
        if relevance_score > 0.05:  # 相关度阈值
            book_slug = case.get('book_slug', '')
            
            results.append(SearchResult(
                type="case",
                id=case_id,
                title=title,
                description=f"控制方法: {', '.join(control_methods[:3])}" if control_methods else "案例研究",
                relevance_score=relevance_score,
                source=book_slug,
                url=f"/cases/{case_id}",
                metadata={
                    "book_slug": book_slug,
                    "difficulty": case.get('difficulty'),
                    "estimated_time": case.get('estimated_time'),
                    "control_methods": control_methods,
                    "tags": tags
                }
            ))
    
    # 按相关度排序
    results.sort(key=lambda x: x.relevance_score, reverse=True)
    return results[:limit]


def search_knowledge(query: str, limit: int, db: Session) -> List[SearchResult]:
    """搜索知识库"""
    results = []
    
    # 搜索知识条目
    entries = db.query(KnowledgeEntry).filter(
        KnowledgeEntry.title.ilike(f"%{query}%") | 
        KnowledgeEntry.content.ilike(f"%{query}%")
    ).limit(limit * 2).all()
    
    for entry in entries:
        # 计算相关度
        title_relevance = calculate_text_relevance(query, entry.title)
        content_relevance = calculate_text_relevance(query, entry.content)
        summary_relevance = calculate_text_relevance(query, entry.summary or "")
        
        relevance_score = max(title_relevance, content_relevance * 0.8, summary_relevance * 0.9)
        
        # 提取预览文本
        preview = entry.summary or ""
        if not preview and entry.content:
            preview = entry.content[:200] + "..." if len(entry.content) > 200 else entry.content
        
        category_name = "未分类"
        if entry.category:
            category_name = entry.category.name
        
        results.append(SearchResult(
            type="knowledge",
            id=entry.id,
            title=entry.title,
            description=category_name,
            relevance_score=relevance_score,
            source=entry.source_name or "知识库",
            url=f"/knowledge/{entry.id}",
            preview=preview,
            metadata={
                "category": category_name,
                "level": entry.level.value if entry.level else None,
                "keywords": entry.keywords or [],
                "tags": entry.tags or [],
                "view_count": entry.view_count
            }
        ))
    
    # 按相关度排序
    results.sort(key=lambda x: x.relevance_score, reverse=True)
    return results[:limit]


@router.get("/", response_model=UnifiedSearchResponse)
async def unified_search(
    query: str = Query(..., min_length=1, description="搜索关键词"),
    limit: int = Query(10, ge=1, le=50, description="每种类型的结果数量"),
    types: Optional[str] = Query(None, description="搜索类型（逗号分隔）: textbook,case,knowledge"),
    textbook_db: Session = Depends(get_textbook_db),
    knowledge_db: Session = Depends(get_knowledge_db)
):
    """
    统一搜索接口 - 跨教材、案例、知识库搜索
    
    示例:
    - /api/search?query=PID控制
    - /api/search?query=水箱&types=textbook,case
    - /api/search?query=模型预测&limit=20
    """
    
    # 解析搜索类型
    search_types = ['textbook', 'case', 'knowledge']
    if types:
        search_types = [t.strip() for t in types.split(',') if t.strip() in search_types]
    
    all_results = []
    results_by_type = {}
    
    # 搜索教材
    if 'textbook' in search_types:
        textbook_results = search_textbooks(query, limit, textbook_db)
        all_results.extend(textbook_results)
        results_by_type['textbook'] = len(textbook_results)
    
    # 搜索案例
    if 'case' in search_types:
        case_results = search_cases(query, limit)
        all_results.extend(case_results)
        results_by_type['case'] = len(case_results)
    
    # 搜索知识库
    if 'knowledge' in search_types:
        knowledge_results = search_knowledge(query, limit, knowledge_db)
        all_results.extend(knowledge_results)
        results_by_type['knowledge'] = len(knowledge_results)
    
    # 综合排序（按相关度）
    all_results.sort(key=lambda x: x.relevance_score, reverse=True)
    
    # 生成搜索建议
    suggestions = []
    if len(all_results) == 0:
        suggestions = ["尝试使用更通用的关键词", "检查拼写是否正确", "尝试搜索相关主题"]
    elif len(all_results) < 3:
        suggestions = ["尝试使用更通用的关键词", "浏览相关主题"]
    
    return UnifiedSearchResponse(
        query=query,
        total_results=len(all_results),
        results_by_type=results_by_type,
        results=all_results[:limit * len(search_types)],  # 总结果数限制
        suggestions=suggestions
    )


@router.get("/suggestions")
async def get_search_suggestions(
    query: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=20)
):
    """
    获取搜索建议（自动完成）
    """
    suggestions = []
    
    # 常见的控制方法关键词
    common_keywords = [
        "PID控制", "PI控制", "PD控制", "开关控制",
        "模型预测控制", "MPC", "LQR最优控制", "状态反馈",
        "串级控制", "前馈控制", "自适应控制", "滑模控制",
        "模糊控制", "神经网络控制", "强化学习控制",
        "水箱", "液位控制", "流量控制", "压力控制",
        "系统辨识", "参数整定", "仿真", "建模"
    ]
    
    query_lower = query.lower()
    for keyword in common_keywords:
        if query_lower in keyword.lower():
            suggestions.append(keyword)
    
    return {
        "query": query,
        "suggestions": suggestions[:limit]
    }


@router.get("/stats")
async def get_search_stats(
    textbook_db: Session = Depends(get_textbook_db),
    knowledge_db: Session = Depends(get_knowledge_db)
):
    """
    获取搜索统计信息
    """
    
    # 统计教材
    textbook_count = textbook_db.query(Textbook).count()
    chapter_count = textbook_db.query(TextbookChapter).count()
    
    # 统计知识库
    knowledge_count = knowledge_db.query(KnowledgeEntry).count()
    category_count = knowledge_db.query(Category).count()
    
    # 统计案例
    enhanced_cases = load_enhanced_cases()
    case_count = len(enhanced_cases)
    
    return {
        "textbooks": {
            "total": textbook_count,
            "chapters": chapter_count
        },
        "cases": {
            "total": case_count
        },
        "knowledge": {
            "total": knowledge_count,
            "categories": category_count
        },
        "total_content": textbook_count + case_count + knowledge_count
    }

