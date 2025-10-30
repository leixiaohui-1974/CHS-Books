#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
案例12：扩展卡尔曼滤波（EKF）状态估计

本案例实现了扩展卡尔曼滤波和无迹卡尔曼滤波，用于非线性运河系统的状态估计。

主要内容：
1. EKF核心算法实现
2. UKF（无迹卡尔曼滤波）实现
3. 标量非线性系统演示
4. 运河系统多状态估计
5. 多传感器融合
6. EKF vs UKF性能对比

作者：Claude
日期：2025
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import sqrtm
from scipy.integrate import odeint
import time

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class ExtendedKalmanFilter:
    """
    扩展卡尔曼滤波器（EKF）

    适用于非线性系统：
        x(k) = f(x(k-1), u(k-1)) + w(k-1)
        y(k) = h(x(k)) + v(k)

    其中 w ~ N(0, Q), v ~ N(0, R)
    """

    def __init__(self, f, h, F_jacobian, H_jacobian, Q, R, x0, P0):
        """
        初始化EKF

        参数:
            f: 状态转移函数 f(x, u)
            h: 观测函数 h(x)
            F_jacobian: 状态雅可比函数 ∂f/∂x
            H_jacobian: 观测雅可比函数 ∂h/∂x
            Q: 过程噪声协方差
            R: 测量噪声协方差
            x0: 初始状态估计
            P0: 初始协方差
        """
        self.f = f
        self.h = h
        self.F_jacobian = F_jacobian
        self.H_jacobian = H_jacobian
        self.Q = Q
        self.R = R

        # 状态估计
        self.x = np.array(x0, dtype=float)
        self.P = np.array(P0, dtype=float)

        # 记录历史（用于分析）
        self.x_prior_history = []
        self.x_post_history = []
        self.P_history = []
        self.K_history = []

    def predict(self, u=None):
        """
        预测步

        参数:
            u: 控制输入
        """
        # 1. 状态预测（先验估计）
        self.x_prior = self.f(self.x, u)

        # 确保x_prior是1维数组
        self.x_prior = np.atleast_1d(np.squeeze(self.x_prior))

        # 2. 计算雅可比矩阵 F
        F = self.F_jacobian(self.x, u)

        # 3. 协方差预测
        self.P_prior = F @ self.P @ F.T + self.Q

        # 确保P_prior保持正确的2维形状
        if self.P_prior.ndim > 2:
            self.P_prior = np.squeeze(self.P_prior)
        self.P_prior = np.atleast_2d(self.P_prior)

        # 记录先验估计
        self.x_prior_history.append(self.x_prior.copy())

        return self.x_prior

    def update(self, y):
        """
        更新步

        参数:
            y: 测量值
        """
        # 1. 计算观测雅可比矩阵 H
        H = self.H_jacobian(self.x_prior)

        # 2. 计算卡尔曼增益
        S = H @ self.P_prior @ H.T + self.R  # 新息协方差
        K = self.P_prior @ H.T @ np.linalg.inv(S)

        # 3. 观测预测
        y_pred = self.h(self.x_prior)

        # 4. 状态更新（后验估计）
        innovation = y - y_pred  # 新息（innovation）
        self.x = self.x_prior + K @ innovation

        # 确保x是1维数组
        self.x = np.atleast_1d(np.squeeze(self.x))

        # 5. 协方差更新
        n = len(self.x)
        I = np.eye(n)
        self.P = (I - K @ H) @ self.P_prior

        # 确保P保持正确的2维形状
        if self.P.ndim > 2:
            self.P = np.squeeze(self.P)
        self.P = np.atleast_2d(self.P)

        # 记录历史
        self.x_post_history.append(self.x.copy())
        self.P_history.append(np.diag(self.P).copy())
        self.K_history.append(K.copy())

        return self.x

    def get_uncertainty(self):
        """返回当前状态的标准差（不确定性）"""
        return np.sqrt(np.diag(self.P))


