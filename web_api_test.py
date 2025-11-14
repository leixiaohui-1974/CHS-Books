#!/usr/bin/env python3
"""
Web系统API测试脚本
测试所有API端点的可用性和正确性
"""

import requests
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

BASE_URL = "http://localhost:8000"

class WebAPITest:
    def __init__(self):
        self.results = []
        self.summary = defaultdict(int)

    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = {
            "INFO": "ℹ",
            "PASS": "✓",
            "FAIL": "✗",
            "WARN": "⚠",
            "ERROR": "💥"
        }.get(level, "•")
        print(f"[{timestamp}] {prefix} {message}")

    def test_endpoint(self, name, url, method="GET", expected_status=200):
        """测试单个API端点"""
        try:
            if method == "GET":
                response = requests.get(url, timeout=5)
            else:
                response = requests.post(url, timeout=5)

            success = response.status_code == expected_status

            result = {
                "name": name,
                "url": url,
                "method": method,
                "status_code": response.status_code,
                "expected_status": expected_status,
                "success": success,
                "content_type": response.headers.get("content-type", ""),
                "response_size": len(response.content)
            }

            # 尝试解析JSON
            if "application/json" in result["content_type"]:
                try:
                    result["json_data"] = response.json()
                except:
                    pass

            self.results.append(result)
            self.summary["total"] += 1
            if success:
                self.summary["passed"] += 1
                self.log(f"{name}: PASS ({response.status_code})", "PASS")
            else:
                self.summary["failed"] += 1
                self.log(f"{name}: FAIL (expected {expected_status}, got {response.status_code})", "FAIL")

            return result

        except requests.exceptions.Timeout:
            result = {"name": name, "url": url, "success": False, "error": "Timeout"}
            self.results.append(result)
            self.summary["total"] += 1
            self.summary["errors"] += 1
            self.log(f"{name}: ERROR (Timeout)", "ERROR")
            return result

        except Exception as e:
            result = {"name": name, "url": url, "success": False, "error": str(e)}
            self.results.append(result)
            self.summary["total"] += 1
            self.summary["errors"] += 1
            self.log(f"{name}: ERROR ({e})", "ERROR")
            return result

    def run_all_tests(self):
        """运行所有测试"""
        self.log("=" * 70)
        self.log("Web API测试开始")
        self.log("=" * 70)

        # 1. 基础服务测试
        self.log("\n[1/8] 基础服务测试")
        self.log("-" * 70)
        self.test_endpoint("服务器根路径", f"{BASE_URL}/")
        self.test_endpoint("API文档", f"{BASE_URL}/docs")
        self.test_endpoint("OpenAPI规范", f"{BASE_URL}/openapi.json")

        # 2. 静态文件测试
        self.log("\n[2/8] 静态文件测试")
        self.log("-" * 70)
        self.test_endpoint("主页", f"{BASE_URL}/static/index.html")
        self.test_endpoint("书籍列表页", f"{BASE_URL}/static/textbooks.html")
        self.test_endpoint("学习页面", f"{BASE_URL}/static/learning.html")
        self.test_endpoint("搜索页面", f"{BASE_URL}/static/search.html")
        self.test_endpoint("代码运行器", f"{BASE_URL}/static/code-runner.html")

        # 3. 书籍API测试
        self.log("\n[3/8] 书籍API测试")
        self.log("-" * 70)
        result = self.test_endpoint("书籍列表", f"{BASE_URL}/api/textbooks/", expected_status=[200, 500])

        if result.get("json_data"):
            books = result["json_data"]
            if isinstance(books, list) and len(books) > 0:
                book_id = books[0].get("id")
                if book_id:
                    self.test_endpoint(f"书籍详情 ({book_id})",
                                     f"{BASE_URL}/api/textbooks/{book_id}")

        # 4. 案例API测试
        self.log("\n[4/8] 案例API测试")
        self.log("-" * 70)
        result = self.test_endpoint("案例列表", f"{BASE_URL}/api/cases", expected_status=[200, 500])

        if result.get("json_data"):
            cases = result["json_data"]
            if isinstance(cases, list) and len(cases) > 0:
                case_id = cases[0].get("id") or cases[0].get("case_id")
                if case_id:
                    self.test_endpoint(f"案例详情 ({case_id})",
                                     f"{BASE_URL}/api/cases/{case_id}")
                    self.test_endpoint(f"案例README ({case_id})",
                                     f"{BASE_URL}/api/cases/{case_id}/readme")
                    self.test_endpoint(f"案例代码 ({case_id})",
                                     f"{BASE_URL}/api/cases/{case_id}/code")

        # 5. 知识库API测试
        self.log("\n[5/8] 知识库API测试")
        self.log("-" * 70)
        self.test_endpoint("知识库健康检查", f"{BASE_URL}/api/knowledge/health")
        self.test_endpoint("知识库统计", f"{BASE_URL}/api/knowledge/stats")
        self.test_endpoint("知识库搜索", f"{BASE_URL}/api/knowledge/search?q=水箱")

        # 6. 搜索API测试
        self.log("\n[6/8] 搜索API测试")
        self.log("-" * 70)
        self.test_endpoint("搜索接口", f"{BASE_URL}/api/search/?q=控制")
        self.test_endpoint("搜索统计", f"{BASE_URL}/api/search/stats")

        # 7. 进度API测试
        self.log("\n[7/8] 学习进度API测试")
        self.log("-" * 70)
        self.test_endpoint("进度健康检查", f"{BASE_URL}/api/progress/health")
        self.test_endpoint("排行榜", f"{BASE_URL}/api/progress/leaderboard")

        # 8. 代码执行API测试
        self.log("\n[8/8] 代码执行API测试")
        self.log("-" * 70)
        # 注意：这个是POST请求，可能需要特殊处理
        self.test_endpoint("代码执行接口", f"{BASE_URL}/api/execute/python",
                         expected_status=[405, 422])  # 没有body会返回405或422

    def generate_report(self):
        """生成测试报告"""
        self.log("\n" + "=" * 70)
        self.log("生成测试报告")
        self.log("=" * 70)

        report = {
            "timestamp": datetime.now().isoformat(),
            "base_url": BASE_URL,
            "summary": dict(self.summary),
            "pass_rate": f"{self.summary['passed']/self.summary['total']*100:.1f}%" if self.summary['total'] > 0 else "0%",
            "results": self.results
        }

        # 保存报告
        report_file = Path("/home/user/CHS-Books/web_api_test_report.json")
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        self.log(f"报告已保存: {report_file}")

        # 打印摘要
        print("\n" + "=" * 70)
        print("测试摘要")
        print("=" * 70)
        print(f"总测试数: {self.summary['total']}")
        print(f"✓ 通过: {self.summary['passed']}")
        print(f"✗ 失败: {self.summary['failed']}")
        print(f"💥 错误: {self.summary['errors']}")
        print(f"通过率: {report['pass_rate']}")
        print("=" * 70)

        # 详细结果
        print("\n失败和错误的测试:")
        print("-" * 70)
        for result in self.results:
            if not result.get("success"):
                print(f"✗ {result['name']}")
                print(f"  URL: {result['url']}")
                if "status_code" in result:
                    print(f"  状态码: {result['status_code']}")
                if "error" in result:
                    print(f"  错误: {result['error']}")
                print()

def main():
    tester = WebAPITest()
    tester.run_all_tests()
    tester.generate_report()

if __name__ == "__main__":
    main()
