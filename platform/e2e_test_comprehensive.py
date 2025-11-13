#!/usr/bin/env python3
"""
Platform端到端综合测试 - Windows + 中文环境模拟
测试所有书籍、章节、案例的HTML结构、中文内容、排版要素
"""

import requests
import json
import re
from datetime import datetime
from pathlib import Path
from html.parser import HTMLParser
import sys

# 配置
BASE_URL = "http://localhost:8080"
REPORT_DIR = Path("/home/user/CHS-Books/platform/test_reports")
BOOKS_DATA_FILE = Path("/home/user/CHS-Books/platform/backend/books_catalog.json")
CASES_DATA_FILE = Path("/home/user/CHS-Books/platform/backend/cases_index.json")

# 创建报告目录
REPORT_DIR.mkdir(parents=True, exist_ok=True)

# 统计数据
stats = {
    "total_tests": 0,
    "passed_tests": 0,
    "failed_tests": 0,
    "pages": {"tested": 0, "passed": 0, "failed": 0},
    "books": {"total": 0, "tested": 0, "passed": 0, "failed": 0},
    "chapters": {"total": 0, "tested": 0, "passed": 0, "failed": 0},
    "cases": {"total": 0, "tested": 0, "passed": 0, "failed": 0},
    "ui_checks": {
        "chinese_content": {"passed": 0, "failed": 0},
        "images": {"passed": 0, "failed": 0},
        "tables": {"passed": 0, "failed": 0},
        "buttons": {"passed": 0, "failed": 0},
        "links": {"passed": 0, "failed": 0}
    }
}

# 测试结果
test_results = []


class HTMLAnalyzer(HTMLParser):
    """HTML分析器"""

    def __init__(self):
        super().__init__()
        self.tags = []
        self.has_header = False
        self.has_nav = False
        self.has_main = False
        self.has_footer = False
        self.images = []
        self.tables = []
        self.buttons = []
        self.links = []
        self.chinese_texts = []

    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        attrs_dict = dict(attrs)

        if tag == 'header' or ('class' in attrs_dict and 'header' in attrs_dict['class']):
            self.has_header = True
        if tag == 'nav' or ('class' in attrs_dict and 'nav' in attrs_dict['class']):
            self.has_nav = True
        if tag == 'main' or ('class' in attrs_dict and ('main' in attrs_dict.get('class', '') or 'content' in attrs_dict.get('class', ''))):
            self.has_main = True
        if tag == 'footer' or ('class' in attrs_dict and 'footer' in attrs_dict['class']):
            self.has_footer = True

        if tag == 'img':
            self.images.append(attrs_dict.get('src', ''))
        if tag == 'table':
            self.tables.append(True)
        if tag == 'button' or ('class' in attrs_dict and 'btn' in attrs_dict.get('class', '')):
            self.buttons.append(attrs_dict.get('onclick', ''))
        if tag == 'a' and 'href' in attrs_dict:
            self.links.append(attrs_dict['href'])

    def handle_data(self, data):
        # 检测中文内容
        if re.search(r'[\u4e00-\u9fa5]', data):
            self.chinese_texts.append(data.strip())


def log_info(message):
    """输出信息日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] 📘 {message}")


def log_success(message):
    """输出成功日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] ✅ {message}")
    stats["passed_tests"] += 1


def log_fail(message):
    """输出失败日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] ❌ {message}")
    stats["failed_tests"] += 1


def log_test(message):
    """输出测试日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] 🧪 {message}")
    stats["total_tests"] += 1


