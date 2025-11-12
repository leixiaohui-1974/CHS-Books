#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Web系统中所有案例的运行情况
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import subprocess
import json
from pathlib import Path
from datetime import datetime

# 项目根目录
ROOT_DIR = Path(__file__).parent.parent.parent
CASES_DIR = ROOT_DIR / "books" / "water-system-control" / "code" / "examples"

def test_case(case_num, case_name):
    """测试单个案例"""
    case_dir = CASES_DIR / case_name
    main_file = case_dir / "main.py"
    
    if not main_file.exists():
        return {
            "status": "skip",
            "message": "main.py不存在",
            "images": 0,
            "time": 0
        }
    
    print(f"\n{'='*60}")
    print(f"案例{case_num}：{case_name}")
    print(f"{'='*60}")
    
    try:
        start_time = datetime.now()
        
        # 运行脚本
        result = subprocess.run(
            [sys.executable, str(main_file)],
            cwd=str(case_dir),
            capture_output=True,
            text=True,
            timeout=120,  # 2分钟超时
            encoding='utf-8',
            errors='replace'
        )
        
        end_time = datetime.now()
        elapsed = (end_time - start_time).total_seconds()
        
        # 检查生成的PNG文件
        png_files = list(case_dir.glob("*.png"))
        diagram_files = [f for f in png_files if 'diagram' in f.name.lower()]
        result_files = [f for f in png_files if 'diagram' not in f.name.lower()]
        
        if result.returncode == 0:
            print(f"✓ 运行成功")
            print(f"✓ 耗时：{elapsed:.1f}秒")
            print(f"✓ 生成图片：{len(result_files)}张结果图")
            if diagram_files:
                print(f"✓ 示意图：{len(diagram_files)}张")
            
            # 提取关键输出信息
            output_lines = result.stdout.split('\n')
            key_info = []
            for line in output_lines[-20:]:  # 最后20行
                if any(keyword in line for keyword in ['成功', '完成', '生成', '保存']):
                    key_info.append(line.strip())
            
            if key_info:
                print("关键信息：")
                for info in key_info[:5]:  # 最多显示5条
                    print(f"  {info}")
            
            return {
                "status": "success",
                "message": "运行成功",
                "images": len(result_files),
                "diagrams": len(diagram_files),
                "time": elapsed,
                "key_info": key_info[:5]
            }
        else:
            print(f"✗ 运行失败（退出码：{result.returncode}）")
            # 提取错误信息
            error_lines = [line for line in result.stderr.split('\n') if line.strip()]
            error_msg = '\n'.join(error_lines[-5:]) if error_lines else "未知错误"
            print(f"错误信息：\n{error_msg}")
            
            return {
                "status": "error",
                "message": error_msg,
                "images": 0,
                "time": elapsed,
                "returncode": result.returncode
            }
    
    except subprocess.TimeoutExpired:
        print(f"✗ 运行超时（>120秒）")
        return {
            "status": "timeout",
            "message": "运行超时",
            "images": 0,
            "time": 120
        }
    except Exception as e:
        print(f"✗ 异常：{str(e)}")
        return {
            "status": "exception",
            "message": str(e),
            "images": 0,
            "time": 0
        }

def main():
    """主函数"""
    print("="*60)
    print("Web系统案例运行测试")
    print(f"测试时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # 所有案例列表
    cases = [
        (1, "case_01_home_water_tower"),
        (2, "case_02_cooling_tower"),
        (3, "case_03_water_supply_station"),
        (4, "case_04_pid_tuning"),
        (5, "case_05_parameter_identification"),
        (6, "case_06_step_response"),
        (7, "case_07_cascade_control"),
        (8, "case_08_feedforward_control"),
        (9, "case_09_system_modeling"),
        (10, "case_10_frequency_analysis"),
        (11, "case_11_state_space"),
        (12, "case_12_observer_lqr"),
        (13, "case_13_adaptive_control"),
        (14, "case_14_model_predictive_control"),
        (15, "case_15_sliding_mode_control"),
        (16, "case_16_fuzzy_control"),
        (17, "case_17_neural_network_control"),
        (18, "case_18_reinforcement_learning_control"),
        (19, "case_19_comprehensive_comparison"),
        (20, "case_20_practical_application"),
    ]
    
    results = {}
    
    # 测试每个案例
    for case_num, case_name in cases:
        result = test_case(case_num, case_name)
        results[f"case_{case_num:02d}"] = result
    
    # 生成总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    
    success_count = sum(1 for r in results.values() if r['status'] == 'success')
    error_count = sum(1 for r in results.values() if r['status'] == 'error')
    timeout_count = sum(1 for r in results.values() if r['status'] == 'timeout')
    skip_count = sum(1 for r in results.values() if r['status'] == 'skip')
    total_count = len(results)
    
    print(f"\n总计：{total_count}个案例")
    print(f"✓ 成功：{success_count}个（{success_count/total_count*100:.1f}%）")
    print(f"✗ 失败：{error_count}个（{error_count/total_count*100:.1f}%）")
    print(f"⏱ 超时：{timeout_count}个（{timeout_count/total_count*100:.1f}%）")
    print(f"⊘ 跳过：{skip_count}个（{skip_count/total_count*100:.1f}%）")
    
    # 详细状态
    print("\n详细状态：")
    for case_num, case_name in cases:
        key = f"case_{case_num:02d}"
        result = results[key]
        status_icon = {
            'success': '✓',
            'error': '✗',
            'timeout': '⏱',
            'skip': '⊘'
        }.get(result['status'], '?')
        
        case_display = f"案例{case_num}"
        print(f"  {status_icon} {case_display:6s}: {result['status']:8s}", end="")
        
        if result['status'] == 'success':
            print(f" - {result['images']}张图，{result['time']:.1f}秒")
        elif result['status'] == 'error':
            print(f" - {result.get('returncode', 'N/A')}")
        else:
            print()
    
    # 失败案例详情
    failed_cases = [(num, name, results[f"case_{num:02d}"]) 
                    for num, name in cases 
                    if results[f"case_{num:02d}"]['status'] in ['error', 'timeout']]
    
    if failed_cases:
        print("\n" + "="*60)
        print("失败案例详情")
        print("="*60)
        for num, name, result in failed_cases:
            print(f"\n案例{num}：{name}")
            print(f"状态：{result['status']}")
            print(f"信息：{result.get('message', 'N/A')[:200]}")
    
    # 性能统计
    success_results = [r for r in results.values() if r['status'] == 'success']
    if success_results:
        total_time = sum(r['time'] for r in success_results)
        avg_time = total_time / len(success_results)
        total_images = sum(r['images'] for r in success_results)
        
        print("\n" + "="*60)
        print("性能统计")
        print("="*60)
        print(f"总运行时间：{total_time:.1f}秒")
        print(f"平均运行时间：{avg_time:.1f}秒/案例")
        print(f"总生成图片：{total_images}张")
        print(f"平均图片数：{total_images/len(success_results):.1f}张/案例")
    
    # 保存报告
    report = {
        "test_time": datetime.now().isoformat(),
        "summary": {
            "total": total_count,
            "success": success_count,
            "error": error_count,
            "timeout": timeout_count,
            "skip": skip_count,
            "success_rate": f"{success_count/total_count*100:.1f}%"
        },
        "results": results
    }
    
    report_file = Path(__file__).parent / "web_test_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n报告已保存：{report_file}")
    
    # 返回状态码
    return 0 if success_count == total_count else 1

if __name__ == "__main__":
    sys.exit(main())



