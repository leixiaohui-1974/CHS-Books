#!/usr/bin/env python3
"""
案例29：渠道-管道耦合系统

本示例展示：
1. 明渠段水力计算（Manning公式）
2. 管道段水力计算（Darcy-Weisbach公式）
3. 过渡段分析
4. 系统优化设计

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

def manning_normal_depth(Q, b, n, S0, tol=1e-6, max_iter=100):
    """
    Manning公式计算正常水深（矩形断面）
    Q = (1/n) * A * R^(2/3) * S0^(1/2)
    """
    # 初始估计
    h = (Q * n / (b * S0**0.5)) ** 0.6

    for i in range(max_iter):
        A = b * h
        P = b + 2 * h
        R = A / P
        Q_calc = (1.0/n) * A * R**(2.0/3.0) * S0**0.5

        # 目标函数
        f = Q_calc - Q
        if abs(f) < tol:
            return h

        # 数值导数
        dh = 1e-6
        A_plus = b * (h + dh)
        P_plus = b + 2 * (h + dh)
        R_plus = A_plus / P_plus
        Q_plus = (1.0/n) * A_plus * R_plus**(2.0/3.0) * S0**0.5
        df = (Q_plus - Q_calc) / dh

        # 牛顿迭代
        h = h - f / df
        h = max(0.01, h)  # 确保正值

    return h


def darcy_friction_factor(Re, epsilon_D):
    """Colebrook-White方程求解摩阻系数"""
    if Re < 2320:
        return 64 / Re
    # Swamee-Jain显式公式
    lambda_f = 0.25 / (np.log10(epsilon_D/3.7 + 5.74/Re**0.9))**2
    return lambda_f


def darcy_head_loss(lambda_f, L, D, v, g=9.81):
    """Darcy-Weisbach公式计算水头损失"""
    h_f = lambda_f * (L/D) * (v**2 / (2*g))
    return h_f


def entrance_loss(v, xi_e=0.5, g=9.81):
    """进口损失"""
    return xi_e * (v**2 / (2*g))


def exit_loss(v, xi_o=1.0, g=9.81):
    """出口损失"""
    return xi_o * (v**2 / (2*g))


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


# ========== 演示1：渠道-管道系统分析 ==========

def demo1_channel_pipe_system():
    """演示1：渠道-管道系统分析"""
    print_header("演示1：渠道-管道系统分析")

    # 系统参数
    Q = 1.2           # 流量 (m³/s)
    # 渠道参数
    L_c = 500         # 渠道长度 (m)
    b = 2.0           # 渠道宽度 (m)
    n_c = 0.015       # Manning糙率
    S0 = 0.0005       # 渠底坡度
    # 管道参数
    L_p = 300         # 管道长度 (m)
    D = 0.8           # 管径 (m)
    epsilon = 0.0003  # 粗糙度 (m)
    nu = 1.0e-6       # 运动粘度 (m²/s)
    g = 9.81          # 重力加速度 (m/s²)

    print("\n【系统参数】")
    print_param("流量 Q", Q, "m³/s")
    print("\n  渠道段：")
    print_param("  长度 L_c", L_c, "m")
    print_param("  宽度 b", b, "m")
    print_param("  糙率 n", n_c, "")
    print_param("  坡度 S0", S0, "")
    print("\n  管道段：")
    print_param("  长度 L_p", L_p, "m")
    print_param("  管径 D", D, "m")
    print_param("  粗糙度 ε", epsilon, "m")

    # 计算渠道正常水深
    h_n = manning_normal_depth(Q, b, n_c, S0)
    A_c = b * h_n
    v_c = Q / A_c
    Fr_c = v_c / np.sqrt(g * h_n)

    print("\n【渠道水力计算】")
    print_param("正常水深 h_n", h_n, "m")
    print_param("断面积 A", A_c, "m²")
    print_param("流速 v_c", v_c, "m/s")
    print_param("Froude数 Fr", Fr_c, "")
    if Fr_c < 1:
        print("  流态：缓流")
    else:
        print("  流态：急流")

    # 计算管道水头损失
    A_p = np.pi * D**2 / 4
    v_p = Q / A_p
    Re = v_p * D / nu
    epsilon_D = epsilon / D
    lambda_f = darcy_friction_factor(Re, epsilon_D)

    h_f_entrance = entrance_loss(v_p, xi_e=0.5, g=g)
    h_f_pipe = darcy_head_loss(lambda_f, L_p, D, v_p, g)
    h_f_exit = exit_loss(v_p, xi_o=1.0, g=g)
    h_f_total = h_f_entrance + h_f_pipe + h_f_exit

    print("\n【管道水力计算】")
    print_param("断面积 A", A_p, "m²")
    print_param("流速 v_p", v_p, "m/s")
    print_param("Reynolds数 Re", Re, "")
    print_param("摩阻系数 λ", lambda_f, "")
    print_param("进口损失", h_f_entrance, "m")
    print_param("沿程损失", h_f_pipe, "m")
    print_param("出口损失", h_f_exit, "m")
    print_param("总水头损失", h_f_total, "m")

    # 过渡段分析
    print("\n【过渡段分析】")
    # 渠道末端比能
    E_c = h_n + v_c**2 / (2*g)
    print_param("渠道末端比能 E_c", E_c, "m")

    # 管道入口所需水头
    H_pool_min = h_f_total + v_p**2/(2*g)
    print_param("进水池最低水位", H_pool_min, "m")

    # 实际进水池水位
    H_pool = h_n + 0.2  # 增加0.2m安全余量
    print_param("推荐进水池水位", H_pool, "m")

    # 渠道末端到管道入口的水头线
    x_transition = np.linspace(0, 50, 100)
    h_transition = np.linspace(h_n, H_pool, 100)

    # 绘图
    fig = plt.figure(figsize=(14, 10))

    # 子图1：系统剖面图
    ax1 = plt.subplot(3, 1, 1)

    # 渠道段
    x_channel = np.array([0, L_c])
    z_channel = np.array([L_c*S0, 0])
    h_channel = np.array([h_n, h_n])
    ax1.fill_between(x_channel, z_channel, z_channel + h_channel,
                     alpha=0.3, color='blue', label='渠道')
    ax1.plot(x_channel, z_channel + h_channel, 'b-', linewidth=2)

    # 过渡段
    x_trans = np.linspace(L_c, L_c+50, 50)
    z_trans = np.zeros_like(x_trans)
    h_trans = np.linspace(h_n, H_pool, 50)
    ax1.fill_between(x_trans, z_trans, h_trans,
                     alpha=0.3, color='cyan', label='过渡段')
    ax1.plot(x_trans, h_trans, 'c-', linewidth=2)

    # 管道段
    x_pipe = np.array([L_c+50, L_c+50+L_p])
    z_pipe = np.array([0, -5])
    ax1.plot(x_pipe, z_pipe, 'r-', linewidth=3, label='管道中心线')

    ax1.axhline(0, color='k', linestyle='--', linewidth=1, alpha=0.3)
    ax1.set_xlabel('距离 (m)', fontsize=11)
    ax1.set_ylabel('高程 (m)', fontsize=11)
    ax1.set_title('渠道-管道系统剖面图', fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=10)
    ax1.set_xlim([0, L_c+50+L_p])
    ax1.set_ylim([-10, 5])

    # 子图2：流速分布
    ax2 = plt.subplot(3, 1, 2)
    x_v = [L_c/2, L_c+25, L_c+50+L_p/2]
    v_array = [v_c, (v_c+v_p)/2, v_p]
    colors = ['blue', 'cyan', 'red']
    labels = ['渠道', '过渡段', '管道']

    ax2.bar(x_v, v_array, width=[L_c*0.8, 40, L_p*0.8],
           color=colors, alpha=0.6, edgecolor='black', linewidth=1.5)

    for i, (x, v, label) in enumerate(zip(x_v, v_array, labels)):
        ax2.text(x, v+0.1, f'{v:.2f} m/s\n({label})',
                ha='center', fontsize=10, fontweight='bold')

    ax2.set_xlabel('距离 (m)', fontsize=11)
    ax2.set_ylabel('流速 (m/s)', fontsize=11)
    ax2.set_title('流速分布', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.set_xlim([0, L_c+50+L_p])

    # 子图3：水头损失分布
    ax3 = plt.subplot(3, 1, 3)

    # 沿程水头线
    x_head = []
    H_head = []

    # 渠道段（水面线）
    x_c_points = np.linspace(0, L_c, 50)
    for x in x_c_points:
        x_head.append(x)
        H_head.append(L_c*S0 - x*S0 + h_n)

    # 过渡段
    x_t_points = np.linspace(L_c, L_c+50, 20)
    H_t_points = np.linspace(h_n, H_pool, 20)
    x_head.extend(x_t_points.tolist())
    H_head.extend(H_t_points.tolist())

    # 管道段（能量线下降）
    x_p_points = np.linspace(L_c+50, L_c+50+L_p, 50)
    for i, x in enumerate(x_p_points):
        x_head.append(x)
        s_ratio = (x - (L_c+50)) / L_p
        H = H_pool - s_ratio * h_f_total
        H_head.append(H)

    ax3.plot(x_head, H_head, 'b-', linewidth=2, label='水头线')
    ax3.fill_between(x_head, 0, H_head, alpha=0.2, color='blue')

    # 标注损失
    ax3.annotate(f'渠道损失\n{L_c*S0:.2f} m',
                xy=(L_c/2, (H_head[0]+H_head[len(x_c_points)//2])/2),
                fontsize=10, ha='center',
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))

    ax3.annotate(f'管道损失\n{h_f_total:.2f} m',
                xy=(L_c+50+L_p/2, (H_pool+H_head[-1])/2),
                fontsize=10, ha='center',
                bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.7))

    ax3.axhline(0, color='k', linestyle='--', linewidth=1, alpha=0.3)
    ax3.set_xlabel('距离 (m)', fontsize=11)
    ax3.set_ylabel('水头 (m)', fontsize=11)
    ax3.set_title('水头损失分布', fontsize=13, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    ax3.legend(fontsize=10)
    ax3.set_xlim([0, L_c+50+L_p])
    ax3.set_ylim([0, 3])

    plt.tight_layout()
    plt.savefig('demo1_channel_pipe_system.png', dpi=300, bbox_inches='tight')
    print(f"\n  ✓ 图形已保存：demo1_channel_pipe_system.png")
    plt.close()


# ========== 演示2：能量平衡分析 ==========

def demo2_energy_balance():
    """演示2：能量平衡分析"""
    print_header("演示2：能量平衡分析")

    # 系统参数
    Q = 1.2
    b = 2.0
    n_c = 0.015
    S0 = 0.0005
    L_c = 500
    L_p = 300
    D = 0.8
    epsilon = 0.0003
    nu = 1.0e-6
    g = 9.81

    # 计算各段能量
    h_n = manning_normal_depth(Q, b, n_c, S0)
    v_c = Q / (b * h_n)

    A_p = np.pi * D**2 / 4
    v_p = Q / A_p
    Re = v_p * D / nu
    epsilon_D = epsilon / D
    lambda_f = darcy_friction_factor(Re, epsilon_D)

    # 渠道段损失
    h_f_channel = L_c * S0

    # 管道段损失
    h_f_entrance = entrance_loss(v_p, xi_e=0.5, g=g)
    h_f_pipe = darcy_head_loss(lambda_f, L_p, D, v_p, g)
    h_f_exit = exit_loss(v_p, xi_o=1.0, g=g)
    h_f_pipe_total = h_f_entrance + h_f_pipe + h_f_exit

    # 总损失
    h_f_total = h_f_channel + h_f_pipe_total

    print("\n【能量平衡计算】")
    print_param("渠道段损失", h_f_channel, "m")
    print_param("管道段损失", h_f_pipe_total, "m")
    print_param("总损失", h_f_total, "m")

    # 能量分配
    losses = {
        '渠道沿程': h_f_channel,
        '进口': h_f_entrance,
        '管道沿程': h_f_pipe,
        '出口': h_f_exit
    }

    # 绘图
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # 子图1：能量分配饼图
    labels = list(losses.keys())
    sizes = list(losses.values())
    colors = ['skyblue', 'lightcoral', 'lightgreen', 'gold']
    explode = (0.05, 0.05, 0.05, 0.05)

    ax1.pie(sizes, explode=explode, labels=labels, colors=colors,
           autopct='%1.1f%%', shadow=True, startangle=90)
    ax1.set_title('能量损失分配', fontsize=13, fontweight='bold')

    # 子图2：能量柱状图
    x_pos = np.arange(len(labels))
    bars = ax2.bar(x_pos, sizes, color=colors, alpha=0.7,
                   edgecolor='black', linewidth=1.5)

    for i, (bar, val) in enumerate(zip(bars, sizes)):
        ax2.text(bar.get_x() + bar.get_width()/2, val + 0.01,
                f'{val:.3f} m\n({val/h_f_total*100:.1f}%)',
                ha='center', va='bottom', fontsize=10, fontweight='bold')

    ax2.set_xlabel('损失类型', fontsize=11)
    ax2.set_ylabel('水头损失 (m)', fontsize=11)
    ax2.set_title('各项损失分析', fontsize=13, fontweight='bold')
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(labels, rotation=15, ha='right')
    ax2.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig('demo2_energy_balance.png', dpi=300, bbox_inches='tight')
    print(f"\n  ✓ 图形已保存：demo2_energy_balance.png")
    plt.close()


# ========== 演示3：管径优化 ==========

def demo3_pipe_diameter_optimization():
    """演示3：管径优化"""
    print_header("演示3：管径优化")

    # 固定参数
    Q = 1.2
    L_p = 300
    epsilon = 0.0003
    nu = 1.0e-6
    g = 9.81

    # 管径范围
    D_array = np.linspace(0.5, 1.5, 30)

    h_f_array = []
    v_array = []
    Re_array = []
    lambda_array = []

    print("\n【管径优化分析】")
    print(f"  管径范围：{D_array[0]:.1f} ~ {D_array[-1]:.1f} m")

    for D in D_array:
        A = np.pi * D**2 / 4
        v = Q / A
        Re = v * D / nu
        epsilon_D = epsilon / D
        lambda_f = darcy_friction_factor(Re, epsilon_D)

        h_f_entrance = entrance_loss(v, xi_e=0.5, g=g)
        h_f_pipe = darcy_head_loss(lambda_f, L_p, D, v, g)
        h_f_exit = exit_loss(v, xi_o=1.0, g=g)
        h_f_total = h_f_entrance + h_f_pipe + h_f_exit

        h_f_array.append(h_f_total)
        v_array.append(v)
        Re_array.append(Re)
        lambda_array.append(lambda_f)

    h_f_array = np.array(h_f_array)
    v_array = np.array(v_array)
    Re_array = np.array(Re_array)
    lambda_array = np.array(lambda_array)

    # 找到最优管径（流速在0.8~2.0 m/s范围内，损失最小）
    v_min, v_max = 0.8, 2.0
    valid_indices = np.where((v_array >= v_min) & (v_array <= v_max))[0]
    if len(valid_indices) > 0:
        i_opt = valid_indices[np.argmin(h_f_array[valid_indices])]
        D_opt = D_array[i_opt]
        h_f_opt = h_f_array[i_opt]
        v_opt = v_array[i_opt]
        print_param("最优管径 D_opt", D_opt, "m")
        print_param("对应水头损失", h_f_opt, "m")
        print_param("对应流速", v_opt, "m/s")
    else:
        print("  未找到满足流速要求的管径")

    # 绘图
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 12))

    # 子图1：水头损失vs管径
    ax1.plot(D_array, h_f_array, 'b-', linewidth=2, label='总损失')
    if len(valid_indices) > 0:
        ax1.plot(D_opt, h_f_opt, 'ro', markersize=12, label=f'最优点 D={D_opt:.2f}m')
        ax1.axvline(D_opt, color='r', linestyle='--', linewidth=1, alpha=0.5)
    ax1.set_xlabel('管径 D (m)', fontsize=11)
    ax1.set_ylabel('水头损失 (m)', fontsize=11)
    ax1.set_title('管径对水头损失的影响', fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=10)

    # 子图2：流速vs管径
    ax2.plot(D_array, v_array, 'g-', linewidth=2, label='流速')
    ax2.axhspan(v_min, v_max, alpha=0.2, color='green', label='推荐范围')
    if len(valid_indices) > 0:
        ax2.plot(D_opt, v_opt, 'ro', markersize=12, label='最优点')
    ax2.set_xlabel('管径 D (m)', fontsize=11)
    ax2.set_ylabel('流速 (m/s)', fontsize=11)
    ax2.set_title('管径对流速的影响', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend(fontsize=10)

    # 子图3：Reynolds数vs管径
    ax3.plot(D_array, Re_array, 'purple', linewidth=2)
    ax3.axhline(2320, color='r', linestyle='--', label='临界Re=2320')
    ax3.set_xlabel('管径 D (m)', fontsize=11)
    ax3.set_ylabel('Reynolds数', fontsize=11)
    ax3.set_title('管径对Reynolds数的影响', fontsize=13, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    ax3.legend(fontsize=10)
    ax3.set_yscale('log')

    # 子图4：摩阻系数vs管径
    ax4.plot(D_array, lambda_array, 'orange', linewidth=2)
    ax4.set_xlabel('管径 D (m)', fontsize=11)
    ax4.set_ylabel('摩阻系数 λ', fontsize=11)
    ax4.set_title('管径对摩阻系数的影响', fontsize=13, fontweight='bold')
    ax4.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('demo3_pipe_diameter_optimization.png', dpi=300, bbox_inches='tight')
    print(f"\n  ✓ 图形已保存：demo3_pipe_diameter_optimization.png")
    plt.close()


# ========== 演示4：设计建议 ==========

def demo4_design_recommendations():
    """演示4：设计建议"""
    print_header("演示4：设计建议")

    # 基准参数
    Q = 1.2
    L_c = 500
    b = 2.0
    n_c = 0.015
    S0_base = 0.0005
    L_p = 300
    D_base = 0.8

    # 不同设计方案
    scenarios = {
        '方案1（基准）': {'S0': 0.0005, 'D': 0.8},
        '方案2（增大坡度）': {'S0': 0.001, 'D': 0.8},
        '方案3（增大管径）': {'S0': 0.0005, 'D': 1.0},
        '方案4（综合优化）': {'S0': 0.0008, 'D': 0.9},
    }

    print("\n【设计方案对比】")
    print(f"  {'方案':<20} {'坡度S0':<12} {'管径D':<12} {'总损失':<12} {'成本系数':<12}")
    print("  " + "-"*70)

    results = {}
    for name, params in scenarios.items():
        S0 = params['S0']
        D = params['D']

        # 渠道损失
        h_f_channel = L_c * S0

        # 管道损失
        A = np.pi * D**2 / 4
        v = Q / A
        Re = v * D / 1.0e-6
        lambda_f = darcy_friction_factor(Re, 0.0003/D)
        h_f_pipe = darcy_head_loss(lambda_f, L_p, D, v) + \
                  entrance_loss(v) + exit_loss(v)

        h_f_total = h_f_channel + h_f_pipe

        # 成本系数（简化模型）
        # 成本 = 渠道开挖成本 + 管道成本
        cost_channel = L_c * S0 * 1000  # 开挖成本与坡度成正比
        cost_pipe = L_p * D**2 * 5000   # 管道成本与管径平方成正比
        cost_total = (cost_channel + cost_pipe) / 1e6  # 百万元

        results[name] = {
            'S0': S0,
            'D': D,
            'h_f': h_f_total,
            'cost': cost_total
        }

        print(f"  {name:<20} {S0:<12.4f} {D:<12.2f} "
              f"{h_f_total:<12.3f} {cost_total:<12.2f}")

    # 绘图
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # 子图1：损失对比
    names = list(results.keys())
    losses = [results[n]['h_f'] for n in names]
    colors = ['blue', 'green', 'orange', 'red']

    bars1 = ax1.bar(range(len(names)), losses, color=colors, alpha=0.7,
                   edgecolor='black', linewidth=1.5)

    for i, (bar, val) in enumerate(zip(bars1, losses)):
        ax1.text(bar.get_x() + bar.get_width()/2, val + 0.01,
                f'{val:.3f} m',
                ha='center', va='bottom', fontsize=10, fontweight='bold')

    ax1.set_xlabel('设计方案', fontsize=11)
    ax1.set_ylabel('总水头损失 (m)', fontsize=11)
    ax1.set_title('各方案水头损失对比', fontsize=13, fontweight='bold')
    ax1.set_xticks(range(len(names)))
    ax1.set_xticklabels([n.replace('方案', '') for n in names], rotation=0)
    ax1.grid(True, alpha=0.3, axis='y')

    # 子图2：成本对比
    costs = [results[n]['cost'] for n in names]
    bars2 = ax2.bar(range(len(names)), costs, color=colors, alpha=0.7,
                   edgecolor='black', linewidth=1.5)

    for i, (bar, val) in enumerate(zip(bars2, costs)):
        ax2.text(bar.get_x() + bar.get_width()/2, val + 0.01,
                f'{val:.2f} M¥',
                ha='center', va='bottom', fontsize=10, fontweight='bold')

    ax2.set_xlabel('设计方案', fontsize=11)
    ax2.set_ylabel('成本 (百万元)', fontsize=11)
    ax2.set_title('各方案成本对比', fontsize=13, fontweight='bold')
    ax2.set_xticks(range(len(names)))
    ax2.set_xticklabels([n.replace('方案', '') for n in names], rotation=0)
    ax2.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig('demo4_design_recommendations.png', dpi=300, bbox_inches='tight')
    print(f"\n  ✓ 图形已保存：demo4_design_recommendations.png")
    plt.close()

    # 推荐方案
    print("\n【推荐方案】")
    print("  综合考虑损失和成本：")
    print("  • 方案1（基准）：成本最低，但损失较大")
    print("  • 方案4（综合优化）：损失和成本平衡最好")
    print("\n  设计建议：")
    print("  1. 渠道坡度：S0 = 0.0005~0.001")
    print("  2. 管径：D = 0.8~1.0 m")
    print("  3. 进水池水位：留0.2~0.5m安全余量")
    print("  4. 过渡段长度：30~50m渐变段")


# ========== 主函数 ==========

def main():
    """主函数"""
    print("\n" + "="*70)
    print("  案例29：渠道-管道耦合系统")
    print("="*70)

    # 运行所有演示
    demo1_channel_pipe_system()
    demo2_energy_balance()
    demo3_pipe_diameter_optimization()
    demo4_design_recommendations()

    print("\n" + "="*70)
    print("  所有演示完成！")
    print("  生成文件：")
    print("    - demo1_channel_pipe_system.png")
    print("    - demo2_energy_balance.png")
    print("    - demo3_pipe_diameter_optimization.png")
    print("    - demo4_design_recommendations.png")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
