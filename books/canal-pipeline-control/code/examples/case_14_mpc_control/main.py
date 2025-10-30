#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
案例14：模型预测控制（MPC）

本案例实现了模型预测控制算法，应用于运河系统控制。

主要内容：
1. 线性MPC基础（质量-弹簧-阻尼系统）
2. 运河系统MPC控制
3. 约束处理与优化
4. 多目标MPC

作者：Claude
日期：2025
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize, Bounds, LinearConstraint
from scipy.linalg import solve_discrete_are
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


# ============================================================================
# MPC控制器类
# ============================================================================

class ModelPredictiveController:
    """
    线性模型预测控制器

    适用于离散线性系统：
        x(k+1) = A x(k) + B u(k)
        y(k) = C x(k)
    """

    def __init__(self, A, B, C, Np, Nc, Q, R, S=None,
                 u_min=None, u_max=None,
                 du_min=None, du_max=None,
                 x_min=None, x_max=None,
                 y_min=None, y_max=None):
        """
        参数:
            A, B, C: 状态空间矩阵
            Np: 预测时域
            Nc: 控制时域
            Q: 跟踪误差权重矩阵（输出）
            R: 控制量权重矩阵
            S: 控制增量权重矩阵
            u_min, u_max: 控制约束
            du_min, du_max: 控制增量约束
            x_min, x_max: 状态约束
            y_min, y_max: 输出约束
        """
        self.A = np.array(A)
        self.B = np.array(B)
        self.C = np.array(C)

        self.Np = Np
        self.Nc = Nc

        self.Q = np.array(Q)
        self.R = np.array(R)
        self.S = np.array(S) if S is not None else np.zeros_like(R)

        # 维度
        self.nx = self.A.shape[0]  # 状态维度
        self.nu = self.B.shape[1]  # 控制维度
        self.ny = self.C.shape[0]  # 输出维度

        # 约束
        self.u_min = u_min if u_min is not None else -np.inf * np.ones(self.nu)
        self.u_max = u_max if u_max is not None else np.inf * np.ones(self.nu)
        self.du_min = du_min if du_min is not None else -np.inf * np.ones(self.nu)
        self.du_max = du_max if du_max is not None else np.inf * np.ones(self.nu)
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max

        # 上一时刻控制
        self.u_prev = np.zeros(self.nu)

        # 构建预测矩阵
        self._build_prediction_matrices()

    def _build_prediction_matrices(self):
        """构建预测矩阵 Sx, Su, Psi, Theta"""
        nx, nu, ny = self.nx, self.nu, self.ny
        Np, Nc = self.Np, self.Nc

        # Sx: [A; A^2; ...; A^Np]
        self.Sx = np.zeros((nx * Np, nx))
        A_power = self.A.copy()
        for i in range(Np):
            self.Sx[i*nx:(i+1)*nx, :] = A_power
            A_power = A_power @ self.A

        # Su: 下三角块矩阵
        self.Su = np.zeros((nx * Np, nu * Nc))
        for i in range(Np):
            for j in range(min(i+1, Nc)):
                if i == j:
                    self.Su[i*nx:(i+1)*nx, j*nu:(j+1)*nu] = self.B
                else:
                    A_power = np.linalg.matrix_power(self.A, i - j)
                    self.Su[i*nx:(i+1)*nx, j*nu:(j+1)*nu] = A_power @ self.B

        # Psi = C * Sx, Theta = C * Su
        C_block = np.kron(np.eye(Np), self.C)
        self.Psi = C_block @ self.Sx
        self.Theta = C_block @ self.Su

    def _build_qp_matrices(self, x0, r_ref):
        """
        构建QP问题的H和f矩阵

        min_U  1/2 U' H U + f' U
        """
        # 参考轨迹向量
        R_ref = np.tile(r_ref, self.Np) if r_ref.ndim == 1 else r_ref

        # H = 2 * (Theta' Q Theta + R_bar + S_bar)
        Q_bar = np.kron(np.eye(self.Np), self.Q)
        R_bar = np.kron(np.eye(self.Nc), self.R)

        # 控制增量矩阵（离散差分）
        if np.any(self.S != 0):
            D = np.eye(self.Nc * self.nu) - np.eye(self.Nc * self.nu, k=-self.nu)
            S_bar = D.T @ np.kron(np.eye(self.Nc), self.S) @ D
        else:
            S_bar = np.zeros((self.Nc * self.nu, self.Nc * self.nu))

        H = 2 * (self.Theta.T @ Q_bar @ self.Theta + R_bar + S_bar)

        # f = 2 * Theta' Q (Psi x0 - R_ref)
        f = 2 * self.Theta.T @ Q_bar @ (self.Psi @ x0 - R_ref)

        # 确保H对称
        H = (H + H.T) / 2

        return H, f

    def _build_constraints(self, x0):
        """构建约束"""
        constraints = []
        bounds_list = []

        # 1. 控制量约束: u_min <= u <= u_max
        for i in range(self.Nc):
            for j in range(self.nu):
                bounds_list.append((self.u_min[j], self.u_max[j]))

        # 2. 控制增量约束: du_min <= u(k) - u(k-1) <= du_max
        if not np.all(np.isinf(self.du_min)) or not np.all(np.isinf(self.du_max)):
            for i in range(self.Nc):
                for j in range(self.nu):
                    idx = i * self.nu + j
                    u_prev_j = self.u_prev[j] if i == 0 else 0  # 只有第一步考虑u_prev

                    if i == 0:
                        # du(0) = u(0) - u_prev
                        lb = self.du_min[j] + u_prev_j
                        ub = self.du_max[j] + u_prev_j
                        bounds_list[idx] = (max(bounds_list[idx][0], lb),
                                           min(bounds_list[idx][1], ub))

        # 3. 状态约束（如果指定）
        if self.x_min is not None or self.x_max is not None:
            # x = Sx x0 + Su U
            # x_min <= Sx x0 + Su U <= x_max
            # -Su U <= -x_min + Sx x0
            # Su U <= x_max - Sx x0

            x_pred_base = self.Sx @ x0

            if self.x_min is not None:
                A_ineq = -self.Su
                b_ineq = -np.tile(self.x_min, self.Np) + x_pred_base
                constraints.append(LinearConstraint(A_ineq, -np.inf, b_ineq))

            if self.x_max is not None:
                A_ineq = self.Su
                b_ineq = np.tile(self.x_max, self.Np) - x_pred_base
                constraints.append(LinearConstraint(A_ineq, -np.inf, b_ineq))

        # 4. 输出约束（如果指定）
        if self.y_min is not None or self.y_max is not None:
            # y = Psi x0 + Theta U
            y_pred_base = self.Psi @ x0

            if self.y_min is not None:
                A_ineq = -self.Theta
                b_ineq = -np.tile(self.y_min, self.Np) + y_pred_base
                constraints.append(LinearConstraint(A_ineq, -np.inf, b_ineq))

            if self.y_max is not None:
                A_ineq = self.Theta
                b_ineq = np.tile(self.y_max, self.Np) - y_pred_base
                constraints.append(LinearConstraint(A_ineq, -np.inf, b_ineq))

        return Bounds([b[0] for b in bounds_list], [b[1] for b in bounds_list]), constraints

    def solve(self, x0, r_ref, u_prev=None):
        """
        求解MPC优化问题

        参数:
            x0: 当前状态
            r_ref: 参考轨迹（标量或向量）
            u_prev: 上一时刻控制（用于增量约束）

        返回:
            u_opt: 最优控制序列的第一个值
            U_opt: 完整最优控制序列
        """
        if u_prev is not None:
            self.u_prev = u_prev

        # 构建QP
        H, f = self._build_qp_matrices(x0, r_ref)

        # 构建约束
        bounds, constraints = self._build_constraints(x0)

        # 初始猜测（上次的解或零）
        U0 = np.zeros(self.Nc * self.nu)

        # 目标函数
        def objective(U):
            return 0.5 * U @ H @ U + f @ U

        # 梯度
        def gradient(U):
            return H @ U + f

        # 求解
        result = minimize(
            objective,
            U0,
            method='SLSQP',
            jac=gradient,
            bounds=bounds,
            constraints=constraints,
            options={'disp': False, 'maxiter': 500}
        )

        if not result.success:
            print(f"⚠️ 优化失败: {result.message}")

        U_opt = result.x

        # 提取第一个控制
        u_opt = U_opt[:self.nu]

        return u_opt, U_opt


