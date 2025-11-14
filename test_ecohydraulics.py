#!/usr/bin/env python3
import subprocess
from pathlib import Path

examples_dir = Path('books/ecohydraulics/code/examples')
case_dirs = sorted([d for d in examples_dir.iterdir()
                   if d.is_dir() and d.name.startswith('case_')])

print(f"生态水力学案例测试 - 共{len(case_dirs)}个案例\n")

passed = 0
failed = 0

for case_dir in case_dirs:
    case_name = case_dir.name
    main_py = case_dir / 'main.py'

    if not main_py.exists():
        continue

    print(f"测试: {case_name}...", end=" ", flush=True)

    try:
        # 从项目根目录运行，这样import路径才正确
        result = subprocess.run(
            ['python', str(main_py)],
            capture_output=True,
            timeout=120,
            cwd='.'  # 在项目根目录运行
        )

        if result.returncode == 0:
            num_images = len(list(case_dir.glob('*.png')))
            print(f"✅ PASS ({num_images}张图片)")
            passed += 1
        else:
            print(f"❌ FAIL (退出码{result.returncode})")
            failed += 1
    except subprocess.TimeoutExpired:
        print("❌ TIMEOUT")
        failed += 1
    except Exception as e:
        print(f"❌ ERROR: {e}")
        failed += 1

print(f"\n总结: ✅{passed}  ❌{failed}  通过率: {passed/(passed+failed)*100:.1f}%")
