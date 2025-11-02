"""
案例15：水文-水动力耦合模拟
=========================

演示水文模型与水动力模型的耦合计算，
实现从降雨产流到河道洪水演进的全过程模拟。

核心内容：
1. 水文模型（新安江）产流计算
2. 径流-流量转换
3. 水动力模型（Saint-Venant）河道演进
4. 耦合流程与接口
5. 水位-流量过程分析

作者: CHS-Books项目组
日期: 2025-11-02
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from core.coupling.hydro_interface import couple_simulation

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def run_coupled_simulation():
    """运行耦合模拟"""
    print("\n" + "="*70)
    print("案例15：水文-水动力耦合模拟")
    print("="*70 + "\n")
    
    output_dir = 'outputs'
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. 设置参数
    print("1. 设置模拟参数...")
    
    # 水文模型参数（新安江）
    hydro_params = {
        'K': 0.8, 'UM': 20.0, 'LM': 80.0, 'C': 0.15,
        'WM': 120.0, 'B': 0.35, 'IM': 0.02,
        'SM': 30.0, 'EX': 1.5, 'KG': 0.4, 'KI': 0.3,
        'CG': 0.98, 'CI': 0.6, 'CS': 0.8
    }
    
    # 水动力模型参数（Saint-Venant）
    hydraulic_params = {
        'L': 2000.0,   # 河段长度 (m)
        'dx': 100.0,   # 空间步长 (m)
        'n': 0.03,     # 曼宁糙率
        'B': 20.0,     # 河道宽度 (m)
        'S0': 0.001,   # 河床坡度
        'h0': 1.5      # 初始水深 (m)
    }
    
    # 流域特征
    watershed_area = 150.0  # km²
    
    print(f"   流域面积: {watershed_area} km²")
    print(f"   河段长度: {hydraulic_params['L']} m")
    print(f"   河道宽度: {hydraulic_params['B']} m\n")
    
    # 2. 生成输入数据
    print("2. 生成降雨过程...")
    n_days = 30
    dt_hydro = 3600.0  # 1小时
    
    # 降雨（三次洪峰）
    rainfall = np.zeros(n_days * 24)
    flood_hours = [5*24, 15*24, 25*24]  # 第5、15、25天
    for hour in flood_hours:
        for i in range(12):  # 12小时降雨
            if hour + i < len(rainfall):
                rainfall[hour + i] = 25 * np.exp(-0.2 * i) * (0.8 + 0.4 * np.random.rand())
    
    # 蒸发
    evaporation = 2.0 + 1.5 * np.sin(2 * np.pi * np.arange(len(rainfall)) / (24*30))
    
    print(f"   时间步数: {len(rainfall)}")
    print(f"   总降雨: {np.sum(rainfall):.1f} mm\n")
    
    # 3. 运行耦合模拟
    print("3. 运行水文-水动力耦合模拟...")
    
    results = couple_simulation(
        rainfall=rainfall,
        evaporation=evaporation,
        hydro_params=hydro_params,
        hydraulic_params=hydraulic_params,
        dt_hydro=dt_hydro,
        dt_hydraulic=60.0,  # 1分钟
        watershed_area=watershed_area
    )
    
    print("\n4. 模拟完成\n")
    
    # 4. 提取结果
    runoff = results['runoff']
    discharge = results['discharge']
    t_hydro = results['t_hydro'] / 3600.0  # 转为小时
    
    hydraulic = results['hydraulic']
    x = hydraulic['x']
    h = hydraulic['h']
    Q = hydraulic['Q']
    t_hydraulic = hydraulic['t'] / 3600.0  # 转为小时
    
    # 统计
    print("="*70)
    print("耦合模拟结果统计")
    print("="*70)
    
    print(f"\n【水文模拟】")
    print(f"  总降雨: {np.sum(rainfall):.1f} mm")
    print(f"  总径流: {np.sum(runoff):.1f} mm")
    print(f"  径流系数: {np.sum(runoff) / np.sum(rainfall):.3f}")
    print(f"  峰值径流: {np.max(runoff):.2f} mm/h")
    print(f"  峰值流量: {np.max(discharge):.1f} m³/s")
    
    print(f"\n【水动力模拟】")
    print(f"  河段长度: {hydraulic_params['L']:.0f} m")
    print(f"  网格点数: {len(x)}")
    print(f"  时间步数: {len(t_hydraulic)}")
    print(f"  最大水深: {np.max(h):.2f} m")
    print(f"  最大流量: {np.max(Q):.1f} m³/s")
    print(f"  最大流速: {np.max(hydraulic['v']):.2f} m/s")
    
    # 出口断面
    Q_outlet = Q[:, -1]
    h_outlet = h[:, -1]
    print(f"\n【出口断面】")
    print(f"  峰值流量: {np.max(Q_outlet):.1f} m³/s")
    print(f"  峰值水深: {np.max(h_outlet):.2f} m")
    print(f"  平均水深: {np.mean(h_outlet):.2f} m")
    
    # 5. 可视化
    print(f"\n5. 生成可视化...")
    
    fig = plt.figure(figsize=(16, 10))
    gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
    
    # 图1：降雨-径流过程
    ax1 = fig.add_subplot(gs[0, :])
    ax1_rain = ax1.twinx()
    
    ax1_rain.bar(t_hydro, rainfall, width=0.8, color='lightblue', 
                alpha=0.5, label='降雨')
    ax1_rain.set_ylim([max(rainfall)*2.5, 0])
    ax1_rain.set_ylabel('降雨 (mm/h)', fontsize=10)
    ax1_rain.legend(loc='upper right', fontsize=9)
    
    ax1.plot(t_hydro, runoff, 'b-', linewidth=2, label='径流')
    ax1.set_xlabel('时间 (小时)', fontsize=11)
    ax1.set_ylabel('径流 (mm/h)', fontsize=10)
    ax1.set_title('【水文模拟】降雨-径流过程', fontsize=12, fontweight='bold')
    ax1.legend(loc='upper left', fontsize=9)
    ax1.grid(True, alpha=0.3)
    
    # 图2：流域出流流量
    ax2 = fig.add_subplot(gs[1, 0])
    ax2.plot(t_hydro, discharge, 'g-', linewidth=2)
    ax2.set_xlabel('时间 (小时)', fontsize=11)
    ax2.set_ylabel('流量 (m³/s)', fontsize=10)
    ax2.set_title('【接口转换】流域出流流量', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    # 图3：出口断面流量
    ax3 = fig.add_subplot(gs[1, 1])
    # 采样显示
    sample_rate = max(1, len(t_hydraulic) // 1000)
    ax3.plot(t_hydraulic[::sample_rate], Q_outlet[::sample_rate], 
            'r-', linewidth=1.5)
    ax3.set_xlabel('时间 (小时)', fontsize=11)
    ax3.set_ylabel('流量 (m³/s)', fontsize=10)
    ax3.set_title('【水动力模拟】出口断面流量', fontsize=12, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    
    # 图4：水深沿程分布（选取几个时刻）
    ax4 = fig.add_subplot(gs[2, 0])
    time_indices = [len(t_hydraulic)//4, len(t_hydraulic)//2, 
                    3*len(t_hydraulic)//4, -1]
    colors = ['blue', 'green', 'orange', 'red']
    labels = ['T/4', 'T/2', '3T/4', 'T']
    
    for idx, color, label in zip(time_indices, colors, labels):
        ax4.plot(x, h[idx, :], color=color, linewidth=2, 
                label=f'{label} ({t_hydraulic[idx]:.1f}h)')
    
    ax4.set_xlabel('河道距离 (m)', fontsize=11)
    ax4.set_ylabel('水深 (m)', fontsize=10)
    ax4.set_title('【水动力模拟】水深沿程分布', fontsize=12, fontweight='bold')
    ax4.legend(fontsize=9)
    ax4.grid(True, alpha=0.3)
    
    # 图5：水深时空分布
    ax5 = fig.add_subplot(gs[2, 1])
    # 降采样
    sample_t = max(1, h.shape[0] // 200)
    sample_x = max(1, h.shape[1] // 50)
    
    im = ax5.contourf(x[::sample_x], t_hydraulic[::sample_t], 
                     h[::sample_t, ::sample_x], 
                     levels=20, cmap='Blues')
    plt.colorbar(im, ax=ax5, label='水深 (m)')
    ax5.set_xlabel('河道距离 (m)', fontsize=11)
    ax5.set_ylabel('时间 (小时)', fontsize=10)
    ax5.set_title('【水动力模拟】水深时空分布', fontsize=12, fontweight='bold')
    
    plt.savefig(f'{output_dir}/coupling_simulation.png', dpi=300, bbox_inches='tight')
    print(f"   图表已保存: {output_dir}/coupling_simulation.png")
    plt.close()
    
    print(f"\n图表已保存到 {output_dir}/ 目录")
    print("="*70 + "\n")


if __name__ == '__main__':
    run_coupled_simulation()
