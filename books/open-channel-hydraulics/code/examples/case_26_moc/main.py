"""
案例26：特征线法(MOC)水锤数值模拟

问题描述：
某输水管道，阀门快速关闭引起水锤，使用特征线法模拟瞬变过程。

已知条件：
- 管道长度 L = 1200 m
- 管道直径 D = 0.6 m
- 管壁厚度 e = 0.012 m
- 初始流速 v0 = 1.5 m/s
- 初始水头 H0 = 60 m
- 摩阻系数 λ = 0.020
- 阀门关闭时间 tc = 1.0 s
- 波速 a = 1200 m/s
- 模拟时长 T = 10 s

求解：
1. MOC网格离散化
2. 管道内压力和流速时空分布
3. 阀门处压力时程
4. 水库和阀门边界条件处理
5. 可视化特征线网格和计算结果

作者：CHS-Books项目
日期：2025-10-30
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
import warnings
warnings.filterwarnings('ignore', category=UserWarning)


# ==================== MOC计算函数 ====================

def space_step(L, N):
    """空间步长 [m]
    Δx = L / N
    """
    dx = L / N
    return dx


def timestep_from_segments(L, N, a):
    """根据分段数计算时间步长 [s]（Courant条件）
    Δt = L / (N × a) = Δx / a
    """
    dt = L / (N * a)
    return dt


def friction_term(lambda_f, v, D, a, dt, g=9.81):
    """摩阻项 R [m]
    R = (λ × v × |v|) / (2gD) × a × Δt
    """
    R = (lambda_f * v * abs(v)) / (2 * g * D) * a * dt
    return R


def c_plus_equation(H_A, v_A, v_P, R_A, a, g=9.81):
    """C⁺方程
    H_P = H_A - (a/g) × (v_P - v_A) - R_A
    """
    H_P = H_A - (a / g) * (v_P - v_A) - R_A
    return H_P


def c_minus_equation(H_B, v_B, v_P, R_B, a, g=9.81):
    """C⁻方程
    H_P = H_B + (a/g) × (v_P - v_B) - R_B
    """
    H_P = H_B + (a / g) * (v_P - v_B) - R_B
    return H_P


def internal_point_velocity(H_A, H_B, v_A, v_B, R_A, R_B, a, g=9.81):
    """内部节点流速（联立C+和C-）
    v_P = [H_A - H_B + (a/g)×(v_A + v_B) - R_A - R_B] / (2a/g)
    """
    numerator = H_A - H_B + (a/g)*(v_A + v_B) - R_A - R_B
    denominator = 2 * a / g
    v_P = numerator / denominator
    return v_P


def internal_point_head(H_A, H_B, v_A, v_B, R_A, R_B, a, g=9.81):
    """内部节点压力水头（联立C+和C-）
    H_P = (H_A + H_B) / 2 + (a/2g) × (v_A - v_B) - (R_A + R_B) / 2
    """
    H_P = (H_A + H_B) / 2 + (a / (2*g)) * (v_A - v_B) - (R_A + R_B) / 2
    return H_P


def valve_closure_coefficient(t, tc):
    """阀门开度系数（线性关闭）
    τ = 1 - t/tc  (0 ≤ t ≤ tc)
    τ = 0         (t > tc)
    """
    if t < tc:
        tau = 1.0 - t / tc
    else:
        tau = 0.0
    return tau


# ==================== MOC主模拟程序 ====================

def moc_simulation(L, D, a, v0, H0, lambda_f, tc, T_sim, N, g=9.81):
    """MOC特征线法水锤模拟

    Args:
        L: 管道长度 [m]
        D: 管道直径 [m]
        a: 波速 [m/s]
        v0: 初始流速 [m/s]
        H0: 初始水头 [m]
        lambda_f: 摩阻系数
        tc: 阀门关闭时间 [s]
        T_sim: 模拟时长 [s]
        N: 管道分段数
        g: 重力加速度 [m/s²]

    Returns:
        t_array: 时间数组
        x_array: 空间位置数组
        H: 压力水头矩阵 [时间×空间]
        v: 流速矩阵 [时间×空间]
    """
    # 离散化参数
    dx = space_step(L, N)
    dt = timestep_from_segments(L, N, a)

    # 时间和空间数组
    n_steps = int(T_sim / dt) + 1
    t_array = np.linspace(0, T_sim, n_steps)
    x_array = np.linspace(0, L, N + 1)

    # 初始化结果矩阵
    H = np.zeros((n_steps, N + 1))
    v = np.zeros((n_steps, N + 1))

    # 初始条件：稳态
    H[0, :] = H0
    v[0, :] = v0

    # 时间推进
    for n in range(n_steps - 1):
        t = t_array[n + 1]

        # 内部节点（i = 1 到 N-1）
        for i in range(1, N):
            # 左侧节点（A）- C+特征线
            i_A = i - 1
            v_A = v[n, i_A]
            H_A = H[n, i_A]
            R_A = friction_term(lambda_f, v_A, D, a, dt, g)

            # 右侧节点（B）- C-特征线
            i_B = i + 1
            v_B = v[n, i_B]
            H_B = H[n, i_B]
            R_B = friction_term(lambda_f, v_B, D, a, dt, g)

            # 当前节点（P）
            v[n+1, i] = internal_point_velocity(H_A, H_B, v_A, v_B,
                                               R_A, R_B, a, g)
            H[n+1, i] = internal_point_head(H_A, H_B, v_A, v_B,
                                           R_A, R_B, a, g)

        # 上游边界（水库，i = 0）
        # 恒定水头边界：H = H0
        H[n+1, 0] = H0

        # 使用C-方程计算流速
        i_B = 1
        v_B = v[n, i_B]
        H_B = H[n, i_B]
        R_B = friction_term(lambda_f, v_B, D, a, dt, g)

        # C-方程：H0 = H_B + (a/g)×(v_P - v_B) - R_B
        # 求解 v_P
        v[n+1, 0] = v_B + (g/a) * (H0 - H_B + R_B)

        # 下游边界（阀门，i = N）
        # 阀门特性：v = τ(t) × v_steady
        tau = valve_closure_coefficient(t, tc)

        # 使用C+方程计算压力
        i_A = N - 1
        v_A = v[n, i_A]
        H_A = H[n, i_A]
        R_A = friction_term(lambda_f, v_A, D, a, dt, g)

        # 假设阀门流速按线性减小
        v[n+1, N] = tau * v0

        # C+方程：H_P = H_A - (a/g)×(v_P - v_A) - R_A
        H[n+1, N] = c_plus_equation(H_A, v_A, v[n+1, N], R_A, a, g)

    return t_array, x_array, H, v


# ==================== 可视化函数 ====================

def plot_characteristic_grid(L, T_sim, a, N, save_path='moc_grid.png'):
    """绘制MOC特征线网格"""
    fig, ax = plt.subplots(figsize=(12, 8))

    dx = L / N
    dt = dx / a
    n_steps = int(T_sim / dt)

    # 绘制空间网格线
    for i in range(N + 1):
        x = i * dx
        ax.axvline(x=x, color='gray', linestyle='-', linewidth=0.5, alpha=0.3)

    # 绘制时间层
    for n in range(min(n_steps, 20)):  # 只绘制前20个时间层
        t = n * dt
        ax.axhline(y=t, color='gray', linestyle='-', linewidth=0.5, alpha=0.3)

    # 绘制特征线（示例：从几个点出发）
    sample_points = [0, N//4, N//2, 3*N//4, N]
    for i in sample_points:
        x0 = i * dx
        # C+特征线（向右）
        for n in range(min(n_steps-1, 15)):
            t1 = n * dt
            t2 = (n + 1) * dt
            x1 = x0 + a * (t1 - 0)
            x2 = x0 + a * (t2 - 0)
            if x2 <= L:
                ax.plot([x1, x2], [t1, t2], 'b-', linewidth=1.5, alpha=0.7)

        # C-特征线（向左）
        for n in range(min(n_steps-1, 15)):
            t1 = n * dt
            t2 = (n + 1) * dt
            x1 = x0 - a * (t1 - 0)
            x2 = x0 - a * (t2 - 0)
            if x2 >= 0:
                ax.plot([x1, x2], [t1, t2], 'r-', linewidth=1.5, alpha=0.7)

    # 标注
    ax.text(L*0.5, T_sim*0.9, 'C+ 特征线 (蓝色)', fontsize=11,
           color='blue', fontweight='bold',
           bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    ax.text(L*0.5, T_sim*0.95, 'C- 特征线 (红色)', fontsize=11,
           color='red', fontweight='bold',
           bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    ax.set_xlabel('距离 x (m)', fontsize=12)
    ax.set_ylabel('时间 t (s)', fontsize=12)
    ax.set_title('MOC特征线网格', fontsize=14, fontweight='bold')
    ax.set_xlim([0, L])
    ax.set_ylim([0, min(T_sim, 20*dt)])
    ax.grid(True, alpha=0.2)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"\n✓ 特征线网格图已保存: {save_path}")


def plot_pressure_time_space(t_array, x_array, H, H0,
                             save_path='pressure_time_space.png'):
    """绘制压力时空分布图"""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

    # 子图1：压力水头等值线图
    T, X = np.meshgrid(t_array, x_array)
    levels = np.linspace(H.min(), H.max(), 20)
    cs = ax1.contourf(T.T, X.T, H, levels=levels, cmap='RdYlBu_r')
    ax1.contour(T.T, X.T, H, levels=levels, colors='black',
               linewidths=0.3, alpha=0.3)

    # 添加colorbar
    cbar = plt.colorbar(cs, ax=ax1)
    cbar.set_label('压力水头 H (m)', fontsize=11)

    # 标注初始水头线
    ax1.contour(T.T, X.T, H, levels=[H0], colors='white',
               linewidths=2, linestyles='--')

    ax1.set_xlabel('时间 t (s)', fontsize=12)
    ax1.set_ylabel('距离 x (m)', fontsize=12)
    ax1.set_title('压力水头时空分布（等值线图）', fontsize=13, fontweight='bold')

    # 子图2：阀门处压力时程
    H_valve = H[:, -1]
    ax2.plot(t_array, H_valve, 'b-', linewidth=2, label='阀门处压力')
    ax2.axhline(y=H0, color='g', linestyle='--', linewidth=1.5,
               label=f'初始水头 H0={H0}m')
    ax2.axhline(y=H_valve.max(), color='r', linestyle='--', linewidth=1.5,
               label=f'最大水头 Hmax={H_valve.max():.1f}m')
    ax2.axhline(y=H_valve.min(), color='orange', linestyle='--',
               linewidth=1.5,
               label=f'最小水头 Hmin={H_valve.min():.1f}m')

    ax2.set_xlabel('时间 t (s)', fontsize=12)
    ax2.set_ylabel('压力水头 H (m)', fontsize=12)
    ax2.set_title('阀门处压力时程曲线', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc='upper right', fontsize=11)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"✓ 压力时空分布图已保存: {save_path}")


def plot_velocity_profiles(t_array, x_array, v, v0,
                           save_path='velocity_profiles.png'):
    """绘制不同时刻的流速分布"""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

    # 子图1：选择几个关键时刻的流速分布
    time_indices = [0, len(t_array)//8, len(t_array)//4,
                   len(t_array)//2, -1]
    colors = ['blue', 'green', 'orange', 'red', 'purple']

    for idx, color in zip(time_indices, colors):
        t_current = t_array[idx]
        v_current = v[idx, :]
        ax1.plot(x_array, v_current, color=color, linewidth=2,
                marker='o', markersize=4, label=f't={t_current:.2f}s')

    ax1.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
    ax1.set_xlabel('距离 x (m)', fontsize=12)
    ax1.set_ylabel('流速 v (m/s)', fontsize=12)
    ax1.set_title('不同时刻管道沿程流速分布', fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='upper right', fontsize=10)

    # 子图2：流速时空等值线图
    T, X = np.meshgrid(t_array, x_array)
    levels = np.linspace(v.min(), v.max(), 20)
    cs = ax2.contourf(T.T, X.T, v, levels=levels, cmap='coolwarm')
    ax2.contour(T.T, X.T, v, levels=levels, colors='black',
               linewidths=0.3, alpha=0.3)

    # 添加colorbar
    cbar = plt.colorbar(cs, ax=ax2)
    cbar.set_label('流速 v (m/s)', fontsize=11)

    ax2.set_xlabel('时间 t (s)', fontsize=12)
    ax2.set_ylabel('距离 x (m)', fontsize=12)
    ax2.set_title('流速时空分布（等值线图）', fontsize=13, fontweight='bold')

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"✓ 流速分布图已保存: {save_path}")


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
    print_separator("案例26：特征线法(MOC)水锤数值模拟")

    # ==================== 第一步：定义问题参数 ====================
    print("\n【步骤1】问题参数")
    print("-" * 80)

    # 管道参数
    L = 1200        # 管道长度 (m)
    D = 0.6         # 管道直径 (m)
    e = 0.012       # 管壁厚度 (m)

    # 流体和材料参数
    v0 = 1.5        # 初始流速 (m/s)
    H0 = 60         # 初始水头 (m)
    lambda_f = 0.020  # 摩阻系数
    a = 1200        # 波速 (m/s)
    g = 9.81        # 重力加速度 (m/s²)

    # 阀门参数
    tc = 1.0        # 关闭时间 (s)

    # 数值模拟参数
    N = 12          # 管道分段数
    T_sim = 10.0    # 模拟时长 (s)

    print(f"管道系统：")
    print(f"  长度 L = {L} m")
    print(f"  直径 D = {D} m")
    print(f"  壁厚 e = {e} m")

    print(f"\n初始条件：")
    print(f"  流速 v0 = {v0} m/s")
    print(f"  水头 H0 = {H0} m")
    print(f"  波速 a = {a} m/s")
    print(f"  摩阻系数 λ = {lambda_f}")

    print(f"\n阀门关闭：")
    print(f"  关闭时间 tc = {tc} s")

    # ==================== 第二步：MOC离散化 ====================
    print("\n【步骤2】MOC网格离散化")
    print("-" * 80)

    dx = space_step(L, N)
    dt = timestep_from_segments(L, N, a)

    print(f"空间离散：")
    print(f"  分段数 N = {N}")
    print(f"  空间步长 Δx = L/N = {dx} m")

    print(f"\n时间离散（Courant条件）：")
    print(f"  时间步长 Δt = Δx/a = {dt:.6f} s")
    print(f"  Courant数 CFL = a×Δt/Δx = {a*dt/dx:.3f} (应等于1.0)")

    n_steps = int(T_sim / dt) + 1
    print(f"\n模拟参数：")
    print(f"  模拟时长 T = {T_sim} s")
    print(f"  时间步数 = {n_steps}")
    print(f"  网格节点数 = {N+1}")

    # ==================== 第三步：MOC数值模拟 ====================
    print("\n【步骤3】MOC数值模拟")
    print("-" * 80)

    print("正在进行MOC计算...")

    t_array, x_array, H, v = moc_simulation(
        L, D, a, v0, H0, lambda_f, tc, T_sim, N, g
    )

    print(f"✓ 模拟完成！")
    print(f"  计算了 {len(t_array)} 个时间步")
    print(f"  计算了 {len(x_array)} 个空间节点")

    # ==================== 第四步：结果分析 ====================
    print("\n【步骤4】计算结果分析")
    print("-" * 80)

    # 阀门处结果
    H_valve = H[:, -1]
    v_valve = v[:, -1]

    H_max = H_valve.max()
    H_min = H_valve.min()
    delta_H_max = H_max - H0
    delta_H_min = H_min - H0

    print(f"阀门处压力变化：")
    print(f"  初始水头：H0 = {H0} m")
    print(f"  最大水头：Hmax = {H_max:.2f} m")
    print(f"  最小水头：Hmin = {H_min:.2f} m")
    print(f"  水头升高：ΔH+ = {delta_H_max:.2f} m")
    print(f"  水头降低：ΔH- = {abs(delta_H_min):.2f} m")

    # Joukowsky理论值对比
    delta_H_jouk = (a / g) * v0
    print(f"\nJoukowsky理论值对比：")
    print(f"  Joukowsky升压：ΔH = (a/g)×v0 = {delta_H_jouk:.2f} m")
    print(f"  MOC计算升压：ΔH = {delta_H_max:.2f} m")
    print(f"  相对误差：{abs(delta_H_max - delta_H_jouk)/delta_H_jouk*100:.1f}%")

    # 流速变化
    print(f"\n流速变化：")
    print(f"  初始流速：v0 = {v0} m/s")
    print(f"  关闭后流速：v = {v_valve[-1]:.6f} m/s (≈0)")

    # ==================== 第五步：生成可视化 ====================
    print("\n【步骤5】生成可视化图形")
    print("-" * 80)

    print("正在生成可视化图形...")

    # 图1：特征线网格
    plot_characteristic_grid(L, T_sim, a, N, 'moc_grid.png')

    # 图2：压力时空分布
    plot_pressure_time_space(t_array, x_array, H, H0,
                            'pressure_time_space.png')

    # 图3：流速分布
    plot_velocity_profiles(t_array, x_array, v, v0,
                          'velocity_profiles.png')

    # ==================== 第六步：数值方法评价 ====================
    print("\n【步骤6】MOC方法评价")
    print("-" * 80)

    print(f"1. 数值稳定性：")
    print(f"   ✓ 满足Courant条件（CFL = 1.0）")
    print(f"   ✓ 特征线法保证了数值稳定性")

    print(f"\n2. 精度分析：")
    error = abs(delta_H_max - delta_H_jouk) / delta_H_jouk * 100
    if error < 5:
        print(f"   ✓ 与Joukowsky理论值误差 {error:.1f}% < 5%")
        print(f"   ✓ 计算精度良好")
    else:
        print(f"   ⚠ 与Joukowsky理论值误差 {error:.1f}%")
        print(f"   ⚠ 摩阻影响较大，建议增加分段数")

    print(f"\n3. 边界条件处理：")
    print(f"   ✓ 上游边界：恒定水头（水库）")
    print(f"   ✓ 下游边界：线性关闭阀门")
    print(f"   ✓ 内部节点：C+和C-方程联立求解")

    print(f"\n4. 计算效率：")
    total_points = len(t_array) * len(x_array)
    print(f"   总计算节点数：{total_points}")
    print(f"   空间节点：{len(x_array)}")
    print(f"   时间步数：{len(t_array)}")

    # ==================== 完成 ====================
    print("\n" + "="*80)
    print("✓ 计算完成！所有可视化图形已保存。")
    print("="*80 + "\n")

    return {
        't': t_array,
        'x': x_array,
        'H': H,
        'v': v,
        'H_max': H_max,
        'H_min': H_min
    }


if __name__ == "__main__":
    results = main()
