#!/usr/bin/env python3
"""
智能案例测试脚本
自动发现并测试每本书的所有案例，检查README、代码、图表完整性
"""

import json
import os
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import re

class SmartCaseTest:
    def __init__(self):
        self.results = []
        self.issues = []

        # 定义需要测试的书籍
        self.books = {
            "ecohydraulics": "生态水力学",
            "water-environment-simulation": "水环境数值模拟",
            "open-channel-hydraulics": "明渠水力学",
            "intelligent-water-network-design": "智能水网设计",
            "photovoltaic-system-modeling-control": "光伏系统建模与控制",
            "wind-power-system-modeling-control": "风电系统建模与控制",
            "distributed-hydrological-model": "分布式水文模型",
            "canal-pipeline-control": "渠道与管道控制"
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

    def discover_cases(self, book_id):
        """发现书籍的所有案例目录"""
        examples_dir = self.base_path / book_id / "code" / "examples"

        if not examples_dir.exists():
            return []

        cases = []
        for item in examples_dir.iterdir():
            if item.is_dir():
                cases.append(item.name)

        return sorted(cases)

    def check_readme(self, case_dir):
        """检查README文件"""
        readme_file = case_dir / "README.md"

        if not readme_file.exists():
            return {
                "exists": False,
                "error": "README.md不存在",
                "success": False
            }

        try:
            with open(readme_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 检查README质量
            checks = {
                "length": len(content),
                "lines": len(content.split('\n')),
                "has_title": bool(re.search(r'#.*案例|#.*Case|#.*[A-Z]', content)),
                "has_description": len(content) > 100,
                "has_code_block": "```" in content,
                "has_chinese": bool(re.search(r'[\u4e00-\u9fff]', content)),
            }

            success = (checks["has_description"] and
                      checks["has_title"] and
                      checks["length"] > 200)

            return {
                "exists": True,
                "file_path": str(readme_file),
                "size": readme_file.stat().st_size,
                "checks": checks,
                "success": success,
                "quality": "优秀" if checks["length"] > 1000 else "良好" if checks["length"] > 500 else "基本"
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
                "error": "main.py不存在",
                "success": False
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
                "has_comments": "#" in content or '"""' in content,
                "has_functions": "def " in content,
            }

            success = checks["code_lines"] > 10 and checks["has_imports"]

            return {
                "exists": True,
                "file_path": str(main_file),
                "size": main_file.stat().st_size,
                "checks": checks,
                "success": success,
                "quality": "优秀" if checks["code_lines"] > 100 else "良好" if checks["code_lines"] > 50 else "基本"
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
            images.extend(case_dir.glob(f"**/*{ext}"))

        # 去重
        images = list(set(images))

        # 检查图片大小和类型
        valid_images = []
        for img in images:
            if img.stat().st_size > 100:  # 至少100字节
                valid_images.append({
                    "filename": img.name,
                    "path": str(img),
                    "size": img.stat().st_size,
                    "extension": img.suffix
                })

        return {
            "count": len(valid_images),
            "images": valid_images,
            "success": len(valid_images) > 0,
            "quality": "优秀" if len(valid_images) >= 3 else "良好" if len(valid_images) >= 1 else "无图片"
        }

    def check_data_files(self, case_dir):
        """检查数据文件"""
        data_extensions = ['.csv', '.txt', '.dat', '.json', '.xlsx', '.xls', '.npy', '.npz']
        data_files = []

        for ext in data_extensions:
            data_files.extend(case_dir.glob(f"*{ext}"))
            data_files.extend(case_dir.glob(f"data/*{ext}"))

        # 去重
        data_files = list(set(data_files))

        valid_data = []
        for df in data_files:
            if df.stat().st_size > 0:
                valid_data.append({
                    "filename": df.name,
                    "path": str(df),
                    "size": df.stat().st_size,
                    "extension": df.suffix
                })

        return {
            "count": len(valid_data),
            "files": valid_data,
            "has_data": len(valid_data) > 0
        }

    def check_other_py_files(self, case_dir):
        """检查其他Python文件（模块化设计）"""
        py_files = list(case_dir.glob("*.py"))

        # 排除main.py
        other_py = [f for f in py_files if f.name != "main.py" and not f.name.startswith("test_")]

        files_info = []
        for pyf in other_py:
            try:
                with open(pyf, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = len(content.split('\n'))
                files_info.append({
                    "filename": pyf.name,
                    "path": str(pyf),
                    "size": pyf.stat().st_size,
                    "lines": lines
                })
            except:
                pass

        return {
            "count": len(files_info),
            "files": files_info,
            "has_modules": len(files_info) > 0
        }

    def test_case(self, book_id, case_name):
        """测试一个案例"""
        case_dir = self.base_path / book_id / "code" / "examples" / case_name

        if not case_dir.exists():
            return {
                "case_name": case_name,
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

        # 计算综合得分
        score = 0
        if readme_result.get("success", False):
            score += 40
        if main_result.get("success", False):
            score += 40
        if images_result.get("success", False):
            score += 10
        if data_result.get("has_data", False):
            score += 5
        if other_py_result.get("has_modules", False):
            score += 5

        result = {
            "case_name": case_name,
            "case_dir": str(case_dir),
            "exists": True,
            "readme": readme_result,
            "main_py": main_result,
            "images": images_result,
            "data": data_result,
            "other_py": other_py_result,
            "critical_success": critical_success,
            "has_images": images_result["success"],
            "success": critical_success,
            "score": score,
            "grade": self.get_grade(score)
        }

        # 记录问题
        if not readme_result.get("success", False):
            self.issues.append({
                "type": "README问题",
                "book_id": book_id,
                "case_name": case_name,
                "detail": readme_result.get("error", "质量不足")
            })

        if not main_result.get("success", False):
            self.issues.append({
                "type": "main.py问题",
                "book_id": book_id,
                "case_name": case_name,
                "detail": main_result.get("error", "质量不足")
            })

        if not images_result["success"]:
            self.issues.append({
                "type": "缺少图片",
                "book_id": book_id,
                "case_name": case_name
            })

        return result

    def get_grade(self, score):
        """根据分数获取等级"""
        if score >= 90:
            return "A+ 优秀"
        elif score >= 80:
            return "A 良好"
        elif score >= 70:
            return "B 合格"
        else:
            return "C 待改进"

    def test_book(self, book_id):
        """测试一本书的所有案例"""
        book_name = self.books[book_id]

        self.log("=" * 70)
        self.log(f"测试书籍: {book_name} ({book_id})")

        # 发现所有案例
        cases = self.discover_cases(book_id)

        if not cases:
            self.log(f"未找到案例目录", "WARN")
            return {
                "book_id": book_id,
                "book_name": book_name,
                "tested_cases": 0,
                "passed_cases": 0,
                "failed_cases": 0,
                "case_results": []
            }

        self.log(f"发现 {len(cases)} 个案例")
        self.log("=" * 70)

        book_results = {
            "book_id": book_id,
            "book_name": book_name,
            "total_cases": len(cases),
            "tested_cases": 0,
            "passed_cases": 0,
            "failed_cases": 0,
            "case_results": [],
            "total_score": 0,
            "average_score": 0
        }

        for case_name in cases:
            result = self.test_case(book_id, case_name)
            book_results["case_results"].append(result)
            book_results["tested_cases"] += 1

            if result.get("success"):
                book_results["passed_cases"] += 1
            else:
                book_results["failed_cases"] += 1

            book_results["total_score"] += result.get("score", 0)

            # 显示简洁信息
            score = result.get("score", 0)
            grade = result.get("grade", "")
            readme_len = result.get("readme", {}).get("checks", {}).get("length", 0)
            code_lines = result.get("main_py", {}).get("checks", {}).get("code_lines", 0)
            img_count = result.get("images", {}).get("count", 0)

            if result.get("success"):
                self.log(
                    f"{case_name}: ✓ {grade} (README:{readme_len}字 代码:{code_lines}行 图:{img_count})",
                    "PASS"
                )
            else:
                errors = []
                if not result.get("readme", {}).get("success", False):
                    errors.append("README")
                if not result.get("main_py", {}).get("success", False):
                    errors.append("main.py")

                self.log(f"{case_name}: ✗ {grade} (问题: {', '.join(errors)})", "FAIL")

        # 计算平均分
        if book_results["tested_cases"] > 0:
            book_results["average_score"] = book_results["total_score"] / book_results["tested_cases"]

        # 书籍汇总
        pass_rate = (book_results["passed_cases"] / book_results["tested_cases"] * 100) if book_results["tested_cases"] > 0 else 0
        avg_score = book_results["average_score"]

        self.log("")
        self.log(f"{book_name} 完成: {book_results['passed_cases']}/{book_results['tested_cases']} ({pass_rate:.1f}%) 平均分:{avg_score:.1f}")
        self.log("=" * 70)

        self.results.append(book_results)
        return book_results

    def run_all_tests(self):
        """运行所有测试"""
        self.log("=" * 70)
        self.log("智能案例测试开始")
        self.log("=" * 70)
        self.log(f"基础路径: {self.base_path}")
        self.log(f"测试书籍数: {len(self.books)}")
        self.log("")

        # 测试每本书
        for book_id in self.books.keys():
            try:
                self.test_book(book_id)
            except Exception as e:
                self.log(f"测试书籍 {book_id} 时出错: {e}", "ERROR")
                import traceback
                traceback.print_exc()

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
        total_score = sum(r.get("total_score", 0) for r in self.results)
        overall_avg_score = total_score / total_cases_tested if total_cases_tested > 0 else 0

        overall_pass_rate = (total_cases_passed / total_cases_tested * 100) if total_cases_tested > 0 else 0

        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_books": total_books,
                "total_cases_tested": total_cases_tested,
                "total_cases_passed": total_cases_passed,
                "total_cases_failed": total_cases_failed,
                "overall_pass_rate": f"{overall_pass_rate:.1f}%",
                "overall_avg_score": f"{overall_avg_score:.1f}",
                "overall_grade": self.get_grade(overall_avg_score)
            },
            "books": self.results,
            "issues": self.issues
        }

        # 保存JSON报告
        report_file = Path("/home/user/CHS-Books/SMART_CASE_TEST_REPORT.json")
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
        print(f"平均分: {overall_avg_score:.1f}/100")
        print(f"总体评级: {self.get_grade(overall_avg_score)}")
        print("=" * 70)

        # 按书籍显示结果
        print("\n按书籍详细统计:")
        print("-" * 70)
        print(f"{'书籍':<25} {'案例数':<8} {'通过率':<10} {'平均分':<8} {'评级'}")
        print("-" * 70)
        for book_result in self.results:
            book_name = book_result.get("book_name", "Unknown")
            tested = book_result.get("tested_cases", 0)
            passed = book_result.get("passed_cases", 0)
            rate = (passed / tested * 100) if tested > 0 else 0
            avg_score = book_result.get("average_score", 0)
            grade = self.get_grade(avg_score)

            status = "✓" if rate == 100 else "⚠" if rate >= 80 else "✗"
            print(f"{status} {book_name:<23} {tested:<8} {rate:>5.1f}%     {avg_score:>5.1f}    {grade}")

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
                shown = 0
                for issue in issue_list:
                    if shown < 5:  # 只显示前5个
                        detail = f" - {issue.get('detail', '')}" if 'detail' in issue else ""
                        print(f"  - {issue['book_id']}/{issue['case_name']}{detail}")
                        shown += 1
                if len(issue_list) > 5:
                    print(f"  ... 还有{len(issue_list) - 5}个")

        return report

    def generate_markdown_report(self, report):
        """生成Markdown格式报告"""
        md_file = Path("/home/user/CHS-Books/SMART_CASE_TEST_REPORT.md")

        with open(md_file, "w", encoding="utf-8") as f:
            f.write("# CHS-Books 智能案例测试报告\n\n")
            f.write(f"**测试日期**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**测试方式**: 智能发现 + 综合评分\n\n")
            f.write("---\n\n")

            # 总体概况
            f.write("## 📊 总体概况\n\n")
            f.write("| 指标 | 数值 |\n")
            f.write("|------|------|\n")
            f.write(f"| 测试书籍数 | {report['summary']['total_books']} |\n")
            f.write(f"| 测试案例总数 | {report['summary']['total_cases_tested']} |\n")
            f.write(f"| ✅ 通过案例 | {report['summary']['total_cases_passed']} |\n")
            f.write(f"| ❌ 失败案例 | {report['summary']['total_cases_failed']} |\n")
            f.write(f"| 📈 通过率 | **{report['summary']['overall_pass_rate']}** |\n")
            f.write(f"| 🎯 平均分 | **{report['summary']['overall_avg_score']}/100** |\n")
            f.write(f"| 🏆 总体评级 | **{report['summary']['overall_grade']}** |\n\n")

            # 评分标准
            f.write("### 评分标准\n\n")
            f.write("每个案例满分100分，评分项目:\n\n")
            f.write("- ✅ **README文档** (40分): 长度>200字符，包含标题和说明\n")
            f.write("- ✅ **main.py代码** (40分): 有效代码行数>10行，包含导入语句\n")
            f.write("- ⭐ **结果图表** (10分): 包含PNG/JPG/SVG等图片文件\n")
            f.write("- ⭐ **数据文件** (5分): 包含CSV/JSON等数据文件\n")
            f.write("- ⭐ **模块化设计** (5分): 包含其他Python模块文件\n\n")

            f.write("**等级划分**:\n")
            f.write("- A+ (90-100分): 优秀\n")
            f.write("- A (80-89分): 良好\n")
            f.write("- B (70-79分): 合格\n")
            f.write("- C (<70分): 待改进\n\n")
            f.write("---\n\n")

            # 按书籍统计
            f.write("## 📚 按书籍详细统计\n\n")
            f.write("| 书籍 | 案例数 | 通过 | 失败 | 通过率 | 平均分 | 评级 |\n")
            f.write("|------|--------|------|------|--------|--------|------|\n")

            for book in report["books"]:
                name = book.get("book_name", "Unknown")
                tested = book.get("tested_cases", 0)
                passed = book.get("passed_cases", 0)
                failed = book.get("failed_cases", 0)
                rate = (passed / tested * 100) if tested > 0 else 0
                avg_score = book.get("average_score", 0)
                grade = self.get_grade(avg_score)

                status_emoji = "✅" if rate == 100 else "⚠️" if rate >= 80 else "❌"

                f.write(f"| {status_emoji} {name} | {tested} | {passed} | {failed} | {rate:.1f}% | {avg_score:.1f} | {grade} |\n")

            f.write("\n---\n\n")

            # 各书籍详情
            f.write("## 📖 各书籍详细分析\n\n")

            for book in report["books"]:
                name = book.get("book_name", "Unknown")
                book_id = book.get("book_id", "")
                tested = book.get("tested_cases", 0)
                passed = book.get("passed_cases", 0)
                failed = book.get("failed_cases", 0)
                rate = (passed / tested * 100) if tested > 0 else 0
                avg_score = book.get("average_score", 0)

                status_emoji = "✅" if rate == 100 else "⚠️" if rate >= 80 else "❌"

                f.write(f"### {status_emoji} {name}\n\n")
                f.write(f"**书籍ID**: `{book_id}`  \n")
                f.write(f"**测试结果**: {passed}/{tested} 通过 ({rate:.1f}%)  \n")
                f.write(f"**平均分**: {avg_score:.1f}/100  \n")
                f.write(f"**评级**: {self.get_grade(avg_score)}\n\n")

                # 列出失败的案例
                if failed > 0:
                    f.write("**待改进案例**:\n\n")
                    case_results = book.get("case_results", [])
                    for case in case_results:
                        if not case.get("success", False):
                            case_name = case["case_name"]
                            score = case.get("score", 0)
                            grade = case.get("grade", "")
                            problems = []
                            if not case.get("readme", {}).get("success", False):
                                problems.append("README")
                            if not case.get("main_py", {}).get("success", False):
                                problems.append("main.py")
                            if not case.get("images", {}).get("success", False):
                                problems.append("无图片")
                            f.write(f"- `{case_name}` - {grade} ({score}分) - 问题: {', '.join(problems)}\n")
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

                    for issue in issue_list[:20]:  # 最多显示20个
                        detail = f" - {issue.get('detail', '')}" if 'detail' in issue else ""
                        f.write(f"- `{issue['book_id']}/{issue['case_name']}`{detail}\n")

                    if len(issue_list) > 20:
                        f.write(f"\n... 还有{len(issue_list) - 20}个\n")

                    f.write("\n")

            # 总结与建议
            f.write("---\n\n")
            f.write("## 💡 总结与建议\n\n")

            total_cases = report['summary']['total_cases_tested']
            pass_rate = float(report['summary']['overall_pass_rate'].rstrip('%'))

            if pass_rate == 100:
                f.write("✅ **优秀！** 所有案例均已达标，文档和代码质量良好。\n\n")
                f.write("**建议**:\n")
                f.write("- 继续保持高质量标准\n")
                f.write("- 为更多案例添加结果图表\n")
                f.write("- 考虑添加更多示例数据\n\n")
            elif pass_rate >= 80:
                f.write("⚠️ **良好！** 大部分案例已达标，但仍有改进空间。\n\n")
                f.write("**建议**:\n")
                f.write("- 优先修复失败的案例\n")
                f.write("- 完善README文档说明\n")
                f.write("- 增加代码注释和文档\n\n")
            else:
                f.write("❌ **需改进！** 较多案例未达标，需要系统性改进。\n\n")
                f.write("**建议**:\n")
                f.write("- 系统性检查和修复所有失败案例\n")
                f.write("- 建立文档和代码质量规范\n")
                f.write("- 为关键案例添加详细说明\n\n")

            # 统计问题类型
            if report["issues"]:
                readme_issues = len([i for i in report["issues"] if i["type"] == "README问题"])
                mainpy_issues = len([i for i in report["issues"] if i["type"] == "main.py问题"])
                image_issues = len([i for i in report["issues"] if i["type"] == "缺少图片"])

                if readme_issues > 0:
                    f.write(f"1. **README文档** ({readme_issues}/{total_cases}个案例需改进, {readme_issues/total_cases*100:.1f}%)\n")
                    f.write("   - 确保每个README.md包含案例说明\n")
                    f.write("   - 添加代码示例和使用说明\n")
                    f.write("   - 长度至少200字符\n\n")

                if mainpy_issues > 0:
                    f.write(f"2. **main.py代码** ({mainpy_issues}/{total_cases}个案例需改进, {mainpy_issues/total_cases*100:.1f}%)\n")
                    f.write("   - 确保main.py存在且可运行\n")
                    f.write("   - 有效代码行数应大于10行\n")
                    f.write("   - 包含必要的导入和主函数\n\n")

                if image_issues > 0:
                    f.write(f"3. **结果图表** ({image_issues}/{total_cases}个案例缺少, {image_issues/total_cases*100:.1f}%)\n")
                    f.write("   - 建议为每个案例添加结果图表\n")
                    f.write("   - 图表应展示计算结果或模型效果\n")
                    f.write("   - 支持格式: PNG, JPG, SVG等\n\n")

            f.write("---\n\n")
            f.write(f"**报告生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        self.log(f"Markdown报告已保存: {md_file}")

def main():
    tester = SmartCaseTest()
    tester.run_all_tests()
    tester.generate_report()

if __name__ == "__main__":
    main()
