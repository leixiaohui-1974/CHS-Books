"""
案例8：单元线法河道汇流
=====================

演示单元线法和Muskingum法的原理和应用

作者: CHS-Books项目组  
日期: 2025-11-02
"""

import sys
sys.path.insert(0, '../../..')

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

from code.core.channel_routing import (
    UnitHydrograph, create_snyder_uh, create_scs_uh,
    create_triangular_uh, MuskingumChannel
)

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 创建输出目录
output_dir = Path('outputs')
output_dir.mkdir(exist_ok=True)


def compare_unit_hydrographs(basin_area, save_path=None):
    """对比三种单元线"""
    dt = 1.0  # h
    
    # 1. 三角形单元线
    tp_tri = 5
    tb_tri = 15
    uh_tri = create_triangular_uh(basin_area, tp_tri, tb_tri, dt)
    
    # 2. Snyder单元线
    L = 20  # 主河道长度 km
    Lc = 10  # 重心到出口 km
    uh_snyder, tp_snyder = create_snyder_uh(basin_area, L, Lc, dt=dt)
    
    # 3. SCS单元线
    tc = 8  # 汇流时间 h
    uh_scs = create_scs_uh(basin_area, tc, dt=dt)
    
    # 绘图
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    
    # 子图1-3: 各单元线
    uhs = [
        ('三角形单元线', uh_tri, 'blue'),
        ('Snyder单元线', uh_snyder, 'red'),
        ('SCS单元线', uh_scs, 'green')
    ]
    
    for idx, (name, uh, color) in enumerate(uhs):
        if idx < 3:
            row = idx // 2
            col = idx % 2
            ax = axes[row, col]
            
            time = np.arange(len(uh)) * dt
            ax.plot(time, uh, linewidth=2.5, color=color, label=name)
            ax.fill_between(time, 0, uh, alpha=0.3, color=color)
            
            peak = np.max(uh)
            peak_time = np.argmax(uh) * dt
            
            ax.axvline(peak_time, color=color, linestyle='--', alpha=0.5)
            ax.set_xlabel('时间 (h)', fontsize=12)
            ax.set_ylabel('单元线纵坐标 (m³/s/mm/km²)', fontsize=11)
            ax.set_title(f'{name}\n峰值={peak:.4f}, 峰现={peak_time:.1f}h',
                        fontsize=13, fontweight='bold')
            ax.grid(True, alpha=0.3)
            ax.legend(fontsize=11)
    
    # 子图4: 综合对比
    ax = axes[1, 1]
    for name, uh, color in uhs:
        time = np.arange(len(uh)) * dt
        ax.plot(time, uh, linewidth=2.5, color=color, label=name)
    
    ax.set_xlabel('时间 (h)', fontsize=12)
    ax.set_ylabel('单元线纵坐标 (m³/s/mm/km²)', fontsize=12)
    ax.set_title('三种单元线对比', fontsize=13, fontweight='bold')
    ax.legend(fontsize=11, loc='upper right')
    ax.grid(True, alpha=0.3)
    
    plt.suptitle('单元线对比分析', fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"图表已保存: {save_path}")
    
    return fig, {'triangular': uh_tri, 'snyder': uh_snyder, 'scs': uh_scs}


def demonstrate_convolution(basin_area, save_path=None):
    """演示单元线卷积"""
    dt = 1.0
    
    # 创建单元线
    tc = 8
    uh = create_scs_uh(basin_area, tc, dt)
    model = UnitHydrograph(uh, dt)
    
    # 模拟净雨过程
    n_steps = 20
    runoff = np.zeros(n_steps)
    runoff[3:8] = [5, 10, 15, 10, 5]  # mm
    
    time_runoff = np.arange(n_steps) * dt
    
    # 卷积计算
    results = model.run(runoff)
    
    # 绘图
    fig, axes = plt.subplots(3, 1, figsize=(14, 12), sharex=True)
    
    # 子图1: 净雨过程
    axes[0].bar(time_runoff, runoff, width=0.8, color='skyblue',
               edgecolor='black', linewidth=1.5, alpha=0.7)
    axes[0].set_ylabel('净雨深度 (mm)', fontsize=12)
    axes[0].set_title('净雨过程', fontsize=13, fontweight='bold')
    axes[0].grid(True, alpha=0.3, axis='y')
    
    # 子图2: 单元线
    time_uh = np.arange(len(uh)) * dt
    axes[1].plot(time_uh, uh, linewidth=2.5, color='red', label='单元线')
    axes[1].fill_between(time_uh, 0, uh, alpha=0.3, color='red')
    axes[1].set_ylabel('UH (m³/s/mm/km²)', fontsize=12)
    axes[1].set_title('单元线', fontsize=13, fontweight='bold')
    axes[1].legend(fontsize=11)
    axes[1].grid(True, alpha=0.3)
    
    # 子图3: 流量过程
    axes[2].plot(results['time'], results['discharge'], 
                linewidth=2.5, color='green', label='流量过程')
    axes[2].fill_between(results['time'], 0, results['discharge'],
                        alpha=0.3, color='green')
    axes[2].set_xlabel('时间 (h)', fontsize=12)
    axes[2].set_ylabel('流量 (m³/s)', fontsize=12)
    axes[2].set_title(f'流量过程（峰值={np.max(results["discharge"]):.2f} m³/s）',
                     fontsize=13, fontweight='bold')
    axes[2].legend(fontsize=11)
    axes[2].grid(True, alpha=0.3)
    
    plt.suptitle('单元线卷积演示', fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"图表已保存: {save_path}")
    
    return fig, results


