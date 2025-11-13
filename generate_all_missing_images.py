#!/usr/bin/env python3
"""
批量生成所有缺失的图片
"""

import os
import subprocess
import json
from pathlib import Path

# 读取缺失图片列表
with open('platform/test_reports/perfect-source-check-20251113_233613.json', 'r') as f:
    data = json.load(f)

missing_images = data['images']['missing']

print(f"发现 {len(missing_images)} 个缺失的图片")
print("="*80)

# 按目录分组
dirs_to_process = {}
for img_info in missing_images:
    img_path = Path(img_info['expected_path'])
    case_dir = img_path.parent

    if case_dir not in dirs_to_process:
        dirs_to_process[case_dir] = []
    dirs_to_process[case_dir].append(img_path.name)

print(f"需要处理 {len(dirs_to_process)} 个案例目录")
print()

generated = 0
failed = 0

for case_dir, images in dirs_to_process.items():
    print(f"\n处理目录: {case_dir}")
    print(f"缺失图片: {', '.join(images)}")

    # 查找main.py或generate_diagram.py
    main_script = None
    if (case_dir / 'main.py').exists():
        main_script = case_dir / 'main.py'
    elif (case_dir / 'generate_diagram.py').exists():
        main_script = case_dir / 'generate_diagram.py'

    if main_script:
        print(f"  找到脚本: {main_script.name}")
        try:
            # 运行Python脚本
            result = subprocess.run(
                ['python3', main_script.name],
                cwd=case_dir,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                # 检查图片是否生成
                generated_count = 0
                for img_name in images:
                    if (case_dir / img_name).exists():
                        generated_count += 1
                        generated += 1

                if generated_count > 0:
                    print(f"  ✅ 成功生成 {generated_count}/{len(images)} 个图片")
                else:
                    print(f"  ⚠️ 脚本运行成功但未生成图片")
                    failed += len(images)
            else:
                print(f"  ❌ 脚本运行失败: {result.stderr[:200]}")
                failed += len(images)

        except subprocess.TimeoutExpired:
            print(f"  ❌ 脚本超时")
            failed += len(images)
        except Exception as e:
            print(f"  ❌ 异常: {str(e)}")
            failed += len(images)
    else:
        print(f"  ⚠️ 未找到生成脚本")
        failed += len(images)

print("\n" + "="*80)
print(f"总计: 成功生成 {generated} 个, 失败 {failed} 个")
print("="*80)
