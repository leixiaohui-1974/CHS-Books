#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全书籍案例深度测试脚本

测试项目中所有书籍的所有案例，确保控制效果达到最严格标准
"""

import subprocess
import re
import sys
import json
from pathlib import Path
from datetime import datetime

# 性能标准（最严格）
PERFORMANCE_STANDARDS = {
    "稳态误差": {"max": 0.1, "unit": "m"},
    "超调量": {"max": 15, "unit": "%"},
    "上升时间": {"max": 30, "unit": "分钟"},
    "调节时间": {"max": 50, "unit": "分钟"}
}

def extract_performance_metrics(output):
    """从输出中提取性能指标"""
    metrics = {}

    # 提取稳态误差
    match = re.search(r'稳态误差[：:]\s*([\d.]+)\s*m', output)
    if match:
        metrics['稳态误差'] = float(match.group(1))

    # 提取超调量
    match = re.search(r'超调量[：:]\s*([\d.]+)%', output)
    if match:
        metrics['超调量'] = float(match.group(1))

    # 提取上升时间
    match = re.search(r'上升时间[：:]\s*([\d.]+|nan)\s*分钟', output)
    if match and match.group(1) != 'nan':
        metrics['上升时间'] = float(match.group(1))

    # 提取调节时间
    match = re.search(r'调节时间.*[：:]\s*([\d.]+|nan)\s*分钟', output)
    if match and match.group(1) != 'nan':
        metrics['调节时间'] = float(match.group(1))

    return metrics

def count_images(case_dir):
    """统计案例生成的图片数量"""
    return len(list(case_dir.glob('*.png')))

def test_case(case_dir):
    """测试单个案例"""
    case_name = case_dir.name
    main_py = case_dir / 'main.py'

    if not main_py.exists():
        return None

    # 运行案例
    try:
        result = subprocess.run(
            ['python', 'main.py'],
            cwd=case_dir,
            capture_output=True,
            text=True,
            timeout=300,
            encoding='utf-8',
            errors='replace'
        )

        output = result.stdout + result.stderr

        # 提取性能指标
        metrics = extract_performance_metrics(output)

        # 统计图片
        num_images = count_images(case_dir)

        # 检查是否有问题
        issues = []
        for metric_name, standard in PERFORMANCE_STANDARDS.items():
            if metric_name in metrics:
                value = metrics[metric_name]
                max_val = standard['max']
                if value > max_val:
                    issues.append(f"{metric_name}={value}{standard['unit']} (超标，标准<{max_val})")

        status = 'PASS' if len(issues) == 0 and result.returncode == 0 else 'ISSUES'

        return {
            'name': case_name,
            'status': status,
            'returncode': result.returncode,
            'metrics': metrics,
            'issues': issues,
            'num_images': num_images
        }

    except subprocess.TimeoutExpired:
        return {
            'name': case_name,
            'status': 'TIMEOUT',
            'returncode': -1,
            'metrics': {},
            'issues': ['执行超时（>300秒）'],
            'num_images': 0
        }
    except Exception as e:
        return {
            'name': case_name,
            'status': 'ERROR',
            'returncode': -1,
            'metrics': {},
            'issues': [str(e)],
            'num_images': 0
        }

def test_book(book_path):
    """测试一本书的所有案例"""
    book_name = book_path.name
    examples_dir = book_path / 'code' / 'examples'

    if not examples_dir.exists():
        return None

    # 找到所有案例目录
    case_dirs = sorted([d for d in examples_dir.iterdir()
                       if d.is_dir() and d.name.startswith('case_')])

    if len(case_dirs) == 0:
        return None

    print(f"\n{'='*80}")
    print(f"测试书籍: {book_name}")
    print(f"{'='*80}")
    print(f"找到 {len(case_dirs)} 个案例\n")

    results = []
    for case_dir in case_dirs:
        print(f"{'='*80}")
        print(f"测试: {case_dir.name}")
        print(f"{'='*80}\n")

        result = test_case(case_dir)
        if result:
            results.append(result)

            # 打印结果
            if result['status'] == 'PASS':
                print(f"✅ {result['name']}: PASS")
            elif result['status'] == 'ISSUES':
                print(f"⚠️ {result['name']}: ISSUES")
            else:
                print(f"❌ {result['name']}: {result['status']}")

            if result['metrics']:
                print("   性能指标:")
                for name, value in result['metrics'].items():
                    unit = PERFORMANCE_STANDARDS.get(name, {}).get('unit', '')
                    print(f"     - {name}: {value}{unit}")

            if result['issues']:
                print("   ⚠️ 问题:")
                for issue in result['issues']:
                    print(f"     - {issue}")

            if result['num_images'] > 0:
                print(f"   📊 生成图片: {result['num_images']}张")

            print()

    # 统计
    total = len(results)
    passed = sum(1 for r in results if r['status'] == 'PASS')
    issues = sum(1 for r in results if r['status'] == 'ISSUES')
    failed = sum(1 for r in results if r['status'] not in ['PASS', 'ISSUES'])

    print(f"{'='*80}")
    print(f"{book_name} 测试总结")
    print(f"{'='*80}")
    print(f"✅ 完美通过: {passed}")
    print(f"⚠️ 有问题: {issues}")
    print(f"❌ 失败: {failed}")
    print(f"📊 总计: {total}")
    if total > 0:
        print(f"通过率: {passed/total*100:.1f}%")
        print(f"完美率: {passed/total*100:.1f}%")
    else:
        print(f"通过率: N/A (无可测试案例)")
        print(f"完美率: N/A (无可测试案例)")

    return {
        'book_name': book_name,
        'total': total,
        'passed': passed,
        'issues': issues,
        'failed': failed,
        'results': results
    }

def main():
    """主函数"""
    print("="*80)
    print("CHS-Books项目 - 全书籍案例深度测试")
    print("标准：最严格")
    print("="*80)

    books_dir = Path('books')

    # 找到所有有案例的书籍
    book_paths = []
    for book_path in sorted(books_dir.iterdir()):
        if book_path.is_dir():
            examples_dir = book_path / 'code' / 'examples'
            if examples_dir.exists():
                case_dirs = [d for d in examples_dir.iterdir()
                           if d.is_dir() and d.name.startswith('case_')]
                if len(case_dirs) > 0:
                    book_paths.append((book_path, len(case_dirs)))

    # 按案例数量从多到少排序
    book_paths.sort(key=lambda x: x[1], reverse=True)

    print(f"\n找到 {len(book_paths)} 本书籍，共 {sum(c for _, c in book_paths)} 个案例\n")

    # 显示书籍列表
    print("书籍列表（按案例数量排序）：")
    for i, (book_path, count) in enumerate(book_paths, 1):
        print(f"  {i}. {book_path.name}: {count}个案例")

    # 测试所有书籍
    all_results = []
    for book_path, _ in book_paths:
        book_result = test_book(book_path)
        if book_result:
            all_results.append(book_result)

    # 生成总体报告
    print(f"\n{'='*80}")
    print("全项目测试总结")
    print(f"{'='*80}")

    total_books = len(all_results)
    total_cases = sum(r['total'] for r in all_results)
    total_passed = sum(r['passed'] for r in all_results)
    total_issues = sum(r['issues'] for r in all_results)
    total_failed = sum(r['failed'] for r in all_results)

    print(f"\n📚 测试书籍数: {total_books}")
    print(f"📊 测试案例数: {total_cases}")
    print(f"✅ 完美通过: {total_passed}")
    print(f"⚠️ 有问题: {total_issues}")
    print(f"❌ 失败: {total_failed}")
    if total_cases > 0:
        print(f"通过率: {total_passed/total_cases*100:.1f}%")
        print(f"完美率: {total_passed/total_cases*100:.1f}%")
    else:
        print(f"通过率: N/A")
        print(f"完美率: N/A")

    # 显示有问题的书籍
    if total_issues > 0 or total_failed > 0:
        print(f"\n需要修复的书籍:")
        for result in all_results:
            if result['issues'] > 0 or result['failed'] > 0:
                print(f"  - {result['book_name']}: "
                      f"{result['issues']}个问题案例, "
                      f"{result['failed']}个失败案例")

    # 保存JSON报告
    report_dir = Path('platform/test_reports')
    report_dir.mkdir(parents=True, exist_ok=True)

    report = {
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'total_books': total_books,
            'total_cases': total_cases,
            'total_passed': total_passed,
            'total_issues': total_issues,
            'total_failed': total_failed,
            'pass_rate': (total_passed/total_cases*100) if total_cases > 0 else 0,
        },
        'books': all_results
    }

    report_file = report_dir / 'all_books_test_report.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n报告已保存: {report_file}")

    return 0 if total_issues == 0 and total_failed == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
