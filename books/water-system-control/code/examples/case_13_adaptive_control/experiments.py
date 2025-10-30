#!/usr/bin/env python3
"""
案例13扩展实验：自适应控制深入研究

本文件包含扩展实验：
1. 自适应增益对MRAC性能的影响
2. 遗忘因子对RLS的影响
3. 测量噪声对参数估计的影响

作者：CHS-Books项目
日期：2025-10-30
版本：1.0
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parents[3]
sys.path.insert(0, str(project_root))

# 设置matplotlib
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


# ============================================================================
# 实验1：自适应增益对MRAC性能的影响
# ============================================================================

def experiment_mrac_gain_effect():
    """
    实验1：不同自适应增益对MRAC收敛速度和稳定性的影响
    """
    print("=" * 80)
    print("实验1：自适应增益对MRAC性能的影响")
    print("=" * 80)

    # 真实系统
    A_true, R_true, K_true = 3.0, 2.0, 1.0

    # 参考模型
    am, bm = 0.5, 0.5

    # 测试不同的增益
    gamma_values = [0.1, 0.5, 1.0, 2.0]

    print("\n[测试不同自适应增益]")

    dt = 0.1
    t = np.arange(0, 50, dt)
    r = 2.0

    fig, axes = plt.subplots(2, 2, figsize=(12, 8))

    for idx, gamma in enumerate(gamma_values):
        # 状态
        y = np.zeros(len(t))
        ym = np.zeros(len(t))
        y[0] = 0.5
        ym[0] = 0.5

        # 自适应参数
        theta1 = np.zeros(len(t))
        theta2 = np.zeros(len(t))
        theta1[0] = 0.1
        theta2[0] = 0.1

        u = np.zeros(len(t))
        e = np.zeros(len(t))

        for i in range(1, len(t)):
            # 控制律
            u[i-1] = theta1[i-1] * r + theta2[i-1] * y[i-1]

            # 实际系统
            dy = -y[i-1] / (A_true * R_true) + K_true / A_true * u[i-1]
            y[i] = y[i-1] + dy * dt

            # 参考模型
            dym = -am * ym[i-1] + bm * r
            ym[i] = ym[i-1] + dym * dt

            # 误差
            e[i] = y[i] - ym[i]

            # MIT规则
            dtheta1 = -gamma * e[i] * r
            dtheta2 = -gamma * e[i] * y[i]

            theta1[i] = theta1[i-1] + dtheta1 * dt
            theta2[i] = theta2[i-1] + dtheta2 * dt

        # 性能指标
        settling_idx = np.where(np.abs(e) <= 0.05)[0]
        settling_time = t[settling_idx[0]] if len(settling_idx) > 0 else t[-1]

        # 可视化
        axes[0, 0].plot(t, y, linewidth=2, label=f'γ={gamma}')
        axes[0, 1].plot(t, e, linewidth=2, label=f'γ={gamma}')
        axes[1, 0].plot(t, theta1, linewidth=2, label=f'γ={gamma}')
        axes[1, 1].plot(t, theta2, linewidth=2, label=f'γ={gamma}')

        print(f"\nγ = {gamma}:")
        print(f"  稳定时间: {settling_time:.2f} min")
        print(f"  最终θ1: {theta1[-1]:.4f}, θ2: {theta2[-1]:.4f}")

    # 参考模型输出
    axes[0, 0].plot(t, ym, 'k--', linewidth=2, alpha=0.5, label='Ref Model')
    axes[0, 0].set_xlabel('Time (min)')
    axes[0, 0].set_ylabel('Output y')
    axes[0, 0].set_title('System Output')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)

    axes[0, 1].axhline(0, color='k', linestyle='--', alpha=0.3)
    axes[0, 1].set_xlabel('Time (min)')
    axes[0, 1].set_ylabel('Tracking Error e')
    axes[0, 1].set_title('Tracking Error')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)

    axes[1, 0].set_xlabel('Time (min)')
    axes[1, 0].set_ylabel('θ1')
    axes[1, 0].set_title('Parameter θ1 Evolution')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)

    axes[1, 1].set_xlabel('Time (min)')
    axes[1, 1].set_ylabel('θ2')
    axes[1, 1].set_title('Parameter θ2 Evolution')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('exp1_mrac_gain_effect.png', dpi=150, bbox_inches='tight')
    print("\n图表已保存：exp1_mrac_gain_effect.png")

    print("\n结论：")
    print("  - γ太小：收敛慢")
    print("  - γ适中：性能最好")
    print("  - γ太大：可能振荡或不稳定")
    print("  - 需要在收敛速度和稳定性间权衡")


# ============================================================================
# 实验2：遗忘因子对RLS的影响
# ============================================================================

def experiment_forgetting_factor():
    """
    实验2：遗忘因子对RLS参数估计的影响
    """
    print("\n" + "=" * 80)
    print("实验2：遗忘因子对RLS的影响")
    print("=" * 80)

    # 真实系统（时变参数）
    def get_params(t):
        if t < 25:
            a, b = -0.167, 0.333  # 初始参数
        else:
            a, b = -0.2, 0.25  # 参数突变
        return a, b

    print("\n[时变系统]")
    print("  t < 25: a = -0.167, b = 0.333")
    print("  t ≥ 25: a = -0.200, b = 0.250 (参数突变)")

    # 测试不同的遗忘因子
    lambda_values = [0.95, 0.98, 0.995, 1.0]

    print("\n[测试不同遗忘因子]")

    dt = 0.1
    t = np.arange(0, 50, dt)

    # 激励信号
    u = np.sin(0.2 * t) + 0.5 * np.sin(0.5 * t) + 1.0

    fig, axes = plt.subplots(2, 2, figsize=(12, 8))

    for idx, lambda_rls in enumerate(lambda_values):
        # 真实系统输出
        y = np.zeros(len(t))
        y[0] = 0.0

        for i in range(1, len(t)):
            a_true, b_true = get_params(t[i])
            dy = a_true * y[i-1] + b_true * u[i-1]
            y[i] = y[i-1] + dy * dt

        # RLS估计
        theta_hat = np.zeros((len(t), 2))
        theta_hat[0, :] = [0.0, 0.0]
        P = np.eye(2) * 100

        for k in range(1, len(t)):
            phi = np.array([y[k-1], u[k-1]])
            y_pred = phi @ theta_hat[k-1, :]
            error = y[k] - y_pred

            K_rls = P @ phi / (lambda_rls + phi @ P @ phi)
            theta_hat[k, :] = theta_hat[k-1, :] + K_rls * error
            P = (np.eye(2) - np.outer(K_rls, phi)) @ P / lambda_rls

        # 可视化
        axes[0, 0].plot(t, theta_hat[:, 0], linewidth=2, label=f'λ={lambda_rls}')
        axes[0, 1].plot(t, theta_hat[:, 1], linewidth=2, label=f'λ={lambda_rls}')

        # 估计误差
        a_true_vec = np.array([get_params(ti)[0] for ti in t])
        b_true_vec = np.array([get_params(ti)[1] for ti in t])

        error_a = theta_hat[:, 0] - a_true_vec
        error_b = theta_hat[:, 1] - b_true_vec

        axes[1, 0].plot(t, error_a, linewidth=2, label=f'λ={lambda_rls}')
        axes[1, 1].plot(t, error_b, linewidth=2, label=f'λ={lambda_rls}')

        print(f"\nλ = {lambda_rls}:")
        print(f"  t=24时估计: a={theta_hat[240, 0]:.4f}, b={theta_hat[240, 1]:.4f}")
        print(f"  t=49时估计: a={theta_hat[-1, 0]:.4f}, b={theta_hat[-1, 1]:.4f}")

    # 真实参数
    a_true_vec = np.array([get_params(ti)[0] for ti in t])
    b_true_vec = np.array([get_params(ti)[1] for ti in t])

    axes[0, 0].plot(t, a_true_vec, 'k--', linewidth=2, alpha=0.7, label='True a')
    axes[0, 0].axvline(25, color='r', linestyle=':', alpha=0.5)
    axes[0, 0].set_xlabel('Time (min)')
    axes[0, 0].set_ylabel('Parameter a')
    axes[0, 0].set_title('Estimation of a')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)

    axes[0, 1].plot(t, b_true_vec, 'k--', linewidth=2, alpha=0.7, label='True b')
    axes[0, 1].axvline(25, color='r', linestyle=':', alpha=0.5)
    axes[0, 1].set_xlabel('Time (min)')
    axes[0, 1].set_ylabel('Parameter b')
    axes[0, 1].set_title('Estimation of b')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)

    axes[1, 0].axhline(0, color='k', linestyle='--', alpha=0.3)
    axes[1, 0].axvline(25, color='r', linestyle=':', alpha=0.5)
    axes[1, 0].set_xlabel('Time (min)')
    axes[1, 0].set_ylabel('Estimation Error')
    axes[1, 0].set_title('Error in a')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)

    axes[1, 1].axhline(0, color='k', linestyle='--', alpha=0.3)
    axes[1, 1].axvline(25, color='r', linestyle=':', alpha=0.5)
    axes[1, 1].set_xlabel('Time (min)')
    axes[1, 1].set_ylabel('Estimation Error')
    axes[1, 1].set_title('Error in b')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('exp2_forgetting_factor.png', dpi=150, bbox_inches='tight')
    print("\n图表已保存：exp2_forgetting_factor.png")

    print("\n结论：")
    print("  - λ = 1.0：无遗忘，参数突变后跟踪慢")
    print("  - λ < 1：有遗忘，能快速跟踪时变参数")
    print("  - λ太小：对噪声敏感，估计可能漂移")
    print("  - λ太大：跟踪时变参数慢")
    print("  - 典型选择：λ = 0.95 ~ 0.99")


# ============================================================================
# 实验3：测量噪声对参数估计的影响
# ============================================================================

def experiment_noise_effect():
    """
    实验3：测量噪声对RLS参数估计的影响
    """
    print("\n" + "=" * 80)
    print("实验3：测量噪声对参数估计的影响")
    print("=" * 80)

    # 真实系统
    a_true, b_true = -0.167, 0.333

    print(f"\n[真实参数]")
    print(f"  a = {a_true:.4f}, b = {b_true:.4f}")

    # 测试不同噪声水平
    noise_levels = [0.0, 0.02, 0.05, 0.10]

    print("\n[测试不同噪声水平]")

    dt = 0.1
    t = np.arange(0, 40, dt)

    # 激励信号
    u = np.sin(0.2 * t) + 0.5 * np.sin(0.5 * t) + 1.0

    fig, axes = plt.subplots(2, 2, figsize=(12, 8))

    for noise_std in noise_levels:
        # 真实系统输出
        y = np.zeros(len(t))
        y[0] = 0.0

        for i in range(1, len(t)):
            dy = a_true * y[i-1] + b_true * u[i-1]
            y[i] = y[i-1] + dy * dt

        # 添加噪声
        np.random.seed(42)
        noise = np.random.normal(0, noise_std, len(t))
        y_meas = y + noise

        # RLS估计
        lambda_rls = 0.98
        theta_hat = np.zeros((len(t), 2))
        theta_hat[0, :] = [0.0, 0.0]
        P = np.eye(2) * 100

        for k in range(1, len(t)):
            phi = np.array([y_meas[k-1], u[k-1]])
            y_pred = phi @ theta_hat[k-1, :]
            error = y_meas[k] - y_pred

            K_rls = P @ phi / (lambda_rls + phi @ P @ phi)
            theta_hat[k, :] = theta_hat[k-1, :] + K_rls * error
            P = (np.eye(2) - np.outer(K_rls, phi)) @ P / lambda_rls

        # 可视化
        label = f'σ={noise_std:.2f}' if noise_std > 0 else 'No noise'
        axes[0, 0].plot(t, theta_hat[:, 0], linewidth=2, label=label)
        axes[0, 1].plot(t, theta_hat[:, 1], linewidth=2, label=label)

        # 估计误差
        error_a = theta_hat[:, 0] - a_true
        error_b = theta_hat[:, 1] - b_true

        axes[1, 0].plot(t, error_a, linewidth=2, label=label)
        axes[1, 1].plot(t, error_b, linewidth=2, label=label)

        # 稳态误差（后半段）
        steady_error_a = np.std(error_a[len(t)//2:])
        steady_error_b = np.std(error_b[len(t)//2:])

        print(f"\n噪声水平 σ = {noise_std:.2f}:")
        print(f"  最终估计: a={theta_hat[-1,0]:.4f}, b={theta_hat[-1,1]:.4f}")
        print(f"  稳态误差std: a={steady_error_a:.4f}, b={steady_error_b:.4f}")

    # 真实值
    axes[0, 0].axhline(a_true, color='k', linestyle='--', linewidth=2, alpha=0.7, label='True a')
    axes[0, 0].set_xlabel('Time (min)')
    axes[0, 0].set_ylabel('Parameter a')
    axes[0, 0].set_title('Estimation of a with Different Noise')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)

    axes[0, 1].axhline(b_true, color='k', linestyle='--', linewidth=2, alpha=0.7, label='True b')
    axes[0, 1].set_xlabel('Time (min)')
    axes[0, 1].set_ylabel('Parameter b')
    axes[0, 1].set_title('Estimation of b with Different Noise')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)

    axes[1, 0].axhline(0, color='k', linestyle='--', alpha=0.3)
    axes[1, 0].set_xlabel('Time (min)')
    axes[1, 0].set_ylabel('Estimation Error')
    axes[1, 0].set_title('Error in a')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)

    axes[1, 1].axhline(0, color='k', linestyle='--', alpha=0.3)
    axes[1, 1].set_xlabel('Time (min)')
    axes[1, 1].set_ylabel('Estimation Error')
    axes[1, 1].set_title('Error in b')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('exp3_noise_effect.png', dpi=150, bbox_inches='tight')
    print("\n图表已保存：exp3_noise_effect.png")

    print("\n结论：")
    print("  - 无噪声：参数估计精确收敛")
    print("  - 小噪声：估计在真值附近小幅波动")
    print("  - 大噪声：估计偏差增大，需要更长时间收敛")
    print("  - 实际应用需考虑噪声影响，可能需要滤波")


# ============================================================================
# 主程序
# ============================================================================

def main():
    """运行所有扩展实验"""
    print("=" * 80)
    print("案例13扩展实验：自适应控制深入研究")
    print("=" * 80)

    # 实验1：MRAC增益影响
    experiment_mrac_gain_effect()

    # 实验2：遗忘因子影响
    experiment_forgetting_factor()

    # 实验3：噪声影响
    experiment_noise_effect()

    print("\n" + "=" * 80)
    print("所有扩展实验完成！")
    print("=" * 80)

    plt.show()


if __name__ == "__main__":
    main()