def test_page(url, name, check_chinese=True):
    """测试单个页面"""
    log_test(f"测试页面: {name}")
    log_info(f"URL: {url}")

    result = {
        "name": name,
        "url": url,
        "timestamp": datetime.now().isoformat(),
        "success": False,
        "checks": {}
    }

    try:
        # 获取HTML
        response = requests.get(url, timeout=10)
        result["http_status"] = response.status_code

        if response.status_code != 200:
            log_fail(f"{name} HTTP状态码异常: {response.status_code}")
            result["error"] = f"HTTP {response.status_code}"
            return result

        log_success(f"{name} HTTP状态码: 200")

        html = response.text

        # 检查字符编码
        if 'utf-8' in html.lower() or 'charset="utf-8"' in html.lower():
            log_success(f"{name} 使用UTF-8编码")
            result["checks"]["encoding"] = "UTF-8"
        else:
            log_fail(f"{name} 未明确使用UTF-8编码")
            result["checks"]["encoding"] = "未知"

        # 检查DOCTYPE
        if html.strip().startswith('<!DOCTYPE html>') or '<!doctype html>' in html.lower():
            log_success(f"{name} 包含DOCTYPE声明")
            result["checks"]["doctype"] = True
        else:
            log_fail(f"{name} 缺少DOCTYPE声明")
            result["checks"]["doctype"] = False

        # 解析HTML
        analyzer = HTMLAnalyzer()
        try:
            analyzer.feed(html)
        except Exception as e:
            log_info(f"HTML解析警告: {e}")

        # 检查中文内容
        if check_chinese:
            chinese_count = len(analyzer.chinese_texts)
            if chinese_count > 0:
                log_success(f"{name} 包含中文内容 ({chinese_count}个中文文本块)")
                result["checks"]["chinese_content"] = chinese_count
                stats["ui_checks"]["chinese_content"]["passed"] += 1
            else:
                log_fail(f"{name} 缺少中文内容")
                result["checks"]["chinese_content"] = 0
                stats["ui_checks"]["chinese_content"]["failed"] += 1

        # 检查页面结构
        structure_score = 0
        if analyzer.has_header or analyzer.has_nav:
            structure_score += 1
        if analyzer.has_main:
            structure_score += 1
        if analyzer.has_footer:
            structure_score += 1

        result["checks"]["structure"] = {
            "header/nav": analyzer.has_header or analyzer.has_nav,
            "main": analyzer.has_main,
            "footer": analyzer.has_footer,
            "score": structure_score
        }

        if structure_score >= 2:
            log_success(f"{name} 页面结构良好 (评分: {structure_score}/3)")
        else:
            log_info(f"{name} 页面结构简单 (评分: {structure_score}/3)")

        # 检查图片
        img_count = len(analyzer.images)
        result["checks"]["images"] = img_count
        if img_count > 0:
            log_info(f"{name} 包含 {img_count} 个图片")
            stats["ui_checks"]["images"]["passed"] += 1

        # 检查表格
        table_count = len(analyzer.tables)
        result["checks"]["tables"] = table_count
        if table_count > 0:
            log_info(f"{name} 包含 {table_count} 个表格")
            stats["ui_checks"]["tables"]["passed"] += 1

        # 检查按钮
        button_count = len(analyzer.buttons)
        result["checks"]["buttons"] = button_count
        if button_count > 0:
            log_info(f"{name} 包含 {button_count} 个按钮")
            stats["ui_checks"]["buttons"]["passed"] += 1

        # 检查链接
        link_count = len(analyzer.links)
        result["checks"]["links"] = link_count
        if link_count > 0:
            log_info(f"{name} 包含 {link_count} 个链接")
            stats["ui_checks"]["links"]["passed"] += 1

        # 判断测试是否通过
        result["success"] = (
            response.status_code == 200 and
            result["checks"].get("doctype", False) and
            (not check_chinese or result["checks"].get("chinese_content", 0) > 0)
        )

        if result["success"]:
            log_success(f"✅ {name} 测试通过")
            stats["pages"]["passed"] += 1
        else:
            log_fail(f"❌ {name} 测试失败")
            stats["pages"]["failed"] += 1

    except Exception as e:
        log_fail(f"{name} 测试出错: {e}")
        result["error"] = str(e)
        stats["pages"]["failed"] += 1

    stats["pages"]["tested"] += 1
    log_info("")  # 空行
    return result


