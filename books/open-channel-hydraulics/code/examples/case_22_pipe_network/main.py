"""
案例22：管网平衡计算与可视化（Hardy-Cross方法）

问题描述：
某城市供水管网，包含一个环路，已知：
- 管道1：L1=500m, D1=200mm, λ1=0.020
- 管道2：L2=400m, D2=150mm, λ2=0.022
- 管道3：L3=600m, D3=200mm, λ3=0.020
- 管道4：L4=300m, D4=150mm, λ4=0.022
- 进水流量：Q_in = 0.08 m³/s (80 L/s)
- 节点需水量：q1=20 L/s, q2=30 L/s

求解：
1. 计算各管道阻力系数
2. Hardy-Cross迭代求解流量分配
3. 可视化管网拓扑和流量
4. 展示迭代收敛过程
5. 绘制水头线图

作者：CHS-Books项目
日期：2025-10-30
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
import warnings
warnings.filterwarnings('ignore', category=UserWarning)


# ==================== 管网计算函数 ====================

def pipe_resistance_coefficient(lambda_f, L, D, g=9.81):
    """计算管道阻力系数K
    h_f = K * Q²
    K = (8*λ*L) / (π²*g*D⁵)
    """
    K = (8 * lambda_f * L) / (np.pi**2 * g * D**5)
    return K


def pipe_head_loss(K, Q, n=2.0):
    """管道水头损失
    h_f = K * Q^n (考虑流向)
    """
    h_f = K * abs(Q)**n * np.sign(Q)
    return h_f


def hardy_cross_correction(pipe_flows, pipe_K_values, n=2.0):
    """Hardy-Cross流量校正量
    ΔQ = -Σh_f / (n * Σ|h_f|/Q)
    """
    h_f_sum = 0.0
    denominator = 0.0

    for i, Q in enumerate(pipe_flows):
        K = pipe_K_values[i]
        h_f = pipe_head_loss(K, Q, n)
        h_f_sum += h_f

        if abs(Q) > 1e-10:
            denominator += abs(h_f) / abs(Q)

    if abs(denominator) < 1e-10:
        return 0.0

    delta_Q = -h_f_sum / (n * denominator)
    return delta_Q


def solve_single_loop_hardy_cross(pipe_K_values, Q_initial, n=2.0,
                                  tol=1e-6, max_iter=100):
    """Hardy-Cross法求解单环管网

    Returns:
        Q_history: 每次迭代的流量历史
        delta_Q_history: 每次迭代的校正量历史
        iterations: 迭代次数
    """
    Q = np.array(Q_initial, dtype=float)
    Q_history = [Q.copy()]
    delta_Q_history = []

    for iteration in range(max_iter):
        # 计算校正量
        delta_Q = hardy_cross_correction(Q, pipe_K_values, n)
        delta_Q_history.append(delta_Q)

        # 更新流量
        Q = Q + delta_Q
        Q_history.append(Q.copy())

        # 检查收敛
        if abs(delta_Q) < tol:
            return np.array(Q_history), np.array(delta_Q_history), iteration + 1

    return np.array(Q_history), np.array(delta_Q_history), max_iter


# ==================== 可视化函数 ====================

def plot_network_topology(Q_final, pipe_lengths, pipe_diameters,
                         save_path='network_topology.png'):
    """绘制管网拓扑和流量分配"""
    fig, ax = plt.subplots(figsize=(12, 10))

    # 节点坐标（设计一个方形环路）
    nodes = {
        'A': (0, 1),      # 进水点
        '1': (1, 1),      # 节点1
        '2': (2, 1),      # 节点2
        '3': (2, 0),      # 节点3
        '4': (1, 0)       # 节点4
    }

    # 管道连接关系
    pipes = {
        'P1': ('A', '1'),  # 进水管
        'P2': ('1', '2'),  # 环路上管道
        'P3': ('2', '3'),
        'P4': ('3', '4'),
        'P5': ('4', '1'),
    }

    # 绘制节点
    for name, (x, y) in nodes.items():
        if name == 'A':
            ax.plot(x, y, 'bs', markersize=20, label='水源')
            ax.text(x-0.15, y, '水源A', fontsize=11, fontweight='bold',
                   ha='right')
        else:
            ax.plot(x, y, 'ro', markersize=15, label='节点' if name=='1' else '')
            ax.text(x, y+0.1, f'节点{name}', fontsize=10, fontweight='bold',
                   ha='center')

    # 绘制管道
    pipe_names = ['P1', 'P2', 'P3', 'P4', 'P5']
    for i, (pipe_name, (start, end)) in enumerate(pipes.items()):
        x1, y1 = nodes[start]
        x2, y2 = nodes[end]

        # 管道线
        ax.plot([x1, x2], [y1, y2], 'k-', linewidth=3, alpha=0.5)

        # 流向箭头
        Q = Q_final[i]
        if Q > 0:
            dx, dy = (x2-x1)*0.4, (y2-y1)*0.4
        else:
            dx, dy = (x1-x2)*0.4, (y1-y2)*0.4
            Q = -Q

        mid_x, mid_y = (x1+x2)/2, (y1+y2)/2
        ax.arrow(mid_x-dx/2, mid_y-dy/2, dx, dy,
                head_width=0.08, head_length=0.06,
                fc='blue', ec='blue', linewidth=2)

        # 标注流量
        offset_x = -0.15 if (x2-x1) == 0 else 0
        offset_y = 0.15 if (x2-x1) != 0 else 0
        ax.text(mid_x+offset_x, mid_y+offset_y,
               f'{pipe_name}\nQ={Q*1000:.1f}L/s\nD={pipe_diameters[i]*1000:.0f}mm',
               fontsize=9, ha='center',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

    ax.set_xlim([-0.5, 2.5])
    ax.set_ylim([-0.5, 1.5])
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.2)
    ax.legend(loc='upper left', fontsize=11)
    ax.set_title('管网拓扑与流量分配图', fontsize=14, fontweight='bold')
    ax.set_xlabel('X (相对位置)', fontsize=11)
    ax.set_ylabel('Y (相对位置)', fontsize=11)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"\n✓ 管网拓扑图已保存: {save_path}")


def plot_convergence_history(Q_history, delta_Q_history,
                            save_path='hardy_cross_convergence.png'):
    """绘制Hardy-Cross迭代收敛过程"""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

    iterations = range(len(delta_Q_history))
    n_pipes = Q_history.shape[1]

    # 子图1：各管道流量迭代历史
    colors = ['b', 'g', 'r', 'c', 'm']
    for i in range(n_pipes):
        ax1.plot(range(len(Q_history)), Q_history[:, i]*1000,
                marker='o', linewidth=2, color=colors[i],
                label=f'管道{i+1}')

    ax1.set_xlabel('迭代次数', fontsize=12)
    ax1.set_ylabel('流量 (L/s)', fontsize=12)
    ax1.set_title('Hardy-Cross迭代过程：各管道流量变化', fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='best', fontsize=11)

    # 子图2：流量校正量（对数坐标）
    ax2.semilogy(iterations, np.abs(delta_Q_history)*1000,
                'ro-', linewidth=2, markersize=8, label='流量校正量|ΔQ|')
    ax2.axhline(y=1e-3, color='g', linestyle='--', linewidth=2,
               label='收敛标准 (0.001 L/s)')

    ax2.set_xlabel('迭代次数', fontsize=12)
    ax2.set_ylabel('流量校正量 |ΔQ| (L/s, 对数坐标)', fontsize=12)
    ax2.set_title('收敛历史：流量校正量', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3, which='both')
    ax2.legend(loc='upper right', fontsize=11)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"✓ 收敛历史图已保存: {save_path}")


def plot_hydraulic_grade_line(Q_final, pipe_K_values, pipe_lengths,
                             save_path='hydraulic_grade_line.png'):
    """绘制水头线图"""
    fig, ax = plt.subplots(figsize=(12, 6))

    # 假设水源水头为30m
    H_source = 30.0

    # 计算各节点水头（沿路径A-1-2-3）
    # 节点位置（累计距离）
    distances = [0]  # 节点A
    heads = [H_source]

    # 节点A到节点1（管道1）
    h_f_1 = pipe_head_loss(pipe_K_values[0], Q_final[0])
    distances.append(pipe_lengths[0])
    heads.append(H_source - h_f_1)

    # 节点1到节点2（管道2）
    h_f_2 = pipe_head_loss(pipe_K_values[1], Q_final[1])
    distances.append(distances[-1] + pipe_lengths[1])
    heads.append(heads[-1] - h_f_2)

    # 节点2到节点3（管道3）
    h_f_3 = pipe_head_loss(pipe_K_values[2], Q_final[2])
    distances.append(distances[-1] + pipe_lengths[2])
    heads.append(heads[-1] - h_f_3)

    # 绘制水头线
    ax.plot(distances, heads, 'b-', linewidth=3, marker='o',
           markersize=10, label='水力坡降线')

    # 标注各节点
    node_names = ['水源A', '节点1', '节点2', '节点3']
    for i, (d, h, name) in enumerate(zip(distances, heads, node_names)):
        ax.text(d, h+1, f'{name}\nH={h:.2f}m',
               ha='center', fontsize=10,
               bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))

    # 标注管道损失
    for i in range(3):
        mid_d = (distances[i] + distances[i+1]) / 2
        mid_h = (heads[i] + heads[i+1]) / 2
        h_f = heads[i] - heads[i+1]
        ax.text(mid_d, mid_h-2, f'hf={h_f:.2f}m',
               ha='center', fontsize=9, color='red', fontweight='bold')

    ax.set_xlabel('管道累计长度 (m)', fontsize=12)
    ax.set_ylabel('测压管水头 (m)', fontsize=12)
    ax.set_title('水力坡降线图', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right', fontsize=11)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"✓ 水力坡降线图已保存: {save_path}")


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
    print_separator("案例22：管网平衡计算（Hardy-Cross方法）")

    # ==================== 第一步：定义问题参数 ====================
    print("\n【步骤1】管网参数")
    print("-" * 80)

    # 管道参数（长度单位m，直径单位m）
    pipe_data = {
        '管道1': {'L': 500, 'D': 0.200, 'lambda': 0.020},  # 进水管
        '管道2': {'L': 400, 'D': 0.150, 'lambda': 0.022},  # 环路上边
        '管道3': {'L': 600, 'D': 0.200, 'lambda': 0.020},  # 环路右边
        '管道4': {'L': 300, 'D': 0.150, 'lambda': 0.022},  # 环路下边
        '管道5': {'L': 400, 'D': 0.150, 'lambda': 0.022},  # 环路左边
    }

    print(f"管网配置（5根管道构成单环）：")
    print(f"{'管道':<8} {'长度(m)':<10} {'直径(mm)':<12} {'摩阻系数λ'}")
    print("-" * 60)
    for name, params in pipe_data.items():
        print(f"{name:<8} {params['L']:<10} {params['D']*1000:<12.0f} {params['lambda']}")

    # 提取参数
    pipe_lengths = np.array([p['L'] for p in pipe_data.values()])
    pipe_diameters = np.array([p['D'] for p in pipe_data.values()])
    pipe_lambdas = np.array([p['lambda'] for p in pipe_data.values()])

    # 流量参数
    Q_in = 0.080  # 进水流量 (m³/s = 80 L/s)
    q1 = 0.020    # 节点1需水量 (m³/s = 20 L/s)
    q2 = 0.030    # 节点2需水量 (m³/s = 30 L/s)

    print(f"\n流量条件：")
    print(f"  进水流量 Q_in = {Q_in*1000:.0f} L/s")
    print(f"  节点1需水量 q1 = {q1*1000:.0f} L/s")
    print(f"  节点2需水量 q2 = {q2*1000:.0f} L/s")

    # ==================== 第二步：计算阻力系数 ====================
    print("\n【步骤2】计算管道阻力系数")
    print("-" * 80)

    pipe_K = np.array([
        pipe_resistance_coefficient(lam, L, D)
        for lam, L, D in zip(pipe_lambdas, pipe_lengths, pipe_diameters)
    ])

    print(f"阻力系数 K（h_f = K×Q²）：")
    for i, K in enumerate(pipe_K):
        print(f"  管道{i+1}: K = {K:.2e} s²/m⁵")

    # ==================== 第三步：初始流量假设 ====================
    print("\n【步骤3】初始流量假设")
    print("-" * 80)

    # 简单假设：均匀分配环路流量
    # 管道1：进水管，流量为总进水量
    # 管道2-5：环路，初始假设均分
    Q_loop = Q_in - q1 - q2  # 环路总流量
    Q_initial = np.array([
        Q_in,            # 管道1
        Q_loop / 2,      # 管道2
        Q_loop / 2,      # 管道3
        Q_loop / 2,      # 管道4
        -Q_loop / 2,     # 管道5（逆向）
    ])

    print(f"初始流量假设（基于流量平衡粗估）：")
    for i, Q in enumerate(Q_initial):
        print(f"  管道{i+1}: Q = {Q*1000:+.1f} L/s {'(逆向)' if Q<0 else ''}")

    # ==================== 第四步：Hardy-Cross迭代求解 ====================
    print("\n【步骤4】Hardy-Cross迭代求解")
    print("-" * 80)

    # 注意：这里只对环路（管道2-5）进行Hardy-Cross迭代
    # 管道1的流量由进水条件确定
    K_loop = pipe_K[1:]  # 环路管道阻力系数
    Q_loop_initial = Q_initial[1:]  # 环路初始流量

    Q_history, delta_Q_history, iterations = solve_single_loop_hardy_cross(
        K_loop, Q_loop_initial, n=2.0, tol=1e-9, max_iter=50
    )

    Q_loop_final = Q_history[-1]
    Q_final = np.array([Q_in] + list(Q_loop_final))

    print(f"Hardy-Cross迭代完成！")
    print(f"  迭代次数：{iterations}")
    print(f"  最终校正量：|ΔQ| = {abs(delta_Q_history[-1])*1000:.6f} L/s")

    print(f"\n最终流量分配：")
    print(f"{'管道':<8} {'流量(L/s)':<15} {'方向'}")
    print("-" * 40)
    for i, Q in enumerate(Q_final):
        direction = '正向' if Q > 0 else '逆向'
        print(f"管道{i+1:<7} {abs(Q)*1000:<15.2f} {direction}")

    # ==================== 第五步：验证流量平衡 ====================
    print("\n【步骤5】流量平衡验证")
    print("-" * 80)

    # 节点1流量平衡
    Q1_in = Q_final[0]  # 管道1进入
    Q1_out_2 = Q_final[1] if Q_final[1] > 0 else 0  # 管道2流出
    Q1_out_5 = -Q_final[4] if Q_final[4] < 0 else 0  # 管道5进入（负值）
    Q1_demand = q1
    balance_1 = Q1_in + Q1_out_5 - Q1_out_2 - Q1_demand

    print(f"节点1流量平衡：")
    print(f"  进入：管道1 ({Q1_in*1000:.2f} L/s) + 管道5 ({Q1_out_5*1000:.2f} L/s)")
    print(f"  流出：管道2 ({Q1_out_2*1000:.2f} L/s) + 需水 ({Q1_demand*1000:.2f} L/s)")
    print(f"  平衡差：{abs(balance_1)*1000:.6f} L/s {'✓' if abs(balance_1)<1e-6 else '✗'}")

    # 环路水头损失平衡
    h_f_loop = [pipe_head_loss(K, Q) for K, Q in zip(K_loop, Q_loop_final)]
    h_f_sum = sum(h_f_loop)

    print(f"\n环路水头损失平衡：")
    print(f"  Σh_f = {h_f_sum:.6e} m")
    print(f"  {'✓ 满足能量守恒' if abs(h_f_sum) < 1e-6 else '✗ 不满足能量守恒'}")

    # ==================== 第六步：生成可视化 ====================
    print("\n【步骤6】生成可视化图形")
    print("-" * 80)

    print("正在生成可视化图形...")

    # 图1：管网拓扑与流量分配
    plot_network_topology(Q_final, pipe_lengths, pipe_diameters,
                         'network_topology.png')

    # 图2：Hardy-Cross收敛历史
    plot_convergence_history(Q_history, delta_Q_history,
                            'hardy_cross_convergence.png')

    # 图3：水力坡降线
    plot_hydraulic_grade_line(Q_final, pipe_K, pipe_lengths,
                             'hydraulic_grade_line.png')

    # ==================== 第七步：工程建议 ====================
    print("\n【步骤7】工程分析与建议")
    print("-" * 80)

    print(f"1. 流量分配合理性：")
    for i, (Q, D) in enumerate(zip(Q_final, pipe_diameters)):
        v = abs(Q) / (np.pi * D**2 / 4)
        print(f"   管道{i+1}: 流速 v = {v:.2f} m/s", end='')
        if 0.5 <= v <= 2.0:
            print(" ✓ 合理")
        elif v < 0.5:
            print(" ⚠ 偏低，可能淤积")
        else:
            print(" ⚠ 偏高，增加损失")

    print(f"\n2. Hardy-Cross方法评价：")
    print(f"   - 迭代次数：{iterations}次")
    if iterations < 10:
        print(f"   ✓ 收敛快速，初始假设合理")
    elif iterations < 20:
        print(f"   ✓ 收敛正常")
    else:
        print(f"   ⚠ 收敛较慢，考虑优化初值")

    print(f"\n3. 管网优化建议：")
    # 检查是否有管道流速过大
    max_v = max([abs(Q) / (np.pi * D**2 / 4)
                for Q, D in zip(Q_final, pipe_diameters)])
    if max_v > 2.0:
        print(f"   - 最大流速{max_v:.2f} m/s偏高，建议增大管径")
    else:
        print(f"   ✓ 流速分布合理")

    # ==================== 完成 ====================
    print("\n" + "="*80)
    print("✓ 计算完成！所有可视化图形已保存。")
    print("="*80 + "\n")

    return {
        'Q_final': Q_final,
        'iterations': iterations,
        'pipe_K': pipe_K
    }


if __name__ == "__main__":
    results = main()
