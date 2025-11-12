#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量修复所有案例的编码问题和matplotlib设置
"""

import os
import re
import sys
import io
from pathlib import Path

# 设置标准输出为UTF-8编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 定义根目录
ROOT_DIR = Path(__file__).parent.parent.parent
CASES_DIR = ROOT_DIR / "books" / "water-system-control" / "code" / "examples"

def fix_encoding_issue(file_path):
    """修复单个Python文件的编码问题"""
    
    print(f"\n处理文件: {file_path.relative_to(ROOT_DIR)}")
    
    # 读取文件
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已经修复
    if '# -*- coding: utf-8 -*-' in content and 'sys.stdout = io.TextIOWrapper' in content:
        print("  ✓ 已修复，跳过")
        return False
    
    lines = content.split('\n')
    new_lines = []
    
    # 标记位置
    found_shebang = False
    found_imports = False
    added_encoding = False
    added_stdout_fix = False
    added_matplotlib_fix = False
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # 1. 处理shebang行
        if i == 0 and line.startswith('#!/usr/bin/env python'):
            new_lines.append(line)
            # 添加编码声明
            if i + 1 < len(lines) and not lines[i + 1].startswith('# -*- coding:'):
                new_lines.append('# -*- coding: utf-8 -*-')
                added_encoding = True
            found_shebang = True
            i += 1
            continue
        
        # 2. 跳过已有的编码声明
        if '# -*- coding:' in line or '# coding:' in line:
            i += 1
            continue
        
        # 3. 处理import部分
        if line.startswith('import ') or line.startswith('from '):
            if not found_imports:
                found_imports = True
                
                # 检查是否需要添加matplotlib.use('Agg')
                if 'import matplotlib.pyplot' in line or 'from matplotlib' in line:
                    if not added_matplotlib_fix:
                        # 在matplotlib导入之前添加
                        new_lines.append('import matplotlib')
                        new_lines.append("matplotlib.use('Agg')  # 必须在import pyplot之前设置")
                        added_matplotlib_fix = True
                    
                    # 修改导入语句
                    if 'import matplotlib.pyplot' in line:
                        new_lines.append(line)
                        i += 1
                        continue
                
                # 添加io导入（如果还没有）
                if 'import sys' in line and not added_stdout_fix:
                    new_lines.append(line)
                    # 检查下一行是否有os导入
                    if i + 1 < len(lines) and 'import os' in lines[i + 1]:
                        i += 1
                        new_lines.append(lines[i])
                    # 添加io导入
                    if 'import io' not in content[:content.find(line) + 100]:
                        new_lines.append('import io')
                    i += 1
                    continue
        
        # 4. 在import结束后添加stdout修复
        if found_imports and not added_stdout_fix:
            # 检查是否import部分结束
            if line.strip() == '' or (not line.startswith('import ') and not line.startswith('from ') and line.strip() and not line.startswith('#')):
                # 添加stdout修复
                new_lines.append('')
                new_lines.append('# 设置标准输出为UTF-8编码')
                new_lines.append("sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')")
                added_stdout_fix = True
        
        new_lines.append(line)
        i += 1
    
    # 写回文件
    new_content = '\n'.join(new_lines)
    
    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"  ✓ 已修复")
        return True
    else:
        print(f"  - 无需修改")
        return False

def main():
    """主函数"""
    print("="*80)
    print("批量修复所有案例的编码问题")
    print("="*80)
    
    fixed_count = 0
    total_count = 0
    
    # 遍历所有案例目录
    for case_dir in sorted(CASES_DIR.glob("case_*")):
        if not case_dir.is_dir():
            continue
        
        # 查找main.py文件
        main_file = case_dir / "main.py"
        if main_file.exists():
            total_count += 1
            if fix_encoding_issue(main_file):
                fixed_count += 1
        
        # 查找experiments.py文件
        exp_file = case_dir / "experiments.py"
        if exp_file.exists():
            total_count += 1
            if fix_encoding_issue(exp_file):
                fixed_count += 1
    
    print("\n" + "="*80)
    print(f"处理完成！")
    print(f"  总文件数: {total_count}")
    print(f"  已修复数: {fixed_count}")
    print(f"  无需修改: {total_count - fixed_count}")
    print("="*80)

if __name__ == "__main__":
    main()

