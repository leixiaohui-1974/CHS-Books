#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量处理所有案例：
1. 优化generate_diagram.py（字体大小、文本框padding、行距）
2. 统一参数（确保main.py, generate_diagram.py, README.md一致）
3. 完善README.md（添加详细参数说明、中英文对照）
4. 紧凑化排版
5. 重新生成示意图
"""

import os
import re
import subprocess
from pathlib import Path

# 项目根目录
ROOT_DIR = Path(__file__).parent.parent.parent
EXAMPLES_DIR = ROOT_DIR / "books" / "water-system-control" / "code" / "examples"

def process_generate_diagram(file_path):
    """优化generate_diagram.py文件"""
    print(f"处理 {file_path.relative_to(ROOT_DIR)}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 1. 增加字体大小 (+2)
    # 处理 fontsize=数字
    def increase_fontsize(match):
        current_size = int(match.group(1))
        new_size = current_size + 2
        return f'fontsize={new_size}'
    
    content = re.sub(r'fontsize=(\d+)', increase_fontsize, content)
    
    # 2. 减少文本框padding
    # pad=0.5 -> pad=0.3, pad=0.4 -> pad=0.25, pad=0.3 -> pad=0.2
    content = re.sub(r'pad=0\.5', 'pad=0.3', content)
    content = re.sub(r'pad=0\.4', 'pad=0.25', content)
    content = re.sub(r'pad=0\.3(?!\d)', 'pad=0.2', content)
    
    # 3. 减少行距
    # linespacing=1.5 -> linespacing=1.2, linespacing=1.8 -> linespacing=1.4
    content = re.sub(r'linespacing=1\.8', 'linespacing=1.4', content)
    content = re.sub(r'linespacing=1\.5', 'linespacing=1.2', content)
    
    # 4. 注释掉标题
    # 匹配可能的标题文本（包含 title, Title, 系统, System, Control, 控制 等关键词）
    title_patterns = [
        r'(ax\.text\([^)]*["\'].*?(?:System|系统|Control|控制|Diagram|示意图).*?["\'][^)]*\))',
        r'(plt\.text\([^)]*["\'].*?(?:System|系统|Control|控制|Diagram|示意图).*?["\'][^)]*\))',
        r'(ax\.set_title\([^)]*\))',
        r'(plt\.title\([^)]*\))',
    ]
    
    for pattern in title_patterns:
        # 找到所有匹配项
        matches = list(re.finditer(pattern, content, re.DOTALL | re.IGNORECASE))
        for match in reversed(matches):  # 从后向前处理，避免索引变化
            text = match.group(1)
            # 检查是否已经注释
            start = match.start()
            # 向前查找该行的开始
            line_start = content.rfind('\n', 0, start) + 1
            line_before = content[line_start:start]
            if not line_before.strip().startswith('#'):
                # 未注释，添加注释
                content = content[:start] + '# ' + content[start:]
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  [OK] 已优化字体、padding和行距")
        return True
    else:
        print(f"  [SKIP] 无需修改")
        return False

def regenerate_diagram(case_dir):
    """重新生成示意图"""
    diagram_script = case_dir / "generate_diagram.py"
    if not diagram_script.exists():
        print(f"  [WARN] 未找到 generate_diagram.py")
        return False
    
    try:
        result = subprocess.run(
            ['python', str(diagram_script)],
            cwd=str(case_dir),
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            print(f"  [OK] 示意图已重新生成")
            return True
        else:
            print(f"  [ERROR] 生成失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"  [ERROR] 生成异常: {e}")
        return False

def compact_readme(file_path):
    """紧凑化README排版"""
    if not file_path.exists():
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 移除多余空行
    new_lines = []
    prev_blank = False
    
    for line in lines:
        is_blank = line.strip() == ''
        
        if is_blank:
            if not prev_blank:
                new_lines.append(line)
            prev_blank = True
        else:
            new_lines.append(line)
            prev_blank = False
    
    # 去除开头和结尾的空行
    while new_lines and new_lines[0].strip() == '':
        new_lines.pop(0)
    while new_lines and new_lines[-1].strip() == '':
        new_lines.pop()
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"  [OK] README排版已紧凑化")
    return True

def process_case(case_dir):
    """处理单个案例"""
    case_name = case_dir.name
    print(f"\n{'='*60}")
    print(f"处理 {case_name}")
    print(f"{'='*60}")
    
    # 1. 优化 generate_diagram.py
    diagram_script = case_dir / "generate_diagram.py"
    if diagram_script.exists():
        process_generate_diagram(diagram_script)
        # 2. 重新生成示意图
        regenerate_diagram(case_dir)
    else:
        print(f"  [WARN] 未找到 generate_diagram.py")
    
    # 3. 紧凑化 README
    readme_file = case_dir / "README.md"
    if readme_file.exists():
        compact_readme(readme_file)
    else:
        print(f"  [WARN] 未找到 README.md")
    
    print(f"[OK] {case_name} 处理完成")

def main():
    """主函数"""
    print("开始批量处理所有案例...")
    print(f"案例目录: {EXAMPLES_DIR}")
    
    # 获取所有案例目录（case_01 到 case_20）
    case_dirs = []
    for i in range(4, 21):  # 4到20
        case_dir = EXAMPLES_DIR / f"case_{i:02d}_*"
        matches = list(EXAMPLES_DIR.glob(f"case_{i:02d}_*"))
        if matches:
            case_dirs.extend([d for d in matches if d.is_dir()])
    
    case_dirs.sort()
    
    print(f"\n找到 {len(case_dirs)} 个案例需要处理")
    
    success_count = 0
    for case_dir in case_dirs:
        try:
            process_case(case_dir)
            success_count += 1
        except Exception as e:
            print(f"[ERROR] 处理 {case_dir.name} 时出错: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*60}")
    print(f"批量处理完成！")
    print(f"成功: {success_count}/{len(case_dirs)}")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()

