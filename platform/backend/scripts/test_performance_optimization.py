#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CHS-Books 性能优化验证测试
测试图片懒加载和缓存管理器的功能
"""

import sys
import io
import time
import json
import requests
from pathlib import Path
from datetime import datetime

# 强制UTF-8输出
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 配置
BASE_URL = "http://localhost:8000"
TEST_RESULTS_FILE = Path(__file__).parent / "performance_test_results.json"

class Colors:
    """终端颜色"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(title):
    """打印标题"""
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*60}")
    print(f"{title:^60}")
    print(f"{'='*60}{Colors.END}\n")

def print_success(msg):
    """打印成功消息"""
    print(f"{Colors.GREEN}✓{Colors.END} {msg}")

def print_error(msg):
    """打印错误消息"""
    print(f"{Colors.RED}✗{Colors.END} {msg}")

def print_warning(msg):
    """打印警告消息"""
    print(f"{Colors.YELLOW}⚠{Colors.END} {msg}")

def print_info(msg):
    """打印信息"""
    print(f"{Colors.BLUE}ℹ{Colors.END} {msg}")

def test_static_files_availability():
    """测试性能优化文件是否可访问"""
    print_header("测试1: 性能优化文件可用性")
    
    files = [
        "/static/lazy-load.js",
        "/static/lazy-load.css",
        "/static/cache-manager.js",
        "/static/common-ui-utils.js",
        "/static/common-ui-styles.css",
        "/static/responsive-layout.css"
    ]
    
    results = {"total": len(files), "success": 0, "failed": 0, "files": {}}
    
    for file_path in files:
        url = f"{BASE_URL}{file_path}"
        try:
            start = time.time()
            response = requests.get(url, timeout=5)
            elapsed = time.time() - start
            
            if response.status_code == 200:
                size_kb = len(response.content) / 1024
                print_success(f"{file_path} - {response.status_code} ({size_kb:.2f} KB, {elapsed:.3f}s)")
                results["success"] += 1
                results["files"][file_path] = {
                    "status": "success",
                    "size_kb": round(size_kb, 2),
                    "time_s": round(elapsed, 3)
                }
            else:
                print_error(f"{file_path} - {response.status_code}")
                results["failed"] += 1
                results["files"][file_path] = {
                    "status": "failed",
                    "code": response.status_code
                }
        except Exception as e:
            print_error(f"{file_path} - 错误: {str(e)}")
            results["failed"] += 1
            results["files"][file_path] = {
                "status": "error",
                "error": str(e)
            }
    
    print(f"\n总计: {results['success']}/{results['total']} 成功")
    return results

def test_page_integration():
    """测试核心页面是否集成了性能优化"""
    print_header("测试2: 核心页面集成检查")
    
    pages = {
        "/": "index.html",
        "/ide.html": "ide.html",
        "/textbooks.html": "textbooks.html",
        "/search.html": "search.html"
    }
    
    results = {"total": len(pages), "success": 0, "failed": 0, "pages": {}}
    
    # 检查点
    checkpoints = {
        "lazy-load.js": "图片懒加载",
        "cache-manager.js": "缓存管理器",
        "common-ui-utils.js": "UI工具库",
        "responsive-layout.css": "响应式布局"
    }
    
    for url_path, page_name in pages.items():
        url = f"{BASE_URL}{url_path}"
        print(f"\n检查 {page_name}...")
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                content = response.text
                page_results = {}
                
                for checkpoint, desc in checkpoints.items():
                    if checkpoint in content:
                        print_success(f"  {desc}: 已集成")
                        page_results[desc] = True
                    else:
                        print_warning(f"  {desc}: 未集成")
                        page_results[desc] = False
                
                integration_rate = sum(page_results.values()) / len(page_results) * 100
                results["pages"][page_name] = {
                    "status": "success",
                    "integration_rate": round(integration_rate, 1),
                    "details": page_results
                }
                
                if integration_rate >= 75:
                    results["success"] += 1
                    print_info(f"  集成率: {integration_rate:.1f}%")
                else:
                    results["failed"] += 1
                    print_warning(f"  集成率偏低: {integration_rate:.1f}%")
            else:
                print_error(f"  HTTP {response.status_code}")
                results["failed"] += 1
                results["pages"][page_name] = {
                    "status": "failed",
                    "code": response.status_code
                }
        except Exception as e:
            print_error(f"  错误: {str(e)}")
            results["failed"] += 1
            results["pages"][page_name] = {
                "status": "error",
                "error": str(e)
            }
    
    print(f"\n总计: {results['success']}/{results['total']} 页面完整集成")
    return results

