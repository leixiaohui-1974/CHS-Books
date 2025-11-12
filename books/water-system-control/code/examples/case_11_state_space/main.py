#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
案例11：状态空间方法 - 现代控制理论入门

场景描述：
工程师使用现代控制理论分析和设计水箱控制系统。
将系统转换为状态空间表示，分析能控性和能观性，
设计状态反馈控制器，并通过极点配置实现期望性能。

教学目标：
1. 掌握状态空间建模方法
2. 理解能控性和能观性概念
3. 学习状态反馈控制器设计
4. 掌握极点配置技术
5. 对比现代控制与经典控制

分析步骤：
1. 建立状态空间模型
2. 分析能控性和能观性
3. 设计状态反馈控制器
4. 进行极点配置
5. 验证闭环系统性能

关键概念：
- 状态空间表示
- 能控性矩阵
- 能观性矩阵
- 状态反馈
- 极点配置

作者：CHS-Books项目
日期：2025-10-30
版本：1.0
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')  # 必须在import pyplot之前设置
import matplotlib.pyplot as plt
from scipy import signal
from scipy import linalg
import sys
import io
from pathlib import Path

# 设置标准输出为UTF-8编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加项目路径
project_root = Path(__file__).parents[3]
sys.path.insert(0, str(project_root))

from code.models.water_tank.single_tank import SingleTank

# 设置matplotlib
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


# ============================================================================
# 第1部分：状态空间建模
# ============================================================================

def state_space_modeling():
    """
    第1部分：从传递函数推导状态空间模型
    """
    print("=" * 80)
    print("第1部分：状态空间建模")
    print("=" * 80)

    # 系统参数
    A_tank = 2.5  # m^2
    R = 1.8      # min/m^2
    K = 1.2      # m^3/min

    tau = A_tank * R
    K_dc = K * R

    print("\n[单水箱系统参数]")
    print(f"  横截面积 A = {A_tank} m²")
    print(f"  阻力系数 R = {R} min/m²")
    print(f"  泵增益 K = {K} m³/min")
    print(f"  时间常数 τ = A×R = {tau} min")
    print(f"  稳态增益 K_dc = K×R = {K_dc}")

    # 传递函数表示
    print("\n[传递函数表示]")
    print("         K_dc          2.16")
    print("  G(s) = ------- = -----------")
    print("         τs + 1     4.5s + 1")

    sys_tf = signal.TransferFunction([K_dc], [tau, 1])

    # 状态空间表示
    # 选择状态变量 x = h (水位)
    # 状态方程：dx/dt = A*x + B*u
    # 输出方程：y = C*x + D*u

    # 从微分方程推导：
    # A*dh/dt = K*u - h/R
    # dh/dt = -1/(A*R)*h + K/A*u
    # y = h

    A_ss = np.array([[-1/(A_tank * R)]])  # 1x1矩阵
    B_ss = np.array([[K / A_tank]])
    C_ss = np.array([[1.0]])
    D_ss = np.array([[0.0]])

    print("\n[状态空间表示]")
    print("状态方程：dx/dt = Ax + Bu")
    print("输出方程：y = Cx + Du")
    print("\n系统矩阵：")
    print(f"  A = {A_ss[0, 0]:.4f}")
    print(f"  B = {B_ss[0, 0]:.4f}")
    print(f"  C = {C_ss[0, 0]:.4f}")
    print(f"  D = {D_ss[0, 0]:.4f}")

    # 验证：从状态空间转换为传递函数
    sys_ss = signal.StateSpace(A_ss, B_ss, C_ss, D_ss)
    num_from_ss, den_from_ss = signal.ss2tf(A_ss, B_ss, C_ss, D_ss)

    print("\n[验证：状态空间→传递函数]")
    print(f"  分子系数：{num_from_ss}")
    print(f"  分母系数：{den_from_ss}")

    # 提取增益和极点（注意ss2tf返回归一化的传递函数）
    # 分子最后一项是增益
    if len(num_from_ss.shape) > 1:
        gain_from_ss = num_from_ss[0, -1] if num_from_ss[0, -1] != 0 else num_from_ss[0, -2]
    else:
        gain_from_ss = num_from_ss[-1] if num_from_ss[-1] != 0 else num_from_ss[-2]

    print(f"  传递函数增益（稳态）：{gain_from_ss / den_from_ss[0]:.4f} (应约为 {K_dc:.4f})")

    # 从状态矩阵A直接获取极点更准确
    pole_from_A = A_ss[0, 0]
    print(f"  系统极点（从A矩阵）：{pole_from_A:.4f} (应为 {-1/tau:.4f})")

    # 系统极点
    poles = np.linalg.eigvals(A_ss)
    print("\n[开环系统极点]")
    print(f"  极点 = {poles[0]:.4f}")
    print(f"  时间常数 τ = {-1/poles[0]:.2f} min")

    return A_ss, B_ss, C_ss, D_ss, sys_ss


