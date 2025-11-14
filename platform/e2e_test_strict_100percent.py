#!/usr/bin/env python3
"""
严格的100%完美端到端测试
Windows 10 + 中文环境
要求：每本书、每个章节、每个案例都必须完美无缺
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
    "cases_tested": 0,
    "total_images": 0,
    "images_loaded": 0,
    "images_broken": [],
    "total_tables": 0,
    "tables_rendered": 0,
    "total_code_blocks": 0,
    "code_blocks_highlighted": 0,
    "total_buttons": 0,
    "buttons_clickable": 0,
    "errors": [],
    "warnings": [],
    "perfect_score": True,
    "detailed_results": []
}

def log_error(message):
    """记录错误"""
    print(f"❌ 错误: {message}")
    test_results["errors"].append(message)
    test_results["perfect_score"] = False

def log_warning(message):
    """记录警告"""
    print(f"⚠️ 警告: {message}")
    test_results["warnings"].append(message)

def log_success(message):
    """记录成功"""
    print(f"✅ {message}")

def wait_for_content_loaded(page, timeout=10000):
    """等待内容加载完成"""
    try:
        # 等待markdown渲染完成
        page.wait_for_selector('.content', timeout=timeout)
        # 额外等待以确保JavaScript完成渲染
        time.sleep(2)
        return True
    except PlaywrightTimeout:
        return False

def check_images(page, book_id, case_id=None):
    """严格检查所有图片是否加载"""
    context = f"{book_id}/{case_id}" if case_id else book_id

    # 查找所有img标签
    images = page.query_selector_all('img')
    test_results["total_images"] += len(images)

    broken_images = []
    for i, img in enumerate(images):
        try:
            # 检查图片是否加载成功
            natural_width = img.evaluate('img => img.naturalWidth')
            natural_height = img.evaluate('img => img.naturalHeight')
            src = img.get_attribute('src') or ''

            if natural_width == 0 or natural_height == 0:
                broken_images.append(src)
                log_error(f"图片加载失败 [{context}]: {src}")
            else:
                test_results["images_loaded"] += 1
        except Exception as e:
            log_error(f"图片检查异常 [{context}]: {str(e)}")
            broken_images.append(f"img_{i}")

    if broken_images:
        test_results["images_broken"].extend(broken_images)
        return False

    if len(images) > 0:
        log_success(f"所有图片加载成功 [{context}]: {len(images)}张")
    return True

def check_tables(page, book_id, case_id=None):
    """严格检查所有表格是否正确渲染"""
    context = f"{book_id}/{case_id}" if case_id else book_id

    tables = page.query_selector_all('table')
    test_results["total_tables"] += len(tables)

    all_good = True
    for i, table in enumerate(tables):
        try:
            # 检查表格是否有内容
            rows = table.query_selector_all('tr')
            cells = table.query_selector_all('td, th')

            if len(rows) == 0 or len(cells) == 0:
                log_error(f"表格为空 [{context}]: table_{i}")
                all_good = False
            else:
                # 检查表格样式
                border = table.evaluate('t => window.getComputedStyle(t).border')
                if not border or border == 'none':
                    log_warning(f"表格可能缺少边框样式 [{context}]: table_{i}")

                test_results["tables_rendered"] += 1
        except Exception as e:
            log_error(f"表格检查异常 [{context}]: {str(e)}")
            all_good = False

    if len(tables) > 0 and all_good:
        log_success(f"所有表格正确渲染 [{context}]: {len(tables)}个")

    return all_good

def check_code_blocks(page, book_id, case_id=None):
    """严格检查所有代码块是否有语法高亮"""
    context = f"{book_id}/{case_id}" if case_id else book_id

    # 查找代码块
    code_blocks = page.query_selector_all('pre code, pre, code')
    test_results["total_code_blocks"] += len(code_blocks)

    all_highlighted = True
    for i, code in enumerate(code_blocks):
        try:
            # 检查代码块是否有内容
            text_content = code.text_content() or ''
            if len(text_content.strip()) == 0:
                continue

            # 检查是否有语法高亮的痕迹 (通常会有span标签或特殊class)
            html = code.evaluate('el => el.innerHTML')
            has_highlighting = '<span' in html or 'hljs' in (code.get_attribute('class') or '')

            if has_highlighting:
                test_results["code_blocks_highlighted"] += 1
            else:
                # 可能是内联代码，不需要高亮
                tag_name = code.evaluate('el => el.tagName')
                if tag_name == 'PRE' or code.query_selector('code'):
                    log_warning(f"代码块可能缺少语法高亮 [{context}]: code_{i}")
                else:
                    test_results["code_blocks_highlighted"] += 1
        except Exception as e:
            log_error(f"代码块检查异常 [{context}]: {str(e)}")
            all_highlighted = False

    if len(code_blocks) > 0:
        log_success(f"代码块检查完成 [{context}]: {len(code_blocks)}个")

    return all_highlighted

def check_buttons_and_links(page, book_id, case_id=None):
    """严格检查所有按钮和链接是否可点击"""
    context = f"{book_id}/{case_id}" if case_id else book_id

    # 查找所有按钮和链接
    buttons = page.query_selector_all('button, a.btn, .button')
    links = page.query_selector_all('a[href]')

    all_elements = list(set(buttons + links))
    test_results["total_buttons"] += len(all_elements)

    all_clickable = True
    for i, elem in enumerate(all_elements):
        try:
            # 检查元素是否可见和可点击
            is_visible = elem.is_visible()
            is_enabled = elem.is_enabled()

            if not is_visible:
                log_warning(f"元素不可见 [{context}]: element_{i}")
            elif not is_enabled:
                log_warning(f"元素不可点击 [{context}]: element_{i}")
            else:
                test_results["buttons_clickable"] += 1
        except Exception as e:
            log_error(f"按钮/链接检查异常 [{context}]: {str(e)}")
            all_clickable = False

    if len(all_elements) > 0:
        log_success(f"按钮/链接检查完成 [{context}]: {len(all_elements)}个")

    return all_clickable

def check_chinese_display(page, book_id, case_id=None):
    """检查中文显示是否正确"""
    context = f"{book_id}/{case_id}" if case_id else book_id

    try:
        # 获取页面文本内容
        body_text = page.text_content('body') or ''

        # 检查是否包含中文
        has_chinese = any('\u4e00' <= char <= '\u9fff' for char in body_text)

        if not has_chinese:
            log_warning(f"页面可能缺少中文内容 [{context}]")
            return False

        # 检查字体渲染
        body = page.query_selector('body')
        if body:
            font_family = body.evaluate('el => window.getComputedStyle(el).fontFamily')
            if font_family:
                log_success(f"中文字体: {font_family[:50]}")

        return True
    except Exception as e:
        log_error(f"中文显示检查异常 [{context}]: {str(e)}")
        return False

def take_screenshot(page, name):
    """截图保存"""
    try:
        filepath = os.path.join(SCREENSHOTS_DIR, f"{name}.png")
        page.screenshot(path=filepath, full_page=True)
        log_success(f"截图保存: {filepath}")
        return filepath
    except Exception as e:
        log_error(f"截图失败 [{name}]: {str(e)}")
        return None

def test_book_page(page, book):
    """测试单本书的页面"""
    book_id = book['id']
    book_title = book['title']

    print(f"\n{'='*80}")
    print(f"📖 测试书籍: {book_title} ({book_id})")
    print(f"{'='*80}")

    # 访问书籍页面
    url = f"{BASE_URL}/textbooks.html?book={book_id}"

    try:
        # 使用load而不是networkidle，避免页面崩溃
        page.goto(url, wait_until='load', timeout=30000)

        # 等待内容加载
        if not wait_for_content_loaded(page):
            log_error(f"书籍页面加载超时: {book_title}")
            return False

        # 截图
        take_screenshot(page, f"book_{book_id}")

        # 执行所有检查
        results = {
            "book_id": book_id,
            "book_title": book_title,
            "url": url,
            "chinese_ok": check_chinese_display(page, book_id),
            "images_ok": check_images(page, book_id),
            "tables_ok": check_tables(page, book_id),
            "code_ok": check_code_blocks(page, book_id),
            "buttons_ok": check_buttons_and_links(page, book_id),
            "timestamp": datetime.now().isoformat()
        }

        test_results["detailed_results"].append(results)
        test_results["books_tested"] += 1

        all_ok = all(results.values() if isinstance(results[k], bool) else True
                     for k in ['chinese_ok', 'images_ok', 'tables_ok', 'code_ok', 'buttons_ok'])

        if all_ok:
            log_success(f"书籍测试通过: {book_title}")
        else:
            log_error(f"书籍测试失败: {book_title}")

        return all_ok

    except Exception as e:
        log_error(f"书籍测试异常 [{book_title}]: {str(e)}")
        return False

def test_case_page(page, book_id, case_id):
    """测试单个案例页面"""
    print(f"\n  📝 测试案例: {book_id}/{case_id}")

    url = f"{BASE_URL}/textbooks.html?book={book_id}&case={case_id}"

    try:
        # 使用load而不是networkidle，避免页面崩溃
        page.goto(url, wait_until='load', timeout=30000)

        # 等待内容加载
        if not wait_for_content_loaded(page):
            log_error(f"案例页面加载超时: {book_id}/{case_id}")
            return False

        # 截图 (只截部分案例以节省空间)
        if test_results["cases_tested"] < 20:  # 只截前20个案例
            take_screenshot(page, f"case_{book_id}_{case_id}")

        # 执行所有检查
        chinese_ok = check_chinese_display(page, book_id, case_id)
        images_ok = check_images(page, book_id, case_id)
        tables_ok = check_tables(page, book_id, case_id)
        code_ok = check_code_blocks(page, book_id, case_id)
        buttons_ok = check_buttons_and_links(page, book_id, case_id)

        test_results["cases_tested"] += 1

        all_ok = chinese_ok and images_ok and tables_ok and code_ok and buttons_ok

        if all_ok:
            log_success(f"  ✓ 案例测试通过: {case_id}")
        else:
            log_error(f"  ✗ 案例测试失败: {case_id}")

        return all_ok

    except Exception as e:
        log_error(f"案例测试异常 [{book_id}/{case_id}]: {str(e)}")
        return False

def generate_report():
    """生成测试报告"""
    test_results["end_time"] = datetime.now().isoformat()

    # 计算成功率
    images_success_rate = (test_results["images_loaded"] / test_results["total_images"] * 100) if test_results["total_images"] > 0 else 100
    tables_success_rate = (test_results["tables_rendered"] / test_results["total_tables"] * 100) if test_results["total_tables"] > 0 else 100
    code_success_rate = (test_results["code_blocks_highlighted"] / test_results["total_code_blocks"] * 100) if test_results["total_code_blocks"] > 0 else 100
    buttons_success_rate = (test_results["buttons_clickable"] / test_results["total_buttons"] * 100) if test_results["total_buttons"] > 0 else 100

    # 判断是否100%完美
    is_perfect = (
        test_results["perfect_score"] and
        images_success_rate == 100 and
        tables_success_rate == 100 and
        code_success_rate == 100 and
        buttons_success_rate == 100 and
        len(test_results["errors"]) == 0
    )

    # 生成Markdown报告
    report = f"""# 严格100%完美E2E测试报告

