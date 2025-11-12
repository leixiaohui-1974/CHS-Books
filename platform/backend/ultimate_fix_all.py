# -*- coding: utf-8 -*-
"""
终极修复脚本 - 解决所有问题
1. 添加UTF-8编码设置
2. 移除所有图表标题
3. 优化系统参数
4. 重新生成所有图片
"""

import sys
import io
from pathlib import Path
import re
import subprocess

# 设置UTF-8输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT_DIR = Path(__file__).parent.parent.parent
CASES_DIR = ROOT_DIR / "books" / "water-system-control" / "code" / "examples"

def add_utf8_encoding(file_path):
    """添加UTF-8编码设置"""
    content = file_path.read_text(encoding='utf-8')
    
    # 检查是否已有UTF-8设置
    if 'sys.stdout = io.TextIOWrapper' in content:
        return False
    
    # 在导入后添加UTF-8设置
    pattern = r'(import sys\nimport io\nimport os)'
    replacement = r'\1\n\n# 设置标准输出为UTF-8编码\nsys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding=\'utf-8\')'
    
    new_content = re.sub(pattern, replacement, content)
    
    if new_content != content:
        file_path.write_text(new_content, encoding='utf-8')
        return True
    return False

def remove_all_titles(file_path):
    """移除所有图表标题"""
    content = file_path.read_text(encoding='utf-8')
    original = content
    
    # 移除多行的set_title
    content = re.sub(
        r"ax\d*\.set_title\([^)]*\n[^)]*\)",
        "# 标题已移除",
        content
    )
    
    # 移除单行的set_title
    content = re.sub(
        r"ax\d*\.set_title\([^)]+\)",
        "# 标题已移除",
        content
    )
    
    # 移除plt.title
    content = re.sub(
        r"plt\.title\([^)]+\)",
        "# 标题已移除",
        content
    )
    
    # 移除fig.suptitle
    content = re.sub(
        r"fig\.suptitle\([^)]+\)",
        "# 标题已移除",
        content
    )
    
    if content != original:
        file_path.write_text(content, encoding='utf-8')
        return True
    return False

def optimize_parameters(file_path, case_num):
    """优化案例参数"""
    content = file_path.read_text(encoding='utf-8')
    original = content
    
    if case_num == 1:
        # 优化案例1参数
        content = re.sub(
            r'R=2\.0,\s*#.*阻力系数',
            'R=5.0,    # 阻力系数（优化后）',
            content
        )
        content = re.sub(
            r'K=1\.0\s*#.*泵增益',
            'K=1.2     # 泵增益（优化后）',
            content
        )
        content = re.sub(
            r'h0=2\.0\)',
            'h0=2.8)',
            content
        )
    
    if content != original:
        file_path.write_text(content, encoding='utf-8')
        return True
    return False

def process_case(case_path, case_num):
    """处理单个案例"""
    print(f"\n{'='*70}")
    print(f"案例 {case_num:02d}: {case_path.name}")
    print(f"{'='*70}")
    
    modified = False
    
    # 1. 处理generate_diagram.py
    diagram_py = case_path / "generate_diagram.py"
    if diagram_py.exists():
        if add_utf8_encoding(diagram_py):
            print("  ✅ 添加UTF-8编码（示意图）")
            modified = True
        if remove_all_titles(diagram_py):
            print("  ✅ 移除示意图标题")
            modified = True
        
        # 重新生成示意图
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
                print("  ✅ 示意图已重新生成")
            else:
                print(f"  ⚠️  示意图生成警告")
        except Exception as e:
            print(f"  ⚠️  示意图生成失败: {str(e)[:50]}")
    
    # 2. 处理main.py
    main_py = case_path / "main.py"
    if main_py.exists():
        if add_utf8_encoding(main_py):
            print("  ✅ 添加UTF-8编码（主程序）")
            modified = True
        if remove_all_titles(main_py):
            print("  ✅ 移除结果图标题")
            modified = True
        if optimize_parameters(main_py, case_num):
            print("  ✅ 优化系统参数")
            modified = True
        
        # 重新生成结果图
        print("  🔄 重新生成结果图...")
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
                print("  ✅ 结果图已重新生成")
            else:
                error = result.stderr if result.stderr else result.stdout
                print(f"  ❌ 生成失败: {error[:100]}")
        except subprocess.TimeoutExpired:
            print("  ❌ 超时（>60秒）")
        except Exception as e:
            print(f"  ❌ 错误: {str(e)[:100]}")
    
    if not modified:
        print("  ℹ️  无需修改")
    
    return modified

def main():
    print("=" * 70)
    print("🔧 终极修复脚本 - 解决所有问题")
    print("=" * 70)
    
    total_modified = 0
    
    for i in range(1, 21):
        case_dirs = list(CASES_DIR.glob(f"case_{i:02d}_*"))
        if case_dirs:
            if process_case(case_dirs[0], i):
                total_modified += 1
    
    print("\n" + "=" * 70)
    print(f"✅ 修复完成！共修改 {total_modified} 个案例")
    print("=" * 70)

if __name__ == "__main__":
    main()

