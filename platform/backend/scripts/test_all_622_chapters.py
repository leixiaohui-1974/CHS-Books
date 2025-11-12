#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全部622个教材章节深度测试
检查每个章节的渲染质量和内容完整性
"""
import sys
import io
if sys.platform == 'win32' and hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import requests
import json
import time
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import re

BASE_URL = "http://localhost:8000"

def print_header(text):
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80 + "\n")

def check_chapter_quality(chapter_data):
    """检查章节内容质量"""
    content = chapter_data.get('content', '')
    
    quality = {
        "length": len(content),
        "has_content": len(content) > 0,
        "word_count": len(content) // 2,  # 粗略估计中文字数
        
        # Markdown元素检查
        "has_headings": bool(re.search(r'^#{1,6}\s', content, re.MULTILINE)),
        "has_code": '```' in content,
        "has_list": bool(re.search(r'^[-*+]\s', content, re.MULTILINE) or 
                        re.search(r'^\d+\.\s', content, re.MULTILINE)),
        "has_bold": '**' in content or '__' in content,
        "has_italic": '*' in content or '_' in content,
        "has_link": '[' in content and '](' in content,
        "has_image": '![' in content,
        "has_table": '|' in content and re.search(r'\|.*\|.*\|', content),
        "has_blockquote": bool(re.search(r'^>\s', content, re.MULTILINE)),
        "has_hr": '---' in content or '***' in content,
        
        # 代码块统计
        "code_blocks": content.count('```') // 2,
        "headings_count": len(re.findall(r'^#{1,6}\s', content, re.MULTILINE)),
        "links_count": content.count(']('),
        "images_count": content.count('!['),
        "tables_count": len(re.findall(r'\|.*\|.*\|', content)) // 3,  # 粗略估计
    }
    
    # 质量评分（0-100）
    score = 0
    if quality['has_content']:
        score += 20
    if quality['word_count'] > 100:
        score += 15
    if quality['word_count'] > 500:
        score += 10
    if quality['has_headings']:
        score += 10
    if quality['has_code']:
        score += 10
    if quality['has_list']:
        score += 5
    if quality['has_table']:
        score += 10
    if quality['has_image']:
        score += 10
    if quality['has_link']:
        score += 5
    if quality['code_blocks'] >= 2:
        score += 5
    
    quality['score'] = min(score, 100)
    
    return quality

def test_textbook_chapters(textbook_id, textbook_title):
    """测试单个教材的所有章节"""
    results = {
        "textbook_id": textbook_id,
        "title": textbook_title,
        "chapters": [],
        "stats": {}
    }
    
    try:
        # 获取章节列表
        response = requests.get(f"{BASE_URL}/api/textbooks/{textbook_id}/chapters", timeout=5)
        if response.status_code != 200:
            results["error"] = f"HTTP {response.status_code}"
            return results
        
        chapters_data = response.json()
        if isinstance(chapters_data, dict):
            chapters = chapters_data.get('chapters', [])
        else:
            chapters = chapters_data
        
        results["total_chapters"] = len(chapters)
        
        # 测试每个章节
        for chapter in chapters:
            chapter_id = chapter.get('id')
            chapter_number = chapter.get('chapter_number', 'N/A')
            chapter_title = chapter.get('title', 'Unknown')
            
            try:
                # 获取章节详情
                detail_response = requests.get(
                    f"{BASE_URL}/api/textbooks/chapter/{chapter_id}", 
                    timeout=5
                )
                
                if detail_response.status_code == 200:
                    detail_data = detail_response.json()
                    chapter_info = detail_data.get('chapter', {})
                    
                    quality = check_chapter_quality(chapter_info)
                    
                    results["chapters"].append({
                        "id": chapter_id,
                        "number": chapter_number,
                        "title": chapter_title,
                        "quality": quality,
                        "status": "success"
                    })
                else:
                    results["chapters"].append({
                        "id": chapter_id,
                        "number": chapter_number,
                        "title": chapter_title,
                        "status": "fail",
                        "error": f"HTTP {detail_response.status_code}"
                    })
            
            except Exception as e:
                results["chapters"].append({
                    "id": chapter_id,
                    "number": chapter_number,
                    "title": chapter_title,
                    "status": "error",
                    "error": str(e)[:100]
                })
            
            time.sleep(0.05)  # 避免请求过快
        
        # 统计数据
        successful = [c for c in results["chapters"] if c.get("status") == "success"]
        if successful:
            scores = [c['quality']['score'] for c in successful]
            results["stats"] = {
                "total": len(chapters),
                "successful": len(successful),
                "avg_score": sum(scores) / len(scores) if scores else 0,
                "empty_chapters": sum(1 for c in successful if c['quality']['word_count'] == 0),
                "with_code": sum(1 for c in successful if c['quality']['has_code']),
                "with_images": sum(1 for c in successful if c['quality']['has_image']),
                "with_tables": sum(1 for c in successful if c['quality']['has_table']),
            }
    
    except Exception as e:
        results["error"] = str(e)[:200]
    
    return results

def main():
    print_header("🧪 全部622个教材章节深度测试")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"测试服务器: {BASE_URL}")
    
    # 获取教材列表
    print_header("📋 第1步：获取教材列表")
    try:
        response = requests.get(f"{BASE_URL}/api/textbooks/", timeout=10)
        textbooks_data = response.json()
        
        if isinstance(textbooks_data, list):
            textbooks = textbooks_data
        else:
            textbooks = textbooks_data.get('textbooks', [])
        
        print(f"✅ 成功获取 {len(textbooks)} 本教材")
    except Exception as e:
        print(f"❌ 获取教材列表失败: {e}")
        return
    
    # 测试所有教材的章节
    print_header("🔍 第2步：逐一测试教材章节")
    print("这将需要几分钟时间...\n")
    
    all_results = []
    total_chapters_tested = 0
    
    for i, textbook in enumerate(textbooks, 1):
        textbook_id = textbook.get('id')
        title = textbook.get('title', 'Unknown')
        total_chapters = textbook.get('total_chapters', 0)
        
        print(f"\n[{i}/{len(textbooks)}] 测试: {title[:50]} ({total_chapters}章)")
        
        result = test_textbook_chapters(textbook_id, title)
        all_results.append(result)
        
        if 'stats' in result:
            stats = result['stats']
            print(f"  ✅ 成功测试 {stats['successful']}/{stats['total']} 章")
            print(f"  📊 平均质量: {stats['avg_score']:.1f}分")
            print(f"  📝 空章节: {stats['empty_chapters']}个")
            print(f"  💻 含代码: {stats['with_code']}章")
            print(f"  🖼️ 含图片: {stats['with_images']}章")
            
            total_chapters_tested += stats['successful']
        elif 'error' in result:
            print(f"  ❌ 错误: {result['error']}")
    
    # 全局统计
    print_header("📊 第3步：全局统计分析")
    
    total_textbooks = len(all_results)
    total_chapters = sum(r.get('total_chapters', 0) for r in all_results)
    successful_chapters = sum(r.get('stats', {}).get('successful', 0) for r in all_results)
    
    all_scores = []
    total_empty = 0
    total_with_code = 0
    total_with_images = 0
    total_with_tables = 0
    
    for result in all_results:
        if 'stats' in result:
            chapters = result.get('chapters', [])
            successful = [c for c in chapters if c.get('status') == 'success']
            all_scores.extend([c['quality']['score'] for c in successful])
            
            stats = result['stats']
            total_empty += stats.get('empty_chapters', 0)
            total_with_code += stats.get('with_code', 0)
            total_with_images += stats.get('with_images', 0)
            total_with_tables += stats.get('with_tables', 0)
    
    avg_score = sum(all_scores) / len(all_scores) if all_scores else 0
    
    print(f"教材总数: {total_textbooks}")
    print(f"章节总数: {total_chapters}")
    print(f"测试成功: {successful_chapters}/{total_chapters} ({successful_chapters/total_chapters*100:.1f}%)")
    print(f"\n平均质量评分: {avg_score:.1f}/100")
    print(f"空章节: {total_empty} ({total_empty/successful_chapters*100:.1f}%)")
    print(f"含代码章节: {total_with_code} ({total_with_code/successful_chapters*100:.1f}%)")
    print(f"含图片章节: {total_with_images} ({total_with_images/successful_chapters*100:.1f}%)")
    print(f"含表格章节: {total_with_tables} ({total_with_tables/successful_chapters*100:.1f}%)")
    
    # 评级
    print("\n" + "="*80)
    if avg_score >= 70:
        print("  内容质量评级: ⭐⭐⭐⭐⭐ 优秀")
    elif avg_score >= 60:
        print("  内容质量评级: ⭐⭐⭐⭐ 良好")
    elif avg_score >= 50:
        print("  内容质量评级: ⭐⭐⭐ 中等")
    else:
        print("  内容质量评级: ⭐⭐ 需改进")
    print("="*80)
    
    # 按质量排序教材
    print_header("📈 第4步：教材质量排名")
    
    textbook_rankings = []
    for result in all_results:
        if 'stats' in result:
            textbook_rankings.append({
                'title': result['title'][:40],
                'chapters': result['stats']['total'],
                'score': result['stats']['avg_score'],
                'empty': result['stats']['empty_chapters']
            })
    
    textbook_rankings.sort(key=lambda x: x['score'], reverse=True)
    
    print("\n前10名教材:")
    for i, tb in enumerate(textbook_rankings[:10], 1):
        print(f"  {i}. {tb['title']} - {tb['score']:.1f}分 ({tb['chapters']}章, {tb['empty']}空)")
    
    if len(textbook_rankings) > 10:
        print(f"\n后{len(textbook_rankings)-10}名教材:")
        for i, tb in enumerate(textbook_rankings[-5:], len(textbook_rankings)-4):
            print(f"  {i}. {tb['title']} - {tb['score']:.1f}分 ({tb['chapters']}章, {tb['empty']}空)")
    
    print_header("✅ 测试完成")
    
    # 保存详细报告
    report = {
        "test_time": datetime.now().isoformat(),
        "summary": {
            "total_textbooks": total_textbooks,
            "total_chapters": total_chapters,
            "successful_chapters": successful_chapters,
            "avg_score": avg_score,
            "empty_chapters": total_empty,
            "chapters_with_code": total_with_code,
            "chapters_with_images": total_with_images,
            "chapters_with_tables": total_with_tables
        },
        "textbooks": all_results
    }
    
    report_file = Path(__file__).parent.parent / "all_622_chapters_test_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"📄 详细报告已保存: {report_file}")
    
    return report

if __name__ == "__main__":
    try:
        report = main()
        
        # 如果平均分低于50，返回警告退出码
        if report and report['summary']['avg_score'] < 50:
            sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️ 测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 测试过程发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

