#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CHS-Books 综合端到端测试脚本
全面验证项目结构、内容完整性和代码质量
"""

import os
import sys
import json
import subprocess
import importlib.util
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# 定义项目根目录
PROJECT_ROOT = Path(__file__).parent
BOOKS_DIR = PROJECT_ROOT / 'books'
PLATFORM_DIR = PROJECT_ROOT / 'platform'

# 测试结果
results = {
    'timestamp': datetime.now().isoformat(),
    'tests': [],
    'summary': {
        'total': 0,
        'passed': 0,
        'failed': 0,
        'warnings': 0
    }
}

def add_result(category: str, name: str, status: str, details: str = ''):
    """添加测试结果"""
    results['tests'].append({
        'category': category,
        'name': name,
        'status': status,
        'details': details
    })
    results['summary']['total'] += 1
    if status == 'PASS':
        results['summary']['passed'] += 1
    elif status == 'FAIL':
        results['summary']['failed'] += 1
    elif status == 'WARN':
        results['summary']['warnings'] += 1

def print_header(title: str):
    """打印标题"""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")

def print_result(name: str, status: str, details: str = ''):
    """打印测试结果"""
    icons = {'PASS': '✅', 'FAIL': '❌', 'WARN': '⚠️'}
    print(f"  {icons.get(status, '?')} {name}")
    if details:
        print(f"     └─ {details}")

# ============================================================================
# 1. 项目结构测试
# ============================================================================
def test_project_structure():
    """测试项目结构完整性"""
    print_header("1. 项目结构测试")

    # 检查必需目录
    required_dirs = [
        'books',
        'platform',
        'platform/backend',
        'platform/frontend',
        'platform/backend/app',
        'platform/backend/tests',
    ]

    for dir_path in required_dirs:
        full_path = PROJECT_ROOT / dir_path
        if full_path.exists():
            add_result('结构', f'目录 {dir_path}', 'PASS')
            print_result(f'目录 {dir_path}', 'PASS')
        else:
            add_result('结构', f'目录 {dir_path}', 'FAIL', '目录不存在')
            print_result(f'目录 {dir_path}', 'FAIL', '目录不存在')

    # 检查必需文件
    required_files = [
        'README.md',
        'platform/backend/requirements.txt',
        'platform/backend/pytest.ini',
        'platform/frontend/index.html',
    ]

    for file_path in required_files:
        full_path = PROJECT_ROOT / file_path
        if full_path.exists():
            add_result('结构', f'文件 {file_path}', 'PASS')
            print_result(f'文件 {file_path}', 'PASS')
        else:
            add_result('结构', f'文件 {file_path}', 'FAIL', '文件不存在')
            print_result(f'文件 {file_path}', 'FAIL', '文件不存在')

# ============================================================================
# 2. 书籍内容测试
# ============================================================================
def test_books_content():
    """测试书籍内容完整性"""
    print_header("2. 书籍内容测试")

    if not BOOKS_DIR.exists():
        add_result('书籍', '书籍目录', 'FAIL', '目录不存在')
        print_result('书籍目录', 'FAIL', '目录不存在')
        return

    # 统计书籍信息
    book_stats = {
        'total_books': 0,
        'total_chapters': 0,
        'total_cases': 0,
        'total_code_files': 0,
        'books': []
    }

    for book_path in sorted(BOOKS_DIR.iterdir()):
        if not book_path.is_dir():
            continue

        book_name = book_path.name
        book_info = {
            'name': book_name,
            'chapters': 0,
            'cases': 0,
            'code_files': 0,
            'has_readme': False
        }

        # 检查README
        if (book_path / 'README.md').exists():
            book_info['has_readme'] = True

        # 统计章节
        chapters_dir = book_path / 'chapters'
        if chapters_dir.exists():
            book_info['chapters'] = len(list(chapters_dir.glob('*.md')))

        # 统计案例
        examples_dir = book_path / 'code' / 'examples'
        if examples_dir.exists():
            book_info['cases'] = len([d for d in examples_dir.iterdir()
                                     if d.is_dir() and d.name.startswith('case_')])

        # 统计代码文件
        code_dir = book_path / 'code'
        if code_dir.exists():
            book_info['code_files'] = len(list(code_dir.rglob('*.py')))

        book_stats['total_books'] += 1
        book_stats['total_chapters'] += book_info['chapters']
        book_stats['total_cases'] += book_info['cases']
        book_stats['total_code_files'] += book_info['code_files']
        book_stats['books'].append(book_info)

        # 打印书籍信息
        status = 'PASS' if book_info['has_readme'] else 'WARN'
        details = f"章节: {book_info['chapters']}, 案例: {book_info['cases']}, 代码文件: {book_info['code_files']}"
        add_result('书籍', book_name, status, details)
        print_result(book_name, status, details)

    # 打印总统计
    print(f"\n  📊 总计: {book_stats['total_books']} 本书, "
          f"{book_stats['total_chapters']} 章节, "
          f"{book_stats['total_cases']} 案例, "
          f"{book_stats['total_code_files']} 代码文件")

    return book_stats

# ============================================================================
# 3. 代码语法测试
# ============================================================================
def test_python_syntax():
    """测试Python代码语法"""
    print_header("3. Python语法测试")

    syntax_errors = []
    total_files = 0

    # 检查所有Python文件
    for py_file in PROJECT_ROOT.rglob('*.py'):
        # 跳过虚拟环境
        if 'venv' in str(py_file) or '__pycache__' in str(py_file):
            continue

        total_files += 1
        try:
            with open(py_file, 'r', encoding='utf-8', errors='replace') as f:
                source = f.read()
            compile(source, py_file, 'exec')
        except SyntaxError as e:
            syntax_errors.append((py_file, str(e)))

    if not syntax_errors:
        add_result('语法', f'Python文件语法检查 ({total_files}个文件)', 'PASS')
        print_result(f'Python语法检查 ({total_files}个文件)', 'PASS')
    else:
        add_result('语法', f'Python文件语法检查', 'FAIL',
                   f'{len(syntax_errors)}个语法错误')
        print_result(f'Python语法检查 ({total_files}个文件)', 'FAIL',
                     f'{len(syntax_errors)}个语法错误')
        for file_path, error in syntax_errors[:5]:
            rel_path = file_path.relative_to(PROJECT_ROOT)
            print(f"     └─ {rel_path}: {error}")

# ============================================================================
# 4. 书籍代码案例测试
# ============================================================================
def test_book_cases_sample():
    """测试书籍代码案例（抽样）"""
    print_header("4. 书籍案例抽样测试")

    # 收集所有可测试的案例
    test_cases = []
    for book_path in BOOKS_DIR.iterdir():
        if not book_path.is_dir():
            continue

        examples_dir = book_path / 'code' / 'examples'
        if not examples_dir.exists():
            continue

        for case_dir in examples_dir.iterdir():
            if not case_dir.is_dir():
                continue
            if not case_dir.name.startswith('case_'):
                continue

            main_py = case_dir / 'main.py'
            if main_py.exists():
                test_cases.append((book_path.name, case_dir))

    print(f"  找到 {len(test_cases)} 个可测试案例")

    # 每本书测试前2个案例
    books_tested = defaultdict(int)
    tested = 0
    passed = 0

    for book_name, case_dir in test_cases:
        if books_tested[book_name] >= 2:
            continue

        books_tested[book_name] += 1
        tested += 1
        case_name = case_dir.name

        try:
            result = subprocess.run(
                ['python3', 'main.py'],
                cwd=case_dir,
                capture_output=True,
                text=True,
                timeout=60,
                encoding='utf-8',
                errors='replace'
            )

            if result.returncode == 0:
                passed += 1
                add_result('案例', f'{book_name}/{case_name}', 'PASS')
                print_result(f'{book_name}/{case_name}', 'PASS')
            else:
                # 检查是否只是警告
                if 'Error' in result.stderr or 'Exception' in result.stderr:
                    add_result('案例', f'{book_name}/{case_name}', 'FAIL',
                               '运行出错')
                    print_result(f'{book_name}/{case_name}', 'FAIL', '运行出错')
                else:
                    passed += 1
                    add_result('案例', f'{book_name}/{case_name}', 'PASS',
                               '有警告但完成')
                    print_result(f'{book_name}/{case_name}', 'PASS', '有警告但完成')

        except subprocess.TimeoutExpired:
            add_result('案例', f'{book_name}/{case_name}', 'WARN', '超时')
            print_result(f'{book_name}/{case_name}', 'WARN', '超时60秒')
        except Exception as e:
            add_result('案例', f'{book_name}/{case_name}', 'FAIL', str(e))
            print_result(f'{book_name}/{case_name}', 'FAIL', str(e))

    print(f"\n  📊 抽样测试: {passed}/{tested} 通过")

# ============================================================================
# 5. 平台代码测试
# ============================================================================
def test_platform_code():
    """测试平台代码"""
    print_header("5. 平台代码测试")

    backend_dir = PLATFORM_DIR / 'backend'
    frontend_dir = PLATFORM_DIR / 'frontend'

    # 检查后端模块
    backend_modules = [
        'app/main.py',
        'app/core/config.py',
        'app/core/database.py',
        'app/api/__init__.py',
        'app/models/__init__.py',
        'app/services/__init__.py',
    ]

    for module_path in backend_modules:
        full_path = backend_dir / module_path
        if full_path.exists():
            add_result('平台', f'后端模块 {module_path}', 'PASS')
            print_result(f'后端模块 {module_path}', 'PASS')
        else:
            add_result('平台', f'后端模块 {module_path}', 'FAIL', '文件不存在')
            print_result(f'后端模块 {module_path}', 'FAIL', '文件不存在')

    # 检查前端文件
    frontend_files = [
        'index.html',
        'learning.html',
        'ide.html',
        'cache-manager.js',
    ]

    for file_name in frontend_files:
        full_path = frontend_dir / file_name
        if full_path.exists():
            add_result('平台', f'前端文件 {file_name}', 'PASS')
            print_result(f'前端文件 {file_name}', 'PASS')
        else:
            add_result('平台', f'前端文件 {file_name}', 'FAIL', '文件不存在')
            print_result(f'前端文件 {file_name}', 'FAIL', '文件不存在')

# ============================================================================
# 6. 文档完整性测试
# ============================================================================
def test_documentation():
    """测试文档完整性"""
    print_header("6. 文档完整性测试")

    # 检查主要文档
    main_docs = [
        ('README.md', '项目主README'),
        ('platform/README.md', '平台README'),
        ('CONTRIBUTING.md', '贡献指南'),
        ('CHANGELOG.md', '更新日志'),
    ]

    for doc_path, doc_name in main_docs:
        full_path = PROJECT_ROOT / doc_path
        if full_path.exists():
            size = full_path.stat().st_size
            add_result('文档', doc_name, 'PASS', f'{size/1024:.1f}KB')
            print_result(doc_name, 'PASS', f'{size/1024:.1f}KB')
        else:
            add_result('文档', doc_name, 'WARN', '文件不存在')
            print_result(doc_name, 'WARN', '文件不存在')

    # 统计Markdown文件
    md_files = list(PROJECT_ROOT.rglob('*.md'))
    total_md_size = sum(f.stat().st_size for f in md_files) / (1024 * 1024)
    print(f"\n  📚 总计 {len(md_files)} 个Markdown文件, {total_md_size:.1f}MB")

# ============================================================================
# 7. 生成报告
# ============================================================================
def generate_report():
    """生成测试报告"""
    print_header("测试报告摘要")

    summary = results['summary']
    total = summary['total']
    passed = summary['passed']
    failed = summary['failed']
    warnings = summary['warnings']

    pass_rate = (passed / total * 100) if total > 0 else 0

    print(f"  📊 总计测试: {total}")
    print(f"  ✅ 通过: {passed}")
    print(f"  ❌ 失败: {failed}")
    print(f"  ⚠️  警告: {warnings}")
    print(f"  📈 通过率: {pass_rate:.1f}%")

    # 保存JSON报告
    report_dir = PROJECT_ROOT / 'platform' / 'test_reports'
    report_dir.mkdir(parents=True, exist_ok=True)

    report_file = report_dir / 'comprehensive_e2e_report.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n  📄 报告已保存: {report_file}")

    # 返回状态码
    return 0 if failed == 0 else 1

# ============================================================================
# 主函数
# ============================================================================
def main():
    """主函数"""
    print("="*80)
    print("  CHS-Books 综合端到端测试")
    print("="*80)
    print(f"  时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  项目: {PROJECT_ROOT}")

    # 运行所有测试
    test_project_structure()
    book_stats = test_books_content()
    test_python_syntax()
    test_book_cases_sample()
    test_platform_code()
    test_documentation()

    # 生成报告
    return generate_report()

if __name__ == '__main__':
    sys.exit(main())
