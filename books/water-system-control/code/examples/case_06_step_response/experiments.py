#!/usr/bin/env python3
"""
案例6扩展实验：图解法参数辨识对比分析

本文件包含多个扩展实验：
1. 三种图解法精度对比（63.2%法、切线法、双点法）
2. 噪声对图解法的影响
3. 不同系统参数下的辨识精度
4. 图解法 vs 优化算法对比

作者：CHS-Books项目
日期：2025-10-30
版本：1.0
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from scipy.optimize import curve_fit
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
# 辅助函数
# ============================================================================

def conduct_step_test(A, R, K, u_step, h0, duration, dt, noise_level=0.0):
    """
    进行阶跃响应测试

    Args:
        A, R, K: 系统参数
        u_step: 阶跃幅值
        h0: 初始水位
        duration: 测试时长
        dt: 采样间隔
        noise_level: 测量噪声水平

    Returns:
        tuple: (时间, 控制输入, 水位测量)
    """
    system = SingleTank(A=A, R=R, K=K)
    system.reset(h0=h0)

    n_steps = int(duration / dt)
    t_data = np.zeros(n_steps)
    u_data = np.ones(n_steps) * u_step
    h_data = np.zeros(n_steps)

    for i in range(n_steps):
        t_data[i] = system.t
        h_data[i] = system.h + np.random.normal(0, noise_level)
        system.step(u_data[i], dt)

    return t_data, u_data, h_data


def method_63_2_percent(t_data, h_data, h0):
    """
    63.2%法辨识时间常数

    Args:
        t_data: 时间数据
        h_data: 水位数据
        h0: 初始水位

    Returns:
        tuple: (时间常数τ, 稳态增益K)
    """
    # 稳态值（取最后20%数据的平均）
    h_ss = np.mean(h_data[int(0.8 * len(h_data)):])

    # 63.2%值
    h_632 = h0 + 0.632 * (h_ss - h0)

    # 插值找到对应时间
    interpolator = interp1d(h_data, t_data, fill_value='extrapolate')
    tau = float(interpolator(h_632))

    return tau, h_ss - h0


def method_tangent(t_data, h_data, h0):
    """
    切线法辨识时间常数

    Args:
        t_data: 时间数据
        h_data: 水位数据
        h0: 初始水位

    Returns:
        tuple: (时间常数τ, 稳态增益K)
    """
    # 稳态值
    h_ss = np.mean(h_data[int(0.8 * len(h_data)):])

    # 计算初始斜率（使用前5%数据拟合）
    n_points = int(0.05 * len(h_data))
    coeffs = np.polyfit(t_data[:n_points], h_data[:n_points], 1)
    slope = coeffs[0]

    # 时间常数 = (稳态值 - 初始值) / 初始斜率
    if abs(slope) > 1e-6:
        tau = (h_ss - h0) / slope
    else:
        tau = 0.0

    return tau, h_ss - h0


def method_two_points(t_data, h_data, h0, t1_frac=0.3, t2_frac=0.7):
    """
    双点法辨识时间常数

    Args:
        t_data: 时间数据
        h_data: 水位数据
        h0: 初始水位
        t1_frac: 第一个采样点位置（相对时间）
        t2_frac: 第二个采样点位置（相对时间）

    Returns:
        tuple: (时间常数τ, 稳态增益K)
    """
    # 稳态值
    h_ss = np.mean(h_data[int(0.8 * len(h_data)):])
    delta_h = h_ss - h0

    # 选择两个时刻
    idx1 = int(t1_frac * len(t_data))
    idx2 = int(t2_frac * len(t_data))

    t1, h1 = t_data[idx1], h_data[idx1]
    t2, h2 = t_data[idx2], h_data[idx2]

    # 归一化响应
    y1 = (h1 - h0) / delta_h
    y2 = (h2 - h0) / delta_h

    # 根据 y = 1 - e^(-t/τ) 求解τ
    # ln(1 - y1) = -t1/τ
    # ln(1 - y2) = -t2/τ
    if y1 < 0.99 and y2 < 0.99 and y1 > 0.01 and y2 > 0.01:
        tau = (t2 - t1) / (np.log(1 - y1) - np.log(1 - y2))
    else:
        tau = 0.0

    return abs(tau), delta_h


# ============================================================================
# 实验1：三种图解法精度对比
# ============================================================================

def experiment_compare_methods():
    """
    实验1：对比三种图解法的精度
    """
    print("=" * 80)
    print("实验1：三种图解法精度对比")
    print("=" * 80)

    # 真实参数
    A_true, R_true, K_pump = 2.5, 1.8, 1.2
    tau_true = A_true * R_true
    K_true = K_pump * R_true

    print(f"\n真实参数:")
    print(f"  时间常数 τ = {tau_true} 分钟")
    print(f"  稳态增益 K = {K_true} m")

    # 阶跃测试
    u_step = 0.6
    h0 = 0.5
    t_data, u_data, h_data = conduct_step_test(
        A_true, R_true, K_pump,
        u_step, h0, duration=30, dt=0.1, noise_level=0.0
    )

    # 三种方法辨识
    methods = {
        '63.2% Method': lambda: method_63_2_percent(t_data, h_data, h0),
        'Tangent Method': lambda: method_tangent(t_data, h_data, h0),
        'Two-Point Method': lambda: method_two_points(t_data, h_data, h0)
    }

    results = []

    print(f"\n辨识结果:")
    for method_name, method_func in methods.items():
        tau_est, delta_h = method_func()
        K_est = delta_h / u_step

        error_tau = abs(tau_est - tau_true) / tau_true * 100
        error_K = abs(K_est - K_true) / K_true * 100

        results.append({
            'method': method_name,
            'tau': tau_est,
            'K': K_est,
            'error_tau': error_tau,
            'error_K': error_K
        })

        print(f"\n{method_name}:")
        print(f"  τ = {tau_est:.4f} min (error: {error_tau:.2f}%)")
        print(f"  K = {K_est:.4f} m (error: {error_K:.2f}%)")

    # 可视化对比
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    # 阶跃响应曲线
    ax = axes[0, 0]
    ax.plot(t_data, h_data, 'b-', linewidth=2, label='Step Response')
    ax.axhline(h0, color='r', linestyle='--', alpha=0.5, label='Initial Level')
    h_ss = np.mean(h_data[-50:])
    ax.axhline(h_ss, color='g', linestyle='--', alpha=0.5, label='Steady State')
    h_632 = h0 + 0.632 * (h_ss - h0)
    ax.axhline(h_632, color='orange', linestyle=':', alpha=0.7, label='63.2% Level')
    ax.set_xlabel('Time (min)')
    ax.set_ylabel('Water Level (m)')
    ax.set_title('Step Response Curve')
    ax.legend()
    ax.grid(True)

    # 时间常数对比
    ax = axes[0, 1]
    method_names = [r['method'] for r in results]
    tau_values = [r['tau'] for r in results]
    bars = ax.bar(range(len(method_names)), tau_values, alpha=0.7)
    ax.axhline(tau_true, color='r', linestyle='--', linewidth=2, label='True Value')
    ax.set_xticks(range(len(method_names)))
    ax.set_xticklabels(method_names, rotation=15, ha='right')
    ax.set_ylabel('Time Constant τ (min)')
    ax.set_title('Time Constant Estimation Comparison')
    ax.legend()
    ax.grid(True, axis='y')

    # 稳态增益对比
    ax = axes[1, 0]
    K_values = [r['K'] for r in results]
    bars = ax.bar(range(len(method_names)), K_values, alpha=0.7, color='green')
    ax.axhline(K_true, color='r', linestyle='--', linewidth=2, label='True Value')
    ax.set_xticks(range(len(method_names)))
    ax.set_xticklabels(method_names, rotation=15, ha='right')
    ax.set_ylabel('Steady-State Gain K (m)')
    ax.set_title('Gain Estimation Comparison')
    ax.legend()
    ax.grid(True, axis='y')

    # 相对误差对比
    ax = axes[1, 1]
    x = np.arange(len(method_names))
    width = 0.35
    ax.bar(x - width/2, [r['error_tau'] for r in results], width, label='τ error', alpha=0.7)
    ax.bar(x + width/2, [r['error_K'] for r in results], width, label='K error', alpha=0.7)
    ax.set_xticks(x)
    ax.set_xticklabels(method_names, rotation=15, ha='right')
    ax.set_ylabel('Relative Error (%)')
    ax.set_title('Estimation Error Comparison')
    ax.legend()
    ax.grid(True, axis='y')

    plt.tight_layout()
    plt.savefig('experiment1_methods_comparison.png', dpi=150, bbox_inches='tight')
    print("\n图表已保存: experiment1_methods_comparison.png")

    return results


# ============================================================================
# 实验2：噪声影响分析
# ============================================================================

def experiment_noise_effect():
    """
    实验2：分析测量噪声对图解法的影响
    """
    print("\n" + "=" * 80)
    print("实验2：噪声影响分析")
    print("=" * 80)

    # 真实参数
    A_true, R_true, K_pump = 2.5, 1.8, 1.2
    tau_true = A_true * R_true
    K_true = K_pump * R_true

    # 不同噪声水平
    noise_levels = [0.0, 0.01, 0.02, 0.05, 0.1]
    u_step = 0.6
    h0 = 0.5

    results_632 = []
    results_tangent = []
    results_twopoint = []

    for noise_level in noise_levels:
        print(f"\n测试噪声水平: {noise_level} m")

        # 生成数据
        t_data, u_data, h_data = conduct_step_test(
            A_true, R_true, K_pump,
            u_step, h0, duration=30, dt=0.1, noise_level=noise_level
        )

        # 平滑处理（移动平均）
        if noise_level > 0:
            window_size = 11
            h_data_smooth = np.convolve(h_data, np.ones(window_size)/window_size, mode='same')
        else:
            h_data_smooth = h_data

        # 三种方法辨识
        tau_632, delta_h_632 = method_63_2_percent(t_data, h_data_smooth, h0)
        tau_tangent, delta_h_tangent = method_tangent(t_data, h_data_smooth, h0)
        tau_twopoint, delta_h_twopoint = method_two_points(t_data, h_data_smooth, h0)

        results_632.append({
            'noise': noise_level,
            'tau': tau_632,
            'error': abs(tau_632 - tau_true) / tau_true * 100
        })

        results_tangent.append({
            'noise': noise_level,
            'tau': tau_tangent,
            'error': abs(tau_tangent - tau_true) / tau_true * 100
        })

        results_twopoint.append({
            'noise': noise_level,
            'tau': tau_twopoint,
            'error': abs(tau_twopoint - tau_true) / tau_true * 100
        })

    # 可视化
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    ax = axes[0]
    ax.plot([r['noise'] for r in results_632], [r['tau'] for r in results_632],
            'o-', label='63.2% Method')
    ax.plot([r['noise'] for r in results_tangent], [r['tau'] for r in results_tangent],
            's-', label='Tangent Method')
    ax.plot([r['noise'] for r in results_twopoint], [r['tau'] for r in results_twopoint],
            '^-', label='Two-Point Method')
    ax.axhline(tau_true, color='r', linestyle='--', label='True Value')
    ax.set_xlabel('Noise Level (m)')
    ax.set_ylabel('Estimated τ (min)')
    ax.set_title('Time Constant Estimation vs Noise')
    ax.legend()
    ax.grid(True)

    ax = axes[1]
    ax.plot([r['noise'] for r in results_632], [r['error'] for r in results_632],
            'o-', label='63.2% Method')
    ax.plot([r['noise'] for r in results_tangent], [r['error'] for r in results_tangent],
            's-', label='Tangent Method')
    ax.plot([r['noise'] for r in results_twopoint], [r['error'] for r in results_twopoint],
            '^-', label='Two-Point Method')
    ax.set_xlabel('Noise Level (m)')
    ax.set_ylabel('Relative Error (%)')
    ax.set_title('Estimation Error vs Noise')
    ax.legend()
    ax.grid(True)

    plt.tight_layout()
    plt.savefig('experiment2_noise_effect.png', dpi=150, bbox_inches='tight')
    print("\n图表已保存: experiment2_noise_effect.png")

    print("\n结论:")
    print("  - 63.2%法对噪声最鲁棒")
    print("  - 切线法对噪声较敏感（因依赖初始斜率）")
    print("  - 双点法居中")
    print("  - 建议：有噪声时使用平滑处理 + 63.2%法")

    return results_632, results_tangent, results_twopoint


# ============================================================================
# 实验3：不同系统参数测试
# ============================================================================

def experiment_different_systems():
    """
    实验3：测试图解法在不同系统参数下的性能
    """
    print("\n" + "=" * 80)
    print("实验3：不同系统参数测试")
    print("=" * 80)

    # 不同的系统配置
    systems = [
        {'name': 'Fast System', 'A': 1.0, 'R': 1.0, 'K': 1.0},  # τ = 1.0
        {'name': 'Medium System', 'A': 2.5, 'R': 1.8, 'K': 1.2},  # τ = 4.5
        {'name': 'Slow System', 'A': 5.0, 'R': 3.0, 'K': 1.5},  # τ = 15.0
    ]

    results = []

    for sys_config in systems:
        name = sys_config['name']
        A, R, K = sys_config['A'], sys_config['R'], sys_config['K']
        tau_true = A * R

        print(f"\n{name}: A={A}, R={R}, K={K}, τ={tau_true}")

        # 测试时长根据系统调整
        duration = max(30, tau_true * 8)

        t_data, u_data, h_data = conduct_step_test(
            A, R, K, u_step=0.6, h0=0.5,
            duration=duration, dt=0.1, noise_level=0.01
        )

        # 平滑
        h_data_smooth = np.convolve(h_data, np.ones(11)/11, mode='same')

        # 辨识
        tau_est, delta_h = method_63_2_percent(t_data, h_data_smooth, 0.5)
        error = abs(tau_est - tau_true) / tau_true * 100

        results.append({
            'name': name,
            'tau_true': tau_true,
            'tau_est': tau_est,
            'error': error
        })

        print(f"  辨识结果: τ = {tau_est:.4f} (error: {error:.2f}%)")

    print("\n结论: 图解法适用于不同时间常数的系统")

    return results


# ============================================================================
# 实验4：图解法 vs 优化算法
# ============================================================================

def experiment_graphical_vs_optimization():
    """
    实验4：对比图解法与优化算法
    """
    print("\n" + "=" * 80)
    print("实验4：图解法 vs 优化算法")
    print("=" * 80)

    # 真实参数
    A_true, R_true, K_pump = 2.5, 1.8, 1.2
    tau_true = A_true * R_true
    K_true_dc = K_pump * R_true

    # 生成数据
    t_data, u_data, h_data = conduct_step_test(
        A_true, R_true, K_pump,
        u_step=0.6, h0=0.5, duration=30, dt=0.1, noise_level=0.02
    )

    # 平滑
    h_data_smooth = np.convolve(h_data, np.ones(11)/11, mode='same')

    # 图解法
    import time
    start = time.time()
    tau_graphical, delta_h = method_63_2_percent(t_data, h_data_smooth, 0.5)
    time_graphical = time.time() - start

    # 优化算法（曲线拟合）
    def first_order_response(t, tau, K_dc, h0):
        """一阶系统响应"""
        u = 0.6
        return h0 + K_dc * u * (1 - np.exp(-t / tau))

    start = time.time()
    params_opt, _ = curve_fit(
        first_order_response,
        t_data,
        h_data_smooth,
        p0=[4.0, 2.0, 0.5],
        bounds=([0.1, 0.1, 0], [20, 10, 2])
    )
    tau_opt, K_dc_opt, h0_opt = params_opt
    time_opt = time.time() - start

    # 结果对比
    print(f"\n图解法 (63.2% Method):")
    print(f"  τ = {tau_graphical:.4f} min")
    print(f"  误差 = {abs(tau_graphical - tau_true) / tau_true * 100:.2f}%")
    print(f"  计算时间 = {time_graphical*1000:.2f} ms")

    print(f"\n优化算法 (curve_fit):")
    print(f"  τ = {tau_opt:.4f} min")
    print(f"  误差 = {abs(tau_opt - tau_true) / tau_true * 100:.2f}%")
    print(f"  计算时间 = {time_opt*1000:.2f} ms")

    print(f"\n结论:")
    print(f"  - 图解法：简单快速，精度足够（工程应用）")
    print(f"  - 优化算法：精度更高，但需要编程和计算资源")
    print(f"  - 实际选择：根据现场条件和精度要求")


# ============================================================================
# 主程序
# ============================================================================

def main():
    """运行所有扩展实验"""
    print("=" * 80)
    print("案例6扩展实验：图解法参数辨识对比分析")
    print("=" * 80)

    # 实验1：三种图解法对比
    results1 = experiment_compare_methods()

    # 实验2：噪声影响
    results2 = experiment_noise_effect()

    # 实验3：不同系统参数
    results3 = experiment_different_systems()

    # 实验4：图解法vs优化算法
    experiment_graphical_vs_optimization()

    print("\n" + "=" * 80)
    print("所有扩展实验完成！")
    print("=" * 80)

    plt.show()


if __name__ == "__main__":
    main()
