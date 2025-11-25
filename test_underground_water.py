#!/usr/bin/env python3
"""Test all underground-water-dynamics cases"""
import subprocess
import os
from pathlib import Path

base_dir = Path("/home/user/CHS-Books/books/underground-water-dynamics/code/examples")
passed = 0
failed = 0
timeout_count = 0

case_dirs = sorted([d for d in base_dir.iterdir() if d.is_dir() and d.name.startswith("case_")])

print(f"Testing {len(case_dirs)} underground-water-dynamics cases...")
print("=" * 50)

for case_dir in case_dirs:
    py_files = list(case_dir.glob("*.py"))
    if py_files:
        py_file = py_files[0]
        try:
            result = subprocess.run(
                ["python", str(py_file)],
                capture_output=True,
                timeout=90,
                cwd=str(case_dir)
            )
            if result.returncode == 0:
                print(f"✅ {case_dir.name}")
                passed += 1
            else:
                print(f"❌ {case_dir.name}")
                # Print error for debugging
                stderr = result.stderr.decode()[-200:] if result.stderr else ""
                if stderr:
                    print(f"   Error: {stderr.split(chr(10))[-2] if stderr else 'Unknown'}")
                failed += 1
        except subprocess.TimeoutExpired:
            print(f"⏱️  {case_dir.name} (timeout)")
            timeout_count += 1

print("=" * 50)
total = passed + failed + timeout_count
pass_rate = passed * 100 // total if total > 0 else 0
print(f"\nResults: {passed} passed, {failed} failed, {timeout_count} timeout")
print(f"Pass rate: {pass_rate}%")
