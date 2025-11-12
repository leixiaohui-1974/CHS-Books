#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
考研教材专用导入脚本
支持增量更新和批量导入，方便随时添加新内容
"""

import sys
import io
from pathlib import Path
import re
from datetime import datetime

# 设置UTF-8输出
if sys.platform == 'win32' and hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.textbook.database import SessionLocal
from services.textbook.models import Textbook, TextbookChapter, DifficultyLevel, Base
from sqlalchemy import create_engine

# 项目根目录
EXAM_PREP_DIR = Path(__file__).parent.parent.parent.parent / "books" / "graduate-exam-prep"

# 15本考研书配置
EXAM_BOOKS = [
    {
        "id": 1,
        "slug": "hydraulics-core-100",
        "title": "水力学考研核心100题",
        "subtitle": "精选题目 + Python代码",
        "description": "水力学考研精选100题，每题配Python代码可视化",
        "target_audience": "水利类考研学生",
        "status": "completed",  # completed/in_progress/planned
        "priority": "P0"
    },
    {
        "id": 2,
        "slug": "hydraulics-advanced",
        "title": "水力学考研高分突破",
        "subtitle": "完整教材 + 真题精讲",
        "description": "水力学考研完整教材，包含300+题目和真题精讲",
        "target_audience": "水利类考研学生",
        "status": "in_progress",  # 正在补充内容
        "priority": "P0"
    },
    {
        "id": 3,
        "slug": "hydrology-exam",
        "title": "水文学考研高分突破",
        "subtitle": "产汇流 + 水文统计",
        "description": "水文学专业课考研教材，涵盖产汇流、水文统计等",
        "target_audience": "水利类考研学生",
        "status": "planned",
        "priority": "P0"
    },
    {
        "id": 4,
        "slug": "mathematics-for-water",
        "title": "水利类数学一速成手册",
        "subtitle": "高数 + 线代 + 概率",
        "description": "针对水利专业的数学一复习教材",
        "target_audience": "水利类考研学生",
        "status": "planned",
        "priority": "P1"
    },
    {
        "id": 5,
        "slug": "hydraulics-1000",
        "title": "水力学1000题详解",
        "subtitle": "海量题库",
        "description": "1000+水力学题目详解，按难度分级",
        "target_audience": "水利类考研学生",
        "status": "planned",
        "priority": "P1"
    },
    {
        "id": 6,
        "slug": "python-for-hydraulic",
        "title": "水利工程Python编程实战",
        "subtitle": "代码 + 算法",
        "description": "50个Python项目，涵盖水力计算各个方面",
        "target_audience": "水利类考研学生",
        "status": "planned",
        "priority": "P1"
    },
    {
        "id": 7,
        "slug": "30days-sprint",
        "title": "30天考研冲刺宝典",
        "subtitle": "考前速成",
        "description": "考前30天核心知识点速成",
        "target_audience": "水利类考研学生",
        "status": "planned",
        "priority": "P2"
    },
    {
        "id": 8,
        "slug": "hydraulic-structures-exam",
        "title": "水工建筑物设计考研专题",
        "subtitle": "工程设计",
        "description": "水工建筑物设计专题教材",
        "target_audience": "水利类考研学生",
        "status": "planned",
        "priority": "P2"
    },
    {
        "id": 9,
        "slug": "water-resources-exam",
        "title": "水资源规划与管理考研专题",
        "subtitle": "优化调度",
        "description": "水资源规划与管理专题教材",
        "target_audience": "水利类考研学生",
        "status": "planned",
        "priority": "P2"
    },
    {
        "id": 10,
        "slug": "ecohydraulics-exam",
        "title": "生态水力学考研专题",
        "subtitle": "生态保护",
        "description": "生态水力学专题教材",
        "target_audience": "水利类考研学生",
        "status": "planned",
        "priority": "P2"
    },
    {
        "id": 11,
        "slug": "groundwater-exam",
        "title": "地下水动力学考研专题",
        "subtitle": "渗流理论",
        "description": "地下水动力学专题教材",
        "target_audience": "水利类考研学生",
        "status": "planned",
        "priority": "P2"
    },
    {
        "id": 12,
        "slug": "water-environment-exam",
        "title": "水环境模拟考研专题",
        "subtitle": "水质模拟",
        "description": "水环境模拟专题教材",
        "target_audience": "水利类考研学生",
        "status": "planned",
        "priority": "P2"
    },
    {
        "id": 13,
        "slug": "numerical-methods-exam",
        "title": "水利类考研数值计算方法",
        "subtitle": "数值算法",
        "description": "水利工程中的数值计算方法",
        "target_audience": "水利类考研学生",
        "status": "planned",
        "priority": "P2"
    },
    {
        "id": 14,
        "slug": "mock-exams",
        "title": "水利类考研全真模拟试卷",
        "subtitle": "模拟测试",
        "description": "10套完整模拟试卷",
        "target_audience": "水利类考研学生",
        "status": "planned",
        "priority": "P3"
    },
    {
        "id": 15,
        "slug": "interview-guide",
        "title": "水利考研面试宝典",
        "subtitle": "面试技巧",
        "description": "考研面试技巧与案例",
        "target_audience": "水利类考研学生",
        "status": "planned",
        "priority": "P3"
    }
]


def parse_markdown_file(file_path):
    """解析Markdown文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except Exception as e:
        print(f"[WARN] 读取文件失败 {file_path}: {e}")
        return ""


