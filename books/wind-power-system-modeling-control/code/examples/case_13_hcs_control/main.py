"""
案例13: HCS控制

本案例演示:
1. 爬山搜索原理
2. 扰动步长影响
3. 更新频率影响
4. 三种MPPT对比

工程背景: 自适应MPPT算法
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from models.control import HCSController
from models.aerodynamics import SimpleRotor

plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False


def demo_hcs_principle():
    """演示1: HCS爬山原理"""
    print("=" * 60)
    print("演示1: HCS爬山搜索原理")
    print("=" * 60)
    
    # 模拟P-ω曲线
    omega_range = np.linspace(1.0, 3.0, 100)
    omega_opt = 2.0
    P_curve = -1e6 * (omega_range - omega_opt)**2 + 1.5e6
    
    # 爬山过程
    omega_hcs = [1.2]
    P_hcs = [-1e6 * (1.2 - omega_opt)**2 + 1.5e6]
    delta_omega = 0.1
    
    print(f"\n爬山搜索演示:")
    print(f"  最优转速: {omega_opt} rad/s")
    print(f"  初始转速: {omega_hcs[0]} rad/s")
    
    for step in range(15):
        omega_new = omega_hcs[-1] + delta_omega
        P_new = -1e6 * (omega_new - omega_opt)**2 + 1.5e6
        
        if P_new < P_hcs[-1]:
            delta_omega = -delta_omega  # 反向
        
        omega_hcs.append(omega_new)
        P_hcs.append(P_new)
        
        if step < 5:
            print(f"  步骤{step+1}: ω={omega_new:.3f}, P={P_new/1e6:.3f}MW, Δω={delta_omega:+.3f}")
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # 功率曲线
    ax = axes[0]
    ax.plot(omega_range, P_curve/1e6, 'b-', linewidth=2, label='P-ω曲线')
    ax.plot(omega_hcs, np.array(P_hcs)/1e6, 'r-o', markersize=6, label='HCS路径')
    ax.axvline(omega_opt, color='g', linestyle='--', label='最优点')
    ax.set_xlabel('转速 (rad/s)', fontsize=12)
    ax.set_ylabel('功率 (MW)', fontsize=12)
    ax.set_title('HCS爬山过程', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 转速轨迹
    ax = axes[1]
    ax.plot(omega_hcs, 'g-o', markersize=6)
    ax.axhline(omega_opt, color='r', linestyle='--', label='最优值')
    ax.set_xlabel('迭代步数', fontsize=12)
    ax.set_ylabel('转速 (rad/s)', fontsize=12)
    ax.set_title('转速收敛过程', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('case13_hcs_principle.png', dpi=300, bbox_inches='tight')
    print("\n图表已保存: case13_hcs_principle.png")


def demo_hcs_parameters():
    """演示2: HCS参数影响"""
    print("\n" + "=" * 60)
    print("演示2: HCS参数影响")
    print("=" * 60)
    
    R = 40
    rotor = SimpleRotor(R=R)
    
    # 不同参数设置
    configs = [
        ("快速", 2e4, 2.0),
        ("中等", 1e4, 5.0),
        ("慢速", 5e3, 10.0),
    ]
    
    t = np.linspace(0, 100, 2000)
    dt = t[1] - t[0]
    v_wind = np.ones_like(t) * 10.0
    v_wind[t >= 50] = 12.0
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    print(f"\n参数对比:")
    
    for name, delta_T, interval in configs:
        hcs = HCSController(delta_T=delta_T, update_interval=interval)
        
        omega = np.ones_like(t) * 1.5
        P = np.zeros_like(t)
        
        J = 1e7
        
        for i in range(1, len(t)):
            result = rotor.calculate_power(v_wind[i], omega[i-1])
            P[i] = result['power']
            T_aero = result['torque']
            
            ctrl = hcs.compute_torque(P[i], dt)
            T_ref = ctrl['T_ref']
            
            domega = (T_aero - T_ref) / J
            omega[i] = omega[i-1] + domega * dt
            omega[i] = max(0.1, omega[i])
        
        print(f"  {name}: Δω={delta_T/1e3:.0f}kN·m, 周期={interval}s")
        print(f"    平均功率: {np.mean(P[1000:])/1e6:.2f}MW")
        
        ax = axes[0, 0]
        ax.plot(t, omega*60/(2*np.pi), linewidth=2, label=name)
        
        ax = axes[0, 1]
        ax.plot(t, P/1e6, linewidth=2, label=name)
    
    ax = axes[0, 0]
    ax.set_ylabel('转速 (RPM)', fontsize=12)
    ax.set_title('转速响应对比', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    ax = axes[0, 1]
    ax.set_ylabel('功率 (MW)', fontsize=12)
    ax.set_title('功率响应对比', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 风速
    ax = axes[1, 0]
    ax.plot(t, v_wind, 'b-', linewidth=2)
    ax.set_xlabel('时间 (s)', fontsize=12)
    ax.set_ylabel('风速 (m/s)', fontsize=12)
    ax.set_title('风速输入', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    # 文字说明
    ax = axes[1, 1]
    ax.axis('off')
    summary = """
    HCS参数影响总结:
    
    1. 扰动步长 ΔT:
       • 大步长: 收敛快，振荡大
       • 小步长: 收敛慢，稳态精度高
    
    2. 更新周期:
       • 短周期: 响应快，易受噪声干扰
       • 长周期: 稳定性好，动态性差
    
    3. 折中设计:
       • ΔT = 1e4 N·m
       • 周期 = 5s
    """
    ax.text(0.1, 0.5, summary, fontsize=11, family='monospace',
           verticalalignment='center')
    
    plt.tight_layout()
    plt.savefig('case13_hcs_parameters.png', dpi=300, bbox_inches='tight')
    print("\n图表已保存: case13_hcs_parameters.png")


def demo_mppt_comparison():
    """演示3: 三种MPPT对比"""
    print("\n" + "=" * 60)
    print("演示3: TSR vs PSF vs HCS综合对比")
    print("=" * 60)
    
    from models.control import TSRController, PSFController
    
    R = 40
    rotor = SimpleRotor(R=R, Cp_max=0.48, lambda_opt=8.0)
    
    # 三种控制器
    tsr = TSRController(lambda_opt=8.0, R=R, Kp=5e4, Ki=5e2)
    Kopt = 0.5 * 1.225 * np.pi * R**5 * 0.48 / 8.0**3
    psf = PSFController(Kopt=Kopt, R=R)
    hcs = HCSController(delta_T=1e4, update_interval=5.0)
    
    # 复杂风速
    t = np.linspace(0, 120, 2400)
    dt = t[1] - t[0]
    v_wind = 8 + 2*np.sin(2*np.pi*0.02*t) + np.random.randn(len(t))*0.3
    v_wind = np.clip(v_wind, 5, 15)
    
    results = {}
    
    print(f"\n仿真三种MPPT算法...")
    
    for name, ctrl in [("TSR", tsr), ("PSF", psf), ("HCS", hcs)]:
        omega = np.ones_like(t) * 2.0
        P = np.zeros_like(t)
        Cp = np.zeros_like(t)
        
        J = 1e7
        
        for i in range(1, len(t)):
            result = rotor.calculate_power(v_wind[i], omega[i-1])
            P[i] = result['power']
            T_aero = result['torque']
            Cp[i] = result['Cp']
            
            if name == "TSR":
                ctrl_result = ctrl.compute_torque(v_wind[i], omega[i-1], dt)
                T_ref = ctrl_result['T_ref']
            elif name == "PSF":
                ctrl_result = ctrl.compute_torque(omega[i-1])
                T_ref = ctrl_result['T_opt']
            else:  # HCS
                ctrl_result = ctrl.compute_torque(P[i], dt)
                T_ref = ctrl_result['T_ref']
            
            domega = (T_aero - T_ref) / J
            omega[i] = omega[i-1] + domega * dt
            omega[i] = max(0.1, omega[i])
        
        results[name] = {
            'omega': omega,
            'P': P,
            'Cp': Cp
        }
        
        print(f"\n{name}控制:")
        print(f"  平均功率: {np.mean(P[500:])/1e6:.3f}MW")
        print(f"  平均Cp: {np.mean(Cp[500:]):.3f}")
        print(f"  Cp标准差: {np.std(Cp[500:]):.4f}")
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # 转速
    ax = axes[0, 0]
    for name in ["TSR", "PSF", "HCS"]:
        ax.plot(t, results[name]['omega']*60/(2*np.pi), linewidth=1.5, label=name, alpha=0.8)
    ax.set_ylabel('转速 (RPM)', fontsize=12)
    ax.set_title('转速对比', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 功率
    ax = axes[0, 1]
    for name in ["TSR", "PSF", "HCS"]:
        ax.plot(t, results[name]['P']/1e6, linewidth=1.5, label=name, alpha=0.8)
    ax.set_ylabel('功率 (MW)', fontsize=12)
    ax.set_title('功率对比', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Cp
    ax = axes[1, 0]
    for name in ["TSR", "PSF", "HCS"]:
        ax.plot(t, results[name]['Cp'], linewidth=1.5, label=name, alpha=0.8)
    ax.axhline(0.48, color='k', linestyle='--', alpha=0.5)
    ax.set_xlabel('时间 (s)', fontsize=12)
    ax.set_ylabel('Cp', fontsize=12)
    ax.set_title('Cp对比', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 性能雷达图
    ax = axes[1, 1]
    categories = ['平均Cp', '稳定性', '响应速度', '实现难度', '鲁棒性']
    N = len(categories)
    angles = np.linspace(0, 2*np.pi, N, endpoint=False).tolist()
    angles += angles[:1]
    
    scores = {
        'TSR': [0.95, 0.90, 0.95, 0.60, 0.70],
        'PSF': [0.92, 0.85, 0.90, 0.90, 0.85],
        'HCS': [0.85, 0.70, 0.60, 0.95, 0.90]
    }
    
    ax = plt.subplot(224, projection='polar')
    for name, score in scores.items():
        score += score[:1]
        ax.plot(angles, score, 'o-', linewidth=2, label=name)
        ax.fill(angles, score, alpha=0.15)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories)
    ax.set_ylim(0, 1)
    ax.set_title('综合性能评价', fontsize=14, fontweight='bold', pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
    ax.grid(True)
    
    plt.tight_layout()
    plt.savefig('case13_mppt_comparison.png', dpi=300, bbox_inches='tight')
    print("\n图表已保存: case13_mppt_comparison.png")


def main():
    print("\n" + "=" * 60)
    print("案例13: HCS控制")
    print("=" * 60)
    
    demo_hcs_principle()
    demo_hcs_parameters()
    demo_mppt_comparison()
    
    print("\n" + "=" * 60)
    print("案例13 运行完成！")
    print("=" * 60)
    print("\n生成的图表:")
    print("  1. case13_hcs_principle.png")
    print("  2. case13_hcs_parameters.png")
    print("  3. case13_mppt_comparison.png")
    
    print("\n核心知识点:")
    print("  ✓ HCS爬山搜索原理")
    print("  ✓ 扰动步长与周期")
    print("  ✓ 三种MPPT算法对比")
    print("  ✓ 算法选择准则")
    
    plt.show()


if __name__ == "__main__":
    main()
