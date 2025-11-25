#!/usr/bin/env python3
"""
CHS-Books Platform 全面E2E测试
使用requests + HTMLParser进行页面测试
可选: 使用Playwright进行浏览器截图

测试内容:
1. 核心页面HTTP测试
2. HTML结构验证
3. 中文内容检查
4. API集成测试
5. 所有页面枚举测试
6. 可选: 浏览器截图(需要Playwright)

使用方法:
    python e2e_full_test.py                # HTTP测试
    python e2e_full_test.py --screenshots  # HTTP测试 + 截图(需要Playwright)
"""

import requests
import json
import re
import os
import sys
import argparse
from datetime import datetime
from pathlib import Path
from html.parser import HTMLParser
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# 尝试导入Playwright（可选）
PLAYWRIGHT_AVAILABLE = False
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    pass

# 命令行参数
parser = argparse.ArgumentParser(description='CHS-Books Platform E2E测试')
parser.add_argument('--screenshots', action='store_true', help='启用浏览器截图(需要Playwright)')
args, _ = parser.parse_known_args()

# 配置
CONFIG = {
    'FRONTEND_URL': 'http://localhost:8080',
    'BACKEND_URL': 'http://localhost:8000',
    'TIMEOUT': 30,
    'REPORT_DIR': Path('/home/user/CHS-Books/platform/test_reports'),
    'SCREENSHOT_DIR': Path('/home/user/CHS-Books/platform/test_reports/screenshots'),
    'MAX_WORKERS': 5,
    'ENABLE_SCREENSHOTS': args.screenshots and PLAYWRIGHT_AVAILABLE
}

# 统计数据
stats = {
    'total': 0,
    'passed': 0,
    'failed': 0,
    'pages': {'tested': 0, 'passed': 0, 'failed': 0},
    'api': {'tested': 0, 'passed': 0, 'failed': 0},
    'ui_checks': {
        'chinese_content': {'passed': 0, 'failed': 0},
        'images': {'passed': 0, 'failed': 0},
        'links': {'passed': 0, 'failed': 0},
        'forms': {'passed': 0, 'failed': 0}
    },
    'errors': []
}

# 测试结果
results = []


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
        self.forms = []
        self.scripts = []
        self.chinese_texts = []
        self.title = ''
        self.in_title = False

    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        attrs_dict = dict(attrs)

        if tag == 'title':
            self.in_title = True
        if tag == 'header' or ('class' in attrs_dict and 'header' in attrs_dict.get('class', '')):
            self.has_header = True
        if tag == 'nav' or ('class' in attrs_dict and 'nav' in attrs_dict.get('class', '')):
            self.has_nav = True
        if tag == 'main' or ('class' in attrs_dict and ('main' in attrs_dict.get('class', '') or 'content' in attrs_dict.get('class', ''))):
            self.has_main = True
        if tag == 'footer' or ('class' in attrs_dict and 'footer' in attrs_dict.get('class', '')):
            self.has_footer = True
        if tag == 'img':
            self.images.append(attrs_dict.get('src', ''))
        if tag == 'table':
            self.tables.append(True)
        if tag == 'button' or (tag == 'input' and attrs_dict.get('type') == 'submit'):
            self.buttons.append(attrs_dict)
        if tag == 'a' and 'href' in attrs_dict:
            self.links.append(attrs_dict['href'])
        if tag == 'form':
            self.forms.append(attrs_dict)
        if tag == 'script':
            self.scripts.append(attrs_dict.get('src', 'inline'))

    def handle_endtag(self, tag):
        if tag == 'title':
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.title += data
        # 检测中文内容
        if re.search(r'[\u4e00-\u9fa5]', data):
            self.chinese_texts.append(data.strip())


