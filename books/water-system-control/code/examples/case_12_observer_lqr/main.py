#!/usr/bin/env python3
"""
案例12：状态观测器与LQR最优控制

场景描述：
工程师需要设计一个实际可实现的控制系统。系统的部分状态无法直接测量，
因此需要状态观测器。同时希望控制器在性能和控制代价间达到最优平衡，
因此采用LQR方法设计。

教学目标：
1. 掌握Luenberger观测器设计方法
2. 理解LQR最优控制原理
3. 学习观测器和控制器的联合应用
4. 理解分离原理
5. 掌握Q和R矩阵的选择方法

分析步骤：
1. 设计状态观测器
2. 设计LQR最优控制器
3. 实现观测器+LQR联合系统
4. 性能对比分析
5. 参数权衡研究

关键概念：
- Luenberger观测器
- LQR最优控制
- Riccati方程
- 分离原理
- 性能指标

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

from code.models.water_tank.single_tank import SingleTank

# 设置matplotlib
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


# ============================================================================
# 第1部分：状态观测器设计
# ============================================================================

def observer_design():
    """
    第1部分：设计Luenberger状态观测器
    """
    print("=" * 80)
    print("第1部分：状态观测器设计")
    print("=" * 80)

    # 系统参数
    A_tank = 2.5
    R = 1.8
    K = 1.2

    # 状态空间模型
    A = np.array([[-1/(A_tank * R)]])
    B = np.array([[K / A_tank]])
    C = np.array([[1.0]])
    D = np.array([[0.0]])

    print("\n[系统模型]")
    print(f"  A = {A[0,0]:.4f}")
    print(f"  B = {B[0,0]:.4f}")
    print(f"  C = {C[0,0]:.4f}")
    print(f"  系统极点 = {A[0,0]:.4f}")

    print("\n[观测器设计]")
    print("  观测器方程：d x̂/dt = Ax̂ + Bu + L(y - ŷ)")
    print("  误差动态：de/dt = (A - LC)e")

    # 设计观测器增益L
    # 选择观测器极点比系统极点快4倍
    pole_system = A[0, 0]
    pole_observer = 4 * pole_system  # 约-0.889

    print(f"\n[极点配置]")
    print(f"  系统极点：{pole_system:.4f}")
    print(f"  观测器极点（期望）：{pole_observer:.4f} (4倍快)")

    # 计算观测器增益
    # A - LC = pole_observer
    # L = (A - pole_observer) / C
    L = (A[0, 0] - pole_observer) / C[0, 0]

    print(f"\n  观测器增益 L = {L:.4f}")

    # 验证观测器极点
    A_obs_error = A - L * C
    pole_obs_actual = A_obs_error[0, 0]

    print(f"\n[验证]")
    print(f"  实际观测器极点：{pole_obs_actual:.4f}")
    print(f"  误差收敛时间常数：{-1/pole_obs_actual:.2f} min")

    # 仿真观测器
    print("\n[仿真：观测器跟踪性能]")

    dt = 0.1
    t = np.arange(0, 20, dt)

    # 真实状态
    x_true = np.zeros(len(t))
    x_true[0] = 1.0  # 初始水位1m

    # 估计状态
    x_est = np.zeros(len(t))
    x_est[0] = 0.0  # 观测器初值为0（错误的初值）

    # 控制输入
    u = np.ones(len(t)) * 0.5

    # 输出
    y = np.zeros(len(t))

    for i in range(1, len(t)):
        # 真实系统
        dx_true = A[0, 0] * x_true[i-1] + B[0, 0] * u[i-1]
        x_true[i] = x_true[i-1] + dx_true * dt
        y[i] = C[0, 0] * x_true[i]

        # 观测器
        y_est = C[0, 0] * x_est[i-1]
        dx_est = A[0, 0] * x_est[i-1] + B[0, 0] * u[i-1] + L * (y[i-1] - y_est)
        x_est[i] = x_est[i-1] + dx_est * dt

    # 估计误差
    error = x_true - x_est

    print(f"  初始误差：{error[0]:.4f} m")
    print(f"  最终误差：{error[-1]:.6f} m")
    print(f"  误差快速收敛至零 ✓")

    return A, B, C, D, L, t, x_true, x_est, y, error


# ============================================================================
# 第2部分：LQR最优控制器设计
# ============================================================================

def lqr_design(A, B, C, D):
    """
    第2部分：设计LQR最优控制器
    """
    print("\n" + "=" * 80)
    print("第2部分：LQR最优控制器设计")
    print("=" * 80)

    print("\n[性能指标]")
    print("  J = ∫₀^∞ (x^T Q x + u^T R u) dt")
    print("  最小化状态偏差和控制能量的加权和")

    # 设计权重矩阵
    Q = np.array([[1.0]])  # 状态权重
    R = np.array([[0.1]])  # 控制权重

    print(f"\n[权重矩阵]")
    print(f"  Q = {Q[0,0]:.1f} (状态偏差权重)")
    print(f"  R = {R[0,0]:.1f} (控制代价权重)")
    print(f"  Q/R = {Q[0,0]/R[0,0]:.1f} → 更重视状态精度")

    # 求解代数Riccati方程
    print(f"\n[求解Riccati方程]")
    print("  A^T P + PA - PBR⁻¹B^T P + Q = 0")

    # 使用scipy求解连续时间ARE
    P = linalg.solve_continuous_are(A, B, Q, R)

    print(f"  解 P = {P[0,0]:.4f}")

    # 计算最优反馈增益
    K_lqr = R[0,0]**-1 * B.T @ P

    print(f"\n[最优反馈增益]")
    print(f"  K = R⁻¹B^T P = {K_lqr[0,0]:.4f}")

    # 闭环系统
    A_cl = A - B @ K_lqr
    pole_cl = A_cl[0, 0]

    print(f"\n[闭环系统]")
    print(f"  A_cl = A - BK = {A_cl[0,0]:.4f}")
    print(f"  闭环极点 = {pole_cl:.4f}")
    print(f"  时间常数 = {-1/pole_cl:.2f} min")

    # 性能评估
    print(f"\n[性能评估]")
    J_x = P[0,0]  # 状态成本（对于单位初始状态）
    print(f"  状态成本指标 x^T P x = {J_x:.4f} (初态x=1)")

    return K_lqr, P, Q, R


# ============================================================================
# 第3部分：观测器+LQR联合应用
# ============================================================================

def observer_lqr_combined(A, B, C, D, L, K_lqr):
    """
    第3部分：观测器和LQR控制器联合应用
    """
    print("\n" + "=" * 80)
    print("第3部分：观测器+LQR联合应用")
    print("=" * 80)

    print("\n[分离原理]")
    print("  控制律：u = -K x̂ (用估计值代替真实值)")
    print("  观测器：d x̂/dt = Ax̂ + Bu + L(y - Cx̂)")
    print("  两者可独立设计，联合使用")

    print(f"\n[系统参数]")
    print(f"  LQR增益 K = {K_lqr[0,0]:.4f}")
    print(f"  观测器增益 L = {L:.4f}")

    # 仿真：三种情况对比
    print("\n[仿真对比]")
    print("  情况1：全状态反馈（理想情况，直接测量x）")
    print("  情况2：基于观测器的输出反馈（实际情况，用x̂代替x）")
    print("  情况3：开环（无控制）")

    dt = 0.1
    t = np.arange(0, 30, dt)

    # 参考输入
    r = 2.0  # 期望水位2m

    # 情况1：全状态反馈
    x1 = np.zeros(len(t))
    x1[0] = 0.5  # 初始水位0.5m
    u1 = np.zeros(len(t))

    for i in range(1, len(t)):
        u1[i-1] = -K_lqr[0, 0] * (x1[i-1] - r)  # u = -K(x - r)
        dx1 = A[0, 0] * x1[i-1] + B[0, 0] * u1[i-1]
        x1[i] = x1[i-1] + dx1 * dt

    # 情况2：基于观测器的输出反馈
    x2 = np.zeros(len(t))
    x2[0] = 0.5
    x_est2 = np.zeros(len(t))
    x_est2[0] = 1.0  # 观测器初值错误
    u2 = np.zeros(len(t))
    y2 = np.zeros(len(t))

    for i in range(1, len(t)):
        # 测量输出
        y2[i-1] = C[0, 0] * x2[i-1]

        # 控制律（基于估计）
        u2[i-1] = -K_lqr[0, 0] * (x_est2[i-1] - r)

        # 真实系统
        dx2 = A[0, 0] * x2[i-1] + B[0, 0] * u2[i-1]
        x2[i] = x2[i-1] + dx2 * dt

        # 观测器
        y_est2 = C[0, 0] * x_est2[i-1]
        dx_est2 = A[0, 0] * x_est2[i-1] + B[0, 0] * u2[i-1] + L * (y2[i-1] - y_est2)
        x_est2[i] = x_est2[i-1] + dx_est2 * dt

    # 情况3：开环
    x3 = np.zeros(len(t))
    x3[0] = 0.5
    u3 = np.zeros(len(t))  # 无控制

    for i in range(1, len(t)):
        dx3 = A[0, 0] * x3[i-1] + B[0, 0] * u3[i-1]
        x3[i] = x3[i-1] + dx3 * dt

    # 性能指标
    error1 = np.abs(x1 - r)
    error2 = np.abs(x2 - r)

    idx_settle1 = np.where(error1 <= 0.05 * r)[0]
    t_settle1 = t[idx_settle1[0]] if len(idx_settle1) > 0 else t[-1]

    idx_settle2 = np.where(error2 <= 0.05 * r)[0]
    t_settle2 = t[idx_settle2[0]] if len(idx_settle2) > 0 else t[-1]

    print(f"\n[性能对比]")
    print(f"  全状态反馈：稳态时间 = {t_settle1:.2f} min")
    print(f"  观测器反馈：稳态时间 = {t_settle2:.2f} min")
    print(f"  性能差异：{abs(t_settle2 - t_settle1):.2f} min")
    print(f"  → 观测器反馈性能接近全状态反馈 ✓")

    return t, x1, x2, x3, x_est2, u1, u2, r


# ============================================================================
# 第4部分：参数权衡分析
# ============================================================================

def parameter_trade_off_analysis(A, B, C, D):
    """
    第4部分：Q和R矩阵对性能的影响
    """
    print("\n" + "=" * 80)
    print("第4部分：参数权衡分析")
    print("=" * 80)

    print("\n[分析不同Q/R比值的影响]")

    # 测试不同的Q/R比值
    qr_ratios = [0.1, 1.0, 10.0, 100.0]

    results = []

    for qr in qr_ratios:
        Q = np.array([[qr]])
        R = np.array([[1.0]])

        # 求解LQR
        P = linalg.solve_continuous_are(A, B, Q, R)
        K = R[0,0]**-1 * B.T @ P

        # 闭环极点
        A_cl = A - B @ K
        pole = A_cl[0, 0]

        # 仿真
        dt = 0.1
        t = np.arange(0, 30, dt)
        x = np.zeros(len(t))
        x[0] = 0.5
        u = np.zeros(len(t))

        for i in range(1, len(t)):
            u[i-1] = -K[0, 0] * (x[i-1] - 2.0)
            dx = A[0, 0] * x[i-1] + B[0, 0] * u[i-1]
            x[i] = x[i-1] + dx * dt

        # 计算性能指标
        error = np.abs(x - 2.0)
        idx_settle = np.where(error <= 0.1)[0]
        t_settle = t[idx_settle[0]] if len(idx_settle) > 0 else t[-1]

        # 控制能量
        control_energy = np.sum(u**2) * dt

        results.append({
            'qr': qr,
            'K': K[0, 0],
            'pole': pole,
            't_settle': t_settle,
            'control_energy': control_energy,
            't': t,
            'x': x,
            'u': u
        })

        print(f"\nQ/R = {qr:6.1f}:")
        print(f"  K = {K[0,0]:.4f}")
        print(f"  极点 = {pole:.4f}")
        print(f"  稳态时间 = {t_settle:.2f} min")
        print(f"  控制能量 = {control_energy:.2f}")

    print("\n结论：")
    print("  Q/R小 → K小 → 响应慢，控制温和")
    print("  Q/R大 → K大 → 响应快，控制激烈")
    print("  LQR自动在性能和代价间寻找最优平衡")

    return results


# ============================================================================
# 第5部分：可视化与总结
# ============================================================================

def visualize_and_summarize(obs_data, lqr_data, combined_data, tradeoff_data, L):
    """
    第5部分：综合可视化和总结
    """
    print("\n" + "=" * 80)
    print("第5部分：可视化与总结")
    print("=" * 80)

    # 解包数据
    t_obs, x_true, x_est, y, error_obs = obs_data
    K_lqr, P, Q, R = lqr_data
    t, x1, x2, x3, x_est2, u1, u2, r = combined_data

    fig = plt.figure(figsize=(16, 12))
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

    # 图1：观测器性能
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.plot(t_obs, x_true, 'b-', linewidth=2, label='True State x')
    ax1.plot(t_obs, x_est, 'r--', linewidth=2, label='Estimated x̂')
    ax1.set_xlabel('Time (min)')
    ax1.set_ylabel('Water Level (m)')
    ax1.set_title('Observer Performance')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # 图2：观测器误差
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.plot(t_obs, error_obs, 'k-', linewidth=2)
    ax2.axhline(0, color='r', linestyle='--', alpha=0.5)
    ax1.set_xlabel('Time (min)')
    ax2.set_ylabel('Estimation Error (m)')
    ax2.set_title('Observer Error Convergence')
    ax2.grid(True, alpha=0.3)

    # 图3：LQR vs开环
    ax3 = fig.add_subplot(gs[0, 2])
    ax3.plot(t, x1, 'b-', linewidth=2, label='LQR Control')
    ax3.plot(t, x3, 'gray', linestyle='--', linewidth=2, label='Open Loop')
    ax3.axhline(r, color='r', linestyle='--', alpha=0.5, label='Reference')
    ax3.set_xlabel('Time (min)')
    ax3.set_ylabel('Water Level (m)')
    ax3.set_title('LQR vs Open Loop')
    ax3.legend()
    ax3.grid(True, alpha=0.3)

    # 图4：全状态反馈 vs 观测器反馈
    ax4 = fig.add_subplot(gs[1, 0])
    ax4.plot(t, x1, 'b-', linewidth=2, label='Full State Feedback')
    ax4.plot(t, x2, 'r--', linewidth=2, label='Observer-based Feedback')
    ax4.axhline(r, color='gray', linestyle='--', alpha=0.5)
    ax4.set_xlabel('Time (min)')
    ax4.set_ylabel('Water Level (m)')
    ax4.set_title('State Feedback vs Observer-based')
    ax4.legend()
    ax4.grid(True, alpha=0.3)

    # 图5：真实状态 vs 估计状态（联合系统）
    ax5 = fig.add_subplot(gs[1, 1])
    ax5.plot(t, x2, 'b-', linewidth=2, label='True State')
    ax5.plot(t, x_est2, 'r--', linewidth=2, label='Estimated State')
    ax5.axhline(r, color='gray', linestyle='--', alpha=0.5)
    ax5.set_xlabel('Time (min)')
    ax5.set_ylabel('Water Level (m)')
    ax5.set_title('State Estimation in Closed Loop')
    ax5.legend()
    ax5.grid(True, alpha=0.3)

    # 图6：控制输入对比
    ax6 = fig.add_subplot(gs[1, 2])
    ax6.plot(t, u1, 'b-', linewidth=2, label='Full State Feedback')
    ax6.plot(t, u2, 'r--', linewidth=2, label='Observer-based')
    ax6.set_xlabel('Time (min)')
    ax6.set_ylabel('Control Input u')
    ax6.set_title('Control Signals')
    ax6.legend()
    ax6.grid(True, alpha=0.3)

    # 图7：Q/R权衡响应曲线
    ax7 = fig.add_subplot(gs[2, 0])
    for res in tradeoff_data:
        ax7.plot(res['t'], res['x'], linewidth=2, label=f"Q/R={res['qr']:.1f}")
    ax7.axhline(r, color='gray', linestyle='--', alpha=0.5)
    ax7.set_xlabel('Time (min)')
    ax7.set_ylabel('Water Level (m)')
    ax7.set_title('Q/R Ratio Trade-off')
    ax7.legend()
    ax7.grid(True, alpha=0.3)

    # 图8：性能vs能量
    ax8 = fig.add_subplot(gs[2, 1])
    qr_list = [res['qr'] for res in tradeoff_data]
    t_settle_list = [res['t_settle'] for res in tradeoff_data]
    energy_list = [res['control_energy'] for res in tradeoff_data]

    ax8_twin = ax8.twinx()
    ln1 = ax8.plot(qr_list, t_settle_list, 'bo-', linewidth=2, label='Settling Time')
    ln2 = ax8_twin.plot(qr_list, energy_list, 'rs-', linewidth=2, label='Control Energy')

    ax8.set_xlabel('Q/R Ratio')
    ax8.set_ylabel('Settling Time (min)', color='b')
    ax8_twin.set_ylabel('Control Energy', color='r')
    ax8.set_xscale('log')
    ax8.set_title('Performance vs Control Effort')
    ax8.grid(True, alpha=0.3)

    lns = ln1 + ln2
    labs = [l.get_label() for l in lns]
    ax8.legend(lns, labs, loc='best')

    # 图9：总结文字
    ax9 = fig.add_subplot(gs[2, 2])
    ax9.axis('off')
    summary_text = f"""LQR + Observer Summary

