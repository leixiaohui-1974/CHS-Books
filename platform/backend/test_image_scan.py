#!/usr/bin/env python3
"""
测试图片扫描功能
"""

from pathlib import Path
import subprocess
import sys
import time
import os

# 路径设置
BACKEND_DIR = Path(__file__).parent
BOOKS_BASE_DIR = BACKEND_DIR.parent.parent  # 指向CHS-Books根目录

book_slug = "water-system-control"
case_id = "case_01_home_water_tower"

# 找到案例路径
case_path = BOOKS_BASE_DIR / "books" / "water-system-control" / "code" / "examples" / case_id
main_file = case_path / "main.py"

print(f"案例路径: {case_path}")
print(f"main.py存在: {main_file.exists()}")
print(f"案例路径存在: {case_path.exists()}")

# 先列出现有的PNG文件
print(f"\n运行前的PNG文件:")
for img_file in case_path.glob("*.png"):
    print(f"  - {img_file.name}")

# 删除旧的PNG文件
print(f"\n删除旧的PNG文件...")
for img_file in case_path.glob("*.png"):
    img_file.unlink()
    print(f"  已删除: {img_file.name}")

# 运行脚本
print(f"\n运行脚本...")
env = os.environ.copy()
env['PYTHONIOENCODING'] = 'utf-8'

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
print(f"执行成功: {result.returncode == 0}")

# 等待文件系统同步
print(f"\n等待文件系统同步...")
time.sleep(0.5)

# 扫描生成的图片文件
print(f"\n扫描生成的PNG文件:")
images = []
for img_file in case_path.glob("*.png"):
    print(f"  找到: {img_file.name}")
    images.append({
        "filename": img_file.name,
        "url": f"/api/v1/books/{book_slug}/cases/{case_id}/images/{img_file.name}"
    })

print(f"\n共找到 {len(images)} 张图片")
for img in images:
    print(f"  - {img['filename']}: {img['url']}")

