#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试教材树API
"""

import sys
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent))

from services.textbook.database import get_db_session
from services.textbook.models import Textbook, TextbookChapter, ChapterCaseMapping

def test_tree_api():
    """测试树API逻辑"""
    db = next(get_db_session())
    
    try:
        # 1. 查询教材
        print("=== 1. 查询教材 ===")
        textbooks = db.query(Textbook).filter(Textbook.is_published == 1).all()
        print(f"找到 {len(textbooks)} 本教材")
        
        for book in textbooks[:3]:
            print(f"  - {book.title} (ID: {book.id})")
        
        # 2. 查询第一本教材的章节
        if textbooks:
            first_book = textbooks[0]
            print(f"\n=== 2. 查询第一本教材的章节: {first_book.title} ===")
            chapters = db.query(TextbookChapter).filter(
                TextbookChapter.textbook_id == first_book.id
            ).order_by(TextbookChapter.order_num).all()
            print(f"找到 {len(chapters)} 个章节")
            
            for ch in chapters[:5]:
                print(f"  - {ch.chapter_number} {ch.title}")
                
                # 查询案例数
                case_count = db.query(ChapterCaseMapping).filter(
                    ChapterCaseMapping.chapter_id == ch.id
                ).count()
                print(f"    案例数: {case_count}")
        
        print("\n✅ 数据库查询正常")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_tree_api()

