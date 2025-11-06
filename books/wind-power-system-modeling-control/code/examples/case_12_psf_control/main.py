"""
案例12: PSF控制

本案例演示:
1. PSF控制原理
2. Kopt计算
3. 最优转矩曲线
4. 与TSR对比

工程背景: 无需风速测量的MPPT
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from models.control import PSFController, TSRController
from models.aerodynamics import SimpleRotor

plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False


def demo_psf_principle():
    """演示1: PSF控制原理"""
    print("=" * 60)
    print("演示1: PSF控制原理")
    print("=" * 60)
    
    R = 40
    rho = 1.225
    Cp_max = 0.48
    lambda_opt = 8.0
    
    # 计算Kopt
    Kopt = PSFController.compute_Kopt(R, rho, Cp_max, lambda_opt)
    
    print(f"\n风轮参数:")
    print(f"  半径: {R} m")
    print(f"  Cp_max: {Cp_max}")
    print(f"  λ_opt: {lambda_opt}")
    print(f"  Kopt: {Kopt:.2e} N·m·s²")
    
    # 转速范围
    omega_range = np.linspace(0.5, 3.0, 50)
    T_opt = Kopt * omega_range**2
    
    # 不同风速下的理论最优点
    v_winds = [6, 8, 10, 12, 14]
    omega_opt_points = []
    T_opt_points = []
    
    print(f"\n不同风速下的最优工作点:")
    for v in v_winds:
        omega_opt = lambda_opt * v / R
        T_opt_val = Kopt * omega_opt**2
        omega_opt_points.append(omega_opt)
        T_opt_points.append(T_opt_val)
        print(f"  v={v}m/s: ω={omega_opt:.3f}rad/s, T={T_opt_val/1e3:.0f}kN·m")
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # 最优转矩曲线
    ax = axes[0]
    ax.plot(omega_range, T_opt/1e3, 'b-', linewidth=3, label='PSF控制曲线')
    ax.scatter(omega_opt_points, np.array(T_opt_points)/1e3, 
              c='red', s=100, zorder=5, label='最优点')
    for i, v in enumerate(v_winds):
        ax.annotate(f'{v}m/s', 
                   (omega_opt_points[i], T_opt_points[i]/1e3),
                   xytext=(5, 5), textcoords='offset points')
    ax.set_xlabel('转速 (rad/s)', fontsize=12)
    ax.set_ylabel('转矩 (kN·m)', fontsize=12)
    ax.set_title('PSF最优转矩曲线', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 功率曲线
    ax = axes[1]
    P_opt = T_opt * omega_range
    ax.plot(omega_range, P_opt/1e6, 'g-', linewidth=3)
    P_opt_points = np.array(T_opt_points) * np.array(omega_opt_points)
    ax.scatter(omega_opt_points, P_opt_points/1e6, c='red', s=100, zorder=5)
    ax.set_xlabel('转速 (rad/s)', fontsize=12)
    ax.set_ylabel('功率 (MW)', fontsize=12)
    ax.set_title('PSF功率曲线', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('case12_psf_principle.png', dpi=300, bbox_inches='tight')
    print("\n图表已保存: case12_psf_principle.png")
    
    return Kopt


def demo_psf_tracking(Kopt):
    """演示2: PSF跟踪性能"""
    print("\n" + "=" * 60)
    print("演示2: PSF跟踪性能")
    print("=" * 60)
    
    R = 40
    psf_ctrl = PSFController(Kopt=Kopt, R=R)
    rotor = SimpleRotor(R=R, Cp_max=0.48, lambda_opt=8.0)
    
    # 风速阶跃
    t = np.linspace(0, 50, 1000)
    dt = t[1] - t[0]
    v_wind = np.ones_like(t) * 8.0
    v_wind[t >= 20] = 10.0
    v_wind[t >= 35] = 12.0
    
    omega = np.ones_like(t) * 1.5
    P = np.zeros_like(t)
    T_ref = np.zeros_like(t)
    Cp_vals = np.zeros_like(t)
    
    print(f"\n仿真PSF跟踪...")
    
    J = 1e7
    
    for i in range(1, len(t)):
        # PSF控制
        ctrl = psf_ctrl.compute_torque(omega[i-1])
        T_ref[i] = ctrl['T_opt']
        
        # 风轮
        result = rotor.calculate_power(v_wind[i], omega[i-1])
        P[i] = result['power']
        T_aero = result['torque']
        Cp_vals[i] = result['Cp']
        
        # 动态
        domega = (T_aero - T_ref[i]) / J
        omega[i] = omega[i-1] + domega * dt
        omega[i] = max(0.1, omega[i])
    
    lambda_vals = omega * R / v_wind
    
    print(f"\n性能:")
    print(f"  最终Cp: {Cp_vals[-1]:.3f}")
    print(f"  最终λ: {lambda_vals[-1]:.2f}")
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    ax = axes[0, 0]
    ax.plot(t, v_wind, 'b-', linewidth=2)
    ax.set_ylabel('风速 (m/s)', fontsize=12)
    ax.set_title('风速输入', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    ax = axes[0, 1]
    ax.plot(t, omega*60/(2*np.pi), 'g-', linewidth=2)
    ax.set_ylabel('转速 (RPM)', fontsize=12)
    ax.set_title('转速响应', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    ax = axes[1, 0]
    ax.plot(t, P/1e6, 'purple', linewidth=2)
    ax.set_xlabel('时间 (s)', fontsize=12)
    ax.set_ylabel('功率 (MW)', fontsize=12)
    ax.set_title('输出功率', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    ax = axes[1, 1]
    ax.plot(t, Cp_vals, 'r-', linewidth=2)
    ax.axhline(0.48, color='g', linestyle='--', label='Cp_max')
    ax.set_xlabel('时间 (s)', fontsize=12)
    ax.set_ylabel('功率系数 Cp', fontsize=12)
    ax.set_title('Cp跟踪', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('case12_psf_tracking.png', dpi=300, bbox_inches='tight')
    print("\n图表已保存: case12_psf_tracking.png")


def demo_psf_vs_tsr():
    """演示3: PSF vs TSR对比"""
    print("\n" + "=" * 60)
    print("演示3: PSF vs TSR对比")
    print("=" * 60)
    
    R = 40
    Kopt = 0.5 * 1.225 * np.pi * R**5 * 0.48 / 8.0**3
    
    psf_ctrl = PSFController(Kopt=Kopt, R=R)
    tsr_ctrl = TSRController(lambda_opt=8.0, R=R, Kp=5e4, Ki=5e2)
    rotor = SimpleRotor(R=R)
    
    # 风速（实际vs测量误差）
    t = np.linspace(0, 60, 1200)
    dt = t[1] - t[0]
    v_actual = 10 + 2*np.sin(2*np.pi*0.05*t)
    v_measured = v_actual + np.random.randn(len(t))*0.3  # 测量噪声
    
    # PSF（无需风速）
    omega_psf = np.ones_like(t) * 2.0
    Cp_psf = np.zeros_like(t)
    
    # TSR（需要风速）
    omega_tsr = np.ones_like(t) * 2.0
    Cp_tsr = np.zeros_like(t)
    
    print(f"\n仿真对比（含风速测量误差）...")
    
    J = 1e7
    
    for i in range(1, len(t)):
        # PSF控制
        ctrl_psf = psf_ctrl.compute_torque(omega_psf[i-1])
        T_psf = ctrl_psf['T_opt']
        
        result = rotor.calculate_power(v_actual[i], omega_psf[i-1])
        T_aero_psf = result['torque']
        Cp_psf[i] = result['Cp']
        
        domega = (T_aero_psf - T_psf) / J
        omega_psf[i] = omega_psf[i-1] + domega * dt
        omega_psf[i] = max(0.1, omega_psf[i])
        
        # TSR控制（使用有噪声的测量）
        ctrl_tsr = tsr_ctrl.compute_torque(v_measured[i], omega_tsr[i-1], dt)
        T_tsr = ctrl_tsr['T_ref']
        
        result = rotor.calculate_power(v_actual[i], omega_tsr[i-1])
        T_aero_tsr = result['torque']
        Cp_tsr[i] = result['Cp']
        
        domega = (T_aero_tsr - T_tsr) / J
        omega_tsr[i] = omega_tsr[i-1] + domega * dt
        omega_tsr[i] = max(0.1, omega_tsr[i])
    
    print(f"\n性能对比:")
    print(f"  PSF平均Cp: {np.mean(Cp_psf[200:]):.3f}")
    print(f"  TSR平均Cp: {np.mean(Cp_tsr[200:]):.3f}")
    print(f"  PSF Cp标准差: {np.std(Cp_psf[200:]):.4f}")
    print(f"  TSR Cp标准差: {np.std(Cp_tsr[200:]):.4f}")
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    ax = axes[0, 0]
    ax.plot(t, v_actual, 'b-', linewidth=1.5, label='实际风速')
    ax.plot(t, v_measured, 'r--', linewidth=0.8, alpha=0.7, label='测量风速(含噪声)')
    ax.set_ylabel('风速 (m/s)', fontsize=12)
    ax.set_title('风速信号', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    ax = axes[0, 1]
    ax.plot(t, omega_psf*60/(2*np.pi), 'b-', linewidth=1.5, label='PSF')
    ax.plot(t, omega_tsr*60/(2*np.pi), 'r--', linewidth=1.5, label='TSR')
    ax.set_ylabel('转速 (RPM)', fontsize=12)
    ax.set_title('转速对比', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    ax = axes[1, 0]
    ax.plot(t, Cp_psf, 'b-', linewidth=1.5, label='PSF')
    ax.plot(t, Cp_tsr, 'r--', linewidth=1.5, label='TSR')
    ax.axhline(0.48, color='g', linestyle='--', alpha=0.5)
    ax.set_xlabel('时间 (s)', fontsize=12)
    ax.set_ylabel('Cp', fontsize=12)
    ax.set_title('Cp对比', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    ax = axes[1, 1]
    hist_psf, bins = np.histogram(Cp_psf[200:], bins=30)
    hist_tsr, _ = np.histogram(Cp_tsr[200:], bins=bins)
    ax.bar(bins[:-1], hist_psf, width=np.diff(bins), alpha=0.5, label='PSF', color='blue')
    ax.bar(bins[:-1], hist_tsr, width=np.diff(bins), alpha=0.5, label='TSR', color='red')
    ax.axvline(0.48, color='g', linestyle='--', linewidth=2)
    ax.set_xlabel('Cp', fontsize=12)
    ax.set_ylabel('频数', fontsize=12)
    ax.set_title('Cp分布', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('case12_psf_vs_tsr.png', dpi=300, bbox_inches='tight')
    print("\n图表已保存: case12_psf_vs_tsr.png")


def main():
    print("\n" + "=" * 60)
    print("案例12: PSF控制")
    print("=" * 60)
    
    Kopt = demo_psf_principle()
    demo_psf_tracking(Kopt)
    demo_psf_vs_tsr()
    
    print("\n" + "=" * 60)
    print("案例12 运行完成！")
    print("=" * 60)
    print("\n生成的图表:")
    print("  1. case12_psf_principle.png")
    print("  2. case12_psf_tracking.png")
    print("  3. case12_psf_vs_tsr.png")
    
    print("\n核心知识点:")
    print("  ✓ PSF控制原理")
    print("  ✓ Kopt计算方法")
    print("  ✓ 无需风速测量")
    print("  ✓ 与TSR性能对比")
    
    plt.show()


if __name__ == "__main__":
    main()
