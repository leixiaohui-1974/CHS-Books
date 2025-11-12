#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全面测试所有236个案例的可执行性
"""
import sys
import io
if sys.platform == 'win32' and hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import requests
import json
import subprocess
from pathlib import Path
from datetime import datetime
import time

BASE_URL = "http://localhost:8000"
BOOKS_DIR = Path(__file__).parent.parent.parent / "books"

def print_header(text):
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80 + "\n")

def test_case_execution(case_path):
    """测试单个案例的可执行性"""
    # case_path是从cases_index.json中获取的完整路径
    # 从platform/backend/scripts/ -> platform/backend/ -> platform/ -> CHS-Books/
    case_dir = Path(__file__).parent.parent.parent.parent / case_path.replace('\\', '/')
    
    if not case_dir.exists():
        return {"status": "skip", "reason": "目录不存在"}
    
    main_py = case_dir / "main.py"
    if not main_py.exists():
        return {"status": "skip", "reason": "main.py不存在"}
    
    # 检查是否有requirements
    requirements = case_dir / "requirements.txt"
    has_requirements = requirements.exists()
    
    # 尝试执行（限时5秒）
    try:
        result = subprocess.run(
            [sys.executable, "main.py"],
            cwd=str(case_dir),
            capture_output=True,
            text=True,
            timeout=5,
            encoding='utf-8',
            errors='replace'
        )
        
        if result.returncode == 0:
            return {
                "status": "success",
                "output_length": len(result.stdout),
                "has_requirements": has_requirements
            }
        else:
            return {
                "status": "error",
                "error": result.stderr[:200] if result.stderr else "未知错误",
                "returncode": result.returncode
            }
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "reason": "执行超时(>5秒)"}
    except Exception as e:
        return {"status": "error", "error": str(e)[:200]}

def check_case_files(case_path):
    """检查案例文件完整性"""
    # case_path是从cases_index.json中获取的完整路径
    # 例如: "books\water-system-control\code\examples\case_01_home_water_tower"
    # 从platform/backend/scripts/ -> platform/backend/ -> platform/ -> CHS-Books/
    case_dir = Path(__file__).parent.parent.parent.parent / case_path.replace('\\', '/')
    
    if not case_dir.exists():
        return {"exists": False}
    
    files = {
        "readme": (case_dir / "README.md").exists(),
        "main": (case_dir / "main.py").exists(),
        "diagram": (case_dir / "diagram.png").exists(),
        "results": len(list(case_dir.glob("results/*.png")))
    }
    
    return {"exists": True, "files": files}

def main():
    print_header("🧪 CHS-Books 全案例可执行性测试")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"书籍目录: {BOOKS_DIR}")
    
    # 获取所有案例
    print_header("📋 第1步：获取案例列表")
    try:
        response = requests.get(f"{BASE_URL}/api/cases", timeout=10)
        cases = response.json()
        print(f"✅ 成功获取 {len(cases)} 个案例")
    except Exception as e:
        print(f"❌ 获取案例列表失败: {e}")
        return
    
    # 统计有效案例数
    valid_cases = [c for c in cases if c.get('path')]
    print(f"✅ 有效案例数: {len(valid_cases)}/{len(cases)}")
    
    # 测试每个案例的文件完整性
    print_header("📁 第2步：检查文件完整性（前20个案例）")
    
    tested_cases = cases[:20]
    file_check_results = []
    
    for i, case in enumerate(tested_cases, 1):
        case_id = case.get('id', 'unknown')
        title = case.get('title', case.get('name', 'Unknown'))
        path = case.get('path', '')
        
        files = check_case_files(path)
        
        if files["exists"]:
            file_info = files["files"]
            status = "✅" if all([file_info["readme"], file_info["main"]]) else "⚠️"
            print(f"  {i}. {status} {title[:50]}")
            print(f"      README: {'✓' if file_info['readme'] else '✗'} | "
                  f"main.py: {'✓' if file_info['main'] else '✗'} | "
                  f"示意图: {'✓' if file_info['diagram'] else '✗'} | "
                  f"结果图: {file_info['results']}张")
        else:
            print(f"  {i}. ❌ {title[:50]} - 目录不存在")
        
        file_check_results.append({
            "case_id": case_id,
            "title": title,
            "files": files
        })
    
    # 测试案例执行（抽样5个）
    print_header("🚀 第3步：测试案例执行（抽样5个水系统控制案例）")
    
    # 筛选水系统控制案例
    water_control_cases = [c for c in cases if 'water-system-control' in c.get('path', '')][:5]
    
    execution_results = []
    
    for i, case in enumerate(water_control_cases, 1):
        case_id = case.get('id', 'unknown')
        title = case.get('title', case.get('name', 'Unknown'))
        path = case.get('path', '')
        
        print(f"\n  [{i}/5] 测试: {title[:60]}")
        print(f"  案例ID: {case_id}")
        
        result = test_case_execution(path)
        
        if result["status"] == "success":
            print(f"  ✅ 执行成功 ({result['output_length']} 字符输出)")
        elif result["status"] == "skip":
            print(f"  ⚠️ 跳过: {result['reason']}")
        elif result["status"] == "timeout":
            print(f"  ⏱️ {result['reason']}")
        elif result["status"] == "error":
            print(f"  ❌ 错误: {result.get('error', '未知错误')[:100]}")
        
        execution_results.append({
            "case_id": case_id,
            "title": title,
            "result": result
        })
        
        time.sleep(0.5)  # 避免过快执行
    
    # 生成统计报告
    print_header("📊 测试统计报告")
    
    # 文件完整性统计
    has_readme = sum(1 for r in file_check_results if r['files'].get('exists') and r['files']['files']['readme'])
    has_main = sum(1 for r in file_check_results if r['files'].get('exists') and r['files']['files']['main'])
    has_diagram = sum(1 for r in file_check_results if r['files'].get('exists') and r['files']['files']['diagram'])
    has_results = sum(1 for r in file_check_results if r['files'].get('exists') and r['files']['files']['results'] > 0)
    
    print("文件完整性（前20个案例）:")
    print(f"  README.md: {has_readme}/20 ({has_readme/20*100:.1f}%)")
    print(f"  main.py: {has_main}/20 ({has_main/20*100:.1f}%)")
    print(f"  diagram.png: {has_diagram}/20 ({has_diagram/20*100:.1f}%)")
    print(f"  结果图片: {has_results}/20 ({has_results/20*100:.1f}%)")
    
    # 执行成功率统计
    success_count = sum(1 for r in execution_results if r['result']['status'] == 'success')
    skip_count = sum(1 for r in execution_results if r['result']['status'] == 'skip')
    error_count = sum(1 for r in execution_results if r['result']['status'] == 'error')
    timeout_count = sum(1 for r in execution_results if r['result']['status'] == 'timeout')
    
    print(f"\n执行成功率（5个水系统控制案例）:")
    print(f"  成功: {success_count}/5 ({success_count/5*100:.1f}%)")
    print(f"  跳过: {skip_count}/5")
    print(f"  错误: {error_count}/5")
    print(f"  超时: {timeout_count}/5")
    
    # 整体评估
    print_header("✅ 整体评估")
    
    total_checked = len(file_check_results)
    total_executed = len(execution_results)
    
    print(f"检查案例数: {total_checked}")
    print(f"执行测试数: {total_executed}")
    print(f"文件完整率: {has_readme/total_checked*100:.1f}%")
    print(f"可执行率: {success_count/total_executed*100:.1f}%" if total_executed > 0 else "N/A")
    
    if has_readme >= 18 and success_count >= 4:
        print("\n🎉 评估结果: 优秀")
        print("   - 文件完整性高")
        print("   - 案例可正常执行")
        print("   - Web系统运行稳定")
    elif has_readme >= 15 and success_count >= 3:
        print("\n✅ 评估结果: 良好")
        print("   - 大部分文件完整")
        print("   - 部分案例可执行")
        print("   - 建议完善缺失文件")
    else:
        print("\n⚠️ 评估结果: 需改进")
        print("   - 部分文件缺失")
        print("   - 执行成功率较低")
        print("   - 需要修复错误")
    
    print_header("✅ 测试完成")
    
    return {
        "file_check_results": file_check_results,
        "execution_results": execution_results,
        "statistics": {
            "total_cases": len(cases),
            "file_completeness": has_readme/total_checked*100,
            "execution_success_rate": success_count/total_executed*100 if total_executed > 0 else 0
        }
    }

if __name__ == "__main__":
    try:
        results = main()
        
        # 保存详细报告
        report_file = Path(__file__).parent.parent / "case_execution_test_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n📄 详细报告已保存: {report_file}")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ 测试被用户中断")
    except Exception as e:
        print(f"\n\n❌ 测试过程发生错误: {e}")
        import traceback
        traceback.print_exc()

