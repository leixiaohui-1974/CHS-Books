#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复案例16-20的编码问题
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent
CASES_DIR = ROOT_DIR / "books" / "water-system-control" / "code" / "examples"

def fix_encoding(case_num, case_name):
    """修复单个案例的编码"""
    case_dir = CASES_DIR / case_name
    main_file = case_dir / "main.py"
    
    if not main_file.exists():
        print(f"案例{case_num}: ✗ main.py不存在")
        return False
    
    print(f"\n案例{case_num}: {case_name}")
    
    # 读取文件
    content = main_file.read_text(encoding='utf-8')
    
    # 检查是否已经有编码设置
    if 'sys.stdout = io.TextIOWrapper' in content:
        print("  ✓ 已有编码设置")
        return True
    
    # 在文件开头添加编码设置
    lines = content.split('\n')
    
    # 找到第一个import的位置
    import_idx = 0
    for i, line in enumerate(lines):
        if line.strip().startswith('import ') or line.strip().startswith('from '):
            import_idx = i
            break
    
    # 插入编码设置
    encoding_lines = [
        'import sys',
        'import io',
        'sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding=\'utf-8\')',
        ''
    ]
    
    # 检查是否已有import sys和import io
    has_sys = any('import sys' in line for line in lines[:10])
    has_io = any('import io' in line for line in lines[:10])
    
    if has_sys:
        encoding_lines.remove('import sys')
    if has_io:
        encoding_lines.remove('import io')
    
    # 插入编码设置
    new_lines = lines[:import_idx] + encoding_lines + lines[import_idx:]
    new_content = '\n'.join(new_lines)
    
    # 写回文件
    main_file.write_text(new_content, encoding='utf-8')
    print("  ✓ 已添加编码设置")
    return True

def main():
    """主函数"""
    print("="*60)
    print("修复案例16-20的编码问题")
    print("="*60)
    
    cases = [
        (16, "case_16_fuzzy_control"),
        (18, "case_18_reinforcement_learning_control"),
        (19, "case_19_comprehensive_comparison"),
        (20, "case_20_practical_application"),
    ]
    
    success_count = 0
    
    for case_num, case_name in cases:
        if fix_encoding(case_num, case_name):
            success_count += 1
    
    print("\n" + "="*60)
    print(f"修复完成：{success_count}/{len(cases)}个案例")
    print("="*60)

if __name__ == "__main__":
    main()

