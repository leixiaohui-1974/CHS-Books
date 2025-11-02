#!/usr/bin/env python3
"""案例32：湖泊分层与内波动力学"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from models.lake_wetland import LakeStratification

rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

def main():
    print("=" * 70)
    print("案例32：湖泊分层与内波动力学分析")
    print("=" * 70)
    
    # 湖泊参数（深水湖泊）
    lake = LakeStratification(
        lake_depth=50.0,  # 50m深
        surface_area=200.0  # 200 km²
    )
    
    print(f"\n湖泊基本参数:")
    print(f"  最大水深: {lake.h:.1f} m")
    print(f"  表面积: {lake.A / 1e6:.1f} km²")
    
    # 1. 温跃层深度（不同季节）
    periods = ['spring', 'summer', 'autumn', 'winter']
    period_names = ['春季', '夏季', '秋季', '冬季']
    thermocline_depths = {}
    
    print(f"\n不同季节温跃层深度:")
    for period, name in zip(periods, period_names):
        depth = lake.thermocline_depth(period)
        thermocline_depths[name] = depth
        print(f"  {name}: {depth:.1f} m")
    
    # 2. 布伦特-韦萨拉频率
    density_gradients = np.linspace(0.1, 2.0, 20)
    N_values = [lake.brunt_vaisala_frequency(dg) for dg in density_gradients]
    
    typical_dg = 0.5  # kg/m³/m
    N_typical = lake.brunt_vaisala_frequency(typical_dg)
    print(f"\n布伦特-韦萨拉频率（密度梯度{typical_dg} kg/m³/m）:")
    print(f"  N = {N_typical:.4f} 1/s")
    print(f"  周期 = {2 * np.pi / N_typical:.1f} s")
    
    # 3. 内波波速
    h1 = 15.0  # 上层厚度
    h2 = 35.0  # 下层厚度
    delta_rho = 2.0  # 密度差 kg/m³
    
    c_internal = lake.internal_wave_speed(h1, h2, delta_rho)
    print(f"\n内波参数（两层模型）:")
    print(f"  上层厚度: {h1:.1f} m")
    print(f"  下层厚度: {h2:.1f} m")
    print(f"  密度差: {delta_rho:.1f} kg/m³")
    print(f"  内波波速: {c_internal:.3f} m/s")
    
    # 4. 内涌周期
    lake_length = 15.0  # km
    T_seiche = lake.internal_seiche_period(lake_length, c_internal)
    print(f"\n内涌特性:")
    print(f"  湖长: {lake_length:.1f} km")
    print(f"  内涌周期: {T_seiche:.1f} 小时")
    
    # 5. 破坏分层所需能量
    temp_diffs = np.linspace(5, 20, 50)
    energies = [lake.mixing_energy_requirement(dt) for dt in temp_diffs]
    
    typical_dt = 10.0  # °C
    E_mixing = lake.mixing_energy_requirement(typical_dt)
    print(f"\n破坏分层所需能量（温差{typical_dt}°C）:")
    print(f"  {E_mixing / 1e6:.2f} MJ/m²")
    
    # 6. 底层缺氧风险
    surface_do = 8.0  # mg/L
    durations = [30, 60, 90, 120]
    
    print(f"\n底层溶解氧预测（表层DO={surface_do} mg/L）:")
    hypoxia_results = []
    for days in durations:
        result = lake.hypoxia_risk_assessment(surface_do, days)
        hypoxia_results.append(result)
        print(f"  分层{days}天: 底层DO={result['bottom_do']:.2f} mg/L, {result['risk_level']}")
    
    # 可视化
    fig = plt.figure(figsize=(15, 10))
    
    # 1. 温度分层剖面（四季对比）
    ax1 = plt.subplot(2, 3, 1)
    depths = np.linspace(0, lake.h, 100)
    
    # 模拟不同季节的温度剖面
    for period, name, color in zip(periods, period_names, ['green', 'red', 'orange', 'blue']):
        tc_depth = thermocline_depths[name]
        
        if period == 'summer':
            T_surf, T_bot = 25, 8
        elif period == 'spring':
            T_surf, T_bot = 15, 8
        elif period == 'autumn':
            T_surf, T_bot = 18, 12
        else:  # winter
            T_surf, T_bot = 4, 4
        
        temps = []
        for z in depths:
            if tc_depth == 0:
                T = T_surf
            elif z < tc_depth:
                T = T_surf
            elif z < tc_depth + 2:
                T = T_surf - (T_surf - T_bot) * (z - tc_depth) / 2
            else:
                T = T_bot
            temps.append(T)
        
        ax1.plot(temps, depths, linewidth=2, label=name, color=color)
    
    ax1.set_xlabel('温度 (°C)', fontsize=10)
    ax1.set_ylabel('深度 (m)', fontsize=10)
    ax1.set_title('四季温度分层剖面', fontsize=12, fontweight='bold')
    ax1.invert_yaxis()
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. 布伦特-韦萨拉频率
    ax2 = plt.subplot(2, 3, 2)
    ax2.plot(density_gradients, N_values, 'b-', linewidth=2)
    ax2.axvline(typical_dg, color='r', linestyle='--', linewidth=2, 
               alpha=0.7, label=f'典型值 {typical_dg} kg/m³/m')
    ax2.set_xlabel('密度梯度 (kg/m³/m)', fontsize=10)
    ax2.set_ylabel('N (1/s)', fontsize=10)
    ax2.set_title('布伦特-韦萨拉频率', fontsize=12, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. 内波波速（不同层厚比）
    ax3 = plt.subplot(2, 3, 3)
    h_ratios = np.linspace(0.1, 0.9, 50)
    wave_speeds = []
    
    for ratio in h_ratios:
        h1_var = lake.h * ratio
        h2_var = lake.h * (1 - ratio)
        c = lake.internal_wave_speed(h1_var, h2_var, delta_rho)
        wave_speeds.append(c)
    
    ax3.plot(h_ratios, wave_speeds, 'g-', linewidth=2)
    ax3.axvline(h1 / lake.h, color='r', linestyle='--', linewidth=2,
               alpha=0.7, label=f'实际层厚比')
    ax3.set_xlabel('上层厚度/总深度', fontsize=10)
    ax3.set_ylabel('内波波速 (m/s)', fontsize=10)
    ax3.set_title('内波波速随层厚比变化', fontsize=12, fontweight='bold')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. 破坏分层所需能量
    ax4 = plt.subplot(2, 3, 4)
    ax4.plot(temp_diffs, np.array(energies) / 1e6, 'r-', linewidth=2)
    ax4.axvline(typical_dt, color='g', linestyle='--', linewidth=2,
               alpha=0.7, label=f'典型温差 {typical_dt}°C')
    ax4.set_xlabel('表底温差 (°C)', fontsize=10)
    ax4.set_ylabel('所需能量 (MJ/m²)', fontsize=10)
    ax4.set_title('破坏分层所需能量', fontsize=12, fontweight='bold')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    # 5. 底层DO随分层时间变化
    ax5 = plt.subplot(2, 3, 5)
    strat_days = np.arange(0, 150, 1)
    bottom_dos = [surface_do - 0.1 * day for day in strat_days]
    bottom_dos = [max(do, 0) for do in bottom_dos]
    
    ax5.plot(strat_days, bottom_dos, 'b-', linewidth=2)
    ax5.axhline(4, color='orange', linestyle='--', linewidth=2, label='轻度缺氧阈值')
    ax5.axhline(2, color='red', linestyle='--', linewidth=2, label='严重缺氧阈值')
    ax5.fill_between(strat_days, 0, 2, color='red', alpha=0.1)
    ax5.fill_between(strat_days, 2, 4, color='orange', alpha=0.1)
    ax5.fill_between(strat_days, 4, 10, color='green', alpha=0.1)
    
    ax5.set_xlabel('分层持续时间 (天)', fontsize=10)
    ax5.set_ylabel('底层DO (mg/L)', fontsize=10)
    ax5.set_title('底层溶解氧变化', fontsize=12, fontweight='bold')
    ax5.legend()
    ax5.grid(True, alpha=0.3)
    ax5.set_xlim([0, 150])
    ax5.set_ylim([0, 10])
    
    # 6. 内波示意图
    ax6 = plt.subplot(2, 3, 6)
    x = np.linspace(0, lake_length * 1000, 200)
    t = 0  # 时刻
    
    # 内波界面起伏
    amplitude = 5.0  # m
    wavelength = lake_length * 1000  # m
    interface = h1 + amplitude * np.sin(2 * np.pi * x / wavelength)
    
    # 绘制上层
    ax6.fill_between(x / 1000, 0, interface, color='lightblue', alpha=0.5, label='上层(暖水)')
    # 绘制下层
    ax6.fill_between(x / 1000, interface, lake.h, color='darkblue', alpha=0.5, label='下层(冷水)')
    # 界面
    ax6.plot(x / 1000, interface, 'r-', linewidth=2, label='温跃层界面')
    
    ax6.set_xlabel('距离 (km)', fontsize=10)
    ax6.set_ylabel('深度 (m)', fontsize=10)
    ax6.set_title('内波界面起伏示意图', fontsize=12, fontweight='bold')
    ax6.invert_yaxis()
    ax6.legend()
    ax6.grid(True, alpha=0.3)
    
    # 标注振幅
    ax6.annotate('', xy=(lake_length * 500 / 1000, h1),
                xytext=(lake_length * 500 / 1000, h1 + amplitude),
                arrowprops=dict(arrowstyle='<->', color='red', lw=2))
    ax6.text(lake_length * 500 / 1000 + 1, h1 + amplitude / 2,
            f'振幅\n{amplitude}m', fontsize=9, ha='left',
            bbox=dict(boxstyle='round', facecolor='wheat'))
    
    plt.tight_layout()
    plt.savefig(Path(__file__).parent / 'lake_stratification_analysis.png', dpi=300)
    print(f"\n图表已保存: lake_stratification_analysis.png")
    print("=" * 70)

if __name__ == '__main__':
    main()
