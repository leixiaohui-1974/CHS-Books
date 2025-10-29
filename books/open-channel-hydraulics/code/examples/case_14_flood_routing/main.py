"""
案例14：洪水演进计算 - 主程序

问题描述：
某河道长50km，上游发生洪水（峰值2000m³/s），
计算洪水在河道中的演进过程，预测下游洪水情况。

参数：
- 河道长度 L = 50000 m
- 河道宽度 b = 80 m
- 河床坡度 S₀ = 0.0001
- 糙率 n = 0.030
- 初始流量 Q₀ = 500 m³/s
- 设计洪峰 Q_peak = 2000 m³/s

作者：CHS-Books项目
日期：2025-10-29
"""

import sys
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# 添加代码库路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from models.channel import RectangularChannel
from solvers.saint_venant import SaintVenantSolver

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


def create_flood_hydrograph(t, Q_base, Q_peak, t_rise, t_fall):
    """创建洪水过程线（三角形）

    Args:
        t: 时间数组 (s)
        Q_base: 基流 (m³/s)
        Q_peak: 洪峰流量 (m³/s)
        t_rise: 涨峰历时 (s)
        t_fall: 退水历时 (s)

    Returns:
        Q: 流量数组 (m³/s)
    """
    Q = np.zeros_like(t)

    for i, ti in enumerate(t):
        if ti <= 0:
            Q[i] = Q_base
        elif ti <= t_rise:
            # 涨水段（线性）
            Q[i] = Q_base + (Q_peak - Q_base) * (ti / t_rise)
        elif ti <= t_rise + t_fall:
            # 退水段（线性）
            t_elapsed = ti - t_rise
            Q[i] = Q_peak - (Q_peak - Q_base) * (t_elapsed / t_fall)
        else:
            Q[i] = Q_base

    return Q


def analyze_flood_wave(times, x_locations, Q_results, Q_base, Q_peak):
    """分析洪水波特性

    Args:
        times: 时间数组
        x_locations: 空间位置数组
        Q_results: 流量结果 [nt, nx]
        Q_base: 基流
        Q_peak: 入流洪峰

    Returns:
        analysis: 分析结果字典
    """
    analysis = {}

    # 对每个断面分析
    for idx, x in enumerate(x_locations):
        Q_at_section = Q_results[:, idx]

        # 洪峰流量和时间
        peak_idx = np.argmax(Q_at_section)
        Q_peak_section = Q_at_section[peak_idx]
        t_peak_section = times[peak_idx]

        # 衰减
        attenuation = (Q_peak - Q_peak_section) / (Q_peak - Q_base) * 100

        analysis[f'x{idx}'] = {
            'x': x,
            'Q_peak': Q_peak_section,
            't_peak': t_peak_section,
            'attenuation': attenuation
        }

    return analysis


def compute_channel_storage(times, Q_in, Q_out, dt):
    """计算河道蓄量

    Args:
        times: 时间数组
        Q_in: 入流过程线
        Q_out: 出流过程线
        dt: 时间步长

    Returns:
        storage: 蓄量过程线 (m³)
    """
    storage = np.zeros_like(times)

    for i in range(1, len(times)):
        # 时段平均流量
        Q_in_avg = (Q_in[i] + Q_in[i-1]) / 2
        Q_out_avg = (Q_out[i] + Q_out[i-1]) / 2

        # 蓄量增量
        dV = (Q_in_avg - Q_out_avg) * dt

        # 累计蓄量
        storage[i] = storage[i-1] + dV

    return storage