class UnscentedKalmanFilter:
    """
    无迹卡尔曼滤波器（UKF）

    使用Unscented Transform避免显式线性化
    """

    def __init__(self, f, h, Q, R, x0, P0, alpha=0.001, beta=2, kappa=0):
        """
        初始化UKF

        参数:
            f: 状态转移函数 f(x, u)
            h: 观测函数 h(x)
            Q: 过程噪声协方差
            R: 测量噪声协方差
            x0: 初始状态估计
            P0: 初始协方差
            alpha: Sigma点分布参数（典型值 0.001）
            beta: 高斯分布参数（典型值 2）
            kappa: 次要缩放参数（典型值 0）
        """
        self.f = f
        self.h = h
        self.Q = Q
        self.R = R

        self.x = np.array(x0, dtype=float)
        self.P = np.array(P0, dtype=float)

        # UKF参数
        self.alpha = alpha
        self.beta = beta
        self.kappa = kappa

        n = len(self.x)
        self.lambda_ = alpha**2 * (n + kappa) - n

        # 计算权重
        self.Wm, self.Wc = self._compute_weights(n)

        # 记录历史
        self.x_history = []
        self.P_history = []

    def _compute_weights(self, n):
        """计算Sigma点权重"""
        lambda_ = self.lambda_

        # 均值权重
        Wm = np.zeros(2*n + 1)
        Wm[0] = lambda_ / (n + lambda_)
        Wm[1:] = 1 / (2*(n + lambda_))

        # 协方差权重
        Wc = np.zeros(2*n + 1)
        Wc[0] = lambda_ / (n + lambda_) + (1 - self.alpha**2 + self.beta)
        Wc[1:] = 1 / (2*(n + lambda_))

        return Wm, Wc

    def _generate_sigma_points(self, x, P):
        """生成Sigma点"""
        n = len(x)
        lambda_ = self.lambda_

        # 计算矩阵平方根
        try:
            L = sqrtm((n + lambda_) * P).real
        except:
            # 如果sqrtm失败，使用Cholesky分解
            L = np.linalg.cholesky((n + lambda_) * P)

        # 生成2n+1个Sigma点
        sigma_points = np.zeros((2*n + 1, n))
        sigma_points[0] = x

        for i in range(n):
            sigma_points[i+1] = x + L[:, i]
            sigma_points[n+i+1] = x - L[:, i]

        return sigma_points

    def predict(self, u=None):
        """预测步"""
        n = len(self.x)

        # 1. 生成Sigma点
        sigma_points = self._generate_sigma_points(self.x, self.P)

        # 2. 传播Sigma点通过状态转移函数
        sigma_points_pred = np.zeros_like(sigma_points)
        for i in range(2*n + 1):
            sigma_points_pred[i] = self.f(sigma_points[i], u)

        # 3. 重构先验状态估计
        self.x_prior = np.sum(self.Wm[:, np.newaxis] * sigma_points_pred, axis=0)

        # 确保x_prior是1维数组
        self.x_prior = np.atleast_1d(np.squeeze(self.x_prior))

        # 4. 重构先验协方差
        P_prior = np.zeros((n, n))
        for i in range(2*n + 1):
            diff = sigma_points_pred[i] - self.x_prior
            P_prior += self.Wc[i] * np.outer(diff, diff)
        self.P_prior = P_prior + self.Q

        # 确保P_prior保持正确的2维形状
        if self.P_prior.ndim > 2:
            self.P_prior = np.squeeze(self.P_prior)
        self.P_prior = np.atleast_2d(self.P_prior)

        return self.x_prior

    def update(self, y):
        """更新步"""
        n = len(self.x)
        m = len(y) if isinstance(y, np.ndarray) else 1

        # 1. 生成新的Sigma点（基于先验）
        sigma_points = self._generate_sigma_points(self.x_prior, self.P_prior)

        # 2. 传播Sigma点通过观测函数
        sigma_y = np.zeros((2*n + 1, m))
        for i in range(2*n + 1):
            sigma_y[i] = self.h(sigma_points[i])

        # 3. 重构观测预测
        y_pred = np.sum(self.Wm[:, np.newaxis] * sigma_y, axis=0)

        # 4. 计算观测协方差和互协方差
        Pyy = np.zeros((m, m))
        Pxy = np.zeros((n, m))

        for i in range(2*n + 1):
            dy = sigma_y[i] - y_pred
            dx = sigma_points[i] - self.x_prior

            Pyy += self.Wc[i] * np.outer(dy, dy)
            Pxy += self.Wc[i] * np.outer(dx, dy)

        Pyy += self.R

        # 5. 卡尔曼增益
        K = Pxy @ np.linalg.inv(Pyy)

        # 6. 状态更新
        innovation = y - y_pred
        self.x = self.x_prior + K @ innovation

        # 确保x是1维数组
        self.x = np.atleast_1d(np.squeeze(self.x))

        # 7. 协方差更新
        self.P = self.P_prior - K @ Pyy @ K.T

        # 确保P保持正确的2维形状
        if self.P.ndim > 2:
            self.P = np.squeeze(self.P)
        self.P = np.atleast_2d(self.P)

        # 记录历史
        self.x_history.append(self.x.copy())
        self.P_history.append(np.diag(self.P).copy())

        return self.x

    def get_uncertainty(self):
        """返回当前状态的标准差（不确定性）"""
        return np.sqrt(np.diag(self.P))


