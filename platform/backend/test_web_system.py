#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web系统全面检测脚本
检测所有优化是否已成功实现
"""

import requests
import time
from pathlib import Path

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def print_section(title):
    """打印分节标题"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")

def check_server():
    """检查服务器是否运行"""
    print_section("1. 检查服务器状态")
    try:
        response = requests.get(BASE_URL, timeout=5)
        if response.status_code == 200:
            print("[OK] 服务器正常运行")
            print(f"     状态码: {response.status_code}")
            return True
        else:
            print(f"[ERROR] 服务器响应异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] 无法连接到服务器: {e}")
        print("     请确保后端服务器正在运行 (python full_server.py)")
        return False

def check_cases_list():
    """检查案例列表API"""
    print_section("2. 检查案例列表API")
    try:
        response = requests.get(f"{API_BASE}/books/water-system-control/cases", timeout=5)
        if response.status_code == 200:
            cases = response.json()
            print(f"[OK] 成功获取案例列表")
            print(f"     案例数量: {len(cases)}")
            print(f"     案例ID: {[c['id'] for c in cases[:5]]}...")
            return cases
        else:
            print(f"[ERROR] 获取案例列表失败: {response.status_code}")
            return []
    except Exception as e:
        print(f"[ERROR] API请求失败: {e}")
        return []

