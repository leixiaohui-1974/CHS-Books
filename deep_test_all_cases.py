#!/usr/bin/env python3
"""
深度测试所有案例的控制效果
检查每个案例的性能指标是否达标
"""

import subprocess
import os
import json
import re
from pathlib import Path

CASES_DIR = Path("/home/user/CHS-Books/books/water-system-control/code/examples")

# 每个案例的性能标准
PERFORMANCE_STANDARDS = {
    "稳态误差": {"max": 0.1, "unit": "m"},  # 最大稳态误差
    "超调量": {"max": 15, "unit": "%"},      # 最大超调量
    "上升时间": {"max": 30, "unit": "分钟"},  # 最大上升时间
    "调节时间": {"max": 50, "unit": "分钟"}   # 最大调节时间
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

def test_case(case_dir):
    """测试单个案例"""
    case_name = case_dir.name
    main_py = case_dir / "main.py"

    if not main_py.exists():
        return {"case": case_name, "status": "skip", "reason": "No main.py"}

    print(f"\n{'='*80}")
    print(f"测试: {case_name}")
    print(f"{'='*80}")

    try:
        env = os.environ.copy()
        env['MPLBACKEND'] = 'Agg'

        result = subprocess.run(
            ['python', 'main.py'],
            cwd=str(case_dir),
            capture_output=True,
            text=True,
            timeout=120,
            env=env
        )

        if result.returncode == 0:
            # 提取性能指标
            metrics = extract_performance_metrics(result.stdout)

            # 检查是否达标
            issues = []
            for metric_name, value in metrics.items():
                if metric_name in PERFORMANCE_STANDARDS:
                    standard = PERFORMANCE_STANDARDS[metric_name]
                    if value > standard['max']:
                        issues.append(f"{metric_name}={value}{standard['unit']} (超标，标准<{standard['max']})")

            # 统计图片
            png_files = list(case_dir.glob('*.png'))

            status = "pass" if len(issues) == 0 else "issues"

            return {
                "case": case_name,
                "status": status,
                "metrics": metrics,
                "issues": issues,
                "images": len(png_files),
                "output_lines": len(result.stdout.split('\n'))
            }
        else:
            return {
                "case": case_name,
                "status": "failed",
                "error": result.stderr[:500]
            }

    except subprocess.TimeoutExpired:
        return {"case": case_name, "status": "timeout"}
    except Exception as e:
        return {"case": case_name, "status": "error", "error": str(e)}

def main():
    """主测试流程"""
    print("="*80)
    print("水系统控制论 - 深度性能测试")
    print("标准：最严格")
    print("="*80)

    # 获取所有案例
    case_dirs = sorted([d for d in CASES_DIR.iterdir() if d.is_dir() and d.name.startswith('case_')])

    print(f"\n找到 {len(case_dirs)} 个案例\n")

    results = []
    passed = 0
    has_issues = 0
    failed = 0

    # 测试每个案例
    for case_dir in case_dirs:
        result = test_case(case_dir)
        results.append(result)

        # 打印结果
        status_emoji = {
            "pass": "✅",
            "issues": "⚠️",
            "failed": "❌",
            "error": "💥",
            "timeout": "⏱️",
            "skip": "⏭️"
        }
        emoji = status_emoji.get(result["status"], "❓")

        print(f"\n{emoji} {result['case']}: {result['status'].upper()}")

        if result.get("metrics"):
            print(f"   性能指标:")
            for metric, value in result["metrics"].items():
                unit = PERFORMANCE_STANDARDS.get(metric, {}).get("unit", "")
                print(f"     - {metric}: {value}{unit}")

        if result.get("issues"):
            print(f"   ⚠️ 问题:")
            for issue in result["issues"]:
                print(f"     - {issue}")

        if result.get("images"):
            print(f"   📊 生成图片: {result['images']}张")

        # 统计
        if result["status"] == "pass":
            passed += 1
        elif result["status"] == "issues":
            has_issues += 1
        elif result["status"] in ["failed", "error", "timeout"]:
            failed += 1

    # 总结
    print("\n" + "="*80)
    print("测试总结")
    print("="*80)
    print(f"✅ 完美通过: {passed}")
    print(f"⚠️ 有问题: {has_issues}")
    print(f"❌ 失败: {failed}")
    print(f"📊 总计: {len(results)}")
    print(f"通过率: {passed / len(results) * 100:.1f}%")
    print(f"完美率: {passed / len(results) * 100:.1f}%")

    # 保存报告
    report_path = Path("/home/user/CHS-Books/platform/test_reports/deep_test_report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump({
            "summary": {
                "total": len(results),
                "passed": passed,
                "has_issues": has_issues,
                "failed": failed
            },
            "results": results
        }, f, ensure_ascii=False, indent=2)

    print(f"\n报告已保存: {report_path}")

    return 0 if has_issues == 0 and failed == 0 else 1

if __name__ == "__main__":
    exit(main())