class CanalReachModel:
    """
    简化的单渠段非线性动力学模型

    状态变量:
        x[0] = h     水位 (m)
        x[1] = Q_out 出流流量 (m³/s)

    控制输入:
        u = Q_in     入流流量 (m³/s)

    动力学方程（连续时间）:
        dh/dt = (Q_in - Q_out)/A_s - C_d*w*sqrt(2g)/A_s * h^(3/2)
        dQ_out/dt = g*A_c/L * (h - h_ds) - f*Q_out^2/(2*D_h*A_c)
    """

    def __init__(self,
                 L=1000.0,      # 渠段长度 (m)
                 B=5.0,         # 渠底宽度 (m)
                 w=5.0,         # 堰宽 (m)
                 C_d=0.6,       # 堰流系数
                 f=0.02,        # 摩阻系数
                 h_ds=1.5,      # 下游水位 (m)
                 dt=1.0):       # 采样时间 (s)

        self.L = L
        self.B = B
        self.w = w
        self.C_d = C_d
        self.f = f
        self.h_ds = h_ds
        self.dt = dt

        self.g = 9.81  # 重力加速度 (m/s²)

    def _continuous_dynamics(self, x, t, u):
        """连续时间动力学（用于积分）"""
        h, Q_out = x
        Q_in = u

        # 防止负值导致的数学错误
        h = max(h, 0.01)
        Q_out = max(Q_out, 0.0)

        # 水面面积和过流面积（矩形断面简化）
        A_s = self.B * self.L
        A_c = self.B * h
        D_h = 4 * A_c / (self.B + 2*h)  # 水力直径

        # 状态方程
        dh_dt = (Q_in - Q_out) / A_s - \
                (self.C_d * self.w * np.sqrt(2*self.g) / A_s) * h**1.5

        dQ_dt = (self.g * A_c / self.L) * (h - self.h_ds) - \
                (self.f * Q_out**2) / (2 * D_h * A_c + 1e-6)

        return [dh_dt, dQ_dt]

    def discrete_dynamics(self, x, u):
        """
        离散时间状态转移函数（用于卡尔曼滤波）

        使用数值积分实现离散化
        """
        # 使用odeint进行数值积分
        t_span = [0, self.dt]
        sol = odeint(self._continuous_dynamics, x, t_span, args=(u,))

        return sol[-1]

    def measurement_model(self, x):
        """
        观测模型

        假设可以测量水位和流量
        """
        h, Q_out = x
        return np.array([h, Q_out])

    def F_jacobian(self, x, u):
        """状态转移雅可比矩阵（数值近似）"""
        epsilon = 1e-6
        n = len(x)
        F = np.zeros((n, n))

        f0 = self.discrete_dynamics(x, u)

        for i in range(n):
            x_perturbed = x.copy()
            x_perturbed[i] += epsilon
            f_perturbed = self.discrete_dynamics(x_perturbed, u)
            F[:, i] = (f_perturbed - f0) / epsilon

        return F

    def H_jacobian(self, x):
        """观测雅可比矩阵"""
        # 对于线性观测 y = x，雅可比就是单位矩阵
        return np.eye(len(x))


def part1_scalar_ekf_demo():
    """
    Part 1: 标量非线性系统EKF演示

    经典问题：估计物体位置
    状态方程: x(k) = x(k-1) + v*dt + 0.5*a*dt^2
    观测方程: y(k) = x(k)^2 / 20 (非线性传感器)
    """
    print("=" * 60)
    print("Part 1: 标量非线性系统EKF演示")
    print("=" * 60)

    # 系统参数
    dt = 0.1
    T = 10.0
    t = np.arange(0, T, dt)
    N = len(t)

    # 真实状态（简单运动）
    x_true = 10 * np.sin(0.5 * t) + 5

    # 状态转移函数（简单的恒定模型）
    def f(x, u):
        return x  # 假设状态不变

    # 观测函数（非线性）
    def h(x):
        return x**2 / 20.0

    # 雅可比矩阵
    def F_jac(x, u):
        return np.array([[1.0]])

    def H_jac(x):
        return np.array([[x / 10.0]])

    # 噪声协方差
    Q = np.array([[0.1]])  # 过程噪声
    R = np.array([[1.0]])  # 测量噪声

    # 生成带噪声的测量
    y_meas = np.zeros(N)
    for i in range(N):
        y_meas[i] = h(x_true[i]) + np.random.randn() * np.sqrt(R[0, 0])

    # 初始化EKF
    x0 = np.array([5.0])
    P0 = np.array([[10.0]])
    ekf = ExtendedKalmanFilter(f, h, F_jac, H_jac, Q, R, x0, P0)

    # 运行EKF
    x_est = np.zeros(N)
    x_prior = np.zeros(N)
    std_est = np.zeros(N)

    for i in range(N):
        # 预测
        ekf.predict(u=None)
        x_prior[i] = ekf.x_prior[0]

        # 更新
        ekf.update(np.array([y_meas[i]]))
        x_est[i] = ekf.x[0]
        std_est[i] = ekf.get_uncertainty()[0]

    # 计算RMSE
    rmse = np.sqrt(np.mean((x_est - x_true)**2))
    print(f"估计RMSE: {rmse:.4f}")

    # 可视化
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))

    # 子图1: 状态估计
    ax = axes[0]
    ax.plot(t, x_true, 'k-', linewidth=2, label='真实状态')
    ax.plot(t, x_est, 'b-', linewidth=1.5, label='EKF后验估计')
    ax.plot(t, x_prior, 'r--', linewidth=1, alpha=0.7, label='EKF先验估计')
    ax.fill_between(t, x_est - 2*std_est, x_est + 2*std_est,
                     alpha=0.3, color='blue', label='95%置信区间')
    ax.set_xlabel('时间 (s)')
    ax.set_ylabel('状态 x')
    ax.set_title('标量非线性系统EKF状态估计')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 子图2: 测量值
    ax = axes[1]
    y_true = np.array([h(x) for x in x_true])
    ax.plot(t, y_true, 'k-', linewidth=2, label='真实观测值')
    ax.plot(t, y_meas, 'r.', markersize=3, alpha=0.6, label='带噪声测量')
    ax.set_xlabel('时间 (s)')
    ax.set_ylabel('观测 y = x²/20')
    ax.set_title('非线性观测模型')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 子图3: 估计误差和不确定性
    ax = axes[2]
    error = x_est - x_true
    ax.plot(t, error, 'b-', linewidth=1.5, label='估计误差')
    ax.plot(t, 2*std_est, 'r--', linewidth=1, label='2σ边界')
    ax.plot(t, -2*std_est, 'r--', linewidth=1)
    ax.axhline(0, color='k', linestyle=':', alpha=0.5)
    ax.set_xlabel('时间 (s)')
    ax.set_ylabel('误差')
    ax.set_title(f'估计误差与不确定性 (RMSE={rmse:.4f})')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('part1_scalar_ekf.png', dpi=300, bbox_inches='tight')
    print("图像已保存: part1_scalar_ekf.png\n")

    return rmse


