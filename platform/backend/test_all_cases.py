#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量测试所有案例的运行情况
"""

import subprocess
import sys
import io
from pathlib import Path
import time

# 设置标准输出为UTF-8编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 定义根目录
ROOT_DIR = Path(__file__).parent.parent.parent
CASES_DIR = ROOT_DIR / "books" / "water-system-control" / "code" / "examples"

def test_case(case_dir, timeout=120):
    """
    测试单个案例
    
    Args:
        case_dir: 案例目录路径
        timeout: 超时时间（秒）
    
    Returns:
        dict: 测试结果
    """
    case_name = case_dir.name
    main_file = case_dir / "main.py"
    
    if not main_file.exists():
        return {
            "case": case_name,
            "status": "skip",
            "message": "main.py不存在",
            "images": 0,
            "time": 0
        }
    
    print(f"\n{'='*80}")
    print(f"测试 {case_name}")
    print(f"{'='*80}")
    
    # 记录开始时间
    start_time = time.time()
    
    try:
        # 运行测试
        result = subprocess.run(
            [sys.executable, str(main_file)],
            cwd=str(case_dir),
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding='utf-8',
            errors='replace',
            env={**subprocess.os.environ, 'PYTHONIOENCODING': 'utf-8'}
        )
        
        # 记录结束时间
        elapsed_time = time.time() - start_time
        
        # 统计生成的PNG文件数
        png_files = list(case_dir.glob("*.png"))
        image_count = len(png_files)
        
        # 检查返回码
        if result.returncode == 0:
            status = "success"
            message = f"成功 ({elapsed_time:.1f}s, {image_count}张图)"
            print(f"✓ {message}")
        else:
            status = "error"
            message = f"失败 (返回码: {result.returncode})"
            print(f"✗ {message}")
            if result.stderr:
                print(f"错误信息:\n{result.stderr[:500]}")
        
        return {
            "case": case_name,
            "status": status,
            "message": message,
            "images": image_count,
            "time": elapsed_time,
            "returncode": result.returncode
        }
    
    except subprocess.TimeoutExpired:
        elapsed_time = time.time() - start_time
        print(f"✗ 超时 (>{timeout}s)")
        return {
            "case": case_name,
            "status": "timeout",
            "message": f"超时 (>{timeout}s)",
            "images": 0,
            "time": elapsed_time
        }
    
    except Exception as e:
        elapsed_time = time.time() - start_time
        print(f"✗ 异常: {str(e)}")
        return {
            "case": case_name,
            "status": "exception",
            "message": f"异常: {str(e)}",
            "images": 0,
            "time": elapsed_time
        }

def main():
    """主函数"""
    print("="*80)
    print("批量测试所有案例")
    print("="*80)
    
    # 开始时间
    total_start = time.time()
    
    results = []
    
    # 遍历所有案例目录
    for case_dir in sorted(CASES_DIR.glob("case_*")):
        if not case_dir.is_dir():
            continue
        
        result = test_case(case_dir, timeout=120)
        results.append(result)
    
    # 总耗时
    total_time = time.time() - total_start
    
    # 统计结果
    print("\n" + "="*80)
    print("测试结果汇总")
    print("="*80)
    
    success_count = sum(1 for r in results if r["status"] == "success")
    error_count = sum(1 for r in results if r["status"] == "error")
    timeout_count = sum(1 for r in results if r["status"] == "timeout")
    skip_count = sum(1 for r in results if r["status"] == "skip")
    exception_count = sum(1 for r in results if r["status"] == "exception")
    total_images = sum(r["images"] for r in results)
    
    print(f"\n总案例数: {len(results)}")
    print(f"  ✓ 成功: {success_count}")
    print(f"  ✗ 失败: {error_count}")
    print(f"  ⏱ 超时: {timeout_count}")
    print(f"  ⊘ 跳过: {skip_count}")
    print(f"  ⚠ 异常: {exception_count}")
    print(f"\n生成图表: {total_images} 张")
    print(f"总耗时: {total_time/60:.1f} 分钟")
    
    # 详细结果
    print("\n" + "-"*80)
    print("详细结果:")
    print("-"*80)
    for r in results:
        status_icon = {
            "success": "✓",
            "error": "✗",
            "timeout": "⏱",
            "skip": "⊘",
            "exception": "⚠"
        }.get(r["status"], "?")
        
        print(f"{status_icon} {r['case']}: {r['message']}")
    
    # 失败案例详情
    failed_cases = [r for r in results if r["status"] in ["error", "exception"]]
    if failed_cases:
        print("\n" + "-"*80)
        print("失败案例:")
        print("-"*80)
        for r in failed_cases:
            print(f"  {r['case']}: {r['message']}")
    
    print("\n" + "="*80)
    print("测试完成！")
    print("="*80)
    
    # 返回成功率
    return success_count == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

