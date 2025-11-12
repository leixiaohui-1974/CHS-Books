"""
教材内容API - 支持左文右码功能
提供section级别的教材内容和代码映射关系
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List, Optional, Dict
from loguru import logger

from app.core.database import get_db
from app.models.book import Book, Chapter, Case

router = APIRouter()


# ========================================
# Pydantic Schemas
# ========================================

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


# ========================================
# API Endpoints
# ========================================

@router.get("/{book_slug}/{chapter_slug}/{case_slug}")
async def get_textbook_content(
    book_slug: str,
    chapter_slug: str,
    case_slug: str,
    db: AsyncSession = Depends(get_db)
) -> TextbookContentResponse:
    """
    获取教材详细内容（支持左文右码）

    返回内容包括：
    - 分段的教材内容（sections）
    - 每个section对应的代码行范围
    - 初始代码和参考解决方案
    """
    logger.info(f"📖 获取教材内容: {book_slug}/{chapter_slug}/{case_slug}")

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

    # 4. 解析教材内容，生成sections
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

    logger.info(f"✅ 返回 {len(sections)} 个sections")
    return response


@router.get("/{book_slug}/{chapter_slug}/{case_slug}/sections/{section_id}")
async def get_section_detail(
    book_slug: str,
    chapter_slug: str,
    case_slug: str,
    section_id: str,
    db: AsyncSession = Depends(get_db)
) -> TextbookSection:
    """
    获取单个section的详细信息
    """
    logger.info(f"📄 获取section详情: {section_id}")

    # 先获取完整内容
    content = await get_textbook_content(book_slug, chapter_slug, case_slug, db)

    # 查找指定section
    for section in content.sections:
        if section.id == section_id:
            return section

    raise HTTPException(status_code=404, detail=f"Section '{section_id}' 不存在")


# ========================================
# 辅助函数
# ========================================

def parse_content_to_sections(content: str, code: str) -> List[TextbookSection]:
    """
    解析教材内容，生成sections并映射到代码行

    解析规则：
    1. 以 ## 二级标题作为section分隔
    2. 每个section包含标题和内容
    3. 自动分析content中的代码引用，映射到代码行
    """
    sections = []

    # 按二级标题分割内容
    import re
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
        # 有标题的情况
        # parts[0] 是标题前的内容（可能为空）
        # parts[1], parts[2], parts[3], parts[4] ... 交替为标题和内容

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

                # 生成section ID（标题转小写，空格转-)
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
    import re

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

    # 如果没有明确标记，尝试智能匹配
    # 这里可以添加更复杂的逻辑，比如关键词匹配等

    return None


# ========================================
# 测试数据生成（开发用）
# ========================================

@router.post("/dev/seed-example")
async def seed_example_textbook(db: AsyncSession = Depends(get_db)):
    """
    创建示例教材数据（仅开发环境）
    """
    logger.info("🌱 创建示例教材数据")

    # 1. 创建或获取书籍
    stmt = select(Book).where(Book.slug == "water-system-intro")
    result = await db.execute(stmt)
    book = result.scalar_one_or_none()

    if not book:
        book = Book(
            slug="water-system-intro",
            title="智慧水利入门",
            description="从零开始学习智慧水利系统",
            difficulty="beginner",
            status="published",
            is_free=True,
            price=0.0,
            estimated_hours=5,
            tags=["水利", "入门", "Python"]
        )
        db.add(book)
        await db.flush()

    # 2. 创建章节
    stmt = select(Chapter).where(
        Chapter.book_id == book.id,
        Chapter.slug == "chapter-01"
    )
    result = await db.execute(stmt)
    chapter = result.scalar_one_or_none()

    if not chapter:
        chapter = Chapter(
            book_id=book.id,
            slug="chapter-01",
            title="第一章：基础概念",
            order=1,
            content="# 第一章\n\n这是第一章的内容"
        )
        db.add(chapter)
        await db.flush()

    # 3. 创建案例
    stmt = select(Case).where(
        Case.chapter_id == chapter.id,
        Case.slug == "case-water-tank"
    )
    result = await db.execute(stmt)
    case = result.scalar_one_or_none()

    if not case:
        case = Case(
            chapter_id=chapter.id,
            slug="case-water-tank",
            title="案例1：水箱实验",
            order=1,
            difficulty="beginner",
            estimated_minutes=30,
            description="""