def part2_canal_state_estimation():
    """
    Part 2: 运河系统状态估计

    估计运河的水位和出流流量
    """
    print("=" * 60)
    print("Part 2: 运河系统状态估计")
    print("=" * 60)

    # 创建运河模型
    canal = CanalReachModel(dt=10.0)  # 10秒采样

    # 仿真参数
    T = 3600.0  # 1小时
    t = np.arange(0, T, canal.dt)
    N = len(t)

    # 控制输入（入流流量变化）
    Q_in = 10.0 + 3.0 * np.sin(2*np.pi*t/1800)  # 30分钟周期

    # 初始状态
    x_true = np.array([2.0, 8.0])  # [h, Q_out]

    # 生成真实状态轨迹
    x_true_history = np.zeros((N, 2))
    x_true_history[0] = x_true

    for i in range(1, N):
        x_true = canal.discrete_dynamics(x_true, Q_in[i-1])
        x_true_history[i] = x_true

    # 生成带噪声的测量
    R = np.diag([0.05**2, 0.5**2])  # 测量噪声 [h:5cm, Q:0.5m³/s]
    y_meas = np.zeros((N, 2))

    for i in range(N):
        noise = np.random.multivariate_normal([0, 0], R)
        y_meas[i] = canal.measurement_model(x_true_history[i]) + noise

    # 初始化EKF
    x0 = np.array([2.5, 7.0])  # 初始猜测有偏差
    P0 = np.diag([0.5**2, 2.0**2])
    Q = np.diag([0.01**2, 0.1**2])  # 过程噪声

    ekf = ExtendedKalmanFilter(
        f=canal.discrete_dynamics,
        h=canal.measurement_model,
        F_jacobian=canal.F_jacobian,
        H_jacobian=canal.H_jacobian,
        Q=Q, R=R, x0=x0, P0=P0
    )

    # 运行EKF
    x_est_history = np.zeros((N, 2))
    std_history = np.zeros((N, 2))

    for i in range(N):
        # 预测
        ekf.predict(u=Q_in[i])

        # 更新
        ekf.update(y_meas[i])
        x_est_history[i] = ekf.x
        std_history[i] = ekf.get_uncertainty()

    # 计算RMSE
    rmse_h = np.sqrt(np.mean((x_est_history[:, 0] - x_true_history[:, 0])**2))
    rmse_Q = np.sqrt(np.mean((x_est_history[:, 1] - x_true_history[:, 1])**2))

    print(f"水位估计RMSE: {rmse_h:.4f} m")
    print(f"流量估计RMSE: {rmse_Q:.4f} m³/s")

    # 可视化
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))

    # 子图1: 水位估计
    ax = axes[0]
    ax.plot(t/60, x_true_history[:, 0], 'k-', linewidth=2, label='真实水位')
    ax.plot(t/60, x_est_history[:, 0], 'b-', linewidth=1.5, label='EKF估计')
    ax.plot(t/60, y_meas[:, 0], 'r.', markersize=2, alpha=0.4, label='测量值')
    ax.fill_between(t/60,
                     x_est_history[:, 0] - 2*std_history[:, 0],
                     x_est_history[:, 0] + 2*std_history[:, 0],
                     alpha=0.3, color='blue', label='95%置信区间')
    ax.set_xlabel('时间 (min)')
    ax.set_ylabel('水位 (m)')
    ax.set_title(f'运河水位估计 (RMSE={rmse_h:.4f} m)')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 子图2: 流量估计
    ax = axes[1]
    ax.plot(t/60, x_true_history[:, 1], 'k-', linewidth=2, label='真实流量')
    ax.plot(t/60, x_est_history[:, 1], 'b-', linewidth=1.5, label='EKF估计')
    ax.plot(t/60, y_meas[:, 1], 'r.', markersize=2, alpha=0.4, label='测量值')
    ax.fill_between(t/60,
                     x_est_history[:, 1] - 2*std_history[:, 1],
                     x_est_history[:, 1] + 2*std_history[:, 1],
                     alpha=0.3, color='blue', label='95%置信区间')
    ax.set_xlabel('时间 (min)')
    ax.set_ylabel('出流流量 (m³/s)')
    ax.set_title(f'运河流量估计 (RMSE={rmse_Q:.4f} m³/s)')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 子图3: 控制输入
    ax = axes[2]
    ax.plot(t/60, Q_in, 'g-', linewidth=1.5, label='入流流量')
    ax.set_xlabel('时间 (min)')
    ax.set_ylabel('入流流量 (m³/s)')
    ax.set_title('控制输入（入流流量）')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('part2_canal_estimation.png', dpi=300, bbox_inches='tight')
    print("图像已保存: part2_canal_estimation.png\n")

    return rmse_h, rmse_Q


