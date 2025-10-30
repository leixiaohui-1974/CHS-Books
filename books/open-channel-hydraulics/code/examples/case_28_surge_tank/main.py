"""
案例28：调压井计算与可视化

问题描述：
某水电站引水系统，已知：
- 压力隧洞长度 L = 2000 m
- 隧洞断面积 A = 15 m²
- 设计流量 Q = 30 m³/s
- 初始流速 v0 = Q/A = 2.0 m/s
- 水库水位至厂房高差 H_r = 100 m

求解：
1. Thoma临界断面积
2. 调压井设计断面积
3. 最高/最低涌浪计算
4. 涌浪振荡过程模拟
5. 不同断面积的影响分析
6. 可视化涌浪时程

作者：CHS-Books项目
日期：2025-10-30
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
import warnings
warnings.filterwarnings('ignore', category=UserWarning)


# ==================== 调压井计算函数 ====================

def thoma_critical_area(L, A, H_r, F_s=1.0):
    """Thoma临界断面积 [m²]
    A_t,crit = (L*A) / (2*H_r) * F_s
    """
    A_t_crit = (L * A) / (2 * H_r) * F_s
    return A_t_crit


def max_surge_simple(v0, L, A_t, g=9.81):
    """最高涌浪简化公式（忽略阻力）[m]
    Z_max ≈ (v₀²/2g) * (L/A_t)
    """
    Z_max = (v0**2 / (2*g)) * (L / A_t)
    return Z_max


def min_surge_simple(v0, L, A_t, g=9.81):
    """最低涌浪简化估算 [m]（加负荷）
    Z_min ≈ -(v₀²/2g) * (L/A_t)
    """
    Z_min = -(v0**2 / (2*g)) * (L / A_t)
    return Z_min


def oscillation_period(L, A, A_t, g=9.81):
    """涌浪振荡周期（简化公式）[s]
    T ≈ 2π * sqrt(L*A_t / (g*A))
    """
    T = 2 * np.pi * np.sqrt((L * A_t) / (g * A))
    return T


def required_freeboard(Z_max, safety_margin=2.0):
    """所需超高（井顶高程）[m]
    井顶应高出静水位的高度
    """
    freeboard = Z_max + safety_margin
    return freeboard


def surge_oscillation_simulation(L, A, A_t, v0, t_end, dt=0.1, damping=0.05):
    """调压井涌浪振荡数值模拟（简化模型）

    采用简化的微分方程：
    d²Z/dt² + (g*A/A_t) * Z + c*(dZ/dt) = 0

    其中 c 为阻尼系数

    Args:
        L: 隧洞长度 [m]
        A: 隧洞断面积 [m²]
        A_t: 调压井断面积 [m²]
        v0: 初始流速 [m/s]
        t_end: 模拟时长 [s]
        dt: 时间步长 [s]
        damping: 阻尼系数

    Returns:
        t: 时间数组
        Z: 涌浪高度数组
    """
    g = 9.81
    n_steps = int(t_end / dt)

    t = np.zeros(n_steps)
    Z = np.zeros(n_steps)
    V = np.zeros(n_steps)  # 涌浪上升速度

    # 初始条件：突然停机，水流惯性导致涌浪
    Z[0] = 0.0
    V[0] = v0 * A / A_t  # 初始上升速度

    # 数值积分（欧拉法）
    for i in range(1, n_steps):
        t[i] = i * dt

        # 恢复力（重力）加速度
        a_gravity = -(g * A / (L * A_t)) * Z[i-1]

        # 阻尼加速度
        a_damping = -damping * V[i-1]

        # 总加速度
        a_total = a_gravity + a_damping

        # 更新速度和位移
        V[i] = V[i-1] + a_total * dt
        Z[i] = Z[i-1] + V[i] * dt

    return t, Z


# ==================== 可视化函数 ====================

def plot_surge_oscillation(L, A, A_t, v0, T, Z_max_theory,
                           save_path='surge_oscillation.png'):
    """绘制涌浪振荡时程曲线"""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

    # 模拟时长：3个周期
    t_end = 3 * T

    # 三种不同阻尼系数的模拟
    dampings = [0.0, 0.05, 0.1]
    labels = ['无阻尼（理想）', '小阻尼（实际）', '大阻尼（节流孔）']
    colors = ['b', 'g', 'r']

    for damp, label, color in zip(dampings, labels, colors):
        t, Z = surge_oscillation_simulation(L, A, A_t, v0, t_end,
                                            dt=0.1, damping=damp)

        # 子图1：涌浪高度时程
        ax1.plot(t, Z, color=color, linewidth=2, label=label)

    # 标注理论最大涌浪
    ax1.axhline(y=Z_max_theory, color='orange', linestyle='--',
               linewidth=2, label=f'理论最大涌浪 Z={Z_max_theory:.2f}m')
    ax1.axhline(y=-Z_max_theory, color='orange', linestyle='--', linewidth=2)
    ax1.axhline(y=0, color='k', linestyle='-', linewidth=0.5)

    # 标注振荡周期
    for i in range(4):
        ax1.axvline(x=i*T, color='gray', linestyle=':', alpha=0.5)
        if i > 0:
            ax1.text(i*T, Z_max_theory+5, f'{i}T',
                    ha='center', fontsize=9, color='gray')

    ax1.set_xlabel('时间 (s)', fontsize=12)
    ax1.set_ylabel('涌浪高度 Z (m)', fontsize=12)
    ax1.set_title('调压井涌浪振荡时程（减负荷）', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='upper right', fontsize=11)
    ax1.set_xlim([0, t_end])

    # 子图2：相平面图（Z vs dZ/dt）
    for damp, label, color in zip(dampings[1:], labels[1:], colors[1:]):
        t, Z = surge_oscillation_simulation(L, A, A_t, v0, t_end,
                                            dt=0.1, damping=damp)
        # 计算速度
        V = np.gradient(Z, t)

        ax2.plot(Z, V, color=color, linewidth=2, label=label, alpha=0.7)

    ax2.plot(0, 0, 'ro', markersize=10, label='平衡点')
    ax2.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
    ax2.axvline(x=0, color='k', linestyle='-', linewidth=0.5)

    ax2.set_xlabel('涌浪高度 Z (m)', fontsize=12)
    ax2.set_ylabel('涌浪速度 dZ/dt (m/s)', fontsize=12)
    ax2.set_title('相平面图（涌浪高度 vs 涌浪速度）', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc='upper right', fontsize=11)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"\n✓ 涌浪振荡图已保存: {save_path}")


def plot_area_comparison(L, A, v0, H_r, A_t_crit,
                         save_path='surge_tank_area_comparison.png'):
    """绘制不同调压井面积的影响对比"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # 调压井面积范围：从0.5倍到3倍临界面积
    A_t_array = np.linspace(0.5*A_t_crit, 3*A_t_crit, 100)
    A_t_ratio = A_t_array / A_t_crit

    # 计算最大涌浪
    Z_max = np.array([max_surge_simple(v0, L, A_t) for A_t in A_t_array])

    # 计算振荡周期
    T = np.array([oscillation_period(L, A, A_t) for A_t in A_t_array])

    # 子图1：最大涌浪 vs 面积
    ax1.plot(A_t_ratio, Z_max, 'b-', linewidth=2)
    ax1.axvline(x=1.0, color='r', linestyle='--', linewidth=2,
               label='临界面积 At=At,crit')

    # 标注稳定/不稳定区域
    ax1.fill_between(A_t_ratio[A_t_ratio<1], 0, Z_max[A_t_ratio<1].max(),
                     alpha=0.2, color='red', label='不稳定区')
    ax1.fill_between(A_t_ratio[A_t_ratio>=1], 0, Z_max[A_t_ratio>=1].max(),
                     alpha=0.2, color='green', label='稳定区')

    ax1.set_xlabel('调压井面积比 At/At,crit', fontsize=12)
    ax1.set_ylabel('最大涌浪 Zmax (m)', fontsize=12)
    ax1.set_title('最大涌浪 vs 调压井面积', fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='upper right', fontsize=11)
    ax1.set_xlim([0.5, 3])

    # 子图2：振荡周期 vs 面积
    ax2.plot(A_t_ratio, T, 'g-', linewidth=2)
    ax2.axvline(x=1.0, color='r', linestyle='--', linewidth=2,
               label='临界面积 At=At,crit')

    ax2.set_xlabel('调压井面积比 At/At,crit', fontsize=12)
    ax2.set_ylabel('振荡周期 T (s)', fontsize=12)
    ax2.set_title('振荡周期 vs 调压井面积', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc='upper right', fontsize=11)
    ax2.set_xlim([0.5, 3])

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"✓ 面积对比图已保存: {save_path}")


