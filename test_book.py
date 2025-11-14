#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

if len(sys.argv) < 2:
    print("用法: python test_book.py <书籍名称>")
    sys.exit(1)

book_name = sys.argv[1]
examples_dir = Path(f'books/{book_name}/code/examples')

if not examples_dir.exists():
    print(f"错误: 找不到{examples_dir}")
    sys.exit(1)

case_dirs = sorted([d for d in examples_dir.iterdir()
                   if d.is_dir() and d.name.startswith('case_')])

print(f"{book_name}案例测试 - 共{len(case_dirs)}个案例\n")

passed = 0
failed = 0

for case_dir in case_dirs:
    case_name = case_dir.name
    main_py = case_dir / 'main.py'

    if not main_py.exists():
        continue

    print(f"测试: {case_name}...", end=" ", flush=True)

    try:
        result = subprocess.run(
            ['python', str(main_py)],
            capture_output=True,
            timeout=120,
            cwd='.'
        )

        if result.returncode == 0:
            num_images = len(list(case_dir.glob('*.png')))
            print(f"✅ PASS ({num_images}张图片)")
            passed += 1
        else:
            print(f"❌ FAIL (退出码{result.returncode})")
            # 打印错误信息帮助调试
            if result.stderr:
                err = result.stderr.decode('utf-8', errors='replace')
                if 'Traceback' in err:
                    # 只打印关键错误行
                    lines = err.split('\n')
                    for line in lines:
                        if 'Error' in line or 'Exception' in line:
                            print(f"      {line.strip()}")
            failed += 1
    except subprocess.TimeoutExpired:
        print("❌ TIMEOUT")
        failed += 1
    except Exception as e:
        print(f"❌ ERROR: {e}")
        failed += 1

print(f"\n总结: ✅{passed}  ❌{failed}  通过率: {passed/(passed+failed)*100:.1f}%")
sys.exit(0 if failed == 0 else 1)
