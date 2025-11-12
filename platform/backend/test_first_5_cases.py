#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试前5个案例
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
    """测试单个案例"""
    case_name = case_dir.name
    main_file = case_dir / "main.py"
    
    if not main_file.exists():
        return {"case": case_name, "status": "skip", "message": "main.py不存在", "images": 0, "time": 0}
    
    print(f"\n{'='*80}")
    print(f"测试 {case_name}")
    print(f"{'='*80}")
    
    start_time = time.time()
    
    try:
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
        
        elapsed_time = time.time() - start_time
        png_files = list(case_dir.glob("*.png"))
        image_count = len(png_files)
        
        if result.returncode == 0:
            status = "success"
            message = f"成功 ({elapsed_time:.1f}s, {image_count}张图)"
            print(f"✓ {message}")
        else:
            status = "error"
            message = f"失败 (返回码: {result.returncode})"
            print(f"✗ {message}")
            print(f"错误信息:\n{result.stderr[:300]}")
        
        return {"case": case_name, "status": status, "message": message, "images": image_count, "time": elapsed_time}
    
    except subprocess.TimeoutExpired:
        elapsed_time = time.time() - start_time
        print(f"✗ 超时 (>{timeout}s)")
        return {"case": case_name, "status": "timeout", "message": f"超时", "images": 0, "time": elapsed_time}
    
    except Exception as e:
        elapsed_time = time.time() - start_time
        print(f"✗ 异常: {str(e)}")
        return {"case": case_name, "status": "exception", "message": f"异常: {str(e)}", "images": 0, "time": elapsed_time}

def main():
    """主函数"""
    print("="*80)
    print("测试前5个案例")
    print("="*80)
    
    total_start = time.time()
    results = []
    
    # 只测试前5个案例
    cases = sorted(CASES_DIR.glob("case_*"))[:5]
    
    for case_dir in cases:
        if not case_dir.is_dir():
            continue
        result = test_case(case_dir, timeout=120)
        results.append(result)
    
    total_time = time.time() - total_start
    
    # 统计
    print("\n" + "="*80)
    print("测试结果汇总")
    print("="*80)
    
    success_count = sum(1 for r in results if r["status"] == "success")
    total_images = sum(r["images"] for r in results)
    
    print(f"\n总案例数: {len(results)}")
    print(f"  ✓ 成功: {success_count}")
    print(f"  ✗ 失败: {len(results) - success_count}")
    print(f"\n生成图表: {total_images} 张")
    print(f"总耗时: {total_time:.1f} 秒")
    
    for r in results:
        status_icon = "✓" if r["status"] == "success" else "✗"
        print(f"{status_icon} {r['case']}: {r['message']}")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    main()

