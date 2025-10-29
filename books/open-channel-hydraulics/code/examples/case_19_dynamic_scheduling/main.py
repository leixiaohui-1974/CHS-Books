"""
案例19：多闸门渠系动态调度优化 - 主程序

问题描述：
5个串联闸门控制渠道供水，根据变化的用水需求优化闸门开度。

方法：
- 基准：简单比例控制
- 优化：粒子群算法（PSO）

作者：CHS-Books项目
日期：2025-10-29
"""

import sys
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))


def print_separator(title="", width=80):
    """打印分隔线"""
    if title:
        print(f"\n{'='*width}")
        print(f"{title:^{width}}")
        print(f"{'='*width}")
    else:
        print(f"{'='*width}")


class CanalSegment:
    """渠段简化模型（集总参数模型）"""

    def __init__(self, length, width, slope, roughness, initial_depth):
        self.L = length  # m
        self.b = width  # m
        self.S0 = slope
        self.n = roughness
        self.h = initial_depth  # 平均水深
        self.Q = 0.0  # 流量

    def update(self, Q_in, Q_out, dt):
        """更新渠段状态（简化连续性方程）"""
        # 体积变化
        dV = (Q_in - Q_out) * dt
        # 面积变化
        dA = dV / self.L
        # 水深变化
        dh = dA / self.b
        self.h += dh
        self.Q = (Q_in + Q_out) / 2
        return self.h


class MultiGateCanalSystem:
    """多闸门渠系模型"""

    def __init__(self, n_gates=5, segment_length=2000, width=8.0):
        self.n_gates = n_gates
        self.L_segment = segment_length
        self.b = width
        self.S0 = 0.0003
        self.n = 0.022
        self.g = 9.81

        # 初始化渠段
        h0 = 2.5  # 初始水深
        self.segments = [CanalSegment(segment_length, width, self.S0, self.n, h0)
                        for _ in range(n_gates)]

        # 闸门开度（初始）
        self.gate_openings = np.full(n_gates, 1.5)  # m

        # 约束
        self.a_min = 0.3
        self.a_max = 3.0
        self.h_target = h0
        self.Q_upstream = 30.0  # 上游供水流量

    def gate_discharge(self, opening, h_upstream):
        """闸门流量公式（简化）"""
        Cd = 0.65
        Q = Cd * self.b * opening * np.sqrt(2 * self.g * h_upstream)
        return max(0.1, Q)  # 避免零流量

    def simulate_step(self, gate_openings, offtake_demands, dt):
        """模拟一个时间步

        Args:
            gate_openings: 5个闸门的开度 [m]
            offtake_demands: 5个取水口的需求 [m³/s]
            dt: 时间步长 [s]

        Returns:
            depths: 各渠段平均水深
            flows: 各闸门流量
            offtakes: 实际取水量
        """
        depths = []
        flows = []
        offtakes = []

        Q_in = self.Q_upstream

        for i in range(self.n_gates):
            # 闸门流量
            h_up = self.segments[i].h
            Q_gate = self.gate_discharge(gate_openings[i], h_up)

            # 取水量（不能超过可用流量）
            Q_offtake = min(offtake_demands[i], Q_gate * 0.9)

            # 下游流量
            Q_out = Q_gate - Q_offtake

            # 更新渠段
            self.segments[i].update(Q_in, Q_gate, dt)

            depths.append(self.segments[i].h)
            flows.append(Q_gate)
            offtakes.append(Q_offtake)

            # 下一段的入流
            Q_in = Q_out

        return np.array(depths), np.array(flows), np.array(offtakes)

    def simulate(self, gate_opening_schedule, demand_schedule, t_total, dt):
        """完整仿真

        Args:
            gate_opening_schedule: (N_steps, n_gates) 闸门开度时程
            demand_schedule: (N_steps, n_gates) 需求时程
            t_total: 总时间 [s]
            dt: 时间步长 [s]

        Returns:
            results: 包含depths, flows, offtakes的字典
        """
        N_steps = len(gate_opening_schedule)
        depths_history = []
        flows_history = []
        offtakes_history = []

        for step in range(N_steps):
            depths, flows, offtakes = self.simulate_step(
                gate_opening_schedule[step],
                demand_schedule[step],
                dt
            )
            depths_history.append(depths)
            flows_history.append(flows)
            offtakes_history.append(offtakes)

        return {
            'depths': np.array(depths_history),
            'flows': np.array(flows_history),
            'offtakes': np.array(offtakes_history)
        }

    def reset(self, h0=2.5):
        """重置系统状态"""
        for segment in self.segments:
            segment.h = h0
            segment.Q = 0.0