def plot_surge_tank_schematic(L, A, A_t, H_r, Z_max, Z_min,
                              save_path='surge_tank_schematic.png'):
    """绘制调压井示意图"""
    fig, ax = plt.subplots(figsize=(10, 8))

    # 水库
    reservoir_x = [0, 0, 0.2, 0.2]
    reservoir_y = [0, H_r, H_r, 0]
    ax.fill(reservoir_x, reservoir_y, color='lightblue', alpha=0.5,
           edgecolor='blue', linewidth=2, label='水库')
    ax.text(0.1, H_r-5, '水库', ha='center', fontsize=11, fontweight='bold')

    # 压力隧洞
    tunnel_x = [0.2, 0.6, 0.6, 0.2]
    tunnel_width = np.sqrt(A) * 0.1  # 按比例绘制
    tunnel_y = [H_r-tunnel_width, H_r-tunnel_width,
               H_r+tunnel_width, H_r+tunnel_width]
    ax.fill(tunnel_x, tunnel_y, color='gray', alpha=0.3,
           edgecolor='black', linewidth=2)
    ax.text(0.4, H_r+10, f'压力隧洞\nL={L}m, A={A}m²',
           ha='center', fontsize=10)

    # 调压井
    surge_x = 0.6
    surge_width = np.sqrt(A_t) * 0.05  # 按比例
    surge_base_y = H_r - 20
    surge_height = Z_max + 20

    # 调压井筒
    shaft = plt.Rectangle((surge_x-surge_width/2, surge_base_y),
                          surge_width, surge_height,
                          facecolor='lightgray', edgecolor='black',
                          linewidth=2, label='调压井')
    ax.add_patch(shaft)

    # 静水位
    ax.plot([surge_x-surge_width, surge_x+surge_width],
           [H_r, H_r], 'b-', linewidth=2, label='静水位')

    # 最高涌浪
    ax.plot([surge_x-surge_width, surge_x+surge_width],
           [H_r+Z_max, H_r+Z_max], 'r--', linewidth=2, label='最高涌浪')
    ax.fill_between([surge_x-surge_width/2, surge_x+surge_width/2],
                    H_r, H_r+Z_max, color='red', alpha=0.2)

    # 最低涌浪
    ax.plot([surge_x-surge_width, surge_x+surge_width],
           [H_r+Z_min, H_r+Z_min], 'orange', linestyle='--',
           linewidth=2, label='最低涌浪')
    ax.fill_between([surge_x-surge_width/2, surge_x+surge_width/2],
                    H_r+Z_min, H_r, color='orange', alpha=0.2)

    # 标注尺寸
    ax.annotate('', xy=(surge_x+0.15, H_r), xytext=(surge_x+0.15, H_r+Z_max),
               arrowprops=dict(arrowstyle='<->', color='red', lw=2))
    ax.text(surge_x+0.18, H_r+Z_max/2, f'Zmax={Z_max:.1f}m',
           fontsize=10, color='red', fontweight='bold')

    ax.annotate('', xy=(surge_x+0.15, H_r+Z_min), xytext=(surge_x+0.15, H_r),
               arrowprops=dict(arrowstyle='<->', color='orange', lw=2))
    ax.text(surge_x+0.18, H_r+Z_min/2, f'Zmin={abs(Z_min):.1f}m',
           fontsize=10, color='orange', fontweight='bold')

    # 厂房
    plant_x = [0.8, 0.8, 0.95, 0.95]
    plant_y = [0, 30, 30, 0]
    ax.fill(plant_x, plant_y, color='lightgreen', alpha=0.5,
           edgecolor='green', linewidth=2)
    ax.text(0.875, 15, '厂房', ha='center', fontsize=11, fontweight='bold')

    # 压力管道到厂房
    pipe_x = [0.6, 0.8, 0.8, 0.6]
    pipe_y = [H_r-tunnel_width, 25, 30, H_r+tunnel_width]
    ax.fill(pipe_x, pipe_y, color='gray', alpha=0.3,
           edgecolor='black', linewidth=2)

    ax.set_xlim([0, 1])
    ax.set_ylim([-10, H_r+Z_max+30])
    ax.set_aspect('equal')
    ax.axis('off')
    ax.legend(loc='upper left', fontsize=11)
    ax.set_title('调压井系统示意图', fontsize=14, fontweight='bold', pad=20)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"✓ 调压井示意图已保存: {save_path}")


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
    print_separator("案例28：调压井计算与可视化")

    # ==================== 第一步：定义问题参数 ====================
    print("\n【步骤1】问题参数")
    print("-" * 80)

    # 引水系统参数
    L = 2000        # 压力隧洞长度 (m)
    A = 15          # 隧洞断面积 (m²)
    Q = 30          # 设计流量 (m³/s)
    v0 = Q / A      # 初始流速 (m/s)
    H_r = 100       # 水头（水库至厂房）(m)
    g = 9.81        # 重力加速度 (m/s²)

    print(f"引水系统参数：")
    print(f"  压力隧洞长度 L = {L} m")
    print(f"  隧洞断面积 A = {A} m²")
    print(f"  设计流量 Q = {Q} m³/s")
    print(f"  初始流速 v0 = Q/A = {v0:.2f} m/s")
    print(f"  水头 Hr = {H_r} m")

    # ==================== 第二步：Thoma临界断面积 ====================
    print("\n【步骤2】Thoma临界断面积")
    print("-" * 80)

    # 不同安全系数
    F_s_values = [1.0, 1.5, 2.0]

    print(f"Thoma公式：At,crit = (L×A)/(2×Hr) × Fs")
    print(f"\n{'安全系数Fs':<12} {'临界面积(m²)':<15} {'临界直径(m)'}")
    print("-" * 50)

    A_t_crit = None
    for F_s in F_s_values:
        A_crit = thoma_critical_area(L, A, H_r, F_s)
        D_crit = np.sqrt(4 * A_crit / np.pi)
        print(f"{F_s:<12.1f} {A_crit:<15.2f} {D_crit:.2f}")

        if F_s == 1.5:
            A_t_crit = A_crit  # 采用Fs=1.5作为设计值

    # ==================== 第三步：设计调压井断面积 ====================
    print("\n【步骤3】设计调压井断面积")
    print("-" * 80)

    # 采用1.5倍临界面积
    A_t = A_t_crit
    D_t = np.sqrt(4 * A_t / np.pi)

    print(f"设计准则：At ≥ At,crit（Fs=1.5）")
    print(f"\n设计断面积：At = {A_t:.2f} m²")
    print(f"设计直径：Dt = {D_t:.2f} m")
    print(f"工程设计：建议采用 D = {np.ceil(D_t):.0f} m 圆形调压井")

    # ==================== 第四步：涌浪计算 ====================
    print("\n【步骤4】涌浪高度计算")
    print("-" * 80)

    # 最高涌浪（减负荷）
    Z_max = max_surge_simple(v0, L, A_t)

    # 最低涌浪（加负荷）
    Z_min = min_surge_simple(v0, L, A_t)

    print(f"减负荷（机组甩负荷或停机）：")
    print(f"  最高涌浪：Zmax = (v0²/2g)×(L/At) = {Z_max:.2f} m")
    print(f"  井内最高水位 = Hr + Zmax = {H_r + Z_max:.2f} m")

    print(f"\n加负荷（机组启动）：")
    print(f"  最低涌浪：Zmin = -{abs(Z_min):.2f} m")
    print(f"  井内最低水位 = Hr + Zmin = {H_r + Z_min:.2f} m")

    # 安全超高
    safety_margin = 2.0
    freeboard = required_freeboard(Z_max, safety_margin)

    print(f"\n安全超高：")
    print(f"  井顶应高出静水位 ≥ Zmax + 安全裕度")
    print(f"  井顶高程 ≥ {H_r} + {freeboard:.2f} = {H_r + freeboard:.2f} m")

    # ==================== 第五步：振荡周期 ====================
    print("\n【步骤5】涌浪振荡周期")
    print("-" * 80)

    T = oscillation_period(L, A, A_t)

    print(f"简化公式：T = 2π × √(L×At / (g×A))")
    print(f"\n振荡周期：T = {T:.1f} s = {T/60:.2f} min")
    print(f"频率：f = 1/T = {1/T*1000:.2f} mHz")

    # ==================== 第六步：生成可视化 ====================
    print("\n【步骤6】生成可视化图形")
    print("-" * 80)

    print("正在生成可视化图形...")

    # 图1：涌浪振荡时程
    plot_surge_oscillation(L, A, A_t, v0, T, Z_max,
                          'surge_oscillation.png')

    # 图2：面积影响对比
    plot_area_comparison(L, A, v0, H_r, A_t_crit,
                        'surge_tank_area_comparison.png')

    # 图3：调压井示意图
    plot_surge_tank_schematic(L, A, A_t, H_r, Z_max, Z_min,
                             'surge_tank_schematic.png')

    # ==================== 第七步：工程建议 ====================
    print("\n【步骤7】工程设计建议")
    print("-" * 80)

    print(f"1. 调压井类型选择：")
    print(f"   - 本工程水头差 Hr = {H_r}m，隧洞长度 L = {L}m")
    print(f"   - 建议采用：普通圆形调压井")
    print(f"   - 若涌浪过大，可考虑：阻抗式调压井（加节流孔）")

    print(f"\n2. 调压井尺寸：")
    print(f"   - 断面积：At ≥ {A_t:.1f} m²")
    print(f"   - 直径：Dt ≥ {D_t:.1f} m（建议 {np.ceil(D_t):.0f}m）")
    print(f"   - 井深：井底应低于隧洞至少 5m")
    print(f"   - 井高：井顶高程 ≥ {H_r + freeboard:.1f} m")

    print(f"\n3. 稳定性校核：")
    A_ratio = A_t / A_t_crit
    if A_ratio >= 1.0:
        print(f"   ✓ At/At,crit = {A_ratio:.2f} ≥ 1.0")
        print(f"   ✓ 满足Thoma稳定性条件")
    else:
        print(f"   ✗ At/At,crit = {A_ratio:.2f} < 1.0")
        print(f"   ✗ 不满足稳定性条件，需增大断面积！")

    print(f"\n4. 运行建议：")
    print(f"   - 机组启停应缓慢，避免突变")
    print(f"   - 监测井内水位，防止溢流或负压")
    print(f"   - 定期检查井筒结构，防止渗漏")
    print(f"   - 设置水位报警装置（高位+低位）")

    # ==================== 完成 ====================
    print("\n" + "="*80)
    print("✓ 计算完成！所有可视化图形已保存。")
    print("="*80 + "\n")

    return {
        'A_t_crit': A_t_crit,
        'A_t': A_t,
        'Z_max': Z_max,
        'Z_min': Z_min,
        'T': T
    }


if __name__ == "__main__":
    results = main()
