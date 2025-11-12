#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
准备所有案例用于生产环境
1. 运行所有案例生成图表
2. 检查README.md是否有图片嵌入
3. 生成缺失的示意图
4. 创建完整的文档报告
"""

import subprocess
import sys
import io
from pathlib import Path
import time
import json

# 设置标准输出为UTF-8编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 定义根目录
ROOT_DIR = Path(__file__).parent.parent.parent
CASES_DIR = ROOT_DIR / "books" / "water-system-control" / "code" / "examples"

def run_case(case_dir, timeout=120):
    """运行单个案例生成图表"""
    case_name = case_dir.name
    main_file = case_dir / "main.py"
    
    if not main_file.exists():
        return {"status": "skip", "message": "main.py不存在"}
    
    print(f"\n{'='*80}")
    print(f"运行 {case_name}")
    print(f"{'='*80}")
    
    try:
        result = subprocess.run(
            [sys.executable, str(main_file)],
            cwd=str(case_dir),
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding='utf-8',
            errors='replace',
            env={**subprocess.os.environ, 'PYTHONIOENCODING': 'utf-8'}
        )
        
        # 统计生成的PNG文件
        png_files = list(case_dir.glob("*.png"))
        image_count = len(png_files)
        
        if result.returncode == 0:
            print(f"✓ 成功生成 {image_count} 张图片")
            return {"status": "success", "images": image_count, "files": [f.name for f in png_files]}
        else:
            print(f"✗ 运行失败")
            return {"status": "error", "message": result.stderr[:200]}
    
    except Exception as e:
        print(f"✗ 异常: {str(e)}")
        return {"status": "exception", "message": str(e)}

def check_readme(case_dir):
    """检查README.md是否完整"""
    readme_file = case_dir / "README.md"
    
    if not readme_file.exists():
        return {"has_readme": False, "has_images": False, "has_diagram": False}
    
    content = readme_file.read_text(encoding='utf-8')
    
    # 检查是否有图片引用
    has_images = '![' in content or '<img' in content
    
    # 检查是否有示意图
    has_diagram = 'diagram' in content.lower() or '示意图' in content
    
    # 检查是否有表格格式的图片说明
    has_table_format = '<table>' in content and '<img' in content
    
    return {
        "has_readme": True,
        "has_images": has_images,
        "has_diagram": has_diagram,
        "has_table_format": has_table_format,
        "image_count": content.count('![') + content.count('<img')
    }

def analyze_case(case_dir):
    """分析单个案例的完整性"""
    case_name = case_dir.name
    
    # 检查文件
    has_main = (case_dir / "main.py").exists()
    has_readme = (case_dir / "README.md").exists()
    
    # 检查PNG文件
    png_files = list(case_dir.glob("*.png"))
    png_count = len(png_files)
    
    # 检查README
    readme_info = check_readme(case_dir)
    
    # 判断是否完整
    is_complete = (
        has_main and
        has_readme and
        png_count > 0 and
        readme_info.get('has_images', False)
    )
    
    return {
        "case": case_name,
        "has_main": has_main,
        "has_readme": has_readme,
        "png_count": png_count,
        "png_files": [f.name for f in png_files],
        "readme_info": readme_info,
        "is_complete": is_complete
    }

def main():
    """主函数"""
    print("="*80)
    print("准备所有案例用于生产环境")
    print("="*80)
    
    # 第1步：运行所有案例生成图表
    print("\n" + "="*80)
    print("第1步：运行所有案例生成图表")
    print("="*80)
    
    run_results = {}
    for case_dir in sorted(CASES_DIR.glob("case_*")):
        if not case_dir.is_dir():
            continue
        result = run_case(case_dir, timeout=120)
        run_results[case_dir.name] = result
        time.sleep(0.5)  # 避免过快
    
    # 第2步：分析所有案例的完整性
    print("\n" + "="*80)
    print("第2步：分析所有案例的完整性")
    print("="*80)
    
    analysis_results = []
    for case_dir in sorted(CASES_DIR.glob("case_*")):
        if not case_dir.is_dir():
            continue
        analysis = analyze_case(case_dir)
        analysis_results.append(analysis)
    
    # 第3步：生成报告
    print("\n" + "="*80)
    print("第3步：完整性分析报告")
    print("="*80)
    
    complete_count = sum(1 for a in analysis_results if a['is_complete'])
    incomplete_cases = [a for a in analysis_results if not a['is_complete']]
    
    print(f"\n总案例数: {len(analysis_results)}")
    print(f"  ✓ 完整: {complete_count}")
    print(f"  ✗ 不完整: {len(incomplete_cases)}")
    
    if incomplete_cases:
        print("\n不完整的案例:")
        for case in incomplete_cases:
            print(f"\n{case['case']}:")
            if not case['has_main']:
                print("  ✗ 缺少 main.py")
            if not case['has_readme']:
                print("  ✗ 缺少 README.md")
            if case['png_count'] == 0:
                print("  ✗ 未生成图片")
            if not case['readme_info'].get('has_images'):
                print("  ✗ README未嵌入图片")
            if not case['readme_info'].get('has_diagram'):
                print("  ⚠ 可能缺少示意图")
            if not case['readme_info'].get('has_table_format'):
                print("  ⚠ 未使用表格格式展示图片")
    
    # 保存详细报告
    report_file = Path(__file__).parent / "案例完整性分析报告.json"
    report_data = {
        "summary": {
            "total": len(analysis_results),
            "complete": complete_count,
            "incomplete": len(incomplete_cases)
        },
        "cases": analysis_results
    }
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n详细报告已保存到: {report_file}")
    
    print("\n" + "="*80)
    print("分析完成！")
    print("="*80)

if __name__ == "__main__":
    main()