def create_demand_profile(t_hours):
    """创建变化的用水需求曲线

    Args:
        t_hours: 时间数组 [小时]

    Returns:
        demands: (N_times, 5) 各支渠需求 [m³/s]
    """
    N = len(t_hours)
    demands = np.zeros((N, 5))

    for i, t in enumerate(t_hours):
        # 支渠1-3：白天高峰（8:00-18:00对应t=2-12小时，假设开始时间为6:00）
        # 简化为：前3小时低需求，中间3小时高需求
        if t < 2:
            demands[i, 0:3] = [3.0, 4.0, 3.5]
        elif t < 4:
            demands[i, 0:3] = [8.0, 9.0, 7.5]
        else:
            demands[i, 0:3] = [4.0, 5.0, 4.5]

        # 支渠4-5：夜间灌溉（简化为：后半程需求高）
        if t < 3:
            demands[i, 3:5] = [2.0, 2.5]
        else:
            demands[i, 3:5] = [6.0, 7.0]

    return demands


def baseline_scheduling(canal_system, demand_schedule, t_total, dt):
    """基准调度方法：简单比例控制

    根据需求比例调整闸门开度
    """
    N_steps = len(demand_schedule)
    n_gates = canal_system.n_gates
    gate_schedule = np.zeros((N_steps, n_gates))

    for step in range(N_steps):
        for i in range(n_gates):
            # 简单策略：开度与需求成比例
            demand = demand_schedule[step, i]
            # a ∝ Q^0.5  (从闸门公式反推)
            a = 0.3 * np.sqrt(demand / 3.0) + 0.8
            a = np.clip(a, canal_system.a_min, canal_system.a_max)
            gate_schedule[step, i] = a

    return gate_schedule


