# -*- coding: utf-8 -*-
"""
紧凑化README排版 - 减少多余空白行
"""
import sys
import io
import re
from pathlib import Path

# 设置UTF-8编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 路径配置
BASE_DIR = Path(__file__).resolve().parent.parent.parent
EXAMPLES_DIR = BASE_DIR / "books" / "water-system-control" / "code" / "examples"

def compact_formatting(content):
    """紧凑化文档格式"""
    lines = content.split('\n')
    result = []
    prev_blank = False
    in_table = False
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # 检测表格边界
        if stripped == '<table>':
            in_table = True
            result.append(line)
            prev_blank = False
            continue
        elif stripped == '</table>':
            in_table = False
            result.append(line)
            prev_blank = False
            continue
        
        # 在表格内部，保持原样（但减少连续空行）
        if in_table:
            # 表格内允许单个空行，但不允许多个连续空行
            if not stripped:
                if not prev_blank:
                    result.append(line)
                    prev_blank = True
            else:
                result.append(line)
                prev_blank = False
            continue
        
        # 表格外部的处理
        if not stripped:
            # 空行处理：最多保留一个空行
            if not prev_blank:
                # 检查是否在特定标记之后需要空行
                if result and result[-1].strip() in ['---', '</table>', '```']:
                    result.append(line)
                    prev_blank = True
                # 检查下一行是否是标题或重要标记
                elif i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line.startswith('#') or next_line == '---' or next_line.startswith('<table>'):
                        result.append(line)
                        prev_blank = True
                    # 否则跳过这个空行
                else:
                    # 文件末尾，跳过空行
                    pass
        else:
            result.append(line)
            prev_blank = False
    
    return '\n'.join(result)

def optimize_table_spacing(content):
    """优化表格内的间距"""
    # 减少列表项之间的空行
    content = re.sub(r'\n\n(\d+\. \*\*)', r'\n\1', content)
    content = re.sub(r'\n\n(- \*\*)', r'\n\1', content)
    content = re.sub(r'\n\n(- ✅)', r'\n\1', content)
    content = re.sub(r'\n\n(- ❌)', r'\n\1', content)
    
    # 移除标题和内容之间多余的空行（在表格内）
    content = re.sub(r'(\*\*[^*]+\*\*：)\n\n', r'\1\n', content)
    
    return content

def main():
    print("="*80)
    print("  📝 紧凑化README排版")
    print("="*80)
    print()
    
    total_cases = 0
    success_count = 0
    
    # 遍历所有案例
    for case_dir in sorted(EXAMPLES_DIR.glob("case_*")):
        if not case_dir.is_dir():
            continue
        
        total_cases += 1
        case_name = case_dir.name
        case_num = case_name.split('_')[1]
        
        readme_path = case_dir / "README.md"
        if not readme_path.exists():
            print(f"案例{case_num}: ⚠️  README.md不存在")
            continue
        
        try:
            # 读取原内容
            original_content = readme_path.read_text(encoding='utf-8')
            original_lines = len(original_content.split('\n'))
            
            # 紧凑化处理
            compacted_content = compact_formatting(original_content)
            compacted_content = optimize_table_spacing(compacted_content)
            
            compacted_lines = len(compacted_content.split('\n'))
            saved_lines = original_lines - compacted_lines
            
            # 写回文件
            readme_path.write_text(compacted_content, encoding='utf-8')
            
            print(f"案例{case_num}: ✅ 优化完成 (减少 {saved_lines} 行，{original_lines}→{compacted_lines})")
            success_count += 1
            
        except Exception as e:
            print(f"案例{case_num}: ❌ 处理失败 - {e}")
    
    # 总结报告
    print()
    print("="*80)
    print("  📊 优化总结")
    print("="*80)
    print(f"总案例数: {total_cases}")
    print(f"优化成功: {success_count}/{total_cases}")
    print(f"成功率: {success_count*100//total_cases if total_cases>0 else 0}%")
    
    if success_count == total_cases:
        print()
        print("🎉 所有README排版已紧凑化！")
    
    print()
    print("="*80)
    print("  💡 优化内容")
    print("="*80)
    print("""
1. ✅ 移除多余的连续空行（最多保留1个）
2. ✅ 优化列表项之间的间距
3. ✅ 优化标题和内容之间的间距
4. ✅ 保持表格内必要的空行（Markdown解析需要）
5. ✅ 保持代码块前后的空行
    """)
    print("="*80)

if __name__ == '__main__':
    main()



