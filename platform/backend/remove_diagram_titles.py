# -*- coding: utf-8 -*-
"""
批量移除所有案例示意图中的标题文字
让图片更加简洁专业
"""

import sys
import io
from pathlib import Path
import re

# 设置UTF-8输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 项目根目录
ROOT_DIR = Path(__file__).parent.parent.parent
CASES_DIR = ROOT_DIR / "books" / "water-system-control" / "code" / "examples"

def remove_title_from_diagram(file_path):
    """移除generate_diagram.py中的标题设置"""
    
    if not file_path.exists():
        return False
    
    content = file_path.read_text(encoding='utf-8')
    original_content = content
    
    # 匹配并移除各种标题设置模式
    patterns = [
        # plt.title('xxx')
        (r"plt\.title\(['\"].*?['\"]\)", "# plt.title() removed for cleaner look"),
        # ax.set_title('xxx')
        (r"ax\.set_title\(['\"].*?['\"]\)", "# ax.set_title() removed for cleaner look"),
        # fig.suptitle('xxx')
        (r"fig\.suptitle\(['\"].*?['\"]\)", "# fig.suptitle() removed for cleaner look"),
        # plt.text(x, y, 'Title Text', ...) - 移除所有包含System/Control/Diagram等关键词的文本
        (r"plt\.text\([^)]*?(?:System|Control|Diagram|Tower|Cooling|Supply|Station|Tuning|Identification|Response|Cascade|Feedforward|Modeling|Analysis|State|Observer|Adaptive|Predictive|Sliding|Fuzzy|Neural|Reinforcement|Comparison|Application)[^)]*?\)", "# title text removed for cleaner look"),
        # ax.text(x, y, 'Title Text', ...) - 同上
        (r"ax\.text\([^)]*?(?:System|Control|Diagram|Tower|Cooling|Supply|Station|Tuning|Identification|Response|Cascade|Feedforward|Modeling|Analysis|State|Observer|Adaptive|Predictive|Sliding|Fuzzy|Neural|Reinforcement|Comparison|Application)[^)]*?\)", "# title text removed for cleaner look"),
    ]
    
    modified = False
    for pattern, replacement in patterns:
        new_content = re.sub(pattern, replacement, content)
        if new_content != content:
            content = new_content
            modified = True
    
    # 如果有修改，写回文件
    if modified:
        file_path.write_text(content, encoding='utf-8')
        return True
    
    return False

def process_all_cases():
    """处理所有案例"""
    print("=" * 80)
    print("批量移除示意图标题")
    print("=" * 80)
    print()
    
    success_count = 0
    skip_count = 0
    total_count = 0
    
    for i in range(1, 21):
        case_pattern = f"case_{i:02d}_*"
        case_dirs = list(CASES_DIR.glob(case_pattern))
        
        if not case_dirs:
            continue
        
        case_path = case_dirs[0]
        diagram_file = case_path / "generate_diagram.py"
        
        total_count += 1
        print(f"处理案例 {i:02d}: {case_path.name}")
        
        if not diagram_file.exists():
            print(f"  ⚠️  未找到 generate_diagram.py")
            skip_count += 1
            continue
        
        if remove_title_from_diagram(diagram_file):
            print(f"  ✅ 已移除标题")
            success_count += 1
            
            # 重新生成示意图
            try:
                import subprocess
                result = subprocess.run(
                    [sys.executable, str(diagram_file)],
                    cwd=str(case_path),
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    print(f"  ✅ 示意图已重新生成")
                else:
                    print(f"  ⚠️  重新生成失败: {result.stderr[:100]}")
            except Exception as e:
                print(f"  ⚠️  重新生成出错: {str(e)[:100]}")
        else:
            print(f"  ℹ️  无需修改（已无标题）")
            skip_count += 1
        
        print()
    
    print("=" * 80)
    print("处理完成")
    print("=" * 80)
    print(f"\n总案例数: {total_count}")
    print(f"✅ 已修改: {success_count}")
    print(f"ℹ️  跳过: {skip_count}")

if __name__ == "__main__":
    process_all_cases()

