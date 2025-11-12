# -*- coding: utf-8 -*-
"""
最终全面修复脚本
修复所有案例的示意图、结果图、文档格式问题
"""
import sys
import io
import subprocess
from pathlib import Path

# 设置UTF-8编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 路径配置
BASE_DIR = Path(__file__).resolve().parent.parent.parent
EXAMPLES_DIR = BASE_DIR / "books" / "water-system-control" / "code" / "examples"

def print_section(title):
    """打印分节标题"""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")

def run_script(script_path, description):
    """运行Python脚本"""
    try:
        result = subprocess.run(
            ['python', str(script_path)],
            capture_output=True,
            text=True,
            encoding='utf-8',
            cwd=script_path.parent
        )
        if result.returncode == 0:
            print(f"✅ {description}: 成功")
            if result.stdout:
                print(f"   输出: {result.stdout.strip()[:100]}")
            return True
        else:
            print(f"❌ {description}: 失败")
            if result.stderr:
                print(f"   错误: {result.stderr.strip()[:200]}")
            return False
    except Exception as e:
        print(f"❌ {description}: 异常 - {str(e)[:200]}")
        return False

def main():
    print_section("🔧 最终全面修复脚本")
    
    # 统计
    total_cases = 0
    diagram_success = 0
    result_success = 0
    
    # 遍历所有案例
    for case_dir in sorted(EXAMPLES_DIR.glob("case_*")):
        if not case_dir.is_dir():
            continue
        
        total_cases += 1
        case_name = case_dir.name
        print(f"\n📁 处理 {case_name}...")
        
        # 1. 生成示意图
        diagram_script = case_dir / "generate_diagram.py"
        if diagram_script.exists():
            if run_script(diagram_script, f"生成示意图"):
                diagram_success += 1
        else:
            print(f"   ⚠️  未找到 generate_diagram.py")
        
        # 2. 生成结果图
        main_script = case_dir / "main.py"
        if main_script.exists():
            if run_script(main_script, f"生成结果图"):
                result_success += 1
        else:
            print(f"   ⚠️  未找到 main.py")
    
    # 最终统计
    print_section("📊 修复统计报告")
    print(f"总案例数: {total_cases}")
    print(f"示意图生成成功: {diagram_success}/{total_cases} ({diagram_success*100//total_cases if total_cases>0 else 0}%)")
    print(f"结果图生成成功: {result_success}/{total_cases} ({result_success*100//total_cases if total_cases>0 else 0}%)")
    
    if diagram_success == total_cases and result_success == total_cases:
        print(f"\n🎉 所有案例修复完成！")
    else:
        print(f"\n⚠️  部分案例需要手动检查")
    
    print("\n" + "="*80)

if __name__ == '__main__':
    main()



