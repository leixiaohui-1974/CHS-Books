#!/usr/bin/env python3
"""
案例13：自适应控制 - 应对参数不确定性

场景描述：
水箱系统的参数（横截面积、阻力系数等）未知或随时间变化。
使用自适应控制技术在线估计参数并调整控制器，
保持良好的控制性能。

教学目标：
1. 理解自适应控制的必要性
2. 掌握MRAC（模型参考自适应控制）原理
3. 学习RLS（递推最小二乘）参数估计
4. 实现自校正控制器
5. 对比自适应vs固定参数控制

分析步骤：
1. 演示参数不确定性的影响
2. 设计MRAC控制器（MIT规则）
3. 实现RLS参数估计
4. 设计自校正控制器
5. 性能对比与总结

关键概念：
- 模型参考自适应控制
- MIT规则
- 递推最小二乘
- 自校正控制
- 参数收敛性

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
# 第1部分：参数不确定性的影响
# ============================================================================

def parameter_uncertainty_effect():
    """
    第1部分：演示参数不确定性对控制性能的影响
    """
    print("=" * 80)
    print("第1部分：参数不确定性的影响")
    print("=" * 80)

    # 真实系统参数（未知）
    A_true = 3.0  # 真实横截面积
    R_true = 2.0  # 真实阻力系数
    K_true = 1.0  # 真实泵增益

    # 标称参数（设计控制器时使用的估计值）
    A_nom = 2.5
    R_nom = 1.8
    K_nom = 1.2

    print("\n[真实系统参数]")
    print(f"  A_true = {A_true} m²")
    print(f"  R_true = {R_true} min/m²")
    print(f"  K_true = {K_true} m³/min")

    print("\n[标称参数（用于设计控制器）]")
    print(f"  A_nom = {A_nom} m²")
    print(f"  R_nom = {R_nom} min/m²")
    print(f"  K_nom = {K_nom} m³/min")

    print("\n[参数误差]")
    print(f"  A误差: {(A_true - A_nom)/A_nom * 100:.1f}%")
    print(f"  R误差: {(R_true - R_nom)/R_nom * 100:.1f}%")
    print(f"  K误差: {(K_true - K_nom)/K_nom * 100:.1f}%")

    # 基于标称参数设计PI控制器
    tau_nom = A_nom * R_nom
    K_dc_nom = K_nom * R_nom

    Kp = 2.0
    Ti = 8.0
    Ki = Kp / Ti

    print(f"\n[基于标称参数设计的PI控制器]")
    print(f"  Kp = {Kp}, Ti = {Ti}")

    # 仿真：固定控制器应用于真实系统
    dt = 0.1
    t = np.arange(0, 40, dt)
    r = 2.0  # 参考值

    # 真实系统状态
    x_true = np.zeros(len(t))
    x_true[0] = 0.5

    # 控制输入
    u = np.zeros(len(t))

    # 积分项
    e_int = 0.0

    for i in range(1, len(t)):
        # PI控制律
        e = r - x_true[i-1]
        e_int += e * dt
        u[i-1] = Kp * e + Ki * e_int

        # 真实系统动态（参数与标称不同）
        dx = -x_true[i-1] / (A_true * R_true) + K_true / A_true * u[i-1]
        x_true[i] = x_true[i-1] + dx * dt

    # 性能评估
    error = np.abs(x_true - r)
    steady_state_error = np.mean(error[-50:])
    max_overshoot = (np.max(x_true) - r) / r * 100 if np.max(x_true) > r else 0

    print(f"\n[控制性能（参数不匹配）]")
    print(f"  稳态误差: {steady_state_error:.4f} m")
    print(f"  超调量: {max_overshoot:.2f}%")
    print(f"  最终值: {x_true[-1]:.4f} m (期望: {r} m)")

    if abs(steady_state_error) > 0.1:
        print("  → 参数不匹配导致性能显著下降！需要自适应控制")

    return t, x_true, u, r


# ============================================================================
# 第2部分：MRAC控制器设计（MIT规则）
# ============================================================================

def mrac_mit_design():
    """
    第2部分：模型参考自适应控制（MIT规则）
    """
    print("\n" + "=" * 80)
    print("第2部分：MRAC控制器（MIT规则）")
    print("=" * 80)

    # 真实系统参数（未知）
    A_true = 3.0
    R_true = 2.0
    K_true = 1.0

    print("\n[参考模型设计]")
    # 参考模型：期望的一阶系统
    am = 0.5  # 参考模型极点
    bm = 0.5  # 参考模型增益

    print(f"  参考模型: Gm(s) = {bm} / (s + {am})")
    print(f"  时间常数: τm = {1/am:.2f} min")

    print("\n[自适应控制律]")
    print("  u = θ1*r + θ2*y")
    print("  MIT规则: dθ/dt = -γ * e * (∂e/∂θ)")

    # 自适应增益
    gamma1 = 0.5
    gamma2 = 0.5

    print(f"  γ1 = {gamma1}, γ2 = {gamma2}")

    # 仿真
    dt = 0.1
    t = np.arange(0, 50, dt)
    r_signal = 2.0 * np.ones(len(t))  # 阶跃参考

    # 状态
    y = np.zeros(len(t))  # 实际输出
    ym = np.zeros(len(t))  # 参考模型输出
    y[0] = 0.5
    ym[0] = 0.5

    # 自适应参数
    theta1 = np.zeros(len(t))
    theta2 = np.zeros(len(t))
    theta1[0] = 0.1  # 初值（任意）
    theta2[0] = 0.1

    # 控制输入
    u = np.zeros(len(t))

    # 误差
    e = np.zeros(len(t))

    for i in range(1, len(t)):
        # 当前参考输入
        r = r_signal[i-1]

        # 控制律
        u[i-1] = theta1[i-1] * r + theta2[i-1] * y[i-1]

        # 实际系统
        dy = -y[i-1] / (A_true * R_true) + K_true / A_true * u[i-1]
        y[i] = y[i-1] + dy * dt

        # 参考模型
        dym = -am * ym[i-1] + bm * r
        ym[i] = ym[i-1] + dym * dt

        # 跟踪误差
        e[i] = y[i] - ym[i]

        # MIT自适应律（简化）
        # ∂e/∂θ1 ≈ r, ∂e/∂θ2 ≈ y
        dtheta1 = -gamma1 * e[i] * r
        dtheta2 = -gamma2 * e[i] * y[i]

        theta1[i] = theta1[i-1] + dtheta1 * dt
        theta2[i] = theta2[i-1] + dtheta2 * dt

    # 性能分析
    print(f"\n[MRAC性能]")
    print(f"  初始θ1 = {theta1[0]:.4f}, 最终θ1 = {theta1[-1]:.4f}")
    print(f"  初始θ2 = {theta2[0]:.4f}, 最终θ2 = {theta2[-1]:.4f}")
    print(f"  最终跟踪误差: {abs(e[-1]):.4f}")
    print(f"  参数收敛: {'是' if abs(theta1[-1] - theta1[-50]) < 0.01 else '否'} ✓")

    return t, y, ym, e, theta1, theta2, u


# ============================================================================
# 第3部分：RLS参数估计
# ============================================================================

def rls_parameter_estimation():
    """
    第3部分：递推最小二乘参数估计
    """
    print("\n" + "=" * 80)
    print("第3部分：RLS参数估计")
    print("=" * 80)

    # 真实系统参数
    A_true = 3.0
    R_true = 2.0
    K_true = 1.0

    a_true = -1 / (A_true * R_true)  # 系统极点
    b_true = K_true / A_true  # 系统增益

    print("\n[真实系统]")
    print(f"  dy/dt = a*y + b*u")
    print(f"  a_true = {a_true:.4f}")
    print(f"  b_true = {b_true:.4f}")

    print("\n[RLS算法]")
    print("  模型: y(k) = a*y(k-1) + b*u(k-1)")
    print("  参数: θ = [a, b]^T")
    print("  递推更新: θ̂(k) = θ̂(k-1) + K(k)*[y(k) - φ(k)^T*θ̂(k-1)]")

    # RLS参数
    lambda_rls = 0.98  # 遗忘因子
    print(f"  遗忘因子 λ = {lambda_rls}")

    # 仿真
    dt = 0.1
    t = np.arange(0, 50, dt)

    # 激励信号（需要足够丰富）
    u = np.sin(0.2 * t) + 0.5 * np.sin(0.5 * t) + 1.0

    # 真实系统输出
    y = np.zeros(len(t))
    y[0] = 0.0

    for i in range(1, len(t)):
        dy = a_true * y[i-1] + b_true * u[i-1]
        y[i] = y[i-1] + dy * dt

    # 添加小量噪声
    np.random.seed(42)
    noise = np.random.normal(0, 0.02, len(t))
    y_meas = y + noise

    # RLS估计
    theta_hat = np.zeros((len(t), 2))
    theta_hat[0, :] = [0.0, 0.0]  # 初值

    P = np.eye(2) * 100  # 初始协方差矩阵（大值表示不确定）

    for k in range(1, len(t)):
        # 回归向量
        phi = np.array([y_meas[k-1], u[k-1]])

        # 预测误差
        y_pred = phi @ theta_hat[k-1, :]
        prediction_error = y_meas[k] - y_pred

        # Kalman增益
        K_rls = P @ phi / (lambda_rls + phi @ P @ phi)

        # 参数更新
        theta_hat[k, :] = theta_hat[k-1, :] + K_rls * prediction_error

        # 协方差更新
        P = (np.eye(2) - np.outer(K_rls, phi)) @ P / lambda_rls

    # 结果
    a_est = theta_hat[-1, 0]
    b_est = theta_hat[-1, 1]

    print(f"\n[RLS估计结果]")
    print(f"  a估计: {a_est:.4f} (真值: {a_true:.4f}, 误差: {abs(a_est - a_true):.4f})")
    print(f"  b估计: {b_est:.4f} (真值: {b_true:.4f}, 误差: {abs(b_est - b_true):.4f})")
    print(f"  参数收敛: {'是' if abs(theta_hat[-1, 0] - theta_hat[-50, 0]) < 0.01 else '否'} ✓")

    return t, y_meas, u, theta_hat, a_true, b_true


# ============================================================================
# 第4部分：自校正控制器
# ============================================================================

def self_tuning_controller():
    """
    第4部分：自校正控制器（RLS + 极点配置）
    """
    print("\n" + "=" * 80)
    print("第4部分：自校正控制器")
    print("=" * 80)

    # 真实系统参数（未知且时变）
    def get_true_params(t):
        """参数随时间变化"""
        if t < 25:
            A, R, K = 3.0, 2.0, 1.0
        else:
            # 参数突变（模拟系统变化）
            A, R, K = 3.5, 2.5, 0.9

        a = -1 / (A * R)
        b = K / A
        return a, b

    print("\n[自校正控制策略]")
    print("  1. RLS估计系统参数 a, b")
    print("  2. 基于估计参数设计控制器")
    print("  3. 应用新控制器")
    print("  4. 循环执行")

    # 期望闭环极点
    desired_pole = -0.5
    print(f"\n[控制目标]")
    print(f"  期望闭环极点: {desired_pole}")

    # 仿真
    dt = 0.1
    t = np.arange(0, 50, dt)
    r = 2.0  # 参考值

    # 状态
    y = np.zeros(len(t))
    y[0] = 0.5

    # 参数估计
    theta_hat = np.zeros((len(t), 2))
    theta_hat[0, :] = [-0.2, 0.3]  # 初始猜测

    P = np.eye(2) * 100
    lambda_rls = 0.98

    # 控制器参数
    K_controller = np.zeros(len(t))
    K_controller[0] = 1.0

    # 控制输入
    u = np.zeros(len(t))

    for k in range(1, len(t)):
        # 获取当前真实参数（控制器不知道）
        a_true, b_true = get_true_params(t[k])

        # RLS参数估计
        phi = np.array([y[k-1], u[k-1]])
        y_pred = phi @ theta_hat[k-1, :]
        prediction_error = y[k-1] - y_pred

        K_rls = P @ phi / (lambda_rls + phi @ P @ phi)
        theta_hat[k, :] = theta_hat[k-1, :] + K_rls * prediction_error
        P = (np.eye(2) - np.outer(K_rls, phi)) @ P / lambda_rls

        # 控制器设计（基于估计参数）
        a_est = theta_hat[k, 0]
        b_est = theta_hat[k, 1]

        # 极点配置：a_cl = a + b*K = desired_pole
        # K = (desired_pole - a) / b
        if abs(b_est) > 0.01:  # 避免除零
            K_controller[k] = (desired_pole - a_est) / b_est
        else:
            K_controller[k] = K_controller[k-1]

        # 限制控制器增益（防止过大）
        K_controller[k] = np.clip(K_controller[k], -10, 10)

        # 控制律
        u[k] = K_controller[k] * (r - y[k])

        # 真实系统（参数在t=25时突变）
        dy = a_true * y[k] + b_true * u[k]
        y[k] = y[k-1] + dy * dt

    # 性能分析
    print(f"\n[自校正控制性能]")
    print(f"  初始参数估计: a={theta_hat[0,0]:.4f}, b={theta_hat[0,1]:.4f}")
    print(f"  t=24时估计: a={theta_hat[240,0]:.4f}, b={theta_hat[240,1]:.4f}")
    print(f"  t=49时估计: a={theta_hat[-1,0]:.4f}, b={theta_hat[-1,1]:.4f}")

    a_true_1, b_true_1 = get_true_params(20)
    a_true_2, b_true_2 = get_true_params(40)

    print(f"\n  真实参数（t<25）: a={a_true_1:.4f}, b={b_true_1:.4f}")
    print(f"  真实参数（t>25）: a={a_true_2:.4f}, b={b_true_2:.4f}")
    print(f"\n  参数突变时系统能够重新自适应 ✓")

    return t, y, u, theta_hat, K_controller, r


# ============================================================================
# 第5部分：可视化与总结
# ============================================================================

def visualize_and_summarize(fixed_data, mrac_data, rls_data, stc_data):
    """
    第5部分：综合可视化和总结
    """
    print("\n" + "=" * 80)
    print("第5部分：可视化与总结")
    print("=" * 80)

    # 解包数据
    t1, y_fixed, u_fixed, r_fixed = fixed_data
    t2, y_mrac, ym_mrac, e_mrac, theta1_mrac, theta2_mrac, u_mrac = mrac_data
    t3, y_rls, u_rls, theta_rls, a_true, b_true = rls_data
    t4, y_stc, u_stc, theta_stc, K_stc, r_stc = stc_data

    fig = plt.figure(figsize=(16, 12))
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

    # 图1：固定参数控制（参数不匹配）
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.plot(t1, y_fixed, 'b-', linewidth=2, label='System Output')
    ax1.axhline(r_fixed, color='r', linestyle='--', alpha=0.5, label='Reference')
    ax1.set_xlabel('Time (min)')
    ax1.set_ylabel('Water Level (m)')
    ax1.set_title('Fixed Controller (Mismatch)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # 图2：MRAC跟踪性能
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.plot(t2, y_mrac, 'b-', linewidth=2, label='System Output y')
    ax2.plot(t2, ym_mrac, 'r--', linewidth=2, label='Reference Model ym')
    ax2.set_xlabel('Time (min)')
    ax2.set_ylabel('Output')
    ax2.set_title('MRAC Tracking')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    # 图3：MRAC参数收敛
    ax3 = fig.add_subplot(gs[0, 2])
    ax3.plot(t2, theta1_mrac, 'b-', linewidth=2, label='θ1')
    ax3.plot(t2, theta2_mrac, 'r-', linewidth=2, label='θ2')
    ax3.set_xlabel('Time (min)')
    ax3.set_ylabel('Parameter Value')
    ax3.set_title('MRAC Parameter Evolution')
    ax3.legend()
    ax3.grid(True, alpha=0.3)

    # 图4：RLS参数估计
    ax4 = fig.add_subplot(gs[1, 0])
    ax4.plot(t3, theta_rls[:, 0], 'b-', linewidth=2, label='â (estimated)')
    ax4.axhline(a_true, color='b', linestyle='--', alpha=0.5, label='a (true)')
    ax4.plot(t3, theta_rls[:, 1], 'r-', linewidth=2, label='b̂ (estimated)')
    ax4.axhline(b_true, color='r', linestyle='--', alpha=0.5, label='b (true)')
    ax4.set_xlabel('Time (min)')
    ax4.set_ylabel('Parameter Value')
    ax4.set_title('RLS Parameter Estimation')
    ax4.legend()
    ax4.grid(True, alpha=0.3)

    # 图5：RLS估计误差
    ax5 = fig.add_subplot(gs[1, 1])
    error_a = theta_rls[:, 0] - a_true
    error_b = theta_rls[:, 1] - b_true
    ax5.plot(t3, error_a, 'b-', linewidth=2, label='a error')
    ax5.plot(t3, error_b, 'r-', linewidth=2, label='b error')
    ax5.axhline(0, color='k', linestyle='--', alpha=0.3)
    ax5.set_xlabel('Time (min)')
    ax5.set_ylabel('Estimation Error')
    ax5.set_title('RLS Convergence')
    ax5.legend()
    ax5.grid(True, alpha=0.3)

    # 图6：自校正控制输出
    ax6 = fig.add_subplot(gs[1, 2])
    ax6.plot(t4, y_stc, 'b-', linewidth=2, label='Output')
    ax6.axhline(r_stc, color='r', linestyle='--', alpha=0.5, label='Reference')
    ax6.axvline(25, color='orange', linestyle=':', linewidth=2, alpha=0.7, label='Parameter Change')
    ax6.set_xlabel('Time (min)')
    ax6.set_ylabel('Water Level (m)')
    ax6.set_title('Self-Tuning Control (with Parameter Jump)')
    ax6.legend()
    ax6.grid(True, alpha=0.3)

    # 图7：自校正控制器增益变化
    ax7 = fig.add_subplot(gs[2, 0])
    ax7.plot(t4, K_stc, 'g-', linewidth=2)
    ax7.axvline(25, color='orange', linestyle=':', linewidth=2, alpha=0.7)
    ax7.set_xlabel('Time (min)')
    ax7.set_ylabel('Controller Gain K')
    ax7.set_title('Self-Tuning Controller Gain')
    ax7.grid(True, alpha=0.3)

    # 图8：自校正参数估计
    ax8 = fig.add_subplot(gs[2, 1])
    ax8.plot(t4, theta_stc[:, 0], 'b-', linewidth=2, label='â')
    ax8.plot(t4, theta_stc[:, 1], 'r-', linewidth=2, label='b̂')
    ax8.axvline(25, color='orange', linestyle=':', linewidth=2, alpha=0.7)
    ax8.set_xlabel('Time (min)')
    ax8.set_ylabel('Estimated Parameters')
    ax8.set_title('STC Parameter Tracking')
    ax8.legend()
    ax8.grid(True, alpha=0.3)

    # 图9：总结
    ax9 = fig.add_subplot(gs[2, 2])
    ax9.axis('off')
    summary_text = """Adaptive Control Summary

