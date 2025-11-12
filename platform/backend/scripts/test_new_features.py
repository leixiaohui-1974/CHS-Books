#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新增功能：教材阅读器和统一搜索
"""
import sys
import io
if sys.platform == 'win32' and hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def print_header(text):
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80 + "\n")

def print_section(text):
    print(f"\n{text}")
    print("-"*60)

def test_frontend_pages():
    """测试前端页面是否可访问"""
    print_header("📄 测试前端页面访问")
    
    pages = [
        ("/", "主页"),
        ("/unified.html", "统一平台"),
        ("/textbooks.html", "教材阅读器"),
        ("/search.html", "搜索页面")
    ]
    
    all_ok = True
    for path, name in pages:
        try:
            response = requests.get(f"{BASE_URL}{path}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {name}: {path} - 状态码 {response.status_code}")
            else:
                print(f"❌ {name}: {path} - 状态码 {response.status_code}")
                all_ok = False
        except Exception as e:
            print(f"❌ {name}: {path} - 错误: {e}")
            all_ok = False
    
    return all_ok

def test_textbook_api():
    """测试教材API"""
    print_header("📖 测试教材API")
    
    all_ok = True
    
    # 1. 获取教材列表
    print_section("[1] GET /api/textbooks/")
    try:
        response = requests.get(f"{BASE_URL}/api/textbooks/")
        data = response.json()
        
        # API返回可能是数组或对象格式
        textbooks = data if isinstance(data, list) else data.get('textbooks', [])
        
        if textbooks and len(textbooks) > 0:
            print(f"✅ 成功获取 {len(textbooks)} 本教材")
            print(f"   第一本: {textbooks[0]['title']} ({textbooks[0]['total_chapters']} 章)")
            textbook_id = textbooks[0]['id']
        else:
            print("❌ 教材列表为空")
            all_ok = False
            return all_ok
    except Exception as e:
        print(f"❌ 失败: {e}")
        import traceback
        traceback.print_exc()
        all_ok = False
        return all_ok
    
    # 2. 获取教材详情
    print_section(f"[2] GET /api/textbooks/{textbook_id}")
    try:
        response = requests.get(f"{BASE_URL}/api/textbooks/{textbook_id}")
        data = response.json()
        if data['success']:
            print(f"✅ 成功获取教材详情")
            print(f"   标题: {data['textbook']['title']}")
            print(f"   章节: {data['textbook']['total_chapters']}")
            print(f"   字数: {data['textbook']['total_words']:,}")
        else:
            print("❌ 获取详情失败")
            all_ok = False
    except Exception as e:
        print(f"❌ 失败: {e}")
        all_ok = False
    
    # 3. 获取章节列表
    print_section(f"[3] GET /api/textbooks/{textbook_id}/chapters")
    try:
        response = requests.get(f"{BASE_URL}/api/textbooks/{textbook_id}/chapters")
        data = response.json()
        if data['success'] and len(data['chapters']) > 0:
            print(f"✅ 成功获取 {len(data['chapters'])} 个章节")
            chapter_id = data['chapters'][0]['id']
            print(f"   第一章: [{data['chapters'][0]['chapter_number']}] {data['chapters'][0]['title']}")
        else:
            print("❌ 章节列表为空")
            all_ok = False
            return all_ok
    except Exception as e:
        print(f"❌ 失败: {e}")
        all_ok = False
        return all_ok
    
    # 4. 获取章节内容
    print_section(f"[4] GET /api/textbooks/chapter/{chapter_id}")
    try:
        response = requests.get(f"{BASE_URL}/api/textbooks/chapter/{chapter_id}")
        data = response.json()
        if data['success']:
            print(f"✅ 成功获取章节内容")
            print(f"   章节: [{data['chapter']['chapter_number']}] {data['chapter']['title']}")
            print(f"   内容长度: {len(data['chapter']['content'])} 字符")
            if data['chapter'].get('associated_cases'):
                print(f"   关联案例: {len(data['chapter']['associated_cases'])} 个")
        else:
            print("❌ 获取章节内容失败")
            all_ok = False
    except Exception as e:
        print(f"❌ 失败: {e}")
        all_ok = False
    
    return all_ok

def test_search_api():
    """测试搜索API"""
    print_header("🔍 测试搜索API")
    
    all_ok = True
    
    # 1. 获取统计信息
    print_section("[1] GET /api/search/stats")
    try:
        response = requests.get(f"{BASE_URL}/api/search/stats")
        data = response.json()
        print("✅ 成功获取统计信息:")
        print(f"   📖 教材: {data['textbooks']['total']} 本, {data['textbooks']['chapters']} 章")
        print(f"   💻 案例: {data['cases']['total']} 个")
        print(f"   🧠 知识库: {data['knowledge']['total']} 条")
        total = data.get('total_items', data.get('total_content', 0))
        print(f"   📦 总计: {total} 项")
    except Exception as e:
        print(f"❌ 失败: {e}")
        import traceback
        traceback.print_exc()
        all_ok = False
    
    # 2. 测试搜索功能
    test_queries = [
        ("PID", ["textbook", "case", "knowledge"]),
        ("水箱", ["textbook", "case"]),
        ("考研", ["textbook"]),
        ("控制系统", ["textbook", "case", "knowledge"])
    ]
    
    for query, types in test_queries:
        print_section(f"[搜索] '{query}' (类型: {', '.join(types)})")
        try:
            params = {
                "query": query,
                "types": ",".join(types),
                "limit": 10
            }
            response = requests.get(f"{BASE_URL}/api/search/", params=params)
            data = response.json()
            
            if data.get('success', False):
                print(f"✅ 找到 {data['total_results']} 个结果")
                by_type = data['results_by_type']
                if by_type.get('textbook'):
                    print(f"   📖 教材: {by_type['textbook']}")
                if by_type.get('case'):
                    print(f"   💻 案例: {by_type['case']}")
                if by_type.get('knowledge'):
                    print(f"   🧠 知识库: {by_type['knowledge']}")
                
                # 显示前3个结果
                if data['results']:
                    print("   前3个结果:")
                    for i, r in enumerate(data['results'][:3], 1):
                        print(f"     {i}. [{r['type']}] {r['title']} (相关度: {r['relevance_score']*100:.0f}%)")
            else:
                print(f"❌ 搜索失败")
                all_ok = False
        except Exception as e:
            print(f"❌ 失败: {e}")
            all_ok = False
    
    return all_ok

def test_case_metadata():
    """测试案例元数据"""
    print_header("💻 测试案例元数据增强")
    
    try:
        response = requests.get(f"{BASE_URL}/api/cases")
        data = response.json()
        
        # API可能返回数组或对象
        books = data if isinstance(data, list) else data.get('books', [])
        
        if books and len(books) > 0:
            cases = books[0].get('cases', [])[:3]  # 取前3个案例
            print(f"✅ 获取案例数据成功")
            
            for case in cases:
                print(f"\n  📋 {case.get('title', 'Unknown')}")
                if case.get('difficulty'):
                    print(f"     难度: {case['difficulty']}")
                if case.get('estimated_time_minutes'):
                    print(f"     预计时间: {case['estimated_time_minutes']} 分钟")
                if case.get('control_methods'):
                    print(f"     控制方法: {', '.join(case['control_methods'])}")
            
            return True
        else:
            print("❌ 获取案例数据失败")
            return False
    except Exception as e:
        print(f"❌ 失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print_header("🧪 CHS-Books 新功能完整测试")
    
    print(f"📡 目标服务器: {BASE_URL}")
    print(f"⏰ 测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 等待服务器启动
    print("\n⏳ 等待服务器就绪...")
    max_retries = 10
    for i in range(max_retries):
        try:
            response = requests.get(BASE_URL, timeout=2)
            if response.status_code == 200:
                print("✅ 服务器已就绪\n")
                break
        except:
            pass
        time.sleep(1)
        print(f"   重试 {i+1}/{max_retries}...")
    else:
        print("❌ 服务器未响应，请检查服务是否已启动")
        return
    
    results = {}
    
    # 运行测试
    results['frontend'] = test_frontend_pages()
    results['textbook_api'] = test_textbook_api()
    results['search_api'] = test_search_api()
    results['case_metadata'] = test_case_metadata()
    
    # 总结
    print_header("📊 测试总结")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {name}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！系统运行正常。")
    else:
        print("\n⚠️ 部分测试失败，请检查日志。")

if __name__ == "__main__":
    main()

