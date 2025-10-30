"""
案例2：多点反馈分布式PID控制

基于案例1扩展：
- 多个传感器沿程分布
- 加权反馈策略
- 传感器故障容错

功能：
- 4种加权策略对比
- 传感器数量影响分析
- 故障检测与容错
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

# 中文字体设置
rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False


# ============================================================================
# 从案例1复用的类定义
# ============================================================================

class CanalReach:
    """渠道段物理模型（从案例1复用）"""

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
        self.q_lat = np.zeros(n_nodes)

        self.Q_upstream = 10.0
        self.h_downstream = 2.0

        self.initialize_uniform_flow(h0=1.8, Q0=10.0)

    def initialize_uniform_flow(self, h0, Q0):
        self.h[:] = h0
        self.Q[:] = Q0

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
        h = self.h.copy()
        Q = self.Q.copy()

        h_new = h.copy()
        Q_new = Q.copy()

        for i in range(1, self.N - 1):
            dQ_dx = (Q[i+1] - Q[i-1]) / (2 * self.dx)
            q_lat_i = self.q_lat[i] if hasattr(self.q_lat, '__len__') else self.q_lat
            h_new[i] = h[i] - dt * dQ_dx + dt * q_lat_i / self.B

            # 确保水位为正且合理
            h_new[i] = np.clip(h_new[i], 0.1, 10.0)

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

        Q_new[0] = self.Q_upstream
        h_new[0] = h_new[1]

        h_new[-1] = h_new[-2]
        # 确保下游水位为正且合理
        h_new[-1] = np.clip(h_new[-1], 0.1, 10.0)
        C_weir = 1.5
        Q_new[-1] = C_weir * self.B * h_new[-1]**1.5

        # 最终检查：确保所有值都是有限的
        h_new = np.nan_to_num(h_new, nan=1.0, posinf=10.0, neginf=0.1)
        Q_new = np.nan_to_num(Q_new, nan=5.0, posinf=50.0, neginf=0.1)

        self.h = h_new
        self.Q = Q_new

    def get_water_level_downstream(self):
        return self.h[-1]

    def set_upstream_flow(self, Q_in):
        self.Q_upstream = Q_in

    def set_lateral_inflow(self, q_lat):
        if isinstance(q_lat, (int, float)):
            self.q_lat[:] = q_lat
        else:
            self.q_lat = q_lat


class GateModel:
    """闸门模型（从案例1复用）"""

    def __init__(self, width, discharge_coeff=0.6):
        self.B = width
        self.mu = discharge_coeff
        self.g = 9.81
        self.h_upstream = 3.0

    def compute_flow(self, u_gate):
        u = np.clip(u_gate, 0.01, 1.5)
        Q = self.mu * u * self.B * np.sqrt(2 * self.g * self.h_upstream)
        return Q


class PIDController:
    """PID控制器（从案例1复用）"""

    def __init__(self, Kp, Ki, Kd, dt, u_min=0.1, u_max=1.0):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.dt = dt
        self.u_min = u_min
        self.u_max = u_max

        self.integral = 0.0
        self.error_prev = 0.0
        self.error_history = []
        self.control_history = []

    def compute(self, target, measurement):
        error = target - measurement
        self.integral += error * self.dt
        derivative = (error - self.error_prev) / self.dt

        u_raw = self.Kp * error + self.Ki * self.integral + self.Kd * derivative
        u = np.clip(u_raw, self.u_min, self.u_max)

        if u_raw != u:
            self.integral -= error * self.dt

        self.error_prev = error
        self.error_history.append(error)
        self.control_history.append(u)

        return u

    def reset(self):
        self.integral = 0.0
        self.error_prev = 0.0
        self.error_history = []
        self.control_history = []


# ============================================================================
# Part 1: 分布式PID控制器
# ============================================================================

class DistributedPIDController:
    """
    分布式PID控制器 - 多点反馈

    加权策略：
    - uniform: 均匀权重
    - distance: 距离加权
    - exponential: 指数加权
    - adaptive: 自适应权重
    """

    def __init__(self, Kp, Ki, Kd, dt, sensor_positions, weighting_method='uniform'):
        """
        Parameters:
        -----------
        Kp, Ki, Kd : float
            PID参数
        dt : float
            采样周期 [s]
        sensor_positions : list
            传感器位置 [m]
        weighting_method : str
            加权方法
        """
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.dt = dt

        self.sensor_positions = np.array(sensor_positions)
        self.n_sensors = len(sensor_positions)
        self.weighting_method = weighting_method

        # PID状态
        self.integral = 0.0
        self.error_prev = 0.0

        # 控制量限制
        self.u_min = 0.1
        self.u_max = 1.0

        # 计算静态权重（用于uniform和distance方法）
        self.static_weights = self.compute_static_weights()

        # 记录
        self.error_history = []
        self.control_history = []
        self.weights_history = []

    def compute_static_weights(self):
        """计算静态权重"""
        L = self.sensor_positions[-1]  # 渠道总长

        if self.weighting_method == 'uniform':
            # 均匀权重
            weights = np.ones(self.n_sensors) / self.n_sensors

        elif self.weighting_method == 'distance':
            # 距离加权（下游权重大）
            distances_to_downstream = L - self.sensor_positions
            # 特殊处理：最下游传感器距离为0，给固定权重
            distances_to_downstream[-1] = L * 0.5  # 设为平均距离
            weights = distances_to_downstream / np.sum(distances_to_downstream)

        elif self.weighting_method == 'exponential':
            # 指数加权
            alpha = 0.002  # 衰减系数
            weights = np.exp(-alpha * (L - self.sensor_positions))
            weights = weights / np.sum(weights)

        else:
            # 默认均匀
            weights = np.ones(self.n_sensors) / self.n_sensors

        return weights

    def compute_adaptive_weights(self, errors):
        """计算自适应权重（基于误差）"""
        abs_errors = np.abs(errors)
        total = np.sum(abs_errors) + 1e-6  # 避免除零
        weights = abs_errors / total
        return weights

    def compute(self, target, measurements):
        """
        计算控制量

        Parameters:
        -----------
        target : float
            目标水位 [m]
        measurements : list or array
            各传感器测量值 [m]

        Returns:
        --------
        u : float
            控制量（闸门开度） [m]
        """
        # 计算各传感器误差
        errors = target - np.array(measurements)

        # 计算权重
        if self.weighting_method == 'adaptive':
            weights = self.compute_adaptive_weights(errors)
        else:
            weights = self.static_weights

        # 加权误差
        e_weighted = np.sum(weights * errors)

        # PID控制律
        self.integral += e_weighted * self.dt
        derivative = (e_weighted - self.error_prev) / self.dt

        u_raw = self.Kp * e_weighted + self.Ki * self.integral + self.Kd * derivative

        # 限幅
        u = np.clip(u_raw, self.u_min, self.u_max)

        # 抗积分饱和
        if u_raw != u:
            self.integral -= e_weighted * self.dt

        # 更新状态
        self.error_prev = e_weighted

        # 记录
        self.error_history.append(e_weighted)
        self.control_history.append(u)
        self.weights_history.append(weights.copy())

        return u

    def reset(self):
        """重置控制器"""
        self.integral = 0.0
        self.error_prev = 0.0
        self.error_history = []
        self.control_history = []
        self.weights_history = []


# ============================================================================
# Part 2: 多传感器系统
# ============================================================================

class MultiSensorSystem:
    """多传感器测量系统"""

    def __init__(self, canal, sensor_indices):
        """
        Parameters:
        -----------
        canal : CanalReach
            渠道对象
        sensor_indices : list
            传感器在节点数组中的索引
        """
        self.canal = canal
        self.sensor_indices = sensor_indices
        self.n_sensors = len(sensor_indices)

        # 传感器故障状态
        self.sensor_healthy = np.ones(self.n_sensors, dtype=bool)

        # 测量噪声水平
        self.noise_std = 0.01  # [m]

    def measure(self, add_noise=False):
        """
        测量各传感器水位

        Parameters:
        -----------
        add_noise : bool
            是否添加测量噪声

        Returns:
        --------
        measurements : array
            各传感器测量值 [m]
        """
        measurements = []

        for i, idx in enumerate(self.sensor_indices):
            if self.sensor_healthy[i]:
                # 读取水位
                h = self.canal.h[idx]

                # 添加噪声
                if add_noise:
                    h += np.random.normal(0, self.noise_std)

                measurements.append(h)
            else:
                # 传感器故障，返回NaN
                measurements.append(np.nan)

        return np.array(measurements)

    def set_sensor_fault(self, sensor_id, is_faulty):
        """设置传感器故障状态"""
        self.sensor_healthy[sensor_id] = not is_faulty

    def get_healthy_measurements(self, measurements):
        """获取健康传感器的测量值"""
        healthy_mask = ~np.isnan(measurements)
        return measurements[healthy_mask], healthy_mask


# ============================================================================
# Part 3: 闭环系统
# ============================================================================

class DistributedClosedLoopSystem:
    """分布式闭环控制系统"""

    def __init__(self, canal, gate, controller, sensor_system):
        self.canal = canal
        self.gate = gate
        self.controller = controller
        self.sensor_system = sensor_system

        # 记录
        self.time_history = []
        self.water_level_history = []
        self.measurements_history = []
        self.control_history = []

    def run(self, T_total, dt_control, dt_sim, target_level):
        """运行闭环仿真"""
        t = 0
        step_count = 0

        self.time_history = []
        self.water_level_history = []
        self.measurements_history = []
        self.control_history = []

        while t < T_total:
            # 控制周期
            if step_count % int(dt_control / dt_sim) == 0:
                # 测量
                measurements = self.sensor_system.measure(add_noise=False)

                # 处理传感器故障
                healthy_measurements, healthy_mask = self.sensor_system.get_healthy_measurements(measurements)

                if np.sum(healthy_mask) > 0:
                    # 至少有一个健康传感器
                    # 对于故障传感器，用最近的健康传感器值替代
                    measurements_filled = measurements.copy()
                    for i in range(len(measurements)):
                        if np.isnan(measurements[i]):
                            # 找最近的健康传感器
                            healthy_indices = np.where(healthy_mask)[0]
                            nearest = healthy_indices[np.argmin(np.abs(healthy_indices - i))]
                            measurements_filled[i] = measurements[nearest]

                    # 控制计算
                    if callable(target_level):
                        h_target = target_level(t)
                    else:
                        h_target = target_level

                    u_gate = self.controller.compute(h_target, measurements_filled)

                    # 闸门执行
                    Q_in = self.gate.compute_flow(u_gate)
                    self.canal.set_upstream_flow(Q_in)

            # 水力学仿真
            self.canal.step(dt_sim)

            # 记录（每60s）
            if step_count % int(60 / dt_sim) == 0:
                self.time_history.append(t)
                self.water_level_history.append(self.canal.h.copy())
                self.measurements_history.append(self.sensor_system.measure())
                self.control_history.append(self.controller.control_history[-1] if self.controller.control_history else 0.5)

            t += dt_sim
            step_count += 1

        return self.time_history, self.water_level_history, self.measurements_history


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
            'steady_state_error': np.nan
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
            'steady_state_error': np.nan
        }

    IAE = np.trapz(np.abs(error_valid), time_valid)
    ISE = np.trapz(error_valid**2, time_valid)
    ITAE = np.trapz(time_valid * np.abs(error_valid), time_valid)

    # 调节时间
    threshold = 0.02
    settling_idx = np.where(np.abs(error_valid) < threshold)[0]
    if len(settling_idx) > 0:
        settling_time = time_valid[settling_idx[0]]
    else:
        settling_time = time_valid[-1]

    # 稳态误差
    steady_state_error = np.mean(np.abs(error_valid[-int(len(error_valid)*0.1):]))

    return {
        'IAE': IAE,
        'ISE': ISE,
        'ITAE': ITAE,
        'settling_time': settling_time,
        'steady_state_error': steady_state_error
    }


# ============================================================================
# 主程序 - 5个演示场景
# ============================================================================

def main():
    print("=" * 80)
    print("案例2：多点反馈分布式PID控制")
    print("=" * 80)

    # ========================================================================
    # Part 1: 加权策略对比
    # ========================================================================
    print("\n[Part 1] 加权策略对比")
    print("-" * 80)

    # 传感器位置
    L = 1000  # 渠道长度
    sensor_positions = [250, 500, 750, 1000]  # 4个传感器
    sensor_indices = [5, 10, 15, 20]  # 对应节点索引（N=21）

    # 测试4种策略 + 单点基线
    strategies = [
        {'name': '单点反馈（基线）', 'method': 'single', 'positions': [1000], 'indices': [20]},
        {'name': '均匀权重', 'method': 'uniform', 'positions': sensor_positions, 'indices': sensor_indices},
        {'name': '距离权重', 'method': 'distance', 'positions': sensor_positions, 'indices': sensor_indices},
        {'name': '自适应权重', 'method': 'adaptive', 'positions': sensor_positions, 'indices': sensor_indices},
    ]

    results = []

    for strategy in strategies:
        print(f"\n测试策略: {strategy['name']}")

        # 初始化
        canal = CanalReach(length=1000, width=5, slope=0.001, roughness=0.025, n_nodes=21)
        gate = GateModel(width=5)

        if strategy['method'] == 'single':
            # 单点反馈（案例1）
            pid = PIDController(Kp=2.0, Ki=0.1, Kd=5.0, dt=60)

            # 简单闭环
            time = []
            h_downstream = []
            control = []
            t = 0
            step = 0
            T_total = 3600
            dt_sim = 10  # 使用dt_sim=10s满足CFL条件

            while t < T_total:
                if step % 6 == 0:  # 每60秒控制一次
                    h_d = canal.get_water_level_downstream()
                    u = pid.compute(2.0, h_d)
                    Q_in = gate.compute_flow(u)
                    canal.set_upstream_flow(Q_in)

                canal.step(dt_sim)

                if step % 6 == 0:  # 每60秒记录一次
                    time.append(t)
                    h_downstream.append(h_d)
                    control.append(u)

                t += dt_sim
                step += 1

            h_downstream = np.array(h_downstream)
            error = 2.0 - h_downstream

        else:
            # 多点反馈
            controller = DistributedPIDController(
                Kp=2.0, Ki=0.1, Kd=5.0, dt=60,
                sensor_positions=strategy['positions'],
                weighting_method=strategy['method']
            )
            sensor_system = MultiSensorSystem(canal, strategy['indices'])
            system = DistributedClosedLoopSystem(canal, gate, controller, sensor_system)

            time, _, measurements = system.run(3600, 60, 10, 2.0)  # 使用dt_sim=10s满足CFL条件

            # 提取下游水位
            h_downstream = np.array([m[-1] for m in measurements])
            error = 2.0 - h_downstream
            control = system.control_history

        # 性能评估
        perf = compute_performance_indices(time, error)

        print(f"  调节时间: {perf['settling_time']/60:.1f} min")
        print(f"  稳态误差: {perf['steady_state_error']:.4f} m")
        print(f"  IAE: {perf['IAE']:.2f}")

        results.append({
            'name': strategy['name'],
            'time': time,
            'h': h_downstream,
            'control': control,
            'perf': perf
        })

    # 可视化对比
    fig, axes = plt.subplots(2, 1, figsize=(12, 10))

    # 水位响应
    for result in results:
        axes[0].plot(np.array(result['time'])/60, result['h'],
                    linewidth=2, label=result['name'])

    axes[0].axhline(2.0, color='r', linestyle='--', alpha=0.5, label='目标水位')
    axes[0].set_xlabel('时间 [min]')
    axes[0].set_ylabel('下游水位 [m]')
    axes[0].set_title('Part 1: 不同加权策略的水位响应对比')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # 性能指标对比
    names = [r['name'] for r in results]
    settling_times = [r['perf']['settling_time']/60 for r in results]
    IAEs = [r['perf']['IAE'] for r in results]

    x = np.arange(len(names))
    width = 0.35

    ax2 = axes[1]
    ax2.bar(x - width/2, settling_times, width, label='调节时间 [min]', alpha=0.8)

    ax2_twin = ax2.twinx()
    ax2_twin.bar(x + width/2, IAEs, width, label='IAE', alpha=0.8, color='orange')

    ax2.set_xlabel('加权策略')
    ax2.set_ylabel('调节时间 [min]')
    ax2_twin.set_ylabel('IAE')
    ax2.set_title('性能指标对比')
    ax2.set_xticks(x)
    ax2.set_xticklabels(names, rotation=15, ha='right')
    ax2.legend(loc='upper left')
    ax2_twin.legend(loc='upper right')
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('part1_weighting_strategies.png', dpi=150, bbox_inches='tight')
    print("\n图表已保存: part1_weighting_strategies.png")
    plt.close()

    # ========================================================================
    # Part 2: 传感器数量影响
    # ========================================================================
    print("\n[Part 2] 传感器数量影响分析")
    print("-" * 80)

    sensor_configs = [
        {'n': 1, 'positions': [1000], 'indices': [20]},
        {'n': 2, 'positions': [500, 1000], 'indices': [10, 20]},
        {'n': 3, 'positions': [333, 667, 1000], 'indices': [7, 14, 20]},
        {'n': 4, 'positions': [250, 500, 750, 1000], 'indices': [5, 10, 15, 20]},
    ]

    results_n = []

    for config in sensor_configs:
        print(f"\n传感器数量: N={config['n']}")

        canal = CanalReach(length=1000, width=5, slope=0.001, roughness=0.025, n_nodes=21)
        gate = GateModel(width=5)

        controller = DistributedPIDController(
            Kp=2.0, Ki=0.1, Kd=5.0, dt=60,
            sensor_positions=config['positions'],
            weighting_method='distance'
        )

        sensor_system = MultiSensorSystem(canal, config['indices'])
        system = DistributedClosedLoopSystem(canal, gate, controller, sensor_system)

        time, _, measurements = system.run(3600, 60, 10, 2.0)  # 使用dt_sim=10s满足CFL条件

        h_downstream = np.array([m[-1] for m in measurements])
        error = 2.0 - h_downstream
        perf = compute_performance_indices(time, error)

        print(f"  调节时间: {perf['settling_time']/60:.1f} min")
        print(f"  IAE: {perf['IAE']:.2f}")

        results_n.append({
            'n': config['n'],
            'time': time,
            'h': h_downstream,
            'perf': perf
        })

    # 可视化
    fig, axes = plt.subplots(2, 1, figsize=(12, 10))

    # 响应曲线
    for result in results_n:
        axes[0].plot(np.array(result['time'])/60, result['h'],
                    linewidth=2, label=f"N={result['n']}")

    axes[0].axhline(2.0, color='r', linestyle='--', alpha=0.5)
    axes[0].set_xlabel('时间 [min]')
    axes[0].set_ylabel('下游水位 [m]')
    axes[0].set_title('Part 2: 传感器数量对控制性能的影响')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # 性能随传感器数量变化
    n_values = [r['n'] for r in results_n]
    settling_times = [r['perf']['settling_time']/60 for r in results_n]
    IAEs = [r['perf']['IAE'] for r in results_n]

    axes[1].plot(n_values, settling_times, 'o-', linewidth=2, markersize=8, label='调节时间')
    ax1_twin = axes[1].twinx()
    ax1_twin.plot(n_values, IAEs, 's-', linewidth=2, markersize=8, color='orange', label='IAE')

    axes[1].set_xlabel('传感器数量 N')
    axes[1].set_ylabel('调节时间 [min]')
    ax1_twin.set_ylabel('IAE')
    axes[1].set_title('性能指标 vs 传感器数量')
    axes[1].legend(loc='upper left')
    ax1_twin.legend(loc='upper right')
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('part2_sensor_number.png', dpi=150, bbox_inches='tight')
    print("\n图表已保存: part2_sensor_number.png")
    plt.close()

    # ========================================================================
    # Part 3: 权重动态变化（自适应）
    # ========================================================================
    print("\n[Part 3] 自适应权重动态变化")
    print("-" * 80)

    canal = CanalReach(length=1000, width=5, slope=0.001, roughness=0.025, n_nodes=21)
    gate = GateModel(width=5)

    controller = DistributedPIDController(
        Kp=2.0, Ki=0.1, Kd=5.0, dt=60,
        sensor_positions=[250, 500, 750, 1000],
        weighting_method='adaptive'
    )

    sensor_system = MultiSensorSystem(canal, [5, 10, 15, 20])
    system = DistributedClosedLoopSystem(canal, gate, controller, sensor_system)

    time, _, measurements = system.run(3600, 60, 10, 2.0)  # 使用dt_sim=10s满足CFL条件

    # 提取权重历史
    weights_history = np.array(controller.weights_history)

    # 可视化
    fig, axes = plt.subplots(2, 1, figsize=(12, 10))

    # 权重变化
    for i in range(4):
        axes[0].plot(np.array(time)/60, weights_history[:, i],
                    linewidth=2, label=f'传感器{i+1} (x={controller.sensor_positions[i]}m)')

    axes[0].set_xlabel('时间 [min]')
    axes[0].set_ylabel('权重系数')
    axes[0].set_title('Part 3: 自适应权重随时间的动态变化')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # 各传感器测量值
    measurements_array = np.array(measurements)
    for i in range(4):
        axes[1].plot(np.array(time)/60, measurements_array[:, i],
                    linewidth=2, label=f'传感器{i+1}')

    axes[1].axhline(2.0, color='r', linestyle='--', alpha=0.5, label='目标')
    axes[1].set_xlabel('时间 [min]')
    axes[1].set_ylabel('水位 [m]')
    axes[1].set_title('各传感器测量值')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('part3_adaptive_weights.png', dpi=150, bbox_inches='tight')
    print("\n图表已保存: part3_adaptive_weights.png")
    plt.close()

    # ========================================================================
    # Part 4: 传感器故障容错
    # ========================================================================
    print("\n[Part 4] 传感器故障容错测试")
    print("-" * 80)

    canal = CanalReach(length=1000, width=5, slope=0.001, roughness=0.025, n_nodes=21)
    canal.initialize_uniform_flow(2.0, 12.5)  # 从稳态开始
    gate = GateModel(width=5)

    controller = DistributedPIDController(
        Kp=2.0, Ki=0.1, Kd=5.0, dt=60,
        sensor_positions=[250, 500, 750, 1000],
        weighting_method='distance'
    )

    sensor_system = MultiSensorSystem(canal, [5, 10, 15, 20])

    # 手动仿真（以便插入故障）
    time = []
    h_downstream = []
    measurements_list = []
    control = []

    t = 0
    step = 0
    T_total = 3600
    dt_sim = 30

    while t < T_total:
        # 模拟传感器故障
        if 1200 < t < 1800:  # 20-30分钟，传感器2故障
            sensor_system.set_sensor_fault(1, True)
        else:
            sensor_system.set_sensor_fault(1, False)

        # 控制
        if step % 2 == 0:
            measurements = sensor_system.measure()
            healthy_m, healthy_mask = sensor_system.get_healthy_measurements(measurements)

            if np.sum(healthy_mask) > 0:
                # 填充故障传感器值
                measurements_filled = measurements.copy()
                for i in range(len(measurements)):
                    if np.isnan(measurements[i]):
                        healthy_indices = np.where(healthy_mask)[0]
                        nearest = healthy_indices[np.argmin(np.abs(healthy_indices - i))]
                        measurements_filled[i] = measurements[nearest]

                u = controller.compute(2.0, measurements_filled)
                Q_in = gate.compute_flow(u)
                canal.set_upstream_flow(Q_in)

        canal.step(dt_sim)

        if step % 2 == 0:
            time.append(t)
            h_downstream.append(canal.get_water_level_downstream())
            measurements_list.append(sensor_system.measure())
            control.append(controller.control_history[-1] if controller.control_history else 0.5)

        t += dt_sim
        step += 1

    time = np.array(time)
    h_downstream = np.array(h_downstream)
    error = 2.0 - h_downstream

    print(f"故障期间最大偏差: {np.max(np.abs(error)):.4f} m")

    # 可视化
    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(time/60, h_downstream, 'b-', linewidth=2, label='下游水位')
    ax.axhline(2.0, color='r', linestyle='--', label='目标水位')
    ax.axvspan(20, 30, alpha=0.2, color='red', label='传感器2故障期')

    ax.set_xlabel('时间 [min]')
    ax.set_ylabel('水位 [m]')
    ax.set_title('Part 4: 传感器故障容错（传感器2在20-30min故障）')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('part4_fault_tolerance.png', dpi=150, bbox_inches='tight')
    print("\n图表已保存: part4_fault_tolerance.png")
    plt.close()

    # ========================================================================
    # Part 5: 性能总结
    # ========================================================================
    print("\n[Part 5] 多点反馈 vs 单点反馈性能总结")
    print("-" * 80)

    # 对比最佳多点策略（距离权重，N=4）vs 单点
    comparison = []

    for config in [
        {'name': '单点反馈', 'method': 'single'},
        {'name': '多点反馈(N=4, 距离权重)', 'method': 'distance'}
    ]:
        canal = CanalReach(length=1000, width=5, slope=0.001, roughness=0.025, n_nodes=21)
        gate = GateModel(width=5)

        if config['method'] == 'single':
            pid = PIDController(Kp=2.0, Ki=0.1, Kd=5.0, dt=60)

            time = []
            h_downstream = []
            t = 0
            step = 0

            while t < 3600:
                if step % 2 == 0:
                    h_d = canal.get_water_level_downstream()
                    u = pid.compute(2.0, h_d)
                    Q_in = gate.compute_flow(u)
                    canal.set_upstream_flow(Q_in)

                canal.step(30)

                if step % 2 == 0:
                    time.append(t)
                    h_downstream.append(h_d)

                t += 30
                step += 1

            h_downstream = np.array(h_downstream)
            error = 2.0 - h_downstream
        else:
            controller = DistributedPIDController(
                Kp=2.0, Ki=0.1, Kd=5.0, dt=60,
                sensor_positions=[250, 500, 750, 1000],
                weighting_method='distance'
            )
            sensor_system = MultiSensorSystem(canal, [5, 10, 15, 20])
            system = DistributedClosedLoopSystem(canal, gate, controller, sensor_system)

            time, _, measurements = system.run(3600, 60, 10, 2.0)  # 使用dt_sim=10s满足CFL条件
            h_downstream = np.array([m[-1] for m in measurements])
            error = 2.0 - h_downstream

        perf = compute_performance_indices(time, error)
        comparison.append({'name': config['name'], 'perf': perf})

    print("\n性能对比:")
    print(f"{'指标':<30s} {'单点反馈':<20s} {'多点反馈':<20s} {'改善':<15s}")
    print("-" * 85)

    metrics = ['settling_time', 'steady_state_error', 'IAE', 'ISE']
    metric_names = ['调节时间 [min]', '稳态误差 [m]', 'IAE', 'ISE']
    metric_scales = [1/60, 1, 1, 1]

    for i, metric in enumerate(metrics):
        single = comparison[0]['perf'][metric] * metric_scales[i]
        multi = comparison[1]['perf'][metric] * metric_scales[i]

        if not np.isnan(single) and not np.isnan(multi):
            improvement = (single - multi) / single * 100
            print(f"{metric_names[i]:<30s} {single:<20.2f} {multi:<20.2f} {improvement:>+14.1f}%")
        else:
            print(f"{metric_names[i]:<30s} {'N/A':<20s} {'N/A':<20s} {'N/A':<15s}")

    print("\n" + "=" * 80)
    print("案例2完成！所有4个部分的图表已保存。")
    print("=" * 80)


if __name__ == '__main__':
    main()
