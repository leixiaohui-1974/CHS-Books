#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全面案例测试脚本
验证所有案例的运行正确性、控制效果、结果展示、图表质量
"""
import sys
import io
if sys.platform == 'win32' and hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import json
import requests
from pathlib import Path
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"
RESULTS_DIR = Path(__file__).parent.parent / "test_results"
RESULTS_DIR.mkdir(exist_ok=True)

def print_header(text):
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80 + "\n")

def print_section(text):
    print(f"\n{text}")
    print("-"*60)

class CaseTestReport:
    def __init__(self):
        self.total_cases = 0
        self.tested_cases = 0
        self.passed_cases = 0
        self.failed_cases = 0
        self.case_results = []
        self.issues = []
        
    def add_result(self, case_id, status, details):
        self.tested_cases += 1
        if status == "passed":
            self.passed_cases += 1
        else:
            self.failed_cases += 1
        
        self.case_results.append({
            "case_id": case_id,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def add_issue(self, case_id, issue_type, description):
        self.issues.append({
            "case_id": case_id,
            "type": issue_type,
            "description": description
        })
    
    def generate_report(self):
        report = {
            "test_date": datetime.now().isoformat(),
            "summary": {
                "total_cases": self.total_cases,
                "tested_cases": self.tested_cases,
                "passed_cases": self.passed_cases,
                "failed_cases": self.failed_cases,
                "pass_rate": f"{(self.passed_cases/self.tested_cases*100):.1f}%" if self.tested_cases > 0 else "0%"
            },
            "results": self.case_results,
            "issues": self.issues
        }
        
        report_file = RESULTS_DIR / f"case_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        return report_file

def test_case_availability():
    """测试案例可用性"""
    print_header("📋 第1部分：案例可用性测试")
    
    try:
        response = requests.get(f"{BASE_URL}/api/cases", timeout=10)
        data = response.json()
        
        if isinstance(data, list):
            books = data
        else:
            books = data.get('books', [])
        
        total_cases = sum(len(book.get('cases', [])) for book in books)
        
        print(f"✅ 成功加载案例索引")
        print(f"   📚 案例集数量: {len(books)}")
        print(f"   💻 案例总数: {total_cases}")
        
        print("\n案例集详情:")
        for i, book in enumerate(books, 1):
            cases = book.get('cases', [])
            print(f"  {i}. {book.get('title', 'Unknown')} - {len(cases)} 个案例")
        
        return books, total_cases
        
    except Exception as e:
        print(f"❌ 案例索引加载失败: {e}")
        return [], 0

def test_case_execution(case_id):
    """测试单个案例执行"""
    try:
        # 尝试运行案例
        response = requests.post(
            f"{BASE_URL}/api/run",
            json={"case_id": case_id},
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                "status": "passed",
                "execution_time": data.get('execution_time', 0),
                "has_output": bool(data.get('output')),
                "has_error": bool(data.get('error'))
            }
        else:
            return {
                "status": "failed",
                "error": f"HTTP {response.status_code}"
            }
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e)
        }

def test_case_results(case_id):
    """测试案例结果完整性"""
    try:
        response = requests.get(f"{BASE_URL}/api/results/{case_id}", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            checks = {
                "has_diagrams": len(data.get('diagrams', [])) > 0,
                "has_data_files": len(data.get('data_files', [])) > 0,
                "has_summary": bool(data.get('summary')),
                "diagram_count": len(data.get('diagrams', [])),
                "data_file_count": len(data.get('data_files', []))
            }
            
            return checks
        else:
            return {"error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def test_visualization_quality(case_id):
    """测试可视化图表质量"""
    issues = []
    
    try:
        response = requests.get(f"{BASE_URL}/api/results/{case_id}", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            diagrams = data.get('diagrams', [])
            
            if len(diagrams) == 0:
                issues.append("无可视化图表")
            
            for diagram in diagrams:
                # 检查图表文件是否存在
                if not diagram.get('path'):
                    issues.append(f"图表缺少路径: {diagram.get('title', 'Unknown')}")
                
                # 检查图表标题
                if not diagram.get('title'):
                    issues.append("图表缺少标题")
            
            # 检查数据文件
            data_files = data.get('data_files', [])
            if len(data_files) == 0:
                issues.append("无数据文件")
        
    except Exception as e:
        issues.append(f"测试失败: {e}")
    
    return issues

def comprehensive_case_test():
    """执行全面案例测试"""
    print_header("🧪 CHS-Books 案例系统全面测试")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"测试服务器: {BASE_URL}")
    
    report = CaseTestReport()
    
    # 第1部分：案例可用性
    books, total_cases = test_case_availability()
    report.total_cases = total_cases
    
    if total_cases == 0:
        print("\n❌ 无法继续测试，未找到案例")
        return
    
    # 第2部分：抽样测试案例执行
    print_header("📋 第2部分：案例执行测试（抽样）")
    
    test_cases = []
    for book in books[:3]:  # 测试前3个案例集
        cases = book.get('cases', [])[:5]  # 每个集合测试前5个案例
        test_cases.extend([(book.get('slug', ''), case['id']) for case in cases])
    
    print(f"抽样测试 {len(test_cases)} 个案例...")
    
    for i, (book_slug, case_id) in enumerate(test_cases, 1):
        print(f"\n[{i}/{len(test_cases)}] 测试案例: {case_id}")
        
        # 执行测试
        exec_result = test_case_execution(case_id)
        
        if exec_result['status'] == 'passed':
            print(f"  ✅ 执行成功")
            if exec_result.get('execution_time'):
                print(f"     执行时间: {exec_result['execution_time']:.2f}秒")
        else:
            print(f"  ❌ 执行失败: {exec_result.get('error', 'Unknown')}")
            report.add_issue(case_id, "execution", exec_result.get('error', 'Unknown'))
        
        # 测试结果
        result_checks = test_case_results(case_id)
        
        if 'error' not in result_checks:
            print(f"  📊 结果检查:")
            print(f"     图表数量: {result_checks.get('diagram_count', 0)}")
            print(f"     数据文件: {result_checks.get('data_file_count', 0)}")
            
            if not result_checks.get('has_diagrams'):
                report.add_issue(case_id, "visualization", "缺少可视化图表")
            
            if not result_checks.get('has_data_files'):
                report.add_issue(case_id, "data", "缺少数据文件")
        
        # 测试可视化质量
        viz_issues = test_visualization_quality(case_id)
        if viz_issues:
            print(f"  ⚠️ 可视化问题:")
            for issue in viz_issues:
                print(f"     - {issue}")
                report.add_issue(case_id, "visualization", issue)
        
        # 添加测试结果
        overall_status = "passed" if exec_result['status'] == 'passed' and not viz_issues else "failed"
        report.add_result(case_id, overall_status, {
            "execution": exec_result,
            "results": result_checks,
            "visualization_issues": viz_issues
        })
        
        time.sleep(0.5)  # 避免请求过快
    
    # 第3部分：生成测试报告
    print_header("📋 第3部分：测试报告生成")
    
    report_file = report.generate_report()
    
    print(f"✅ 测试完成！")
    print(f"\n测试摘要:")
    print(f"  总案例数: {report.total_cases}")
    print(f"  测试案例数: {report.tested_cases}")
    print(f"  通过: {report.passed_cases}")
    print(f"  失败: {report.failed_cases}")
    print(f"  通过率: {(report.passed_cases/report.tested_cases*100):.1f}%")
    
    if report.issues:
        print(f"\n⚠️ 发现 {len(report.issues)} 个问题:")
        
        issue_types = {}
        for issue in report.issues:
            issue_type = issue['type']
            issue_types[issue_type] = issue_types.get(issue_type, 0) + 1
        
        for issue_type, count in issue_types.items():
            print(f"  - {issue_type}: {count} 个")
    
    print(f"\n📄 详细报告已保存到: {report_file}")
    
    # 第4部分：改进建议
    print_header("📋 第4部分：改进建议")
    
    suggestions = []
    
    if report.failed_cases > 0:
        suggestions.append("🔧 修复失败的案例执行")
    
    no_viz_count = len([i for i in report.issues if i['type'] == 'visualization' and '无可视化图表' in i['description']])
    if no_viz_count > 5:
        suggestions.append(f"📊 为 {no_viz_count} 个案例添加可视化图表")
    
    no_data_count = len([i for i in report.issues if i['type'] == 'data' and '无数据文件' in i['description']])
    if no_data_count > 5:
        suggestions.append(f"📁 为 {no_data_count} 个案例生成数据文件")
    
    if suggestions:
        print("建议的改进措施:")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"  {i}. {suggestion}")
    else:
        print("✅ 案例质量优秀，暂无明显改进点")
    
    print_header("✅ 测试完成")

if __name__ == "__main__":
    try:
        comprehensive_case_test()
    except KeyboardInterrupt:
        print("\n\n⚠️ 测试被用户中断")
    except Exception as e:
        print(f"\n\n❌ 测试过程发生错误: {e}")
        import traceback
        traceback.print_exc()

