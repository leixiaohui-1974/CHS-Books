#!/usr/bin/env python3
"""
案例24：虹吸与倒虹吸设计

本示例展示：
1. 倒虹吸水力计算（水头损失、流速、压力分布）
2. 虹吸管真空度计算
3. 汽蚀校核
4. 安全运行条件分析

运行方式：
    python main.py

作者：CHS-Books项目
日期：2025-10-30
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


# ========== 水力计算函数 ==========

def darcy_friction_factor(Re, epsilon_D):
    """Colebrook-White方程求解摩阻系数"""
    if Re < 2320:
        return 64 / Re
    # Swamee-Jain显式公式
    lambda_f = 0.25 / (np.log10(epsilon_D/3.7 + 5.74/Re**0.9))**2
    return lambda_f


def head_loss_pipe(lambda_f, L, D, v, g=9.81):
    """管道沿程损失"""
    h_f = lambda_f * (L/D) * (v**2 / (2*g))
    return h_f


def head_loss_entrance(v, xi_e=0.5, g=9.81):
    """进口损失"""
    h_e = xi_e * (v**2 / (2*g))
    return h_e


def head_loss_exit(v, xi_o=1.0, g=9.81):
    """出口损失"""
    h_o = xi_o * (v**2 / (2*g))
    return h_o


def head_loss_bend(v, xi_b=0.3, g=9.81):
    """弯管损失"""
    h_b = xi_b * (v**2 / (2*g))
    return h_b


def reynolds_number(v, D, nu=1.0e-6):
    """Reynolds数"""
    return v * D / nu


def vacuum_height(p_atm, p_local):
    """真空度（米水柱）"""
    return p_atm - p_local


# ========== 打印函数 ==========

def print_header(title, width=70):
    """打印标题"""
    print("\n" + "="*width)
    print(f"  {title}")
    print("="*width)


def print_param(name, value, unit="", width=50):
    """打印参数"""
    if unit:
        print(f"  {name:.<{width}} {value:>12.4f} {unit}")
    else:
        print(f"  {name:.<{width}} {value:>12}")


# ========== 演示1：倒虹吸水力计算 ==========

def demo1_inverted_siphon():
    """演示1：倒虹吸水力计算"""
    print_header("演示1：倒虹吸水力计算")

    # 参数
    Q = 1.5         # 流量 (m³/s)
    D = 1.0         # 管径 (m)
    L = 80          # 水平长度 (m)
    H1 = 50         # 上游水面高程 (m)
    H2 = 48         # 下游水面高程 (m)
    H_bed = 35      # 河床高程 (m)
    epsilon = 0.0003  # 粗糙度 (m)
    nu = 1.0e-6     # 运动粘度 (m²/s)
    g = 9.81        # 重力加速度 (m/s²)

    # 计算流速
    A = np.pi * D**2 / 4
    v = Q / A

    # Reynolds数和摩阻系数
    Re = reynolds_number(v, D, nu)
    epsilon_D = epsilon / D
    lambda_f = darcy_friction_factor(Re, epsilon_D)

    # 各种损失
    h_entrance = head_loss_entrance(v, xi_e=0.5, g=g)
    h_pipe = head_loss_pipe(lambda_f, L, D, v, g)
    h_bend = 2 * head_loss_bend(v, xi_b=0.3, g=g)  # 两个弯管
    h_exit = head_loss_exit(v, xi_o=1.0, g=g)
    h_total = h_entrance + h_pipe + h_bend + h_exit

    # 打印结果
    print("\n【输入参数】")
    print_param("流量 Q", Q, "m³/s")
    print_param("管径 D", D, "m")
    print_param("长度 L", L, "m")
    print_param("上游高程 H1", H1, "m")
    print_param("下游高程 H2", H2, "m")
    print_param("河床高程 H_bed", H_bed, "m")

    print("\n【水力计算】")
    print_param("断面积 A", A, "m²")
    print_param("流速 v", v, "m/s")
    print_param("Reynolds数 Re", Re, "")
    print_param("摩阻系数 λ", lambda_f, "")

    print("\n【水头损失】")
    print_param("进口损失 h_entrance", h_entrance, "m")
    print_param("沿程损失 h_pipe", h_pipe, "m")
    print_param("弯管损失 h_bend", h_bend, "m")
    print_param("出口损失 h_exit", h_exit, "m")
    print_param("总损失 h_total", h_total, "m")

    print("\n【校核】")
    available_head = H1 - H2
    print_param("可用水头", available_head, "m")
    print_param("需要水头", h_total, "m")
    if h_total < available_head:
        print("  ✓ 水头满足要求")
    else:
        print("  ✗ 水头不足")

    # 压力分布计算
    # 沿管道长度的压力分布
    n_points = 100
    s_array = np.linspace(0, L, n_points)  # 沿程距离

    # 高程分布（倒虹吸形状）
    # 分三段：下降段、水平段、上升段
    L_down = 20  # 下降段长度
    L_flat = 40  # 水平段长度
    L_up = 20    # 上升段长度

    z_array = np.zeros(n_points)
    for i, s in enumerate(s_array):
        if s < L_down:
            # 下降段
            z_array[i] = H1 - (H1 - H_bed) * (s / L_down)
        elif s < L_down + L_flat:
            # 水平段
            z_array[i] = H_bed
        else:
            # 上升段
            s_up = s - (L_down + L_flat)
            z_array[i] = H_bed + (H2 - H_bed) * (s_up / L_up)

    # 压力水头分布
    h_f_s = h_entrance + (s_array / L) * h_pipe  # 累积沿程损失
    p_head_array = H1 - z_array - h_f_s - v**2/(2*g)

    # 绘图
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

    # 子图1：倒虹吸剖面
    ax1.fill_between(s_array, 0, z_array, alpha=0.3, color='brown', label='管道')
    ax1.plot(s_array, z_array, 'k-', linewidth=2, label='管道中心线')
    ax1.axhline(H1, color='blue', linestyle='--', label=f'上游水位 ({H1}m)')
    ax1.axhline(H2, color='cyan', linestyle='--', label=f'下游水位 ({H2}m)')
    ax1.axhline(H_bed, color='gray', linestyle=':', label=f'河床 ({H_bed}m)')
    ax1.set_xlabel('沿程距离 (m)', fontsize=11)
    ax1.set_ylabel('高程 (m)', fontsize=11)
    ax1.set_title('倒虹吸剖面图', fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=10)
    ax1.set_ylim([0, 55])

    # 子图2：压力分布
    ax2.plot(s_array, p_head_array, 'r-', linewidth=2, label='压力水头')
    ax2.axhline(0, color='k', linestyle='--', linewidth=1)
    ax2.fill_between(s_array, 0, p_head_array, alpha=0.2, color='red')
    ax2.set_xlabel('沿程距离 (m)', fontsize=11)
    ax2.set_ylabel('压力水头 (m)', fontsize=11)
    ax2.set_title('倒虹吸压力分布', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend(fontsize=10)

    # 标注最大压力点
    i_max = np.argmax(p_head_array)
    ax2.plot(s_array[i_max], p_head_array[i_max], 'ro', markersize=10)
    ax2.annotate(f'最大压力\n{p_head_array[i_max]:.2f} m',
                xy=(s_array[i_max], p_head_array[i_max]),
                xytext=(s_array[i_max]+10, p_head_array[i_max]+2),
                fontsize=10, ha='left',
                arrowprops=dict(arrowstyle='->', color='red', lw=1.5))

    plt.tight_layout()
    plt.savefig('demo1_inverted_siphon.png', dpi=300, bbox_inches='tight')
    print(f"\n  ✓ 图形已保存：demo1_inverted_siphon.png")
    plt.close()

    return {
        'Q': Q, 'v': v, 'h_total': h_total,
        'p_max': p_head_array.max()
    }


# ========== 演示2：虹吸管真空度计算 ==========

def demo2_siphon_vacuum():
    """演示2：虹吸管真空度计算"""
    print_header("演示2：虹吸管真空度计算")

    # 参数
    Q = 0.8          # 流量 (m³/s)
    D = 0.8          # 管径 (m)
    L_total = 150    # 总长度 (m)
    H1 = 45          # 上游水位 (m)
    H2 = 43          # 下游水位 (m)
    H_peak = 50      # 山脊顶高程 (m)
    epsilon = 0.0003 # 粗糙度 (m)
    nu = 1.0e-6      # 运动粘度 (m²/s)
    g = 9.81         # 重力加速度 (m/s²)
    p_atm = 10.33    # 大气压 (m水柱)
    p_vapor = 0.238  # 饱和蒸汽压 (m水柱, 20°C)

    # 计算流速
    A = np.pi * D**2 / 4
    v = Q / A

    # Reynolds数和摩阻系数
    Re = reynolds_number(v, D, nu)
    epsilon_D = epsilon / D
    lambda_f = darcy_friction_factor(Re, epsilon_D)

    # 沿程分布
    n_points = 200
    s_array = np.linspace(0, L_total, n_points)

    # 高程分布（虹吸形状）
    L_up = 60    # 上升段
    L_down = 90  # 下降段

    z_array = np.zeros(n_points)
    for i, s in enumerate(s_array):
        if s < L_up:
            # 上升段
            z_array[i] = H1 + (H_peak - H1) * (s / L_up)
        else:
            # 下降段
            s_d = s - L_up
            z_array[i] = H_peak - (H_peak - H2) * (s_d / L_down)

    # 各种损失
    h_entrance = head_loss_entrance(v, xi_e=0.5, g=g)
    h_pipe_total = head_loss_pipe(lambda_f, L_total, D, v, g)
    h_bend = 2 * head_loss_bend(v, xi_b=0.3, g=g)
    h_exit = head_loss_exit(v, xi_o=1.0, g=g)
    h_total = h_entrance + h_pipe_total + h_bend + h_exit

    # 沿程压力水头
    h_f_s = h_entrance + (s_array / L_total) * h_pipe_total
    p_head_array = H1 - z_array - h_f_s - v**2/(2*g)

    # 真空度
    vacuum_array = p_atm - p_head_array

    # 最高点真空度
    i_peak = np.argmin(p_head_array)
    h_vac_peak = vacuum_array[i_peak]
    p_peak = p_head_array[i_peak]

    # 打印结果
    print("\n【输入参数】")
    print_param("流量 Q", Q, "m³/s")
    print_param("管径 D", D, "m")
    print_param("总长度 L", L_total, "m")
    print_param("上游水位 H1", H1, "m")
    print_param("下游水位 H2", H2, "m")
    print_param("山脊顶高程 H_peak", H_peak, "m")

    print("\n【水力计算】")
    print_param("流速 v", v, "m/s")
    print_param("Reynolds数 Re", Re, "")
    print_param("摩阻系数 λ", lambda_f, "")
    print_param("总水头损失", h_total, "m")

    print("\n【真空度分析】")
    print_param("大气压 p_atm", p_atm, "m")
    print_param("最高点压力水头 p_peak", p_peak, "m")
    print_param("最高点真空度 h_vac", h_vac_peak, "m")
    print_param("允许真空度", 7.0, "m")

    if h_vac_peak < 7.0:
        print("  ✓ 真空度满足要求")
    else:
        print("  ✗ 真空度过大，有风险")

    print("\n【汽蚀校核】")
    print_param("饱和蒸汽压 p_vapor", p_vapor, "m")
    print_param("最高点压力 p_peak", p_peak, "m")
    NPSH = p_peak - p_vapor
    print_param("汽蚀余量 NPSH", NPSH, "m")

    if NPSH > 0.5:
        print("  ✓ 无汽蚀风险")
    else:
        print("  ✗ 有汽蚀风险")

    # 绘图
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 14))

    # 子图1：虹吸管剖面
    ax1.fill_between(s_array, 0, z_array, alpha=0.3, color='blue', label='管道')
    ax1.plot(s_array, z_array, 'k-', linewidth=2, label='管道中心线')
    ax1.axhline(H1, color='cyan', linestyle='--', label=f'上游水位 ({H1}m)')
    ax1.axhline(H2, color='green', linestyle='--', label=f'下游水位 ({H2}m)')
    ax1.axhline(H_peak, color='red', linestyle=':', label=f'山脊顶 ({H_peak}m)')
    ax1.plot(s_array[i_peak], z_array[i_peak], 'ro', markersize=12, label='最高点')
    ax1.set_xlabel('沿程距离 (m)', fontsize=11)
    ax1.set_ylabel('高程 (m)', fontsize=11)
    ax1.set_title('虹吸管剖面图', fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=10)
    ax1.set_ylim([0, 55])

    # 子图2：压力分布
    ax2.plot(s_array, p_head_array, 'b-', linewidth=2, label='压力水头')
    ax2.axhline(0, color='k', linestyle='--', linewidth=1, label='大气压基准')
    ax2.axhline(p_vapor, color='r', linestyle=':', linewidth=2, label=f'饱和蒸汽压 ({p_vapor}m)')
    ax2.fill_between(s_array, 0, p_head_array, alpha=0.2, color='blue')
    ax2.plot(s_array[i_peak], p_head_array[i_peak], 'ro', markersize=10)
    ax2.annotate(f'最低压力\n{p_peak:.2f} m',
                xy=(s_array[i_peak], p_peak),
                xytext=(s_array[i_peak]+20, p_peak-3),
                fontsize=10, ha='left',
                arrowprops=dict(arrowstyle='->', color='red', lw=1.5))
    ax2.set_xlabel('沿程距离 (m)', fontsize=11)
    ax2.set_ylabel('压力水头 (m)', fontsize=11)
    ax2.set_title('虹吸管压力分布', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend(fontsize=10)

    # 子图3：真空度分布
    ax3.plot(s_array, vacuum_array, 'r-', linewidth=2, label='真空度')
    ax3.axhline(7.0, color='orange', linestyle='--', linewidth=2, label='允许真空度 (7m)')
    ax3.fill_between(s_array, 0, vacuum_array, alpha=0.2, color='red')
    ax3.plot(s_array[i_peak], h_vac_peak, 'ro', markersize=10)
    ax3.annotate(f'最大真空度\n{h_vac_peak:.2f} m',
                xy=(s_array[i_peak], h_vac_peak),
                xytext=(s_array[i_peak]+20, h_vac_peak+1),
                fontsize=10, ha='left',
                arrowprops=dict(arrowstyle='->', color='red', lw=1.5))
    ax3.set_xlabel('沿程距离 (m)', fontsize=11)
    ax3.set_ylabel('真空度 (m)', fontsize=11)
    ax3.set_title('虹吸管真空度分布', fontsize=13, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    ax3.legend(fontsize=10)
    ax3.set_ylim([0, 10])

    plt.tight_layout()
    plt.savefig('demo2_siphon_vacuum.png', dpi=300, bbox_inches='tight')
    print(f"\n  ✓ 图形已保存：demo2_siphon_vacuum.png")
    plt.close()

    return {
        'Q': Q, 'v': v, 'h_vac_peak': h_vac_peak,
        'NPSH': NPSH
    }


# ========== 演示3：流量对真空度的影响 ==========

def demo3_flow_rate_effect():
    """演示3：流量对真空度的影响"""
    print_header("演示3：流量对真空度的影响")

    # 固定参数
    D = 0.8
    L_total = 150
    H1 = 45
    H2 = 43
    H_peak = 50
    epsilon = 0.0003
    nu = 1.0e-6
    g = 9.81
    p_atm = 10.33
    L_up = 60

    # 流量范围
    Q_array = np.linspace(0.2, 1.5, 20)
    h_vac_array = []
    NPSH_array = []

    print("\n【流量变化分析】")
    print(f"  流量范围：{Q_array[0]:.1f} ~ {Q_array[-1]:.1f} m³/s")

    for Q in Q_array:
        A = np.pi * D**2 / 4
        v = Q / A
        Re = reynolds_number(v, D, nu)
        epsilon_D = epsilon / D
        lambda_f = darcy_friction_factor(Re, epsilon_D)

        # 最高点损失
        h_entrance = head_loss_entrance(v, xi_e=0.5, g=g)
        h_pipe_to_peak = head_loss_pipe(lambda_f, L_up, D, v, g)
        h_bend = head_loss_bend(v, xi_b=0.3, g=g)

        # 最高点压力
        p_peak = H1 - H_peak - h_entrance - h_pipe_to_peak - h_bend - v**2/(2*g)
        h_vac = p_atm - p_peak

        h_vac_array.append(h_vac)
        NPSH_array.append(p_peak - 0.238)  # 20°C

    h_vac_array = np.array(h_vac_array)
    NPSH_array = np.array(NPSH_array)

    # 找到临界流量
    i_critical = np.where(h_vac_array > 7.0)[0]
    if len(i_critical) > 0:
        Q_critical = Q_array[i_critical[0]]
        print_param("临界流量 Q_critical", Q_critical, "m³/s")
    else:
        print("  所有流量均安全")

    # 绘图
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10))

    # 子图1：真空度vs流量
    ax1.plot(Q_array, h_vac_array, 'b-', linewidth=2, label='真空度')
    ax1.axhline(7.0, color='r', linestyle='--', linewidth=2, label='允许真空度')
    ax1.fill_between(Q_array, 0, h_vac_array, alpha=0.2, color='blue')

    if len(i_critical) > 0:
        ax1.axvspan(Q_critical, Q_array[-1], alpha=0.2, color='red', label='危险区')
        ax1.axvline(Q_critical, color='orange', linestyle=':', linewidth=2)
        ax1.annotate(f'Q_crit = {Q_critical:.2f} m³/s',
                    xy=(Q_critical, 7), xytext=(Q_critical-0.2, 8),
                    fontsize=10, ha='right',
                    arrowprops=dict(arrowstyle='->', color='orange', lw=1.5))

    ax1.set_xlabel('流量 Q (m³/s)', fontsize=11)
    ax1.set_ylabel('真空度 (m)', fontsize=11)
    ax1.set_title('流量对真空度的影响', fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=10)

    # 子图2：NPSH vs流量
    ax2.plot(Q_array, NPSH_array, 'g-', linewidth=2, label='NPSH')
    ax2.axhline(0.5, color='r', linestyle='--', linewidth=2, label='最小NPSH')
    ax2.axhline(0, color='k', linestyle='-', linewidth=1)
    ax2.fill_between(Q_array, 0, NPSH_array, alpha=0.2, color='green')
    ax2.set_xlabel('流量 Q (m³/s)', fontsize=11)
    ax2.set_ylabel('汽蚀余量 NPSH (m)', fontsize=11)
    ax2.set_title('流量对汽蚀余量的影响', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend(fontsize=10)

    plt.tight_layout()
    plt.savefig('demo3_flow_rate_effect.png', dpi=300, bbox_inches='tight')
    print(f"\n  ✓ 图形已保存：demo3_flow_rate_effect.png")
    plt.close()


# ========== 演示4：优化设计建议 ==========

def demo4_design_optimization():
    """演示4：优化设计建议"""
    print_header("演示4：优化设计建议")

    # 基准参数
    Q = 0.8
    L_total = 150
    H1 = 45
    H2 = 43
    epsilon = 0.0003
    nu = 1.0e-6
    g = 9.81
    p_atm = 10.33
    L_up = 60

    # 不同管径和峰顶高程的组合
    D_array = np.array([0.6, 0.7, 0.8, 0.9, 1.0])
    H_peak_array = np.array([47, 48, 49, 50, 51])

    print("\n【优化设计矩阵】")
    print(f"  管径范围：{D_array[0]:.1f} ~ {D_array[-1]:.1f} m")
    print(f"  峰顶高程：{H_peak_array[0]} ~ {H_peak_array[-1]} m")

    # 创建网格
    D_grid, H_peak_grid = np.meshgrid(D_array, H_peak_array)
    h_vac_grid = np.zeros_like(D_grid)

    for i in range(len(H_peak_array)):
        for j in range(len(D_array)):
            D = D_grid[i, j]
            H_peak = H_peak_grid[i, j]

            A = np.pi * D**2 / 4
            v = Q / A
            Re = reynolds_number(v, D, nu)
            epsilon_D = epsilon / D
            lambda_f = darcy_friction_factor(Re, epsilon_D)

            # 最高点压力
            h_entrance = head_loss_entrance(v, xi_e=0.5, g=g)
            h_pipe_to_peak = head_loss_pipe(lambda_f, L_up, D, v, g)
            h_bend = head_loss_bend(v, xi_b=0.3, g=g)

            p_peak = H1 - H_peak - h_entrance - h_pipe_to_peak - h_bend - v**2/(2*g)
            h_vac = p_atm - p_peak
            h_vac_grid[i, j] = h_vac

    # 打印设计表
    print("\n【真空度设计表 (m)】")
    header = "H_peak \\ D"
    print(f"  {header:<10}", end="")
    for D in D_array:
        print(f"{D:>8.1f}", end="")
    print()

    for i, H_peak in enumerate(H_peak_array):
        print(f"  {H_peak:<10.0f}", end="")
        for j in range(len(D_array)):
            h_vac = h_vac_grid[i, j]
            if h_vac < 7.0:
                print(f"{h_vac:>8.2f}", end="")
            else:
                print(f"{h_vac:>7.2f}*", end="")  # 超标标记
        print()

    print("\n  注：* 表示真空度超过7m（不安全）")

    # 绘图
    fig, ax = plt.subplots(figsize=(10, 8))

    # 等值线图
    contour = ax.contourf(D_grid, H_peak_grid, h_vac_grid,
                         levels=np.linspace(2, 10, 17),
                         cmap='RdYlGn_r')

    # 添加等值线
    contour_lines = ax.contour(D_grid, H_peak_grid, h_vac_grid,
                               levels=[5, 6, 7, 8, 9],
                               colors='black', linewidths=1.5, alpha=0.5)
    ax.clabel(contour_lines, inline=True, fontsize=10, fmt='%.1f m')

    # 标记7m等值线（安全边界）
    safety_line = ax.contour(D_grid, H_peak_grid, h_vac_grid,
                             levels=[7.0],
                             colors='red', linewidths=3)
    ax.clabel(safety_line, inline=True, fontsize=12, fmt='安全界限 %.0f m')

    # 色标
    cbar = plt.colorbar(contour, ax=ax)
    cbar.set_label('真空度 (m)', fontsize=11)

    # 标注安全区和危险区
    ax.text(0.95, 47.5, '安全区', fontsize=14, color='green',
           bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    ax.text(0.65, 50.5, '危险区', fontsize=14, color='red',
           bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    ax.set_xlabel('管径 D (m)', fontsize=11)
    ax.set_ylabel('峰顶高程 H_peak (m)', fontsize=11)
    ax.set_title(f'虹吸管设计优化图 (Q={Q} m³/s)', fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('demo4_design_optimization.png', dpi=300, bbox_inches='tight')
    print(f"\n  ✓ 图形已保存：demo4_design_optimization.png")
    plt.close()

    # 推荐设计
    print("\n【设计建议】")
    safe_combinations = np.sum(h_vac_grid < 7.0)
    total_combinations = h_vac_grid.size
    print_param("安全方案数", safe_combinations, "")
    print_param("总方案数", total_combinations, "")
    print_param("安全率", safe_combinations/total_combinations*100, "%")

    print("\n  推荐组合：")
    print("  1. D ≥ 0.8 m，H_peak ≤ 49 m（最经济）")
    print("  2. D ≥ 0.9 m，H_peak ≤ 50 m（适中）")
    print("  3. D ≥ 1.0 m，任意H_peak（最保守）")


# ========== 主函数 ==========

def main():
    """主函数"""
    print("\n" + "="*70)
    print("  案例24：虹吸与倒虹吸设计")
    print("="*70)

    # 运行所有演示
    demo1_inverted_siphon()
    demo2_siphon_vacuum()
    demo3_flow_rate_effect()
    demo4_design_optimization()

    print("\n" + "="*70)
    print("  所有演示完成！")
    print("  生成文件：")
    print("    - demo1_inverted_siphon.png")
    print("    - demo2_siphon_vacuum.png")
    print("    - demo3_flow_rate_effect.png")
    print("    - demo4_design_optimization.png")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
