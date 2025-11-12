#!/usr/bin/env python3
"""
完整模拟后端图片API逻辑
"""

from pathlib import Path
import json

# 路径设置 - 与full_server.py相同
BACKEND_DIR = Path(__file__).parent
CASES_INDEX_FILE = BACKEND_DIR / "cases_index.json"
BOOKS_BASE_DIR = BACKEND_DIR.parent.parent  # 指向CHS-Books根目录

def load_cases_index():
    """加载案例索引"""
    if not CASES_INDEX_FILE.exists():
        return {"books": []}
    
    with open(CASES_INDEX_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_case_image(book_slug: str, case_id: str, filename: str):
    """模拟后端get_case_image函数"""
    print(f"\n=== Simulating API call ===")
    print(f"book_slug: {book_slug}")
    print(f"case_id: {case_id}")
    print(f"filename: {filename}")
    
    cases_index = load_cases_index()
    print(f"\nLoaded cases_index, has {len(cases_index.get('books', []))} books")
    
    case_path = None
    for book_cases in cases_index.get("books", []):
        print(f"\nChecking book: {book_cases.get('slug')}")
        if book_cases["slug"] == book_slug:
            print(f"  [OK] Book matched!")
            cases = book_cases.get("cases", [])
            print(f"  Found {len(cases)} cases")
            for case in cases:
                if case["id"] == case_id:
                    print(f"    [OK] Case matched: {case['id']}")
                    case_path = BOOKS_BASE_DIR / case["path"]
                    print(f"    case_path: {case_path}")
                    break
            break
    
    if not case_path:
        print("\n[ERROR] Case not found in index!")
        return {"status": 404, "detail": "Case not found in index"}
    
    if not case_path.exists():
        print(f"\n[ERROR] Case path does not exist: {case_path}")
        return {"status": 404, "detail": "Path does not exist"}
    
    print(f"\n[OK] Case path exists")
    
    image_path = case_path / filename
    print(f"\nimage_path: {image_path}")
    print(f"  exists: {image_path.exists()}")
    print(f"  suffix: {image_path.suffix}")
    
    if not image_path.exists():
        print(f"\n[ERROR] Image file does not exist")
        return {"status": 404, "detail": "File does not exist"}
    
    if image_path.suffix != '.png':
        print(f"\n[ERROR] File is not a PNG")
        return {"status": 404, "detail": "Not a PNG file"}
    
    print(f"\n[OK] All checks passed! Would serve: {image_path}")
    print(f"  File size: {image_path.stat().st_size} bytes")
    return {"status": 200, "path": str(image_path)}

# 测试
result = get_case_image(
    book_slug="water-system-control",
    case_id="case_01_home_water_tower",
    filename="water_tower_diagram.png"
)

print(f"\n=== Result ===")
print(result)

