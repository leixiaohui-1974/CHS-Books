#!/usr/bin/env python3
"""
自动测试水系统控制论的所有案例
"""

import sys
import io
import subprocess
import json
from pathlib import Path
from datetime import datetime
import time

# 设置UTF-8编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 配置
BOOKS_BASE = Path(__file__).parent.parent.parent / "books"
BOOK_PATH = BOOKS_BASE / "water-system-control" / "code" / "examples"

def test_case(case_id: str, case_path: Path) -> dict:
    """测试单个案例"""
    print(f"\n{'=' * 60}")
    print(f"📝 测试案例: {case_id}")
    print(f"{'=' * 60}")
    
    # 检查文件
    main_file = case_path / "main.py"
    readme_file = case_path / "README.md"
    
    if not main_file.exists():
        print(f"❌ main.py 不存在")
        return {
            "case_id": case_id,
            "success": False,
            "error": "main.py不存在"
        }
    
    # 读取README
    readme_content = ""
    if readme_file.exists():
        with open(readme_file, 'r', encoding='utf-8') as f:
            readme_content = f.read()
            # 提取标题
            first_line = readme_content.split('\n')[0]
            if first_line.startswith('#'):
                case_title = first_line.lstrip('#').strip()
                print(f"📖 {case_title}")
    
    print(f"📂 路径: {case_path}")
    print(f"🔧 运行 main.py...")
    
    # 运行案例
    start_time = time.time()
    try:
        result = subprocess.run(
            [sys.executable, str(main_file)],
            cwd=str(case_path),
            capture_output=True,
            text=True,
            timeout=60,
            encoding='utf-8',
            errors='replace'
        )
        execution_time = time.time() - start_time
        
        # 判断是否成功
        success = result.returncode == 0
        
        if success:
            print(f"✅ 执行成功 (耗时: {execution_time:.2f}秒)")
            
            # 检查输出
            if result.stdout:
                lines = result.stdout.split('\n')
                print(f"📊 输出行数: {len(lines)}")
                # 显示前3行和后3行
                print("\n输出预览:")
                for line in lines[:3]:
                    if line.strip():
                        print(f"  {line[:100]}")
                if len(lines) > 6:
                    print("  ...")
                    for line in lines[-3:]:
                        if line.strip():
                            print(f"  {line[:100]}")
        else:
            print(f"❌ 执行失败 (返回码: {result.returncode})")
            if result.stderr:
                print(f"\n错误信息:")
                for line in result.stderr.split('\n')[:10]:
                    if line.strip():
                        print(f"  {line}")
        
        return {
            "case_id": case_id,
            "success": success,
            "returncode": result.returncode,
            "execution_time": execution_time,
            "stdout_lines": len(result.stdout.split('\n')),
            "stderr_lines": len(result.stderr.split('\n')) if result.stderr else 0,
            "has_readme": readme_file.exists()
        }
        
    except subprocess.TimeoutExpired:
        print(f"⏱️ 执行超时 (>60秒)")
        return {
            "case_id": case_id,
            "success": False,
            "error": "执行超时"
        }
    except Exception as e:
        print(f"❌ 执行异常: {str(e)}")
        return {
            "case_id": case_id,
            "success": False,
            "error": str(e)
        }

def main():
    """主测试函数"""
    print("=" * 60)
    print("🧪 水系统控制论 - 自动测试系统")
    print("=" * 60)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    if not BOOK_PATH.exists():
        print(f"❌ 找不到案例目录: {BOOK_PATH}")
        return
    
    # 扫描所有案例
    cases = []
    for case_dir in sorted(BOOK_PATH.iterdir()):
        if case_dir.is_dir() and case_dir.name.startswith('case_'):
            cases.append(case_dir)
    
    print(f"📚 找到 {len(cases)} 个案例")
    print()
    
    # 测试所有案例
    results = []
    success_count = 0
    
    for i, case_dir in enumerate(cases, 1):
        print(f"\n进度: [{i}/{len(cases)}]")
        
        result = test_case(case_dir.name, case_dir)
        results.append(result)
        
        if result['success']:
            success_count += 1
    
    # 生成报告
    print("\n" + "=" * 60)
    print("📊 测试总结")
    print("=" * 60)
    print(f"总案例数: {len(results)}")
    print(f"✅ 成功: {success_count}")
    print(f"❌ 失败: {len(results) - success_count}")
    print(f"成功率: {success_count / len(results) * 100:.1f}%")
    print()
    
    # 列出失败的案例
    failed_cases = [r for r in results if not r['success']]
    if failed_cases:
        print("失败案例:")
        for r in failed_cases:
            error = r.get('error', '未知错误')
            print(f"  ❌ {r['case_id']}: {error}")
    
    # 保存详细报告
    report = {
        "test_time": datetime.now().isoformat(),
        "book": "water-system-control",
        "total_cases": len(results),
        "success_count": success_count,
        "success_rate": success_count / len(results) if results else 0,
        "results": results
    }
    
    report_file = Path(__file__).parent / "test_report_water_system_control.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 详细报告已保存: {report_file}")
    print(f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

if __name__ == "__main__":
    main()

