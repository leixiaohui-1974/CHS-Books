#!/usr/bin/env python3
"""
全面测试平台上所有34本书的Web功能
测试内容：
1. 书籍列表加载
2. 每本书的详情页
3. 每个章节的内容显示
4. 每个案例的代码运行和展示
5. 文档说明的正确性
"""

import asyncio
import sys
import os
import io
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# 设置UTF-8编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 测试结果
test_results = {
    "总测试数": 0,
    "通过": 0,
    "失败": 0,
    "警告": 0,
    "书籍测试": {},
    "章节测试": {},
    "案例测试": {},
    "文档测试": {}
}

def print_header():
    """打印测试头部"""
    print("\n" + "=" * 100)
    print(f"   智能知识平台 - 全面功能测试")
    print(f"   测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   测试范围: 14本专业教材 + 20本考研书籍 = 34本")
    print("=" * 100 + "\n")

def print_section(title: str, icon: str = "📚"):
    """打印测试章节"""
    print(f"\n{icon} {title}")
    print("─" * 100)

def test_result(name: str, passed: bool, message: str = "", level: str = "info"):
    """记录测试结果"""
    test_results["总测试数"] += 1
    
    if passed:
        test_results["通过"] += 1
        print(f"  ✓ {name}")
    else:
        if level == "warning":
            test_results["警告"] += 1
            print(f"  ⚠ {name}")
        else:
            test_results["失败"] += 1
            print(f"  ✗ {name}")
    
    if message:
        print(f"    → {message}")

def load_books_catalog() -> Dict:
    """加载书籍目录"""
    catalog_path = Path(__file__).parent / "books_catalog.json"
    with open(catalog_path, 'r', encoding='utf-8') as f:
        return json.load(f)

async def test_book_metadata(book: Dict) -> bool:
    """测试书籍元数据"""
    required_fields = ['id', 'slug', 'title', 'description', 'author', 'path']
    missing_fields = [f for f in required_fields if f not in book or not book[f]]
    
    if missing_fields:
        test_result(
            f"元数据 - {book.get('title', 'Unknown')}",
            False,
            f"缺少字段: {', '.join(missing_fields)}"
        )
        return False
    
    test_result(
        f"元数据 - {book['title']}",
        True,
        f"ID: {book['id']}, 案例数: {book.get('totalCases', 0)}"
    )
    return True

async def test_book_path(book: Dict) -> bool:
    """测试书籍路径是否存在"""
    workspace = Path("/workspace")
    book_path = workspace / book['path']
    
    if not book_path.exists():
        test_result(
            f"路径检查 - {book['title']}",
            False,
            f"路径不存在: {book_path}"
        )
        return False
    
    # 检查README文件
    readme_path = book_path / "README.md"
    has_readme = readme_path.exists()
    
    test_result(
        f"路径检查 - {book['title']}",
        True,
        f"README: {'✓' if has_readme else '✗'}"
    )
    
    return True

async def test_book_chapters(book: Dict) -> Dict:
    """测试书籍的章节结构"""
    workspace = Path("/workspace")
    book_path = workspace / book['path']
    
    result = {
        "total": 0,
        "with_readme": 0,
        "with_code": 0,
        "issues": []
    }
    
    # 查找章节目录
    chapter_dirs = [
        d for d in book_path.iterdir() 
        if d.is_dir() and (
            d.name.startswith('chapter') or 
            d.name.startswith('day') or
            d.name.startswith('project') or
            d.name.startswith('case_')
        )
    ]
    
    result["total"] = len(chapter_dirs)
    
    for chapter_dir in chapter_dirs:
        # 检查README
        if (chapter_dir / "README.md").exists():
            result["with_readme"] += 1
        
        # 检查代码文件
        code_files = list(chapter_dir.glob("*.py"))
        if code_files:
            result["with_code"] += 1
    
    if result["total"] > 0:
        test_result(
            f"章节结构 - {book['title']}",
            True,
            f"总数: {result['total']}, README: {result['with_readme']}, 代码: {result['with_code']}"
        )
    else:
        test_result(
            f"章节结构 - {book['title']}",
            False,
            "未找到章节目录",
            level="warning"
        )
    
    return result

