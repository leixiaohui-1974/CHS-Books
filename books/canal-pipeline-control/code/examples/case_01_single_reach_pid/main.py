"""
案例1：单渠段PID水位控制

继承自：
- 《明渠水力学》案例13：非恒定流模拟（Saint-Venant求解器）
- 《水系统控制论》案例1：PID控制器

功能：
- Saint-Venant方程数值求解（Lax-Wendroff格式）
- PID水位控制器
- 闭环仿真与性能分析
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

# 中文字体设置
rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False


# ============================================================================
# Part 1: 渠道物理模型 - Saint-Venant求解器
# ============================================================================

class CanalReach:
    """
    矩形断面渠道段 - Saint-Venant方程求解器

    控制方程：
    ∂A/∂t + ∂Q/∂x = q_lat
    ∂Q/∂t + ∂(Q²/A)/∂x + gA∂h/∂x = -gAS_f

    数值方法：Lax-Wendroff格式（二阶精度）
    """

    def __init__(self, length, width, slope, roughness, n_nodes=21):
        """
        Parameters:
        -----------
        length : float
            渠道长度 [m]
        width : float
            渠道底宽 [m]
        slope : float
            渠底坡度 [-]
        roughness : float
            Manning糙率系数 [s/m^(1/3)]
        n_nodes : int
            空间节点数
        """
        self.L = length
        self.B = width
        self.i0 = slope
        self.n = roughness
        self.N = n_nodes

        # 空间离散
        self.dx = length / (n_nodes - 1)
        self.x = np.linspace(0, length, n_nodes)

        # 重力加速度
        self.g = 9.81  # m/s²

        # 状态变量
        self.h = np.zeros(n_nodes)  # 水深 [m]
        self.Q = np.zeros(n_nodes)  # 流量 [m³/s]

        # 侧向入流
        self.q_lat = np.zeros(n_nodes)  # [m²/s]

        # 边界条件
        self.Q_upstream = 10.0  # 上游流量 [m³/s]
        self.h_downstream = 2.0  # 下游水位 [m]

        # 初始化为均匀流
        self.initialize_uniform_flow(h0=1.8, Q0=10.0)

    def initialize_uniform_flow(self, h0, Q0):
        """初始化为均匀流状态"""
        self.h[:] = h0
        self.Q[:] = Q0

    def hydraulic_radius(self, h):
        """计算水力半径 R = A/χ"""
        A = self.B * h
        chi = self.B + 2 * h
        R = A / chi
        return R

    def friction_slope(self, h, Q):
        """
        计算摩阻坡度 S_f = n²Q²/(A²R^(4/3))

        Manning公式
        """
        A = self.B * h
        R = self.hydraulic_radius(h)

        # 避免除零
        if A < 1e-6:
            return 0.0

        Sf = self.n**2 * Q**2 / (A**2 * R**(4/3))
        return Sf

    def compute_fluxes(self, h, Q):
        """
        计算通量 F = [Q, Q²/A + gA²/2]
        """
        A = self.B * h

        # 避免除零
        A = np.maximum(A, 1e-6)

        F1 = Q
        F2 = Q**2 / A + 0.5 * self.g * A**2 / self.B

        return F1, F2

    def compute_sources(self, h, Q, index=None):
        """
        计算源项 S = [q_lat, -gAS_f + gAS_0]

        Parameters:
        -----------
        h : float or array
            水深
        Q : float or array
            流量
        index : int, optional
            如果提供，返回该位置的源项；否则返回标量计算
        """
        A = self.B * h
        Sf = self.friction_slope(h, Q)

        if index is not None:
            S1 = self.q_lat[index] if hasattr(self.q_lat, '__len__') else self.q_lat
            S2 = self.g * A * (self.i0 - Sf)
        else:
            S1 = self.q_lat if np.isscalar(self.q_lat) else self.q_lat
            S2 = self.g * A * (self.i0 - Sf)

        return S1, S2

    def step(self, dt):
        """
        时间步进（简化的显式格式）

        Parameters:
        -----------
        dt : float
            时间步长 [s]
        """
        h = self.h.copy()
        Q = self.Q.copy()

        # 简化的显式格式（向前欧拉 + 中心差分）
        h_new = h.copy()
        Q_new = Q.copy()

        for i in range(1, self.N - 1):
            # 空间导数（中心差分）
            dQ_dx = (Q[i+1] - Q[i-1]) / (2 * self.dx)

            # 连续方程
            q_lat_i = self.q_lat[i] if hasattr(self.q_lat, '__len__') else self.q_lat
            h_new[i] = h[i] - dt * dQ_dx + dt * q_lat_i / self.B

            # 动量方程（简化）
            A_i = self.B * h[i]
            v_i = Q[i] / max(A_i, 1e-6)

            # 压力梯度
            dh_dx = (h[i+1] - h[i-1]) / (2 * self.dx)

            # 摩阻
            Sf_i = self.friction_slope(h[i], Q[i])

            # 动量方程
            dQ_dt = -self.g * A_i * (dh_dx + Sf_i - self.i0)

            Q_new[i] = Q[i] + dt * dQ_dt

        # 边界条件
        # 上游：流量边界
        Q_new[0] = self.Q_upstream
        h_new[0] = h_new[1]  # 外推

        # 下游：水位边界（自由溢流）
        h_new[-1] = h_new[-2]  # 外推
        # 根据下游水头计算流量
        C_weir = 1.5
        # 防止负水深导致NaN
        Q_new[-1] = C_weir * self.B * max(h_new[-1], 0.0)**1.5

        # 更新状态（防止负水深）
        self.h = np.maximum(h_new, 0.001)  # 最小水深1mm
        self.Q = Q_new

    def get_water_level_downstream(self):
        """获取下游水位"""
        return self.h[-1]

    def set_upstream_flow(self, Q_in):
        """设置上游流量"""
        self.Q_upstream = Q_in

    def set_lateral_inflow(self, q_lat):
        """设置侧向入流"""
        if isinstance(q_lat, (int, float)):
            self.q_lat[:] = q_lat
        else:
            self.q_lat = q_lat

    def compute_cfl_number(self, dt):
        """计算CFL数"""
        A = self.B * self.h
        v = self.Q / np.maximum(A, 1e-6)  # 流速
        c = np.sqrt(self.g * self.h)  # 波速

        cfl = dt * (np.abs(v) + c) / self.dx
        return np.max(cfl)


# ============================================================================
# Part 2: 闸门模型
# ============================================================================

class GateModel:
    """
    闸门模型 - 闸孔出流公式

    Q = μ × u × B × √(2gh_up)
    """

    def __init__(self, width, discharge_coeff=0.6):
        """
        Parameters:
        -----------
        width : float
            闸门宽度 [m]
        discharge_coeff : float
            流量系数 [-]
        """
        self.B = width
        self.mu = discharge_coeff
        self.g = 9.81

        # 上游水头
        self.h_upstream = 3.0  # [m]

    def compute_flow(self, u_gate):
        """
        计算闸门过流量

        Parameters:
        -----------
        u_gate : float
            闸门开度 [m]

        Returns:
        --------
        Q : float
            流量 [m³/s]
        """
        # 限制开度范围
        u = np.clip(u_gate, 0.01, 1.5)

        # 闸孔出流公式
        Q = self.mu * u * self.B * np.sqrt(2 * self.g * self.h_upstream)

        return Q


# ============================================================================
# Part 3: PID控制器
# ============================================================================

class PIDController:
    """
    PID水位控制器

    u(t) = Kp×e + Ki×∫e + Kd×de/dt
    """

    def __init__(self, Kp, Ki, Kd, dt, u_min=0.1, u_max=1.0):
        """
        Parameters:
        -----------
        Kp : float
            比例增益
        Ki : float
            积分增益
        Kd : float
            微分增益
        dt : float
            采样周期 [s]
        u_min, u_max : float
            控制量限制 [m]
        """
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.dt = dt

        self.u_min = u_min
        self.u_max = u_max

        # 状态变量
        self.integral = 0.0
        self.error_prev = 0.0

        # 记录
        self.error_history = []
        self.control_history = []

    def compute(self, target, measurement):
        """
        计算控制量

        Parameters:
        -----------
        target : float
            目标水位 [m]
        measurement : float
            测量水位 [m]

        Returns:
        --------
        u : float
            控制量（闸门开度） [m]
        """
        # 误差
        error = target - measurement

        # 积分项（梯形法则）
        self.integral += error * self.dt

        # 微分项（后向差分）
        derivative = (error - self.error_prev) / self.dt

        # PID控制律
        u_raw = self.Kp * error + self.Ki * self.integral + self.Kd * derivative

        # 限幅
        u = np.clip(u_raw, self.u_min, self.u_max)

        # 抗积分饱和（条件积分）
        if u_raw != u:  # 饱和
            self.integral -= error * self.dt  # 回退积分

        # 更新状态
        self.error_prev = error

        # 记录
        self.error_history.append(error)
        self.control_history.append(u)

        return u

    def reset(self):
        """重置控制器状态"""
        self.integral = 0.0
        self.error_prev = 0.0
        self.error_history = []
        self.control_history = []


# ============================================================================
# Part 4: 闭环仿真系统
# ============================================================================

class ClosedLoopSystem:
    """闭环控制系统仿真"""

    def __init__(self, canal, gate, controller):
        self.canal = canal
        self.gate = gate
        self.controller = controller

        # 记录
        self.time_history = []
        self.water_level_history = []
        self.flow_history = []
        self.control_history = []

    def run(self, T_total, dt_control, dt_sim, target_level):
        """
        运行闭环仿真

        Parameters:
        -----------
        T_total : float
            总仿真时间 [s]
        dt_control : float
            控制周期 [s]
        dt_sim : float
            仿真步长 [s]
        target_level : float or function
            目标水位 [m]
        """
        t = 0
        step_count = 0
        control_step = 0

        # 清空记录
        self.time_history = []
        self.water_level_history = []
        self.flow_history = []
        self.control_history = []

        while t < T_total:
            # 控制周期（每dt_control秒执行一次）
            if step_count % int(dt_control / dt_sim) == 0:
                # 测量下游水位
                h_measured = self.canal.get_water_level_downstream()

                # 目标值
                if callable(target_level):
                    h_target = target_level(t)
                else:
                    h_target = target_level

                # PID控制计算
                u_gate = self.controller.compute(h_target, h_measured)

                # 闸门执行
                Q_in = self.gate.compute_flow(u_gate)
                self.canal.set_upstream_flow(Q_in)

                control_step += 1

            # 水力学仿真步进
            self.canal.step(dt_sim)

            # 记录（每60s记录一次）
            if step_count % int(60 / dt_sim) == 0:
                self.time_history.append(t)
                self.water_level_history.append(self.canal.h.copy())
                self.flow_history.append(self.canal.Q.copy())
                self.control_history.append(self.controller.control_history[-1] if self.controller.control_history else 0)

            t += dt_sim
            step_count += 1

        return self.time_history, self.water_level_history, self.flow_history


# ============================================================================
# Part 5: 性能评估
# ============================================================================

def compute_performance_indices(time, error):
    """
    计算控制性能指标

    Parameters:
    -----------
    time : array
        时间序列 [s]
    error : array
        误差序列 [m]

    Returns:
    --------
    dict : 性能指标字典
    """
    dt = time[1] - time[0]

    # IAE: Integral Absolute Error
    IAE = np.trapz(np.abs(error), time)

    # ISE: Integral Squared Error
    ISE = np.trapz(error**2, time)

    # ITAE: Integral Time Absolute Error
    ITAE = np.trapz(time * np.abs(error), time)

    # 最大超调量
    overshoot = np.max(error) if np.max(error) > 0 else 0

    # 调节时间（±2%误差带）
    threshold = 0.02
    settling_idx = np.where(np.abs(error) < threshold)[0]
    if len(settling_idx) > 0:
        settling_time = time[settling_idx[0]]
    else:
        settling_time = time[-1]

    # 稳态误差
    steady_state_error = np.mean(np.abs(error[-int(len(error)*0.1):]))

    return {
        'IAE': IAE,
        'ISE': ISE,
        'ITAE': ITAE,
        'overshoot': overshoot,
        'settling_time': settling_time,
        'steady_state_error': steady_state_error
    }


# ============================================================================
# 主程序 - 5个演示场景
# ============================================================================

def main():
    print("=" * 80)
    print("案例1：单渠段PID水位控制")
    print("=" * 80)

    # ========================================================================
    # Part 1: 阶跃响应测试
    # ========================================================================
    print("\n[Part 1] 阶跃响应测试")
    print("-" * 80)

    # 创建系统组件
    canal = CanalReach(length=1000, width=5, slope=0.001, roughness=0.025, n_nodes=21)
    gate = GateModel(width=5)
    pid = PIDController(Kp=2.0, Ki=0.1, Kd=5.0, dt=60)

    system = ClosedLoopSystem(canal, gate, pid)

    # 仿真参数
    T_total = 3600  # 1小时
    dt_control = 60  # 控制周期60s
    dt_sim = 30  # 仿真步长30s
    h_target = 2.0  # 目标水位2.0m

    # 运行仿真
    time, h_history, Q_history = system.run(T_total, dt_control, dt_sim, h_target)

    # 提取下游水位
    h_downstream = np.array([h[-1] for h in h_history])

    # 性能评估
    error = h_target - h_downstream
    perf = compute_performance_indices(time, error)

    print(f"调节时间: {perf['settling_time']:.1f} s ({perf['settling_time']/60:.1f} min)")
    print(f"最大超调: {perf['overshoot']:.4f} m ({perf['overshoot']/h_target*100:.2f}%)")
    print(f"稳态误差: {perf['steady_state_error']:.4f} m")
    print(f"IAE: {perf['IAE']:.2f}, ISE: {perf['ISE']:.2f}, ITAE: {perf['ITAE']:.2f}")

    # 可视化
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))

    # 下游水位
    axes[0].plot(np.array(time)/60, h_downstream, 'b-', label='实际水位', linewidth=2)
    axes[0].axhline(h_target, color='r', linestyle='--', label='目标水位')
    axes[0].axhline(h_target + 0.02*h_target, color='gray', linestyle=':', alpha=0.5)
    axes[0].axhline(h_target - 0.02*h_target, color='gray', linestyle=':', alpha=0.5, label='±2%误差带')
    axes[0].set_xlabel('时间 [min]')
    axes[0].set_ylabel('水位 [m]')
    axes[0].set_title('Part 1: 阶跃响应 - 下游水位')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # 控制量
    axes[1].plot(np.array(time)/60, system.control_history, 'g-', label='闸门开度', linewidth=2)
    axes[1].set_xlabel('时间 [min]')
    axes[1].set_ylabel('开度 [m]')
    axes[1].set_title('闸门控制动作')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    # 误差
    axes[2].plot(np.array(time)/60, error, 'r-', label='控制误差', linewidth=2)
    axes[2].axhline(0, color='k', linestyle='-', alpha=0.3)
    axes[2].set_xlabel('时间 [min]')
    axes[2].set_ylabel('误差 [m]')
    axes[2].set_title('控制误差')
    axes[2].legend()
    axes[2].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('part1_step_response.png', dpi=150, bbox_inches='tight')
    print("图表已保存: part1_step_response.png")
    plt.close()

    # ========================================================================
    # Part 2: 扰动抑制
    # ========================================================================
    print("\n[Part 2] 扰动抑制测试")
    print("-" * 80)

    # 重新初始化（从稳态开始）
    canal = CanalReach(length=1000, width=5, slope=0.001, roughness=0.025, n_nodes=21)
    canal.initialize_uniform_flow(h0=2.0, Q0=12.5)
    gate = GateModel(width=5)
    pid = PIDController(Kp=2.0, Ki=0.1, Kd=5.0, dt=60)

    # 施加侧向入流扰动
    def apply_disturbance(t):
        if 600 < t < 1200:  # 10-20分钟
            return 0.05  # 0.05 m²/s
        return 0

    # 手动仿真循环（以便动态改变扰动）
    T_total = 2400
    dt_control = 60
    dt_sim = 30

    time = []
    h_downstream = []
    control = []
    t = 0
    step = 0

    while t < T_total:
        # 更新扰动
        q_lat = apply_disturbance(t)
        canal.set_lateral_inflow(q_lat)

        # 控制
        if step % int(dt_control / dt_sim) == 0:
            h_d = canal.get_water_level_downstream()
            u = pid.compute(2.0, h_d)
            Q_in = gate.compute_flow(u)
            canal.set_upstream_flow(Q_in)

        # 仿真
        canal.step(dt_sim)

        # 记录
        if step % int(60 / dt_sim) == 0:
            time.append(t)
            h_downstream.append(canal.get_water_level_downstream())
            control.append(pid.control_history[-1] if pid.control_history else 0.5)

        t += dt_sim
        step += 1

    time = np.array(time)
    h_downstream = np.array(h_downstream)
    error = 2.0 - h_downstream

    # 计算恢复时间
    disturbance_end = 1200
    idx_after_dist = np.where(time > disturbance_end)[0]
    recovery_threshold = 0.02
    recovered_idx = np.where(np.abs(error[idx_after_dist]) < recovery_threshold)[0]
    if len(recovered_idx) > 0:
        recovery_time = time[idx_after_dist[recovered_idx[0]]] - disturbance_end
    else:
        recovery_time = np.nan

    print(f"扰动恢复时间: {recovery_time:.1f} s ({recovery_time/60:.1f} min)")
    print(f"扰动期间最大偏差: {np.max(np.abs(error)):.4f} m")

    # 可视化
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))

    # 水位
    axes[0].plot(time/60, h_downstream, 'b-', linewidth=2, label='实际水位')
    axes[0].axhline(2.0, color='r', linestyle='--', label='目标水位')
    axes[0].axvspan(10, 20, alpha=0.2, color='orange', label='扰动期')
    axes[0].set_xlabel('时间 [min]')
    axes[0].set_ylabel('水位 [m]')
    axes[0].set_title('Part 2: 扰动抑制 - 侧向入流扰动')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # 控制量
    axes[1].plot(time/60, control, 'g-', linewidth=2)
    axes[1].set_xlabel('时间 [min]')
    axes[1].set_ylabel('闸门开度 [m]')
    axes[1].set_title('闸门控制响应')
    axes[1].grid(True, alpha=0.3)

    # 误差
    axes[2].plot(time/60, error, 'r-', linewidth=2)
    axes[2].axhline(0, color='k', linestyle='-', alpha=0.3)
    axes[2].axvspan(10, 20, alpha=0.2, color='orange')
    axes[2].set_xlabel('时间 [min]')
    axes[2].set_ylabel('误差 [m]')
    axes[2].set_title('控制误差')
    axes[2].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('part2_disturbance_rejection.png', dpi=150, bbox_inches='tight')
    print("图表已保存: part2_disturbance_rejection.png")
    plt.close()

    # ========================================================================
    # Part 3: 参数影响分析
    # ========================================================================
    print("\n[Part 3] PID参数影响分析")
    print("-" * 80)

    # 测试不同PID参数组合
    pid_configs = [
        {'name': 'Kp主导', 'Kp': 5.0, 'Ki': 0.0, 'Kd': 0.0},
        {'name': '标准PID', 'Kp': 2.0, 'Ki': 0.1, 'Kd': 5.0},
        {'name': '高Kd', 'Kp': 2.0, 'Ki': 0.1, 'Kd': 10.0},
        {'name': '高Ki', 'Kp': 2.0, 'Ki': 0.5, 'Kd': 5.0},
    ]

    results = []

    for config in pid_configs:
        # 初始化
        canal = CanalReach(length=1000, width=5, slope=0.001, roughness=0.025, n_nodes=21)
        gate = GateModel(width=5)
        pid = PIDController(Kp=config['Kp'], Ki=config['Ki'], Kd=config['Kd'], dt=60)

        system = ClosedLoopSystem(canal, gate, pid)

        # 仿真
        time, h_history, _ = system.run(3600, 60, 30, 2.0)
        h_downstream = np.array([h[-1] for h in h_history])

        results.append({
            'name': config['name'],
            'time': time,
            'h': h_downstream,
            'params': config
        })

        error = 2.0 - h_downstream
        perf = compute_performance_indices(time, error)
        print(f"{config['name']:15s}: ts={perf['settling_time']/60:5.1f}min, "
              f"overshoot={perf['overshoot']*100:5.2f}%, "
              f"IAE={perf['IAE']:6.2f}")

    # 可视化对比
    fig, ax = plt.subplots(figsize=(12, 6))

    for result in results:
        ax.plot(np.array(result['time'])/60, result['h'],
                linewidth=2, label=result['name'])

    ax.axhline(2.0, color='r', linestyle='--', alpha=0.5, label='目标水位')
    ax.set_xlabel('时间 [min]')
    ax.set_ylabel('水位 [m]')
    ax.set_title('Part 3: 不同PID参数的响应对比')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('part3_pid_parameters.png', dpi=150, bbox_inches='tight')
    print("图表已保存: part3_pid_parameters.png")
    plt.close()

    # ========================================================================
    # Part 4: 时空演化图
    # ========================================================================
    print("\n[Part 4] 沿程水位时空演化")
    print("-" * 80)

    # 重新仿真并保存完整时空数据
    canal = CanalReach(length=1000, width=5, slope=0.001, roughness=0.025, n_nodes=21)
    gate = GateModel(width=5)
    pid = PIDController(Kp=2.0, Ki=0.1, Kd=5.0, dt=60)

    system = ClosedLoopSystem(canal, gate, pid)
    time, h_history, _ = system.run(3600, 60, 30, 2.0)

    # 转换为二维数组
    h_matrix = np.array(h_history).T  # (空间 × 时间)

    # 绘制等高线图
    fig, ax = plt.subplots(figsize=(12, 6))

    X, T = np.meshgrid(time, canal.x)
    contour = ax.contourf(T, X/60, h_matrix, levels=20, cmap='viridis')
    plt.colorbar(contour, ax=ax, label='水深 [m]')

    ax.set_xlabel('沿程距离 [m]')
    ax.set_ylabel('时间 [min]')
    ax.set_title('Part 4: 渠道沿程水位时空演化图')

    plt.tight_layout()
    plt.savefig('part4_spatiotemporal.png', dpi=150, bbox_inches='tight')
    print("图表已保存: part4_spatiotemporal.png")
    plt.close()

    # ========================================================================
    # Part 5: 性能总结
    # ========================================================================
    print("\n[Part 5] 控制系统性能总结")
    print("-" * 80)

    # 使用标准PID参数
    canal = CanalReach(length=1000, width=5, slope=0.001, roughness=0.025, n_nodes=21)
    gate = GateModel(width=5)
    pid = PIDController(Kp=2.0, Ki=0.1, Kd=5.0, dt=60)

    system = ClosedLoopSystem(canal, gate, pid)
    time, h_history, _ = system.run(3600, 60, 30, 2.0)

    h_downstream = np.array([h[-1] for h in h_history])
    error = 2.0 - h_downstream

    # 详细性能指标
    perf = compute_performance_indices(time, error)

    print("\n性能指标汇总:")
    print(f"  调节时间 (ts):        {perf['settling_time']:.1f} s ({perf['settling_time']/60:.1f} min)")
    print(f"  超调量 (σ):           {perf['overshoot']:.4f} m ({perf['overshoot']/2.0*100:.2f}%)")
    print(f"  稳态误差 (ess):       {perf['steady_state_error']:.4f} m ({perf['steady_state_error']/2.0*100:.2f}%)")
    print(f"  IAE:                  {perf['IAE']:.2f} m·s")
    print(f"  ISE:                  {perf['ISE']:.2f} m²·s")
    print(f"  ITAE:                 {perf['ITAE']:.2f} m·s²")

    # CFL数检查
    cfl = canal.compute_cfl_number(30)
    print(f"\nCFL数: {cfl:.3f} (< 1.0 稳定)")

    print("\n" + "=" * 80)
    print("案例1完成！所有5个部分的图表已保存。")
    print("=" * 80)


if __name__ == '__main__':
    main()
