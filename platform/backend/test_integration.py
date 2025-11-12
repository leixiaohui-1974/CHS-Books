#!/usr/bin/env python3
"""
集成测试 - 验证教材API完整流程

测试流程:
1. 启动数据库
2. 创建测试数据
3. 测试API端点
4. 验证响应格式
5. 测试section解析
6. 测试代码行映射

运行: python test_integration.py
"""

import asyncio
import sys
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from loguru import logger

# 配置日志
logger.remove()
logger.add(sys.stdout, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{message}</level>")

# 测试数据库URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


async def test_full_integration():
    """完整集成测试"""

    print("\n" + "=" * 80)
    print("🚀 开始集成测试：教材API完整流程")
    print("=" * 80)

    # ========================================
    # 步骤1: 创建数据库引擎
    # ========================================
    logger.info("📦 步骤1: 创建数据库引擎")
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    # 创建所有表
    from app.core.database import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.success("✅ 数据库表创建成功")

    # 创建会话
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    # ========================================
    # 步骤2: 创建测试数据
    # ========================================
    logger.info("\n📦 步骤2: 创建测试数据")

    from app.models.book import Book, Chapter, Case

    async with async_session() as session:
        # 创建书籍
        book = Book(
            slug="test-water-intro",
            title="智慧水利入门（测试）",
            description="测试数据",
            difficulty="beginner",
            status="published",
            is_free=True,
            price=0.0,
            estimated_hours=5,
            tags=["测试", "水利"]
        )
        session.add(book)
        await session.flush()

        # 创建章节
        chapter = Chapter(
            book_id=book.id,
            slug="test-chapter-01",
            title="第一章：基础",
            order=1
        )
        session.add(chapter)
        await session.flush()

        # 创建案例（带完整教材内容）
        case = Case(
            chapter_id=chapter.id,
            slug="test-water-tank",
            title="水箱模拟实验",
            order=1,
            difficulty="beginner",
            estimated_minutes=30,
            description="""
## 实验目标

学习水箱系统的基本原理和数值模拟方法。

## 物理原理

水箱的水量变化遵循质量守恒定律 [代码行 5-8]：

$$\\frac{dV}{dt} = Q_{in} - Q_{out}$$

## 数值求解

使用欧拉法进行数值积分 [代码行 12-15]。

## 结果分析

观察水量随时间的变化趋势。
            """,
            starter_code="""# 水箱模拟
import numpy as np

# 参数设置
V0 = 100.0  # 初始水量
Qin = 10.0  # 入流量
Qout = 8.0  # 出流量
dt = 1.0    # 时间步长

# 数值求解
V = V0
for t in range(100):
    dV = (Qin - Qout) * dt
    V = V + dV
    print(f"t={t}, V={V}")

# 输出结果
print(f"最终水量: {V}")
""",
            solution_code="# 完整解决方案\nprint('Solution')",
            tags=["水箱", "数值模拟"]
        )
        session.add(case)
        await session.commit()

        book_id = book.id
        chapter_id = chapter.id
        case_id = case.id

    logger.success(f"✅ 测试数据创建成功")
    logger.info(f"   - Book ID: {book_id}")
    logger.info(f"   - Chapter ID: {chapter_id}")
    logger.info(f"   - Case ID: {case_id}")

    # ========================================
    # 步骤3: 测试教材内容解析
    # ========================================
    logger.info("\n📦 步骤3: 测试教材内容解析")

    from app.api.endpoints.textbooks import parse_content_to_sections

    test_content = """
## 第一部分

这是第一部分的内容 [代码行 1-5]。

## 第二部分

这是第二部分的内容。

## 第三部分

这是第三部分的内容 [代码行 10-12]。
    """

    test_code = "print('test')\n" * 15

    sections = parse_content_to_sections(test_content, test_code)

    logger.info(f"   解析到 {len(sections)} 个sections:")
    for section in sections:
        code_info = f"代码行 {section.code_lines.start}-{section.code_lines.end}" if section.code_lines else "无代码"
        logger.info(f"   - [{section.id}] {section.title} ({code_info})")

    # 验证
    assert len(sections) == 3, f"期望3个sections，实际{len(sections)}个"
    assert sections[0].code_lines is not None, "第一个section应该有代码映射"
    assert sections[0].code_lines.start == 1, f"第一个section代码起始行错误: {sections[0].code_lines.start}"
    logger.success("✅ 教材内容解析测试通过")

    # ========================================
    # 步骤4: 测试API端点
    # ========================================
    logger.info("\n📦 步骤4: 测试API端点")

    from app.api.endpoints.textbooks import get_textbook_content
    from sqlalchemy import select

    async with async_session() as session:
        # 查询并验证
        response = await get_textbook_content(
            book_slug="test-water-intro",
            chapter_slug="test-chapter-01",
            case_slug="test-water-tank",
            db=session
        )

        logger.info(f"   API响应:")
        logger.info(f"   - 标题: {response.title}")
        logger.info(f"   - Sections: {len(response.sections)}")
        logger.info(f"   - 代码长度: {len(response.starter_code)} 字符")
        logger.info(f"   - 难度: {response.difficulty}")
        logger.info(f"   - 预估时间: {response.estimated_minutes}分钟")

        # 验证响应结构
        assert response.book_slug == "test-water-intro"
        assert response.chapter_slug == "test-chapter-01"
        assert response.case_slug == "test-water-tank"
        assert len(response.sections) == 4  # 实验目标、物理原理、数值求解、结果分析
        assert response.starter_code != ""

        # 验证section内容
        logger.info(f"\n   Section详情:")
        for section in response.sections:
            code_info = (
                f"[代码 {section.code_lines.start}-{section.code_lines.end}]"
                if section.code_lines
                else "[无代码]"
            )
            logger.info(f"   - {section.title} {code_info}")
            logger.info(f"     内容长度: {len(section.content)} 字符")

        logger.success("✅ API端点测试通过")

    # ========================================
    # 步骤5: 测试代码行映射提取
    # ========================================
    logger.info("\n📦 步骤5: 测试代码行映射提取")

    from app.api.endpoints.textbooks import extract_code_line_mapping

    test_cases = [
        ("这是文本 [代码行 10-20]", 10, 20),
        ("参考代码 [代码行 5-8] 的实现", 5, 8),
        ("没有代码标记", None, None),
    ]

    for content, expected_start, expected_end in test_cases:
        result = extract_code_line_mapping(content, "")
        if expected_start is None:
            assert result is None, f"期望None，实际得到{result}"
            logger.info(f"   ✓ '{content[:20]}...' → 无映射")
        else:
            assert result is not None, f"期望有映射，实际为None"
            assert result.start == expected_start, f"起始行不匹配: {result.start} != {expected_start}"
            assert result.end == expected_end, f"结束行不匹配: {result.end} != {expected_end}"
            logger.info(f"   ✓ '{content[:20]}...' → {result.start}-{result.end}")

    logger.success("✅ 代码行映射提取测试通过")

    # ========================================
    # 清理
    # ========================================
    await engine.dispose()

    # ========================================
    # 总结
    # ========================================
    print("\n" + "=" * 80)
    print("🎉 所有集成测试通过！")
    print("=" * 80)
    print("\n✅ 测试覆盖:")
    print("   1. ✓ 数据库模型创建")
    print("   2. ✓ 教材内容解析（Markdown → Sections）")
    print("   3. ✓ 代码行映射提取（[代码行 X-Y]）")
    print("   4. ✓ API端点响应格式")
    print("   5. ✓ 完整数据流（数据库 → API → 响应）")

    print("\n📋 下一步:")
    print("   1. 启动后端服务: uvicorn app.main:app --reload")
    print("   2. 创建示例数据: POST /api/v1/textbooks/dev/seed-example")
    print("   3. 启动前端服务: npm run dev")
    print("   4. 访问演示页面: http://localhost:3000/textbook-demo")
    print()

    return 0


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(test_full_integration())
        sys.exit(exit_code)
    except Exception as e:
        logger.error(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
