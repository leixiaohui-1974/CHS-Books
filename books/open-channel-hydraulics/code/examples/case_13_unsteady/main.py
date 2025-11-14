"""
案例13：明渠非恒定流基础 - 主程序

问题描述：
某矩形明渠，初始为恒定均匀流，上游流量突然增加，
研究洪水波传播过程。

参数：
- 渠道长度 L = 10000 m
- 渠道宽度 b = 20 m
- 渠底坡度 S₀ = 0.0002
- 糙率 n = 0.025
- 初始流量 Q₀ = 100 m³/s
- 上游增加至 Q₁ = 150 m³/s

作者：CHS-Books项目
日期：2025-10-29
"""

import sys
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')  # 非交互式后端
import matplotlib.pyplot as plt
from matplotlib import font_manager

# 添加代码库路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from models.channel import RectangularChannel
from solvers.saint_venant import SaintVenantSolver


# 配置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def print_separator(title="", width=80):
    """打印分隔线"""
    if title:
        print(f"\n{'='*width}")
        print(f"{title:^{width}}")
        print(f"{'='*width}")
    else:
        print(f"{'='*width}")


def main():
    """主函数"""
    print_separator("案例13：明渠非恒定流基础")

    # ==================== 第一步：定义问题参数 ====================
    print("\n【步骤1】问题参数")
    print("-" * 80)

    L = 10000.0   # 渠道长度 (m)
    b = 20.0      # 渠道宽度 (m)
    S0 = 0.0002   # 渠底坡度
    n = 0.025     # 糙率
    Q0 = 100.0    # 初始流量 (m³/s)
    Q1 = 150.0    # 上游增加流量 (m³/s)
    g = 9.81

    print(f"渠道几何：")
    print(f"  长度 L = {L} m")
    print(f"  宽度 b = {b} m")
    print(f"  坡度 S₀ = {S0}")

    print(f"\n水力参数：")
    print(f"  糙率 n = {n}")
    print(f"  初始流量 Q₀ = {Q0} m³/s")
    print(f"  上游流量 Q₁ = {Q1} m³/s")
    print(f"  流量增幅 = {(Q1-Q0)/Q0*100:.1f}%")

    # ==================== 第二步：计算初始恒定流 ====================
    print("\n【步骤2】初始恒定流状态")
    print("-" * 80)

    channel = RectangularChannel(b=b, S0=S0, n=n)
    h0 = channel.compute_normal_depth(Q0)
    v0 = Q0 / (b * h0)
    Fr0 = channel.froude_number(h0)
    c0 = np.sqrt(g * h0)

    print(f"\n正常水深计算：")
    print(f"  水深 h₀ = {h0:.4f} m")
    print(f"  流速 v₀ = {v0:.3f} m/s")
    print(f"  Froude数 Fr₀ = {Fr0:.3f}")
    print(f"  流态：{'缓流' if Fr0<1 else '急流'}")

    print(f"\n波速计算：")
    print(f"  重力波速 c = √(gh) = {c0:.3f} m/s")
    print(f"  正向波速 λ+ = v + c = {v0+c0:.3f} m/s")
    print(f"  负向波速 λ- = v - c = {v0-c0:.3f} m/s")
    print(f"  （负向波速>0，说明是缓流）")

    # ==================== 第三步：数值网格设置 ====================
    print("\n【步骤3】数值网格设置")
    print("-" * 80)

    dx = 100.0  # 空间步长 (m)
    nx = int(L / dx) + 1

    print(f"\n空间离散：")
    print(f"  空间步长 Δx = {dx} m")
    print(f"  节点数 nx = {nx}")
    print(f"  总长度 = {(nx-1)*dx} m")

    # 时间步长由CFL条件确定
    cfl = 0.7
    dt_max = cfl * dx / (v0 + c0)

    print(f"\nCFL稳定性条件：")
    print(f"  Courant数 Cr = (|v| + c) × Δt / Δx ≤ 1")
    print(f"  最大时间步 Δt_max = {dt_max:.2f} s")
    print(f"  采用自动时间步长（Cr = {cfl}）")

    # ==================== 第四步：创建求解器 ====================
    print("\n【步骤4】创建Saint-Venant求解器")
    print("-" * 80)

    solver = SaintVenantSolver(L=L, b=b, S0=S0, n=n, dx=dx, dt=None, g=g)

    print(f"\n求解器配置：")
    print(f"  {solver}")
    print(f"  自动时间步长：是")
    print(f"  数值格式：Lax显式格式")

    # ==================== 第五步：设置初始条件 ====================
    print("\n【步骤5】设置初始条件（均匀流）")
    print("-" * 80)

    solver.set_uniform_initial(h0=h0, Q0=Q0)

    print(f"\n初始状态：")
    print(f"  水深 h = {h0:.4f} m（全域均匀）")
    print(f"  流量 Q = {Q0:.2f} m³/s（全域均匀）")
    print(f"  流速 v = {v0:.3f} m/s")

    # ==================== 第六步：设置边界条件 ====================
    print("\n【步骤6】设置边界条件")
    print("-" * 80)

    # 计算增大流量后的水深
    h1 = channel.compute_normal_depth(Q1)
    v1 = Q1 / (b * h1)

    print(f"\n上游边界（流量边界）：")
    print(f"  t < 0:     Q = {Q0:.2f} m³/s")
    print(f"  t ≥ 0:     Q = {Q1:.2f} m³/s（阶跃变化）")
    print(f"  对应水深：  h = {h1:.4f} m")
    print(f"  对应流速：  v = {v1:.3f} m/s")

    def bc_upstream(t):
        """上游边界：流量阶跃变化"""
        if t < 0:
            return h0, Q0
        else:
            return h1, Q1

    print(f"\n下游边界（水深边界）：")
    print(f"  保持初始正常水深 h = {h0:.4f} m")

    # 下游使用外推边界条件，允许洪峰自由传播
    solver.set_boundary_conditions(bc_upstream, None)

    # ==================== 第七步：运行模拟 ====================
    print("\n【步骤7】运行非恒定流模拟")
    print("-" * 80)

    t_end = 3600.0  # 模拟1小时
    dt_output = 300.0  # 每5分钟输出一次

    print(f"\n模拟参数：")
    print(f"  总时长 = {t_end} s = {t_end/60:.0f} min")
    print(f"  输出间隔 = {dt_output} s = {dt_output/60:.0f} min")
    print(f"  输出次数 = {int(t_end/dt_output)+1}")

    print(f"\n开始计算...")
    results = solver.run(t_end=t_end, dt_output=dt_output, verbose=True)
    print(f"计算完成！")

    # ==================== 第八步：结果分析 ====================
    print("\n【步骤8】洪水波传播分析")
    print("-" * 80)

    x = results['x']
    times = results['times']
    h_results = results['h']
    Q_results = results['Q']

    # 找到洪峰到达下游的时间
    Q_downstream = Q_results[:, -1]
    Q_threshold = Q0 + 0.5 * (Q1 - Q0)

    arrival_idx = np.where(Q_downstream > Q_threshold)[0]
    if len(arrival_idx) > 0:
        t_arrival = times[arrival_idx[0]]
        wave_speed_avg = L / t_arrival
    else:
        t_arrival = np.nan
        wave_speed_avg = np.nan

    print(f"\n波传播特性：")
    print(f"  理论波速 c = {c0:.3f} m/s")
    print(f"  实际波速 ≈ {wave_speed_avg:.3f} m/s")
    if not np.isnan(t_arrival):
        print(f"  到达下游时间 = {t_arrival:.0f} s = {t_arrival/60:.1f} min")

    # 峰值分析
    print(f"\n流量峰值分析：")
    print(f"  上游输入峰值 = {Q1:.2f} m³/s")
    Q_max_down = np.max(Q_downstream)
    print(f"  下游出现峰值 = {Q_max_down:.2f} m³/s")
    if Q_max_down > Q0:
        attenuation = (Q1 - Q_max_down) / (Q1 - Q0) * 100
        print(f"  峰值衰减 = {attenuation:.1f}%")

    # 水深变化
    h_max = np.max(h_results)
    h_increase = h_max - h0

    print(f"\n水深变化：")
    print(f"  初始水深 = {h0:.4f} m")
    print(f"  最大水深 = {h_max:.4f} m")
    print(f"  水深增幅 = {h_increase:.4f} m = {h_increase*100:.1f} cm")

    # ==================== 第九步：绘制结果 ====================
    print("\n【步骤9】绘制结果图形")
    print("-" * 80)

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('明渠非恒定流模拟结果', fontsize=16, fontweight='bold')

    # 图1：不同时刻的水深分布
    ax1 = axes[0, 0]
    time_indices = [0, len(times)//4, len(times)//2, 3*len(times)//4, -1]
    for idx in time_indices:
        t_plot = times[idx]
        h_plot = h_results[idx, :]
        label = f't = {t_plot/60:.0f} min'
        ax1.plot(x/1000, h_plot, label=label, linewidth=2)

    ax1.axhline(y=h0, color='k', linestyle='--', alpha=0.3, label='初始水深')
    ax1.set_xlabel('距离 (km)', fontsize=12)
    ax1.set_ylabel('水深 (m)', fontsize=12)
    ax1.set_title('水深沿程分布', fontsize=13, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)

    # 图2：不同时刻的流量分布
    ax2 = axes[0, 1]
    for idx in time_indices:
        t_plot = times[idx]
        Q_plot = Q_results[idx, :]
        label = f't = {t_plot/60:.0f} min'
        ax2.plot(x/1000, Q_plot, label=label, linewidth=2)

    ax2.axhline(y=Q0, color='k', linestyle='--', alpha=0.3, label='初始流量')
    ax2.axhline(y=Q1, color='r', linestyle='--', alpha=0.3, label='上游流量')
    ax2.set_xlabel('距离 (km)', fontsize=12)
    ax2.set_ylabel('流量 (m³/s)', fontsize=12)
    ax2.set_title('流量沿程分布', fontsize=13, fontweight='bold')
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)

    # 图3：上下游流量过程线
    ax3 = axes[1, 0]
    ax3.plot(times/60, Q_results[:, 0], 'b-', linewidth=2, label='上游')
    ax3.plot(times/60, Q_results[:, -1], 'r-', linewidth=2, label='下游')
    ax3.axhline(y=Q0, color='k', linestyle='--', alpha=0.3)
    ax3.axhline(y=Q1, color='k', linestyle='--', alpha=0.3)
    ax3.set_xlabel('时间 (min)', fontsize=12)
    ax3.set_ylabel('流量 (m³/s)', fontsize=12)
    ax3.set_title('上下游流量过程线', fontsize=13, fontweight='bold')
    ax3.legend(fontsize=10)
    ax3.grid(True, alpha=0.3)

    # 图4：水深-时间等值线图
    ax4 = axes[1, 1]
    T, X = np.meshgrid(times/60, x/1000)
    levels = np.linspace(h0, h_max, 20)
    contour = ax4.contourf(T.T, X.T, h_results, levels=levels, cmap='viridis')
    plt.colorbar(contour, ax=ax4, label='水深 (m)')
    ax4.set_xlabel('时间 (min)', fontsize=12)
    ax4.set_ylabel('距离 (km)', fontsize=12)
    ax4.set_title('水深时空分布', fontsize=13, fontweight='bold')

    plt.tight_layout()
    plt.savefig('case_13_results.png', dpi=150, bbox_inches='tight')
    print(f"\n图形已保存：case_13_results.png")

    # ==================== 第十步：工程应用建议 ====================
    print("\n【步骤10】工程应用建议")
    print("-" * 80)

    print(f"\n基于本案例的设计要点：")

    print(f"\n1. 数值计算参数：")
    print(f"   - 空间步长：Δx = {dx} m（河道长度的1%左右）")
    print(f"   - 时间步长：满足CFL条件，Cr ≈ 0.5-0.8")
    print(f"   - 数值格式：Lax显式（简单但耗散大）")
    print(f"   - 计算时长：根据波到达时间确定")

    print(f"\n2. 洪水预报应用：")
    print(f"   - 波速：c ≈ {c0:.1f} m/s = {c0*3.6:.1f} km/h")
    print(f"   - 预见期：L/c ≈ {L/c0/60:.0f} min")
    print(f"   - 峰值衰减：考虑河道蓄水作用")
    print(f"   - 误差来源：糙率、断面、边界条件")

    print(f"\n3. 实际河道应用：")
    print(f"   - 断面：采用实测复杂断面")
    print(f"   - 糙率：分段率定")
    print(f"   - 边界：实测流量或水位")
    print(f"   - 校验：历史洪水验证")

    print(f"\n4. 模型改进方向：")
    print(f"   - 高精度格式：MacCormack、TVD")
    print(f"   - 复杂断面：非均匀断面处理")
    print(f"   - 支流汇流：多河道耦合")
    print(f"   - 闸坝调度：动边界处理")

    # ==================== 完成 ====================
    print("\n" + "="*80)
    print("计算完成！")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
