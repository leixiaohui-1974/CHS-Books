#!/usr/bin/env python3
"""测试路径是否正确"""

from pathlib import Path

# 模拟textbook_routes.py中的路径计算
current_file = Path(__file__)  # scripts/test_paths.py
print(f"当前文件: {current_file}")
print(f"  .parent: {current_file.parent}")  # scripts
print(f"  .parent.parent: {current_file.parent.parent}")  # backend
print(f"  .parent.parent.parent: {current_file.parent.parent.parent}")  # platform
print(f"  .parent.parent.parent.parent: {current_file.parent.parent.parent.parent}")  # project_root

# 计算books路径（从scripts出发）
books_from_scripts = current_file.parent.parent.parent / 'books'
print(f"\n从scripts计算books路径: {books_from_scripts}")
print(f"存在: {books_from_scripts.exists()}")

# 模拟从textbook_routes.py计算（需要多一层parent）
# textbook_routes.py -> platform/backend/api/textbook_routes.py
api_file = current_file.parent.parent / 'api' / 'textbook_routes.py'
print(f"\ntextbook_routes.py的模拟路径: {api_file}")
books_from_api = api_file.parent.parent.parent.parent / 'books'
print(f"从API计算books路径: {books_from_api}")
print(f"存在: {books_from_api.exists()}")

# 列出books目录
if books_from_api.exists():
    print(f"\nbooks目录内容:")
    for item in sorted(books_from_api.iterdir()):
        if item.is_dir():
            examples = item / 'code' / 'examples'
            if examples.exists():
                case_count = len([d for d in examples.iterdir() if d.is_dir()])
                print(f"  - {item.name}: {case_count} 个案例")
            else:
                print(f"  - {item.name}: 无案例目录")