def extract_chapter_info(content, file_path):
    """从Markdown内容中提取章节信息"""
    lines = content.split('\n')
    
    # 提取第一个标题作为章节名
    title = file_path.stem
    for line in lines[:20]:
        if line.startswith('# '):
            title = line[2:].strip()
            break
    
    # 计算字数
    word_count = len(re.findall(r'[\u4e00-\u9fa5]', content))
    
    # 检测内容特征
    has_code = '```python' in content or '```' in content
    has_formula = '$$' in content or '$' in content or '\\[' in content
    has_image = '![' in content or '<img' in content
    
    # 提取关键词
    keywords = []
    keyword_map = {
        'PID': 'PID控制',
        'MPC': '模型预测控制',
        '考研': '考研',
        '真题': '真题',
        '水箱': '水箱系统',
        '明渠': '明渠流',
        '管道': '管道流',
        '水力': '水力学',
        '水文': '水文学'
    }
    
    for key, value in keyword_map.items():
        if key in content:
            keywords.append(value)
    
    return {
        'title': title,
        'content': content,
        'word_count': word_count,
        'has_code': has_code,
        'has_formula': has_formula,
        'has_image': has_image,
        'keywords': keywords[:5]
    }


def determine_chapter_number(file_path, index):
    """确定章节编号"""
    filename = file_path.stem
    
    # 匹配章节号
    patterns = [
        r'第(\d+)章',
        r'第(\d+)节',
        r'chapter[_\s]?(\d+)',
        r'ch(\d+)',
        r'(\d+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, filename, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return str(index + 1)


def import_or_update_book(book_config, db, force_update=False):
    """导入或更新单本教材"""
    book_slug = book_config['slug']
    book_path = EXAM_PREP_DIR / book_slug
    
    if not book_path.exists():
        print(f"[SKIP] 路径不存在: {book_path}")
        return None
    
    print(f"\n{'='*70}")
    print(f"[{book_config['id']}] {book_config['title']}")
    print(f"状态: {book_config['status']} | 优先级: {book_config['priority']}")
    print(f"{'='*70}")
    
    # 检查是否已存在
    existing = db.query(Textbook).filter(Textbook.title == book_config['title']).first()
    
    if existing and not force_update:
        print(f"[EXISTS] 已存在，跳过（使用 --update 强制更新）")
        return existing
    
    # 查找章节文件
    chapters_dir = book_path / "chapters"
    chapter_files = []
    
    if chapters_dir.exists():
        chapter_files = sorted(chapters_dir.glob("*.md"))
    
    if not chapter_files:
        print(f"[WARN] 未找到章节文件")
        return None
    
    print(f"[INFO] 找到 {len(chapter_files)} 个章节文件")
    
    # 创建或更新教材记录
    if existing:
        textbook = existing
        print(f"[UPDATE] 更新现有教材")
        # 删除旧章节
        db.query(TextbookChapter).filter(TextbookChapter.textbook_id == textbook.id).delete()
    else:
        textbook = Textbook(
            title=book_config['title'],
            subtitle=book_config.get('subtitle'),
            description=book_config['description'],
            target_audience=book_config['target_audience'],
            total_chapters=len(chapter_files),
            total_words=0,
            is_published=1 if book_config['status'] == 'completed' else 0
        )
        db.add(textbook)
        db.flush()
        print(f"[NEW] 创建新教材")
    
    # 导入章节
    total_words = 0
    
    for i, chapter_file in enumerate(chapter_files):
        content = parse_markdown_file(chapter_file)
        if not content:
            continue
        
        chapter_info = extract_chapter_info(content, chapter_file)
        chapter_number = determine_chapter_number(chapter_file, i)
        
        level = 1
        if '.' in chapter_number:
            level = chapter_number.count('.') + 1
        
        chapter = TextbookChapter(
            textbook_id=textbook.id,
            chapter_number=chapter_number,
            title=chapter_info['title'],
            level=level,
            order_num=i,
            content=chapter_info['content'],
            word_count=chapter_info['word_count'],
            has_code=1 if chapter_info['has_code'] else 0,
            has_formula=1 if chapter_info['has_formula'] else 0,
            has_image=1 if chapter_info['has_image'] else 0,
            keywords=chapter_info['keywords'],
            difficulty=DifficultyLevel.BEGINNER
        )
        
        db.add(chapter)
        total_words += chapter_info['word_count']
        
        print(f"  [{chapter_number}] {chapter_info['title'][:50]} ({chapter_info['word_count']} 字)")
    
    # 更新教材总字数
    textbook.total_words = total_words
    textbook.total_chapters = len(chapter_files)
    textbook.updated_at = datetime.utcnow()
    
    db.commit()
    
    print(f"\n[OK] 成功: {len(chapter_files)} 章，共 {total_words:,} 字")
    return textbook


def import_all_books(force_update=False, status_filter=None):
    """批量导入所有考研教材"""
    print("\n" + "="*80)
    print("  📚 考研教材批量导入")
    print("="*80)
    
    # 初始化数据库
    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(exist_ok=True)
    db_path = data_dir / "textbooks.db"
    TEXTBOOK_DB_URL = f"sqlite:///{db_path}"
    engine = create_engine(TEXTBOOK_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    print(f"[OK] 数据库: {db_path}\n")
    
    db = SessionLocal()
    
    try:
        # 过滤要导入的书籍
        books_to_import = EXAM_BOOKS
        if status_filter:
            books_to_import = [b for b in EXAM_BOOKS if b['status'] == status_filter]
            print(f"[FILTER] 只导入状态为 '{status_filter}' 的书籍\n")
        
        imported_count = 0
        updated_count = 0
        skipped_count = 0
        
        for book_config in books_to_import:
            result = import_or_update_book(book_config, db, force_update)
            
            if result:
                if force_update and db.query(Textbook).filter(
                    Textbook.title == book_config['title']
                ).count() > 0:
                    updated_count += 1
                else:
                    imported_count += 1
            else:
                skipped_count += 1
        
        # 最终统计
        from sqlalchemy import func
        total_exam_books = db.query(Textbook).filter(
            Textbook.target_audience.like('%考研%')
        ).count()
        total_exam_chapters = db.query(TextbookChapter).join(Textbook).filter(
            Textbook.target_audience.like('%考研%')
        ).count()
        total_exam_words = db.query(func.sum(Textbook.total_words)).filter(
            Textbook.target_audience.like('%考研%')
        ).scalar() or 0
        
        print("\n" + "="*80)
        print(f"  导入完成!")
        print("="*80)
        print(f"\n✅ 新导入: {imported_count} 本")
        print(f"🔄 更新: {updated_count} 本")
        print(f"⏭️  跳过: {skipped_count} 本")
        
        print(f"\n📊 考研教材统计:")
        print(f"  教材总数: {total_exam_books} 本")
        print(f"  章节总数: {total_exam_chapters} 个")
        print(f"  总字数: {total_exam_words:,} 字")
        print()
        
    except Exception as e:
        print(f"\n[ERROR] 导入失败: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


def show_book_status():
    """显示所有考研书籍的状态"""
    print("\n" + "="*80)
    print("  📋 15本考研教材开发状态")
    print("="*80 + "\n")
    
    status_emoji = {
        'completed': '✅',
        'in_progress': '🚧',
        'planned': '📋'
    }
    
    for book in EXAM_BOOKS:
        emoji = status_emoji.get(book['status'], '❓')
        path = EXAM_PREP_DIR / book['slug']
        exists = path.exists()
        
        print(f"{book['id']:2d}. {emoji} {book['title']}")
        print(f"     状态: {book['status']} | 优先级: {book['priority']}")
        print(f"     路径: {'✓ 存在' if exists else '✗ 不存在'} - {path.name}")
        
        if exists:
            chapters_dir = path / "chapters"
            if chapters_dir.exists():
                chapter_count = len(list(chapters_dir.glob("*.md")))
                print(f"     章节: {chapter_count} 个")
        print()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='考研教材导入工具')
    parser.add_argument('--update', action='store_true', help='强制更新已存在的教材')
    parser.add_argument('--status', choices=['completed', 'in_progress', 'planned'], 
                       help='只导入特定状态的教材')
    parser.add_argument('--list', action='store_true', help='显示所有教材状态')
    
    args = parser.parse_args()
    
    if args.list:
        show_book_status()
    else:
        import_all_books(force_update=args.update, status_filter=args.status)


if __name__ == "__main__":
    main()

