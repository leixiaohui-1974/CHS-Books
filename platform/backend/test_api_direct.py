#!/usr/bin/env python3
"""
直接测试API逻辑
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from pathlib import Path
import json
import subprocess
import os

# 路径设置
BACKEND_DIR = Path(__file__).parent
CASES_INDEX_FILE = BACKEND_DIR / "cases_index.json"
BOOKS_BASE_DIR = BACKEND_DIR.parent.parent  # 指向CHS-Books根目录

def load_cases_index():
    """加载案例索引"""
    if not CASES_INDEX_FILE.exists():
        print(f"❌ cases_index.json 不存在: {CASES_INDEX_FILE}")
        return {"books": [], "total_cases": 0}
    with open(CASES_INDEX_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def test_case_execution():
    """测试案例执行"""
    book_slug = "water-system-control"
    case_id = "case_01_home_water_tower"
    
    print(f"📚 测试案例执行")
    print(f"书籍: {book_slug}")
    print(f"案例: {case_id}")
    print()
    
    # 加载索引
    cases_index = load_cases_index()
    print(f"✓ 加载索引，共 {cases_index.get('total_cases', 0)} 个案例")
    print(f"✓ 共 {len(cases_index.get('books', []))} 本书")
    print()
    
    # 查找案例路径
    case_path = None
    for book_cases in cases_index.get("books", []):
        print(f"检查书籍: {book_cases['slug']}")
        if book_cases["slug"] == book_slug:
            print(f"  ✓ 找到匹配的书籍")
            cases = book_cases.get("cases", [])
            print(f"  案例数: {len(cases)}")
            for case in cases:
                if case["id"] == case_id:
                    print(f"  ✓ 找到案例: {case_id}")
                    case_path = BOOKS_BASE_DIR / case["path"]
                    print(f"  路径: {case_path}")
                    break
            break
    
    if not case_path:
        print(f"❌ 未找到案例路径")
        return
    
    if not case_path.exists():
        print(f"❌ 案例路径不存在: {case_path}")
        return
    
    print(f"✓ 案例路径存在")
    
    # 检查main.py
    main_file = case_path / "main.py"
    if not main_file.exists():
        print(f"❌ main.py 不存在: {main_file}")
        return
    
    print(f"✓ main.py 存在")
    print()
    
    # 执行案例
    print(f"🚀 执行案例...")
    print("-" * 60)
    
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    
    try:
        result = subprocess.run(
            [sys.executable, str(main_file)],
            cwd=str(case_path),
            capture_output=True,
            text=True,
            timeout=60,
            encoding='utf-8',
            errors='replace',
            env=env
        )
        
        print(f"返回码: {result.returncode}")
        print(f"成功: {result.returncode == 0}")
        print()
        
        if result.stdout:
            print("📤 标准输出:")
            print(result.stdout)
        else:
            print("📤 标准输出: (无)")
        
        if result.stderr:
            print()
            print("📤 标准错误:")
            print(result.stderr)
        else:
            print()
            print("📤 标准错误: (无)")
            
    except Exception as e:
        print(f"❌ 执行失败: {e}")

if __name__ == "__main__":
    test_case_execution()

