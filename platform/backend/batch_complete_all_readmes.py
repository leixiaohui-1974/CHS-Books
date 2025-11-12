#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量完善所有案例的README.md
自动添加示意图和结果图的表格格式
"""

import sys
import io
from pathlib import Path
import re

# 设置标准输出为UTF-8编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 定义根目录
ROOT_DIR = Path(__file__).parent.parent.parent
CASES_DIR = ROOT_DIR / "books" / "water-system-control" / "code" / "examples"

# 示意图表格模板
DIAGRAM_TEMPLATE = """### 图1：{title}示意图

<table>
<tr>
<td width="50%"><img src="{filename}" alt="{alt}" width="100%"/></td>
<td width="50%">

**系统架构说明：**

这张示意图展示了{description}的完整系统架构：

**主要组成部分：**

1. **[组件1]**：[说明]
2. **[组件2]**：[说明]
3. **[组件3]**：[说明]
4. **[组件4]**：[说明]

**控制逻辑：**
- [逻辑1]
- [逻辑2]
- [逻辑3]

**系统特点：**
{features}

</td>
</tr>
</table>

"""

# 结果图表格模板
RESULT_TEMPLATE = """### 图{num}：{title}

<table>
<tr>
<td width="50%"><img src="{filename}" alt="{alt}" width="100%"/></td>
<td width="50%">

**图表说明：**

这张图展示了{description}，包含{subplots}个子图：

**{subplot1_title}：**
- **[元素1]**：[说明]
- **[元素2]**：[说明]
- [更多说明...]

**关键观察点：**
- [观察点1]
- [观察点2]
- [观察点3]

**结论：**
{conclusion}

</td>
</tr>
</table>

"""

def find_diagram_file(case_dir):
    """查找示意图文件"""
    patterns = ['*diagram*.png', '*schematic*.png', '*structure*.png', '*system*.png']
    for pattern in patterns:
        files = list(case_dir.glob(pattern))
        if files:
            return files[0].name
    return None

def find_result_files(case_dir):
    """查找所有结果图文件"""
    all_pngs = list(case_dir.glob("*.png"))
    diagram_file = find_diagram_file(case_dir)
    
    result_files = []
    for png in all_pngs:
        # 排除示意图
        if diagram_file and png.name == diagram_file:
            continue
        # 排除包含diagram/schematic/structure的文件
        if any(keyword in png.name.lower() for keyword in ['diagram', 'schematic', 'structure']):
            continue
        result_files.append(png.name)
    
    return sorted(result_files)

def has_diagram_section(readme_content):
    """检查README是否已有示意图部分"""
    return '示意图' in readme_content or 'diagram' in readme_content.lower()

def has_result_images(readme_content):
    """检查README是否已有结果图"""
    return '<img src=' in readme_content or '![' in readme_content

def add_diagram_to_readme(case_dir, readme_file):
    """为README添加示意图部分"""
    
    if not readme_file.exists():
        print(f"  ✗ README.md不存在")
        return False
    
    # 读取README
    content = readme_file.read_text(encoding='utf-8')
    
    # 检查是否已有示意图
    if has_diagram_section(content):
        print(f"  ✓ 示意图部分已存在")
        return True
    
    # 查找示意图文件
    diagram_file = find_diagram_file(case_dir)
    if not diagram_file:
        print(f"  ⚠ 未找到示意图文件")
        return False
    
    # 查找插入位置（"案例背景"或"问题描述"部分之后）
    insert_pattern = r'(##\s*📖\s*案例背景\s*\n)'
    match = re.search(insert_pattern, content)
    
    if not match:
        print(f"  ⚠ 未找到插入位置")
        return False
    
    # 准备插入的内容（简化版，需要手动完善）
    case_name = case_dir.name.replace('case_', '案例').replace('_', ' ')
    diagram_section = f"""
### 图1：系统示意图

