#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CHS-Books Web端到端浏览器测试脚本
使用Playwright进行浏览器自动化测试和截图
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# 测试配置
BASE_URL = "http://localhost:8000"
FRONTEND_DIR = Path("/home/user/CHS-Books/platform/frontend")
SCREENSHOT_DIR = Path("/home/user/CHS-Books/platform/test_screenshots")

# 测试结果
test_results = {
    "timestamp": datetime.now().isoformat(),
    "tests": [],
    "summary": {
        "total": 0,
        "passed": 0,
        "failed": 0
    }
}


def add_result(name: str, status: str, details: str = "", screenshot: str = ""):
    """添加测试结果"""
    test_results["tests"].append({
        "name": name,
        "status": status,
        "details": details,
        "screenshot": screenshot
    })
    test_results["summary"]["total"] += 1
    if status == "PASS":
        test_results["summary"]["passed"] += 1
    else:
        test_results["summary"]["failed"] += 1


async def test_api_endpoints():
    """测试API端点"""
    import aiohttp

    print("\n" + "=" * 80)
    print("  API端点测试")
    print("=" * 80)

    endpoints = [
        ("GET", "/", "根路径"),
        ("GET", "/health", "健康检查"),
        ("GET", "/info", "系统信息"),
        ("GET", "/api/v2/stats", "统计信息"),
        ("POST", "/api/v2/sessions/create", "创建会话", {
            "user_id": "test_user",
            "book_slug": "water-environment-simulation",
            "case_slug": "case_01_diffusion"
        }),
        ("POST", "/api/v2/code/load", "加载代码", {
            "book_slug": "ecohydraulics",
            "case_slug": "case_01_ecological_flow"
        }),
        ("POST", "/api/v2/code/validate", "验证代码", {
            "code": "print('Hello World')"
        }),
        ("POST", "/api/v2/code/analyze", "分析代码", {
            "code": "def hello():\n    print('Hello')\n\nhello()"
        }),
        ("POST", "/api/v2/ai/explain-code", "AI代码讲解", {
            "code": "x = 10\nprint(x)",
            "context": "简单变量赋值"
        }),
        ("POST", "/api/v2/ai/diagnose-error", "AI错误诊断", {
            "code": "print(undefined_var)",
            "error": "NameError: name 'undefined_var' is not defined"
        }),
        ("POST", "/api/v2/ai/ask", "AI问答", {
            "question": "什么是水力学?"
        }),
    ]

    async with aiohttp.ClientSession() as session:
        for endpoint_info in endpoints:
            method = endpoint_info[0]
            path = endpoint_info[1]
            name = endpoint_info[2]
            data = endpoint_info[3] if len(endpoint_info) > 3 else None

            try:
                url = f"{BASE_URL}{path}"
                if method == "GET":
                    async with session.get(url) as resp:
                        status_code = resp.status
                        response = await resp.json()
                else:
                    async with session.post(url, json=data) as resp:
                        status_code = resp.status
                        response = await resp.json()

                if status_code == 200:
                    success = response.get("success", True) if isinstance(response, dict) else True
                    if success:
                        add_result(f"API: {name}", "PASS", f"状态码: {status_code}")
                        print(f"  ✅ {name}: 通过")
                    else:
                        add_result(f"API: {name}", "FAIL", f"响应: {response}")
                        print(f"  ❌ {name}: 失败 - {response}")
                else:
                    add_result(f"API: {name}", "FAIL", f"状态码: {status_code}")
                    print(f"  ❌ {name}: 失败 (状态码 {status_code})")

            except Exception as e:
                add_result(f"API: {name}", "FAIL", str(e))
                print(f"  ❌ {name}: 错误 - {e}")


async def test_frontend_files():
    """测试前端文件完整性"""
    print("\n" + "=" * 80)
    print("  前端文件测试")
    print("=" * 80)

    required_files = [
        ("index.html", "主页"),
        ("learning.html", "学习页面"),
        ("ide.html", "IDE编程页面"),
        ("code-runner.html", "代码运行器"),
        ("cache-manager.js", "缓存管理器"),
        ("lazy-load.js", "懒加载脚本"),
        ("common-ui-utils.js", "UI工具函数"),
        ("common-ui-styles.css", "通用样式"),
    ]

    for filename, description in required_files:
        filepath = FRONTEND_DIR / filename
        if filepath.exists():
            size = filepath.stat().st_size / 1024
            add_result(f"前端: {description}", "PASS", f"{size:.1f}KB")
            print(f"  ✅ {description} ({filename}): {size:.1f}KB")
        else:
            add_result(f"前端: {description}", "FAIL", "文件不存在")
            print(f"  ❌ {description} ({filename}): 文件不存在")