# ============================================================================
# 简化运河模型
# ============================================================================

class SimplifiedCanalModel:
    """
    简化的运河渠段线性模型

    状态: x = [h, Q]' (水位, 流量)
    控制: u = Q_in (入流)
    输出: y = h (水位)
    """

    def __init__(self, L=1000, B=5.0, S0=0.001, n=0.025, h0=2.0, Q0=10.0, dt=10.0):
        """
        参数:
            L: 渠段长度 (m)
            B: 渠底宽度 (m)
            S0: 渠底坡度
            n: 曼宁系数
            h0: 平衡水位 (m)
            Q0: 平衡流量 (m³/s)
            dt: 采样时间 (s)
        """
        self.L = L
        self.B = B
        self.S0 = S0
        self.n = n
        self.h0 = h0
        self.Q0 = Q0
        self.dt = dt
        self.g = 9.81

        # 线性化系数（在平衡点附近）
        A = B * h0
        P = B + 2 * h0
        R = A / P
        V = Q0 / A

        # 连续时间线性化
        a11 = -V / L
        a12 = 1 / (B * L)
        a21 = -self.g * A / L
        a22 = -2 * V / L - 2 * self.g * n**2 * V / (R**(4/3))

        b1 = 1 / (B * L)
        b2 = self.g * A / L

        Ac = np.array([[a11, a12],
                       [a21, a22]])
        Bc = np.array([[b1],
                       [b2]])
        Cc = np.array([[1, 0]])  # 输出是水位

        # 离散化（零阶保持）
        self.A = np.eye(2) + Ac * dt
        self.B = Bc * dt
        self.C = Cc

    def simulate(self, x0, U, disturbance=None):
        """
        仿真系统响应

        参数:
            x0: 初始状态 [h, Q]
            U: 控制序列 (N,)
            disturbance: 扰动序列 (N,)

        返回:
            X: 状态轨迹 (N+1, 2)
            Y: 输出轨迹 (N+1,)
        """
        N = len(U)
        X = np.zeros((N+1, 2))
        Y = np.zeros(N+1)

        X[0] = x0
        Y[0] = self.C @ x0

        for k in range(N):
            u = U[k]
            if disturbance is not None and k < len(disturbance):
                u += disturbance[k]

            X[k+1] = self.A @ X[k] + self.B.flatten() * u
            Y[k+1] = self.C @ X[k+1]

        return X, Y


