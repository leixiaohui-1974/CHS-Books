#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成教材统计报告
分析教材内容质量、覆盖度、关联情况等
"""
import sys
import io
if sys.platform == 'win32' and hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.textbook.database import SessionLocal
from services.textbook.models import Textbook, TextbookChapter, ChapterCaseMapping, DifficultyLevel
from sqlalchemy import func
import json

def print_header(text):
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80 + "\n")

def generate_comprehensive_stats():
    """生成综合统计报告"""
    db = SessionLocal()
    
    try:
        print_header("📊 CHS-Books 教材系统综合统计报告")
        
        # 1. 基础统计
        print("[1] 基础数据统计")
        print("-" * 60)
        
        total_textbooks = db.query(Textbook).count()
        total_chapters = db.query(TextbookChapter).count()
        total_words = db.query(func.sum(TextbookChapter.word_count)).scalar() or 0
        total_associations = db.query(ChapterCaseMapping).count()
        
        print(f"  📖 教材总数: {total_textbooks} 本")
        print(f"  📄 章节总数: {total_chapters} 个")
        print(f"  📝 总字数: {total_words:,} 字")
        print(f"  🔗 教材-案例关联: {total_associations} 条")
        
        # 2. 教材规模分析
        print("\n[2] 教材规模排行 (Top 10)")
        print("-" * 60)
        
        textbooks = db.query(
            Textbook.title,
            Textbook.total_chapters,
            Textbook.total_words
        ).order_by(Textbook.total_words.desc()).limit(10).all()
        
        for i, (title, chapters, words) in enumerate(textbooks, 1):
            print(f"  {i:2d}. {title[:40]:<40} | {chapters:3d}章 | {words:7,d}字")
        
        # 3. 章节难度分布
        print("\n[3] 章节难度分布")
        print("-" * 60)
        
        difficulty_stats = db.query(
            TextbookChapter.difficulty,
            func.count(TextbookChapter.id)
        ).group_by(TextbookChapter.difficulty).all()
        
        difficulty_map = {
            DifficultyLevel.BEGINNER: "初级",
            DifficultyLevel.INTERMEDIATE: "中级",
            DifficultyLevel.ADVANCED: "高级",
            DifficultyLevel.EXPERT: "专家",
            None: "未分级"
        }
        
        for difficulty, count in difficulty_stats:
            level_name = difficulty_map.get(difficulty, "未分级")
            percentage = (count / total_chapters * 100) if total_chapters > 0 else 0
            bar = "█" * int(percentage / 2)
            print(f"  {level_name:<8} | {count:4d} ({percentage:5.1f}%) {bar}")
        
        # 4. 内容特征统计
        print("\n[4] 内容特征统计")
        print("-" * 60)
        
        chapters_with_code = db.query(func.count(TextbookChapter.id)).filter(
            TextbookChapter.has_code == 1
        ).scalar() or 0
        
        chapters_with_formula = db.query(func.count(TextbookChapter.id)).filter(
            TextbookChapter.has_formula == 1
        ).scalar() or 0
        
        chapters_with_image = db.query(func.count(TextbookChapter.id)).filter(
            TextbookChapter.has_image == 1
        ).scalar() or 0
        
        print(f"  💻 包含代码的章节: {chapters_with_code} ({chapters_with_code/total_chapters*100:.1f}%)")
        print(f"  🧮 包含公式的章节: {chapters_with_formula} ({chapters_with_formula/total_chapters*100:.1f}%)")
        print(f"  🖼️  包含图片的章节: {chapters_with_image} ({chapters_with_image/total_chapters*100:.1f}%)")
        
        # 5. 关联度分析
        print("\n[5] 教材-案例关联分析")
        print("-" * 60)
        
        chapters_with_cases = db.query(
            func.count(func.distinct(ChapterCaseMapping.chapter_id))
        ).scalar() or 0
        
        avg_cases_per_chapter = total_associations / total_chapters if total_chapters > 0 else 0
        
        print(f"  有关联案例的章节: {chapters_with_cases} / {total_chapters} ({chapters_with_cases/total_chapters*100:.1f}%)")
        print(f"  平均每章节关联案例数: {avg_cases_per_chapter:.2f} 个")
        
        # 找出关联最多的章节
        top_associated = db.query(
            TextbookChapter.title,
            Textbook.title.label('textbook_title'),
            func.count(ChapterCaseMapping.id).label('case_count')
        ).join(
            ChapterCaseMapping, TextbookChapter.id == ChapterCaseMapping.chapter_id
        ).join(
            Textbook, TextbookChapter.textbook_id == Textbook.id
        ).group_by(
            TextbookChapter.id
        ).order_by(
            func.count(ChapterCaseMapping.id).desc()
        ).limit(5).all()
        
        if top_associated:
            print("\n  关联案例最多的章节 (Top 5):")
            for i, (chapter_title, textbook_title, count) in enumerate(top_associated, 1):
                print(f"    {i}. {chapter_title[:35]:<35} | {count} 个案例 | {textbook_title[:30]}")
        
        # 6. 字数分布
        print("\n[6] 章节字数分布")
        print("-" * 60)
        
        word_ranges = [
            (0, 100, "< 100字"),
            (100, 500, "100-500字"),
            (500, 1000, "500-1,000字"),
            (1000, 5000, "1,000-5,000字"),
            (5000, 10000, "5,000-10,000字"),
            (10000, 999999, "> 10,000字")
        ]
        
        for min_words, max_words, label in word_ranges:
            count = db.query(func.count(TextbookChapter.id)).filter(
                TextbookChapter.word_count >= min_words,
                TextbookChapter.word_count < max_words
            ).scalar() or 0
            
            percentage = (count / total_chapters * 100) if total_chapters > 0 else 0
            bar = "█" * int(percentage / 2)
            print(f"  {label:<15} | {count:4d} ({percentage:5.1f}%) {bar}")
        
        # 7. 考研教材统计
        print("\n[7] 考研教材专项统计")
        print("-" * 60)
        
        exam_books = db.query(Textbook).filter(
            Textbook.title.contains("考研")
        ).all()
        
        if exam_books:
            print(f"  考研教材数量: {len(exam_books)} 本")
            exam_chapters = sum(b.total_chapters for b in exam_books)
            exam_words = sum(b.total_words for b in exam_books)
            print(f"  考研章节总数: {exam_chapters} 章")
            print(f"  考研内容总字数: {exam_words:,} 字")
            
            print("\n  考研教材列表:")
            for i, book in enumerate(exam_books, 1):
                print(f"    {i}. {book.title} ({book.total_chapters}章, {book.total_words:,}字)")
        else:
            print("  暂无考研教材")
        
        # 8. 质量评估
        print("\n[8] 内容质量评估")
        print("-" * 60)
        
        # 计算质量指标
        quality_score = 0
        max_score = 5
        
        # 指标1: 内容完整性 (有描述、关键词等)
        chapters_with_summary = db.query(func.count(TextbookChapter.id)).filter(
            TextbookChapter.summary.isnot(None)
        ).scalar() or 0
        completeness = chapters_with_summary / total_chapters if total_chapters > 0 else 0
        quality_score += completeness
        
        # 指标2: 案例覆盖率
        coverage = chapters_with_cases / total_chapters if total_chapters > 0 else 0
        quality_score += coverage
        
        # 指标3: 多样性 (代码、公式、图片)
        diversity = (chapters_with_code + chapters_with_formula + chapters_with_image) / (total_chapters * 3) if total_chapters > 0 else 0
        quality_score += diversity
        
        # 指标4: 平均字数 (理想范围: 500-5000字)
        avg_words = total_words / total_chapters if total_chapters > 0 else 0
        word_quality = 1.0 if 500 <= avg_words <= 5000 else 0.5
        quality_score += word_quality
        
        # 指标5: 难度分级覆盖
        difficulty_coverage = len([d for d, c in difficulty_stats if d is not None]) / 4  # 4个难度等级
        quality_score += difficulty_coverage
        
        quality_percentage = (quality_score / max_score) * 100
        
        print(f"  内容完整性: {completeness*100:.1f}% (章节摘要覆盖)")
        print(f"  案例覆盖率: {coverage*100:.1f}% (章节关联案例)")
        print(f"  内容多样性: {diversity*100:.1f}% (代码/公式/图片)")
        print(f"  字数合理性: {word_quality*100:.1f}% (平均{avg_words:.0f}字/章)")
        print(f"  难度分级: {difficulty_coverage*100:.1f}% (难度等级覆盖)")
        print(f"\n  📊 综合质量评分: {quality_score:.2f}/{max_score} ({quality_percentage:.1f}%)")
        
        quality_level = "优秀" if quality_percentage >= 80 else "良好" if quality_percentage >= 60 else "一般" if quality_percentage >= 40 else "需改进"
        print(f"  评级: {quality_level}")
        
        # 9. 建议改进
        print("\n[9] 改进建议")
        print("-" * 60)
        
        suggestions = []
        
        if completeness < 0.5:
            suggestions.append("• 增加章节摘要和关键词，提升内容完整性")
        
        if coverage < 0.4:
            suggestions.append("• 增加教材与案例的关联，当前覆盖率较低")
        
        if chapters_with_code / total_chapters < 0.3:
            suggestions.append("• 增加代码示例，提升实践性")
        
        if chapters_with_formula / total_chapters < 0.2:
            suggestions.append("• 增加公式推导，加强理论深度")
        
        if avg_words < 300:
            suggestions.append("• 部分章节内容较少，建议扩充")
        
        if difficulty_coverage < 0.5:
            suggestions.append("• 完善难度分级，覆盖所有等级")
        
        if len(exam_books) < 10:
            suggestions.append("• 继续开发考研教材，目标15本")
        
        if suggestions:
            for suggestion in suggestions:
                print(f"  {suggestion}")
        else:
            print("  ✅ 内容质量优秀，暂无明显改进点")
        
        print_header("📋 报告生成完成")
        
    finally:
        db.close()

def export_stats_to_json():
    """导出统计数据为JSON格式"""
    db = SessionLocal()
    
    try:
        stats = {
            "generated_at": datetime.now().isoformat(),
            "basic_stats": {
                "total_textbooks": db.query(Textbook).count(),
                "total_chapters": db.query(TextbookChapter).count(),
                "total_words": db.query(func.sum(TextbookChapter.word_count)).scalar() or 0,
                "total_associations": db.query(ChapterCaseMapping).count()
            },
            "textbooks": []
        }
        
        textbooks = db.query(Textbook).all()
        for textbook in textbooks:
            stats["textbooks"].append({
                "id": textbook.id,
                "title": textbook.title,
                "total_chapters": textbook.total_chapters,
                "total_words": textbook.total_words,
                "author": textbook.author,
                "version": textbook.version
            })
        
        output_file = Path(__file__).parent.parent / "data" / "textbook_stats.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 统计数据已导出到: {output_file}")
        
    finally:
        db.close()

if __name__ == "__main__":
    from datetime import datetime
    generate_comprehensive_stats()
    
    print("\n是否导出JSON格式统计数据? (y/n): ", end='')
    # 自动导出
    try:
        export_stats_to_json()
    except Exception as e:
        print(f"导出失败: {e}")