<table>
<tr>
<td width="50%"><img src="{diagram_file}" alt="系统示意图" width="100%"/></td>
<td width="50%">

**系统架构说明：**

待完善...

**主要组成部分：**

1. **组件1**：说明
2. **组件2**：说明
3. **组件3**：说明

**控制逻辑：**
- 待完善...

**系统特点：**
待完善...

</td>
</tr>
</table>

"""
    
    # 插入内容
    insert_pos = match.end()
    new_content = content[:insert_pos] + diagram_section + content[insert_pos:]
    
    # 写回文件
    readme_file.write_text(new_content, encoding='utf-8')
    print(f"  ✓ 已添加示意图部分（需手动完善说明）")
    return True

def check_case_completeness(case_dir):
    """检查单个案例的完整性"""
    case_name = case_dir.name
    readme_file = case_dir / "README.md"
    
    # 检查文件
    has_readme = readme_file.exists()
    has_diagram_script = (case_dir / "generate_diagram.py").exists()
    
    # 检查图片
    diagram_file = find_diagram_file(case_dir)
    result_files = find_result_files(case_dir)
    
    # 检查README内容
    readme_has_diagram = False
    readme_has_results = False
    if has_readme:
        content = readme_file.read_text(encoding='utf-8')
        readme_has_diagram = has_diagram_section(content)
        readme_has_results = has_result_images(content)
    
    return {
        "case": case_name,
        "has_readme": has_readme,
        "has_diagram_script": has_diagram_script,
        "diagram_file": diagram_file,
        "result_files": result_files,
        "readme_has_diagram": readme_has_diagram,
        "readme_has_results": readme_has_results,
        "is_complete": (
            has_readme and
            diagram_file is not None and
            readme_has_diagram and
            (len(result_files) == 0 or readme_has_results)
        )
    }

def main():
    """主函数"""
    print("="*80)
    print("批量完善所有案例的README.md")
    print("="*80)
    
    # 扫描所有案例
    results = []
    for case_dir in sorted(CASES_DIR.glob("case_*")):
        if not case_dir.is_dir():
            continue
        
        print(f"\n检查 {case_dir.name}:")
        result = check_case_completeness(case_dir)
        results.append(result)
        
        # 显示状态
        status_icon = "✓" if result["is_complete"] else "⚠"
        print(f"{status_icon} README: {'存在' if result['has_readme'] else '缺失'}")
        print(f"{status_icon} 示意图: {result['diagram_file'] if result['diagram_file'] else '缺失'}")
        print(f"{status_icon} 结果图: {len(result['result_files'])}张")
        print(f"{status_icon} README已嵌入示意图: {'是' if result['readme_has_diagram'] else '否'}")
        print(f"{status_icon} README已嵌入结果图: {'是' if result['readme_has_results'] else '否'}")
    
    # 统计
    print("\n" + "="*80)
    print("完整性统计")
    print("="*80)
    
    complete_count = sum(1 for r in results if r["is_complete"])
    has_diagram_count = sum(1 for r in results if r["diagram_file"])
    has_readme_count = sum(1 for r in results if r["has_readme"])
    
    print(f"\n总案例数: {len(results)}")
    print(f"  完全完成: {complete_count}/{len(results)} ({complete_count*100//len(results)}%)")
    print(f"  有README: {has_readme_count}/{len(results)}")
    print(f"  有示意图: {has_diagram_count}/{len(results)}")
    
    # 列出未完成的案例
    incomplete = [r for r in results if not r["is_complete"]]
    if incomplete:
        print(f"\n未完成的案例({len(incomplete)}个):")
        for r in incomplete:
            issues = []
            if not r["readme_has_diagram"]:
                issues.append("缺示意图嵌入")
            if not r["readme_has_results"] and len(r["result_files"]) > 0:
                issues.append("缺结果图嵌入")
            if not r["diagram_file"]:
                issues.append("缺示意图文件")
            print(f"  - {r['case']}: {', '.join(issues)}")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    main()

