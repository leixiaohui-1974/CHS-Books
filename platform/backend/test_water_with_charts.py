#!/usr/bin/env python3
"""
Water System Control - Complete Testing with Charts
Tests all 20 cases and generates detailed reports with charts (English labels)
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
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np

# Path settings
BACKEND_DIR = Path(__file__).parent
CASES_INDEX_FILE = BACKEND_DIR / "cases_index.json"
BOOKS_BASE_DIR = BACKEND_DIR.parent.parent

def load_cases_index():
    """Load cases index"""
    with open(CASES_INDEX_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def test_single_case(case_id, case_path, case_title, index):
    """Test single case"""
    print(f"\n{'='*80}")
    print(f"[{index}] Testing: {case_id}")
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
    
    # Execute case
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
            "error": result.stderr[-200:] if not success and result.stderr else None
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
    """Generate charts with English labels"""
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # Chart 1: Success/Fail Pie Chart
    fig, ax = plt.subplots(figsize=(10, 8))
    success_count = sum(1 for r in results if r['success'])
    fail_count = len(results) - success_count
    
    colors = ['#4CAF50', '#F44336']
    explode = (0.05, 0.05)
    
    wedges, texts, autotexts = ax.pie(
        [success_count, fail_count],
        labels=['Success', 'Failed'],
        autopct='%1.1f%%',
        colors=colors,
        explode=explode,
        shadow=True,
        startangle=90
    )
    
    for text in texts:
        text.set_fontsize(14)
        text.set_weight('bold')
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize(12)
        autotext.set_weight('bold')
    
    ax.set_title('Water System Control - Test Results', fontsize=16, weight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(output_dir / 'test_results_pie.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Chart saved: test_results_pie.png")
    
    # Chart 2: Execution Time Bar Chart
    fig, ax = plt.subplots(figsize=(16, 10))
    
    case_nums = [i+1 for i in range(len(results))]
    times = [r.get('execution_time', 0) for r in results]
    colors_bar = ['#4CAF50' if r['success'] else '#F44336' for r in results]
    
    bars = ax.bar(case_nums, times, color=colors_bar, alpha=0.8, edgecolor='black', linewidth=0.5)
    
    ax.set_xlabel('Case Number', fontsize=14, weight='bold')
    ax.set_ylabel('Execution Time (seconds)', fontsize=14, weight='bold')
    ax.set_title('Execution Time for Each Test Case', fontsize=16, weight='bold', pad=20)
    ax.set_xticks(case_nums)
    ax.set_xticklabels([f'C{i}' for i in case_nums], rotation=45, ha='right')
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#4CAF50', label='Success'),
        Patch(facecolor='#F44336', label='Failed')
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=12)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'execution_time_bar.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Chart saved: execution_time_bar.png")
    
    # Chart 3: Cumulative Success Rate
    fig, ax = plt.subplots(figsize=(14, 8))
    
    cumulative_success = []
    running_success = 0
    for i, r in enumerate(results, 1):
        if r['success']:
            running_success += 1
        cumulative_success.append((running_success / i) * 100)
    
    ax.plot(case_nums, cumulative_success, marker='o', linewidth=2, 
            markersize=6, color='#2196F3', markerfacecolor='white', 
            markeredgewidth=2, markeredgecolor='#2196F3')
    
    ax.set_xlabel('Case Number', fontsize=14, weight='bold')
    ax.set_ylabel('Cumulative Success Rate (%)', fontsize=14, weight='bold')
    ax.set_title('Cumulative Success Rate Over Test Cases', fontsize=16, weight='bold', pad=20)
    ax.set_xticks(case_nums)
    ax.set_xticklabels([f'C{i}' for i in case_nums], rotation=45, ha='right')
    ax.set_ylim([0, 105])
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Add horizontal line at 100%
    ax.axhline(y=100, color='green', linestyle='--', linewidth=1, alpha=0.5)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'cumulative_success_rate.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Chart saved: cumulative_success_rate.png")
    
    # Chart 4: Statistics Summary
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # 4.1: Success vs Failed Count
    categories = ['Success', 'Failed']
    counts = [success_count, fail_count]
    bars1 = ax1.bar(categories, counts, color=['#4CAF50', '#F44336'], alpha=0.8, edgecolor='black')
    ax1.set_ylabel('Number of Cases', fontsize=12, weight='bold')
    ax1.set_title('Success vs Failed Cases', fontsize=14, weight='bold')
    ax1.grid(axis='y', alpha=0.3)
    for bar in bars1:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontsize=12, weight='bold')
    
    # 4.2: Execution Time Statistics
    exec_times = [r.get('execution_time', 0) for r in results if r['success']]
    if exec_times:
        stats_labels = ['Min', 'Max', 'Mean', 'Median']
        stats_values = [
            min(exec_times),
            max(exec_times),
            np.mean(exec_times),
            np.median(exec_times)
        ]
        bars2 = ax2.bar(stats_labels, stats_values, color='#2196F3', alpha=0.8, edgecolor='black')
        ax2.set_ylabel('Time (seconds)', fontsize=12, weight='bold')
        ax2.set_title('Execution Time Statistics', fontsize=14, weight='bold')
        ax2.grid(axis='y', alpha=0.3)
        for bar in bars2:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}',
                    ha='center', va='bottom', fontsize=10, weight='bold')
    
    # 4.3: Success Rate Progress
    success_rates_per_5 = []
    for i in range(0, len(results), 5):
        batch = results[i:i+5]
        batch_success = sum(1 for r in batch if r['success'])
        success_rates_per_5.append((batch_success / len(batch)) * 100)
    
    batch_labels = [f'Cases {i+1}-{min(i+5, len(results))}' for i in range(0, len(results), 5)]
    bars3 = ax3.bar(range(len(success_rates_per_5)), success_rates_per_5, 
                    color='#FF9800', alpha=0.8, edgecolor='black')
    ax3.set_ylabel('Success Rate (%)', fontsize=12, weight='bold')
    ax3.set_title('Success Rate by Batch (5 cases)', fontsize=14, weight='bold')
    ax3.set_xticks(range(len(success_rates_per_5)))
    ax3.set_xticklabels(batch_labels, rotation=15, ha='right', fontsize=9)
    ax3.set_ylim([0, 105])
    ax3.grid(axis='y', alpha=0.3)
    ax3.axhline(y=100, color='green', linestyle='--', linewidth=1, alpha=0.5)
    
    # 4.4: Overall Summary Text
    ax4.axis('off')
    summary_text = f"""
    Test Summary
    {'='*40}
    
    Total Cases:        {len(results)}
    Successful:         {success_count}
    Failed:            {fail_count}
    Success Rate:      {(success_count/len(results)*100):.1f}%
    
    Total Time:        {sum(r.get('execution_time', 0) for r in results):.2f}s
    Average Time:      {sum(r.get('execution_time', 0) for r in results)/len(results):.2f}s
    
    Fastest Case:      {min(exec_times) if exec_times else 0:.2f}s
    Slowest Case:      {max(exec_times) if exec_times else 0:.2f}s
    """
    ax4.text(0.1, 0.5, summary_text, fontsize=12, family='monospace',
            verticalalignment='center', bbox=dict(boxstyle='round', 
            facecolor='wheat', alpha=0.3))
    
    plt.tight_layout()
    plt.savefig(output_dir / 'statistics_summary.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Chart saved: statistics_summary.png")

def generate_html_report(results, report_file):
    """Generate HTML report"""
    success_count = sum(1 for r in results if r['success'])
    total_time = sum(r.get('execution_time', 0) for r in results)
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Water System Control - Test Report</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
                background-color: #f5f5f5;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background-color: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #2196F3;
                border-bottom: 3px solid #2196F3;
                padding-bottom: 10px;
            }}
            .summary {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin: 20px 0;
            }}
            .stat-card {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 10px;
                text-align: center;
            }}
            .stat-card.success {{
                background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            }}
            .stat-card.failed {{
                background: linear-gradient(135deg, #F44336 0%, #d32f2f 100%);
            }}
            .stat-value {{
                font-size: 36px;
                font-weight: bold;
                margin: 10px 0;
            }}
            .stat-label {{
                font-size: 14px;
                opacity: 0.9;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }}
            th {{
                background-color: #2196F3;
                color: white;
                padding: 12px;
                text-align: left;
            }}
            td {{
                padding: 10px;
                border-bottom: 1px solid #ddd;
            }}
            tr:hover {{
                background-color: #f5f5f5;
            }}
            .success-icon {{
                color: #4CAF50;
                font-weight: bold;
            }}
            .failed-icon {{
                color: #F44336;
                font-weight: bold;
            }}
            .charts {{
                margin: 30px 0;
            }}
            .chart-image {{
                width: 100%;
                margin: 20px 0;
                border: 1px solid #ddd;
                border-radius: 5px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Water System Control - Test Report</h1>
            <p><strong>Test Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            
            <div class="summary">
                <div class="stat-card">
                    <div class="stat-label">Total Cases</div>
                    <div class="stat-value">{len(results)}</div>
                </div>
                <div class="stat-card success">
                    <div class="stat-label">Successful</div>
                    <div class="stat-value">{success_count}</div>
                </div>
                <div class="stat-card failed">
                    <div class="stat-label">Failed</div>
                    <div class="stat-value">{len(results) - success_count}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Success Rate</div>
                    <div class="stat-value">{success_count / len(results) * 100:.1f}%</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Total Time</div>
                    <div class="stat-value">{total_time:.1f}s</div>
                </div>
            </div>
            
            <h2>📊 Test Charts</h2>
            <div class="charts">
                <img src="test_results_pie.png" class="chart-image" alt="Test Results">
                <img src="execution_time_bar.png" class="chart-image" alt="Execution Time">
                <img src="cumulative_success_rate.png" class="chart-image" alt="Success Rate">
                <img src="statistics_summary.png" class="chart-image" alt="Statistics">
            </div>
            
            <h2>📋 Detailed Results</h2>
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Case ID</th>
                        <th>Title</th>
                        <th>Status</th>
                        <th>Time (s)</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    for i, r in enumerate(results, 1):
        status_icon = '✅' if r['success'] else '❌'
        status_class = 'success-icon' if r['success'] else 'failed-icon'
        html_content += f"""
                    <tr>
                        <td>{i}</td>
                        <td><code>{r['case_id']}</code></td>
                        <td>{r['title']}</td>
                        <td class="{status_class}">{status_icon}</td>
                        <td>{r.get('execution_time', 0):.2f}</td>
                    </tr>
        """
    
    html_content += """
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ HTML report saved: {report_file}")

