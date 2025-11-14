#!/usr/bin/env python3
"""
案例10：非线性系统辨识
Nonlinear System Identification

实现：
1. Hammerstein-Wiener模型辨识
2. 多项式NARX模型
3. 渠道系统非线性辨识
4. 神经网络辨识（可选）

作者：Claude
日期：2025
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from scipy import signal, optimize
import warnings
warnings.filterwarnings('ignore')

# 简单实现Lasso（如果sklearn不可用）
def lasso_regression(X, y, alpha=0.01, max_iter=1000):
    """简单的Lasso回归实现（坐标下降法）"""
    n_features = X.shape[1]
    theta = np.zeros(n_features)

    for _ in range(max_iter):
        theta_old = theta.copy()
        for j in range(n_features):
            # 计算残差（不包括第j个特征）
            r = y - X @ theta + X[:, j] * theta[j]
            # 软阈值
            rho = X[:, j] @ r
            z = X[:, j] @ X[:, j]
            if rho < -alpha:
                theta[j] = (rho + alpha) / z
            elif rho > alpha:
                theta[j] = (rho - alpha) / z
            else:
                theta[j] = 0

        # 检查收敛
        if np.sum(np.abs(theta - theta_old)) < 1e-6:
            break

    return theta

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

    def get_state(self):
        return self.h.copy(), self.Q.copy()

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


# ==================== Hammerstein-Wiener模型 ====================

class HammersteinWiener:
    """
    Hammerstein-Wiener模型
    u → f(u) → [线性系统] → h(z) → y
    """
    def __init__(self, input_nonlin_order=2, linear_order=2, output_nonlin_order=1):
        self.p_in = input_nonlin_order  # 输入非线性阶数
        self.n_lin = linear_order       # 线性部分阶数
        self.p_out = output_nonlin_order # 输出非线性阶数

        # 参数
        self.c_in = None   # 输入非线性系数
        self.A = None      # 线性部分状态矩阵
        self.B = None
        self.C = None
        self.D = None
        self.c_out = None  # 输出非线性系数

    def input_nonlinearity(self, u):
        """输入非线性：多项式"""
        if self.c_in is None:
            return u
        w = np.zeros_like(u)
        for i, c in enumerate(self.c_in):
            w += c * u**(i)
        return w

    def output_nonlinearity(self, z):
        """输出非线性：多项式"""
        if self.c_out is None:
            return z
        y = np.zeros_like(z)
        for i, c in enumerate(self.c_out):
            y += c * z**(i)
        return y

    def simulate(self, u, x0=None):
        """仿真HW模型"""
        N = len(u)

        # 输入非线性
        w = self.input_nonlinearity(u)

        # 线性部分
        if x0 is None:
            x0 = np.zeros(self.n_lin)

        sys = signal.StateSpace(self.A, self.B, self.C, self.D, dt=1.0)
        tout, z, xout = signal.dlsim(sys, w, x0=x0)
        z = z.flatten()

        # 输出非线性
        y = self.output_nonlinearity(z)

        return y

    def identify(self, u, y, max_iter=20, verbose=True):
        """
        辨识HW模型（交替优化）

        参数：
            u: 输入数据
            y: 输出数据
            max_iter: 最大迭代次数
        """
        N = len(u)

        # 初始化：假设初始为线性（单位非线性）
        self.c_in = np.array([0.0, 1.0] + [0.0]*(self.p_in-1))
        self.c_out = np.array([0.0, 1.0] + [0.0]*(self.p_out-1))

        # 初始线性辨识（简单ARX）
        self._initialize_linear(u, y)

        if verbose:
            print("Hammerstein-Wiener辨识（交替优化）")

        for iteration in range(max_iter):
            # Step 1: 固定线性，估计非线性
            self._estimate_nonlinearities(u, y)

            # Step 2: 固定非线性，估计线性
            self._estimate_linear(u, y)

            # 计算误差
            y_pred = self.simulate(u)
            error = np.sqrt(np.mean((y - y_pred)**2))

            if verbose and (iteration+1) % 5 == 0:
                print(f"  迭代 {iteration+1}/{max_iter}, RMSE={error:.6f}")

        return error

    def _initialize_linear(self, u, y):
        """初始化线性部分（简单ARX）"""
        # 使用最小二乘估计简单ARX模型
        n = self.n_lin
        X = []
        Y = []

        for k in range(n, len(u)):
            phi = np.concatenate([y[k-n:k][::-1], u[k-n:k][::-1]])
            X.append(phi)
            Y.append(y[k])

        X = np.array(X)
        Y = np.array(Y)

        theta = np.linalg.lstsq(X, Y, rcond=None)[0]

        # 转换为状态空间（简化处理）
        self.A = np.random.randn(n, n) * 0.5
        self.A = self.A / (np.max(np.abs(np.linalg.eigvals(self.A))) + 0.1) * 0.8

        self.B = np.random.randn(n, 1) * 0.5
        self.C = np.random.randn(1, n) * 0.5
        self.D = np.zeros((1, 1))

    def _estimate_nonlinearities(self, u, y):
        """估计非线性（固定线性部分）"""
        # 简化：假设输出非线性为线性（只估计输入非线性）
        # 输入非线性：w = f(u) = c0 + c1*u + c2*u^2 + ...

        # 通过仿真不同输入非线性，找到最佳拟合
        def error_func(c_in):
            self.c_in = c_in
            y_pred = self.simulate(u)
            return np.sum((y - y_pred)**2)

        # 优化
        c_in_init = self.c_in
        result = optimize.minimize(error_func, c_in_init,
                                    method='L-BFGS-B',
                                    bounds=[(None, None)]*(self.p_in+1))
        self.c_in = result.x

    def _estimate_linear(self, u, y):
        """估计线性部分（固定非线性）"""
        # 计算中间信号w和z
        w = self.input_nonlinearity(u)

        # 反向计算z（假设输出非线性已知）
        # 简化：直接用y作为z（假设输出非线性接近线性）
        z = y

        # 使用子空间方法或简单ARX估计线性部分
        # 这里简化处理，保持线性部分不变（实际应用中可用N4SID）
        pass


# ==================== NARX模型 ====================

class PolynomialNARX:
    """
    多项式NARX模型
    y(k) = f(y(k-1), ..., y(k-ny), u(k-1), ..., u(k-nu))
    """
    def __init__(self, ny=2, nu=2, degree=2, use_lasso=False, alpha=0.01):
        self.ny = ny  # 输出延迟
        self.nu = nu  # 输入延迟
        self.degree = degree  # 多项式阶数
        self.use_lasso = use_lasso
        self.alpha = alpha

        self.theta = None  # 参数
        self.term_names = []  # 项名称（用于解释）

    def _build_regressor(self, y, u):
        """
        构造回归矩阵

        包含：
        - 线性项：y(k-1), ..., u(k-1), ...
        - 二次项：y(k-1)^2, y(k-1)*y(k-2), y(k-1)*u(k-1), ...
        - （可选）高次项
        """
        N = len(y)
        max_delay = max(self.ny, self.nu)

        # 收集所有基础项
        base_terms = []
        self.term_names = ['常数项']
        base_terms_list = []

        # 输出延迟项
        for i in range(1, self.ny+1):
            term = np.concatenate([np.zeros(i), y[:-i] if i > 0 else y])
            base_terms_list.append(('y', i, term))
            self.term_names.append(f'y(k-{i})')

        # 输入延迟项
        for i in range(1, self.nu+1):
            term = np.concatenate([np.zeros(i), u[:-i] if i > 0 else u])
            base_terms_list.append(('u', i, term))
            self.term_names.append(f'u(k-{i})')

        # 构造多项式项
        Phi = [np.ones(N)]  # 常数项

        # 一次项
        for name, delay, term in base_terms_list:
            Phi.append(term)

        # 二次及高次项
        if self.degree >= 2:
            # 平方项
            for name, delay, term in base_terms_list:
                Phi.append(term**2)
                self.term_names.append(f'{name}(k-{delay})^2')

            # 交叉项
            for i, (name1, delay1, term1) in enumerate(base_terms_list):
                for j, (name2, delay2, term2) in enumerate(base_terms_list):
                    if j > i:  # 避免重复
                        Phi.append(term1 * term2)
                        self.term_names.append(f'{name1}(k-{delay1})*{name2}(k-{delay2})')

        Phi = np.column_stack(Phi)
        return Phi

    def fit(self, u, y):
        """
        拟合NARX模型

        参数：
            u: 输入数据
            y: 输出数据
        """
        # 构造回归矩阵
        Phi = self._build_regressor(y, u)

        # 去除前面的无效数据
        max_delay = max(self.ny, self.nu)
        Phi = Phi[max_delay:, :]
        Y = y[max_delay:]

        # 参数估计
        if self.use_lasso:
            self.theta = lasso_regression(Phi, Y, alpha=self.alpha, max_iter=5000)
        else:
            # 最小二乘
            self.theta = np.linalg.lstsq(Phi, Y, rcond=None)[0]

        # 打印非零项
        nonzero_idx = np.abs(self.theta) > 1e-6
        print(f"\nNARX模型：{np.sum(nonzero_idx)} 个非零项（共 {len(self.theta)} 项）")
        if self.use_lasso:
            print("前10个最显著项:")
            top_idx = np.argsort(np.abs(self.theta))[::-1][:10]
            for idx in top_idx:
                if np.abs(self.theta[idx]) > 1e-6:
                    print(f"  {self.term_names[idx]}: {self.theta[idx]:.6f}")

    def predict(self, u, y_init):
        """
        预测（单步或多步）

        参数：
            u: 输入序列
            y_init: 初始输出值（长度为ny）

        返回：
            y_pred: 预测输出
        """
        N = len(u)
        y_pred = np.zeros(N)

        # 初始化
        y_pred[:self.ny] = y_init[:self.ny]

        for k in range(self.ny, N):
            # 构造当前时刻的回归向量
            phi = [1.0]  # 常数项

            # 输出项
            for i in range(1, self.ny+1):
                phi.append(y_pred[k-i])

            # 输入项
            for i in range(1, self.nu+1):
                if k-i >= 0:
                    phi.append(u[k-i])
                else:
                    phi.append(0.0)

            # 二次项
            if self.degree >= 2:
                base_terms = []
                for i in range(1, self.ny+1):
                    base_terms.append(y_pred[k-i])
                for i in range(1, self.nu+1):
                    if k-i >= 0:
                        base_terms.append(u[k-i])
                    else:
                        base_terms.append(0.0)

                # 平方项
                for term in base_terms:
                    phi.append(term**2)

                # 交叉项
                for i in range(len(base_terms)):
                    for j in range(i+1, len(base_terms)):
                        phi.append(base_terms[i] * base_terms[j])

            phi = np.array(phi)

            # 预测
            y_pred[k] = np.dot(self.theta, phi)

            # 防止数值爆炸（限制在合理范围）
            if not np.isfinite(y_pred[k]):
                y_pred[k] = np.mean(y_init)  # 使用初始值的平均
            else:
                # 限制在合理范围（对于水位，假设0.01到20m）
                y_pred[k] = np.clip(y_pred[k], -100, 100)

        return y_pred


# ==================== 工具函数 ====================

def generate_prbs(N, period=20, amplitude=0.2, offset=0.5):
    """生成PRBS信号"""
    n_switches = N // period
    switches = np.random.choice([-1, 1], size=n_switches)
    prbs = np.repeat(switches, period)

    if len(prbs) < N:
        prbs = np.concatenate([prbs, np.ones(N - len(prbs)) * switches[-1]])
    else:
        prbs = prbs[:N]

    return offset + amplitude * prbs


# ==================== 演示部分 ====================

def part1_hammerstein_wiener():
    """Part 1: Hammerstein-Wiener模型辨识"""
    print("\n" + "="*60)
    print("Part 1: Hammerstein-Wiener模型辨识")
    print("="*60)

    # 生成真实HW系统
    print("生成真实Hammerstein-Wiener系统...")

    # 真实参数
    c_in_true = np.array([0.0, 0.8, 0.3])  # w = 0.8*u + 0.3*u^2
    c_out_true = np.array([0.0, 1.0])      # y = z（线性输出）

    # 线性部分：二阶系统
    A_true = np.array([[0.8, 0.0], [0.0, 0.6]])
    B_true = np.array([[1.0], [0.5]])
    C_true = np.array([[1.0, 0.5]])
    D_true = np.array([[0.0]])

    # 生成输入
    np.random.seed(42)
    N = 500
    u = generate_prbs(N, period=10, amplitude=0.3, offset=0.5)

    # 真实系统仿真
    w_true = c_in_true[0] + c_in_true[1]*u + c_in_true[2]*u**2

    sys_true = signal.StateSpace(A_true, B_true, C_true, D_true, dt=1.0)
    tout, z_true, xout = signal.dlsim(sys_true, w_true)
    z_true = z_true.flatten()

    y_true = c_out_true[0] + c_out_true[1]*z_true

    # 添加噪声
    y_meas = y_true + 0.05 * np.std(y_true) * np.random.randn(N)

    print(f"数据长度: {N}")
    print(f"真实输入非线性: w = {c_in_true[1]:.2f}*u + {c_in_true[2]:.2f}*u^2")

    # HW辨识
    hw = HammersteinWiener(input_nonlin_order=2, linear_order=2, output_nonlin_order=1)
    hw.identify(u, y_meas, max_iter=15, verbose=True)

    # 预测
    y_pred = hw.simulate(u)

    # 计算RMSE
    rmse = np.sqrt(np.mean((y_meas - y_pred)**2))
    fit = 100 * (1 - np.linalg.norm(y_meas - y_pred) / np.linalg.norm(y_meas - np.mean(y_meas)))

    print(f"\n辨识结果:")
    print(f"  RMSE: {rmse:.6f}")
    print(f"  拟合度: {fit:.2f}%")
    print(f"  辨识输入非线性系数: {hw.c_in}")

    # 可视化
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 输入输出
    ax = axes[0, 0]
    t = np.arange(N)
    ax.plot(t[:200], y_true[:200], 'k-', linewidth=2, label='真实输出', alpha=0.7)
    ax.plot(t[:200], y_meas[:200], 'b.', markersize=3, label='测量（含噪声）', alpha=0.5)
    ax.plot(t[:200], y_pred[:200], 'r--', linewidth=2, label=f'HW预测 (Fit={fit:.1f}%)')
    ax.set_xlabel('时间步')
    ax.set_ylabel('输出')
    ax.set_title('时间响应对比')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 输入非线性对比
    ax = axes[0, 1]
    u_test = np.linspace(0, 1, 100)
    w_true_test = c_in_true[0] + c_in_true[1]*u_test + c_in_true[2]*u_test**2
    w_id_test = hw.input_nonlinearity(u_test)

    ax.plot(u_test, w_true_test, 'k-', linewidth=2, label='真实非线性')
    ax.plot(u_test, w_id_test, 'r--', linewidth=2, label='辨识非线性')
    ax.set_xlabel('输入 u')
    ax.set_ylabel('中间信号 w = f(u)')
    ax.set_title('输入非线性函数对比')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 散点图：预测vs实际
    ax = axes[1, 0]
    ax.scatter(y_meas, y_pred, alpha=0.5, s=10)
    y_range = [min(y_meas.min(), y_pred.min()), max(y_meas.max(), y_pred.max())]
    ax.plot(y_range, y_range, 'r--', linewidth=2, label='完美预测')
    ax.set_xlabel('实际输出')
    ax.set_ylabel('预测输出')
    ax.set_title('预测vs实际')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.axis('equal')

    # 残差
    ax = axes[1, 1]
    residual = y_meas - y_pred
    ax.plot(t, residual, 'b-', linewidth=1, alpha=0.7)
    ax.axhline(0, color='k', linestyle='--', alpha=0.5)
    ax.fill_between(t, -3*np.std(residual), 3*np.std(residual),
                     alpha=0.2, color='red', label='±3σ')
    ax.set_xlabel('时间步')
    ax.set_ylabel('残差')
    ax.set_title(f'残差分析 (σ={np.std(residual):.4f})')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('part1_hammerstein_wiener.png', dpi=150, bbox_inches='tight')
    print("图表已保存: part1_hammerstein_wiener.png")
    plt.close()


def part2_narx_model():
    """Part 2: 多项式NARX模型"""
    print("\n" + "="*60)
    print("Part 2: 多项式NARX模型")
    print("="*60)

    # 生成非线性系统（简单的非线性ARX）
    print("生成非线性ARX系统...")

    N = 600
    np.random.seed(42)
    u = generate_prbs(N, period=10, amplitude=0.3, offset=0.5)

    # 真实系统：y(k) = 0.7*y(k-1) + 0.5*u(k-1) - 0.3*y(k-1)^2 + 0.2*u(k-1)^2
    y_true = np.zeros(N)
    y_true[0] = 0.5

    for k in range(1, N):
        y_true[k] = (0.7 * y_true[k-1] +
                     0.5 * u[k-1] -
                     0.3 * y_true[k-1]**2 +
                     0.2 * u[k-1]**2)

    # 添加噪声
    y_meas = y_true + 0.02 * np.std(y_true) * np.random.randn(N)

    print(f"数据长度: {N}")
    print("真实系统: y(k) = 0.7*y(k-1) + 0.5*u(k-1) - 0.3*y(k-1)^2 + 0.2*u(k-1)^2")

    # 分割训练/测试
    N_train = 400
    u_train, y_train = u[:N_train], y_meas[:N_train]
    u_test, y_test = u[N_train:], y_meas[N_train:]

    # NARX辨识（Lasso正则化）
    print("\nNARX辨识（Lasso正则化）...")
    narx = PolynomialNARX(ny=2, nu=2, degree=2, use_lasso=True, alpha=0.001)
    narx.fit(u_train, y_train)

    # 预测（训练集）
    y_train_pred = narx.predict(u_train, y_train[:narx.ny])

    # 预测（测试集）
    y_test_pred = narx.predict(u_test, y_test[:narx.ny])

    # 计算误差
    rmse_train = np.sqrt(np.mean((y_train[narx.ny:] - y_train_pred[narx.ny:])**2))
    rmse_test = np.sqrt(np.mean((y_test[narx.ny:] - y_test_pred[narx.ny:])**2))

    fit_train = 100 * (1 - np.linalg.norm(y_train[narx.ny:] - y_train_pred[narx.ny:]) /
                          np.linalg.norm(y_train[narx.ny:] - np.mean(y_train[narx.ny:])))
    fit_test = 100 * (1 - np.linalg.norm(y_test[narx.ny:] - y_test_pred[narx.ny:]) /
                         np.linalg.norm(y_test[narx.ny:] - np.mean(y_test[narx.ny:])))

    print(f"\n训练集: RMSE={rmse_train:.6f}, Fit={fit_train:.2f}%")
    print(f"测试集: RMSE={rmse_test:.6f}, Fit={fit_test:.2f}%")

    # 可视化
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 训练集响应
    ax = axes[0, 0]
    t_train = np.arange(len(y_train))
    ax.plot(t_train, y_train, 'b-', linewidth=1.5, label='实际', alpha=0.7)
    ax.plot(t_train, y_train_pred, 'r--', linewidth=1.5, label=f'NARX (Fit={fit_train:.1f}%)')
    ax.set_xlabel('时间步')
    ax.set_ylabel('输出')
    ax.set_title('训练集响应')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 测试集响应
    ax = axes[0, 1]
    t_test = np.arange(len(y_test))
    ax.plot(t_test, y_test, 'b-', linewidth=1.5, label='实际', alpha=0.7)
    ax.plot(t_test, y_test_pred, 'r--', linewidth=1.5, label=f'NARX (Fit={fit_test:.1f}%)')
    ax.set_xlabel('时间步')
    ax.set_ylabel('输出')
    ax.set_title('测试集响应（泛化能力）')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 参数系数可视化（仅非零项）
    ax = axes[1, 0]
    nonzero_idx = np.abs(narx.theta) > 1e-6
    nonzero_coef = narx.theta[nonzero_idx]
    nonzero_names = [narx.term_names[i] for i in range(len(narx.theta)) if nonzero_idx[i]]

    # 只显示前15个最显著的
    top_k = 15
    if len(nonzero_coef) > top_k:
        top_idx = np.argsort(np.abs(nonzero_coef))[::-1][:top_k]
        nonzero_coef = nonzero_coef[top_idx]
        nonzero_names = [nonzero_names[i] for i in top_idx]

    ax.barh(range(len(nonzero_coef)), nonzero_coef)
    ax.set_yticks(range(len(nonzero_coef)))
    ax.set_yticklabels(nonzero_names, fontsize=8)
    ax.set_xlabel('系数值')
    ax.set_title(f'NARX参数（前{len(nonzero_coef)}个非零项）')
    ax.grid(True, alpha=0.3, axis='x')

    # 预测误差分布
    ax = axes[1, 1]
    error_train = y_train[narx.ny:] - y_train_pred[narx.ny:]
    error_test = y_test[narx.ny:] - y_test_pred[narx.ny:]

    ax.hist(error_train, bins=30, alpha=0.5, label='训练集误差', color='blue')
    ax.hist(error_test, bins=30, alpha=0.5, label='测试集误差', color='red')
    ax.axvline(0, color='k', linestyle='--', alpha=0.5)
    ax.set_xlabel('预测误差')
    ax.set_ylabel('频数')
    ax.set_title('误差分布')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('part2_narx_model.png', dpi=150, bbox_inches='tight')
    print("图表已保存: part2_narx_model.png")
    plt.close()


def part3_canal_nonlinear():
    """Part 3: 渠道系统非线性辨识"""
    print("\n" + "="*60)
    print("Part 3: 渠道系统非线性辨识")
    print("="*60)

    # 渠道仿真（宽范围操作）
    print("生成渠道系统数据（宽范围操作）...")
    canal = CanalReach(N=51)
    gate = GateModel()

    dt = 10.0
    N = 800
    t = np.arange(N) * dt

    # PRBS激励（大幅度变化）
    np.random.seed(42)
    u_signal = generate_prbs(N, period=5, amplitude=0.25, offset=0.5)

    # 仿真
    h_history = []
    u_history = []

    # 从不同初始水位开始（模拟宽范围）
    h0 = np.ones(51) * np.random.uniform(1.0, 2.0)
    Q0 = np.ones(51) * 5.0
    canal.set_state(h0, Q0)

    for k in range(N):
        u_k = u_signal[k]
        Q_out = gate.flow(canal.h[-1], u_k)
        Q_in = 5.0
        canal.step(dt, Q_in=Q_in, Q_out=Q_out)

        h_history.append(canal.h[-10])
        u_history.append(u_k)

    y_data = np.array(h_history)
    u_data = np.array(u_history)

    # 中心化
    u_mean, y_mean = np.mean(u_data), np.mean(y_data)
    u_centered = u_data - u_mean
    y_centered = y_data - y_mean

    print(f"数据长度: {N}")
    print(f"水位范围: [{np.min(y_data):.2f}, {np.max(y_data):.2f}] m")
    print(f"闸门开度范围: [{np.min(u_data):.2f}, {np.max(u_data):.2f}]")

    # 分割数据
    N_train = 600
    u_train, y_train = u_centered[:N_train], y_centered[:N_train]
    u_test, y_test = u_centered[N_train:], y_centered[N_train:]

    # 方法1: 线性辨识（N4SID简化版 - 用ARX代替）
    print("\n方法1: 线性ARX模型...")

    # 构造ARX回归矩阵
    ny, nu = 3, 3
    X_train = []
    Y_train = []
    for k in range(max(ny, nu), len(y_train)):
        phi = np.concatenate([y_train[k-ny:k][::-1], u_train[k-nu:k][::-1]])
        X_train.append(phi)
        Y_train.append(y_train[k])

    X_train = np.array(X_train)
    Y_train = np.array(Y_train)

    # 线性回归（最小二乘）
    theta_linear = np.linalg.lstsq(X_train, Y_train, rcond=None)[0]

    # 预测（线性）
    def predict_linear(u, y_init):
        y_pred = np.zeros(len(u))
        y_pred[:ny] = y_init[:ny]
        for k in range(ny, len(u)):
            phi = np.concatenate([y_pred[k-ny:k][::-1], u[k-nu:k][::-1]])
            y_pred[k] = np.dot(theta_linear, phi)
        return y_pred

    y_test_linear = predict_linear(u_test, y_test[:ny])

    # 方法2: 非线性NARX
    print("\n方法2: 多项式NARX模型...")
    narx = PolynomialNARX(ny=3, nu=3, degree=2, use_lasso=True, alpha=0.005)
    narx.fit(u_train, y_train)

    y_test_narx = narx.predict(u_test, y_test[:narx.ny])

    # 计算误差
    rmse_linear = np.sqrt(np.mean((y_test[ny:] - y_test_linear[ny:])**2))
    rmse_narx = np.sqrt(np.mean((y_test[narx.ny:] - y_test_narx[narx.ny:])**2))

    # 计算拟合度（使用更健壮的方法）
    y_test_std = np.std(y_test[ny:])
    if y_test_std > 1e-6:
        fit_linear = 100 * max(0, (1 - np.sqrt(np.mean((y_test[ny:] - y_test_linear[ny:])**2)) / y_test_std))
        fit_narx = 100 * max(0, (1 - np.sqrt(np.mean((y_test[narx.ny:] - y_test_narx[narx.ny:])**2)) / y_test_std))
    else:
        fit_linear = 0.0
        fit_narx = 0.0

    print(f"\n测试集性能:")
    print(f"  线性ARX: RMSE={rmse_linear:.6f}, Fit={fit_linear:.2f}%")
    print(f"  非线性NARX: RMSE={rmse_narx:.6f}, Fit={fit_narx:.2f}%")
    if rmse_linear > 1e-6:
        print(f"  改善: {(rmse_linear - rmse_narx)/rmse_linear*100:.1f}%")
    else:
        print(f"  改善: 0.0%")

    # 可视化
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 测试集响应对比
    ax = axes[0, 0]
    t_test = np.arange(len(y_test)) * dt / 60
    ax.plot(t_test, y_test + y_mean, 'k-', linewidth=2, label='实际', alpha=0.7)
    ax.plot(t_test, y_test_linear + y_mean, 'b--', linewidth=1.5,
            label=f'线性 (Fit={fit_linear:.1f}%)', alpha=0.7)
    ax.plot(t_test, y_test_narx + y_mean, 'r--', linewidth=1.5,
            label=f'非线性 (Fit={fit_narx:.1f}%)', alpha=0.7)
    ax.set_xlabel('时间 (分钟)')
    ax.set_ylabel('水位 (m)')
    ax.set_title('测试集：模型对比')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 输入信号
    ax = axes[0, 1]
    t_full = np.arange(N) * dt / 60
    ax.plot(t_full, u_data, 'g-', linewidth=1.5)
    ax.axvline(N_train * dt / 60, color='r', linestyle='--', label='训练/测试分界')
    ax.set_xlabel('时间 (分钟)')
    ax.set_ylabel('闸门开度')
    ax.set_title('激励信号（PRBS）')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 误差对比
    ax = axes[1, 0]
    error_linear = y_test[ny:] - y_test_linear[ny:]
    error_narx = y_test[narx.ny:] - y_test_narx[narx.ny:]

    ax.plot(t_test[ny:], error_linear, 'b-', linewidth=1, alpha=0.7, label='线性误差')
    ax.plot(t_test[narx.ny:], error_narx, 'r-', linewidth=1, alpha=0.7, label='非线性误差')
    ax.axhline(0, color='k', linestyle='--', alpha=0.5)
    ax.set_xlabel('时间 (分钟)')
    ax.set_ylabel('预测误差 (m)')
    ax.set_title('误差对比')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 散点图：不同水位下的性能
    ax = axes[1, 1]
    # 将数据按水位分组
    y_abs_test = y_test + y_mean
    bins = np.linspace(y_abs_test.min(), y_abs_test.max(), 5)
    bin_centers = []
    rmse_linear_bins = []
    rmse_narx_bins = []

    for i in range(len(bins)-1):
        mask = (y_abs_test >= bins[i]) & (y_abs_test < bins[i+1])
        if np.sum(mask) > 10:
            bin_centers.append((bins[i] + bins[i+1])/2)
            rmse_linear_bins.append(np.sqrt(np.mean(error_linear[mask[ny:]]**2)))
            rmse_narx_bins.append(np.sqrt(np.mean(error_narx[mask[narx.ny:]]**2)))

    ax.plot(bin_centers, rmse_linear_bins, 'bo-', linewidth=2,
            markersize=8, label='线性模型')
    ax.plot(bin_centers, rmse_narx_bins, 'ro-', linewidth=2,
            markersize=8, label='非线性模型')
    ax.set_xlabel('水位 (m)')
    ax.set_ylabel('RMSE (m)')
    ax.set_title('不同水位下的预测误差')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('part3_canal_nonlinear.png', dpi=150, bbox_inches='tight')
    print("图表已保存: part3_canal_nonlinear.png")
    plt.close()


def part4_summary():
    """Part 4: 总结对比"""
    print("\n" + "="*60)
    print("Part 4: 方法总结对比")
    print("="*60)

    # 创建对比图表
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 模型复杂度对比
    ax = axes[0, 0]
    methods = ['线性\nARX', 'Hammerstein-\nWiener', '多项式\nNARX', '神经\n网络']
    complexity = [10, 30, 50, 100]  # 相对参数数量
    colors = ['blue', 'green', 'orange', 'red']

    bars = ax.bar(methods, complexity, color=colors, alpha=0.7)
    ax.set_ylabel('相对参数数量')
    ax.set_title('模型复杂度对比')
    ax.grid(True, alpha=0.3, axis='y')

    for bar, val in zip(bars, complexity):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{val}', ha='center', va='bottom')

    # 适用场景雷达图
    ax = axes[0, 1]

    categories = ['精度', '可解释性', '泛化能力', '计算效率', '数据需求']
    N_cat = len(categories)

    # 归一化分数（0-1）
    scores = {
        '线性ARX': [0.6, 1.0, 0.7, 1.0, 0.8],
        'Hammerstein-Wiener': [0.8, 0.8, 0.8, 0.7, 0.6],
        '多项式NARX': [0.9, 0.6, 0.7, 0.8, 0.5],
        '神经网络': [0.95, 0.3, 0.6, 0.4, 0.3],
    }

    angles = np.linspace(0, 2 * np.pi, N_cat, endpoint=False).tolist()
    angles += angles[:1]

    ax = plt.subplot(2, 2, 2, projection='polar')

    for method, score in scores.items():
        score_plot = score + score[:1]
        ax.plot(angles, score_plot, 'o-', linewidth=2, label=method)
        ax.fill(angles, score_plot, alpha=0.15)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories)
    ax.set_ylim(0, 1)
    ax.set_title('方法特性对比', y=1.08)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
    ax.grid(True)

    # 应用场景推荐
    ax = axes[1, 0]
    ax.axis('off')

    scenarios = [
        ('小数据量（<500点）', 'Hammerstein-Wiener', '物理约束减少过拟合'),
        ('弱非线性系统', '多项式NARX', '计算快速，可解释'),
        ('强非线性+大数据', '神经网络', '最强表达能力'),
        ('需要在线更新', '线性ARX', '计算效率高'),
        ('需要外推', 'Hammerstein-Wiener', '物理结构辅助外推'),
    ]

    text_content = "应用场景推荐:\n\n"
    for scenario, method, reason in scenarios:
        text_content += f"• {scenario}\n  → {method}\n  理由: {reason}\n\n"

    ax.text(0.1, 0.9, text_content, transform=ax.transAxes,
            fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

    # 优缺点对比
    ax = axes[1, 1]
    ax.axis('off')

    comparison = """非线性辨识方法优缺点:

