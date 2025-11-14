#!/usr/bin/env python3
"""
文件系统案例详细测试脚本
直接测试文件系统中的案例，检查文档、代码、图表完整性
"""

import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import re

class FileSystemCaseTest:
    def __init__(self):
        self.results = []
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

        self.base_path = Path("/home/user/CHS-Books/books")

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

    def check_readme(self, case_dir):
        """检查README文件"""
        readme_file = case_dir / "README.md"

        if not readme_file.exists():
            return {
                "exists": False,
                "error": "README.md不存在"
            }

        try:
            with open(readme_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 检查README质量
            checks = {
                "length": len(content),
                "lines": len(content.split('\n')),
                "has_title": bool(re.search(r'#.*案例|#.*Case', content)),
                "has_description": len(content) > 100,
                "has_code_block": "```" in content,
                "has_chinese": bool(re.search(r'[\u4e00-\u9fff]', content)),
            }

            return {
                "exists": True,
                "file_path": str(readme_file),
                "size": readme_file.stat().st_size,
                "checks": checks,
                "success": checks["has_description"]
            }
        except Exception as e:
            return {
                "exists": True,
                "error": str(e),
                "success": False
            }

    def check_main_py(self, case_dir):
        """检查main.py文件"""
        main_file = case_dir / "main.py"

        if not main_file.exists():
            return {
                "exists": False,
                "error": "main.py不存在"
            }

        try:
            with open(main_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 检查代码质量
            lines = content.split('\n')
            code_lines = [l for l in lines if l.strip() and not l.strip().startswith('#')]

            checks = {
                "total_lines": len(lines),
                "code_lines": len(code_lines),
                "has_imports": "import " in content,
                "has_main": "if __name__" in content,
                "has_comments": "#" in content,
            }

            return {
                "exists": True,
                "file_path": str(main_file),
                "size": main_file.stat().st_size,
                "checks": checks,
                "success": checks["code_lines"] > 10
            }
        except Exception as e:
            return {
                "exists": True,
                "error": str(e),
                "success": False
            }

    def check_images(self, case_dir):
        """检查图片文件"""
        image_extensions = ['.png', '.jpg', '.jpeg', '.svg', '.gif', '.pdf']
        images = []

        for ext in image_extensions:
            images.extend(case_dir.glob(f"*{ext}"))
            # 也检查子目录
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

        return {
            "count": len(valid_images),
            "images": valid_images,
            "success": len(valid_images) > 0
        }

    def check_data_files(self, case_dir):
        """检查数据文件"""
        data_extensions = ['.csv', '.txt', '.dat', '.json', '.xlsx', '.xls']
        data_files = []

        for ext in data_extensions:
            data_files.extend(case_dir.glob(f"*{ext}"))
            data_files.extend(case_dir.glob(f"**/*{ext}"))

        # 去重
        data_files = list(set(data_files))

        valid_data = []
        for df in data_files:
            if df.stat().st_size > 0:
                valid_data.append({
                    "filename": df.name,
                    "path": str(df),
                    "size": df.stat().st_size
                })

        return {
            "count": len(valid_data),
            "files": valid_data,
            "has_data": len(valid_data) > 0
        }

    def check_other_py_files(self, case_dir):
        """检查其他Python文件"""
        py_files = list(case_dir.glob("*.py"))

        # 排除main.py
        other_py = [f for f in py_files if f.name != "main.py"]

        files_info = []
        for pyf in other_py:
            files_info.append({
                "filename": pyf.name,
                "path": str(pyf),
                "size": pyf.stat().st_size
            })

        return {
            "count": len(files_info),
            "files": files_info
        }

    def test_case(self, book_id, case_id):
        """测试一个案例"""
        case_dir = self.base_path / book_id / "code" / "examples" / case_id

        if not case_dir.exists():
            return {
                "case_id": case_id,
                "exists": False,
                "error": f"案例目录不存在: {case_dir}",
                "success": False
            }

        # 检查各项内容
        readme_result = self.check_readme(case_dir)
        main_result = self.check_main_py(case_dir)
        images_result = self.check_images(case_dir)
        data_result = self.check_data_files(case_dir)
        other_py_result = self.check_other_py_files(case_dir)

        # 评估整体状态
        critical_success = (
            readme_result.get("success", False) and
            main_result.get("success", False)
        )

        result = {
            "case_id": case_id,
            "case_dir": str(case_dir),
            "exists": True,
            "readme": readme_result,
            "main_py": main_result,
            "images": images_result,
            "data": data_result,
            "other_py": other_py_result,
            "critical_success": critical_success,
            "has_images": images_result["success"],
            "success": critical_success  # README和main.py必须成功
        }

        # 记录问题
        if not readme_result.get("success", False):
            self.issues.append({
                "type": "README问题",
                "book_id": book_id,
                "case_id": case_id,
                "detail": readme_result.get("error", "质量不足")
            })

        if not main_result.get("success", False):
            self.issues.append({
                "type": "main.py问题",
                "book_id": book_id,
                "case_id": case_id,
                "detail": main_result.get("error", "质量不足")
            })

        if not images_result["success"]:
            self.issues.append({
                "type": "缺少图片",
                "book_id": book_id,
                "case_id": case_id
            })

        return result

    def test_book(self, book_id, case_count):
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

            result = self.test_case(book_id, case_id)
            book_results["case_results"].append(result)
            book_results["tested_cases"] += 1

            if result["success"]:
                book_results["passed_cases"] += 1

                # 显示详细信息
                readme_len = result["readme"].get("checks", {}).get("length", 0)
                code_lines = result["main_py"].get("checks", {}).get("code_lines", 0)
                img_count = result["images"]["count"]

                self.log(
                    f"{case_id}: ✓ (README:{readme_len}字, 代码:{code_lines}行, 图片:{img_count}个)",
                    "PASS"
                )
            else:
                book_results["failed_cases"] += 1

                errors = []
                if not result.get("exists"):
                    errors.append("目录不存在")
                if not result.get("readme", {}).get("success", False):
                    errors.append("README")
                if not result.get("main_py", {}).get("success", False):
                    errors.append("main.py")
                if not result.get("images", {}).get("success", False):
                    errors.append("图片")

                self.log(f"{case_id}: ✗ ({', '.join(errors)})", "FAIL")

        # 书籍汇总
        pass_rate = (book_results["passed_cases"] / book_results["tested_cases"] * 100) if book_results["tested_cases"] > 0 else 0

        self.log("")
        self.log(f"{book_name} 完成: {book_results['passed_cases']}/{book_results['tested_cases']} ({pass_rate:.1f}%)")
        self.log("=" * 70)

        self.results.append(book_results)
        return book_results

    def run_all_tests(self):
        """运行所有测试"""
        self.log("=" * 70)
        self.log("文件系统案例详细测试开始")
        self.log("=" * 70)
        self.log(f"基础路径: {self.base_path}")
        self.log(f"测试书籍数: {len(self.books)}")
        self.log(f"预期案例总数: {sum(b['cases'] for b in self.books.values())}")
        self.log("")

        # 测试每本书
        for book_id, book_info in self.books.items():
            try:
                self.test_book(book_id, book_info["cases"])
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
        report_file = Path("/home/user/CHS-Books/file_system_case_test_report.json")
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
            status = "✓" if rate == 100 else "⚠" if rate >= 80 else "✗"
            print(f"{status} {book_name}: {passed}/{tested} ({rate:.1f}%)")

        # 显示问题汇总
        if self.issues:
            print("\n" + "=" * 70)
            print(f"发现问题: {len(self.issues)}个")
            print("=" * 70)

            # 按类型分组
            issues_by_type = defaultdict(list)
            for issue in self.issues:
                issues_by_type[issue["type"]].append(issue)

            for issue_type, issue_list in sorted(issues_by_type.items()):
                print(f"\n{issue_type}: {len(issue_list)}个")
                for issue in issue_list[:10]:  # 只显示前10个
                    detail = f" - {issue.get('detail', '')}" if 'detail' in issue else ""
                    print(f"  - {issue['book_id']}/{issue['case_id']}{detail}")
                if len(issue_list) > 10:
                    print(f"  ... 还有{len(issue_list) - 10}个")

        return report

    def generate_markdown_report(self, report):
        """生成Markdown格式报告"""
        md_file = Path("/home/user/CHS-Books/FILE_SYSTEM_CASE_TEST_REPORT.md")

        with open(md_file, "w", encoding="utf-8") as f:
            f.write("# CHS-Books 文件系统案例详细测试报告\n\n")
            f.write(f"**测试日期**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**测试方式**: 直接文件系统检查\n")
            f.write(f"**基础路径**: `/home/user/CHS-Books/books`\n\n")
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

            # 测试标准
            f.write("### 测试标准\n\n")
            f.write("每个案例必须包含:\n\n")
            f.write("- ✅ **README.md**: 长度>100字符，包含标题和代码块\n")
            f.write("- ✅ **main.py**: 有效代码行数>10行\n")
            f.write("- ⚠️ **图片文件**: 建议包含结果图表（.png/.jpg/.svg）\n")
            f.write("- ℹ️ **数据文件**: 可选（.csv/.txt/.json等）\n\n")
            f.write("---\n\n")

            # 按书籍统计
            f.write("## 📚 按书籍详细统计\n\n")

            for book in report["books"]:
                name = book.get("book_name", "Unknown")
                book_id = book.get("book_id", "")
                tested = book.get("tested_cases", 0)
                passed = book.get("passed_cases", 0)
                failed = book.get("failed_cases", 0)
                rate = (passed / tested * 100) if tested > 0 else 0

                status_emoji = "✅" if rate == 100 else "⚠️" if rate >= 80 else "❌"

                f.write(f"### {status_emoji} {name}\n\n")
                f.write(f"**书籍ID**: `{book_id}`  \n")
                f.write(f"**测试结果**: {passed}/{tested} 通过 ({rate:.1f}%)  \n")
                f.write(f"**失败案例**: {failed}个\n\n")

                # 列出失败的案例
                if failed > 0:
                    f.write("**失败案例列表**:\n\n")
                    case_results = book.get("case_results", [])
                    for case in case_results:
                        if not case.get("success", False):
                            case_id = case["case_id"]
                            problems = []
                            if not case.get("readme", {}).get("success", False):
                                problems.append("README")
                            if not case.get("main_py", {}).get("success", False):
                                problems.append("main.py")
                            if not case.get("images", {}).get("success", False):
                                problems.append("无图片")
                            f.write(f"- `{case_id}`: {', '.join(problems)}\n")
                    f.write("\n")

                f.write("---\n\n")

            # 问题分类汇总
            if report["issues"]:
                f.write("## ⚠️ 问题分类汇总\n\n")

                issues_by_type = defaultdict(list)
                for issue in report["issues"]:
                    issues_by_type[issue["type"]].append(issue)

                for issue_type, issue_list in sorted(issues_by_type.items()):
                    f.write(f"### {issue_type} ({len(issue_list)}个)\n\n")

                    for issue in issue_list:
                        detail = f" - {issue.get('detail', '')}" if 'detail' in issue else ""
                        f.write(f"- `{issue['book_id']}/{issue['case_id']}`{detail}\n")

                    f.write("\n")

            # 建议
            f.write("---\n\n")
            f.write("## 💡 改进建议\n\n")

            # 统计问题类型
            readme_issues = len([i for i in report["issues"] if i["type"] == "README问题"])
            mainpy_issues = len([i for i in report["issues"] if i["type"] == "main.py问题"])
            image_issues = len([i for i in report["issues"] if i["type"] == "缺少图片"])

            if readme_issues > 0:
                f.write(f"1. **README文档** ({readme_issues}个案例需改进)\n")
                f.write("   - 确保每个README.md包含案例说明\n")
                f.write("   - 添加代码示例和使用说明\n")
                f.write("   - 长度至少100字符\n\n")

            if mainpy_issues > 0:
                f.write(f"2. **main.py代码** ({mainpy_issues}个案例需改进)\n")
                f.write("   - 确保main.py存在且可运行\n")
                f.write("   - 有效代码行数应大于10行\n")
                f.write("   - 包含必要的导入和主函数\n\n")

            if image_issues > 0:
                f.write(f"3. **结果图表** ({image_issues}个案例缺少)\n")
                f.write("   - 建议为每个案例添加结果图表\n")
                f.write("   - 图表应展示计算结果或模型效果\n")
                f.write("   - 支持格式: PNG, JPG, SVG等\n\n")

            f.write("---\n\n")
            f.write(f"**报告生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        self.log(f"Markdown报告已保存: {md_file}")

def main():
    tester = FileSystemCaseTest()
    tester.run_all_tests()
    tester.generate_report()

if __name__ == "__main__":
    main()