def pso_optimization(canal_system, demand_schedule, t_total, dt,
                    n_particles=20, max_iter=50):
    """粒子群算法优化闸门调度

    Args:
        canal_system: 渠系模型
        demand_schedule: 需求时程
        t_total: 总时间
        dt: 时间步长
        n_particles: 粒子数
        max_iter: 最大迭代数

    Returns:
        best_schedule: 最优闸门开度时程
        best_cost: 最优成本
        cost_history: 成本历史
    """
    N_steps, n_gates = demand_schedule.shape
    n_vars = N_steps * n_gates  # 优化变量维度

    print(f"\nPSO优化：{n_particles}个粒子, {max_iter}次迭代")
    print(f"优化变量维度：{n_vars} ({N_steps}时间步 × {n_gates}闸门)")

    # 初始化粒子
    particles = np.random.uniform(canal_system.a_min, canal_system.a_max,
                                 (n_particles, n_vars))
    velocities = np.random.uniform(-0.1, 0.1, (n_particles, n_vars))

    # 个体最优和全局最优
    p_best = particles.copy()
    p_best_costs = np.full(n_particles, np.inf)

    g_best = particles[0].copy()
    g_best_cost = np.inf

    cost_history = []

    # PSO参数
    w = 0.7  # 惯性权重
    c1 = 1.5  # 个体学习因子
    c2 = 1.5  # 社会学习因子

    def evaluate_cost(gate_schedule_flat):
        """评估目标函数"""
        # 重塑为(N_steps, n_gates)
        gate_schedule = gate_schedule_flat.reshape(N_steps, n_gates)

        # 重置系统
        canal_system.reset()

        # 仿真
        results = canal_system.simulate(gate_schedule, demand_schedule, t_total, dt)

        # 成本计算
        depths = results['depths']
        offtakes = results['offtakes']

        # 目标1：水位偏差
        depth_errors = depths - canal_system.h_target
        J1 = np.sum(depth_errors**2)

        # 目标2：供水偏差
        supply_errors = offtakes - demand_schedule
        J2 = np.sum(supply_errors**2)

        # 目标3：操作平滑度（相邻时间步变化）
        gate_changes = np.diff(gate_schedule, axis=0)
        J3 = np.sum(gate_changes**2)

        # 加权总成本
        cost = 1.0 * J1 + 2.0 * J2 + 0.5 * J3

        # 约束惩罚（水位范围）
        penalty = 0
        h_min, h_max = 1.0, 4.0
        penalty += np.sum(np.maximum(0, h_min - depths)**2) * 1000
        penalty += np.sum(np.maximum(0, depths - h_max)**2) * 1000

        return cost + penalty

    # PSO主循环
    for iter in range(max_iter):
        # 评估所有粒子
        for i in range(n_particles):
            cost = evaluate_cost(particles[i])

            # 更新个体最优
            if cost < p_best_costs[i]:
                p_best_costs[i] = cost
                p_best[i] = particles[i].copy()

            # 更新全局最优
            if cost < g_best_cost:
                g_best_cost = cost
                g_best = particles[i].copy()

        cost_history.append(g_best_cost)

        # 更新粒子位置和速度
        r1 = np.random.rand(n_particles, n_vars)
        r2 = np.random.rand(n_particles, n_vars)

        velocities = (w * velocities +
                     c1 * r1 * (p_best - particles) +
                     c2 * r2 * (g_best - particles))

        particles = particles + velocities

        # 边界处理
        particles = np.clip(particles, canal_system.a_min, canal_system.a_max)

        if (iter + 1) % 10 == 0:
            print(f"  迭代 {iter+1}/{max_iter}: 最优成本 = {g_best_cost:.2f}")

    best_schedule = g_best.reshape(N_steps, n_gates)
    return best_schedule, g_best_cost, cost_history


def evaluate_performance(results, demand_schedule, canal_system):
    """评估调度性能"""
    depths = results['depths']
    offtakes = results['offtakes']

    # 水位RMSE
    depth_errors = depths - canal_system.h_target
    rmse_depth = np.sqrt(np.mean(depth_errors**2))

    # 供水误差
    supply_errors = offtakes - demand_schedule
    rmse_supply = np.sqrt(np.mean(supply_errors**2))

    # 供水满足率
    satisfaction = np.sum(offtakes >= demand_schedule * 0.95) / offtakes.size * 100

    # 平均水深
    mean_depth = np.mean(depths)

    return {
        'rmse_depth': rmse_depth,
        'rmse_supply': rmse_supply,
        'satisfaction': satisfaction,
        'mean_depth': mean_depth
    }