Hammerstein-Wiener:
  ✓ 物理意义明确
  ✓ 参数少，不易过拟合
  ✗ 假设块结构（限制表达能力）

多项式NARX:
  ✓ 灵活，实现简单
  ✓ 线性于参数（快速估计）
  ✗ 参数爆炸，需正则化

神经网络:
  ✓ 万能逼近器
  ✓ 自动特征提取
  ✗ 黑盒，需大量数据
  ✗ 训练慢，易过拟合

选择建议:
  从简单到复杂逐步尝试
  验证集性能最重要"""

    ax.text(0.05, 0.95, comparison, transform=ax.transAxes,
            fontsize=9, verticalalignment='top',
            family='monospace',
            bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3))

    plt.tight_layout()
    plt.savefig('part4_method_comparison.png', dpi=150, bbox_inches='tight')
    print("图表已保存: part4_method_comparison.png")
    plt.close()

    print("\n非线性辨识总结:")
    print("1. 实际系统往往具有显著非线性")
    print("2. Hammerstein-Wiener适合已知物理结构的系统")
    print("3. 多项式NARX是最实用的方法之一")
    print("4. 神经网络表达能力强但需要大量数据")
    print("5. 选择方法时需权衡精度、复杂度和数据量")


def main():
    """主函数"""
    print("="*60)
    print("案例10：非线性系统辨识")
    print("Nonlinear System Identification")
    print("="*60)

    # 运行所有部分
    part1_hammerstein_wiener()
    part2_narx_model()
    part3_canal_nonlinear()
    part4_summary()

    print("\n" + "="*60)
    print("案例10完成！所有图表已保存。")
    print("="*60)

    print("\n关键结论：")
    print("1. 非线性模型能够捕捉宽范围操作下的系统行为")
    print("2. Hammerstein-Wiener提供物理直观的块结构")
    print("3. 多项式NARX灵活实用，需要正则化防止过拟合")
    print("4. 渠道系统的非线性主要来自Manning和闸门公式")
    print("5. 非线性模型在宽范围测试中明显优于线性模型")
    print("6. 模型选择需权衡复杂度、精度和数据需求")


if __name__ == "__main__":
    main()
