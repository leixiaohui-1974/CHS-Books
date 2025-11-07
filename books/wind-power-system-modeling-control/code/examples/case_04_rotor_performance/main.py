"""
案例4: 风轮功率特性

本案例演示:
1. Cp-λ性能曲线优化
2. 最优叶尖速比确定
3. 风轮效率分析
4. 风速-功率特性

工程背景: 风力机性能评估与优化
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from models.aerodynamics import BEMSolver, AirfoilData, design_blade_twist, design_blade_chord
from models.wind_resource import WeibullDistribution

plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False


def create_baseline_rotor():
    """创建基准风轮"""
    R = 40  # m
    r_hub = 1.5
    B = 3
    airfoil = AirfoilData.create_naca0012()
    r_array = np.linspace(r_hub, R, 15)
    chord = design_blade_chord(r_array, R, B)
    twist = design_blade_twist(r_array, R, lambda_design=8.0)
    
    return BEMSolver(R, r_hub, B, airfoil, chord, twist)


def demo_cp_lambda_optimization():
    """演示1: Cp-λ曲线优化"""
    print("=" * 60)
    print("演示1: 风轮Cp-λ性能曲线")
    print("=" * 60)
    
    bem = create_baseline_rotor()
    v_wind = 10.0
    TSR_range = np.linspace(2, 14, 30)
    omega_range = TSR_range * v_wind / bem.R
    
    Cp_vals = []
    power_vals = []
    
    print(f"\n计算Cp-λ曲线... (风速: {v_wind} m/s)")
    for omega in omega_range:
        result = bem.solve_rotor(v_wind, omega, n_elements=15)
        Cp_vals.append(result['Cp'])
        power_vals.append(result['power'] / 1000)  # kW
    
    idx_max = np.argmax(Cp_vals)
    lambda_opt = TSR_range[idx_max]
    Cp_max = Cp_vals[idx_max]
    P_max = power_vals[idx_max]
    
    print(f"\n最优工作点:")
    print(f"  λ_opt = {lambda_opt:.2f}")
    print(f"  Cp_max = {Cp_max:.4f}")
    print(f"  P_max = {P_max:.1f} kW")
    print(f"  Betz效率 = {Cp_max/0.593*100:.1f}%")
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    ax = axes[0]
    ax.plot(TSR_range, Cp_vals, 'b-', linewidth=2, marker='o', markersize=4)
    ax.plot(lambda_opt, Cp_max, 'r*', markersize=15, label=f'最优点')
    ax.axhline(0.593, color='g', linestyle='--', label='Betz极限')
    ax.set_xlabel('叶尖速比 λ', fontsize=12)
    ax.set_ylabel('功率系数 Cp', fontsize=12)
    ax.set_title('Cp-λ曲线', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    ax = axes[1]
    ax.plot(TSR_range, power_vals, 'r-', linewidth=2)
    ax.plot(lambda_opt, P_max, 'b*', markersize=15)
    ax.set_xlabel('叶尖速比 λ', fontsize=12)
    ax.set_ylabel('功率 (kW)', fontsize=12)
    ax.set_title('功率-λ曲线', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('case04_cp_lambda_curve.png', dpi=300, bbox_inches='tight')
    print("\n图表已保存: case04_cp_lambda_curve.png")
    
    return lambda_opt


def demo_power_curve(lambda_opt):
    """演示2: 风速-功率曲线"""
    print("\n" + "=" * 60)
    print("演示2: 风力机功率曲线")
    print("=" * 60)
    
    bem = create_baseline_rotor()
    v_range = np.linspace(3, 25, 50)
    
    # 额定参数
    v_rated = 12.0  # m/s
    P_rated = 2000  # kW
    omega_rated = lambda_opt * v_rated / bem.R
    
    power_vals = []
    omega_vals = []
    
    print(f"\n额定参数:")
    print(f"  额定风速: {v_rated} m/s")
    print(f"  额定功率: {P_rated} kW")
    print(f"  最优λ: {lambda_opt:.2f}")
    
    print("\n计算功率曲线...")
    for v in v_range:
        if v < 3:  # 切入风速以下
            P = 0
            omega = 0
        elif v < v_rated:  # 最优λ运行
            omega = lambda_opt * v / bem.R
            result = bem.solve_rotor(v, omega, n_elements=12)
            P = result['power'] / 1000
        else:  # 额定功率运行
            P = P_rated
            omega = omega_rated
        
        power_vals.append(P)
        omega_vals.append(omega * 60 / (2*np.pi))  # RPM
    
    print(f"\n关键工况:")
    for v_test in [5, 8, 12, 15, 20]:
        idx = np.argmin(np.abs(v_range - v_test))
        print(f"  v={v_test}m/s: P={power_vals[idx]:.0f}kW, n={omega_vals[idx]:.1f}RPM")
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    ax = axes[0]
    ax.plot(v_range, power_vals, 'b-', linewidth=2)
    ax.axvline(v_rated, color='r', linestyle='--', label=f'额定风速({v_rated}m/s)')
    ax.axhline(P_rated, color='g', linestyle='--', label=f'额定功率({P_rated}kW)')
    ax.set_xlabel('风速 (m/s)', fontsize=12)
    ax.set_ylabel('功率 (kW)', fontsize=12)
    ax.set_title('风力机功率曲线', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    ax = axes[1]
    ax.plot(v_range, omega_vals, 'r-', linewidth=2)
    ax.set_xlabel('风速 (m/s)', fontsize=12)
    ax.set_ylabel('转速 (RPM)', fontsize=12)
    ax.set_title('转速曲线', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('case04_power_curve.png', dpi=300, bbox_inches='tight')
    print("\n图表已保存: case04_power_curve.png")


def demo_annual_energy():
    """演示3: 年发电量分析"""
    print("\n" + "=" * 60)
    print("演示3: 年发电量估算")
    print("=" * 60)
    
    bem = create_baseline_rotor()
    weibull = WeibullDistribution(k=2.0, c=8.0)
    
    # 风速bins
    v_bins = np.arange(3, 26, 1)
    P_bins = []
    hours_bins = []
    
    print(f"\n场址风资源:")
    print(f"  Weibull参数: k={weibull.k}, c={weibull.c}")
    print(f"  平均风速: {weibull.mean_speed:.2f} m/s")
    
    # 计算每个风速bin的功率和小时数
    for v in v_bins:
        # 功率
        if v < 12:
            omega = 8.0 * v / bem.R  # 最优λ=8
            result = bem.solve_rotor(v, omega, n_elements=12)
            P = result['power'] / 1000
        else:
            P = 2000  # 额定功率
        
        # 年小时数
        prob = weibull.pdf(np.array([v]))[0]
        hours = prob * 8760 * 1  # 1m/s宽度的bin
        
        P_bins.append(P)
        hours_bins.append(hours)
    
    # 年发电量
    E_annual = np.sum(np.array(P_bins) * np.array(hours_bins))
    
    # 容量因子
    CF = E_annual / (2000 * 8760) * 100
    
    print(f"\n发电量统计:")
    print(f"  年发电量: {E_annual:.0f} MWh")
    print(f"  容量因子: {CF:.1f}%")
    print(f"  等效满发小时: {E_annual/2000:.0f} h")
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    ax = axes[0]
    ax.bar(v_bins, hours_bins, width=0.8, alpha=0.7, label='年小时数')
    ax.set_xlabel('风速 (m/s)', fontsize=12)
    ax.set_ylabel('年小时数 (h)', fontsize=12)
    ax.set_title('风速分布', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    ax = axes[1]
    energy_bins = np.array(P_bins) * np.array(hours_bins) / 1000  # MWh
    ax.bar(v_bins, energy_bins, width=0.8, alpha=0.7, color='green', label='发电量贡献')
    ax.set_xlabel('风速 (m/s)', fontsize=12)
    ax.set_ylabel('发电量贡献 (MWh)', fontsize=12)
    ax.set_title('各风速段发电量贡献', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('case04_annual_energy.png', dpi=300, bbox_inches='tight')
    print("\n图表已保存: case04_annual_energy.png")


def main():
    print("\n" + "=" * 60)
    print("案例4: 风轮功率特性")
    print("=" * 60)
    
    lambda_opt = demo_cp_lambda_optimization()
    demo_power_curve(lambda_opt)
    demo_annual_energy()
    
    print("\n" + "=" * 60)
    print("案例4 运行完成！")
    print("=" * 60)
    print("\n生成的图表:")
    print("  1. case04_cp_lambda_curve.png")
    print("  2. case04_power_curve.png")
    print("  3. case04_annual_energy.png")
    
    plt.show()


if __name__ == "__main__":
    main()
