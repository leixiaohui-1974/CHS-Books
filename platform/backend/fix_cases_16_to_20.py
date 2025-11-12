#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复案例16-20的编码问题并生成图片
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent
CASES_DIR = ROOT_DIR / "books" / "water-system-control" / "code" / "examples"

def fix_and_run_case(case_num, case_name):
    """修复单个案例并运行"""
    case_dir = CASES_DIR / case_name
    main_file = case_dir / "main.py"
    
    if not main_file.exists():
        print(f"案例{case_num}: ✗ main.py不存在")
        return False
    
    print(f"\n{'='*60}")
    print(f"案例{case_num}：{case_name}")
    print(f"{'='*60}")
    
    # 读取文件
    try:
        content = main_file.read_text(encoding='utf-8')
    except:
        content = main_file.read_text(encoding='gbk')
    
    # 检查是否已经有编码设置
    needs_fix = False
    if 'sys.stdout = io.TextIOWrapper' not in content:
        needs_fix = True
        print("  需要添加UTF-8编码支持")
    
    if needs_fix:
        # 在文件开头添加编码支持
        lines = content.split('\n')
        
        # 找到import语句的位置
        import_pos = 0
        for i, line in enumerate(lines):
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                import_pos = i
                break
        
        # 在import之前插入编码设置
        if import_pos > 0:
            encoding_lines = [
                'import sys',
                'import io',
                'sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")',
                ''
            ]
            
            # 检查是否已有import sys
            has_sys = any('import sys' in line for line in lines[:import_pos+5])
            has_io = any('import io' in line for line in lines[:import_pos+5])
            
            insert_lines = []
            if not has_sys:
                insert_lines.append('import sys')
            if not has_io:
                insert_lines.append('import io')
            insert_lines.append('sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")')
            insert_lines.append('')
            
            lines = lines[:import_pos] + insert_lines + lines[import_pos:]
            
            # 写回文件
            new_content = '\n'.join(lines)
            main_file.write_text(new_content, encoding='utf-8')
            print("  ✓ 已添加UTF-8编码支持")
    else:
        print("  ✓ 已有UTF-8编码支持")
    
    # 运行脚本生成图片
    print("  运行脚本生成图片...")
    try:
        result = subprocess.run(
            [sys.executable, str(main_file)],
            cwd=str(case_dir),
            capture_output=True,
            text=True,
            timeout=120,
            encoding='utf-8',
            errors='replace'
        )
        
        if result.returncode == 0:
            # 检查生成的PNG
            png_files = list(case_dir.glob("*.png"))
            result_files = [f for f in png_files if 'diagram' not in f.name.lower()]
            
            print(f"  ✓ 运行成功")
            print(f"  ✓ 生成图片：{len(result_files)}张")
            
            for png in result_files:
                size_kb = png.stat().st_size / 1024
                print(f"    - {png.name} ({size_kb:.1f}KB)")
            
            return True
        else:
            print(f"  ✗ 运行失败")
            error_lines = result.stderr.split('\n')[-5:]
            for line in error_lines:
                if line.strip():
                    print(f"    {line}")
            return False
    
    except subprocess.TimeoutExpired:
        print(f"  ✗ 运行超时")
        return False
    except Exception as e:
        print(f"  ✗ 异常：{str(e)}")
        return False

def main():
    """主函数"""
    print("="*60)
    print("修复案例16-20的编码问题并生成图片")
    print("="*60)
    
    cases = [
        (16, "case_16_fuzzy_control"),
        (17, "case_17_neural_network_control"),
        (18, "case_18_reinforcement_learning_control"),
        (19, "case_19_comprehensive_comparison"),
        (20, "case_20_practical_application"),
    ]
    
    success_count = 0
    
    for case_num, case_name in cases:
        if fix_and_run_case(case_num, case_name):
            success_count += 1
    
    # 总结
    print("\n" + "="*60)
    print("总结")
    print("="*60)
    print(f"成功：{success_count}/{len(cases)}")
    print(f"成功率：{success_count/len(cases)*100:.1f}%")
    
    if success_count == len(cases):
        print("\n✓ 所有案例都已成功修复并生成图片！")
    else:
        print(f"\n⚠ 还有{len(cases)-success_count}个案例需要手动检查")

if __name__ == "__main__":
    main()



