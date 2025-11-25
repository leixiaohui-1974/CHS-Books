#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全案例执行测试
============
对所有236个案例进行实际代码执行测试
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime
from collections import defaultdict

PROJECT_ROOT = Path(__file__).parent
BOOKS_DIR = PROJECT_ROOT / "books"


class FullCaseExecutionTester:
    """全案例执行测试器"""

    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "cases": [],
            "by_book": defaultdict(lambda: {"total": 0, "passed": 0, "failed": 0, "timeout": 0}),
            "summary": {}
        }
        self.total = 0
        self.passed = 0
        self.failed = 0
        self.timeout = 0

    def log(self, msg, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{level}] {msg}")

    def find_all_cases(self):
        """查找所有案例目录"""
        cases = []
        patterns = ["case_*", "example_*", "project_*"]

        for book_dir in BOOKS_DIR.iterdir():
            if not book_dir.is_dir():
                continue

            book_name = book_dir.name

            # 在codes或code/examples目录下查找案例
            search_dirs = [
                book_dir / "codes",
                book_dir / "code" / "examples",
                book_dir / "code" / "cases",
            ]

            for search_dir in search_dirs:
                if not search_dir.exists():
                    continue

                for pattern in patterns:
                    for case_dir in search_dir.glob(pattern):
                        if case_dir.is_dir():
                            cases.append({
                                "book": book_name,
                                "case": case_dir.name,
                                "path": case_dir
                            })

        return cases

    def find_main_file(self, case_dir):
        """查找案例的主入口文件"""
        py_files = list(case_dir.glob("*.py"))

        if not py_files:
            return None

        # 优先级: main.py > 与目录同名 > 第一个文件
        for pf in py_files:
            if pf.name == "main.py":
                return pf
            if pf.name == "__init__.py":
                continue
            if pf.stem == case_dir.name:
                return pf

        # 排除__init__.py
        for pf in py_files:
            if pf.name != "__init__.py":
                return pf

        return None

    def execute_case(self, case_info):
        """执行单个案例"""
        case_dir = case_info["path"]
        book_name = case_info["book"]
        case_name = case_info["case"]

        result = {
            "book": book_name,
            "case": case_name,
            "path": str(case_dir.relative_to(PROJECT_ROOT)),
            "status": "UNKNOWN",
            "main_file": None,
            "duration": 0,
            "output": "",
            "error": ""
        }

        main_file = self.find_main_file(case_dir)

        if not main_file:
            result["status"] = "SKIP"
            result["error"] = "No Python file found"
            return result

        result["main_file"] = main_file.name

        start_time = time.time()

        try:
            # 执行代码(超时30秒)
            env = os.environ.copy()
            env["PYTHONPATH"] = str(PROJECT_ROOT)
            env["MPLBACKEND"] = "Agg"  # 禁用matplotlib GUI

            proc = subprocess.run(
                [sys.executable, str(main_file)],
                capture_output=True,
                text=True,
                timeout=90,
                cwd=str(case_dir),
                env=env
            )

            result["duration"] = time.time() - start_time
            result["output"] = proc.stdout[-500:] if proc.stdout else ""

            if proc.returncode == 0:
                result["status"] = "PASS"
            else:
                result["status"] = "FAIL"
                result["error"] = proc.stderr[-300:] if proc.stderr else f"Exit code: {proc.returncode}"

        except subprocess.TimeoutExpired:
            result["status"] = "TIMEOUT"
            result["duration"] = 90
            result["error"] = "Execution exceeded 90s timeout"
        except Exception as e:
            result["status"] = "ERROR"
            result["error"] = str(e)
            result["duration"] = time.time() - start_time

        return result

    def run_all_tests(self):
        """运行所有测试"""
        self.log("=" * 60)
        self.log("全案例执行测试")
        self.log("=" * 60)

        cases = self.find_all_cases()
        self.log(f"发现 {len(cases)} 个案例")

        # 按书籍分组
        cases_by_book = defaultdict(list)
        for case in cases:
            cases_by_book[case["book"]].append(case)

        for book_name in sorted(cases_by_book.keys()):
            book_cases = cases_by_book[book_name]
            self.log(f"\n📚 {book_name} ({len(book_cases)} 个案例)")

            for case_info in book_cases:
                result = self.execute_case(case_info)
                self.results["cases"].append(result)

                # 更新统计
                self.total += 1
                self.results["by_book"][book_name]["total"] += 1

                if result["status"] == "PASS":
                    self.passed += 1
                    self.results["by_book"][book_name]["passed"] += 1
                    status_icon = "✅"
                elif result["status"] == "TIMEOUT":
                    self.timeout += 1
                    self.results["by_book"][book_name]["timeout"] += 1
                    status_icon = "⏱️"
                elif result["status"] == "SKIP":
                    status_icon = "⏭️"
                else:
                    self.failed += 1
                    self.results["by_book"][book_name]["failed"] += 1
                    status_icon = "❌"

                duration_str = f"({result['duration']:.1f}s)" if result['duration'] > 0 else ""
                self.log(f"  {status_icon} {case_info['case']} {duration_str}")

        # 生成总结
        self.results["summary"] = {
            "total": self.total,
            "passed": self.passed,
            "failed": self.failed,
            "timeout": self.timeout,
            "pass_rate": self.passed / self.total * 100 if self.total > 0 else 0
        }

        return self.results

    def save_report(self):
        """保存报告"""
        report_path = PROJECT_ROOT / "full_case_execution_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2, default=str)

        self.log(f"\n报告已保存: {report_path}")

    def print_summary(self):
        """打印总结"""
        print("\n" + "=" * 60)
        print("执行测试总结")
        print("=" * 60)

        print(f"\n总案例数: {self.total}")
        print(f"通过: {self.passed}")
        print(f"失败: {self.failed}")
        print(f"超时: {self.timeout}")
        print(f"通过率: {self.results['summary']['pass_rate']:.1f}%")

        print("\n按书籍统计:")
        print("-" * 50)
        for book_name, stats in sorted(self.results["by_book"].items()):
            rate = stats["passed"] / stats["total"] * 100 if stats["total"] > 0 else 0
            print(f"  {book_name}: {stats['passed']}/{stats['total']} ({rate:.0f}%)")


def main():
    tester = FullCaseExecutionTester()
    start_time = time.time()

    tester.run_all_tests()
    tester.save_report()
    tester.print_summary()

    duration = time.time() - start_time
    print(f"\n总耗时: {duration:.1f}秒")


if __name__ == "__main__":
    main()
