"""
案例3：前馈-反馈复合控制

实现内容：
1. 前馈控制器（扰动补偿）
2. 反馈控制器（PID）
3. 复合控制系统（前馈+反馈）
4. 4个演示实验

作者：Claude
日期：2025-10-30
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

# 配置中文字体
rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False


# ============================================================================
# 从案例1/2复用的类定义
# ============================================================================

class CanalReach:
    """渠道段物理模型（支持侧向入流）"""

    def __init__(self, length, width, slope, roughness, n_nodes=21):
        self.L = length
        self.B = width
        self.i0 = slope
        self.n = roughness
        self.N = n_nodes

        self.dx = length / (n_nodes - 1)
        self.x = np.linspace(0, length, n_nodes)
        self.g = 9.81

        self.h = np.zeros(n_nodes)
        self.Q = np.zeros(n_nodes)
        self.q_lat = np.zeros(n_nodes)  # 侧向入流 [m³/s/m]

        self.Q_upstream = 10.0
        self.h_downstream = 2.0

        self.initialize_uniform_flow(h0=1.8, Q0=10.0)

    def initialize_uniform_flow(self, h0, Q0):
        self.h[:] = h0
        self.Q[:] = Q0

    def set_lateral_inflow(self, q_lateral_array):
        """
        设置侧向入流分布

        Parameters:
        -----------
        q_lateral_array : array-like
            每个节点的侧向入流 [m³/s/m]
        """
        self.q_lat = np.array(q_lateral_array)

    def set_point_source(self, x_location, q_discharge):
        """
        在指定位置设置点源扰动

        Parameters:
        -----------
        x_location : float
            扰动位置 [m]
        q_discharge : float
            扰动流量 [m³/s]
        """
        # 找到最近的节点
        idx = np.argmin(np.abs(self.x - x_location))
        # 转换为单位长度流量（集中在一个节点）
        self.q_lat = np.zeros(self.N)
        self.q_lat[idx] = q_discharge / self.dx

    def hydraulic_radius(self, h):
        A = self.B * h
        chi = self.B + 2 * h
        R = A / chi
        return R

    def friction_slope(self, h, Q):
        A = self.B * h
        R = self.hydraulic_radius(h)
        if A < 1e-6:
            return 0.0
        Sf = self.n**2 * Q**2 / (A**2 * R**(4/3))
        return Sf

    def step(self, dt):
        """时间步进（显式格式，增强数值稳定性）"""
        h = self.h.copy()
        Q = self.Q.copy()

        h_new = h.copy()
        Q_new = Q.copy()

        for i in range(1, self.N - 1):
            # 连续性方程
            dQ_dx = (Q[i+1] - Q[i-1]) / (2 * self.dx)
            q_lat_i = self.q_lat[i] if hasattr(self.q_lat, '__len__') else self.q_lat
            h_new[i] = h[i] - dt * dQ_dx / self.B + dt * q_lat_i / self.B

            # 确保水位为正且合理
            h_new[i] = np.clip(h_new[i], 0.1, 10.0)

            # 动量方程
            A_i = self.B * h[i]
            dh_dx = (h[i+1] - h[i-1]) / (2 * self.dx)
            Sf_i = self.friction_slope(h[i], Q[i])

            # 确保摩阻坡度合理
            if not np.isfinite(Sf_i):
                Sf_i = self.i0
            Sf_i = np.clip(Sf_i, 0.0, 0.1)

            dQ_dt = -self.g * A_i * (dh_dx + Sf_i - self.i0)
            Q_new[i] = Q[i] + dt * dQ_dt

            # 确保流量合理
            Q_new[i] = np.clip(Q_new[i], 0.1, 50.0)

        # 边界条件
        Q_new[0] = self.Q_upstream
        h_new[0] = h_new[1]

        h_new[-1] = h_new[-2]
        h_new[-1] = np.clip(h_new[-1], 0.1, 10.0)
        C_weir = 1.5
        Q_new[-1] = C_weir * self.B * h_new[-1]**1.5

        # 最终检查：确保所有值都是有限的
        h_new = np.nan_to_num(h_new, nan=1.0, posinf=10.0, neginf=0.1)
        Q_new = np.nan_to_num(Q_new, nan=5.0, posinf=50.0, neginf=0.1)

        self.h = h_new
        self.Q = Q_new

    def set_upstream_flow(self, Q):
        self.Q_upstream = Q

    def get_water_level_downstream(self):
        return self.h[-1]


class GateModel:
    """闸门模型（从案例1复用）"""

    def __init__(self, width, Cd=0.6):
        self.B = width
        self.Cd = Cd

    def compute_flow(self, gate_opening):
        """
        计算闸门流量

        Parameters:
        -----------
        gate_opening : float
            闸门开度 [m]，范围 [0.1, 1.0]

        Returns:
        --------
        Q : float
            流量 [m³/s]
        """
        a = gate_opening
        h_upstream = 2.0  # 假设上游水位恒定
        v = self.Cd * np.sqrt(2 * 9.81 * h_upstream)
        Q = self.B * a * v
        return Q


class PIDController:
    """PID控制器（基础版本，用于纯反馈）"""

    def __init__(self, Kp, Ki, Kd, dt, u_min=0.1, u_max=1.0):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.dt = dt

        self.u_min = u_min
        self.u_max = u_max

        self.integral = 0.0
        self.error_prev = 0.0

        # 记录
        self.error_history = []
        self.control_history = []

    def compute(self, target, measurement):
        """
        计算PID控制量

        Parameters:
        -----------
        target : float
            目标值
        measurement : float
            测量值

        Returns:
        --------
        u : float
            控制量
        """
        error = target - measurement

        # PID控制律
        self.integral += error * self.dt
        derivative = (error - self.error_prev) / self.dt

        u_raw = self.Kp * error + self.Ki * self.integral + self.Kd * derivative

        # 限幅
        u = np.clip(u_raw, self.u_min, self.u_max)

        # 抗积分饱和
        if u_raw != u:
            self.integral -= error * self.dt

        # 更新状态
        self.error_prev = error

        # 记录
        self.error_history.append(error)
        self.control_history.append(u)

        return u

    def reset(self):
        """重置控制器"""
        self.integral = 0.0
        self.error_prev = 0.0
        self.error_history = []
        self.control_history = []


# ============================================================================
# Part 1: 前馈-反馈复合控制器
# ============================================================================

class FeedforwardFeedbackController:
    """
    前馈-反馈复合控制器

    u_total = u_ff + u_fb

    u_ff = K_ff * q_disturbance  (前馈补偿)
    u_fb = PID(error)             (反馈修正)
    """

    def __init__(self, Kp, Ki, Kd, K_ff, dt, u_min=0.1, u_max=1.0):
        """
        Parameters:
        -----------
        Kp, Ki, Kd : float
            PID参数（反馈部分）
        K_ff : float
            前馈增益
        dt : float
            采样周期 [s]
        u_min, u_max : float
            控制量限幅
        """
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.K_ff = K_ff
        self.dt = dt

        self.u_min = u_min
        self.u_max = u_max

        # PID状态
        self.integral = 0.0
        self.error_prev = 0.0

        # 记录
        self.error_history = []
        self.control_history = []
        self.feedforward_history = []
        self.feedback_history = []

    def compute(self, h_target, h_measured, q_disturbance):
        """
        计算复合控制量

        Parameters:
        -----------
        h_target : float
            目标水位 [m]
        h_measured : float
            测量水位 [m]
        q_disturbance : float
            侧向入流扰动 [m³/s]

        Returns:
        --------
        u_total : float
            总控制量（闸门开度）[m]
        u_ff : float
            前馈部分
        u_fb : float
            反馈部分
        """
        # 前馈控制（扰动补偿）
        # 物理意义：侧向入流需要增加上游流量来补偿
        # 这里K_ff将扰动流量转换为闸门开度增量
        u_ff = self.K_ff * q_disturbance

        # 反馈控制（PID）
        error = h_target - h_measured
        self.integral += error * self.dt
        derivative = (error - self.error_prev) / self.dt

        u_fb = self.Kp * error + self.Ki * self.integral + self.Kd * derivative

        # 复合控制
        u_total = u_ff + u_fb

        # 限幅
        u_total_saturated = np.clip(u_total, self.u_min, self.u_max)

        # 抗积分饱和
        if u_total_saturated != u_total:
            self.integral -= error * self.dt

        # 更新状态
        self.error_prev = error

        # 记录
        self.error_history.append(error)
        self.control_history.append(u_total_saturated)
        self.feedforward_history.append(u_ff)
        self.feedback_history.append(u_fb)

        return u_total_saturated, u_ff, u_fb

    def reset(self):
        """重置控制器"""
        self.integral = 0.0
        self.error_prev = 0.0
        self.error_history = []
        self.control_history = []
        self.feedforward_history = []
        self.feedback_history = []


# ============================================================================
# Part 2: 扰动生成器
# ============================================================================

class DisturbanceGenerator:
    """扰动信号生成器"""

    @staticmethod
    def step(t, t_start, amplitude):
        """阶跃扰动"""
        if t >= t_start:
            return amplitude
        else:
            return 0.0

    @staticmethod
    def ramp(t, t_start, slope):
        """斜坡扰动"""
        if t >= t_start:
            return slope * (t - t_start)
        else:
            return 0.0

    @staticmethod
    def sine(t, t_start, amplitude, period):
        """正弦扰动"""
        if t >= t_start:
            return amplitude * (1 + np.sin(2 * np.pi * (t - t_start) / period))
        else:
            return 0.0


# ============================================================================
# Part 3: 闭环仿真系统
# ============================================================================

class ClosedLoopSystem:
    """闭环控制系统仿真"""

    def __init__(self, canal, gate, controller, disturbance_location=500):
        self.canal = canal
        self.gate = gate
        self.controller = controller
        self.disturbance_location = disturbance_location

        # 记录
        self.time_history = []
        self.water_level_history = []
        self.control_history = []
        self.disturbance_history = []

    def run(self, T_total, dt_control, dt_sim, h_target, disturbance_func):
        """
        运行闭环仿真

        Parameters:
        -----------
        T_total : float
            总仿真时间 [s]
        dt_control : float
            控制周期 [s]
        dt_sim : float
            仿真时间步长 [s]
        h_target : float
            目标水位 [m]
        disturbance_func : callable
            扰动函数 disturbance_func(t) -> q_disturbance

        Returns:
        --------
        time_history : list
            时间序列
        water_level_history : list
            下游水位序列
        control_history : list
            控制量序列
        disturbance_history : list
            扰动序列
        """
        t = 0
        step_count = 0

        self.time_history = []
        self.water_level_history = []
        self.control_history = []
        self.disturbance_history = []

        while t < T_total:
            # 计算当前扰动
            q_disturbance = disturbance_func(t)

            # 设置扰动到渠道
            self.canal.set_point_source(self.disturbance_location, q_disturbance)

            # 控制周期
            if step_count % int(dt_control / dt_sim) == 0:
                # 测量下游水位
                h_d = self.canal.get_water_level_downstream()

                # 控制计算
                if hasattr(self.controller, 'compute'):
                    # 检查是否是复合控制器
                    if isinstance(self.controller, FeedforwardFeedbackController):
                        u, _, _ = self.controller.compute(h_target, h_d, q_disturbance)
                    else:
                        # 纯反馈控制器（PID）
                        u = self.controller.compute(h_target, h_d)

                # 闸门执行
                Q_in = self.gate.compute_flow(u)
                self.canal.set_upstream_flow(Q_in)

            # 水力学仿真
            self.canal.step(dt_sim)

            # 记录（每60s）
            if step_count % int(60 / dt_sim) == 0:
                self.time_history.append(t)
                self.water_level_history.append(self.canal.h[-1])
                self.control_history.append(self.controller.control_history[-1] if self.controller.control_history else 0.5)
                self.disturbance_history.append(q_disturbance)

            t += dt_sim
            step_count += 1

        return self.time_history, self.water_level_history, self.control_history, self.disturbance_history


# ============================================================================
# Part 4: 性能评估
# ============================================================================

def compute_performance_indices(time, error):
    """计算性能指标"""
    if len(error) == 0 or np.all(np.isnan(error)):
        return {
            'IAE': np.nan,
            'ISE': np.nan,
            'ITAE': np.nan,
            'settling_time': np.nan,
            'max_deviation': np.nan,
            'overshoot': np.nan
        }

    dt = time[1] - time[0] if len(time) > 1 else 1.0

    # 去除NaN
    valid_mask = ~np.isnan(error)
    error_valid = error[valid_mask]
    time_valid = np.array(time)[valid_mask]

    if len(error_valid) == 0:
        return {
            'IAE': np.nan,
            'ISE': np.nan,
            'ITAE': np.nan,
            'settling_time': np.nan,
            'max_deviation': np.nan,
            'overshoot': np.nan
        }

    # 积分指标
    IAE = np.trapezoid(np.abs(error_valid), time_valid)
    ISE = np.trapezoid(error_valid**2, time_valid)
    ITAE = np.trapezoid(time_valid * np.abs(error_valid), time_valid)

    # 调节时间（进入±2%误差带）
    threshold = 0.02
    settling_idx = np.where(np.abs(error_valid) < threshold)[0]
    if len(settling_idx) > 0:
        settling_time = time_valid[settling_idx[0]]
    else:
        settling_time = time_valid[-1]

    # 最大偏差
    max_deviation = np.max(np.abs(error_valid))

    # 超调量
    overshoot = np.max(error_valid) if np.max(error_valid) > 0 else 0.0

    return {
        'IAE': IAE,
        'ISE': ISE,
        'ITAE': ITAE,
        'settling_time': settling_time,
        'max_deviation': max_deviation,
        'overshoot': overshoot
    }


# ============================================================================
# 主程序 - 4个演示场景
# ============================================================================

def main():
    print("=" * 80)
    print("案例3：前馈-反馈复合控制")
    print("=" * 80)

    # ========================================================================
    # Part 1: 控制策略对比
    # ========================================================================
    print("\n[Part 1] 控制策略对比")
    print("-" * 80)

    # 扰动函数：阶跃扰动
    def disturbance_step(t):
        return DisturbanceGenerator.step(t, t_start=300, amplitude=2.0)

    # 测试3种策略
    strategies = [
        {
            'name': '纯反馈控制',
            'Kp': 2.0, 'Ki': 0.1, 'Kd': 5.0,
            'K_ff': 0.0,  # 前馈关闭
            'type': 'feedback_only'
        },
        {
            'name': '纯前馈控制',
            'Kp': 0.0, 'Ki': 0.0, 'Kd': 0.0,
            'K_ff': 0.20,  # 只有前馈
            'type': 'feedforward_only'
        },
        {
            'name': '复合控制',
            'Kp': 2.0, 'Ki': 0.1, 'Kd': 5.0,
            'K_ff': 0.20,  # 前馈+反馈
            'type': 'composite'
        }
    ]

    results = []

    for strategy in strategies:
        print(f"\n测试策略: {strategy['name']}")

        # 初始化
        canal = CanalReach(length=1000, width=5, slope=0.001, roughness=0.025, n_nodes=21)
        gate = GateModel(width=5)

        controller = FeedforwardFeedbackController(
            Kp=strategy['Kp'],
            Ki=strategy['Ki'],
            Kd=strategy['Kd'],
            K_ff=strategy['K_ff'],
            dt=60
        )

        system = ClosedLoopSystem(canal, gate, controller, disturbance_location=500)

        # 运行仿真
        time, h_downstream, control, disturbance = system.run(
            T_total=1800,  # 30分钟
            dt_control=60,
            dt_sim=10,
            h_target=2.0,
            disturbance_func=disturbance_step
        )

        # 计算性能
        h_downstream = np.array(h_downstream)
        error = 2.0 - h_downstream
        perf = compute_performance_indices(time, error)

        print(f"  最大偏差: {perf['max_deviation']:.4f} m")
        print(f"  调节时间: {perf['settling_time']/60:.1f} min")
        print(f"  IAE: {perf['IAE']:.2f}")
        print(f"  ISE: {perf['ISE']:.2f}")

        results.append({
            'name': strategy['name'],
            'time': time,
            'h_downstream': h_downstream,
            'error': error,
            'control': control,
            'disturbance': disturbance,
            'perf': perf
        })

    # 可视化
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))

    colors = ['blue', 'green', 'red']
    linestyles = ['-', '--', '-.']

    for i, result in enumerate(results):
        # 子图1：水位响应
        axes[0].plot(np.array(result['time'])/60, result['h_downstream'],
                    color=colors[i], linestyle=linestyles[i], linewidth=2,
                    label=result['name'])

        # 子图2：控制量
        axes[1].plot(np.array(result['time'])/60, result['control'],
                    color=colors[i], linestyle=linestyles[i], linewidth=2,
                    label=result['name'])

        # 子图3：误差
        axes[2].plot(np.array(result['time'])/60, result['error'],
                    color=colors[i], linestyle=linestyles[i], linewidth=2,
                    label=result['name'])

    # 添加扰动指示
    axes[0].axvline(300/60, color='k', linestyle=':', alpha=0.5, label='扰动开始')
    axes[0].axhline(2.0, color='r', linestyle='--', alpha=0.3, label='目标水位')

    axes[0].set_ylabel('下游水位 [m]')
    axes[0].set_title('Part 1: 控制策略对比 - 水位响应')
    axes[0].legend(loc='best')
    axes[0].grid(True, alpha=0.3)

    axes[1].set_ylabel('闸门开度 [m]')
    axes[1].set_title('控制量变化')
    axes[1].legend(loc='best')
    axes[1].grid(True, alpha=0.3)

    axes[2].set_xlabel('时间 [min]')
    axes[2].set_ylabel('误差 [m]')
    axes[2].set_title('水位误差')
    axes[2].axhline(0, color='k', linestyle='-', linewidth=0.5)
    axes[2].legend(loc='best')
    axes[2].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('part1_strategy_comparison.png', dpi=150, bbox_inches='tight')
    print("\n图表已保存: part1_strategy_comparison.png")
    plt.close()

    # ========================================================================
    # Part 2: 前馈增益优化
    # ========================================================================
    print("\n[Part 2] 前馈增益优化")
    print("-" * 80)

    # 测试不同的K_ff值
    K_ff_values = [0.0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30]

    optimization_results = []

    for K_ff in K_ff_values:
        print(f"\n测试K_ff = {K_ff:.2f}")

        canal = CanalReach(length=1000, width=5, slope=0.001, roughness=0.025, n_nodes=21)
        gate = GateModel(width=5)

        controller = FeedforwardFeedbackController(
            Kp=2.0, Ki=0.1, Kd=5.0, K_ff=K_ff, dt=60
        )

        system = ClosedLoopSystem(canal, gate, controller, disturbance_location=500)

        time, h_downstream, control, disturbance = system.run(
            T_total=1800, dt_control=60, dt_sim=10,
            h_target=2.0, disturbance_func=disturbance_step
        )

        error = 2.0 - np.array(h_downstream)
        perf = compute_performance_indices(time, error)

        print(f"  IAE: {perf['IAE']:.2f}")
        print(f"  ISE: {perf['ISE']:.2f}")

        optimization_results.append({
            'K_ff': K_ff,
            'IAE': perf['IAE'],
            'ISE': perf['ISE'],
            'max_deviation': perf['max_deviation']
        })

    # 可视化优化结果
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    K_ff_array = np.array([r['K_ff'] for r in optimization_results])
    IAE_array = np.array([r['IAE'] for r in optimization_results])
    ISE_array = np.array([r['ISE'] for r in optimization_results])

    # 子图1：IAE vs K_ff
    axes[0].plot(K_ff_array, IAE_array, 'o-', linewidth=2, markersize=8, color='blue')
    axes[0].set_xlabel('前馈增益 K_ff')
    axes[0].set_ylabel('IAE')
    axes[0].set_title('Part 2: 前馈增益优化 - IAE')
    axes[0].grid(True, alpha=0.3)

    # 标注最优点
    min_idx = np.argmin(IAE_array)
    axes[0].plot(K_ff_array[min_idx], IAE_array[min_idx], 'r*', markersize=15,
                label=f'最优: K_ff={K_ff_array[min_idx]:.2f}')
    axes[0].legend()

    # 子图2：ISE vs K_ff
    axes[1].plot(K_ff_array, ISE_array, 's-', linewidth=2, markersize=8, color='green')
    axes[1].set_xlabel('前馈增益 K_ff')
    axes[1].set_ylabel('ISE')
    axes[1].set_title('ISE vs K_ff')
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('part2_gain_optimization.png', dpi=150, bbox_inches='tight')
    print("\n图表已保存: part2_gain_optimization.png")
    plt.close()

    print(f"\n最优前馈增益: K_ff* = {K_ff_array[min_idx]:.2f}")

    # ========================================================================
    # Part 3: 扰动位置影响
    # ========================================================================
    print("\n[Part 3] 扰动位置影响")
    print("-" * 80)

    disturbance_locations = [250, 500, 750]  # 不同扰动位置

    location_results = []

    for x_d in disturbance_locations:
        print(f"\n扰动位置: x = {x_d} m")

        canal = CanalReach(length=1000, width=5, slope=0.001, roughness=0.025, n_nodes=21)
        gate = GateModel(width=5)

        controller = FeedforwardFeedbackController(
            Kp=2.0, Ki=0.1, Kd=5.0, K_ff=0.20, dt=60
        )

        system = ClosedLoopSystem(canal, gate, controller, disturbance_location=x_d)

        time, h_downstream, control, disturbance = system.run(
            T_total=1800, dt_control=60, dt_sim=10,
            h_target=2.0, disturbance_func=disturbance_step
        )

        error = 2.0 - np.array(h_downstream)
        perf = compute_performance_indices(time, error)

        print(f"  最大偏差: {perf['max_deviation']:.4f} m")
        print(f"  IAE: {perf['IAE']:.2f}")

        location_results.append({
            'location': x_d,
            'time': time,
            'h_downstream': h_downstream,
            'error': error,
            'perf': perf
        })

    # 可视化
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))

    colors_loc = ['blue', 'green', 'red']

    for i, result in enumerate(location_results):
        axes[0].plot(np.array(result['time'])/60, result['h_downstream'],
                    color=colors_loc[i], linewidth=2,
                    label=f'x_d = {result["location"]} m')

        axes[1].plot(np.array(result['time'])/60, result['error'],
                    color=colors_loc[i], linewidth=2,
                    label=f'x_d = {result["location"]} m')

    axes[0].axhline(2.0, color='r', linestyle='--', alpha=0.3, label='目标')
    axes[0].axvline(300/60, color='k', linestyle=':', alpha=0.5, label='扰动开始')
    axes[0].set_ylabel('下游水位 [m]')
    axes[0].set_title('Part 3: 扰动位置影响 - 水位响应')
    axes[0].legend(loc='best')
    axes[0].grid(True, alpha=0.3)

    axes[1].set_xlabel('时间 [min]')
    axes[1].set_ylabel('误差 [m]')
    axes[1].set_title('水位误差')
    axes[1].axhline(0, color='k', linestyle='-', linewidth=0.5)
    axes[1].legend(loc='best')
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('part3_disturbance_location.png', dpi=150, bbox_inches='tight')
    print("\n图表已保存: part3_disturbance_location.png")
    plt.close()

    # ========================================================================
    # Part 4: 时变扰动响应
    # ========================================================================
    print("\n[Part 4] 时变扰动响应")
    print("-" * 80)

    # 定义3种扰动类型
    disturbance_types = [
        {
            'name': '阶跃扰动',
            'func': lambda t: DisturbanceGenerator.step(t, t_start=300, amplitude=2.0)
        },
        {
            'name': '斜坡扰动',
            'func': lambda t: DisturbanceGenerator.ramp(t, t_start=300, slope=0.005)
        },
        {
            'name': '周期扰动',
            'func': lambda t: DisturbanceGenerator.sine(t, t_start=0, amplitude=1.0, period=600)
        }
    ]

    timevarying_results = []

    for dist_type in disturbance_types:
        print(f"\n扰动类型: {dist_type['name']}")

        # 复合控制
        canal_comp = CanalReach(length=1000, width=5, slope=0.001, roughness=0.025, n_nodes=21)
        gate_comp = GateModel(width=5)
        controller_comp = FeedforwardFeedbackController(
            Kp=2.0, Ki=0.1, Kd=5.0, K_ff=0.20, dt=60
        )
        system_comp = ClosedLoopSystem(canal_comp, gate_comp, controller_comp, disturbance_location=500)

        time_comp, h_comp, control_comp, dist_comp = system_comp.run(
            T_total=1800, dt_control=60, dt_sim=10,
            h_target=2.0, disturbance_func=dist_type['func']
        )

        # 纯反馈控制（对比）
        canal_fb = CanalReach(length=1000, width=5, slope=0.001, roughness=0.025, n_nodes=21)
        gate_fb = GateModel(width=5)
        controller_fb = FeedforwardFeedbackController(
            Kp=2.0, Ki=0.1, Kd=5.0, K_ff=0.0, dt=60  # K_ff=0: 纯反馈
        )
        system_fb = ClosedLoopSystem(canal_fb, gate_fb, controller_fb, disturbance_location=500)

        time_fb, h_fb, control_fb, dist_fb = system_fb.run(
            T_total=1800, dt_control=60, dt_sim=10,
            h_target=2.0, disturbance_func=dist_type['func']
        )

        # 计算性能
        error_comp = 2.0 - np.array(h_comp)
        error_fb = 2.0 - np.array(h_fb)
        perf_comp = compute_performance_indices(time_comp, error_comp)
        perf_fb = compute_performance_indices(time_fb, error_fb)

        print(f"  复合控制 - IAE: {perf_comp['IAE']:.2f}")
        print(f"  纯反馈   - IAE: {perf_fb['IAE']:.2f}")
        print(f"  改善: {(1 - perf_comp['IAE']/perf_fb['IAE'])*100:.1f}%")

        timevarying_results.append({
            'name': dist_type['name'],
            'time': time_comp,
            'h_comp': h_comp,
            'h_fb': h_fb,
            'disturbance': dist_comp,
            'perf_comp': perf_comp,
            'perf_fb': perf_fb
        })

    # 可视化
    fig, axes = plt.subplots(3, 2, figsize=(14, 12))

    for i, result in enumerate(timevarying_results):
        # 左列：扰动信号
        axes[i, 0].plot(np.array(result['time'])/60, result['disturbance'],
                       color='purple', linewidth=2)
        axes[i, 0].set_ylabel('扰动流量 [m³/s]')
        axes[i, 0].set_title(f'{result["name"]} - 扰动信号')
        axes[i, 0].grid(True, alpha=0.3)

        # 右列：水位响应对比
        axes[i, 1].plot(np.array(result['time'])/60, result['h_comp'],
                       color='red', linewidth=2, label='复合控制')
        axes[i, 1].plot(np.array(result['time'])/60, result['h_fb'],
                       color='blue', linestyle='--', linewidth=2, label='纯反馈')
        axes[i, 1].axhline(2.0, color='k', linestyle=':', alpha=0.3, label='目标')
        axes[i, 1].set_ylabel('下游水位 [m]')
        axes[i, 1].set_title(f'{result["name"]} - 水位响应对比')
        axes[i, 1].legend(loc='best')
        axes[i, 1].grid(True, alpha=0.3)

        if i == 2:
            axes[i, 0].set_xlabel('时间 [min]')
            axes[i, 1].set_xlabel('时间 [min]')

    plt.tight_layout()
    plt.savefig('part4_time_varying_disturbance.png', dpi=150, bbox_inches='tight')
    print("\n图表已保存: part4_time_varying_disturbance.png")
    plt.close()

    # ========================================================================
    # Part 5: 性能总结
    # ========================================================================
    print("\n[Part 5] 性能总结")
    print("=" * 80)

    print("\nPart 1 - 控制策略对比:")
    print(f"{'策略':<20} {'IAE':<15} {'ISE':<15} {'最大偏差 [m]':<15}")
    print("-" * 65)
    for result in results:
        print(f"{result['name']:<20} {result['perf']['IAE']:<15.2f} "
              f"{result['perf']['ISE']:<15.2f} {result['perf']['max_deviation']:<15.4f}")

    print("\nPart 2 - 最优前馈增益:")
    print(f"K_ff* = {K_ff_array[min_idx]:.2f}")

    print("\nPart 4 - 时变扰动性能:")
    print(f"{'扰动类型':<15} {'复合IAE':<12} {'反馈IAE':<12} {'改善':<10}")
    print("-" * 50)
    for result in timevarying_results:
        improvement = (1 - result['perf_comp']['IAE']/result['perf_fb']['IAE'])*100
        print(f"{result['name']:<15} {result['perf_comp']['IAE']:<12.2f} "
              f"{result['perf_fb']['IAE']:<12.2f} {improvement:>8.1f}%")

    print("\n" + "=" * 80)
    print("案例3完成！所有4个部分的图表已保存。")
    print("=" * 80)


if __name__ == '__main__':
    main()
