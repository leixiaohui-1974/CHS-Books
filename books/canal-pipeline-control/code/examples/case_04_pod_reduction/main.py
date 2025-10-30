"""
案例4：POD降阶 - 本征正交分解

实现内容：
1. 快照数据收集
2. SVD分解与POD模态提取
3. Galerkin投影降阶模型
4. 降阶模型控制
5. 4个演示实验

作者：Claude
日期：2025-10-30
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
import time

# 配置中文字体
rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False


# ============================================================================
# 从案例1复用的类定义
# ============================================================================

class CanalReach:
    """渠道段物理模型（全阶模型）"""

    def __init__(self, length, width, slope, roughness, n_nodes=51):
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

    def set_lateral_inflow(self, q_lateral_array):
        self.q_lat = np.array(q_lateral_array)

    def set_point_source(self, x_location, q_discharge):
        idx = np.argmin(np.abs(self.x - x_location))
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
    """闸门模型"""

    def __init__(self, width, Cd=0.6):
        self.B = width
        self.Cd = Cd

    def compute_flow(self, gate_opening):
        a = gate_opening
        h_upstream = 2.0
        v = self.Cd * np.sqrt(2 * 9.81 * h_upstream)
        Q = self.B * a * v
        return Q


class PIDController:
    """PID控制器"""

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
# Part 1: POD降阶模块
# ============================================================================

class POD:
    """
    POD（本征正交分解）类

    功能：
    1. 收集快照数据
    2. SVD分解
    3. 提取POD模态
    4. 计算能量捕获率
    """

    def __init__(self):
        self.snapshots = []
        self.U = None  # 左奇异向量（POD模态）
        self.S = None  # 奇异值
        self.Vt = None  # 右奇异向量
        self.Phi = None  # POD基矩阵
        self.r = None  # 降阶维数
        self.mean_snapshot = None  # 平均值（用于去中心化）

    def add_snapshot(self, h):
        """添加快照"""
        self.snapshots.append(h.copy())

    def compute_POD(self, r=None, energy_threshold=0.99, subtract_mean=True):
        """
        计算POD基

        Parameters:
        -----------
        r : int or None
            降阶维数。如果为None，根据energy_threshold自动确定
        energy_threshold : float
            能量捕获率阈值（如0.99表示99%）
        subtract_mean : bool
            是否减去平均值

        Returns:
        --------
        Phi : ndarray
            POD基矩阵 (N × r)
        """
        if len(self.snapshots) == 0:
            raise ValueError("No snapshots available. Call add_snapshot() first.")

        # 构造快照矩阵
        X = np.column_stack(self.snapshots)  # N × M

        # 去中心化（可选）
        if subtract_mean:
            self.mean_snapshot = np.mean(X, axis=1, keepdims=True)
            X = X - self.mean_snapshot
        else:
            self.mean_snapshot = np.zeros((X.shape[0], 1))

        # SVD分解
        print(f"  执行SVD分解，快照矩阵大小: {X.shape}")
        self.U, self.S, self.Vt = np.linalg.svd(X, full_matrices=False)

        # 计算能量捕获率
        total_energy = np.sum(self.S**2)
        cumulative_energy = np.cumsum(self.S**2)
        energy_ratios = cumulative_energy / total_energy

        # 确定降阶维数
        if r is None:
            # 根据能量阈值自动确定
            r = np.searchsorted(energy_ratios, energy_threshold) + 1
            print(f"  自动选择降阶维数: r = {r} (能量捕获率: {energy_ratios[r-1]:.4f})")
        else:
            print(f"  使用指定降阶维数: r = {r} (能量捕获率: {energy_ratios[r-1]:.4f})")

        self.r = r

        # 提取前r个POD模态
        self.Phi = self.U[:, :r]

        return self.Phi

    def get_energy_ratio(self, r):
        """计算指定维数的能量捕获率"""
        if self.S is None:
            raise ValueError("SVD not computed yet. Call compute_POD() first.")

        total_energy = np.sum(self.S**2)
        captured_energy = np.sum(self.S[:r]**2)
        return captured_energy / total_energy

    def project_to_reduced(self, h):
        """将全阶状态投影到降阶空间"""
        h_centered = h - self.mean_snapshot.ravel()
        a = self.Phi.T @ h_centered
        return a

    def reconstruct_from_reduced(self, a):
        """从降阶状态重构全阶状态"""
        h = self.Phi @ a + self.mean_snapshot.ravel()
        return h


# ============================================================================
# Part 2: 降阶模型类
# ============================================================================

class ReducedOrderModel:
    """
    降阶模型（基于Galerkin投影）

    简化版本：
    - 假设流量Q可以从水位h通过经验关系估计
    - 使用POD基投影连续性方程
    """

    def __init__(self, canal, pod):
        """
        Parameters:
        -----------
        canal : CanalReach
            全阶渠道模型（用于获取参数和右端项计算）
        pod : POD
            POD对象（包含基矩阵Phi）
        """
        self.canal = canal
        self.pod = pod
        self.r = pod.r

        # 降阶状态
        self.a = np.zeros(self.r)

        # 初始化降阶状态
        h_init = canal.h.copy()
        self.a = pod.project_to_reduced(h_init)

    def step(self, dt):
        """
        降阶模型时间步进

        使用Galerkin投影的降阶方程：
        da/dt = Phi^T * f(Phi*a, u)
        """
        # 重构全阶状态
        h_full = self.pod.reconstruct_from_reduced(self.a)

        # 确保物理合理性
        h_full = np.clip(h_full, 0.1, 10.0)

        # 临时设置全阶模型的水位
        self.canal.h = h_full.copy()

        # 计算流量（简化：使用Manning公式估计）
        Q_full = np.zeros_like(h_full)
        for i in range(len(h_full)):
            A = self.canal.B * h_full[i]
            R = self.canal.hydraulic_radius(h_full[i])
            if R > 0:
                Q_full[i] = A * R**(2/3) * np.sqrt(self.canal.i0) / self.canal.n
            else:
                Q_full[i] = 0.1

        Q_full = np.clip(Q_full, 0.1, 50.0)
        self.canal.Q = Q_full

        # 计算右端项（连续性方程）
        dh_dt_full = np.zeros_like(h_full)
        for i in range(1, self.canal.N - 1):
            dQ_dx = (Q_full[i+1] - Q_full[i-1]) / (2 * self.canal.dx)
            q_lat_i = self.canal.q_lat[i]
            dh_dt_full[i] = -dQ_dx / self.canal.B + q_lat_i / self.canal.B

        # 边界条件
        dh_dt_full[0] = 0.0
        dh_dt_full[-1] = 0.0

        # Galerkin投影：da/dt = Phi^T * dh_dt
        dh_dt_centered = dh_dt_full
        da_dt = self.pod.Phi.T @ dh_dt_centered

        # 欧拉前向积分
        self.a = self.a + dt * da_dt

        # 更新重构的水位
        self.canal.h = self.pod.reconstruct_from_reduced(self.a)
        self.canal.h = np.clip(self.canal.h, 0.1, 10.0)

    def get_water_level_downstream(self):
        """获取下游水位"""
        h = self.pod.reconstruct_from_reduced(self.a)
        return h[-1]

    def set_upstream_flow(self, Q):
        """设置上游流量"""
        self.canal.set_upstream_flow(Q)

    def set_point_source(self, x_location, q_discharge):
        """设置点源扰动"""
        self.canal.set_point_source(x_location, q_discharge)


# ============================================================================
# Part 3: 辅助函数
# ============================================================================

def collect_snapshots(canal, gate, controller, T_total, dt_sim, dt_snapshot, h_target):
    """
    收集快照数据

    Parameters:
    -----------
    canal : CanalReach
        渠道模型
    gate : GateModel
        闸门模型
    controller : PIDController
        控制器
    T_total : float
        总仿真时间
    dt_sim : float
        仿真步长
    dt_snapshot : float
        快照间隔
    h_target : float
        目标水位

    Returns:
    --------
    snapshots : list
        水位快照列表
    """
    snapshots = []
    t = 0
    step_count = 0

    print(f"  收集快照中...")

    while t < T_total:
        # 控制
        if step_count % int(60 / dt_sim) == 0:
            h_d = canal.get_water_level_downstream()
            u = controller.compute(h_target, h_d)
            Q_in = gate.compute_flow(u)
            canal.set_upstream_flow(Q_in)

        # 仿真
        canal.step(dt_sim)

        # 记录快照
        if step_count % int(dt_snapshot / dt_sim) == 0:
            snapshots.append(canal.h.copy())

        t += dt_sim
        step_count += 1

    print(f"  收集完成，共{len(snapshots)}个快照")

    return snapshots


def compute_reconstruction_error(h_full, h_rom):
    """计算重构误差"""
    h_full = np.array(h_full)
    h_rom = np.array(h_rom)

    # L2相对误差
    error_l2 = np.linalg.norm(h_full - h_rom) / np.linalg.norm(h_full)

    # 最大误差
    error_max = np.max(np.abs(h_full - h_rom))

    return error_l2, error_max


# ============================================================================
# 主程序 - 4个演示场景
# ============================================================================

def main():
    print("=" * 80)
    print("案例4：POD降阶 - 本征正交分解")
    print("=" * 80)

    # ========================================================================
    # Part 1: POD基提取与可视化
    # ========================================================================
    print("\n[Part 1] POD基提取与可视化")
    print("-" * 80)

    # 初始化全阶模型
    canal = CanalReach(length=1000, width=5, slope=0.001, roughness=0.025, n_nodes=51)
    gate = GateModel(width=5)
    controller = PIDController(Kp=2.0, Ki=0.1, Kd=5.0, dt=60)

    # 收集快照数据
    snapshots = collect_snapshots(
        canal, gate, controller,
        T_total=1800,  # 30分钟
        dt_sim=10,
        dt_snapshot=10,  # 每10秒一个快照
        h_target=2.0
    )

    # 计算POD
    pod = POD()
    for snapshot in snapshots:
        pod.add_snapshot(snapshot)

    Phi = pod.compute_POD(r=None, energy_threshold=0.99, subtract_mean=True)

    print(f"\nPOD基矩阵大小: {Phi.shape}")
    print(f"降阶维数: {pod.r}")

    # 可视化前4个POD模态
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.ravel()

    for i in range(min(4, pod.r)):
        axes[i].plot(canal.x, Phi[:, i], linewidth=2, color=f'C{i}')
        axes[i].set_xlabel('位置 x [m]')
        axes[i].set_ylabel(f'模态 φ_{i+1}')
        axes[i].set_title(f'POD模态 {i+1} (σ_{i+1} = {pod.S[i]:.2f})')
        axes[i].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('part1_pod_modes.png', dpi=150, bbox_inches='tight')
    print("\n图表已保存: part1_pod_modes.png")
    plt.close()

    # ========================================================================
    # Part 2: 不同降阶维数性能对比
    # ========================================================================
    print("\n[Part 2] 不同降阶维数性能对比")
    print("-" * 80)

    r_values = [2, 5, 10, 15, 20]
    comparison_results = []

    # 运行全阶模型（作为参考）
    print("\n运行全阶模型...")
    canal_full = CanalReach(length=1000, width=5, slope=0.001, roughness=0.025, n_nodes=51)
    gate_full = GateModel(width=5)
    controller_full = PIDController(Kp=2.0, Ki=0.1, Kd=5.0, dt=60)

    # 添加扰动
    canal_full.set_point_source(500, 2.0)

    time_history_full = []
    h_downstream_full = []

    t_start_full = time.time()

    t = 0
    step = 0
    while t < 1200:  # 20分钟
        if step % int(60/10) == 0:
            h_d = canal_full.get_water_level_downstream()
            u = controller_full.compute(2.0, h_d)
            Q_in = gate_full.compute_flow(u)
            canal_full.set_upstream_flow(Q_in)

        canal_full.step(10)

        if step % int(60/10) == 0:
            time_history_full.append(t)
            h_downstream_full.append(h_d)

        t += 10
        step += 1

    time_full = time.time() - t_start_full
    print(f"  全阶模型计算时间: {time_full:.3f} s")

    # 测试不同降阶维数
    for r in r_values:
        print(f"\n测试降阶维数: r = {r}")

        # 重新计算POD基（使用指定维数）
        pod_r = POD()
        for snapshot in snapshots:
            pod_r.add_snapshot(snapshot)
        pod_r.compute_POD(r=r, subtract_mean=True)

        # 创建降阶模型
        canal_rom = CanalReach(length=1000, width=5, slope=0.001, roughness=0.025, n_nodes=51)
        rom = ReducedOrderModel(canal_rom, pod_r)

        gate_rom = GateModel(width=5)
        controller_rom = PIDController(Kp=2.0, Ki=0.1, Kd=5.0, dt=60)

        # 添加扰动
        rom.set_point_source(500, 2.0)

        time_history_rom = []
        h_downstream_rom = []

        t_start_rom = time.time()

        t = 0
        step = 0
        while t < 1200:
            if step % int(60/10) == 0:
                h_d = rom.get_water_level_downstream()
                u = controller_rom.compute(2.0, h_d)
                Q_in = gate_rom.compute_flow(u)
                rom.set_upstream_flow(Q_in)

            rom.step(10)

            if step % int(60/10) == 0:
                time_history_rom.append(t)
                h_downstream_rom.append(h_d)

            t += 10
            step += 1

        time_rom = time.time() - t_start_rom

        # 计算误差
        error_l2, error_max = compute_reconstruction_error(h_downstream_full, h_downstream_rom)
        energy_ratio = pod_r.get_energy_ratio(r)
        speedup = time_full / time_rom

        print(f"  能量捕获率: {energy_ratio:.4f}")
        print(f"  L2重构误差: {error_l2:.4f}")
        print(f"  最大误差: {error_max:.4f} m")
        print(f"  计算时间: {time_rom:.3f} s")
        print(f"  加速比: {speedup:.1f}x")

        comparison_results.append({
            'r': r,
            'energy_ratio': energy_ratio,
            'error_l2': error_l2,
            'error_max': error_max,
            'time': time_rom,
            'speedup': speedup,
            'h_rom': h_downstream_rom
        })

    # 可视化
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 子图1：能量捕获率
    r_array = [res['r'] for res in comparison_results]
    energy_array = [res['energy_ratio'] for res in comparison_results]
    axes[0, 0].plot(r_array, energy_array, 'o-', linewidth=2, markersize=8, color='blue')
    axes[0, 0].axhline(0.99, color='r', linestyle='--', alpha=0.5, label='99%阈值')
    axes[0, 0].set_xlabel('降阶维数 r')
    axes[0, 0].set_ylabel('能量捕获率')
    axes[0, 0].set_title('能量捕获率 vs 降阶维数')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)

    # 子图2：重构误差
    error_array = [res['error_l2'] for res in comparison_results]
    axes[0, 1].semilogy(r_array, error_array, 's-', linewidth=2, markersize=8, color='green')
    axes[0, 1].set_xlabel('降阶维数 r')
    axes[0, 1].set_ylabel('L2重构误差')
    axes[0, 1].set_title('重构误差 vs 降阶维数')
    axes[0, 1].grid(True, alpha=0.3)

    # 子图3：加速比
    speedup_array = [res['speedup'] for res in comparison_results]
    axes[1, 0].plot(r_array, speedup_array, '^-', linewidth=2, markersize=8, color='red')
    axes[1, 0].set_xlabel('降阶维数 r')
    axes[1, 0].set_ylabel('加速比')
    axes[1, 0].set_title('计算加速比 vs 降阶维数')
    axes[1, 0].grid(True, alpha=0.3)

    # 子图4：水位响应对比
    axes[1, 1].plot(np.array(time_history_full)/60, h_downstream_full,
                   linewidth=2, color='black', label='全阶模型')
    colors = ['blue', 'green', 'orange', 'red', 'purple']
    for i, res in enumerate(comparison_results):
        axes[1, 1].plot(np.array(time_history_rom)/60, res['h_rom'],
                       linestyle='--', linewidth=1.5, color=colors[i],
                       label=f'r={res["r"]}')
    axes[1, 1].axhline(2.0, color='k', linestyle=':', alpha=0.3)
    axes[1, 1].set_xlabel('时间 [min]')
    axes[1, 1].set_ylabel('下游水位 [m]')
    axes[1, 1].set_title('水位响应对比')
    axes[1, 1].legend(loc='best', fontsize=8)
    axes[1, 1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('part2_dimension_comparison.png', dpi=150, bbox_inches='tight')
    print("\n图表已保存: part2_dimension_comparison.png")
    plt.close()

    # ========================================================================
    # Part 3: 降阶模型控制性能
    # ========================================================================
    print("\n[Part 3] 降阶模型控制性能")
    print("-" * 80)

    # 使用r=10的降阶模型
    r_optimal = 10
    print(f"\n使用最优降阶维数: r = {r_optimal}")

    # 构建POD基
    pod_opt = POD()
    for snapshot in snapshots:
        pod_opt.add_snapshot(snapshot)
    pod_opt.compute_POD(r=r_optimal, subtract_mean=True)

    # 全阶模型控制
    print("\n运行全阶模型控制...")
    canal_full_ctrl = CanalReach(length=1000, width=5, slope=0.001, roughness=0.025, n_nodes=51)
    gate_full_ctrl = GateModel(width=5)
    controller_full_ctrl = PIDController(Kp=2.0, Ki=0.1, Kd=5.0, dt=60)

    time_hist_full = []
    h_hist_full = []
    control_hist_full = []

    # 添加阶跃扰动
    def disturbance(t):
        return 2.0 if t >= 300 else 0.0

    t = 0
    step = 0
    t_start = time.time()

    while t < 1800:
        q_d = disturbance(t)
        canal_full_ctrl.set_point_source(500, q_d)

        if step % int(60/10) == 0:
            h_d = canal_full_ctrl.get_water_level_downstream()
            u = controller_full_ctrl.compute(2.0, h_d)
            Q_in = gate_full_ctrl.compute_flow(u)
            canal_full_ctrl.set_upstream_flow(Q_in)

        canal_full_ctrl.step(10)

        if step % int(60/10) == 0:
            time_hist_full.append(t)
            h_hist_full.append(h_d)
            control_hist_full.append(u)

        t += 10
        step += 1

    time_full_ctrl = time.time() - t_start
    print(f"  全阶模型计算时间: {time_full_ctrl:.3f} s")

    # 降阶模型控制
    print("\n运行降阶模型控制...")
    canal_rom_ctrl = CanalReach(length=1000, width=5, slope=0.001, roughness=0.025, n_nodes=51)
    rom_ctrl = ReducedOrderModel(canal_rom_ctrl, pod_opt)
    gate_rom_ctrl = GateModel(width=5)
    controller_rom_ctrl = PIDController(Kp=2.0, Ki=0.1, Kd=5.0, dt=60)

    time_hist_rom = []
    h_hist_rom = []
    control_hist_rom = []

    t = 0
    step = 0
    t_start = time.time()

    while t < 1800:
        q_d = disturbance(t)
        rom_ctrl.set_point_source(500, q_d)

        if step % int(60/10) == 0:
            h_d = rom_ctrl.get_water_level_downstream()
            u = controller_rom_ctrl.compute(2.0, h_d)
            Q_in = gate_rom_ctrl.compute_flow(u)
            rom_ctrl.set_upstream_flow(Q_in)

        rom_ctrl.step(10)

        if step % int(60/10) == 0:
            time_hist_rom.append(t)
            h_hist_rom.append(h_d)
            control_hist_rom.append(u)

        t += 10
        step += 1

    time_rom_ctrl = time.time() - t_start
    print(f"  降阶模型计算时间: {time_rom_ctrl:.3f} s")
    print(f"  加速比: {time_full_ctrl / time_rom_ctrl:.1f}x")

    # 计算控制性能
    error_full = 2.0 - np.array(h_hist_full)
    error_rom = 2.0 - np.array(h_hist_rom)

    IAE_full = np.trapezoid(np.abs(error_full), time_hist_full)
    IAE_rom = np.trapezoid(np.abs(error_rom), time_hist_rom)

    print(f"\n控制性能:")
    print(f"  全阶模型 - IAE: {IAE_full:.2f}")
    print(f"  降阶模型 - IAE: {IAE_rom:.2f}")
    print(f"  性能损失: {(IAE_rom/IAE_full - 1)*100:.1f}%")

    # 可视化
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))

    # 子图1：水位响应
    axes[0].plot(np.array(time_hist_full)/60, h_hist_full,
                linewidth=2, color='blue', label='全阶模型')
    axes[0].plot(np.array(time_hist_rom)/60, h_hist_rom,
                linestyle='--', linewidth=2, color='red', label='降阶模型(r=10)')
    axes[0].axhline(2.0, color='k', linestyle=':', alpha=0.3, label='目标')
    axes[0].axvline(300/60, color='gray', linestyle='--', alpha=0.5, label='扰动开始')
    axes[0].set_ylabel('下游水位 [m]')
    axes[0].set_title('Part 3: 降阶模型控制性能 - 水位响应')
    axes[0].legend(loc='best')
    axes[0].grid(True, alpha=0.3)

    # 子图2：控制量
    axes[1].plot(np.array(time_hist_full)/60, control_hist_full,
                linewidth=2, color='blue', label='全阶模型')
    axes[1].plot(np.array(time_hist_rom)/60, control_hist_rom,
                linestyle='--', linewidth=2, color='red', label='降阶模型(r=10)')
    axes[1].set_ylabel('闸门开度 [m]')
    axes[1].set_title('控制量对比')
    axes[1].legend(loc='best')
    axes[1].grid(True, alpha=0.3)

    # 子图3：误差
    axes[2].plot(np.array(time_hist_full)/60, error_full,
                linewidth=2, color='blue', label='全阶模型')
    axes[2].plot(np.array(time_hist_rom)/60, error_rom,
                linestyle='--', linewidth=2, color='red', label='降阶模型(r=10)')
    axes[2].axhline(0, color='k', linestyle='-', linewidth=0.5)
    axes[2].set_xlabel('时间 [min]')
    axes[2].set_ylabel('水位误差 [m]')
    axes[2].set_title('误差对比')
    axes[2].legend(loc='best')
    axes[2].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('part3_control_performance.png', dpi=150, bbox_inches='tight')
    print("\n图表已保存: part3_control_performance.png")
    plt.close()

    # ========================================================================
    # Part 4: 性能总结
    # ========================================================================
    print("\n[Part 4] 性能总结")
    print("=" * 80)

    print("\nPOD降阶模型性能:")
    print(f"{'指标':<25} {'全阶':<15} {'降阶(r=10)':<15} {'差异':<15}")
    print("-" * 70)
    print(f"{'节点数':<25} {51:<15} {10:<15} {'-':<15}")
    print(f"{'能量捕获率':<25} {'-':<15} {pod_opt.get_energy_ratio(10):.4f} {'-':<15}")
    print(f"{'计算时间 [s]':<25} {time_full_ctrl:<15.3f} {time_rom_ctrl:<15.3f} "
          f"{time_full_ctrl/time_rom_ctrl:.1f}x加速")
    print(f"{'IAE':<25} {IAE_full:<15.2f} {IAE_rom:<15.2f} "
          f"{(IAE_rom/IAE_full-1)*100:+.1f}%")

    print("\n" + "=" * 80)
    print("案例4完成！所有3个部分的图表已保存。")
    print("=" * 80)


if __name__ == '__main__':
    main()
