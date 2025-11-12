# -*- coding: utf-8 -*-
"""
批量重新生成所有案例的示意图
确保图片没有标题
"""

import sys
import io
from pathlib import Path
import subprocess

# 设置UTF-8输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 项目根目录
ROOT_DIR = Path(__file__).parent.parent.parent
CASES_DIR = ROOT_DIR / "books" / "water-system-control" / "code" / "examples"

def regenerate_diagram(case_path):
    """重新生成案例的示意图"""
    diagram_script = case_path / "generate_diagram.py"
    
    if not diagram_script.exists():
        return False, "未找到generate_diagram.py"
    
    try:
        result = subprocess.run(
            [sys.executable, str(diagram_script)],
            cwd=str(case_path),
            capture_output=True,
            text=True,
            timeout=15,
            encoding='utf-8',
            errors='ignore'
        )
        
        if result.returncode == 0:
            return True, "成功"
        else:
            error_msg = result.stderr[:200] if result.stderr else "未知错误"
            return False, error_msg
    except subprocess.TimeoutExpired:
        return False, "超时"
    except Exception as e:
        return False, str(e)[:200]

def main():
    print("=" * 80)
    print("批量重新生成示意图")
    print("=" * 80)
    print()
    
    success_count = 0
    fail_count = 0
    skip_count = 0
    
    for i in range(1, 21):
        case_pattern = f"case_{i:02d}_*"
        case_dirs = list(CASES_DIR.glob(case_pattern))
        
        if not case_dirs:
            continue
        
        case_path = case_dirs[0]
        print(f"处理案例 {i:02d}: {case_path.name}")
        
        success, message = regenerate_diagram(case_path)
        
        if success:
            print(f"  ✅ {message}")
            success_count += 1
        elif "未找到" in message:
            print(f"  ℹ️  {message}")
            skip_count += 1
        else:
            print(f"  ❌ {message}")
            fail_count += 1
        
        print()
    
    print("=" * 80)
    print("生成完成")
    print("=" * 80)
    print(f"\n✅ 成功: {success_count}")
    print(f"❌ 失败: {fail_count}")
    print(f"ℹ️  跳过: {skip_count}")

if __name__ == "__main__":
    main()



