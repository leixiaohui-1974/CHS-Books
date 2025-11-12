#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量导入所有教材到数据库
包括专业教材和考研资料
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

# 项目根目录
BOOKS_DIR = Path(__file__).parent.parent.parent.parent / "books"

# 教材配置
TEXTBOOK_CONFIGS = [
    {
        "slug": "water-system-control",
        "title": "水系统控制论",
        "path": "water-system-control",
        "description": "基于案例驱动的水系统控制理论与实践教材",
        "target_audience": "水利工程专业本科生、研究生",
        "priority": 1
    },
    {
        "slug": "open-channel-hydraulics",
        "title": "明渠水力学计算",
        "path": "open-channel-hydraulics",
        "description": "明渠流动的水力学原理与数值计算方法",
        "target_audience": "水利工程专业学生",
        "priority": 1
    },
    {
        "slug": "water-environment-simulation",
        "title": "水环境模拟",
        "path": "water-environment-simulation",
        "description": "水环境数值模拟理论、方法与应用",
        "target_audience": "环境工程、水利工程专业",
        "priority": 1
    },
    {
        "slug": "ecohydraulics",
        "title": "生态水力学",
        "path": "ecohydraulics",
        "description": "河流生态系统与水力学的交叉学科",
        "target_audience": "水利、环境、生态专业",
        "priority": 1
    },
    {
        "slug": "distributed-hydrological-model",
        "title": "分布式水文模型",
        "path": "distributed-hydrological-model",
        "description": "流域水文过程的分布式数值模拟",
        "target_audience": "水文学、水资源专业",
        "priority": 1
    },
    {
        "slug": "underground-water-dynamics",
        "title": "地下水动力学",
        "path": "underground-water-dynamics",
        "description": "地下水运动规律与数值模拟",
        "target_audience": "水文地质、水资源专业",
        "priority": 1
    },
    {
        "slug": "water-resource-planning-management",
        "title": "水资源规划与管理",
        "path": "water-resource-planning-management",
        "description": "水资源系统的优化调度与管理",
        "target_audience": "水资源、水利规划专业",
        "priority": 1
    },
    {
        "slug": "intelligent-water-network-design",
        "title": "智能水网设计",
        "path": "intelligent-water-network-design",
        "description": "城市供水管网的智能化设计与优化",
        "target_audience": "市政工程、给排水专业",
        "priority": 1
    },
    {
        "slug": "canal-pipeline-control",
        "title": "渠道管道控制",
        "path": "canal-pipeline-control",
        "description": "输水系统的先进控制理论与实践",
        "target_audience": "水利自动化专业",
        "priority": 2
    },
    {
        "slug": "photovoltaic-system-modeling-control",
        "title": "光伏系统建模与控制",
        "path": "photovoltaic-system-modeling-control",
        "description": "太阳能光伏发电系统的建模、控制与优化",
        "target_audience": "新能源、电气工程专业",
        "priority": 2
    },
    {
        "slug": "wind-power-system-modeling-control",
        "title": "风力发电系统建模与控制",
        "path": "wind-power-system-modeling-control",
        "description": "风力发电系统的动态特性与控制策略",
        "target_audience": "新能源、电气工程专业",
        "priority": 2
    },
    {
        "slug": "graduate-exam-prep/hydraulics-core-100",
        "title": "水力学考研核心100题",
        "path": "graduate-exam-prep/hydraulics-core-100",
        "description": "水力学考研精选题目，以实际考题为导向",
        "target_audience": "水利类考研学生",
        "priority": 1,
        "is_exam_prep": True
    },
    {
        "slug": "graduate-exam-prep/hydraulics-advanced",
        "title": "水力学考研高分突破",
        "path": "graduate-exam-prep/hydraulics-advanced",
        "description": "水力学考研完整教材，包含真题精讲",
        "target_audience": "水利类考研学生",
        "priority": 1,
        "is_exam_prep": True
    },
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
    if 'PID' in content:
        keywords.append('PID控制')
    if 'MPC' in content or '模型预测' in content:
        keywords.append('模型预测控制')
    if '水箱' in content:
        keywords.append('水箱系统')
    if '明渠' in content:
        keywords.append('明渠流')
    if '管道' in content:
        keywords.append('管道流')
    
    return {
        'title': title,
        'content': content,
        'word_count': word_count,
        'has_code': has_code,
        'has_formula': has_formula,
        'has_image': has_image,
        'keywords': keywords[:5]  # 最多5个关键词
    }


def determine_chapter_number(file_path, index):
    """确定章节编号"""
    # 尝试从文件名提取章节号
    filename = file_path.stem
    
    # 匹配 "第X章" 或 "第X节" 或 "chapterXX"
    patterns = [
        r'第(\d+)章',
        r'第(\d+)节',
        r'chapter_?(\d+)',
        r'ch(\d+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, filename, re.IGNORECASE)
        if match:
            return match.group(1)
    
    # 如果没有匹配，使用索引
    return str(index + 1)


def import_textbook(config, db):
    """导入单本教材"""
    book_slug = config['slug']
    book_path = BOOKS_DIR / config['path']
    
    if not book_path.exists():
        print(f"[SKIP] 路径不存在: {book_path}")
        return False
    
    print(f"\n{'='*60}")
    print(f"导入: {config['title']}")
    print(f"{'='*60}")
    
    # 检查是否已导入
    existing = db.query(Textbook).filter(Textbook.title == config['title']).first()
    if existing:
        print(f"[SKIP] 已存在，跳过")
        return False
    
    # 查找所有chapter的markdown文件
    chapter_files = []
    
    # 查找chapters目录
    chapters_dir = book_path / "chapters"
    if chapters_dir.exists():
        chapter_files = sorted(chapters_dir.glob("*.md"))
    
    # 如果没有chapters目录，查找docs目录
    if not chapter_files:
        docs_dir = book_path / "docs"
        if docs_dir.exists():
            chapter_files = sorted(docs_dir.glob("*.md"))
    
    # 如果还是没有，查找根目录的md文件（排除README等）
    if not chapter_files:
        chapter_files = sorted([
            f for f in book_path.glob("*.md")
            if f.stem not in ['README', 'LICENSE', 'CHANGELOG', 'TODO']
        ])
    
    if not chapter_files:
        print(f"[WARN] 未找到章节文件")
        return False
    
    print(f"[INFO] 找到 {len(chapter_files)} 个章节文件")
    
    # 创建教材记录
    textbook = Textbook(
        title=config['title'],
        description=config['description'],
        target_audience=config['target_audience'],
        total_chapters=len(chapter_files),
        total_words=0,
        is_published=1
    )
    
    db.add(textbook)
    db.flush()  # 获取textbook.id
    
    # 导入章节
    total_words = 0
    
    for i, chapter_file in enumerate(chapter_files):
        content = parse_markdown_file(chapter_file)
        if not content:
            continue
        
        chapter_info = extract_chapter_info(content, chapter_file)
        chapter_number = determine_chapter_number(chapter_file, i)
        
        # 判断层级
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
        
        print(f"  [{chapter_number}] {chapter_info['title'][:40]} ({chapter_info['word_count']} 字)")
    
    # 更新教材总字数
    textbook.total_words = total_words
    
    db.commit()
    
    print(f"\n[OK] 导入成功: {len(chapter_files)} 章，共 {total_words:,} 字")
    return True


def main():
    print("\n" + "="*80)
    print("  📚 批量导入所有教材")
    print("="*80)
    
    # 初始化数据库
    from sqlalchemy import create_engine
    import os
    
    # 确保data目录存在
    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(exist_ok=True)
    
    db_path = data_dir / "textbooks.db"
    TEXTBOOK_DB_URL = f"sqlite:///{db_path}"
    engine = create_engine(TEXTBOOK_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    print(f"[OK] 数据库已初始化: {db_path}")
    
    db = SessionLocal()
    
    try:
        # 按优先级排序
        configs = sorted(TEXTBOOK_CONFIGS, key=lambda x: x['priority'])
        
        imported_count = 0
        skipped_count = 0
        
        for config in configs:
            result = import_textbook(config, db)
            if result:
                imported_count += 1
            else:
                skipped_count += 1
        
        print("\n" + "="*80)
        print(f"  导入完成!")
        print("="*80)
        print(f"\n✅ 成功导入: {imported_count} 本")
        print(f"⏭️  跳过: {skipped_count} 本")
        
        # 显示最终统计
        from sqlalchemy import func
        total_textbooks = db.query(Textbook).count()
        total_chapters = db.query(TextbookChapter).count()
        total_words = db.query(func.sum(Textbook.total_words)).scalar() or 0
        
        print(f"\n📊 数据库统计:")
        print(f"  教材总数: {total_textbooks} 本")
        print(f"  章节总数: {total_chapters} 个")
        print(f"  总字数: {total_words:,} 字")
        print()
        
    except Exception as e:
        print(f"\n[ERROR] 导入失败: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()