def main():
    """Main test function"""
    print("\n" + "="*80)
    print("🚀 Water System Control - Complete Testing with Charts")
    print("="*80)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Load cases
    cases_index = load_cases_index()
    
    book_slug = "water-system-control"
    water_cases = None
    
    for book in cases_index.get("books", []):
        if book["slug"] == book_slug:
            water_cases = book.get("cases", [])
            print(f"📚 Found: Water System Control ({len(water_cases)} cases)")
            break
    
    if not water_cases:
        print(f"❌ Water System Control cases not found")
        return
    
    print()
    print(f"Preparing to test {len(water_cases)} cases...")
    print()
    
    # Test all cases
    results = []
    
    for i, case in enumerate(water_cases, 1):
        result = test_single_case(
            case["id"],
            BOOKS_BASE_DIR / case["path"],
            case.get("title", case["id"]),
            i
        )
        results.append(result)
    
    # Generate summary
    success_count = sum(1 for r in results if r['success'])
    total_time = sum(r.get('execution_time', 0) for r in results)
    
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
    
    # Save reports
    print("Generating reports and charts...")
    
    # JSON report
    report = {
        "test_time": datetime.now().isoformat(),
        "book": "water-system-control",
        "total_cases": len(results),
        "success_count": success_count,
        "success_rate": success_count / len(results),
        "total_time": total_time,
        "results": results
    }
    
    report_file = BACKEND_DIR / "water_test_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"✅ JSON report saved: {report_file}")
    
    # Generate charts
    generate_charts(results, BACKEND_DIR)
    
    # Generate HTML report
    html_file = BACKEND_DIR / "water_test_report.html"
    generate_html_report(results, html_file)
    
    print()
    print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    print()
    print("✅ All reports and charts generated!")
    print(f"   - JSON: water_test_report.json")
    print(f"   - HTML: water_test_report.html")
    print(f"   - Charts: *.png")

if __name__ == "__main__":
    main()

