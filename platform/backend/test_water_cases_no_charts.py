#!/usr/bin/env python3
"""
Water System Control - Testing WITHOUT Charts
Tests all 20 cases and generates reports (no visualization)
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from pathlib import Path
import json
import subprocess
import os
from datetime import datetime
import time

# Path settings
BACKEND_DIR = Path(__file__).parent
CASES_INDEX_FILE = BACKEND_DIR / "cases_index.json"
BOOKS_BASE_DIR = BACKEND_DIR.parent.parent

def load_cases_index():
    """Load cases index"""
    with open(CASES_INDEX_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def test_single_case(case_id, case_path, case_title):
    """Test a single case"""
    print(f"\n{'='*80}")
    print(f"Testing: {case_id}")
    print(f"Title: {case_title}")
    print(f"{'='*80}")
    
    main_file = case_path / "main.py"
    if not main_file.exists():
        print(f"❌ main.py not found")
        return {
            "case_id": case_id,
            "title": case_title,
            "success": False,
            "error": "main.py not found",
            "execution_time": 0
        }
    
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    
    start_time = time.time()
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
        execution_time = time.time() - start_time
        
        success = result.returncode == 0
        
        if success:
            print(f"✅ Success! (Time: {execution_time:.2f}s)")
            lines = [l for l in result.stdout.split('\n') if l.strip()]
            print(f"📊 Output lines: {len(lines)}")
        else:
            print(f"❌ Failed! (Return code: {result.returncode})")
            if result.stderr:
                error_lines = [l for l in result.stderr.split('\n') if l.strip()][:3]
                for line in error_lines:
                    print(f"   {line}")
        
        return {
            "case_id": case_id,
            "title": case_title,
            "success": success,
            "returncode": result.returncode,
            "execution_time": execution_time,
            "stdout_lines": len(result.stdout.split('\n')),
            "stderr_lines": len(result.stderr.split('\n')) if result.stderr else 0,
            "error": result.stderr[-500:] if not success and result.stderr else None
        }
        
    except subprocess.TimeoutExpired:
        execution_time = time.time() - start_time
        print(f"⏱️ Timeout (>60s)")
        return {
            "case_id": case_id,
            "title": case_title,
            "success": False,
            "error": "Timeout",
            "execution_time": execution_time
        }
    except Exception as e:
        execution_time = time.time() - start_time
        print(f"❌ Exception: {str(e)}")
        return {
            "case_id": case_id,
            "title": case_title,
            "success": False,
            "error": str(e),
            "execution_time": execution_time
        }

def main():
    """Main test function"""
    print("\n" + "="*80)
    print("🚀 Water System Control - Complete Testing (No Charts)")
    print("="*80)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Load cases index
    cases_index = load_cases_index()
    
    # Find water system control cases
    book_slug = "water-system-control"
    water_cases = None
    
    for book in cases_index.get("books", []):
        if book["slug"] == book_slug:
            water_cases = book.get("cases", [])
            print(f"📚 Found 'Water System Control': {len(water_cases)} cases")
            break
    
    if not water_cases:
        print(f"❌ Cases not found")
        return
    
    print()
    print(f"Preparing to test {len(water_cases)} cases...")
    print()
    
    # Test all cases
    results = []
    success_count = 0
    total_time = 0
    
    for i, case in enumerate(water_cases, 1):
        case_id = case["id"]
        case_title = case.get("title", case_id)
        case_path = BOOKS_BASE_DIR / case["path"]
        
        print(f"\n[{i}/{len(water_cases)}] ", end="")
        result = test_single_case(case_id, case_path, case_title)
        results.append(result)
        
        if result["success"]:
            success_count += 1
        
        total_time += result.get("execution_time", 0)
    
    # Generate summary report
    print("\n" + "="*80)
    print("📊 Test Summary")
    print("="*80)
    print(f"Total Cases: {len(results)}")
    print(f"✅ Success: {success_count}")
    print(f"❌ Failed: {len(results) - success_count}")
    print(f"Success Rate: {success_count / len(results) * 100:.1f}%")
    print(f"Total Time: {total_time:.2f}s")
    print(f"Average Time: {total_time / len(results):.2f}s/case")
    print()
    
    # Show failed cases
    failed_cases = [r for r in results if not r["success"]]
    if failed_cases:
        print("❌ Failed Cases:")
        for r in failed_cases:
            print(f"  - {r['case_id']}: {r.get('error', 'Unknown')}")
        print()
    
    # Show successful cases
    print("✅ Successful Cases:")
    success_cases = [r for r in results if r["success"]]
    for r in success_cases:
        print(f"  - {r['case_id']}: {r['execution_time']:.2f}s")
    print()
    
    # Save detailed report
    report = {
        "test_time": datetime.now().isoformat(),
        "book": "water-system-control",
        "book_title": "Water System Control",
        "total_cases": len(results),
        "success_count": success_count,
        "failed_count": len(results) - success_count,
        "success_rate": success_count / len(results) if results else 0,
        "total_time": total_time,
        "average_time": total_time / len(results) if results else 0,
        "results": results
    }
    
    report_file = BACKEND_DIR / "water_test_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"📄 Report saved: {report_file}")
    
    # Generate Markdown report
    md_report_file = BACKEND_DIR / "Water_Test_Report.md"
    with open(md_report_file, 'w', encoding='utf-8') as f:
        f.write(f"# Water System Control - Test Report\n\n")
        f.write(f"**Test Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write(f"## Summary\n\n")
        f.write(f"- **Total Cases**: {len(results)}\n")
        f.write(f"- **✅ Success**: {success_count}\n")
        f.write(f"- **❌ Failed**: {len(results) - success_count}\n")
        f.write(f"- **Success Rate**: {success_count / len(results) * 100:.1f}%\n")
        f.write(f"- **Total Time**: {total_time:.2f}s\n")
        f.write(f"- **Average Time**: {total_time / len(results):.2f}s/case\n\n")
        
        f.write(f"## Detailed Results\n\n")
        f.write(f"| No. | Case ID | Title | Status | Time(s) |\n")
        f.write(f"|-----|---------|-------|--------|----------|\n")
        for i, r in enumerate(results, 1):
            status = "✅" if r["success"] else "❌"
            time_str = f"{r.get('execution_time', 0):.2f}"
            title = r['title'][:40]
            f.write(f"| {i} | {r['case_id']} | {title} | {status} | {time_str} |\n")
        
        if failed_cases:
            f.write(f"\n## Failed Cases\n\n")
            for r in failed_cases:
                f.write(f"### {r['case_id']}\n\n")
                f.write(f"- **Title**: {r['title']}\n")
                f.write(f"- **Error**: {r.get('error', 'Unknown')}\n\n")
    
    print(f"📄 Markdown report saved: {md_report_file}")
    print()
    print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    print()

if __name__ == "__main__":
    main()