def main():
    """主函数"""
    print_separator("案例19：多闸门渠系动态调度优化")

    # ==================== 参数设置 ====================
    n_gates = 5
    t_total = 6 * 3600  # 6小时（秒）
    dt = 600  # 10分钟时间步（秒）
    N_steps = int(t_total / dt) + 1

    print(f"\n系统参数：")
    print(f"  闸门数量：{n_gates}")
    print(f"  调度周期：{t_total/3600}小时")
    print(f"  时间步长：{dt/60}分钟")
    print(f"  总步数：{N_steps}")

    # ==================== 创建系统和需求 ====================
    canal_system = MultiGateCanalSystem(n_gates=n_gates)

    t_hours = np.linspace(0, t_total/3600, N_steps)
    demand_schedule = create_demand_profile(t_hours)

    print(f"\n用水需求范围：")
    print(f"  支渠1-3：{demand_schedule[:, 0:3].min():.1f} - {demand_schedule[:, 0:3].max():.1f} m³/s")
    print(f"  支渠4-5：{demand_schedule[:, 3:5].min():.1f} - {demand_schedule[:, 3:5].max():.1f} m³/s")

    # ==================== 方法1：基准调度 ====================
    print_separator("方法1：基准调度（简单比例控制）")

    canal_system.reset()
    baseline_schedule = baseline_scheduling(canal_system, demand_schedule, t_total, dt)
    baseline_results = canal_system.simulate(baseline_schedule, demand_schedule, t_total, dt)
    baseline_perf = evaluate_performance(baseline_results, demand_schedule, canal_system)

    print(f"\n基准性能：")
    print(f"  水位RMSE：{baseline_perf['rmse_depth']:.3f} m")
    print(f"  供水RMSE：{baseline_perf['rmse_supply']:.3f} m³/s")
    print(f"  供水满足率：{baseline_perf['satisfaction']:.1f}%")

    # ==================== 方法2：PSO优化 ====================
    print_separator("方法2：粒子群算法优化")

    canal_system.reset()
    optimized_schedule, opt_cost, cost_history = pso_optimization(
        canal_system, demand_schedule, t_total, dt,
        n_particles=15, max_iter=30  # 减小规模以加快计算
    )
    optimized_results = canal_system.simulate(optimized_schedule, demand_schedule, t_total, dt)
    optimized_perf = evaluate_performance(optimized_results, demand_schedule, canal_system)

    print(f"\n优化性能：")
    print(f"  水位RMSE：{optimized_perf['rmse_depth']:.3f} m")
    print(f"  供水RMSE：{optimized_perf['rmse_supply']:.3f} m³/s")
    print(f"  供水满足率：{optimized_perf['satisfaction']:.1f}%")

    print(f"\n改善效果：")
    print(f"  水位RMSE改善：{(1 - optimized_perf['rmse_depth']/baseline_perf['rmse_depth'])*100:.1f}%")
    print(f"  供水RMSE改善：{(1 - optimized_perf['rmse_supply']/baseline_perf['rmse_supply'])*100:.1f}%")

    # ==================== 绘图 ====================
    plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False

    fig = plt.figure(figsize=(16, 12))
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

    # 图1：需求曲线
    ax1 = fig.add_subplot(gs[0, 0])
    for i in range(n_gates):
        ax1.plot(t_hours, demand_schedule[:, i], label=f'支渠{i+1}')
    ax1.set_xlabel('时间 (h)')
    ax1.set_ylabel('需求 (m³/s)')
    ax1.set_title('用水需求时程')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # 图2：基准-闸门开度
    ax2 = fig.add_subplot(gs[0, 1])
    for i in range(n_gates):
        ax2.plot(t_hours, baseline_schedule[:, i], label=f'闸门{i+1}')
    ax2.set_xlabel('时间 (h)')
    ax2.set_ylabel('开度 (m)')
    ax2.set_title('基准调度-闸门开度')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    # 图3：优化-闸门开度
    ax3 = fig.add_subplot(gs[0, 2])
    for i in range(n_gates):
        ax3.plot(t_hours, optimized_schedule[:, i], label=f'闸门{i+1}')
    ax3.set_xlabel('时间 (h)')
    ax3.set_ylabel('开度 (m)')
    ax3.set_title('优化调度-闸门开度')
    ax3.legend()
    ax3.grid(True, alpha=0.3)

    # 图4：基准-水深
    ax4 = fig.add_subplot(gs[1, 0])
    for i in range(n_gates):
        ax4.plot(t_hours, baseline_results['depths'][:, i], label=f'渠段{i+1}')
    ax4.axhline(y=canal_system.h_target, color='k', linestyle='--', label='目标')
    ax4.set_xlabel('时间 (h)')
    ax4.set_ylabel('水深 (m)')
    ax4.set_title('基准-渠段水深')
    ax4.legend()
    ax4.grid(True, alpha=0.3)

    # 图5：优化-水深
    ax5 = fig.add_subplot(gs[1, 1])
    for i in range(n_gates):
        ax5.plot(t_hours, optimized_results['depths'][:, i], label=f'渠段{i+1}')
    ax5.axhline(y=canal_system.h_target, color='k', linestyle='--', label='目标')
    ax5.set_xlabel('时间 (h)')
    ax5.set_ylabel('水深 (m)')
    ax5.set_title('优化-渠段水深')
    ax5.legend()
    ax5.grid(True, alpha=0.3)

    # 图6：水深对比（渠段3为例）
    ax6 = fig.add_subplot(gs[1, 2])
    ax6.plot(t_hours, baseline_results['depths'][:, 2], 'b-', label='基准', linewidth=2)
    ax6.plot(t_hours, optimized_results['depths'][:, 2], 'r-', label='优化', linewidth=2)
    ax6.axhline(y=canal_system.h_target, color='k', linestyle='--', label='目标')
    ax6.set_xlabel('时间 (h)')
    ax6.set_ylabel('水深 (m)')
    ax6.set_title('水深对比（渠段3）')
    ax6.legend()
    ax6.grid(True, alpha=0.3)

    # 图7：供水精度（支渠2为例）
    ax7 = fig.add_subplot(gs[2, 0])
    ax7.plot(t_hours, demand_schedule[:, 1], 'k--', label='需求', linewidth=2)
    ax7.plot(t_hours, baseline_results['offtakes'][:, 1], 'b-', label='基准供水')
    ax7.plot(t_hours, optimized_results['offtakes'][:, 1], 'r-', label='优化供水')
    ax7.set_xlabel('时间 (h)')
    ax7.set_ylabel('流量 (m³/s)')
    ax7.set_title('供水精度（支渠2）')
    ax7.legend()
    ax7.grid(True, alpha=0.3)

    # 图8：PSO收敛曲线
    ax8 = fig.add_subplot(gs[2, 1])
    ax8.plot(cost_history, 'b-', linewidth=2)
    ax8.set_xlabel('迭代次数')
    ax8.set_ylabel('成本函数值')
    ax8.set_title('PSO收敛曲线')
    ax8.grid(True, alpha=0.3)

    # 图9：性能对比
    ax9 = fig.add_subplot(gs[2, 2])
    metrics = ['水位RMSE', '供水RMSE', '满足率']
    baseline_vals = [baseline_perf['rmse_depth'], baseline_perf['rmse_supply'],
                    baseline_perf['satisfaction']/10]  # 满足率缩放
    optimized_vals = [optimized_perf['rmse_depth'], optimized_perf['rmse_supply'],
                     optimized_perf['satisfaction']/10]

    x = np.arange(len(metrics))
    width = 0.35
    ax9.bar(x - width/2, baseline_vals, width, label='基准', alpha=0.8)
    ax9.bar(x + width/2, optimized_vals, width, label='优化', alpha=0.8)
    ax9.set_ylabel('指标值')
    ax9.set_title('性能指标对比')
    ax9.set_xticks(x)
    ax9.set_xticklabels(metrics)
    ax9.legend()
    ax9.grid(True, alpha=0.3, axis='y')

    plt.suptitle('多闸门渠系动态调度优化', fontsize=16, fontweight='bold')
    plt.savefig('case_19_dynamic_scheduling.png', dpi=150, bbox_inches='tight')
    print(f"\n图形已保存：case_19_dynamic_scheduling.png")

    print("\n" + "="*80)
    print("计算完成！")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