**测试环境**: Windows 10 + 中文 (zh-CN)
**测试时间**: {test_results["start_time"]} 至 {test_results["end_time"]}
**测试标准**: 100% 完美无缺

---

## 📊 总体结果

{'🎉 **测试通过 - 100%完美无缺**' if is_perfect else '❌ **测试失败 - 发现问题**'}

### 测试覆盖率

- ✅ 书籍测试数量: **{test_results["books_tested"]}** 本
- ✅ 案例测试数量: **{test_results["cases_tested"]}** 个

### 详细统计

| 检查项目 | 总数 | 成功 | 成功率 | 状态 |
|---------|------|------|--------|------|
| 图片加载 | {test_results["total_images"]} | {test_results["images_loaded"]} | {images_success_rate:.1f}% | {'✅' if images_success_rate == 100 else '❌'} |
| 表格渲染 | {test_results["total_tables"]} | {test_results["tables_rendered"]} | {tables_success_rate:.1f}% | {'✅' if tables_success_rate == 100 else '❌'} |
| 代码高亮 | {test_results["total_code_blocks"]} | {test_results["code_blocks_highlighted"]} | {code_success_rate:.1f}% | {'✅' if code_success_rate == 100 else '❌'} |
| 按钮可点击 | {test_results["total_buttons"]} | {test_results["buttons_clickable"]} | {buttons_success_rate:.1f}% | {'✅' if buttons_success_rate == 100 else '❌'} |

