#!/usr/bin/env python3
"""
水系统控制论 - 完整自动化测试
测试所有20个案例并生成详细报告
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from pathlib import Path
import json
import subprocess
import os
from datetime import datetime
import time

# 路径设置
BACKEND_DIR = Path(__file__).parent
CASES_INDEX_FILE = BACKEND_DIR / "cases_index.json"
BOOKS_BASE_DIR = BACKEND_DIR.parent.parent  # 指向CHS-Books根目录

def load_cases_index():
    """加载案例索引"""
    with open(CASES_INDEX_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def test_single_case(case_id, case_path, case_title):
    """测试单个案例"""
    print(f"\n{'='*80}")
    print(f"测试案例: {case_id}")
    print(f"标题: {case_title}")
    print(f"路径: {case_path}")
    print(f"{'='*80}")
    
    main_file = case_path / "main.py"
    if not main_file.exists():
        print(f"❌ main.py 不存在")
        return {
            "case_id": case_id,
            "title": case_title,
            "success": False,
            "error": "main.py不存在",
            "execution_time": 0
        }
    
    # 执行案例
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    
    start_time = time.time()
    try:
        result = subprocess.run(
            [sys.executable, str(main_file)],
            cwd=str(case_path),
            capture_output=True,
            text=True,
            timeout=60,
            encoding='utf-8',
            errors='replace',
            env=env
        )
        execution_time = time.time() - start_time
        
        success = result.returncode == 0
        
        if success:
            print(f"✅ 执行成功！(耗时: {execution_time:.2f}秒)")
            # 统计输出信息
            lines = [l for l in result.stdout.split('\n') if l.strip()]
            print(f"📊 输出行数: {len(lines)}")
            
            # 显示前3行和后3行
            if len(lines) > 6:
                print(f"\n输出预览（前3行）:")
                for line in lines[:3]:
                    print(f"  {line[:100]}")
                print(f"  ...")
                print(f"输出预览（后3行）:")
                for line in lines[-3:]:
                    print(f"  {line[:100]}")
            else:
                print(f"\n完整输出:")
                for line in lines:
                    print(f"  {line[:100]}")
        else:
            print(f"❌ 执行失败！(返回码: {result.returncode})")
            if result.stderr:
                error_lines = [l for l in result.stderr.split('\n') if l.strip()][:5]
                print(f"错误信息:")
                for line in error_lines:
                    print(f"  {line}")
        
        return {
            "case_id": case_id,
            "title": case_title,
            "success": success,
            "returncode": result.returncode,
            "execution_time": execution_time,
            "stdout_lines": len(result.stdout.split('\n')),
            "stderr_lines": len(result.stderr.split('\n')) if result.stderr else 0,
            "error": result.stderr[-500:] if not success and result.stderr else None
        }
        
    except subprocess.TimeoutExpired:
        execution_time = time.time() - start_time
        print(f"⏱️ 执行超时 (>60秒)")
        return {
            "case_id": case_id,
            "title": case_title,
            "success": False,
            "error": "执行超时",
            "execution_time": execution_time
        }
    except Exception as e:
        execution_time = time.time() - start_time
        print(f"❌ 执行异常: {str(e)}")
        return {
            "case_id": case_id,
            "title": case_title,
            "success": False,
            "error": str(e),
            "execution_time": execution_time
        }

def main():
    """主测试函数"""
    print("\n" + "="*80)
    print("🚀 水系统控制论 - 完整自动化测试系统")
    print("="*80)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 加载案例索引
    cases_index = load_cases_index()
    
    # 查找水系统控制论的案例
    book_slug = "water-system-control"
    water_cases = None
    
    for book in cases_index.get("books", []):
        if book["slug"] == book_slug:
            water_cases = book.get("cases", [])
            print(f"📚 找到《水系统控制论》: {len(water_cases)} 个案例")
            break
    
    if not water_cases:
        print(f"❌ 未找到《水系统控制论》的案例")
        return
    
    print()
    print(f"准备测试 {len(water_cases)} 个案例...")
    print()
    
    # 测试所有案例
    results = []
    success_count = 0
    total_time = 0
    
    for i, case in enumerate(water_cases, 1):
        case_id = case["id"]
        case_title = case.get("title", case_id)
        case_path = BOOKS_BASE_DIR / case["path"]
        
        print(f"\n[{i}/{len(water_cases)}] ", end="")
        result = test_single_case(case_id, case_path, case_title)
        results.append(result)
        
        if result["success"]:
            success_count += 1
        
        total_time += result.get("execution_time", 0)
    
    # 生成总结报告
    print("\n" + "="*80)
    print("📊 测试总结")
    print("="*80)
    print(f"测试案例总数: {len(results)}")
    print(f"✅ 成功: {success_count}")
    print(f"❌ 失败: {len(results) - success_count}")
    print(f"成功率: {success_count / len(results) * 100:.1f}%")
    print(f"总耗时: {total_time:.2f}秒")
    print(f"平均耗时: {total_time / len(results):.2f}秒/案例")
    print()
    
    # 显示失败的案例
    failed_cases = [r for r in results if not r["success"]]
    if failed_cases:
        print("❌ 失败的案例:")
        for r in failed_cases:
            print(f"  - {r['case_id']}: {r.get('error', '未知错误')}")
        print()
    
    # 显示成功的案例
    print("✅ 成功的案例:")
    for r in results:
        if r["success"]:
            print(f"  - {r['case_id']}: {r['execution_time']:.2f}秒")
    print()
    
    # 保存详细报告
    report = {
        "test_time": datetime.now().isoformat(),
        "book": "water-system-control",
        "book_title": "水系统控制论",
        "total_cases": len(results),
        "success_count": success_count,
        "failed_count": len(results) - success_count,
        "success_rate": success_count / len(results) if results else 0,
        "total_time": total_time,
        "average_time": total_time / len(results) if results else 0,
        "results": results
    }
    
    report_file = BACKEND_DIR / "water_system_control_test_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"📄 详细报告已保存: {report_file}")
    print()
    
    # 生成Markdown报告
    md_report_file = BACKEND_DIR / "水系统控制论测试报告.md"
    with open(md_report_file, 'w', encoding='utf-8') as f:
        f.write(f"# 水系统控制论 - 完整测试报告\n\n")
        f.write(f"**测试时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n\\n")
        f.write(f"## 测试概要\n\n")
        f.write(f"- **测试案例总数**: {len(results)}\\n")
        f.write(f"- **✅ 成功**: {success_count}\\n")
        f.write(f"- **❌ 失败**: {len(results) - success_count}\\n")
        f.write(f"- **成功率**: {success_count / len(results) * 100:.1f}%\\n")
        f.write(f"- **总耗时**: {total_time:.2f}秒\\n")
        f.write(f"- **平均耗时**: {total_time / len(results):.2f}秒/案例\\n\\n")
        
        f.write(f"## 详细结果\n\n")
        f.write(f"| 序号 | 案例ID | 标题 | 状态 | 耗时(秒) |\\n")
        f.write(f"|------|--------|------|------|----------|\\n")
        for i, r in enumerate(results, 1):
            status = "✅" if r["success"] else "❌"
            time_str = f"{r.get('execution_time', 0):.2f}"
            f.write(f"| {i} | {r['case_id']} | {r['title']} | {status} | {time_str} |\\n")
        
        if failed_cases:
            f.write(f"\\n## 失败案例详情\\n\\n")
            for r in failed_cases:
                f.write(f"### {r['case_id']}\\n\\n")
                f.write(f"- **标题**: {r['title']}\\n")
                f.write(f"- **错误**: {r.get('error', '未知错误')}\\n\\n")
    
    print(f"📄 Markdown报告已保存: {md_report_file}")
    print()
    print(f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    print()

if __name__ == "__main__":
    main()

