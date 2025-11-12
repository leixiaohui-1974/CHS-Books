#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量生成所有案例的示意图并完善README
这个脚本将自动化大部分重复性工作
"""

import sys
import io
from pathlib import Path
import json

# 设置标准输出为UTF-8编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 定义根目录
ROOT_DIR = Path(__file__).parent.parent.parent
CASES_DIR = ROOT_DIR / "books" / "water-system-control" / "code" / "examples"

# 案例信息（需要手动填写）
CASE_INFO = {
    "case_03_water_supply_station": {
        "name": "供水泵站无静差控制",
        "system_type": "PI Control Water Supply Station",
        "diagram_name": "supply_station_diagram.png",
        "main_components": [
            "高位水箱：储存水并维持压力",
            "PI控制器：消除稳态误差",
            "变频泵：连续调速",
            "压力传感器：实时监测水位",
            "供水管网：向用户供水"
        ],
        "control_logic": [
            "误差计算：e = h_setpoint - h(t)",
            "比例项：u_p = Kp × e（快速响应）",
            "积分项：u_i = Ki × ∫e dt（消除稳态误差）",
            "控制律：u = u_p + u_i",
            "抗饱和：防止积分饱和"
        ]
    },
    "case_04_pid_tuning": {
        "name": "PID控制与参数整定",
        "system_type": "PID Control Tuning",
        "diagram_name": "pid_tuning_diagram.png",
        "main_components": [
            "工业水箱：被控对象",
            "PID控制器：完整三项控制",
            "执行机构：精确控制",
            "传感器：高精度测量",
            "用户接口：参数整定"
        ],
        "control_logic": [
            "比例项P：快速响应误差",
            "积分项I：消除稳态误差",
            "微分项D：抑制超调和振荡",
            "参数整定：Ziegler-Nichols法",
            "自适应调整：实时优化"
        ]
    },
    # 其他案例信息可以逐步添加...
}

def create_readme_diagram_section(case_info):
    """创建README的示意图部分"""
    template = f"""
### 图1：{case_info['name']}系统示意图

<table>
<tr>
<td width="50%"><img src="{case_info['diagram_name']}" alt="示意图" width="100%"/></td>
<td width="50%">

**系统架构说明：**

这张示意图展示了{case_info['name']}的完整系统架构：

**主要组成部分：**

"""
    
    for i, comp in enumerate(case_info['main_components'], 1):
        template += f"{i}. **{comp.split('：')[0]}**：{comp.split('：')[1] if '：' in comp else comp}\n\n"
    
    template += "\n**控制逻辑：**\n"
    for logic in case_info['control_logic']:
        template += f"- {logic}\n"
    
    template += """
**系统特点：**
[根据具体案例补充]

</td>
</tr>
</table>
"""
    return template

def process_case(case_dir):
    """处理单个案例"""
    case_name = case_dir.name
    
    if case_name not in CASE_INFO:
        print(f"⊘ {case_name}: 缺少案例信息，跳过")
        return False
    
    print(f"\n{'='*80}")
    print(f"处理 {case_name}")
    print(f"{'='*80}")
    
    case_info = CASE_INFO[case_name]
    
    # 1. 检查README是否存在
    readme_file = case_dir / "README.md"
    if not readme_file.exists():
        print(f"  ✗ README.md 不存在")
        return False
    
    # 2. 读取README
    content = readme_file.read_text(encoding='utf-8')
    
    # 3. 检查是否已经有示意图部分
    if '### 图1：' in content or case_info['diagram_name'] in content:
        print(f"  ✓ 示意图已存在，跳过")
        return True
    
    # 4. 在"案例背景"后添加示意图
    if '## 📖 案例背景' in content:
        diagram_section = create_readme_diagram_section(case_info)
        content = content.replace(
            '## 📖 案例背景',
            f'## 📖 案例背景{diagram_section}'
        )
        
        # 保存修改
        readme_file.write_text(content, encoding='utf-8')
        print(f"  ✓ 已添加示意图部分到README")
        return True
    else:
        print(f"  ✗ 未找到'案例背景'标记")
        return False

def main():
    """主函数"""
    print("="*80)
    print("批量生成示意图并完善README")
    print("="*80)
    
    # 统计
    total = 0
    success = 0
    skipped = 0
    
    # 处理案例3-20
    for i in range(3, 21):
        case_name = f"case_{i:02d}_*"
        cases = list(CASES_DIR.glob(case_name))
        
        if not cases:
            continue
        
        case_dir = cases[0]
        total += 1
        
        if case_dir.name in CASE_INFO:
            if process_case(case_dir):
                success += 1
        else:
            skipped += 1
            print(f"⊘ {case_dir.name}: 待添加案例信息")
    
    # 总结
    print("\n" + "="*80)
    print("处理完成！")
    print(f"  总案例数: {total}")
    print(f"  成功处理: {success}")
    print(f"  跳过: {skipped}")
    print("="*80)
    
    # 生成待办清单
    print("\n待完成工作：")
    print("1. 为每个案例填写CASE_INFO字典")
    print("2. 为每个案例创建generate_diagram.py脚本")
    print("3. 运行所有generate_diagram.py生成PNG")
    print("4. 为实验结果部分添加图表说明")
    print("5. Web系统验证")

if __name__ == "__main__":
    main()