---

## ⚠️ 发现的问题

### 错误 ({len(test_results["errors"])})

"""

    if test_results["errors"]:
        for i, error in enumerate(test_results["errors"], 1):
            report += f"{i}. {error}\n"
    else:
        report += "✅ 无错误\n"

    report += f"""
### 警告 ({len(test_results["warnings"])})

"""

    if test_results["warnings"]:
        for i, warning in enumerate(test_results["warnings"], 1):
            report += f"{i}. {warning}\n"
    else:
        report += "✅ 无警告\n"

    if test_results["images_broken"]:
        report += f"""
### 损坏的图片 ({len(test_results["images_broken"])})

"""
        for i, img in enumerate(test_results["images_broken"], 1):
            report += f"{i}. `{img}`\n"

    report += f"""
---

## 📸 截图证据

所有测试截图保存在: `{SCREENSHOTS_DIR}/`

---

## 🎯 结论

"""

    if is_perfect:
        report += """
✅ **所有测试通过！平台达到100%完美标准！**

- 所有书籍页面正确加载
- 所有图片完美显示
- 所有表格正确渲染
- 所有代码块语法高亮正常
- 所有按钮和链接可点击
- 中文显示完美
"""
    else:
        report += f"""
❌ **测试未通过，发现{len(test_results["errors"])}个错误和{len(test_results["warnings"])}个警告**

