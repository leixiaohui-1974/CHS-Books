#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试脚本 - 每本书只测试第一个案例
"""

import subprocess
from pathlib import Path

def quick_test_case(case_dir):
    """快速测试一个案例"""
    main_py = case_dir / 'main.py'
    if not main_py.exists():
        return None

    try:
        result = subprocess.run(
            ['python', 'main.py'],
            cwd=case_dir,
            capture_output=True,
            text=True,
            timeout=60,
            encoding='utf-8',
            errors='replace'
        )
        return result.returncode == 0
    except:
        return False

def main():
    books_dir = Path('books')

    print("="*80)
    print("快速测试 - 每本书的第一个案例")
    print("="*80)

    results = []

    for book_path in sorted(books_dir.iterdir()):
        if not book_path.is_dir():
            continue

        examples_dir = book_path / 'code' / 'examples'
        if not examples_dir.exists():
            continue

        case_dirs = sorted([d for d in examples_dir.iterdir()
                          if d.is_dir() and d.name.startswith('case_')])

        if len(case_dirs) == 0:
            continue

        book_name = book_path.name
        first_case = case_dirs[0]

        print(f"\n{book_name} ({len(case_dirs)}个案例)")
        print(f"  测试: {first_case.name}...", end=" ")

        success = quick_test_case(first_case)

        if success:
            print("✅ PASS")
        else:
            print("❌ FAIL")

        results.append({
            'book': book_name,
            'total_cases': len(case_dirs),
            'first_case_pass': success
        })

    print(f"\n{'='*80}")
    print("快速测试总结")
    print(f"{'='*80}")

    total_books = len(results)
    passed_books = sum(1 for r in results if r['first_case_pass'])

    print(f"测试书籍: {total_books}")
    print(f"第一案例通过: {passed_books}")
    print(f"第一案例失败: {total_books - passed_books}")

    if passed_books < total_books:
        print(f"\n需要关注的书籍:")
        for r in results:
            if not r['first_case_pass']:
                print(f"  ❌ {r['book']} (共{r['total_cases']}个案例)")

if __name__ == '__main__':
    main()