def part3_multi_sensor_fusion():
    """
    Part 3: 多传感器融合

    场景：3个水位传感器 + 1个流量传感器
    演示传感器冗余和故障检测
    """
    print("=" * 60)
    print("Part 3: 多传感器融合")
    print("=" * 60)

    # 创建运河模型
    canal = CanalReachModel(dt=10.0)

    # 仿真参数
    T = 1800.0  # 30分钟
    t = np.arange(0, T, canal.dt)
    N = len(t)

    # 控制输入
    Q_in = 10.0 * np.ones(N)

    # 初始状态
    x_true = np.array([2.0, 8.0])

    # 生成真实状态轨迹
    x_true_history = np.zeros((N, 2))
    x_true_history[0] = x_true

    for i in range(1, N):
        x_true = canal.discrete_dynamics(x_true, Q_in[i-1])
        x_true_history[i] = x_true

    # 多传感器测量模型
    # 3个水位传感器（不同精度）+ 1个流量传感器
    def multi_sensor_measurement(x):
        """
        返回4个测量值: [h1, h2, h3, Q]
        3个水位传感器测量同一个水位，但精度不同
        """
        h, Q = x
        return np.array([h, h, h, Q])

    def H_multi_jacobian(x):
        """多传感器观测雅可比"""
        return np.array([
            [1, 0],  # 水位传感器1
            [1, 0],  # 水位传感器2
            [1, 0],  # 水位传感器3
            [0, 1],  # 流量传感器
        ])

    # 测量噪声（不同传感器精度不同）
    R_multi = np.diag([
        0.03**2,  # 传感器1: 高精度 (3cm)
        0.05**2,  # 传感器2: 中精度 (5cm)
        0.10**2,  # 传感器3: 低精度 (10cm)
        0.5**2,   # 流量传感器 (0.5 m³/s)
    ])

    # 生成测量（模拟传感器2在t>900s时故障）
    y_multi = np.zeros((N, 4))
    for i in range(N):
        noise = np.random.multivariate_normal([0, 0, 0, 0], R_multi)
        y_multi[i] = multi_sensor_measurement(x_true_history[i]) + noise

        # 模拟传感器2故障（产生大偏差）
        if t[i] > 900:
            y_multi[i, 1] += 0.5  # 传感器2漂移

    # 初始化EKF（多传感器）
    x0 = np.array([2.5, 7.0])
    P0 = np.diag([0.5**2, 2.0**2])
    Q = np.diag([0.01**2, 0.1**2])

    ekf_multi = ExtendedKalmanFilter(
        f=canal.discrete_dynamics,
        h=multi_sensor_measurement,
        F_jacobian=canal.F_jacobian,
        H_jacobian=H_multi_jacobian,
        Q=Q, R=R_multi, x0=x0, P0=P0
    )

    # 同时运行单传感器EKF（仅传感器1）
    def single_sensor_measurement(x):
        return np.array([x[0], x[1]])

    R_single = np.diag([0.03**2, 0.5**2])

    ekf_single = ExtendedKalmanFilter(
        f=canal.discrete_dynamics,
        h=single_sensor_measurement,
        F_jacobian=canal.F_jacobian,
        H_jacobian=canal.H_jacobian,
        Q=Q, R=R_single, x0=x0, P0=P0
    )

    # 运行两个滤波器
    x_est_multi = np.zeros((N, 2))
    x_est_single = np.zeros((N, 2))
    std_multi = np.zeros((N, 2))
    std_single = np.zeros((N, 2))

    for i in range(N):
        # 多传感器EKF
        ekf_multi.predict(u=Q_in[i])
        ekf_multi.update(y_multi[i])
        x_est_multi[i] = ekf_multi.x
        std_multi[i] = ekf_multi.get_uncertainty()

        # 单传感器EKF（仅用传感器1和流量传感器）
        ekf_single.predict(u=Q_in[i])
        ekf_single.update(y_multi[i, [0, 3]])  # 只用传感器1和流量
        x_est_single[i] = ekf_single.x
        std_single[i] = ekf_single.get_uncertainty()

    # 计算RMSE
    rmse_multi = np.sqrt(np.mean((x_est_multi[:, 0] - x_true_history[:, 0])**2))
    rmse_single = np.sqrt(np.mean((x_est_single[:, 0] - x_true_history[:, 0])**2))

    print(f"多传感器融合RMSE: {rmse_multi:.4f} m")
    print(f"单传感器RMSE: {rmse_single:.4f} m")
    print(f"性能提升: {(rmse_single - rmse_multi)/rmse_single * 100:.1f}%")

    # 可视化
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))

    # 子图1: 多传感器测量对比
    ax = axes[0]
    ax.plot(t/60, x_true_history[:, 0], 'k-', linewidth=2, label='真实水位')
    ax.plot(t/60, y_multi[:, 0], 'b.', markersize=2, alpha=0.5, label='传感器1 (高精度)')
    ax.plot(t/60, y_multi[:, 1], 'r.', markersize=2, alpha=0.5, label='传感器2 (故障)')
    ax.plot(t/60, y_multi[:, 2], 'g.', markersize=2, alpha=0.5, label='传感器3 (低精度)')
    ax.axvline(900/60, color='orange', linestyle='--', linewidth=2, label='传感器2故障时刻')
    ax.set_xlabel('时间 (min)')
    ax.set_ylabel('水位 (m)')
    ax.set_title('多传感器测量（传感器2在15min后故障）')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 子图2: 融合估计对比
    ax = axes[1]
    ax.plot(t/60, x_true_history[:, 0], 'k-', linewidth=2, label='真实水位')
    ax.plot(t/60, x_est_multi[:, 0], 'b-', linewidth=1.5, label='多传感器融合')
    ax.plot(t/60, x_est_single[:, 0], 'r-', linewidth=1.5, label='单传感器')
    ax.fill_between(t/60,
                     x_est_multi[:, 0] - 2*std_multi[:, 0],
                     x_est_multi[:, 0] + 2*std_multi[:, 0],
                     alpha=0.2, color='blue')
    ax.axvline(900/60, color='orange', linestyle='--', linewidth=2, alpha=0.7)
    ax.set_xlabel('时间 (min)')
    ax.set_ylabel('水位 (m)')
    ax.set_title(f'多传感器融合 vs 单传感器 (RMSE: {rmse_multi:.4f} vs {rmse_single:.4f} m)')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 子图3: 估计不确定性对比
    ax = axes[2]
    ax.plot(t/60, std_multi[:, 0], 'b-', linewidth=1.5, label='多传感器不确定性')
    ax.plot(t/60, std_single[:, 0], 'r-', linewidth=1.5, label='单传感器不确定性')
    ax.axvline(900/60, color='orange', linestyle='--', linewidth=2, alpha=0.7, label='传感器2故障')
    ax.set_xlabel('时间 (min)')
    ax.set_ylabel('标准差 (m)')
    ax.set_title('估计不确定性对比（多传感器降低不确定性）')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('part3_sensor_fusion.png', dpi=300, bbox_inches='tight')
    print("图像已保存: part3_sensor_fusion.png\n")

    return rmse_multi, rmse_single


