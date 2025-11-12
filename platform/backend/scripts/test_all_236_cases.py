#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全部236个案例深度测试
逐一访问每个案例，检查内容完整性和显示正确性
"""
import sys
import io
if sys.platform == 'win32' and hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import requests
import json
import time
from pathlib import Path
from datetime import datetime
from collections import defaultdict

BASE_URL = "http://localhost:8000"
BOOKS_DIR = Path(__file__).parent.parent.parent.parent / "books"

def print_header(text):
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80 + "\n")

def check_case_detail(case_id, case_title):
    """检查单个案例的详细信息"""
    result = {
        "case_id": case_id,
        "title": case_title,
        "checks": {}
    }
    
    try:
        # 1. 获取案例详情
        response = requests.get(f"{BASE_URL}/api/cases/{case_id}", timeout=5)
        if response.status_code != 200:
            result["checks"]["api_access"] = {"status": "fail", "reason": f"HTTP {response.status_code}"}
            return result
        
        case_data = response.json()
        result["checks"]["api_access"] = {"status": "pass"}
        
        # 2. 检查README
        readme = case_data.get('readme', '')
        if readme:
            result["checks"]["readme"] = {
                "status": "pass",
                "length": len(readme),
                "has_title": "# " in readme or "## " in readme,
                "has_code": "```" in readme,
                "has_image": "![" in readme or "<img" in readme
            }
        else:
            result["checks"]["readme"] = {"status": "fail", "reason": "README为空"}
        
        # 3. 检查文件列表
        files_response = requests.get(f"{BASE_URL}/api/files/{case_id}", timeout=5)
        if files_response.status_code == 200:
            files = files_response.json()
            result["checks"]["files"] = {
                "status": "pass",
                "count": len(files) if isinstance(files, list) else 0,
                "has_main": any(f.get('name') == 'main.py' for f in files) if isinstance(files, list) else False
            }
        
        # 4. 检查图片（从README中提取）
        image_count = readme.count('![') + readme.count('<img')
        result["checks"]["images"] = {
            "status": "pass" if image_count > 0 else "warn",
            "count": image_count
        }
        
        # 5. 检查表格
        table_count = readme.count('|')
        result["checks"]["tables"] = {
            "status": "pass" if table_count > 0 else "warn",
            "count": table_count // 3  # 粗略估计
        }
        
        return result
        
    except requests.Timeout:
        result["checks"]["api_access"] = {"status": "fail", "reason": "请求超时"}
        return result
    except Exception as e:
        result["checks"]["api_access"] = {"status": "fail", "reason": str(e)[:100]}
        return result

def analyze_results(results):
    """分析测试结果"""
    stats = {
        "total": len(results),
        "api_pass": 0,
        "readme_pass": 0,
        "files_pass": 0,
        "has_images": 0,
        "has_tables": 0,
        "issues": []
    }
    
    for result in results:
        checks = result.get("checks", {})
        
        if checks.get("api_access", {}).get("status") == "pass":
            stats["api_pass"] += 1
        else:
            stats["issues"].append({
                "case": result["title"],
                "type": "api_access",
                "detail": checks.get("api_access", {})
            })
        
        if checks.get("readme", {}).get("status") == "pass":
            stats["readme_pass"] += 1
            if checks["readme"].get("length", 0) < 500:
                stats["issues"].append({
                    "case": result["title"],
                    "type": "short_readme",
                    "detail": f"README过短: {checks['readme'].get('length')}字符"
                })
        else:
            stats["issues"].append({
                "case": result["title"],
                "type": "readme",
                "detail": checks.get("readme", {})
            })
        
        if checks.get("files", {}).get("status") == "pass":
            stats["files_pass"] += 1
        
        if checks.get("images", {}).get("count", 0) > 0:
            stats["has_images"] += 1
        
        if checks.get("tables", {}).get("count", 0) > 0:
            stats["has_tables"] += 1
    
    return stats

def main():
    print_header("🧪 全部236个案例深度测试")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"测试服务器: {BASE_URL}")
    
    # 获取所有案例
    print_header("📋 第1步：获取案例列表")
    try:
        response = requests.get(f"{BASE_URL}/api/cases", timeout=10)
        cases = response.json()
        print(f"✅ 成功获取 {len(cases)} 个案例")
    except Exception as e:
        print(f"❌ 获取案例列表失败: {e}")
        return
    
    # 测试所有案例
    print_header("🔍 第2步：逐一测试案例（共236个）")
    print("这将需要几分钟时间...\n")
    
    results = []
    failed_count = 0
    
    for i, case in enumerate(cases, 1):
        case_id = case.get('id', 'unknown')
        title = case.get('title', case.get('name', 'Unknown'))
        
        # 显示进度
        progress = i / len(cases) * 100
        status_icon = "✅" if i % 10 == 0 else "⏳"
        print(f"{status_icon} [{i}/{len(cases)}] ({progress:.1f}%) 测试: {title[:60]}", end='\r')
        
        result = check_case_detail(case_id, title)
        results.append(result)
        
        # 检查是否失败
        if result["checks"].get("api_access", {}).get("status") != "pass":
            failed_count += 1
        
        # 避免请求过快
        time.sleep(0.1)
    
    print("\n")  # 换行
    
    # 分析结果
    print_header("📊 第3步：结果分析")
    stats = analyze_results(results)
    
    print(f"总测试案例: {stats['total']}")
    print(f"API访问成功: {stats['api_pass']}/{stats['total']} ({stats['api_pass']/stats['total']*100:.1f}%)")
    print(f"README完整: {stats['readme_pass']}/{stats['total']} ({stats['readme_pass']/stats['total']*100:.1f}%)")
    print(f"文件列表可用: {stats['files_pass']}/{stats['total']} ({stats['files_pass']/stats['total']*100:.1f}%)")
    print(f"包含图片: {stats['has_images']}/{stats['total']} ({stats['has_images']/stats['total']*100:.1f}%)")
    print(f"包含表格: {stats['has_tables']}/{stats['total']} ({stats['has_tables']/stats['total']*100:.1f}%)")
    
    # 问题汇总
    if stats['issues']:
        print_header(f"⚠️ 发现 {len(stats['issues'])} 个问题")
        
        # 按类型分组
        issues_by_type = defaultdict(list)
        for issue in stats['issues']:
            issues_by_type[issue['type']].append(issue)
        
        for issue_type, issues in issues_by_type.items():
            print(f"\n[{issue_type}] {len(issues)} 个问题:")
            for issue in issues[:5]:  # 只显示前5个
                print(f"  - {issue['case'][:50]}")
            if len(issues) > 5:
                print(f"  ... 还有 {len(issues)-5} 个")
    
    # 质量评估
    print_header("✅ 质量评估")
    
    api_rate = stats['api_pass'] / stats['total'] * 100
    readme_rate = stats['readme_pass'] / stats['total'] * 100
    image_rate = stats['has_images'] / stats['total'] * 100
    
    overall_score = (api_rate + readme_rate + image_rate) / 3
    
    print(f"API可用性: {api_rate:.1f}%")
    print(f"内容完整性: {readme_rate:.1f}%")
    print(f"图文丰富度: {image_rate:.1f}%")
    print(f"\n综合得分: {overall_score:.1f}/100")
    
    if overall_score >= 90:
        print("评级: ⭐⭐⭐⭐⭐ 优秀")
    elif overall_score >= 80:
        print("评级: ⭐⭐⭐⭐ 良好")
    elif overall_score >= 70:
        print("评级: ⭐⭐⭐ 中等")
    else:
        print("评级: ⭐⭐ 需改进")
    
    print_header("✅ 测试完成")
    
    # 保存详细报告
    report = {
        "test_time": datetime.now().isoformat(),
        "total_cases": stats['total'],
        "statistics": stats,
        "results": results
    }
    
    report_file = Path(__file__).parent.parent / "all_236_cases_test_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"📄 详细报告已保存: {report_file}")
    
    return stats

if __name__ == "__main__":
    try:
        stats = main()
        
        # 退出码：如果有超过10%的案例失败，返回1
        if stats and stats['api_pass'] / stats['total'] < 0.9:
            sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️ 测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 测试过程发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

