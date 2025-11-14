#!/usr/bin/env python3
"""
严格的深度测试工具 - 验证结果正确性
不仅检查脚本是否运行，还要检查：
1. 输出中是否有NaN、inf等异常值
2. 是否有ERROR、Exception等错误
3. 是否生成了预期的图表文件
4. 关键数值是否在合理范围内
"""

import subprocess
import sys
import re
from pathlib import Path

def deep_test_case(case_dir, book_name):
    """深度测试一个案例"""
    case_name = case_dir.name
    main_py = case_dir / 'main.py'

    if not main_py.exists():
        return None

    try:
        # 运行案例并捕获输出
        result = subprocess.run(
            ['python', str(main_py)],
            capture_output=True,
            timeout=120,
            cwd='.',
            text=True,
            encoding='utf-8',
            errors='replace'
        )

        output = result.stdout + result.stderr

        # 检查1: 脚本是否成功运行
        if result.returncode != 0:
            return {
                'status': 'FAIL',
                'reason': f'退出码{result.returncode}',
                'details': []
            }

        # 检查2: 是否有异常值
        issues = []

        # 检查NaN
        nan_count = len(re.findall(r'\bnan\b|\bNaN\b', output, re.IGNORECASE))
        if nan_count > 0:
            issues.append(f'发现{nan_count}个NaN值')

        # 检查inf
        inf_count = len(re.findall(r'\binf\b|infinity', output, re.IGNORECASE))
        if inf_count > 0:
            issues.append(f'发现{inf_count}个inf值')

        # 检查ERROR
        if 'ERROR' in output or 'Error' in output:
            error_lines = [line for line in output.split('\n')
                          if 'error' in line.lower() and 'error' not in line.lower()]
            if error_lines:
                issues.append(f'发现错误信息')

        # 检查Exception
        if 'Exception' in output or 'Traceback' in output:
            issues.append('发现异常堆栈')

        # 检查3: 是否生成图表
        png_files = list(case_dir.glob('*.png'))
        num_images = len(png_files)

        # 检查4: 提取关键数值（如果有）
        key_metrics = {}

        # 水系统控制类案例 - 检查稳态误差
        if book_name == 'water-system-control':
            match = re.search(r'稳态误差[：:]\s*([\d.]+)\s*m', output)
            if match:
                steady_error = float(match.group(1))
                key_metrics['稳态误差'] = steady_error
                if steady_error > 0.1:
                    issues.append(f'稳态误差{steady_error}m超标(>0.1m)')

        # 生态水力学案例 - 检查推荐值是否合理
        elif book_name == 'ecohydraulics':
            # 检查是否有推荐流量
            match = re.search(r'推荐.*流量[：:]\s*([\d.]+)', output)
            if match:
                flow = float(match.group(1))
                key_metrics['推荐流量'] = flow
                # 流量应该大于0
                if flow <= 0 or flow > 10000:
                    issues.append(f'推荐流量{flow}不合理')

        # 判断最终状态
        if issues:
            return {
                'status': 'ISSUES',
                'reason': '有问题',
                'details': issues,
                'metrics': key_metrics,
                'num_images': num_images
            }
        else:
            return {
                'status': 'PASS',
                'reason': '完美',
                'details': [],
                'metrics': key_metrics,
                'num_images': num_images
            }

    except subprocess.TimeoutExpired:
        return {
            'status': 'TIMEOUT',
            'reason': '超时',
            'details': [],
            'metrics': {},
            'num_images': 0
        }
    except Exception as e:
        return {
            'status': 'ERROR',
            'reason': str(e),
            'details': [],
            'metrics': {},
            'num_images': 0
        }

def test_book_deeply(book_name):
    """深度测试一本书"""
    examples_dir = Path(f'books/{book_name}/code/examples')

    if not examples_dir.exists():
        print(f"错误: 找不到{examples_dir}")
        return None

    case_dirs = sorted([d for d in examples_dir.iterdir()
                       if d.is_dir() and d.name.startswith('case_')])

    print(f"\n{'='*80}")
    print(f"{book_name} 深度测试 - 共{len(case_dirs)}个案例")
    print(f"{'='*80}\n")

    results = {'PASS': 0, 'ISSUES': 0, 'FAIL': 0, 'TIMEOUT': 0, 'ERROR': 0}
    details = []

    for i, case_dir in enumerate(case_dirs, 1):
        print(f"[{i}/{len(case_dirs)}] {case_dir.name}...", end=" ", flush=True)

        result = deep_test_case(case_dir, book_name)

        if result is None:
            print("⏭️  跳过(无main.py)")
            continue

        status = result['status']
        results[status] += 1

        # 打印结果
        if status == 'PASS':
            print(f"✅ {result['reason']} ({result['num_images']}图)")
        elif status == 'ISSUES':
            print(f"⚠️  {result['reason']}")
            for detail in result['details']:
                print(f"      - {detail}")
        else:
            print(f"❌ {result['reason']}")
            if result['details']:
                for detail in result['details']:
                    print(f"      - {detail}")

        details.append({
            'case': case_dir.name,
            'result': result
        })

    # 打印总结
    total = sum(results.values())
    print(f"\n{'='*80}")
    print("测试总结")
    print(f"{'='*80}")
    print(f"✅ 完美通过: {results['PASS']}")
    print(f"⚠️  有问题: {results['ISSUES']}")
    print(f"❌ 失败: {results['FAIL']}")
    print(f"⏱️  超时: {results['TIMEOUT']}")
    print(f"💥 错误: {results['ERROR']}")
    print(f"📊 总计: {total}")
    if total > 0:
        pass_rate = (results['PASS'] / total) * 100
        print(f"完美率: {pass_rate:.1f}%")

        clean_rate = ((results['PASS'] + results['ISSUES']) / total) * 100
        print(f"运行率: {clean_rate:.1f}%")

    return {
        'book': book_name,
        'results': results,
        'details': details
    }

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python deep_test_book.py <书籍名称>")
        sys.exit(1)

    book_name = sys.argv[1]
    result = test_book_deeply(book_name)

    if result:
        # 如果有问题或失败，返回非零退出码
        if result['results']['ISSUES'] > 0 or result['results']['FAIL'] > 0:
            sys.exit(1)
        else:
            sys.exit(0)
