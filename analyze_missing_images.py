#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析缺少图片的案例
"""

import json
from pathlib import Path

def analyze_missing_images():
    """分析缺少图片的案例"""

    # 读取测试报告
    report_path = Path('/home/user/CHS-Books/SMART_CASE_TEST_REPORT.json')
    with open(report_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print("\n" + "=" * 70)
    print("缺少图片的案例分析")
    print("=" * 70)

    missing_by_book = {}
    total_missing = 0

    for book in data['books']:
        book_name = book['book_name']
        book_id = book['book_id']

        missing_cases = []
        for case in book['case_results']:
            images = case.get('images', {})
            if not images.get('success', False):
                missing_cases.append({
                    'name': case['case_name'],
                    'dir': case['case_dir'],
                    'has_main': case.get('main_py', {}).get('exists', False)
                })

        if missing_cases:
            missing_by_book[book_name] = {
                'book_id': book_id,
                'cases': missing_cases
            }
            total_missing += len(missing_cases)

    # 按书籍分类输出
    for book_name, info in missing_by_book.items():
        print(f"\n{book_name} ({len(info['cases'])}个案例):")
        print("-" * 70)
        for case in info['cases']:
            has_main = "✓有main.py" if case['has_main'] else "✗无main.py"
            print(f"  {case['name']:<40} [{has_main}]")

    print("\n" + "=" * 70)
    print(f"总计: {total_missing}个案例缺少图片")
    print("=" * 70)

    # 统计有main.py但缺少图片的案例
    has_main_no_images = []
    for book_name, info in missing_by_book.items():
        for case in info['cases']:
            if case['has_main']:
                has_main_no_images.append({
                    'book': book_name,
                    'case': case['name'],
                    'dir': case['dir']
                })

    print(f"\n有main.py但缺少图片生成代码的案例: {len(has_main_no_images)}个")
    print("-" * 70)
    for item in has_main_no_images[:10]:  # 只显示前10个
        print(f"  {item['book']}/{item['case']}")
    if len(has_main_no_images) > 10:
        print(f"  ... 还有{len(has_main_no_images)-10}个")

    return missing_by_book, has_main_no_images

if __name__ == '__main__':
    missing_by_book, has_main_no_images = analyze_missing_images()
