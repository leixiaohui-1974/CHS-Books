#!/usr/bin/env python3
"""
内容展示友好度测试脚本
检查所有文档的格式、图片、代码块等是否友好展示
"""

import asyncio
import sys
import os
import io
from pathlib import Path
from datetime import datetime
import json
import re

# 设置UTF-8编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 测试结果
test_results = {
    "总文档数": 0,
    "格式良好": 0,
    "需要改进": 0,
    "问题统计": {
        "标题层级问题": 0,
        "代码块不完整": 0,
        "图片链接失效": 0,
        "表格格式问题": 0,
        "数学公式问题": 0
    },
    "详情": {}
}

def print_header():
    """打印测试头部"""
    print("\n" + "=" * 100)
    print(f"   内容展示友好度测试")
    print(f"   测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 100 + "\n")

def print_section(title: str):
    """打印测试章节"""
    print(f"\n{'─' * 100}")
    print(f" {title}")
    print(f"{'─' * 100}")

def check_markdown_quality(content: str, file_path: Path) -> dict:
    """检查Markdown文档质量"""
    issues = []
    score = 100
    
    # 1. 检查标题层级
    headings = re.findall(r'^(#{1,6})\s+(.+)$', content, re.MULTILINE)
    if headings:
        levels = [len(h[0]) for h in headings]
        if max(levels) - min(levels) > 3:
            issues.append("标题层级跨度过大")
            score -= 10
    
    # 2. 检查代码块
    code_blocks = re.findall(r'```(\w*)\n(.*?)\n```', content, re.DOTALL)
    unclosed_code = content.count('```') % 2
    if unclosed_code != 0:
        issues.append("代码块未闭合")
        score -= 20
    
    # 3. 检查图片链接
    images = re.findall(r'!\[([^\]]*)\]\(([^\)]+)\)', content)
    for alt, url in images:
        if url.startswith('http'):
            continue  # 外部链接不检查
        img_path = file_path.parent / url
        if not img_path.exists():
            issues.append(f"图片不存在: {url}")
            score -= 5
    
    # 4. 检查表格格式
    tables = re.findall(r'\|[^\n]+\|', content)
    if tables:
        for table in tables[:3]:  # 只检查前3个表格
            cells = table.count('|')
            if cells < 2:
                issues.append("表格格式可能有问题")
                score -= 5
                break
    
    # 5. 检查数学公式
    math_inline = re.findall(r'\$[^\$]+\$', content)
    math_block = re.findall(r'\$\$[^\$]+\$\$', content)
    
    # 6. 检查列表格式
    lists = re.findall(r'^[\*\-\+]\s+.+$', content, re.MULTILINE)
    
    # 7. 检查链接
    links = re.findall(r'\[([^\]]+)\]\(([^\)]+)\)', content)
    
    return {
        "score": max(0, score),
        "issues": issues,
        "stats": {
            "headings": len(headings),
            "code_blocks": len(code_blocks),
            "images": len(images),
            "tables": len(tables),
            "math_formulas": len(math_inline) + len(math_block),
            "lists": len(lists),
            "links": len(links)
        }
    }

async def test_document(doc_path: Path) -> dict:
    """测试单个文档"""
    result = {
        "path": str(doc_path),
        "score": 0,
        "issues": [],
        "stats": {}
    }
    
    try:
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        quality = check_markdown_quality(content, doc_path)
        result.update(quality)
        
    except Exception as e:
        result["issues"].append(f"读取失败: {str(e)}")
        result["score"] = 0
    
    return result

async def test_book_display(book_path: Path, book_title: str) -> dict:
    """测试一本书的展示友好度"""
    result = {
        "total_docs": 0,
        "good": 0,
        "needs_improvement": 0,
        "docs": []
    }
    
    # 查找所有Markdown文件
    md_files = list(book_path.rglob("*.md"))
    # 排除特定文件
    md_files = [
        f for f in md_files 
        if 'node_modules' not in str(f) and
           '.git' not in str(f)
    ]
    
    result["total_docs"] = len(md_files)
    
    # 测试前10个文档
    test_files = md_files[:10] if len(md_files) > 10 else md_files
    
    for doc_file in test_files:
        doc_result = await test_document(doc_file)
        result["docs"].append(doc_result)
        
        if doc_result["score"] >= 80:
            result["good"] += 1
            print(f"  ✓ {doc_file.name} (评分: {doc_result['score']})")
        else:
            result["needs_improvement"] += 1
            print(f"  ⚠ {doc_file.name} (评分: {doc_result['score']})")
            if doc_result["issues"]:
                for issue in doc_result["issues"][:2]:  # 只显示前2个问题
                    print(f"    → {issue}")
    
    return result

async def main():
    """主测试函数"""
    print_header()
    
    # 加载书籍目录
    workspace = Path("/workspace")
    catalog_path = workspace / "platform/backend/books_catalog.json"
    
    with open(catalog_path, 'r', encoding='utf-8') as f:
        catalog = json.load(f)
    
    books = catalog["books"]
    
    # 测试所有书籍的文档（采样测试）
    print_section("开始内容展示友好度测试（每本书测试10个文档）")
    
    for i, book in enumerate(books, 1):
        book_path = workspace / book['path']
        
        print(f"\n[{i}/{len(books)}] 测试: {book['title']}")
        
        book_result = await test_book_display(book_path, book['title'])
        test_results["总文档数"] += book_result["total_docs"]
        test_results["格式良好"] += book_result["good"]
        test_results["需要改进"] += book_result["needs_improvement"]
        test_results["详情"][book['id']] = book_result
        
        print(f"  结果: {book_result['good']}/{len(book_result['docs'])} 格式良好")
    
    # 统计结果
    print_section("测试统计")
    print(f"\n  总文档数: {test_results['总文档数']}")
    print(f"  已测试: {test_results['格式良好'] + test_results['需要改进']}")
    print(f"  ✓ 格式良好: {test_results['格式良好']}")
    print(f"  ⚠ 需要改进: {test_results['需要改进']}")
    
    if test_results['格式良好'] + test_results['需要改进'] > 0:
        quality_rate = test_results['格式良好'] / (test_results['格式良好'] + test_results['需要改进']) * 100
        print(f"\n  优质率: {quality_rate:.1f}%")
    
    # 保存报告
    report_path = Path(__file__).parent / "test_display_friendliness_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "总文档数": test_results['总文档数'],
                "格式良好": test_results['格式良好'],
                "需要改进": test_results['需要改进'],
                "问题统计": test_results['问题统计']
            },
            "details": test_results["详情"]
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n  详细报告已保存: {report_path}")
    
    print("\n" + "=" * 100)
    print("✅ 展示友好度测试完成！")
    print("=" * 100 + "\n")
    
    return 0

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
