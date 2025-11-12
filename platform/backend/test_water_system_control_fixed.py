#!/usr/bin/env python3
"""
自动测试水系统控制论的所有案例 - 修复版
"""

import sys
import io
import subprocess
import json
from pathlib import Path
from datetime import datetime
import time
import os

# 设置UTF-8编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 设置环境变量强制使用UTF-8
os.environ['PYTHONIOENCODING'] = 'utf-8'

# 配置
BOOKS_BASE = Path(__file__).parent.parent.parent / "books"
BOOK_PATH = BOOKS_BASE / "water-system-control" / "code" / "examples"

def test_case(case_id: str, case_path: Path) -> dict:
    """测试单个案例"""
    print(f"\n{'=' * 60}")
    print(f"测试案例: {case_id}")
    print(f"{'=' * 60}")
    
    # 检查文件
    main_file = case_path / "main.py"
    readme_file = case_path / "README.md"
    
    if not main_file.exists():
        print(f"X main.py 不存在")
        return {
            "case_id": case_id,
            "success": False,
            "error": "main.py不存在"
        }
    
    # 读取README
    if readme_file.exists():
        with open(readme_file, 'r', encoding='utf-8') as f:
            readme_content = f.read()
            first_line = readme_content.split('\n')[0]
            if first_line.startswith('#'):
                case_title = first_line.lstrip('#').strip()
                print(f"标题: {case_title}")
    
    print(f"路径: {case_path}")
    print(f"运行 main.py...")
    
    # 运行案例（添加环境变量）
    start_time = time.time()
    try:
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        
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
            print(f"✓ 执行成功 (耗时: {execution_time:.2f}秒)")
            if result.stdout:
                lines = [l for l in result.stdout.split('\n') if l.strip()]
                print(f"输出行数: {len(lines)}")
        else:
            print(f"X 执行失败 (返回码: {result.returncode})")
            if result.stderr:
                error_lines = result.stderr.split('\n')
                # 只显示最后几行关键错误
                for line in error_lines[-5:]:
                    if line.strip() and not line.startswith('  File'):
                        print(f"  {line}")
        
        return {
            "case_id": case_id,
            "success": success,
            "returncode": result.returncode,
            "execution_time": execution_time,
            "has_readme": readme_file.exists(),
            "error": result.stderr[-500:] if not success and result.stderr else None
        }
        
    except subprocess.TimeoutExpired:
        print(f"超时 (>60秒)")
        return {
            "case_id": case_id,
            "success": False,
            "error": "执行超时"
        }
    except Exception as e:
        print(f"X 执行异常: {str(e)}")
        return {
            "case_id": case_id,
            "success": False,
            "error": str(e)
        }

def main():
    """主测试函数"""
    print("=" * 60)
    print("水系统控制论 - 自动测试系统")
    print("=" * 60)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    if not BOOK_PATH.exists():
        print(f"X 找不到案例目录: {BOOK_PATH}")
        return
    
    # 扫描所有案例
    cases = []
    for case_dir in sorted(BOOK_PATH.iterdir()):
        if case_dir.is_dir() and case_dir.name.startswith('case_'):
            cases.append(case_dir)
    
    print(f"找到 {len(cases)} 个案例")
    print()
    
    # 只测试前5个案例作为快速验证
    test_cases = cases[:5]
    print(f"快速测试前 {len(test_cases)} 个案例...")
    
    # 测试案例
    results = []
    success_count = 0
    
    for i, case_dir in enumerate(test_cases, 1):
        print(f"\n进度: [{i}/{len(test_cases)}]")
        
        result = test_case(case_dir.name, case_dir)
        results.append(result)
        
        if result['success']:
            success_count += 1
    
    # 生成报告
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"测试案例数: {len(results)}")
    print(f"✓ 成功: {success_count}")
    print(f"X 失败: {len(results) - success_count}")
    print(f"成功率: {success_count / len(results) * 100:.1f}%")
    print()
    
    # 保存报告
    report = {
        "test_time": datetime.now().isoformat(),
        "book": "water-system-control",
        "total_cases": len(results),
        "success_count": success_count,
        "success_rate": success_count / len(results) if results else 0,
        "results": results
    }
    
    report_file = Path(__file__).parent / "quick_test_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"详细报告已保存: {report_file}")
    print(f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

if __name__ == "__main__":
    main()

