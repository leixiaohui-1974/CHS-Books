#!/usr/bin/env python3
"""
深度内容展示测试 - 验证章节、案例、图表、排版
"""

import requests
import json
import re
from pathlib import Path
from collections import defaultdict

BASE_URL = "http://localhost:8080"
BOOKS_DIR = Path("/home/user/CHS-Books/books")
REPORT_FILE = Path("/home/user/CHS-Books/platform/test_reports/content-display-test.md")

# 统计
stats = {
    "total_cases": 0,
    "cases_with_readme": 0,
    "missing_images": [],
    "broken_links": [],
    "markdown_issues": []
}

def check_markdown_file(md_file):
    """检查单个Markdown文件的内容"""
    result = {
        "file": str(md_file.relative_to(BOOKS_DIR)),
        "has_chinese": False,
        "has_code_blocks": False,
        "has_tables": False,
        "has_images": False,
        "image_references": [],
        "missing_images": [],
        "line_count": 0
    }

    try:
        content = md_file.read_text(encoding='utf-8')
        result["line_count"] = len(content.split('\n'))

        # 检查中文
        if re.search(r'[\u4e00-\u9fa5]', content):
            result["has_chinese"] = True

        # 检查代码块
        if '```' in content:
            result["has_code_blocks"] = True
            result["code_block_count"] = content.count('```') // 2

        # 检查表格
        if re.search(r'\|.*\|.*\|', content):
            result["has_tables"] = True

        # 检查图片引用
        image_pattern = r'!\[([^\]]*)\]\(([^\)]+)\)'
        images = re.findall(image_pattern, content)

        if images:
            result["has_images"] = True
            result["image_references"] = images

            # 检查图片文件是否存在
            for alt_text, img_path in images:
                img_file = md_file.parent / img_path
                if not img_file.exists():
                    result["missing_images"].append(img_path)
                    stats["missing_images"].append({
                        "file": str(md_file.relative_to(BOOKS_DIR)),
                        "image": img_path
                    })

    except Exception as e:
        result["error"] = str(e)

    return result

def scan_book_cases(book_dir):
    """扫描一本书的所有案例"""
    book_name = book_dir.name
    results = {
        "book": book_name,
        "cases": [],
        "total_cases": 0,
        "cases_with_readme": 0
    }

    # 查找所有案例目录
    examples_dir = book_dir / "code" / "examples"
    if not examples_dir.exists():
        return results

    for case_dir in sorted(examples_dir.iterdir()):
        if not case_dir.is_dir():
            continue

        if case_dir.name.startswith('.') or case_dir.name == '__pycache__':
            continue

        stats["total_cases"] += 1
        results["total_cases"] += 1

        case_result = {
            "name": case_dir.name,
            "has_readme": False,
            "readme_analysis": None
        }

        # 检查README
        readme_file = case_dir / "README.md"
        if readme_file.exists():
            stats["cases_with_readme"] += 1
            results["cases_with_readme"] += 1
            case_result["has_readme"] = True
            case_result["readme_analysis"] = check_markdown_file(readme_file)

        results["cases"].append(case_result)

    return results

