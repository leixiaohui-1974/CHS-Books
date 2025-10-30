#!/usr/bin/env python3
"""
案例11：SINDy稀疏辨识
Sparse Identification of Nonlinear Dynamics

实现：
1. SINDy核心算法（STLS）
2. 函数库构建（多项式、三角函数）
3. Lorenz系统验证
4. 渠道系统方程发现
5. 集成SINDy

作者：Claude
日期：2025
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from scipy import signal, integrate
from itertools import combinations_with_replacement
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

# ==================== 渠道系统仿真 ====================

class CanalReach:
    """渠段模型"""
    def __init__(self, L=1000, B=5, i0=0.001, n=0.025, N=51):
        self.L = L
        self.B = B
        self.i0 = i0
        self.n = n
        self.N = N
        self.dx = L / (N - 1)
        self.x = np.linspace(0, L, N)
        self.h = np.ones(N) * 1.0
        self.Q = np.ones(N) * 5.0
        self.q_lat = np.zeros(N)
        self.g = 9.81

    def set_state(self, h, Q):
        self.h = h.copy()
        self.Q = Q.copy()

    def manning_flow(self, h):
        A = self.B * h
        P = self.B + 2 * h
        R = A / (P + 1e-6)
        Q = (1/self.n) * A * R**(2/3) * np.sqrt(self.i0)
        return Q

    def friction_slope(self, Q, h):
        A = self.B * h
        P = self.B + 2 * h
        R = A / (P + 1e-6)
        if R > 1e-6:
            Sf = (self.n * Q / A)**2 / R**(4/3)
        else:
            Sf = self.i0
        return Sf

    def step(self, dt, Q_in=None, Q_out=None):
        h, Q = self.h.copy(), self.Q.copy()
        h_new, Q_new = h.copy(), Q.copy()

        if Q_in is not None:
            Q_new[0] = Q_in

        for i in range(1, self.N-1):
            dQ_dx = (Q[i+1] - Q[i-1]) / (2 * self.dx)
            h_new[i] = h[i] - dt * (dQ_dx / self.B - self.q_lat[i])
            h_new[i] = np.clip(h_new[i], 0.1, 10.0)

        if Q_out is not None:
            Q_new[-1] = Q_out
        else:
            Q_new[-1] = self.manning_flow(h_new[-1])

        for i in range(1, self.N-1):
            A_i = self.B * h[i]
            dh_dx = (h[i+1] - h[i-1]) / (2 * self.dx)
            Sf_i = self.friction_slope(Q[i], h[i])
            Sf_i = np.clip(Sf_i, 0.0, 0.1)
            Q_new[i] = Q[i] - dt * (self.g * A_i * (dh_dx + Sf_i - self.i0))

        h_new = np.nan_to_num(h_new, nan=1.0, posinf=10.0, neginf=0.1)
        Q_new = np.nan_to_num(Q_new, nan=5.0, posinf=50.0, neginf=0.1)

        self.h = h_new
        self.Q = Q_new

        return h_new, Q_new


class GateModel:
    """闸门模型"""
    def __init__(self, B=5):
        self.B = B
        self.g = 9.81

    def flow(self, h_up, opening):
        if opening < 0.01:
            return 0.0
        Cd = 0.6
        Q = Cd * self.B * opening * np.sqrt(2 * self.g * h_up)
        return Q


# ==================== SINDy算法 ====================

class SINDy:
    """
    SINDy: Sparse Identification of Nonlinear Dynamics
    """
    def __init__(self, threshold=0.05, max_iter=10, alpha=0.05):
        """
        参数：
            threshold: 稀疏阈值
            max_iter: STLS最大迭代次数
            alpha: 正则化参数（可选）
        """
        self.threshold = threshold
        self.max_iter = max_iter
        self.alpha = alpha

        self.Xi = None  # 系数矩阵
        self.feature_names = []  # 特征名称

    def fit(self, X, Xdot, library_function):
        """
        拟合SINDy模型

        参数：
            X: 状态数据 (m, n) - m个时间点，n维状态
            Xdot: 状态导数 (m, n)
            library_function: 函数库构造函数
        """
        # 构造函数库
        Theta, self.feature_names = library_function(X)

        # STLS算法
        self.Xi = self._stls(Theta, Xdot)

        return self.Xi

    def _stls(self, Theta, Xdot):
        """Sequential Threshold Least Squares"""
        n = Xdot.shape[1]
        p = Theta.shape[1]

        # 初始最小二乘
        Xi = np.linalg.lstsq(Theta, Xdot, rcond=None)[0]

        for iteration in range(self.max_iter):
            Xi_old = Xi.copy()

            # 对每个状态变量
            for i in range(n):
                # 阈值化
                small_inds = np.abs(Xi[:, i]) < self.threshold
                Xi[small_inds, i] = 0

                # 重新拟合非零项
                big_inds = ~small_inds
                if np.sum(big_inds) > 0:
                    Xi[big_inds, i] = np.linalg.lstsq(
                        Theta[:, big_inds],
                        Xdot[:, i],
                        rcond=None
                    )[0]

            # 检查收敛
            if np.sum(np.abs(Xi - Xi_old)) < 1e-6:
                break

        return Xi

    def predict(self, x0, t, library_function):
        """
        使用发现的方程预测

        参数：
            x0: 初始状态
            t: 时间数组
            library_function: 函数库（与训练时相同）

        返回：
            X: 预测的状态轨迹
        """
        def dynamics(x, t):
            # 构造函数库
            Theta, _ = library_function(x.reshape(1, -1))
            # 计算导数
            dxdt = Theta @ self.Xi
            return dxdt.flatten()

        # 数值积分
        X = integrate.odeint(dynamics, x0, t)
        return X

    def print_equations(self, state_names=None):
        """打印发现的方程"""
        n = self.Xi.shape[1]

        if state_names is None:
            state_names = [f'x{i}' for i in range(n)]

        print("\n发现的控制方程:")
        print("="*60)

        for i in range(n):
            # 非零项
            nonzero_idx = np.abs(self.Xi[:, i]) > 1e-10

            if np.sum(nonzero_idx) == 0:
                print(f"d{state_names[i]}/dt = 0")
                continue

            terms = []
            for j, (coef, name) in enumerate(zip(self.Xi[:, i], self.feature_names)):
                if np.abs(coef) > 1e-10:
                    if coef > 0:
                        terms.append(f"+{coef:.4f}*{name}")
                    else:
                        terms.append(f"{coef:.4f}*{name}")

            equation = f"d{state_names[i]}/dt = " + " ".join(terms)
            print(equation)

        print("="*60)

    def score(self, X, Xdot, library_function):
        """计算R²分数"""
        Theta, _ = library_function(X)
        Xdot_pred = Theta @ self.Xi

        ss_res = np.sum((Xdot - Xdot_pred)**2)
        ss_tot = np.sum((Xdot - np.mean(Xdot, axis=0))**2)

        r2 = 1 - ss_res / ss_tot
        return r2


# ==================== 函数库构造 ====================

def polynomial_library(X, degree=2, include_bias=True):
    """
    多项式函数库

    参数：
        X: 数据 (m, n)
        degree: 多项式阶数
        include_bias: 是否包含常数项

    返回：
        Theta: 函数库矩阵
        names: 特征名称
    """
    m, n = X.shape
    features = []
    names = []

    # 常数项
    if include_bias:
        features.append(np.ones(m))
        names.append('1')

    # 状态变量名
    var_names = [f'x{i}' for i in range(n)]

    # 生成所有组合
    for d in range(1, degree + 1):
        for combo in combinations_with_replacement(range(n), d):
            # 计算特征
            feature = np.ones(m)
            name_parts = []

            for idx in combo:
                feature *= X[:, idx]
                name_parts.append(var_names[idx])

            features.append(feature)

            # 生成名称
            if len(set(combo)) == 1:
                # 单变量的幂
                name = f"{var_names[combo[0]]}^{len(combo)}" if len(combo) > 1 else var_names[combo[0]]
            else:
                # 混合项
                name = "*".join(name_parts)

            names.append(name)

    Theta = np.column_stack(features)
    return Theta, names


def polynomial_library_with_trig(X, poly_degree=2, include_trig=True):
    """
    多项式+三角函数库

    参数：
        X: 数据
        poly_degree: 多项式阶数
        include_trig: 是否包含三角函数
    """
    # 先构造多项式库
    Theta_poly, names_poly = polynomial_library(X, degree=poly_degree)

    if not include_trig:
        return Theta_poly, names_poly

    # 添加三角函数
    m, n = X.shape
    trig_features = []
    trig_names = []

    for i in range(n):
        trig_features.append(np.sin(X[:, i]))
        trig_names.append(f'sin(x{i})')

        trig_features.append(np.cos(X[:, i]))
        trig_names.append(f'cos(x{i})')

    if len(trig_features) > 0:
        Theta_trig = np.column_stack(trig_features)
        Theta = np.hstack([Theta_poly, Theta_trig])
        names = names_poly + trig_names
    else:
        Theta = Theta_poly
        names = names_poly

    return Theta, names


# ==================== 数值微分 ====================

def finite_difference(X, dt, order=1):
    """
    有限差分法计算导数

    参数：
        X: 数据 (m, n)
        dt: 时间步长
        order: 1=前向，2=中心

    返回：
        Xdot: 导数
    """
    m, n = X.shape
    Xdot = np.zeros_like(X)

    if order == 1:
        # 前向差分
        Xdot[:-1, :] = (X[1:, :] - X[:-1, :]) / dt
        Xdot[-1, :] = Xdot[-2, :]  # 最后一点用前一点
    elif order == 2:
        # 中心差分
        Xdot[1:-1, :] = (X[2:, :] - X[:-2, :]) / (2 * dt)
        Xdot[0, :] = (X[1, :] - X[0, :]) / dt  # 边界用前向
        Xdot[-1, :] = (X[-1, :] - X[-2, :]) / dt
    else:
        raise ValueError("order must be 1 or 2")

    return Xdot


def polynomial_derivative(X, dt, window=5, poly_order=3):
    """
    多项式拟合法计算导数（更稳健）

    参数：
        X: 数据 (m, n)
        dt: 时间步长
        window: 窗口大小（奇数）
        poly_order: 多项式阶数
    """
    m, n = X.shape

    # 确保window是奇数
    if window % 2 == 0:
        window += 1

    half_window = window // 2
    Xdot = np.zeros_like(X)

    for i in range(n):
        for k in range(m):
            # 确定窗口范围
            start = max(0, k - half_window)
            end = min(m, k + half_window + 1)

            # 局部时间
            t_local = np.arange(end - start) * dt

            # 多项式拟合
            try:
                coeffs = np.polyfit(t_local, X[start:end, i], poly_order)
                # 求导（解析）
                deriv_coeffs = np.polyder(coeffs)
                # 在中心点求值
                t_center = (k - start) * dt
                Xdot[k, i] = np.polyval(deriv_coeffs, t_center)
            except:
                # 如果拟合失败，使用简单差分
                if k < m - 1:
                    Xdot[k, i] = (X[k+1, i] - X[k, i]) / dt
                else:
                    Xdot[k, i] = (X[k, i] - X[k-1, i]) / dt

    return Xdot


# ==================== 集成SINDy ====================

class EnsembleSINDy:
    """
    集成SINDy：通过Bootstrap提高鲁棒性
    """
    def __init__(self, n_models=100, threshold=0.05, vote_threshold=0.5):
        """
        参数：
            n_models: 集成模型数量
            threshold: 单个模型的稀疏阈值
            vote_threshold: 投票阈值（保留频率>此值的项）
        """
        self.n_models = n_models
        self.threshold = threshold
        self.vote_threshold = vote_threshold

        self.Xi_ensemble = None  # 集成后的系数
        self.feature_names = []

    def fit(self, X, Xdot, library_function, noise_level=0.01):
        """
        拟合集成SINDy模型

        参数：
            X, Xdot: 数据
            library_function: 函数库
            noise_level: 添加噪声水平（用于Bootstrap）
        """
        m, n = X.shape

        # 存储所有模型的系数
        Xi_list = []

        print(f"运行集成SINDy ({self.n_models}个模型)...")

        for i in range(self.n_models):
            # Bootstrap采样
            indices = np.random.choice(m, m, replace=True)
            X_boot = X[indices, :]
            Xdot_boot = Xdot[indices, :]

            # 添加小噪声
            X_boot += np.random.randn(*X_boot.shape) * noise_level * np.std(X, axis=0)
            Xdot_boot += np.random.randn(*Xdot_boot.shape) * noise_level * np.std(Xdot, axis=0)

            # 拟合单个SINDy模型
            sindy = SINDy(threshold=self.threshold)
            Xi = sindy.fit(X_boot, Xdot_boot, library_function)

            Xi_list.append(Xi)

            if (i+1) % 20 == 0:
                print(f"  完成 {i+1}/{self.n_models}")

        Xi_list = np.array(Xi_list)  # (n_models, p, n)

        # 集成：投票机制
        # 某项在多数模型中非零 → 保留
        nonzero_votes = np.sum(np.abs(Xi_list) > 1e-10, axis=0)  # (p, n)
        vote_ratio = nonzero_votes / self.n_models

        # 对通过投票的项，取平均值
        self.Xi_ensemble = np.zeros_like(Xi_list[0])

        for i in range(Xi_list.shape[1]):  # 特征
            for j in range(Xi_list.shape[2]):  # 状态
                if vote_ratio[i, j] >= self.vote_threshold:
                    # 只对非零值取平均
                    nonzero_vals = Xi_list[:, i, j][np.abs(Xi_list[:, i, j]) > 1e-10]
                    if len(nonzero_vals) > 0:
                        self.Xi_ensemble[i, j] = np.median(nonzero_vals)

        # 保存特征名
        _, self.feature_names = library_function(X[:1, :])

        print(f"\n集成完成！")
        print(f"  保留的项数: {np.sum(np.abs(self.Xi_ensemble) > 1e-10)}")

        return self.Xi_ensemble

    def print_equations(self, state_names=None):
        """打印发现的方程"""
        sindy_temp = SINDy()
        sindy_temp.Xi = self.Xi_ensemble
        sindy_temp.feature_names = self.feature_names
        sindy_temp.print_equations(state_names)


# ==================== 演示部分 ====================

def part1_sindy_lorenz():
    """Part 1: SINDy在Lorenz系统上的验证"""
    print("\n" + "="*60)
    print("Part 1: SINDy验证（Lorenz系统）")
    print("="*60)

    # Lorenz系统参数
    sigma = 10
    rho = 28
    beta = 8/3

    print(f"Lorenz系统参数: σ={sigma}, ρ={rho}, β={beta:.3f}")

    # 生成数据
    def lorenz(state, t):
        x, y, z = state
        dxdt = sigma * (y - x)
        dydt = x * (rho - z) - y
        dzdt = x * y - beta * z
        return [dxdt, dydt, dzdt]

    # 积分
    t = np.arange(0, 50, 0.01)
    x0 = [1, 1, 1]
    X = integrate.odeint(lorenz, x0, t)

    print(f"数据长度: {len(t)} 个时间点")

    # 计算导数
    dt = t[1] - t[0]
    Xdot = polynomial_derivative(X, dt, window=5, poly_order=3)

    # SINDy辨识
    print("\n运行SINDy...")
    sindy = SINDy(threshold=0.05, max_iter=10)

    # 使用多项式库（3阶）
    library = lambda X: polynomial_library(X, degree=3, include_bias=False)

    Xi = sindy.fit(X, Xdot, library)

    # 打印方程
    sindy.print_equations(['x', 'y', 'z'])

    # 计算R²
    r2 = sindy.score(X, Xdot, library)
    print(f"\nR² 分数: {r2:.6f}")

    # 预测（长期）
    t_pred = np.arange(0, 100, 0.01)
    X_pred = sindy.predict(x0, t_pred, library)

    # 真实解（用于对比）
    X_true = integrate.odeint(lorenz, x0, t_pred)

    # 可视化
    fig = plt.figure(figsize=(14, 10))

    # 3D轨迹对比
    ax = fig.add_subplot(2, 2, 1, projection='3d')
    ax.plot(X_true[:2000, 0], X_true[:2000, 1], X_true[:2000, 2],
            'k-', linewidth=1, alpha=0.7, label='真实')
    ax.plot(X_pred[:2000, 0], X_pred[:2000, 1], X_pred[:2000, 2],
            'r--', linewidth=1, alpha=0.7, label='SINDy')
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')
    ax.set_title('Lorenz吸引子（3D轨迹）')
    ax.legend()

    # 时间序列对比
    ax = fig.add_subplot(2, 2, 2)
    ax.plot(t_pred[:500], X_true[:500, 0], 'k-', linewidth=2, label='真实', alpha=0.7)
    ax.plot(t_pred[:500], X_pred[:500, 0], 'r--', linewidth=2, label='SINDy', alpha=0.7)
    ax.set_xlabel('时间')
    ax.set_ylabel('x')
    ax.set_title('x分量时间序列')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 系数矩阵可视化
    ax = fig.add_subplot(2, 2, 3)
    im = ax.imshow(np.abs(Xi.T), aspect='auto', cmap='Reds')
    ax.set_xlabel('特征索引')
    ax.set_ylabel('状态变量')
    ax.set_yticks([0, 1, 2])
    ax.set_yticklabels(['x', 'y', 'z'])
    ax.set_title('系数矩阵（绝对值）')
    plt.colorbar(im, ax=ax)

    # 预测误差
    ax = fig.add_subplot(2, 2, 4)
    error = np.linalg.norm(X_true - X_pred, axis=1)
    ax.semilogy(t_pred, error, 'b-', linewidth=2)
    ax.set_xlabel('时间')
    ax.set_ylabel('预测误差（L2范数）')
    ax.set_title('长期预测误差')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('part1_sindy_lorenz.png', dpi=150, bbox_inches='tight')
    print("图表已保存: part1_sindy_lorenz.png")
    plt.close()


def part2_library_comparison():
    """Part 2: 函数库对比"""
    print("\n" + "="*60)
    print("Part 2: 函数库设计对比")
    print("="*60)

    # 简单摆系统：θ'' = -(g/L)sin(θ)
    g, L = 9.81, 1.0

    def pendulum(state, t):
        theta, omega = state
        dtheta = omega
        domega = -(g/L) * np.sin(theta)
        return [dtheta, domega]

    # 生成数据
    t = np.arange(0, 20, 0.02)
    x0 = [np.pi/3, 0]  # 初始角度60度
    X = integrate.odeint(pendulum, x0, t)

    dt = t[1] - t[0]
    Xdot = polynomial_derivative(X, dt)

    print(f"简单摆系统")
    print(f"真实方程: θ'' = -{g/L:.3f}*sin(θ)")

    # 测试不同函数库
    libraries = {
        '多项式(2阶)': lambda X: polynomial_library(X, degree=2, include_bias=False),
        '多项式(3阶)': lambda X: polynomial_library(X, degree=3, include_bias=False),
        '多项式+三角': lambda X: polynomial_library_with_trig(X, poly_degree=2, include_trig=True),
    }

    results = {}

    for name, lib_func in libraries.items():
        print(f"\n测试函数库: {name}")
        sindy = SINDy(threshold=0.05)
        Xi = sindy.fit(X, Xdot, lib_func)

        # 评分
        r2 = sindy.score(X, Xdot, lib_func)
        n_terms = np.sum(np.abs(Xi) > 1e-10)

        print(f"  R² = {r2:.6f}")
        print(f"  非零项数 = {n_terms}")

        # 预测
        t_pred = np.arange(0, 40, 0.02)
        X_pred = sindy.predict(x0, t_pred, lib_func)
        X_true = integrate.odeint(pendulum, x0, t_pred)

        # 长期误差
        error = np.linalg.norm(X_true - X_pred, axis=1)
        mean_error = np.mean(error[-100:])  # 后期平均误差

        results[name] = {
            'r2': r2,
            'n_terms': n_terms,
            'mean_error': mean_error,
            'X_pred': X_pred,
            'Xi': Xi
        }

        sindy.print_equations(['θ', 'ω'])

    # 可视化
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 轨迹对比
    ax = axes[0, 0]
    X_true = integrate.odeint(pendulum, x0, t_pred)
    ax.plot(X_true[:, 0], X_true[:, 1], 'k-', linewidth=2, label='真实', alpha=0.7)

    colors = ['blue', 'red', 'green']
    for (name, res), color in zip(results.items(), colors):
        ax.plot(res['X_pred'][:, 0], res['X_pred'][:, 1],
                '--', color=color, linewidth=1.5, label=name, alpha=0.7)

    ax.set_xlabel('θ (rad)')
    ax.set_ylabel('ω (rad/s)')
    ax.set_title('相平面轨迹对比')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # R²对比
    ax = axes[0, 1]
    names_list = list(results.keys())
    r2_list = [results[n]['r2'] for n in names_list]
    bars = ax.bar(range(len(names_list)), r2_list, color=colors, alpha=0.7)
    ax.set_xticks(range(len(names_list)))
    ax.set_xticklabels(names_list, rotation=15, ha='right')
    ax.set_ylabel('R² 分数')
    ax.set_title('拟合质量对比')
    ax.set_ylim([0, 1.1])
    ax.grid(True, alpha=0.3, axis='y')

    for bar, val in zip(bars, r2_list):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.4f}', ha='center', va='bottom')

    # 稀疏度对比
    ax = axes[1, 0]
    n_terms_list = [results[n]['n_terms'] for n in names_list]
    bars = ax.bar(range(len(names_list)), n_terms_list, color=colors, alpha=0.7)
    ax.set_xticks(range(len(names_list)))
    ax.set_xticklabels(names_list, rotation=15, ha='right')
    ax.set_ylabel('非零项数量')
    ax.set_title('模型稀疏度对比')
    ax.grid(True, alpha=0.3, axis='y')

    for bar, val in zip(bars, n_terms_list):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(val)}', ha='center', va='bottom')

    # 长期误差对比
    ax = axes[1, 1]
    for (name, res), color in zip(results.items(), colors):
        error = np.linalg.norm(X_true - res['X_pred'], axis=1)
        ax.semilogy(t_pred, error, color=color, linewidth=2, label=name, alpha=0.7)

    ax.set_xlabel('时间 (s)')
    ax.set_ylabel('预测误差（L2范数）')
    ax.set_title('长期预测误差')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('part2_library_comparison.png', dpi=150, bbox_inches='tight')
    print("\n图表已保存: part2_library_comparison.png")
    plt.close()


def part3_canal_discovery():
    """Part 3: 渠道系统方程发现"""
    print("\n" + "="*60)
    print("Part 3: 渠道系统方程发现")
    print("="*60)

    # 简化的渠道动力学（降阶模型）
    # 状态：[h, Q] 在某个固定位置
    # 控制：u（闸门开度）

    print("生成渠道系统数据...")
    canal = CanalReach(N=51)
    gate = GateModel()

    dt_sim = 10.0
    t = np.arange(0, 1800, dt_sim)
    N = len(t)

    # 初始化
    h0 = np.ones(51) * 1.5
    Q0 = np.ones(51) * 5.0
    canal.set_state(h0, Q0)

    # PRBS激励
    np.random.seed(42)
    u_signal = np.zeros(N)
    for k in range(N):
        if k % 10 == 0:
            u_signal[k] = np.random.uniform(0.3, 0.7)
        else:
            u_signal[k] = u_signal[k-1]

    # 仿真并记录（取中点的h和Q）
    h_history = []
    Q_history = []

    for k in range(N):
        u_k = u_signal[k]
        Q_out = gate.flow(canal.h[-1], u_k)
        Q_in = 5.0
        canal.step(dt_sim, Q_in=Q_in, Q_out=Q_out)

        # 记录中点状态
        idx_mid = len(canal.h) // 2
        h_history.append(canal.h[idx_mid])
        Q_history.append(canal.Q[idx_mid])

    # 构造状态矩阵
    X = np.column_stack([h_history, Q_history])  # [h, Q]

    # 中心化
    X_mean = np.mean(X, axis=0)
    X_centered = X - X_mean

    print(f"数据长度: {N} 个时间点")
    print(f"状态范围: h=[{np.min(X[:, 0]):.2f}, {np.max(X[:, 0]):.2f}], " +
          f"Q=[{np.min(X[:, 1]):.2f}, {np.max(X[:, 1]):.2f}]")

    # 计算导数
    Xdot = polynomial_derivative(X_centered, dt_sim, window=5)

    # SINDy辨识
    print("\n运行SINDy...")
    sindy = SINDy(threshold=0.02)

    # 使用简单多项式库（2阶）
    library = lambda X: polynomial_library(X, degree=2, include_bias=True)

    Xi = sindy.fit(X_centered, Xdot, library)

    # 打印方程
    sindy.print_equations(['h', 'Q'])

    # 预测验证
    # 使用后半段数据验证
    N_train = N // 2
    X_test = X_centered[N_train:, :]

    # 逐步预测
    X_pred = np.zeros_like(X_test)
    X_pred[0, :] = X_test[0, :]

    for k in range(1, len(X_test)):
        Theta, _ = library(X_pred[k-1:k, :])
        X_pred[k, :] = X_pred[k-1, :] + dt_sim * (Theta @ Xi).flatten()

    # 计算误差
    rmse = np.sqrt(np.mean((X_test - X_pred)**2, axis=0))
    print(f"\n预测RMSE: h={rmse[0]:.6f}, Q={rmse[1]:.6f}")

    # 可视化
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 状态轨迹（h vs Q）
    ax = axes[0, 0]
    ax.plot(X[:N_train, 0], X[:N_train, 1], 'b-',
            linewidth=1, label='训练数据', alpha=0.7)
    ax.plot(X[N_train:, 0], X[N_train:, 1], 'k-',
            linewidth=2, label='测试数据（真实）', alpha=0.7)
    ax.plot(X_pred[:, 0] + X_mean[0], X_pred[:, 1] + X_mean[1], 'r--',
            linewidth=2, label='SINDy预测', alpha=0.7)
    ax.set_xlabel('水位 h (m)')
    ax.set_ylabel('流量 Q (m³/s)')
    ax.set_title('状态空间轨迹')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # h时间序列
    ax = axes[0, 1]
    t_test = t[N_train:]
    ax.plot(t_test / 60, X[N_train:, 0], 'k-',
            linewidth=2, label='真实', alpha=0.7)
    ax.plot(t_test / 60, X_pred[:, 0] + X_mean[0], 'r--',
            linewidth=2, label=f'SINDy (RMSE={rmse[0]:.3f})', alpha=0.7)
    ax.set_xlabel('时间 (分钟)')
    ax.set_ylabel('水位 h (m)')
    ax.set_title('水位预测')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Q时间序列
    ax = axes[1, 0]
    ax.plot(t_test / 60, X[N_train:, 1], 'k-',
            linewidth=2, label='真实', alpha=0.7)
    ax.plot(t_test / 60, X_pred[:, 1] + X_mean[1], 'r--',
            linewidth=2, label=f'SINDy (RMSE={rmse[1]:.3f})', alpha=0.7)
    ax.set_xlabel('时间 (分钟)')
    ax.set_ylabel('流量 Q (m³/s)')
    ax.set_title('流量预测')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 系数矩阵
    ax = axes[1, 1]
    im = ax.imshow(np.abs(Xi.T), aspect='auto', cmap='Reds')
    ax.set_xlabel('特征索引')
    ax.set_ylabel('状态变量')
    ax.set_yticks([0, 1])
    ax.set_yticklabels(['h', 'Q'])
    ax.set_title('SINDy系数矩阵')
    plt.colorbar(im, ax=ax, label='|系数|')

    plt.tight_layout()
    plt.savefig('part3_canal_discovery.png', dpi=150, bbox_inches='tight')
    print("图表已保存: part3_canal_discovery.png")
    plt.close()


def part4_ensemble_sindy():
    """Part 4: 集成SINDy鲁棒性测试"""
    print("\n" + "="*60)
    print("Part 4: 集成SINDy鲁棒性测试")
    print("="*60)

    # 使用范德波尔振子
    mu = 1.0

    def van_der_pol(state, t):
        x, y = state
        dxdt = y
        dydt = mu * (1 - x**2) * y - x
        return [dxdt, dydt]

    # 生成数据
    t = np.arange(0, 25, 0.05)
    x0 = [2, 0]
    X_clean = integrate.odeint(van_der_pol, x0, t)

    # 添加噪声
    noise_level = 0.1
    X_noisy = X_clean + noise_level * np.std(X_clean, axis=0) * np.random.randn(*X_clean.shape)

    print(f"数据长度: {len(t)}")
    print(f"噪声水平: {noise_level*100}% std")

    dt = t[1] - t[0]

    # 计算导数（使用稳健方法）
    Xdot_clean = polynomial_derivative(X_clean, dt, window=5)
    Xdot_noisy = polynomial_derivative(X_noisy, dt, window=7)  # 更大窗口

    # 方法1: 普通SINDy（无噪声数据）
    print("\n方法1: 普通SINDy (无噪声)")
    sindy_clean = SINDy(threshold=0.05)
    library = lambda X: polynomial_library(X, degree=3, include_bias=False)
    Xi_clean = sindy_clean.fit(X_clean, Xdot_clean, library)
    sindy_clean.print_equations(['x', 'y'])

    # 方法2: 普通SINDy（含噪声数据）
    print("\n方法2: 普通SINDy (含噪声)")
    sindy_noisy = SINDy(threshold=0.05)
    Xi_noisy = sindy_noisy.fit(X_noisy, Xdot_noisy, library)
    sindy_noisy.print_equations(['x', 'y'])

    # 方法3: 集成SINDy（含噪声数据）
    print("\n方法3: 集成SINDy (含噪声)")
    ensemble = EnsembleSINDy(n_models=50, threshold=0.05, vote_threshold=0.6)
    Xi_ensemble = ensemble.fit(X_noisy, Xdot_noisy, library, noise_level=0.02)
    ensemble.print_equations(['x', 'y'])

    # 预测对比
    t_pred = np.arange(0, 50, 0.05)
    X_true = integrate.odeint(van_der_pol, x0, t_pred)

    X_pred_clean = sindy_clean.predict(x0, t_pred, library)
    X_pred_noisy = sindy_noisy.predict(x0, t_pred, library)

    # 集成SINDy预测（手动）
    def dynamics_ensemble(x, t):
        Theta, _ = library(x.reshape(1, -1))
        dxdt = Theta @ Xi_ensemble
        return dxdt.flatten()

    X_pred_ensemble = integrate.odeint(dynamics_ensemble, x0, t_pred)

    # 可视化
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 相平面轨迹
    ax = axes[0, 0]
    ax.plot(X_true[:, 0], X_true[:, 1], 'k-', linewidth=2,
            label='真实', alpha=0.7)
    ax.plot(X_pred_clean[:, 0], X_pred_clean[:, 1], 'b--',
            linewidth=1.5, label='无噪声SINDy', alpha=0.7)
    ax.plot(X_pred_noisy[:, 0], X_pred_noisy[:, 1], 'r:',
            linewidth=1.5, label='含噪声SINDy', alpha=0.7)
    ax.plot(X_pred_ensemble[:, 0], X_pred_ensemble[:, 1], 'g--',
            linewidth=1.5, label='集成SINDy', alpha=0.7)
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_title('相平面轨迹对比')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 时间序列
    ax = axes[0, 1]
    ax.plot(t_pred[:400], X_true[:400, 0], 'k-', linewidth=2, label='真实', alpha=0.7)
    ax.plot(t_pred[:400], X_pred_clean[:400, 0], 'b--',
            linewidth=1.5, label='无噪声SINDy', alpha=0.7)
    ax.plot(t_pred[:400], X_pred_noisy[:400, 0], 'r:',
            linewidth=1.5, label='含噪声SINDy', alpha=0.7)
    ax.plot(t_pred[:400], X_pred_ensemble[:400, 0], 'g--',
            linewidth=1.5, label='集成SINDy', alpha=0.7)
    ax.set_xlabel('时间')
    ax.set_ylabel('x')
    ax.set_title('x分量时间序列')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 长期误差
    ax = axes[1, 0]
    error_clean = np.linalg.norm(X_true - X_pred_clean, axis=1)
    error_noisy = np.linalg.norm(X_true - X_pred_noisy, axis=1)
    error_ensemble = np.linalg.norm(X_true - X_pred_ensemble, axis=1)

    ax.semilogy(t_pred, error_clean, 'b-', linewidth=2, label='无噪声SINDy', alpha=0.7)
    ax.semilogy(t_pred, error_noisy, 'r-', linewidth=2, label='含噪声SINDy', alpha=0.7)
    ax.semilogy(t_pred, error_ensemble, 'g-', linewidth=2, label='集成SINDy', alpha=0.7)
    ax.set_xlabel('时间')
    ax.set_ylabel('预测误差（L2范数）')
    ax.set_title('长期预测误差对比')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 系数对比
    ax = axes[1, 1]
    coef_comparison = np.array([
        np.abs(Xi_clean[:, 1]),  # y方程的系数
        np.abs(Xi_noisy[:, 1]),
        np.abs(Xi_ensemble[:, 1])
    ])

    im = ax.imshow(coef_comparison, aspect='auto', cmap='YlOrRd')
    ax.set_xlabel('特征索引')
    ax.set_yticks([0, 1, 2])
    ax.set_yticklabels(['无噪声', '含噪声', '集成'])
    ax.set_title('y方程系数对比（绝对值）')
    plt.colorbar(im, ax=ax, label='|系数|')

    plt.tight_layout()
    plt.savefig('part4_ensemble_sindy.png', dpi=150, bbox_inches='tight')
    print("图表已保存: part4_ensemble_sindy.png")
    plt.close()

    # 打印误差统计
    print(f"\n长期误差统计（t={t_pred[-1]:.1f}）:")
    print(f"  无噪声SINDy: {error_clean[-1]:.6f}")
    print(f"  含噪声SINDy: {error_noisy[-1]:.6f}")
    print(f"  集成SINDy: {error_ensemble[-1]:.6f}")


def main():
    """主函数"""
    print("="*60)
    print("案例11：SINDy稀疏辨识")
    print("Sparse Identification of Nonlinear Dynamics")
    print("="*60)

    # 运行所有部分
    part1_sindy_lorenz()
    part2_library_comparison()
    part3_canal_discovery()
    part4_ensemble_sindy()

    print("\n" + "="*60)
    print("案例11完成！所有图表已保存。")
    print("="*60)

    print("\n关键结论：")
    print("1. SINDy能从数据中自动发现控制方程")
    print("2. 稀疏优化是核心，假设方程只包含少量项")
    print("3. 函数库设计直接影响发现质量")
    print("4. 数值微分对噪声敏感，需要稳健方法")
    print("5. 集成SINDy显著提高鲁棒性")
    print("6. SINDy的可解释性是最大优势")


if __name__ == "__main__":
    main()
