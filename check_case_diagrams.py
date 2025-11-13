#!/usr/bin/env python3
"""
检查每个案例是否有问题描述示意图
"""

import os
import re
from pathlib import Path

results = {
    "total_cases": 0,
    "cases_with_diagram": 0,
    "cases_without_diagram": [],
    "cases_with_multiple_images": 0,
    "diagram_quality_issues": []
}

def check_readme_for_diagrams(readme_path):
    """检查README是否有示意图"""
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 查找图片引用 (Markdown格式和HTML格式)
        md_image_pattern = r'!\[([^\]]*)\]\(([^\)]+)\)'
        html_image_pattern = r'<img[^>]+src=["\']([^"\']+)["\']'

        md_images = re.findall(md_image_pattern, content)
        html_images = re.findall(html_image_pattern, content)

        # 合并两种格式（统一为(alt, src)格式）
        images = [(alt, src) for alt, src in md_images]
        images.extend([('', src) for src in html_images])

        # 查找"示意图"关键词
        has_diagram_keyword = bool(re.search(r'(示意图|系统图|架构图|原理图|流程图)', content))

        # 检查是否在文档开头部分（前1000字符）有图片
        has_early_image = bool(
            re.search(md_image_pattern, content[:1000]) or
            re.search(html_image_pattern, content[:1000])
        )

        case_dir = readme_path.parent

        # 检查图片文件是否存在
        existing_images = []
        for item in images:
            # 处理不同格式：(alt, src) 或 ('', src)
            img_path = item[1] if len(item) > 1 else item[0]
            if not img_path.startswith(('http://', 'https://')):
                full_path = case_dir / img_path
                if full_path.exists():
                    existing_images.append(img_path)

        return {
            "has_images": len(images) > 0,
            "image_count": len(images),
            "has_diagram_keyword": has_diagram_keyword,
            "has_early_image": has_early_image,
            "existing_images": existing_images,
            "has_problem_description_diagram": has_diagram_keyword and has_early_image and len(existing_images) > 0
        }

    except Exception as e:
        return None

def main():
    """主检查流程"""
    print("="*80)
    print("检查所有案例的问题描述示意图")
    print("="*80)

    # 扫描专业教材
    base_dir = Path('books')

    # 查找所有案例目录（包含README.md的code/examples子目录）
    for book_dir in base_dir.iterdir():
        if not book_dir.is_dir():
            continue

        examples_dir = book_dir / 'code' / 'examples'
        if not examples_dir.exists():
            continue

        book_name = book_dir.name
        print(f"\n{'='*80}")
        print(f"📚 书籍: {book_name}")
        print(f"{'='*80}")

        # 遍历所有案例
        for case_dir in sorted(examples_dir.iterdir()):
            if not case_dir.is_dir():
                continue

            readme = case_dir / 'README.md'
            if not readme.exists():
                continue

            results["total_cases"] += 1
            case_name = case_dir.name

            check_result = check_readme_for_diagrams(readme)

            if check_result:
                if check_result["has_problem_description_diagram"]:
                    results["cases_with_diagram"] += 1
                    status = "✅"

                    if check_result["image_count"] > 3:
                        results["cases_with_multiple_images"] += 1
                else:
                    try:
                        rel_path = str(readme.relative_to(Path.cwd()))
                    except ValueError:
                        rel_path = str(readme)
                    results["cases_without_diagram"].append(rel_path)
                    status = "❌"

                print(f"  {status} {case_name}: {check_result['image_count']}个图片, "
                      f"{'有' if check_result['has_diagram_keyword'] else '无'}示意图关键词, "
                      f"{'有' if check_result['has_early_image'] else '无'}开头图片")

    # 生成报告
    print("\n" + "="*80)
    print("📊 统计结果")
    print("="*80)

    coverage_rate = (results["cases_with_diagram"] / results["total_cases"] * 100) if results["total_cases"] > 0 else 0

    print(f"\n总案例数: {results['total_cases']}")
    print(f"有问题描述示意图: {results['cases_with_diagram']} ({coverage_rate:.1f}%)")
    print(f"缺少问题描述示意图: {len(results['cases_without_diagram'])} ({100-coverage_rate:.1f}%)")
    print(f"有多张图片(>3): {results['cases_with_multiple_images']}")

    if results["cases_without_diagram"]:
        print(f"\n❌ 缺少问题描述示意图的案例 ({len(results['cases_without_diagram'])}个):")
        for i, case in enumerate(results['cases_without_diagram'][:20], 1):
            print(f"  {i}. {case}")

        if len(results['cases_without_diagram']) > 20:
            print(f"  ... 还有 {len(results['cases_without_diagram']) - 20} 个案例")

    print("\n" + "="*80)
    if coverage_rate == 100:
        print("🎉 完美！所有案例都有问题描述示意图！")
    else:
        print(f"⚠️  需要为 {len(results['cases_without_diagram'])} 个案例添加问题描述示意图")
    print("="*80)

if __name__ == "__main__":
    main()