def generate_report(all_results):
    """生成测试报告"""
    from datetime import datetime
    report = f"""# Platform内容展示深度测试报告

## 测试时间
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 测试范围
本次测试深入检查了所有书籍的案例README文件，验证内容展示的完整性。

---

## 📊 总体统计

| 指标 | 数量 | 说明 |
|------|------|------|
| 扫描书籍数 | {len(all_results)} | 所有书籍 |
| 案例总数 | {stats['total_cases']} | 所有案例目录 |
| 包含README的案例 | {stats['cases_with_readme']} | {stats['cases_with_readme']/stats['total_cases']*100:.1f}% |
| 缺失图片引用 | {len(stats['missing_images'])} | 引用但文件不存在 |

---

## 🔍 详细检查结果

"""

    for book_result in all_results:
        report += f"\n### 📚 {book_result['book']}\n\n"
        report += f"- 案例总数: {book_result['total_cases']}\n"
        report += f"- 有README: {book_result['cases_with_readme']}\n\n"

        if book_result['cases']:
            report += "| 案例名 | README | 中文 | 代码块 | 表格 | 图片 | 行数 |\n"
            report += "|--------|--------|------|--------|------|------|------|\n"

            for case in book_result['cases']:
                readme_status = "✅" if case['has_readme'] else "❌"

                if case['readme_analysis']:
                    ra = case['readme_analysis']
                    chinese = "✅" if ra['has_chinese'] else "❌"
                    code = f"✅ ({ra.get('code_block_count', 0)})" if ra['has_code_blocks'] else "❌"
                    table = "✅" if ra['has_tables'] else "❌"
                    image = f"✅ ({len(ra['image_references'])})" if ra['has_images'] else "❌"
                    lines = ra['line_count']
                else:
                    chinese = code = table = image = "-"
                    lines = 0

                report += f"| {case['name']} | {readme_status} | {chinese} | {code} | {table} | {image} | {lines} |\n"

            report += "\n"

    # 缺失图片列表
    if stats['missing_images']:
        report += "\n## ⚠️ 缺失的图片文件\n\n"
        report += "以下图片在README中被引用，但文件不存在：\n\n"
        report += "| 文件 | 引用的图片 |\n"
        report += "|------|------------|\n"

        for item in stats['missing_images'][:50]:  # 只显示前50个
            report += f"| {item['file']} | `{item['image']}` |\n"

        if len(stats['missing_images']) > 50:
            report += f"\n*还有 {len(stats['missing_images']) - 50} 个缺失图片未列出*\n"

    # 总结
    report += "\n---\n\n## ✅ 测试结论\n\n"

    readme_rate = stats['cases_with_readme'] / stats['total_cases'] * 100 if stats['total_cases'] > 0 else 0

    if readme_rate >= 90:
        report += f"**README覆盖率：优秀** ({readme_rate:.1f}%)\n\n"
    elif readme_rate >= 70:
        report += f"**README覆盖率：良好** ({readme_rate:.1f}%)\n\n"
    else:
        report += f"**README覆盖率：需改进** ({readme_rate:.1f}%)\n\n"

    if len(stats['missing_images']) > 0:
        report += f"⚠️ **发现 {len(stats['missing_images'])} 个缺失的图片文件**\n\n"
        report += "建议：\n"
        report += "1. 为引用的图片生成实际文件\n"
        report += "2. 或删除README中的图片引用\n"
        report += "3. 或使用占位图片\n\n"
    else:
        report += "✅ **所有引用的图片文件都存在**\n\n"

    return report

def main():
    print("🔍 开始深度内容展示测试...")
    print(f"扫描目录: {BOOKS_DIR}")
    print()

    all_results = []

    # 扫描所有书籍
    for book_dir in sorted(BOOKS_DIR.iterdir()):
        if not book_dir.is_dir():
            continue

        if book_dir.name.startswith('.'):
            continue

        print(f"📚 扫描书籍: {book_dir.name}")
        result = scan_book_cases(book_dir)
        all_results.append(result)
        print(f"  - 案例数: {result['total_cases']}, README: {result['cases_with_readme']}")

    print()
    print("=" * 80)
    print("📊 测试统计")
    print("=" * 80)
    print(f"总案例数: {stats['total_cases']}")
    print(f"有README: {stats['cases_with_readme']} ({stats['cases_with_readme']/stats['total_cases']*100:.1f}%)")
    print(f"缺失图片: {len(stats['missing_images'])}")
    print()

    # 生成报告
    report = generate_report(all_results)

    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text(report, encoding='utf-8')

    print(f"✅ 报告已生成: {REPORT_FILE}")
    print()

    # 输出关键问题
    if len(stats['missing_images']) > 0:
        print("⚠️ 发现问题：")
        print(f"  - {len(stats['missing_images'])} 个图片文件缺失")
        print()
        print("前10个缺失的图片：")
        for i, item in enumerate(stats['missing_images'][:10], 1):
            print(f"  {i}. {item['file']} -> {item['image']}")

    return 0 if len(stats['missing_images']) == 0 else 1

if __name__ == "__main__":
    from datetime import datetime
    exit(main())
