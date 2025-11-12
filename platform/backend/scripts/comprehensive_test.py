#!/usr/bin/env python3
"""
全面功能测试脚本
测试教材、章节、案例的完整链路
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / 'platform' / 'backend'))

import requests
import json

BASE_URL = "http://localhost:8000"

def print_section(title):
    """打印分节标题"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}\n")

def test_textbooks_tree():
    """测试1: 教材树结构API"""
    print_section("测试 1: 教材树结构 API")
    
    try:
        response = requests.get(f"{BASE_URL}/api/textbooks/tree", timeout=10)
        print(f"[OK] API响应状态: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            textbooks = data.get('textbooks', [])
            print(f"[OK] 教材总数: {len(textbooks)}")
            
            for i, book in enumerate(textbooks[:3], 1):  # 只显示前3本
                print(f"\n教材 {i}: {book['title']}")
                print(f"  - 章节数: {book['total_chapters']}")
                print(f"  - 章节结构: {len(book.get('chapters', []))} 个顶级章节")
                
                # 检查有案例的章节
                has_case_count = 0
                def count_cases(chapters):
                    count = 0
                    for ch in chapters:
                        if ch.get('case_count', 0) > 0:
                            count += 1
                        count += count_cases(ch.get('children', []))
                    return count
                
                has_case_count = count_cases(book.get('chapters', []))
                print(f"  - 有案例章节数: {has_case_count}")
        else:
            print(f"[FAIL] API失败: {response.text}")
            
    except Exception as e:
        print(f"[FAIL] 测试失败: {e}")

def test_chapter_details():
    """测试2: 章节详情API"""
    print_section("测试 2: 章节详情 API")
    
    # 获取树结构找到一个有案例的章节
    try:
        response = requests.get(f"{BASE_URL}/api/textbooks/tree", timeout=10)
        data = response.json()
        textbooks = data.get('textbooks', [])
        
        # 查找第一个有案例的章节
        chapter_found = None
        book_title = None
        
        def find_chapter_with_cases(chapters, book_name):
            for ch in chapters:
                if ch.get('case_count', 0) > 0:
                    return ch, book_name
                result = find_chapter_with_cases(ch.get('children', []), book_name)
                if result[0]:
                    return result
            return None, None
        
        for book in textbooks:
            chapter_found, book_title = find_chapter_with_cases(book.get('chapters', []), book['title'])
            if chapter_found:
                break
        
        if not chapter_found:
            print("[FAIL] 未找到任何有案例的章节")
            return
        
        print(f"找到章节: {chapter_found.get('title')} (来自《{book_title}》)")
        print(f"案例数: {chapter_found.get('case_count', 0)}")
        
        # 测试章节详情API
        chapter_id = chapter_found.get('id')
        print(f"\n获取章节详情: {chapter_id}")
        
        response = requests.get(f"{BASE_URL}/api/textbooks/chapters/{chapter_id}/full", timeout=10)
        print(f"[OK] API响应状态: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            chapter = data.get('chapter', {})
            cases = data.get('related_cases', [])
            
            print(f"\n章节信息:")
            print(f"  - 标题: {chapter.get('title')}")
            print(f"  - 字数: {chapter.get('word_count', 0)}")
            print(f"  - 难度: {chapter.get('difficulty', 'N/A')}")
            print(f"  - 内容长度: {len(chapter.get('content', ''))}")
            
            print(f"\n关联案例 ({len(cases)}个):")
            for case in cases:
                print(f"  - {case.get('icon', '📦')} {case.get('title', 'Unknown')}")
                print(f"    类型: {case.get('relation_type', 'N/A')}")
                print(f"    相关度: {case.get('relevance_score', 0)}")
                print(f"    路径: {case.get('path', 'N/A')}")
        else:
            print(f"[FAIL] API失败: {response.text}")
            
    except Exception as e:
        print(f"[FAIL] 测试失败: {e}")

def test_case_files():
    """测试3: 案例文件结构"""
    print_section("测试 3: 案例文件结构")
    
    books_dir = project_root / 'books'
    print(f"books目录: {books_dir}")
    print(f"目录存在: {books_dir.exists()}")
    
    if not books_dir.exists():
        print("[FAIL] books目录不存在!")
        return
    
    # 查找所有案例目录
    case_count = 0
    for book_dir in books_dir.iterdir():
        if not book_dir.is_dir():
            continue
        
        examples_dir = book_dir / 'code' / 'examples'
        if not examples_dir.exists():
            continue
        
        print(f"\n教材: {book_dir.name}")
        for case_dir in examples_dir.iterdir():
            if not case_dir.is_dir():
                continue
            
            case_count += 1
            readme = case_dir / 'README.md'
            main_py = case_dir / 'main.py'
            
            print(f"  案例: {case_dir.name}")
            print(f"    - README.md: {'[OK]' if readme.exists() else '[FAIL]'}")
            print(f"    - main.py: {'[OK]' if main_py.exists() else '[FAIL]'}")
            
            if readme.exists():
                content = readme.read_text(encoding='utf-8')
                lines = content.split('\n')
                title_line = next((l for l in lines if l.startswith('#')), None)
                if title_line:
                    print(f"    - 标题: {title_line.strip('#').strip()}")
    
    print(f"\n[OK] 总共找到 {case_count} 个案例")

def test_api_execute():
    """测试4: 代码执行API"""
    print_section("测试 4: 代码执行 API")
    
    test_code = '''
import numpy as np
import matplotlib.pyplot as plt

# 简单测试
x = np.linspace(0, 10, 100)
y = np.sin(x)

print(f"x范围: [{x.min():.2f}, {x.max():.2f}]")
print(f"y范围: [{y.min():.2f}, {y.max():.2f}]")
print("[OK] 代码执行成功")
'''
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/code/execute",
            json={"code": test_code},
            timeout=30
        )
        print(f"[OK] API响应状态: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n执行结果:")
            print(f"  - 状态: {data.get('status')}")
            print(f"  - 输出:\n{data.get('output', '')}")
            if data.get('error'):
                print(f"  - 错误: {data.get('error')}")
        else:
            print(f"[FAIL] API失败: {response.text}")
            
    except Exception as e:
        print(f"[FAIL] 测试失败: {e}")

def test_frontend_pages():
    """测试5: 前端页面可访问性"""
    print_section("测试 5: 前端页面可访问性")
    
    pages = [
        ("/", "主页"),
        ("/learning", "统一学习平台"),
        ("/docs", "API文档"),
    ]
    
    for path, name in pages:
        try:
            response = requests.get(f"{BASE_URL}{path}", timeout=10)
            status = "[OK]" if response.status_code == 200 else "[FAIL]"
            print(f"{status} {name} ({path}): {response.status_code}")
        except Exception as e:
            print(f"[FAIL] {name} ({path}): {e}")

def test_database_integrity():
    """测试6: 数据库完整性"""
    print_section("测试 6: 数据库完整性")
    
    try:
        # 导入数据库相关模块
        from services.textbook.database import SessionLocal
        from services.textbook.models import Textbook, TextbookChapter, ChapterCaseMapping
        
        db = SessionLocal()
        
        # 统计数据
        textbook_count = db.query(Textbook).count()
        chapter_count = db.query(TextbookChapter).count()
        mapping_count = db.query(ChapterCaseMapping).count()
        
        print(f"[OK] 教材数: {textbook_count}")
        print(f"[OK] 章节数: {chapter_count}")
        print(f"[OK] 章节-案例映射数: {mapping_count}")
        
        # 检查有案例的章节
        chapters_with_cases = db.query(TextbookChapter.id).join(
            ChapterCaseMapping
        ).distinct().count()
        
        print(f"[OK] 有案例的章节数: {chapters_with_cases}")
        
        # 检查案例ID是否有效
        print(f"\n案例ID样本:")
        mappings = db.query(ChapterCaseMapping).limit(5).all()
        for mapping in mappings:
            chapter = db.query(TextbookChapter).filter(TextbookChapter.id == mapping.chapter_id).first()
            print(f"  - 章节: {chapter.title if chapter else 'Unknown'}")
            print(f"    案例ID: {mapping.case_id}")
            print(f"    类型: {mapping.relation_type}")
        
        db.close()
        
    except Exception as e:
        print(f"[FAIL] 测试失败: {e}")
        import traceback
        traceback.print_exc()

def main():
    """运行所有测试"""
    print(f"\n{'#'*60}")
    print(f"# CHS-Books 全面功能测试")
    print(f"# 测试时间: {Path(__file__).stat().st_mtime}")
    print(f"{'#'*60}")
    
    tests = [
        ("教材树结构API", test_textbooks_tree),
        ("章节详情API", test_chapter_details),
        ("案例文件结构", test_case_files),
        ("代码执行API", test_api_execute),
        ("前端页面可访问性", test_frontend_pages),
        ("数据库完整性", test_database_integrity),
    ]
    
    for name, test_func in tests:
        try:
            test_func()
        except KeyboardInterrupt:
            print(f"\n\n用户中断测试")
            break
        except Exception as e:
            print(f"\n[FAIL] {name} 测试失败: {e}")
            import traceback
            traceback.print_exc()
    
    print_section("测试完成")
    print("请根据上述结果修复发现的问题\n")

if __name__ == "__main__":
    main()

