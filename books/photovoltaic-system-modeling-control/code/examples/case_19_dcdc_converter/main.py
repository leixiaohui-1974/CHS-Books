"""
案例19: DC/DC变换器建模
演示Boost、Buck、Buck-Boost三种拓扑

实验内容:
1. Boost升压变换器
2. Buck降压变换器
3. Buck-Boost升降压变换器
4. 三种拓扑性能对比

Author: CHS-BOOKS Project
Date: 2025-11-04
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from models.dcdc_converter import BoostConverter, BuckConverter, BuckBoostConverter

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def experiment_1_boost_converter():
    """
    实验1: Boost升压变换器
    测试不同占空比下的升压特性
    """
    print("=" * 60)
    print("实验1: Boost升压变换器")
    print("=" * 60)
    
    # 参数
    L = 100e-6  # 100uH
    C = 100e-6  # 100uF
    R = 10.0    # 10Ω
    V_in = 12.0  # 12V输入
    
    # 测试不同占空比
    duty_cycles = [0.3, 0.5, 0.7, 0.8]
    
    print(f"\n参数: L={L*1e6:.0f}uH, C={C*1e6:.0f}uF, R={R:.0f}Ω, Vin={V_in:.0f}V\n")
    print(f"{'占空比':<10} {'理论Vout':<12} {'实际Vout':<12} {'误差(%)':<10}")
    print("-" * 50)
    
    results = []
    
    for d in duty_cycles:
        # 创建Boost变换器
        boost = BoostConverter(L, C, R)
        
        # 仿真
        dt = 1e-6  # 1us
        t_total = 0.01  # 10ms
        time = np.arange(0, t_total, dt)
        
        v_C_arr = np.zeros(len(time))
        
        for i, t in enumerate(time):
            i_L, v_C = boost.update(V_in, d, dt)
            v_C_arr[i] = v_C
        
        # 稳态输出电压
        v_out_actual = np.mean(v_C_arr[-1000:])
        
        # 理论输出电压
        v_out_theory = V_in / (1 - d)
        
        # 误差
        error = abs(v_out_actual - v_out_theory) / v_out_theory * 100
        
        print(f"{d:<10.1f} {v_out_theory:<12.2f} {v_out_actual:<12.2f} {error:<10.2f}")
        
        results.append({
            'd': d,
            'time': time,
            'v_C': v_C_arr,
            'v_out': v_out_actual
        })
    
    # 绘图
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))
    
    # 电压波形
    for res in results:
        axes[0].plot(res['time']*1000, res['v_C'], label=f"D={res['d']}")
    
    axes[0].set_xlabel('时间 (ms)', fontsize=11)
    axes[0].set_ylabel('输出电压 (V)', fontsize=11)
    axes[0].set_title('Boost变换器 - 不同占空比输出电压', fontsize=13, fontweight='bold')
    axes[0].legend(fontsize=10)
    axes[0].grid(True, alpha=0.3)
    
    # 升压比
    duty_range = np.linspace(0, 0.9, 100)
    gain_theory = 1 / (1 - duty_range)
    gain_actual = [res['v_out'] / V_in for res in results]
    d_actual = [res['d'] for res in results]
    
    axes[1].plot(duty_range, gain_theory, 'b-', linewidth=2, label='理论')
    axes[1].plot(d_actual, gain_actual, 'ro', markersize=8, label='实际')
    axes[1].set_xlabel('占空比', fontsize=11)
    axes[1].set_ylabel('升压比 (Vout/Vin)', fontsize=11)
    axes[1].set_title('Boost变换器 - 升压比特性', fontsize=11, fontweight='bold')
    axes[1].legend(fontsize=10)
    axes[1].grid(True, alpha=0.3)
    axes[1].set_ylim([0, 10])
    
    plt.tight_layout()
    plt.savefig('case_19_exp1_boost.png', dpi=300, bbox_inches='tight')
    print("\n✓ 图1已保存")
    plt.show()


def experiment_2_buck_converter():
    """
    实验2: Buck降压变换器
    测试不同占空比下的降压特性
    """
    print("\n" + "=" * 60)
    print("实验2: Buck降压变换器")
    print("=" * 60)
    
    # 参数
    L = 100e-6
    C = 100e-6
    R = 10.0
    V_in = 24.0  # 24V输入
    
    duty_cycles = [0.2, 0.4, 0.6, 0.8]
    
    print(f"\n参数: L={L*1e6:.0f}uH, C={C*1e6:.0f}uF, R={R:.0f}Ω, Vin={V_in:.0f}V\n")
    print(f"{'占空比':<10} {'理论Vout':<12} {'实际Vout':<12} {'误差(%)':<10}")
    print("-" * 50)
    
    results = []
    
    for d in duty_cycles:
        buck = BuckConverter(L, C, R)
        
        dt = 1e-6
        t_total = 0.01
        time = np.arange(0, t_total, dt)
        
        v_C_arr = np.zeros(len(time))
        
        for i, t in enumerate(time):
            i_L, v_C = buck.update(V_in, d, dt)
            v_C_arr[i] = v_C
        
        v_out_actual = np.mean(v_C_arr[-1000:])
        v_out_theory = d * V_in
        error = abs(v_out_actual - v_out_theory) / v_out_theory * 100
        
        print(f"{d:<10.1f} {v_out_theory:<12.2f} {v_out_actual:<12.2f} {error:<10.2f}")
        
        results.append({
            'd': d,
            'time': time,
            'v_C': v_C_arr,
            'v_out': v_out_actual
        })
    
    # 绘图
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))
    
    for res in results:
        axes[0].plot(res['time']*1000, res['v_C'], label=f"D={res['d']}")
    
    axes[0].set_xlabel('时间 (ms)', fontsize=11)
    axes[0].set_ylabel('输出电压 (V)', fontsize=11)
    axes[0].set_title('Buck变换器 - 不同占空比输出电压', fontsize=13, fontweight='bold')
    axes[0].legend(fontsize=10)
    axes[0].grid(True, alpha=0.3)
    
    # 降压比
    duty_range = np.linspace(0, 1, 100)
    gain_theory = duty_range
    gain_actual = [res['v_out'] / V_in for res in results]
    d_actual = [res['d'] for res in results]
    
    axes[1].plot(duty_range, gain_theory, 'b-', linewidth=2, label='理论')
    axes[1].plot(d_actual, gain_actual, 'ro', markersize=8, label='实际')
    axes[1].set_xlabel('占空比', fontsize=11)
    axes[1].set_ylabel('降压比 (Vout/Vin)', fontsize=11)
    axes[1].set_title('Buck变换器 - 降压比特性', fontsize=11, fontweight='bold')
    axes[1].legend(fontsize=10)
    axes[1].grid(True, alpha=0.3)
    axes[1].set_ylim([0, 1.2])
    
    plt.tight_layout()
    plt.savefig('case_19_exp2_buck.png', dpi=300, bbox_inches='tight')
    print("\n✓ 图2已保存")
    plt.show()


def experiment_3_topology_comparison():
    """
    实验3: 三种拓扑对比
    相同条件下对比性能
    """
    print("\n" + "=" * 60)
    print("实验3: 三种拓扑性能对比")
    print("=" * 60)
    
    # 统一参数
    L = 100e-6
    C = 100e-6
    R = 10.0
    V_in = 20.0
    d = 0.5  # 统一占空比
    
    # 三种变换器
    boost = BoostConverter(L, C, R)
    buck = BuckConverter(L, C, R)
    buck_boost = BuckBoostConverter(L, C, R)
    
    # 仿真
    dt = 1e-6
    t_total = 0.015
    time = np.arange(0, t_total, dt)
    N = len(time)
    
    v_boost = np.zeros(N)
    v_buck = np.zeros(N)
    v_buckboost = np.zeros(N)
    
    for i in range(N):
        _, v_boost[i] = boost.update(V_in, d, dt)
        _, v_buck[i] = buck.update(V_in, d, dt)
        _, v_buckboost[i] = buck_boost.update(V_in, d, dt)
    
    # 稳态值
    v_boost_ss = np.mean(v_boost[-1000:])
    v_buck_ss = np.mean(v_buck[-1000:])
    v_buckboost_ss = abs(np.mean(v_buckboost[-1000:]))  # 取绝对值
    
    print(f"\n统一条件: Vin={V_in}V, D={d}, L={L*1e6:.0f}uH, C={C*1e6:.0f}uF\n")
    print(f"{'拓扑':<15} {'输出电压':<12} {'升降压比':<12} {'特点':<20}")
    print("-" * 65)
    print(f"{'Boost':<15} {v_boost_ss:<12.2f} {v_boost_ss/V_in:<12.2f} {'仅升压, >Vin':<20}")
    print(f"{'Buck':<15} {v_buck_ss:<12.2f} {v_buck_ss/V_in:<12.2f} {'仅降压, <Vin':<20}")
    print(f"{'Buck-Boost':<15} {v_buckboost_ss:<12.2f} {v_buckboost_ss/V_in:<12.2f} {'升降压, 极性反':<20}")
    
    # 绘图
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))
    
    axes[0].plot(time*1000, v_boost, 'b-', linewidth=1)
    axes[0].axhline(v_boost_ss, color='r', linestyle='--', alpha=0.7, label=f'稳态={v_boost_ss:.1f}V')
    axes[0].set_ylabel('电压 (V)', fontsize=11)
    axes[0].set_title('Boost: 升压 (Vout > Vin)', fontsize=11, fontweight='bold')
    axes[0].legend(fontsize=10)
    axes[0].grid(True, alpha=0.3)
    
    axes[1].plot(time*1000, v_buck, 'g-', linewidth=1)
    axes[1].axhline(v_buck_ss, color='r', linestyle='--', alpha=0.7, label=f'稳态={v_buck_ss:.1f}V')
    axes[1].set_ylabel('电压 (V)', fontsize=11)
    axes[1].set_title('Buck: 降压 (Vout < Vin)', fontsize=11, fontweight='bold')
    axes[1].legend(fontsize=10)
    axes[1].grid(True, alpha=0.3)
    
    axes[2].plot(time*1000, v_buckboost, 'm-', linewidth=1)
    axes[2].axhline(v_buckboost[-1], color='r', linestyle='--', alpha=0.7, 
                    label=f'稳态={v_buckboost_ss:.1f}V (绝对值)')
    axes[2].set_xlabel('时间 (ms)', fontsize=11)
    axes[2].set_ylabel('电压 (V)', fontsize=11)
    axes[2].set_title('Buck-Boost: 升降压 (Vout极性反)', fontsize=11, fontweight='bold')
    axes[2].legend(fontsize=10)
    axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('case_19_exp3_comparison.png', dpi=300, bbox_inches='tight')
    print("\n✓ 图3已保存")
    plt.show()


def main():
    """主函数"""
    print("=" * 60)
    print("案例19: DC/DC变换器建模")
    print("Boost / Buck / Buck-Boost 拓扑对比")
    print("=" * 60)
    
    experiment_1_boost_converter()
    experiment_2_buck_converter()
    experiment_3_topology_comparison()
    
    print("\n" + "=" * 60)
    print("✅ 所有实验完成!")
    print("=" * 60)
    print("\n总结:")
    print("  1. Boost: 升压 (Vout > Vin), M = 1/(1-D)")
    print("  2. Buck: 降压 (Vout < Vin), M = D")
    print("  3. Buck-Boost: 升降压 (极性反), M = -D/(1-D)")
    print("  4. 状态空间模型准确预测动态特性")


if __name__ == "__main__":
    main()
