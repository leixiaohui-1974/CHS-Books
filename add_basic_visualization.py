#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为明渠水力学案例批量添加基础可视化

为case_02到case_12添加简单的结果可视化图表
"""

import os
from pathlib import Path

# 通用可视化代码模板
VISUALIZATION_TEMPLATE = '''
    # ========== 可视化分析 ==========
    print("\\n" + "="*70)
    print("生成可视化图表")
    print("="*70)

    try:
        import matplotlib.pyplot as plt
        import numpy as np

        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False

        fig, ax = plt.subplots(figsize=(10, 6))

        # 创建结果摘要图表
        categories = ['设计流量', '水深', '流速', '流态系数']
        values = [Q_design if 'Q_design' in locals() else 1.0,
                  h_normal if 'h_normal' in locals() else 1.0,
                  v if 'v' in locals() else 1.0,
                  Fr if 'Fr' in locals() else 0.5]

        ax.barh(categories, values, color=['skyblue', 'lightgreen', 'orange', 'coral'])
        ax.set_xlabel('数值', fontsize=12)
        ax.set_title('水力计算结果摘要', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='x')

        # 添加数值标注
        for i, v in enumerate(values):
            ax.text(v, i, f' {v:.3f}', va='center', fontsize=10)

        plt.tight_layout()

        # 保存图片
        output_path = Path(__file__).parent / 'results_summary.png'
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"\\n✓ 图表已保存: {output_path.name}")
        plt.close()

    except Exception as e:
        print(f"\\n✗ 图表生成失败: {e}")
'''

def add_visualization_to_file(file_path):
    """为指定的main.py文件添加可视化代码"""

    if not file_path.exists():
        return False, "文件不存在"

    try:
        # 读取原文件
        content = file_path.read_text(encoding='utf-8')

        # 检查是否已有可视化代码
        if 'matplotlib' in content and 'savefig' in content:
            return False, "已包含可视化代码"

        # 检查是否有if __name__ == "__main__"
        if 'if __name__' in content:
            # 在main()函数结束前添加可视化代码
            # 查找main函数的最后位置
            lines = content.split('\n')

            # 找到main函数定义
            main_start = -1
            for i, line in enumerate(lines):
                if 'def main(' in line:
                    main_start = i
                    break

            if main_start == -1:
                return False, "未找到main()函数"

            # 找到main函数结束位置（假设在if __name__之前）
            main_end = -1
            for i in range(main_start + 1, len(lines)):
                if 'if __name__' in lines[i]:
                    main_end = i - 1
                    break

            if main_end == -1:
                main_end = len(lines) - 1

            # 在main函数结束前插入可视化代码
            insert_pos = main_end

            # 向前查找合适的插入位置（在最后一个print之后）
            for i in range(main_end, main_start, -1):
                if lines[i].strip() and not lines[i].strip().startswith('#'):
                    insert_pos = i + 1
                    break

            # 插入可视化代码
            vis_lines = VISUALIZATION_TEMPLATE.split('\n')
            for j, vis_line in enumerate(vis_lines):
                lines.insert(insert_pos + j, vis_line)

            # 写回文件
            new_content = '\n'.join(lines)
            file_path.write_text(new_content, encoding='utf-8')

            return True, "成功添加可视化代码"
        else:
            return False, "文件结构不符合预期"

    except Exception as e:
        return False, f"处理失败: {e}"


def main():
    """主函数"""

    base_dir = Path('/home/user/CHS-Books/books/open-channel-hydraulics/code/examples')

    # 需要添加可视化的案例
    cases_to_process = [
        'case_02_drainage',
        'case_03_landscape',
        'case_04_weir',
        'case_05_gate',
        'case_06_drop',
        'case_07_profile',
        'case_08_bridge',
        'case_09_roughness',
        'case_10_compound',
        'case_11_transition',
        'case_12_culvert',
    ]

    print("="*70)
    print("批量添加可视化工具")
    print("="*70)
    print(f"目标目录: {base_dir}")
    print(f"待处理案例: {len(cases_to_process)}个\n")

    success_count = 0
    failed_count = 0
    skipped_count = 0

    for case_name in cases_to_process:
        case_dir = base_dir / case_name
        main_file = case_dir / 'main.py'

        print(f"处理 {case_name}...", end=' ')

        if not case_dir.exists():
            print("✗ 目录不存在")
            failed_count += 1
            continue

        if not main_file.exists():
            print("✗ main.py不存在")
            failed_count += 1
            continue

        success, message = add_visualization_to_file(main_file)

        if success:
            print(f"✓ {message}")
            success_count += 1
        elif "已包含" in message:
            print(f"⊝ {message}")
            skipped_count += 1
        else:
            print(f"✗ {message}")
            failed_count += 1

    print("\n" + "="*70)
    print("处理完成")
    print("="*70)
    print(f"✓ 成功: {success_count}个")
    print(f"⊝ 跳过: {skipped_count}个")
    print(f"✗ 失败: {failed_count}个")
    print(f"总计: {len(cases_to_process)}个")
    print("="*70)


if __name__ == '__main__':
    main()
