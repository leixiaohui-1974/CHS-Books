"""
案例17: 功率因数控制
演示PQ解耦控制和功率因数调节

实验内容:
1. 功率计算与PQ解耦
2. 有功功率控制
3. 无功功率控制  
4. 功率因数调节

Author: CHS-BOOKS Project
Date: 2025-11-04
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from models.inverter_control import PowerController, PQController, SRFPLL

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def experiment_1_power_calculation():
    """
    实验1: 功率计算与PQ解耦
    演示dq坐标系下的功率计算
    """
    print("=" * 60)
    print("实验1: 功率计算与PQ解耦")
    print("=" * 60)
    
    # 创建功率计算器
    power_calc = PowerController(V_grid=311.0)
    
    # 测试不同工况
    test_cases = [
        {"name": "纯有功(PF=1)", "i_d": 10.0, "i_q": 0.0},
        {"name": "纯无功(PF=0)", "i_d": 0.0, "i_q": 10.0},
        {"name": "容性(超前)", "i_d": 10.0, "i_q": -5.0},
        {"name": "感性(滞后)", "i_d": 10.0, "i_q": 5.0},
    ]
    
    print(f"\n电网电压: V_d = 311V, V_q = 0V (电压定向)\n")
    print(f"{'工况':<15} {'i_d(A)':<10} {'i_q(A)':<10} {'P(W)':<10} {'Q(Var)':<10} {'PF':<8}")
    print("-" * 70)
    
    for case in test_cases:
        # 电网电压定向于d轴
        v_d = 311.0
        v_q = 0.0
        i_d = case["i_d"]
        i_q = case["i_q"]
        
        # 计算功率
        P, Q, S, PF = power_calc.calculate_power(v_d, v_q, i_d, i_q)
        
        print(f"{case['name']:<15} {i_d:<10.1f} {i_q:<10.1f} {P:<10.0f} {Q:<10.0f} {PF:<8.3f}")
    
    print("\n观察:")
    print("  1. i_d控制有功功率P")
    print("  2. i_q控制无功功率Q")
    print("  3. PQ完全解耦")
    print("  4. 功率因数 PF = P/√(P²+Q²)")


def experiment_2_active_power_control():
    """
    实验2: 有功功率控制
    测试有功功率阶跃响应
    """
    print("\n" + "=" * 60)
    print("实验2: 有功功率控制")
    print("=" * 60)
    
    # 系统参数
    V_grid = 311.0
    L = 5e-3
    omega = 2 * np.pi * 50
    
    # 创建PLL和PQ控制器
    pll = SRFPLL(Kp=50.0, Ki=1000.0)
    pq_ctrl = PQController(
        V_grid=V_grid,
        Kp_i=0.5,
        Ki_i=100.0,
        L=L,
        omega=omega,
        P_limit=5000.0,
        Q_limit=2000.0
    )
    
    # 仿真
    dt = 1e-4
    t_total = 0.3
    time = np.arange(0, t_total, dt)
    N = len(time)
    
    # 初始化
    i_a, i_b, i_c = 0.0, 0.0, 0.0
    
    # 记录
    P_ref_arr = np.zeros(N)
    P_arr = np.zeros(N)
    Q_arr = np.zeros(N)
    PF_arr = np.zeros(N)
    
    # 仿真循环
    for i, t in enumerate(time):
        # 三相电网电压
        theta_g = omega * t
        va = V_grid * np.sin(theta_g)
        vb = V_grid * np.sin(theta_g - 2 * np.pi / 3)
        vc = V_grid * np.sin(theta_g + 2 * np.pi / 3)
        
        # PLL同步
        theta, _, _ = pll.update(va, vb, vc, dt)
        
        # 有功功率参考 (阶跃)
        if t < 0.1:
            P_ref = 1000.0
        elif t < 0.2:
            P_ref = 3000.0
        else:
            P_ref = 2000.0
        
        # 无功功率为0 (功率因数=1)
        Q_ref = 0.0
        
        # PQ控制
        v_a_out, v_b_out, v_c_out = pq_ctrl.update(
            P_ref, Q_ref, va, vb, vc, i_a, i_b, i_c, theta, dt
        )
        
        # 简化的负载模型 (RL)
        R_load = 1.0
        L_load = 10e-3
        
        di_a = (v_a_out - va - R_load * i_a) / L_load
        di_b = (v_b_out - vb - R_load * i_b) / L_load
        di_c = (v_c_out - vc - R_load * i_c) / L_load
        
        i_a += di_a * dt
        i_b += di_b * dt
        i_c += di_c * dt
        
        # 记录
        P_ref_arr[i] = P_ref
        status = pq_ctrl.get_status()
        P_arr[i] = status['power']['P']
        Q_arr[i] = status['power']['Q']
        PF_arr[i] = status['power']['PF']
    
    # 绘图
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))
    
    time_ms = time * 1000
    
    # 有功功率
    axes[0].plot(time_ms, P_ref_arr, 'r--', linewidth=2, alpha=0.7, label='参考功率')
    axes[0].plot(time_ms, P_arr, 'b-', linewidth=1.5, label='实际功率')
    axes[0].set_ylabel('有功功率 (W)', fontsize=11)
    axes[0].set_title('有功功率控制', fontsize=13, fontweight='bold')
    axes[0].grid(True, alpha=0.3)
    axes[0].legend(fontsize=10)
    
    # 无功功率
    axes[1].plot(time_ms, Q_arr, 'g-', linewidth=1.5)
    axes[1].axhline(0, color='r', linestyle='--', linewidth=1, alpha=0.5)
    axes[1].set_ylabel('无功功率 (Var)', fontsize=11)
    axes[1].set_title('无功功率 (应保持为0)', fontsize=11, fontweight='bold')
    axes[1].grid(True, alpha=0.3)
    
    # 功率因数
    axes[2].plot(time_ms, PF_arr, 'm-', linewidth=1.5)
    axes[2].axhline(1.0, color='r', linestyle='--', linewidth=1, alpha=0.5, label='目标PF=1')
    axes[2].set_xlabel('时间 (ms)', fontsize=11)
    axes[2].set_ylabel('功率因数', fontsize=11)
    axes[2].set_title('功率因数', fontsize=11, fontweight='bold')
    axes[2].grid(True, alpha=0.3)
    axes[2].legend(fontsize=10)
    axes[2].set_ylim([0.8, 1.05])
    
    plt.tight_layout()
    plt.savefig('case_17_exp2_active_power.png', dpi=300, bbox_inches='tight')
    print("\n✓ 图1已保存")
    plt.show()
    
    # 性能
    print(f"\n性能指标:")
    steady_1 = P_arr[int(0.08/dt):int(0.1/dt)]
    steady_2 = P_arr[int(0.28/dt):]
    print(f"  阶跃1 稳态误差: {abs(np.mean(steady_1) - 1000):.1f} W")
    print(f"  阶跃2 稳态误差: {abs(np.mean(steady_2) - 2000):.1f} W")
    print(f"  平均功率因数: {np.mean(PF_arr[1000:]):.3f}")


def experiment_3_reactive_power_control():
    """
    实验3: 无功功率控制
    测试无功功率调节和功率因数变化
    """
    print("\n" + "=" * 60)
    print("实验3: 无功功率与功率因数控制")
    print("=" * 60)
    
    # 创建功率计算器
    power_calc = PowerController(V_grid=311.0)
    
    # 固定有功功率，改变无功功率
    P_ref = 2000.0
    Q_values = np.array([0, 500, 1000, -500, -1000])
    
    print(f"\n有功功率: P = {P_ref} W\n")
    print(f"{'Q(Var)':<12} {'S(VA)':<12} {'PF':<10} {'类型':<10}")
    print("-" * 50)
    
    for Q_ref in Q_values:
        S = np.sqrt(P_ref**2 + Q_ref**2)
        PF = P_ref / S if S > 0 else 1.0
        
        if Q_ref > 0:
            pf_type = "感性(滞后)"
        elif Q_ref < 0:
            pf_type = "容性(超前)"
        else:
            pf_type = "纯阻性"
        
        print(f"{Q_ref:<12.0f} {S:<12.0f} {PF:<10.3f} {pf_type:<10}")
    
    print("\n观察:")
    print("  1. Q=0时，PF=1 (纯阻性负载)")
    print("  2. Q>0时，PF<1，感性(滞后)")
    print("  3. Q<0时，PF<1，容性(超前)")
    print("  4. |Q|越大，功率因数越小")


def main():
    """主函数"""
    print("=" * 60)
    print("案例17: 功率因数控制")
    print("有功无功功率PQ解耦控制")
    print("=" * 60)
    
    experiment_1_power_calculation()
    experiment_2_active_power_control()
    experiment_3_reactive_power_control()
    
    print("\n" + "=" * 60)
    print("✅ 所有实验完成!")
    print("=" * 60)
    print("\n总结:")
    print("  1. dq坐标系: PQ完全解耦")
    print("  2. i_d控制P，i_q控制Q")
    print("  3. 功率因数可调: PF = P/√(P²+Q²)")
    print("  4. 并网要求: 通常PF>0.95")


if __name__ == "__main__":
    main()
