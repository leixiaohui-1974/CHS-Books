#!/usr/bin/env python3
"""
批量运行所有案例示例程序

自动发现并运行所有案例的可执行示例，生成可视化结果和统计报告。

作者：CHS-Books项目
日期：2025-10-30
"""

import os
import sys
import time
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple


def find_all_examples(examples_dir: Path) -> List[Path]:
    """
    查找所有案例的main.py文件

    Args:
        examples_dir: examples目录路径

    Returns:
        排序后的main.py文件路径列表
    """
    example_files = []
    for case_dir in sorted(examples_dir.iterdir()):
        if case_dir.is_dir() and case_dir.name.startswith('case_'):
            main_py = case_dir / 'main.py'
            if main_py.exists():
                example_files.append(main_py)
    return example_files


def count_png_files(case_dir: Path) -> int:
    """
    统计目录中的PNG文件数量

    Args:
        case_dir: 案例目录路径

    Returns:
        PNG文件数量
    """
    return len(list(case_dir.glob('*.png')))


def run_example(main_py: Path) -> Tuple[bool, float, str]:
    """
    运行单个案例示例程序

    Args:
        main_py: main.py文件路径

    Returns:
        (是否成功, 执行时间, 错误信息)
    """
    case_dir = main_py.parent
    case_name = case_dir.name

    print(f"\n{'='*70}")
    print(f"运行: {case_name}")
    print(f"{'='*70}")

    # 记录运行前的PNG文件数量
    png_before = count_png_files(case_dir)

    # 运行程序
    start_time = time.time()
    try:
        result = subprocess.run(
            [sys.executable, str(main_py)],
            cwd=str(case_dir),
            capture_output=True,
            text=True,
            timeout=300  # 5分钟超时
        )
        elapsed_time = time.time() - start_time

        # 检查是否成功
        if result.returncode == 0:
            # 记录运行后的PNG文件数量
            png_after = count_png_files(case_dir)
            png_generated = png_after - png_before

            print(f"✓ 成功完成 (耗时: {elapsed_time:.2f}秒)")
            if png_generated > 0:
                print(f"  生成了 {png_generated} 个PNG文件")

            return True, elapsed_time, ""
        else:
            print(f"✗ 运行失败 (返回码: {result.returncode})")
            error_msg = result.stderr if result.stderr else result.stdout
            print(f"  错误信息: {error_msg[:200]}")
            return False, elapsed_time, error_msg

    except subprocess.TimeoutExpired:
        elapsed_time = time.time() - start_time
        error_msg = "执行超时（超过5分钟）"
        print(f"✗ {error_msg}")
        return False, elapsed_time, error_msg

    except Exception as e:
        elapsed_time = time.time() - start_time
        error_msg = str(e)
        print(f"✗ 运行异常: {error_msg}")
        return False, elapsed_time, error_msg


def generate_report(results: List[Dict], total_time: float, output_file: Path):
    """
    生成运行报告

    Args:
        results: 运行结果列表
        total_time: 总运行时间
        output_file: 报告输出文件路径
    """
    successful = sum(1 for r in results if r['success'])
    failed = len(results) - successful

    report_lines = [
        "=" * 80,
        "明渠水力学案例示例程序批量运行报告",
        "=" * 80,
        "",
        f"运行时间: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"总案例数: {len(results)}",
        f"成功: {successful}",
        f"失败: {failed}",
        f"成功率: {successful/len(results)*100:.1f}%",
        f"总耗时: {total_time:.2f}秒",
        "",
        "=" * 80,
        "详细结果",
        "=" * 80,
        ""
    ]

    # 按案例编号排序
    sorted_results = sorted(results, key=lambda r: r['case_name'])

    for result in sorted_results:
        status = "✓ 成功" if result['success'] else "✗ 失败"
        report_lines.append(
            f"{result['case_name']:<30} {status:<10} {result['time']:.2f}秒"
        )
        if not result['success'] and result['error']:
            # 只显示错误信息的前100个字符
            error_preview = result['error'][:100].replace('\n', ' ')
            report_lines.append(f"  错误: {error_preview}...")

    # 统计PNG文件
    report_lines.extend([
        "",
        "=" * 80,
        "可视化文件统计",
        "=" * 80,
        ""
    ])

    total_png = 0
    for result in sorted_results:
        case_dir = result['main_py'].parent
        png_count = count_png_files(case_dir)
        total_png += png_count
        if png_count > 0:
            report_lines.append(f"{result['case_name']:<30} {png_count} 个PNG文件")

    report_lines.extend([
        "",
        f"总计: {total_png} 个PNG文件",
        ""
    ])

    # 失败案例详情
    if failed > 0:
        report_lines.extend([
            "=" * 80,
            "失败案例详情",
            "=" * 80,
            ""
        ])

        for result in sorted_results:
            if not result['success']:
                report_lines.append(f"\n{result['case_name']}:")
                report_lines.append(f"  文件: {result['main_py']}")
                report_lines.append(f"  错误: {result['error'][:300]}")

    report_lines.append("")
    report_lines.append("=" * 80)

    # 写入报告文件
    report_content = "\n".join(report_lines)
    output_file.write_text(report_content, encoding='utf-8')

    # 同时打印到控制台
    print("\n" + report_content)


def main():
    """主函数"""
    # 获取examples目录
    script_dir = Path(__file__).parent
    examples_dir = script_dir

    print("=" * 80)
    print("明渠水力学案例示例程序批量运行工具")
    print("=" * 80)
    print(f"\n正在扫描目录: {examples_dir}")

    # 查找所有示例
    example_files = find_all_examples(examples_dir)
    print(f"找到 {len(example_files)} 个案例示例程序\n")

    if not example_files:
        print("错误: 未找到任何案例示例程序")
        return 1

    # 运行所有示例
    results = []
    total_start_time = time.time()

    for main_py in example_files:
        success, elapsed_time, error_msg = run_example(main_py)
        results.append({
            'case_name': main_py.parent.name,
            'main_py': main_py,
            'success': success,
            'time': elapsed_time,
            'error': error_msg
        })

    total_time = time.time() - total_start_time

    # 生成报告
    report_file = examples_dir / 'run_all_examples_report.txt'
    generate_report(results, total_time, report_file)

    print(f"\n报告已保存至: {report_file}")

    # 返回状态码
    failed_count = sum(1 for r in results if not r['success'])
    return 0 if failed_count == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