def part4_ekf_vs_ukf():
    """
    Part 4: EKF vs UKF性能对比

    在高度非线性运河系统中对比两种滤波器
    """
    print("=" * 60)
    print("Part 4: EKF vs UKF性能对比")
    print("=" * 60)

    # 创建运河模型（更强的非线性）
    canal = CanalReachModel(dt=10.0, C_d=0.8, f=0.03)  # 增强非线性

    # 仿真参数
    T = 3600.0
    t = np.arange(0, T, canal.dt)
    N = len(t)

    # 控制输入（大幅度变化）
    Q_in = 10.0 + 5.0 * np.sin(2*np.pi*t/1800) + 2.0 * np.sin(2*np.pi*t/600)

    # 初始状态
    x_true = np.array([2.0, 8.0])

    # 生成真实状态轨迹
    x_true_history = np.zeros((N, 2))
    x_true_history[0] = x_true

    for i in range(1, N):
        x_true = canal.discrete_dynamics(x_true, Q_in[i-1])
        x_true_history[i] = x_true

    # 生成带噪声的测量
    R = np.diag([0.1**2, 1.0**2])  # 较大的测量噪声
    y_meas = np.zeros((N, 2))

    for i in range(N):
        noise = np.random.multivariate_normal([0, 0], R)
        y_meas[i] = canal.measurement_model(x_true_history[i]) + noise

    # 初始化EKF
    x0 = np.array([3.0, 6.0])  # 较大的初始误差
    P0 = np.diag([1.0**2, 3.0**2])
    Q = np.diag([0.05**2, 0.2**2])

    ekf = ExtendedKalmanFilter(
        f=canal.discrete_dynamics,
        h=canal.measurement_model,
        F_jacobian=canal.F_jacobian,
        H_jacobian=canal.H_jacobian,
        Q=Q, R=R, x0=x0, P0=P0
    )

    # 初始化UKF
    ukf = UnscentedKalmanFilter(
        f=canal.discrete_dynamics,
        h=canal.measurement_model,
        Q=Q, R=R, x0=x0, P0=P0
    )

    # 运行EKF
    x_est_ekf = np.zeros((N, 2))
    std_ekf = np.zeros((N, 2))
    time_ekf = 0

    for i in range(N):
        t_start = time.time()
        ekf.predict(u=Q_in[i])
        ekf.update(y_meas[i])
        time_ekf += time.time() - t_start

        x_est_ekf[i] = ekf.x
        std_ekf[i] = ekf.get_uncertainty()

    # 运行UKF
    x_est_ukf = np.zeros((N, 2))
    std_ukf = np.zeros((N, 2))
    time_ukf = 0

    for i in range(N):
        t_start = time.time()
        ukf.predict(u=Q_in[i])
        ukf.update(y_meas[i])
        time_ukf += time.time() - t_start

        x_est_ukf[i] = ukf.x
        std_ukf[i] = ukf.get_uncertainty()

    # 计算性能指标
    rmse_ekf_h = np.sqrt(np.mean((x_est_ekf[:, 0] - x_true_history[:, 0])**2))
    rmse_ekf_Q = np.sqrt(np.mean((x_est_ekf[:, 1] - x_true_history[:, 1])**2))
    rmse_ukf_h = np.sqrt(np.mean((x_est_ukf[:, 0] - x_true_history[:, 0])**2))
    rmse_ukf_Q = np.sqrt(np.mean((x_est_ukf[:, 1] - x_true_history[:, 1])**2))

    print(f"\n性能对比:")
    print(f"{'指标':<20} {'EKF':>12} {'UKF':>12} {'改善':>12}")
    print("-" * 60)
    print(f"{'水位RMSE (m)':<20} {rmse_ekf_h:>12.4f} {rmse_ukf_h:>12.4f} {(rmse_ekf_h-rmse_ukf_h)/rmse_ekf_h*100:>11.1f}%")
    print(f"{'流量RMSE (m³/s)':<20} {rmse_ekf_Q:>12.4f} {rmse_ukf_Q:>12.4f} {(rmse_ekf_Q-rmse_ukf_Q)/rmse_ekf_Q*100:>11.1f}%")
    print(f"{'总计算时间 (ms)':<20} {time_ekf*1000:>12.2f} {time_ukf*1000:>12.2f} {(time_ekf-time_ukf)/time_ekf*100:>11.1f}%")
    print(f"{'单步时间 (ms)':<20} {time_ekf/N*1000:>12.4f} {time_ukf/N*1000:>12.4f}")

    # 可视化
    fig = plt.figure(figsize=(14, 10))
    gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)

    # 子图1: 水位估计对比
    ax1 = fig.add_subplot(gs[0, :])
    ax1.plot(t/60, x_true_history[:, 0], 'k-', linewidth=2, label='真实水位')
    ax1.plot(t/60, x_est_ekf[:, 0], 'b-', linewidth=1.5, alpha=0.7, label=f'EKF (RMSE={rmse_ekf_h:.4f}m)')
    ax1.plot(t/60, x_est_ukf[:, 0], 'r-', linewidth=1.5, alpha=0.7, label=f'UKF (RMSE={rmse_ukf_h:.4f}m)')
    ax1.plot(t/60, y_meas[:, 0], 'g.', markersize=1, alpha=0.3, label='测量值')
    ax1.set_xlabel('时间 (min)')
    ax1.set_ylabel('水位 (m)')
    ax1.set_title('EKF vs UKF: 水位估计对比')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # 子图2: 流量估计对比
    ax2 = fig.add_subplot(gs[1, :])
    ax2.plot(t/60, x_true_history[:, 1], 'k-', linewidth=2, label='真实流量')
    ax2.plot(t/60, x_est_ekf[:, 1], 'b-', linewidth=1.5, alpha=0.7, label=f'EKF (RMSE={rmse_ekf_Q:.4f}m³/s)')
    ax2.plot(t/60, x_est_ukf[:, 1], 'r-', linewidth=1.5, alpha=0.7, label=f'UKF (RMSE={rmse_ukf_Q:.4f}m³/s)')
    ax2.plot(t/60, y_meas[:, 1], 'g.', markersize=1, alpha=0.3, label='测量值')
    ax2.set_xlabel('时间 (min)')
    ax2.set_ylabel('流量 (m³/s)')
    ax2.set_title('EKF vs UKF: 流量估计对比')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    # 子图3: 水位估计误差
    ax3 = fig.add_subplot(gs[2, 0])
    error_ekf_h = x_est_ekf[:, 0] - x_true_history[:, 0]
    error_ukf_h = x_est_ukf[:, 0] - x_true_history[:, 0]
    ax3.plot(t/60, error_ekf_h, 'b-', linewidth=1, alpha=0.7, label='EKF误差')
    ax3.plot(t/60, error_ukf_h, 'r-', linewidth=1, alpha=0.7, label='UKF误差')
    ax3.axhline(0, color='k', linestyle=':', alpha=0.5)
    ax3.set_xlabel('时间 (min)')
    ax3.set_ylabel('水位误差 (m)')
    ax3.set_title('水位估计误差对比')
    ax3.legend()
    ax3.grid(True, alpha=0.3)

    # 子图4: 流量估计误差
    ax4 = fig.add_subplot(gs[2, 1])
    error_ekf_Q = x_est_ekf[:, 1] - x_true_history[:, 1]
    error_ukf_Q = x_est_ukf[:, 1] - x_true_history[:, 1]
    ax4.plot(t/60, error_ekf_Q, 'b-', linewidth=1, alpha=0.7, label='EKF误差')
    ax4.plot(t/60, error_ukf_Q, 'r-', linewidth=1, alpha=0.7, label='UKF误差')
    ax4.axhline(0, color='k', linestyle=':', alpha=0.5)
    ax4.set_xlabel('时间 (min)')
    ax4.set_ylabel('流量误差 (m³/s)')
    ax4.set_title('流量估计误差对比')
    ax4.legend()
    ax4.grid(True, alpha=0.3)

    plt.savefig('part4_ekf_vs_ukf.png', dpi=300, bbox_inches='tight')
    print("\n图像已保存: part4_ekf_vs_ukf.png\n")

    return {
        'rmse_ekf': (rmse_ekf_h, rmse_ekf_Q),
        'rmse_ukf': (rmse_ukf_h, rmse_ukf_Q),
        'time_ekf': time_ekf,
        'time_ukf': time_ukf
    }


