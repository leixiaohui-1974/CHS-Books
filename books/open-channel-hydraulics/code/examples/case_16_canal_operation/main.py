"""
案例16：渠道非恒定流调度 - 主程序

问题描述：
某灌溉渠道需要根据下游用水需求调整闸门开度，
模拟闸门调度过程和渠道水位响应。

参数：
- 渠道长度 L = 5000 m
- 渠道宽度 b = 10.0 m
- 渠道坡度 S₀ = 0.0002
- 糙率系数 n = 0.025
- 初始流量 Q₀ = 20 m³/s

作者：CHS-Books项目
日期：2025-10-29
"""

import sys
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')  # 非交互式后端
import matplotlib.pyplot as plt

# 添加代码库路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from models.channel import RectangularChannel
from solvers.saint_venant import SaintVenantSolver


def print_separator(title="", width=80):
    """打印分隔线"""
    if title:
        print(f"\n{'='*width}")
        print(f"{title:^{width}}")
        print(f"{'='*width}")
    else:
        print(f"{'='*width}")


def gate_opening_schedule(t, schedule_type='linear_increase', t_start=0, t_end=3600,
                         a_init=0.5, a_final=0.8, gate_height=3.0):
    """
    闸门开度调节时程

    Args:
        t: 时间 (s)
        schedule_type: 调度类型
        t_start: 开始时间 (s)
        t_end: 结束时间 (s)
        a_init: 初始开度（相对高度，0-1）
        a_final: 最终开度（相对高度，0-1）
        gate_height: 闸门总高度 (m)

    Returns:
        a: 实际开度 (m)
    """
    if t < t_start:
        return a_init * gate_height
    elif t > t_end:
        return a_final * gate_height

    # 归一化时间 [0, 1]
    tau = (t - t_start) / (t_end - t_start)

    if schedule_type == 'linear_increase':
        # 线性增加
        a_rel = a_init + (a_final - a_init) * tau
    elif schedule_type == 'linear_decrease':
        # 线性减少
        a_rel = a_init + (a_final - a_init) * tau
    elif schedule_type == 'exponential':
        # 指数曲线（平滑过渡）
        alpha = 3.0  # 时间常数
        a_rel = a_init + (a_final - a_init) * (1 - np.exp(-alpha * tau))
    elif schedule_type == 's_curve':
        # S型曲线（最平滑）
        a_rel = a_init + (a_final - a_init) * 0.5 * (1 + np.tanh(6 * (tau - 0.5)))
    elif schedule_type == 'step':
        # 阶跃变化
        a_rel = a_final if tau > 0.5 else a_init
    else:
        # 默认线性
        a_rel = a_init + (a_final - a_init) * tau

    return a_rel * gate_height


def compute_gate_discharge(a, h1, b, Cd=0.6, g=9.81):
    """
    计算闸门出流量（自由出流）

    Args:
        a: 闸门开度 (m)
        h1: 上游水深 (m)
        b: 渠道宽度 (m)
        Cd: 流量系数
        g: 重力加速度 (m/s²)

    Returns:
        Q: 流量 (m³/s)
    """
    if h1 <= a:
        # 闸门全开或水深不足，按堰流计算
        Q = 1.7 * b * h1**(1.5)
    else:
        # 自由出流
        Q = Cd * b * a * np.sqrt(2 * g * h1)

    return max(Q, 0.1)  # 避免零流量


