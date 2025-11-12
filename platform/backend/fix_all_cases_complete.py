# -*- coding: utf-8 -*-
"""
完整修复所有案例
1. 移除所有图表标题
2. 优化系统参数
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

def remove_plot_titles(file_path):
    """移除Python脚本中的所有图表标题"""
    content = file_path.read_text(encoding='utf-8')
    original = content
    
    # 移除 ax.set_title(...) 行
    content = re.sub(
        r"^\s*ax\d?\.set_title\([^)]+\).*$",
        "    # 标题已移除，保持图表简洁",
        content,
        flags=re.MULTILINE
    )
    
    # 移除 plt.title(...) 行
    content = re.sub(
        r"^\s*plt\.title\([^)]+\).*$",
        "    # 标题已移除，保持图表简洁",
        content,
        flags=re.MULTILINE
    )
    
    # 移除 fig.suptitle(...) 行
    content = re.sub(
        r"^\s*fig\.suptitle\([^)]+\).*$",
        "    # 标题已移除，保持图表简洁",
        content,
        flags=re.MULTILINE
    )
    
    if content != original:
        file_path.write_text(content, encoding='utf-8')
        return True
    return False

def fix_case_parameters(case_path, case_num):
    """修复案例参数"""
    main_py = case_path / "main.py"
    if not main_py.exists():
        return False
    
    content = main_py.read_text(encoding='utf-8')
    original = content
    
    # 案例1：优化参数
    if case_num == 1:
        content = re.sub(
            r"SingleTank\(\s*A=2\.0,\s*R=2\.0,\s*K=1\.0\s*\)",
            "SingleTank(A=2.0, R=5.0, K=1.2)",
            content
        )
        content = re.sub(
            r"tank\.reset\(h0=2\.0\)",
            "tank.reset(h0=2.8)",
            content
        )
    
    # 案例2：优化参数
    if case_num == 2:
        content = re.sub(
            r"SingleTank\(\s*A=2\.0,\s*R=2\.0,\s*K=1\.0\s*\)",
            "SingleTank(A=2.0, R=5.0, K=1.5)",
            content
        )
        content = re.sub(
            r"tank\.reset\(h0=2\.0\)",
            "tank.reset(h0=2.5)",
            content
        )
    
    if content != original:
        main_py.write_text(content, encoding='utf-8')
        return True
    return False

def regenerate_case(case_path):
    """重新运行案例生成图片"""
    main_py = case_path / "main.py"
    if not main_py.exists():
        return False, "main.py不存在"
    
    try:
        result = subprocess.run(
            [sys.executable, str(main_py)],
            cwd=str(case_path),
            capture_output=True,
            text=True,
            timeout=30,
            encoding='utf-8',
            errors='ignore'
        )
        
        if result.returncode == 0:
            return True, "成功"
        else:
            return False, result.stderr[:200]
    except subprocess.TimeoutExpired:
        return False, "超时"
    except Exception as e:
        return False, str(e)[:200]

def main():
    print("=" * 80)
    print("完整修复所有案例")
    print("=" * 80)
    print()
    
    for i in range(1, 21):
        case_pattern = f"case_{i:02d}_*"
        case_dirs = list(CASES_DIR.glob(case_pattern))
        
        if not case_dirs:
            continue
        
        case_path = case_dirs[0]
        print(f"\n{'='*80}")
        print(f"处理案例 {i:02d}: {case_path.name}")
        print(f"{'='*80}")
        
        # 步骤1: 移除generate_diagram.py中的标题
        diagram_py = case_path / "generate_diagram.py"
        if diagram_py.exists():
            if remove_plot_titles(diagram_py):
                print("  ✅ 已移除示意图标题")
                # 重新生成示意图
                try:
                    subprocess.run(
                        [sys.executable, str(diagram_py)],
                        cwd=str(case_path),
                        capture_output=True,
                        timeout=15
                    )
                    print("  ✅ 示意图已重新生成")
                except:
                    print("  ⚠️  示意图生成失败")
            else:
                print("  ℹ️  示意图已无标题")
        else:
            print("  ℹ️  无示意图脚本")
        
        # 步骤2: 移除main.py中的图表标题
        main_py = case_path / "main.py"
        if main_py.exists():
            if remove_plot_titles(main_py):
                print("  ✅ 已移除结果图标题")
            else:
                print("  ℹ️  结果图已无标题")
        
        # 步骤3: 修复参数
        if fix_case_parameters(case_path, i):
            print("  ✅ 已优化系统参数")
        
        # 步骤4: 重新运行生成结果图
        if main_py.exists():
            print("  🔄 正在重新生成结果图...")
            success, message = regenerate_case(case_path)
            if success:
                print("  ✅ 结果图已重新生成")
            else:
                print(f"  ❌ 生成失败: {message}")
    
    print("\n" + "=" * 80)
    print("修复完成！")
    print("=" * 80)

if __name__ == "__main__":
    main()



