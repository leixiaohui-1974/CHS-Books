"""
案例4: 光伏阵列配置
Case 4: PV Array Configuration

工程背景:
--------
实际光伏电站需要将大量组件串并联形成阵列
典型配置: 10-30个组件串联, 多串并联
系统规模: kW到MW级

学习目标:
--------
1. 理解串并联组合设计原则
2. 掌握阵列配置优化方法
3. 学习MW级电站建模
4. 分析不同配置的性能差异

核心原理:
--------
串联: V↑ I=  (提升电压)
并联: V=  I↑ (提升电流)
功率: P = Ns × Np × Pmodule
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

# 设置中文字体
rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

from code.models.pv_cell import SingleDiodeModel
from code.models.pv_module import PVModule
from code.models.pv_array import PVArray


def main():
    """
    主函数: 演示光伏阵列配置设计
    """
    print("=" * 80)
    print("案例4: 光伏阵列配置")
    print("Case 4: PV Array Configuration")
    print("=" * 80)
    
    # 1. 创建标准组件
    print("\n步骤1: 创建标准60片组件")
    print("-" * 80)
    
    cell = SingleDiodeModel(
        Isc=8.0, Voc=0.6, Imp=7.5, Vmp=0.48,
        T=298.15, G=1000.0
    )
    
    module = PVModule(
        cell_model=cell,
        Ns=60,
        Nb=3,
        name="60片标准组件"
    )
    
    vmpp_m, impp_m, pmpp_m = module.find_mpp()
    print(f"标准组件参数:")
    print(f"  Voc = {module.Voc:.2f} V")
    print(f"  Isc = {module.Isc:.2f} A")
    print(f"  Pmpp = {pmpp_m:.2f} W")
    
    # 2. 创建不同配置的阵列
    print("\n步骤2: 创建不同配置的光伏阵列")
    print("-" * 80)
    
    configs = [
        (1, 1, "单串单组", "1P1S"),
        (10, 1, "10串联", "1P10S"),
        (1, 10, "10并联", "10P1S"),
        (20, 5, "小型系统", "5P20S"),
        (25, 10, "中型系统", "10P25S"),
    ]
    
    arrays = []
    for Ns, Np, name, config in configs:
        array = PVArray(
            module=module,
            Ns=Ns,
            Np=Np,
            name=f"{name} ({config})"
        )
        arrays.append(array)
        
        vmpp, impp, pmpp = array.find_mpp()
        print(f"\n{name} ({config}):")
        print(f"  配置: {Np}串 × {Ns}组件/串 = {Ns*Np}个组件")
        print(f"  Voc = {array.Voc:.2f} V")
        print(f"  Isc = {array.Isc:.2f} A")
        print(f"  Vmpp = {vmpp:.2f} V")
        print(f"  Impp = {impp:.2f} A")
        print(f"  Pmpp = {pmpp:.2f} W = {pmpp/1000:.2f} kW")
    
    # 3. 设计1MW光伏电站
    print("\n步骤3: 设计1MW光伏电站")
    print("-" * 80)
    
    # 目标: 1MW = 1,000,000W
    target_power = 1e6  # W
    
    # 组件功率
    module_power = pmpp_m  # ~216W
    
    # 需要的组件数
    num_modules_needed = int(target_power / module_power)
    print(f"目标功率: {target_power/1e6:.2f} MW")
    print(f"组件功率: {module_power:.2f} W")
    print(f"需要组件: {num_modules_needed} 个")
    
    # 设计配置: 25组件/串 × 200串
    Ns_mw = 25
    Np_mw = 200
    
    array_mw = PVArray(
        module=module,
        Ns=Ns_mw,
        Np=Np_mw,
        name="1MW光伏电站"
    )
    
    array_mw.print_parameters()
    
    # 计算系统规模
    size_info = array_mw.calculate_system_size(module_area=1.6)
    print(f"\n系统规模:")
    print(f"  组件面积:              {size_info['module_area']:.2f} m²/个")
    print(f"  占地面积:              {size_info['total_area']:.2f} m² = {size_info['total_area']/1000:.2f} 亩")
    print(f"  实际功率:              {size_info['power_MW']:.3f} MW")
    print(f"  系统效率:              {size_info['efficiency']:.2f} %")
    print(f"  单位面积功率:          {size_info['kW_per_m2']:.3f} kW/m²")
    
    # 4. 绘制对比图
    print("\n步骤4: 绘制特性曲线对比")
    print("-" * 80)
    
    fig = plt.figure(figsize=(16, 12))
    
    # 图1-4: 不同配置的I-V曲线
    for idx, array in enumerate(arrays[:4], 1):
        ax = plt.subplot(3, 3, idx)
        V, I = array.get_iv_curve(200)
        vmpp, impp, pmpp = array.find_mpp()
        
        ax.plot(V, I, 'b-', linewidth=2)
        ax.plot(vmpp, impp, 'ro', markersize=10, label=f'MPP')
        ax.set_xlabel('电压 (V)', fontsize=10)
        ax.set_ylabel('电流 (A)', fontsize=10)
        ax.set_title(array.name, fontsize=11)
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=9)
    
    # 图5-8: 对应的P-V曲线
    for idx, array in enumerate(arrays[:4], 1):
        ax = plt.subplot(3, 3, idx + 4)
        V, P = array.get_pv_curve(200)
        vmpp, impp, pmpp = array.find_mpp()
        
        ax.plot(V, P/1000, 'g-', linewidth=2)
        ax.plot(vmpp, pmpp/1000, 'ro', markersize=10, label=f'{pmpp/1000:.1f}kW')
        ax.set_xlabel('电压 (V)', fontsize=10)
        ax.set_ylabel('功率 (kW)', fontsize=10)
        ax.set_title(f'{array.name} - P-V', fontsize=11)
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=9)
    
    # 图9: 配置对比柱状图
    ax9 = plt.subplot(3, 3, 9)
    names = [arr.name for arr in arrays]
    powers = [arr.find_mpp()[2]/1000 for arr in arrays]
    
    colors = ['steelblue', 'seagreen', 'coral', 'gold', 'mediumpurple']
    bars = ax9.bar(range(len(names)), powers, color=colors, alpha=0.7)
    ax9.set_ylabel('最大功率 (kW)', fontsize=10)
    ax9.set_title('不同配置功率对比', fontsize=11)
    ax9.set_xticks(range(len(names)))
    ax9.set_xticklabels([n.split('(')[1].strip(')') for n in names], rotation=30, fontsize=9)
    ax9.grid(True, alpha=0.3, axis='y')
    
    # 添加数值标签
    for i, (bar, power) in enumerate(zip(bars, powers)):
        height = bar.get_height()
        ax9.text(bar.get_x() + bar.get_width()/2., height,
                f'{power:.1f}kW',
                ha='center', va='bottom', fontsize=8)
    
    plt.suptitle('光伏阵列配置设计与对比分析', fontsize=14, fontweight='bold', y=0.995)
    plt.tight_layout()
    
    # 保存图表
    output_dir = os.path.join(os.path.dirname(__file__), 'outputs')
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(os.path.join(output_dir, 'array_configurations.png'), dpi=300, bbox_inches='tight')
    print(f"\n图表已保存到: {output_dir}/array_configurations.png")
    
    # 5. 配置设计分析
    print("\n步骤5: 配置设计分析")
    print("=" * 80)
    
    print("\n串并联特性验证:")
    arr_10s = arrays[1]  # 10串联
    arr_10p = arrays[2]  # 10并联
    
    v10s, i10s, p10s = arr_10s.find_mpp()
    v10p, i10p, p10p = arr_10p.find_mpp()
    
    print(f"\n10串联 (1P10S):")
    print(f"  Vmpp = {v10s:.2f} V = {v10s/vmpp_m:.1f} × Vmpp_module")
    print(f"  Impp = {i10s:.2f} A ≈ Impp_module")
    print(f"  验证: 串联提升电压 ✓")
    
    print(f"\n10并联 (10P1S):")
    print(f"  Vmpp = {v10p:.2f} V ≈ Vmpp_module")
    print(f"  Impp = {i10p:.2f} A = {i10p/impp_m:.1f} × Impp_module")
    print(f"  验证: 并联提升电流 ✓")
    
    print(f"\n功率缩放:")
    print(f"  单组件: {pmpp_m:.2f} W")
    print(f"  10串联: {p10s:.2f} W = {p10s/pmpp_m:.1f} × Pmodule")
    print(f"  10并联: {p10p:.2f} W = {p10p/pmpp_m:.1f} × Pmodule")
    print(f"  验证: P = Ns × Np × Pmodule ✓")
    
    print("\n" + "=" * 80)
    print("案例4主程序完成！")
    print("=" * 80)
    
    # 显示图表
    plt.show()


if __name__ == "__main__":
    main()