def test_api_response_time():
    """测试API响应时间（为缓存做基准）"""
    print_header("测试3: API响应时间基准测试")
    
    endpoints = [
        "/api/books",
        "/api/textbooks",
        "/api/search/stats"
    ]
    
    results = {"endpoints": {}}
    
    for endpoint in endpoints:
        url = f"{BASE_URL}{endpoint}"
        print(f"\n测试 {endpoint}...")
        
        times = []
        for i in range(5):
            try:
                start = time.time()
                response = requests.get(url, timeout=10)
                elapsed = (time.time() - start) * 1000  # 毫秒
                
                if response.status_code == 200:
                    times.append(elapsed)
                    print_info(f"  第{i+1}次: {elapsed:.2f}ms")
                else:
                    print_warning(f"  第{i+1}次: HTTP {response.status_code}")
            except Exception as e:
                print_error(f"  第{i+1}次: {str(e)}")
        
        if times:
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            
            print_success(f"  平均: {avg_time:.2f}ms, 最快: {min_time:.2f}ms, 最慢: {max_time:.2f}ms")
            
            results["endpoints"][endpoint] = {
                "average_ms": round(avg_time, 2),
                "min_ms": round(min_time, 2),
                "max_ms": round(max_time, 2),
                "samples": len(times)
            }
            
            # 评估
            if avg_time < 100:
                print_success(f"  评估: 优秀 (< 100ms)")
            elif avg_time < 300:
                print_info(f"  评估: 良好 (< 300ms)")
            elif avg_time < 500:
                print_warning(f"  评估: 一般 (< 500ms)")
            else:
                print_warning(f"  评估: 较慢 (>= 500ms)")
    
    return results

def test_concurrent_requests():
    """测试并发请求性能"""
    print_header("测试4: 并发请求压力测试")
    
    import concurrent.futures
    
    url = f"{BASE_URL}/api/books"
    concurrent_levels = [5, 10, 20]
    
    results = {"levels": {}}
    
    def make_request():
        try:
            start = time.time()
            response = requests.get(url, timeout=10)
            elapsed = time.time() - start
            return {
                "success": response.status_code == 200,
                "time": elapsed,
                "status_code": response.status_code
            }
        except Exception as e:
            return {
                "success": False,
                "time": 0,
                "error": str(e)
            }
    
    for level in concurrent_levels:
        print(f"\n并发级别: {level}")
        
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=level) as executor:
            futures = [executor.submit(make_request) for _ in range(level)]
            request_results = [f.result() for f in concurrent.futures.as_completed(futures)]
        total_time = time.time() - start_time
        
        success_count = sum(1 for r in request_results if r.get("success"))
        avg_response_time = sum(r.get("time", 0) for r in request_results if r.get("success")) / max(success_count, 1)
        
        print_info(f"  总耗时: {total_time:.2f}s")
        print_info(f"  成功率: {success_count}/{level} ({success_count/level*100:.1f}%)")
        print_info(f"  平均响应: {avg_response_time*1000:.2f}ms")
        
        results["levels"][level] = {
            "total_time_s": round(total_time, 2),
            "success_count": success_count,
            "total_count": level,
            "success_rate": round(success_count/level*100, 1),
            "avg_response_ms": round(avg_response_time*1000, 2)
        }
        
        if success_count == level and avg_response_time < 1:
            print_success(f"  评估: 优秀")
        elif success_count >= level * 0.9:
            print_info(f"  评估: 良好")
        else:
            print_warning(f"  评估: 需要优化")
    
    return results

def test_large_payload_handling():
    """测试大数据量处理"""
    print_header("测试5: 大数据量处理能力")
    
    # 测试教材章节列表（大数据量）
    url = f"{BASE_URL}/api/textbooks"
    
    try:
        print("正在请求教材数据...")
        start = time.time()
        response = requests.get(url, timeout=30)
        elapsed = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            
            # 分析数据
            textbooks = data.get("textbooks", data) if isinstance(data, dict) else data
            if isinstance(textbooks, list):
                total_textbooks = len(textbooks)
                total_chapters = sum(len(t.get("chapters", [])) for t in textbooks)
                payload_size_kb = len(response.content) / 1024
                
                print_success(f"数据加载成功")
                print_info(f"  教材数: {total_textbooks}")
                print_info(f"  章节数: {total_chapters}")
                print_info(f"  数据大小: {payload_size_kb:.2f} KB")
                print_info(f"  加载时间: {elapsed:.2f}s")
                print_info(f"  吞吐量: {payload_size_kb/elapsed:.2f} KB/s")
                
                # 评估
                if elapsed < 2 and payload_size_kb < 1000:
                    print_success(f"评估: 优秀 - 适合缓存")
                elif elapsed < 5:
                    print_info(f"评估: 良好 - 建议缓存")
                else:
                    print_warning(f"评估: 较慢 - 强烈建议缓存")
                
                return {
                    "status": "success",
                    "total_textbooks": total_textbooks,
                    "total_chapters": total_chapters,
                    "payload_size_kb": round(payload_size_kb, 2),
                    "load_time_s": round(elapsed, 2),
                    "throughput_kbps": round(payload_size_kb/elapsed, 2)
                }
        else:
            print_error(f"HTTP {response.status_code}")
            return {"status": "failed", "code": response.status_code}
            
    except Exception as e:
        print_error(f"错误: {str(e)}")
        return {"status": "error", "error": str(e)}

