#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查所有教材和数据库状态
"""

import sys
import io
from pathlib import Path

# 设置UTF-8输出
if sys.platform == 'win32' and hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.textbook.database import SessionLocal
from services.textbook.models import Textbook, TextbookChapter

# 项目根目录
BOOKS_DIR = Path(__file__).parent.parent.parent.parent / "books"

def count_markdown_files(directory):
    """统计目录下的markdown文件数量"""
    if not directory.exists():
        return 0
    return len(list(directory.rglob("*.md")))

def scan_all_books():
    """扫描books目录下的所有教材"""
    print("\n" + "="*80)
    print("  📚 扫描项目中的所有教材")
    print("="*80 + "\n")
    
    book_dirs = [d for d in BOOKS_DIR.iterdir() if d.is_dir() and not d.name.startswith('_')]
    book_dirs.sort()
    
    print(f"发现 {len(book_dirs)} 个教材项目：\n")
    
    total_md_files = 0
    
    for i, book_dir in enumerate(book_dirs, 1):
        md_count = count_markdown_files(book_dir)
        total_md_files += md_count
        
        # 检查是否有chapters或docs目录
        has_chapters = (book_dir / "chapters").exists() or (book_dir / "docs").exists()
        
        status = "📖" if has_chapters else "📁"
        
        print(f"{i:2d}. {status} {book_dir.name}")
        print(f"     MD文件: {md_count} 个")
        
        # 特别标注考研资料
        if book_dir.name == "graduate-exam-prep":
            subdirs = [d for d in book_dir.iterdir() if d.is_dir()]
            exam_books = [d for d in subdirs if d.name.startswith('hydraulics')]
            if exam_books:
                print(f"     考研书籍: {len(exam_books)} 本")
                for exam_book in exam_books:
                    exam_md = count_markdown_files(exam_book)
                    print(f"       - {exam_book.name}: {exam_md} MD")
        print()
    
    print(f"\n总计: {len(book_dirs)} 个教材项目，{total_md_files} 个MD文件\n")
    return book_dirs

def check_database_status():
    """检查数据库中的教材状态"""
    print("\n" + "="*80)
    print("  🗄️  数据库中的教材状态")
    print("="*80 + "\n")
    
    db = SessionLocal()
    
    try:
        textbooks = db.query(Textbook).all()
        
        if not textbooks:
            print("⚠️  数据库为空，尚未导入任何教材\n")
            return
        
        print(f"已导入 {len(textbooks)} 本教材：\n")
        
        total_chapters = 0
        total_words = 0
        
        for i, textbook in enumerate(textbooks, 1):
            chapters_count = db.query(TextbookChapter).filter(
                TextbookChapter.textbook_id == textbook.id
            ).count()
            
            total_chapters += chapters_count
            total_words += textbook.total_words or 0
            
            print(f"{i:2d}. 📖 {textbook.title}")
            print(f"     章节: {chapters_count} 个 | 字数: {textbook.total_words:,} 字")
            print(f"     创建: {textbook.created_at.strftime('%Y-%m-%d')}")
            print()
        
        print(f"总计: {len(textbooks)} 本教材，{total_chapters} 个章节，{total_words:,} 字\n")
        
    finally:
        db.close()

def generate_import_recommendations():
    """生成导入建议"""
    print("\n" + "="*80)
    print("  💡 导入建议")
    print("="*80 + "\n")
    
    db = SessionLocal()
    
    try:
        imported_titles = {t.title for t in db.query(Textbook).all()}
        
        # 建议导入的教材（根据目录结构）
        priority_books = [
            ("water-system-control", "水系统控制论", "高优先级 - 62案例"),
            ("open-channel-hydraulics", "明渠水力学", "高优先级 - 100案例"),
            ("water-environment-simulation", "水环境模拟", "高优先级 - 90案例"),
            ("ecohydraulics", "生态水力学", "高优先级 - 81案例"),
            ("distributed-hydrological-model", "分布式水文模型", "高优先级 - 61案例"),
            ("underground-water-dynamics", "地下水动力学", "高优先级 - 70案例"),
            ("water-resource-planning-management", "水资源规划管理", "高优先级 - 86案例"),
            ("intelligent-water-network-design", "智能水网设计", "高优先级 - 48案例"),
            ("canal-pipeline-control", "渠道管道控制", "中优先级 - 20案例"),
            ("photovoltaic-system-modeling-control", "光伏系统建模控制", "中优先级"),
            ("wind-power-system-modeling-control", "风力发电系统", "中优先级"),
            ("graduate-exam-prep/hydraulics-core-100", "水力学考研核心100题", "考研资料 - 6章"),
            ("graduate-exam-prep/hydraulics-advanced", "水力学考研高分突破", "考研资料 - 15章"),
        ]
        
        need_import = []
        
        for slug, title, note in priority_books:
            if title not in imported_titles:
                need_import.append((slug, title, note))
        
        if need_import:
            print("以下教材尚未导入，建议导入：\n")
            for i, (slug, title, note) in enumerate(need_import, 1):
                print(f"{i:2d}. 📚 {title}")
                print(f"     目录: books/{slug}")
                print(f"     说明: {note}")
                print()
            
            print(f"共 {len(need_import)} 本教材待导入\n")
        else:
            print("✅ 所有重要教材已导入！\n")
        
    finally:
        db.close()

def main():
    print("\n" + "="*80)
    print("  📊 CHS-Books 教材全面检查")
    print("="*80)
    
    # 扫描所有教材
    book_dirs = scan_all_books()
    
    # 检查数据库状态
    check_database_status()
    
    # 生成导入建议
    generate_import_recommendations()
    
    print("="*80)
    print("  检查完成！")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()

