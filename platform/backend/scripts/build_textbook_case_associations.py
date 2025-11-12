#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
建立教材-案例关联脚本
基于关键词和内容分析自动建立教材章节与案例的关联关系
"""

import sys
import json
from pathlib import Path
from typing import List, Dict, Tuple
import re

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.textbook.database import SessionLocal
from services.textbook.models import TextbookChapter, ChapterCaseMapping

# 案例索引文件
CASES_INDEX_FILE = Path(__file__).parent.parent / "cases_index.json"


def load_cases_index():
    """加载案例索引"""
    if not CASES_INDEX_FILE.exists():
        print(f"[ERROR] 案例索引文件不存在: {CASES_INDEX_FILE}")
        return {"books": []}
    
    with open(CASES_INDEX_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def extract_keywords_from_case(case_data: Dict) -> List[str]:
    """从案例数据中提取关键词"""
    keywords = set()
    
    # 从标题提取
    title = case_data.get('title', '')
    keywords.update(re.findall(r'[\u4e00-\u9fa5]+', title))
    
    # 从描述提取
    description = case_data.get('description', '')
    keywords.update(re.findall(r'[\u4e00-\u9fa5]{2,}', description))
    
    # 预定义的控制理论关键词
    control_keywords = [
        'PID', 'PI', 'PD', '开关控制', '比例控制', '积分', '微分',
        '水塔', '水箱', '液位', '控制', '仿真', '模型',
        '状态空间', '传递函数', '串级', '前馈', '反馈',
        '参数辨识', '阶跃响应', '频域', '时域',
        '自适应', '预测控制', 'MPC', 'LQR', '滑模', '模糊', '神经网络'
    ]
    
    # 检查标题和描述中是否包含这些关键词
    combined_text = title + description
    for kw in control_keywords:
        if kw in combined_text:
            keywords.add(kw)
    
    return list(keywords)


def calculate_relevance(chapter: TextbookChapter, case_keywords: List[str]) -> float:
    """计算章节与案例的相关度"""
    if not chapter.keywords and not chapter.content:
        return 0.0
    
    # 章节关键词
    chapter_keywords = set(chapter.keywords or [])
    
    # 从章节标题和内容提取关键词
    title_keywords = set(re.findall(r'[\u4e00-\u9fa5]+', chapter.title))
    chapter_keywords.update(title_keywords)
    
    # 从内容提取关键词（前500字）
    content = (chapter.content or '')[:500]
    content_keywords = set(re.findall(r'[\u4e00-\u9fa5]{2,}', content))
    chapter_keywords.update(content_keywords)
    
    # 计算关键词重叠度
    case_kw_set = set(case_keywords)
    intersection = chapter_keywords & case_kw_set
    
    if not intersection:
        return 0.0
    
    # 相关度 = 交集大小 / (章节关键词数 + 案例关键词数 - 交集大小)
    # Jaccard相似度
    union = chapter_keywords | case_kw_set
    relevance = len(intersection) / len(union) if union else 0.0
    
    return relevance


def determine_relation_type(chapter: TextbookChapter, case_data: Dict) -> str:
    """判断关联类型"""
    title = chapter.title.lower()
    case_title = case_data.get('title', '').lower()
    
    # 理论章节
    theory_keywords = ['原理', '理论', '概念', '定义', '基础', '介绍']
    if any(kw in title for kw in theory_keywords):
        return 'theory'
    
    # 实践章节
    practice_keywords = ['案例', '实验', '实践', '应用', '示例']
    if any(kw in title for kw in practice_keywords):
        return 'practice'
    
    # 对比章节
    if '对比' in title or '比较' in title:
        return 'comparison'
    
    # 扩展章节
    if '扩展' in title or '进阶' in title or '高级' in title:
        return 'extension'
    
    # 默认为实践
    return 'practice'


def build_associations():
    """建立教材-案例关联"""
    db = SessionLocal()
    
    print("\n" + "="*60)
    print("  建立教材-案例关联")
    print("="*60 + "\n")
    
    try:
        # 加载案例索引
        cases_index = load_cases_index()
        
        # 获取所有案例
        all_cases = []
        for book in cases_index.get('books', []):
            for case in book.get('cases', []):
                case['book_slug'] = book.get('slug')
                all_cases.append(case)
        
        print(f"[INFO] 找到 {len(all_cases)} 个案例")
        
        # 为每个案例提取关键词
        case_keywords_map = {}
        for case in all_cases:
            case_id = case['id']
            keywords = extract_keywords_from_case(case)
            case_keywords_map[case_id] = keywords
            print(f"  案例 {case_id}: {len(keywords)} 个关键词")
        
        # 获取所有章节
        chapters = db.query(TextbookChapter).all()
        print(f"\n[INFO] 找到 {len(chapters)} 个章节")
        
        # 建立关联
        associations_count = 0
        threshold = 0.05  # 相关度阈值（降低以匹配更多）
        
        print(f"\n[INFO] 开始建立关联（相关度阈值: {threshold}）\n")
        
        for chapter in chapters:
            chapter_associations = []
            
            for case in all_cases:
                case_id = case['id']
                case_keywords = case_keywords_map.get(case_id, [])
                
                # 计算相关度
                relevance = calculate_relevance(chapter, case_keywords)
                
                if relevance >= threshold:
                    chapter_associations.append({
                        'case_id': case_id,
                        'relevance': relevance,
                        'case_title': case['title']
                    })
            
            # 按相关度排序，取前3个
            chapter_associations.sort(key=lambda x: x['relevance'], reverse=True)
            top_associations = chapter_associations[:3]
            
            if top_associations:
                print(f"[{chapter.chapter_number}] {chapter.title}")
                
                for i, assoc in enumerate(top_associations):
                    # 判断关联类型
                    relation_type = determine_relation_type(chapter, case)
                    
                    # 创建关联记录
                    mapping = ChapterCaseMapping(
                        chapter_id=chapter.id,
                        case_id=assoc['case_id'],
                        relation_type=relation_type,
                        relevance_score=assoc['relevance'],
                        description=f"基于关键词自动匹配",
                        order_num=i,
                        is_auto_generated=1
                    )
                    
                    db.add(mapping)
                    associations_count += 1
                    
                    print(f"  → {assoc['case_title']} "
                          f"(相关度: {assoc['relevance']:.2f}, 类型: {relation_type})")
        
        db.commit()
        
        print(f"\n{'='*60}")
        print(f"  关联建立完成")
        print(f"{'='*60}")
        print(f"\n✅ 成功建立 {associations_count} 条关联")
        print(f"✅ 平均每章节: {associations_count/len(chapters):.1f} 个案例")
        
        # 统计每个案例被关联的次数
        case_usage = {}
        for mapping in db.query(ChapterCaseMapping).all():
            case_usage[mapping.case_id] = case_usage.get(mapping.case_id, 0) + 1
        
        print(f"\n📊 案例使用统计:")
        sorted_usage = sorted(case_usage.items(), key=lambda x: x[1], reverse=True)
        for case_id, count in sorted_usage[:10]:
            case_title = next((c['title'] for c in all_cases if c['id'] == case_id), case_id)
            print(f"  {case_id}: {count}次 - {case_title}")
        
    except Exception as e:
        print(f"\n[ERROR] 建立关联失败: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    import sys
    import io
    
    # 设置UTF-8输出
    if sys.platform == 'win32' and hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    
    build_associations()


