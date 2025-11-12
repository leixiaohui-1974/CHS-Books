# -*- coding: utf-8 -*-
"""
最终验证脚本 - 检查所有修复是否完成
"""
import sys
import io
from pathlib import Path

# 设置UTF-8编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 路径配置
BASE_DIR = Path(__file__).resolve().parent.parent.parent
EXAMPLES_DIR = BASE_DIR / "books" / "water-system-control" / "code" / "examples"

def check_files_exist(case_dir, case_name):
    """检查案例文件是否存在"""
    results = {
        'diagram': False,
        'diagram_script': False,
        'main': False,
        'readme': False,
        'result_images': []
    }
    
    # 检查generate_diagram.py
    diagram_script = case_dir / "generate_diagram.py"
    results['diagram_script'] = diagram_script.exists()
    
    # 检查示意图（可能有不同命名）
    diagram_patterns = ['*_diagram.png', '*_schematic.png', '*_system.png']
    for pattern in diagram_patterns:
        diagrams = list(case_dir.glob(pattern))
        if diagrams:
            results['diagram'] = True
            break
    
    # 检查main.py
    main_script = case_dir / "main.py"
    results['main'] = main_script.exists()
    
    # 检查README.md
    readme = case_dir / "README.md"
    results['readme'] = readme.exists()
    
    # 检查结果图（排除diagram）
    all_pngs = list(case_dir.glob("*.png"))
    for png in all_pngs:
        if 'diagram' not in png.name and 'schematic' not in png.name:
            results['result_images'].append(png.name)
    
    return results

def main():
    print("="*80)
    print("  🔍 最终验证报告")
    print("="*80)
    print()
    
    # 统计
    total_cases = 0
    has_diagram = 0
    has_main = 0
    has_readme = 0
    has_results = 0
    
    issues = []
    
    # 遍历所有案例
    for case_dir in sorted(EXAMPLES_DIR.glob("case_*")):
        if not case_dir.is_dir():
            continue
        
        total_cases += 1
        case_name = case_dir.name
        case_num = case_name.split('_')[1]
        
        results = check_files_exist(case_dir, case_name)
        
        # 状态图标
        diagram_icon = "✅" if results['diagram'] else "❌"
        main_icon = "✅" if results['main'] else "❌"
        readme_icon = "✅" if results['readme'] else "❌"
        result_icon = "✅" if len(results['result_images']) > 0 else "❌"
        
        # 统计
        if results['diagram']:
            has_diagram += 1
        if results['main']:
            has_main += 1
        if results['readme']:
            has_readme += 1
        if len(results['result_images']) > 0:
            has_results += 1
        
        # 打印案例状态
        print(f"案例{case_num}: {diagram_icon}示意图 {main_icon}脚本 {readme_icon}文档 {result_icon}结果图({len(results['result_images'])})")
        
        # 记录问题
        case_issues = []
        if not results['diagram'] and results['diagram_script']:
            case_issues.append("示意图缺失但脚本存在")
        if not results['main']:
            case_issues.append("缺少main.py")
        if not results['readme']:
            case_issues.append("缺少README.md")
        if len(results['result_images']) == 0 and results['main']:
            case_issues.append("结果图缺失但脚本存在")
        
        if case_issues:
            issues.append((case_name, case_issues))
    
    # 总结报告
    print()
    print("="*80)
    print("  📊 统计总结")
    print("="*80)
    print(f"总案例数: {total_cases}")
    print(f"有示意图: {has_diagram}/{total_cases} ({has_diagram*100//total_cases if total_cases>0 else 0}%)")
    print(f"有脚本:   {has_main}/{total_cases} ({has_main*100//total_cases if total_cases>0 else 0}%)")
    print(f"有文档:   {has_readme}/{total_cases} ({has_readme*100//total_cases if total_cases>0 else 0}%)")
    print(f"有结果图: {has_results}/{total_cases} ({has_results*100//total_cases if total_cases>0 else 0}%)")
    
    # 问题列表
    if issues:
        print()
        print("="*80)
        print("  ⚠️  需要关注的问题")
        print("="*80)
        for case_name, case_issues in issues:
            print(f"\n{case_name}:")
            for issue in case_issues:
                print(f"  - {issue}")
    else:
        print()
        print("🎉 所有案例文件完整！")
    
    # 修复建议
    print()
    print("="*80)
    print("  💡 下一步建议")
    print("="*80)
    print("1. 启动服务器: python platform/backend/full_server.py")
    print("2. 访问页面: http://localhost:8000")
    print("3. 强制刷新: Ctrl+F5 清除浏览器缓存")
    print("4. 检查显示: 查看示意图、结果图、表格、代码块")
    print("5. 测试主题: 切换深色/浅色主题验证效果")
    print()
    print("="*80)

if __name__ == '__main__':
    main()