def main():
    """主函数"""
    print_separator("案例14：洪水演进计算")

    # ==================== 第一步：定义问题参数 ====================
    print("\n【步骤1】河道和洪水参数")
    print("-" * 80)

    L = 50000.0   # 河道长度 (m)
    b = 80.0      # 河道宽度 (m)
    S0 = 0.0001   # 河床坡度
    n = 0.030     # 糙率
    Q_base = 500.0   # 基流 (m³/s)
    Q_peak = 2000.0  # 洪峰流量 (m³/s)
    g = 9.81

    print(f"河道参数：")
    print(f"  长度 L = {L/1000:.0f} km")
    print(f"  宽度 b = {b} m")
    print(f"  坡度 S₀ = {S0}")
    print(f"  糙率 n = {n}（天然河道）")

    print(f"\n设计洪水：")
    print(f"  基流 Q_base = {Q_base} m³/s")
    print(f"  洪峰流量 Q_peak = {Q_peak} m³/s")
    print(f"  洪峰倍比 = {Q_peak/Q_base:.1f}")

    # ==================== 第二步：构造洪水过程线 ====================
    print("\n【步骤2】构造上游洪水过程线")
    print("-" * 80)

    t_rise = 6 * 3600    # 涨峰历时 6小时
    t_fall = 12 * 3600   # 退水历时 12小时
    t_duration = t_rise + t_fall + 6 * 3600  # 总历时（加6小时余量）

    print(f"\n洪水过程特征：")
    print(f"  涨峰历时 = {t_rise/3600:.0f} 小时")
    print(f"  退水历时 = {t_fall/3600:.0f} 小时")
    print(f"  总历时 = {t_duration/3600:.0f} 小时")
    print(f"  过程线类型：三角形")

    # 计算洪量
    W = 0.5 * (t_rise + t_fall) * (Q_peak - Q_base)
    print(f"  洪水总量 W = {W/1e6:.2f} 百万m³")

    # ==================== 第三步：计算初始状态 ====================
    print("\n【步骤3】计算河道初始状态（基流）")
    print("-" * 80)

    channel = RectangularChannel(b=b, S0=S0, n=n)
    h_base = channel.compute_normal_depth(Q_base)
    v_base = Q_base / (b * h_base)
    Fr_base = channel.froude_number(h_base)
    c_base = np.sqrt(g * h_base)

    print(f"\n基流状态：")
    print(f"  水深 h = {h_base:.3f} m")
    print(f"  流速 v = {v_base:.3f} m/s")
    print(f"  Froude数 Fr = {Fr_base:.3f}")
    print(f"  波速 c = {c_base:.3f} m/s")
    print(f"  流态：{'缓流' if Fr_base < 1 else '急流'}")

    print(f"\n洪峰传播速度估算：")
    v_peak_theory = v_base + c_base
    print(f"  理论波速 = v + c = {v_peak_theory:.3f} m/s")
    print(f"  预计到达时间 = {L/v_peak_theory/3600:.2f} 小时")

    # ==================== 第四步：数值模拟设置 ====================
    print("\n【步骤4】数值模拟设置")
    print("-" * 80)

    dx = 500.0  # 空间步长 (m)
    nx = int(L / dx) + 1

    print(f"\n网格参数：")
    print(f"  空间步长 Δx = {dx} m")
    print(f"  节点数 nx = {nx}")
    print(f"  模拟时长 = {t_duration/3600:.0f} 小时")

    # ==================== 第五步：创建求解器 ====================
    print("\n【步骤5】创建洪水演进求解器")
    print("-" * 80)

    solver = SaintVenantSolver(L=L, b=b, S0=S0, n=n, dx=dx, dt=None, g=g)
    solver.set_uniform_initial(h0=h_base, Q0=Q_base)

    print(f"求解器：{solver}")
    print(f"时间步长：自动调整（CFL条件）")

    # 创建上游洪水过程线
    t_hydrograph = np.linspace(0, t_duration, 1000)
    Q_hydrograph = create_flood_hydrograph(t_hydrograph, Q_base, Q_peak,
                                          t_rise, t_fall)

    # 插值函数用于边界条件
    def get_upstream_Q(t):
        """获取上游流量"""
        return np.interp(t, t_hydrograph, Q_hydrograph)

    def bc_upstream(t):
        """上游边界条件：给定洪水过程线"""
        Q = get_upstream_Q(t)
        h = channel.compute_normal_depth(Q) if Q > 0 else h_base
        return h, Q

    # 下游边界使用外推（None），让洪峰自由通过
    solver.set_boundary_conditions(bc_upstream, downstream=None)

    print(f"\n边界条件：")
    print(f"  上游：给定流量过程线")
    print(f"  下游：自由出流")

    # ==================== 第六步：运行模拟 ====================
    print("\n【步骤6】运行洪水演进模拟")
    print("-" * 80)

    dt_output = 900.0  # 每15分钟输出一次（捕捉洪峰）

    print(f"\n开始计算...")
    print(f"输出间隔：{dt_output/60:.0f} 分钟")

    results = solver.run(t_end=t_duration, dt_output=dt_output, verbose=True)

    print(f"\n计算完成！")
    print(f"总时间步数：{solver.time_step}")

    # ==================== 第七步：洪水波分析 ====================
    print("\n【步骤7】洪水波传播分析")
    print("-" * 80)

    x = results['x']
    times = results['times']
    Q_results = results['Q']
    h_results = results['h']

    # 选择关键断面
    sections = [
        (0, "上游（0km）"),
        (nx//4, f"上游1/4（{L/4000:.0f}km）"),
        (nx//2, f"中游（{L/2000:.0f}km）"),
        (3*nx//4, f"下游3/4（{3*L/4000:.0f}km）"),
        (nx-1, f"下游（{L/1000:.0f}km）")
    ]

    print(f"\n关键断面洪水特性：")
    print("-" * 120)
    print(f"{'断面':^20} | {'距离(km)':^12} | {'洪峰Q(m³/s)':^15} | "
          f"{'峰现时间(h)':^15} | {'衰减率(%)':^12} | {'滞后时间(h)':^15}")
    print("-" * 120)

    t_peak_upstream = None
    for idx, name in sections:
        Q_section = Q_results[:, idx]
        peak_idx = np.argmax(Q_section)
        Q_peak_section = Q_section[peak_idx]
        t_peak_section = times[peak_idx] / 3600  # 转换为小时

        attenuation = (Q_peak - Q_peak_section) / (Q_peak - Q_base) * 100

        if t_peak_upstream is None:
            t_peak_upstream = t_peak_section
            lag = 0
        else:
            lag = t_peak_section - t_peak_upstream

        print(f"{name:^20} | {x[idx]/1000:^12.1f} | {Q_peak_section:^15.1f} | "
              f"{t_peak_section:^15.2f} | {attenuation:^12.1f} | {lag:^15.2f}")

    print("-" * 120)

    # 计算平均波速
    t_peak_down = times[np.argmax(Q_results[:, -1])] / 3600
    wave_speed_avg = L / (t_peak_down * 3600)

    print(f"\n洪峰传播速度：")
    print(f"  理论波速：{v_peak_theory:.3f} m/s = {v_peak_theory*3.6:.2f} km/h")
    print(f"  实际波速：{wave_speed_avg:.3f} m/s = {wave_speed_avg*3.6:.2f} km/h")
    print(f"  传播时间：{t_peak_down:.2f} 小时")
    print(f"  预见期：{t_peak_down:.2f} 小时（下游防洪准备时间）")

    # ==================== 第八步：河道调蓄分析 ====================
    print("\n【步骤8】河道调蓄作用分析")
    print("-" * 80)

    # 计算河道蓄量
    Q_in = Q_results[:, 0]
    Q_out = Q_results[:, -1]
    dt_avg = np.mean(np.diff(times))
    storage = compute_channel_storage(times, Q_in, Q_out, dt_avg)

    max_storage_idx = np.argmax(storage)
    max_storage = storage[max_storage_idx]
    t_max_storage = times[max_storage_idx] / 3600

    print(f"\n河道蓄量变化：")
    print(f"  最大蓄量：{max_storage/1e6:.2f} 百万m³")
    print(f"  最大蓄量时刻：{t_max_storage:.2f} 小时")
    print(f"  占洪水总量比例：{max_storage/W*100:.1f}%")

    # 削峰效果
    Q_peak_in = np.max(Q_in)
    Q_peak_out = np.max(Q_out)
    peak_reduction = Q_peak_in - Q_peak_out
    reduction_pct = peak_reduction / (Q_peak_in - Q_base) * 100

    print(f"\n削峰作用：")
    print(f"  入流洪峰：{Q_peak_in:.1f} m³/s")
    print(f"  出流洪峰：{Q_peak_out:.1f} m³/s")
    print(f"  削峰量：{peak_reduction:.1f} m³/s")
    print(f"  削峰率：{reduction_pct:.1f}%")

    # ==================== 第九步：绘制结果 ====================
    print("\n【步骤9】绘制分析图形")
    print("-" * 80)

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('洪水演进计算结果', fontsize=16, fontweight='bold')

    # 图1：关键断面流量过程线
    ax1 = axes[0, 0]
    for idx, name in sections[::2]:  # 只画部分断面避免太密
        Q_section = Q_results[:, idx]
        ax1.plot(times/3600, Q_section, linewidth=2, label=name)

    ax1.axhline(y=Q_base, color='k', linestyle='--', alpha=0.3, label='基流')
    ax1.set_xlabel('时间 (小时)', fontsize=12)
    ax1.set_ylabel('流量 (m³/s)', fontsize=12)
    ax1.set_title('各断面流量过程线', fontsize=13, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)

    # 图2：洪峰沿程变化
    ax2 = axes[0, 1]
    Q_peaks = []
    for i in range(nx):
        Q_peaks.append(np.max(Q_results[:, i]))

    ax2.plot(x/1000, Q_peaks, 'b-', linewidth=2, label='洪峰流量')
    ax2.axhline(y=Q_peak, color='r', linestyle='--', label='入流洪峰')
    ax2.set_xlabel('距离 (km)', fontsize=12)
    ax2.set_ylabel('洪峰流量 (m³/s)', fontsize=12)
    ax2.set_title('洪峰沿程衰减', fontsize=13, fontweight='bold')
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)

    # 图3：河道蓄量过程
    ax3 = axes[1, 0]
    ax3.plot(times/3600, storage/1e6, 'g-', linewidth=2, label='河道蓄量')
    ax3.axvline(x=t_max_storage, color='r', linestyle='--', alpha=0.5,
                label=f'最大蓄量时刻')
    ax3.set_xlabel('时间 (小时)', fontsize=12)
    ax3.set_ylabel('蓄量 (百万m³)', fontsize=12)
    ax3.set_title('河道蓄量过程', fontsize=13, fontweight='bold')
    ax3.legend(fontsize=10)
    ax3.grid(True, alpha=0.3)

    # 图4：流量时空分布等值线
    ax4 = axes[1, 1]
    T, X = np.meshgrid(times/3600, x/1000)
    levels = np.linspace(Q_base, Q_peak, 20)
    contour = ax4.contourf(T.T, X.T, Q_results, levels=levels, cmap='YlOrRd')
    plt.colorbar(contour, ax=ax4, label='流量 (m³/s)')
    ax4.set_xlabel('时间 (小时)', fontsize=12)
    ax4.set_ylabel('距离 (km)', fontsize=12)
    ax4.set_title('洪水传播时空分布', fontsize=13, fontweight='bold')

    plt.tight_layout()
    plt.savefig('case_14_flood_routing.png', dpi=150, bbox_inches='tight')
    print(f"\n图形已保存：case_14_flood_routing.png")

    # ==================== 第十步：工程应用建议 ====================
    print("\n【步骤10】洪水预报和防洪建议")
    print("-" * 80)

    print(f"\n基于本次洪水演进分析：")

    print(f"\n1. 预报信息：")
    print(f"   - 上游洪峰：{Q_peak:.0f} m³/s")
    print(f"   - 下游预报洪峰：{Q_peak_out:.0f} m³/s")
    print(f"   - 预见期：{t_peak_down:.1f} 小时")
    print(f"   - 削峰率：{reduction_pct:.1f}%")

    print(f"\n2. 防洪措施建议：")
    if Q_peak_out > 1500:
        print(f"   ⚠ 预警级别：严重")
        print(f"   - 立即启动防洪应急预案")
        print(f"   - 组织低洼地区人员转移")
        print(f"   - 加强堤防巡查")
        print(f"   - 准备抢险物资")
    elif Q_peak_out > 1000:
        print(f"   ⚠ 预警级别：较重")
        print(f"   - 加强值班监测")
        print(f"   - 通知沿岸居民注意")
        print(f"   - 检查防洪设施")
    else:
        print(f"   ✓ 预警级别：一般")
        print(f"   - 正常监测")

    print(f"\n3. 河道调蓄作用：")
    print(f"   - 最大蓄量：{max_storage/1e6:.2f} 百万m³")
    print(f"   - 河道有明显的削峰调蓄作用")
    print(f"   - 保护河道行洪能力重要")

    print(f"\n4. 模型应用：")
    print(f"   - 可用于实时洪水预报")
    print(f"   - 需要实测资料校验模型")
    print(f"   - 建议多方案比较分析")
    print(f"   - 考虑不同量级洪水")

    # ==================== 完成 ====================
    print("\n" + "="*80)
    print("计算完成！")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