# ============================================================================
# 第2部分：能控性和能观性分析
# ============================================================================

def controllability_observability_analysis(A, B, C):
    """
    第2部分：分析系统的能控性和能观性
    """
    print("\n" + "=" * 80)
    print("第2部分：能控性和能观性分析")
    print("=" * 80)

    n = A.shape[0]  # 系统阶数

    # 能控性分析
    print("\n[能控性分析]")
    print("能控性矩阵 Mc = [B  AB  A²B  ...  A^(n-1)B]")

    # 构造能控性矩阵
    Mc = np.zeros((n, n))
    for i in range(n):
        if i == 0:
            Mc[:, i:i+1] = B
        else:
            Mc[:, i:i+1] = np.linalg.matrix_power(A, i) @ B

    print(f"\n  Mc = {Mc}")
    rank_Mc = np.linalg.matrix_rank(Mc)
    print(f"  秩(Mc) = {rank_Mc}")
    print(f"  系统阶数 n = {n}")

    if rank_Mc == n:
        print("  结论：系统完全能控 ✓")
        controllable = True
    else:
        print(f"  结论：系统不完全能控 ✗ (能控维数 = {rank_Mc})")
        controllable = False

    print("\n物理意义：")
    print("  能控 → 控制输入u可以影响状态x")
    print("  对于单水箱：泵流量u可以控制水位h → 系统能控")

    # 能观性分析
    print("\n" + "-" * 80)
    print("[能观性分析]")
    print("能观性矩阵 Mo = [C; CA; CA²; ...; CA^(n-1)]")

    # 构造能观性矩阵
    Mo = np.zeros((n, n))
    for i in range(n):
        if i == 0:
            Mo[i:i+1, :] = C
        else:
            Mo[i:i+1, :] = C @ np.linalg.matrix_power(A, i)

    print(f"\n  Mo = {Mo}")
    rank_Mo = np.linalg.matrix_rank(Mo)
    print(f"  秩(Mo) = {rank_Mo}")
    print(f"  系统阶数 n = {n}")

    if rank_Mo == n:
        print("  结论：系统完全能观 ✓")
        observable = True
    else:
        print(f"  结论：系统不完全能观 ✗ (能观维数 = {rank_Mo})")
        observable = False

    print("\n物理意义：")
    print("  能观 → 可以从输出y推断状态x")
    print("  对于单水箱：输出y=h直接测量水位 → 系统能观")

    # 对偶性
    print("\n" + "-" * 80)
    print("[对偶性验证]")
    print("理论：(A, B)能控 ⟺ (A^T, C^T)能观")

    # 检查(A^T, C^T)的能观性
    A_dual = A.T
    C_dual = B.T
    Mo_dual = np.zeros((n, n))
    for i in range(n):
        if i == 0:
            Mo_dual[i:i+1, :] = C_dual
        else:
            Mo_dual[i:i+1, :] = C_dual @ np.linalg.matrix_power(A_dual, i)

    rank_Mo_dual = np.linalg.matrix_rank(Mo_dual)

    print(f"  (A, B)能控性：秩(Mc) = {rank_Mc}")
    print(f"  (A^T, C^T)能观性：秩(Mo_dual) = {rank_Mo_dual}")
    print(f"  对偶性满足：{rank_Mc == rank_Mo_dual} ✓")

    return controllable, observable, Mc, Mo


# ============================================================================
# 第3部分：状态反馈控制器设计
# ============================================================================

