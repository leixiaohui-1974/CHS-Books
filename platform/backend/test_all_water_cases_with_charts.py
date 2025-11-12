#!/usr/bin/env python3
"""
Water System Control - Complete Automated Testing with Charts
Tests all 20 cases and generates detailed reports with visualizations
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Set matplotlib to non-interactive mode BEFORE importing pyplot
import matplotlib
matplotlib.use('Agg')  # Must be before importing pyplot

from pathlib import Path
import json
import subprocess
import os
from datetime import datetime
import time
import matplotlib.pyplot as plt
import numpy as np

# Ensure no display
plt.ioff()  # Turn off interactive mode

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

def generate_charts(results, output_dir):
    """Generate visualization charts"""
    print("\n📊 Generating charts...")
    
    # Set style
    plt.style.use('seaborn-v0_8-darkgrid')
    
    # Chart 1: Success Rate Pie Chart
    success_count = sum(1 for r in results if r['success'])
    failed_count = len(results) - success_count
    
    fig, ax = plt.subplots(figsize=(10, 8))
    colors = ['#28a745', '#dc3545']
    sizes = [success_count, failed_count]
    labels = [f'Success: {success_count}', f'Failed: {failed_count}']
    explode = (0.05, 0.05)
    
    wedges, texts, autotexts = ax.pie(sizes, explode=explode, labels=labels, colors=colors,
                                        autopct='%1.1f%%', shadow=True, startangle=90,
                                        textprops={'fontsize': 12, 'weight': 'bold'})
    
    ax.set_title('Test Results - Success Rate', fontsize=16, weight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(output_dir / 'success_rate_pie.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✅ Success rate pie chart saved")
    
    # Chart 2: Execution Time Bar Chart
    case_ids = [r['case_id'].replace('case_', 'C') for r in results]
    times = [r.get('execution_time', 0) for r in results]
    colors_bar = ['#28a745' if r['success'] else '#dc3545' for r in results]
    
    fig, ax = plt.subplots(figsize=(16, 8))
    bars = ax.bar(range(len(case_ids)), times, color=colors_bar, alpha=0.8, edgecolor='black', linewidth=1.2)
    
    ax.set_xlabel('Case ID', fontsize=14, weight='bold')
    ax.set_ylabel('Execution Time (seconds)', fontsize=14, weight='bold')
    ax.set_title('Execution Time per Case', fontsize=16, weight='bold', pad=20)
    ax.set_xticks(range(len(case_ids)))
    ax.set_xticklabels(case_ids, rotation=45, ha='right')
    ax.grid(axis='y', alpha=0.3)
    
    # Add value labels on bars
    for i, (bar, time_val) in enumerate(zip(bars, times)):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{time_val:.2f}s',
                ha='center', va='bottom', fontsize=9, weight='bold')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'execution_time_bar.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✅ Execution time bar chart saved")
    
    # Chart 3: Statistics Summary
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
    
    # 3.1 Total cases
    ax1.text(0.5, 0.5, f'{len(results)}', ha='center', va='center', 
             fontsize=60, weight='bold', color='#007bff')
    ax1.text(0.5, 0.2, 'Total Cases', ha='center', va='center',
             fontsize=16, weight='bold')
    ax1.axis('off')
    
    # 3.2 Success count
    ax2.text(0.5, 0.5, f'{success_count}', ha='center', va='center',
             fontsize=60, weight='bold', color='#28a745')
    ax2.text(0.5, 0.2, 'Successful Cases', ha='center', va='center',
             fontsize=16, weight='bold')
    ax2.axis('off')
    
    # 3.3 Success rate
    success_rate = (success_count / len(results) * 100) if results else 0
    ax3.text(0.5, 0.5, f'{success_rate:.1f}%', ha='center', va='center',
             fontsize=60, weight='bold', color='#ffc107')
    ax3.text(0.5, 0.2, 'Success Rate', ha='center', va='center',
             fontsize=16, weight='bold')
    ax3.axis('off')
    
    # 3.4 Average time
    avg_time = sum(r.get('execution_time', 0) for r in results) / len(results) if results else 0
    ax4.text(0.5, 0.5, f'{avg_time:.2f}s', ha='center', va='center',
             fontsize=60, weight='bold', color='#6f42c1')
    ax4.text(0.5, 0.2, 'Average Time', ha='center', va='center',
             fontsize=16, weight='bold')
    ax4.axis('off')
    
    fig.suptitle('Test Statistics Summary', fontsize=18, weight='bold', y=0.98)
    plt.tight_layout()
    plt.savefig(output_dir / 'statistics_summary.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✅ Statistics summary chart saved")
    
    # Chart 4: Cumulative Time Line Chart
    cumulative_times = []
    cumsum = 0
    for r in results:
        cumsum += r.get('execution_time', 0)
        cumulative_times.append(cumsum)
    
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(range(1, len(results)+1), cumulative_times, 
            marker='o', linewidth=2, markersize=6, color='#007bff')
    ax.fill_between(range(1, len(results)+1), cumulative_times, alpha=0.3, color='#007bff')
    
    ax.set_xlabel('Case Number', fontsize=14, weight='bold')
    ax.set_ylabel('Cumulative Time (seconds)', fontsize=14, weight='bold')
    ax.set_title('Cumulative Execution Time', fontsize=16, weight='bold', pad=20)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'cumulative_time_line.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✅ Cumulative time line chart saved")
    
    print("✅ All charts generated successfully!\n")

def main():
    """Main test function"""
    print("\n" + "="*80)
    print("🚀 Water System Control - Complete Automated Testing")
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
    
    report_file = BACKEND_DIR / "water_system_control_test_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"📄 Detailed report saved: {report_file}")
    
    # Generate charts
    generate_charts(results, BACKEND_DIR)
    
    # Generate Markdown report with English
    md_report_file = BACKEND_DIR / "Water_System_Control_Test_Report.md"
    with open(md_report_file, 'w', encoding='utf-8') as f:
        f.write(f"# Water System Control - Complete Test Report\n\n")
        f.write(f"**Test Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write(f"## Test Summary\n\n")
        f.write(f"- **Total Cases**: {len(results)}\n")
        f.write(f"- **✅ Success**: {success_count}\n")
        f.write(f"- **❌ Failed**: {len(results) - success_count}\n")
        f.write(f"- **Success Rate**: {success_count / len(results) * 100:.1f}%\n")
        f.write(f"- **Total Time**: {total_time:.2f}s\n")
        f.write(f"- **Average Time**: {total_time / len(results):.2f}s/case\n\n")
        
        f.write(f"## Visualizations\n\n")
        f.write(f"### Success Rate\n")
        f.write(f"![Success Rate](success_rate_pie.png)\n\n")
        f.write(f"### Execution Time per Case\n")
        f.write(f"![Execution Time](execution_time_bar.png)\n\n")
        f.write(f"### Statistics Summary\n")
        f.write(f"![Statistics](statistics_summary.png)\n\n")
        f.write(f"### Cumulative Time\n")
        f.write(f"![Cumulative Time](cumulative_time_line.png)\n\n")
        
        f.write(f"## Detailed Results\n\n")
        f.write(f"| No. | Case ID | Title | Status | Time(s) |\n")
        f.write(f"|-----|---------|-------|--------|----------|\n")
        for i, r in enumerate(results, 1):
            status = "✅" if r["success"] else "❌"
            time_str = f"{r.get('execution_time', 0):.2f}"
            title = r['title'][:50]  # Truncate long titles
            f.write(f"| {i} | {r['case_id']} | {title} | {status} | {time_str} |\n")
        
        failed_cases = [r for r in results if not r["success"]]
        if failed_cases:
            f.write(f"\n## Failed Cases Details\n\n")
            for r in failed_cases:
                f.write(f"### {r['case_id']}\n\n")
                f.write(f"- **Title**: {r['title']}\n")
                f.write(f"- **Error**: {r.get('error', 'Unknown error')}\n\n")
    
    print(f"📄 Markdown report saved: {md_report_file}")
    print()
    print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    print()

if __name__ == "__main__":
    main()

