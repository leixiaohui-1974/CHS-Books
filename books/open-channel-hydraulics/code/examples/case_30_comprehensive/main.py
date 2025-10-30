#!/usr/bin/env python3
"""
案例30：泵站-渠道-管道综合系统

本示例展示：
1. 泵站-渠道-管道全系统水力计算
2. 系统能量平衡分析
3. 泵站扬程校核
4. 系统效率计算
5. 综合优化设计

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
    """Manning公式计算正常水深（矩形断面）"""
    h = (Q * n / (b * S0**0.5)) ** 0.6
    for i in range(max_iter):
        A = b * h
        P = b + 2 * h
        R = A / P
        Q_calc = (1.0/n) * A * R**(2.0/3.0) * S0**0.5
        f = Q_calc - Q
        if abs(f) < tol:
            return h
        dh = 1e-6
        A_plus = b * (h + dh)
        P_plus = b + 2 * (h + dh)
        R_plus = A_plus / P_plus
        Q_plus = (1.0/n) * A_plus * R_plus**(2.0/3.0) * S0**0.5
        df = (Q_plus - Q_calc) / dh
        h = h - f / df
        h = max(0.01, h)
    return h


def darcy_friction_factor(Re, epsilon_D):
    """Colebrook-White方程求解摩阻系数"""
    if Re < 2320:
        return 64 / Re
    lambda_f = 0.25 / (np.log10(epsilon_D/3.7 + 5.74/Re**0.9))**2
    return lambda_f


def darcy_head_loss(lambda_f, L, D, v, g=9.81):
    """Darcy-Weisbach公式计算水头损失"""
    return lambda_f * (L/D) * (v**2 / (2*g))


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


# ========== 演示1：全系统水力计算 ==========

def demo1_full_system_hydraulics():
    """演示1：全系统水力计算"""
    print_header("演示1：全系统水力计算")

    # 系统参数
    Q = 1.5           # 流量 (m³/s)
    g = 9.81          # 重力加速度 (m/s²)
    rho = 1000        # 水密度 (kg/m³)

    # 水库和目标水池
    H_r = 10          # 水库水位 (m)
    H_t = 35          # 目标水池水位 (m)

    # 吸水段
    L_s = 50          # 吸水管长度 (m)
    D_s = 0.8         # 吸水管径 (m)

    # 渠道段
    L_c = 500         # 渠道长度 (m)
    b = 2.5           # 渠道宽度 (m)
    n_c = 0.020       # Manning糙率
    S0 = 0.001        # 渠底坡度

    # 管道段
    L_p = 400         # 管道长度 (m)
    D_p = 0.7         # 管径 (m)

    # 粗糙度
    epsilon = 0.0003  # 绝对粗糙度 (m)
    nu = 1.0e-6       # 运动粘度 (m²/s)

    print("\n【系统参数】")
    print(f"\n  水源与目标：")
    print_param("  水库水位 H_r", H_r, "m")
    print_param("  目标水位 H_t", H_t, "m")
    print_param("  流量 Q", Q, "m³/s")

    # 1. 吸水段计算
    A_s = np.pi * D_s**2 / 4
    v_s = Q / A_s
    Re_s = v_s * D_s / nu
    lambda_s = darcy_friction_factor(Re_s, epsilon/D_s)
    h_f_suction = darcy_head_loss(lambda_s, L_s, D_s, v_s, g) + \
                  0.5 * (v_s**2 / (2*g))  # 进口损失

    print(f"\n  吸水段：")
    print_param("  管长 L_s", L_s, "m")
    print_param("  管径 D_s", D_s, "m")
    print_param("  流速 v_s", v_s, "m/s")
    print_param("  水头损失 h_f_s", h_f_suction, "m")

    # 2. 渠道段计算
    h_n = manning_normal_depth(Q, b, n_c, S0)
    A_c = b * h_n
    v_c = Q / A_c
    h_f_channel = L_c * S0

    print(f"\n  渠道段：")
    print_param("  长度 L_c", L_c, "m")
    print_param("  宽度 b", b, "m")
    print_param("  正常水深 h_n", h_n, "m")
    print_param("  流速 v_c", v_c, "m/s")
    print_param("  水头损失 h_f_c", h_f_channel, "m")

    # 3. 管道段计算
    A_p = np.pi * D_p**2 / 4
    v_p = Q / A_p
    Re_p = v_p * D_p / nu
    lambda_p = darcy_friction_factor(Re_p, epsilon/D_p)
    h_f_pipe = darcy_head_loss(lambda_p, L_p, D_p, v_p, g) + \
               0.5 * (v_p**2 / (2*g)) + \
               1.0 * (v_p**2 / (2*g))  # 进口+出口损失

    print(f"\n  管道段：")
    print_param("  管长 L_p", L_p, "m")
    print_param("  管径 D_p", D_p, "m")
    print_param("  流速 v_p", v_p, "m/s")
    print_param("  水头损失 h_f_p", h_f_pipe, "m")

    # 4. 泵站扬程计算
    H_geo = H_t - H_r  # 几何扬程
    h_f_total = h_f_suction + h_f_channel + h_f_pipe
    H_pump_required = H_geo + h_f_total + v_p**2/(2*g)

    print(f"\n【泵站扬程】")
    print_param("几何扬程 H_geo", H_geo, "m")
    print_param("总水头损失 h_f_total", h_f_total, "m")
    print_param("出口动能 v²/2g", v_p**2/(2*g), "m")
    print_param("所需扬程 H_pump", H_pump_required, "m")

    # 5. 功率和效率
    eta_pump = 0.75   # 泵效率
    P_hydraulic = rho * g * Q * H_pump_required / 1000  # kW
    P_shaft = P_hydraulic / eta_pump
    P_motor = P_shaft / 0.95  # 电机效率95%

    print(f"\n【功率计算】")
    print_param("水功率 P_h", P_hydraulic, "kW")
    print_param("轴功率 P_shaft", P_shaft, "kW")
    print_param("电机功率 P_motor", P_motor, "kW")

    # 系统效率
    eta_system = (rho * g * Q * H_geo) / (P_motor * 1000)
    print(f"\n【系统效率】")
    print_param("泵效率", eta_pump*100, "%")
    print_param("系统效率", eta_system*100, "%")

    # 绘制系统剖面图
    fig, ax = plt.subplots(figsize=(16, 8))

    # 各段位置
    x_start = 0
    x_pump = x_start + 100
    x_channel_start = x_pump + 50
    x_channel_end = x_channel_start + L_c
    x_pipe_start = x_channel_end + 50
    x_pipe_end = x_pipe_start + L_p

    # 水库
    ax.fill_between([x_start, x_pump], [0, 0], [H_r, H_r],
                    alpha=0.3, color='lightblue', label='水库')
    ax.plot([x_start, x_pump], [H_r, H_r], 'b-', linewidth=2)

    # 吸水管
    x_suction = np.linspace(x_pump-L_s/10, x_pump, 20)
    z_suction = H_r - np.linspace(0, 2, 20)
    ax.plot(x_suction, z_suction, 'r-', linewidth=3, label='吸水管')

    # 泵站
    ax.plot(x_pump, H_r-2, 'rs', markersize=20, label='泵站')
    ax.arrow(x_pump, H_r-2, 0, H_pump_required*0.8, head_width=20,
            head_length=2, fc='red', ec='red', linewidth=2, alpha=0.7)
    ax.text(x_pump+30, H_r-2+H_pump_required*0.4, f'H_pump\n{H_pump_required:.1f}m',
           fontsize=11, fontweight='bold', ha='left')

    # 渠道
    H_channel_start = H_r - 2 + H_pump_required - h_f_suction
    x_channel = np.linspace(x_channel_start, x_channel_end, 100)
    z_channel_bed = H_channel_start - (x_channel - x_channel_start) * S0
    h_channel = h_n * np.ones_like(x_channel)
    ax.fill_between(x_channel, z_channel_bed, z_channel_bed + h_channel,
                    alpha=0.3, color='cyan', label='渠道')
    ax.plot(x_channel, z_channel_bed + h_channel, 'c-', linewidth=2)

    # 进水池
    H_pool = z_channel_bed[-1] + h_n
    ax.fill_between([x_channel_end, x_pipe_start], [H_pool-h_n, H_pool-h_n],
                    [H_pool, H_pool], alpha=0.3, color='lightgreen', label='进水池')
    ax.plot([x_channel_end, x_pipe_start], [H_pool, H_pool], 'g-', linewidth=2)

    # 压力管道
    x_pipe = np.linspace(x_pipe_start, x_pipe_end, 100)
    z_pipe = H_pool - (x_pipe - x_pipe_start) / L_p * (H_pool - H_t + 5) - 5
    ax.plot(x_pipe, z_pipe, 'm-', linewidth=3, label='压力管道')

    # 目标水池
    ax.fill_between([x_pipe_end, x_pipe_end+100], [0, 0], [H_t, H_t],
                    alpha=0.3, color='lightyellow', label='目标水池')
    ax.plot([x_pipe_end, x_pipe_end+100], [H_t, H_t], 'orange', linewidth=2)

    # 能量线
    x_energy = [x_start, x_pump, x_channel_start, x_channel_end,
                x_pipe_start, x_pipe_end]
    H_energy = [
        H_r,
        H_r - h_f_suction,
        H_r - h_f_suction + H_pump_required,
        H_r - h_f_suction + H_pump_required - h_f_channel,
        H_r - h_f_suction + H_pump_required - h_f_channel,
        H_t + v_p**2/(2*g)
    ]
    ax.plot(x_energy, H_energy, 'r--', linewidth=2, label='能量线', alpha=0.7)

    # 标注
    ax.text(x_start+50, H_r+2, f'水库\nH={H_r}m', ha='center', fontsize=10,
           bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))
    ax.text(x_pipe_end+50, H_t+2, f'目标水池\nH={H_t}m', ha='center', fontsize=10,
           bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.7))

    ax.set_xlabel('距离 (m)', fontsize=12)
    ax.set_ylabel('高程 (m)', fontsize=12)
    ax.set_title('泵站-渠道-管道综合系统剖面图', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=10, loc='upper left')
    ax.set_xlim([x_start, x_pipe_end+100])
    ax.set_ylim([0, 60])

    plt.tight_layout()
    plt.savefig('demo1_full_system_hydraulics.png', dpi=300, bbox_inches='tight')
    print(f"\n  ✓ 图形已保存：demo1_full_system_hydraulics.png")
    plt.close()

    return {
        'H_pump': H_pump_required,
        'P_motor': P_motor,
        'eta_system': eta_system
    }


# ========== 演示2：能量分配分析 ==========

def demo2_energy_distribution():
    """演示2：能量分配分析"""
    print_header("演示2：能量分配分析")

    # 从演示1获取数据（简化重新计算）
    Q = 1.5
    H_r = 10
    H_t = 35
    g = 9.81

    # 各段损失（简化计算）
    h_f_suction = 0.5
    h_f_channel = 0.5
    h_f_pipe = 2.0
    H_geo = H_t - H_r
    H_pump = H_geo + h_f_suction + h_f_channel + h_f_pipe

    print("\n【能量分配】")
    print_param("几何扬程", H_geo, "m")
    print_param("吸水损失", h_f_suction, "m")
    print_param("渠道损失", h_f_channel, "m")
    print_param("管道损失", h_f_pipe, "m")
    print_param("泵站扬程", H_pump, "m")

    # 能量分配
    components = {
        '几何扬程\n(有效能量)': H_geo,
        '吸水段损失': h_f_suction,
        '渠道段损失': h_f_channel,
        '管道段损失': h_f_pipe
    }

    # 绘图
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # 子图1：能量分配饼图
    labels = list(components.keys())
    sizes = list(components.values())
    colors = ['lightgreen', 'lightcoral', 'lightyellow', 'lightblue']
    explode = (0.1, 0, 0, 0)  # 突出几何扬程

    ax1.pie(sizes, explode=explode, labels=labels, colors=colors,
           autopct='%1.1f%%', shadow=True, startangle=90, textprops={'fontsize': 10})
    ax1.set_title(f'能量分配 (总扬程={H_pump:.1f}m)', fontsize=13, fontweight='bold')

    # 子图2：能量累积柱状图
    labels_short = ['几何扬程', '吸水损失', '渠道损失', '管道损失']
    y_positions = np.arange(len(labels_short))
    cumulative = np.cumsum([0] + sizes[:-1])

    for i, (size, cum, color) in enumerate(zip(sizes, cumulative, colors)):
        ax2.barh(y_positions[i], size, left=cum, color=color, alpha=0.7,
                edgecolor='black', linewidth=1.5, label=labels_short[i])
        # 标注数值
        ax2.text(cum + size/2, y_positions[i], f'{size:.1f}m\n({size/H_pump*100:.1f}%)',
                ha='center', va='center', fontsize=10, fontweight='bold')

    ax2.axvline(H_geo, color='green', linestyle='--', linewidth=2, alpha=0.7)
    ax2.text(H_geo, 3.3, '有效能量', fontsize=10, ha='center', color='green',
            fontweight='bold')
    ax2.axvline(H_pump, color='red', linestyle='--', linewidth=2, alpha=0.7)
    ax2.text(H_pump, 3.3, '总扬程', fontsize=10, ha='center', color='red',
            fontweight='bold')

    ax2.set_yticks(y_positions)
    ax2.set_yticklabels(labels_short)
    ax2.set_xlabel('扬程 (m)', fontsize=11)
    ax2.set_title('能量累积分析', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='x')
    ax2.set_xlim([0, H_pump*1.1])

    plt.tight_layout()
    plt.savefig('demo2_energy_distribution.png', dpi=300, bbox_inches='tight')
    print(f"\n  ✓ 图形已保存：demo2_energy_distribution.png")
    plt.close()


# ========== 演示3：不同工况分析 ==========

def demo3_operating_conditions():
    """演示3：不同工况分析"""
    print_header("演示3：不同工况分析")

    # 流量范围
    Q_array = np.linspace(0.5, 2.5, 20)

    # 固定参数
    H_r = 10
    H_t = 35
    H_geo = H_t - H_r
    g = 9.81
    rho = 1000

    # 计算不同流量下的参数
    H_pump_array = []
    P_motor_array = []
    eta_system_array = []

    print("\n【工况分析】")
    print(f"  流量范围：{Q_array[0]:.1f} ~ {Q_array[-1]:.1f} m³/s")

    for Q in Q_array:
        # 简化损失计算
        v_avg = Q / 1.0  # 假设平均断面积1m²
        h_f_total = 0.5 + 0.5 + 0.02 * v_avg**2  # 简化模型

        H_pump = H_geo + h_f_total
        H_pump_array.append(H_pump)

        # 功率
        eta_pump = 0.75
        P_motor = rho * g * Q * H_pump / (1000 * eta_pump * 0.95)
        P_motor_array.append(P_motor)

        # 系统效率
        eta_system = (rho * g * Q * H_geo) / (P_motor * 1000)
        eta_system_array.append(eta_system)

    H_pump_array = np.array(H_pump_array)
    P_motor_array = np.array(P_motor_array)
    eta_system_array = np.array(eta_system_array)

    # 设计工况点
    Q_design = 1.5
    i_design = np.argmin(np.abs(Q_array - Q_design))

    print_param("设计流量", Q_design, "m³/s")
    print_param("设计扬程", H_pump_array[i_design], "m")
    print_param("设计功率", P_motor_array[i_design], "kW")
    print_param("设计效率", eta_system_array[i_design]*100, "%")

    # 绘图
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 12))

    # 子图1：扬程-流量曲线
    ax1.plot(Q_array, H_pump_array, 'b-', linewidth=2, label='所需扬程')
    ax1.plot(Q_design, H_pump_array[i_design], 'ro', markersize=12,
            label='设计工况')
    ax1.axhline(H_geo, color='green', linestyle='--', linewidth=2,
               alpha=0.5, label='几何扬程')
    ax1.fill_between(Q_array, H_geo, H_pump_array, alpha=0.2, color='blue')
    ax1.set_xlabel('流量 Q (m³/s)', fontsize=11)
    ax1.set_ylabel('扬程 H (m)', fontsize=11)
    ax1.set_title('扬程-流量特性', fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=10)

    # 子图2：功率-流量曲线
    ax2.plot(Q_array, P_motor_array, 'r-', linewidth=2, label='电机功率')
    ax2.plot(Q_design, P_motor_array[i_design], 'ro', markersize=12,
            label='设计工况')
    ax2.fill_between(Q_array, 0, P_motor_array, alpha=0.2, color='red')
    ax2.set_xlabel('流量 Q (m³/s)', fontsize=11)
    ax2.set_ylabel('功率 P (kW)', fontsize=11)
    ax2.set_title('功率-流量特性', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend(fontsize=10)

    # 子图3：效率-流量曲线
    ax3.plot(Q_array, eta_system_array*100, 'g-', linewidth=2,
            label='系统效率')
    ax3.plot(Q_design, eta_system_array[i_design]*100, 'ro', markersize=12,
            label='设计工况')
    ax3.axhline(60, color='orange', linestyle='--', linewidth=2,
               alpha=0.5, label='目标效率60%')
    ax3.fill_between(Q_array, 0, eta_system_array*100, alpha=0.2, color='green')
    ax3.set_xlabel('流量 Q (m³/s)', fontsize=11)
    ax3.set_ylabel('效率 η (%)', fontsize=11)
    ax3.set_title('效率-流量特性', fontsize=13, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    ax3.legend(fontsize=10)
    ax3.set_ylim([0, 100])

    # 子图4：综合性能图
    ax4_twin1 = ax4.twinx()
    ax4_twin2 = ax4.twinx()
    ax4_twin2.spines['right'].set_position(('outward', 60))

    p1 = ax4.plot(Q_array, H_pump_array, 'b-', linewidth=2, label='扬程')
    p2 = ax4_twin1.plot(Q_array, P_motor_array, 'r-', linewidth=2, label='功率')
    p3 = ax4_twin2.plot(Q_array, eta_system_array*100, 'g-', linewidth=2,
                        label='效率')

    ax4.plot(Q_design, H_pump_array[i_design], 'ko', markersize=10)
    ax4.axvline(Q_design, color='k', linestyle=':', linewidth=1.5, alpha=0.5)

    ax4.set_xlabel('流量 Q (m³/s)', fontsize=11)
    ax4.set_ylabel('扬程 H (m)', fontsize=11, color='b')
    ax4_twin1.set_ylabel('功率 P (kW)', fontsize=11, color='r')
    ax4_twin2.set_ylabel('效率 η (%)', fontsize=11, color='g')

    ax4.tick_params(axis='y', labelcolor='b')
    ax4_twin1.tick_params(axis='y', labelcolor='r')
    ax4_twin2.tick_params(axis='y', labelcolor='g')

    ax4.set_title('综合性能曲线', fontsize=13, fontweight='bold')
    ax4.grid(True, alpha=0.3)

    # 合并图例
    lines = p1 + p2 + p3
    labels = [l.get_label() for l in lines]
    ax4.legend(lines, labels, fontsize=10, loc='upper left')

    plt.tight_layout()
    plt.savefig('demo3_operating_conditions.png', dpi=300, bbox_inches='tight')
    print(f"\n  ✓ 图形已保存：demo3_operating_conditions.png")
    plt.close()


# ========== 演示4：优化设计建议 ==========

def demo4_optimization_recommendations():
    """演示4：优化设计建议"""
    print_header("演示4：优化设计建议")

    # 优化方案对比
    scenarios = {
        '方案1\n(基准)': {'S0': 0.001, 'D_p': 0.7, 'H_pump': 28.0, 'cost': 1.0},
        '方案2\n(增大坡度)': {'S0': 0.002, 'D_p': 0.7, 'H_pump': 27.5, 'cost': 1.2},
        '方案3\n(增大管径)': {'S0': 0.001, 'D_p': 0.9, 'H_pump': 27.0, 'cost': 1.15},
        '方案4\n(综合优化)': {'S0': 0.0015, 'D_p': 0.8, 'H_pump': 27.2, 'cost': 1.08},
    }

    print("\n【优化方案对比】")
    print(f"  {'方案':<18} {'S0':<10} {'D_p (m)':<10} {'H_pump (m)':<12} {'相对成本':<12}")
    print("  " + "-"*65)

    for name, params in scenarios.items():
        name_clean = name.replace('\n', '')
        print(f"  {name_clean:<18} {params['S0']:<10.4f} {params['D_p']:<10.1f} "
              f"{params['H_pump']:<12.1f} {params['cost']:<12.2f}")

    # 绘图
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(16, 5))

    names = list(scenarios.keys())
    H_pumps = [scenarios[n]['H_pump'] for n in names]
    costs = [scenarios[n]['cost'] for n in names]
    colors = ['blue', 'green', 'orange', 'red']

    # 子图1：扬程对比
    bars1 = ax1.bar(range(len(names)), H_pumps, color=colors, alpha=0.7,
                   edgecolor='black', linewidth=1.5)
    for i, (bar, val) in enumerate(zip(bars1, H_pumps)):
        ax1.text(bar.get_x() + bar.get_width()/2, val + 0.2,
                f'{val:.1f} m', ha='center', va='bottom', fontsize=10,
                fontweight='bold')

    ax1.set_ylabel('泵站扬程 (m)', fontsize=11)
    ax1.set_title('扬程对比', fontsize=13, fontweight='bold')
    ax1.set_xticks(range(len(names)))
    ax1.set_xticklabels(names, rotation=0, fontsize=9)
    ax1.grid(True, alpha=0.3, axis='y')
    ax1.set_ylim([26, 29])

    # 子图2：成本对比
    bars2 = ax2.bar(range(len(names)), costs, color=colors, alpha=0.7,
                   edgecolor='black', linewidth=1.5)
    for i, (bar, val) in enumerate(zip(bars2, costs)):
        ax2.text(bar.get_x() + bar.get_width()/2, val + 0.02,
                f'{val:.2f}', ha='center', va='bottom', fontsize=10,
                fontweight='bold')

    ax2.set_ylabel('相对成本', fontsize=11)
    ax2.set_title('成本对比', fontsize=13, fontweight='bold')
    ax2.set_xticks(range(len(names)))
    ax2.set_xticklabels(names, rotation=0, fontsize=9)
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.set_ylim([0.9, 1.3])

    # 子图3：综合评价雷达图
    categories = ['扬程\n(低越好)', '成本\n(低越好)', '可靠性', '施工难度\n(低越好)']
    N = len(categories)

    # 归一化评分（0-1，越高越好）
    scores = {
        '方案1\n(基准)': [0.7, 1.0, 0.8, 1.0],
        '方案2\n(增大坡度)': [0.8, 0.7, 0.7, 0.6],
        '方案3\n(增大管径)': [0.9, 0.8, 0.9, 0.9],
        '方案4\n(综合优化)': [0.85, 0.9, 0.85, 0.85],
    }

    angles = np.linspace(0, 2*np.pi, N, endpoint=False).tolist()
    angles += angles[:1]

    ax3 = plt.subplot(133, projection='polar')

    for i, (name, score) in enumerate(scores.items()):
        score += score[:1]
        ax3.plot(angles, score, 'o-', linewidth=2, label=name.replace('\n', ''),
                color=colors[i])
        ax3.fill(angles, score, alpha=0.15, color=colors[i])

    ax3.set_xticks(angles[:-1])
    ax3.set_xticklabels(categories, fontsize=9)
    ax3.set_ylim(0, 1)
    ax3.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax3.set_yticklabels(['0.2', '0.4', '0.6', '0.8', '1.0'], fontsize=8)
    ax3.set_title('综合评价雷达图', fontsize=13, fontweight='bold', pad=20)
    ax3.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0), fontsize=9)
    ax3.grid(True)

    plt.tight_layout()
    plt.savefig('demo4_optimization_recommendations.png', dpi=300, bbox_inches='tight')
    print(f"\n  ✓ 图形已保存：demo4_optimization_recommendations.png")
    plt.close()

    # 最终建议
    print("\n【最终设计建议】")
    print("\n  推荐方案：方案4（综合优化）")
    print("    • 渠道坡度：S0 = 0.0015")
    print("    • 管道管径：D = 0.8 m")
    print("    • 泵站扬程：H = 27.2 m")
    print("    • 综合评价：扬程适中，成本合理，可靠性好")
    print("\n  设计要点：")
    print("    1. 泵站选型：Q = 1.5 m³/s，H = 28 m（留10%余量）")
    print("    2. 渠道设计：矩形断面 b×h = 2.5×1.5 m")
    print("    3. 管道材料：钢筋混凝土管或PE管")
    print("    4. 过渡段：设置进水池，留0.5m安全余量")
    print("    5. 监控系统：流量计、压力表、水位计")


# ========== 主函数 ==========

def main():
    """主函数"""
    print("\n" + "="*70)
    print("  案例30：泵站-渠道-管道综合系统")
    print("="*70)

    # 运行所有演示
    demo1_full_system_hydraulics()
    demo2_energy_distribution()
    demo3_operating_conditions()
    demo4_optimization_recommendations()

    print("\n" + "="*70)
    print("  所有演示完成！")
    print("  生成文件：")
    print("    - demo1_full_system_hydraulics.png")
    print("    - demo2_energy_distribution.png")
    print("    - demo3_operating_conditions.png")
    print("    - demo4_optimization_recommendations.png")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