def state_feedback_control(A, B, C, D):
    """
    第3部分：设计状态反馈控制器
    """
    print("\n" + "=" * 80)
    print("第3部分：状态反馈控制器设计")
    print("=" * 80)

    print("\n[控制律设计]")
    print("  控制律：u = -Kx + r")
    print("  闭环系统：dx/dt = (A - BK)x + Br")

    # 开环极点
    poles_open = np.linalg.eigvals(A)
    print(f"\n[开环系统特性]")
    print(f"  极点：{poles_open[0]:.4f}")
    print(f"  时间常数：{-1/poles_open[0]:.2f} min")

    # 设计目标：将极点从-0.222移至-0.5（加快响应）
    desired_poles = np.array([-0.5])

    print(f"\n[设计目标]")
    print(f"  期望极点：{desired_poles[0]:.4f}")
    print(f"  期望时间常数：{-1/desired_poles[0]:.2f} min")

    # 使用极点配置计算K
    # 闭环系统：dx/dt = (A - BK)x
    # 闭环极点：A_cl = A - BK = p_desired
    # 求解：BK = A - p_desired
    #      K = (A - p_desired) / B

    K = (A[0, 0] - desired_poles[0]) / B[0, 0]

    print(f"\n[反馈增益计算]")
    print(f"  K = {K:.4f}")

    # 闭环系统矩阵
    A_cl = A - B @ np.array([[K]])

    print(f"\n[闭环系统矩阵]")
    print(f"  A_cl = A - BK = {A_cl[0, 0]:.4f}")

    # 验证闭环极点
    poles_closed = np.linalg.eigvals(A_cl)
    print(f"\n[闭环极点验证]")
    print(f"  期望极点：{desired_poles[0]:.4f}")
    print(f"  实际极点：{poles_closed[0]:.4f}")
    print(f"  误差：{abs(poles_closed[0] - desired_poles[0]):.6f}")

    # 时域仿真对比
    print(f"\n[仿真对比：开环 vs 闭环]")

    t = np.linspace(0, 30, 300)
    t_span = (t[0], t[-1])

    # 开环阶跃响应
    sys_open = signal.StateSpace(A, B, C, D)
    t_open, y_open = signal.step(sys_open, T=t)

    # 闭环阶跃响应
    sys_closed = signal.StateSpace(A_cl, B, C, D)
    t_closed, y_closed = signal.step(sys_closed, T=t)

    # 计算性能指标
    # 开环
    idx_95_open = np.where(y_open >= 0.95 * y_open[-1])[0]
    t_settle_open = t_open[idx_95_open[0]] if len(idx_95_open) > 0 else t_open[-1]

    # 闭环
    idx_95_closed = np.where(y_closed >= 0.95 * y_closed[-1])[0]
    t_settle_closed = t_closed[idx_95_closed[0]] if len(idx_95_closed) > 0 else t_closed[-1]

    print(f"\n  开环稳态时间：{t_settle_open:.2f} min")
    print(f"  闭环稳态时间：{t_settle_closed:.2f} min")
    print(f"  改善比例：{t_settle_open / t_settle_closed:.2f}x")

    return K, A_cl, poles_closed, t_open, y_open, t_closed, y_closed


# ============================================================================
# 第4部分：极点配置实验
# ============================================================================

def pole_placement_experiments(A, B, C, D):
    """
    第4部分：不同极点配置的性能对比
    """
    print("\n" + "=" * 80)
    print("第4部分：极点配置实验")
    print("=" * 80)

    print("\n[实验：不同极点位置的影响]")

    # 开环极点
    pole_open = A[0, 0]

    # 测试不同的极点配置
    pole_configs = [
        ("Very Slow", -0.1, "保守设计"),
        ("Open Loop", pole_open, "原始系统"),
        ("Moderate", -0.5, "平衡设计"),
        ("Fast", -1.0, "激进设计"),
        ("Very Fast", -2.0, "非常快")
    ]

    results = []
    t = np.linspace(0, 30, 300)

    print("\n配置方案：")
    for name, pole_desired, description in pole_configs:
        # 计算反馈增益
        if pole_desired == pole_open:
            K = 0.0  # 开环，无反馈
        else:
            K = (A[0, 0] - pole_desired) / B[0, 0]

        # 闭环系统
        A_cl = A - B @ np.array([[K]])

        # 阶跃响应
        sys_closed = signal.StateSpace(A_cl, B, C, D)
        t_sim, y = signal.step(sys_closed, T=t)

        # 性能指标
        idx_95 = np.where(y >= 0.95 * y[-1])[0]
        t_settle = t_sim[idx_95[0]] if len(idx_95) > 0 else t_sim[-1]

        idx_63 = np.where(y >= 0.63 * y[-1])[0]
        t_63 = t_sim[idx_63[0]] if len(idx_63) > 0 else t_sim[-1]

        results.append({
            'name': name,
            'pole': pole_desired,
            'description': description,
            'K': K,
            't': t_sim,
            'y': y,
            't_settle': t_settle,
            't_63': t_63
        })

        print(f"\n{name} ({description}):")
        print(f"  极点：{pole_desired:.4f}")
        print(f"  反馈增益 K：{K:.4f}")
        print(f"  时间常数：{-1/pole_desired:.2f} min" if pole_desired < 0 else "  不稳定")
        print(f"  稳态时间：{t_settle:.2f} min")

    return results