def check_case_details(case_id):
    """检查单个案例的详细信息"""
    try:
        response = requests.get(
            f"{API_BASE}/books/water-system-control/cases/{case_id}",
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            return {
                'success': True,
                'has_readme': len(data.get('readme', '')) > 0,
                'readme_length': len(data.get('readme', '')),
                'has_code': len(data.get('code', '')) > 0,
            }
        else:
            return {'success': False, 'error': f"HTTP {response.status_code}"}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def check_case_images(case_id):
    """检查案例的图片"""
    # 常见的图片文件名
    common_images = [
        f"{case_id}_diagram.png",
        "water_tower_diagram.png",
        "cooling_tower_diagram.png",
        "water_supply_station_diagram.png",
        "pid_system_diagram.png",
        "parameter_identification_diagram.png",
        "step_response_diagram.png",
        "cascade_control_diagram.png",
        "feedforward_control_diagram.png",
        "system_modeling_diagram.png",
        "frequency_analysis_diagram.png",
        "state_space_diagram.png",
    ]
    
    found_images = []
    for img in common_images:
        try:
            response = requests.head(
                f"{API_BASE}/books/water-system-control/cases/{case_id}/images/{img}",
                timeout=2
            )
            if response.status_code == 200:
                found_images.append(img)
        except:
            pass
    
    return found_images

def check_all_cases():
    """检查所有案例（4-20）"""
    print_section("3. 检查案例4-20的详细信息")
    
    results = {}
    # 使用完整的案例ID（包含名称）
    case_ids = [
        "case_04_pid_tuning",
        "case_05_parameter_identification",
        "case_06_step_response",
        "case_07_cascade_control",
        "case_08_feedforward_control",
        "case_09_system_modeling",
        "case_10_frequency_analysis",
        "case_11_state_space",
        "case_12_observer_lqr",
        "case_13_adaptive_control",
        "case_14_model_predictive_control",
        "case_15_sliding_mode_control",
        "case_16_fuzzy_control",
        "case_17_neural_network_control",
        "case_18_reinforcement_learning_control",
        "case_19_comprehensive_comparison",
        "case_20_practical_application",
    ]
    
    for case_id in case_ids:
        print(f"\n检查 {case_id}...")
        
        # 检查案例详情
        details = check_case_details(case_id)
        
        if details['success']:
            print(f"  [OK] 案例数据加载成功")
            print(f"       README长度: {details['readme_length']} 字符")
            print(f"       包含代码: {'是' if details['has_code'] else '否'}")
            
            # 检查图片
            images = check_case_images(case_id)
            if images:
                print(f"       找到示意图: {images[0]}")
            else:
                print(f"       示意图: 未找到或不适用")
        else:
            print(f"  [ERROR] 加载失败: {details.get('error', 'Unknown')}")
        
        results[case_id] = details
    
    return results

def check_readme_formatting():
    """检查README格式是否紧凑"""
    print_section("4. 检查README排版紧凑度")
    
    ROOT_DIR = Path(__file__).parent.parent.parent
    EXAMPLES_DIR = ROOT_DIR / "books" / "water-system-control" / "code" / "examples"
    
    issues = []
    for i in range(4, 21):
        case_dir = list(EXAMPLES_DIR.glob(f"case_{i:02d}_*"))
        if case_dir:
            readme_file = case_dir[0] / "README.md"
            if readme_file.exists():
                with open(readme_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检查连续空行
                lines = content.split('\n')
                consecutive_blanks = 0
                max_consecutive = 0
                
                for line in lines:
                    if line.strip() == '':
                        consecutive_blanks += 1
                        max_consecutive = max(max_consecutive, consecutive_blanks)
                    else:
                        consecutive_blanks = 0
                
                case_name = case_dir[0].name
                if max_consecutive > 1:
                    issues.append(f"{case_name}: 发现{max_consecutive}个连续空行")
                    print(f"  [WARN] {case_name}: 有{max_consecutive}个连续空行")
                else:
                    print(f"  [OK] {case_name}: 排版紧凑")
    
    if not issues:
        print("\n[OK] 所有README排版紧凑，无多余空行")
    else:
        print(f"\n[WARN] 发现{len(issues)}个排版问题")
    
    return len(issues) == 0

def check_diagrams_updated():
    """检查示意图是否已更新"""
    print_section("5. 检查示意图更新时间")
    
    ROOT_DIR = Path(__file__).parent.parent.parent
    EXAMPLES_DIR = ROOT_DIR / "books" / "water-system-control" / "code" / "examples"
    
    recent_threshold = time.time() - 3600  # 最近1小时内
    
    updated_count = 0
    for i in range(4, 12):  # case_04 到 case_11
        case_dir = list(EXAMPLES_DIR.glob(f"case_{i:02d}_*"))
        if case_dir:
            diagram_files = list(case_dir[0].glob("*_diagram.png"))
            if diagram_files:
                diagram_file = diagram_files[0]
                mtime = diagram_file.stat().st_mtime
                
                if mtime > recent_threshold:
                    print(f"  [OK] {case_dir[0].name}: 示意图已更新 ({time.strftime('%H:%M:%S', time.localtime(mtime))})")
                    updated_count += 1
                else:
                    print(f"  [OLD] {case_dir[0].name}: 示意图较旧 ({time.strftime('%H:%M:%S', time.localtime(mtime))})")
            else:
                print(f"  [SKIP] {case_dir[0].name}: 未找到示意图文件")
    
    print(f"\n[INFO] {updated_count}/8 个示意图在最近1小时内更新")
    return updated_count

def check_frontend_files():
    """检查前端文件是否已优化"""
    print_section("6. 检查前端文件")
    
    ROOT_DIR = Path(__file__).parent.parent.parent
    frontend_file = ROOT_DIR / "platform" / "frontend" / "unified.html"
    
    if not frontend_file.exists():
        print("[ERROR] 前端文件不存在")
        return False
    
    with open(frontend_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查关键优化是否存在
    checks = {
        '图片路径修复': 'marked.parse(caseData.readme)' in content,
        '表格图片处理': 'querySelectorAll(\'td\')' in content,
        'README样式优化': '.readme-content' in content,
        '表格样式': '.readme-content table' in content,
        '代码块样式': '.readme-content code' in content,
        '加载动画': 'showLoading' in content,
        '友好错误提示': 'showFriendlyError' in content,
        '图片预览': 'showImagePreview' in content,
    }
    
    all_ok = True
    for name, exists in checks.items():
        if exists:
            print(f"  [OK] {name}: 已实现")
        else:
            print(f"  [ERROR] {name}: 未找到")
            all_ok = False
    
    return all_ok

def generate_report(server_ok, cases_results, readme_ok, diagrams_count, frontend_ok):
    """生成检测报告"""
    print_section("检测报告总结")
    
    print("\n[服务器状态]")
    print(f"  服务器运行: {'[OK] 正常' if server_ok else '[ERROR] 异常'}")
    
    print("\n[案例检测]")
    success_count = sum(1 for r in cases_results.values() if r.get('success'))
    print(f"  案例4-20加载: {success_count}/17 成功")
    
    print("\n[文档优化]")
    print(f"  README排版: {'[OK] 紧凑' if readme_ok else '[WARN] 有问题'}")
    
    print("\n[示意图优化]")
    print(f"  案例4-11示意图: {diagrams_count}/8 已更新")
    
    print("\n[前端优化]")
    print(f"  前端功能: {'[OK] 完整' if frontend_ok else '[WARN] 不完整'}")
    
    print("\n[整体评估]")
    total_score = (
        (1 if server_ok else 0) +
        (1 if success_count >= 15 else 0) +
        (1 if readme_ok else 0) +
        (1 if diagrams_count >= 6 else 0) +
        (1 if frontend_ok else 0)
    )
    
    print(f"  完成度: {total_score}/5")
    
    if total_score == 5:
        print("\n  [EXCELLENT] 所有优化均已成功实现！")
    elif total_score >= 3:
        print("\n  [GOOD] 大部分优化已实现，仍有少量问题需要解决")
    else:
        print("\n  [FAILED] 多项优化未成功，需要重新检查")
    
    print("\n" + "="*70)

def main():
    """主函数"""
    print("\n" + "="*70)
    print("  水系统控制平台 - Web系统全面检测")
    print("="*70)
    
    # 1. 检查服务器
    server_ok = check_server()
    if not server_ok:
        print("\n[ERROR] 服务器未运行，无法继续检测")
        return
    
    # 2. 检查案例列表
    cases = check_cases_list()
    
    # 3. 检查所有案例详情
    cases_results = check_all_cases()
    
    # 4. 检查README格式
    readme_ok = check_readme_formatting()
    
    # 5. 检查示意图更新
    diagrams_count = check_diagrams_updated()
    
    # 6. 检查前端文件
    frontend_ok = check_frontend_files()
    
    # 7. 生成报告
    generate_report(server_ok, cases_results, readme_ok, diagrams_count, frontend_ok)

if __name__ == '__main__':
    main()

