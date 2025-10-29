"""
案例17：潮汐河口非恒定流 - 主程序

问题描述：
某河口地区受潮汐影响，模拟潮汐传播过程
和河流-海洋相互作用。

参数：
- 河道长度 L = 20000 m
- 河道宽度 b = 200 m
- 河道坡度 S₀ = 0.00005
- 糙率系数 n = 0.03
- 上游径流 Qr = 500 m³/s
- 潮汐振幅 A = 2.0 m
- 潮汐周期 T = 12.42 小时

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


def tidal_elevation(t, h0, A, T, phi=0, ramp_time=None):
    """
    计算潮汐水位（含缓启动功能）

    Args:
        t: 时间 (s)
        h0: 平均潮位 (m)
        A: 潮汐振幅 (m)
        T: 潮汐周期 (s)
        phi: 初相位 (rad)
        ramp_time: 缓启动时间 (s)，None表示不使用缓启动

    Returns:
        h: 潮位 (m)
    """
    omega = 2 * np.pi / T

    # 基础潮汐高度
    h_tide = h0 + A * np.sin(omega * t + phi)

    # 缓启动：逐渐增加潮汐振幅
    if ramp_time is not None and t < ramp_time:
        ramp_factor = 0.5 * (1 - np.cos(np.pi * t / ramp_time))  # 平滑从0到1
        h_tide = h0 + (h_tide - h0) * ramp_factor

    return h_tide


def analyze_tidal_propagation(results, x_grid, times, T):
    """
    分析潮汐传播特性

    Args:
        results: 模拟结果
        x_grid: 空间网格
        times: 时间数组
        T: 潮汐周期 (s)

    Returns:
        analysis: 分析结果字典
    """
    h_results = results['h']

    # 检查时间数组长度
    if len(times) < 2:
        print(f"  警告：时间数组过短（长度={len(times)}），使用全部数据")
        idx_start = 0
    else:
        # 选择最后一个完整周期进行分析
        dt = times[1] - times[0]
        idx_start = len(times) - int(T / dt) - 1
        idx_start = max(0, idx_start)

    h_cycle = h_results[idx_start:, :]
    t_cycle = times[idx_start:] - times[idx_start]

    # 提取每个位置的潮汐特征
    analysis = {}

    for i, x in enumerate(x_grid):
        h_series = h_cycle[:, i]

        # 潮差（高潮位-低潮位）
        h_max = np.max(h_series)
        h_min = np.min(h_series)
        tidal_range = h_max - h_min

        # 平均潮位
        h_mean = np.mean(h_series)

        # 高潮时刻
        idx_max = np.argmax(h_series)
        t_high_tide = t_cycle[idx_max]

        analysis[f'x{i}'] = {
            'x': x,
            'h_max': h_max,
            'h_min': h_min,
            'h_mean': h_mean,
            'tidal_range': tidal_range,
            't_high_tide': t_high_tide
        }

    return analysis


def main():
    """主函数"""
    print_separator("案例17：潮汐河口非恒定流")

    # ==================== 第一步：定义河口参数 ====================
    print("\n【步骤1】河口系统参数")
    print("-" * 80)

    L = 20000.0   # 河道长度 (m)
    b = 200.0     # 河道宽度 (m)
    S0 = 0.00005  # 河道坡度（极缓坡）
    n = 0.03      # 糙率系数
    Qr = 500.0    # 上游径流 (m³/s)
    g = 9.81

    print(f"河口几何：")
    print(f"  长度 L = {L/1000:.0f} km")
    print(f"  宽度 b = {b} m")
    print(f"  坡度 S₀ = {S0}（极缓坡）")
    print(f"  糙率 n = {n}（淤泥河床）")

    print(f"\n径流条件：")
    print(f"  上游径流 Qr = {Qr} m³/s")

    # ==================== 第二步：定义潮汐参数 ====================
    print("\n【步骤2】潮汐条件")
    print("-" * 80)

    # 潮汐参数
    T_tide = 12.42 * 3600  # 潮汐周期（半日潮） (s)
    A_tide = 2.0           # 潮汐振幅 (m)
    h0_tide = 5.0          # 平均潮位 (m)

    print(f"\n潮汐参数（半日潮）：")
    print(f"  周期 T = {T_tide/3600:.2f} 小时")
    print(f"  振幅 A = {A_tide} m")
    print(f"  平均潮位 h₀ = {h0_tide} m")
    print(f"  高潮位 = {h0_tide + A_tide} m")
    print(f"  低潮位 = {h0_tide - A_tide} m")
    print(f"  潮差 = {2*A_tide} m")

    # ==================== 第三步：计算初始状态 ====================
    print("\n【步骤3】计算初始稳态")
    print("-" * 80)

    # 创建渠道对象
    channel = RectangularChannel(b=b, S0=S0, n=n)

    # 初始水深（基于平均潮位估算）
    h_init = h0_tide
    v_init = Qr / (b * h_init)
    Fr_init = v_init / np.sqrt(g * h_init)
    c_init = np.sqrt(g * h_init)

    print(f"\n初始水力参数（基于平均潮位）：")
    print(f"  水深 h = {h_init:.3f} m")
    print(f"  流速 v = {v_init:.3f} m/s")
    print(f"  Froude数 Fr = {Fr_init:.3f}")
    print(f"  波速 c = {c_init:.3f} m/s")

    # 潮波传播时间
    t_propagation = L / c_init
    print(f"\n潮波传播时间估算：")
    print(f"  理论传播时间 = L/c = {t_propagation:.0f} s = {t_propagation/3600:.2f} 小时")

    # 径流-潮汐比
    R_ratio = Qr / (A_tide * b * c_init)
    print(f"\n径流-潮汐比：")
    print(f"  R = Qr/(A·b·c) = {R_ratio:.3f}")
    if R_ratio < 0.1:
        regime = "潮汐主导"
    elif R_ratio > 1.0:
        regime = "径流主导"
    else:
        regime = "径流与潮汐相当"
    print(f"  流态：{regime}")

    # ==================== 第四步：数值模拟设置 ====================
    print("\n【步骤4】数值模拟设置")
    print("-" * 80)

    dx = 1000.0  # 空间步长 (m)
    nx = int(L / dx) + 1
    n_cycles = 1.5  # 模拟1.5个潮周期
    t_total = n_cycles * T_tide

    print(f"\n网格参数：")
    print(f"  空间步长 Δx = {dx} m")
    print(f"  节点数 nx = {nx}")
    print(f"  模拟时长 = {n_cycles:.1f} 个潮周期 = {t_total/3600:.1f} 小时")
    print(f"  时间步长：自动（CFL=0.3，更保守的稳定性条件）")

    # ==================== 第五步：创建求解器 ====================
    print("\n【步骤5】创建Saint-Venant求解器")
    print("-" * 80)

    solver = SaintVenantSolver(L=L, b=b, S0=S0, n=n, dx=dx, dt=None, g=g)

    # 初始条件：均匀流
    h_init_array = np.full(nx, h_init)
    Q_init_array = np.full(nx, Qr)
    solver.set_initial_conditions(h_init_array, Q_init_array)

    print(f"求解器：{solver}")
    print(f"\n初始条件：")
    print(f"  水深 h(x,0) = {h_init} m")
    print(f"  流量 Q(x,0) = {Qr} m³/s")

    # ==================== 第六步：设置边界条件 ====================
    print("\n【步骤6】边界条件")
    print("-" * 80)

    # 定义缓启动时间（1/4潮周期，约3小时）
    ramp_time = T_tide / 4.0

    # 上游边界：恒定径流
    def bc_upstream(t):
        """上游径流边界"""
        Q = Qr
        # 简化：假设上游水深为正常水深
        h = channel.compute_normal_depth(Q) if Q > 0.1 else h_init
        return h, Q

    # 下游边界：周期性潮汐
    # 注意：给定水位边界，流量需要求解器外推或指定
    # 这里简化为使用外推边界，潮汐通过初始条件影响
    # 完整实现需要特殊的潮汐边界处理

    # 改进方案：使用缓启动和更合理的流量估算
    def bc_downstream(t):
        """下游边界（改进版：含缓启动）"""
        # 计算潮汐水位（含缓启动）
        h_tide = tidal_elevation(t, h0_tide, A_tide, T_tide, phi=0, ramp_time=ramp_time)

        # 改进：基于潮汐变化率估算流量
        # dh/dt = A*omega*cos(omega*t)
        omega = 2 * np.pi / T_tide
        dh_dt = A_tide * omega * np.cos(omega * t)

        # 缓启动修正
        if t < ramp_time:
            ramp_factor = 0.5 * (1 - np.cos(np.pi * t / ramp_time))
            dh_dt *= ramp_factor

        # 潮汐流量估算：Q_tide = b * c * dh（基于特征线法）
        c_tide = np.sqrt(g * h_tide)
        Q_tide = b * c_tide * dh_dt * 10  # 乘以经验系数

        # 总流量 = 径流 + 潮汐流量
        Q_down = Qr + Q_tide
        Q_down = max(Q_down, 0.1)  # 保证非负

        return h_tide, Q_down

    solver.set_boundary_conditions(upstream=bc_upstream, downstream=bc_downstream)

    print(f"边界条件：")
    print(f"  上游：恒定径流 Q = {Qr} m³/s")
    print(f"  下游：周期性潮汐 h(t) = {h0_tide} + {A_tide}·sin(2πt/T)")
    print(f"  缓启动时间：{ramp_time/3600:.2f} 小时（避免初始激波）")

    # ==================== 第七步：运行模拟 ====================
    print("\n【步骤7】运行模拟")
    print("-" * 80)

    dt_output = 3600.0  # 每60分钟输出一次

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

    # ==================== 第八步：潮汐传播分析 ====================
    print("\n【步骤8】潮汐传播分析")
    print("-" * 80)

    times = results['times']
    h_results = results['h']
    Q_results = results['Q']
    x_grid = results['x']

    # 分析潮汐传播
    analysis = analyze_tidal_propagation(results, x_grid, times, T_tide)

    # 选择关键断面
    sections = [0, nx//4, nx//2, 3*nx//4, nx-1]
    section_names = ['下游（河口）', '下游1/4', '中游', '上游3/4', '上游']

    print(f"\n关键断面潮汐特征：")
    print("-" * 110)
    print(f"{'位置':^12} | {'距河口(km)':^12} | {'潮差(m)':^10} | "
          f"{'高潮位(m)':^12} | {'低潮位(m)':^12} | {'相位滞后(h)':^14}")
    print("-" * 110)

    # 下游（河口）作为参考
    t_ref = analysis['x' + str(sections[0])]['t_high_tide']

    for idx, name in zip(sections, section_names):
        data = analysis[f'x{idx}']
        x_km = data['x'] / 1000
        phase_lag = (data['t_high_tide'] - t_ref) / 3600  # 转换为小时

        print(f"{name:^12} | {x_km:^12.1f} | {data['tidal_range']:^10.3f} | "
              f"{data['h_max']:^12.3f} | {data['h_min']:^12.3f} | {phase_lag:^14.2f}")

    print("-" * 110)

    # 潮差衰减率
    tidal_range_mouth = analysis['x' + str(sections[0])]['tidal_range']
    tidal_range_upstream = analysis['x' + str(sections[-1])]['tidal_range']
    attenuation = (1 - tidal_range_upstream / tidal_range_mouth) * 100

    print(f"\n潮汐衰减：")
    print(f"  河口潮差：{tidal_range_mouth:.3f} m")
    print(f"  上游潮差：{tidal_range_upstream:.3f} m")
    print(f"  衰减率：{attenuation:.1f}%")

    # ==================== 第九步：流速分析 ====================
    print("\n【步骤9】潮流分析")
    print("-" * 80)

    # 分析最后一个周期的流速
    idx_last_cycle = len(times) - int(T_tide / dt_output) - 1
    idx_last_cycle = max(0, idx_last_cycle)

    print(f"\n各断面最大流速：")
    print("-" * 100)
    print(f"{'位置':^12} | {'距河口(km)':^12} | {'涨潮最大流速(m/s)':^20} | {'落潮最大流速(m/s)':^20}")
    print("-" * 100)

    for idx, name in zip(sections, section_names):
        x_km = x_grid[idx] / 1000
        v_series = results['v'][idx_last_cycle:, idx]

        v_max_flood = np.max(v_series)  # 正向为涨潮
        v_max_ebb = np.min(v_series)    # 负向为落潮

        print(f"{name:^12} | {x_km:^12.1f} | {v_max_flood:^20.3f} | {v_max_ebb:^20.3f}")

    print("-" * 100)

    # ==================== 第十步：绘制结果 ====================
    print("\n【步骤10】绘制分析图形")
    print("-" * 80)

    # 配置中文字体
    plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False

    fig = plt.figure(figsize=(16, 10))
    gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)

    # 图1：潮位时程（多个位置）
    ax1 = fig.add_subplot(gs[0, 0])
    for idx, name in zip(sections, section_names):
        ax1.plot(times/3600, h_results[:, idx], linewidth=2, label=name)

    ax1.set_xlabel('时间 (h)', fontsize=12)
    ax1.set_ylabel('潮位 (m)', fontsize=12)
    ax1.set_title('各断面潮位变化', fontsize=13, fontweight='bold')
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3)

    # 图2：流速时程（多个位置）
    ax2 = fig.add_subplot(gs[0, 1])
    for idx, name in zip(sections, section_names):
        ax2.plot(times/3600, results['v'][:, idx], linewidth=2, label=name)

    ax2.axhline(y=0, color='k', linestyle='--', alpha=0.3)
    ax2.set_xlabel('时间 (h)', fontsize=12)
    ax2.set_ylabel('流速 (m/s)', fontsize=12)
    ax2.set_title('各断面流速变化', fontsize=13, fontweight='bold')
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3)

    # 图3：潮差沿程分布
    ax3 = fig.add_subplot(gs[1, 0])
    x_plot = [analysis[f'x{i}']['x']/1000 for i in range(0, nx, 5)]
    tidal_range_plot = [analysis[f'x{i}']['tidal_range'] for i in range(0, nx, 5)]

    ax3.plot(x_plot, tidal_range_plot, 'bo-', linewidth=2, markersize=6)
    ax3.set_xlabel('距河口距离 (km)', fontsize=12)
    ax3.set_ylabel('潮差 (m)', fontsize=12)
    ax3.set_title('潮差沿程分布', fontsize=13, fontweight='bold')
    ax3.grid(True, alpha=0.3)

    # 图4：相位滞后沿程分布
    ax4 = fig.add_subplot(gs[1, 1])
    phase_lag_plot = [(analysis[f'x{i}']['t_high_tide'] - t_ref)/3600 for i in range(0, nx, 5)]

    ax4.plot(x_plot, phase_lag_plot, 'ro-', linewidth=2, markersize=6)
    ax4.set_xlabel('距河口距离 (km)', fontsize=12)
    ax4.set_ylabel('相位滞后 (h)', fontsize=12)
    ax4.set_title('高潮时刻滞后', fontsize=13, fontweight='bold')
    ax4.grid(True, alpha=0.3)

    # 图5：水位时空分布（最后一个周期）
    ax5 = fig.add_subplot(gs[2, :])
    T_mesh, X_mesh = np.meshgrid(times/3600, x_grid/1000)
    levels = np.linspace(h_results.min(), h_results.max(), 20)
    contour = ax5.contourf(T_mesh.T, X_mesh.T, h_results, levels=levels, cmap='Blues')
    plt.colorbar(contour, ax=ax5, label='水位 (m)')

    ax5.set_xlabel('时间 (h)', fontsize=12)
    ax5.set_ylabel('距河口距离 (km)', fontsize=12)
    ax5.set_title('潮位时空分布', fontsize=13, fontweight='bold')

    plt.suptitle('潮汐河口非恒定流分析', fontsize=16, fontweight='bold', y=0.995)
    plt.savefig('case_17_tidal_river.png', dpi=150, bbox_inches='tight')
    print(f"\n图形已保存：case_17_tidal_river.png")

    # ==================== 完成 ====================
    print("\n" + "="*80)
    print("计算完成！")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
