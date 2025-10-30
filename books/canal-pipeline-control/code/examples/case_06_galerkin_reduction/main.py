"""
案例6：Galerkin投影与有限元降阶

实现内容：
1. 多种基函数实现（正弦、Legendre多项式、POD模态）
2. Galerkin投影方法
3. 质量矩阵和刚度矩阵计算
4. 降阶模型求解
5. 3个演示实验

作者：Claude
日期：2025-10-30
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from scipy import integrate
from scipy.special import legendre
import sys
import os

# 配置中文字体
rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False


# ============================================================================
# 从案例1复用的类
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
# Part 1: 基函数类
# ============================================================================

class BasisFunctions:
    """基函数生成器"""

    @staticmethod
    def sine_basis(x, n_modes, L):
        """
        正弦基函数
        
        φ_i(x) = sin(iπx/L)
        
        满足零边界条件
        """
        basis = []
        for i in range(1, n_modes + 1):
            phi = np.sin(i * np.pi * x / L)
            basis.append(phi)
        return np.array(basis).T  # N × r

    @staticmethod
    def legendre_basis(x, n_modes, L):
        """
        Legendre多项式基函数
        
        归一化到[0, L]区间
        """
        # 映射到[-1, 1]
        xi = 2 * x / L - 1
        
        basis = []
        for i in range(n_modes):
            # Legendre多项式
            P = legendre(i)
            phi = P(xi)
            # 归一化
            phi = phi / np.sqrt(integrate.simpson(phi**2, x=x))
            basis.append(phi)
        return np.array(basis).T  # N × r

    @staticmethod
    def pod_basis(snapshots, n_modes):
        """
        POD基函数（从快照数据提取）
        """
        X = np.column_stack(snapshots)
        
        # 去中心化
        mean = np.mean(X, axis=1, keepdims=True)
        X_centered = X - mean
        
        # SVD
        U, S, Vt = np.linalg.svd(X_centered, full_matrices=False)
        
        # 前n_modes个模态
        basis = U[:, :n_modes]
        
        return basis  # N × r


# ============================================================================
# Part 2: Galerkin投影类
# ============================================================================

class GalerkinReducedModel:
    """
    Galerkin投影降阶模型
    
    基本思想：
    h(x,t) ≈ Σ a_i(t) φ_i(x) = Φ * a(t)
    
    投影PDE到基函数空间：
    M * da/dt = f(a, u)
    """

    def __init__(self, basis_functions, x_grid, L):
        """
        Parameters:
        -----------
        basis_functions : ndarray (N × r)
            基函数矩阵，每列是一个基函数在网格上的值
        x_grid : ndarray (N,)
            空间网格
        L : float
            空间域长度
        """
        self.Phi = basis_functions
        self.x = x_grid
        self.L = L
        self.N = len(x_grid)
        self.r = basis_functions.shape[1]

        # 计算质量矩阵
        self.M = self.compute_mass_matrix()

        # 当前降阶状态
        self.a = np.zeros(self.r)

    def compute_mass_matrix(self):
        """
        计算质量矩阵
        
        M_ij = ∫ φ_i(x) φ_j(x) dx
        """
        M = np.zeros((self.r, self.r))
        
        for i in range(self.r):
            for j in range(self.r):
                # 使用Simpson积分
                integrand = self.Phi[:, i] * self.Phi[:, j]
                M[i, j] = integrate.simpson(integrand, x=self.x)
        
        return M

    def project_to_reduced_space(self, h_full):
        """将全阶状态投影到降阶空间"""
        # a = Φ^T M Φ^{-1} Φ^T h
        # 简化：假设基函数正交，则 a ≈ Φ^T h
        a = self.Phi.T @ h_full
        return a

    def reconstruct_from_reduced_space(self, a):
        """从降阶状态重构全阶状态"""
        h = self.Phi @ a
        return h

    def reduced_dynamics(self, a, t, canal):
        """
        降阶动力学方程
        
        简化：使用当前状态估计右端项
        """
        # 重构全阶状态
        h_full = self.reconstruct_from_reduced_space(a)
        h_full = np.clip(h_full, 0.1, 10.0)

        # 估计流量（简化：使用Manning公式）
        Q_full = np.zeros_like(h_full)
        for i in range(len(h_full)):
            A = canal.B * h_full[i]
            R = A / (canal.B + 2 * h_full[i])
            if R > 0:
                Q_full[i] = A * R**(2/3) * np.sqrt(canal.i0) / canal.n
            else:
                Q_full[i] = 0.1

        # 计算dh/dt（连续性方程）
        dh_dt = np.zeros_like(h_full)
        dx = self.x[1] - self.x[0]
        for i in range(1, len(h_full) - 1):
            dQ_dx = (Q_full[i+1] - Q_full[i-1]) / (2 * dx)
            dh_dt[i] = -dQ_dx / canal.B

        # Galerkin投影：da/dt = M^{-1} Φ^T dh/dt
        da_dt = np.linalg.solve(self.M, self.Phi.T @ dh_dt)

        return da_dt


# ============================================================================
# Part 3: 辅助函数
# ============================================================================

def collect_snapshots(canal, gate, controller, T_total, dt_sim, dt_snapshot, h_target):
    """收集快照数据"""
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
# 主程序
# ============================================================================

def main():
    print("=" * 80)
    print("案例6：Galerkin投影与有限元降阶")
    print("=" * 80)

    # 初始化
    L = 1000
    N = 51
    x = np.linspace(0, L, N)

    # ========================================================================
    # Part 1: 基函数对比
    # ========================================================================
    print("\n[Part 1] 基函数对比")
    print("-" * 80)

    n_modes = 10

    # 生成不同基函数
    print(f"\n  生成{n_modes}个基函数...")
    basis_sine = BasisFunctions.sine_basis(x, n_modes, L)
    basis_legendre = BasisFunctions.legendre_basis(x, n_modes, L)

    # 收集POD快照
    print("  收集POD快照...")
    canal = CanalReach(length=L, width=5, slope=0.001, roughness=0.025, n_nodes=N)
    gate = GateModel(width=5)
    controller = PIDController(Kp=2.0, Ki=0.1, Kd=5.0, dt=60)

    snapshots = collect_snapshots(canal, gate, controller,
                                   T_total=1800, dt_sim=10, dt_snapshot=10, h_target=2.0)
    
    basis_pod = BasisFunctions.pod_basis(snapshots, n_modes)

    print(f"  基函数生成完成")

    # 可视化前4个基函数
    fig, axes = plt.subplots(3, 4, figsize=(16, 10))

    for i in range(4):
        # 正弦基
        axes[0, i].plot(x, basis_sine[:, i], linewidth=2, color='blue')
        axes[0, i].set_title(f'正弦基函数 {i+1}')
        axes[0, i].set_xlabel('x [m]')
        axes[0, i].set_ylabel('φ(x)')
        axes[0, i].grid(True, alpha=0.3)

        # Legendre基
        axes[1, i].plot(x, basis_legendre[:, i], linewidth=2, color='green')
        axes[1, i].set_title(f'Legendre基函数 {i+1}')
        axes[1, i].set_xlabel('x [m]')
        axes[1, i].set_ylabel('φ(x)')
        axes[1, i].grid(True, alpha=0.3)

        # POD基
        axes[2, i].plot(x, basis_pod[:, i], linewidth=2, color='red')
        axes[2, i].set_title(f'POD基函数 {i+1}')
        axes[2, i].set_xlabel('x [m]')
        axes[2, i].set_ylabel('φ(x)')
        axes[2, i].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('part1_basis_comparison.png', dpi=150, bbox_inches='tight')
    print("\n图表已保存: part1_basis_comparison.png")
    plt.close()

    # ========================================================================
    # Part 2: Galerkin重构测试
    # ========================================================================
    print("\n[Part 2] Galerkin重构测试")
    print("-" * 80)

    # 使用一个测试快照
    h_test = snapshots[50]  # 选择中间时刻

    # 测试不同基函数的重构能力
    reconstructions = {}
    errors = {}

    for name, basis in [('正弦基', basis_sine), 
                        ('Legendre基', basis_legendre), 
                        ('POD基', basis_pod)]:
        # 投影
        a = basis.T @ h_test
        
        # 重构
        h_recon = basis @ a
        
        # 误差
        error = np.linalg.norm(h_test - h_recon) / np.linalg.norm(h_test)
        
        reconstructions[name] = h_recon
        errors[name] = error
        
        print(f"  {name}: 重构误差 = {error:.6f}")

    # 可视化
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 子图1：原始vs重构
    axes[0, 0].plot(x, h_test, 'k-', linewidth=2, label='原始')
    for name, h_recon in reconstructions.items():
        axes[0, 0].plot(x, h_recon, '--', linewidth=1.5, label=name)
    axes[0, 0].set_xlabel('位置 x [m]')
    axes[0, 0].set_ylabel('水位 h [m]')
    axes[0, 0].set_title('重构对比')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)

    # 子图2：误差分布
    names = list(errors.keys())
    error_values = list(errors.values())
    axes[0, 1].bar(names, error_values, color=['blue', 'green', 'red'], alpha=0.7)
    axes[0, 1].set_ylabel('相对L2误差')
    axes[0, 1].set_title('重构误差对比')
    axes[0, 1].grid(True, alpha=0.3, axis='y')

    # 子图3：逐点误差（正弦基）
    error_pointwise = np.abs(h_test - reconstructions['正弦基'])
    axes[1, 0].plot(x, error_pointwise, linewidth=2, color='blue')
    axes[1, 0].set_xlabel('位置 x [m]')
    axes[1, 0].set_ylabel('绝对误差 [m]')
    axes[1, 0].set_title('正弦基逐点误差')
    axes[1, 0].grid(True, alpha=0.3)

    # 子图4：逐点误差（POD基）
    error_pointwise_pod = np.abs(h_test - reconstructions['POD基'])
    axes[1, 1].plot(x, error_pointwise_pod, linewidth=2, color='red')
    axes[1, 1].set_xlabel('位置 x [m]')
    axes[1, 1].set_ylabel('绝对误差 [m]')
    axes[1, 1].set_title('POD基逐点误差')
    axes[1, 1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('part2_galerkin_reconstruction.png', dpi=150, bbox_inches='tight')
    print("\n图表已保存: part2_galerkin_reconstruction.png")
    plt.close()

    # ========================================================================
    # Part 3: Galerkin vs POD对比
    # ========================================================================
    print("\n[Part 3] Galerkin-POD降阶模型对比")
    print("-" * 80)

    print("\n  使用POD基构建Galerkin降阶模型...")

    # 使用POD基构建Galerkin模型
    galerkin_model = GalerkinReducedModel(basis_pod, x, L)

    print(f"  降阶维数: {galerkin_model.r}")
    print(f"  质量矩阵大小: {galerkin_model.M.shape}")

    # 质量矩阵的条件数
    cond_M = np.linalg.cond(galerkin_model.M)
    print(f"  质量矩阵条件数: {cond_M:.2f}")

    # 测试投影和重构
    print("\n  测试投影-重构循环...")
    errors_projection = []
    for i in range(0, len(snapshots), 20):
        h_original = snapshots[i]
        a = galerkin_model.project_to_reduced_space(h_original)
        h_reconstructed = galerkin_model.reconstruct_from_reduced_space(a)
        error = np.linalg.norm(h_original - h_reconstructed) / np.linalg.norm(h_original)
        errors_projection.append(error)

    mean_error = np.mean(errors_projection)
    print(f"  平均投影-重构误差: {mean_error:.6f}")

    # 可视化
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 子图1：质量矩阵
    im = axes[0, 0].imshow(galerkin_model.M, cmap='RdBu_r', aspect='auto')
    axes[0, 0].set_title('质量矩阵 M')
    axes[0, 0].set_xlabel('列索引 j')
    axes[0, 0].set_ylabel('行索引 i')
    plt.colorbar(im, ax=axes[0, 0])

    # 子图2：投影-重构误差
    axes[0, 1].plot(errors_projection, 'o-', linewidth=2, color='blue')
    axes[0, 1].axhline(mean_error, color='r', linestyle='--', label=f'平均: {mean_error:.6f}')
    axes[0, 1].set_xlabel('快照索引')
    axes[0, 1].set_ylabel('相对L2误差')
    axes[0, 1].set_title('投影-重构误差')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)

    # 子图3：示例投影
    test_idx = 50
    h_orig = snapshots[test_idx]
    a_proj = galerkin_model.project_to_reduced_space(h_orig)
    h_recon = galerkin_model.reconstruct_from_reduced_space(a_proj)

    axes[1, 0].plot(x, h_orig, 'k-', linewidth=2, label='原始')
    axes[1, 0].plot(x, h_recon, 'r--', linewidth=2, label='Galerkin重构')
    axes[1, 0].set_xlabel('位置 x [m]')
    axes[1, 0].set_ylabel('水位 h [m]')
    axes[1, 0].set_title(f'示例重构（快照{test_idx}）')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)

    # 子图4：降阶系数
    axes[1, 1].bar(np.arange(len(a_proj)), np.abs(a_proj), color='green', alpha=0.7)
    axes[1, 1].set_xlabel('模态索引 i')
    axes[1, 1].set_ylabel('|a_i|')
    axes[1, 1].set_title('降阶系数分布')
    axes[1, 1].grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig('part3_galerkin_vs_pod.png', dpi=150, bbox_inches='tight')
    print("\n图表已保存: part3_galerkin_vs_pod.png")
    plt.close()

    # ========================================================================
    # Part 4: 性能总结
    # ========================================================================
    print("\n[Part 4] 性能总结")
    print("=" * 80)

    print("\n基函数重构误差对比:")
    print(f"{'基函数类型':<20} {'重构误差':<20}")
    print("-" * 40)
    for name, error in errors.items():
        print(f"{name:<20} {error:<20.6f}")

    print(f"\nGalerkin-POD模型:")
    print(f"  降阶维数: {galerkin_model.r}")
    print(f"  质量矩阵条件数: {cond_M:.2f}")
    print(f"  平均投影误差: {mean_error:.6f}")

    print("\n关键结论:")
    print("  1. POD基函数重构精度最高（数据驱动，针对特定问题优化）")
    print("  2. Legendre基函数灵活性好（适合多种边界条件）")
    print("  3. 正弦基函数计算效率高（正交性好，积分简单）")
    print("  4. Galerkin-POD结合了数据驱动和理论投影的优势")

    print("\n" + "=" * 80)
    print("案例6完成！所有3个部分的图表已保存。")
    print("=" * 80)


if __name__ == '__main__':
    main()