## 实验目标

在这个实验中，我们将学习如何模拟一个简单的水箱系统。

## 物理原理

水箱的水量变化遵循质量守恒定律：

$$\\frac{dV}{dt} = Q_{in} - Q_{out}$$

其中：
- $V$ 是水箱中的水量（立方米）
- $Q_{in}$ 是入流量（立方米/秒）
- $Q_{out}$ 是出流量（立方米/秒）

## 数值求解

我们使用欧拉法进行数值积分 [代码行 8-10]：

```python
V = V + (Qin - Qout) * dt
```

## 可视化结果

最后，我们绘制水量随时间的变化曲线 [代码行 14-16]。

## 思考题

1. 如果入流量大于出流量，水量会如何变化？
2. 如果要保持水量恒定，应该如何调整？
            """,
            starter_code="""# 水箱实验
# 初始化参数
V = 100.0  # 初始水量 (m³)
Qin = 10.0  # 入流量 (m³/s)
Qout = 8.0  # 出流量 (m³/s)
dt = 1.0  # 时间步长 (s)
T = 100  # 总时间 (s)

# 数值求解
time_list = []
volume_list = []

for t in range(T):
    V = V + (Qin - Qout) * dt
    time_list.append(t)
    volume_list.append(V)

# 可视化
import matplotlib.pyplot as plt

plt.figure(figsize=(10, 6))
plt.plot(time_list, volume_list, linewidth=2)
plt.xlabel('时间 (秒)')
plt.ylabel('水量 (立方米)')
plt.title('水箱水量变化')
plt.grid(True)
plt.show()

print(f"最终水量: {V:.2f} 立方米")
""",
            solution_code="""# 完整解决方案（带注释）
import matplotlib.pyplot as plt

# 初始化参数
V = 100.0  # 初始水量 (m³)
Qin = 10.0  # 入流量 (m³/s)
Qout = 8.0  # 出流量 (m³/s)
dt = 1.0  # 时间步长 (s)
T = 100  # 总时间 (s)

# 存储数据
time_list = []
volume_list = []

# 数值求解（欧拉法）
for t in range(T):
    # 质量守恒方程
    dV_dt = Qin - Qout
    V = V + dV_dt * dt

    # 记录数据
    time_list.append(t)
    volume_list.append(V)

# 可视化
plt.figure(figsize=(12, 6))

# 子图1：水量变化
plt.subplot(1, 2, 1)
plt.plot(time_list, volume_list, 'b-', linewidth=2, label='水量')
plt.axhline(y=100, color='r', linestyle='--', label='初始水量')
plt.xlabel('时间 (秒)')
plt.ylabel('水量 (立方米)')
plt.title('水箱水量随时间变化')
plt.legend()
plt.grid(True)

# 子图2：变化率
plt.subplot(1, 2, 2)
plt.axhline(y=Qin-Qout, color='g', linewidth=2)
plt.xlabel('时间 (秒)')
plt.ylabel('变化率 (m³/s)')
plt.title('水量变化率（恒定）')
plt.grid(True)

plt.tight_layout()
plt.show()

# 输出结果
print(f"初始水量: 100.00 立方米")
print(f"最终水量: {V:.2f} 立方米")
print(f"水量增加: {V - 100:.2f} 立方米")
print(f"理论值: {(Qin - Qout) * T:.2f} 立方米")
""",
            tags=["水箱", "质量守恒", "数值模拟"]
        )
        db.add(case)

    await db.commit()

    logger.info("✅ 示例教材数据创建成功")

    return {
        "message": "示例教材数据已创建",
        "book_slug": "water-system-intro",
        "chapter_slug": "chapter-01",
        "case_slug": "case-water-tank",
        "preview_url": "/api/v1/textbooks/water-system-intro/chapter-01/case-water-tank"
    }
