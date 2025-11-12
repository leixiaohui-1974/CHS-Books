#!/usr/bin/env python3
"""
Quick test - First 5 cases only
No GUI, save charts to files
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

# Import matplotlib with non-GUI backend FIRST
import matplotlib
matplotlib.use('Agg')  # Must be before importing pyplot
import matplotlib.pyplot as plt

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
    print(f"\n{'='*60}")
    print(f"Testing: {case_id}")
    print(f"Title: {case_title}")
    
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
            timeout=30,  # Shorter timeout for quick test
            encoding='utf-8',
            errors='replace',
            env=env
        )
        execution_time = time.time() - start_time
        
        success = result.returncode == 0
        
        if success:
            print(f"✅ Success! (Time: {execution_time:.2f}s)")
        else:
            print(f"❌ Failed! (Return code: {result.returncode})")
            if result.stderr:
                print(f"Error: {result.stderr[:200]}")
        
        return {
            "case_id": case_id,
            "title": case_title,
            "success": success,
            "returncode": result.returncode,
            "execution_time": execution_time,
            "error": result.stderr[-300:] if not success and result.stderr else None
        }
        
    except subprocess.TimeoutExpired:
        execution_time = time.time() - start_time
        print(f"⏱️ Timeout (>30s)")
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

def generate_simple_chart(results, output_dir):
    """Generate simple bar chart - no GUI"""
    print("\n📊 Generating chart (no GUI)...")
    
    case_ids = [r['case_id'].replace('case_', 'C').replace('_home_water_tower', '1').replace('_cooling_tower', '2').replace('_water_supply_station', '3').replace('_pid_tuning', '4').replace('_parameter_identification', '5') for r in results]
    times = [r.get('execution_time', 0) for r in results]
    colors = ['#28a745' if r['success'] else '#dc3545' for r in results]
    
    # Create figure without showing
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(range(len(case_ids)), times, color=colors, alpha=0.8, edgecolor='black')
    
    ax.set_xlabel('Case ID', fontsize=12, weight='bold')
    ax.set_ylabel('Execution Time (seconds)', fontsize=12, weight='bold')
    ax.set_title('Execution Time - First 5 Cases', fontsize=14, weight='bold')
    ax.set_xticks(range(len(case_ids)))
    ax.set_xticklabels(case_ids)
    ax.grid(axis='y', alpha=0.3)
    
    # Add value labels
    for bar, time_val in zip(bars, times):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{time_val:.2f}s',
                ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    
    # Save without showing
    chart_file = output_dir / 'quick_test_chart.png'
    plt.savefig(chart_file, dpi=200, bbox_inches='tight')
    plt.close(fig)  # Close the figure explicitly
    
    print(f"✅ Chart saved to: {chart_file}")
    return chart_file

def main():
    """Main test function"""
    print("\n" + "="*60)
    print("🚀 Quick Test - First 5 Cases")
    print("="*60)
    print(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Load cases
    cases_index = load_cases_index()
    
    water_cases = None
    for book in cases_index.get("books", []):
        if book["slug"] == "water-system-control":
            water_cases = book.get("cases", [])[:5]  # Only first 5
            break
    
    if not water_cases:
        print("❌ Cases not found")
        return
    
    print(f"\n📚 Testing {len(water_cases)} cases...")
    
    # Test cases
    results = []
    for i, case in enumerate(water_cases, 1):
        case_id = case["id"]
        case_title = case.get("title", case_id)
        case_path = BOOKS_BASE_DIR / case["path"]
        
        print(f"\n[{i}/{len(water_cases)}]")
        result = test_single_case(case_id, case_path, case_title)
        results.append(result)
    
    # Summary
    success_count = sum(1 for r in results if r['success'])
    total_time = sum(r.get('execution_time', 0) for r in results)
    
    print("\n" + "="*60)
    print("📊 Summary")
    print("="*60)
    print(f"Total: {len(results)}")
    print(f"✅ Success: {success_count}")
    print(f"❌ Failed: {len(results) - success_count}")
    print(f"Success Rate: {success_count / len(results) * 100:.1f}%")
    print(f"Total Time: {total_time:.2f}s")
    print(f"Average: {total_time / len(results):.2f}s/case")
    
    # Generate chart (no GUI)
    chart_file = generate_simple_chart(results, BACKEND_DIR)
    
    # Save report
    report_file = BACKEND_DIR / "quick_test_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump({
            "test_time": datetime.now().isoformat(),
            "results": results,
            "summary": {
                "total": len(results),
                "success": success_count,
                "failed": len(results) - success_count,
                "total_time": total_time
            }
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 Report saved: {report_file}")
    print(f"📊 Chart saved: {chart_file}")
    print(f"\nEnd: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

if __name__ == "__main__":
    # Ensure no GUI is shown
    import os
    os.environ['MPLBACKEND'] = 'Agg'
    main()

