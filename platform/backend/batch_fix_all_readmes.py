# -*- coding: utf-8 -*-
"""
批量修复所有案例README，确保：
1. 所有示意图和结果图都正确显示
2. 采用1行2列表格布局
3. 每个图都有详细说明
"""

import os
import sys
import io
from pathlib import Path

# 设置UTF-8输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 项目根目录
ROOT_DIR = Path(__file__).parent.parent.parent
CASES_DIR = ROOT_DIR / "books" / "water-system-control" / "code" / "examples"

def check_case_images(case_path):
    """检查案例的图片文件"""
    images = list(case_path.glob("*.png"))
    return [img.name for img in images]

def check_readme_images(readme_path):
    """检查README中引用的图片"""
    if not readme_path.exists():
        return []
    
    content = readme_path.read_text(encoding='utf-8')
    import re
    # 匹配 ![xxx](xxx.png) 和 <img src="xxx.png"
    pattern1 = r'!\[.*?\]\((.*?\.png)\)'
    pattern2 = r'<img\s+src="(.*?\.png)"'
    
    images1 = re.findall(pattern1, content)
    images2 = re.findall(pattern2, content)
    
    return list(set(images1 + images2))

def check_table_format(readme_path):
    """检查是否使用了表格格式"""
    if not readme_path.exists():
        return False
    
    content = readme_path.read_text(encoding='utf-8')
    return '<table' in content and '<tr>' in content and '<td' in content

def scan_all_cases():
    """扫描所有案例"""
    print("正在扫描所有案例...")
    print("=" * 80)
    
    results = []
    
    for i in range(1, 21):
        case_id = f"case_{i:02d}_"
        case_dirs = list(CASES_DIR.glob(f"{case_id}*"))
        
        if not case_dirs:
            continue
        
        case_path = case_dirs[0]
        readme_path = case_path / "README.md"
        
        # 检查图片文件
        image_files = check_case_images(case_path)
        
        # 检查README中的图片引用
        readme_images = check_readme_images(readme_path) if readme_path.exists() else []
        
        # 检查表格格式
        has_table = check_table_format(readme_path) if readme_path.exists() else False
        
        # 计算缺失的图片
        missing_in_readme = [img for img in image_files if img not in readme_images]
        
        result = {
            'id': i,
            'path': case_path,
            'name': case_path.name,
            'image_files': image_files,
            'readme_images': readme_images,
            'missing': missing_in_readme,
            'has_table': has_table,
            'has_readme': readme_path.exists()
        }
        
        results.append(result)
        
        # 输出结果
        status = "✅" if not missing_in_readme and has_table else "❌"
        print(f"{status} 案例{i:02d}: {case_path.name}")
        print(f"   - 图片文件: {len(image_files)}张")
        print(f"   - README引用: {len(readme_images)}张")
        print(f"   - 缺失图片: {len(missing_in_readme)}张")
        print(f"   - 表格格式: {'是' if has_table else '否'}")
        
        if missing_in_readme:
            print(f"   - 缺失列表: {', '.join(missing_in_readme)}")
        
        print()
    
    return results

def generate_summary(results):
    """生成汇总报告"""
    print("=" * 80)
    print("汇总报告")
    print("=" * 80)
    
    total_cases = len(results)
    perfect_cases = sum(1 for r in results if not r['missing'] and r['has_table'])
    has_table_cases = sum(1 for r in results if r['has_table'])
    
    print(f"\n总案例数: {total_cases}")
    print(f"完美案例: {perfect_cases} ({perfect_cases/total_cases*100:.1f}%)")
    print(f"使用表格: {has_table_cases} ({has_table_cases/total_cases*100:.1f}%)")
    
    print(f"\n需要修复的案例:")
    for r in results:
        if r['missing'] or not r['has_table']:
            print(f"  - 案例{r['id']:02d}: {r['name']}")
            if r['missing']:
                print(f"    缺失图片: {', '.join(r['missing'])}")
            if not r['has_table']:
                print(f"    缺少表格格式")

if __name__ == "__main__":
    print("=" * 80)
    print("批量扫描所有案例README")
    print("=" * 80)
    print()
    
    results = scan_all_cases()
    generate_summary(results)
    
    print()
    print("=" * 80)
    print("扫描完成！")
    print("=" * 80)



