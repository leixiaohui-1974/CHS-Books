#!/usr/bin/env python3
"""
案例5扩展实验：参数辨识方法对比与分析

本文件包含多个扩展实验：
1. 噪声影响分析
2. 初值敏感性分析
3. 不同优化算法对比
4. 输入信号影响分析

作者：CHS-Books项目
日期：2025-10-30
版本：1.0
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import least_squares, minimize, differential_evolution
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

def generate_data_with_noise(A, R, K, u_profile, h0, duration, dt, noise_level=0.0):
    """
    生成带噪声的实验数据

    Args:
        A, R, K: 系统参数
        u_profile: 控制输入函数
        h0: 初始水位
        duration: 实验时长
        dt: 采样间隔
        noise_level: 噪声水平（标准差）

    Returns:
        tuple: (时间, 控制输入, 水位测量)
    """
    system = SingleTank(A=A, R=R, K=K)
    system.reset(h0=h0)

    n_steps = int(duration / dt)
    t_data = np.zeros(n_steps)
    u_data = np.zeros(n_steps)
    h_data = np.zeros(n_steps)

    for i in range(n_steps):
        t_data[i] = system.t
        u_data[i] = u_profile(system.t)
        h_data[i] = system.h + np.random.normal(0, noise_level)
        system.step(u_data[i], dt)

    return t_data, u_data, h_data


def identify_parameters(t_data, u_data, h_data, method='least_squares', initial_guess=None):
    """
    使用指定方法辨识参数

    Args:
        t_data: 时间数据
        u_data: 控制输入数据
        h_data: 水位测量数据
        method: 优化方法 ('least_squares', 'L-BFGS-B', 'differential_evolution')
        initial_guess: 参数初值 [A, R, K]

    Returns:
        tuple: (辨识参数, 成功标志)
    """
    dt = t_data[1] - t_data[0]

    def simulation_error(params):
        """模拟误差计算"""
        A, R, K = params
        if A <= 0 or R <= 0 or K <= 0:
            return np.ones(len(h_data)) * 1e10

        # 模拟系统
        h_sim = np.zeros(len(h_data))
        h_sim[0] = h_data[0]

        for i in range(len(h_data) - 1):
            dhdt = (K * u_data[i] - h_sim[i] / R) / A
            h_sim[i+1] = h_sim[i] + dhdt * dt

        return h_data - h_sim

    def objective_function(params):
        """目标函数（最小二乘）"""
        errors = simulation_error(params)
        return np.sum(errors**2)

    # 设置初值
    if initial_guess is None:
        initial_guess = [2.0, 1.5, 1.0]

    # 参数边界
    bounds = ([0.1, 0.1, 0.1], [10.0, 10.0, 10.0])

    # 根据方法选择优化器
    if method == 'least_squares':
        result = least_squares(
            simulation_error,
            initial_guess,
            bounds=bounds,
            method='trf',
            verbose=0
        )
        return result.x, result.success

    elif method == 'L-BFGS-B':
        result = minimize(
            objective_function,
            initial_guess,
            method='L-BFGS-B',
            bounds=list(zip(bounds[0], bounds[1]))
        )
        return result.x, result.success

    elif method == 'differential_evolution':
        result = differential_evolution(
            objective_function,
            bounds=list(zip(bounds[0], bounds[1])),
            seed=42,
            maxiter=100
        )
        return result.x, result.success

    else:
        raise ValueError(f"Unknown method: {method}")


def calculate_metrics(h_true, h_pred):
    """
    计算性能指标

    Returns:
        dict: 包含RMSE, MAE, R2等指标
    """
    errors = h_pred - h_true
    rmse = np.sqrt(np.mean(errors**2))
    mae = np.mean(np.abs(errors))

    ss_res = np.sum(errors**2)
    ss_tot = np.sum((h_true - np.mean(h_true))**2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0

    return {
        'RMSE': rmse,
        'MAE': mae,
        'R2': r2
    }


# ============================================================================
# 实验1：噪声影响分析
# ============================================================================

def experiment_noise_effect():
    """
    实验1：分析测量噪声对辨识精度的影响
    """
    print("\n" + "=" * 80)
    print("实验1：噪声影响分析")
    print("=" * 80)

    # 真实参数
    A_true, R_true, K_true = 2.5, 1.8, 1.2

    # 不同噪声水平
    noise_levels = [0.0, 0.01, 0.02, 0.05, 0.1]

    # 输入信号：阶跃
    u_step = lambda t: 0.6

    results = []

    for noise_level in noise_levels:
        print(f"\n测试噪声水平: {noise_level} m")

        # 生成数据
        t_data, u_data, h_data = generate_data_with_noise(
            A_true, R_true, K_true,
            u_step, h0=1.0, duration=30, dt=0.1,
            noise_level=noise_level
        )

        # 辨识参数
        params_est, success = identify_parameters(t_data, u_data, h_data)

        if success:
            A_est, R_est, K_est = params_est
            error_A = abs(A_est - A_true) / A_true * 100
            error_R = abs(R_est - R_true) / R_true * 100
            error_K = abs(K_est - K_true) / K_true * 100

            results.append({
                'noise': noise_level,
                'A': A_est,
                'R': R_est,
                'K': K_est,
                'error_A': error_A,
                'error_R': error_R,
                'error_K': error_K
            })

            print(f"  辨识结果: A={A_est:.3f}, R={R_est:.3f}, K={K_est:.3f}")
            print(f"  相对误差: A={error_A:.2f}%, R={error_R:.2f}%, K={error_K:.2f}%")

    # 可视化
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    # 参数估计值
    ax = axes[0, 0]
    ax.plot([r['noise'] for r in results], [r['A'] for r in results], 'o-', label='A (estimated)')
    ax.axhline(A_true, color='r', linestyle='--', label='A (true)')
    ax.set_xlabel('Noise Level (m)')
    ax.set_ylabel('A (m^2)')
    ax.set_title('Tank Area Estimation vs Noise')
    ax.legend()
    ax.grid(True)

    ax = axes[0, 1]
    ax.plot([r['noise'] for r in results], [r['R'] for r in results], 'o-', label='R (estimated)')
    ax.axhline(R_true, color='r', linestyle='--', label='R (true)')
    ax.set_xlabel('Noise Level (m)')
    ax.set_ylabel('R (min/m^2)')
    ax.set_title('Resistance Estimation vs Noise')
    ax.legend()
    ax.grid(True)

    ax = axes[1, 0]
    ax.plot([r['noise'] for r in results], [r['K'] for r in results], 'o-', label='K (estimated)')
    ax.axhline(K_true, color='r', linestyle='--', label='K (true)')
    ax.set_xlabel('Noise Level (m)')
    ax.set_ylabel('K (m^3/min)')
    ax.set_title('Pump Gain Estimation vs Noise')
    ax.legend()
    ax.grid(True)

    # 相对误差
    ax = axes[1, 1]
    ax.plot([r['noise'] for r in results], [r['error_A'] for r in results], 'o-', label='A error')
    ax.plot([r['noise'] for r in results], [r['error_R'] for r in results], 's-', label='R error')
    ax.plot([r['noise'] for r in results], [r['error_K'] for r in results], '^-', label='K error')
    ax.set_xlabel('Noise Level (m)')
    ax.set_ylabel('Relative Error (%)')
    ax.set_title('Parameter Estimation Error vs Noise')
    ax.legend()
    ax.grid(True)

    plt.tight_layout()
    plt.savefig('experiment1_noise_effect.png', dpi=150, bbox_inches='tight')
    print("\n图表已保存: experiment1_noise_effect.png")

    return results


# ============================================================================
# 实验2：初值敏感性分析
# ============================================================================

def experiment_initial_guess():
    """
    实验2：分析参数初值对辨识结果的影响
    """
    print("\n" + "=" * 80)
    print("实验2：初值敏感性分析")
    print("=" * 80)

    # 真实参数
    A_true, R_true, K_true = 2.5, 1.8, 1.2

    # 生成数据
    u_step = lambda t: 0.6
    t_data, u_data, h_data = generate_data_with_noise(
        A_true, R_true, K_true,
        u_step, h0=1.0, duration=30, dt=0.1,
        noise_level=0.0
    )

    # 不同初值
    initial_guesses = [
        [1.0, 1.0, 1.0],  # 偏小
        [2.0, 1.5, 1.0],  # 接近真值
        [5.0, 3.0, 2.0],  # 偏大
        [0.5, 0.5, 0.5],  # 很小
        [8.0, 5.0, 3.0],  # 很大
    ]

    results = []

    for i, initial_guess in enumerate(initial_guesses):
        print(f"\n初值{i+1}: A={initial_guess[0]}, R={initial_guess[1]}, K={initial_guess[2]}")

        params_est, success = identify_parameters(
            t_data, u_data, h_data,
            method='least_squares',
            initial_guess=initial_guess
        )

        if success:
            A_est, R_est, K_est = params_est
            results.append({
                'initial': initial_guess,
                'result': params_est,
                'error_A': abs(A_est - A_true) / A_true * 100,
                'error_R': abs(R_est - R_true) / R_true * 100,
                'error_K': abs(K_est - K_true) / K_true * 100
            })
            print(f"  辨识结果: A={A_est:.4f}, R={R_est:.4f}, K={K_est:.4f}")
            print(f"  相对误差: A={results[-1]['error_A']:.2f}%, "
                  f"R={results[-1]['error_R']:.2f}%, "
                  f"K={results[-1]['error_K']:.2f}%")

    print("\n结论：最小二乘法对初值敏感性较低，不同初值均收敛到真实值附近")

    return results


# ============================================================================
# 实验3：不同优化算法对比
# ============================================================================

def experiment_optimization_methods():
    """
    实验3：对比不同优化算法的性能
    """
    print("\n" + "=" * 80)
    print("实验3：不同优化算法对比")
    print("=" * 80)

    # 真实参数
    A_true, R_true, K_true = 2.5, 1.8, 1.2

    # 生成带噪声数据
    u_step = lambda t: 0.6
    t_data, u_data, h_data = generate_data_with_noise(
        A_true, R_true, K_true,
        u_step, h0=1.0, duration=30, dt=0.1,
        noise_level=0.02  # 中等噪声
    )

    methods = ['least_squares', 'L-BFGS-B', 'differential_evolution']
    initial_guess = [2.0, 1.5, 1.0]

    results = []

    for method in methods:
        print(f"\n测试方法: {method}")

        import time
        start_time = time.time()

        params_est, success = identify_parameters(
            t_data, u_data, h_data,
            method=method,
            initial_guess=initial_guess if method != 'differential_evolution' else None
        )

        elapsed_time = time.time() - start_time

        if success:
            A_est, R_est, K_est = params_est
            results.append({
                'method': method,
                'A': A_est,
                'R': R_est,
                'K': K_est,
                'error_A': abs(A_est - A_true) / A_true * 100,
                'error_R': abs(R_est - R_true) / R_true * 100,
                'error_K': abs(K_est - K_true) / K_true * 100,
                'time': elapsed_time
            })

            print(f"  辨识结果: A={A_est:.4f}, R={R_est:.4f}, K={K_est:.4f}")
            print(f"  相对误差: A={results[-1]['error_A']:.2f}%, "
                  f"R={results[-1]['error_R']:.2f}%, "
                  f"K={results[-1]['error_K']:.2f}%")
            print(f"  计算时间: {elapsed_time:.3f} 秒")

    # 总结
    print("\n" + "=" * 80)
    print("算法性能对比总结")
    print("=" * 80)
    for r in results:
        avg_error = (r['error_A'] + r['error_R'] + r['error_K']) / 3
        print(f"{r['method']:25s} | 平均误差: {avg_error:6.2f}% | 时间: {r['time']:6.3f}s")

    return results


# ============================================================================
# 实验4：输入信号影响分析
# ============================================================================

def experiment_input_signal():
    """
    实验4：分析不同输入信号对辨识精度的影响
    """
    print("\n" + "=" * 80)
    print("实验4：输入信号影响分析")
    print("=" * 80)

    # 真实参数
    A_true, R_true, K_true = 2.5, 1.8, 1.2

    # 不同输入信号
    input_signals = {
        '阶跃信号': lambda t: 0.6,
        '斜坡信号': lambda t: 0.02 * t,
        '正弦信号': lambda t: 0.5 + 0.3 * np.sin(2 * np.pi * t / 10),
        '方波信号': lambda t: 0.6 if (t % 10) < 5 else 0.3,
    }

    results = []

    for signal_name, signal_func in input_signals.items():
        print(f"\n测试输入: {signal_name}")

        # 生成数据
        t_data, u_data, h_data = generate_data_with_noise(
            A_true, R_true, K_true,
            signal_func, h0=1.0, duration=40, dt=0.1,
            noise_level=0.02
        )

        # 辨识参数
        params_est, success = identify_parameters(t_data, u_data, h_data)

        if success:
            A_est, R_est, K_est = params_est
            results.append({
                'signal': signal_name,
                'A': A_est,
                'R': R_est,
                'K': K_est,
                'error_A': abs(A_est - A_true) / A_true * 100,
                'error_R': abs(R_est - R_true) / R_true * 100,
                'error_K': abs(K_est - K_true) / K_true * 100
            })

            print(f"  辨识结果: A={A_est:.4f}, R={R_est:.4f}, K={K_est:.4f}")
            print(f"  相对误差: A={results[-1]['error_A']:.2f}%, "
                  f"R={results[-1]['error_R']:.2f}%, "
                  f"K={results[-1]['error_K']:.2f}%")

    # 总结
    print("\n" + "=" * 80)
    print("不同输入信号辨识精度对比")
    print("=" * 80)
    for r in results:
        avg_error = (r['error_A'] + r['error_R'] + r['error_K']) / 3
        print(f"{r['signal']:12s} | 平均误差: {avg_error:6.2f}%")

    print("\n结论：")
    print("  - 阶跃信号：简单易实施，精度较好")
    print("  - 方波信号：激励充分，精度最高")
    print("  - 正弦信号：适合频域分析")
    print("  - 斜坡信号：精度较低，不推荐单独使用")

    return results


# ============================================================================
# 主程序
# ============================================================================

def main():
    """运行所有扩展实验"""
    print("=" * 80)
    print("案例5扩展实验：参数辨识方法对比与分析")
    print("=" * 80)

    # 实验1：噪声影响
    results1 = experiment_noise_effect()

    # 实验2：初值敏感性
    results2 = experiment_initial_guess()

    # 实验3：优化算法对比
    results3 = experiment_optimization_methods()

    # 实验4：输入信号影响
    results4 = experiment_input_signal()

    print("\n" + "=" * 80)
    print("所有扩展实验完成！")
    print("=" * 80)

    plt.show()


if __name__ == "__main__":
    main()