def main():
    """主函数"""
    print("\n" + "="*60)
    print("案例12：扩展卡尔曼滤波（EKF）状态估计")
    print("="*60 + "\n")

    # 设置随机种子（可复现）
    np.random.seed(42)

    # Part 1: 标量系统EKF演示
    rmse_scalar = part1_scalar_ekf_demo()

    # Part 2: 运河系统状态估计
    rmse_h, rmse_Q = part2_canal_state_estimation()

    # Part 3: 多传感器融合
    rmse_multi, rmse_single = part3_multi_sensor_fusion()

    # Part 4: EKF vs UKF对比
    results = part4_ekf_vs_ukf()

    # 总结
    print("=" * 60)
    print("案例12总结")
    print("=" * 60)
    print("\n1. 标量系统EKF演示:")
    print(f"   - 估计RMSE: {rmse_scalar:.4f}")
    print(f"   - 成功处理非线性观测模型 y = x²/20")

    print("\n2. 运河系统状态估计:")
    print(f"   - 水位RMSE: {rmse_h:.4f} m")
    print(f"   - 流量RMSE: {rmse_Q:.4f} m³/s")
    print(f"   - 成功估计双状态非线性系统")

    print("\n3. 多传感器融合:")
    print(f"   - 多传感器RMSE: {rmse_multi:.4f} m")
    print(f"   - 单传感器RMSE: {rmse_single:.4f} m")
    print(f"   - 性能提升: {(rmse_single-rmse_multi)/rmse_single*100:.1f}%")
    print(f"   - 展示了传感器冗余的价值和故障容错能力")

    print("\n4. EKF vs UKF对比:")
    print(f"   - EKF水位RMSE: {results['rmse_ekf'][0]:.4f} m")
    print(f"   - UKF水位RMSE: {results['rmse_ukf'][0]:.4f} m")
    print(f"   - UKF精度提升: {(results['rmse_ekf'][0]-results['rmse_ukf'][0])/results['rmse_ekf'][0]*100:.1f}%")
    print(f"   - EKF计算时间: {results['time_ekf']*1000:.2f} ms")
    print(f"   - UKF计算时间: {results['time_ukf']*1000:.2f} ms")

    print("\n工程意义:")
    print("   - EKF是实时系统的首选（快速、够用）")
    print("   - UKF适合高精度要求、强非线性场景")
    print("   - 多传感器融合显著提高鲁棒性")
    print("   - 是数字孪生技术的核心算法")

    print("\n所有图像已生成！")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
