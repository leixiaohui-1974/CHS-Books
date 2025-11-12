#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试案例2-6的运行情况和控制效果
"""

import subprocess
import sys
from pathlib import Path
import json
from datetime import datetime

# 项目根目录
ROOT_DIR = Path(__file__).parent.parent.parent
CASES_DIR = ROOT_DIR / "books" / "water-system-control" / "code" / "examples"

def test_case(case_name, case_path):
    """测试单个案例"""
    print(f"\n{'='*80}")
    print(f"测试 {case_name}")
    print(f"{'='*80}")
    
    main_file = case_path / "main.py"
    if not main_file.exists():
        return {"status": "skip", "message": "main.py不存在"}
    
    try:
        result = subprocess.run(
            [sys.executable, str(main_file)],
            cwd=str(case_path),
            capture_output=True,
            text=True,
            timeout=120,
            encoding='utf-8',
            errors='replace'
        )
        
        # 检查PNG文件
        png_files = list(case_path.glob("*.png"))
        png_count = len(png_files)
        
        # 检查输出中的关键信息
        output = result.stdout + result.stderr
        
        if result.returncode == 0:
            print(f"✓ 运行成功")
            print(f"✓ 生成图片：{png_count}张")
            
            # 提取性能指标
            metrics = {}
            if "稳态误差" in output:
                for line in output.split('\n'):
                    if "稳态误差" in line and "m" in line:
                        print(f"  {line.strip()}")
                        metrics['steady_error'] = line.strip()
                    elif "最终水位" in line and "m" in line:
                        print(f"  {line.strip()}")
                        metrics['final_level'] = line.strip()
            
            return {
                "status": "success",
                "images": png_count,
                "metrics": metrics
            }
        else:
            print(f"✗ 运行失败")
            error_lines = result.stderr.split('\n')[-10:]
            print("错误信息（最后10行）:")
            for line in error_lines:
                if line.strip():
                    print(f"  {line}")
            return {
                "status": "error",
                "message": result.stderr[-500:]
            }
    
    except subprocess.TimeoutExpired:
        print(f"✗ 运行超时（>120秒）")
        return {"status": "timeout"}
    except Exception as e:
        print(f"✗ 异常：{str(e)}")
        return {"status": "exception", "message": str(e)}

def main():
    """主函数"""
    print("="*80)
    print("案例2-6运行测试")
    print(f"测试时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    cases = [
        ("案例2：工业冷却塔", CASES_DIR / "case_02_cooling_tower"),
        ("案例3：供水泵站", CASES_DIR / "case_03_water_supply_station"),
        ("案例4：PID控制", CASES_DIR / "case_04_pid_tuning"),
        ("案例5：参数辨识", CASES_DIR / "case_05_parameter_identification"),
        ("案例6：阶跃响应", CASES_DIR / "case_06_step_response"),
    ]
    
    results = {}
    
    for case_name, case_path in cases:
        result = test_case(case_name, case_path)
        results[case_name] = result
    
    # 生成总结
    print("\n" + "="*80)
    print("测试总结")
    print("="*80)
    
    success_count = sum(1 for r in results.values() if r['status'] == 'success')
    total_count = len(results)
    
    print(f"\n成功：{success_count}/{total_count}")
    print(f"成功率：{success_count/total_count*100:.1f}%")
    
    print("\n各案例状态：")
    for case_name, result in results.items():
        status_icon = "✓" if result['status'] == 'success' else "✗"
        print(f"  {status_icon} {case_name}: {result['status']}")
        if result['status'] == 'success':
            print(f"     图片：{result['images']}张")
    
    # 保存报告
    report_file = Path(__file__).parent / "案例2-6测试报告.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump({
            "test_time": datetime.now().isoformat(),
            "results": results,
            "summary": {
                "total": total_count,
                "success": success_count,
                "success_rate": f"{success_count/total_count*100:.1f}%"
            }
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n报告已保存：{report_file}")

if __name__ == "__main__":
    main()