def main():
    """主函数"""
    print_separator("案例16：渠道非恒定流调度")

    # ==================== 第一步：定义渠道参数 ====================
    print("\n【步骤1】渠道系统参数")
    print("-" * 80)

    L = 5000.0    # 渠道长度 (m)
    b = 10.0      # 渠道宽度 (m)
    S0 = 0.0002   # 渠道坡度
    n = 0.025     # 糙率系数（混凝土衬砌）
    Q0 = 20.0     # 初始流量 (m³/s)
    g = 9.81

    print(f"渠道几何：")
    print(f"  长度 L = {L/1000:.1f} km")
    print(f"  宽度 b = {b} m")
    print(f"  坡度 S₀ = {S0}")
    print(f"  糙率 n = {n}")

    print(f"\n初始状态：")
    print(f"  初始流量 Q₀ = {Q0} m³/s")

    # ==================== 第二步：计算初始稳态 ====================
    print("\n【步骤2】计算初始稳态流动")
    print("-" * 80)

    # 创建渠道对象
    channel = RectangularChannel(b=b, S0=S0, n=n)

    # 计算初始正常水深
    h0 = channel.compute_normal_depth(Q0)
    v0 = Q0 / (b * h0)
    Fr0 = v0 / np.sqrt(g * h0)
    c0 = np.sqrt(g * h0)

    print(f"\n初始水力参数：")
    print(f"  正常水深 h₀ = {h0:.3f} m")
    print(f"  流速 v₀ = {v0:.3f} m/s")
    print(f"  Froude数 Fr₀ = {Fr0:.3f}")
    print(f"  波速 c = {c0:.3f} m/s")
    print(f"  流态：{'缓流' if Fr0 < 1 else '急流'}")

    # 波传播时间估算
    t_wave = L / (v0 + c0)
    print(f"\n波传播时间估算：")
    print(f"  上游→下游：t ≈ L/(v+c) = {t_wave:.0f} s = {t_wave/60:.1f} min")

    # ==================== 第三步：定义调度场景 ====================
    print("\n【步骤3】定义调度场景")
    print("-" * 80)

    # 场景：增加供水（闸门开度从50%增至80%）
    gate_height = 3.0  # 闸门总高度 (m)
    a_init_rel = 0.50  # 初始开度（相对）
    a_final_rel = 0.80  # 最终开度（相对）

    t_schedule_start = 600.0   # 调度开始时间 (s) = 10 min
    t_schedule_end = 1800.0    # 调度结束时间 (s) = 30 min

    print(f"\n调度场景：增加供水")
    print(f"  闸门总高度 H = {gate_height} m")
    print(f"  初始开度 = {a_init_rel*100:.0f}% = {a_init_rel*gate_height:.2f} m")
    print(f"  最终开度 = {a_final_rel*100:.0f}% = {a_final_rel*gate_height:.2f} m")
    print(f"  调度时段 = {t_schedule_start/60:.0f} ~ {t_schedule_end/60:.0f} min")
    print(f"  调度类型 = S曲线（平滑过渡）")

    # ==================== 第四步：数值模拟设置 ====================
    print("\n【步骤4】数值模拟设置")
    print("-" * 80)

    dx = 100.0  # 空间步长 (m)
    nx = int(L / dx) + 1
    t_total = 4 * 3600.0  # 总模拟时长 4小时

    print(f"\n网格参数：")
    print(f"  空间步长 Δx = {dx} m")
    print(f"  节点数 nx = {nx}")
    print(f"  模拟时长 = {t_total/3600:.0f} 小时")
    print(f"  时间步长：自动（CFL=0.4）")

    # ==================== 第五步：创建求解器 ====================
    print("\n【步骤5】创建Saint-Venant求解器")
    print("-" * 80)

    solver = SaintVenantSolver(L=L, b=b, S0=S0, n=n, dx=dx, dt=None, g=g)

    # 初始条件：稳态分布
    h_init = np.full(nx, h0)
    Q_init = np.full(nx, Q0)
    solver.set_initial_conditions(h_init, Q_init)

    print(f"求解器：{solver}")
    print(f"\n初始条件：均匀流")
    print(f"  水深 h(x,0) = {h0:.3f} m")
    print(f"  流量 Q(x,0) = {Q0:.2f} m³/s")

    # ==================== 第六步：设置边界条件 ====================
    print("\n【步骤6】边界条件")
    print("-" * 80)

    # 上游边界：闸门控制流量（简化为直接给定流量）
    def bc_upstream(t):
        """上游闸门边界条件"""
        # 根据闸门开度比例计算流量变化
        # 简化：假设流量与开度成正比
        if t < t_schedule_start:
            Q_rel = a_init_rel
        elif t > t_schedule_end:
            Q_rel = a_final_rel
        else:
            tau = (t - t_schedule_start) / (t_schedule_end - t_schedule_start)
            # S曲线
            Q_rel = a_init_rel + (a_final_rel - a_init_rel) * 0.5 * (1 + np.tanh(6 * (tau - 0.5)))

        # 计算实际流量（相对于最大流量40 m³/s）
        Q_max = 40.0  # 最大流量
        Q = Q_rel * Q_max

        # 计算对应的水深
        h = channel.compute_normal_depth(Q) if Q > 0.1 else h0

        return h, Q

    # 下游边界：自由出流（外推）
    solver.set_boundary_conditions(upstream=bc_upstream, downstream=None)

    print(f"边界条件设置：")
    print(f"  上游：闸门控制流量（时变）")
    print(f"  下游：自由出流（外推边界）")

    # ==================== 第七步：运行模拟 ====================
    print("\n【步骤7】运行模拟")
    print("-" * 80)

    dt_output = 300.0  # 每5分钟输出一次

    print(f"\n开始计算...")
    print(f"输出间隔：{dt_output/60:.0f} 分钟")

    try:
        results = solver.run(t_end=t_total, dt_output=dt_output, verbose=True)
        print(f"\n计算完成！")
        print(f"总时间步数：{solver.time_step}")
    except Exception as e:
        print(f"\n计算出错：{e}")
        import traceback
        traceback.print_exc()
        return

    # ==================== 第八步：结果分析 ====================
    print("\n【步骤8】调度效果分析")
    print("-" * 80)

    times = results['times']
    h_results = results['h']
    Q_results = results['Q']
    x_grid = results['x']

    # 分析关键断面
    idx_upstream = 0
    idx_mid = nx // 2
    idx_downstream = -1

    print(f"\n关键断面水位变化：")
    print("-" * 100)
    print(f"{'时间(min)':^12} | {'上游水深(m)':^14} | {'中游水深(m)':^14} | {'下游水深(m)':^14}")
    print("-" * 100)

    for i in [0, len(times)//4, len(times)//2, 3*len(times)//4, -1]:
        t = times[i]
        h_up = h_results[i, idx_upstream]
        h_mid = h_results[i, idx_mid]
        h_down = h_results[i, idx_downstream]

        print(f"{t/60:^12.0f} | {h_up:^14.3f} | {h_mid:^14.3f} | {h_down:^14.3f}")

    print("-" * 100)

    # 分析流量变化
    print(f"\n关键断面流量变化：")
    print("-" * 100)
    print(f"{'时间(min)':^12} | {'上游流量(m³/s)':^18} | {'中游流量(m³/s)':^18} | {'下游流量(m³/s)':^18}")
    print("-" * 100)

    for i in [0, len(times)//4, len(times)//2, 3*len(times)//4, -1]:
        t = times[i]
        Q_up = Q_results[i, idx_upstream]
        Q_mid = Q_results[i, idx_mid]
        Q_down = Q_results[i, idx_downstream]

        print(f"{t/60:^12.0f} | {Q_up:^18.2f} | {Q_mid:^18.2f} | {Q_down:^18.2f}")

    print("-" * 100)

    # 响应时间分析
    print(f"\n响应时间分析：")

    # 找到下游流量达到稳定的时间
    Q_down_series = Q_results[:, idx_downstream]
    Q_down_final = Q_down_series[-1]
    Q_down_90 = 0.9 * (Q_down_final - Q0) + Q0

    idx_90 = np.where(Q_down_series >= Q_down_90)[0]
    if len(idx_90) > 0:
        t_90 = times[idx_90[0]]
        print(f"  下游流量达到90%新值的时间：{t_90/60:.1f} min")
        print(f"  响应延迟：{(t_90 - t_schedule_start)/60:.1f} min")

    # ==================== 第九步：绘制结果 ====================
    print("\n【步骤9】绘制分析图形")
    print("-" * 80)

    # 配置中文字体
    plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('渠道非恒定流调度分析', fontsize=16, fontweight='bold')

    # 图1：闸门开度和上游流量时程
    ax1 = axes[0, 0]
    t_plot = np.linspace(0, t_total, 500)
    a_plot = np.array([gate_opening_schedule(t, 's_curve', t_schedule_start, t_schedule_end,
                                             a_init_rel, a_final_rel, gate_height) for t in t_plot])

    ax1_twin = ax1.twinx()
    line1 = ax1.plot(t_plot/60, a_plot, 'b-', linewidth=2, label='闸门开度')
    line2 = ax1_twin.plot(times/60, Q_results[:, idx_upstream], 'r-', linewidth=2, label='上游流量')

    ax1.set_xlabel('时间 (min)', fontsize=12)
    ax1.set_ylabel('闸门开度 (m)', fontsize=12, color='b')
    ax1_twin.set_ylabel('流量 (m³/s)', fontsize=12, color='r')
    ax1.tick_params(axis='y', labelcolor='b')
    ax1_twin.tick_params(axis='y', labelcolor='r')
    ax1.set_title('闸门调度时程', fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3)

    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, fontsize=10)

    # 图2：不同位置的流量响应
    ax2 = axes[0, 1]
    ax2.plot(times/60, Q_results[:, idx_upstream], '-', linewidth=2, label='上游（x=0）')
    ax2.plot(times/60, Q_results[:, idx_mid], '-', linewidth=2, label=f'中游（x={L/2000:.1f}km）')
    ax2.plot(times/60, Q_results[:, idx_downstream], '-', linewidth=2, label=f'下游（x={L/1000:.1f}km）')
    ax2.axvline(x=t_schedule_start/60, color='k', linestyle='--', alpha=0.3, label='调度开始')
    ax2.axvline(x=t_schedule_end/60, color='k', linestyle=':', alpha=0.3, label='调度结束')

    ax2.set_xlabel('时间 (min)', fontsize=12)
    ax2.set_ylabel('流量 (m³/s)', fontsize=12)
    ax2.set_title('各断面流量响应', fontsize=13, fontweight='bold')
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)

    # 图3：不同位置的水位响应
    ax3 = axes[1, 0]
    ax3.plot(times/60, h_results[:, idx_upstream], '-', linewidth=2, label='上游（x=0）')
    ax3.plot(times/60, h_results[:, idx_mid], '-', linewidth=2, label=f'中游（x={L/2000:.1f}km）')
    ax3.plot(times/60, h_results[:, idx_downstream], '-', linewidth=2, label=f'下游（x={L/1000:.1f}km）')
    ax3.axvline(x=t_schedule_start/60, color='k', linestyle='--', alpha=0.3)
    ax3.axvline(x=t_schedule_end/60, color='k', linestyle=':', alpha=0.3)

    ax3.set_xlabel('时间 (min)', fontsize=12)
    ax3.set_ylabel('水深 (m)', fontsize=12)
    ax3.set_title('各断面水位响应', fontsize=13, fontweight='bold')
    ax3.legend(fontsize=10)
    ax3.grid(True, alpha=0.3)

    # 图4：水深时空分布
    ax4 = axes[1, 1]
    T, X = np.meshgrid(times/60, x_grid/1000)
    levels = np.linspace(h_results.min(), h_results.max(), 20)
    contour = ax4.contourf(T.T, X.T, h_results, levels=levels, cmap='Blues')
    plt.colorbar(contour, ax=ax4, label='水深 (m)')

    ax4.set_xlabel('时间 (min)', fontsize=12)
    ax4.set_ylabel('距离 (km)', fontsize=12)
    ax4.set_title('水深时空分布', fontsize=13, fontweight='bold')

    plt.tight_layout()
    plt.savefig('case_16_canal_operation.png', dpi=150, bbox_inches='tight')
    print(f"\n图形已保存：case_16_canal_operation.png")

    # ==================== 完成 ====================
    print("\n" + "="*80)
    print("计算完成！")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
