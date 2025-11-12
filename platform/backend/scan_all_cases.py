#!/usr/bin/env python3
"""
扫描所有书稿和案例脚本
生成完整的案例索引
"""

import os
import json
import sys
from pathlib import Path
from typing import Dict, List

# 设置UTF-8编码
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def scan_book_cases(book_path: Path) -> List[Dict]:
    """扫描单本书的所有案例"""
    cases = []
    code_path = book_path / "code" / "examples"
    
    if not code_path.exists():
        print(f"⚠️ {book_path.name} 没有找到examples目录")
        return cases
    
    # 扫描所有案例目录
    for case_dir in sorted(code_path.iterdir()):
        if not case_dir.is_dir() or case_dir.name.startswith('.'):
            continue
        
        # 提取案例编号和名称
        case_name = case_dir.name
        if not case_name.startswith('case_'):
            continue
        
        # 读取README获取案例信息
        readme_path = case_dir / "README.md"
        main_path = case_dir / "main.py"
        
        case_info = {
            "id": case_name,
            "name": case_name.replace('_', ' ').title(),
            "path": str(case_dir.relative_to(book_path.parent.parent)),
            "has_readme": readme_path.exists(),
            "has_main": main_path.exists(),
            "has_experiments": (case_dir / "experiments.py").exists()
        }
        
        # 尝试从README中提取标题
        if readme_path.exists():
            try:
                with open(readme_path, 'r', encoding='utf-8') as f:
                    first_line = f.readline().strip()
                    if first_line.startswith('#'):
                        case_info["title"] = first_line.lstrip('#').strip()
            except:
                pass
        
        cases.append(case_info)
    
    return cases

def main():
    """主函数"""
    print("=" * 60)
    print("📚 CHS-Books 案例扫描工具")
    print("=" * 60)
    print()
    
    # 定位books目录
    books_base = Path(__file__).parent.parent.parent / "books"
    
    if not books_base.exists():
        print(f"❌ 找不到books目录: {books_base}")
        return
    
    all_books_data = []
    total_cases = 0
    
    # 要扫描的书籍列表
    books_to_scan = [
        "water-system-control",
        "open-channel-hydraulics",
        "canal-pipeline-control",
        "ecohydraulics",
        "distributed-hydrological-model",
        "water-environment-simulation",
        "water-resource-planning-management",
        "underground-water-dynamics",
        "intelligent-water-network-design",
        "photovoltaic-system-modeling-control",
        "wind-power-system-modeling-control",
        "energy-storage-system-modeling-control",
        "integrated-energy-system-simulation-optimization",
    ]
    
    for book_slug in books_to_scan:
        book_path = books_base / book_slug
        
        if not book_path.exists():
            print(f"⚠️  {book_slug} 目录不存在，跳过")
            continue
        
        print(f"\n📖 扫描: {book_slug}")
        print("-" * 60)
        
        cases = scan_book_cases(book_path)
        
        book_data = {
            "slug": book_slug,
            "path": str(book_path.relative_to(books_base.parent)),
            "cases_count": len(cases),
            "cases": cases
        }
        
        all_books_data.append(book_data)
        total_cases += len(cases)
        
        print(f"   找到 {len(cases)} 个案例")
        
        # 显示前5个案例
        for i, case in enumerate(cases[:5]):
            status = "✅" if case['has_main'] else "❌"
            print(f"   {status} {case['id']}")
        
        if len(cases) > 5:
            print(f"   ... 还有 {len(cases) - 5} 个案例")
    
    # 扫描考研系列
    print(f"\n📖 扫描: graduate-exam-prep (研究生考试系列)")
    print("-" * 60)
    
    grad_base = books_base / "graduate-exam-prep"
    if grad_base.exists():
        # 水力学核心100题
        core100_path = grad_base / "hydraulics-core-100"
        if core100_path.exists():
            # 扫描章节
            chapters = []
            for chapter_dir in sorted(core100_path.iterdir()):
                if chapter_dir.is_dir() and chapter_dir.name.startswith('第'):
                    chapter_cases = []
                    code_dir = chapter_dir / "code"
                    if code_dir.exists():
                        for case_file in sorted(code_dir.glob("题*.py")):
                            chapter_cases.append({
                                "id": case_file.stem,
                                "path": str(case_file.relative_to(books_base.parent)),
                                "has_main": True
                            })
                    
                    if chapter_cases:
                        chapters.append({
                            "chapter": chapter_dir.name,
                            "cases_count": len(chapter_cases),
                            "cases": chapter_cases
                        })
                        total_cases += len(chapter_cases)
            
            book_data = {
                "slug": "hydraulics-core-100",
                "path": str(core100_path.relative_to(books_base.parent)),
                "chapters_count": len(chapters),
                "cases_count": sum(ch['cases_count'] for ch in chapters),
                "chapters": chapters
            }
            all_books_data.append(book_data)
            print(f"   找到 {len(chapters)} 个章节，共 {book_data['cases_count']} 个题目")
        
        # 高等水力学
        advanced_path = grad_base / "hydraulics-advanced"
        if advanced_path.exists():
            chapters = []
            for chapter_dir in sorted(advanced_path.iterdir()):
                if chapter_dir.is_dir() and chapter_dir.name.startswith('第'):
                    chapter_cases = []
                    code_dir = chapter_dir / "code"
                    if code_dir.exists():
                        for case_file in sorted(code_dir.glob("*.py")):
                            if not case_file.name.startswith('__'):
                                chapter_cases.append({
                                    "id": case_file.stem,
                                    "path": str(case_file.relative_to(books_base.parent)),
                                    "has_main": True
                                })
                    
                    if chapter_cases:
                        chapters.append({
                            "chapter": chapter_dir.name,
                            "cases_count": len(chapter_cases),
                            "cases": chapter_cases
                        })
                        total_cases += len(chapter_cases)
            
            book_data = {
                "slug": "hydraulics-advanced",
                "path": str(advanced_path.relative_to(books_base.parent)),
                "chapters_count": len(chapters),
                "cases_count": sum(ch['cases_count'] for ch in chapters),
                "chapters": chapters
            }
            all_books_data.append(book_data)
            print(f"   找到 {len(chapters)} 个章节，共 {book_data['cases_count']} 个案例")
    
    # 保存扫描结果
    output_file = Path(__file__).parent / "cases_index.json"
    
    scan_result = {
        "total_books": len(all_books_data),
        "total_cases": total_cases,
        "books": all_books_data
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(scan_result, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 60)
    print("✅ 扫描完成！")
    print(f"   总书籍数: {len(all_books_data)}")
    print(f"   总案例数: {total_cases}")
    print(f"   索引文件: {output_file}")
    print("=" * 60)

if __name__ == "__main__":
    main()