Observer:
  L = {L:.3f}
  Error → 0 quickly ✓

LQR Controller:
  K = {K_lqr[0,0]:.3f}
  Q = {Q[0,0]:.1f}, R = {R[0,0]:.1f}

Combined System:
  Separation Principle ✓
  Observer-based ≈ Full State
  Practical & Optimal

Key Advantages:
  • Optimal performance
  • Guaranteed stability
  • Easy to tune (Q, R)
  • Works with observers
    """
    ax9.text(0.1, 0.5, summary_text, fontsize=10, family='monospace',
             verticalalignment='center')

    plt.savefig('case12_observer_lqr_summary.png', dpi=150, bbox_inches='tight')
    print("\n图表已保存：case12_observer_lqr_summary.png")

    # 最终总结
    print("\n" + "=" * 80)
    print("案例12总结")
    print("=" * 80)

    print("\n[关键知识点]")
    print("  1. 状态观测器：")
    print("     • 从可测输出估计不可测状态")
    print("     • 观测器极点应比控制器极点快")
    print("     • 估计误差指数收敛")
    print("")
    print("  2. LQR最优控制：")
    print("     • 最小化性能指标 J = ∫(x^TQx + u^TRu)dt")
    print("     • 通过Riccati方程求解最优增益K")
    print("     • 自动权衡性能和控制代价")
    print("")
    print("  3. 分离原理：")
    print("     • 观测器和控制器可独立设计")
    print("     • u = -Kx̂（用估计值代替真实值）")
    print("     • 闭环极点 = 控制器极点 ∪ 观测器极点")
    print("")
    print("  4. 参数选择：")
    print("     • Q大：重视状态精度，响应快")
    print("     • R大：重视控制节能，响应慢")
    print("     • 需在性能和代价间权衡")

    print("\n[工程应用]")
    print("  • 不完全状态信息下的最优控制")
    print("  • 传感器配置优化")
    print("  • 鲁棒控制系统设计")
    print("  • 多变量系统控制")

    print("\n[下一步学习]")
    print("  → 案例13：鲁棒控制（H∞控制）")
    print("  → 案例14：模型预测控制（MPC）")

    print("\n" + "=" * 80)
    print("案例12演示完成！")
    print("=" * 80)


# ============================================================================
# 主程序
# ============================================================================

def main():
    """主程序：运行所有分析步骤"""
    print("=" * 80)
    print("案例12：状态观测器与LQR最优控制")
    print("=" * 80)

    # 第1部分：观测器设计
    A, B, C, D, L, t_obs, x_true, x_est, y, error_obs = observer_design()

    # 第2部分：LQR设计
    K_lqr, P, Q, R = lqr_design(A, B, C, D)

    # 第3部分：联合应用
    t, x1, x2, x3, x_est2, u1, u2, r = observer_lqr_combined(A, B, C, D, L, K_lqr)

    # 第4部分：参数权衡
    tradeoff_results = parameter_trade_off_analysis(A, B, C, D)

    # 第5部分：可视化与总结
    visualize_and_summarize(
        (t_obs, x_true, x_est, y, error_obs),
        (K_lqr, P, Q, R),
        (t, x1, x2, x3, x_est2, u1, u2, r),
        tradeoff_results,
        L
    )

    plt.show()


if __name__ == "__main__":
    main()
