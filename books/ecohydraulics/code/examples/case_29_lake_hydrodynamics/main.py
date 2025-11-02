#!/usr/bin/env python3
"""案例29：湖泊风生流与水质模拟"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from models.lake_wetland import LakeHydrodynamics, simulate_lake_wind_event

rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

def main():
    print("=" * 70)
    print("案例29：湖泊风生流与水质模拟")
    print("=" * 70)
    
    # 湖泊参数（以某大型湖泊为例）
    lake = LakeHydrodynamics(
        lake_area=100.0,  # 100 km²
        average_depth=5.0,  # 5 m
        fetch_length=8000.0  # 8 km
    )
    
    print(f"\n湖泊基本参数:")
    print(f"  面积: {lake.A / 1e6:.1f} km²")
    print(f"  平均水深: {lake.h:.1f} m")
    print(f"  风区长度: {lake.F / 1000:.1f} km")
    
    # 1. 风应力与表层流速分析
    wind_speeds = np.linspace(0, 15, 50)
    wind_stresses = [lake.wind_stress(U) for U in wind_speeds]
    surface_velocities = [lake.surface_current_velocity(U) for U in wind_speeds]
    wind_setups = [lake.wind_setup(U) for U in wind_speeds]
    
    print(f"\n典型风速下的水动力响应（10 m/s风速）:")
    U_typical = 10.0
    tau = lake.wind_stress(U_typical)
    u_surf = lake.surface_current_velocity(U_typical)
    setup = lake.wind_setup(U_typical)
    
    print(f"  风应力: {tau:.4f} Pa")
    print(f"  表层流速: {u_surf:.3f} m/s")
    print(f"  风壅水高: {setup:.3f} m")
    
    # 2. 风浪参数
    wave_params = lake.wave_parameters(U_typical)
    print(f"\n风浪参数:")
    print(f"  有效波高: {wave_params['significant_wave_height']:.2f} m")
    print(f"  平均周期: {wave_params['mean_period']:.2f} s")
    print(f"  波长: {wave_params['wavelength']:.1f} m")
    print(f"  波陡: {wave_params['wave_steepness']:.4f}")
    
    # 3. 温度分层分析
    stratification = lake.thermal_stratification(
        surface_temp=28.0,  # 夏季表层温度
        bottom_temp=18.0    # 底层温度
    )
    
    print(f"\n温度分层:")
    print(f"  温跃层深度: {stratification['thermocline_depth']:.2f} m")
    print(f"  表层密度: {stratification['surface_density']:.2f} kg/m³")
    print(f"  底层密度: {stratification['bottom_density']:.2f} kg/m³")
    print(f"  理查森数: {stratification['richardson_number']:.1f}")
    print(f"  分层状态: {stratification['stratification_status']}")
    
    # 4. 藻类水华风险评估
    bloom_risk = lake.algae_bloom_risk(
        temperature=28.0,
        total_phosphorus=0.08,  # mg/L
        total_nitrogen=1.2,     # mg/L
        light_extinction=0.5    # 1/m
    )
    
    print(f"\n藻类水华风险评估:")
    print(f"  温度因子: {bloom_risk['temperature_factor']:.2f}")
    print(f"  营养盐因子: {bloom_risk['nutrient_factor']:.2f}")
    print(f"  光照因子: {bloom_risk['light_factor']:.2f}")
    print(f"  真光层深度: {bloom_risk['euphotic_depth']:.2f} m")
    print(f"  综合风险指数: {bloom_risk['risk_index']:.2f}")
    print(f"  风险等级: {bloom_risk['risk_level']}")
    
    # 5. 风事件模拟
    duration = 24  # 24小时
    wind_event = 5 + 5 * np.sin(np.linspace(0, 2*np.pi, duration))  # 正弦变化的风速
    simulation = simulate_lake_wind_event(lake, wind_event, duration)
    
    # 可视化
    fig = plt.figure(figsize=(15, 10))
    
    # 1. 风速-风应力-表层流速关系
    ax1 = plt.subplot(2, 3, 1)
    ax1.plot(wind_speeds, wind_stresses, 'b-', linewidth=2, label='风应力')
    ax1.set_xlabel('风速 (m/s)', fontsize=10)
    ax1.set_ylabel('风应力 (Pa)', fontsize=10, color='b')
    ax1.tick_params(axis='y', labelcolor='b')
    ax1.grid(True, alpha=0.3)
    
    ax1_twin = ax1.twinx()
    ax1_twin.plot(wind_speeds, surface_velocities, 'r-', linewidth=2, label='表层流速')
    ax1_twin.set_ylabel('表层流速 (m/s)', fontsize=10, color='r')
    ax1_twin.tick_params(axis='y', labelcolor='r')
    ax1.set_title('风速-风应力-表层流速关系', fontsize=12, fontweight='bold')
    
    # 2. 风壅水高
    ax2 = plt.subplot(2, 3, 2)
    ax2.plot(wind_speeds, wind_setups, 'g-', linewidth=2)
    ax2.set_xlabel('风速 (m/s)', fontsize=10)
    ax2.set_ylabel('风壅水高 (m)', fontsize=10)
    ax2.set_title('风壅水效应', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.axhline(0.1, color='r', linestyle='--', alpha=0.5, label='显著影响阈值')
    ax2.legend()
    
    # 3. 风浪参数随风速变化
    ax3 = plt.subplot(2, 3, 3)
    wave_heights = []
    wave_periods = []
    for U in wind_speeds:
        params = lake.wave_parameters(U)
        wave_heights.append(params['significant_wave_height'])
        wave_periods.append(params['mean_period'])
    
    ax3.plot(wind_speeds, wave_heights, 'b-', linewidth=2, label='有效波高')
    ax3.set_xlabel('风速 (m/s)', fontsize=10)
    ax3.set_ylabel('有效波高 (m)', fontsize=10, color='b')
    ax3.tick_params(axis='y', labelcolor='b')
    ax3.grid(True, alpha=0.3)
    
    ax3_twin = ax3.twinx()
    ax3_twin.plot(wind_speeds, wave_periods, 'r-', linewidth=2, label='平均周期')
    ax3_twin.set_ylabel('平均周期 (s)', fontsize=10, color='r')
    ax3_twin.tick_params(axis='y', labelcolor='r')
    ax3.set_title('风浪参数', fontsize=12, fontweight='bold')
    
    # 4. 温度分层剖面
    ax4 = plt.subplot(2, 3, 4)
    depths = np.linspace(0, lake.h, 50)
    temps = []
    tc_depth = stratification['thermocline_depth']
    T_surf = 28.0
    T_bot = 18.0
    
    for z in depths:
        if z < tc_depth:
            T = T_surf
        elif z < tc_depth + 1.0:
            T = T_surf - (T_surf - T_bot) * (z - tc_depth) / 1.0
        else:
            T = T_bot
        temps.append(T)
    
    ax4.plot(temps, depths, 'b-', linewidth=2)
    ax4.axhline(tc_depth, color='r', linestyle='--', linewidth=2, label='温跃层')
    ax4.set_xlabel('温度 (°C)', fontsize=10)
    ax4.set_ylabel('深度 (m)', fontsize=10)
    ax4.set_title('温度垂向分布', fontsize=12, fontweight='bold')
    ax4.invert_yaxis()
    ax4.grid(True, alpha=0.3)
    ax4.legend()
    
    # 5. 风事件模拟时间序列
    ax5 = plt.subplot(2, 3, 5)
    ax5.plot(simulation['time'], simulation['wind_speed'], 'k-', 
            linewidth=2, label='风速')
    ax5.set_xlabel('时间 (h)', fontsize=10)
    ax5.set_ylabel('风速 (m/s)', fontsize=10)
    ax5.set_title('风事件模拟', fontsize=12, fontweight='bold')
    ax5.grid(True, alpha=0.3)
    ax5.legend()
    
    ax5_twin = ax5.twinx()
    ax5_twin.plot(simulation['time'], simulation['surface_velocity'], 'b-',
                 linewidth=2, alpha=0.7, label='表层流速')
    ax5_twin.set_ylabel('表层流速 (m/s)', fontsize=10, color='b')
    ax5_twin.tick_params(axis='y', labelcolor='b')
    
    # 6. 藻华风险因子雷达图
    ax6 = plt.subplot(2, 3, 6, projection='polar')
    categories = ['温度', '营养盐', '光照']
    values = [
        bloom_risk['temperature_factor'],
        bloom_risk['nutrient_factor'],
        bloom_risk['light_factor']
    ]
    
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    values += values[:1]
    angles += angles[:1]
    
    ax6.plot(angles, values, 'o-', linewidth=2, color='red', label='当前状态')
    ax6.fill(angles, values, alpha=0.25, color='red')
    ax6.set_xticks(angles[:-1])
    ax6.set_xticklabels(categories, fontsize=10)
    ax6.set_ylim(0, 1)
    ax6.set_title('藻华风险因子', fontsize=12, fontweight='bold', pad=20)
    ax6.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
    ax6.grid(True)
    
    plt.tight_layout()
    plt.savefig(Path(__file__).parent / 'lake_hydrodynamics_analysis.png', dpi=300)
    print(f"\n图表已保存: lake_hydrodynamics_analysis.png")
    print("=" * 70)

if __name__ == '__main__':
    main()
