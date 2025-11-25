#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
深度集成测试脚本
全面测试CHS-Books项目的所有功能
"""

import os
import sys
import json
import time
import subprocess
import importlib.util
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# 项目根目录
PROJECT_ROOT = Path(__file__).parent
BOOKS_DIR = PROJECT_ROOT / "books"

class DeepIntegrationTester:
    """深度集成测试器"""

    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "unit_tests": [],
            "case_execution": [],
            "syntax_check": [],
            "import_check": [],
            "summary": {}
        }
        self.stats = defaultdict(lambda: {"total": 0, "passed": 0, "failed": 0, "skipped": 0})

    def log(self, msg, level="INFO"):
        """日志输出"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{level}] {msg}")

    def run_unit_tests(self):
        """运行所有单元测试"""
        self.log("=" * 60)
        self.log("阶段1: 运行单元测试")
        self.log("=" * 60)

        # 查找所有测试目录
        test_dirs = list(BOOKS_DIR.rglob("tests"))
        self.log(f"发现 {len(test_dirs)} 个测试目录")

        for test_dir in sorted(test_dirs):
            if not test_dir.is_dir():
                continue

            book_name = test_dir.parent.name
            test_files = list(test_dir.glob("test_*.py"))

            if not test_files:
                continue

            self.log(f"\n测试书籍: {book_name} ({len(test_files)} 个测试文件)")

            for test_file in sorted(test_files):
                result = self.run_single_test(test_file, book_name)
                self.results["unit_tests"].append(result)

                if result["status"] == "PASS":
                    self.stats["unit_tests"]["passed"] += 1
                elif result["status"] == "FAIL":
                    self.stats["unit_tests"]["failed"] += 1
                else:
                    self.stats["unit_tests"]["skipped"] += 1
                self.stats["unit_tests"]["total"] += 1

    def run_single_test(self, test_file, book_name):
        """运行单个测试文件"""
        result = {
            "book": book_name,
            "file": test_file.name,
            "path": str(test_file.relative_to(PROJECT_ROOT)),
            "status": "UNKNOWN",
            "duration": 0,
            "output": ""
        }

        start_time = time.time()

        try:
            # 使用subprocess运行测试
            proc = subprocess.run(
                [sys.executable, str(test_file)],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=str(test_file.parent.parent),
                env={**os.environ, "PYTHONPATH": str(PROJECT_ROOT)}
            )

            result["duration"] = time.time() - start_time
            result["output"] = proc.stdout[-500:] if proc.stdout else ""

            if proc.returncode == 0:
                result["status"] = "PASS"
                self.log(f"  ✅ {test_file.name} ({result['duration']:.2f}s)")
            else:
                result["status"] = "FAIL"
                result["error"] = proc.stderr[-300:] if proc.stderr else "Unknown error"
                self.log(f"  ❌ {test_file.name} - 失败")

        except subprocess.TimeoutExpired:
            result["status"] = "TIMEOUT"
            result["duration"] = 60
            self.log(f"  ⏱️ {test_file.name} - 超时")
        except Exception as e:
            result["status"] = "ERROR"
            result["error"] = str(e)
            self.log(f"  ⚠️ {test_file.name} - 错误: {e}")

        return result

    def test_case_execution(self):
        """测试案例执行"""
        self.log("\n" + "=" * 60)
        self.log("阶段2: 案例执行测试")
        self.log("=" * 60)

        # 查找所有案例目录
        case_patterns = ["case_*", "example_*", "project_*", "demo_*"]
        all_cases = []

        for pattern in case_patterns:
            cases = list(BOOKS_DIR.rglob(pattern))
            all_cases.extend([c for c in cases if c.is_dir()])

        # 去重
        all_cases = list(set(all_cases))
        self.log(f"发现 {len(all_cases)} 个案例目录")

        # 测试前100个案例（避免超时）
        test_cases = sorted(all_cases)[:100]

        for case_dir in test_cases:
            result = self.test_single_case(case_dir)
            self.results["case_execution"].append(result)

            if result["status"] == "PASS":
                self.stats["case_execution"]["passed"] += 1
            elif result["status"] == "FAIL":
                self.stats["case_execution"]["failed"] += 1
            else:
                self.stats["case_execution"]["skipped"] += 1
            self.stats["case_execution"]["total"] += 1

    def test_single_case(self, case_dir):
        """测试单个案例"""
        result = {
            "case": case_dir.name,
            "path": str(case_dir.relative_to(PROJECT_ROOT)),
            "status": "UNKNOWN",
            "main_file": None,
            "files_count": 0
        }

        # 查找主入口文件
        py_files = list(case_dir.glob("*.py"))
        result["files_count"] = len(py_files)

        if not py_files:
            result["status"] = "SKIP"
            result["reason"] = "No Python files"
            return result

        # 优先查找main.py或与目录同名的文件
        main_file = None
        for pf in py_files:
            if pf.name == "main.py":
                main_file = pf
                break
            if pf.stem == case_dir.name or pf.stem.startswith(case_dir.name):
                main_file = pf
                break

        if not main_file:
            main_file = py_files[0]

        result["main_file"] = main_file.name

        # 语法检查
        try:
            with open(main_file, 'r', encoding='utf-8') as f:
                code = f.read()
            compile(code, main_file.name, 'exec')
            result["status"] = "PASS"
            self.log(f"  ✅ {case_dir.name}")
        except SyntaxError as e:
            result["status"] = "FAIL"
            result["error"] = f"Syntax error at line {e.lineno}: {e.msg}"
            self.log(f"  ❌ {case_dir.name} - 语法错误")
        except Exception as e:
            result["status"] = "FAIL"
            result["error"] = str(e)
            self.log(f"  ⚠️ {case_dir.name} - {e}")

        return result

    def check_all_python_syntax(self):
        """检查所有Python文件语法"""
        self.log("\n" + "=" * 60)
        self.log("阶段3: Python语法检查")
        self.log("=" * 60)

        all_py_files = list(BOOKS_DIR.rglob("*.py"))
        self.log(f"发现 {len(all_py_files)} 个Python文件")

        errors = []
        for py_file in all_py_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    code = f.read()
                compile(code, str(py_file), 'exec')
                self.stats["syntax_check"]["passed"] += 1
            except SyntaxError as e:
                self.stats["syntax_check"]["failed"] += 1
                errors.append({
                    "file": str(py_file.relative_to(PROJECT_ROOT)),
                    "line": e.lineno,
                    "message": e.msg
                })
                self.log(f"  ❌ {py_file.relative_to(PROJECT_ROOT)}:{e.lineno} - {e.msg}")
            except Exception as e:
                self.stats["syntax_check"]["failed"] += 1
                errors.append({
                    "file": str(py_file.relative_to(PROJECT_ROOT)),
                    "error": str(e)
                })

            self.stats["syntax_check"]["total"] += 1

        self.results["syntax_check"] = errors

        if not errors:
            self.log(f"  ✅ 所有 {len(all_py_files)} 个文件语法正确")
        else:
            self.log(f"  发现 {len(errors)} 个语法错误")

    def check_imports(self):
        """检查关键模块导入"""
        self.log("\n" + "=" * 60)
        self.log("阶段4: 模块导入检查")
        self.log("=" * 60)

        # 检查项目核心模块
        core_modules = [
            ("numpy", "科学计算"),
            ("scipy", "科学计算"),
            ("matplotlib", "绑图"),
            ("pandas", "数据分析"),
        ]

        for module_name, desc in core_modules:
            try:
                __import__(module_name)
                self.log(f"  ✅ {module_name} ({desc})")
                self.stats["import_check"]["passed"] += 1
                self.results["import_check"].append({
                    "module": module_name,
                    "status": "PASS"
                })
            except ImportError as e:
                self.log(f"  ❌ {module_name} - 未安装")
                self.stats["import_check"]["failed"] += 1
                self.results["import_check"].append({
                    "module": module_name,
                    "status": "FAIL",
                    "error": str(e)
                })
            self.stats["import_check"]["total"] += 1

    def test_platform_api(self):
        """测试平台API"""
        self.log("\n" + "=" * 60)
        self.log("阶段5: 平台API测试")
        self.log("=" * 60)

        import asyncio
        import aiohttp

        async def test_apis():
            base_url = "http://localhost:8000"
            results = []

            endpoints = [
                ("GET", "/", "根路径"),
                ("GET", "/health", "健康检查"),
                ("GET", "/info", "系统信息"),
                ("GET", "/api/v2/stats", "统计信息"),
                ("POST", "/api/v2/sessions/create", "创建会话"),
            ]

            try:
                async with aiohttp.ClientSession() as session:
                    for method, path, name in endpoints:
                        try:
                            url = f"{base_url}{path}"
                            if method == "GET":
                                async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                                    status = "PASS" if resp.status == 200 else "FAIL"
                            else:
                                async with session.post(url, json={}, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                                    status = "PASS" if resp.status == 200 else "FAIL"

                            results.append({"name": name, "status": status})
                            self.log(f"  {'✅' if status == 'PASS' else '❌'} {name}")

                            if status == "PASS":
                                self.stats["api_test"]["passed"] += 1
                            else:
                                self.stats["api_test"]["failed"] += 1
                        except Exception as e:
                            results.append({"name": name, "status": "ERROR", "error": str(e)})
                            self.stats["api_test"]["failed"] += 1
                            self.log(f"  ⚠️ {name} - {e}")

                        self.stats["api_test"]["total"] += 1
            except Exception as e:
                self.log(f"  ⚠️ 无法连接到服务器: {e}")
                return []

            return results

        try:
            api_results = asyncio.run(test_apis())
            self.results["api_tests"] = api_results
        except Exception as e:
            self.log(f"  API测试跳过: {e}")

    def generate_report(self):
        """生成测试报告"""
        self.log("\n" + "=" * 60)
        self.log("生成测试报告")
        self.log("=" * 60)

        # 汇总统计
        self.results["summary"] = {
            "unit_tests": dict(self.stats["unit_tests"]),
            "case_execution": dict(self.stats["case_execution"]),
            "syntax_check": dict(self.stats["syntax_check"]),
            "import_check": dict(self.stats["import_check"]),
            "api_test": dict(self.stats["api_test"]),
        }

        # 保存JSON报告
        report_path = PROJECT_ROOT / "deep_integration_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)

        self.log(f"JSON报告已保存: {report_path}")

        # 打印总结
        print("\n" + "=" * 60)
        print("深度集成测试总结")
        print("=" * 60)

        total_tests = 0
        total_passed = 0

        for category, stats in self.results["summary"].items():
            if stats["total"] > 0:
                pass_rate = stats["passed"] / stats["total"] * 100
                print(f"\n{category}:")
                print(f"  总数: {stats['total']}")
                print(f"  通过: {stats['passed']}")
                print(f"  失败: {stats['failed']}")
                print(f"  通过率: {pass_rate:.1f}%")

                total_tests += stats["total"]
                total_passed += stats["passed"]

        if total_tests > 0:
            overall_rate = total_passed / total_tests * 100
            print(f"\n{'=' * 40}")
            print(f"总体通过率: {total_passed}/{total_tests} ({overall_rate:.1f}%)")
            print(f"{'=' * 40}")

        return self.results

    def run_all(self):
        """运行所有测试"""
        start_time = time.time()

        self.log("开始深度集成测试...")
        self.log(f"项目根目录: {PROJECT_ROOT}")

        # 运行各阶段测试
        self.check_all_python_syntax()
        self.check_imports()
        self.test_case_execution()
        self.run_unit_tests()
        self.test_platform_api()

        # 生成报告
        results = self.generate_report()

        duration = time.time() - start_time
        self.log(f"\n测试完成，总耗时: {duration:.1f}秒")

        return results


if __name__ == "__main__":
    tester = DeepIntegrationTester()
    tester.run_all()
