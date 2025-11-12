#!/usr/bin/env python3
"""
快速测试教材API - 验证功能

运行: python test_textbook_api.py
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# 测试数据库URL (SQLite内存数据库)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


async def test_textbook_parsing():
    """测试教材内容解析"""
    from app.api.endpoints.textbooks import parse_content_to_sections

    # 测试内容
    content = """
## 实验目标

这是第一个section的内容。

## 物理原理

这是第二个section的内容 [代码行 5-10]。

## 数值求解

这是第三个section的内容。
    """

    code = """
# 示例代码
V = 100
Qin = 10
Qout = 8

for t in range(100):
    V = V + (Qin - Qout) * dt

print(V)
    """

    sections = parse_content_to_sections(content, code)

    print("\n" + "="*60)
    print("📚 教材内容解析测试")
    print("="*60)
    print(f"\n解析结果: 找到 {len(sections)} 个 sections\n")

    for section in sections:
        print(f"Section ID: {section.id}")
        print(f"  标题: {section.title}")
        print(f"  内容长度: {len(section.content)} 字符")
        if section.code_lines:
            print(f"  代码行: {section.code_lines.start}-{section.code_lines.end}")
        else:
            print(f"  代码行: 无")
        print()

    assert len(sections) == 3, f"期望3个sections，实际{len(sections)}个"
    assert sections[1].code_lines is not None, "第二个section应该有代码行映射"
    assert sections[1].code_lines.start == 5, f"代码起始行应该是5，实际是{sections[1].code_lines.start}"
    assert sections[1].code_lines.end == 10, f"代码结束行应该是10，实际是{sections[1].code_lines.end}"

    print("✅ 所有测试通过！")


async def test_database_models():
    """测试数据库模型"""
    print("\n" + "="*60)
    print("💾 数据库模型测试")
    print("="*60)

    # 创建测试引擎
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    # 创建所有表
    from app.core.database import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 创建会话
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        # 导入模型
        from app.models.book import Book, Chapter, Case

        # 创建测试数据
        book = Book(
            slug="test-book",
            title="测试书籍",
            description="这是一个测试",
            difficulty="beginner",
            status="published",
            is_free=True,
            price=0.0,
            estimated_hours=1,
            tags=["测试"]
        )
        session.add(book)
        await session.flush()

        chapter = Chapter(
            book_id=book.id,
            slug="test-chapter",
            title="测试章节",
            order=1
        )
        session.add(chapter)
        await session.flush()

        case = Case(
            chapter_id=chapter.id,
            slug="test-case",
            title="测试案例",
            order=1,
            difficulty="beginner",
            estimated_minutes=30,
            description="测试描述",
            starter_code="print('Hello')",
            tags=["测试"]
        )
        session.add(case)
        await session.commit()

        print(f"\n✅ 成功创建:")
        print(f"  - 书籍: {book.title} (ID: {book.id})")
        print(f"  - 章节: {chapter.title} (ID: {chapter.id})")
        print(f"  - 案例: {case.title} (ID: {case.id})")

    await engine.dispose()
    print("\n✅ 数据库模型测试通过！")


async def main():
    """主测试函数"""
    print("\n" + "🚀 "*20)
    print("开始测试教材API功能")
    print("🚀 "*20)

    try:
        # 测试1: 内容解析
        await test_textbook_parsing()

        # 测试2: 数据库模型
        await test_database_models()

        print("\n" + "="*60)
        print("🎉 所有测试通过！")
        print("="*60)
        print("\n下一步:")
        print("1. 运行快速启动脚本: ./scripts/quick_start.sh")
        print("2. 启动后端服务器: uvicorn app.main:app --reload")
        print("3. 访问API文档: http://localhost:8000/docs")
        print("4. 测试新端点: GET /api/v1/textbooks/{book}/{chapter}/{case}")
        print()

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))
