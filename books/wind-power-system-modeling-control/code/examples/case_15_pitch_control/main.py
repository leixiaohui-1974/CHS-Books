"""
案例15: 变桨距控制

本案例演示:
1. 变桨距原理
2. PI桨距角控制
3. 功率限制
4. MPPT+变桨综合

工程背景: 超额定风速功率调节
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from models.control import PitchController, RegionController, PSFController
from models.aerodynamics import SimpleRotor

plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False


def demo_pitch_effect():
    """演示1: 桨距角对功率的影响"""
    print("=" * 60)
    print("演示1: 桨距角对功率的影响")
    print("=" * 60)
    
    R = 40
    rotor = SimpleRotor(R=R, Cp_max=0.48, lambda_opt=8.0)
    
    # 不同桨距角
    beta_vals = [0, 5, 10, 15, 20]
    v_range = np.linspace(5, 25, 50)
    omega_fixed = 2.5  # 额定转速
    
    print(f"\n固定转速: {omega_fixed} rad/s ({omega_fixed*60/(2*np.pi):.0f} RPM)")
    print(f"\n不同桨距角下的功率特性:")
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    for beta in beta_vals:
        P_vals = []
        Cp_vals = []
        
        for v in v_range:
            # 简化：Cp随β降低
            Cp_beta = 0.48 * (1 - beta/30)**2 if beta < 30 else 0.01
            # 修正lambda
            lambda_val = omega_fixed * R / v
            Cp = Cp_beta * rotor.Cp_curve(lambda_val) / rotor.Cp_curve(8.0)
            Cp = max(0, min(0.48, Cp))
            
            P = 0.5 * 1.225 * np.pi * R**2 * v**3 * Cp
            P_vals.append(P)
            Cp_vals.append(Cp)
        
        ax = axes[0]
        ax.plot(v_range, np.array(P_vals)/1e6, linewidth=2, label=f'β={beta}°')
        
        ax = axes[1]
        ax.plot(v_range, Cp_vals, linewidth=2, label=f'β={beta}°')
        
        # 打印关键点
        idx_15 = np.argmin(np.abs(v_range - 15))
        print(f"  β={beta:2d}°, v=15m/s: P={P_vals[idx_15]/1e6:.2f}MW, Cp={Cp_vals[idx_15]:.3f}")
    
    ax = axes[0]
    ax.axhline(2.0, color='r', linestyle='--', label='额定功率(2MW)')
    ax.set_xlabel('风速 (m/s)', fontsize=12)
    ax.set_ylabel('功率 (MW)', fontsize=12)
    ax.set_title('桨距角对功率的影响', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    ax = axes[1]
    ax.set_xlabel('风速 (m/s)', fontsize=12)
    ax.set_ylabel('Cp', fontsize=12)
    ax.set_title('桨距角对Cp的影响', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('case15_pitch_effect.png', dpi=300, bbox_inches='tight')
    print("\n图表已保存: case15_pitch_effect.png")


def demo_pitch_control():
    """演示2: 变桨距控制器"""
    print("\n" + "=" * 60)
    print("演示2: 变桨距功率限制")
    print("=" * 60)
    
    R = 40
    P_rated = 2e6
    omega_rated = 2.5
    
    pitch_ctrl = PitchController(
        P_rated=P_rated,
        omega_rated=omega_rated,
        Kp_pitch=3.0,
        Ki_pitch=0.3,
        beta_max=25
    )
    
    rotor = SimpleRotor(R=R)
    
    # 风速：从额定到超额定
    t = np.linspace(0, 100, 2000)
    dt = t[1] - t[0]
    v_wind = np.ones_like(t) * 12.0  # 额定风速
    v_wind[t >= 30] = 16.0  # 超额定
    v_wind[t >= 60] = 20.0  # 高风速
    
    omega = np.ones_like(t) * omega_rated
    beta = np.zeros_like(t)
    P = np.zeros_like(t)
    T_ref = np.zeros_like(t)
    
    print(f"\n额定参数:")
    print(f"  额定功率: {P_rated/1e6}MW")
    print(f"  额定转速: {omega_rated}rad/s ({omega_rated*60/(2*np.pi):.0f}RPM)")
    print(f"  额定风速: 12m/s")
    
    print(f"\n仿真变桨控制...")
    
    J = 1e7
    
    for i in range(1, len(t)):
        if v_wind[i] >= 12:  # 超额定区
            # 变桨控制
            ctrl = pitch_ctrl.compute_pitch_angle(omega[i-1], dt)
            beta[i] = ctrl['beta']
            T_ref[i] = P_rated / omega[i-1] if omega[i-1] > 0 else 0
        else:
            # 额定以下，β=0
            beta[i] = 0
            T_ref[i] = 0.5 * 1.225 * np.pi * R**5 * 0.48 / 8.0**3 * omega[i-1]**2
        
        # 风轮（考虑桨距角影响）
        Cp_beta = 0.48 * (1 - beta[i]/30)**2 if beta[i] < 30 else 0.01
        lambda_val = omega[i-1] * R / v_wind[i]
        Cp = Cp_beta * rotor.Cp_curve(lambda_val) / rotor.Cp_curve(8.0)
        Cp = max(0, min(0.48, Cp))
        
        P[i] = 0.5 * 1.225 * np.pi * R**2 * v_wind[i]**3 * Cp
        T_aero = P[i] / omega[i-1] if omega[i-1] > 0 else 0
        
        # 动态
        domega = (T_aero - T_ref[i]) / J
        omega[i] = omega[i-1] + domega * dt
        omega[i] = max(0.1, min(3.0, omega[i]))
    
    print(f"\n控制效果:")
    print(f"  v=12m/s: β={beta[int(0.4*len(t))]:.1f}°, P={P[int(0.4*len(t))]/1e6:.2f}MW")
    print(f"  v=16m/s: β={beta[int(0.7*len(t))]:.1f}°, P={P[int(0.7*len(t))]/1e6:.2f}MW")
    print(f"  v=20m/s: β={beta[-100]:.1f}°, P={P[-100]/1e6:.2f}MW")
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    ax = axes[0, 0]
    ax.plot(t, v_wind, 'b-', linewidth=2)
    ax.set_ylabel('风速 (m/s)', fontsize=12)
    ax.set_title('风速输入', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    ax = axes[0, 1]
    ax.plot(t, beta, 'g-', linewidth=2)
    ax.set_ylabel('桨距角 (度)', fontsize=12)
    ax.set_title('桨距角响应', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    ax = axes[1, 0]
    ax.plot(t, omega*60/(2*np.pi), 'purple', linewidth=2)
    ax.axhline(omega_rated*60/(2*np.pi), color='r', linestyle='--', label='额定转速')
    ax.set_xlabel('时间 (s)', fontsize=12)
    ax.set_ylabel('转速 (RPM)', fontsize=12)
    ax.set_title('转速调节', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    ax = axes[1, 1]
    ax.plot(t, P/1e6, 'r-', linewidth=2)
    ax.axhline(P_rated/1e6, color='g', linestyle='--', linewidth=2, label='额定功率')
    ax.set_xlabel('时间 (s)', fontsize=12)
    ax.set_ylabel('功率 (MW)', fontsize=12)
    ax.set_title('功率限制', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('case15_pitch_control.png', dpi=300, bbox_inches='tight')
    print("\n图表已保存: case15_pitch_control.png")


def demo_full_range_control():
    """演示3: 全风速范围控制"""
    print("\n" + "=" * 60)
    print("演示3: MPPT+变桨综合控制")
    print("=" * 60)
    
    R = 40
    P_rated = 2e6
    v_rated = 12.0
    omega_rated = 2.5
    
    # 综合控制器
    Kopt = 0.5 * 1.225 * np.pi * R**5 * 0.48 / 8.0**3
    mppt_ctrl = PSFController(Kopt=Kopt, R=R)
    pitch_ctrl = PitchController(P_rated=P_rated, omega_rated=omega_rated, Kp_pitch=3.0, Ki_pitch=0.3)
    region_ctrl = RegionController(mppt_ctrl, pitch_ctrl, v_rated, omega_rated, P_rated)
    
    rotor = SimpleRotor(R=R)
    
    # 全风速扫描
    t = np.linspace(0, 200, 4000)
    dt = t[1] - t[0]
    v_wind = 5 + 15 * t / t[-1]  # 5→20m/s线性增加
    
    omega = np.ones_like(t) * 1.0
    beta = np.zeros_like(t)
    P = np.zeros_like(t)
    region = np.zeros_like(t)
    
    print(f"\n全风速范围仿真: 5-20m/s")
    
    J = 1e7
    
    for i in range(1, len(t)):
        # 分区控制
        ctrl = region_ctrl.compute_control(v_wind[i], omega[i-1], P[i-1], dt)
        beta[i] = ctrl['beta']
        T_ref = ctrl.get('T_ref', P_rated/omega[i-1] if omega[i-1]>0 else 0)
        region[i] = 2 if ctrl['region'] == 'II_MPPT' else 3
        
        # 风轮
        Cp_beta = 0.48 * (1 - beta[i]/30)**2 if beta[i] < 30 else 0.01
        lambda_val = omega[i-1] * R / v_wind[i] if v_wind[i] > 0 else 0
        Cp = Cp_beta * rotor.Cp_curve(lambda_val) / rotor.Cp_curve(8.0)
        Cp = max(0, min(0.48, Cp))
        
        P[i] = 0.5 * 1.225 * np.pi * R**2 * v_wind[i]**3 * Cp
        T_aero = P[i] / omega[i-1] if omega[i-1] > 0 else 0
        
        domega = (T_aero - T_ref) / J
        omega[i] = omega[i-1] + domega * dt
        omega[i] = max(0.1, min(3.5, omega[i]))
    
    print(f"\n关键点:")
    for v_test in [8, 12, 16]:
        idx = np.argmin(np.abs(v_wind - v_test))
        print(f"  v={v_test}m/s: β={beta[idx]:.1f}°, ω={omega[idx]*60/(2*np.pi):.0f}RPM, P={P[idx]/1e6:.2f}MW")
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # 风速与分区
    ax = axes[0, 0]
    ax.plot(t, v_wind, 'b-', linewidth=2)
    ax.axhline(v_rated, color='r', linestyle='--', label='额定风速')
    ax.fill_between(t, 0, v_rated, alpha=0.2, color='green', label='Region II')
    ax.fill_between(t, v_rated, 25, alpha=0.2, color='orange', label='Region III')
    ax.set_ylabel('风速 (m/s)', fontsize=12)
    ax.set_title('风速输入与分区', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 转速
    ax = axes[0, 1]
    ax.plot(t, omega*60/(2*np.pi), 'g-', linewidth=2)
    ax.axhline(omega_rated*60/(2*np.pi), color='r', linestyle='--', label='额定转速')
    ax.set_ylabel('转速 (RPM)', fontsize=12)
    ax.set_title('转速变化', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 桨距角
    ax = axes[1, 0]
    ax.plot(t, beta, 'purple', linewidth=2)
    ax.set_xlabel('时间 (s)', fontsize=12)
    ax.set_ylabel('桨距角 (度)', fontsize=12)
    ax.set_title('桨距角调节', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    # 功率
    ax = axes[1, 1]
    ax.plot(t, P/1e6, 'r-', linewidth=2)
    ax.axhline(P_rated/1e6, color='g', linestyle='--', linewidth=2, label='额定功率')
    ax.set_xlabel('时间 (s)', fontsize=12)
    ax.set_ylabel('功率 (MW)', fontsize=12)
    ax.set_title('功率输出', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('case15_full_range_control.png', dpi=300, bbox_inches='tight')
    print("\n图表已保存: case15_full_range_control.png")


def main():
    print("\n" + "=" * 60)
    print("案例15: 变桨距控制")
    print("=" * 60)
    
    demo_pitch_effect()
    demo_pitch_control()
    demo_full_range_control()
    
    print("\n" + "=" * 60)
    print("案例15 运行完成！")
    print("=" * 60)
    print("\n生成的图表:")
    print("  1. case15_pitch_effect.png")
    print("  2. case15_pitch_control.png")
    print("  3. case15_full_range_control.png")
    
    print("\n核心知识点:")
    print("  ✓ 桨距角对功率影响")
    print("  ✓ PI变桨控制器")
    print("  ✓ 功率限制策略")
    print("  ✓ MPPT+变桨综合控制")
    
    plt.show()


if __name__ == "__main__":
    main()
