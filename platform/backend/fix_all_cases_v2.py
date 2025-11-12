#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量修复所有案例的编码问题和matplotlib设置 - 改进版
"""

import sys
import io
from pathlib import Path

# 设置标准输出为UTF-8编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 定义根目录
ROOT_DIR = Path(__file__).parent.parent.parent
CASES_DIR = ROOT_DIR / "books" / "water-system-control" / "code" / "examples"

# 需要添加的代码片段
UTF8_ENCODING_FIX = """
# 设置标准输出为UTF-8编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
"""

def fix_main_py(file_path):
    """修复main.py文件"""
    print(f"\n处理: {file_path.relative_to(ROOT_DIR)}")
    
    # 读取文件
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已经修复
    if '# -*- coding: utf-8 -*-' in content and 'sys.stdout = io.TextIOWrapper' in content:
        print("  ✓ 已修复，跳过")
        return False
    
    modified = False
    
    # 1. 添加编码声明
    if '# -*- coding: utf-8 -*-' not in content:
        if content.startswith('#!/usr/bin/env python'):
            content = content.replace('#!/usr/bin/env python3\n', '#!/usr/bin/env python3\n# -*- coding: utf-8 -*-\n', 1)
            modified = True
    
    # 2. 添加matplotlib.use('Agg')
    if 'import matplotlib.pyplot' in content and "matplotlib.use('Agg')" not in content:
        # 在import matplotlib.pyplot之前添加
        content = content.replace(
            'import matplotlib.pyplot as plt',
            "import matplotlib\nmatplotlib.use('Agg')  # 必须在import pyplot之前设置\nimport matplotlib.pyplot as plt"
        )
        modified = True
    
    # 3. 确保有io导入
    if 'import sys' in content and 'import io' not in content:
        content = content.replace('import sys\n', 'import sys\nimport io\n')
        modified = True
    
    # 4. 添加UTF-8输出设置
    if 'sys.stdout = io.TextIOWrapper' not in content:
        # 找到import部分结束的位置
        lines = content.split('\n')
        insert_pos = -1
        for i, line in enumerate(lines):
            if line.startswith('from pathlib import Path') or line.startswith('from Path import'):
                insert_pos = i + 1
                break
        
        if insert_pos > 0:
            lines.insert(insert_pos, '')
            lines.insert(insert_pos + 1, '# 设置标准输出为UTF-8编码')
            lines.insert(insert_pos + 2, "sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')")
            content = '\n'.join(lines)
            modified = True
    
    # 写回文件
    if modified:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("  ✓ 已修复")
        return True
    else:
        print("  - 无需修改")
        return False

def main():
    """主函数"""
    print("="*80)
    print("批量修复所有案例的编码问题 - 改进版")
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
            if fix_main_py(main_file):
                fixed_count += 1
    
    print("\n" + "="*80)
    print(f"处理完成！")
    print(f"  总文件数: {total_count}")
    print(f"  已修复数: {fixed_count}")
    print(f"  无需修改: {total_count - fixed_count}")
    print("="*80)

if __name__ == "__main__":
    main()

