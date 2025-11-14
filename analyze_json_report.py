#!/usr/bin/env python3
"""
分析测试JSON报告，找出优化空间
"""
import json

def main():
    with open('/home/user/CHS-Books/SMART_CASE_TEST_REPORT.json', 'r', encoding='utf-8') as f:
        report = json.load(f)

    print("="*70)
    print("评分构成分析 - 寻找优化空间")
    print("="*70)
    print()

    # 统计整体情况
    total_cases = 0
    cases_missing_data = []
    cases_missing_modules = []
    scores_by_book = {}

    for book in report['books']:
        book_name = book['book_name']
        scores_by_book[book_name] = []

        for case in book['case_results']:
            total_cases += 1

            # 记录评分
            scores_by_book[book_name].append(case['score'])

            # 检查缺少数据文件
            if not case['data']['has_data']:
                cases_missing_data.append({
                    'book': book_name,
                    'case': case['case_name'],
                    'score': case['score']
                })

            # 检查缺少模块
            if not case['other_py']['has_modules']:
                cases_missing_modules.append({
                    'book': book_name,
                    'case': case['case_name'],
                    'score': case['score']
                })

    print(f"总案例数: {total_cases}")
    print(f"平均分: {report['summary']['overall_avg_score']}")
    print()

    # 按书籍统计
    print("="*70)
    print("按书籍详细分析")
    print("="*70)
    print()

    for book_name, scores in sorted(scores_by_book.items(), key=lambda x: sum(x[1])/len(x[1])):
        avg_score = sum(scores) / len(scores)
        missing_data_count = len([c for c in cases_missing_data if c['book'] == book_name])
        missing_module_count = len([c for c in cases_missing_modules if c['book'] == book_name])

        print(f"📚 {book_name}")
        print(f"   平均分: {avg_score:.1f}/100")
        print(f"   案例数: {len(scores)}")
        print(f"   缺少数据文件: {missing_data_count}个 ({missing_data_count/len(scores)*100:.0f}%)")
        print(f"   缺少模块文件: {missing_module_count}个 ({missing_module_count/len(scores)*100:.0f}%)")

        # 计算潜在提升
        potential_from_data = (missing_data_count * 5) / len(scores)
        potential_from_modules = (missing_module_count * 5) / len(scores)
        total_potential = potential_from_data + potential_from_modules

        if total_potential > 0:
            print(f"   💡 潜在提升: +{total_potential:.1f}分 (数据+{potential_from_data:.1f}, 模块+{potential_from_modules:.1f})")
            print(f"   🎯 理论最高分: {avg_score + total_potential:.1f}/100")
        print()

    # 整体统计
    print("="*70)
    print("整体优化潜力")
    print("="*70)
    print()

    print(f"缺少数据文件: {len(cases_missing_data)}/{total_cases} ({len(cases_missing_data)/total_cases*100:.1f}%)")
    print(f"缺少模块文件: {len(cases_missing_modules)}/{total_cases} ({len(cases_missing_modules)/total_cases*100:.1f}%)")
    print()

    # 计算如果全部添加的提升效果
    current_avg = float(report['summary']['overall_avg_score'])

    if len(cases_missing_data) > 0:
        potential_from_data = (len(cases_missing_data) * 5) / total_cases
        print(f"💡 如果为所有案例添加数据文件 (CSV/JSON/TXT):")
        print(f"   可提升: +{potential_from_data:.2f}分")
        print(f"   新平均分: {current_avg + potential_from_data:.2f}/100")
        print()

    if len(cases_missing_modules) > 0:
        potential_from_modules = (len(cases_missing_modules) * 5) / total_cases
        print(f"💡 如果为所有案例添加模块文件 (额外.py文件):")
        print(f"   可提升: +{potential_from_modules:.2f}分")
        print(f"   新平均分: {current_avg + potential_from_modules:.2f}/100")
        print()

    # 如果两者都添加
    if len(cases_missing_data) > 0 or len(cases_missing_modules) > 0:
        total_potential = ((len(cases_missing_data) + len(cases_missing_modules)) * 5) / total_cases
        print(f"🎯 如果同时添加数据文件和模块:")
        print(f"   总提升: +{total_potential:.2f}分")
        print(f"   **最终平均分: {current_avg + total_potential:.2f}/100**")
        print()

    # 推荐优化策略
    print("="*70)
    print("推荐优化策略")
    print("="*70)
    print()

    # 找出平均分<93的书籍，它们最值得优化
    books_to_optimize = []
    for book_name, scores in scores_by_book.items():
        avg_score = sum(scores) / len(scores)
        if avg_score < 93.0:
            missing_data_count = len([c for c in cases_missing_data if c['book'] == book_name])
            missing_module_count = len([c for c in cases_missing_modules if c['book'] == book_name])
            potential = ((missing_data_count + missing_module_count) * 5) / len(scores)
            books_to_optimize.append({
                'name': book_name,
                'current': avg_score,
                'potential': potential,
                'target': avg_score + potential,
                'cases': len(scores),
                'missing_data': missing_data_count,
                'missing_modules': missing_module_count
            })

    books_to_optimize.sort(key=lambda x: x['potential'], reverse=True)

    if books_to_optimize:
        print("优先优化以下书籍（按潜力排序）：")
        print()
        for i, book in enumerate(books_to_optimize, 1):
            print(f"{i}. {book['name']}")
            print(f"   当前: {book['current']:.1f}分 → 目标: {book['target']:.1f}分 (提升{book['potential']:.1f}分)")
            print(f"   需要添加: 数据文件{book['missing_data']}个, 模块{book['missing_modules']}个")
            print()

if __name__ == '__main__':
    main()
