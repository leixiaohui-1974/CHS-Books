#!/usr/bin/env python3
"""
测试图片路径解析
"""

from pathlib import Path
import json

# 路径设置
BACKEND_DIR = Path(__file__).parent
BOOKS_BASE_DIR = BACKEND_DIR.parent.parent  # 指向CHS-Books根目录
CASES_INDEX_FILE = BACKEND_DIR / "cases_index.json"

print(f"BACKEND_DIR: {BACKEND_DIR}")
print(f"BOOKS_BASE_DIR: {BOOKS_BASE_DIR}")
print(f"CASES_INDEX_FILE: {CASES_INDEX_FILE}")
print(f"cases_index.json exists: {CASES_INDEX_FILE.exists()}")

# 加载cases_index.json
with open(CASES_INDEX_FILE, 'r', encoding='utf-8') as f:
    cases_index = json.load(f)

# 查找water-system-control/case_01_home_water_tower
book_slug = "water-system-control"
case_id = "case_01_home_water_tower"

case_path = None
for book_cases in cases_index.get("books", []):
    if book_cases["slug"] == book_slug:
        cases = book_cases.get("cases", [])
        for case in cases:
            if case["id"] == case_id:
                case_path = BOOKS_BASE_DIR / case["path"]
                print(f"\nFound case!")
                print(f"  case['path']: {case['path']}")
                print(f"  Resolved case_path: {case_path}")
                print(f"  case_path exists: {case_path.exists()}")
                break
        break

if case_path:
    # 检查水塔示意图
    diagram_path = case_path / "water_tower_diagram.png"
    print(f"\nwater_tower_diagram.png:")
    print(f"  Path: {diagram_path}")
    print(f"  Exists: {diagram_path.exists()}")
    if diagram_path.exists():
        print(f"  Size: {diagram_path.stat().st_size} bytes")
    
    # 列出所有PNG文件
    print(f"\nAll PNG files in case directory:")
    for png_file in case_path.glob("*.png"):
        print(f"  - {png_file.name} ({png_file.stat().st_size} bytes)")
else:
    print("Case not found!")

