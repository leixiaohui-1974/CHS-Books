"""
案例1: 光伏电池I-V特性建模
Case 1: PV Cell I-V Characteristic Modeling

工程背景:
--------
单晶硅光伏电池特性测试和建模
使用单二极管等效电路模型

学习目标:
--------
1. 理解光伏电池单二极管等效电路模型
2. 掌握I-V特性曲线和P-V特性曲线的计算方法
3. 分析温度和辐照度对光伏电池性能的影响
4. 学会寻找最大功率点(MPP)

核心方程:
--------
I = Iph - I0 * [exp((V + I*Rs)/(n*Vt)) - 1] - (V + I*Rs)/Rsh

其中:
- Iph: 光生电流
- I0: 二极管反向饱和电流
- Rs: 串联电阻
- Rsh: 并联电阻
- n: 理想因子
- Vt: 热电压 = kT/q
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

# 设置中文字体
rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

from code.models.pv_cell import SingleDiodeModel


def plot_iv_curve(pv_cell: SingleDiodeModel, title: str = "I-V特性曲线"):
    """
    绘制I-V特性曲线
    
    Parameters:
    -----------
    pv_cell : SingleDiodeModel
        光伏电池模型
    title : str
        图表标题
    """
    # 获取I-V曲线数据
    V, I = pv_cell.get_iv_curve(300)
    
    # 创建图表
    plt.figure(figsize=(10, 6))
    plt.plot(V, I, 'b-', linewidth=2, label='I-V曲线')
    
    # 标记关键点
    plt.plot(0, pv_cell.Isc, 'ro', markersize=10, label=f'短路点: Isc={pv_cell.Isc:.3f}A')
    plt.plot(pv_cell.Voc, 0, 'go', markersize=10, label=f'开路点: Voc={pv_cell.Voc:.3f}V')
    
    # 找到MPP
    vmpp, impp, pmpp = pv_cell.find_mpp()
    plt.plot(vmpp, impp, 'r*', markersize=15, label=f'MPP: V={vmpp:.3f}V, I={impp:.3f}A')
    
    plt.xlabel('电压 V (V)', fontsize=12)
    plt.ylabel('电流 I (A)', fontsize=12)
    plt.title(title, fontsize=14)
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=10)
    plt.tight_layout()
    
    return plt.gcf()


def plot_pv_curve(pv_cell: SingleDiodeModel, title: str = "P-V特性曲线"):
    """
    绘制P-V特性曲线
    
    Parameters:
    -----------
    pv_cell : SingleDiodeModel
        光伏电池模型
    title : str
        图表标题
    """
    # 获取P-V曲线数据
    V, P = pv_cell.get_pv_curve(300)
    
    # 创建图表
    plt.figure(figsize=(10, 6))
    plt.plot(V, P, 'r-', linewidth=2, label='P-V曲线')
    
    # 找到MPP
    vmpp, impp, pmpp = pv_cell.find_mpp()
    plt.plot(vmpp, pmpp, 'r*', markersize=15, 
             label=f'MPP: Vmpp={vmpp:.3f}V, Pmpp={pmpp:.3f}W')
    
    plt.xlabel('电压 V (V)', fontsize=12)
    plt.ylabel('功率 P (W)', fontsize=12)
    plt.title(title, fontsize=14)
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=10)
    plt.tight_layout()
    
    return plt.gcf()


def plot_iv_and_pv(pv_cell: SingleDiodeModel, title: str = "光伏电池特性曲线"):
    """
    同时绘制I-V和P-V曲线
    
    Parameters:
    -----------
    pv_cell : SingleDiodeModel
        光伏电池模型
    title : str
        图表标题
    """
    # 获取曲线数据
    V, I = pv_cell.get_iv_curve(300)
    _, P = pv_cell.get_pv_curve(300)
    
    # 创建子图
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
    
    # I-V曲线
    ax1.plot(V, I, 'b-', linewidth=2)
    ax1.plot(0, pv_cell.Isc, 'ro', markersize=10, label=f'Isc={pv_cell.Isc:.3f}A')
    ax1.plot(pv_cell.Voc, 0, 'go', markersize=10, label=f'Voc={pv_cell.Voc:.3f}V')
    
    vmpp, impp, pmpp = pv_cell.find_mpp()
    ax1.plot(vmpp, impp, 'r*', markersize=15, label=f'MPP')
    
    ax1.set_xlabel('电压 V (V)', fontsize=12)
    ax1.set_ylabel('电流 I (A)', fontsize=12)
    ax1.set_title('I-V特性曲线', fontsize=13)
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=10)
    
    # P-V曲线
    ax2.plot(V, P, 'r-', linewidth=2)
    ax2.plot(vmpp, pmpp, 'r*', markersize=15, label=f'Pmpp={pmpp:.3f}W')
    
    ax2.set_xlabel('电压 V (V)', fontsize=12)
    ax2.set_ylabel('功率 P (W)', fontsize=12)
    ax2.set_title('P-V特性曲线', fontsize=13)
    ax2.grid(True, alpha=0.3)
    ax2.legend(fontsize=10)
    
    fig.suptitle(title, fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    return fig


def main():
    """
    主函数: 演示光伏电池I-V特性建模
    """
    print("=" * 80)
    print("案例1: 光伏电池I-V特性建模")
    print("Case 1: PV Cell I-V Characteristic Modeling")
    print("=" * 80)
    
    # 创建标准光伏电池模型
    # 典型单晶硅电池参数 (156mm × 156mm)
    print("\n创建光伏电池模型...")
    pv = SingleDiodeModel(
        Isc=8.0,      # 短路电流 8A
        Voc=0.6,      # 开路电压 0.6V
        Imp=7.5,      # 最大功率点电流 7.5A
        Vmp=0.48,     # 最大功率点电压 0.48V
        T=298.15,     # 温度 25°C
        G=1000.0,     # 辐照度 1000W/m²
        n=1.2,        # 理想因子
        name="单晶硅光伏电池"
    )
    
    # 打印模型参数
    pv.print_parameters()
    
    # 计算关键点
    print("\n" + "=" * 80)
    print("关键点计算:")
    print("=" * 80)
    
    test_voltages = [0, 0.1, 0.2, 0.3, 0.4, 0.48, 0.5, 0.55, 0.6]
    print(f"{'电压V (V)':<15} {'电流I (A)':<15} {'功率P (W)':<15}")
    print("-" * 45)
    for v in test_voltages:
        i = pv.calculate_current(v)
        p = pv.calculate_power(v)
        print(f"{v:<15.3f} {i:<15.3f} {p:<15.3f}")
    
    # 寻找最大功率点
    vmpp, impp, pmpp = pv.find_mpp()
    print("\n" + "=" * 80)
    print("最大功率点 (MPP):")
    print("=" * 80)
    print(f"Vmpp = {vmpp:.4f} V")
    print(f"Impp = {impp:.4f} A")
    print(f"Pmpp = {pmpp:.4f} W")
    
    # 计算填充因子 (Fill Factor)
    FF = pmpp / (pv.Voc * pv.Isc)
    print(f"\n填充因子 FF = {FF:.4f} ({FF*100:.2f}%)")
    print(f"(理想填充因子通常在0.7-0.85之间)")
    
    # 计算效率 (假设电池面积为156mm × 156mm = 0.024336 m²)
    area = 0.024336  # m²
    efficiency = pmpp / (pv.G * area)
    print(f"\n电池效率 η = {efficiency:.4f} ({efficiency*100:.2f}%)")
    print(f"(面积: {area*10000:.1f} cm², 辐照度: {pv.G} W/m²)")
    
    # 绘制特性曲线
    print("\n" + "=" * 80)
    print("绘制特性曲线...")
    print("=" * 80)
    
    # 绘制I-V和P-V曲线
    fig = plot_iv_and_pv(pv, f"光伏电池特性曲线 (T={pv.T-273.15:.0f}°C, G={pv.G:.0f}W/m²)")
    
    # 保存图片
    output_dir = os.path.join(os.path.dirname(__file__), 'outputs')
    os.makedirs(output_dir, exist_ok=True)
    
    fig.savefig(os.path.join(output_dir, 'pv_cell_characteristics.png'), dpi=300, bbox_inches='tight')
    print(f"\n图表已保存到: {output_dir}/pv_cell_characteristics.png")
    
    print("\n" + "=" * 80)
    print("案例1完成！")
    print("=" * 80)
    
    # 显示图表
    plt.show()


if __name__ == "__main__":
    main()
