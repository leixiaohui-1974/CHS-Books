# -*- coding: utf-8 -*-
"""
检查并修复所有README中的表格格式
"""
import sys
import io
import re
from pathlib import Path

# 设置UTF-8编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 路径配置
BASE_DIR = Path(__file__).resolve().parent.parent.parent
EXAMPLES_DIR = BASE_DIR / "books" / "water-system-control" / "code" / "examples"

def check_table_format(content, readme_path):
    """检查README中的表格格式"""
    issues = []
    
    # 查找所有表格
    table_pattern = r'<table>.*?</table>'
    tables = re.findall(table_pattern, content, re.DOTALL)
    
    if not tables:
        return []
    
    for i, table in enumerate(tables, 1):
        # 检查是否有<tr>标签
        if '<tr>' not in table:
            issues.append(f"表格{i}: 缺少<tr>标签")
        
        # 检查是否有<td>标签
        if '<td>' not in table:
            issues.append(f"表格{i}: 缺少<td>标签")
        
        # 检查<td>是否有width属性
        td_tags = re.findall(r'<td[^>]*>', table)
        for j, td in enumerate(td_tags, 1):
            if 'width=' not in td and 'width =' not in td:
                issues.append(f"表格{i} 单元格{j}: 建议添加width属性")
        
        # 检查图片标签
        img_tags = re.findall(r'<img[^>]*>', table)
        for j, img in enumerate(img_tags, 1):
            if 'width=' not in img and 'width =' not in img:
                issues.append(f"表格{i} 图片{j}: 建议添加width属性")
    
    return issues

def fix_table_format(content):
    """修复表格格式"""
    # 确保表格有正确的结构
    # 这里主要是检查，不做自动修复，避免破坏内容
    return content

def main():
    print("="*80)
    print("  🔍 检查所有README表格格式")
    print("="*80)
    print()
    
    total_cases = 0
    total_tables = 0
    cases_with_issues = []
    
    # 遍历所有案例
    for case_dir in sorted(EXAMPLES_DIR.glob("case_*")):
        if not case_dir.is_dir():
            continue
        
        total_cases += 1
        case_name = case_dir.name
        case_num = case_name.split('_')[1]
        
        readme_path = case_dir / "README.md"
        if not readme_path.exists():
            print(f"案例{case_num}: ⚠️  README.md不存在")
            continue
        
        # 读取README内容
        try:
            content = readme_path.read_text(encoding='utf-8')
        except Exception as e:
            print(f"案例{case_num}: ❌ 读取失败 - {e}")
            continue
        
        # 检查表格
        issues = check_table_format(content, readme_path)
        
        # 统计表格数量
        table_count = content.count('<table>')
        total_tables += table_count
        
        if issues:
            print(f"案例{case_num}: ⚠️  发现{len(issues)}个问题 (共{table_count}个表格)")
            for issue in issues[:3]:  # 只显示前3个问题
                print(f"  - {issue}")
            if len(issues) > 3:
                print(f"  ... 还有{len(issues)-3}个问题")
            cases_with_issues.append((case_name, issues, table_count))
        else:
            if table_count > 0:
                print(f"案例{case_num}: ✅ 表格格式正确 ({table_count}个表格)")
            else:
                print(f"案例{case_num}: ℹ️  无表格")
    
    # 总结报告
    print()
    print("="*80)
    print("  📊 检查总结")
    print("="*80)
    print(f"总案例数: {total_cases}")
    print(f"总表格数: {total_tables}")
    print(f"有问题的案例: {len(cases_with_issues)}")
    
    if cases_with_issues:
        print()
        print("="*80)
        print("  🔧 需要检查的案例")
        print("="*80)
        for case_name, issues, table_count in cases_with_issues:
            print(f"\n{case_name} ({table_count}个表格):")
            for issue in issues:
                print(f"  {issue}")
    else:
        print()
        print("🎉 所有表格格式完美！")
    
    # 提供修复建议
    print()
    print("="*80)
    print("  💡 表格最佳实践")
    print("="*80)
    print("""
标准表格格式：

<table>
<tr>
<td width="50%"><img src="image.png" alt="说明" width="100%"/></td>
<td width="50%">

**说明文字：**

内容...

</td>
</tr>
</table>

关键点：
1. <td> 必须有 width="50%" 属性（确保1行2列布局）
2. <img> 必须有 width="100%" 属性（自适应单元格）
3. 右侧单元格内容前后要有空行（Markdown解析需要）
4. 图片src使用相对路径（如 image.png）
    """)
    print("="*80)

if __name__ == '__main__':
    main()



