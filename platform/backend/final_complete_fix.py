# -*- coding: utf-8 -*-
"""
最终完整修复方案
修复所有用户提出的需求：
1. 移除所有示意图和结果图的标题
2. 修复案例1的参数和数据问题
3. 重新生成所有图片
"""

import sys
import io
from pathlib import Path
import re
import subprocess

# 设置UTF-8输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 项目根目录
ROOT_DIR = Path(__file__).parent.parent.parent
CASES_DIR = ROOT_DIR / "books" / "water-system-control" / "code" / "examples"

def remove_all_titles(file_path):
    """移除Python文件中所有图表标题"""
    if not file_path.exists():
        return False
        
    content = file_path.read_text(encoding='utf-8')
    original = content
    
    # 移除 ax.set_title(...)，支持换行
    content = re.sub(
        r"ax\d?\.set_title\([^)]+(\n[^)]*)*\)",
        "# 标题已移除",
        content
    )
    
    # 移除 plt.title(...)
    content = re.sub(
        r"plt\.title\([^)]+(\n[^)]*)*\)",
        "# 标题已移除",
        content
    )
    
    # 移除 fig.suptitle(...)
    content = re.sub(
        r"fig\.suptitle\([^)]+(\n[^)]*)*\)",
        "# 标题已移除",
        content
    )
    
    if content != original:
        file_path.write_text(content, encoding='utf-8')
        return True
    return False

def fix_case1_parameters(case_path):
    """修复案例1的参数"""
    main_py = case_path / "main.py"
    if not main_py.exists():
        return False
    
    content = main_py.read_text(encoding='utf-8')
    original = content
    
    # 修复SingleTank参数
    content = re.sub(
        r"SingleTank\s*\(\s*A\s*=\s*2\.0\s*,\s*R\s*=\s*2\.0\s*,\s*K\s*=\s*1\.0\s*\)",
        "SingleTank(A=2.0, R=5.0, K=1.2)",
        content
    )
    
    # 修复初始水位
    content = re.sub(
        r"tank\.reset\s*\(\s*h0\s*=\s*2\.0\s*\)",
        "tank.reset(h0=2.8)",
        content
    )
    
    if content != original:
        main_py.write_text(content, encoding='utf-8')
        return True
    return False

def regenerate_diagrams_and_results(case_path):
    """重新生成示意图和结果图"""
    results = {'diagram': False, 'results': False}
    
    # 1. 重新生成示意图
    diagram_py = case_path / "generate_diagram.py"
    if diagram_py.exists():
        try:
            result = subprocess.run(
                [sys.executable, str(diagram_py)],
                cwd=str(case_path),
                capture_output=True,
                timeout=15,
                encoding='utf-8',
                errors='ignore'
            )
            if result.returncode == 0:
                results['diagram'] = True
        except:
            pass
    
    # 2. 重新生成结果图
    main_py = case_path / "main.py"
    if main_py.exists():
        try:
            result = subprocess.run(
                [sys.executable, str(main_py)],
                cwd=str(case_path),
                capture_output=True,
                timeout=60,
                encoding='utf-8',
                errors='ignore'
            )
            if result.returncode == 0:
                results['results'] = True
        except:
            pass
    
    return results

def main():
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 24 + "最终完整修复方案" + " " * 38 + "║")
    print("╚" + "═" * 78 + "╝")
    print()
    
    total_cases = 0
    success_count = 0
    
    for i in range(1, 21):
        case_pattern = f"case_{i:02d}_*"
        case_dirs = list(CASES_DIR.glob(case_pattern))
        
        if not case_dirs:
            continue
        
        case_path = case_dirs[0]
        case_name = case_path.name
        total_cases += 1
        
        print(f"\n{'━' * 80}")
        print(f"📦 案例 {i:02d}: {case_name}")
        print(f"{'━' * 80}")
        
        case_fixed = False
        
        # 步骤1: 移除示意图标题
        diagram_py = case_path / "generate_diagram.py"
        if diagram_py.exists():
            if remove_all_titles(diagram_py):
                print("  ✅ 示意图标题已移除")
                case_fixed = True
            else:
                print("  ✓  示意图无标题")
        
        # 步骤2: 移除结果图标题
        main_py = case_path / "main.py"
        if main_py.exists():
            if remove_all_titles(main_py):
                print("  ✅ 结果图标题已移除")
                case_fixed = True
            else:
                print("  ✓  结果图无标题")
        
        # 步骤3: 特殊修复案例1
        if i == 1:
            if fix_case1_parameters(case_path):
                print("  ✅ 案例1参数已优化")
                case_fixed = True
        
        # 步骤4: 重新生成图片
        if case_fixed or i == 1:  # 案例1强制重新生成
            print("  🔄 重新生成图片...")
            results = regenerate_diagrams_and_results(case_path)
            
            if results['diagram']:
                print("  ✅ 示意图已生成")
            if results['results']:
                print("  ✅ 结果图已生成")
            
            if results['diagram'] or results['results']:
                success_count += 1
                print(f"  🎉 案例 {i:02d} 修复完成！")
        else:
            print("  ✓  无需修复")
    
    print(f"\n{'━' * 80}")
    print(f"📊 修复统计")
    print(f"{'━' * 80}")
    print(f"  总案例数: {total_cases}")
    print(f"  修复成功: {success_count}")
    print(f"  成功率: {success_count/total_cases*100:.1f}%")
    print()
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 28 + "修复完成！" + " " * 40 + "║")
    print("╚" + "═" * 78 + "╝")

if __name__ == "__main__":
    main()

