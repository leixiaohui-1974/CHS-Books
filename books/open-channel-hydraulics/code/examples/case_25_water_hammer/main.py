"""
案例25：水锤基础计算与可视化

问题描述：
某输水管道系统，已知：
- 管道长度 L = 1200 m
- 管道直径 D = 0.6 m
- 管壁厚度 e = 0.012 m
- 初始流速 v0 = 1.5 m/s
- 初始水头 H0 = 60 m
- 水的体积模量 K = 2.1×10⁹ Pa
- 管道弹性模量 E = 200×10⁹ Pa（钢管）
- 水的密度 ρ = 1000 kg/m³

求解：
1. 压力波速
2. 临界时间
3. Joukowsky水锤压力
4. 不同关闭时间的影响
5. 可视化压力波传播过程

作者：CHS-Books项目
日期：2025-10-30
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
import warnings
warnings.filterwarnings('ignore', category=UserWarning)


# ==================== 水锤计算函数 ====================

def wave_speed_elastic_pipe(K, rho, E, D, e):
    """弹性管道中的压力波速 [m/s]
    a = √(K/ρ) / √(1 + K*D/(E*e))
    """
    a_rigid = np.sqrt(K / rho)
    correction = np.sqrt(1 + (K * D) / (E * e))
    a = a_rigid / correction
    return a


def joukowsky_head_rise(a, delta_v, g=9.81):
    """Joukowsky公式：水锤水头升高 [m]
    ΔH = (a/g) * Δv
    """
    delta_H = (a / g) * delta_v
    return delta_H


def critical_time(L, a):
    """临界时间（相时间）[s]
    T_c = 2L/a
    """
    T_c = 2 * L / a
    return T_c


def max_head_rapid_closure(H0, a, v0, g=9.81):
    """快速关闭最大水头 [m]
    H_max = H₀ + (a/g)*v₀
    """
    H_max = H0 + (a / g) * v0
    return H_max


def max_head_slow_closure(H0, a, v0, T_c, t_c, g=9.81):
    """缓慢关闭最大水头 [m]
    H_max = H₀ + (a/g)*v₀*(T_c/t_c)
    """
    H_max = H0 + (a / g) * v0 * (T_c / t_c)
    return H_max


def pressure_wave_at_valve(t, T_c, H0, delta_H_max, n_cycles=3):
    """阀门处压力波动（简化正弦波模型）

    Args:
        t: 时间数组
        T_c: 临界时间
        H0: 初始水头
        delta_H_max: 最大水头升高
        n_cycles: 波动衰减周期数

    Returns:
        H: 水头时程
    """
    H = np.zeros_like(t)
    for i, ti in enumerate(t):
        # 简化模型：方波 + 指数衰减
        if ti < T_c / 2:
            # 第一个升压阶段
            H[i] = H0 + delta_H_max
        elif ti < T_c:
            # 第一个降压阶段
            H[i] = H0
        else:
            # 后续波动（衰减正弦波）
            cycle = int(ti / T_c)
            if cycle < n_cycles * 2:
                phase = (ti / T_c) * 2 * np.pi
                decay = np.exp(-0.1 * ti / T_c)  # 衰减系数
                H[i] = H0 + delta_H_max * np.sin(phase) * decay
            else:
                H[i] = H0
    return H


def pressure_wave_along_pipe(x_positions, t, L, a, H0, delta_H_max):
    """计算管道各点的压力波传播

    Args:
        x_positions: 管道各点位置 [m]
        t: 时间 [s]
        L: 管道长度 [m]
        a: 波速 [m/s]
        H0: 初始水头 [m]
        delta_H_max: 最大水头升高 [m]

    Returns:
        H: 各点水头
    """
    H = np.zeros(len(x_positions))

    # 波传播到各点的时间
    for i, x in enumerate(x_positions):
        t_arrival = x / a  # 波传到x处的时间

        if t < t_arrival:
            # 波尚未到达
            H[i] = H0
        elif t < t_arrival + (2*L - 2*x) / a:
            # 高压波阶段
            H[i] = H0 + delta_H_max
        else:
            # 反射后的低压波
            H[i] = H0

    return H


# ==================== 可视化函数 ====================

def plot_pressure_wave_propagation(L, a, H0, delta_H_max, T_c,
                                   save_path='water_hammer_propagation.png'):
    """绘制压力波传播过程

    展示不同时刻管道沿程的压力分布
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 管道离散点
    x = np.linspace(0, L, 100)

    # 四个关键时刻
    times = [T_c/4, T_c/2, 3*T_c/4, T_c]
    time_labels = ['T_c/4', 'T_c/2', '3T_c/4', 'T_c']

    for idx, (t, label) in enumerate(zip(times, time_labels)):
        ax = axes.flat[idx]

        # 计算该时刻的压力分布
        H = pressure_wave_along_pipe(x, t, L, a, H0, delta_H_max)

        # 绘图
        ax.plot(x, H, 'b-', linewidth=2, label='压力水头')
        ax.axhline(y=H0, color='g', linestyle='--', linewidth=1,
                  label=f'初始水头 H0={H0}m')
        ax.axhline(y=H0+delta_H_max, color='r', linestyle='--', linewidth=1,
                  label=f'最大水头 Hmax={H0+delta_H_max:.1f}m')

        # 标注阀门和水库位置
        ax.plot(L, H[-1], 'ro', markersize=10, label='阀门')
        ax.plot(0, H[0], 'bs', markersize=10, label='水库')

        ax.set_xlabel('管道距离 (m)', fontsize=11)
        ax.set_ylabel('水头 (m)', fontsize=11)
        ax.set_title(f'时刻 t = {label} = {t:.2f}s', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='best', fontsize=9)
        ax.set_ylim([H0 - 10, H0 + delta_H_max + 10])

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"\n✓ 压力波传播图已保存: {save_path}")


