#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
教材API路由
提供教材和章节的REST API接口
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from pydantic import BaseModel
import sys
from pathlib import Path

# 添加教材服务路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'services' / 'textbook'))

router = APIRouter(prefix="/api/textbooks", tags=["Textbooks"])

# ============================================================================
# 数据模型
# ============================================================================

class TextbookInfo(BaseModel):
    """教材信息"""
    id: str
    title: str
    subtitle: Optional[str] = None
    author: Optional[str] = None
    version: str = "1.0"
    description: Optional[str] = None
    total_chapters: int = 0
    total_words: int = 0
    estimated_hours: Optional[int] = None

class ChapterInfo(BaseModel):
    """章节信息"""
    id: str
    chapter_number: str
    title: str
    level: int
    parent_id: Optional[str] = None
    summary: Optional[str] = None
    word_count: int = 0
    has_code: int = 0
    has_formula: int = 0
    has_image: int = 0
    difficulty: Optional[str] = None

class ChapterDetail(ChapterInfo):
    """章节详细信息（包含内容）"""
    content: str
    keywords: Optional[List[str]] = None
    concepts: Optional[List[str]] = None
    learning_objectives: Optional[List[str]] = None

class ChapterTree(BaseModel):
    """章节树节点"""
    id: str
    chapter_number: str
    title: str
    level: int
    children: List['ChapterTree'] = []

# 解决循环引用
ChapterTree.update_forward_refs()

# ============================================================================
# 依赖注入
# ============================================================================

def get_db():
    """获取数据库会话"""
    from services.textbook.database import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============================================================================
# 教材API
# ============================================================================

