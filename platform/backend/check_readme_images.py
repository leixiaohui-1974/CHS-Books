#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查所有README文件中的图片引用是否正确
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from pathlib import Path
import re

ROOT_DIR = Path(__file__).parent.parent.parent
CASES_DIR = ROOT_DIR / "books" / "water-system-control" / "code" / "examples"

def check_readme(case_num, case_name):
    """检查单个README"""
    case_dir = CASES_DIR / case_name
    readme_file = case_dir / "README.md"
    
    if not readme_file.exists():
        return {"status": "no_readme", "images": []}
    
    content = readme_file.read_text(encoding='utf-8')
    
    # 查找所有图片引用
    img_pattern = r'<img\s+src="([^"]+)"'
    images = re.findall(img_pattern, content)
    
    # 检查图片是否存在
    results = []
    for img in images:
        img_path = case_dir / img
        exists = img_path.exists()
        size = img_path.stat().st_size if exists else 0
        results.append({
            "name": img,
            "exists": exists,
            "size": size
        })
    
    # 检查是否有示意图部分
    has_diagram_section = "## 系统示意图" in content
    
    return {
        "status": "ok",
        "has_diagram_section": has_diagram_section,
        "images": results,
        "total_images": len(results)
    }

def main():
    """主函数"""
    print("="*60)
    print("README图片引用检查")
    print("="*60)
    
    cases = [
        (i, f"case_{i:02d}_*") for i in range(1, 21)
    ]
    
    all_results = {}
    
    for case_num, pattern in cases:
        case_dirs = list(CASES_DIR.glob(pattern))
        if not case_dirs:
            print(f"案例{case_num}: ✗ 目录不存在")
            continue
        
        case_dir = case_dirs[0]
        case_name = case_dir.name
        result = check_readme(case_num, case_name)
        all_results[case_num] = result
        
        # 打印结果
        status_icon = "✓" if result["status"] == "ok" else "✗"
        print(f"\n案例{case_num}: {status_icon} {case_name}")
        
        if result["status"] == "ok":
            if result["has_diagram_section"]:
                print(f"  ✓ 有示意图部分")
            else:
                print(f"  ✗ 缺少示意图部分")
            
            print(f"  图片数量: {result['total_images']}张")
            
            for img in result["images"]:
                exists_icon = "✓" if img["exists"] else "✗"
                size_str = f"{img['size']/1024:.1f}KB" if img["exists"] else "不存在"
                print(f"    {exists_icon} {img['name']:40s} {size_str}")
    
    # 总结
    print("\n" + "="*60)
    print("总结")
    print("="*60)
    
    total = len(all_results)
    with_diagram = sum(1 for r in all_results.values() 
                       if r.get("has_diagram_section", False))
    total_images = sum(r.get("total_images", 0) for r in all_results.values())
    missing_images = sum(1 for r in all_results.values() 
                        for img in r.get("images", []) 
                        if not img["exists"])
    
    print(f"总案例数: {total}")
    print(f"有示意图部分: {with_diagram}个 ({with_diagram/total*100:.1f}%)")
    print(f"图片总数: {total_images}张")
    print(f"缺失图片: {missing_images}张")
    
    if missing_images == 0:
        print("\n✓ 所有图片引用都正确！")
    else:
        print(f"\n✗ 有{missing_images}张图片缺失")

if __name__ == "__main__":
    main()