def generate_summary(all_results):
    """生成测试摘要"""
    print_header("测试总结")
    
    # 文件可用性
    file_test = all_results.get("file_availability", {})
    file_success_rate = file_test.get("success", 0) / max(file_test.get("total", 1), 1) * 100
    
    # 页面集成
    page_test = all_results.get("page_integration", {})
    page_success_rate = page_test.get("success", 0) / max(page_test.get("total", 1), 1) * 100
    
    # API性能
    api_test = all_results.get("api_performance", {})
    endpoints = api_test.get("endpoints", {})
    if endpoints:
        avg_api_time = sum(e.get("average_ms", 0) for e in endpoints.values()) / len(endpoints)
    else:
        avg_api_time = 0
    
    # 并发测试
    concurrent_test = all_results.get("concurrent_test", {})
    levels = concurrent_test.get("levels", {})
    if levels:
        avg_success_rate = sum(l.get("success_rate", 0) for l in levels.values()) / len(levels)
    else:
        avg_success_rate = 0
    
    print(f"文件可用性:   {file_success_rate:.1f}% ({file_test.get('success', 0)}/{file_test.get('total', 0)})")
    print(f"页面集成率:   {page_success_rate:.1f}% ({page_test.get('success', 0)}/{page_test.get('total', 0)})")
    print(f"API平均响应:  {avg_api_time:.2f}ms")
    print(f"并发成功率:   {avg_success_rate:.1f}%")
    
    # 总体评分
    total_score = (file_success_rate + page_success_rate + min(100, 100 - avg_api_time/5) + avg_success_rate) / 4
    
    print(f"\n{Colors.BOLD}总体评分: {total_score:.1f}/100{Colors.END}")
    
    if total_score >= 90:
        print_success("评级: 优秀 ⭐⭐⭐⭐⭐")
    elif total_score >= 80:
        print_info("评级: 良好 ⭐⭐⭐⭐")
    elif total_score >= 70:
        print_warning("评级: 一般 ⭐⭐⭐")
    else:
        print_warning("评级: 需要改进 ⭐⭐")
    
    return {
        "file_success_rate": round(file_success_rate, 1),
        "page_success_rate": round(page_success_rate, 1),
        "avg_api_time_ms": round(avg_api_time, 2),
        "concurrent_success_rate": round(avg_success_rate, 1),
        "total_score": round(total_score, 1)
    }

def main():
    """主函数"""
    print(f"{Colors.BOLD}{Colors.CYAN}")
    print("=" * 60)
    print("  CHS-Books 性能优化验证测试")
    print("=" * 60)
    print(f"{Colors.END}")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"目标服务器: {BASE_URL}")
    
    # 检查服务器
    try:
        response = requests.get(BASE_URL, timeout=5)
        if response.status_code == 200:
            print_success("服务器连接正常\n")
        else:
            print_warning(f"服务器响应异常: {response.status_code}\n")
    except Exception as e:
        print_error(f"无法连接到服务器: {str(e)}")
        print_info("请确保后端服务正在运行: python full_server.py")
        return 1
    
    # 执行测试
    all_results = {
        "timestamp": datetime.now().isoformat(),
        "base_url": BASE_URL
    }
    
    try:
        # 测试1: 文件可用性
        all_results["file_availability"] = test_static_files_availability()
        
        # 测试2: 页面集成
        all_results["page_integration"] = test_page_integration()
        
        # 测试3: API性能
        all_results["api_performance"] = test_api_response_time()
        
        # 测试4: 并发测试
        all_results["concurrent_test"] = test_concurrent_requests()
        
        # 测试5: 大数据处理
        all_results["large_payload"] = test_large_payload_handling()
        
        # 生成总结
        all_results["summary"] = generate_summary(all_results)
        
        # 保存结果
        with open(TEST_RESULTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n{Colors.GREEN}测试结果已保存到: {TEST_RESULTS_FILE}{Colors.END}")
        
        # 返回结果
        total_score = all_results["summary"]["total_score"]
        if total_score >= 80:
            return 0  # 成功
        else:
            return 1  # 需要改进
            
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}测试被用户中断{Colors.END}")
        return 2
    except Exception as e:
        print(f"\n{Colors.RED}测试过程中发生错误: {str(e)}{Colors.END}")
        import traceback
        traceback.print_exc()
        return 3

if __name__ == "__main__":
    sys.exit(main())