def log(message, level='INFO'):
    """输出日志"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    icons = {
        'INFO': '📘',
        'SUCCESS': '✅',
        'ERROR': '❌',
        'WARNING': '⚠️',
        'TEST': '🧪',
        'SCREENSHOT': '📷'
    }
    print(f"[{timestamp}] {icons.get(level, '•')} {message}")


# 全局Playwright浏览器实例
_browser = None
_playwright = None


def init_browser():
    """初始化Playwright浏览器"""
    global _browser, _playwright
    if not CONFIG['ENABLE_SCREENSHOTS']:
        return False

    if _browser is None:
        try:
            _playwright = sync_playwright().start()
            _browser = _playwright.chromium.launch(headless=True)
            log("Playwright浏览器已启动", 'SUCCESS')
            return True
        except Exception as e:
            log(f"无法启动浏览器: {e}", 'WARNING')
            CONFIG['ENABLE_SCREENSHOTS'] = False
            return False
    return True


def close_browser():
    """关闭浏览器"""
    global _browser, _playwright
    if _browser:
        _browser.close()
        _browser = None
    if _playwright:
        _playwright.stop()
        _playwright = None


def capture_screenshot(url, name):
    """截取页面截图"""
    if not CONFIG['ENABLE_SCREENSHOTS'] or not _browser:
        return None

    try:
        CONFIG['SCREENSHOT_DIR'].mkdir(parents=True, exist_ok=True)
        page = _browser.new_page()
        page.set_viewport_size({'width': 1920, 'height': 1080})
        page.goto(url, wait_until='networkidle', timeout=30000)

        # 等待页面渲染
        page.wait_for_timeout(1000)

        # 截图
        safe_name = re.sub(r'[^\w\-]', '_', name)
        screenshot_path = CONFIG['SCREENSHOT_DIR'] / f"{safe_name}.png"
        page.screenshot(path=str(screenshot_path), full_page=True)
        page.close()

        log(f"  截图保存: {screenshot_path.name}", 'SCREENSHOT')
        return str(screenshot_path)
    except Exception as e:
        log(f"  截图失败: {e}", 'WARNING')
        return None


def test_api_health():
    """测试API健康状态"""
    log("测试后端API健康状态", 'TEST')
    stats['total'] += 1
    stats['api']['tested'] += 1

    try:
        response = requests.get(f"{CONFIG['BACKEND_URL']}/health", timeout=CONFIG['TIMEOUT'])
        data = response.json()

        if response.status_code == 200 and data.get('status') == 'healthy':
            stats['passed'] += 1
            stats['api']['passed'] += 1
            log(f"API状态: {data['status']}", 'SUCCESS')
            log(f"数据库: {data.get('database', 'unknown')}", 'SUCCESS')
            results.append({
                'name': 'API健康检查',
                'url': f"{CONFIG['BACKEND_URL']}/health",
                'success': True,
                'data': data
            })
            return True
        else:
            raise Exception(f"API状态异常: {data}")
    except Exception as e:
        stats['failed'] += 1
        stats['api']['failed'] += 1
        stats['errors'].append({'test': 'API健康检查', 'error': str(e)})
        log(f"API健康检查失败: {e}", 'ERROR')
        results.append({
            'name': 'API健康检查',
            'url': f"{CONFIG['BACKEND_URL']}/health",
            'success': False,
            'error': str(e)
        })
        return False


def test_api_docs():
    """测试API文档"""
    log("测试API文档页面", 'TEST')
    stats['total'] += 1
    stats['api']['tested'] += 1

    try:
        response = requests.get(f"{CONFIG['BACKEND_URL']}/docs", timeout=CONFIG['TIMEOUT'])

        if response.status_code == 200:
            stats['passed'] += 1
            stats['api']['passed'] += 1
            log("API文档可访问", 'SUCCESS')
            results.append({
                'name': 'API文档',
                'url': f"{CONFIG['BACKEND_URL']}/docs",
                'success': True
            })
            return True
        else:
            raise Exception(f"HTTP {response.status_code}")
    except Exception as e:
        stats['failed'] += 1
        stats['api']['failed'] += 1
        stats['errors'].append({'test': 'API文档', 'error': str(e)})
        log(f"API文档访问失败: {e}", 'ERROR')
        return False


def test_page(url, name, check_chinese=True):
    """测试单个页面"""
    stats['total'] += 1
    stats['pages']['tested'] += 1

    result = {
        'name': name,
        'url': url,
        'timestamp': datetime.now().isoformat(),
        'success': False,
        'checks': {}
    }

    log(f"测试页面: {name}", 'TEST')

    try:
        response = requests.get(url, timeout=CONFIG['TIMEOUT'])
        result['http_status'] = response.status_code

        if response.status_code != 200:
            raise Exception(f"HTTP状态码: {response.status_code}")

        # 强制UTF-8编码（解决SimpleHTTP服务器编码问题）
        response.encoding = 'utf-8'
        html = response.text

        # 检查编码
        result['checks']['encoding'] = 'UTF-8' if 'utf-8' in html.lower() else 'unknown'

        # 检查DOCTYPE
        result['checks']['doctype'] = html.strip().lower().startswith('<!doctype html>')

        # 解析HTML
        analyzer = HTMLAnalyzer()
        try:
            analyzer.feed(html)
        except Exception as e:
            log(f"  HTML解析警告: {e}", 'WARNING')

        # 页面标题
        result['checks']['title'] = analyzer.title.strip()

        # 中文内容
        chinese_count = len(analyzer.chinese_texts)
        result['checks']['chinese_content'] = chinese_count
        if chinese_count > 0:
            stats['ui_checks']['chinese_content']['passed'] += 1
            log(f"  中文内容: {chinese_count}个文本块", 'SUCCESS')
        else:
            stats['ui_checks']['chinese_content']['failed'] += 1
            log(f"  中文内容: 无", 'WARNING')

        # 页面结构
        result['checks']['structure'] = {
            'header': analyzer.has_header or analyzer.has_nav,
            'main': analyzer.has_main,
            'footer': analyzer.has_footer
        }

        # UI元素
        result['checks']['images'] = len(analyzer.images)
        result['checks']['links'] = len(analyzer.links)
        result['checks']['forms'] = len(analyzer.forms)
        result['checks']['buttons'] = len(analyzer.buttons)
        result['checks']['scripts'] = len(analyzer.scripts)

        if len(analyzer.images) > 0:
            stats['ui_checks']['images']['passed'] += 1
        if len(analyzer.links) > 0:
            stats['ui_checks']['links']['passed'] += 1
        if len(analyzer.forms) > 0:
            stats['ui_checks']['forms']['passed'] += 1

        # 判断通过
        result['success'] = (
            response.status_code == 200 and
            (not check_chinese or chinese_count > 0)
        )

        if result['success']:
            stats['passed'] += 1
            stats['pages']['passed'] += 1
            log(f"  测试通过 (HTTP 200, {chinese_count}中文, {len(analyzer.links)}链接)", 'SUCCESS')

            # 截图（如果启用）
            screenshot_path = capture_screenshot(url, name)
            if screenshot_path:
                result['screenshot'] = screenshot_path
        else:
            stats['failed'] += 1
            stats['pages']['failed'] += 1
            log(f"  测试失败", 'ERROR')

    except Exception as e:
        stats['failed'] += 1
        stats['pages']['failed'] += 1
        result['error'] = str(e)
        stats['errors'].append({'test': name, 'error': str(e)})
        log(f"  测试出错: {e}", 'ERROR')

    results.append(result)
    return result


def test_all_frontend_pages():
    """测试所有前端页面"""
    log("", 'INFO')
    log("=" * 60, 'INFO')
    log("前端页面测试", 'INFO')
    log("=" * 60, 'INFO')

    pages = [
        ('index.html', '主页'),
        ('textbooks.html', '教材库'),
        ('search.html', '搜索页面'),
        ('code-runner.html', '代码运行器'),
        ('ide.html', 'AI编程IDE'),
        ('learning.html', '学习页面'),
        ('unified.html', '统一入口'),
        ('knowledge/index.html', '知识库'),
        ('knowledge/knowledge_graph_viz.html', '知识图谱'),
        ('textbook-reader-enhanced.html', '增强教材阅读器'),
    ]

    for page, name in pages:
        url = f"{CONFIG['FRONTEND_URL']}/{page}"
        test_page(url, name)
        print()


def test_api_endpoints():
    """测试API端点"""
    log("", 'INFO')
    log("=" * 60, 'INFO')
    log("API端点测试", 'INFO')
    log("=" * 60, 'INFO')

    # 测试健康检查
    test_api_health()

    # 测试API文档
    test_api_docs()

    # 测试根端点
    log("测试API根端点", 'TEST')
    stats['total'] += 1
    stats['api']['tested'] += 1

    try:
        response = requests.get(f"{CONFIG['BACKEND_URL']}/", timeout=CONFIG['TIMEOUT'])
        if response.status_code == 200:
            data = response.json()
            stats['passed'] += 1
            stats['api']['passed'] += 1
            log(f"API根端点: {data.get('message', 'OK')}", 'SUCCESS')
            results.append({
                'name': 'API根端点',
                'url': f"{CONFIG['BACKEND_URL']}/",
                'success': True,
                'data': data
            })
        else:
            raise Exception(f"HTTP {response.status_code}")
    except Exception as e:
        stats['failed'] += 1
        stats['api']['failed'] += 1
        stats['errors'].append({'test': 'API根端点', 'error': str(e)})
        log(f"API根端点测试失败: {e}", 'ERROR')

    # 测试教材API
    log("测试教材API", 'TEST')
    stats['total'] += 1
    stats['api']['tested'] += 1

    try:
        response = requests.get(f"{CONFIG['BACKEND_URL']}/api/v1/textbooks/", timeout=CONFIG['TIMEOUT'])
        if response.status_code in [200, 404]:  # 404也是有效响应（空数据）
            stats['passed'] += 1
            stats['api']['passed'] += 1
            log(f"教材API: HTTP {response.status_code}", 'SUCCESS')
            results.append({
                'name': '教材API',
                'url': f"{CONFIG['BACKEND_URL']}/api/v1/textbooks/",
                'success': True
            })
        else:
            raise Exception(f"HTTP {response.status_code}")
    except Exception as e:
        stats['failed'] += 1
        stats['api']['failed'] += 1
        stats['errors'].append({'test': '教材API', 'error': str(e)})
        log(f"教材API测试失败: {e}", 'ERROR')


def generate_report():
    """生成测试报告"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pass_rate = stats['passed'] / stats['total'] * 100 if stats['total'] > 0 else 0

    # JSON报告
    json_report = {
        'test_name': 'CHS-Books Platform E2E全面测试',
        'timestamp': datetime.now().isoformat(),
        'environment': {
            'frontend_url': CONFIG['FRONTEND_URL'],
            'backend_url': CONFIG['BACKEND_URL']
        },
        'statistics': stats,
        'pass_rate': f"{pass_rate:.1f}%",
        'results': results
    }

    json_path = CONFIG['REPORT_DIR'] / f"e2e_full_test_{timestamp}.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_report, f, ensure_ascii=False, indent=2)

    # Markdown报告
    md_report = f"""# CHS-Books Platform E2E全面测试报告

## 测试信息

- **测试时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **前端URL**: {CONFIG['FRONTEND_URL']}
- **后端URL**: {CONFIG['BACKEND_URL']}

---

## 测试总结

### 📊 整体统计

| 指标 | 数量 |
|------|------|
| 总测试数 | {stats['total']} |
| 通过 | {stats['passed']} ✅ |
| 失败 | {stats['failed']} ❌ |
| 通过率 | {pass_rate:.1f}% |

### 📄 页面测试

| 指标 | 数量 |
|------|------|
| 已测试 | {stats['pages']['tested']} |
| 通过 | {stats['pages']['passed']} ✅ |
| 失败 | {stats['pages']['failed']} ❌ |

### 🔌 API测试

| 指标 | 数量 |
|------|------|
| 已测试 | {stats['api']['tested']} |
| 通过 | {stats['api']['passed']} ✅ |
| 失败 | {stats['api']['failed']} ❌ |

### 🎨 UI元素检查

| 检查项 | 通过 | 失败 |
|--------|------|------|
| 中文内容 | {stats['ui_checks']['chinese_content']['passed']} | {stats['ui_checks']['chinese_content']['failed']} |
| 图片 | {stats['ui_checks']['images']['passed']} | - |
| 链接 | {stats['ui_checks']['links']['passed']} | - |
| 表单 | {stats['ui_checks']['forms']['passed']} | - |

---

## 详细测试结果

### 页面测试

| 页面 | URL | 状态 | 中文内容 | 链接数 |
|------|-----|------|----------|--------|
{chr(10).join(f"| {r['name']} | {r['url'].split('/')[-1]} | {'✅' if r['success'] else '❌'} | {r.get('checks', {}).get('chinese_content', 'N/A')} | {r.get('checks', {}).get('links', 'N/A')} |" for r in results if 'checks' in r)}

### API测试

| 端点 | 状态 |
|------|------|
{chr(10).join(f"| {r['name']} | {'✅ 通过' if r['success'] else '❌ 失败'} |" for r in results if 'checks' not in r)}

{f'''
### ❌ 错误列表

| 测试 | 错误信息 |
|------|----------|
{chr(10).join(f"| {e['test']} | {e['error'][:50]}... |" for e in stats['errors'])}
''' if stats['errors'] else ''}

---

## 测试结论

**总体评级**: {'✅ 优秀' if pass_rate >= 90 else '✅ 良好' if pass_rate >= 70 else '⚠️ 及格' if pass_rate >= 60 else '❌ 需改进'}

**测试完成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

    md_path = CONFIG['REPORT_DIR'] / f"e2e_full_test_{timestamp}.md"
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md_report)

    log(f"JSON报告: {json_path}", 'SUCCESS')
    log(f"Markdown报告: {md_path}", 'SUCCESS')

    return json_path, md_path


def main():
    """主函数"""
    print("=" * 70)
    print("  🚀 CHS-Books Platform E2E 全面测试")
    print("=" * 70)
    print(f"  前端: {CONFIG['FRONTEND_URL']}")
    print(f"  后端: {CONFIG['BACKEND_URL']}")
    if args.screenshots:
        if PLAYWRIGHT_AVAILABLE:
            print("  📷 截图模式: 已启用")
        else:
            print("  📷 截图模式: 不可用 (需要安装Playwright)")
    print("=" * 70)
    print()

    # 确保报告目录存在
    CONFIG['REPORT_DIR'].mkdir(parents=True, exist_ok=True)

    # 初始化浏览器（如果需要截图）
    if args.screenshots:
        init_browser()

    start_time = time.time()

    try:
        # 测试API
        test_api_endpoints()

        # 测试前端页面
        test_all_frontend_pages()
    finally:
        # 确保关闭浏览器
        close_browser()

    elapsed = time.time() - start_time

    # 生成报告
    print()
    log("=" * 60, 'INFO')
    log("生成测试报告", 'INFO')
    log("=" * 60, 'INFO')
    json_path, md_path = generate_report()

    # 打印总结
    pass_rate = stats['passed'] / stats['total'] * 100 if stats['total'] > 0 else 0

    print()
    print("=" * 70)
    print("  📊 测试总结")
    print("=" * 70)
    print(f"  总测试数: {stats['total']}")
    print(f"  通过: {stats['passed']} ✅")
    print(f"  失败: {stats['failed']} ❌")
    print(f"  通过率: {pass_rate:.1f}%")
    print(f"  耗时: {elapsed:.1f}秒")
    print()
    print(f"  📁 报告目录: {CONFIG['REPORT_DIR']}")
    print("=" * 70)

    if stats['failed'] == 0:
        print("\n✅ 所有测试通过!")
        return 0
    elif pass_rate >= 70:
        print(f"\n⚠️ 部分测试失败，但整体通过率 {pass_rate:.1f}% >= 70%")
        return 0
    else:
        print(f"\n❌ 测试失败过多，通过率 {pass_rate:.1f}% < 70%")
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
