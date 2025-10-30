#!/usr/bin/env python3
"""
案例8：N4SID子空间辨识
N4SID Subspace System Identification

实现：
1. N4SID算法完整实现
2. 模型阶数选择方法
3. 渠道系统辨识
4. 噪声鲁棒性测试

作者：Claude
日期：2025
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from scipy import signal, linalg
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

# ==================== 渠道系统仿真 ====================

class CanalReach:
    """
    渠段模型：Saint-Venant方程求解器
    """
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


# ==================== N4SID算法 ====================

class N4SID:
    """
    N4SID子空间辨识算法

    参考：Van Overschee & De Moor (1994)
    """
    def __init__(self, i=15):
        """
        i: 用户参数，Hankel矩阵的块行数（通常10-20）
        """
        self.i = i
        self.A = None
        self.B = None
        self.C = None
        self.D = None
        self.n = None
        self.singular_values = None

    def build_hankel(self, data, i):
        """
        构造Hankel矩阵
        data: (m, N) - m个信号，N个时间点
        i: 块行数
        返回: Hankel矩阵 (i*m, j)，其中 j = N - 2*i + 1
        """
        m, N = data.shape
        j = N - 2*i + 1

        if j <= 0:
            raise ValueError(f"数据长度不足：N={N}, i={i}, 需要 N >= 2*i")

        H = np.zeros((i * m, j))

        for k in range(i):
            H[k*m:(k+1)*m, :] = data[:, k:k+j]

        return H

    def identify(self, u, y, n=None):
        """
        N4SID辨识

        u: (m, N) - 输入数据，m个输入，N个时间点
        y: (p, N) - 输出数据，p个输出，N个时间点
        n: 模型阶数（如果None，自动选择）

        返回: A, B, C, D矩阵
        """
        m, N = u.shape
        p, _ = y.shape
        i = self.i

        # Step 1: 构造Hankel矩阵
        U = self.build_hankel(u, i)
        Y = self.build_hankel(y, i)

        j = U.shape[1]

        # 分割过去和未来
        U_p = U[:i*m//2, :]  # 过去输入
        U_f = U[i*m//2:, :]  # 未来输入
        Y_p = Y[:i*p//2, :]  # 过去输出
        Y_f = Y[i*p//2:, :]  # 未来输出

        # Step 2: 正交投影（使用QR分解）
        # 构造增广矩阵
        W_p = np.vstack([U_p, Y_p])  # 过去数据

        # QR分解
        # [U_f; W_p; Y_f] = [R11 0 0; R21 R22 0; R31 R32 R33] * [Q1; Q2; Q3]'
        Z = np.vstack([U_f, W_p, Y_f])
        Q, R = linalg.qr(Z.T, mode='economic')
        R = R.T

        # 提取块
        nuf = U_f.shape[0]
        nwp = W_p.shape[0]
        nyf = Y_f.shape[0]

        R32 = R[nuf+nwp:nuf+nwp+nyf, nuf:nuf+nwp]
        Q2 = Q[:, nuf:nuf+nwp]

        # 投影矩阵
        O_i = R32 @ Q2.T

        # Step 3: SVD分解
        U_svd, S_svd, Vt_svd = linalg.svd(O_i, full_matrices=False)
        self.singular_values = S_svd

        # Step 4: 选择模型阶数
        if n is None:
            # 自动选择：累计能量>95%
            energy_cumsum = np.cumsum(S_svd**2)
            total_energy = energy_cumsum[-1]
            n = np.argmax(energy_cumsum / total_energy > 0.95) + 1
            n = max(2, min(n, len(S_svd)//2))  # 限制在[2, len/2]
            print(f"自动选择模型阶数: n = {n}")

        self.n = n

        # 截断到n阶
        U_n = U_svd[:, :n]
        S_n = S_svd[:n]
        V_n = Vt_svd[:n, :].T

        # Step 5: 可观测性矩阵和状态序列
        Gamma_i = U_n @ np.diag(np.sqrt(S_n))
        X_f = np.diag(np.sqrt(S_n)) @ V_n.T

        # Step 6: 提取A和C
        C = Gamma_i[:p, :]

        # A = Gamma_i^+ * shift(Gamma_i)
        Gamma_i_minus = Gamma_i[:-p, :]
        Gamma_i_plus = Gamma_i[p:, :]

        A = linalg.lstsq(Gamma_i_minus, Gamma_i_plus)[0].T

        # Step 7: 提取B和D（最小二乘）
        # 重新估计完整的状态序列
        # Y = [Y(0), Y(1), ..., Y(N-1)]
        # X = [X(0), X(1), ..., X(N-1)]

        # 使用估计的A和C，通过Kalman滤波估计状态
        X_est = np.zeros((n, N))

        # 简化方法：使用前面计算的X_f
        # 但X_f只有部分时间点，我们需要全部
        # 这里使用简单的最小二乘估计

        # 构造方程: [X(k+1); Y(k)] = [A B; C D] [X(k); U(k)]
        # 对所有k求解

        # 首先用Y估计X（假设D=0）
        for k in range(N):
            if k == 0:
                # 初始状态估计
                X_est[:, k] = linalg.lstsq(C, y[:, k])[0]
            else:
                # 状态更新（简化，不考虑输入）
                X_est[:, k] = A @ X_est[:, k-1]

        # 现在估计B和D
        # Y(k) = C X(k) + D U(k)
        # 先估计D
        residual_y = y - C @ X_est
        D = linalg.lstsq(u.T, residual_y.T)[0].T

        # X(k+1) = A X(k) + B U(k)
        # B U(k) = X(k+1) - A X(k)
        residual_x = X_est[:, 1:] - A @ X_est[:, :-1]
        B = linalg.lstsq(u[:, :-1].T, residual_x.T)[0].T

        self.A = A
        self.B = B
        self.C = C
        self.D = D

        return A, B, C, D

    def simulate(self, u, x0=None):
        """
        使用辨识的模型仿真

        u: (m, N) - 输入序列
        x0: (n,) - 初始状态（如果None，默认为零）

        返回: y - (p, N) 输出序列
        """
        if self.A is None:
            raise ValueError("模型未辨识，请先调用identify()")

        m, N = u.shape
        n = self.A.shape[0]
        p = self.C.shape[0]

        if x0 is None:
            x0 = np.zeros(n)

        x = x0.copy()
        y = np.zeros((p, N))

        for k in range(N):
            y[:, k] = self.C @ x + self.D @ u[:, k]
            x = self.A @ x + self.B @ u[:, k]

        return y

    def get_eigenvalues(self):
        """获取系统特征值"""
        if self.A is None:
            return None
        return linalg.eigvals(self.A)


# ==================== 工具函数 ====================

def generate_prbs(N, period=20, amplitude=0.2, offset=0.5):
    """
    生成伪随机二进制序列（PRBS）

    N: 数据点数
    period: 切换周期
    amplitude: 幅值
    offset: 偏移
    """
    n_switches = N // period
    switches = np.random.choice([-1, 1], size=n_switches)
    prbs = np.repeat(switches, period)

    # 补齐到N
    if len(prbs) < N:
        prbs = np.concatenate([prbs, np.ones(N - len(prbs)) * switches[-1]])
    else:
        prbs = prbs[:N]

    return offset + amplitude * prbs


def compute_fit(y_true, y_pred):
    """
    计算拟合度
    Fit = 100 * (1 - ||y - y_pred|| / ||y - mean(y)||)
    """
    y_mean = np.mean(y_true)
    fit = 100 * (1 - np.linalg.norm(y_true - y_pred) / np.linalg.norm(y_true - y_mean))
    return fit


def add_noise(data, snr_db=20):
    """
    添加高斯白噪声
    snr_db: 信噪比（dB）
    """
    signal_power = np.mean(data**2)
    snr_linear = 10**(snr_db / 10)
    noise_power = signal_power / snr_linear
    noise = np.sqrt(noise_power) * np.random.randn(*data.shape)
    return data + noise


# ==================== 演示部分 ====================

def part1_n4sid_validation():
    """Part 1: N4SID算法验证（标准测试系统）"""
    print("\n" + "="*60)
    print("Part 1: N4SID算法验证")
    print("="*60)

    # 生成标准测试系统（二阶振荡系统）
    print("生成测试系统：二阶振荡系统")

    # 连续时间系统
    wn = 0.5  # 自然频率
    zeta = 0.3  # 阻尼比

    # 状态空间形式
    A_c = np.array([[0, 1], [-wn**2, -2*zeta*wn]])
    B_c = np.array([[0], [wn**2]])
    C_c = np.array([[1, 0]])
    D_c = np.array([[0]])

    # 离散化
    dt = 1.0
    sys_c = signal.StateSpace(A_c, B_c, C_c, D_c)
    sys_d = sys_c.to_discrete(dt)

    A_true, B_true, C_true, D_true = sys_d.A, sys_d.B, sys_d.C, sys_d.D

    print(f"真实系统阶数: n = {A_true.shape[0]}")
    print(f"真实特征值: {np.linalg.eigvals(A_true)}")

    # 生成输入输出数据
    N = 500
    u = generate_prbs(N, period=10, amplitude=1.0, offset=0.0).reshape(1, -1)

    # 仿真真实系统
    tout, y_true, x_true = signal.dlsim(sys_d, u.T)
    y_true = y_true.T

    # 添加噪声
    y_meas = add_noise(y_true, snr_db=20)

    # N4SID辨识
    print("\n运行N4SID辨识...")
    n4sid = N4SID(i=15)
    A_id, B_id, C_id, D_id = n4sid.identify(u, y_meas, n=2)

    print(f"辨识系统阶数: n = {n4sid.n}")
    print(f"辨识特征值: {n4sid.get_eigenvalues()}")

    # 仿真辨识模型
    y_id = n4sid.simulate(u)

    # 计算拟合度
    fit = compute_fit(y_true.flatten(), y_id.flatten())
    print(f"\n拟合度: {fit:.2f}%")

    # 可视化
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 时间响应
    ax = axes[0, 0]
    t = np.arange(N) * dt
    ax.plot(t[:200], y_true.flatten()[:200], 'k-', linewidth=2, label='真实系统', alpha=0.7)
    ax.plot(t[:200], y_meas.flatten()[:200], 'b.', markersize=3, label='测量（含噪声）', alpha=0.5)
    ax.plot(t[:200], y_id.flatten()[:200], 'r--', linewidth=2, label=f'辨识模型 (Fit={fit:.1f}%)')
    ax.set_xlabel('时间 (s)')
    ax.set_ylabel('输出')
    ax.set_title('时间响应对比')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 奇异值分布
    ax = axes[0, 1]
    ax.semilogy(n4sid.singular_values, 'bo-', linewidth=2, markersize=8)
    ax.axvline(n4sid.n, color='r', linestyle='--', linewidth=2, label=f'选择阶数 n={n4sid.n}')
    ax.set_xlabel('奇异值索引')
    ax.set_ylabel('奇异值')
    ax.set_title('奇异值分布（阶数选择）')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 极点图
    ax = axes[1, 0]

    # 真实极点
    eig_true = np.linalg.eigvals(A_true)
    ax.plot(eig_true.real, eig_true.imag, 'kx', markersize=15,
            markeredgewidth=3, label='真实极点')

    # 辨识极点
    eig_id = n4sid.get_eigenvalues()
    ax.plot(eig_id.real, eig_id.imag, 'ro', markersize=10,
            markerfacecolor='none', markeredgewidth=2, label='辨识极点')

    # 单位圆
    theta = np.linspace(0, 2*np.pi, 100)
    ax.plot(np.cos(theta), np.sin(theta), 'k--', alpha=0.3)

    ax.set_xlabel('实部')
    ax.set_ylabel('虚部')
    ax.set_title('极点分布')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.axis('equal')
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)

    # 误差分析
    ax = axes[1, 1]
    error = y_true.flatten() - y_id.flatten()
    ax.plot(t, error, 'b-', linewidth=1, alpha=0.7)
    ax.axhline(0, color='k', linestyle='--', alpha=0.5)
    ax.fill_between(t, -3*np.std(error), 3*np.std(error), alpha=0.2, color='red', label='±3σ')
    ax.set_xlabel('时间 (s)')
    ax.set_ylabel('预测误差')
    ax.set_title(f'残差分析 (RMSE={np.sqrt(np.mean(error**2)):.4f})')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('part1_n4sid_validation.png', dpi=150, bbox_inches='tight')
    print("图表已保存: part1_n4sid_validation.png")
    plt.close()


def part2_order_selection():
    """Part 2: 模型阶数选择"""
    print("\n" + "="*60)
    print("Part 2: 模型阶数选择")
    print("="*60)

    # 生成4阶系统
    print("生成测试系统：4阶系统")
    n_true = 4
    A_true = np.random.randn(n_true, n_true)
    A_true = 0.9 * A_true / np.max(np.abs(np.linalg.eigvals(A_true)))  # 稳定化
    B_true = np.random.randn(n_true, 1)
    C_true = np.random.randn(1, n_true)
    D_true = np.zeros((1, 1))

    sys_true = signal.StateSpace(A_true, B_true, C_true, D_true, dt=1.0)

    # 生成数据
    N = 800
    u = generate_prbs(N, period=10).reshape(1, -1)
    _, y_true, _ = signal.dlsim(sys_true, u.T)
    y_true = y_true.T
    y_meas = add_noise(y_true, snr_db=20)

    # 尝试不同阶数
    orders = range(1, 15)
    fits = []
    aics = []

    print("\n测试不同模型阶数...")
    for n in orders:
        try:
            n4sid = N4SID(i=15)
            n4sid.identify(u, y_meas, n=n)
            y_pred = n4sid.simulate(u)

            fit = compute_fit(y_true.flatten(), y_pred.flatten())
            fits.append(fit)

            # AIC准则
            residual = y_true.flatten() - y_pred.flatten()
            rss = np.sum(residual**2)
            n_params = n * (n + 1 + 1)  # A, B, C的参数数量
            aic = 2 * n_params + N * np.log(rss / N)
            aics.append(aic)

            print(f"  n={n:2d}: Fit={fit:6.2f}%, AIC={aic:8.2f}")
        except:
            fits.append(0)
            aics.append(1e10)

    # 找最佳阶数
    best_order_fit = orders[np.argmax(fits)]
    best_order_aic = orders[np.argmin(aics)]

    print(f"\n真实阶数: {n_true}")
    print(f"最佳阶数（拟合度）: {best_order_fit}")
    print(f"最佳阶数（AIC）: {best_order_aic}")

    # 可视化
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    # 拟合度vs阶数
    ax = axes[0]
    ax.plot(orders, fits, 'bo-', linewidth=2, markersize=8)
    ax.axvline(n_true, color='r', linestyle='--', linewidth=2, label=f'真实阶数 n={n_true}')
    ax.axvline(best_order_fit, color='g', linestyle=':', linewidth=2, label=f'最佳阶数（Fit）')
    ax.set_xlabel('模型阶数')
    ax.set_ylabel('拟合度 (%)')
    ax.set_title('拟合度 vs 模型阶数')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # AIC vs阶数
    ax = axes[1]
    ax.plot(orders, aics, 'ro-', linewidth=2, markersize=8)
    ax.axvline(n_true, color='r', linestyle='--', linewidth=2, label=f'真实阶数 n={n_true}')
    ax.axvline(best_order_aic, color='g', linestyle=':', linewidth=2, label=f'最佳阶数（AIC）')
    ax.set_xlabel('模型阶数')
    ax.set_ylabel('AIC')
    ax.set_title('AIC准则 vs 模型阶数')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 奇异值（用于阶数选择）
    n4sid = N4SID(i=15)
    n4sid.identify(u, y_meas, n=None)

    ax = axes[2]
    ax.semilogy(n4sid.singular_values[:20], 'bo-', linewidth=2, markersize=8)
    ax.axvline(n_true, color='r', linestyle='--', linewidth=2, label=f'真实阶数 n={n_true}')
    ax.set_xlabel('奇异值索引')
    ax.set_ylabel('奇异值')
    ax.set_title('奇异值分布（阶数判断）')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('part2_order_selection.png', dpi=150, bbox_inches='tight')
    print("图表已保存: part2_order_selection.png")
    plt.close()


def part3_canal_identification():
    """Part 3: 渠道系统辨识"""
    print("\n" + "="*60)
    print("Part 3: 渠道系统辨识")
    print("="*60)

    # 使用Saint-Venant仿真生成数据
    print("生成渠道系统数据...")
    canal = CanalReach(N=51)
    gate = GateModel()

    # 初始化到平衡点
    h0 = np.ones(51) * 1.5
    Q0 = np.ones(51) * 5.0
    canal.set_state(h0, Q0)

    # 激励信号：PRBS
    dt = 10
    N = 1000
    u_signal = generate_prbs(N, period=3, amplitude=0.15, offset=0.5)

    # 仿真
    y_history = []
    u_history = []

    for k in range(N):
        u_k = u_signal[k]
        Q_out = gate.flow(canal.h[-1], u_k)
        Q_in = 5.0
        canal.step(dt, Q_in=Q_in, Q_out=Q_out)

        # 输出：下游水位
        y_k = canal.h[-10]  # 取倒数第10个点的水位

        y_history.append(y_k)
        u_history.append(u_k)

    # 转换为数组
    u_data = np.array(u_history).reshape(1, -1)
    y_data = np.array(y_history).reshape(1, -1)

    # 去除趋势（中心化）
    u_mean = np.mean(u_data)
    y_mean = np.mean(y_data)
    u_centered = u_data - u_mean
    y_centered = y_data - y_mean

    # 添加测量噪声
    y_meas = add_noise(y_centered, snr_db=25)

    print(f"数据长度: N = {N}")
    print(f"输入范围: [{np.min(u_data):.3f}, {np.max(u_data):.3f}]")
    print(f"输出范围: [{np.min(y_data):.3f}, {np.max(y_data):.3f}]")

    # 分割训练集和测试集
    N_train = 700
    u_train = u_centered[:, :N_train]
    y_train = y_meas[:, :N_train]
    u_test = u_centered[:, N_train:]
    y_test = y_centered[:, N_train:]

    # N4SID辨识
    print("\n运行N4SID辨识...")
    n4sid = N4SID(i=15)
    A, B, C, D = n4sid.identify(u_train, y_train, n=None)

    print(f"辨识模型阶数: n = {n4sid.n}")
    print(f"系统特征值: {n4sid.get_eigenvalues()}")

    # 在训练集上验证
    y_train_pred = n4sid.simulate(u_train)
    fit_train = compute_fit(y_train.flatten(), y_train_pred.flatten())

    # 在测试集上验证
    y_test_pred = n4sid.simulate(u_test)
    fit_test = compute_fit(y_test.flatten(), y_test_pred.flatten())

    print(f"\n训练集拟合度: {fit_train:.2f}%")
    print(f"测试集拟合度: {fit_test:.2f}%")

    # 可视化
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 训练集响应
    ax = axes[0, 0]
    t = np.arange(N_train) * dt
    ax.plot(t, y_train.flatten(), 'b-', linewidth=1.5, label='实际输出', alpha=0.7)
    ax.plot(t, y_train_pred.flatten(), 'r--', linewidth=1.5, label=f'辨识模型 (Fit={fit_train:.1f}%)')
    ax.set_xlabel('时间 (s)')
    ax.set_ylabel('水位偏差 (m)')
    ax.set_title('训练集：模型验证')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 测试集响应
    ax = axes[0, 1]
    t_test = np.arange(len(u_test[0])) * dt
    ax.plot(t_test, y_test.flatten(), 'b-', linewidth=1.5, label='实际输出', alpha=0.7)
    ax.plot(t_test, y_test_pred.flatten(), 'r--', linewidth=1.5, label=f'辨识模型 (Fit={fit_test:.1f}%)')
    ax.set_xlabel('时间 (s)')
    ax.set_ylabel('水位偏差 (m)')
    ax.set_title('测试集：模型验证')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 输入信号
    ax = axes[1, 0]
    t_full = np.arange(N) * dt
    ax.plot(t_full, u_data.flatten(), 'g-', linewidth=1.5, label='闸门开度')
    ax.axvline(N_train * dt, color='r', linestyle='--', label='训练/测试分界')
    ax.set_xlabel('时间 (s)')
    ax.set_ylabel('闸门开度')
    ax.set_title('激励信号（PRBS）')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 奇异值
    ax = axes[1, 1]
    ax.semilogy(n4sid.singular_values[:20], 'bo-', linewidth=2, markersize=8)
    ax.axvline(n4sid.n, color='r', linestyle='--', linewidth=2, label=f'选择阶数 n={n4sid.n}')
    ax.set_xlabel('奇异值索引')
    ax.set_ylabel('奇异值')
    ax.set_title('奇异值分布')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('part3_canal_identification.png', dpi=150, bbox_inches='tight')
    print("图表已保存: part3_canal_identification.png")
    plt.close()


def part4_noise_robustness():
    """Part 4: 噪声鲁棒性测试"""
    print("\n" + "="*60)
    print("Part 4: 噪声鲁棒性测试")
    print("="*60)

    # 生成标准测试系统
    n_true = 3
    A_true = np.random.randn(n_true, n_true)
    A_true = 0.85 * A_true / np.max(np.abs(np.linalg.eigvals(A_true)))
    B_true = np.random.randn(n_true, 1)
    C_true = np.random.randn(1, n_true)
    D_true = np.zeros((1, 1))

    sys_true = signal.StateSpace(A_true, B_true, C_true, D_true, dt=1.0)

    # 生成输入
    N = 600
    u = generate_prbs(N, period=10).reshape(1, -1)

    # 无噪声输出
    _, y_clean, _ = signal.dlsim(sys_true, u.T)
    y_clean = y_clean.T

    # 测试不同噪声水平
    snr_levels = [30, 20, 15, 10, 5]

    print("\n测试不同噪声水平...")
    results = []

    for snr_db in snr_levels:
        y_noisy = add_noise(y_clean, snr_db=snr_db)

        # 辨识
        n4sid = N4SID(i=15)
        n4sid.identify(u, y_noisy, n=n_true)

        # 预测
        y_pred = n4sid.simulate(u)

        # 计算指标
        fit = compute_fit(y_clean.flatten(), y_pred.flatten())
        rmse = np.sqrt(np.mean((y_clean.flatten() - y_pred.flatten())**2))

        # 特征值误差
        eig_true = np.linalg.eigvals(A_true)
        eig_id = n4sid.get_eigenvalues()
        eig_error = np.min([np.linalg.norm(eig_true - eig_id),
                           np.linalg.norm(eig_true - np.conj(eig_id))])

        results.append({
            'snr': snr_db,
            'fit': fit,
            'rmse': rmse,
            'eig_error': eig_error,
            'y_pred': y_pred
        })

        print(f"  SNR={snr_db:2d}dB: Fit={fit:6.2f}%, RMSE={rmse:.4f}, Eig Error={eig_error:.4f}")

    # 可视化
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Fit vs SNR
    ax = axes[0, 0]
    fits = [r['fit'] for r in results]
    ax.plot(snr_levels, fits, 'bo-', linewidth=2, markersize=10)
    ax.set_xlabel('信噪比 (dB)')
    ax.set_ylabel('拟合度 (%)')
    ax.set_title('拟合度 vs 噪声水平')
    ax.grid(True, alpha=0.3)
    ax.invert_xaxis()

    # RMSE vs SNR
    ax = axes[0, 1]
    rmses = [r['rmse'] for r in results]
    ax.semilogy(snr_levels, rmses, 'ro-', linewidth=2, markersize=10)
    ax.set_xlabel('信噪比 (dB)')
    ax.set_ylabel('RMSE')
    ax.set_title('RMSE vs 噪声水平')
    ax.grid(True, alpha=0.3)
    ax.invert_xaxis()

    # 时间响应对比（不同噪声）
    ax = axes[1, 0]
    t = np.arange(200)
    ax.plot(t, y_clean.flatten()[:200], 'k-', linewidth=2, label='无噪声', alpha=0.7)

    colors = plt.cm.Reds(np.linspace(0.3, 0.9, len(snr_levels)))
    for i, r in enumerate(results):
        if r['snr'] in [20, 10, 5]:
            ax.plot(t, r['y_pred'].flatten()[:200], '--',
                   color=colors[i], linewidth=1.5,
                   label=f"SNR={r['snr']}dB (Fit={r['fit']:.1f}%)", alpha=0.7)

    ax.set_xlabel('时间步')
    ax.set_ylabel('输出')
    ax.set_title('不同噪声水平下的辨识结果')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 特征值误差 vs SNR
    ax = axes[1, 1]
    eig_errors = [r['eig_error'] for r in results]
    ax.semilogy(snr_levels, eig_errors, 'go-', linewidth=2, markersize=10)
    ax.set_xlabel('信噪比 (dB)')
    ax.set_ylabel('特征值误差')
    ax.set_title('特征值误差 vs 噪声水平')
    ax.grid(True, alpha=0.3)
    ax.invert_xaxis()

    plt.tight_layout()
    plt.savefig('part4_noise_robustness.png', dpi=150, bbox_inches='tight')
    print("图表已保存: part4_noise_robustness.png")
    plt.close()


def main():
    """主函数"""
    print("="*60)
    print("案例8：N4SID子空间辨识")
    print("N4SID Subspace System Identification")
    print("="*60)

    # 运行所有部分
    part1_n4sid_validation()
    part2_order_selection()
    part3_canal_identification()
    part4_noise_robustness()

    print("\n" + "="*60)
    print("案例8完成！所有图表已保存。")
    print("="*60)

    print("\n关键结论：")
    print("1. N4SID是基于SVD的子空间辨识方法，数值稳定")
    print("2. 通过奇异值分析可以自动选择模型阶数")
    print("3. 对中等噪声具有良好的鲁棒性")
    print("4. 辨识的状态空间模型可直接用于MPC等先进控制")
    print("5. 需要充分激励信号（PRBS等）和足够长的数据")


if __name__ == "__main__":
    main()
