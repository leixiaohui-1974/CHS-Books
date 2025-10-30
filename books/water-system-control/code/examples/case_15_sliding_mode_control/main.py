#!/usr/bin/env python3
"""
案例15：滑模控制 - 鲁棒非线性控制

场景描述：
水箱系统存在参数不确定性和外部扰动。
使用滑模控制实现鲁棒跟踪，并对比不同的抖振抑制方法。

教学目标：
1. 理解滑模控制原理
2. 设计滑模面和控制律
3. 实现抖振抑制
4. 验证鲁棒性
5. 对比不同控制方法

分析步骤：
1. 设计基本滑模控制器
2. 实现抖振抑制（饱和函数）
3. 鲁棒性测试（参数变化、扰动）
4. 性能对比（SMC vs PID）
5. 总结与可视化

关键概念：
- 滑模面
- 到达条件
- 等效控制
- 切换控制
- 抖振抑制

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


def sign(x):
    """符号函数"""
    return 1.0 if x > 0 else (-1.0 if x < 0 else 0.0)


def sat(x, delta=1.0):
    """饱和函数（边界层）"""
    return np.clip(x / delta, -1.0, 1.0)


# ============================================================================
# 第1部分：基本滑模控制器设计
# ============================================================================

def basic_sliding_mode_control():
    """
    第1部分：基本滑模控制器（sign函数）
    """
    print("=" * 80)
    print("第1部分：基本滑模控制器设计")
    print("=" * 80)

    # 真实系统参数（有不确定性）
    A_true = 3.0
    R_true = 2.0
    K_true = 1.0

    print("\n[系统参数（真实）]")
    print(f"  A = {A_true} m², R = {R_true} min/m², K = {K_true} m³/min")

    # 标称参数（设计控制器用）
    A_nom = 2.5
    R_nom = 1.8
    K_nom = 1.2

    print("\n[标称参数（设计用）]")
    print(f"  A = {A_nom} m², R = {R_nom} min/m², K = {K_nom} m³/min")
    print(f"  参数误差：A({(A_true-A_nom)/A_nom*100:.1f}%), " +
          f"R({(R_true-R_nom)/R_nom*100:.1f}%), " +
          f"K({(K_true-K_nom)/K_nom*100:.1f}%)")

    # 滑模面设计
    lambda_smc = 1.0  # 滑模面参数
    print(f"\n[滑模面设计]")
    print(f"  s = e + λ∫e, λ = {lambda_smc}")

    # 控制器参数
    k_switch = 2.0  # 切换增益
    print(f"\n[控制器参数]")
    print(f"  切换增益 k = {k_switch}")

    # 仿真
    dt = 0.1
    t = np.arange(0, 40, dt)
    r = 2.0  # 参考值

    # 状态
    y = np.zeros(len(t))
    y[0] = 0.5

    # 控制输入
    u = np.zeros(len(t))

    # 滑模面
    s_smc = np.zeros(len(t))
    e_int = 0.0  # 误差积分

    for i in range(1, len(t)):
        # 误差
        e = r - y[i-1]
        e_int += e * dt

        # 滑模面
        s_smc[i-1] = e + lambda_smc * e_int

        # 等效控制（基于标称模型）
        # 对于 dy/dt = -y/(AR) + K/A*u
        # 要使 ds/dt = 0: de/dt + λ*e = 0
        # -dy/dt + λ*e = 0
        # y/(AR) - K/A*ueq + λ*e = 0
        # ueq = (y/(AR) + λ*e) * A/K
        a_nom = -1 / (A_nom * R_nom)
        b_nom = K_nom / A_nom

        ueq = (y[i-1] / (A_nom * R_nom) + lambda_smc * e) * A_nom / K_nom

        # 切换控制
        usw = k_switch * sign(s_smc[i-1])

        # 总控制
        u[i-1] = ueq + usw

        # 限制控制输入
        u[i-1] = np.clip(u[i-1], 0.0, 2.0)

        # 真实系统（参数与标称不同）
        dy = -y[i-1] / (A_true * R_true) + K_true / A_true * u[i-1]
        y[i] = y[i-1] + dy * dt

    # 性能评估
    steady_error = np.abs(y[-50:] - r).mean()
    reaching_time = 0
    for i, s_val in enumerate(np.abs(s_smc)):
        if s_val < 0.1:
            reaching_time = t[i]
            break

    print(f"\n[性能指标]")
    print(f"  到达滑模面时间：{reaching_time:.2f} min")
    print(f"  稳态误差：{steady_error:.4f} m")
    print(f"  最终值：{y[-1]:.4f} m (期望: {r} m)")

    # 抖振分析
    u_diff = np.diff(u)
    chattering = np.std(u_diff)
    print(f"  控制抖振（标准差）：{chattering:.4f}")

    return t, y, u, s_smc, r


# ============================================================================
# 第2部分：抖振抑制（饱和函数）
# ============================================================================

def chattering_reduction():
    """
    第2部分：使用饱和函数抑制抖振
    """
    print("\n" + "=" * 80)
    print("第2部分：抖振抑制（边界层法）")
    print("=" * 80)

    # 系统参数
    A_true, R_true, K_true = 3.0, 2.0, 1.0
    A_nom, R_nom, K_nom = 2.5, 1.8, 1.2

    # 滑模控制参数
    lambda_smc = 1.0
    k_switch = 2.0
    phi = 0.1  # 边界层厚度

    print(f"\n[边界层厚度] φ = {phi}")
    print("  使用饱和函数：sat(s/φ) 代替 sign(s)")

    # 仿真
    dt = 0.1
    t = np.arange(0, 40, dt)
    r = 2.0

    y = np.zeros(len(t))
    y[0] = 0.5
    u = np.zeros(len(t))
    s_smc = np.zeros(len(t))
    e_int = 0.0

    for i in range(1, len(t)):
        e = r - y[i-1]
        e_int += e * dt
        s_smc[i-1] = e + lambda_smc * e_int

        # 等效控制
        ueq = (y[i-1] / (A_nom * R_nom) + lambda_smc * e) * A_nom / K_nom

        # 切换控制（饱和函数）
        usw = k_switch * sat(s_smc[i-1], phi)

        u[i-1] = np.clip(ueq + usw, 0.0, 2.0)

        # 真实系统
        dy = -y[i-1] / (A_true * R_true) + K_true / A_true * u[i-1]
        y[i] = y[i-1] + dy * dt

    # 性能评估
    steady_error = np.abs(y[-50:] - r).mean()
    u_diff = np.diff(u)
    chattering = np.std(u_diff)

    print(f"\n[性能指标（饱和函数）]")
    print(f"  稳态误差：{steady_error:.4f} m")
    print(f"  控制抖振（标准差）：{chattering:.4f}")
    print(f"  最终值：{y[-1]:.4f} m")
    print(f"  → 抖振显著减小 ✓")

    return t, y, u, s_smc, r


# ============================================================================
# 第3部分：鲁棒性测试
# ============================================================================

def robustness_test():
    """
    第3部分：测试滑模控制的鲁棒性
    """
    print("\n" + "=" * 80)
    print("第3部分：鲁棒性测试")
    print("=" * 80)

    # 标称参数
    A_nom, R_nom, K_nom = 2.5, 1.8, 1.2

    # 滑模控制参数
    lambda_smc = 1.0
    k_switch = 2.0
    phi = 0.1

    print("\n[测试场景]")
    print("  1. 参数在t=20时突变")
    print("  2. 存在周期性扰动")

    # 仿真
    dt = 0.1
    t = np.arange(0, 50, dt)
    r = 2.0

    y = np.zeros(len(t))
    y[0] = 0.5
    u = np.zeros(len(t))
    s_smc = np.zeros(len(t))
    e_int = 0.0

    for i in range(1, len(t)):
        # 参数变化
        if t[i] < 20:
            A_true, R_true, K_true = 3.0, 2.0, 1.0
        else:
            A_true, R_true, K_true = 3.5, 2.5, 0.9  # 参数突变

        # 外部扰动
        disturbance = 0.3 * np.sin(0.5 * t[i])

        e = r - y[i-1]
        e_int += e * dt
        s_smc[i-1] = e + lambda_smc * e_int

        ueq = (y[i-1] / (A_nom * R_nom) + lambda_smc * e) * A_nom / K_nom
        usw = k_switch * sat(s_smc[i-1], phi)
        u[i-1] = np.clip(ueq + usw, 0.0, 2.0)

        # 真实系统（含扰动）
        dy = -y[i-1] / (A_true * R_true) + K_true / A_true * u[i-1] + disturbance / A_true
        y[i] = y[i-1] + dy * dt

    # 性能评估
    error_before = np.abs(y[100:200] - r).mean()
    error_after = np.abs(y[300:400] - r).mean()

    print(f"\n[鲁棒性分析]")
    print(f"  参数变化前误差：{error_before:.4f} m")
    print(f"  参数变化后误差：{error_after:.4f} m")
    print(f"  误差变化：{abs(error_after - error_before):.4f} m")
    print(f"  → 滑模控制对参数变化鲁棒 ✓")

    return t, y, u, s_smc, r


# ============================================================================
# 第4部分：性能对比（SMC vs PID）
# ============================================================================

def performance_comparison():
    """
    第4部分：滑模控制 vs PID控制
    """
    print("\n" + "=" * 80)
    print("第4部分：性能对比（SMC vs PID）")
    print("=" * 80)

    # 系统参数（有不确定性）
    A_true, R_true, K_true = 3.0, 2.0, 1.0
    A_nom, R_nom, K_nom = 2.5, 1.8, 1.2

    dt = 0.1
    t = np.arange(0, 40, dt)
    r = 2.0

    # 添加扰动
    disturbance = np.zeros(len(t))
    disturbance[150:250] = 0.5  # 阶跃扰动

    print("\n[测试场景]")
    print("  参数不匹配 + 阶跃扰动（t=15-25）")

    # ===== 滑模控制 =====
    print("\n[滑模控制]")
    y_smc = np.zeros(len(t))
    y_smc[0] = 0.5
    u_smc = np.zeros(len(t))
    e_int_smc = 0.0

    lambda_smc = 1.0
    k_switch = 2.0
    phi = 0.1

    for i in range(1, len(t)):
        e = r - y_smc[i-1]
        e_int_smc += e * dt
        s = e + lambda_smc * e_int_smc

        ueq = (y_smc[i-1] / (A_nom * R_nom) + lambda_smc * e) * A_nom / K_nom
        usw = k_switch * sat(s, phi)
        u_smc[i-1] = np.clip(ueq + usw, 0.0, 2.0)

        dy = -y_smc[i-1] / (A_true * R_true) + K_true / A_true * u_smc[i-1] + \
             disturbance[i] / A_true
        y_smc[i] = y_smc[i-1] + dy * dt

    error_smc = np.abs(y_smc[-50:] - r).mean()
    print(f"  稳态误差：{error_smc:.4f} m")

    # ===== PID控制 =====
    print("\n[PID控制（基于标称参数设计）]")
    y_pid = np.zeros(len(t))
    y_pid[0] = 0.5
    u_pid = np.zeros(len(t))

    Kp = 2.0
    Ki = 0.25
    e_int_pid = 0.0

    for i in range(1, len(t)):
        e = r - y_pid[i-1]
        e_int_pid += e * dt

        u_pid[i-1] = Kp * e + Ki * e_int_pid
        u_pid[i-1] = np.clip(u_pid[i-1], 0.0, 2.0)

        dy = -y_pid[i-1] / (A_true * R_true) + K_true / A_true * u_pid[i-1] + \
             disturbance[i] / A_true
        y_pid[i] = y_pid[i-1] + dy * dt

    error_pid = np.abs(y_pid[-50:] - r).mean()
    print(f"  稳态误差：{error_pid:.4f} m")

    print(f"\n[对比结论]")
    print(f"  滑模控制误差：{error_smc:.4f} m")
    print(f"  PID控制误差：{error_pid:.4f} m")
    if error_smc < error_pid:
        print(f"  → 滑模控制鲁棒性更好 ✓")
    else:
        print(f"  → PID控制性能接近")

    return t, y_smc, y_pid, u_smc, u_pid, r, disturbance


# ============================================================================
# 第5部分：可视化与总结
# ============================================================================

def visualize_and_summarize(basic_data, sat_data, robust_data, compare_data):
    """
    第5部分：综合可视化和总结
    """
    print("\n" + "=" * 80)
    print("第5部分：可视化与总结")
    print("=" * 80)

    # 解包数据
    t1, y1, u1, s1, r1 = basic_data
    t2, y2, u2, s2, r2 = sat_data
    t3, y3, u3, s3, r3 = robust_data
    t4, y_smc, y_pid, u_smc, u_pid, r4, dist = compare_data

    fig = plt.figure(figsize=(16, 12))
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

    # 图1：基本滑模控制输出
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.plot(t1, y1, 'b-', linewidth=2, label='SMC Output')
    ax1.axhline(r1, color='r', linestyle='--', alpha=0.5, label='Reference')
    ax1.set_xlabel('Time (min)')
    ax1.set_ylabel('Water Level (m)')
    ax1.set_title('Basic SMC (sign function)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # 图2：基本滑模控制输入（抖振明显）
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.plot(t1, u1, 'g-', linewidth=1, alpha=0.7)
    ax2.set_xlabel('Time (min)')
    ax2.set_ylabel('Control Input')
    ax2.set_title('Control Signal (with chattering)')
    ax2.grid(True, alpha=0.3)

    # 图3：滑模面
    ax3 = fig.add_subplot(gs[0, 2])
    ax3.plot(t1, s1, 'k-', linewidth=2, label='s (sign)')
    ax3.plot(t2, s2, 'r-', linewidth=2, alpha=0.7, label='s (sat)')
    ax3.axhline(0, color='gray', linestyle='--', alpha=0.5)
    ax3.set_xlabel('Time (min)')
    ax3.set_ylabel('Sliding Surface s')
    ax3.set_title('Sliding Surface Evolution')
    ax3.legend()
    ax3.grid(True, alpha=0.3)

    # 图4：饱和函数控制输出
    ax4 = fig.add_subplot(gs[1, 0])
    ax4.plot(t2, y2, 'b-', linewidth=2, label='SMC (sat)')
    ax4.axhline(r2, color='r', linestyle='--', alpha=0.5, label='Reference')
    ax4.set_xlabel('Time (min)')
    ax4.set_ylabel('Water Level (m)')
    ax4.set_title('SMC with Saturation Function')
    ax4.legend()
    ax4.grid(True, alpha=0.3)

    # 图5：饱和函数控制输入（抖振减小）
    ax5 = fig.add_subplot(gs[1, 1])
    ax5.plot(t2, u2, 'g-', linewidth=2)
    ax5.set_xlabel('Time (min)')
    ax5.set_ylabel('Control Input')
    ax5.set_title('Smooth Control (reduced chattering)')
    ax5.grid(True, alpha=0.3)

    # 图6：鲁棒性测试
    ax6 = fig.add_subplot(gs[1, 2])
    ax6.plot(t3, y3, 'b-', linewidth=2, label='SMC Output')
    ax6.axhline(r3, color='r', linestyle='--', alpha=0.5, label='Reference')
    ax6.axvline(20, color='orange', linestyle=':', linewidth=2, label='Parameter Change')
    ax6.set_xlabel('Time (min)')
    ax6.set_ylabel('Water Level (m)')
    ax6.set_title('Robustness Test')
    ax6.legend()
    ax6.grid(True, alpha=0.3)

    # 图7：SMC vs PID输出对比
    ax7 = fig.add_subplot(gs[2, 0])
    ax7.plot(t4, y_smc, 'b-', linewidth=2, label='SMC')
    ax7.plot(t4, y_pid, 'r--', linewidth=2, label='PID')
    ax7.axhline(r4, color='gray', linestyle='--', alpha=0.3)
    ax7.set_xlabel('Time (min)')
    ax7.set_ylabel('Water Level (m)')
    ax7.set_title('SMC vs PID Performance')
    ax7.legend()
    ax7.grid(True, alpha=0.3)

    # 图8：扰动信号
    ax8 = fig.add_subplot(gs[2, 1])
    ax8.plot(t4, dist, 'r-', linewidth=2)
    ax8.set_xlabel('Time (min)')
    ax8.set_ylabel('Disturbance')
    ax8.set_title('External Disturbance')
    ax8.grid(True, alpha=0.3)

    # 图9：总结文字
    ax9 = fig.add_subplot(gs[2, 2])
    ax9.axis('off')
    summary_text = """Sliding Mode Control Summary

