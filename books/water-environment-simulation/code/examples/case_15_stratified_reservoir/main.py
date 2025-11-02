"""
案例15：水库温度分层与水质模拟
Stratified Reservoir Temperature and Water Quality Simulation
"""

import numpy as np
import matplotlib.pyplot as plt
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from models.stratified_reservoir import (StratifiedReservoir1D, 
                                          calculate_buoyancy_frequency,
                                          estimate_mixing_depth)

plt.switch_backend('Agg')
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def main():
    print("=" * 70)
    print("案例15：水库温度分层与水质模拟")
    print("=" * 70)
    
    # 初始化模型
    H = 80  # 水深80m
    nz = 41  # 41个节点
    
    # 初始温度：线性分布
    z = np.linspace(0, H, nz)
    T_init = 15 + 10 * np.exp(-z/20)  # 表层25°C，底层15°C
    DO_init = 8 * np.ones(nz)  # 初始均匀8 mg/L
    
    model = StratifiedReservoir1D(H, nz, T_init, DO_init)
    
    # 设置强分层（夏季）
    model.set_vertical_diffusivity(Kz=1e-5)
    
    # 任务1：温度分层演变
    print("\n" + "=" * 70)
    print("任务1：温度分层演变（90天）")
    print("=" * 70)
    
    t_sim = np.linspace(0, 90, 100)
    t_out, T_field = model.solve_temperature_1d(t_sim, T_surface=28)
    
    # 温跃层
    z_thermo, dT_dz = model.calculate_thermocline_depth()
    
    # 任务2：DO分布
    print("\n" + "=" * 70)
    print("任务2：溶解氧分布")
    print("=" * 70)
    
    t_out, DO_field = model.solve_do_1d(t_sim)
    
    # 缺氧评估
    anoxic_depth, fraction = model.assess_anoxia_risk(DO_threshold=2.0)
    
    # 混合层深度
    h_mix = estimate_mixing_depth(model.T, model.z, dT_threshold=0.5)
    
    # 绘图
    print("\n生成图表...")
    
    # 图1：温度和DO剖面
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6), sharey=True)
    
    # 温度剖面
    ax1.plot(model.T, model.z, 'r-', linewidth=2.5, label='Final Temperature')
    ax1.plot(T_init, model.z, 'b--', linewidth=2, label='Initial Temperature')
    if z_thermo:
        ax1.axhline(y=z_thermo, color='g', linestyle=':', linewidth=2, label=f'Thermocline ({z_thermo:.1f} m)')
    ax1.set_xlabel('Temperature (°C)', fontsize=12)
    ax1.set_ylabel('Depth (m)', fontsize=12)
    ax1.set_title('Temperature Profile', fontsize=13, fontweight='bold')
    ax1.invert_yaxis()
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    # DO剖面
    ax2.plot(model.DO, model.z, 'b-', linewidth=2.5, label='Dissolved Oxygen')
    ax2.axvline(x=2, color='r', linestyle='--', linewidth=2, label='Anoxia Threshold (2 mg/L)')
    if anoxic_depth:
        ax2.axhline(y=anoxic_depth, color='orange', linestyle=':', linewidth=2, 
                    label=f'Anoxic Zone ({anoxic_depth:.1f} m)')
    ax2.set_xlabel('DO (mg/L)', fontsize=12)
    ax2.set_title('DO Profile', fontsize=13, fontweight='bold')
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('profiles.png', dpi=150, bbox_inches='tight')
    print("  ✓ 已保存: profiles.png")
    plt.close()
    
    # 图2：时空演变
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10))
    
    # 温度时空图
    extent = [0, 90, H, 0]
    im1 = ax1.contourf(t_out, model.z, T_field, levels=20, cmap='hot')
    ax1.set_xlabel('Time (d)', fontsize=12)
    ax1.set_ylabel('Depth (m)', fontsize=12)
    ax1.set_title('Temperature Evolution', fontsize=13, fontweight='bold')
    plt.colorbar(im1, ax=ax1, label='Temperature (°C)')
    
    # DO时空图
    im2 = ax2.contourf(t_out, model.z, DO_field, levels=20, cmap='Blues')
    ax2.set_xlabel('Time (d)', fontsize=12)
    ax2.set_ylabel('Depth (m)', fontsize=12)
    ax2.set_title('DO Evolution', fontsize=13, fontweight='bold')
    plt.colorbar(im2, ax=ax2, label='DO (mg/L)')
    
    plt.tight_layout()
    plt.savefig('evolution.png', dpi=150, bbox_inches='tight')
    print("  ✓ 已保存: evolution.png")
    plt.close()
    
    # 总结
    print("\n" + "=" * 70)
    print("案例15完成！")
    print("=" * 70)
    
    print(f"\n主要结论:")
    print(f"1. 温跃层深度: {z_thermo:.1f} m")
    print(f"2. 混合层深度: {h_mix:.1f} m")
    print(f"3. 底层DO: {model.DO[-1]:.2f} mg/L")
    if anoxic_depth:
        print(f"4. 缺氧层起始: {anoxic_depth:.1f} m, 占比{fraction*100:.1f}%")
        print(f"   ⚠️  存在底层缺氧风险！")
    else:
        print(f"4. ✓ 无缺氧风险")
    
    print(f"\n工程建议:")
    print(f"  1. 取水口应设在{h_mix:.0f}m以上（混合层内）")
    print(f"  2. 考虑曝气改善底层DO")
    print(f"  3. 监测温跃层深度变化")
    print(f"  4. 秋季翻转期加强监测")


if __name__ == '__main__':
    main()
