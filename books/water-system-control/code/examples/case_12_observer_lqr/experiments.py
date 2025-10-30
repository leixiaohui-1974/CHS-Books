#!/usr/bin/env python3
"""
案例12扩展实验：观测器与LQR深入研究

本文件包含扩展实验：
1. 双水箱系统的LQR控制
2. 观测器极点速度对噪声敏感性的影响
3. LQR鲁棒性分析

作者：CHS-Books项目
日期：2025-10-30
版本：1.0
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from scipy import linalg
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parents[3]
sys.path.insert(0, str(project_root))

# 设置matplotlib
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


# ============================================================================
# 实验1：双水箱系统的LQR控制
# ============================================================================

def experiment_two_tank_lqr():
    """
    实验1：双水箱系统的LQR最优控制
    """
    print("=" * 80)
    print("实验1：双水箱系统的LQR控制")
    print("=" * 80)

    # 双水箱参数
    A1, A2 = 2.5, 2.0
    R1, R2 = 1.5, 2.0
    K = 1.2

    # 状态空间模型
    A = np.array([
        [-1/(A1*R1),        0      ],
        [ 1/(A2*R1),  -1/(A2*R2)   ]
    ])

    B = np.array([
        [K/A1],
        [0   ]
    ])

    C = np.array([[0, 1]])  # 测量下游水位
    D = np.array([[0]])

    print("\n[双水箱系统]")
    print(f"A = \n{A}")
    print(f"B = \n{B.flatten()}")
    print(f"C = {C.flatten()}")

    # LQR设计
    Q = np.diag([1.0, 10.0])  # 更重视下游水位
    R = np.array([[0.1]])

    print(f"\n[LQR设计]")
    print(f"Q = \n{Q}")
    print(f"R = {R[0,0]}")

    # 求解Riccati方程
    P = linalg.solve_continuous_are(A, B, Q, R)
    K_lqr = linalg.inv(R) @ B.T @ P

    print(f"\n反馈增益 K = {K_lqr.flatten()}")

    # 闭环系统
    A_cl = A - B @ K_lqr
    poles_cl = np.linalg.eigvals(A_cl)

    print(f"\n闭环极点：")
    for i, p in enumerate(poles_cl):
        print(f"  极点{i+1} = {p:.4f}")

    # 仿真
    dt = 0.1
    t = np.arange(0, 50, dt)

    # 参考值
    r = np.array([[3.0], [2.0]])  # 期望状态

    # 状态初值
    x = np.zeros((len(t), 2))
    x[0, :] = [1.0, 0.5]

    u = np.zeros(len(t))

    for i in range(1, len(t)):
        u[i-1] = (-K_lqr @ (x[i-1, :].reshape(-1, 1) - r))[0, 0]
        dx = A @ x[i-1, :] + B.flatten() * u[i-1]
        x[i, :] = x[i-1, :] + dx * dt

    # 可视化
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))

    # 状态轨迹
    axes[0, 0].plot(t, x[:, 0], 'b-', linewidth=2, label='h1 (Upper)')
    axes[0, 0].plot(t, x[:, 1], 'r-', linewidth=2, label='h2 (Lower)')
    axes[0, 0].axhline(r[0, 0], color='b', linestyle='--', alpha=0.3)
    axes[0, 0].axhline(r[1, 0], color='r', linestyle='--', alpha=0.3)
    axes[0, 0].set_xlabel('Time (min)')
    axes[0, 0].set_ylabel('Water Level (m)')
    axes[0, 0].set_title('State Trajectories')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)

    # 控制输入
    axes[0, 1].plot(t, u, 'k-', linewidth=2)
    axes[0, 1].set_xlabel('Time (min)')
    axes[0, 1].set_ylabel('Control Input u')
    axes[0, 1].set_title('Control Signal')
    axes[0, 1].grid(True, alpha=0.3)

    # 极点位置
    axes[1, 0].plot(poles_cl.real, poles_cl.imag, 'rs', markersize=12, label='Closed Loop')
    poles_open = np.linalg.eigvals(A)
    axes[1, 0].plot(poles_open.real, poles_open.imag, 'bo', markersize=12, label='Open Loop')
    axes[1, 0].axvline(0, color='r', linestyle='--', alpha=0.5)
    axes[1, 0].axhline(0, color='k', linestyle='-', linewidth=0.5)
    axes[1, 0].set_xlabel('Real Part')
    axes[1, 0].set_ylabel('Imaginary Part')
    axes[1, 0].set_title('Pole Locations')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)

    # 误差
    error = np.sqrt((x[:, 0] - r[0, 0])**2 + (x[:, 1] - r[1, 0])**2)
    axes[1, 1].plot(t, error, 'k-', linewidth=2)
    axes[1, 1].set_xlabel('Time (min)')
    axes[1, 1].set_ylabel('Tracking Error')
    axes[1, 1].set_title('State Error Norm')
    axes[1, 1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('exp1_two_tank_lqr.png', dpi=150, bbox_inches='tight')
    print("\n图表已保存：exp1_two_tank_lqr.png")

    print("\n结论：")
    print("  - LQR自然处理多变量系统")
    print("  - 通过Q矩阵权衡不同状态的重要性")
    print("  - 自动协调多个控制目标")


# ============================================================================
# 实验2：观测器速度与噪声敏感性
# ============================================================================

def experiment_observer_noise_sensitivity():
    """
    实验2：观测器极点速度对噪声敏感性的影响
    """
    print("\n" + "=" * 80)
    print("实验2：观测器速度与噪声敏感性")
    print("=" * 80)

    # 系统参数
    A_tank = 2.5
    R = 1.8
    K_pump = 1.2

    A = np.array([[-1/(A_tank * R)]])
    B = np.array([[K_pump / A_tank]])
    C = np.array([[1.0]])

    pole_system = A[0, 0]

    print("\n[测试不同观测器速度]")

    # 不同的观测器极点
    observer_speeds = [2, 4, 8, 16]  # 系统极点的倍数
    colors = ['blue', 'green', 'orange', 'red']

    dt = 0.1
    t = np.arange(0, 20, dt)

    # 真实状态（有初值误差）
    x_true = np.zeros(len(t))
    x_true[0] = 1.0
    u = np.ones(len(t)) * 0.5

    # 测量噪声
    np.random.seed(42)
    noise_std = 0.05  # 5cm测量噪声
    noise = np.random.normal(0, noise_std, len(t))

    for i in range(1, len(t)):
        dx = A[0, 0] * x_true[i-1] + B[0, 0] * u[i-1]
        x_true[i] = x_true[i-1] + dx * dt

    # 带噪声的测量
    y_noisy = C[0, 0] * x_true + noise

    fig, axes = plt.subplots(2, 2, figsize=(12, 8))

    for idx, speed in enumerate(observer_speeds):
        # 观测器设计
        pole_obs = speed * pole_system
        L = (A[0, 0] - pole_obs) / C[0, 0]

        # 观测器仿真
        x_est = np.zeros(len(t))
        x_est[0] = 0.0  # 初值误差

        for i in range(1, len(t)):
            y_est = C[0, 0] * x_est[i-1]
            dx_est = A[0, 0] * x_est[i-1] + B[0, 0] * u[i-1] + L * (y_noisy[i-1] - y_est)
            x_est[i] = x_est[i-1] + dx_est * dt

        # 估计误差
        error = x_true - x_est

        # 可视化
        axes[0, 0].plot(t, x_est, color=colors[idx], linewidth=2,
                       label=f'{speed}x speed', alpha=0.7)
        axes[0, 1].plot(t, error, color=colors[idx], linewidth=2,
                       label=f'{speed}x speed', alpha=0.7)

    # 真实状态
    axes[0, 0].plot(t, x_true, 'k--', linewidth=2, label='True State', alpha=0.5)
    axes[0, 0].set_xlabel('Time (min)')
    axes[0, 0].set_ylabel('State Estimate')
    axes[0, 0].set_title('Observer Estimates (with Noise)')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)

    axes[0, 1].axhline(0, color='k', linestyle='--', alpha=0.5)
    axes[0, 1].set_xlabel('Time (min)')
    axes[0, 1].set_ylabel('Estimation Error')
    axes[0, 1].set_title('Estimation Errors')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)

    # 噪声测量
    axes[1, 0].plot(t, y_noisy, 'gray', linewidth=1, alpha=0.5, label='Noisy Measurement')
    axes[1, 0].plot(t, x_true, 'k-', linewidth=2, label='True State')
    axes[1, 0].set_xlabel('Time (min)')
    axes[1, 0].set_ylabel('Measurement')
    axes[1, 0].set_title(f'Noisy Measurements (σ={noise_std}m)')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)

    # 误差标准差对比
    std_errors = []
    for idx, speed in enumerate(observer_speeds):
        pole_obs = speed * pole_system
        L = (A[0, 0] - pole_obs) / C[0, 0]

        x_est = np.zeros(len(t))
        x_est[0] = 0.0

        for i in range(1, len(t)):
            y_est = C[0, 0] * x_est[i-1]
            dx_est = A[0, 0] * x_est[i-1] + B[0, 0] * u[i-1] + L * (y_noisy[i-1] - y_est)
            x_est[i] = x_est[i-1] + dx_est * dt

        # 稳态后的误差标准差（后半段）
        error_steady = (x_true - x_est)[len(t)//2:]
        std_errors.append(np.std(error_steady))

    axes[1, 1].bar(range(len(observer_speeds)), std_errors,
                   tick_label=[f'{s}x' for s in observer_speeds],
                   color=colors, alpha=0.7)
    axes[1, 1].set_xlabel('Observer Speed')
    axes[1, 1].set_ylabel('Steady-State Error Std')
    axes[1, 1].set_title('Noise Sensitivity vs Speed')
    axes[1, 1].grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig('exp2_observer_noise.png', dpi=150, bbox_inches='tight')
    print("\n图表已保存：exp2_observer_noise.png")

    print("\n[误差标准差]")
    for i, speed in enumerate(observer_speeds):
        print(f"  {speed}x速度：σ_error = {std_errors[i]:.4f} m")

    print("\n结论：")
    print("  - 观测器越快，收敛越快")
    print("  - 但快速观测器对噪声更敏感")
    print("  - 需要在收敛速度和噪声抑制间权衡")
    print("  - 典型选择：控制器极点的2-4倍")


# ============================================================================
# 实验3：LQR鲁棒性分析
# ============================================================================

def experiment_lqr_robustness():
    """
    实验3：LQR对参数不确定性的鲁棒性
    """
    print("\n" + "=" * 80)
    print("实验3：LQR鲁棒性分析")
    print("=" * 80)

    # 标称系统
    A_tank_nom = 2.5
    R_nom = 1.8
    K_nom = 1.2

    A_nom = np.array([[-1/(A_tank_nom * R_nom)]])
    B_nom = np.array([[K_nom / A_tank_nom]])

    # 基于标称模型设计LQR
    Q = np.array([[1.0]])
    R_lqr = np.array([[0.1]])

    P = linalg.solve_continuous_are(A_nom, B_nom, Q, R_lqr)
    K_lqr = linalg.inv(R_lqr) @ B_nom.T @ P

    print(f"\n[标称系统LQR设计]")
    print(f"  K_lqr = {K_lqr[0,0]:.4f}")
    print(f"  标称闭环极点 = {(A_nom - B_nom @ K_lqr)[0,0]:.4f}")

    # 测试参数变化
    print("\n[测试参数不确定性]")

    variations = np.linspace(0.5, 1.5, 21)  # ±50%
    results = {'A_var': [], 'R_var': [], 'K_var': []}

    dt = 0.1
    t = np.arange(0, 30, dt)
    r = 2.0  # 参考值

    # 变化A
    for factor in variations:
        A_tank = A_tank_nom * factor
        A = np.array([[-1/(A_tank * R_nom)]])
        B = np.array([[K_nom / A_tank]])

        # 使用标称K_lqr控制真实系统
        x = np.zeros(len(t))
        x[0] = 0.5
        u = np.zeros(len(t))

        for i in range(1, len(t)):
            u[i-1] = -K_lqr[0, 0] * (x[i-1] - r)
            dx = A[0, 0] * x[i-1] + B[0, 0] * u[i-1]
            x[i] = x[i-1] + dx * dt

        # 性能指标
        error = np.abs(x - r)
        idx_settle = np.where(error <= 0.1)[0]
        t_settle = t[idx_settle[0]] if len(idx_settle) > 0 else t[-1]

        results['A_var'].append(t_settle)

    # 变化R
    for factor in variations:
        R_param = R_nom * factor
        A = np.array([[-1/(A_tank_nom * R_param)]])
        B = np.array([[K_nom / A_tank_nom]])

        x = np.zeros(len(t))
        x[0] = 0.5

        for i in range(1, len(t)):
            u_val = -K_lqr[0, 0] * (x[i-1] - r)
            dx = A[0, 0] * x[i-1] + B[0, 0] * u_val
            x[i] = x[i-1] + dx * dt

        error = np.abs(x - r)
        idx_settle = np.where(error <= 0.1)[0]
        t_settle = t[idx_settle[0]] if len(idx_settle) > 0 else t[-1]

        results['R_var'].append(t_settle)

    # 可视化
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    axes[0].plot(variations * 100, results['A_var'], 'o-', linewidth=2, label='A variation')
    axes[0].axvline(100, color='r', linestyle='--', alpha=0.5, label='Nominal')
    axes[0].set_xlabel('Parameter Variation (%)')
    axes[0].set_ylabel('Settling Time (min)')
    axes[0].set_title('Robustness: A Variation')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(variations * 100, results['R_var'], 's-', linewidth=2, label='R variation', color='green')
    axes[1].axvline(100, color='r', linestyle='--', alpha=0.5, label='Nominal')
    axes[1].set_xlabel('Parameter Variation (%)')
    axes[1].set_ylabel('Settling Time (min)')
    axes[1].set_title('Robustness: R Variation')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('exp3_lqr_robustness.png', dpi=150, bbox_inches='tight')
    print("\n图表已保存：exp3_lqr_robustness.png")

    print("\n结论：")
    print("  - LQR对参数变化有一定鲁棒性")
    print("  - 在±50%参数变化下系统仍稳定")
    print("  - 性能随参数变化有所降低但可接受")
    print("  - LQR固有的稳定裕度提供鲁棒性保证")


# ============================================================================
# 主程序
# ============================================================================

def main():
    """运行所有扩展实验"""
    print("=" * 80)
    print("案例12扩展实验：观测器与LQR深入研究")
    print("=" * 80)

    # 实验1：双水箱LQR
    experiment_two_tank_lqr()

    # 实验2：观测器噪声敏感性
    experiment_observer_noise_sensitivity()

    # 实验3：LQR鲁棒性
    experiment_lqr_robustness()

    print("\n" + "=" * 80)
    print("所有扩展实验完成！")
    print("=" * 80)

    plt.show()


if __name__ == "__main__":
    main()
