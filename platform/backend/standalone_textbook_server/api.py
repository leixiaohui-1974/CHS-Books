"""
Textbooks API - 独立服务器版本
提供section级别的教材内容和代码映射关系
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List, Optional
import re

from database import get_db
from models import Book, Chapter, Case

router = APIRouter()


# ==================== Schemas ====================

class CodeLineMapping(BaseModel):
    """代码行映射"""
    start: int
    end: int


class TextbookSection(BaseModel):
    """教材章节"""
    id: str
    title: str
    content: str
    code_lines: Optional[CodeLineMapping] = None
    order: int


class TextbookContentResponse(BaseModel):
    """教材内容响应"""
    book_slug: str
    chapter_slug: str
    case_slug: str
    title: str
    description: Optional[str]
    sections: List[TextbookSection]
    starter_code: str
    solution_code: Optional[str]
    difficulty: str
    estimated_minutes: int
    tags: List[str]


# ==================== API Endpoints ====================

@router.get("/{book_slug}/{chapter_slug}/{case_slug}")
async def get_textbook_content(
    book_slug: str,
    chapter_slug: str,
    case_slug: str,
    db: AsyncSession = Depends(get_db)
) -> TextbookContentResponse:
    """
    获取教材详细内容（支持左文右码）
    """
    print(f"📖 获取教材内容: {book_slug}/{chapter_slug}/{case_slug}")

    # 1. 查询书籍
    stmt = select(Book).where(Book.slug == book_slug)
    result = await db.execute(stmt)
    book = result.scalar_one_or_none()

    if not book:
        raise HTTPException(status_code=404, detail=f"书籍 '{book_slug}' 不存在")

    # 2. 查询章节
    stmt = select(Chapter).where(
        Chapter.book_id == book.id,
        Chapter.slug == chapter_slug
    )
    result = await db.execute(stmt)
    chapter = result.scalar_one_or_none()

    if not chapter:
        raise HTTPException(status_code=404, detail=f"章节 '{chapter_slug}' 不存在")

    # 3. 查询案例
    stmt = select(Case).where(
        Case.chapter_id == chapter.id,
        Case.slug == case_slug
    )
    result = await db.execute(stmt)
    case = result.scalar_one_or_none()

    if not case:
        raise HTTPException(status_code=404, detail=f"案例 '{case_slug}' 不存在")

    # 4. 解析教材内容
    sections = parse_content_to_sections(
        content=case.description or "",
        code=case.starter_code or ""
    )

    # 5. 构建响应
    response = TextbookContentResponse(
        book_slug=book_slug,
        chapter_slug=chapter_slug,
        case_slug=case_slug,
        title=case.title,
        description=case.description,
        sections=sections,
        starter_code=case.starter_code or "",
        solution_code=case.solution_code,
        difficulty=case.difficulty or "beginner",
        estimated_minutes=case.estimated_minutes or 30,
        tags=case.tags or []
    )

    print(f"✅ 返回 {len(sections)} 个sections")
    return response


# ==================== Helper Functions ====================

def parse_content_to_sections(content: str, code: str) -> List[TextbookSection]:
    """
    解析教材内容，生成sections并映射到代码行
    """
    sections = []

    # 按二级标题分割内容
    parts = re.split(r'^## (.+)$', content, flags=re.MULTILINE)

    if len(parts) == 1:
        # 没有标题，整个内容作为一个section
        sections.append(TextbookSection(
            id="intro",
            title="介绍",
            content=content,
            code_lines=None,
            order=0
        ))
    else:
        order = 0

        # 如果有标题前的内容，作为intro section
        if parts[0].strip():
            sections.append(TextbookSection(
                id="intro",
                title="介绍",
                content=parts[0].strip(),
                code_lines=None,
                order=order
            ))
            order += 1

        # 处理标题和内容
        for i in range(1, len(parts), 2):
            if i + 1 < len(parts):
                title = parts[i].strip()
                section_content = parts[i + 1].strip()

                # 生成section ID
                section_id = title.lower().replace(' ', '-').replace(':', '')
                section_id = re.sub(r'[^\w\-]', '', section_id)

                # 分析代码引用
                code_lines = extract_code_line_mapping(section_content, code)

                sections.append(TextbookSection(
                    id=section_id,
                    title=title,
                    content=section_content,
                    code_lines=code_lines,
                    order=order
                ))
                order += 1

    return sections


def extract_code_line_mapping(content: str, code: str) -> Optional[CodeLineMapping]:
    """
    从教材内容中提取代码行映射

    支持的标记：
    - [代码行 15-20] → 映射到第15-20行
    - (#code-line-15) → 映射到第15行
    """
    # 查找 [代码行 X-Y] 格式
    match = re.search(r'\[代码行\s+(\d+)-(\d+)\]', content)
    if match:
        start = int(match.group(1))
        end = int(match.group(2))
        return CodeLineMapping(start=start, end=end)

    # 查找 (#code-line-X) 格式
    match = re.search(r'#code-line-(\d+)', content)
    if match:
        line = int(match.group(1))
        return CodeLineMapping(start=line, end=line)

    return None
