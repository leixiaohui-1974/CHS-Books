"""
案例5：动态模态分解（DMD）

实现内容：
1. DMD算法实现
2. DMD模态提取与分析
3. DMD vs POD对比
4. DMD预测能力测试
5. 4个演示实验

作者：Claude
日期：2025-10-30
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
import time
import sys
import os

# 添加案例4的路径以复用POD类
sys.path.append(os.path.join(os.path.dirname(__file__), '../case_04_pod_reduction'))

# 配置中文字体
rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False


# ============================================================================
# 从案例1/4复用的类定义
# ============================================================================

class CanalReach:
    """渠道段物理模型"""

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
        h = self.h.copy()
        Q = self.Q.copy()

        h_new = h.copy()
        Q_new = Q.copy()

        for i in range(1, self.N - 1):
            dQ_dx = (Q[i+1] - Q[i-1]) / (2 * self.dx)
            q_lat_i = self.q_lat[i]
            h_new[i] = h[i] - dt * dQ_dx / self.B + dt * q_lat_i / self.B
            h_new[i] = np.clip(h_new[i], 0.1, 10.0)

            A_i = self.B * h[i]
            dh_dx = (h[i+1] - h[i-1]) / (2 * self.dx)
            Sf_i = self.friction_slope(h[i], Q[i])

            if not np.isfinite(Sf_i):
                Sf_i = self.i0
            Sf_i = np.clip(Sf_i, 0.0, 0.1)

            dQ_dt = -self.g * A_i * (dh_dx + Sf_i - self.i0)
            Q_new[i] = Q[i] + dt * dQ_dt
            Q_new[i] = np.clip(Q_new[i], 0.1, 50.0)

        Q_new[0] = self.Q_upstream
        h_new[0] = h_new[1]

        h_new[-1] = h_new[-2]
        h_new[-1] = np.clip(h_new[-1], 0.1, 10.0)
        C_weir = 1.5
        Q_new[-1] = C_weir * self.B * h_new[-1]**1.5

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
# Part 1: DMD类实现
# ============================================================================

class DMD:
    """
    动态模态分解（Dynamic Mode Decomposition）

    基于Koopman算子理论的数据驱动降阶方法
    """

    def __init__(self, svd_rank=None):
        """
        Parameters:
        -----------
        svd_rank : int or None
            SVD降阶的秩。如果为None，保留所有非零奇异值
        """
        self.svd_rank = svd_rank

        # DMD结果
        self.modes = None  # DMD模态 (N × r)
        self.eigenvalues = None  # DMD特征值 (r,)
        self.amplitudes = None  # 初始系数 (r,)

        # SVD结果
        self.U = None
        self.S = None
        self.Vt = None

        # 时间步长
        self.dt = None

    def fit(self, X, Y=None, dt=1.0):
        """
        拟合DMD模型

        Parameters:
        -----------
        X : ndarray (N × M)
            数据矩阵：[x₀, x₁, ..., x_{M-1}]
        Y : ndarray (N × M) or None
            如果为None，Y = [x₁, x₂, ..., x_M]（从X自动构造）
        dt : float
            时间步长

        Returns:
        --------
        self
        """
        self.dt = dt

        # 构造Y（如果未提供）
        if Y is None:
            X_data = X[:, :-1]
            Y_data = X[:, 1:]
        else:
            X_data = X
            Y_data = Y

        # 步骤1：SVD分解X
        self.U, self.S, self.Vt = np.linalg.svd(X_data, full_matrices=False)

        # 确定秩
        if self.svd_rank is None:
            r = len(self.S)
        else:
            r = min(self.svd_rank, len(self.S))

        # 截断SVD
        U_r = self.U[:, :r]
        S_r = self.S[:r]
        Vt_r = self.Vt[:r, :]

        # 步骤2：计算降阶算子 A_tilde
        # A_tilde = U_r^T @ Y @ V_r @ S_r^{-1}
        A_tilde = U_r.T @ Y_data @ Vt_r.T @ np.diag(1.0 / S_r)

        # 步骤3：特征分解A_tilde
        eigenvalues, eigenvectors = np.linalg.eig(A_tilde)

        # 步骤4：计算DMD模态
        # Phi = Y @ V_r @ S_r^{-1} @ W
        self.modes = Y_data @ Vt_r.T @ np.diag(1.0 / S_r) @ eigenvectors

        # DMD特征值
        self.eigenvalues = eigenvalues

        # 步骤5：计算初始系数
        # b = Phi^dagger @ x0
        x0 = X_data[:, 0]
        self.amplitudes = np.linalg.lstsq(self.modes, x0, rcond=None)[0]

        return self

    def reconstruct(self, n_timesteps=None):
        """
        重构时间序列

        Parameters:
        -----------
        n_timesteps : int or None
            重构的时间步数。如果为None，使用拟合时的步数

        Returns:
        --------
        X_recon : ndarray (N × n_timesteps)
            重构的数据矩阵
        """
        if n_timesteps is None:
            n_timesteps = len(self.amplitudes)

        X_recon = []
        for n in range(n_timesteps):
            # x_n = Phi @ (Lambda^n * b)
            x_n = np.real(self.modes @ (self.eigenvalues**n * self.amplitudes))
            X_recon.append(x_n)

        return np.column_stack(X_recon)

    def predict(self, x0, n_steps):
        """
        从初始状态x0预测未来n_steps步

        Parameters:
        -----------
        x0 : ndarray (N,)
            初始状态
        n_steps : int
            预测步数

        Returns:
        --------
        X_pred : ndarray (N × n_steps)
            预测的状态序列
        """
        # 计算初始系数
        b = np.linalg.lstsq(self.modes, x0, rcond=None)[0]

        X_pred = []
        for n in range(n_steps):
            x_n = np.real(self.modes @ (self.eigenvalues**n * b))
            X_pred.append(x_n)

        return np.column_stack(X_pred)

    def get_frequencies(self):
        """计算各模态的频率 [rad/s]"""
        omega = np.angle(self.eigenvalues) / self.dt
        return omega

    def get_growth_rates(self):
        """计算各模态的增长率 [1/s]"""
        sigma = np.log(np.abs(self.eigenvalues)) / self.dt
        return sigma

    def get_periods(self):
        """计算各模态的周期 [s]"""
        omega = self.get_frequencies()
        periods = np.zeros_like(omega)
        nonzero = np.abs(omega) > 1e-10
        periods[nonzero] = 2 * np.pi / np.abs(omega[nonzero])
        return periods


# ============================================================================
# Part 2: POD类（从案例4）
# ============================================================================

class POD:
    """POD（本征正交分解）类"""

    def __init__(self):
        self.snapshots = []
        self.U = None
        self.S = None
        self.Vt = None
        self.Phi = None
        self.r = None
        self.mean_snapshot = None

    def add_snapshot(self, h):
        self.snapshots.append(h.copy())

    def compute_POD(self, r=None, energy_threshold=0.99, subtract_mean=True):
        if len(self.snapshots) == 0:
            raise ValueError("No snapshots available.")

        X = np.column_stack(self.snapshots)

        if subtract_mean:
            self.mean_snapshot = np.mean(X, axis=1, keepdims=True)
            X = X - self.mean_snapshot
        else:
            self.mean_snapshot = np.zeros((X.shape[0], 1))

        self.U, self.S, self.Vt = np.linalg.svd(X, full_matrices=False)

        total_energy = np.sum(self.S**2)
        cumulative_energy = np.cumsum(self.S**2)
        energy_ratios = cumulative_energy / total_energy

        if r is None:
            r = np.searchsorted(energy_ratios, energy_threshold) + 1

        self.r = r
        self.Phi = self.U[:, :r]

        return self.Phi

    def get_energy_ratio(self, r):
        if self.S is None:
            raise ValueError("SVD not computed yet.")
        total_energy = np.sum(self.S**2)
        captured_energy = np.sum(self.S[:r]**2)
        return captured_energy / total_energy


# ============================================================================
# Part 3: 辅助函数
# ============================================================================

def collect_snapshots_timeseries(canal, gate, controller, T_total, dt_sim, dt_snapshot, h_target):
    """收集时间序列快照"""
    snapshots = []
    t = 0
    step_count = 0

    while t < T_total:
        if step_count % int(60 / dt_sim) == 0:
            h_d = canal.get_water_level_downstream()
            u = controller.compute(h_target, h_d)
            Q_in = gate.compute_flow(u)
            canal.set_upstream_flow(Q_in)

        canal.step(dt_sim)

        if step_count % int(dt_snapshot / dt_sim) == 0:
            snapshots.append(canal.h.copy())

        t += dt_sim
        step_count += 1

    return snapshots


# ============================================================================
# 主程序 - 4个演示场景
# ============================================================================

def main():
    print("=" * 80)
    print("案例5：动态模态分解（DMD）")
    print("=" * 80)

    # ========================================================================
    # Part 1: DMD模态提取与分析
    # ========================================================================
    print("\n[Part 1] DMD模态提取与分析")
    print("-" * 80)

    # 收集数据
    canal = CanalReach(length=1000, width=5, slope=0.001, roughness=0.025, n_nodes=51)
    gate = GateModel(width=5)
    controller = PIDController(Kp=2.0, Ki=0.1, Kd=5.0, dt=60)

    print("  收集时间序列数据...")
    snapshots = collect_snapshots_timeseries(
        canal, gate, controller,
        T_total=1800,
        dt_sim=10,
        dt_snapshot=10,
        h_target=2.0
    )
    print(f"  收集完成，共{len(snapshots)}个快照")

    # 构造数据矩阵
    X = np.column_stack(snapshots)

    # DMD分解
    print("\n  执行DMD分解...")
    dmd = DMD(svd_rank=10)
    dmd.fit(X, dt=10.0)

    print(f"  DMD模态数: {dmd.modes.shape[1]}")

    # 分析频率和增长率
    frequencies = dmd.get_frequencies()
    growth_rates = dmd.get_growth_rates()
    periods = dmd.get_periods()

    print("\n  前5个DMD模态特性:")
    print(f"  {'模态':<8} {'频率[rad/s]':<15} {'周期[s]':<15} {'增长率[1/s]':<15}")
    print("-" * 60)
    for i in range(min(5, len(frequencies))):
        print(f"  {i+1:<8} {frequencies[i]:<15.6f} {periods[i]:<15.2f} {growth_rates[i]:<15.6f}")

    # 可视化前4个DMD模态
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.ravel()

    for i in range(min(4, dmd.modes.shape[1])):
        mode_real = np.real(dmd.modes[:, i])
        axes[i].plot(canal.x, mode_real, linewidth=2, color=f'C{i}')
        axes[i].set_xlabel('位置 x [m]')
        axes[i].set_ylabel(f'DMD模态 φ_{i+1} (实部)')
        axes[i].set_title(f'DMD模态{i+1}: ω={frequencies[i]:.4f} rad/s, σ={growth_rates[i]:.4f} 1/s')
        axes[i].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('part1_dmd_modes.png', dpi=150, bbox_inches='tight')
    print("\n图表已保存: part1_dmd_modes.png")
    plt.close()

    # ========================================================================
    # Part 2: DMD vs POD对比
    # ========================================================================
    print("\n[Part 2] DMD vs POD对比")
    print("-" * 80)

    # POD分解
    print("\n  执行POD分解...")
    pod = POD()
    for snapshot in snapshots:
        pod.add_snapshot(snapshot)
    pod.compute_POD(r=10, subtract_mean=True)

    print(f"  POD模态数: {pod.Phi.shape[1]}")

    # 重构对比
    print("\n  重构精度对比...")
    X_dmd = dmd.reconstruct(len(snapshots))
    
    # POD重构
    X_pod = np.zeros_like(X)
    for i, snapshot in enumerate(snapshots):
        a = pod.Phi.T @ (snapshot - pod.mean_snapshot.ravel())
        X_pod[:, i] = pod.Phi @ a + pod.mean_snapshot.ravel()

    # 计算误差
    error_dmd = np.linalg.norm(X - X_dmd, 'fro') / np.linalg.norm(X, 'fro')
    error_pod = np.linalg.norm(X - X_pod, 'fro') / np.linalg.norm(X, 'fro')

    print(f"  DMD重构误差: {error_dmd:.6f}")
    print(f"  POD重构误差: {error_pod:.6f}")

    # 可视化对比
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 子图1：DMD模态1 vs POD模态1
    axes[0, 0].plot(canal.x, np.real(dmd.modes[:, 0]), 'b-', linewidth=2, label='DMD模态1')
    axes[0, 0].plot(canal.x, pod.Phi[:, 0], 'r--', linewidth=2, label='POD模态1')
    axes[0, 0].set_xlabel('位置 x [m]')
    axes[0, 0].set_ylabel('模态幅值')
    axes[0, 0].set_title('模态对比：第1模态')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)

    # 子图2：重构误差对比
    methods = ['DMD', 'POD']
    errors = [error_dmd, error_pod]
    axes[0, 1].bar(methods, errors, color=['blue', 'red'], alpha=0.7)
    axes[0, 1].set_ylabel('重构误差（相对Frobenius范数）')
    axes[0, 1].set_title('重构精度对比')
    axes[0, 1].grid(True, alpha=0.3, axis='y')

    # 子图3：DMD频率谱
    axes[1, 0].stem(np.arange(len(frequencies)), np.abs(frequencies), basefmt=' ')
    axes[1, 0].set_xlabel('模态索引')
    axes[1, 0].set_ylabel('频率 [rad/s]')
    axes[1, 0].set_title('DMD频率谱')
    axes[1, 0].grid(True, alpha=0.3)

    # 子图4：POD能量分布
    energy_fraction = pod.S**2 / np.sum(pod.S**2)
    axes[1, 1].bar(np.arange(len(energy_fraction[:10])), energy_fraction[:10], color='red', alpha=0.7)
    axes[1, 1].set_xlabel('模态索引')
    axes[1, 1].set_ylabel('能量占比')
    axes[1, 1].set_title('POD能量分布')
    axes[1, 1].grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig('part2_dmd_vs_pod.png', dpi=150, bbox_inches='tight')
    print("\n图表已保存: part2_dmd_vs_pod.png")
    plt.close()

    # ========================================================================
    # Part 3: DMD预测能力测试
    # ========================================================================
    print("\n[Part 3] DMD预测能力测试")
    print("-" * 80)

    # 使用前120个快照训练
    n_train = 120
    X_train = X[:, :n_train]

    # 重新训练DMD
    dmd_pred = DMD(svd_rank=10)
    dmd_pred.fit(X_train, dt=10.0)

    # 预测未来60步（10分钟）
    n_predict = 60
    x0 = X_train[:, -1]
    X_predicted = dmd_pred.predict(x0, n_predict)

    # 实际数据（用于验证）
    X_actual = X[:, n_train:n_train+n_predict]

    # 计算预测误差（随时间）
    prediction_errors = []
    for i in range(n_predict):
        error = np.linalg.norm(X_predicted[:, i] - X_actual[:, i]) / np.linalg.norm(X_actual[:, i])
        prediction_errors.append(error)

    print(f"\n  预测误差:")
    print(f"  1分钟 (6步): {prediction_errors[5]:.4f}")
    print(f"  2分钟 (12步): {prediction_errors[11]:.4f}")
    print(f"  5分钟 (30步): {prediction_errors[29]:.4f}")

    # 可视化
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))

    # 子图1：下游水位预测
    time_train = np.arange(n_train) * 10 / 60
    time_pred = (n_train + np.arange(n_predict)) * 10 / 60

    axes[0].plot(time_train, X_train[-1, :], 'b-', linewidth=2, label='训练数据')
    axes[0].plot(time_pred, X_predicted[-1, :], 'r--', linewidth=2, label='DMD预测')
    axes[0].plot(time_pred, X_actual[-1, :], 'g:', linewidth=2, label='实际值')
    axes[0].axvline(n_train * 10 / 60, color='k', linestyle='--', alpha=0.5, label='预测起点')
    axes[0].set_xlabel('时间 [min]')
    axes[0].set_ylabel('下游水位 [m]')
    axes[0].set_title('Part 3: DMD预测能力 - 下游水位')
    axes[0].legend(loc='best')
    axes[0].grid(True, alpha=0.3)

    # 子图2：预测误差随时间变化
    axes[1].plot(np.arange(n_predict) * 10 / 60, prediction_errors, 'o-', linewidth=2, color='purple')
    axes[1].set_xlabel('预测时长 [min]')
    axes[1].set_ylabel('相对预测误差')
    axes[1].set_title('预测误差随时间变化')
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('part3_dmd_prediction.png', dpi=150, bbox_inches='tight')
    print("\n图表已保存: part3_dmd_prediction.png")
    plt.close()

    # ========================================================================
    # Part 4: 性能总结
    # ========================================================================
    print("\n[Part 4] 性能总结")
    print("=" * 80)

    print("\nDMD vs POD性能对比:")
    print(f"{'指标':<25} {'DMD':<20} {'POD':<20}")
    print("-" * 65)
    print(f"{'重构误差':<25} {error_dmd:<20.6f} {error_pod:<20.6f}")
    print(f"{'包含时间信息':<25} {'是（频率+增长率）':<20} {'否':<20}")
    print(f"{'预测能力':<25} {'强':<20} {'弱':<20}")
    print(f"{'主要用途':<25} {'动力学分析、预测':<20} {'数据压缩、降阶':<20}")

    print(f"\nDMD主导频率:")
    print(f"  模态1: {frequencies[0]:.6f} rad/s (周期: {periods[0]:.2f} s)")
    print(f"  模态2: {frequencies[1]:.6f} rad/s (周期: {periods[1]:.2f} s)")

    print("\n" + "=" * 80)
    print("案例5完成！所有3个部分的图表已保存。")
    print("=" * 80)


if __name__ == '__main__':
    main()