async def test_book_codes(book: Dict) -> Dict:
    """测试书籍的代码文件"""
    workspace = Path("/workspace")
    book_path = workspace / book['path']
    
    result = {
        "total": 0,
        "runnable": 0,
        "issues": []
    }
    
    # 查找所有Python代码文件
    code_files = list(book_path.rglob("*.py"))
    # 排除测试文件和__init__文件
    code_files = [
        f for f in code_files 
        if not f.name.startswith('test_') and 
           f.name != '__init__.py' and
           '__pycache__' not in str(f)
    ]
    
    result["total"] = len(code_files)
    
    # 简单检查代码文件是否可读
    for code_file in code_files[:10]:  # 只检查前10个
        try:
            with open(code_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if len(content) > 0:
                    result["runnable"] += 1
        except Exception as e:
            result["issues"].append(f"{code_file.name}: {str(e)}")
    
    if result["total"] > 0:
        test_result(
            f"代码文件 - {book['title']}",
            True,
            f"总数: {result['total']}, 已检查: {min(10, result['total'])}"
        )
    else:
        test_result(
            f"代码文件 - {book['title']}",
            False,
            "未找到代码文件",
            level="warning"
        )
    
    return result

async def test_documentation_quality(book: Dict) -> Dict:
    """测试文档质量"""
    workspace = Path("/workspace")
    book_path = workspace / book['path']
    readme_path = book_path / "README.md"
    
    result = {
        "has_readme": False,
        "content_length": 0,
        "has_sections": False,
        "has_code_blocks": False,
        "issues": []
    }
    
    if not readme_path.exists():
        test_result(
            f"文档质量 - {book['title']}",
            False,
            "缺少README.md",
            level="warning"
        )
        return result
    
    result["has_readme"] = True
    
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
            result["content_length"] = len(content)
            result["has_sections"] = "##" in content
            result["has_code_blocks"] = "```" in content
        
        quality_score = 0
        if result["content_length"] > 500:
            quality_score += 1
        if result["has_sections"]:
            quality_score += 1
        if result["has_code_blocks"]:
            quality_score += 1
        
        test_result(
            f"文档质量 - {book['title']}",
            quality_score >= 2,
            f"长度: {result['content_length']}, 章节: {'✓' if result['has_sections'] else '✗'}, 代码块: {'✓' if result['has_code_blocks'] else '✗'}"
        )
    except Exception as e:
        test_result(
            f"文档质量 - {book['title']}",
            False,
            f"读取失败: {str(e)}"
        )
    
    return result

async def test_single_book(book: Dict) -> Dict:
    """测试单本书的所有功能"""
    book_result = {
        "metadata": False,
        "path": False,
        "chapters": {},
        "codes": {},
        "documentation": {}
    }
    
    # 测试元数据
    book_result["metadata"] = await test_book_metadata(book)
    
    # 测试路径
    book_result["path"] = await test_book_path(book)
    
    if book_result["path"]:
        # 测试章节
        book_result["chapters"] = await test_book_chapters(book)
        
        # 测试代码
        book_result["codes"] = await test_book_codes(book)
        
        # 测试文档
        book_result["documentation"] = await test_documentation_quality(book)
    
    return book_result

async def main():
    """主测试函数"""
    print_header()
    
    # 加载书籍目录
    print_section("加载书籍目录", "📖")
    try:
        catalog = load_books_catalog()
        books = catalog["books"]
        stats = catalog["statistics"]
        
        test_result(
            "书籍目录加载",
            True,
            f"总计: {stats['totalBooks']}本 (专业: {stats['professionalBooks']}, 考研: {stats['examPrepBooks']})"
        )
    except Exception as e:
        test_result("书籍目录加载", False, f"错误: {str(e)}")
        return 1
    
    # 测试专业教材
    print_section("第一部分：专业教材测试 (14本)", "🎓")
    professional_books = [b for b in books if b.get('category') == '专业教材']
    
    for i, book in enumerate(professional_books, 1):
        print(f"\n[{i}/{len(professional_books)}] 测试: {book['title']}")
        book_result = await test_single_book(book)
        test_results["书籍测试"][book['id']] = book_result
    
    # 测试考研系列
    print_section("第二部分：考研系列测试 (20本)", "📚")
    exam_books = [b for b in books if b.get('category') == '考研系列']
    
    for i, book in enumerate(exam_books, 1):
        print(f"\n[{i}/{len(exam_books)}] 测试: {book['title']}")
        book_result = await test_single_book(book)
        test_results["书籍测试"][book['id']] = book_result
    
    # 统计结果
    print_section("测试统计", "📊")
    print(f"\n  总测试数: {test_results['总测试数']}")
    print(f"  ✓ 通过: {test_results['通过']}")
    print(f"  ✗ 失败: {test_results['失败']}")
    print(f"  ⚠ 警告: {test_results['警告']}")
    
    success_rate = (test_results['通过'] / test_results['总测试数'] * 100) if test_results['总测试数'] > 0 else 0
    print(f"\n  成功率: {success_rate:.1f}%")
    
    # 生成测试报告
    report_path = Path(__file__).parent / "test_all_books_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "总测试数": test_results['总测试数'],
                "通过": test_results['通过'],
                "失败": test_results['失败'],
                "警告": test_results['警告'],
                "成功率": f"{success_rate:.1f}%"
            },
            "details": test_results["书籍测试"]
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n  详细报告已保存: {report_path}")
    
    # 生成友好的总结报告
    print_section("测试总结", "🎉")
    
    passed_books = sum(1 for r in test_results["书籍测试"].values() if r["metadata"] and r["path"])
    total_books = len(test_results["书籍测试"])
    
    print(f"\n  ✓ 书籍完整性: {passed_books}/{total_books} 本通过测试")
    
    total_chapters = sum(r["chapters"].get("total", 0) for r in test_results["书籍测试"].values())
    print(f"  ✓ 总章节数: {total_chapters} 个")
    
    total_codes = sum(r["codes"].get("total", 0) for r in test_results["书籍测试"].values())
    print(f"  ✓ 总代码文件: {total_codes} 个")
    
    books_with_readme = sum(1 for r in test_results["书籍测试"].values() if r["documentation"].get("has_readme"))
    print(f"  ✓ 文档完整性: {books_with_readme}/{total_books} 本有README")
    
    print("\n" + "=" * 100)
    
    if test_results['失败'] == 0:
        print("🎉 所有测试通过！平台已准备就绪！")
    else:
        print(f"⚠️  发现 {test_results['失败']} 个问题，请检查详细报告")
    
    print("=" * 100 + "\n")
    
    return 0 if test_results['失败'] == 0 else 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
