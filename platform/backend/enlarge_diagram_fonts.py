# -*- coding: utf-8 -*-
"""
放大示意图中的字体，但避免重叠
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

def enlarge_fonts(content):
    """
    增大字体大小，按照以下规则：
    - fontsize=8 -> 10
    - fontsize=9 -> 11
    - fontsize=10 -> 12
    - fontsize=11 -> 13
    - fontsize=12 -> 14
    - fontsize=13 -> 15
    - fontsize=14+ 保持不变
    """
    # 替换fontsize参数
    def replace_fontsize(match):
        size = int(match.group(1))
        if size <= 8:
            new_size = 10
        elif size == 9:
            new_size = 11
        elif size == 10:
            new_size = 12
        elif size == 11:
            new_size = 13
        elif size == 12:
            new_size = 14
        elif size == 13:
            new_size = 15
        else:
            new_size = size  # 14及以上保持不变
        return f'fontsize={new_size}'
    
    # 匹配 fontsize=数字
    content = re.sub(r'fontsize=(\d+)', replace_fontsize, content)
    
    return content

def main():
    print("="*80)
    print("  📝 放大示意图字体")
    print("="*80)
    print()
    
    total_cases = 0
    success_count = 0
    font_changes = 0
    
    # 遍历所有案例
    for case_dir in sorted(EXAMPLES_DIR.glob("case_*")):
        if not case_dir.is_dir():
            continue
        
        total_cases += 1
        case_name = case_dir.name
        case_num = case_name.split('_')[1]
        
        diagram_script = case_dir / "generate_diagram.py"
        if not diagram_script.exists():
            print(f"案例{case_num}: ⚠️  未找到 generate_diagram.py")
            continue
        
        try:
            # 读取原内容
            original_content = diagram_script.read_text(encoding='utf-8')
            
            # 计算原始字体数量
            original_fonts = len(re.findall(r'fontsize=(\d+)', original_content))
            
            # 放大字体
            new_content = enlarge_fonts(original_content)
            
            # 计算修改后的字体数量
            if new_content != original_content:
                diagram_script.write_text(new_content, encoding='utf-8')
                
                # 统计变化
                changed_fonts = len(re.findall(r'fontsize=(\d+)', new_content))
                font_changes += changed_fonts
                
                print(f"案例{case_num}: ✅ 字体已放大 ({original_fonts}处)")
                success_count += 1
            else:
                print(f"案例{case_num}: ℹ️  无需修改")
                success_count += 1
                
        except Exception as e:
            print(f"案例{case_num}: ❌ 处理失败 - {e}")
    
    # 总结报告
    print()
    print("="*80)
    print("  📊 处理总结")
    print("="*80)
    print(f"总案例数: {total_cases}")
    print(f"处理成功: {success_count}/{total_cases}")
    print(f"字体修改: {font_changes}处")
    
    if success_count == total_cases:
        print()
        print("🎉 所有示意图字体已优化！")
        print()
        print("💡 下一步：运行以下命令重新生成示意图")
        print("   python platform/backend/regenerate_all_diagrams.py")
    
    print()
    print("="*80)
    print("  📝 字体放大规则")
    print("="*80)
    print("""
原字体 → 新字体
  8px  →  10px  (+2)
  9px  →  11px  (+2)
 10px  →  12px  (+2)
 11px  →  13px  (+2)
 12px  →  14px  (+2)
 13px  →  15px  (+2)
 14px+ →  保持   (已足够大)
    """)
    print("="*80)

if __name__ == '__main__':
    main()



