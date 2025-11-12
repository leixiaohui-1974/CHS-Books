#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完善案例元数据脚本
从案例README文件中提取详细信息并更新数据库
"""

import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Optional

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.textbook.database import SessionLocal
from services.textbook.models import ChapterCaseMapping

# 案例索引文件
CASES_INDEX_FILE = Path(__file__).parent.parent / "cases_index.json"
BOOKS_BASE_DIR = Path(__file__).parent.parent.parent.parent  # CHS-Books root


def load_cases_index():
    """加载案例索引"""
    if not CASES_INDEX_FILE.exists():
        print(f"[ERROR] 案例索引文件不存在: {CASES_INDEX_FILE}")
        return {"books": []}
    
    with open(CASES_INDEX_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def extract_metadata_from_readme(readme_path: Path) -> Dict:
    """从README文件中提取元数据"""
    if not readme_path.exists():
        return {}
    
    try:
        content = readme_path.read_text(encoding='utf-8')
    except Exception as e:
        print(f"[WARN] 读取README失败 {readme_path}: {e}")
        return {}
    
    metadata = {
        'difficulty': None,
        'estimated_time': None,
        'learning_objectives': [],
        'key_concepts': [],
        'tags': [],
        'prerequisites': [],
        'control_methods': []
    }
    
    # 提取难度等级
    difficulty_patterns = [
        r'难度[：:]\s*([⭐★]+)',
        r'难度级别[：:]\s*(\w+)',
        r'\*\*难度\*\*[：:]\s*([⭐★]+)'
    ]
    for pattern in difficulty_patterns:
        match = re.search(pattern, content)
        if match:
            difficulty_str = match.group(1)
            star_count = len([c for c in difficulty_str if c in '⭐★'])
            if star_count == 1:
                metadata['difficulty'] = '初级'
            elif star_count == 2:
                metadata['difficulty'] = '初级'
            elif star_count == 3:
                metadata['difficulty'] = '中级'
            elif star_count == 4:
                metadata['difficulty'] = '高级'
            else:
                metadata['difficulty'] = '专家'
            break
    
    # 提取预计时间
    time_patterns = [
        r'预计时间[：:]\s*(\d+)\s*分钟',
        r'学习时长[：:]\s*(\d+)\s*分钟',
        r'时间[：:]\s*(\d+)\s*min'
    ]
    for pattern in time_patterns:
        match = re.search(pattern, content)
        if match:
            metadata['estimated_time'] = int(match.group(1))
            break
    
    # 提取学习目标
    objectives_section = re.search(r'##\s*学习目标(.*?)(?=##|$)', content, re.DOTALL)
    if objectives_section:
        objectives_text = objectives_section.group(1)
        # 提取列表项
        objectives = re.findall(r'[-*]\s*(.+)', objectives_text)
        metadata['learning_objectives'] = [obj.strip() for obj in objectives if obj.strip()]
    
    # 提取关键概念/核心内容
    concepts_patterns = [
        r'##\s*关键概念(.*?)(?=##|$)',
        r'##\s*核心内容(.*?)(?=##|$)',
        r'##\s*涉及理论(.*?)(?=##|$)'
    ]
    for pattern in concepts_patterns:
        concepts_section = re.search(pattern, content, re.DOTALL)
        if concepts_section:
            concepts_text = concepts_section.group(1)
            concepts = re.findall(r'[-*]\s*(.+)', concepts_text)
            metadata['key_concepts'].extend([c.strip() for c in concepts if c.strip()])
    
    # 提取控制方法
    control_keywords = {
        'PID': 'PID控制',
        'PI控制': 'PI控制',
        'PD控制': 'PD控制',
        '开关控制': '开关控制',
        'MPC': '模型预测控制',
        '模型预测控制': '模型预测控制',
        'LQR': 'LQR最优控制',
        '状态反馈': '状态反馈',
        '串级控制': '串级控制',
        '前馈控制': '前馈控制',
        '自适应控制': '自适应控制',
        '滑模控制': '滑模控制',
        '模糊控制': '模糊控制',
        '神经网络': '神经网络控制',
        '强化学习': '强化学习控制'
    }
    
    for keyword, method in control_keywords.items():
        if keyword in content:
            if method not in metadata['control_methods']:
                metadata['control_methods'].append(method)
    
    # 提取标签
    tags_section = re.search(r'标签[：:]\s*(.+)', content)
    if tags_section:
        tags_text = tags_section.group(1)
        tags = re.findall(r'`([^`]+)`', tags_text)
        metadata['tags'] = tags
    else:
        # 从控制方法生成标签
        metadata['tags'] = metadata['control_methods'][:5]
    
    return metadata


def save_enhanced_metadata():
    """保存增强的案例元数据到JSON文件"""
    cases_index = load_cases_index()
    
    enhanced_cases = []
    
    for book_data in cases_index.get("books", []):
        book_slug = book_data.get("slug", "")
        
        for case in book_data.get("cases", []):
            case_id = case.get("id")
            case_path = BOOKS_BASE_DIR / "books" / book_slug / "code" / "examples" / case_id
            readme_path = case_path / "README.md"
            
            # 提取元数据
            metadata = extract_metadata_from_readme(readme_path)
            
            # 合并元数据
            enhanced_case = {
                **case,
                "book_slug": book_slug,
                **metadata
            }
            
            enhanced_cases.append(enhanced_case)
    
    # 保存到JSON文件
    output_file = Path(__file__).parent.parent / "enhanced_cases_metadata.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "total_cases": len(enhanced_cases),
            "cases": enhanced_cases
        }, f, ensure_ascii=False, indent=2)
    
    print(f"[OK] 已保存增强元数据到: {output_file}")
    return enhanced_cases


def update_chapter_case_mappings(enhanced_cases: List[Dict]):
    """更新章节-案例关联的描述信息"""
    db = SessionLocal()
    
    try:
        # 创建案例元数据映射
        case_metadata_map = {case['id']: case for case in enhanced_cases}
        
        # 获取所有关联记录
        mappings = db.query(ChapterCaseMapping).all()
        
        updated_count = 0
        
        for mapping in mappings:
            case_id = mapping.case_id
            
            if case_id in case_metadata_map:
                case_meta = case_metadata_map[case_id]
                
                # 更新描述
                description_parts = []
                
                if case_meta.get('difficulty'):
                    description_parts.append(f"难度: {case_meta['difficulty']}")
                
                if case_meta.get('control_methods'):
                    methods = ', '.join(case_meta['control_methods'][:3])
                    description_parts.append(f"控制方法: {methods}")
                
                if case_meta.get('estimated_time'):
                    description_parts.append(f"时长: {case_meta['estimated_time']}分钟")
                
                if description_parts:
                    mapping.description = '; '.join(description_parts)
                    updated_count += 1
        
        db.commit()
        print(f"[OK] 更新了 {updated_count} 条关联记录的描述信息")
        
    except Exception as e:
        print(f"[ERROR] 更新失败: {e}")
        db.rollback()
    finally:
        db.close()


def generate_statistics(enhanced_cases: List[Dict]):
    """生成统计信息"""
    print("\n" + "="*60)
    print("  案例元数据统计")
    print("="*60 + "\n")
    
    # 难度分布
    difficulty_count = {}
    for case in enhanced_cases:
        diff = case.get('difficulty', '未知')
        difficulty_count[diff] = difficulty_count.get(diff, 0) + 1
    
    print("📊 难度分布:")
    for diff, count in sorted(difficulty_count.items(), key=lambda x: (x[0] is None, x[0])):
        print(f"  {diff if diff else '未知'}: {count} 个案例")
    
    # 控制方法统计
    method_count = {}
    for case in enhanced_cases:
        for method in case.get('control_methods', []):
            method_count[method] = method_count.get(method, 0) + 1
    
    print("\n🎯 控制方法统计 (Top 10):")
    sorted_methods = sorted(method_count.items(), key=lambda x: x[1], reverse=True)
    for method, count in sorted_methods[:10]:
        print(f"  {method}: {count} 个案例")
    
    # 学习时间统计
    time_cases = [c for c in enhanced_cases if c.get('estimated_time')]
    if time_cases:
        avg_time = sum(c['estimated_time'] for c in time_cases) / len(time_cases)
        min_time = min(c['estimated_time'] for c in time_cases)
        max_time = max(c['estimated_time'] for c in time_cases)
        
        print(f"\n⏱️  学习时间统计:")
        print(f"  平均时长: {avg_time:.0f} 分钟")
        print(f"  最短: {min_time} 分钟")
        print(f"  最长: {max_time} 分钟")
    
    # 有学习目标的案例数
    with_objectives = len([c for c in enhanced_cases if c.get('learning_objectives')])
    print(f"\n📝 有学习目标的案例: {with_objectives}/{len(enhanced_cases)}")
    
    # 有关键概念的案例数
    with_concepts = len([c for c in enhanced_cases if c.get('key_concepts')])
    print(f"💡 有关键概念的案例: {with_concepts}/{len(enhanced_cases)}")


def main():
    print("\n" + "="*60)
    print("  完善案例元数据")
    print("="*60 + "\n")
    
    print("[STEP 1] 从README文件提取元数据...")
    enhanced_cases = save_enhanced_metadata()
    
    print(f"\n[STEP 2] 处理了 {len(enhanced_cases)} 个案例")
    
    print("\n[STEP 3] 更新章节-案例关联描述...")
    update_chapter_case_mappings(enhanced_cases)
    
    print("\n[STEP 4] 生成统计信息...")
    generate_statistics(enhanced_cases)
    
    print("\n" + "="*60)
    print("  元数据完善完成")
    print("="*60 + "\n")


if __name__ == "__main__":
    import sys
    import io
    
    # 设置UTF-8输出
    if sys.platform == 'win32' and hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    
    main()

