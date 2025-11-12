from pathlib import Path

# 模拟case_routes.py的路径计算
case_routes_file = Path(__file__).parent.parent / 'api' / 'case_routes.py'
books_root = case_routes_file.parent.parent.parent.parent / 'books'

print(f"case_routes.py位置: {case_routes_file}")
print(f"books_root: {books_root}")
print(f"books_root存在: {books_root.exists()}")

if books_root.exists():
    print(f"\nbooks_root内容:")
    for item in sorted(books_root.iterdir())[:5]:
        print(f"  - {item.name}")
    
    # 测试water-system-control
    wsc_dir = books_root / 'water-system-control'
    examples_dir = wsc_dir / 'code' / 'examples'
    print(f"\nexamples_dir: {examples_dir}")
    print(f"examples_dir存在: {examples_dir.exists()}")
    
    if examples_dir.exists():
        print(f"\nexamples_dir内容:")
        for item in sorted(examples_dir.iterdir())[:5]:
            print(f"  - {item.name}")
        
        # 测试case_01_home_water_tower
        case_dir = examples_dir / 'case_01_home_water_tower'
        print(f"\ncase_dir: {case_dir}")
        print(f"case_dir存在: {case_dir.exists()}")
        
        if case_dir.exists():
            readme = case_dir / 'README.md'
            print(f"README.md存在: {readme.exists()}")

