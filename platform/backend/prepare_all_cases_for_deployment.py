#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
准备所有案例用于部署：
1. 运行所有案例生成图片
2. 检查是否有示意图
3. 确保README.md中图片正确嵌入
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

def run_case_to_generate_images(case_dir, timeout=120):
    """运行案例生成所有图片"""
    case_name = case_dir.name
    main_file = case_dir / "main.py"
    
    if not main_file.exists():
        return {"case": case_name, "status": "skip", "message": "main.py不存在"}
    
    print(f"\n{'='*80}")
    print(f"运行 {case_name} 生成图片")
    print(f"{'='*80}")
    
    start_time = time.time()
    
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
        
        elapsed_time = time.time() - start_time
        
        # 检查生成的PNG文件
        png_files = list(case_dir.glob("*.png"))
        
        # 分类图片
        diagram_files = [f for f in png_files if 'diagram' in f.name.lower() or 'schematic' in f.name.lower() or 'structure' in f.name.lower()]
        result_files = [f for f in png_files if f not in diagram_files]
        
        if result.returncode == 0:
            status = "success"
            message = f"成功 ({elapsed_time:.1f}s)"
            print(f"  ✓ 运行成功")
            print(f"  - 示意图: {len(diagram_files)} 张")
            print(f"  - 结果图: {len(result_files)} 张")
            
            for f in diagram_files:
                print(f"    • {f.name}")
            for f in result_files:
                print(f"    • {f.name}")
        else:
            status = "error"
            message = f"失败 (返回码: {result.returncode})"
            print(f"  ✗ 运行失败")
            if result.stderr:
                print(f"  错误: {result.stderr[:200]}")
        
        return {
            "case": case_name,
            "status": status,
            "message": message,
            "diagrams": [f.name for f in diagram_files],
            "results": [f.name for f in result_files],
            "time": elapsed_time
        }
    
    except subprocess.TimeoutExpired:
        elapsed_time = time.time() - start_time
        print(f"  ✗ 超时 (>{timeout}s)")
        return {
            "case": case_name,
            "status": "timeout",
            "message": f"超时",
            "diagrams": [],
            "results": [],
            "time": elapsed_time
        }
    
    except Exception as e:
        elapsed_time = time.time() - start_time
        print(f"  ✗ 异常: {str(e)}")
        return {
            "case": case_name,
            "status": "exception",
            "message": f"异常: {str(e)}",
            "diagrams": [],
            "results": [],
            "time": elapsed_time
        }

def check_readme_images(case_dir):
    """检查README.md中的图片引用"""
    readme_file = case_dir / "README.md"
    
    if not readme_file.exists():
        return {"has_readme": False, "images_in_readme": []}
    
    with open(readme_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找所有图片引用
    import re
    img_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
    images = re.findall(img_pattern, content)
    
    return {
        "has_readme": True,
        "images_in_readme": [img[1] for img in images]
    }

def main():
    """主函数"""
    print("="*80)
    print("准备所有案例用于部署")
    print("="*80)
    print("\n任务:")
    print("  1. 运行所有案例生成图片")
    print("  2. 检查示意图是否存在")
    print("  3. 检查README.md图片引用")
    print()
    
    total_start = time.time()
    results = []
    
    # 遍历所有案例
    cases = sorted(CASES_DIR.glob("case_*"))
    
    for case_dir in cases:
        if not case_dir.is_dir():
            continue
        
        # 运行案例生成图片
        run_result = run_case_to_generate_images(case_dir, timeout=120)
        
        # 检查README
        readme_info = check_readme_images(case_dir)
        
        # 合并结果
        result = {**run_result, **readme_info}
        results.append(result)
    
    total_time = time.time() - total_start
    
    # 生成报告
    print("\n" + "="*80)
    print("准备结果汇总")
    print("="*80)
    
    success_count = sum(1 for r in results if r["status"] == "success")
    total_diagrams = sum(len(r.get("diagrams", [])) for r in results)
    total_results_imgs = sum(len(r.get("results", [])) for r in results)
    
    print(f"\n总案例数: {len(results)}")
    print(f"  ✓ 成功: {success_count}")
    print(f"  ✗ 失败: {len(results) - success_count}")
    print(f"\n生成图片:")
    print(f"  - 示意图: {total_diagrams} 张")
    print(f"  - 结果图: {total_results_imgs} 张")
    print(f"  - 总计: {total_diagrams + total_results_imgs} 张")
    print(f"\n总耗时: {total_time/60:.1f} 分钟")
    
    # 详细结果
    print("\n" + "-"*80)
    print("详细结果:")
    print("-"*80)
    
    # 需要创建示意图的案例
    need_diagram = []
    
    for r in results:
        status_icon = "✓" if r["status"] == "success" else "✗"
        has_readme = "📄" if r.get("has_readme") else "❌"
        has_diagram = "🖼️" if r.get("diagrams") else "❌"
        
        print(f"{status_icon} {r['case']}: {r['message']}")
        print(f"   README: {has_readme}  示意图: {has_diagram}  结果图: {len(r.get('results', []))}张")
        
        if not r.get("diagrams"):
            need_diagram.append(r['case'])
    
    # 需要创建示意图的案例列表
    if need_diagram:
        print("\n" + "-"*80)
        print("⚠️  需要创建示意图的案例:")
        print("-"*80)
        for case in need_diagram:
            print(f"  - {case}")
    
    # 保存结果到JSON
    report_file = Path(__file__).parent / "deployment_preparation_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n详细报告已保存到: {report_file.name}")
    
    print("\n" + "="*80)
    print("准备完成！")
    print("="*80)
    
    return success_count == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

