#!/usr/bin/env python3
"""
Web系统案例详细测试脚本
测试每个书籍的每个案例，检查文档、代码、图表显示情况
"""

import requests
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import os
import re

BASE_URL = "http://localhost:8000"

class WebCaseDetailTest:
    def __init__(self):
        self.results = []
        self.summary = defaultdict(int)
        self.issues = []

        # 定义所有书籍
        self.books = {
            "ecohydraulics": {"name": "生态水力学", "cases": 32},
            "water-environment-simulation": {"name": "水环境数值模拟", "cases": 30},
            "open-channel-hydraulics": {"name": "明渠水力学", "cases": 30},
            "intelligent-water-network-design": {"name": "智能水网设计", "cases": 25},
            "photovoltaic-system-modeling-control": {"name": "光伏系统建模与控制", "cases": 20},
            "wind-power-system-modeling-control": {"name": "风电系统建模与控制", "cases": 15},
            "distributed-hydrological-model": {"name": "分布式水文模型", "cases": 24},
            "canal-pipeline-control": {"name": "渠道与管道控制", "cases": 20}
        }

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

    def check_file_exists(self, book_id, case_id, filename):
        """检查文件是否存在"""
        file_path = Path(f"/home/user/CHS-Books/books/{book_id}/code/examples/{case_id}/{filename}")
        return file_path.exists(), file_path

    def test_case_readme(self, book_id, case_id):
        """测试案例README文档"""
        try:
            url = f"{BASE_URL}/api/cases/{case_id}/readme"
            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                readme_content = response.text

                # 检查README内容
                checks = {
                    "length": len(readme_content),
                    "has_title": bool(re.search(r'#.*案例|#.*Case', readme_content)),
                    "has_description": len(readme_content) > 100,
                    "has_code_block": "```" in readme_content or "···" in readme_content,
                }

                # 检查本地文件是否存在
                file_exists, file_path = self.check_file_exists(book_id, case_id, "README.md")

                result = {
                    "test": "README文档",
                    "book_id": book_id,
                    "case_id": case_id,
                    "url": url,
                    "status_code": response.status_code,
                    "content_length": len(readme_content),
                    "checks": checks,
                    "file_exists": file_exists,
                    "file_path": str(file_path) if file_exists else None,
                    "success": response.status_code == 200 and checks["has_description"]
                }

                if not checks["has_description"]:
                    self.issues.append({
                        "type": "README内容过短",
                        "book_id": book_id,
                        "case_id": case_id,
                        "length": len(readme_content)
                    })

                return result
            else:
                return {
                    "test": "README文档",
                    "book_id": book_id,
                    "case_id": case_id,
                    "url": url,
                    "status_code": response.status_code,
                    "success": False,
                    "error": f"HTTP {response.status_code}"
                }

        except Exception as e:
            return {
                "test": "README文档",
                "book_id": book_id,
                "case_id": case_id,
                "success": False,
                "error": str(e)
            }

    def test_case_code(self, book_id, case_id):
        """测试案例代码文件"""
        try:
            url = f"{BASE_URL}/api/cases/{case_id}/code"
            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                try:
                    code_data = response.json()
                except:
                    code_data = {"main.py": response.text}

                # 检查代码内容
                total_lines = 0
                file_count = 0

                if isinstance(code_data, dict):
                    for filename, content in code_data.items():
                        file_count += 1
                        total_lines += len(content.split('\n'))

                # 检查本地main.py是否存在
                file_exists, file_path = self.check_file_exists(book_id, case_id, "main.py")

                result = {
                    "test": "代码文件",
                    "book_id": book_id,
                    "case_id": case_id,
                    "url": url,
                    "status_code": response.status_code,
                    "file_count": file_count,
                    "total_lines": total_lines,
                    "main_py_exists": file_exists,
                    "file_path": str(file_path) if file_exists else None,
                    "success": response.status_code == 200 and total_lines > 0
                }

                if total_lines == 0:
                    self.issues.append({
                        "type": "代码文件为空",
                        "book_id": book_id,
                        "case_id": case_id
                    })

                return result
            else:
                return {
                    "test": "代码文件",
                    "book_id": book_id,
                    "case_id": case_id,
                    "url": url,
                    "status_code": response.status_code,
                    "success": False,
                    "error": f"HTTP {response.status_code}"
                }

        except Exception as e:
            return {
                "test": "代码文件",
                "book_id": book_id,
                "case_id": case_id,
                "success": False,
                "error": str(e)
            }

    def test_case_images(self, book_id, case_id):
        """测试案例图表文件"""
        case_dir = Path(f"/home/user/CHS-Books/books/{book_id}/code/examples/{case_id}")

        if not case_dir.exists():
            return {
                "test": "图表文件",
                "book_id": book_id,
                "case_id": case_id,
                "success": False,
                "error": "案例目录不存在"
            }

        # 查找所有图片文件
        image_extensions = ['.png', '.jpg', '.jpeg', '.svg', '.gif']
        images = []

        for ext in image_extensions:
            images.extend(case_dir.glob(f"*{ext}"))
            images.extend(case_dir.glob(f"**/*{ext}"))

        # 去重
        images = list(set(images))

        # 检查图片大小
        valid_images = []
        for img in images:
            if img.stat().st_size > 0:
                valid_images.append({
                    "filename": img.name,
                    "path": str(img),
                    "size": img.stat().st_size
                })

        result = {
            "test": "图表文件",
            "book_id": book_id,
            "case_id": case_id,
            "image_count": len(valid_images),
            "images": valid_images,
            "success": len(valid_images) > 0
        }

        if len(valid_images) == 0:
            self.issues.append({
                "type": "缺少图表文件",
                "book_id": book_id,
                "case_id": case_id
            })

        return result

    def test_case_detail(self, book_id, case_id):
        """测试案例详情API"""
        try:
            url = f"{BASE_URL}/api/cases/{case_id}"
            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                try:
                    case_data = response.json()

                    result = {
                        "test": "案例详情",
                        "book_id": book_id,
                        "case_id": case_id,
                        "url": url,
                        "status_code": response.status_code,
                        "has_title": "title" in case_data,
                        "has_description": "description" in case_data,
                        "title": case_data.get("title", "N/A"),
                        "success": True
                    }

                    return result
                except:
                    return {
                        "test": "案例详情",
                        "book_id": book_id,
                        "case_id": case_id,
                        "success": False,
                        "error": "JSON解析失败"
                    }
            else:
                return {
                    "test": "案例详情",
                    "book_id": book_id,
                    "case_id": case_id,
                    "url": url,
                    "status_code": response.status_code,
                    "success": False,
                    "error": f"HTTP {response.status_code}"
                }

        except Exception as e:
            return {
                "test": "案例详情",
                "book_id": book_id,
                "case_id": case_id,
                "success": False,
                "error": str(e)
            }

    def test_book_cases(self, book_id, case_count):
        """测试一本书的所有案例"""
        book_name = self.books[book_id]["name"]
        self.log("=" * 70)
        self.log(f"测试书籍: {book_name} ({book_id})")
        self.log(f"预期案例数: {case_count}")
        self.log("=" * 70)

        book_results = {
            "book_id": book_id,
            "book_name": book_name,
            "expected_cases": case_count,
            "tested_cases": 0,
            "passed_cases": 0,
            "failed_cases": 0,
            "case_results": []
        }

        for i in range(1, case_count + 1):
            case_id = f"case_{i:02d}"

            self.log(f"\n测试案例: {case_id}")
            self.log("-" * 70)

            # 测试案例详情
            detail_result = self.test_case_detail(book_id, case_id)

            # 测试README
            readme_result = self.test_case_readme(book_id, case_id)

            # 测试代码
            code_result = self.test_case_code(book_id, case_id)

            # 测试图表
            image_result = self.test_case_images(book_id, case_id)

            # 汇总案例结果
            case_result = {
                "case_id": case_id,
                "detail": detail_result,
                "readme": readme_result,
                "code": code_result,
                "images": image_result,
                "overall_success": all([
                    detail_result.get("success", False),
                    readme_result.get("success", False),
                    code_result.get("success", False),
                    image_result.get("success", False)
                ])
            }

            book_results["case_results"].append(case_result)
            book_results["tested_cases"] += 1

            if case_result["overall_success"]:
                book_results["passed_cases"] += 1
                self.log(f"{case_id}: ✓ PASS", "PASS")
            else:
                book_results["failed_cases"] += 1
                self.log(f"{case_id}: ✗ FAIL", "FAIL")

                # 输出失败详情
                if not detail_result.get("success"):
                    self.log(f"  - 详情API失败: {detail_result.get('error', 'Unknown')}", "WARN")
                if not readme_result.get("success"):
                    self.log(f"  - README失败: {readme_result.get('error', 'Unknown')}", "WARN")
                if not code_result.get("success"):
                    self.log(f"  - 代码失败: {code_result.get('error', 'Unknown')}", "WARN")
                if not image_result.get("success"):
                    self.log(f"  - 图表缺失", "WARN")

        # 书籍汇总
        pass_rate = (book_results["passed_cases"] / book_results["tested_cases"] * 100) if book_results["tested_cases"] > 0 else 0

        self.log("\n" + "=" * 70)
        self.log(f"{book_name} 测试完成")
        self.log(f"通过: {book_results['passed_cases']}/{book_results['tested_cases']} ({pass_rate:.1f}%)")
        self.log("=" * 70)

        self.results.append(book_results)

        return book_results

    def run_all_tests(self):
        """运行所有测试"""
        self.log("=" * 70)
        self.log("Web系统案例详细测试开始")
        self.log("=" * 70)
        self.log(f"基础URL: {BASE_URL}")
        self.log(f"测试书籍数: {len(self.books)}")
        self.log(f"预期案例总数: {sum(b['cases'] for b in self.books.values())}")
        self.log("")

        # 测试每本书
        for book_id, book_info in self.books.items():
            try:
                self.test_book_cases(book_id, book_info["cases"])
            except Exception as e:
                self.log(f"测试书籍 {book_id} 时出错: {e}", "ERROR")
                self.results.append({
                    "book_id": book_id,
                    "book_name": book_info["name"],
                    "error": str(e),
                    "tested_cases": 0,
                    "passed_cases": 0,
                    "failed_cases": 0
                })

    def generate_report(self):
        """生成测试报告"""
        self.log("\n" + "=" * 70)
        self.log("生成测试报告")
        self.log("=" * 70)

        # 统计
        total_books = len(self.results)
        total_cases_tested = sum(r.get("tested_cases", 0) for r in self.results)
        total_cases_passed = sum(r.get("passed_cases", 0) for r in self.results)
        total_cases_failed = sum(r.get("failed_cases", 0) for r in self.results)

        overall_pass_rate = (total_cases_passed / total_cases_tested * 100) if total_cases_tested > 0 else 0

        report = {
            "timestamp": datetime.now().isoformat(),
            "base_url": BASE_URL,
            "summary": {
                "total_books": total_books,
                "total_cases_tested": total_cases_tested,
                "total_cases_passed": total_cases_passed,
                "total_cases_failed": total_cases_failed,
                "overall_pass_rate": f"{overall_pass_rate:.1f}%"
            },
            "books": self.results,
            "issues": self.issues
        }

        # 保存JSON报告
        report_file = Path("/home/user/CHS-Books/web_case_detail_report.json")
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        self.log(f"JSON报告已保存: {report_file}")

        # 生成Markdown报告
        self.generate_markdown_report(report)

        # 打印摘要
        print("\n" + "=" * 70)
        print("测试摘要")
        print("=" * 70)
        print(f"测试书籍数: {total_books}")
        print(f"测试案例总数: {total_cases_tested}")
        print(f"✓ 通过: {total_cases_passed}")
        print(f"✗ 失败: {total_cases_failed}")
        print(f"通过率: {overall_pass_rate:.1f}%")
        print("=" * 70)

        # 按书籍显示结果
        print("\n按书籍统计:")
        print("-" * 70)
        for book_result in self.results:
            book_name = book_result.get("book_name", "Unknown")
            tested = book_result.get("tested_cases", 0)
            passed = book_result.get("passed_cases", 0)
            rate = (passed / tested * 100) if tested > 0 else 0
            print(f"{book_name}: {passed}/{tested} ({rate:.1f}%)")

        # 显示问题汇总
        if self.issues:
            print("\n" + "=" * 70)
            print(f"发现问题: {len(self.issues)}个")
            print("=" * 70)

            # 按类型分组
            issues_by_type = defaultdict(list)
            for issue in self.issues:
                issues_by_type[issue["type"]].append(issue)

            for issue_type, issue_list in issues_by_type.items():
                print(f"\n{issue_type}: {len(issue_list)}个")
                for issue in issue_list[:5]:  # 只显示前5个
                    print(f"  - {issue['book_id']}/{issue['case_id']}")
                if len(issue_list) > 5:
                    print(f"  ... 还有{len(issue_list) - 5}个")

    def generate_markdown_report(self, report):
        """生成Markdown格式报告"""
        md_file = Path("/home/user/CHS-Books/WEB_CASE_DETAIL_REPORT.md")

        with open(md_file, "w", encoding="utf-8") as f:
            f.write("# CHS-Books Web系统案例详细测试报告\n\n")
            f.write(f"**测试日期**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**测试工具**: Web案例详细测试脚本\n")
            f.write(f"**服务器**: {BASE_URL}\n\n")
            f.write("---\n\n")

            # 总体概况
            f.write("## 📊 总体概况\n\n")
            f.write("| 指标 | 数值 |\n")
            f.write("|------|------|\n")
            f.write(f"| 测试书籍数 | {report['summary']['total_books']} |\n")
            f.write(f"| 测试案例总数 | {report['summary']['total_cases_tested']} |\n")
            f.write(f"| 通过案例 | {report['summary']['total_cases_passed']} |\n")
            f.write(f"| 失败案例 | {report['summary']['total_cases_failed']} |\n")
            f.write(f"| **总体通过率** | **{report['summary']['overall_pass_rate']}** |\n\n")
            f.write("---\n\n")

            # 按书籍统计
            f.write("## 📚 按书籍统计\n\n")
            f.write("| 书籍 | 测试案例数 | 通过 | 失败 | 通过率 |\n")
            f.write("|------|-----------|------|------|--------|\n")

            for book in report["books"]:
                name = book.get("book_name", "Unknown")
                tested = book.get("tested_cases", 0)
                passed = book.get("passed_cases", 0)
                failed = book.get("failed_cases", 0)
                rate = (passed / tested * 100) if tested > 0 else 0
                f.write(f"| {name} | {tested} | {passed} | {failed} | {rate:.1f}% |\n")

            f.write("\n---\n\n")

            # 问题汇总
            if report["issues"]:
                f.write("## ⚠️ 发现的问题\n\n")

                issues_by_type = defaultdict(list)
                for issue in report["issues"]:
                    issues_by_type[issue["type"]].append(issue)

                for issue_type, issue_list in issues_by_type.items():
                    f.write(f"### {issue_type} ({len(issue_list)}个)\n\n")
                    for issue in issue_list:
                        f.write(f"- `{issue['book_id']}/{issue['case_id']}`")
                        if "length" in issue:
                            f.write(f" (长度: {issue['length']})")
                        f.write("\n")
                    f.write("\n")

            f.write("---\n\n")
            f.write(f"**报告生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        self.log(f"Markdown报告已保存: {md_file}")

def main():
    tester = WebCaseDetailTest()
    tester.run_all_tests()
    tester.generate_report()

if __name__ == "__main__":
    main()
