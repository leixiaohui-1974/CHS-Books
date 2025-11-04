"""
案例2: 双二极管精确模型
Case 2: Double Diode Precise Model

工程背景:
--------
高精度光伏电池建模需求
使用双二极管等效电路模型,考虑扩散电流和复合电流
提高模型精度,特别是在低辐照度和高温条件下

学习目标:
--------
1. 理解双二极管模型的物理意义
2. 掌握扩散电流和复合电流的区别
3. 对比单二极管和双二极管模型的精度差异
4. 分析不同条件下模型的适用性

核心方程:
--------
I = Iph - I01*[exp((V+I*Rs)/(n1*Vt)) - 1] - I02*[exp((V+I*Rs)/(n2*Vt)) - 1] - (V+I*Rs)/Rsh

其中:
- I01: 扩散电流饱和值 (主导)
- I02: 复合电流饱和值 (辅助)
- n1: 扩散理想因子 (≈1.0)
- n2: 复合理想因子 (≈2.0)
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

from code.models.pv_cell import SingleDiodeModel, DoubleDiodeModel


def compare_models(title="单二极管 vs 双二极管模型对比"):
    """
    对比单二极管和双二极管模型
    """
    # 创建两个模型
    pv1 = SingleDiodeModel(
        Isc=8.0, Voc=0.6, Imp=7.5, Vmp=0.48,
        T=298.15, G=1000.0,
        name="单二极管模型"
    )
    
    pv2 = DoubleDiodeModel(
        Isc=8.0, Voc=0.6, Imp=7.5, Vmp=0.48,
        T=298.15, G=1000.0,
        name="双二极管模型"
    )
    
    # 获取I-V曲线
    V1, I1 = pv1.get_iv_curve(300)
    V2, I2 = pv2.get_iv_curve(300)
    
    # 获取P-V曲线
    _, P1 = pv1.get_pv_curve(300)
    _, P2 = pv2.get_pv_curve(300)
    
    # 创建图表
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    
    # 1. I-V对比
    ax1.plot(V1, I1, 'b-', linewidth=2, label='单二极管')
    ax1.plot(V2, I2, 'r--', linewidth=2, label='双二极管')
    ax1.set_xlabel('电压 V (V)', fontsize=12)
    ax1.set_ylabel('电流 I (A)', fontsize=12)
    ax1.set_title('I-V特性对比', fontsize=13)
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=11)
    
    # 2. P-V对比
    ax2.plot(V1, P1, 'b-', linewidth=2, label='单二极管')
    ax2.plot(V2, P2, 'r--', linewidth=2, label='双二极管')
    ax2.set_xlabel('电压 V (V)', fontsize=12)
    ax2.set_ylabel('功率 P (W)', fontsize=12)
    ax2.set_title('P-V特性对比', fontsize=13)
    ax2.grid(True, alpha=0.3)
    ax2.legend(fontsize=11)
    
    # 3. 电流差异
    I_diff = np.abs(I1 - I2)
    ax3.plot(V1, I_diff, 'g-', linewidth=2)
    ax3.set_xlabel('电压 V (V)', fontsize=12)
    ax3.set_ylabel('电流差异 |ΔI| (A)', fontsize=12)
    ax3.set_title('电流差异', fontsize=13)
    ax3.grid(True, alpha=0.3)
    
    # 统计
    max_diff = np.max(I_diff)
    mean_diff = np.mean(I_diff)
    ax3.text(0.05, 0.95, f'最大差异: {max_diff:.4f}A\n平均差异: {mean_diff:.4f}A',
             transform=ax3.transAxes, fontsize=10,
             verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    # 4. 功率差异
    P_diff = np.abs(P1 - P2)
    ax4.plot(V1, P_diff, 'm-', linewidth=2)
    ax4.set_xlabel('电压 V (V)', fontsize=12)
    ax4.set_ylabel('功率差异 |ΔP| (W)', fontsize=12)
    ax4.set_title('功率差异', fontsize=13)
    ax4.grid(True, alpha=0.3)
    
    max_p_diff = np.max(P_diff)
    mean_p_diff = np.mean(P_diff)
    ax4.text(0.05, 0.95, f'最大差异: {max_p_diff:.4f}W\n平均差异: {mean_p_diff:.4f}W',
             transform=ax4.transAxes, fontsize=10,
             verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    fig.suptitle(title, fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    return fig, (pv1, pv2)


def main():
    """
    主函数: 演示双二极管模型
    """
    print("=" * 80)
    print("案例2: 双二极管精确模型")
    print("Case 2: Double Diode Precise Model")
    print("=" * 80)
    
    # 创建单二极管模型
    print("\n创建单二极管模型...")
    pv1 = SingleDiodeModel(
        Isc=8.0, Voc=0.6, Imp=7.5, Vmp=0.48,
        T=298.15, G=1000.0,
        name="单二极管模型"
    )
    pv1.print_parameters()
    
    # 创建双二极管模型
    print("\n\n创建双二极管模型...")
    pv2 = DoubleDiodeModel(
        Isc=8.0, Voc=0.6, Imp=7.5, Vmp=0.48,
        T=298.15, G=1000.0,
        name="双二极管模型"
    )
    pv2.print_parameters()
    
    # 计算并对比MPP
    print("\n" + "=" * 80)
    print("最大功率点 (MPP) 对比:")
    print("=" * 80)
    
    vmpp1, impp1, pmpp1 = pv1.find_mpp()
    print(f"\n单二极管模型:")
    print(f"  Vmpp = {vmpp1:.4f} V")
    print(f"  Impp = {impp1:.4f} A")
    print(f"  Pmpp = {pmpp1:.4f} W")
    FF1 = pmpp1 / (pv1.Voc * pv1.Isc)
    print(f"  FF   = {FF1:.4f} ({FF1*100:.2f}%)")
    
    vmpp2, impp2, pmpp2 = pv2.find_mpp()
    print(f"\n双二极管模型:")
    print(f"  Vmpp = {vmpp2:.4f} V")
    print(f"  Impp = {impp2:.4f} A")
    print(f"  Pmpp = {pmpp2:.4f} W")
    FF2 = pmpp2 / (pv2.Voc * pv2.Isc)
    print(f"  FF   = {FF2:.4f} ({FF2*100:.2f}%)")
    
    # 差异分析
    print(f"\n差异分析:")
    print(f"  ΔVmpp = {abs(vmpp2-vmpp1):.4f} V ({abs(vmpp2-vmpp1)/vmpp1*100:.2f}%)")
    print(f"  ΔImpp = {abs(impp2-impp1):.4f} A ({abs(impp2-impp1)/impp1*100:.2f}%)")
    print(f"  ΔPmpp = {abs(pmpp2-pmpp1):.4f} W ({abs(pmpp2-pmpp1)/pmpp1*100:.2f}%)")
    print(f"  ΔFF   = {abs(FF2-FF1):.4f} ({abs(FF2-FF1)/FF1*100:.2f}%)")
    
    # 特征点对比
    print("\n" + "=" * 80)
    print("特征点对比:")
    print("=" * 80)
    
    test_voltages = [0, 0.1, 0.2, 0.3, 0.4, 0.48, 0.5, 0.55, 0.6]
    print(f"\n{'电压V(V)':<12} {'单I(A)':<12} {'双I(A)':<12} {'差异(A)':<12} {'差异(%)':<12}")
    print("-" * 60)
    for v in test_voltages:
        i1 = pv1.calculate_current(v)
        i2 = pv2.calculate_current(v)
        diff = abs(i2 - i1)
        diff_pct = (diff / i1 * 100) if i1 > 0.01 else 0
        print(f"{v:<12.3f} {i1:<12.4f} {i2:<12.4f} {diff:<12.4f} {diff_pct:<12.2f}")
    
    # 绘制对比图
    print("\n" + "=" * 80)
    print("绘制模型对比图...")
    print("=" * 80)
    
    fig, _ = compare_models("单二极管 vs 双二极管模型对比 (STC)")
    
    # 保存图片
    output_dir = os.path.join(os.path.dirname(__file__), 'outputs')
    os.makedirs(output_dir, exist_ok=True)
    
    fig.savefig(os.path.join(output_dir, 'model_comparison.png'), dpi=300, bbox_inches='tight')
    print(f"\n图表已保存到: {output_dir}/model_comparison.png")
    
    # 关键发现
    print("\n" + "=" * 80)
    print("关键发现:")
    print("=" * 80)
    print("\n1. 模型精度:")
    print("   • 双二极管模型考虑了复合电流,物理意义更完整")
    print("   • 在标准条件下(STC),两个模型差异较小")
    print(f"   • 最大功率差异约 {abs(pmpp2-pmpp1)/pmpp1*100:.2f}%")
    
    print("\n2. 参数特点:")
    print("   • 单二极管: 5个参数 (Iph, I0, Rs, Rsh, n)")
    print("   • 双二极管: 7个参数 (Iph, I01, I02, Rs, Rsh, n1, n2)")
    print("   • n1≈1.0 (扩散), n2≈2.0 (复合)")
    
    print("\n3. 适用场景:")
    print("   • 单二极管: 快速计算,标准条件,工程应用")
    print("   • 双二极管: 高精度要求,极端条件,科研分析")
    
    print("\n4. 计算复杂度:")
    print("   • 单二极管: 简单快速")
    print("   • 双二极管: 略复杂,但精度更高")
    
    print("\n" + "=" * 80)
    print("案例2完成！")
    print("=" * 80)
    
    # 显示图表
    plt.show()


if __name__ == "__main__":
    main()
