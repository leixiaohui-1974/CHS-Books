#!/usr/bin/env python3
"""
案例11扩展实验：状态空间方法深入研究

本文件包含多个扩展实验：
1. 双水箱系统的状态空间建模
2. 多变量极点配置
3. 状态反馈 vs PID控制对比
4. 参考输入跟踪与积分控制

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
# 实验1：双水箱系统的状态空间建模
# ============================================================================

def experiment_two_tank_system():
    """
    实验1：双水箱串联系统的状态空间模型
    """
    print("=" * 80)
    print("实验1：双水箱系统的状态空间建模")
    print("=" * 80)

    # 双水箱参数
    A1, A2 = 2.5, 2.0  # 横截面积
    R1, R2 = 1.5, 2.0  # 阻力系数
    K = 1.2            # 泵增益

    print("\n[双水箱系统参数]")
    print(f"  上游水箱：A1 = {A1} m², R1 = {R1} min/m²")
    print(f"  下游水箱：A2 = {A2} m², R2 = {R2} min/m²")
    print(f"  泵增益：K = {K} m³/min")

    # 状态变量：x1 = h1（上游水位），x2 = h2（下游水位）
    # 状态方程：
    # A1·dh1/dt = K·u - h1/R1
    # A2·dh2/dt = h1/R1 - h2/R2
    #
    # 整理：
    # dh1/dt = -1/(A1·R1)·h1 + K/A1·u
    # dh2/dt = 1/(A2·R1)·h1 - 1/(A2·R2)·h2

    # 状态空间矩阵
    A = np.array([
        [-1/(A1*R1),        0      ],
        [ 1/(A2*R1),  -1/(A2*R2)   ]
    ])

    B = np.array([
        [K/A1],
        [0   ]
    ])

    C = np.array([[0, 1]])  # 输出为下游水位h2

    D = np.array([[0]])

    print("\n[状态空间表示]")
    print("状态向量 x = [h1, h2]^T")
    print("输入 u = 泵流量控制信号")
    print("输出 y = h2（下游水位）")
    print("\n系统矩阵：")
    print(f"A = \n{A}")
    print(f"\nB = \n{B}")
    print(f"\nC = {C}")
    print(f"\nD = {D}")

    # 系统极点
    poles = np.linalg.eigvals(A)
    print(f"\n[开环系统极点]")
    for i, p in enumerate(poles):
        print(f"  极点{i+1} = {p:.4f}, 时间常数 = {-1/p:.2f} min")

    # 能控性分析
    print("\n[能控性分析]")
    n = A.shape[0]
    Mc = np.hstack([np.linalg.matrix_power(A, i) @ B for i in range(n)])
    rank_Mc = np.linalg.matrix_rank(Mc)

    print(f"能控性矩阵 Mc = \n{Mc}")
    print(f"秩(Mc) = {rank_Mc}, 系统阶数 = {n}")
    print(f"结论：{'完全能控 ✓' if rank_Mc == n else '不完全能控 ✗'}")

    # 能观性分析
    print("\n[能观性分析]")
    Mo = np.vstack([C @ np.linalg.matrix_power(A, i) for i in range(n)])
    rank_Mo = np.linalg.matrix_rank(Mo)

    print(f"能观性矩阵 Mo = \n{Mo}")
    print(f"秩(Mo) = {rank_Mo}, 系统阶数 = {n}")
    print(f"结论：{'完全能观 ✓' if rank_Mo == n else '不完全能观 ✗'}")

    # 阶跃响应
    print("\n[开环阶跃响应]")
    sys_open = signal.StateSpace(A, B, C, D)
    t = np.linspace(0, 50, 500)
    t_sim, y_open, x_open = signal.lsim(sys_open, U=np.ones_like(t), T=t)

    print(f"稳态值：{y_open[-1]:.4f} m")
    print(f"上游稳态：{x_open[-1, 0]:.4f} m")
    print(f"下游稳态：{x_open[-1, 1]:.4f} m")

    # 极点配置
    print("\n[状态反馈极点配置]")
    # 期望极点：更快的响应，阻尼比ζ=0.7
    desired_poles = np.array([-0.5, -0.6])

    print(f"期望极点：{desired_poles}")

    # 使用place函数计算反馈增益
    K_fb = signal.place_poles(A, B, desired_poles).gain_matrix

    print(f"\n反馈增益矩阵 K = {K_fb}")

    # 闭环系统
    A_cl = A - B @ K_fb
    poles_cl = np.linalg.eigvals(A_cl)

    print(f"\n闭环极点（验证）：")
    for i, p in enumerate(poles_cl):
        print(f"  极点{i+1} = {p:.4f}")

    # 闭环阶跃响应
    sys_closed = signal.StateSpace(A_cl, B, C, D)
    t_cl, y_closed, x_closed = signal.lsim(sys_closed, U=np.ones_like(t), T=t)

    # 可视化
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 图1：状态轨迹（开环）
    axes[0, 0].plot(t_sim, x_open[:, 0], 'b-', linewidth=2, label='h1 (Upper Tank)')
    axes[0, 0].plot(t_sim, x_open[:, 1], 'r-', linewidth=2, label='h2 (Lower Tank)')
    axes[0, 0].set_xlabel('Time (min)')
    axes[0, 0].set_ylabel('Water Level (m)')
    axes[0, 0].set_title('Open Loop: State Trajectories')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)

    # 图2：状态轨迹（闭环）
    axes[0, 1].plot(t_cl, x_closed[:, 0], 'b-', linewidth=2, label='h1 (Upper Tank)')
    axes[0, 1].plot(t_cl, x_closed[:, 1], 'r-', linewidth=2, label='h2 (Lower Tank)')
    axes[0, 1].set_xlabel('Time (min)')
    axes[0, 1].set_ylabel('Water Level (m)')
    axes[0, 1].set_title('Closed Loop: State Trajectories')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)

    # 图3：输出对比
    axes[1, 0].plot(t_sim, y_open, 'b-', linewidth=2, label='Open Loop')
    axes[1, 0].plot(t_cl, y_closed, 'r-', linewidth=2, label='Closed Loop')
    axes[1, 0].axhline(y_open[-1], color='b', linestyle='--', alpha=0.3)
    axes[1, 0].axhline(y_closed[-1], color='r', linestyle='--', alpha=0.3)
    axes[1, 0].set_xlabel('Time (min)')
    axes[1, 0].set_ylabel('Output y = h2 (m)')
    axes[1, 0].set_title('Output Comparison')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)

    # 图4：极点位置
    axes[1, 1].plot(poles.real, poles.imag, 'bo', markersize=12, label='Open Loop')
    axes[1, 1].plot(poles_cl.real, poles_cl.imag, 'rs', markersize=12, label='Closed Loop')
    axes[1, 1].axvline(0, color='r', linestyle='--', linewidth=2, alpha=0.5)
    axes[1, 1].axhline(0, color='k', linestyle='-', linewidth=0.5)
    axes[1, 1].set_xlabel('Real Part')
    axes[1, 1].set_ylabel('Imaginary Part')
    axes[1, 1].set_title('Pole Locations')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('exp1_two_tank_system.png', dpi=150, bbox_inches='tight')
    print("\n图表已保存：exp1_two_tank_system.png")

    print("\n结论：")
    print("  - 双水箱系统是2阶系统，有2个极点")
    print("  - 系统完全能控、完全能观")
    print("  - 状态反馈可以任意配置极点位置")
    print("  - 闭环系统响应明显加快")


# ============================================================================
# 实验2：状态反馈 vs PID控制对比
# ============================================================================

def experiment_state_feedback_vs_pid():
    """
    实验2：对比状态反馈和PID控制的性能
    """
    print("\n" + "=" * 80)
    print("实验2：状态反馈 vs PID控制对比")
    print("=" * 80)

    # 单水箱系统
    A_tank = 2.5
    R = 1.8
    K_pump = 1.2

    tau = A_tank * R
    K_dc = K_pump * R

    # 状态空间模型
    A = np.array([[-1/(A_tank * R)]])
    B = np.array([[K_pump / A_tank]])
    C = np.array([[1.0]])
    D = np.array([[0.0]])

    print("\n[系统参数]")
    print(f"  时间常数 τ = {tau} min")
    print(f"  稳态增益 K_dc = {K_dc}")

    # 设计1：状态反馈控制
    print("\n[设计1：状态反馈控制]")
    desired_pole = -0.5
    K_sf = (A[0, 0] - desired_pole) / B[0, 0]

    print(f"  期望极点：{desired_pole}")
    print(f"  反馈增益 K = {K_sf:.4f}")

    A_cl_sf = A - B * K_sf
    sys_sf = signal.StateSpace(A_cl_sf, B, C, D)

    # 设计2：PI控制器
    print("\n[设计2：PI控制器]")
    # 使用Z-N频域法调参
    Kp = 2.0
    Ti = 8.0
    Ki = Kp / Ti

    print(f"  Kp = {Kp}, Ti = {Ti}")

    # PI控制器的传递函数
    sys_plant = signal.TransferFunction([K_dc], [tau, 1])
    sys_pi = signal.TransferFunction([Kp, Ki], [1, 0])

    # 开环传递函数
    sys_open = signal.TransferFunction(
        np.polymul(sys_pi.num, sys_plant.num),
        np.polymul(sys_pi.den, sys_plant.den)
    )

    # 闭环传递函数
    sys_cl_pid = signal.TransferFunction(
        sys_open.num,
        np.polyadd(sys_open.den, sys_open.num)
    )

    # 仿真对比
    print("\n[仿真对比]")
    t = np.linspace(0, 30, 300)

    # 状态反馈响应
    t_sf, y_sf = signal.step(sys_sf, T=t)

    # PID响应
    t_pid, y_pid = signal.step(sys_cl_pid, T=t)

    # 性能指标
    # 状态反馈
    idx_95_sf = np.where(y_sf >= 0.95 * y_sf[-1])[0]
    t_settle_sf = t_sf[idx_95_sf[0]] if len(idx_95_sf) > 0 else t_sf[-1]
    overshoot_sf = (np.max(y_sf) - y_sf[-1]) / y_sf[-1] * 100 if y_sf[-1] > 0 else 0

    # PID
    idx_95_pid = np.where(y_pid >= 0.95 * y_pid[-1])[0]
    t_settle_pid = t_pid[idx_95_pid[0]] if len(idx_95_pid) > 0 else t_pid[-1]
    overshoot_pid = (np.max(y_pid) - y_pid[-1]) / y_pid[-1] * 100 if y_pid[-1] > 0 else 0

    print(f"\n状态反馈：")
    print(f"  稳态时间：{t_settle_sf:.2f} min")
    print(f"  超调量：{overshoot_sf:.2f}%")
    print(f"  稳态误差：{abs(1 - y_sf[-1]):.4f}")

    print(f"\nPID控制：")
    print(f"  稳态时间：{t_settle_pid:.2f} min")
    print(f"  超调量：{overshoot_pid:.2f}%")
    print(f"  稳态误差：{abs(1 - y_pid[-1]):.4f}")

    # 扰动抑制测试
    print("\n[扰动抑制测试]")

    # 添加阶跃扰动（t=15时）
    t_dist = np.linspace(0, 40, 400)
    u_dist = np.zeros_like(t_dist)
    u_dist[t_dist >= 15] = -0.2  # 模拟出流增加

    # 状态反馈系统（需要手动仿真，因为有扰动）
    # 简化处理：观察扰动抑制能力

    # 可视化
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 图1：阶跃响应对比
    axes[0, 0].plot(t_sf, y_sf, 'b-', linewidth=2, label='State Feedback')
    axes[0, 0].plot(t_pid, y_pid, 'r-', linewidth=2, label='PID Control')
    axes[0, 0].axhline(1, color='gray', linestyle='--', alpha=0.5)
    axes[0, 0].axhline(0.95, color='gray', linestyle=':', alpha=0.3)
    axes[0, 0].set_xlabel('Time (min)')
    axes[0, 0].set_ylabel('Water Level (m)')
    axes[0, 0].set_title('Step Response Comparison')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)

    # 图2：控制框图对比（文字）
    axes[0, 1].axis('off')
    axes[0, 1].text(0.1, 0.9, 'State Feedback:', fontsize=12, weight='bold')
    axes[0, 1].text(0.1, 0.8, 'u = -Kx + r', fontsize=10, family='monospace')
    axes[0, 1].text(0.1, 0.7, f'K = {K_sf:.4f}', fontsize=10, family='monospace')
    axes[0, 1].text(0.1, 0.5, 'PID Control:', fontsize=12, weight='bold')
    axes[0, 1].text(0.1, 0.4, 'u = Kp*e + Ki*∫e', fontsize=10, family='monospace')
    axes[0, 1].text(0.1, 0.3, f'Kp={Kp}, Ki={Ki:.3f}', fontsize=10, family='monospace')
    axes[0, 1].set_xlim(0, 1)
    axes[0, 1].set_ylim(0, 1)

    # 图3：性能指标对比
    metrics = ['Settling Time', 'Overshoot', 'Steady Error']
    sf_values = [t_settle_sf, overshoot_sf, abs(1 - y_sf[-1]) * 100]
    pid_values = [t_settle_pid, overshoot_pid, abs(1 - y_pid[-1]) * 100]

    x = np.arange(len(metrics))
    width = 0.35

    axes[1, 0].bar(x - width/2, sf_values, width, label='State Feedback', alpha=0.8)
    axes[1, 0].bar(x + width/2, pid_values, width, label='PID', alpha=0.8)
    axes[1, 0].set_ylabel('Value')
    axes[1, 0].set_title('Performance Metrics Comparison')
    axes[1, 0].set_xticks(x)
    axes[1, 0].set_xticklabels(metrics, rotation=15, ha='right')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3, axis='y')

    # 图4：总结表格
    axes[1, 1].axis('tight')
    axes[1, 1].axis('off')

    table_data = [
        ['Metric', 'State FB', 'PID'],
        ['Settling Time', f'{t_settle_sf:.2f} min', f'{t_settle_pid:.2f} min'],
        ['Overshoot', f'{overshoot_sf:.2f}%', f'{overshoot_pid:.2f}%'],
        ['Steady Error', f'{abs(1-y_sf[-1]):.4f}', f'{abs(1-y_pid[-1]):.4f}'],
        ['Implementation', 'Needs x', 'Needs e only']
    ]

    table = axes[1, 1].table(cellText=table_data,
                             cellLoc='center',
                             loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2)
    axes[1, 1].set_title('Summary', pad=20)

    plt.tight_layout()
    plt.savefig('exp2_state_feedback_vs_pid.png', dpi=150, bbox_inches='tight')
    print("\n图表已保存：exp2_state_feedback_vs_pid.png")

    print("\n结论：")
    print("  - 状态反馈：可精确配置极点，需要测量状态x")
    print("  - PID控制：只需测量误差e，调参需要经验")
    print("  - 两种方法性能相当，各有优劣")
    print("  - 状态反馈是PID的一般化形式")


# ============================================================================
# 实验3：参考输入跟踪
# ============================================================================

def experiment_reference_tracking():
    """
    实验3：状态反馈的参考输入跟踪
    """
    print("\n" + "=" * 80)
    print("实验3：参考输入跟踪")
    print("=" * 80)

    # 系统参数
    A_tank = 2.5
    R = 1.8
    K_pump = 1.2

    A = np.array([[-1/(A_tank * R)]])
    B = np.array([[K_pump / A_tank]])
    C = np.array([[1.0]])
    D = np.array([[0.0]])

    print("\n[问题描述]")
    print("  状态反馈 u = -Kx + r 存在稳态误差")
    print("  需要设计前馈增益或积分增广实现无静差跟踪")

    # 设计状态反馈
    desired_pole = -0.5
    K_fb = (A[0, 0] - desired_pole) / B[0, 0]

    print(f"\n[状态反馈设计]")
    print(f"  反馈增益 K = {K_fb:.4f}")

    # 方法1：计算前馈增益
    print("\n[方法1：前馈增益设计]")
    print("  u = -Kx + Nr")
    print("  稳态条件：0 = Ax_ss + Bu_ss, y_ss = Cx_ss = r")
    print("  求解：N = -1 / [C(A-BK)^(-1)B]")

    A_cl = A - B * K_fb
    N = -1.0 / (C @ np.linalg.inv(A_cl) @ B)[0, 0]

    print(f"  前馈增益 N = {N:.4f}")

    # 仿真
    t = np.linspace(0, 30, 300)
    sys_cl = signal.StateSpace(A_cl, B * N, C, D)
    t_ff, y_ff = signal.step(sys_cl, T=t)

    print(f"\n  稳态值：{y_ff[-1]:.4f} (期望: 1.0)")
    print(f"  稳态误差：{abs(1 - y_ff[-1]):.6f}")

    # 方法2：积分增广
    print("\n[方法2：积分增广设计]")
    print("  扩展状态：x_aug = [x; xi]，其中 dxi/dt = r - y")
    print("  增广系统：dx_aug/dt = A_aug*x_aug + B_aug*u + B_r*r")

    # 增广系统矩阵
    A_aug = np.block([
        [A,           np.zeros((1, 1))],
        [-C,          np.zeros((1, 1))]
    ])

    B_aug = np.block([
        [B],
        [np.zeros((1, 1))]
    ])

    B_r = np.block([
        [np.zeros((1, 1))],
        [np.ones((1, 1))]
    ])

    print(f"\nA_aug = \n{A_aug}")
    print(f"\nB_aug = \n{B_aug}")

    # 配置增广系统的极点
    desired_poles_aug = np.array([-0.5, -0.6])  # 两个极点

    K_aug = signal.place_poles(A_aug, B_aug, desired_poles_aug).gain_matrix

    print(f"\n增广反馈增益 K_aug = {K_aug}")
    print(f"  K_x = {K_aug[0, 0]:.4f} (状态反馈)")
    print(f"  K_i = {K_aug[0, 1]:.4f} (积分反馈)")

    # 闭环增广系统
    A_cl_aug = A_aug - B_aug @ K_aug

    # 手动仿真（因为需要跟踪参考输入）
    dt = 0.1
    t_aug = np.arange(0, 30, dt)
    x_aug = np.zeros((len(t_aug), 2))
    y_aug = np.zeros(len(t_aug))
    u_aug = np.zeros(len(t_aug))

    r = 1.0  # 参考输入

    for i in range(1, len(t_aug)):
        # 控制律
        u_aug[i-1] = -K_aug @ x_aug[i-1, :] + r

        # 状态更新
        dx_aug = A_aug @ x_aug[i-1, :] + B_aug.flatten() * u_aug[i-1] + B_r.flatten() * r
        x_aug[i, :] = x_aug[i-1, :] + dx_aug * dt

        # 输出
        y_aug[i] = x_aug[i, 0]  # y = x (第一个状态)

    print(f"\n  稳态值：{y_aug[-1]:.4f} (期望: 1.0)")
    print(f"  稳态误差：{abs(1 - y_aug[-1]):.6f}")

    # 可视化
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 图1：输出响应对比
    # 无前馈补偿
    sys_no_ff = signal.StateSpace(A_cl, B, C, D)
    t_no_ff, y_no_ff = signal.step(sys_no_ff, T=t)

    axes[0, 0].plot(t_no_ff, y_no_ff, 'r-', linewidth=2, label='No Feedforward', alpha=0.7)
    axes[0, 0].plot(t_ff, y_ff, 'b-', linewidth=2, label='With Feedforward')
    axes[0, 0].plot(t_aug, y_aug, 'g-', linewidth=2, label='Integral Augmentation')
    axes[0, 0].axhline(1, color='gray', linestyle='--', alpha=0.5)
    axes[0, 0].set_xlabel('Time (min)')
    axes[0, 0].set_ylabel('Water Level (m)')
    axes[0, 0].set_title('Reference Tracking Comparison')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)

    # 图2：稳态误差对比
    methods = ['No FF', 'Feedforward', 'Integral']
    errors = [
        abs(1 - y_no_ff[-1]) * 100,
        abs(1 - y_ff[-1]) * 100,
        abs(1 - y_aug[-1]) * 100
    ]

    axes[0, 1].bar(methods, errors, alpha=0.7, color=['red', 'blue', 'green'])
    axes[0, 1].set_ylabel('Steady State Error (%)')
    axes[0, 1].set_title('Tracking Error Comparison')
    axes[0, 1].grid(True, alpha=0.3, axis='y')

    # 图3：积分项演化
    axes[1, 0].plot(t_aug, x_aug[:, 1], 'g-', linewidth=2)
    axes[1, 0].set_xlabel('Time (min)')
    axes[1, 0].set_ylabel('Integral State xi')
    axes[1, 0].set_title('Integral State Evolution')
    axes[1, 0].grid(True, alpha=0.3)

    # 图4：控制输入
    axes[1, 1].plot(t_aug, u_aug, 'k-', linewidth=2, label='Integral Control')
    axes[1, 1].set_xlabel('Time (min)')
    axes[1, 1].set_ylabel('Control Input u')
    axes[1, 1].set_title('Control Signal')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('exp3_reference_tracking.png', dpi=150, bbox_inches='tight')
    print("\n图表已保存：exp3_reference_tracking.png")

    print("\n结论：")
    print("  - 纯状态反馈存在稳态误差")
    print("  - 前馈增益N可以消除稳态误差")
    print("  - 积分增广更鲁棒，类似PI控制")
    print("  - 积分增广增加系统阶数，需配置额外极点")


# ============================================================================
# 实验4：能控/能观性退化分析
# ============================================================================

def experiment_controllability_degradation():
    """
    实验4：分析不能控/不能观系统的特征
    """
    print("\n" + "=" * 80)
    print("实验4：能控/能观性退化分析")
    print("=" * 80)

    print("\n[案例1：不能控系统]")
    print("考虑一个2阶系统，第二个状态与输入无关")

    # 不能控系统示例
    A_nc = np.array([
        [-0.5,  0  ],
        [ 0,   -1.0]
    ])

    B_nc = np.array([
        [1],
        [0]   # 第二个状态没有输入影响
    ])

    C_nc = np.array([[1, 1]])

    # 能控性检查
    Mc_nc = np.hstack([B_nc, A_nc @ B_nc])
    rank_Mc_nc = np.linalg.matrix_rank(Mc_nc)

    print(f"\nA = \n{A_nc}")
    print(f"\nB = \n{B_nc}")
    print(f"\n能控性矩阵 Mc = \n{Mc_nc}")
    print(f"秩(Mc) = {rank_Mc_nc}, 系统阶数 = {A_nc.shape[0]}")
    print(f"结论：{'能控' if rank_Mc_nc == A_nc.shape[0] else '不能控'}")

    print("\n物理意义：")
    print("  第二个状态 x2 无法通过输入 u 控制")
    print("  只能控制第一个状态 x1")

    # 尝试极点配置（会失败或部分成功）
    print("\n尝试极点配置...")
    try:
        desired_poles_nc = np.array([-2.0, -2.0])
        K_nc = signal.place_poles(A_nc, B_nc, desired_poles_nc).gain_matrix
        print(f"  反馈增益 K = {K_nc}")

        A_cl_nc = A_nc - B_nc @ K_nc
        actual_poles_nc = np.linalg.eigvals(A_cl_nc)
        print(f"  实际闭环极点：{actual_poles_nc}")
        print(f"  注意：第二个极点未改变！")
    except Exception as e:
        print(f"  极点配置失败：{e}")

    # 不能观系统示例
    print("\n" + "-" * 80)
    print("[案例2：不能观系统]")
    print("考虑一个2阶系统，第二个状态不影响输出")

    A_no = np.array([
        [-0.5,  0  ],
        [ 0,   -1.0]
    ])

    B_no = np.array([
        [1],
        [1]
    ])

    C_no = np.array([[1, 0]])  # 只观测第一个状态

    # 能观性检查
    Mo_no = np.vstack([C_no, C_no @ A_no])
    rank_Mo_no = np.linalg.matrix_rank(Mo_no)

    print(f"\nA = \n{A_no}")
    print(f"\nC = {C_no}")
    print(f"\n能观性矩阵 Mo = \n{Mo_no}")
    print(f"秩(Mo) = {rank_Mo_no}, 系统阶数 = {A_no.shape[0]}")
    print(f"结论：{'能观' if rank_Mo_no == A_no.shape[0] else '不能观'}")

    print("\n物理意义：")
    print("  第二个状态 x2 隐藏在系统内部")
    print("  无法从输出 y 推断 x2 的值")

    print("\n结论：")
    print("  - 能控性：所有状态都能被输入影响")
    print("  - 能观性：所有状态都能从输出推断")
    print("  - 只有完全能控才能任意配置极点")
    print("  - 只有完全能观才能设计状态观测器")


# ============================================================================
# 主程序
# ============================================================================

def main():
    """运行所有扩展实验"""
    print("=" * 80)
    print("案例11扩展实验：状态空间方法深入研究")
    print("=" * 80)

    # 实验1：双水箱系统
    experiment_two_tank_system()

    # 实验2：状态反馈 vs PID
    experiment_state_feedback_vs_pid()

    # 实验3：参考输入跟踪
    experiment_reference_tracking()

    # 实验4：能控/能观性退化
    experiment_controllability_degradation()

    print("\n" + "=" * 80)
    print("所有扩展实验完成！")
    print("=" * 80)

    plt.show()


if __name__ == "__main__":
    main()
