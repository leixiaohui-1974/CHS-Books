"""
案例14: 最优转矩控制

本案例演示:
1. 最优转矩表
2. 查表法控制
3. 分区控制
4. 转矩限制

工程背景: 实用MPPT实现
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from models.control import OptimalTorqueController
from models.aerodynamics import SimpleRotor

plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False


def demo_optimal_torque_table():
    """演示1: 最优转矩表生成"""
    print("=" * 60)
    print("演示1: 最优转矩表生成")
    print("=" * 60)
    
    R = 40
    rotor = SimpleRotor(R=R, Cp_max=0.48, lambda_opt=8.0)
    
    # 转速范围
    omega_table = np.linspace(0.5, 3.0, 50)
    T_table = []
    P_table = []
    
    print(f"\n生成最优转矩表...")
    print(f"  转速范围: {omega_table[0]:.1f} - {omega_table[-1]:.1f} rad/s")
    
    # 对每个转速，找最优转矩
    for omega in omega_table:
        # 搜索最优转矩
        T_search = np.linspace(1e3, 1e6, 100)
        P_search = []
        
        for T in T_search:
            # 简化：假设稳态，T_aero = T_gen
            # 从T和omega推算功率
            # 实际应迭代求解
            P = T * omega
            P_search.append(P)
        
        # 最优点（简化：使用PSF公式）
        Kopt = 0.5 * 1.225 * np.pi * R**5 * 0.48 / 8.0**3
        T_opt = Kopt * omega**2
        P_opt = T_opt * omega
        
        T_table.append(T_opt)
        P_table.append(P_opt)
    
    T_table = np.array(T_table)
    P_table = np.array(P_table)
    
    print(f"\n最优转矩表样本:")
    for i in [0, len(omega_table)//2, -1]:
        print(f"  ω={omega_table[i]:.2f}rad/s: T={T_table[i]/1e3:.0f}kN·m, P={P_table[i]/1e6:.2f}MW")
    
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    
    # 转矩表
    ax = axes[0]
    ax.plot(omega_table, T_table/1e3, 'b-o', linewidth=2, markersize=4)
    ax.set_xlabel('转速 (rad/s)', fontsize=12)
    ax.set_ylabel('最优转矩 (kN·m)', fontsize=12)
    ax.set_title('最优转矩查找表', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    # 功率表
    ax = axes[1]
    ax.plot(omega_table, P_table/1e6, 'g-o', linewidth=2, markersize=4)
    ax.set_xlabel('转速 (rad/s)', fontsize=12)
    ax.set_ylabel('最优功率 (MW)', fontsize=12)
    ax.set_title('最优功率曲线', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    # 转矩-功率关系
    ax = axes[2]
    ax.plot(T_table/1e3, P_table/1e6, 'r-o', linewidth=2, markersize=4)
    ax.set_xlabel('转矩 (kN·m)', fontsize=12)
    ax.set_ylabel('功率 (MW)', fontsize=12)
    ax.set_title('转矩-功率关系', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('case14_optimal_torque_table.png', dpi=300, bbox_inches='tight')
    print("\n图表已保存: case14_optimal_torque_table.png")
    
    return omega_table, T_table


def demo_lookup_control(omega_table, T_table):
    """演示2: 查表法控制"""
    print("\n" + "=" * 60)
    print("演示2: 查表法控制")
    print("=" * 60)
    
    R = 40
    ctrl = OptimalTorqueController(omega_table, T_table)
    rotor = SimpleRotor(R=R)
    
    # 风速变化
    t = np.linspace(0, 60, 1200)
    dt = t[1] - t[0]
    v_wind = 8 + 3*np.sin(2*np.pi*0.03*t)
    
    omega = np.ones_like(t) * 1.5
    T_ref = np.zeros_like(t)
    P = np.zeros_like(t)
    Cp = np.zeros_like(t)
    
    print(f"\n仿真查表控制...")
    
    J = 1e7
    
    for i in range(1, len(t)):
        # 查表
        T_ref[i] = ctrl.compute_torque(omega[i-1])
        
        # 风轮
        result = rotor.calculate_power(v_wind[i], omega[i-1])
        P[i] = result['power']
        T_aero = result['torque']
        Cp[i] = result['Cp']
        
        # 动态
        domega = (T_aero - T_ref[i]) / J
        omega[i] = omega[i-1] + domega * dt
        omega[i] = max(0.1, omega[i])
    
    print(f"\n性能:")
    print(f"  平均功率: {np.mean(P[200:])/1e6:.2f}MW")
    print(f"  平均Cp: {np.mean(Cp[200:]):.3f}")
    
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
    ax.plot(t, T_ref/1e3, 'r-', linewidth=2)
    ax.set_xlabel('时间 (s)', fontsize=12)
    ax.set_ylabel('参考转矩 (kN·m)', fontsize=12)
    ax.set_title('转矩指令', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    ax = axes[1, 1]
    ax.plot(t, P/1e6, 'purple', linewidth=2)
    ax.set_xlabel('时间 (s)', fontsize=12)
    ax.set_ylabel('功率 (MW)', fontsize=12)
    ax.set_title('输出功率', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('case14_lookup_control.png', dpi=300, bbox_inches='tight')
    print("\n图表已保存: case14_lookup_control.png")


def demo_region_control():
    """演示3: 分区转矩控制"""
    print("\n" + "=" * 60)
    print("演示3: 分区转矩控制")
    print("=" * 60)
    
    R = 40
    rotor = SimpleRotor(R=R)
    
    # 分区定义
    omega_cut_in = 0.5
    omega_rated = 2.5
    omega_cut_out = 3.0
    T_rated = 8e5
    P_rated = 2e6
    
    # 转速范围
    omega_range = np.linspace(0, 3.5, 100)
    T_command = np.zeros_like(omega_range)
    
    print(f"\n分区定义:")
    print(f"  Region I (启动): 0 - {omega_cut_in} rad/s")
    print(f"  Region II (MPPT): {omega_cut_in} - {omega_rated} rad/s")
    print(f"  Region III (额定): {omega_rated} - {omega_cut_out} rad/s")
    print(f"  Region IV (停机): > {omega_cut_out} rad/s")
    
    Kopt = 0.5 * 1.225 * np.pi * R**5 * 0.48 / 8.0**3
    
    for i, omega in enumerate(omega_range):
        if omega < omega_cut_in:
            # Region I: 最小转矩
            T_command[i] = 0
        elif omega < omega_rated:
            # Region II: MPPT
            T_command[i] = Kopt * omega**2
        elif omega < omega_cut_out:
            # Region III: 额定功率
            T_command[i] = P_rated / omega if omega > 0 else T_rated
        else:
            # Region IV: 紧急制动
            T_command[i] = 2 * T_rated
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # 转矩分区
    ax = axes[0]
    colors = ['gray', 'green', 'blue', 'red']
    regions = [
        (0, omega_cut_in, 'I启动'),
        (omega_cut_in, omega_rated, 'II MPPT'),
        (omega_rated, omega_cut_out, 'III额定'),
        (omega_cut_out, omega_range[-1], 'IV停机')
    ]
    
    for (start, end, label), color in zip(regions, colors):
        mask = (omega_range >= start) & (omega_range < end)
        ax.plot(omega_range[mask], T_command[mask]/1e3, 
               linewidth=3, label=label, color=color)
    
    ax.axhline(T_rated/1e3, color='k', linestyle='--', alpha=0.5, label='额定转矩')
    ax.set_xlabel('转速 (rad/s)', fontsize=12)
    ax.set_ylabel('转矩指令 (kN·m)', fontsize=12)
    ax.set_title('分区转矩控制', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 功率分区
    ax = axes[1]
    P_command = T_command * omega_range
    
    for (start, end, label), color in zip(regions, colors):
        mask = (omega_range >= start) & (omega_range < end)
        if np.any(mask):
            ax.plot(omega_range[mask], P_command[mask]/1e6, 
                   linewidth=3, label=label, color=color)
    
    ax.axhline(P_rated/1e6, color='k', linestyle='--', alpha=0.5, label='额定功率')
    ax.set_xlabel('转速 (rad/s)', fontsize=12)
    ax.set_ylabel('功率 (MW)', fontsize=12)
    ax.set_title('分区功率曲线', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('case14_region_control.png', dpi=300, bbox_inches='tight')
    print("\n图表已保存: case14_region_control.png")


def main():
    print("\n" + "=" * 60)
    print("案例14: 最优转矩控制")
    print("=" * 60)
    
    omega_table, T_table = demo_optimal_torque_table()
    demo_lookup_control(omega_table, T_table)
    demo_region_control()
    
    print("\n" + "=" * 60)
    print("案例14 运行完成！")
    print("=" * 60)
    print("\n生成的图表:")
    print("  1. case14_optimal_torque_table.png")
    print("  2. case14_lookup_control.png")
    print("  3. case14_region_control.png")
    
    print("\n核心知识点:")
    print("  ✓ 最优转矩表生成")
    print("  ✓ 查表法控制")
    print("  ✓ 分区控制策略")
    print("  ✓ 转矩/功率限制")
    
    plt.show()


if __name__ == "__main__":
    main()