# ============================================================================
# Part 1: 线性MPC基础
# ============================================================================

def part1_linear_mpc_basics():
    """
    Part 1: 线性MPC基础

    质量-弹簧-阻尼系统
    """
    print("=" * 60)
    print("Part 1: 线性MPC基础（质量-弹簧-阻尼系统）")
    print("=" * 60)

    # 系统参数
    m = 1.0  # 质量
    k = 1.0  # 弹簧系数
    c = 0.5  # 阻尼系数

    # 连续时间状态空间
    Ac = np.array([[0, 1],
                   [-k/m, -c/m]])
    Bc = np.array([[0],
                   [1/m]])
    Cc = np.array([[1, 0]])  # 位置输出

    # 离散化
    dt = 0.1
    A = np.eye(2) + Ac * dt
    B = Bc * dt
    C = Cc

    # MPC参数
    Np = 20  # 预测时域
    Nc = 10  # 控制时域
    Q = np.array([[10.0]])  # 跟踪权重
    R = np.array([[0.1]])   # 控制权重
    S = np.array([[0.5]])   # 控制增量权重

    # 约束
    u_min = np.array([-5.0])
    u_max = np.array([5.0])
    y_min = np.array([-2.0])
    y_max = np.array([2.0])

    # 创建MPC控制器（有约束）
    mpc_constrained = ModelPredictiveController(
        A, B, C, Np, Nc, Q, R, S,
        u_min=u_min, u_max=u_max,
        y_min=y_min, y_max=y_max
    )

    # 创建MPC控制器（无约束）
    mpc_unconstrained = ModelPredictiveController(
        A, B, C, Np, Nc, Q, R, S
    )

    # 仿真参数
    T_sim = 10.0
    t = np.arange(0, T_sim, dt)
    N = len(t)

    # 参考轨迹（阶跃）
    r_ref = np.ones(N) * 1.0
    r_ref[N//2:] = -0.5  # 中途改变

    # 初始状态
    x0 = np.array([0.0, 0.0])

    # 仿真（有约束MPC）
    X_constrained = np.zeros((N, 2))
    Y_constrained = np.zeros(N)
    U_constrained = np.zeros(N)
    X_constrained[0] = x0
    Y_constrained[0] = C @ x0

    x_current = x0.copy()
    u_prev = np.zeros(1)

    for k in range(N-1):
        # 求解MPC
        u_opt, _ = mpc_constrained.solve(x_current, r_ref[k], u_prev)

        # 应用控制
        x_current = A @ x_current + B.flatten() * u_opt
        y_current = C @ x_current

        U_constrained[k] = u_opt[0]
        X_constrained[k+1] = x_current
        Y_constrained[k+1] = y_current[0]
        u_prev = u_opt

    # 仿真（无约束MPC）
    X_unconstrained = np.zeros((N, 2))
    Y_unconstrained = np.zeros(N)
    U_unconstrained = np.zeros(N)
    X_unconstrained[0] = x0
    Y_unconstrained[0] = C @ x0

    x_current = x0.copy()
    u_prev = np.zeros(1)

    for k in range(N-1):
        u_opt, _ = mpc_unconstrained.solve(x_current, r_ref[k], u_prev)

        x_current = A @ x_current + B.flatten() * u_opt
        y_current = C @ x_current

        U_unconstrained[k] = u_opt[0]
        X_unconstrained[k+1] = x_current
        Y_unconstrained[k+1] = y_current[0]
        u_prev = u_opt

    # 计算性能指标
    ise_constrained = np.sum((Y_constrained - r_ref)**2) * dt
    ise_unconstrained = np.sum((Y_unconstrained - r_ref)**2) * dt
    energy_constrained = np.sum(U_constrained**2) * dt
    energy_unconstrained = np.sum(U_unconstrained**2) * dt

    print(f"\n性能对比:")
    print(f"  有约束MPC - ISE: {ise_constrained:.4f}, 控制能量: {energy_constrained:.4f}")
    print(f"  无约束MPC - ISE: {ise_unconstrained:.4f}, 控制能量: {energy_unconstrained:.4f}")

    # 可视化
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))

    # 子图1: 位置跟踪
    ax = axes[0]
    ax.plot(t, r_ref, 'k--', linewidth=2, label='参考轨迹')
    ax.plot(t, Y_constrained, 'b-', linewidth=2, label='有约束MPC')
    ax.plot(t, Y_unconstrained, 'r-', linewidth=2, alpha=0.7, label='无约束MPC')
    ax.axhline(y_max, color='orange', linestyle=':', linewidth=1.5, label='输出约束')
    ax.axhline(y_min, color='orange', linestyle=':', linewidth=1.5)
    ax.set_xlabel('时间 (s)')
    ax.set_ylabel('位置 (m)')
    ax.set_title(f'位置跟踪（有约束ISE={ise_constrained:.2f}, 无约束ISE={ise_unconstrained:.2f}）')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 子图2: 控制输入
    ax = axes[1]
    ax.plot(t, U_constrained, 'b-', linewidth=2, label='有约束MPC')
    ax.plot(t, U_unconstrained, 'r-', linewidth=2, alpha=0.7, label='无约束MPC')
    ax.axhline(u_max, color='red', linestyle='--', linewidth=1.5, label='控制约束')
    ax.axhline(u_min, color='red', linestyle='--', linewidth=1.5)
    ax.set_xlabel('时间 (s)')
    ax.set_ylabel('控制力 (N)')
    ax.set_title('控制输入对比')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 子图3: 控制增量
    ax = axes[2]
    du_constrained = np.diff(U_constrained, prepend=0)
    du_unconstrained = np.diff(U_unconstrained, prepend=0)
    ax.plot(t, du_constrained, 'b-', linewidth=2, label='有约束MPC')
    ax.plot(t, du_unconstrained, 'r-', linewidth=2, alpha=0.7, label='无约束MPC')
    ax.set_xlabel('时间 (s)')
    ax.set_ylabel('控制增量 ΔU (N)')
    ax.set_title('控制平滑性对比')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('part1_linear_mpc.png', dpi=300, bbox_inches='tight')
    print("图像已保存: part1_linear_mpc.png\n")

    return mpc_constrained