def demonstrate_muskingum(save_path=None):
    """演示Muskingum河道演进"""
    # Muskingum参数
    params = {
        'K': 6.0,    # 6小时
        'X': 0.25,   # 典型河道
        'dt': 1.0    # 1小时
    }
    
    model = MuskingumChannel(params)
    
    # 模拟入流洪水
    time = np.arange(30)
    inflow = np.zeros(30)
    inflow[5:12] = [100, 200, 400, 600, 500, 300, 150]
    
    # 运行模型
    results = model.run(inflow)
    
    # 绘图
    fig, axes = plt.subplots(2, 1, figsize=(14, 10))
    
    # 子图1: 入流vs出流
    ax = axes[0]
    ax.plot(time, inflow, linewidth=2.5, color='blue', 
           marker='o', markersize=6, label='入流')
    ax.plot(time, results['outflow'], linewidth=2.5, color='red',
           marker='s', markersize=6, label='出流')
    ax.fill_between(time, 0, inflow, alpha=0.2, color='blue')
    ax.fill_between(time, 0, results['outflow'], alpha=0.2, color='red')
    
    ax.set_xlabel('时间 (h)', fontsize=12)
    ax.set_ylabel('流量 (m³/s)', fontsize=12)
    ax.set_title(f'Muskingum河道演进 (K={params["K"]}h, X={params["X"]})',
                fontsize=14, fontweight='bold')
    ax.legend(fontsize=12, loc='upper right')
    ax.grid(True, alpha=0.3)
    
    # 标注削峰和滞时
    peak_in = np.max(inflow)
    peak_out = np.max(results['outflow'])
    ax.text(0.02, 0.98, 
           f'削峰率: {results["attenuation"]:.1%}\n滞时: {results["lag"]}h',
           transform=ax.transAxes, fontsize=12,
           verticalalignment='top',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    # 子图2: 蓄量变化
    ax = axes[1]
    ax.plot(time, results['storage'] / 1e6, linewidth=2.5, color='purple')
    ax.fill_between(time, 0, results['storage'] / 1e6, alpha=0.3, color='purple')
    ax.set_xlabel('时间 (h)', fontsize=12)
    ax.set_ylabel('蓄量 (10⁶ m³)', fontsize=12)
    ax.set_title('河道蓄量变化', fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"图表已保存: {save_path}")
    
    return fig, results


def main():
    """主函数"""
    print("=" * 70)
    print("案例8：单元线法河道汇流")
    print("=" * 70)
    print()
    
    basin_area = 100  # km²
    
    # 1. 单元线对比
    print("1. 三种单元线对比...")
    fig1, uhs = compare_unit_hydrographs(basin_area,
                                        save_path=output_dir / 'uh_comparison.png')
    plt.close(fig1)
    
    for name, uh in uhs.items():
        peak = np.max(uh)
        peak_time = np.argmax(uh)
        print(f"   {name:12s}: 峰值={peak:.4f}, 峰现={peak_time}h")
    print()
    
    # 2. 卷积演示
    print("2. 单元线卷积演示...")
    fig2, conv_results = demonstrate_convolution(basin_area,
                                                save_path=output_dir / 'convolution_demo.png')
    plt.close(fig2)
    
    print(f"   峰值流量: {np.max(conv_results['discharge']):.2f} m³/s")
    print(f"   峰现时间: {np.argmax(conv_results['discharge'])} h")
    print()
    
    # 3. Muskingum演进
    print("3. Muskingum河道演进...")
    fig3, musk_results = demonstrate_muskingum(
        save_path=output_dir / 'muskingum_routing.png'
    )
    plt.close(fig3)
    
    print(f"   削峰率: {musk_results['attenuation']:.1%}")
    print(f"   滞时: {musk_results['lag']} h")
    print(f"   演算系数: C0={musk_results['C0']:.3f}, "
          f"C1={musk_results['C1']:.3f}, C2={musk_results['C2']:.3f}")
    print()
    
    # 4. 总结
    print("=" * 70)
    print("分析完成！")
    print("=" * 70)
    print()
    print("生成的文件:")
    print("  - outputs/uh_comparison.png      : 单元线对比")
    print("  - outputs/convolution_demo.png   : 卷积演示")
    print("  - outputs/muskingum_routing.png  : Muskingum演进")
    print()
    print("关键发现:")
    print("  1. 三种单元线形状各有特点，SCS最标准化")
    print("  2. 单元线卷积可快速计算流量过程")
    print("  3. Muskingum法能有效模拟河道调蓄作用")
    print("  4. 河道对洪水有明显的削峰滞后效果")
    print()


if __name__ == '__main__':
    main()
