#!/usr/bin/env python3
"""
Web系统端到端测试脚本
使用Playwright进行浏览器自动化测试和截图
"""

from playwright.sync_api import sync_playwright
import time
import json
from pathlib import Path
from datetime import datetime

# 配置
BASE_URL = "http://localhost:8000"
SCREENSHOTS_DIR = Path("/home/user/CHS-Books/web_test_screenshots")
SCREENSHOTS_DIR.mkdir(exist_ok=True)

class WebE2ETest:
    def __init__(self):
        self.results = []
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    def log(self, message, level="INFO"):
        """记录日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")

    def save_screenshot(self, page, name, description=""):
        """保存截图"""
        filename = f"{self.timestamp}_{name}.png"
        filepath = SCREENSHOTS_DIR / filename
        page.screenshot(path=str(filepath), full_page=True)
        self.log(f"截图已保存: {filename}")
        return str(filepath)

    def test_homepage(self, page):
        """测试主页"""
        self.log("=" * 70)
        self.log("测试 1/7: 主页展示")
        self.log("=" * 70)

        try:
            # 访问主页
            page.goto(f"{BASE_URL}/static/index.html", wait_until="networkidle")
            time.sleep(2)

            # 检查标题
            title = page.title()
            self.log(f"页面标题: {title}")

            # 截图
            screenshot = self.save_screenshot(page, "01_homepage", "主页全景")

            # 检查关键元素
            checks = []

            # 检查导航栏
            if page.locator("nav").count() > 0:
                checks.append({"name": "导航栏", "status": "✓"})
            else:
                checks.append({"name": "导航栏", "status": "✗"})

            # 检查内容区域
            if page.locator(".container, #app, main").count() > 0:
                checks.append({"name": "主内容区", "status": "✓"})
            else:
                checks.append({"name": "主内容区", "status": "✗"})

            result = {
                "test": "主页展示",
                "url": f"{BASE_URL}/static/index.html",
                "title": title,
                "screenshot": screenshot,
                "checks": checks,
                "status": "PASS" if all(c["status"] == "✓" for c in checks) else "FAIL"
            }

            self.results.append(result)
            self.log(f"主页测试完成: {result['status']}")

            for check in checks:
                self.log(f"  {check['status']} {check['name']}")

        except Exception as e:
            self.log(f"主页测试失败: {e}", "ERROR")
            result = {
                "test": "主页展示",
                "status": "ERROR",
                "error": str(e)
            }
            self.results.append(result)

    def test_books_list(self, page):
        """测试书籍列表页"""
        self.log("=" * 70)
        self.log("测试 2/7: 书籍列表页")
        self.log("=" * 70)

        try:
            page.goto(f"{BASE_URL}/static/textbooks.html", wait_until="networkidle")
            time.sleep(2)

            title = page.title()
            self.log(f"页面标题: {title}")

            screenshot = self.save_screenshot(page, "02_books_list", "书籍列表页")

            # 检查书籍卡片
            books = page.locator(".book-card, .card, [data-book]").count()
            self.log(f"发现书籍卡片: {books}个")

            result = {
                "test": "书籍列表页",
                "url": f"{BASE_URL}/static/textbooks.html",
                "title": title,
                "books_count": books,
                "screenshot": screenshot,
                "status": "PASS" if books > 0 else "WARN"
            }

            self.results.append(result)
            self.log(f"书籍列表测试完成: {result['status']}")

        except Exception as e:
            self.log(f"书籍列表测试失败: {e}", "ERROR")
            self.results.append({
                "test": "书籍列表页",
                "status": "ERROR",
                "error": str(e)
            })

    def test_learning_page(self, page):
        """测试学习页面"""
        self.log("=" * 70)
        self.log("测试 3/7: 学习页面")
        self.log("=" * 70)

        try:
            page.goto(f"{BASE_URL}/static/learning.html", wait_until="networkidle")
            time.sleep(2)

            screenshot = self.save_screenshot(page, "03_learning_page", "学习页面")

            result = {
                "test": "学习页面",
                "url": f"{BASE_URL}/static/learning.html",
                "screenshot": screenshot,
                "status": "PASS"
            }

            self.results.append(result)
            self.log("学习页面测试完成: PASS")

        except Exception as e:
            self.log(f"学习页面测试失败: {e}", "ERROR")
            self.results.append({
                "test": "学习页面",
                "status": "ERROR",
                "error": str(e)
            })

    def test_api_textbooks(self, page):
        """测试书籍API"""
        self.log("=" * 70)
        self.log("测试 4/7: 书籍API")
        self.log("=" * 70)

        try:
            # 访问API文档页面
            page.goto(f"{BASE_URL}/docs", wait_until="networkidle")
            time.sleep(2)

            screenshot = self.save_screenshot(page, "04_api_docs", "API文档页面")

            # 尝试调用书籍列表API
            response = page.request.get(f"{BASE_URL}/api/v1/textbooks/list")

            if response.ok:
                data = response.json()
                books_count = len(data.get("books", []))
                self.log(f"API返回书籍数量: {books_count}")

                result = {
                    "test": "书籍API",
                    "endpoint": "/api/v1/textbooks/list",
                    "books_count": books_count,
                    "screenshot": screenshot,
                    "status": "PASS"
                }
            else:
                result = {
                    "test": "书籍API",
                    "status": "FAIL",
                    "error": f"HTTP {response.status}"
                }

            self.results.append(result)
            self.log(f"书籍API测试完成: {result['status']}")

        except Exception as e:
            self.log(f"书籍API测试失败: {e}", "ERROR")
            self.results.append({
                "test": "书籍API",
                "status": "ERROR",
                "error": str(e)
            })

    def test_case_detail(self, page, book_id="water-system-control", case_id="case_01"):
        """测试案例详情页"""
        self.log("=" * 70)
        self.log(f"测试 5/7: 案例详情页 ({book_id}/{case_id})")
        self.log("=" * 70)

        try:
            # 尝试通过API获取案例详情
            response = page.request.get(f"{BASE_URL}/api/v1/books/{book_id}/cases/{case_id}")

            if response.ok:
                data = response.json()
                self.log(f"案例标题: {data.get('title', 'N/A')}")
                self.log(f"README长度: {len(data.get('readme', ''))} 字符")
                self.log(f"代码长度: {len(data.get('code', ''))} 字符")

                result = {
                    "test": "案例详情",
                    "book_id": book_id,
                    "case_id": case_id,
                    "title": data.get('title'),
                    "has_readme": len(data.get('readme', '')) > 0,
                    "has_code": len(data.get('code', '')) > 0,
                    "status": "PASS"
                }
            else:
                result = {
                    "test": "案例详情",
                    "status": "FAIL",
                    "error": f"HTTP {response.status}"
                }

            self.results.append(result)
            self.log(f"案例详情测试完成: {result['status']}")

        except Exception as e:
            self.log(f"案例详情测试失败: {e}", "ERROR")
            self.results.append({
                "test": "案例详情",
                "status": "ERROR",
                "error": str(e)
            })

    def test_code_runner(self, page):
        """测试代码运行器页面"""
        self.log("=" * 70)
        self.log("测试 6/7: 代码运行器页面")
        self.log("=" * 70)

        try:
            page.goto(f"{BASE_URL}/static/code-runner.html", wait_until="networkidle")
            time.sleep(2)

            screenshot = self.save_screenshot(page, "06_code_runner", "代码运行器")

            # 检查代码编辑器区域
            has_editor = page.locator("textarea, .editor, #code-editor").count() > 0

            result = {
                "test": "代码运行器",
                "url": f"{BASE_URL}/static/code-runner.html",
                "has_editor": has_editor,
                "screenshot": screenshot,
                "status": "PASS" if has_editor else "WARN"
            }

            self.results.append(result)
            self.log(f"代码运行器测试完成: {result['status']}")

        except Exception as e:
            self.log(f"代码运行器测试失败: {e}", "ERROR")
            self.results.append({
                "test": "代码运行器",
                "status": "ERROR",
                "error": str(e)
            })

    def test_search_function(self, page):
        """测试搜索功能"""
        self.log("=" * 70)
        self.log("测试 7/7: 搜索功能")
        self.log("=" * 70)

        try:
            page.goto(f"{BASE_URL}/static/search.html", wait_until="networkidle")
            time.sleep(2)

            screenshot = self.save_screenshot(page, "07_search", "搜索页面")

            # 检查搜索输入框
            has_search = page.locator("input[type='search'], input[type='text'][placeholder*='搜索']").count() > 0

            result = {
                "test": "搜索功能",
                "url": f"{BASE_URL}/static/search.html",
                "has_search_box": has_search,
                "screenshot": screenshot,
                "status": "PASS" if has_search else "WARN"
            }

            self.results.append(result)
            self.log(f"搜索功能测试完成: {result['status']}")

        except Exception as e:
            self.log(f"搜索功能测试失败: {e}", "ERROR")
            self.results.append({
                "test": "搜索功能",
                "status": "ERROR",
                "error": str(e)
            })

    def generate_report(self):
        """生成测试报告"""
        self.log("=" * 70)
        self.log("生成测试报告")
        self.log("=" * 70)

        # 统计
        total = len(self.results)
        passed = sum(1 for r in self.results if r.get("status") == "PASS")
        failed = sum(1 for r in self.results if r.get("status") == "FAIL")
        errors = sum(1 for r in self.results if r.get("status") == "ERROR")
        warnings = sum(1 for r in self.results if r.get("status") == "WARN")

        # 生成JSON报告
        report = {
            "timestamp": self.timestamp,
            "summary": {
                "total": total,
                "passed": passed,
                "failed": failed,
                "errors": errors,
                "warnings": warnings,
                "pass_rate": f"{passed/total*100:.1f}%" if total > 0 else "0%"
            },
            "results": self.results,
            "screenshots_dir": str(SCREENSHOTS_DIR)
        }

        report_file = Path("/home/user/CHS-Books/web_e2e_test_report.json")
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        self.log(f"测试报告已保存: {report_file}")

        # 打印摘要
        print("\n" + "=" * 70)
        print("测试摘要")
        print("=" * 70)
        print(f"总测试数: {total}")
        print(f"✓ 通过: {passed}")
        print(f"✗ 失败: {failed}")
        print(f"💥 错误: {errors}")
        print(f"⚠ 警告: {warnings}")
        print(f"通过率: {report['summary']['pass_rate']}")
        print(f"\n截图目录: {SCREENSHOTS_DIR}")
        print(f"报告文件: {report_file}")
        print("=" * 70)

    def run(self):
        """运行所有测试"""
        self.log("=" * 70)
        self.log("Web系统端到端测试开始")
        self.log("=" * 70)
        self.log(f"基础URL: {BASE_URL}")
        self.log(f"截图目录: {SCREENSHOTS_DIR}")
        self.log("")

        with sync_playwright() as p:
            # 启动浏览器（使用Chromium）
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={"width": 1920, "height": 1080},
                locale="zh-CN"
            )
            page = context.new_page()

            try:
                # 执行所有测试
                self.test_homepage(page)
                self.test_books_list(page)
                self.test_learning_page(page)
                self.test_api_textbooks(page)
                self.test_case_detail(page)
                self.test_code_runner(page)
                self.test_search_function(page)

            finally:
                browser.close()

        # 生成报告
        self.generate_report()

def main():
    """主函数"""
    tester = WebE2ETest()
    tester.run()

if __name__ == "__main__":
    main()