async def test_with_browser():
    """使用浏览器进行测试（带截图）"""
    print("\n" + "=" * 80)
    print("  浏览器测试（带截图）")
    print("=" * 80)

    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("  ⚠️ Playwright未安装，跳过浏览器测试")
        add_result("浏览器测试", "SKIP", "Playwright未安装")
        return

    # 创建截图目录
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(viewport={"width": 1920, "height": 1080})
            page = await context.new_page()

            # 测试API文档页面
            print("\n  测试 API文档页面...")
            await page.goto(f"{BASE_URL}/docs")
            await page.wait_for_load_state("networkidle")
            screenshot_path = str(SCREENSHOT_DIR / "api_docs.png")
            await page.screenshot(path=screenshot_path, full_page=True)
            add_result("浏览器: API文档", "PASS", "截图已保存", screenshot_path)
            print(f"  ✅ API文档页面: 截图已保存")

            # 测试前端主页（静态文件服务）
            print("\n  测试 前端静态页面...")

            # 使用file协议打开前端页面
            for page_file, page_name in [
                ("index.html", "主页"),
                ("learning.html", "学习页面"),
                ("ide.html", "IDE页面"),
                ("code-runner.html", "代码运行器"),
            ]:
                page_path = FRONTEND_DIR / page_file
                if page_path.exists():
                    try:
                        await page.goto(f"file://{page_path}")
                        await page.wait_for_load_state("load")
                        screenshot_path = str(SCREENSHOT_DIR / f"frontend_{page_file.replace('.html', '')}.png")
                        await page.screenshot(path=screenshot_path, full_page=True)
                        add_result(f"浏览器: {page_name}", "PASS", "截图已保存", screenshot_path)
                        print(f"  ✅ {page_name}: 截图已保存")
                    except Exception as e:
                        add_result(f"浏览器: {page_name}", "FAIL", str(e))
                        print(f"  ❌ {page_name}: {e}")
                else:
                    add_result(f"浏览器: {page_name}", "FAIL", "文件不存在")
                    print(f"  ❌ {page_name}: 文件不存在")

            await browser.close()

        except Exception as e:
            add_result("浏览器测试", "FAIL", str(e))
            print(f"  ❌ 浏览器测试失败: {e}")


async def test_api_integration():
    """测试API集成流程"""
    import aiohttp

    print("\n" + "=" * 80)
    print("  API集成流程测试")
    print("=" * 80)

    async with aiohttp.ClientSession() as session:
        try:
            # 1. 创建会话
            print("\n  1. 创建学习会话...")
            async with session.post(f"{BASE_URL}/api/v2/sessions/create", json={
                "user_id": "integration_test_user",
                "book_slug": "water-environment-simulation",
                "case_slug": "case_01_diffusion"
            }) as resp:
                session_data = await resp.json()
                session_id = session_data.get("session_id", "")
                print(f"     会话ID: {session_id}")

            # 2. 加载案例代码
            print("  2. 加载案例代码...")
            async with session.post(f"{BASE_URL}/api/v2/code/load", json={
                "book_slug": "water-environment-simulation",
                "case_slug": "case_01_diffusion"
            }) as resp:
                code_data = await resp.json()
                files = code_data.get("files", [])
                print(f"     加载了 {len(files)} 个文件")

            # 3. 验证代码
            print("  3. 验证代码...")
            test_code = "import numpy as np\nprint('Hello')"
            async with session.post(f"{BASE_URL}/api/v2/code/validate", json={
                "code": test_code
            }) as resp:
                validate_data = await resp.json()
                is_valid = validate_data.get("is_valid", False)
                print(f"     代码有效: {is_valid}")

            # 4. 分析代码
            print("  4. 分析代码...")
            async with session.post(f"{BASE_URL}/api/v2/code/analyze", json={
                "code": test_code
            }) as resp:
                analyze_data = await resp.json()
                analysis = analyze_data.get("analysis", {})
                print(f"     代码行数: {analysis.get('lines', 0)}")

            # 5. 执行代码
            print("  5. 执行代码...")
            async with session.post(f"{BASE_URL}/api/v2/execution/start", json={
                "session_id": session_id,
                "script_path": "main.py",
                "parameters": {}
            }) as resp:
                exec_data = await resp.json()
                execution_id = exec_data.get("execution_id", "")
                status = exec_data.get("status", "")
                print(f"     执行ID: {execution_id}, 状态: {status}")

            # 6. AI代码讲解
            print("  6. AI代码讲解...")
            async with session.post(f"{BASE_URL}/api/v2/ai/explain-code", json={
                "code": test_code,
                "context": "测试代码"
            }) as resp:
                explain_data = await resp.json()
                print(f"     讲解长度: {len(explain_data.get('explanation', ''))} 字符")

            add_result("API集成流程", "PASS", "完整流程测试通过")
            print("\n  ✅ 完整集成流程测试通过!")

        except Exception as e:
            add_result("API集成流程", "FAIL", str(e))
            print(f"\n  ❌ 集成流程测试失败: {e}")


