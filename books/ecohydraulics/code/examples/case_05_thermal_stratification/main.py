"""
案例5：水温分层与溶解氧分布模拟
=============================

本案例演示水库热分层和DO动力学的基本概念和计算方法。
由于时间限制，采用简化模型。实际工程应用需要更复杂的数值模型。

作者: CHS-Books 生态水力学课程组
日期: 2025-11-02
"""

import sys
import os
import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from code.models.thermal import (
    create_summer_stratification,
    create_winter_stratification,
    DissolvedOxygenModel,
    ReservoirStratificationAnalyzer
)

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def main():
    print("\n" + "="*80)
    print("案例5：水温分层与溶解氧分布模拟".center(80))
    print("="*80)
    
    depth = 30.0  # 水库水深30m
    
    # 夏季分层
    print("\n夏季分层模拟...")
    summer_model = create_summer_stratification(depth, n_layers=30)
    do_summer = DissolvedOxygenModel(depth, n_layers=30)
    do_summer.set_temperature(summer_model.temperature)
    do_summer.simulate_DO_profile(time_days=30, wind_speed=3.0)
    
    layers_summer = ReservoirStratificationAnalyzer.classify_layers(summer_model, do_summer)
    habitat_summer = ReservoirStratificationAnalyzer.fish_habitat_assessment(do_summer, 4.0)
    
    print(f"温跃层深度: {layers_summer['thermocline']['depth']:.1f} m")
    print(f"表温层平均温度: {layers_summer['epilimnion']['mean_temp']:.1f}°C")
    print(f"底温层平均温度: {layers_summer['hypolimnion']['mean_temp']:.1f}°C")
    print(f"鱼类可利用水层: {habitat_summer['suitable_thickness']:.1f} m ({habitat_summer['suitable_ratio']:.1%})")
    print(f"栖息地状况: {habitat_summer['status']}")
    
    # 可视化
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
    
    # 温度剖面
    ax1.plot(summer_model.temperature, -summer_model.z, 'r-', linewidth=2, label='Summer')
    ax1.axhline(-layers_summer['thermocline']['depth'], color='gray', linestyle='--', label='Thermocline')
    ax1.set_xlabel('Temperature (°C)', fontsize=11)
    ax1.set_ylabel('Depth (m)', fontsize=11)
    ax1.set_title('Temperature Profile', fontsize=12, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # DO剖面
    ax2.plot(do_summer.DO, -do_summer.z, 'b-', linewidth=2)
    ax2.axvline(4.0, color='r', linestyle='--', label='Min requirement')
    ax2.set_xlabel('DO (mg/L)', fontsize=11)
    ax2.set_ylabel('Depth (m)', fontsize=11)
    ax2.set_title('DO Profile', fontsize=12, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 密度剖面
    density = [summer_model.water_density(T) for T in summer_model.temperature]
    ax3.plot(density, -summer_model.z, 'g-', linewidth=2)
    ax3.set_xlabel('Density (kg/m³)', fontsize=11)
    ax3.set_ylabel('Depth (m)', fontsize=11)
    ax3.set_title('Density Profile', fontsize=12, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    
    # 温度梯度
    dT_dz = np.gradient(summer_model.temperature, summer_model.dz)
    ax4.plot(dT_dz, -summer_model.z, 'orange', linewidth=2)
    ax4.set_xlabel('Temperature Gradient (°C/m)', fontsize=11)
    ax4.set_ylabel('Depth (m)', fontsize=11)
    ax4.set_title('Temperature Gradient', fontsize=12, fontweight='bold')
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('stratification_profiles.png', dpi=300, bbox_inches='tight')
    print("\n✓ 已保存: stratification_profiles.png")
    plt.close()
    
    print("\n" + "="*80)
    print("模拟完成！".center(80))
    print("="*80)

if __name__ == "__main__":
    main()
