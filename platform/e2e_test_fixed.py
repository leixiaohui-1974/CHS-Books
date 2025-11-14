#!/usr/bin/env python3
"""
修复版端到端测试 - 测试前端页面显示
"""

import json
import time
import os
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import sys

# 配置
BASE_URL = "http://localhost:8080"
SCREENSHOTS_DIR = "/home/user/CHS-Books/platform/test_reports/screenshots"
RESULTS_DIR = "/home/user/CHS-Books/platform/test_reports"

# 确保目录存在
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# 测试结果
test_results = {
    "start_time": datetime.now().isoformat(),
    "books_tested": 0,
    "pages_loaded": 0,
    "pages_failed": 0,
    "errors": [],
    "warnings": [],
    "screenshots": []
}

def log_info(message):
    """记录信息"""
    print(f"ℹ️  {message}")

def log_error(message):
    """记录错误"""
    print(f"❌ {message}")
    test_results["errors"].append(message)

def log_success(message):
    """记录成功"""
    print(f"✅ {message}")

def take_screenshot(page, name):
    """截图"""
    try:
        filepath = os.path.join(SCREENSHOTS_DIR, f"{name}.png")
        page.screenshot(path=filepath, full_page=True)
        log_success(f"截图保存: {name}.png")
        test_results["screenshots"].append(filepath)
        return filepath
    except Exception as e:
        log_error(f"截图失败 [{name}]: {str(e)}")
        return None

def test_page(page, url, name):
    """测试单个页面"""
    log_info(f"\n测试: {name}")
    log_info(f"URL: {url}")

    try:
        # 使用load等待策略，避免崩溃
        response = page.goto(url, wait_until='load', timeout=15000)

        if not response:
            log_error(f"{name}: 无响应")
            test_results["pages_failed"] += 1
            return False

        status = response.status
        log_info(f"HTTP状态: {status}")

        if status != 200:
            log_error(f"{name}: HTTP {status}")
            test_results["pages_failed"] += 1
            return False

        # 等待页面渲染
        time.sleep(2)

        # 截图
        take_screenshot(page, name.replace(" ", "_").replace("/", "-"))

        # 检查中文内容（通过JavaScript）
        try:
            text = page.evaluate("() => document.body.innerText")
            has_chinese = any('\u4e00' <= char <= '\u9fff' for char in (text or '')[:500])
            if has_chinese:
                log_success(f"{name}: 包含中文内容")
            else:
                log_info(f"{name}: 未检测到中文内容（可能需要JS渲染）")
        except Exception as e:
            log_info(f"内容检查跳过: {e}")

        test_results["pages_loaded"] += 1
        log_success(f"{name}: 测试通过")
        return True

    except PlaywrightTimeout as e:
        log_error(f"{name}: 超时 - {str(e)}")
        test_results["pages_failed"] += 1
        return False
    except Exception as e:
        log_error(f"{name}: 异常 - {str(e)}")
        test_results["pages_failed"] += 1
        return False

def main():
    """主测试流程"""
    print("="*80)
    print("修复版E2E测试 - 前端页面显示测试")
    print("="*80)

    # 读取书籍目录
    catalog_path = '/home/user/CHS-Books/platform/backend/books_catalog.json'
    try:
        with open(catalog_path, 'r', encoding='utf-8') as f:
            catalog = json.load(f)
        books = catalog['books'][:5]  # 只测试前5本书
        log_info(f"将测试 {len(books)} 本书")
    except Exception as e:
        log_error(f"无法加载书籍目录: {e}")
        return 1

    with sync_playwright() as p:
        # 启动浏览器
        browser = p.chromium.launch(
            headless=True,
            args=['--lang=zh-CN', '--disable-dev-shm-usage', '--no-sandbox']
        )

        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            locale='zh-CN',
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0'
        )

        page = context.new_page()

        try:
            # 测试核心页面
            log_info("\n" + "="*80)
            log_info("第1部分: 核心页面测试")
            log_info("="*80)

            core_pages = [
                (f"{BASE_URL}/index.html", "主页"),
                (f"{BASE_URL}/textbooks.html", "教材库页面"),
            ]

            for url, name in core_pages:
                test_page(page, url, name)
                time.sleep(1)

            # 测试书籍页面
            log_info("\n" + "="*80)
            log_info("第2部分: 书籍页面测试")
            log_info("="*80)

            for book in books:
                book_url = f"{BASE_URL}/textbooks.html?book={book['slug']}"
                test_page(page, book_url, f"书籍: {book['title']}")
                test_results["books_tested"] += 1
                time.sleep(1)

        finally:
            browser.close()

    # 生成报告
    test_results["end_time"] = datetime.now().isoformat()

    # 保存JSON报告
    report_path = os.path.join(RESULTS_DIR, f"e2e-test-fixed-{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(test_results, f, ensure_ascii=False, indent=2)

    # 打印总结
    print("\n" + "="*80)
    print("测试总结")
    print("="*80)
    print(f"✅ 页面加载成功: {test_results['pages_loaded']}")
    print(f"❌ 页面加载失败: {test_results['pages_failed']}")
    print(f"📚 书籍测试数量: {test_results['books_tested']}")
    print(f"📸 截图数量: {len(test_results['screenshots'])}")
    print(f"❌ 错误数量: {len(test_results['errors'])}")
    print(f"\n📄 报告已保存: {report_path}")

    if test_results['errors']:
        print("\n错误列表:")
        for i, error in enumerate(test_results['errors'][:10], 1):
            print(f"  {i}. {error}")

    # 返回退出码
    return 0 if test_results['pages_failed'] == 0 else 1

if __name__ == "__main__":
    exit(main())