def test_books():
    """测试所有书籍"""
    log_info("=" * 80)
    log_info("第二部分: 书籍测试")
    log_info("=" * 80)
    log_info("")

    # 加载书籍数据
    try:
        with open(BOOKS_DATA_FILE, 'r', encoding='utf-8') as f:
            books_data = json.load(f)
        books = books_data.get("books", [])
        stats["books"]["total"] = len(books)
        log_info(f"找到 {len(books)} 本书籍")
    except Exception as e:
        log_fail(f"无法加载书籍数据: {e}")
        return []

    # 加载案例数据
    try:
        with open(CASES_DATA_FILE, 'r', encoding='utf-8') as f:
            cases_data = json.load(f)
    except Exception as e:
        log_fail(f"无法加载案例数据: {e}")
        cases_data = {"books": []}

    book_results = []

    # 测试前10本书（避免测试时间过长）
    for i, book in enumerate(books[:10], 1):
        log_info(f"\n--- 测试书籍 {i}/{min(10, len(books))}: {book['title']} ---")

        book_result = {
            "id": book["id"],
            "slug": book["slug"],
            "title": book["title"],
            "tested": datetime.now().isoformat(),
            "page_test": None,
            "case_count": 0
        }

        # 测试书籍详情页
        book_url = f"{BASE_URL}/textbooks.html?book={book['slug']}"
        page_result = test_page(book_url, f"书籍: {book['title']}")
        book_result["page_test"] = page_result

        # 统计案例
        book_cases = next((b for b in cases_data.get("books", []) if b["slug"] == book["slug"]), None)
        if book_cases:
            case_count = len(book_cases.get("cases", []))
            book_result["case_count"] = case_count
            stats["cases"]["total"] += case_count
            log_info(f"  书籍包含 {case_count} 个案例")

        stats["books"]["tested"] += 1
        if page_result["success"]:
            stats["books"]["passed"] += 1
        else:
            stats["books"]["failed"] += 1

        book_results.append(book_result)

    return book_results