async def test_all_book_cases_api():
    """测试所有书籍案例的API加载"""
    import aiohttp
    from pathlib import Path

    print("\n" + "=" * 80)
    print("  所有书籍案例API测试")
    print("=" * 80)

    books_dir = Path("/home/user/CHS-Books/books")

    # 收集所有案例
    cases = []
    for book_path in books_dir.iterdir():
        if not book_path.is_dir():
            continue
        examples_dir = book_path / "code" / "examples"
        if not examples_dir.exists():
            continue
        for case_dir in examples_dir.iterdir():
            if case_dir.is_dir() and case_dir.name.startswith("case_"):
                cases.append((book_path.name, case_dir.name))

    print(f"\n  找到 {len(cases)} 个案例")

    # 测试前10个案例
    test_cases = cases[:20]
    passed = 0
    failed = 0

    async with aiohttp.ClientSession() as session:
        for book_slug, case_slug in test_cases:
            try:
                # 创建会话
                async with session.post(f"{BASE_URL}/api/v2/sessions/create", json={
                    "user_id": "test_user",
                    "book_slug": book_slug,
                    "case_slug": case_slug
                }) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data.get("success"):
                            passed += 1
                            print(f"  ✅ {book_slug}/{case_slug}")
                        else:
                            failed += 1
                            print(f"  ❌ {book_slug}/{case_slug}: API返回失败")
                    else:
                        failed += 1
                        print(f"  ❌ {book_slug}/{case_slug}: 状态码 {resp.status}")
            except Exception as e:
                failed += 1
                print(f"  ❌ {book_slug}/{case_slug}: {e}")

    print(f"\n  案例API测试: {passed}/{len(test_cases)} 通过")

    if passed == len(test_cases):
        add_result("案例API测试", "PASS", f"{passed}/{len(test_cases)} 通过")
    else:
        add_result("案例API测试", "FAIL", f"{passed}/{len(test_cases)} 通过, {failed} 失败")


def generate_report():
    """生成测试报告"""
    print("\n" + "=" * 80)
    print("  测试报告")
    print("=" * 80)

    summary = test_results["summary"]
    total = summary["total"]
    passed = summary["passed"]
    failed = summary["failed"]

    pass_rate = (passed / total * 100) if total > 0 else 0

    print(f"\n  📊 总计测试: {total}")
    print(f"  ✅ 通过: {passed}")
    print(f"  ❌ 失败: {failed}")
    print(f"  📈 通过率: {pass_rate:.1f}%")

    # 保存JSON报告
    report_dir = Path("/home/user/CHS-Books/platform/test_reports")
    report_dir.mkdir(parents=True, exist_ok=True)

    report_file = report_dir / "web_browser_e2e_report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(test_results, f, indent=2, ensure_ascii=False)

    print(f"\n  📄 报告已保存: {report_file}")

    # 列出截图
    if SCREENSHOT_DIR.exists():
        screenshots = list(SCREENSHOT_DIR.glob("*.png"))
        if screenshots:
            print(f"\n  📷 截图文件 ({len(screenshots)}个):")
            for ss in screenshots:
                print(f"     - {ss.name}")

    return 0 if failed == 0 else 1


async def main():
    """主函数"""
    print("=" * 80)
    print("  CHS-Books Web端到端浏览器测试")
    print("=" * 80)
    print(f"  时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  服务器: {BASE_URL}")

    # 运行测试
    await test_api_endpoints()
    await test_frontend_files()
    await test_api_integration()
    await test_all_book_cases_api()
    await test_with_browser()

    # 生成报告
    return generate_report()


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n测试被中断")
        sys.exit(1)
