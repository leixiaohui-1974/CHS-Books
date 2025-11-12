#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
教材解析脚本
从Markdown文件中解析教材章节结构和内容
"""

import re
import sys
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import hashlib

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.textbook.models import DifficultyLevel
from services.textbook.database import SessionLocal, init_database
from services.textbook.models import Textbook, TextbookChapter


class TextbookParser:
    """教材解析器"""
    
    def __init__(self):
        self.chapters = []
        self.current_chapter_stack = []  # 章节层级栈
        
    def parse_markdown_file(self, filepath: Path) -> Dict:
        """解析单个Markdown文件"""
        if not filepath.exists():
            print(f"[ERROR] 文件不存在: {filepath}")
            return None
            
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"[ERROR] 读取文件失败 {filepath}: {e}")
            return None
        
        # 提取标题和元数据
        metadata = self._extract_metadata(content)
        
        # 解析章节结构
        chapters = self._parse_chapters(content)
        
        return {
            'metadata': metadata,
            'chapters': chapters,
            'source_file': str(filepath)
        }
    
    def _extract_metadata(self, content: str) -> Dict:
        """提取教材元数据"""
        metadata = {
            'title': '',
            'author': '',
            'version': '1.0',
            'description': '',
            'target_audience': '',
            'total_words': len(content)
        }
        
        # 提取第一个一级标题作为教材标题
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if title_match:
            metadata['title'] = title_match.group(1).strip()
        
        # 提取作者（如果有）
        author_match = re.search(r'\*\*作者[：:]\*\*\s*(.+)', content)
        if author_match:
            metadata['author'] = author_match.group(1).strip()
        
        # 提取版本
        version_match = re.search(r'\*\*版本[：:]\*\*\s*v?(\d+\.\d+\.?\d*)', content)
        if version_match:
            metadata['version'] = version_match.group(1).strip()
        
        # 提取目标受众
        audience_match = re.search(r'\*\*目标受众[：:]\*\*\s*(.+)', content)
        if audience_match:
            metadata['target_audience'] = audience_match.group(1).strip()
        
        return metadata
    
    def _parse_chapters(self, content: str) -> List[Dict]:
        """解析章节结构"""
        chapters = []
        lines = content.split('\n')
        
        current_chapter = None
        current_content_lines = []
        chapter_counter = {1: 0, 2: 0, 3: 0, 4: 0}  # 各级章节计数器
        
        for i, line in enumerate(lines):
            # 匹配标题（# ## ### ####）
            heading_match = re.match(r'^(#{1,4})\s+(.+)$', line)
            
            if heading_match:
                # 保存上一个章节
                if current_chapter:
                    current_chapter['content'] = '\n'.join(current_content_lines).strip()
                    current_chapter['word_count'] = len(current_chapter['content'])
                    chapters.append(current_chapter)
                    current_content_lines = []
                
                # 解析新章节
                level = len(heading_match.group(1))
                title = heading_match.group(2).strip()
                
                # 更新计数器
                chapter_counter[level] += 1
                for l in range(level + 1, 5):
                    chapter_counter[l] = 0
                
                # 生成章节号
                if level == 1:
                    chapter_number = f"{chapter_counter[1]}"
                elif level == 2:
                    chapter_number = f"{chapter_counter[1]}.{chapter_counter[2]}"
                elif level == 3:
                    chapter_number = f"{chapter_counter[1]}.{chapter_counter[2]}.{chapter_counter[3]}"
                else:
                    chapter_number = f"{chapter_counter[1]}.{chapter_counter[2]}.{chapter_counter[3]}.{chapter_counter[4]}"
                
                current_chapter = {
                    'chapter_number': chapter_number,
                    'title': title,
                    'level': level,
                    'order_num': len(chapters),
                    'content': '',
                    'keywords': self._extract_keywords(title),
                    'has_code': 0,
                    'has_formula': 0,
                    'has_image': 0
                }
            else:
                if current_chapter:
                    current_content_lines.append(line)
                    
                    # 检测内容特征
                    if '```' in line:
                        current_chapter['has_code'] = 1
                    if '$' in line or '$$' in line:
                        current_chapter['has_formula'] = 1
                    if '![' in line or '<img' in line:
                        current_chapter['has_image'] = 1
        
        # 保存最后一个章节
        if current_chapter:
            current_chapter['content'] = '\n'.join(current_content_lines).strip()
            current_chapter['word_count'] = len(current_chapter['content'])
            chapters.append(current_chapter)
        
        return chapters
    
    def _extract_keywords(self, text: str) -> List[str]:
        """从文本中提取关键词"""
        keywords = []
        
        # 常见的控制理论关键词
        keyword_patterns = [
            'PID', 'PI', 'PD', '控制', '系统', '水箱', '模型', '仿真',
            '状态空间', '传递函数', '频域', '时域', '稳定性', '鲁棒',
            '优化', '自适应', '预测', '神经网络', '模糊', '强化学习',
            '观测器', 'LQR', 'MPC', '串级', '前馈', '反馈'
        ]
        
        for keyword in keyword_patterns:
            if keyword in text:
                keywords.append(keyword)
        
        return keywords[:10]  # 最多10个关键词


def import_textbook_from_markdown(filepath: Path, db_session):
    """从Markdown文件导入教材到数据库"""
    parser = TextbookParser()
    
    print(f"\n[INFO] 正在解析: {filepath}")
    result = parser.parse_markdown_file(filepath)
    
    if not result:
        return None
    
    metadata = result['metadata']
    chapters_data = result['chapters']
    
    # 创建教材记录
    textbook = Textbook(
        title=metadata['title'] or filepath.stem,
        author=metadata.get('author', ''),
        version=metadata.get('version', '1.0'),
        description=metadata.get('description', ''),
        target_audience=metadata.get('target_audience', ''),
        total_chapters=len(chapters_data),
        total_words=metadata['total_words']
    )
    
    db_session.add(textbook)
    db_session.flush()  # 获取textbook.id
    
    print(f"[OK] 创建教材: {textbook.title}")
    print(f"[INFO] 发现 {len(chapters_data)} 个章节")
    
    # 创建章节记录
    chapter_id_map = {}  # 章节号 -> 章节ID的映射
    parent_stack = [None] * 5  # 各级父章节ID栈
    
    for chapter_data in chapters_data:
        level = chapter_data['level']
        
        # 确定父章节ID
        parent_id = parent_stack[level - 1] if level > 1 else None
        
        chapter = TextbookChapter(
            textbook_id=textbook.id,
            chapter_number=chapter_data['chapter_number'],
            title=chapter_data['title'],
            level=level,
            order_num=chapter_data['order_num'],
            parent_id=parent_id,
            content=chapter_data['content'],
            keywords=chapter_data['keywords'],
            word_count=chapter_data['word_count'],
            has_code=chapter_data['has_code'],
            has_formula=chapter_data['has_formula'],
            has_image=chapter_data['has_image'],
            difficulty=DifficultyLevel.BEGINNER  # 默认难度
        )
        
        db_session.add(chapter)
        db_session.flush()  # 获取chapter.id
        
        # 更新父章节栈
        parent_stack[level] = chapter.id
        for i in range(level + 1, 5):
            parent_stack[i] = None
        
        chapter_id_map[chapter_data['chapter_number']] = chapter.id
        
        print(f"  [{level}] {chapter.chapter_number} {chapter.title[:50]}")
    
    db_session.commit()
    print(f"[SUCCESS] 教材导入完成!")
    
    return textbook


def scan_and_import_textbooks(docs_dir: Path):
    """扫描目录并导入所有教材"""
    init_database()
    db_session = SessionLocal()
    
    # 设置输出编码（在函数开始处）
    import sys
    import io
    original_stdout = sys.stdout
    if sys.platform == 'win32' and hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    
    try:
        # 查找所有Markdown文件
        md_files = list(docs_dir.rglob("*.md"))
        
        print(f"\n{'='*60}")
        print(f"  教材批量导入")
        print(f"{'='*60}")
        print(f"\n发现 {len(md_files)} 个Markdown文件")
        
        imported_count = 0
        
        for md_file in md_files:
            # 跳过一些非教材文件
            skip_patterns = ['README', 'CHANGELOG', 'TODO', 'LICENSE']
            if any(pattern in md_file.name for pattern in skip_patterns):
                print(f"[SKIP] {md_file.name}")
                continue
            
            try:
                textbook = import_textbook_from_markdown(md_file, db_session)
                if textbook:
                    imported_count += 1
            except Exception as e:
                print(f"[ERROR] 导入失败 {md_file}: {e}")
                db_session.rollback()
                continue
        
        print(f"\n{'='*60}")
        print(f"  导入完成: {imported_count}/{len(md_files)} 个教材")
        print(f"{'='*60}\n")
        
    finally:
        db_session.close()


if __name__ == "__main__":
    import sys
    import io
    
    # 设置输出编码
    if sys.platform == 'win32' and hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    
    if len(sys.argv) > 1:
        docs_path = Path(sys.argv[1])
    else:
        # 默认导入两个路径
        base_path = Path(__file__).parent.parent.parent.parent / "books" / "water-system-control"
        docs_paths = [
            base_path / "docs",
            base_path / "code" / "examples"  # 也导入案例目录的教程文档
        ]
        
        for docs_path in docs_paths:
            if docs_path.exists():
                print(f"\n扫描目录: {docs_path}")
                scan_and_import_textbooks(docs_path)
        
        sys.exit(0)
    
    if not docs_path.exists():
        print(f"[ERROR] 路径不存在: {docs_path}")
        sys.exit(1)
    
    scan_and_import_textbooks(docs_path)

