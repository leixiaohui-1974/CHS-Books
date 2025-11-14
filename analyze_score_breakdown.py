#!/usr/bin/env python3
"""
分析案例评分构成，找出提升空间
"""
import os
import json
from pathlib import Path

def analyze_case_score(case_path):
    """详细分析单个案例的评分构成"""
    score_breakdown = {
        'readme': 0,
        'main_py': 0,
        'images': 0,
        'data_files': 0,
        'modules': 0,
        'total': 0
    }

    details = {
        'readme_chars': 0,
        'code_lines': 0,
        'image_count': 0,
        'data_files_list': [],
        'modules_list': []
    }

    # 检查README (40分)
    readme_path = case_path / 'README.md'
    if readme_path.exists():
        content = readme_path.read_text(encoding='utf-8')
        details['readme_chars'] = len(content)
        if len(content) > 200:
            score_breakdown['readme'] = 40

    # 检查main.py (40分)
    main_path = case_path / 'main.py'
    if main_path.exists():
        content = main_path.read_text(encoding='utf-8')
        lines = [l for l in content.split('\n') if l.strip() and not l.strip().startswith('#')]
        details['code_lines'] = len(lines)
        if len(lines) > 10:
            score_breakdown['main_py'] = 40

    # 检查图片 (10分)
    image_extensions = {'.png', '.jpg', '.jpeg', '.svg', '.gif'}
    image_files = []
    for ext in image_extensions:
        image_files.extend(case_path.glob(f'*{ext}'))
    details['image_count'] = len(image_files)
    if image_files:
        score_breakdown['images'] = 10

    # 检查数据文件 (5分)
    data_extensions = {'.csv', '.json', '.txt', '.dat', '.xlsx'}
    data_files = []
    for ext in data_extensions:
        data_files.extend(case_path.glob(f'*{ext}'))
    details['data_files_list'] = [f.name for f in data_files]
    if data_files:
        score_breakdown['data_files'] = 5

    # 检查其他模块 (5分)
    py_files = list(case_path.glob('*.py'))
    modules = [f.name for f in py_files if f.name != 'main.py']
    details['modules_list'] = modules
    if modules:
        score_breakdown['modules'] = 5

    score_breakdown['total'] = sum(score_breakdown.values())

    return score_breakdown, details

def analyze_book(book_path):
    """分析整本书的评分情况"""
    book_name = book_path.name
    cases = sorted([d for d in book_path.iterdir() if d.is_dir() and d.name.startswith('case')])

    total_score = 0
    case_scores = []
    missing_data_cases = []
    missing_module_cases = []

    for case in cases:
        score_breakdown, details = analyze_case_score(case)
        total_score += score_breakdown['total']
        case_scores.append({
            'name': case.name,
            'score': score_breakdown['total'],
            'breakdown': score_breakdown,
            'details': details
        })

        # 记录缺少数据文件或模块的案例
        if score_breakdown['data_files'] == 0:
            missing_data_cases.append(case.name)
        if score_breakdown['modules'] == 0:
            missing_module_cases.append(case.name)

    avg_score = total_score / len(cases) if cases else 0

    return {
        'book_name': book_name,
        'case_count': len(cases),
        'avg_score': avg_score,
        'case_scores': case_scores,
        'missing_data_count': len(missing_data_cases),
        'missing_data_cases': missing_data_cases[:5],  # 只显示前5个
        'missing_module_count': len(missing_module_cases),
        'missing_module_cases': missing_module_cases[:5]  # 只显示前5个
    }

def main():
    books_dir = Path('/home/user/CHS-Books/books')

    # 只分析90.0分的书籍
    target_books = [
        'wind-power-system-modeling-control',
        'water-environment-simulation',
        'distributed-hydrological-model',
        'canal-pipeline-control'
    ]

    print("="*70)
    print("评分详细分析 - 寻找优化空间")
    print("="*70)
    print()

    all_results = []

    for book_dir in target_books:
        book_path = books_dir / book_dir
        if not book_path.exists():
            continue

        result = analyze_book(book_path)
        all_results.append(result)

        print(f"📚 {result['book_name']}")
        print(f"   案例数: {result['case_count']}")
        print(f"   平均分: {result['avg_score']:.1f}/100")
        print(f"   缺少数据文件: {result['missing_data_count']}个案例")
        if result['missing_data_cases']:
            print(f"   示例: {', '.join(result['missing_data_cases'])}")
        print(f"   缺少模块文件: {result['missing_module_count']}个案例")
        if result['missing_module_cases']:
            print(f"   示例: {', '.join(result['missing_module_cases'])}")
        print()

    # 分析提升潜力
    print("="*70)
    print("优化潜力分析")
    print("="*70)
    print()

    total_missing_data = sum(r['missing_data_count'] for r in all_results)
    total_missing_modules = sum(r['missing_module_count'] for r in all_results)
    total_cases = sum(r['case_count'] for r in all_results)

    print(f"总案例数: {total_cases}")
    print(f"缺少数据文件: {total_missing_data}个 ({total_missing_data/total_cases*100:.1f}%)")
    print(f"缺少模块文件: {total_missing_modules}个 ({total_missing_modules/total_cases*100:.1f}%)")
    print()

    if total_missing_data > 0:
        potential_gain = (total_missing_data * 5) / total_cases
        print(f"💡 如果为所有案例添加数据文件(CSV/JSON):")
        print(f"   可提升约 {potential_gain:.2f} 分 (每案例+5分)")
        print()

    if total_missing_modules > 0:
        potential_gain = (total_missing_modules * 5) / total_cases
        print(f"💡 如果为所有案例添加模块文件(额外.py文件):")
        print(f"   可提升约 {potential_gain:.2f} 分 (每案例+5分)")
        print()

    # 保存详细结果
    output_file = '/home/user/CHS-Books/score_breakdown_analysis.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    print(f"详细分析已保存: {output_file}")

if __name__ == '__main__':
    main()
