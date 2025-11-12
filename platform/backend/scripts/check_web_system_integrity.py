#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web系统完整性检查
确保所有书稿、案例、章节都能在Web系统中正确打开和运行
"""
import sys
import io
if sys.platform == 'win32' and hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import requests
import json
from pathlib import Path
from datetime import datetime

BASE_URL = "http://localhost:8000"

def print_header(text):
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80 + "\n")

def print_section(text):
    print(f"\n{text}")
    print("-"*60)

class WebSystemChecker:
    def __init__(self):
        self.issues = []
        self.checks_passed = 0
        self.checks_failed = 0
        
    def add_issue(self, category, item, problem):
        self.issues.append({
            "category": category,
            "item": item,
            "problem": problem
        })
        self.checks_failed += 1
    
    def add_success(self):
        self.checks_passed += 1

def check_1_server_availability():
    """检查1：服务器可用性"""
    print_header("✅ 检查1：服务器可用性")
    
    try:
        response = requests.get(BASE_URL, timeout=5)
        if response.status_code == 200:
            print("✅ 服务器运行正常")
            print(f"   状态码: {response.status_code}")
            return True
        else:
            print(f"❌ 服务器响应异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法连接到服务器: {e}")
        return False

def check_2_frontend_pages():
    """检查2：前端页面可访问性"""
    print_header("✅ 检查2：前端页面可访问性")
    
    pages = [
        ("/", "主页"),
        ("/unified.html", "统一平台"),
        ("/textbooks.html", "教材阅读器"),
        ("/search.html", "搜索页面"),
        ("/ide", "IDE页面")
    ]
    
    results = []
    for path, name in pages:
        try:
            response = requests.get(f"{BASE_URL}{path}", timeout=5)
            status = "✅" if response.status_code == 200 else "❌"
            print(f"{status} {name}: {path} (状态码: {response.status_code})")
            results.append(response.status_code == 200)
        except Exception as e:
            print(f"❌ {name}: {path} - 错误: {e}")
            results.append(False)
    
    return all(results)

def check_3_textbook_system():
    """检查3：教材系统完整性"""
    print_header("✅ 检查3：教材系统完整性")
    
    checker = WebSystemChecker()
    
    # 3.1 教材列表API
    print_section("[3.1] 教材列表API")
    try:
        response = requests.get(f"{BASE_URL}/api/textbooks/")
        data = response.json()
        
        if isinstance(data, list):
            textbooks = data
        else:
            textbooks = data.get('textbooks', [])
        
        if textbooks:
            print(f"✅ 成功获取 {len(textbooks)} 本教材")
            checker.add_success()
            
            # 3.2 检查每本教材的详情
            print_section("[3.2] 教材详情检查（抽样前5本）")
            for i, textbook in enumerate(textbooks[:5], 1):
                textbook_id = textbook.get('id')
                title = textbook.get('title', 'Unknown')
                
                try:
                    detail_response = requests.get(f"{BASE_URL}/api/textbooks/{textbook_id}", timeout=5)
                    if detail_response.status_code == 200:
                        print(f"  {i}. ✅ {title}")
                        checker.add_success()
                    else:
                        print(f"  {i}. ❌ {title} - HTTP {detail_response.status_code}")
                        checker.add_issue("textbook_detail", title, f"HTTP {detail_response.status_code}")
                except Exception as e:
                    print(f"  {i}. ❌ {title} - 错误: {e}")
                    checker.add_issue("textbook_detail", title, str(e))
            
            # 3.3 检查章节列表
            print_section("[3.3] 章节列表检查（抽样第1本）")
            first_textbook = textbooks[0]
            textbook_id = first_textbook.get('id')
            title = first_textbook.get('title', 'Unknown')
            
            try:
                chapters_response = requests.get(f"{BASE_URL}/api/textbooks/{textbook_id}/chapters", timeout=5)
                if chapters_response.status_code == 200:
                    chapters_data = chapters_response.json()
                    
                    if isinstance(chapters_data, list):
                        chapters = chapters_data
                    else:
                        chapters = chapters_data.get('chapters', [])
                    
                    print(f"✅ {title} - {len(chapters)} 个章节")
                    checker.add_success()
                    
                    # 3.4 检查章节内容（抽样前3章）
                    print_section("[3.4] 章节内容检查（前3章）")
                    for i, chapter in enumerate(chapters[:3], 1):
                        chapter_id = chapter.get('id')
                        chapter_title = chapter.get('title', 'Unknown')
                        
                        try:
                            content_response = requests.get(f"{BASE_URL}/api/textbooks/chapter/{chapter_id}", timeout=5)
                            if content_response.status_code == 200:
                                content_data = content_response.json()
                                chapter_info = content_data.get('chapter', {})
                                content = chapter_info.get('content', '')
                                
                                if content:
                                    print(f"  {i}. ✅ [{chapter.get('chapter_number')}] {chapter_title} ({len(content)} 字符)")
                                    checker.add_success()
                                else:
                                    print(f"  {i}. ⚠️ [{chapter.get('chapter_number')}] {chapter_title} - 内容为空")
                                    checker.add_issue("chapter_content", chapter_title, "内容为空")
                            else:
                                print(f"  {i}. ❌ {chapter_title} - HTTP {content_response.status_code}")
                                checker.add_issue("chapter_content", chapter_title, f"HTTP {content_response.status_code}")
                        except Exception as e:
                            print(f"  {i}. ❌ {chapter_title} - 错误: {e}")
                            checker.add_issue("chapter_content", chapter_title, str(e))
                else:
                    print(f"❌ 无法获取章节列表 - HTTP {chapters_response.status_code}")
                    checker.add_issue("chapters_list", title, f"HTTP {chapters_response.status_code}")
            except Exception as e:
                print(f"❌ 章节列表获取失败: {e}")
                checker.add_issue("chapters_list", title, str(e))
        else:
            print("❌ 教材列表为空")
            checker.add_issue("textbooks_list", "all", "列表为空")
    except Exception as e:
        print(f"❌ 教材API调用失败: {e}")
        checker.add_issue("textbooks_api", "api", str(e))
    
    return checker

def check_4_case_system():
    """检查4：案例系统完整性"""
    print_header("✅ 检查4：案例系统完整性")
    
    checker = WebSystemChecker()
    
    # 4.1 案例列表API
    print_section("[4.1] 案例列表API")
    try:
        response = requests.get(f"{BASE_URL}/api/cases", timeout=10)
        cases = response.json()
        
        if isinstance(cases, list) and len(cases) > 0:
            print(f"✅ 成功获取 {len(cases)} 个案例")
            checker.add_success()
            
            # 4.2 检查案例详情（抽样前5个）
            print_section("[4.2] 案例详情检查（前5个）")
            for i, case in enumerate(cases[:5], 1):
                case_id = case.get('id', 'unknown')
                title = case.get('title', case.get('name', 'Unknown'))
                
                try:
                    detail_response = requests.get(f"{BASE_URL}/api/cases/{case_id}", timeout=5)
                    if detail_response.status_code == 200:
                        case_data = detail_response.json()
                        readme = case_data.get('readme', '')
                        
                        if readme:
                            print(f"  {i}. ✅ {title} (README: {len(readme)} 字符)")
                            checker.add_success()
                        else:
                            print(f"  {i}. ⚠️ {title} - README为空")
                            checker.add_issue("case_readme", title, "README为空")
                    else:
                        print(f"  {i}. ❌ {title} - HTTP {detail_response.status_code}")
                        checker.add_issue("case_detail", title, f"HTTP {detail_response.status_code}")
                except Exception as e:
                    print(f"  {i}. ❌ {title} - 错误: {e}")
                    checker.add_issue("case_detail", title, str(e))
            
            # 4.3 检查案例文件（抽样第1个）
            print_section("[4.3] 案例文件检查（第1个案例）")
            first_case = cases[0]
            case_id = first_case.get('id', 'unknown')
            title = first_case.get('title', first_case.get('name', 'Unknown'))
            
            try:
                # 检查文件列表
                files_response = requests.get(f"{BASE_URL}/api/files/{case_id}", timeout=5)
                if files_response.status_code == 200:
                    files_list = files_response.json()
                    
                    # files_list 是一个数组
                    if isinstance(files_list, list):
                        main_py_exists = any(f.get('name') == 'main.py' for f in files_list)
                        
                        if main_py_exists:
                            # 获取main.py内容
                            content_response = requests.get(
                                f"{BASE_URL}/api/file_content",
                                params={"case_id": case_id, "file_path": "main.py"},
                                timeout=5
                            )
                            if content_response.status_code == 200:
                                content_data = content_response.json()
                                main_py = content_data.get('content', '')
                                print(f"✅ main.py 存在 ({len(main_py)} 字符)")
                                checker.add_success()
                            else:
                                print(f"⚠️ main.py 无法读取")
                                checker.add_issue("case_files", "main.py", "无法读取内容")
                        else:
                            print(f"⚠️ main.py 不存在")
                            checker.add_issue("case_files", "main.py", "文件不存在")
                    else:
                        print(f"⚠️ 文件列表格式错误")
                        checker.add_issue("case_files", title, "API返回格式错误")
                else:
                    print(f"❌ 无法获取案例文件 - HTTP {files_response.status_code}")
                    checker.add_issue("case_files", title, f"HTTP {files_response.status_code}")
            except Exception as e:
                print(f"❌ 案例文件检查失败: {e}")
                checker.add_issue("case_files", title, str(e))
        else:
            print(f"❌ 案例列表为空或格式错误")
            checker.add_issue("cases_list", "all", "列表为空或格式错误")
    except Exception as e:
        print(f"❌ 案例API调用失败: {e}")
        checker.add_issue("cases_api", "api", str(e))
    
    return checker

def check_5_search_system():
    """检查5：搜索系统功能"""
    print_header("✅ 检查5：搜索系统功能")
    
    checker = WebSystemChecker()
    
    # 5.1 搜索统计API
    print_section("[5.1] 搜索统计API")
    try:
        response = requests.get(f"{BASE_URL}/api/search/stats", timeout=5)
        stats = response.json()
        
        print(f"✅ 搜索统计获取成功")
        print(f"   教材: {stats.get('textbooks', {}).get('total', 0)} 本")
        print(f"   案例: {stats.get('cases', {}).get('total', 0)} 个")
        print(f"   知识库: {stats.get('knowledge', {}).get('total', 0)} 条")
        checker.add_success()
    except Exception as e:
        print(f"❌ 搜索统计API失败: {e}")
        checker.add_issue("search_stats", "api", str(e))
    
    # 5.2 搜索功能测试
    print_section("[5.2] 搜索功能测试")
    test_queries = ["PID", "水箱", "控制"]
    
    for query in test_queries:
        try:
            response = requests.get(
                f"{BASE_URL}/api/search/",
                params={"query": query, "types": "textbook,case,knowledge", "limit": 5},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                total = data.get('total_results', 0)
                print(f"✅ 搜索 '{query}': {total} 个结果")
                checker.add_success()
            else:
                print(f"❌ 搜索 '{query}' 失败 - HTTP {response.status_code}")
                checker.add_issue("search_query", query, f"HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ 搜索 '{query}' 错误: {e}")
            checker.add_issue("search_query", query, str(e))
    
    return checker

def generate_final_report(textbook_checker, case_checker, search_checker):
    """生成最终报告"""
    print_header("📋 Web系统完整性检查报告")
    
    total_passed = (textbook_checker.checks_passed + 
                   case_checker.checks_passed + 
                   search_checker.checks_passed)
    total_failed = (textbook_checker.checks_failed + 
                   case_checker.checks_failed + 
                   search_checker.checks_failed)
    total_checks = total_passed + total_failed
    
    print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"总检查项: {total_checks}")
    print(f"通过: {total_passed} ({total_passed/total_checks*100:.1f}%)" if total_checks > 0 else "通过: 0")
    print(f"失败: {total_failed}")
    
    all_issues = (textbook_checker.issues + 
                 case_checker.issues + 
                 search_checker.issues)
    
    if all_issues:
        print(f"\n⚠️ 发现 {len(all_issues)} 个问题:")
        
        # 按类别分组
        issues_by_category = {}
        for issue in all_issues:
            category = issue['category']
            if category not in issues_by_category:
                issues_by_category[category] = []
            issues_by_category[category].append(issue)
        
        for category, issues in issues_by_category.items():
            print(f"\n  [{category}] {len(issues)} 个问题:")
            for issue in issues[:5]:  # 只显示前5个
                print(f"    - {issue['item']}: {issue['problem']}")
            if len(issues) > 5:
                print(f"    ... 还有 {len(issues)-5} 个问题")
    
    if total_passed == total_checks and total_checks > 0:
        print("\n✅ 所有检查通过！Web系统运行正常。")
        return True
    elif total_failed == 0:
        print("\n⚠️ 未进行任何检查，请确认服务器是否运行。")
        return False
    else:
        print(f"\n⚠️ 有 {total_failed} 项检查未通过，需要修复。")
        return False

def main():
    print_header("🔍 CHS-Books Web系统完整性检查")
    print(f"测试服务器: {BASE_URL}")
    print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 检查1：服务器
    if not check_1_server_availability():
        print("\n❌ 服务器不可用，无法继续检查")
        print("\n请先启动服务器: python full_server.py")
        return
    
    # 检查2：前端页面
    check_2_frontend_pages()
    
    # 检查3：教材系统
    textbook_checker = check_3_textbook_system()
    
    # 检查4：案例系统
    case_checker = check_4_case_system()
    
    # 检查5：搜索系统
    search_checker = check_5_search_system()
    
    # 生成最终报告
    success = generate_final_report(textbook_checker, case_checker, search_checker)
    
    print_header("✅ 检查完成")
    
    if success:
        print("\n🎉 Web系统运行完美！所有功能正常。")
    else:
        print("\n📝 建议的修复措施:")
        print("  1. 检查数据库文件是否存在")
        print("  2. 运行数据导入脚本")
        print("  3. 检查API路由配置")
        print("  4. 查看服务器日志")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ 检查被用户中断")
    except Exception as e:
        print(f"\n\n❌ 检查过程发生错误: {e}")
        import traceback
        traceback.print_exc()

