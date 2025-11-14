#!/usr/bin/env python3
"""
全面测试和修复方案
"""

import subprocess
import os
import json
from pathlib import Path

# 配置
BOOKS_ROOT = Path("/home/user/CHS-Books/books/water-system-control/code/examples")
BASE_URL = "http://localhost:8080"

def test_case(case_dir):
    """测试单个案例"""
    case_name = case_dir.name
    main_py = case_dir / "main.py"

    if not main_py.exists():
        return {"case": case_name, "status": "skip", "reason": "No main.py"}

    print(f"\n{'='*80}")
    print(f"测试案例: {case_name}")
    print(f"{'='*80}")

    # 运行案例
    try:
        # 设置matplotlib使用非交互式后端
        env = os.environ.copy()
        env['MPLBACKEND'] = 'Agg'

        result = subprocess.run(
            ['python3', 'main.py'],
            cwd=str(case_dir),
            capture_output=True,
            text=True,
            timeout=60,
            env=env
        )

        # 检查输出
        if result.returncode == 0:
            # 检查是否生成了图片
            png_files = list(case_dir.glob('*.png'))

            return {
                "case": case_name,
                "status": "success",
                "images": len(png_files),
                "output": result.stdout[:500]
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
    print("水系统控制论案例全面测试")
    print("="*80)

    results = []

    # 获取所有案例目录
    case_dirs = sorted([d for d in BOOKS_ROOT.iterdir() if d.is_dir() and d.name.startswith('case_')])

    print(f"\n找到 {len(case_dirs)} 个案例")

    # 测试每个案例
    for case_dir in case_dirs:
        result = test_case(case_dir)
        results.append(result)

        # 打印结果
        status_emoji = {
            "success": "✅",
            "failed": "❌",
            "error": "⚠️",
            "timeout": "⏱️",
            "skip": "⏭️"
        }
        emoji = status_emoji.get(result["status"], "❓")
        print(f"{emoji} {result['case']}: {result['status']}")

        if result.get("images"):
            print(f"   生成图片: {result['images']} 张")

    # 统计
    print("\n" + "="*80)
    print("测试统计")
    print("="*80)

    status_counts = {}
    for r in results:
        status = r["status"]
        status_counts[status] = status_counts.get(status, 0) + 1

    for status, count in sorted(status_counts.items()):
        print(f"{status}: {count}")

    # 保存报告
    report_path = Path("/home/user/CHS-Books/platform/test_reports/case_test_report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n报告已保存: {report_path}")

    # 返回成功率
    success_count = status_counts.get("success", 0)
    total_count = len(results)
    success_rate = success_count / total_count * 100 if total_count > 0 else 0

    print(f"\n成功率: {success_rate:.1f}% ({success_count}/{total_count})")

    return 0 if success_rate >= 80 else 1

if __name__ == "__main__":
    exit(main())
