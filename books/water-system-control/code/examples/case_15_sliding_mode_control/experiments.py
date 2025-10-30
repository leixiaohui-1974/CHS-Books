#!/usr/bin/env python3
"""
案例15扩展实验：滑模控制深入研究

本文件包含扩展实验：
1. 切换增益对性能的影响
2. 边界层厚度优化
3. 不同滑模面参数对比

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


def sat(x, delta=1.0):
    """饱和函数"""
    return np.clip(x / delta, -1.0, 1.0)


# ============================================================================
# 实验1：切换增益影响
# ============================================================================

def experiment_switching_gain():
    """
    实验1：不同切换增益对收敛速度和抖振的影响
    """
    print("=" * 80)
    print("实验1：切换增益影响")
    print("=" * 80)

    # 系统参数
    A_true, R_true, K_true = 3.0, 2.0, 1.0
    A_nom, R_nom, K_nom = 2.5, 1.8, 1.2

    # 测试不同的切换增益
    k_values = [0.5, 1.0, 2.0, 4.0]

    print("\n[测试不同切换增益k]")

    dt = 0.1
    t = np.arange(0, 30, dt)
    r = 2.0

    lambda_smc = 1.0
    phi = 0.1

    fig, axes = plt.subplots(2, 2, figsize=(12, 8))

    for k_switch in k_values:
        y = np.zeros(len(t))
        y[0] = 0.5
        u = np.zeros(len(t))
        s = np.zeros(len(t))
        e_int = 0.0

        for i in range(1, len(t)):
            e = r - y[i-1]
            e_int += e * dt
            s[i-1] = e + lambda_smc * e_int

            ueq = (y[i-1] / (A_nom * R_nom) + lambda_smc * e) * A_nom / K_nom
            usw = k_switch * sat(s[i-1], phi)
            u[i-1] = np.clip(ueq + usw, 0.0, 2.0)

            dy = -y[i-1] / (A_true * R_true) + K_true / A_true * u[i-1]
            y[i] = y[i-1] + dy * dt

        # 性能指标
        reaching_idx = np.where(np.abs(s) < 0.05)[0]
        reaching_time = t[reaching_idx[0]] if len(reaching_idx) > 0 else t[-1]

        u_diff = np.diff(u)
        chattering = np.std(u_diff)

        # 可视化
        axes[0, 0].plot(t, y, linewidth=2, label=f'k={k_switch}')
        axes[0, 1].plot(t, s, linewidth=2, label=f'k={k_switch}')
        axes[1, 0].plot(t, u, linewidth=2, label=f'k={k_switch}', alpha=0.7)

        print(f"\nk = {k_switch}:")
        print(f"  到达时间: {reaching_time:.2f} min")
        print(f"  抖振程度: {chattering:.4f}")

    # 图表设置
    axes[0, 0].axhline(r, color='r', linestyle='--', alpha=0.5)
    axes[0, 0].set_xlabel('Time (min)')
    axes[0, 0].set_ylabel('Output y')
    axes[0, 0].set_title('System Output')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)

    axes[0, 1].axhline(0, color='k', linestyle='--', alpha=0.3)
    axes[0, 1].set_xlabel('Time (min)')
    axes[0, 1].set_ylabel('Sliding Surface s')
    axes[0, 1].set_title('Sliding Surface')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)

    axes[1, 0].set_xlabel('Time (min)')
    axes[1, 0].set_ylabel('Control Input u')
    axes[1, 0].set_title('Control Signal')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)

    # 性能对比柱状图
    reaching_times = []
    chatterings = []
    for k_switch in k_values:
        y = np.zeros(len(t))
        y[0] = 0.5
        u = np.zeros(len(t))
        s = np.zeros(len(t))
        e_int = 0.0

        for i in range(1, len(t)):
            e = r - y[i-1]
            e_int += e * dt
            s[i-1] = e + lambda_smc * e_int

            ueq = (y[i-1] / (A_nom * R_nom) + lambda_smc * e) * A_nom / K_nom
            usw = k_switch * sat(s[i-1], phi)
            u[i-1] = np.clip(ueq + usw, 0.0, 2.0)

            dy = -y[i-1] / (A_true * R_true) + K_true / A_true * u[i-1]
            y[i] = y[i-1] + dy * dt

        reaching_idx = np.where(np.abs(s) < 0.05)[0]
        reaching_time = t[reaching_idx[0]] if len(reaching_idx) > 0 else t[-1]
        reaching_times.append(reaching_time)

        u_diff = np.diff(u)
        chatterings.append(np.std(u_diff))

    x_pos = np.arange(len(k_values))
    axes[1, 1].bar(x_pos, reaching_times, alpha=0.7)
    axes[1, 1].set_xlabel('Switching Gain k')
    axes[1, 1].set_ylabel('Reaching Time (min)')
    axes[1, 1].set_title('Convergence Speed')
    axes[1, 1].set_xticks(x_pos)
    axes[1, 1].set_xticklabels([f'{k}' for k in k_values])
    axes[1, 1].grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig('exp1_switching_gain.png', dpi=150, bbox_inches='tight')
    print("\n图表已保存：exp1_switching_gain.png")

    print("\n结论：")
    print("  - k越大：收敛越快，但抖振越严重")
    print("  - k越小：控制平滑，但收敛慢")
    print("  - 需要在速度和抖振间权衡")
    print("  - 推荐：k = 1.0 ~ 2.0")


# ============================================================================
# 实验2：边界层厚度优化
# ============================================================================

def experiment_boundary_layer():
    """
    实验2：边界层厚度对性能的影响
    """
    print("\n" + "=" * 80)
    print("实验2：边界层厚度优化")
    print("=" * 80)

    # 系统参数
    A_true, R_true, K_true = 3.0, 2.0, 1.0
    A_nom, R_nom, K_nom = 2.5, 1.8, 1.2

    # 测试不同的边界层厚度
    phi_values = [0.01, 0.05, 0.1, 0.2]

    print("\n[测试不同边界层厚度φ]")

    dt = 0.1
    t = np.arange(0, 30, dt)
    r = 2.0

    lambda_smc = 1.0
    k_switch = 2.0

    fig, axes = plt.subplots(2, 2, figsize=(12, 8))

    for phi in phi_values:
        y = np.zeros(len(t))
        y[0] = 0.5
        u = np.zeros(len(t))
        e_int = 0.0

        for i in range(1, len(t)):
            e = r - y[i-1]
            e_int += e * dt
            s = e + lambda_smc * e_int

            ueq = (y[i-1] / (A_nom * R_nom) + lambda_smc * e) * A_nom / K_nom
            usw = k_switch * sat(s, phi)
            u[i-1] = np.clip(ueq + usw, 0.0, 2.0)

            dy = -y[i-1] / (A_true * R_true) + K_true / A_true * u[i-1]
            y[i] = y[i-1] + dy * dt

        # 性能指标
        steady_error = np.abs(y[-50:] - r).mean()
        u_diff = np.diff(u)
        chattering = np.std(u_diff)

        # 可视化
        axes[0, 0].plot(t, y, linewidth=2, label=f'φ={phi}')
        axes[0, 1].plot(t, u, linewidth=2, label=f'φ={phi}', alpha=0.7)

        print(f"\nφ = {phi}:")
        print(f"  稳态误差: {steady_error:.4f} m")
        print(f"  抖振程度: {chattering:.4f}")

    # 图表设置
    axes[0, 0].axhline(r, color='r', linestyle='--', alpha=0.5)
    axes[0, 0].set_xlabel('Time (min)')
    axes[0, 0].set_ylabel('Output y')
    axes[0, 0].set_title('Output with Different φ')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)

    axes[0, 1].set_xlabel('Time (min)')
    axes[0, 1].set_ylabel('Control Input u')
    axes[0, 1].set_title('Control Signal')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)

    # 性能指标对比
    errors = []
    chatterings = []

    for phi in phi_values:
        y = np.zeros(len(t))
        y[0] = 0.5
        u = np.zeros(len(t))
        e_int = 0.0

        for i in range(1, len(t)):
            e = r - y[i-1]
            e_int += e * dt
            s = e + lambda_smc * e_int

            ueq = (y[i-1] / (A_nom * R_nom) + lambda_smc * e) * A_nom / K_nom
            usw = k_switch * sat(s, phi)
            u[i-1] = np.clip(ueq + usw, 0.0, 2.0)

            dy = -y[i-1] / (A_true * R_true) + K_true / A_true * u[i-1]
            y[i] = y[i-1] + dy * dt

        errors.append(np.abs(y[-50:] - r).mean())
        chatterings.append(np.std(np.diff(u)))

    x_pos = np.arange(len(phi_values))

    axes[1, 0].bar(x_pos, errors, alpha=0.7)
    axes[1, 0].set_xlabel('Boundary Layer φ')
    axes[1, 0].set_ylabel('Steady-State Error (m)')
    axes[1, 0].set_title('Tracking Accuracy')
    axes[1, 0].set_xticks(x_pos)
    axes[1, 0].set_xticklabels([f'{p}' for p in phi_values])
    axes[1, 0].grid(True, alpha=0.3, axis='y')

    axes[1, 1].bar(x_pos, chatterings, alpha=0.7, color='orange')
    axes[1, 1].set_xlabel('Boundary Layer φ')
    axes[1, 1].set_ylabel('Chattering (std)')
    axes[1, 1].set_title('Control Smoothness')
    axes[1, 1].set_xticks(x_pos)
    axes[1, 1].set_xticklabels([f'{p}' for p in phi_values])
    axes[1, 1].grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig('exp2_boundary_layer.png', dpi=150, bbox_inches='tight')
    print("\n图表已保存：exp2_boundary_layer.png")

    print("\n结论：")
    print("  - φ越小：跟踪精度高，但抖振大")
    print("  - φ越大：控制平滑，但精度降低")
    print("  - 存在最优折衷值")
    print("  - 推荐：φ = 0.05 ~ 0.1")


# ============================================================================
# 实验3：滑模面参数影响
# ============================================================================

def experiment_sliding_surface():
    """
    实验3：滑模面参数λ对性能的影响
    """
    print("\n" + "=" * 80)
    print("实验3：滑模面参数影响")
    print("=" * 80)

    # 系统参数
    A_true, R_true, K_true = 3.0, 2.0, 1.0
    A_nom, R_nom, K_nom = 2.5, 1.8, 1.2

    # 测试不同的λ值
    lambda_values = [0.5, 1.0, 2.0, 4.0]

    print("\n[测试不同滑模面参数λ]")

    dt = 0.1
    t = np.arange(0, 30, dt)
    r = 2.0

    k_switch = 2.0
    phi = 0.1

    fig, axes = plt.subplots(2, 2, figsize=(12, 8))

    for lambda_smc in lambda_values:
        y = np.zeros(len(t))
        y[0] = 0.5
        u = np.zeros(len(t))
        s = np.zeros(len(t))
        e_int = 0.0

        for i in range(1, len(t)):
            e = r - y[i-1]
            e_int += e * dt
            s[i-1] = e + lambda_smc * e_int

            ueq = (y[i-1] / (A_nom * R_nom) + lambda_smc * e) * A_nom / K_nom
            usw = k_switch * sat(s[i-1], phi)
            u[i-1] = np.clip(ueq + usw, 0.0, 2.0)

            dy = -y[i-1] / (A_true * R_true) + K_true / A_true * u[i-1]
            y[i] = y[i-1] + dy * dt

        # 性能指标
        idx_95 = np.where(np.abs(y - r) <= 0.05 * r)[0]
        settling_time = t[idx_95[0]] if len(idx_95) > 0 else t[-1]

        # 可视化
        axes[0, 0].plot(t, y, linewidth=2, label=f'λ={lambda_smc}')
        axes[0, 1].plot(t, s, linewidth=2, label=f'λ={lambda_smc}')
        axes[1, 0].plot(t, u, linewidth=2, label=f'λ={lambda_smc}', alpha=0.7)

        print(f"\nλ = {lambda_smc}:")
        print(f"  稳定时间: {settling_time:.2f} min")

    # 图表设置
    axes[0, 0].axhline(r, color='r', linestyle='--', alpha=0.5)
    axes[0, 0].set_xlabel('Time (min)')
    axes[0, 0].set_ylabel('Output y')
    axes[0, 0].set_title('System Output')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)

    axes[0, 1].axhline(0, color='k', linestyle='--', alpha=0.3)
    axes[0, 1].set_xlabel('Time (min)')
    axes[0, 1].set_ylabel('Sliding Surface s')
    axes[0, 1].set_title('Sliding Surface Evolution')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)

    axes[1, 0].set_xlabel('Time (min)')
    axes[1, 0].set_ylabel('Control Input u')
    axes[1, 0].set_title('Control Signal')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)

    # 稳定时间对比
    settling_times = []
    for lambda_smc in lambda_values:
        y = np.zeros(len(t))
        y[0] = 0.5
        u = np.zeros(len(t))
        e_int = 0.0

        for i in range(1, len(t)):
            e = r - y[i-1]
            e_int += e * dt
            s = e + lambda_smc * e_int

            ueq = (y[i-1] / (A_nom * R_nom) + lambda_smc * e) * A_nom / K_nom
            usw = k_switch * sat(s, phi)
            u[i-1] = np.clip(ueq + usw, 0.0, 2.0)

            dy = -y[i-1] / (A_true * R_true) + K_true / A_true * u[i-1]
            y[i] = y[i-1] + dy * dt

        idx_95 = np.where(np.abs(y - r) <= 0.05 * r)[0]
        settling_time = t[idx_95[0]] if len(idx_95) > 0 else t[-1]
        settling_times.append(settling_time)

    axes[1, 1].bar(range(len(lambda_values)), settling_times, alpha=0.7)
    axes[1, 1].set_xlabel('λ Parameter')
    axes[1, 1].set_ylabel('Settling Time (min)')
    axes[1, 1].set_title('Convergence Speed')
    axes[1, 1].set_xticks(range(len(lambda_values)))
    axes[1, 1].set_xticklabels([f'{l}' for l in lambda_values])
    axes[1, 1].grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig('exp3_sliding_surface.png', dpi=150, bbox_inches='tight')
    print("\n图表已保存：exp3_sliding_surface.png")

    print("\n结论：")
    print("  - λ越大：收敛越快，控制越激进")
    print("  - λ越小：响应平缓，控制温和")
    print("  - λ影响滑模面的斜率")
    print("  - 推荐：λ = 0.5 ~ 2.0")


# ============================================================================
# 主程序
# ============================================================================

def main():
    """运行所有扩展实验"""
    print("=" * 80)
    print("案例15扩展实验：滑模控制深入研究")
    print("=" * 80)

    # 实验1：切换增益影响
    experiment_switching_gain()

    # 实验2：边界层厚度
    experiment_boundary_layer()

    # 实验3：滑模面参数
    experiment_sliding_surface()

    print("\n" + "=" * 80)
    print("所有扩展实验完成！")
    print("=" * 80)

    plt.show()


if __name__ == "__main__":
    main()
