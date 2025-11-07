"""
案例11: TSR控制

本案例演示:
1. TSR控制原理
2. 参考转速计算
3. PI转速控制器
4. 风速变化响应

工程背景: 最常用的MPPT控制策略
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from models.control import TSRController
from models.aerodynamics import SimpleRotor

plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False


def demo_tsr_principle():
    """演示1: TSR控制原理"""
    print("=" * 60)
    print("演示1: TSR控制原理")
    print("=" * 60)
    
    R = 40  # m
    lambda_opt = 8.0
    
    # 风速范围
    v_range = np.linspace(5, 15, 50)
    omega_ref = lambda_opt * v_range / R
    omega_rpm = omega_ref * 60 / (2*np.pi)
    
    print(f"\n风轮参数:")
    print(f"  半径: {R} m")
    print(f"  最优λ: {lambda_opt}")
    
    print(f"\n关键点:")
    for v in [6, 10, 14]:
        omega = lambda_opt * v / R
        print(f"  v={v}m/s: ω_ref={omega:.3f}rad/s ({omega*60/(2*np.pi):.1f}RPM)")
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # 参考转速
    ax = axes[0]
    ax.plot(v_range, omega_ref, 'b-', linewidth=2)
    ax.set_xlabel('风速 (m/s)', fontsize=12)
    ax.set_ylabel('参考转速 (rad/s)', fontsize=12)
    ax.set_title('TSR控制参考转速', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    # RPM
    ax = axes[1]
    ax.plot(v_range, omega_rpm, 'g-', linewidth=2)
    ax.set_xlabel('风速 (m/s)', fontsize=12)
    ax.set_ylabel('参考转速 (RPM)', fontsize=12)
    ax.set_title('TSR控制参考转速（RPM）', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('case11_tsr_principle.png', dpi=300, bbox_inches='tight')
    print("\n图表已保存: case11_tsr_principle.png")


def demo_tsr_tracking():
    """演示2: TSR跟踪性能"""
    print("\n" + "=" * 60)
    print("演示2: TSR跟踪性能")
    print("=" * 60)
    
    R = 40
    lambda_opt = 8.0
    tsr_ctrl = TSRController(lambda_opt=lambda_opt, R=R, Kp=1e5, Ki=1e3)
    rotor = SimpleRotor(R=R, Cp_max=0.48, lambda_opt=lambda_opt)
    
    # 风速阶跃
    t = np.linspace(0, 50, 1000)
    dt = t[1] - t[0]
    v_wind = np.ones_like(t) * 8.0
    v_wind[t >= 20] = 10.0
    v_wind[t >= 35] = 12.0
    
    # 初始化
    omega = np.zeros_like(t)
    omega[0] = 1.5
    T_ref = np.zeros_like(t)
    P = np.zeros_like(t)
    lambda_vals = np.zeros_like(t)
    
    print(f"\n仿真TSR跟踪...")
    print(f"  风速阶跃: 8→10→12 m/s")
    
    J = 1e7  # 转动惯量
    
    for i in range(1, len(t)):
        # TSR控制
        ctrl = tsr_ctrl.compute_torque(v_wind[i], omega[i-1], dt)
        T_ref[i] = ctrl['T_ref']
        lambda_vals[i] = ctrl['lambda_actual']
        
        # 风轮功率
        result = rotor.calculate_power(v_wind[i], omega[i-1])
        P[i] = result['power']
        T_aero = result['torque']
        
        # 转速动态
        domega = (T_aero - T_ref[i]) / J
        omega[i] = omega[i-1] + domega * dt
        omega[i] = max(0.1, omega[i])
    
    omega_rpm = omega * 60 / (2*np.pi)
    omega_ref = lambda_opt * v_wind / R
    omega_ref_rpm = omega_ref * 60 / (2*np.pi)
    
    print(f"\n跟踪性能:")
    print(f"  最终λ: {lambda_vals[-1]:.2f} (目标: {lambda_opt})")
    print(f"  λ误差: {abs(lambda_vals[-1]-lambda_opt)/lambda_opt*100:.1f}%")
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # 风速
    ax = axes[0, 0]
    ax.plot(t, v_wind, 'b-', linewidth=2)
    ax.set_ylabel('风速 (m/s)', fontsize=12)
    ax.set_title('风速输入', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    # 转速跟踪
    ax = axes[0, 1]
    ax.plot(t, omega_rpm, 'b-', linewidth=2, label='实际转速')
    ax.plot(t, omega_ref_rpm, 'r--', linewidth=2, label='参考转速')
    ax.set_ylabel('转速 (RPM)', fontsize=12)
    ax.set_title('转速跟踪', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 叶尖速比
    ax = axes[1, 0]
    ax.plot(t, lambda_vals, 'g-', linewidth=2)
    ax.axhline(lambda_opt, color='r', linestyle='--', label=f'最优λ={lambda_opt}')
    ax.set_xlabel('时间 (s)', fontsize=12)
    ax.set_ylabel('叶尖速比 λ', fontsize=12)
    ax.set_title('叶尖速比跟踪', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 功率
    ax = axes[1, 1]
    ax.plot(t, P/1e6, 'purple', linewidth=2)
    ax.set_xlabel('时间 (s)', fontsize=12)
    ax.set_ylabel('功率 (MW)', fontsize=12)
    ax.set_title('输出功率', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('case11_tsr_tracking.png', dpi=300, bbox_inches='tight')
    print("\n图表已保存: case11_tsr_tracking.png")


def demo_tsr_disturbance():
    """演示3: 风速扰动响应"""
    print("\n" + "=" * 60)
    print("演示3: 风速扰动响应")
    print("=" * 60)
    
    R = 40
    lambda_opt = 8.0
    tsr_ctrl = TSRController(lambda_opt=lambda_opt, R=R, Kp=5e4, Ki=5e2)
    rotor = SimpleRotor(R=R)
    
    # 风速（含脉动）
    t = np.linspace(0, 100, 2000)
    dt = t[1] - t[0]
    v_mean = 10.0
    v_turb = 2*np.sin(2*np.pi*0.1*t) + np.random.randn(len(t))*0.5
    v_wind = v_mean + v_turb
    v_wind = np.clip(v_wind, 5, 15)
    
    # 初始化
    omega = np.ones_like(t) * 2.0
    lambda_vals = np.zeros_like(t)
    Cp_vals = np.zeros_like(t)
    
    print(f"\n仿真湍流风响应...")
    print(f"  平均风速: {v_mean} m/s")
    print(f"  湍流强度: ~{np.std(v_turb)/v_mean*100:.0f}%")
    
    J = 1e7
    
    for i in range(1, len(t)):
        ctrl = tsr_ctrl.compute_torque(v_wind[i], omega[i-1], dt)
        T_ref = ctrl['T_ref']
        lambda_vals[i] = ctrl['lambda_actual']
        
        result = rotor.calculate_power(v_wind[i], omega[i-1])
        T_aero = result['torque']
        Cp_vals[i] = result['Cp']
        
        domega = (T_aero - T_ref) / J
        omega[i] = omega[i-1] + domega * dt
        omega[i] = max(0.1, omega[i])
    
    print(f"\n性能统计:")
    print(f"  平均λ: {np.mean(lambda_vals[500:]):.2f}")
    print(f"  λ标准差: {np.std(lambda_vals[500:]):.2f}")
    print(f"  平均Cp: {np.mean(Cp_vals[500:]):.3f}")
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # 风速
    ax = axes[0, 0]
    ax.plot(t, v_wind, 'b-', linewidth=0.8)
    ax.axhline(v_mean, color='r', linestyle='--', label=f'平均({v_mean}m/s)')
    ax.set_ylabel('风速 (m/s)', fontsize=12)
    ax.set_title('湍流风速', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 转速
    ax = axes[0, 1]
    ax.plot(t, omega*60/(2*np.pi), 'g-', linewidth=0.8)
    ax.set_ylabel('转速 (RPM)', fontsize=12)
    ax.set_title('转速响应', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    # 叶尖速比
    ax = axes[1, 0]
    ax.plot(t, lambda_vals, 'purple', linewidth=0.8)
    ax.axhline(lambda_opt, color='r', linestyle='--')
    ax.fill_between(t, lambda_opt-0.5, lambda_opt+0.5, alpha=0.2, color='green')
    ax.set_xlabel('时间 (s)', fontsize=12)
    ax.set_ylabel('叶尖速比 λ', fontsize=12)
    ax.set_title('叶尖速比波动', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    # Cp
    ax = axes[1, 1]
    ax.plot(t, Cp_vals, 'r-', linewidth=0.8)
    ax.set_xlabel('时间 (s)', fontsize=12)
    ax.set_ylabel('功率系数 Cp', fontsize=12)
    ax.set_title('Cp波动', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('case11_tsr_disturbance.png', dpi=300, bbox_inches='tight')
    print("\n图表已保存: case11_tsr_disturbance.png")


def main():
    print("\n" + "=" * 60)
    print("案例11: TSR控制")
    print("=" * 60)
    
    demo_tsr_principle()
    demo_tsr_tracking()
    demo_tsr_disturbance()
    
    print("\n" + "=" * 60)
    print("案例11 运行完成！")
    print("=" * 60)
    print("\n生成的图表:")
    print("  1. case11_tsr_principle.png")
    print("  2. case11_tsr_tracking.png")
    print("  3. case11_tsr_disturbance.png")
    
    print("\n核心知识点:")
    print("  ✓ TSR控制原理")
    print("  ✓ 参考转速计算")
    print("  ✓ PI转速跟踪")
    print("  ✓ 湍流风响应")
    
    plt.show()


if __name__ == "__main__":
    main()
