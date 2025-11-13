#!/usr/bin/env python3
"""
为案例添加问题描述示意图
1. 运行Python脚本生成图片
2. 更新README，在开头添加示意图section
3. 验证图片质量
"""

import os
import re
import subprocess
from pathlib import Path
import time

def find_main_script(case_dir):
    """查找案例的main.py或generate_diagram.py脚本"""
    main_py = case_dir / 'main.py'
    gen_diagram_py = case_dir / 'generate_diagram.py'

    if gen_diagram_py.exists():
        return gen_diagram_py
    elif main_py.exists():
        return main_py
    return None

def run_script_and_generate_images(case_dir, script_path):
    """运行脚本生成图片"""
    print(f"    🔧 运行脚本: {script_path.name}")

    try:
        # 运行脚本
        result = subprocess.run(
            ['python3', script_path.name],
            cwd=case_dir,
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0:
            # 查找生成的PNG文件
            png_files = list(case_dir.glob('*.png'))
            if png_files:
                print(f"    ✅ 成功生成 {len(png_files)} 个图片")
                return True, png_files
            else:
                print(f"    ⚠️  脚本运行成功但未生成PNG文件")
                return False, []
        else:
            error_msg = result.stderr[:200] if result.stderr else "Unknown error"
            print(f"    ❌ 脚本运行失败: {error_msg}")
            return False, []

    except subprocess.TimeoutExpired:
        print(f"    ❌ 脚本运行超时")
        return False, []
    except Exception as e:
        print(f"    ❌ 异常: {str(e)}")
        return False, []

def find_primary_diagram(case_dir, png_files):
    """找到主要的示意图（优先选择包含summary/diagram/system等关键词的）"""
    # 优先级关键词
    priority_keywords = ['summary', 'diagram', 'system', 'overview', 'architecture']

    # 按优先级排序
    for keyword in priority_keywords:
        for png in png_files:
            if keyword in png.name.lower():
                return png

    # 如果没有找到，返回第一个
    return png_files[0] if png_files else None

def add_diagram_section_to_readme(readme_path, diagram_filename, case_name):
    """在README开头添加示意图section"""

    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查是否已经有示意图section
        if '## 系统示意图' in content or '## 问题示意图' in content:
            print(f"    ⚠️  README已包含示意图section，跳过")
            return False

        # 提取标题
        title_match = re.search(r'^#\s+(.+?)(?:\n|$)', content, re.MULTILINE)
        if not title_match:
            print(f"    ❌ 无法找到标题")
            return False

        title = title_match.group(0)
        rest_content = content[title_match.end():]

        # 创建示意图section
        diagram_section = f"""
## 系统示意图

### 图1：问题描述与系统架构

<table>
<tr>
<td width="50%"><img src="{diagram_filename}" alt="系统示意图" width="100%"/></td>
<td width="50%">

**系统架构说明：**

这张图展示了本案例的核心问题和系统架构：

**核心要素：**
1. **控制对象**：水箱系统及其动态特性
2. **控制目标**：精确的水位控制和性能优化
3. **控制策略**：本案例采用的具体控制方法
4. **系统特性**：关键参数和性能指标

**应用价值：**
- 理解控制系统的基本原理
- 掌握实际工程问题的建模方法
- 学习控制器设计和参数调优
- 分析系统性能和鲁棒性

**学习重点：**
通过本案例，您将深入理解控制理论在实际系统中的应用。

</td>
</tr>
</table>

"""

        # 组合新内容
        new_content = title + diagram_section + rest_content

        # 写回文件
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        print(f"    ✅ 已添加示意图section到README开头")
        return True

    except Exception as e:
        print(f"    ❌ 更新README失败: {str(e)}")
        return False

def verify_image_quality(image_path):
    """验证图片质量（基本检查：文件大小、存在性）"""
    try:
        if not image_path.exists():
            return False, "图片文件不存在"

        file_size = image_path.stat().st_size

        # 检查文件大小（至少10KB）
        if file_size < 10 * 1024:
            return False, f"图片文件太小 ({file_size} bytes)"

        # 检查文件大小（不超过5MB）
        if file_size > 5 * 1024 * 1024:
            return False, f"图片文件太大 ({file_size} bytes)"

        return True, f"图片质量OK ({file_size // 1024}KB)"

    except Exception as e:
        return False, f"验证失败: {str(e)}"

def process_single_case(case_dir):
    """处理单个案例"""
    case_name = case_dir.name
    readme_path = case_dir / 'README.md'

    print(f"\n  📝 处理案例: {case_name}")

    if not readme_path.exists():
        print(f"    ❌ README.md不存在")
        return False

    # 1. 查找脚本
    script_path = find_main_script(case_dir)
    if not script_path:
        print(f"    ⚠️  未找到main.py或generate_diagram.py")
        return False

    # 2. 运行脚本生成图片
    success, png_files = run_script_and_generate_images(case_dir, script_path)

    if not success or not png_files:
        print(f"    ⚠️  跳过（无法生成图片）")
        return False

    # 3. 选择主要示意图
    primary_diagram = find_primary_diagram(case_dir, png_files)
    if not primary_diagram:
        print(f"    ❌ 未找到主要示意图")
        return False

    print(f"    📊 选择主图: {primary_diagram.name}")

    # 4. 验证图片质量
    is_valid, msg = verify_image_quality(primary_diagram)
    print(f"    🔍 质量检查: {msg}")

    if not is_valid:
        print(f"    ❌ 图片质量不合格")
        return False

    # 5. 更新README
    success = add_diagram_section_to_readme(readme_path, primary_diagram.name, case_name)

    return success

def main():
    """主函数"""
    print("="*80)
    print("🎯 为 water-system-control 案例添加问题描述示意图")
    print("="*80)

    # 定位water-system-control案例目录
    book_dir = Path('books/water-system-control/code/examples')

    if not book_dir.exists():
        print(f"❌ 目录不存在: {book_dir}")
        return 1

    # 获取所有案例目录（排除已经有示意图的case_01）
    case_dirs = sorted([d for d in book_dir.iterdir()
                       if d.is_dir() and d.name.startswith('case_')])

    print(f"\n找到 {len(case_dirs)} 个案例目录")

    success_count = 0
    failed_count = 0

    for case_dir in case_dirs:
        try:
            if process_single_case(case_dir):
                success_count += 1
            else:
                failed_count += 1
        except Exception as e:
            print(f"  ❌ 处理异常: {str(e)}")
            failed_count += 1

        # 短暂延迟，避免过快
        time.sleep(0.5)

    # 总结
    print("\n" + "="*80)
    print("📊 处理完成")
    print("="*80)
    print(f"✅ 成功: {success_count} 个案例")
    print(f"❌ 失败: {failed_count} 个案例")
    print(f"📈 成功率: {success_count / len(case_dirs) * 100:.1f}%")
    print("="*80)

    return 0 if success_count > 0 else 1

if __name__ == "__main__":
    exit(main())
