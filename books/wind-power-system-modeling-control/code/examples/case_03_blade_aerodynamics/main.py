"""
案例3: 叶片气动力计算

本案例演示:
1. 翼型气动特性 (Cl-α, Cd-α曲线)
2. 叶素动量理论 (BEM)
3. 诱导因子计算
4. 风轮性能曲线 (Cp-λ)

工程背景: 风力机气动设计基础
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

# 添加models路径
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from models.aerodynamics import (
    AirfoilData,
    BEMSolver,
    SimpleRotor,
    design_blade_twist,
    design_blade_chord
)

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False


def demo_airfoil_characteristics():
    """演示1: 翼型气动特性"""
    print("=" * 60)
    print("演示1: 翼型气动特性 (Cl-α, Cd-α曲线)")
    print("=" * 60)
    
    # 创建翼型数据
    airfoil_flat = AirfoilData.create_flat_plate()
    airfoil_naca = AirfoilData.create_naca0012()
    
    # 打印信息
    for airfoil in [airfoil_flat, airfoil_naca]:
        status = airfoil.get_status()
        print(f"\n{status['name']}:")
        print(f"  攻角范围: {status['alpha_range'][0]:.1f}° ~ {status['alpha_range'][1]:.1f}°")
        print(f"  最大Cl: {status['Cl_max']:.3f}")
        print(f"  最小Cd: {status['Cd_min']:.4f}")
    
    # 可视化
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # 图1: Cl-α曲线
    ax = axes[0]
    ax.plot(airfoil_flat.alpha, airfoil_flat.Cl, 'b-', 
            linewidth=2, label='平板翼型')
    ax.plot(airfoil_naca.alpha, airfoil_naca.Cl, 'r--', 
            linewidth=2, label='NACA0012')
    ax.axhline(0, color='gray', linestyle='-', linewidth=0.5)
    ax.axvline(0, color='gray', linestyle='-', linewidth=0.5)
    ax.set_xlabel('攻角 α (度)', fontsize=12)
    ax.set_ylabel('升力系数 Cl', fontsize=12)
    ax.set_title('升力系数曲线', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 图2: Cd-α曲线
    ax = axes[1]
    ax.plot(airfoil_flat.alpha, airfoil_flat.Cd, 'b-', 
            linewidth=2, label='平板翼型')
    ax.plot(airfoil_naca.alpha, airfoil_naca.Cd, 'r--', 
            linewidth=2, label='NACA0012')
    ax.set_xlabel('攻角 α (度)', fontsize=12)
    ax.set_ylabel('阻力系数 Cd', fontsize=12)
    ax.set_title('阻力系数曲线', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('case03_airfoil_characteristics.png', dpi=300, bbox_inches='tight')
    print("\n图表已保存: case03_airfoil_characteristics.png")


def demo_blade_design():
    """演示2: 叶片几何设计"""
    print("\n" + "=" * 60)
    print("演示2: 叶片弦长和扭角分布")
    print("=" * 60)
    
    # 风轮参数
    R = 40  # 风轮半径 (m)
    r_hub = 1.5  # 轮毂半径 (m)
    B = 3  # 叶片数
    
    # 径向位置
    r_array = np.linspace(r_hub, R, 20)
    
    # 设计弦长和扭角
    chord = design_blade_chord(r_array, R, B)
    twist = design_blade_twist(r_array, R, lambda_design=8.0)
    
    print(f"\n风轮参数:")
    print(f"  半径: {R} m")
    print(f"  轮毂: {r_hub} m")
    print(f"  叶片数: {B}")
    print(f"  设计叶尖速比: 8.0")
    
    print(f"\n叶片几何（关键位置）:")
    for i, r in enumerate([r_array[5], r_array[10], r_array[15], r_array[-1]]):
        idx = np.argmin(np.abs(r_array - r))
        print(f"  r = {r:.1f}m: 弦长 = {chord[idx]:.3f}m, 扭角 = {twist[idx]:.2f}°")
    
    # 可视化
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # 图1: 弦长分布
    ax = axes[0]
    ax.plot(r_array, chord, 'b-', linewidth=2, marker='o', markersize=4)
    ax.set_xlabel('径向位置 r (m)', fontsize=12)
    ax.set_ylabel('弦长 c (m)', fontsize=12)
    ax.set_title('叶片弦长分布', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    # 图2: 扭角分布
    ax = axes[1]
    ax.plot(r_array, twist, 'r-', linewidth=2, marker='s', markersize=4)
    ax.set_xlabel('径向位置 r (m)', fontsize=12)
    ax.set_ylabel('扭角 β (度)', fontsize=12)
    ax.set_title('叶片扭角分布', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('case03_blade_design.png', dpi=300, bbox_inches='tight')
    print("\n图表已保存: case03_blade_design.png")
    
    return R, r_hub, B, r_array, chord, twist


def demo_bem_solver(R, r_hub, B, r_array, chord, twist):
    """演示3: BEM理论求解"""
    print("\n" + "=" * 60)
    print("演示3: BEM理论求解风轮性能")
    print("=" * 60)
    
    # 创建翼型
    airfoil = AirfoilData.create_naca0012()
    
    # 创建BEM求解器
    bem = BEMSolver(R, r_hub, B, airfoil, chord, twist)
    
    # 工况
    v_wind = 10.0  # m/s
    omega = 2.0  # rad/s (约19 RPM)
    
    print(f"\n工况:")
    print(f"  风速: {v_wind} m/s")
    print(f"  转速: {omega:.3f} rad/s ({omega * 60 / (2*np.pi):.1f} RPM)")
    print(f"  叶尖速比: {omega * R / v_wind:.2f}")
    
    # 求解
    print("\n求解中...")
    result = bem.solve_rotor(v_wind, omega, n_elements=20)
    
    print(f"\n结果:")
    print(f"  功率系数 Cp: {result['Cp']:.4f}")
    print(f"  推力系数 Ct: {result['Ct']:.4f}")
    print(f"  功率: {result['power']/1000:.2f} kW")
    print(f"  转矩: {result['torque']/1000:.2f} kN·m")
    print(f"  推力: {result['thrust']/1000:.2f} kN")
    
    # 检查收敛性
    converged_count = sum([elem['converged'] for elem in result['blade_elements']])
    print(f"  收敛叶素数: {converged_count}/{len(result['blade_elements'])}")
    
    # 可视化叶素结果
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    
    r_plot = [elem['r'] for elem in result['blade_elements']]
    
    # 图1: 轴向诱导因子
    ax = axes[0, 0]
    a_vals = [elem['a'] for elem in result['blade_elements']]
    ax.plot(r_plot, a_vals, 'b-', linewidth=2, marker='o')
    ax.axhline(1/3, color='r', linestyle='--', label='Betz极限(a=1/3)')
    ax.set_xlabel('径向位置 r (m)', fontsize=11)
    ax.set_ylabel('轴向诱导因子 a', fontsize=11)
    ax.set_title('轴向诱导因子分布', fontsize=12, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 图2: 切向诱导因子
    ax = axes[0, 1]
    a_prime_vals = [elem['a_prime'] for elem in result['blade_elements']]
    ax.plot(r_plot, a_prime_vals, 'g-', linewidth=2, marker='s')
    ax.set_xlabel('径向位置 r (m)', fontsize=11)
    ax.set_ylabel('切向诱导因子 a\'', fontsize=11)
    ax.set_title('切向诱导因子分布', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    # 图3: 攻角分布
    ax = axes[0, 2]
    alpha_vals = [elem['alpha'] for elem in result['blade_elements']]
    ax.plot(r_plot, alpha_vals, 'r-', linewidth=2, marker='^')
    ax.set_xlabel('径向位置 r (m)', fontsize=11)
    ax.set_ylabel('攻角 α (度)', fontsize=11)
    ax.set_title('攻角分布', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    # 图4: 升力系数
    ax = axes[1, 0]
    Cl_vals = [elem['Cl'] for elem in result['blade_elements']]
    ax.plot(r_plot, Cl_vals, 'b-', linewidth=2, marker='o')
    ax.set_xlabel('径向位置 r (m)', fontsize=11)
    ax.set_ylabel('升力系数 Cl', fontsize=11)
    ax.set_title('升力系数分布', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    # 图5: 切向力分布
    ax = axes[1, 1]
    dFt_vals = [elem['dFt'] for elem in result['blade_elements']]
    ax.plot(r_plot, dFt_vals, 'orange', linewidth=2, marker='d')
    ax.set_xlabel('径向位置 r (m)', fontsize=11)
    ax.set_ylabel('切向力 dFt (N/m)', fontsize=11)
    ax.set_title('切向力分布', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    # 图6: Prandtl修正因子
    ax = axes[1, 2]
    F_vals = [elem['F'] for elem in result['blade_elements']]
    ax.plot(r_plot, F_vals, 'purple', linewidth=2, marker='*')
    ax.set_xlabel('径向位置 r (m)', fontsize=11)
    ax.set_ylabel('Prandtl因子 F', fontsize=11)
    ax.set_title('Prandtl叶尖损失修正', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('case03_bem_solution.png', dpi=300, bbox_inches='tight')
    print("\n图表已保存: case03_bem_solution.png")
    
    return bem


def demo_cp_lambda_curve(bem):
    """演示4: Cp-λ曲线"""
    print("\n" + "=" * 60)
    print("演示4: 风轮性能曲线 (Cp-λ)")
    print("=" * 60)
    
    v_wind = 10.0  # m/s
    
    # 叶尖速比范围
    TSR_range = np.linspace(2, 14, 25)
    omega_range = TSR_range * v_wind / bem.R
    
    Cp_vals = []
    Ct_vals = []
    
    print(f"\n扫描叶尖速比: {TSR_range[0]:.1f} ~ {TSR_range[-1]:.1f}")
    print("计算中...")
    
    for i, omega in enumerate(omega_range):
        result = bem.solve_rotor(v_wind, omega, n_elements=15)
        Cp_vals.append(result['Cp'])
        Ct_vals.append(result['Ct'])
        
        if i % 5 == 0:
            print(f"  λ = {TSR_range[i]:.1f}: Cp = {result['Cp']:.4f}")
    
    # 找到最大Cp
    idx_max = np.argmax(Cp_vals)
    Cp_max = Cp_vals[idx_max]
    lambda_opt = TSR_range[idx_max]
    
    print(f"\n最优工作点:")
    print(f"  最优叶尖速比: {lambda_opt:.2f}")
    print(f"  最大功率系数: {Cp_max:.4f}")
    print(f"  Betz极限: 0.593")
    print(f"  效率: {Cp_max/0.593*100:.1f}%")
    
    # 简化模型对比
    simple_rotor = SimpleRotor(bem.R, Cp_max=0.48, lambda_opt=8.0)
    Cp_simple = [simple_rotor.Cp_curve(lam) for lam in TSR_range]
    
    # 可视化
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # 图1: Cp-λ曲线
    ax = axes[0]
    ax.plot(TSR_range, Cp_vals, 'b-', linewidth=2, marker='o', 
            label='BEM理论')
    ax.plot(TSR_range, Cp_simple, 'r--', linewidth=2, 
            label='简化模型')
    ax.axhline(0.593, color='green', linestyle=':', linewidth=2, 
               label='Betz极限')
    ax.plot(lambda_opt, Cp_max, 'r*', markersize=15, 
            label=f'最优点 (λ={lambda_opt:.1f}, Cp={Cp_max:.3f})')
    ax.set_xlabel('叶尖速比 λ', fontsize=12)
    ax.set_ylabel('功率系数 Cp', fontsize=12)
    ax.set_title('功率系数曲线', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_ylim([0, 0.6])
    
    # 图2: Ct-λ曲线
    ax = axes[1]
    ax.plot(TSR_range, Ct_vals, 'b-', linewidth=2, marker='s')
    ax.set_xlabel('叶尖速比 λ', fontsize=12)
    ax.set_ylabel('推力系数 Ct', fontsize=12)
    ax.set_title('推力系数曲线', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('case03_cp_lambda_curve.png', dpi=300, bbox_inches='tight')
    print("\n图表已保存: case03_cp_lambda_curve.png")


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("案例3: 叶片气动力计算 (BEM理论)")
    print("=" * 60)
    
    # 演示1: 翼型特性
    demo_airfoil_characteristics()
    
    # 演示2: 叶片设计
    R, r_hub, B, r_array, chord, twist = demo_blade_design()
    
    # 演示3: BEM求解
    bem = demo_bem_solver(R, r_hub, B, r_array, chord, twist)
    
    # 演示4: Cp-λ曲线
    demo_cp_lambda_curve(bem)
    
    print("\n" + "=" * 60)
    print("案例3 运行完成！")
    print("=" * 60)
    print("\n生成的图表:")
    print("  1. case03_airfoil_characteristics.png")
    print("  2. case03_blade_design.png")
    print("  3. case03_bem_solution.png")
    print("  4. case03_cp_lambda_curve.png")
    
    plt.show()


if __name__ == "__main__":
    main()
