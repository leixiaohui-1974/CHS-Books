#!/usr/bin/env python3
"""
案例9扩展实验：系统建模深入分析

本文件包含多个扩展实验：
1. 参数敏感性分析
2. 非线性建模与线性化
3. 模型阶数选择
4. 模型简化方法

作者：CHS-Books项目
日期：2025-10-30
版本：1.0
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parents[3]
sys.path.insert(0, str(project_root))

from code.models.water_tank.single_tank import SingleTank

# 设置matplotlib
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


# ============================================================================
# 实验1：参数敏感性分析
# ============================================================================

def experiment_parameter_sensitivity():
    """
    实验1：分析不同参数对系统响应的影响
    """
    print("=" * 80)
    print("实验1：参数敏感性分析")
    print("=" * 80)

    # 基准参数
    A_base, R_base, K_base = 2.5, 1.8, 1.2

    # 测试不同的A值（横截面积）
    A_values = [1.5, 2.0, 2.5, 3.0, 3.5]

    print("\n[测试参数A（横截面积）的影响]")

    results_A = {}

    for A in A_values:
        system = SingleTank(A=A, R=R_base, K=K_base)
        system.reset(h0=0.0)

        tau = A * R_base
        print(f"  A = {A} m² → τ = {tau} min")

        # 仿真
        duration = 20
        dt = 0.1
        n_steps = int(duration / dt)

        time = np.zeros(n_steps)
        h_data = np.zeros(n_steps)

        for i in range(n_steps):
            time[i] = system.t
            h_data[i] = system.h
            system.step(0.5, dt)

        results_A[A] = {'time': time, 'h': h_data, 'tau': tau}

    # 可视化A的影响
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    ax = axes[0]
    for A, data in results_A.items():
        ax.plot(data['time'], data['h'], linewidth=2, label=f'A = {A} m²')
    ax.set_xlabel('Time (min)')
    ax.set_ylabel('Water Level (m)')
    ax.set_title('Effect of Tank Area A on Response')
    ax.legend()
    ax.grid(True)

    ax = axes[1]
    A_list = list(results_A.keys())
    tau_list = [results_A[A]['tau'] for A in A_list]
    ax.plot(A_list, tau_list, 'o-', linewidth=2)
    ax.set_xlabel('Tank Area A (m²)')
    ax.set_ylabel('Time Constant τ (min)')
    ax.set_title('Time Constant vs Tank Area')
    ax.grid(True)

    plt.tight_layout()
    plt.savefig('exp1_parameter_A.png', dpi=150, bbox_inches='tight')
    print("\n图表已保存: exp1_parameter_A.png")

    print("\n结论：")
    print("  - A越大，τ越大，系统响应越慢")
    print("  - τ = A × R，线性关系")
    print("  - 物理意义：水箱越大，水位变化越慢")

    return results_A


# ============================================================================
# 实验2：非线性建模与线性化
# ============================================================================

def experiment_nonlinear_modeling():
    """
    实验2：对比线性模型和非线性模型
    """
    print("\n" + "=" * 80)
    print("实验2：非线性建模与线性化")
    print("=" * 80)

    print("\n[线性模型 vs 非线性模型]")
    print("  线性模型：Q_out = h / R")
    print("  非线性模型：Q_out = C * sqrt(h)")

    # 参数
    A = 2.5
    R = 1.8
    K = 1.2
    C = 1.0  # 非线性系数

    # 工作点线性化
    h0 = 2.0  # 工作点水位
    R_eq = 2 * np.sqrt(h0) / C  # 等效阻力

    print(f"\n[在h0 = {h0} m处线性化]")
    print(f"  等效阻力 R_eq = 2*sqrt(h0)/C = {R_eq:.4f}")

    # 线性系统
    system_linear = SingleTank(A=A, R=R, K=K)
    system_linear.reset(h0=0.0)

    # 非线性系统仿真（手动实现）
    def simulate_nonlinear(A, C, K, u, h0, duration, dt):
        """非线性系统仿真"""
        n_steps = int(duration / dt)
        time = np.zeros(n_steps)
        h = np.zeros(n_steps)
        h[0] = h0

        for i in range(1, n_steps):
            time[i] = i * dt
            Q_in = K * u
            Q_out = C * np.sqrt(max(h[i-1], 0))
            dhdt = (Q_in - Q_out) / A
            h[i] = h[i-1] + dhdt * dt

        return time, h

    # 仿真对比
    u_step = 0.5
    duration = 30
    dt = 0.1
    n_steps = int(duration / dt)

    # 线性
    time_linear = np.zeros(n_steps)
    h_linear = np.zeros(n_steps)
    for i in range(n_steps):
        time_linear[i] = system_linear.t
        h_linear[i] = system_linear.h
        system_linear.step(u_step, dt)

    # 非线性
    time_nonlinear, h_nonlinear = simulate_nonlinear(A, C, K, u_step, 0.0, duration, dt)

    # 可视化
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    ax = axes[0]
    ax.plot(time_linear, h_linear, 'b-', linewidth=2, label='Linear Model')
    ax.plot(time_nonlinear, h_nonlinear, 'r--', linewidth=2, label='Nonlinear Model')
    ax.set_xlabel('Time (min)')
    ax.set_ylabel('Water Level (m)')
    ax.set_title('Linear vs Nonlinear Model')
    ax.legend()
    ax.grid(True)

    ax = axes[1]
    error = h_linear - h_nonlinear
    ax.plot(time_linear, error, 'g-', linewidth=2)
    ax.axhline(0, color='k', linestyle='--', linewidth=0.5)
    ax.set_xlabel('Time (min)')
    ax.set_ylabel('Error (m)')
    ax.set_title('Model Difference (Linear - Nonlinear)')
    ax.grid(True)

    plt.tight_layout()
    plt.savefig('exp2_nonlinear.png', dpi=150, bbox_inches='tight')
    print("\n图表已保存: exp2_nonlinear.png")

    max_error = np.max(np.abs(error))
    print(f"\n最大误差: {max_error:.4f} m")
    print("\n结论：")
    print("  - 小范围内，线性化模型足够准确")
    print("  - 大范围工作时，非线性效应显著")
    print("  - 需要根据应用选择合适的模型")


# ============================================================================
# 实验3：模型阶数选择
# ============================================================================

def experiment_model_order():
    """
    实验3：对比不同阶数模型的精度
    """
    print("\n" + "=" * 80)
    print("实验3：模型阶数选择")
    print("=" * 80)

    print("\n[一阶模型 vs 二阶模型]")

    # 参数
    A, R, K = 2.5, 1.8, 1.2
    tau = A * R
    K_dc = K * R

    # 一阶模型传递函数
    sys_1st = signal.TransferFunction([K_dc], [tau, 1])

    # 二阶模型（加入小时滞近似）
    tau_delay = 0.5  # 小时滞
    # 用Pade近似时滞
    # e^(-s*tau_d) ≈ (1 - s*tau_d/2) / (1 + s*tau_d/2)
    # 组合后得二阶系统
    a = tau * (1 + tau_delay / (2 * tau))
    b = 1 + tau_delay / (2 * tau)
    sys_2nd = signal.TransferFunction([K_dc], [a, b, 1])

    # 阶跃响应
    t = np.linspace(0, 30, 300)
    t1, y1 = signal.step(sys_1st, T=t)
    t2, y2 = signal.step(sys_2nd, T=t)

    # 可视化
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(t1, y1 * 0.5, 'b-', linewidth=2, label='1st Order Model')
    ax.plot(t2, y2 * 0.5, 'r--', linewidth=2, label='2nd Order Model (with delay)')
    ax.set_xlabel('Time (min)')
    ax.set_ylabel('Water Level (m)')
    ax.set_title('Model Order Comparison')
    ax.legend()
    ax.grid(True)

    plt.tight_layout()
    plt.savefig('exp3_model_order.png', dpi=150, bbox_inches='tight')
    print("\n图表已保存: exp3_model_order.png")

    print("\n结论：")
    print("  - 一阶模型：简单，参数少，适合大多数应用")
    print("  - 二阶模型：更精确，但参数多，辨识困难")
    print("  - 选择原则：在满足精度要求前提下，尽量简单")


# ============================================================================
# 实验4：频域特性分析
# ============================================================================

def experiment_frequency_characteristics():
    """
    实验4：分析不同参数对频域特性的影响
    """
    print("\n" + "=" * 80)
    print("实验4：频域特性分析")
    print("=" * 80)

    # 不同时间常数的系统
    tau_values = [2.0, 4.5, 9.0]
    K_dc = 2.16

    fig, axes = plt.subplots(2, 1, figsize=(10, 10))

    w = np.logspace(-2, 1, 100)

    for tau in tau_values:
        sys = signal.TransferFunction([K_dc], [tau, 1])
        w_temp, mag, phase = signal.bode(sys, w)

        axes[0].semilogx(w_temp, mag, linewidth=2, label=f'τ = {tau} min')
        axes[1].semilogx(w_temp, phase, linewidth=2, label=f'τ = {tau} min')

    axes[0].set_ylabel('Magnitude (dB)')
    axes[0].set_title('Bode Plot: Effect of Time Constant')
    axes[0].legend()
    axes[0].grid(True, which='both')
    axes[0].axhline(-3, color='r', linestyle='--', alpha=0.5)

    axes[1].set_xlabel('Frequency (rad/min)')
    axes[1].set_ylabel('Phase (degrees)')
    axes[1].legend()
    axes[1].grid(True, which='both')
    axes[1].axhline(-45, color='r', linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.savefig('exp4_frequency.png', dpi=150, bbox_inches='tight')
    print("\n图表已保存: exp4_frequency.png")

    print("\n结论：")
    print("  - τ越大，截止频率越低")
    print("  - τ越大，相位滞后越早出现")
    print("  - 高频衰减速度相同（-20 dB/decade）")


# ============================================================================
# 主程序
# ============================================================================

def main():
    """运行所有扩展实验"""
    print("=" * 80)
    print("案例9扩展实验：系统建模深入分析")
    print("=" * 80)

    # 实验1：参数敏感性
    results1 = experiment_parameter_sensitivity()

    # 实验2：非线性建模
    experiment_nonlinear_modeling()

    # 实验3：模型阶数
    experiment_model_order()

    # 实验4：频域特性
    experiment_frequency_characteristics()

    print("\n" + "=" * 80)
    print("所有扩展实验完成！")
    print("=" * 80)

    plt.show()


if __name__ == "__main__":
    main()