# ============================================================================
# 第5部分：可视化与总结
# ============================================================================

def visualize_and_summarize(A, B, C, D, K, A_cl, t_open, y_open, t_closed, y_closed, pole_results):
    """
    第5部分：综合可视化和总结
    """
    print("\n" + "=" * 80)
    print("第5部分：可视化与总结")
    print("=" * 80)

    fig = plt.figure(figsize=(16, 12))
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

    # 图1：系统框图（文字描述）
    ax1 = fig.add_subplot(gs[0, :])
    ax1.axis('off')
    ax1.text(0.5, 0.8, 'State Space Model', ha='center', fontsize=16, weight='bold')
    ax1.text(0.5, 0.6, 'dx/dt = Ax + Bu', ha='center', fontsize=14, family='monospace')
    ax1.text(0.5, 0.4, 'y = Cx + Du', ha='center', fontsize=14, family='monospace')
    ax1.text(0.5, 0.2, f'A={A[0,0]:.4f}, B={B[0,0]:.4f}, C={C[0,0]:.1f}, D={D[0,0]:.1f}',
             ha='center', fontsize=12, family='monospace')
    ax1.set_xlim(0, 1)
    ax1.set_ylim(0, 1)

    # 图2：开环 vs 闭环阶跃响应
    ax2 = fig.add_subplot(gs[1, 0])
    ax2.plot(t_open, y_open, 'b-', linewidth=2, label='Open Loop')
    ax2.plot(t_closed, y_closed, 'r-', linewidth=2, label=f'Closed Loop (K={K:.3f})')
    ax2.axhline(1, color='gray', linestyle='--', alpha=0.5)
    ax2.axhline(0.95, color='gray', linestyle=':', alpha=0.5, label='95% settling')
    ax2.set_xlabel('Time (min)')
    ax2.set_ylabel('Water Level (m)')
    # 标题已移除，保持图表简洁
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    # 图3：不同极点配置的响应
    ax3 = fig.add_subplot(gs[1, 1])
    for res in pole_results:
        ax3.plot(res['t'], res['y'], linewidth=2, label=f"{res['name']} (p={res['pole']:.2f})")
    ax3.axhline(1, color='gray', linestyle='--', alpha=0.5)
    ax3.set_xlabel('Time (min)')
    ax3.set_ylabel('Water Level (m)')
    # 标题已移除，保持图表简洁
    ax3.legend(fontsize=8)
    ax3.grid(True, alpha=0.3)

    # 图4：极点位置图
    ax4 = fig.add_subplot(gs[1, 2])
    # 开环极点
    ax4.plot(A[0, 0], 0, 'bo', markersize=12, label='Open Loop')
    # 闭环极点
    ax4.plot(A_cl[0, 0], 0, 'rs', markersize=12, label='Closed Loop')
    # 其他极点
    for i, res in enumerate(pole_results):
        if res['name'] not in ['Open Loop']:
            ax4.plot(res['pole'], 0, 'g^', markersize=8, alpha=0.6)
            if i % 2 == 0:  # 只标注部分，避免拥挤
                ax4.text(res['pole'], 0.05, res['name'], fontsize=8, ha='center')

    ax4.axvline(0, color='r', linestyle='--', linewidth=2, alpha=0.5, label='Stability Boundary')
    ax4.axhline(0, color='k', linestyle='-', linewidth=0.5)
    ax4.set_xlabel('Real Part')
    ax4.set_ylabel('Imaginary Part')
    # 标题已移除，保持图表简洁
    ax4.legend(fontsize=8)
    ax4.grid(True, alpha=0.3)
    ax4.set_ylim(-0.2, 0.2)

    # 图5：稳态时间 vs 极点位置
    ax5 = fig.add_subplot(gs[2, 0])
    poles_list = [res['pole'] for res in pole_results]
    t_settle_list = [res['t_settle'] for res in pole_results]
    colors = ['blue' if p == A[0,0] else 'red' if p == A_cl[0,0] else 'green'
              for p in poles_list]

    ax5.scatter(poles_list, t_settle_list, c=colors, s=100, alpha=0.7)
    for res in pole_results:
        ax5.text(res['pole'], res['t_settle'], res['name'], fontsize=8, ha='right')

    ax5.set_xlabel('Pole Location')
    ax5.set_ylabel('Settling Time (min)')
    # 标题已移除，保持图表简洁
    ax5.grid(True, alpha=0.3)
    ax5.invert_xaxis()  # 更负的极点在右边

    # 图6：反馈增益 vs 极点位置
    ax6 = fig.add_subplot(gs[2, 1])
    K_list = [res['K'] for res in pole_results]

    ax6.scatter(poles_list, K_list, c=colors, s=100, alpha=0.7)
    for res in pole_results:
        if res['name'] != 'Open Loop':  # 开环K=0不标注
            ax6.text(res['pole'], res['K'], res['name'], fontsize=8, ha='right')

    ax6.axhline(0, color='k', linestyle='-', linewidth=0.5)
    ax6.set_xlabel('Pole Location')
    ax6.set_ylabel('Feedback Gain K')
    # 标题已移除，保持图表简洁
    ax6.grid(True, alpha=0.3)

    # 图7：性能总结表格
    ax7 = fig.add_subplot(gs[2, 2])
    ax7.axis('tight')
    ax7.axis('off')

    table_data = []
    for res in pole_results[:4]:  # 只显示前4个
        table_data.append([
            res['name'],
            f"{res['pole']:.2f}",
            f"{res['K']:.3f}",
            f"{res['t_settle']:.1f}"
        ])

    table = ax7.table(cellText=table_data,
                      colLabels=['Config', 'Pole', 'K', 'Ts(min)'],
                      cellLoc='center',
                      loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2)
    # 标题已移除，保持图表简洁

    plt.savefig('case11_state_space_summary.png', dpi=150, bbox_inches='tight')
    print("\n图表已保存：case11_state_space_summary.png")

    # 最终总结
    print("\n" + "=" * 80)
    print("案例11总结")
    print("=" * 80)

    print("\n[关键知识点]")
    print("  1. 状态空间建模：")
    print(f"     • 系统矩阵 A = {A[0,0]:.4f}, B = {B[0,0]:.4f}")
    print("     • 与传递函数等价，但更适合MIMO系统")
    print("")
    print("  2. 能控性和能观性：")
    print("     • 单水箱系统完全能控、完全能观")
    print("     • 这是状态反馈控制的前提")
    print("")
    print("  3. 状态反馈控制：")
    print(f"     • 反馈增益 K = {K:.4f}")
    print(f"     • 闭环极点从 {A[0,0]:.4f} 移至 {A_cl[0,0]:.4f}")
    print("     • 响应速度提升明显")
    print("")
    print("  4. 极点配置：")
    print("     • 极点越负，响应越快")
    print("     • 但需要更大的控制增益")
    print("     • 实际设计需权衡性能和控制代价")
    print("")
    print("  5. 现代控制 vs 经典控制：")
    print("     • 状态空间：内部状态显式，适合MIMO")
    print("     • 传递函数：输入输出关系，适合SISO")
    print("     • 两者可以相互转换")

    print("\n[工程应用]")
    print("  • 多变量系统控制（双水箱、多级系统）")
    print("  • 最优控制设计（LQR、LQG）")
    print("  • 状态观测器设计（Kalman滤波）")
    print("  • 非线性系统分析（线性化、相平面）")

    print("\n[下一步学习]")
    print("  → 案例12：状态观测器与LQR最优控制")
    print("  → 案例13：鲁棒控制与不确定性处理")

    print("\n" + "=" * 80)
    print("案例11演示完成！")
    print("=" * 80)


# ============================================================================
# 主程序
# ============================================================================

def main():
    """主程序：运行所有分析步骤"""
    print("=" * 80)
    print("案例11：状态空间方法 - 现代控制理论入门")
    print("=" * 80)

    # 第1部分：状态空间建模
    A, B, C, D, sys_ss = state_space_modeling()

    # 第2部分：能控性和能观性分析
    controllable, observable, Mc, Mo = controllability_observability_analysis(A, B, C)

    # 第3部分：状态反馈控制器设计
    K, A_cl, poles_closed, t_open, y_open, t_closed, y_closed = state_feedback_control(A, B, C, D)

    # 第4部分：极点配置实验
    pole_results = pole_placement_experiments(A, B, C, D)

    # 第5部分：可视化与总结
    visualize_and_summarize(A, B, C, D, K, A_cl, t_open, y_open, t_closed, y_closed, pole_results)

    plt.show()


if __name__ == "__main__":
    main()