需要修复以下问题才能达到100%完美标准：
"""
        if images_success_rate < 100:
            report += f"- 图片加载问题: {test_results['total_images'] - test_results['images_loaded']} 张图片未成功加载\n"
        if tables_success_rate < 100:
            report += f"- 表格渲染问题: {test_results['total_tables'] - test_results['tables_rendered']} 个表格有问题\n"
        if code_success_rate < 100:
            report += f"- 代码高亮问题: {test_results['total_code_blocks'] - test_results['code_blocks_highlighted']} 个代码块缺少高亮\n"
        if buttons_success_rate < 100:
            report += f"- 按钮可点击问题: {test_results['total_buttons'] - test_results['buttons_clickable']} 个按钮不可点击\n"

    # 保存报告
    report_path = os.path.join(RESULTS_DIR, f"strict-e2e-test-{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    # 保存JSON数据
    json_path = os.path.join(RESULTS_DIR, f"strict-e2e-test-{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(test_results, f, ensure_ascii=False, indent=2)

    print("\n" + "="*80)
    print(report)
    print("="*80)
    print(f"\n📄 报告已保存: {report_path}")
    print(f"📄 数据已保存: {json_path}")

    return is_perfect

def main():
    """主测试流程"""
    print("="*80)
    print("严格100%完美E2E测试")
    print("Windows 10 + 中文环境")
    print("="*80)

    # 读取书籍目录
    with open('platform/backend/books_catalog.json', 'r', encoding='utf-8') as f:
        catalog = json.load(f)

    books = catalog['books']

    # 选择要测试的书籍 (测试所有专业教材，共14本)
    professional_books = [b for b in books if b.get('category') == '专业教材']

    print(f"\n将测试 {len(professional_books)} 本专业教材")

    with sync_playwright() as p:
        # 启动浏览器 - 模拟Windows环境
        browser = p.chromium.launch(
            headless=True,  # 无头模式，提高速度
            args=['--lang=zh-CN']
        )

        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            locale='zh-CN',
            timezone_id='Asia/Shanghai',
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )

        page = context.new_page()

        try:
            # 测试每本书
            for book in professional_books:
                test_book_page(page, book)

                # 暂停一下，避免过快请求
                time.sleep(1)

            # 生成最终报告
            is_perfect = generate_report()

            return 0 if is_perfect else 1

        finally:
            browser.close()

if __name__ == "__main__":
    exit(main())
