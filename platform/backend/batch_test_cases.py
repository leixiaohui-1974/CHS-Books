#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
批量测试案例脚本
自动测试指定书籍的所有案例
"""
import sys
import io
import requests
import json
import time
from datetime import datetime

# 修复编码问题
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:8000"

def test_case(book_slug, case_slug, user_id="batch_test_user"):
    """测试单个案例"""
    try:
        print(f"\n{'='*80}")
        print(f"📝 测试案例: {case_slug}")
        print(f"{'='*80}")
        
        url = f"{BASE_URL}/api/v1/execute"
        payload = {
            "user_id": user_id,
            "book_slug": book_slug,
            "case_slug": case_slug,
            "script_path": "main.py"
        }
        
        start_time = time.time()
        response = requests.post(url, json=payload, timeout=300)  # 5分钟超时
        duration = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                result = data.get("result", {})
                return_code = result.get("return_code", -1)
                output = result.get("output", "")
                
                if return_code == 0:
                    print(f"✅ 案例 {case_slug} 测试成功！")
                    print(f"⏱️  执行时间: {duration:.2f}秒")
                    return {
                        "case": case_slug,
                        "status": "success",
                        "duration": duration,
                        "return_code": return_code,
                        "output_length": len(output)
                    }
                else:
                    print(f"❌ 案例 {case_slug} 测试失败 (返回码: {return_code})")
                    print(f"输出: {output[:500]}")  # 只打印前500字符
                    return {
                        "case": case_slug,
                        "status": "failed",
                        "duration": duration,
                        "return_code": return_code,
                        "error": output[:500]
                    }
            else:
                error_msg = data.get("message", "Unknown error")
                print(f"❌ 案例 {case_slug} 测试失败: {error_msg}")
                return {
                    "case": case_slug,
                    "status": "failed",
                    "duration": duration,
                    "error": error_msg
                }
        else:
            print(f"❌ 请求失败 (HTTP {response.status_code})")
            return {
                "case": case_slug,
                "status": "failed",
                "duration": duration,
                "error": f"HTTP {response.status_code}"
            }
            
    except requests.Timeout:
        print(f"⏱️  案例 {case_slug} 超时（>5分钟）")
        return {
            "case": case_slug,
            "status": "timeout",
            "error": "Timeout after 5 minutes"
        }
    except Exception as e:
        print(f"❌ 案例 {case_slug} 出错: {e}")
        return {
            "case": case_slug,
            "status": "error",
            "error": str(e)
        }

def get_book_cases(book_slug):
    """获取书籍的所有案例"""
    try:
        url = f"{BASE_URL}/api/v1/books/{book_slug}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                book = data.get("book", {})
                cases = book.get("cases", [])
                print(f"\n📚 书籍: {book.get('title')}")
                print(f"📝 共有 {len(cases)} 个案例")
                return [case["id"] for case in cases]  # 使用id而不是slug
        
        print(f"❌ 无法获取书籍案例列表")
        return []
    except Exception as e:
        print(f"❌ 获取案例列表出错: {e}")
        return []

def batch_test_book(book_slug, case_range=None):
    """批量测试书籍的所有案例"""
    print(f"\n{'#'*80}")
    print(f"# 批量测试开始")
    print(f"# 书籍: {book_slug}")
    print(f"# 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'#'*80}\n")
    
    # 获取所有案例
    case_slugs = get_book_cases(book_slug)
    if not case_slugs:
        print("❌ 没有找到案例")
        return
    
    # 如果指定了范围，只测试部分案例
    if case_range:
        start, end = case_range
        case_slugs = case_slugs[start:end]
        print(f"📌 只测试案例 {start+1}-{end}")
    
    # 测试所有案例
    results = []
    start_time = time.time()
    
    for i, case_slug in enumerate(case_slugs, 1):
        print(f"\n[{i}/{len(case_slugs)}] ", end="")
        result = test_case(book_slug, case_slug)
        results.append(result)
        
        # 短暂延迟，避免过载
        time.sleep(0.5)
    
    total_duration = time.time() - start_time
    
    # 统计结果
    print(f"\n{'#'*80}")
    print(f"# 批量测试完成")
    print(f"{'#'*80}\n")
    
    success_count = sum(1 for r in results if r["status"] == "success")
    failed_count = sum(1 for r in results if r["status"] == "failed")
    error_count = sum(1 for r in results if r["status"] in ["error", "timeout"])
    
    print(f"📊 测试统计:")
    print(f"   总案例数: {len(results)}")
    print(f"   ✅ 成功: {success_count}")
    print(f"   ❌ 失败: {failed_count}")
    print(f"   ⚠️ 错误/超时: {error_count}")
    print(f"   成功率: {success_count/len(results)*100:.1f}%")
    print(f"   总耗时: {total_duration:.2f}秒 ({total_duration/60:.1f}分钟)")
    
    # 保存结果到文件
    report_file = f"test_report_{book_slug}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump({
            "book": book_slug,
            "timestamp": datetime.now().isoformat(),
            "total_cases": len(results),
            "success": success_count,
            "failed": failed_count,
            "errors": error_count,
            "success_rate": success_count/len(results)*100,
            "total_duration": total_duration,
            "results": results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 详细报告已保存到: {report_file}")
    
    return results

if __name__ == "__main__":
    # 测试水系统控制论的所有案例
    batch_test_book("water-system-control")

