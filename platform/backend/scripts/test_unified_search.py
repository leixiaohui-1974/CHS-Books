#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试统一搜索API功能
"""

import sys
import io
from pathlib import Path
import requests
import json

# 设置UTF-8输出
if sys.platform == 'win32' and hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE_URL = "http://localhost:8000"


def test_search_api():
    """测试统一搜索API"""
    print("\n" + "="*80)
    print("  🔍 测试统一搜索API")
    print("="*80 + "\n")
    
    # 测试用例
    test_queries = [
        {
            "query": "PID控制",
            "description": "搜索PID控制相关内容"
        },
        {
            "query": "水箱",
            "description": "搜索水箱系统相关内容"
        },
        {
            "query": "明渠流",
            "description": "搜索明渠流相关内容"
        },
        {
            "query": "考研",
            "description": "搜索考研相关内容"
        }
    ]
    
    for i, test_case in enumerate(test_queries, 1):
        print(f"\n[测试 {i}] {test_case['description']}")
        print(f"查询词: {test_case['query']}")
        print("-" * 60)
        
        try:
            response = requests.get(
                f"{BASE_URL}/api/search/",
                params={"query": test_case['query'], "limit": 5}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 状态: 成功")
                print(f"📊 总结果数: {data['total_results']}")
                print(f"📦 分类统计: {data['results_by_type']}")
                
                if data['results']:
                    print(f"\n前5个结果:")
                    for j, result in enumerate(data['results'][:5], 1):
                        print(f"\n  {j}. [{result['type']}] {result['title']}")
                        print(f"     来源: {result['source']}")
                        print(f"     相关度: {result['relevance_score']:.2f}")
                        if result.get('preview'):
                            preview = result['preview'][:100] + "..." if len(result['preview']) > 100 else result['preview']
                            print(f"     预览: {preview}")
                else:
                    print("⚠️  未找到相关结果")
            else:
                print(f"❌ 错误: HTTP {response.status_code}")
                print(f"   {response.text}")
        
        except requests.exceptions.ConnectionError:
            print(f"❌ 错误: 无法连接到服务器 {BASE_URL}")
            print(f"   请确保服务器正在运行")
            return False
        except Exception as e:
            print(f"❌ 错误: {e}")
            return False
    
    print("\n" + "="*80)
    print("  ✅ 统一搜索API测试完成")
    print("="*80 + "\n")
    return True


def test_search_stats():
    """测试搜索统计API"""
    print("\n" + "="*80)
    print("  📊 测试搜索统计API")
    print("="*80 + "\n")
    
    try:
        response = requests.get(f"{BASE_URL}/api/search/stats")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 统计信息获取成功\n")
            
            print(f"📚 教材统计:")
            print(f"   总数: {data['textbooks']['total']} 本")
            print(f"   章节: {data['textbooks']['chapters']} 个")
            
            print(f"\n📋 案例统计:")
            print(f"   总数: {data['cases']['total']} 个")
            
            print(f"\n🧠 知识库统计:")
            print(f"   总数: {data['knowledge']['total']} 条")
            print(f"   分类: {data['knowledge']['categories']} 个")
            
            print(f"\n📦 总内容数: {data['total_content']}")
            
            return True
        else:
            print(f"❌ 错误: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def test_search_suggestions():
    """测试搜索建议API"""
    print("\n" + "="*80)
    print("  💡 测试搜索建议API")
    print("="*80 + "\n")
    
    test_queries = ["PID", "水", "控制"]
    
    for query in test_queries:
        try:
            response = requests.get(
                f"{BASE_URL}/api/search/suggestions",
                params={"query": query, "limit": 5}
            )
            
            if response.status_code == 200:
                data = response.json()
                suggestions = data.get('suggestions', [])
                print(f"查询 '{query}' 的建议:")
                if suggestions:
                    for suggestion in suggestions:
                        print(f"  - {suggestion}")
                else:
                    print(f"  (无建议)")
                print()
            else:
                print(f"❌ 错误: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 错误: {e}")
            return False
    
    return True


def main():
    print("\n" + "="*80)
    print("  🧪 统一搜索API 完整测试")
    print("="*80)
    
    # 测试统计信息
    if not test_search_stats():
        print("\n❌ 统计API测试失败")
        return
    
    # 测试搜索功能
    if not test_search_api():
        print("\n❌ 搜索API测试失败")
        return
    
    # 测试搜索建议
    if not test_search_suggestions():
        print("\n❌ 搜索建议API测试失败")
        return
    
    print("\n" + "="*80)
    print("  ✅ 所有测试通过！")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()