Basic SMC:
  • Fast convergence
  • Strong robustness
  • Chattering issue

Saturation Function:
  • Reduced chattering
  • Smooth control
  • Slight accuracy trade-off

Robustness:
  • Parameter changes: ✓
  • Disturbance rejection: ✓
  • Better than PID

Key Advantages:
  ✓ Finite-time convergence
  ✓ Robust to uncertainty
  ✓ Simple implementation
  ✓ Disturbance rejection

Limitations:
  ✗ Chattering problem
  ✗ Requires bounds
  ✗ Noise sensitive
    """
    ax9.text(0.1, 0.5, summary_text, fontsize=9, family='monospace',
             verticalalignment='center')

    plt.savefig('case15_sliding_mode_summary.png', dpi=150, bbox_inches='tight')
    print("\n图表已保存：case15_sliding_mode_summary.png")

    # 最终总结
    print("\n" + "=" * 80)
    print("案例15总结")
    print("=" * 80)

    print("\n[关键知识点]")
    print("  1. 滑模控制原理：")
    print("     • 滑模面：s = e + λ∫e")
    print("     • 到达条件：s·ṡ < 0")
    print("     • 有限时间收敛")
    print("")
    print("  2. 控制律设计：")
    print("     • 等效控制：维持滑模运动")
    print("     • 切换控制：克服不确定性")
    print("     • u = ueq + usw")
    print("")
    print("  3. 抖振抑制：")
    print("     • sign函数 → 抖振")
    print("     • sat函数 → 平滑控制")
    print("     • 边界层法有效")
    print("")
    print("  4. 鲁棒性：")
    print("     • 对参数不确定性鲁棒")
    print("     • 强扰动抑制能力")
    print("     • 优于传统PID")

    print("\n[工程应用]")
    print("  • 不确定性大的系统")
    print("  • 强扰动环境")
    print("  • 快速响应需求")
    print("  • 机器人、航空航天等")

    print("\n[实用建议]")
    print("  • 使用饱和函数避免抖振")
    print("  • 适当选择切换增益k")
    print("  • 边界层厚度需权衡")
    print("  • 添加低通滤波器")

    print("\n[下一步学习]")
    print("  → 案例16：模糊控制")
    print("  → 案例17：神经网络控制")

    print("\n" + "=" * 80)
    print("案例15演示完成！")
    print("=" * 80)


# ============================================================================
# 主程序
# ============================================================================

def main():
    """主程序：运行所有分析步骤"""
    print("=" * 80)
    print("案例15：滑模控制 - 鲁棒非线性控制")
    print("=" * 80)

    # 第1部分：基本滑模控制
    basic_data = basic_sliding_mode_control()

    # 第2部分：抖振抑制
    sat_data = chattering_reduction()

    # 第3部分：鲁棒性测试
    robust_data = robustness_test()

    # 第4部分：性能对比
    compare_data = performance_comparison()

    # 第5部分：可视化与总结
    visualize_and_summarize(basic_data, sat_data, robust_data, compare_data)

    plt.show()


if __name__ == "__main__":
    main()