# ============================================================================
# Part 2: 运河系统MPC控制
# ============================================================================

def part2_canal_mpc_control():
    """
    Part 2: 运河系统MPC控制

    水位跟踪 + 流量平滑
    """
    print("=" * 60)
    print("Part 2: 运河系统MPC控制")
    print("=" * 60)

    # 创建运河模型
    canal = SimplifiedCanalModel(L=1000, B=5.0, h0=2.0, Q0=10.0, dt=10.0)

    # MPC参数
    Np = 30  # 预测时域（30步 = 300秒）
    Nc = 15  # 控制时域
    Q = np.array([[50.0]])  # 水位跟踪权重
    R = np.array([[0.1]])   # 控制权重
    S = np.array([[1.0]])   # 控制增量权重（平滑）

    # 约束
    u_min = np.array([5.0])   # 最小流量 5 m³/s
    u_max = np.array([20.0])  # 最大流量 20 m³/s
    du_min = np.array([-2.0])  # 最大减少 2 m³/s
    du_max = np.array([2.0])   # 最大增加 2 m³/s
    y_min = np.array([1.5])   # 最低水位 1.5 m
    y_max = np.array([2.5])   # 最高水位 2.5 m

    # 创建MPC控制器
    mpc = ModelPredictiveController(
        canal.A, canal.B, canal.C, Np, Nc, Q, R, S,
        u_min=u_min, u_max=u_max,
        du_min=du_min, du_max=du_max,
        y_min=y_min, y_max=y_max
    )

    # 仿真参数
    T_sim = 1800.0  # 30分钟
    t = np.arange(0, T_sim, canal.dt)
    N = len(t)

    # 参考轨迹（水位目标）
    r_ref = np.ones(N) * 2.0  # 目标水位 2.0 m
    r_ref[N//3:2*N//3] = 2.2   # 中间段提高到 2.2 m

    # 扰动（用水需求变化）
    disturbance = np.zeros(N)
    disturbance[N//2:N//2+50] = -2.0  # 突然增加用水（相当于出流增加）

    # 初始状态
    x0 = np.array([2.0, 10.0])  # [h=2m, Q=10m³/s]

    # 仿真
    X = np.zeros((N, 2))
    Y = np.zeros(N)
    U = np.zeros(N)
    X[0] = x0
    Y[0] = canal.C @ x0

    x_current = x0.copy()
    u_prev = np.array([10.0])  # 初始控制

    for k in range(N-1):
        # 求解MPC
        try:
            u_opt, _ = mpc.solve(x_current, r_ref[k], u_prev)
        except:
            u_opt = u_prev  # 如果优化失败，保持上次控制

        # 应用控制 + 扰动
        u_actual = u_opt[0] + (disturbance[k] if k < len(disturbance) else 0)
        x_current = canal.A @ x_current + canal.B.flatten() * u_actual
        y_current = canal.C @ x_current

        U[k] = u_opt[0]
        X[k+1] = x_current
        Y[k+1] = y_current[0]
        u_prev = u_opt

    # 计算性能指标
    tracking_error = np.mean(np.abs(Y - r_ref))
    control_variation = np.sum(np.abs(np.diff(U)))

    print(f"\n性能指标:")
    print(f"  平均跟踪误差: {tracking_error:.4f} m")
    print(f"  控制变化总量: {control_variation:.2f} m³/s")
    print(f"  约束违背次数: {np.sum((Y < y_min) | (Y > y_max))}")

    # 可视化
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))

    # 子图1: 水位跟踪
    ax = axes[0]
    ax.plot(t/60, r_ref, 'k--', linewidth=2, label='目标水位')
    ax.plot(t/60, Y, 'b-', linewidth=2, label='实际水位')
    ax.axhline(y_max, color='red', linestyle=':', linewidth=1.5, label='水位上限')
    ax.axhline(y_min, color='red', linestyle=':', linewidth=1.5, label='水位下限')
    ax.fill_between(t/60, y_min, y_max, alpha=0.1, color='green', label='安全范围')
    ax.set_xlabel('时间 (min)')
    ax.set_ylabel('水位 (m)')
    ax.set_title(f'运河水位MPC控制（平均误差={tracking_error:.4f}m）')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 子图2: 控制输入
    ax = axes[1]
    ax.plot(t/60, U, 'g-', linewidth=2, label='入流流量')
    ax.axhline(u_max, color='red', linestyle='--', linewidth=1.5, label='流量上限')
    ax.axhline(u_min, color='red', linestyle='--', linewidth=1.5, label='流量下限')
    ax.set_xlabel('时间 (min)')
    ax.set_ylabel('入流流量 (m³/s)')
    ax.set_title('MPC控制输入（满足约束）')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 子图3: 扰动响应
    ax = axes[2]
    ax.plot(t/60, disturbance, 'r-', linewidth=2, label='扰动（用水变化）')
    ax.set_xlabel('时间 (min)')
    ax.set_ylabel('扰动 (m³/s)')
    ax.set_title('扰动信号（MPC能够提前补偿）')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('part2_canal_mpc.png', dpi=300, bbox_inches='tight')
    print("图像已保存: part2_canal_mpc.png\n")

    return mpc


