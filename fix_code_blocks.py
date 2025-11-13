#!/usr/bin/env python3
"""
自动修复Markdown文件中缺少语言标识的代码块
智能检测代码类型并添加语言标识
"""

import os
import re
from pathlib import Path

def detect_code_language(code_content):
    """智能检测代码语言"""
    code = code_content.strip()

    # Python特征检测
    python_patterns = [
        r'^\s*import\s+\w+',
        r'^\s*from\s+\w+\s+import',
        r'^\s*def\s+\w+\s*\(',
        r'^\s*class\s+\w+',
        r'^\s*if\s+__name__\s*==\s*[\'"]__main__[\'"]',
        r'print\s*\(',
        r'^\s*#\s+',
    ]

    # Bash/Shell特征检测
    bash_patterns = [
        r'^\s*#!/bin/(bash|sh)',
        r'^\s*(cd|ls|mkdir|echo|grep|cat)\s+',
        r'\$\{?\w+\}?',
        r'^\s*export\s+',
    ]

    # JSON特征检测
    json_patterns = [
        r'^\s*[\{\[]',
        r'"\w+"\s*:\s*',
    ]

    # MATLAB特征检测
    matlab_patterns = [
        r'^\s*function\s+',
        r'\bdisp\(',
        r'\bplot\(',
        r'%\s+',
    ]

    # 数学公式特征
    math_patterns = [
        r'\\frac\{',
        r'\\int_',
        r'\\sum_',
        r'\$\$',
    ]

    # 检测Python
    for pattern in python_patterns:
        if re.search(pattern, code, re.MULTILINE):
            return 'python'

    # 检测Bash
    for pattern in bash_patterns:
        if re.search(pattern, code, re.MULTILINE):
            return 'bash'

    # 检测JSON
    for pattern in json_patterns:
        if re.search(pattern, code, re.MULTILINE):
            return 'json'

    # 检测MATLAB
    for pattern in matlab_patterns:
        if re.search(pattern, code, re.MULTILINE):
            return 'matlab'

    # 检测数学公式
    for pattern in math_patterns:
        if re.search(pattern, code, re.MULTILINE):
            return 'math'

    # 默认Python（因为这是水利工程书籍，大部分是Python）
    return 'python'

def fix_code_blocks_in_file(filepath):
    """修复单个文件中的代码块"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content
        fixed_count = 0

        # 查找所有代码块: ```(没有语言标识的)
        # 匹配模式: ```\n 或 ``` \n（后面跟换行符，没有语言名）
        pattern = r'```[ \t]*\n(.*?)```'

        def replace_code_block(match):
            nonlocal fixed_count
            code_content = match.group(1)

            # 检测语言
            language = detect_code_language(code_content)

            fixed_count += 1
            return f'```{language}\n{code_content}```'

        # 替换所有匹配的代码块
        content = re.sub(pattern, replace_code_block, content, flags=re.DOTALL)

        # 只有在有修改时才写入
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return fixed_count
        else:
            return 0

    except Exception as e:
        print(f"  ❌ 处理文件失败: {e}")
        return 0

def main():
    """主函数"""
    print("="*80)
    print("自动修复代码块语言标识")
    print("="*80)

    # 扫描所有专业教材的README.md
    base_dir = Path('books')

    if not base_dir.exists():
        print("❌ books目录不存在")
        return 1

    total_files = 0
    total_fixed = 0

    # 查找所有README.md文件
    for readme in base_dir.rglob('README.md'):
        total_files += 1
        rel_path = readme.relative_to(base_dir)

        print(f"\n处理: {rel_path}")
        fixed_count = fix_code_blocks_in_file(readme)

        if fixed_count > 0:
            print(f"  ✅ 修复了 {fixed_count} 个代码块")
            total_fixed += fixed_count
        else:
            print(f"  跳过（无需修复）")

    print("\n" + "="*80)
    print(f"总计: 处理 {total_files} 个文件, 修复 {total_fixed} 个代码块")
    print("="*80)

    return 0

if __name__ == "__main__":
    exit(main())