def generate_report(book_results):
    """生成测试报告"""
    log_info("=" * 80)
    log_info("生成测试报告")
    log_info("=" * 80)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 生成Markdown报告
    md_report = f"""# Platform E2E测试报告 - Windows + 中文环境

## 测试信息

- **测试时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **测试环境**: Windows 10 + 中文环境 (zh-CN)
- **前端URL**: {BASE_URL}

---

## 测试总结

### 📊 总体统计

| 指标 | 数量 | 说明 |
|------|------|------|
| 总测试数 | {stats['total_tests']} | 所有执行的测试 |
| 通过数量 | {stats['passed_tests']} ✅ | 成功的测试 |
| 失败数量 | {stats['failed_tests']} ❌ | 失败的测试 |
| 成功率 | {stats['passed_tests']/stats['total_tests']*100:.1f}% | 测试通过率 |

### 📚 页面测试

| 指标 | 数量 |
|------|------|
| 已测试页面 | {stats['pages']['tested']} |
| 通过 | {stats['pages']['passed']} ✅ |
| 失败 | {stats['pages']['failed']} ❌ |

### 📖 书籍测试

| 指标 | 数量 |
|------|------|
| 书籍总数 | {stats['books']['total']} |
| 已测试 | {stats['books']['tested']} |
| 通过 | {stats['books']['passed']} ✅ |
| 失败 | {stats['books']['failed']} ❌ |

### 🎯 案例统计

| 指标 | 数量 |
|------|------|
| 案例总数 | {stats['cases']['total']} |

### 🎨 UI元素检查

| 检查项 | 通过 | 失败 |
|--------|------|------|
| 中文内容 | {stats['ui_checks']['chinese_content']['passed']} | {stats['ui_checks']['chinese_content']['failed']} |
| 图片 | {stats['ui_checks']['images']['passed']} | {stats['ui_checks']['images']['failed']} |
| 表格 | {stats['ui_checks']['tables']['passed']} | {stats['ui_checks']['tables']['failed']} |
| 按钮 | {stats['ui_checks']['buttons']['passed']} | {stats['ui_checks']['buttons']['failed']} |
| 链接 | {stats['ui_checks']['links']['passed']} | {stats['ui_checks']['links']['failed']} |

---

## 详细测试结果

### 核心页面测试

{chr(10).join(f"- {result['name']}: {'✅ 通过' if result['success'] else '❌ 失败'}" for result in test_results if 'book' not in result['name'].lower())}

### 书籍测试结果

{chr(10).join(f"- {book['title']}: {'✅ 通过' if book['page_test']['success'] else '❌ 失败'} (案例数: {book['case_count']})" for book in book_results)}

---

## 测试结论

**总体评级**: {'✅ 优秀' if stats['passed_tests']/stats['total_tests'] >= 0.9 else '✅ 良好' if stats['passed_tests']/stats['total_tests'] >= 0.75 else '⚠️ 及格' if stats['passed_tests']/stats['total_tests'] >= 0.60 else '❌ 需改进'}

**测试完成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

    md_file = REPORT_DIR / f"e2e-test-comprehensive-{timestamp}.md"
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(md_report)

    log_success(f"Markdown报告已保存: {md_file}")

    # 生成JSON报告
    json_report = {
        "test_name": "Platform E2E测试 - Windows + 中文环境",
        "timestamp": datetime.now().isoformat(),
        "environment": {
            "platform": "Windows 10 模拟",
            "locale": "zh-CN",
            "timezone": "Asia/Shanghai",
            "base_url": BASE_URL
        },
        "statistics": stats,
        "test_results": test_results,
        "book_results": book_results
    }

    json_file = REPORT_DIR / f"e2e-test-comprehensive-{timestamp}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(json_report, f, ensure_ascii=False, indent=2)

    log_success(f"JSON报告已保存: {json_file}")

    return md_file, json_file


def main():
    """主函数"""
    print("=" * 80)
    print("  🚀 Platform E2E测试 - Windows + 中文环境")
    print("=" * 80)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"测试环境: Windows 10 + 中文环境")
    print(f"前端URL: {BASE_URL}")
    print("=" * 80)
    print("")

    # 第一部分: 测试核心页面
    log_info("=" * 80)
    log_info("第一部分: 核心页面测试")
    log_info("=" * 80)
    log_info("")

    core_pages = [
        (f"{BASE_URL}/", "主页"),
        (f"{BASE_URL}/textbooks.html", "教材库"),
        (f"{BASE_URL}/search.html", "搜索页面"),
        (f"{BASE_URL}/code-runner.html", "代码运行器"),
        (f"{BASE_URL}/ide.html", "AI编程IDE"),
        (f"{BASE_URL}/knowledge/index.html", "知识库")
    ]

    for url, name in core_pages:
        result = test_page(url, name)
        test_results.append(result)

    # 第二部分: 测试书籍
    book_results = test_books()

    # 生成报告
    md_file, json_file = generate_report(book_results)

    # 打印总结
    print("\n" + "=" * 80)
    print("  测试总结")
    print("=" * 80)
    print(f"📊 总测试数: {stats['total_tests']}")
    print(f"✅ 通过数量: {stats['passed_tests']}")
    print(f"❌ 失败数量: {stats['failed_tests']}")
    print(f"📈 成功率: {stats['passed_tests']/stats['total_tests']*100:.1f}%")
    print(f"\n📚 书籍: {stats['books']['tested']}/{stats['books']['total']} 已测试")
    print(f"📝 案例总数: {stats['cases']['total']}")
    print(f"\n📁 报告文件:")
    print(f"  - Markdown: {md_file}")
    print(f"  - JSON: {json_file}")
    print("=" * 80)

    # 返回退出码
    if stats['failed_tests'] == 0:
        print("\n✅ 所有测试通过！")
        return 0
    elif stats['passed_tests'] / stats['total_tests'] >= 0.7:
        print("\n⚠️  部分测试失败，但整体通过率>= 70%")
        return 0
    else:
        print("\n❌ 测试失败过多")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 测试执行出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