# ============================================================================
# Part 3: 约束处理对比
# ============================================================================

def part3_constraint_handling():
    """
    Part 3: 约束处理与优化

    对比：无约束 vs 软约束 vs 硬约束
    """
    print("=" * 60)
    print("Part 3: 约束处理对比")
    print("=" * 60)

    # 创建运河模型
    canal = SimplifiedCanalModel(L=1000, B=5.0, h0=2.0, Q0=10.0, dt=10.0)

    # 基本MPC参数
    Np = 25
    Nc = 12
    Q = np.array([[30.0]])
    R = np.array([[0.1]])
    S = np.array([[0.5]])

    # 约束
    u_min = np.array([5.0])
    u_max = np.array([15.0])  # 较严格的流量限制
    y_min = np.array([1.7])
    y_max = np.array([2.3])  # 较严格的水位限制

    # 1. 无约束MPC
    mpc_no_constraint = ModelPredictiveController(
        canal.A, canal.B, canal.C, Np, Nc, Q, R, S
    )

    # 2. 只有控制约束
    mpc_control_constraint = ModelPredictiveController(
        canal.A, canal.B, canal.C, Np, Nc, Q, R, S,
        u_min=u_min, u_max=u_max
    )

    # 3. 完全约束（控制+输出）
    mpc_full_constraint = ModelPredictiveController(
        canal.A, canal.B, canal.C, Np, Nc, Q, R, S,
        u_min=u_min, u_max=u_max,
        y_min=y_min, y_max=y_max
    )

    # 仿真参数
    T_sim = 600.0
    t = np.arange(0, T_sim, canal.dt)
    N = len(t)

    # 具有挑战性的参考轨迹（超出安全范围）
    r_ref = np.ones(N) * 2.0
    r_ref[N//4:N//2] = 2.5  # 超过上限
    r_ref[N//2:3*N//4] = 1.5  # 低于下限

    # 初始状态
    x0 = np.array([2.0, 10.0])

    # 仿真三种策略
    results = {}

    for name, mpc in [("无约束", mpc_no_constraint),
                      ("仅控制约束", mpc_control_constraint),
                      ("完全约束", mpc_full_constraint)]:
        X = np.zeros((N, 2))
        Y = np.zeros(N)
        U = np.zeros(N)
        X[0] = x0
        Y[0] = canal.C @ x0

        x_current = x0.copy()
        u_prev = np.array([10.0])

        for k in range(N-1):
            try:
                u_opt, _ = mpc.solve(x_current, r_ref[k], u_prev)
            except:
                u_opt = u_prev

            x_current = canal.A @ x_current + canal.B.flatten() * u_opt
            y_current = canal.C @ x_current

            U[k] = u_opt[0]
            X[k+1] = x_current
            Y[k+1] = y_current[0]
            u_prev = u_opt

        results[name] = {'Y': Y, 'U': U}

        # 统计约束违背
        y_violations = np.sum((Y < y_min) | (Y > y_max))
        u_violations = np.sum((U < u_min) | (U > u_max))
        print(f"\n{name}:")
        print(f"  水位约束违背次数: {y_violations}")
        print(f"  控制约束违背次数: {u_violations}")

    # 可视化
    fig = plt.figure(figsize=(14, 10))
    gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)

    # 子图1: 水位对比
    ax1 = fig.add_subplot(gs[0, :])
    ax1.plot(t/60, r_ref, 'k--', linewidth=2, label='参考轨迹')
    ax1.plot(t/60, results["无约束"]['Y'], 'r-', linewidth=2, alpha=0.7, label='无约束')
    ax1.plot(t/60, results["仅控制约束"]['Y'], 'orange', linewidth=2, alpha=0.7, label='仅控制约束')
    ax1.plot(t/60, results["完全约束"]['Y'], 'b-', linewidth=2, label='完全约束')
    ax1.axhline(y_max, color='red', linestyle=':', linewidth=2, label='水位上限')
    ax1.axhline(y_min, color='red', linestyle=':', linewidth=2)
    ax1.fill_between(t/60, y_min, y_max, alpha=0.1, color='green')
    ax1.set_xlabel('时间 (min)')
    ax1.set_ylabel('水位 (m)')
    ax1.set_title('约束处理对比：水位响应')
    ax1.legend(loc='upper right')
    ax1.grid(True, alpha=0.3)

    # 子图2: 控制输入对比
    ax2 = fig.add_subplot(gs[1, 0])
    ax2.plot(t/60, results["无约束"]['U'], 'r-', linewidth=2, alpha=0.7, label='无约束')
    ax2.plot(t/60, results["仅控制约束"]['U'], 'orange', linewidth=2, alpha=0.7, label='仅控制约束')
    ax2.plot(t/60, results["完全约束"]['U'], 'b-', linewidth=2, label='完全约束')
    ax2.axhline(u_max, color='red', linestyle='--', linewidth=1.5)
    ax2.axhline(u_min, color='red', linestyle='--', linewidth=1.5)
    ax2.set_xlabel('时间 (min)')
    ax2.set_ylabel('入流流量 (m³/s)')
    ax2.set_title('控制输入对比')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    # 子图3: 约束违背统计
    ax3 = fig.add_subplot(gs[1, 1])
    names = list(results.keys())
    y_viols = [np.sum((results[n]['Y'] < y_min) | (results[n]['Y'] > y_max)) for n in names]
    u_viols = [np.sum((results[n]['U'] < u_min) | (results[n]['U'] > u_max)) for n in names]

    x_pos = np.arange(len(names))
    width = 0.35

    ax3.bar(x_pos - width/2, y_viols, width, label='水位约束违背', color='red', alpha=0.7)
    ax3.bar(x_pos + width/2, u_viols, width, label='控制约束违背', color='blue', alpha=0.7)
    ax3.set_xlabel('MPC类型')
    ax3.set_ylabel('违背次数')
    ax3.set_title('约束违背统计（越少越好）')
    ax3.set_xticks(x_pos)
    ax3.set_xticklabels(names, rotation=15)
    ax3.legend()
    ax3.grid(True, alpha=0.3, axis='y')

    plt.savefig('part3_constraint_handling.png', dpi=300, bbox_inches='tight')
    print("\n图像已保存: part3_constraint_handling.png\n")

    return mpc_full_constraint


# ============================================================================
# Part 4: 多目标MPC
# ============================================================================

def part4_multi_objective_mpc():
    """
    Part 4: 多目标MPC

    同时优化：水位跟踪 + 节能 + 控制平滑
    """
    print("=" * 60)
    print("Part 4: 多目标MPC")
    print("=" * 60)

    # 创建运河模型
    canal = SimplifiedCanalModel(L=1000, B=5.0, h0=2.0, Q0=10.0, dt=10.0)

    # 基本参数
    Np = 30
    Nc = 15
    u_min = np.array([5.0])
    u_max = np.array([20.0])
    y_min = np.array([1.7])
    y_max = np.array([2.3])

    # 三种权重配置
    configs = {
        "高跟踪精度": {"Q": 100.0, "R": 0.1, "S": 0.5},
        "节能优先": {"Q": 10.0, "R": 10.0, "S": 5.0},
        "平衡策略": {"Q": 50.0, "R": 1.0, "S": 2.0}
    }

    # 仿真参数
    T_sim = 900.0
    t = np.arange(0, T_sim, canal.dt)
    N = len(t)

    # 参考轨迹
    r_ref = np.ones(N) * 2.0
    r_ref[N//3:2*N//3] = 2.15  # 小幅度变化

    # 初始状态
    x0 = np.array([2.0, 10.0])

    # 仿真不同配置
    results = {}

    for name, params in configs.items():
        Q = np.array([[params["Q"]]])
        R = np.array([[params["R"]]])
        S = np.array([[params["S"]]])

        mpc = ModelPredictiveController(
            canal.A, canal.B, canal.C, Np, Nc, Q, R, S,
            u_min=u_min, u_max=u_max,
            y_min=y_min, y_max=y_max
        )

        X = np.zeros((N, 2))
        Y = np.zeros(N)
        U = np.zeros(N)
        X[0] = x0
        Y[0] = canal.C @ x0

        x_current = x0.copy()
        u_prev = np.array([10.0])

        for k in range(N-1):
            try:
                u_opt, _ = mpc.solve(x_current, r_ref[k], u_prev)
            except:
                u_opt = u_prev

            x_current = canal.A @ x_current + canal.B.flatten() * u_opt
            y_current = canal.C @ x_current

            U[k] = u_opt[0]
            X[k+1] = x_current
            Y[k+1] = y_current[0]
            u_prev = u_opt

        # 计算性能指标
        tracking_error = np.sqrt(np.mean((Y - r_ref)**2))
        energy = np.sum(U**2) * canal.dt
        smoothness = np.sum(np.abs(np.diff(U)))

        results[name] = {
            'Y': Y,
            'U': U,
            'tracking_error': tracking_error,
            'energy': energy,
            'smoothness': smoothness
        }

        print(f"\n{name}:")
        print(f"  跟踪误差(RMSE): {tracking_error:.4f} m")
        print(f"  控制能量: {energy:.2f}")
        print(f"  控制平滑度: {smoothness:.2f}")

    # 可视化
    fig = plt.figure(figsize=(14, 10))
    gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)

    # 子图1: 水位跟踪
    ax1 = fig.add_subplot(gs[0, :])
    ax1.plot(t/60, r_ref, 'k--', linewidth=2, label='目标水位')
    colors = {'高跟踪精度': 'blue', '节能优先': 'green', '平衡策略': 'red'}
    for name, res in results.items():
        ax1.plot(t/60, res['Y'], color=colors[name], linewidth=2, alpha=0.7, label=name)
    ax1.set_xlabel('时间 (min)')
    ax1.set_ylabel('水位 (m)')
    ax1.set_title('多目标MPC：水位跟踪对比')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # 子图2: 控制输入
    ax2 = fig.add_subplot(gs[1, 0])
    for name, res in results.items():
        ax2.plot(t/60, res['U'], color=colors[name], linewidth=2, alpha=0.7, label=name)
    ax2.set_xlabel('时间 (min)')
    ax2.set_ylabel('入流流量 (m³/s)')
    ax2.set_title('控制输入对比')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    # 子图3: 控制增量
    ax3 = fig.add_subplot(gs[1, 1])
    for name, res in results.items():
        du = np.diff(res['U'], prepend=res['U'][0])
        ax3.plot(t/60, du, color=colors[name], linewidth=2, alpha=0.7, label=name)
    ax3.set_xlabel('时间 (min)')
    ax3.set_ylabel('控制增量 Δu (m³/s)')
    ax3.set_title('控制平滑性对比')
    ax3.legend()
    ax3.grid(True, alpha=0.3)

    # 子图4: 性能雷达图
    ax4 = fig.add_subplot(gs[2, :], projection='polar')

    categories = ['跟踪精度\n(1/RMSE)', '节能性\n(1/Energy)', '平滑性\n(1/Smooth)']
    N_metrics = len(categories)
    angles = np.linspace(0, 2 * np.pi, N_metrics, endpoint=False).tolist()
    angles += angles[:1]

    for name, res in results.items():
        # 归一化指标（越大越好）
        values = [
            1 / (res['tracking_error'] + 0.001),
            1000 / (res['energy'] + 1),
            10 / (res['smoothness'] + 1)
        ]
        # 归一化到0-1
        max_vals = [50, 20, 2]
        values = [min(v/m, 1.0) for v, m in zip(values, max_vals)]
        values += values[:1]

        ax4.plot(angles, values, 'o-', linewidth=2, label=name, color=colors[name])
        ax4.fill(angles, values, alpha=0.15, color=colors[name])

    ax4.set_xticks(angles[:-1])
    ax4.set_xticklabels(categories)
    ax4.set_ylim(0, 1)
    ax4.set_title('多目标性能雷达图（外圈越好）', pad=20)
    ax4.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
    ax4.grid(True)

    plt.savefig('part4_multi_objective_mpc.png', dpi=300, bbox_inches='tight')
    print("\n图像已保存: part4_multi_objective_mpc.png\n")

    return results


# ============================================================================
# 主函数
# ============================================================================

def main():
    """主函数"""
    print("\n" + "="*60)
    print("案例14：模型预测控制（MPC）")
    print("="*60 + "\n")

    # 设置随机种子
    np.random.seed(42)

    # Part 1: 线性MPC基础
    mpc1 = part1_linear_mpc_basics()

    # Part 2: 运河系统MPC控制
    mpc2 = part2_canal_mpc_control()

    # Part 3: 约束处理对比
    mpc3 = part3_constraint_handling()

    # Part 4: 多目标MPC
    results = part4_multi_objective_mpc()

    # 总结
    print("=" * 60)
    print("案例14总结")
    print("=" * 60)

    print("\n1. 线性MPC基础：")
    print("   - 演示了MPC的预测-优化-反馈循环")
    print("   - 有约束MPC能显式满足物理限制")
    print("   - 控制增量权重实现平滑控制")

    print("\n2. 运河系统MPC控制：")
    print("   - 成功跟踪水位目标，满足所有约束")
    print("   - 提前预测扰动，主动补偿")
    print("   - 平衡跟踪精度和控制平滑性")

    print("\n3. 约束处理：")
    print("   - 无约束MPC可能违背物理限制，不安全")
    print("   - 仅控制约束保护执行器，但输出可能超限")
    print("   - 完全约束MPC保证系统安全运行")

    print("\n4. 多目标MPC：")
    print("   - 通过调整权重矩阵实现不同目标")
    print("   - 高跟踪精度配置：误差小，但能耗高")
    print("   - 节能优先配置：能耗低，但跟踪稍差")
    print("   - 平衡策略：综合性能最优")

    print("\n工程意义：")
    print("   - MPC是先进控制的首选方案")
    print("   - 显式处理约束，保证系统安全")
    print("   - 多变量协同优化，提高整体性能")
    print("   - 前瞻性预测，提前补偿扰动")

    print("\n关键参数调优：")
    print("   - Np（预测时域）：取系统时间常数的2-5倍")
    print("   - Nc（控制时域）：通常取Np/2，减少计算量")
    print("   - Q（跟踪权重）：越大越重视跟踪精度")
    print("   - R（控制权重）：越大越节能")
    print("   - S（控制增量权重）：越大越平滑")

    print("\n所有图像已生成！")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