def plot_pressure_time_history(T_c, H0, delta_H_max,
                               save_path='water_hammer_time_history.png'):
    """绘制阀门处压力时程曲线"""
    fig, ax = plt.subplots(figsize=(12, 6))

    # 时间数组（显示3个周期）
    t = np.linspace(0, 3*T_c, 1000)

    # 计算阀门处压力波动
    H = pressure_wave_at_valve(t, T_c, H0, delta_H_max, n_cycles=3)

    # 绘制时程曲线
    ax.plot(t, H, 'b-', linewidth=2, label='阀门处水头')
    ax.axhline(y=H0, color='g', linestyle='--', linewidth=1.5,
              label=f'初始水头 H0={H0}m')
    ax.axhline(y=H0+delta_H_max, color='r', linestyle='--', linewidth=1.5,
              label=f'最大水头 Hmax={H0+delta_H_max:.1f}m')

    # 标注临界时间
    for i in range(4):
        ax.axvline(x=i*T_c, color='gray', linestyle=':', alpha=0.5)
        ax.text(i*T_c, H0+delta_H_max+5, f'{i}Tc',
               ha='center', fontsize=9, color='gray')

    ax.set_xlabel('时间 (s)', fontsize=12)
    ax.set_ylabel('水头 (m)', fontsize=12)
    ax.set_title('阀门处压力时程曲线（水锤波动）', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right', fontsize=11)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"✓ 压力时程图已保存: {save_path}")


def plot_closure_time_comparison(L, a, H0, v0, T_c,
                                 save_path='closure_time_comparison.png'):
    """绘制不同关闭时间对最大压力的影响"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # 关闭时间范围：从0.1Tc到10Tc
    t_c_array = np.linspace(0.1*T_c, 10*T_c, 100)
    t_c_ratio = t_c_array / T_c

    # 计算最大水头
    H_max = np.zeros_like(t_c_array)
    for i, t_c in enumerate(t_c_array):
        if t_c <= T_c:
            # 快速关闭
            H_max[i] = max_head_rapid_closure(H0, a, v0)
        else:
            # 缓慢关闭
            H_max[i] = max_head_slow_closure(H0, a, v0, T_c, t_c)

    # 子图1：最大水头 vs 关闭时间
    ax1.plot(t_c_ratio, H_max, 'b-', linewidth=2)
    ax1.axvline(x=1.0, color='r', linestyle='--', linewidth=2,
               label='临界时间 tc=Tc')
    ax1.axhline(y=H0, color='g', linestyle='--', linewidth=1,
               label=f'初始水头 H0={H0}m')

    # 标注快速/缓慢关闭区域
    ax1.fill_between(t_c_ratio[t_c_ratio<=1],
                     H0, H_max[t_c_ratio<=1].max()+10,
                     alpha=0.2, color='red', label='快速关闭区')
    ax1.fill_between(t_c_ratio[t_c_ratio>1],
                     H0, H_max[t_c_ratio>1].max()+10,
                     alpha=0.2, color='blue', label='缓慢关闭区')

    ax1.set_xlabel('关闭时间比 tc/Tc', fontsize=12)
    ax1.set_ylabel('最大水头 Hmax (m)', fontsize=12)
    ax1.set_title('最大水头 vs 关闭时间', fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='upper right', fontsize=10)
    ax1.set_xlim([0, 10])

    # 子图2：水头升高 vs 关闭时间
    delta_H = H_max - H0
    ax2.plot(t_c_ratio, delta_H, 'r-', linewidth=2)
    ax2.axvline(x=1.0, color='b', linestyle='--', linewidth=2,
               label='临界时间 tc=Tc')
    ax2.axhline(y=0, color='k', linestyle='-', linewidth=0.5)

    # Joukowsky最大值
    delta_H_jouk = (a/9.81) * v0
    ax2.axhline(y=delta_H_jouk, color='orange', linestyle='--', linewidth=2,
               label=f'Joukowsky极限 ΔH={(a/9.81)*v0:.1f}m')

    ax2.set_xlabel('关闭时间比 tc/Tc', fontsize=12)
    ax2.set_ylabel('水头升高 ΔH (m)', fontsize=12)
    ax2.set_title('水头升高 vs 关闭时间', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc='upper right', fontsize=10)
    ax2.set_xlim([0, 10])

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"✓ 关闭时间对比图已保存: {save_path}")


# ==================== 主程序 ====================

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
    print_separator("案例25：水锤基础计算与可视化")

    # ==================== 第一步：定义问题参数 ====================
    print("\n【步骤1】问题参数")
    print("-" * 80)

    # 管道参数
    L = 1200        # 管道长度 (m)
    D = 0.6         # 管道直径 (m)
    e = 0.012       # 管壁厚度 (m)

    # 流体参数
    rho = 1000      # 水的密度 (kg/m³)
    K = 2.1e9       # 水的体积模量 (Pa)
    g = 9.81        # 重力加速度 (m/s²)

    # 管道材料参数
    E = 200e9       # 钢管弹性模量 (Pa)

    # 初始运行条件
    v0 = 1.5        # 初始流速 (m/s)
    H0 = 60         # 初始水头 (m)

    print(f"管道系统参数：")
    print(f"  管道长度 L = {L} m")
    print(f"  管道直径 D = {D} m")
    print(f"  管壁厚度 e = {e} m")
    print(f"  管道材料：钢管（E = {E/1e9:.0f} GPa）")
    print(f"\n流体参数：")
    print(f"  密度 ρ = {rho} kg/m³")
    print(f"  体积模量 K = {K/1e9:.1f} GPa")
    print(f"\n初始运行条件：")
    print(f"  流速 v0 = {v0} m/s")
    print(f"  水头 H0 = {H0} m")

    # ==================== 第二步：计算压力波速 ====================
    print("\n【步骤2】压力波速计算")
    print("-" * 80)

    a = wave_speed_elastic_pipe(K, rho, E, D, e)

    # 刚性管波速（对比）
    a_rigid = np.sqrt(K / rho)

    print(f"刚性管波速：a_rigid = √(K/ρ) = {a_rigid:.1f} m/s")
    print(f"弹性管波速：a = {a:.1f} m/s")
    print(f"波速降低：{(1 - a/a_rigid)*100:.1f}%（由于管壁弹性）")

    # ==================== 第三步：临界时间 ====================
    print("\n【步骤3】临界时间（相时间）")
    print("-" * 80)

    T_c = critical_time(L, a)

    print(f"临界时间：Tc = 2L/a = 2×{L}/{a:.1f} = {T_c:.3f} s")
    print(f"\n关闭时间判别：")
    print(f"  tc ≤ Tc = {T_c:.3f}s  →  快速关闭（水锤压力 = Joukowsky极限）")
    print(f"  tc > Tc = {T_c:.3f}s  →  缓慢关闭（水锤压力 < Joukowsky极限）")

    # ==================== 第四步：Joukowsky水锤压力 ====================
    print("\n【步骤4】Joukowsky水锤压力（快速关闭）")
    print("-" * 80)

    delta_H_jouk = joukowsky_head_rise(a, v0, g)
    H_max_rapid = max_head_rapid_closure(H0, a, v0, g)

    print(f"Joukowsky公式：ΔH = (a/g) × Δv")
    print(f"  压力波速 a = {a:.1f} m/s")
    print(f"  流速变化 Δv = v0 = {v0} m/s（从v0减至0）")
    print(f"\n水锤水头升高：ΔH = ({a:.1f}/{g}) × {v0} = {delta_H_jouk:.2f} m")
    print(f"最大水头：Hmax = H0 + ΔH = {H0} + {delta_H_jouk:.2f} = {H_max_rapid:.2f} m")
    print(f"水头升高比例：{delta_H_jouk/H0*100:.1f}%")

    # ==================== 第五步：不同关闭时间的影响 ====================
    print("\n【步骤5】不同关闭时间的影响")
    print("-" * 80)

    # 测试几个典型关闭时间
    closure_times = {
        '瞬时关闭': 0.5 * T_c,
        '快速关闭': 1.0 * T_c,
        '正常关闭': 2.0 * T_c,
        '缓慢关闭': 5.0 * T_c
    }

    print(f"{'关闭方式':<12} {'关闭时间tc(s)':<15} {'tc/Tc':<10} {'最大水头(m)':<15} {'水头升高(m)'}")
    print("-" * 80)

    for name, t_c in closure_times.items():
        if t_c <= T_c:
            H_max = max_head_rapid_closure(H0, a, v0, g)
        else:
            H_max = max_head_slow_closure(H0, a, v0, T_c, t_c, g)

        delta_H = H_max - H0
        ratio = t_c / T_c

        print(f"{name:<12} {t_c:<15.3f} {ratio:<10.2f} {H_max:<15.2f} {delta_H:.2f}")

    # ==================== 第六步：生成可视化 ====================
    print("\n【步骤6】生成可视化图形")
    print("-" * 80)

    print("正在生成可视化图形...")

    # 图1：压力波传播过程
    plot_pressure_wave_propagation(L, a, H0, delta_H_jouk, T_c,
                                   'water_hammer_propagation.png')

    # 图2：阀门处压力时程
    plot_pressure_time_history(T_c, H0, delta_H_jouk,
                              'water_hammer_time_history.png')

    # 图3：关闭时间对比
    plot_closure_time_comparison(L, a, H0, v0, T_c,
                                'closure_time_comparison.png')

    # ==================== 第七步：工程建议 ====================
    print("\n【步骤7】工程设计建议")
    print("-" * 80)

    # 计算安全关闭时间（将水锤压力限制在初始水头的20%以内）
    delta_H_limit = 0.2 * H0
    t_c_safe = T_c * (delta_H_jouk / delta_H_limit)

    print(f"1. 水锤防护措施：")
    print(f"   - 临界时间 Tc = {T_c:.3f} s")
    print(f"   - Joukowsky最大升压 ΔH = {delta_H_jouk:.2f} m")
    print(f"   - 若限制升压不超过初始水头的20%（ΔH ≤ {delta_H_limit:.1f}m）")
    print(f"   - 建议关闭时间 tc ≥ {t_c_safe:.2f} s")

    print(f"\n2. 防护设备选择：")
    if delta_H_jouk > 0.3 * H0:
        print(f"   ⚠ 水锤升压显著（>{0.3*H0:.1f}m），建议采用：")
        print(f"     - 调压井（适用于长距离输水管道）")
        print(f"     - 空气阀（释放负压，防止管道破坏）")
        print(f"     - 单向调压塔（适用于泵站系统）")
    else:
        print(f"   ✓ 水锤升压适中，可采用：")
        print(f"     - 缓慢关闭阀门（tc > {T_c:.2f}s）")
        print(f"     - 空气阀（作为安全措施）")

    print(f"\n3. 管道设计：")
    delta_P_jouk = rho * a * v0 / 1e6  # MPa
    print(f"   - Joukowsky压力升高 ΔP = {delta_P_jouk:.2f} MPa")
    print(f"   - 建议管道设计压力 ≥ {H0*rho*g/1e6 + delta_P_jouk:.2f} MPa")
    print(f"   - 安全系数建议 ≥ 1.5")

    # ==================== 完成 ====================
    print("\n" + "="*80)
    print("✓ 计算完成！所有可视化图形已保存。")
    print("="*80 + "\n")

    return {
        'wave_speed': a,
        'critical_time': T_c,
        'joukowsky_head_rise': delta_H_jouk,
        'max_head_rapid': H_max_rapid
    }


if __name__ == "__main__":
    results = main()