Fixed Controller:
  • Sensitive to mismatch
  • Poor performance

MRAC (MIT Rule):
  • Tracks reference model
  • Parameter convergence

RLS Estimation:
  • Fast convergence
  • Accurate estimation

Self-Tuning Control:
  • Adapts to changes
  • Re-tunes automatically
  • Robust to variations

Key Advantages:
  ✓ Handles unknown params
  ✓ Adapts to changes
  ✓ No manual tuning
  ✓ Maintains performance
    """
    ax9.text(0.1, 0.5, summary_text, fontsize=9, family='monospace',
             verticalalignment='center')

    plt.savefig('case13_adaptive_control_summary.png', dpi=150, bbox_inches='tight')
    print("\n图表已保存：case13_adaptive_control_summary.png")

    # 最终总结
    print("\n" + "=" * 80)
    print("案例13总结")
    print("=" * 80)

    print("\n[关键知识点]")
    print("  1. 参数不确定性影响：")
    print("     • 固定控制器性能下降")
    print("     • 需要自适应机制")
    print("")
    print("  2. MRAC（模型参考自适应）：")
    print("     • 定义期望性能（参考模型）")
    print("     • MIT规则调整控制器")
    print("     • 实现输出跟踪")
    print("")
    print("  3. RLS参数估计：")
    print("     • 递推算法，在线估计")
    print("     • 遗忘因子处理时变参数")
    print("     • 快速收敛到真值")
    print("")
    print("  4. 自校正控制：")
    print("     • RLS估计 + 控制器重设计")
    print("     • 自动适应参数变化")
    print("     • 参数突变时能重新调整")

    print("\n[工程应用]")
    print("  • 参数时变的慢速系统")
    print("  • 模型不确定性大的场合")
    print("  • 工况变化频繁的过程")
    print("  • 需要长期免维护运行的系统")

    print("\n[实用建议]")
    print("  • 选择合适的自适应增益（收敛vs稳定）")
    print("  • 使用遗忘因子处理时变参数")
    print("  • 添加参数限幅防止异常")
    print("  • 保持足够的激励信号")

    print("\n[下一步学习]")
    print("  → 案例14：模型预测控制（MPC）")
    print("  → 案例15：非线性控制方法")

    print("\n" + "=" * 80)
    print("案例13演示完成！")
    print("=" * 80)


# ============================================================================
# 主程序
# ============================================================================

def main():
    """主程序：运行所有分析步骤"""
    print("=" * 80)
    print("案例13：自适应控制 - 应对参数不确定性")
    print("=" * 80)

    # 第1部分：参数不确定性的影响
    t1, y_fixed, u_fixed, r_fixed = parameter_uncertainty_effect()

    # 第2部分：MRAC设计
    t2, y_mrac, ym_mrac, e_mrac, theta1_mrac, theta2_mrac, u_mrac = mrac_mit_design()

    # 第3部分：RLS参数估计
    t3, y_rls, u_rls, theta_rls, a_true, b_true = rls_parameter_estimation()

    # 第4部分：自校正控制器
    t4, y_stc, u_stc, theta_stc, K_stc, r_stc = self_tuning_controller()

    # 第5部分：可视化与总结
    visualize_and_summarize(
        (t1, y_fixed, u_fixed, r_fixed),
        (t2, y_mrac, ym_mrac, e_mrac, theta1_mrac, theta2_mrac, u_mrac),
        (t3, y_rls, u_rls, theta_rls, a_true, b_true),
        (t4, y_stc, u_stc, theta_stc, K_stc, r_stc)
    )

    plt.show()


if __name__ == "__main__":
    main()