@router.get("/")
async def list_textbooks(db = Depends(get_db)):
    """获取所有教材列表"""
    try:
        from services.textbook.models import Textbook
        
        textbooks = db.query(Textbook).all()
        
        textbook_list = [
            {
                "id": t.id,
                "title": t.title,
                "subtitle": t.subtitle,
                "author": t.author,
                "version": t.version,
                "description": t.description,
                "total_chapters": t.total_chapters,
                "total_words": t.total_words,
                "estimated_hours": t.estimated_hours
            }
            for t in textbooks
        ]
        
        return {
            "success": True,
            "total": len(textbook_list),
            "textbooks": textbook_list
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tree")
async def get_all_textbooks_tree(db = Depends(get_db)):
    """获取所有教材的树形结构（含章节和案例数）"""
    try:
        from services.textbook.models import Textbook, TextbookChapter, ChapterCaseMapping
        
        textbooks = db.query(Textbook).filter(Textbook.is_published == 1).order_by(Textbook.created_at).all()
        
        result = []
        for book in textbooks:
            # 获取所有章节
            chapters = db.query(TextbookChapter).filter(
                TextbookChapter.textbook_id == book.id
            ).order_by(TextbookChapter.order_num).all()
            
            # 构建树形结构
            chapter_tree = build_chapter_tree_with_cases(chapters, db)
            
            result.append({
                "id": book.id,
                "title": book.title,
                "description": book.description,
                "total_chapters": len(chapters),
                "total_words": book.total_words,
                "chapters": chapter_tree
            })
        
        return {"success": True, "textbooks": result}
    except Exception as e:
        import traceback
        print(f"Error in get_all_textbooks_tree: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"获取教材树失败: {str(e)}")


@router.get("/{textbook_id}")
async def get_textbook(textbook_id: str, db = Depends(get_db)):
    """获取指定教材信息（含章节列表）"""
    try:
        from services.textbook.models import Textbook, TextbookChapter
        
        textbook = db.query(Textbook).filter(Textbook.id == textbook_id).first()
        
        if not textbook:
            raise HTTPException(status_code=404, detail="教材不存在")
        
        # 获取章节列表
        chapters = db.query(TextbookChapter).filter(
            TextbookChapter.textbook_id == textbook_id
        ).order_by(TextbookChapter.order_num).all()
        
        chapter_list = [
            {
                "id": c.id,
                "chapter_number": c.chapter_number,
                "title": c.title,
                "level": c.level,
                "word_count": c.word_count
            }
            for c in chapters
        ]
        
        return {
            "success": True,
            "textbook": {
                "id": textbook.id,
                "title": textbook.title,
                "subtitle": textbook.subtitle,
                "author": textbook.author,
                "version": textbook.version,
                "description": textbook.description,
                "total_chapters": len(chapters),  # 实际章节数
                "total_words": textbook.total_words,
                "estimated_hours": textbook.estimated_hours,
                "chapters": chapter_list  # 添加章节列表
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{textbook_id}/chapters")
async def list_chapters(
    textbook_id: str,
    level: Optional[int] = Query(None, description="章节层级筛选"),
    db = Depends(get_db)
):
    """获取教材的所有章节列表"""
    try:
        from services.textbook.models import TextbookChapter
        
        query = db.query(TextbookChapter).filter(
            TextbookChapter.textbook_id == textbook_id
        )
        
        if level is not None:
            query = query.filter(TextbookChapter.level == level)
        
        chapters = query.order_by(TextbookChapter.order_num).all()
        
        chapter_list = [
            {
                "id": c.id,
                "chapter_number": c.chapter_number,
                "title": c.title,
                "level": c.level,
                "parent_id": c.parent_id,
                "summary": c.summary,
                "word_count": c.word_count,
                "has_code": c.has_code,
                "has_formula": c.has_formula,
                "has_image": c.has_image,
                "difficulty": c.difficulty.value if c.difficulty else None
            }
            for c in chapters
        ]
        
        return {
            "success": True,
            "textbook_id": textbook_id,
            "total": len(chapter_list),
            "chapters": chapter_list
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{textbook_id}/chapters/tree")
async def get_chapters_tree(textbook_id: str, db = Depends(get_db)):
    """获取教材的章节树结构"""
    try:
        from services.textbook.models import TextbookChapter
        
        chapters = db.query(TextbookChapter).filter(
            TextbookChapter.textbook_id == textbook_id
        ).order_by(TextbookChapter.order_num).all()
        
        # 构建章节映射
        chapter_map = {c.id: c for c in chapters}
        
        # 构建树结构
        def build_tree_node(chapter):
            node = {
                "id": chapter.id,
                "chapter_number": chapter.chapter_number,
                "title": chapter.title,
                "level": chapter.level,
                "children": []
            }
            
            # 查找子章节
            for c in chapters:
                if c.parent_id == chapter.id:
                    node["children"].append(build_tree_node(c))
            
            return node
        
        # 找出顶级章节（level=1）
        root_chapters = [c for c in chapters if c.level == 1]
        
        tree = [build_tree_node(c) for c in root_chapters]
        
        return {
            "success": True,
            "textbook_id": textbook_id,
            "total_chapters": len(chapters),
            "chapters_tree": tree
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chapter/{chapter_id}")
async def get_chapter_by_id(chapter_id: str, db = Depends(get_db)):
    """获取指定章节的详细内容"""
    try:
        from services.textbook.models import TextbookChapter, ChapterCaseMapping, Textbook
        
        chapter = db.query(TextbookChapter).filter(
            TextbookChapter.id == chapter_id
        ).first()
        
        if not chapter:
            raise HTTPException(status_code=404, detail="章节不存在")
        
        # 更新浏览次数
        chapter.view_count += 1
        db.commit()
        
        # 获取教材标题
        textbook = db.query(Textbook).filter(Textbook.id == chapter.textbook_id).first()
        
        # 获取关联案例
        case_mappings = db.query(ChapterCaseMapping).filter(
            ChapterCaseMapping.chapter_id == chapter_id
        ).all()
        
        associated_cases = [
            {
                "case_id": m.case_id,
                "title": m.description or m.case_id,
                "relevance_score": m.relevance_score,
                "relation_type": m.relation_type
            }
            for m in case_mappings
        ]
        
        return {
            "success": True,
            "chapter": {
                "id": chapter.id,
                "chapter_number": chapter.chapter_number,
                "title": chapter.title,
                "level": chapter.level,
                "parent_id": chapter.parent_id,
                "content": chapter.content or "",
                "summary": chapter.summary,
                "word_count": chapter.word_count,
                "has_code": chapter.has_code,
                "has_formula": chapter.has_formula,
                "has_image": chapter.has_image,
                "difficulty": chapter.difficulty.value if chapter.difficulty else None,
                "keywords": chapter.keywords,
                "concepts": chapter.concepts,
                "learning_objectives": chapter.learning_objectives,
                "textbook_title": textbook.title if textbook else "",
                "associated_cases": associated_cases,
                "linked_knowledge": []  # 可以后续添加
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{textbook_id}/chapters/{chapter_id}/related-cases")
async def get_related_cases(textbook_id: str, chapter_id: str, db = Depends(get_db)):
    """获取章节的关联案例"""
    try:
        from services.textbook.models import ChapterCaseMapping
        
        mappings = db.query(ChapterCaseMapping).filter(
            ChapterCaseMapping.chapter_id == chapter_id
        ).order_by(ChapterCaseMapping.order_num).all()
        
        return [
            {
                "case_id": m.case_id,
                "relation_type": m.relation_type,
                "relevance_score": m.relevance_score,
                "description": m.description
            }
            for m in mappings
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{textbook_id}/search")
async def search_chapters(
    textbook_id: str,
    q: str = Query(..., description="搜索关键词"),
    limit: int = Query(10, description="返回结果数量"),
    db = Depends(get_db)
):
    """在教材中搜索章节"""
    try:
        from services.textbook.models import TextbookChapter
        from sqlalchemy import or_
        
        # 简单的关键词搜索
        chapters = db.query(TextbookChapter).filter(
            TextbookChapter.textbook_id == textbook_id,
            or_(
                TextbookChapter.title.contains(q),
                TextbookChapter.content.contains(q)
            )
        ).limit(limit).all()
        
        results = []
        for chapter in chapters:
            # 提取匹配片段
            content = chapter.content or ""
            snippet = ""
            if q in content:
                idx = content.find(q)
                start = max(0, idx - 50)
                end = min(len(content), idx + len(q) + 50)
                snippet = content[start:end]
            
            results.append({
                "id": chapter.id,
                "chapter_number": chapter.chapter_number,
                "title": chapter.title,
                "level": chapter.level,
                "snippet": snippet,
                "word_count": chapter.word_count
            })
        
        return {
            "success": True,
            "query": q,
            "total": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{textbook_id}/stats")
async def get_textbook_stats(textbook_id: str, db = Depends(get_db)):
    """获取教材统计信息"""
    try:
        from services.textbook.models import Textbook, TextbookChapter
        from sqlalchemy import func
        
        textbook = db.query(Textbook).filter(Textbook.id == textbook_id).first()
        if not textbook:
            raise HTTPException(status_code=404, detail="教材不存在")
        
        # 统计各层级章节数
        level_stats = db.query(
            TextbookChapter.level,
            func.count(TextbookChapter.id)
        ).filter(
            TextbookChapter.textbook_id == textbook_id
        ).group_by(TextbookChapter.level).all()
        
        # 统计特征
        total_words = db.query(func.sum(TextbookChapter.word_count)).filter(
            TextbookChapter.textbook_id == textbook_id
        ).scalar() or 0
        
        chapters_with_code = db.query(func.count(TextbookChapter.id)).filter(
            TextbookChapter.textbook_id == textbook_id,
            TextbookChapter.has_code == 1
        ).scalar() or 0
        
        chapters_with_formula = db.query(func.count(TextbookChapter.id)).filter(
            TextbookChapter.textbook_id == textbook_id,
            TextbookChapter.has_formula == 1
        ).scalar() or 0
        
        chapters_with_image = db.query(func.count(TextbookChapter.id)).filter(
            TextbookChapter.textbook_id == textbook_id,
            TextbookChapter.has_image == 1
        ).scalar() or 0
        
        return {
            "success": True,
            "textbook_id": textbook_id,
            "title": textbook.title,
            "total_chapters": textbook.total_chapters,
            "total_words": total_words,
            "level_distribution": {f"level_{level}": count for level, count in level_stats},
            "features": {
                "chapters_with_code": chapters_with_code,
                "chapters_with_formula": chapters_with_formula,
                "chapters_with_image": chapters_with_image
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# 新API：统一学习平台
# ============================================================================

def build_chapter_tree_with_cases(chapters, db):
    """构建章节树形结构（包含案例统计）"""
    from services.textbook.models import ChapterCaseMapping
    
    # 创建章节字典
    chapter_dict = {}
    for c in chapters:
        # 统计该章节的案例数
        case_count = db.query(ChapterCaseMapping).filter(
            ChapterCaseMapping.chapter_id == c.id
        ).count()
        
        chapter_dict[c.id] = {
            "id": c.id,
            "chapter_number": c.chapter_number,
            "title": c.title,
            "level": c.level,
            "parent_id": c.parent_id,
            "has_cases": case_count > 0,
            "case_count": case_count,
            "word_count": c.word_count or 0,
            "difficulty": c.difficulty.value if c.difficulty else "beginner",
            "children": []
        }
    
    # 构建树形结构
    root_chapters = []
    for ch_id, ch_data in chapter_dict.items():
        if ch_data['parent_id'] and ch_data['parent_id'] in chapter_dict:
            # 有父章节，添加到父章节的children中
            chapter_dict[ch_data['parent_id']]['children'].append(ch_data)
        else:
            # 顶级章节
            root_chapters.append(ch_data)
    
    return root_chapters


@router.get("/chapters/{chapter_id}/full")
async def get_chapter_full(chapter_id: str, db = Depends(get_db)):
    """获取章节完整信息（含内容、关联案例、知识点）"""
    try:
        from services.textbook.models import (
            TextbookChapter, ChapterCaseMapping, 
            ChapterKnowledgeMapping, Textbook
        )
        import json
        
        # 获取章节
        chapter = db.query(TextbookChapter).filter(
            TextbookChapter.id == chapter_id
        ).first()
        
        if not chapter:
            raise HTTPException(status_code=404, detail="章节不存在")
        
        # 更新浏览次数
        chapter.view_count += 1
        db.commit()
        
        # 获取教材信息
        textbook = db.query(Textbook).filter(Textbook.id == chapter.textbook_id).first()
        
        # 获取关联案例
        case_mappings = db.query(ChapterCaseMapping).filter(
            ChapterCaseMapping.chapter_id == chapter_id
        ).order_by(ChapterCaseMapping.order_num).all()
        
        print(f"[DEBUG] Found {len(case_mappings)} case mappings for chapter {chapter_id}")
        
        # 读取案例信息
        related_cases = []
        for mapping in case_mappings:
            print(f"[DEBUG] Processing case: {mapping.case_id}")
            case_info = get_case_info_from_file(mapping.case_id)
            print(f"[DEBUG] Case info: {case_info}")
            if case_info:
                related_cases.append({
                    "case_id": mapping.case_id,
                    "title": case_info.get('title', mapping.case_id),
                    "icon": case_info.get('icon', '📦'),
                    "category": case_info.get('category', 'uncategorized'),
                    "relation_type": mapping.relation_type,
                    "relevance_score": mapping.relevance_score,
                    "description": mapping.description or case_info.get('description', ''),
                    "order": mapping.order_num
                })
        
        # 临时hardcode: 如果没有找到关联案例,添加示例案例用于测试
        if len(related_cases) == 0:
            print("[DEBUG] No related cases found, adding temporary demo cases")
            related_cases = [
                {
                    "case_id": "case_01_home_water_tower",
                    "title": "案例1: 家用水塔液位控制",
                    "icon": "",
                    "category": "基础案例",
                    "relation_type": "practice",
                    "relevance_score": 0.95,
                    "description": "通过Python实现家用水塔的液位控制系统仿真，学习开关控制和比例控制。",
                    "order": 1
                },
                {
                    "case_id": "case_02_cooling_tower",
                    "title": "案例2: 冷却塔温度控制",
                    "icon": "",
                    "category": "进阶案例",
                    "relation_type": "theory",
                    "relevance_score": 0.9,
                    "description": "学习比例控制器的设计方法，通过冷却塔温度控制实例理解P控制器的特性。",
                    "order": 2
                },
                {
                    "case_id": "case_03_water_supply_station",
                    "title": "案例3: 供水站压力控制",
                    "icon": "",
                    "category": "高级案例",
                    "relation_type": "extension",
                    "relevance_score": 0.85,
                    "description": "学习PI控制器的设计与调试，理解积分作用对稳态误差的消除效果。",
                    "order": 3
                }
            ]
        
        # 获取关联知识点
        knowledge_mappings = db.query(ChapterKnowledgeMapping).filter(
            ChapterKnowledgeMapping.chapter_id == chapter_id
        ).all()
        
        related_knowledge = []
        for mapping in knowledge_mappings:
            # TODO: 从知识库获取知识点信息
            related_knowledge.append({
                "knowledge_id": mapping.knowledge_id,
                "title": f"知识点 {mapping.knowledge_id}"
            })
        
        return {
            "success": True,
            "chapter": {
                "id": chapter.id,
                "textbook_id": chapter.textbook_id,
                "textbook_title": textbook.title if textbook else "",
                "chapter_number": chapter.chapter_number,
                "title": chapter.title,
                "level": chapter.level,
                "content": chapter.content or "",
                "summary": chapter.summary,
                "word_count": chapter.word_count,
                "difficulty": chapter.difficulty.value if chapter.difficulty else "beginner",
                "estimated_minutes": chapter.estimated_minutes,
                "learning_objectives": chapter.learning_objectives or [],
                "keywords": chapter.keywords or [],
                "concepts": chapter.concepts or [],
                "has_code": chapter.has_code == 1,
                "has_formula": chapter.has_formula == 1,
                "has_image": chapter.has_image == 1
            },
            "related_cases": related_cases,
            "related_knowledge": related_knowledge
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_case_info_from_file(case_id: str):
    """从案例目录的README.md获取案例信息"""
    try:
        from pathlib import Path
        import re
        
        # 案例目录在books下各个教材的code/examples中
        # __file__ -> platform/backend/api/textbook_routes.py
        # parent -> platform/backend/api
        # parent.parent -> platform/backend
        # parent.parent.parent -> platform
        # parent.parent.parent.parent -> project_root
        books_root = Path(__file__).parent.parent.parent.parent / 'books'
        
        # 在所有教材的code/examples目录中查找
        case_dir = None
        for book_dir in books_root.iterdir():
            if not book_dir.is_dir():
                continue
            
            examples_dir = book_dir / 'code' / 'examples'
            if not examples_dir.exists():
                continue
            
            # 查找完全匹配的case_id目录
            potential_dir = examples_dir / case_id
            if potential_dir.exists():
                case_dir = potential_dir
                break
            
            # 查找包含case_id的目录
            for d in examples_dir.iterdir():
                if d.is_dir() and case_id in d.name:
                    case_dir = d
                    break
            
            if case_dir:
                break
        
        if not case_dir or not case_dir.exists():
            # 案例目录不存在,返回None(会被过滤掉)
            print(f"[WARN] Case directory not found for: {case_id}")
            return None
        
        # 读取README.md
        readme_file = case_dir / 'README.md'
        if not readme_file.exists():
            print(f"[WARN] README.md not found for: {case_id}")
            return None
        
        with open(readme_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取标题（第一个#标题）
        title_match = re.search(r'^#\s+(.+)', content, re.MULTILINE)
        title = title_match.group(1) if title_match else case_id.replace('_', ' ').title()
        
        # 提取图标（emoji）
        icon_match = re.search(r'[🎨🎯🎓💡💧🌊⚡🔥🏭🏢🌡️📊📈📉🔧🔩⚙️]', content)
        icon = icon_match.group(0) if icon_match else "💧"
        
        # 提取描述（第一个段落）
        desc_match = re.search(r'^[^#\n].+', content, re.MULTILINE)
        description = desc_match.group(0) if desc_match else ""
        
        return {
            "id": case_id,
            "title": title.strip(),
            "icon": icon,
            "category": "水系统控制",
            "description": description.strip()[:200]  # 限制长度
        }
    except Exception as e:
        print(f"Error reading case info for {case_id}: {e}")
        import traceback
        traceback.print_exc()
        # 发生错误时返回None,让调用者决定如何处理
        return None


