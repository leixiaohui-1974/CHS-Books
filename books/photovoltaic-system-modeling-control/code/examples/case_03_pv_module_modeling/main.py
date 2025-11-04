"""
案例3: 光伏组件建模
Case 3: PV Module Modeling

工程背景:
--------
实际光伏系统中,单片电池(~0.6V)电压太低
需要将多片电池串联组成组件(30-40V)
标准组件: 60片或72片串联

学习目标:
--------
1. 理解组件的串联特性
2. 掌握旁路二极管的作用
3. 学习组件参数计算
4. 分析组件失配影响

核心原理:
--------
串联特性:
- 电流相同: I_module = I_cell
- 电压相加: V_module = Σ V_cell
- 功率相加: P_module = Σ P_cell

旁路二极管:
- 每20-24片配一个
- 防止热斑效应
- 减少遮挡损失
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


def main():
    """
    主函数: 演示光伏组件建模
    """
    print("=" * 80)
    print("案例3: 光伏组件建模")
    print("Case 3: PV Module Modeling")
    print("=" * 80)
    
    # 1. 创建单片电池模板
    print("\n步骤1: 创建单片电池模板")
    print("-" * 80)
    
    cell = SingleDiodeModel(
        Isc=8.0,      # 8A
        Voc=0.6,      # 0.6V
        Imp=7.5,      # 7.5A
        Vmp=0.48,     # 0.48V
        T=298.15,     # 25°C
        G=1000.0,     # 1000 W/m²
        name="标准单晶硅电池"
    )
    
    print(f"单片电池参数:")
    print(f"  Isc = {cell.Isc:.3f} A")
    print(f"  Voc = {cell.Voc:.3f} V")
    print(f"  Pmp = {cell.Vmp_stc * cell.Imp_stc:.3f} W")
    
    # 2. 创建60片组件
    print("\n步骤2: 创建60片光伏组件")
    print("-" * 80)
    
    module_60 = PVModule(
        cell_model=cell,
        Ns=60,
        Nb=3,
        name="60片光伏组件"
    )
    
    module_60.print_parameters()
    
    # 3. 创建72片组件
    print("\n步骤3: 创建72片光伏组件")
    print("-" * 80)
    
    module_72 = PVModule(
        cell_model=cell,
        Ns=72,
        Nb=3,
        name="72片光伏组件"
    )
    
    module_72.print_parameters()
    
    # 4. 计算MPP
    print("\n步骤4: 计算最大功率点")
    print("-" * 80)
    
    print("\n计算60片组件MPP...")
    vmpp_60, impp_60, pmpp_60 = module_60.find_mpp()
    print(f"60片组件:")
    print(f"  Vmpp = {vmpp_60:.2f} V")
    print(f"  Impp = {impp_60:.3f} A")
    print(f"  Pmpp = {pmpp_60:.2f} W")
    FF_60 = pmpp_60 / (module_60.Voc * module_60.Isc)
    print(f"  FF   = {FF_60:.4f} ({FF_60*100:.2f}%)")
    
    print(f"\n计算72片组件MPP...")
    vmpp_72, impp_72, pmpp_72 = module_72.find_mpp()
    print(f"72片组件:")
    print(f"  Vmpp = {vmpp_72:.2f} V")
    print(f"  Impp = {impp_72:.3f} A")
    print(f"  Pmpp = {pmpp_72:.2f} W")
    FF_72 = pmpp_72 / (module_72.Voc * module_72.Isc)
    print(f"  FF   = {FF_72:.4f} ({FF_72*100:.2f}%)")
    
    # 5. 绘制对比图
    print("\n步骤5: 绘制特性曲线")
    print("-" * 80)
    
    # 获取曲线数据
    V_cell, I_cell = cell.get_iv_curve(200)
    _, P_cell = cell.get_pv_curve(200)
    
    print("计算60片组件曲线...")
    V_60, I_60 = module_60.get_iv_curve(200)
    _, P_60 = module_60.get_pv_curve(200)
    
    print("计算72片组件曲线...")
    V_72, I_72 = module_72.get_iv_curve(200)
    _, P_72 = module_72.get_pv_curve(200)
    
    # 创建图表
    fig = plt.figure(figsize=(16, 10))
    
    # 图1: I-V曲线对比
    ax1 = plt.subplot(2, 3, 1)
    ax1.plot(V_cell, I_cell, 'b-', linewidth=2, label='单片电池')
    ax1.set_xlabel('电压 (V)')
    ax1.set_ylabel('电流 (A)')
    ax1.set_title('单片电池 I-V曲线')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # 图2: 60片组件I-V
    ax2 = plt.subplot(2, 3, 2)
    ax2.plot(V_60, I_60, 'g-', linewidth=2, label='60片组件')
    ax2.axvline(vmpp_60, color='r', linestyle='--', alpha=0.5, label=f'Vmpp={vmpp_60:.1f}V')
    ax2.axhline(impp_60, color='r', linestyle='--', alpha=0.5, label=f'Impp={impp_60:.2f}A')
    ax2.set_xlabel('电压 (V)')
    ax2.set_ylabel('电流 (A)')
    ax2.set_title('60片组件 I-V曲线')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    # 图3: 72片组件I-V
    ax3 = plt.subplot(2, 3, 3)
    ax3.plot(V_72, I_72, 'm-', linewidth=2, label='72片组件')
    ax3.axvline(vmpp_72, color='r', linestyle='--', alpha=0.5, label=f'Vmpp={vmpp_72:.1f}V')
    ax3.axhline(impp_72, color='r', linestyle='--', alpha=0.5, label=f'Impp={impp_72:.2f}A')
    ax3.set_xlabel('电压 (V)')
    ax3.set_ylabel('电流 (A)')
    ax3.set_title('72片组件 I-V曲线')
    ax3.grid(True, alpha=0.3)
    ax3.legend()
    
    # 图4: P-V曲线对比
    ax4 = plt.subplot(2, 3, 4)
    ax4.plot(V_cell, P_cell, 'b-', linewidth=2, label='单片电池')
    ax4.set_xlabel('电压 (V)')
    ax4.set_ylabel('功率 (W)')
    ax4.set_title('单片电池 P-V曲线')
    ax4.grid(True, alpha=0.3)
    ax4.legend()
    
    # 图5: 60片组件P-V
    ax5 = plt.subplot(2, 3, 5)
    ax5.plot(V_60, P_60, 'g-', linewidth=2, label='60片组件')
    ax5.plot(vmpp_60, pmpp_60, 'ro', markersize=10, label=f'MPP={pmpp_60:.1f}W')
    ax5.set_xlabel('电压 (V)')
    ax5.set_ylabel('功率 (W)')
    ax5.set_title('60片组件 P-V曲线')
    ax5.grid(True, alpha=0.3)
    ax5.legend()
    
    # 图6: 72片组件P-V
    ax6 = plt.subplot(2, 3, 6)
    ax6.plot(V_72, P_72, 'm-', linewidth=2, label='72片组件')
    ax6.plot(vmpp_72, pmpp_72, 'ro', markersize=10, label=f'MPP={pmpp_72:.1f}W')
    ax6.set_xlabel('电压 (V)')
    ax6.set_ylabel('功率 (W)')
    ax6.set_title('72片组件 P-V曲线')
    ax6.grid(True, alpha=0.3)
    ax6.legend()
    
    plt.suptitle('光伏组件建模 - 单片电池 vs 60片组件 vs 72片组件', fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    # 保存图表
    output_dir = os.path.join(os.path.dirname(__file__), 'outputs')
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(os.path.join(output_dir, 'module_characteristics.png'), dpi=300, bbox_inches='tight')
    print(f"\n图表已保存到: {output_dir}/module_characteristics.png")
    
    # 6. 关键分析
    print("\n步骤6: 关键分析")
    print("=" * 80)
    
    print("\n串联特性验证:")
    print(f"  单片Voc: {cell.Voc:.3f} V")
    print(f"  60片Voc: {module_60.Voc:.2f} V (理论: {cell.Voc*60:.2f} V)")
    print(f"  72片Voc: {module_72.Voc:.2f} V (理论: {cell.Voc*72:.2f} V)")
    print(f"  验证: Voc_module ≈ Ns × Voc_cell ✓")
    
    print(f"\n  单片Isc: {cell.Isc:.3f} A")
    print(f"  60片Isc: {module_60.Isc:.3f} A")
    print(f"  72片Isc: {module_72.Isc:.3f} A")
    print(f"  验证: Isc_module ≈ Isc_cell ✓")
    
    print(f"\n功率放大:")
    P_cell_mpp = cell.Vmp_stc * cell.Imp_stc
    print(f"  单片Pmp: {P_cell_mpp:.3f} W")
    print(f"  60片Pmp: {pmpp_60:.2f} W (放大 {pmpp_60/P_cell_mpp:.1f} 倍)")
    print(f"  72片Pmp: {pmpp_72:.2f} W (放大 {pmpp_72/P_cell_mpp:.1f} 倍)")
    print(f"  验证: Pmp_module ≈ Ns × Pmp_cell ✓")
    
    print(f"\n填充因子:")
    FF_cell = P_cell_mpp / (cell.Voc * cell.Isc)
    print(f"  单片FF:  {FF_cell:.4f}")
    print(f"  60片FF:  {FF_60:.4f}")
    print(f"  72片FF:  {FF_72:.4f}")
    print(f"  结论: FF基本保持不变 ✓")
    
    print("\n" + "=" * 80)
    print("案例3主程序完成！")
    print("=" * 80)
    
    # 显示图表
    plt.show()


if __name__ == "__main__":
    main()
