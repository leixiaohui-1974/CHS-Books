#!/usr/bin/env python3
"""
案例9：频域辨识方法
Frequency Domain Identification

实现：
1. ETFE（经验传递函数估计）
2. Welch谱估计方法
3. 渠道系统频域辨识
4. 参数化模型拟合

作者：Claude
日期：2025
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from scipy import signal, optimize
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

# ==================== 渠道系统仿真 ====================

class CanalReach:
    """渠段模型：Saint-Venant方程求解器"""
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


# ==================== 频域辨识方法 ====================

def etfe(u, y, dt, nfft=None):
    """
    经验传递函数估计（ETFE）

    参数：
        u: 输入信号 (N,)
        y: 输出信号 (N,)
        dt: 采样时间
        nfft: FFT点数

    返回：
        freq: 频率数组
        G: 传递函数估计
    """
    N = len(u)

    if nfft is None:
        nfft = N

    # FFT
    U = np.fft.fft(u, n=nfft)
    Y = np.fft.fft(y, n=nfft)

    # 传递函数估计
    G = Y / (U + 1e-10)

    # 频率轴
    freq = np.fft.fftfreq(nfft, dt)

    # 只取正频率
    positive_freq_idx = freq >= 0
    freq = freq[positive_freq_idx]
    G = G[positive_freq_idx]

    return freq, G


def welch_estimate(u, y, dt, nperseg=256, noverlap=None):
    """
    Welch方法估计频率响应

    参数：
        u: 输入信号
        y: 输出信号
        dt: 采样时间
        nperseg: 每段长度
        noverlap: 重叠点数

    返回：
        freq: 频率数组
        G: 传递函数估计
        coherence: 相干函数
    """
    if noverlap is None:
        noverlap = nperseg // 2

    # 计算交叉功率谱和自功率谱
    freq, Pyu = signal.csd(y, u, fs=1/dt, nperseg=nperseg, noverlap=noverlap)
    _, Puu = signal.welch(u, fs=1/dt, nperseg=nperseg, noverlap=noverlap)
    _, Pyy = signal.welch(y, fs=1/dt, nperseg=nperseg, noverlap=noverlap)

    # 传递函数估计
    G = Pyu / (Puu + 1e-10)

    # 相干函数
    coherence = np.abs(Pyu)**2 / (Puu * Pyy + 1e-10)

    return freq, G, coherence


def generate_chirp(t, f0, f1, method='linear'):
    """
    生成Chirp扫频信号

    参数：
        t: 时间数组
        f0: 起始频率
        f1: 终止频率
        method: 'linear' 或 'logarithmic'

    返回：
        chirp信号
    """
    if method == 'linear':
        return signal.chirp(t, f0, t[-1], f1, method='linear')
    else:
        return signal.chirp(t, f0, t[-1], f1, method='logarithmic')


def bode_plot(freq, G, ax_mag=None, ax_phase=None, label=None, **kwargs):
    """
    绘制Bode图

    参数：
        freq: 频率数组
        G: 复数传递函数
        ax_mag: 幅频图axes
        ax_phase: 相频图axes
        label: 标签
    """
    mag_db = 20 * np.log10(np.abs(G) + 1e-10)
    phase_deg = np.angle(G, deg=True)

    if ax_mag is not None:
        ax_mag.semilogx(freq, mag_db, label=label, **kwargs)
        ax_mag.set_ylabel('幅值 (dB)')
        ax_mag.grid(True, which='both', alpha=0.3)
        if label:
            ax_mag.legend()

    if ax_phase is not None:
        ax_phase.semilogx(freq, phase_deg, label=label, **kwargs)
        ax_phase.set_xlabel('频率 (Hz)')
        ax_phase.set_ylabel('相位 (度)')
        ax_phase.grid(True, which='both', alpha=0.3)
        if label:
            ax_phase.legend()

    return mag_db, phase_deg


def fit_first_order_delay(freq, G_measured):
    """
    拟合一阶+延迟模型: G(s) = K * exp(-tau*s) / (T*s + 1)

    参数：
        freq: 频率数组
        G_measured: 测量的频率响应

    返回：
        K, T, tau: 模型参数
    """
    omega = 2 * np.pi * freq

    def model(omega, K, T, tau):
        s = 1j * omega
        G = K * np.exp(-tau * s) / (T * s + 1)
        return G

    def error(params):
        K, T, tau = params
        G_model = model(omega, K, T, tau)

        # 幅值误差
        mag_error = np.abs(np.abs(G_model) - np.abs(G_measured))

        # 相位误差（加权较小，因为相位更难拟合）
        phase_error = 0.1 * np.abs(np.angle(G_model) - np.angle(G_measured))

        return np.sum(mag_error**2 + phase_error**2)

    # 初始猜测
    K0 = np.abs(G_measured[0])
    T0 = 100.0
    tau0 = 10.0

    result = optimize.minimize(error, [K0, T0, tau0],
                               bounds=[(0.1, 10), (1, 1000), (0, 100)],
                               method='L-BFGS-B')

    K, T, tau = result.x
    return K, T, tau


# ==================== 演示部分 ====================

def part1_etfe_method():
    """Part 1: ETFE方法验证"""
    print("\n" + "="*60)
    print("Part 1: ETFE方法验证")
    print("="*60)

    # 生成测试系统：二阶系统
    wn = 0.5  # 自然频率
    zeta = 0.3  # 阻尼比
    K = 2.0  # 增益

    num = [K * wn**2]
    den = [1, 2*zeta*wn, wn**2]
    sys = signal.TransferFunction(num, den)

    print(f"测试系统：二阶系统")
    print(f"  自然频率 ωn = {wn} rad/s")
    print(f"  阻尼比 ζ = {zeta}")
    print(f"  增益 K = {K}")

    # 生成Chirp激励
    dt = 0.5
    t = np.arange(0, 1000, dt)
    u = generate_chirp(t, f0=0.01, f1=1.0, method='logarithmic')

    # 系统响应
    _, y, _ = signal.lsim(sys, u, t)

    # 添加噪声
    noise_level = 0.05
    y_noisy = y + noise_level * np.std(y) * np.random.randn(len(y))

    # ETFE估计
    freq_etfe, G_etfe = etfe(u, y_noisy, dt, nfft=4096)

    # 理论Bode图
    freq_theory = np.logspace(-3, 1, 200)
    _, G_theory = signal.freqs(num, den, worN=2*np.pi*freq_theory)

    print(f"\n生成数据: {len(t)} 个采样点")
    print(f"ETFE频率分辨率: {freq_etfe[1] - freq_etfe[0]:.6f} Hz")

    # 可视化
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))

    # 时域信号
    ax = axes[0]
    ax.plot(t[:500], u[:500], 'b-', linewidth=1, alpha=0.7, label='输入（Chirp）')
    ax.plot(t[:500], y_noisy[:500], 'r-', linewidth=1, alpha=0.7, label='输出（含噪声）')
    ax.set_xlabel('时间 (s)')
    ax.set_ylabel('幅值')
    ax.set_title('时域信号')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Bode图 - 幅频
    ax = axes[1]
    bode_plot(freq_theory, G_theory, ax_mag=ax, label='理论值',
              linewidth=2, color='black')
    bode_plot(freq_etfe[1:], G_etfe[1:], ax_mag=ax, label='ETFE估计',
              linewidth=1, alpha=0.5, color='blue')
    ax.set_title('Bode图：幅频特性')
    ax.set_xlim([0.01, 1.0])

    # Bode图 - 相频
    ax = axes[2]
    bode_plot(freq_theory, G_theory, ax_phase=ax, label='理论值',
              linewidth=2, color='black')
    bode_plot(freq_etfe[1:], G_etfe[1:], ax_phase=ax, label='ETFE估计',
              linewidth=1, alpha=0.5, color='blue')
    ax.set_title('Bode图：相频特性')
    ax.set_xlim([0.01, 1.0])

    plt.tight_layout()
    plt.savefig('part1_etfe_method.png', dpi=150, bbox_inches='tight')
    print("图表已保存: part1_etfe_method.png")
    plt.close()


def part2_welch_spectrum():
    """Part 2: Welch谱估计"""
    print("\n" + "="*60)
    print("Part 2: Welch谱估计")
    print("="*60)

    # 生成测试系统
    num = [1.5]
    den = [1, 0.8, 0.5]
    sys = signal.TransferFunction(num, den)

    # 生成随机激励
    dt = 0.5
    t = np.arange(0, 2000, dt)
    np.random.seed(42)
    u = np.random.randn(len(t))

    # 系统响应
    _, y, _ = signal.lsim(sys, u, t)

    # 添加较强噪声
    y_noisy = y + 0.3 * np.std(y) * np.random.randn(len(y))

    print(f"数据长度: {len(t)} 点")
    print(f"信噪比: 约10 dB")

    # 方法1: ETFE（原始周期图）
    freq_etfe, G_etfe = etfe(u, y_noisy, dt)

    # 方法2: Welch方法
    nperseg = 256
    freq_welch, G_welch, coherence = welch_estimate(u, y_noisy, dt,
                                                     nperseg=nperseg,
                                                     noverlap=nperseg//2)

    # 理论值
    freq_theory = np.logspace(-3, 0, 200)
    _, G_theory = signal.freqs(num, den, worN=2*np.pi*freq_theory)

    print(f"\nWelch参数:")
    print(f"  每段长度: {nperseg}")
    print(f"  段数: 约{len(t)//nperseg}")
    print(f"  频率分辨率: {freq_welch[1] - freq_welch[0]:.6f} Hz")

    # 可视化
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Bode图对比 - 幅频
    ax = axes[0, 0]
    bode_plot(freq_theory, G_theory, ax_mag=ax, label='理论值',
              linewidth=2, color='black')
    bode_plot(freq_etfe[1:100], G_etfe[1:100], ax_mag=ax, label='ETFE（原始）',
              linewidth=1, alpha=0.3, color='red')
    bode_plot(freq_welch, G_welch, ax_mag=ax, label='Welch（平滑）',
              linewidth=2, color='blue')
    ax.set_title('幅频特性对比')
    ax.set_xlim([0.01, 1.0])

    # Bode图对比 - 相频
    ax = axes[0, 1]
    bode_plot(freq_theory, G_theory, ax_phase=ax, label='理论值',
              linewidth=2, color='black')
    bode_plot(freq_etfe[1:100], G_etfe[1:100], ax_phase=ax, label='ETFE（原始）',
              linewidth=1, alpha=0.3, color='red')
    bode_plot(freq_welch, G_welch, ax_phase=ax, label='Welch（平滑）',
              linewidth=2, color='blue')
    ax.set_title('相频特性对比')
    ax.set_xlim([0.01, 1.0])

    # 相干函数
    ax = axes[1, 0]
    ax.semilogx(freq_welch, coherence, 'b-', linewidth=2)
    ax.axhline(0.8, color='r', linestyle='--', alpha=0.5, label='阈值0.8')
    ax.set_xlabel('频率 (Hz)')
    ax.set_ylabel('相干函数')
    ax.set_title('相干函数分析')
    ax.set_ylim([0, 1.1])
    ax.set_xlim([0.01, 1.0])
    ax.legend()
    ax.grid(True, which='both', alpha=0.3)

    # 幅值误差对比
    ax = axes[1, 1]

    # 插值到相同频率以计算误差
    from scipy.interpolate import interp1d

    # ETFE误差
    valid_idx = (freq_etfe > 0.01) & (freq_etfe < 1.0)
    freq_valid = freq_etfe[valid_idx]
    G_etfe_valid = G_etfe[valid_idx]

    f_theory = interp1d(freq_theory, np.abs(G_theory), kind='linear',
                        bounds_error=False, fill_value='extrapolate')

    error_etfe = np.abs(np.abs(G_etfe_valid) - f_theory(freq_valid))

    # Welch误差
    error_welch = np.abs(np.abs(G_welch) - f_theory(freq_welch))

    ax.loglog(freq_valid[::10], error_etfe[::10], 'r.', alpha=0.3,
              markersize=2, label='ETFE误差')
    ax.loglog(freq_welch, error_welch, 'b-', linewidth=2, label='Welch误差')
    ax.set_xlabel('频率 (Hz)')
    ax.set_ylabel('幅值误差')
    ax.set_title('估计误差对比')
    ax.legend()
    ax.grid(True, which='both', alpha=0.3)

    print(f"\n平均幅值误差:")
    print(f"  ETFE: {np.mean(error_etfe):.4f}")
    print(f"  Welch: {np.mean(error_welch):.4f}")
    print(f"  改善: {np.mean(error_etfe)/np.mean(error_welch):.2f}x")

    plt.tight_layout()
    plt.savefig('part2_welch_spectrum.png', dpi=150, bbox_inches='tight')
    print("图表已保存: part2_welch_spectrum.png")
    plt.close()


def part3_canal_frequency():
    """Part 3: 渠道系统频域辨识"""
    print("\n" + "="*60)
    print("Part 3: 渠道系统频域辨识")
    print("="*60)

    # 渠道仿真
    print("生成渠道系统数据...")
    canal = CanalReach(N=51)
    gate = GateModel()

    # 初始化
    h0 = np.ones(51) * 1.5
    Q0 = np.ones(51) * 5.0
    canal.set_state(h0, Q0)

    # Chirp激励
    dt = 10.0  # 采样时间10s
    t = np.arange(0, 3600, dt)  # 1小时

    # 低频Chirp（0.001 - 0.05 Hz）
    f0, f1 = 0.001, 0.05
    chirp_signal = 0.5 + 0.15 * generate_chirp(t, f0, f1, method='logarithmic')

    print(f"激励信号: Chirp扫频")
    print(f"  频率范围: {f0} - {f1} Hz")
    print(f"  持续时间: {t[-1]} s")
    print(f"  采样间隔: {dt} s")

    # 仿真
    u_history = []
    y_history = []

    for k in range(len(t)):
        u_k = chirp_signal[k]
        Q_out = gate.flow(canal.h[-1], u_k)
        Q_in = 5.0
        canal.step(dt, Q_in=Q_in, Q_out=Q_out)

        # 输出：下游水位
        y_k = canal.h[-10]

        u_history.append(u_k)
        y_history.append(y_k)

    u_data = np.array(u_history)
    y_data = np.array(y_history)

    # 去趋势（中心化）
    u_centered = u_data - np.mean(u_data)
    y_centered = y_data - np.mean(y_data)

    print(f"\n数据统计:")
    print(f"  输入范围: [{np.min(u_data):.3f}, {np.max(u_data):.3f}]")
    print(f"  输出范围: [{np.min(y_data):.3f}, {np.max(y_data):.3f}]")

    # Welch频率响应估计
    nperseg = 64
    freq, G_est, coherence = welch_estimate(u_centered, y_centered, dt,
                                            nperseg=nperseg, noverlap=nperseg//2)

    print(f"\nWelch估计:")
    print(f"  频率分辨率: {freq[1]-freq[0]:.6f} Hz")
    print(f"  有效频段（相干>0.7）: ", end='')
    valid_freq = freq[coherence > 0.7]
    if len(valid_freq) > 0:
        print(f"{valid_freq[0]:.4f} - {valid_freq[-1]:.4f} Hz")
    else:
        print("无")

    # 可视化
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 时域信号
    ax = axes[0, 0]
    ax.plot(t/60, u_data, 'b-', linewidth=1.5, alpha=0.7, label='输入（闸门开度）')
    ax.set_xlabel('时间 (分钟)')
    ax.set_ylabel('闸门开度')
    ax.set_title('Chirp激励信号')
    ax.legend()
    ax.grid(True, alpha=0.3)

    ax2 = ax.twinx()
    ax2.plot(t/60, y_data, 'r-', linewidth=1.5, alpha=0.7, label='输出（水位）')
    ax2.set_ylabel('水位 (m)', color='r')
    ax2.tick_params(axis='y', labelcolor='r')

    # Bode图 - 幅频
    ax = axes[0, 1]
    valid_idx = freq > 0
    bode_plot(freq[valid_idx], G_est[valid_idx], ax_mag=ax,
              label='Welch估计', linewidth=2, color='blue')
    ax.set_title('Bode图：幅频特性')
    ax.set_xlim([0.001, 0.1])

    # Bode图 - 相频
    ax = axes[1, 0]
    bode_plot(freq[valid_idx], G_est[valid_idx], ax_phase=ax,
              label='Welch估计', linewidth=2, color='blue')
    ax.set_title('Bode图：相频特性')
    ax.set_xlim([0.001, 0.1])

    # 相干函数
    ax = axes[1, 1]
    ax.semilogx(freq[valid_idx], coherence[valid_idx], 'g-', linewidth=2)
    ax.axhline(0.7, color='r', linestyle='--', alpha=0.5, label='阈值0.7')
    ax.set_xlabel('频率 (Hz)')
    ax.set_ylabel('相干函数')
    ax.set_title('相干函数（线性度检验）')
    ax.set_ylim([0, 1.1])
    ax.set_xlim([0.001, 0.1])
    ax.legend()
    ax.grid(True, which='both', alpha=0.3)

    plt.tight_layout()
    plt.savefig('part3_canal_frequency.png', dpi=150, bbox_inches='tight')
    print("图表已保存: part3_canal_frequency.png")
    plt.close()


def part4_model_fitting():
    """Part 4: 参数化模型拟合"""
    print("\n" + "="*60)
    print("Part 4: 参数化模型拟合")
    print("="*60)

    # 使用Part 3的渠道数据
    print("重新生成渠道系统数据...")
    canal = CanalReach(N=51)
    gate = GateModel()

    h0 = np.ones(51) * 1.5
    Q0 = np.ones(51) * 5.0
    canal.set_state(h0, Q0)

    dt = 10.0
    t = np.arange(0, 3600, dt)

    chirp_signal = 0.5 + 0.15 * generate_chirp(t, 0.001, 0.05, method='logarithmic')

    u_history = []
    y_history = []

    for k in range(len(t)):
        u_k = chirp_signal[k]
        Q_out = gate.flow(canal.h[-1], u_k)
        canal.step(dt, Q_in=5.0, Q_out=Q_out)
        u_history.append(u_k)
        y_history.append(canal.h[-10])

    u_data = np.array(u_history)
    y_data = np.array(y_history)

    u_centered = u_data - np.mean(u_data)
    y_centered = y_data - np.mean(y_data)

    # Welch估计
    nperseg = 64
    freq, G_est, coherence = welch_estimate(u_centered, y_centered, dt,
                                            nperseg=nperseg, noverlap=nperseg//2)

    # 选择高相干度频段
    valid_mask = coherence > 0.6
    freq_valid = freq[valid_mask]
    G_valid = G_est[valid_mask]

    print(f"用于拟合的频点数: {len(freq_valid)}")

    # 拟合一阶+延迟模型
    print("\n拟合一阶+延迟模型: G(s) = K*exp(-τ*s)/(T*s+1)")

    try:
        K, T, tau = fit_first_order_delay(freq_valid, G_valid)
        print(f"\n拟合结果:")
        print(f"  增益 K = {K:.4f}")
        print(f"  时间常数 T = {T:.2f} s")
        print(f"  延迟 τ = {tau:.2f} s")

        # 生成拟合模型的频率响应
        omega = 2 * np.pi * freq_valid
        s = 1j * omega
        G_fitted = K * np.exp(-tau * s) / (T * s + 1)

        # 计算拟合误差
        mag_error = np.mean(np.abs(np.abs(G_fitted) - np.abs(G_valid)))
        print(f"  平均幅值误差: {mag_error:.4f}")

        fitting_success = True
    except Exception as e:
        print(f"拟合失败: {e}")
        print("将仅显示估计的频率响应")
        fitting_success = False

    # 可视化
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Bode图 - 幅频（拟合对比）
    ax = axes[0, 0]
    valid_idx = freq > 0
    bode_plot(freq[valid_idx], G_est[valid_idx], ax_mag=ax,
              label='Welch估计', linewidth=2, color='blue', alpha=0.7)

    if fitting_success:
        bode_plot(freq_valid, G_fitted, ax_mag=ax,
                  label=f'拟合模型 (K={K:.2f}, T={T:.0f}s, τ={tau:.0f}s)',
                  linewidth=2, color='red', linestyle='--')

    ax.set_title('Bode图：幅频特性（拟合对比）')
    ax.set_xlim([0.001, 0.1])

    # Bode图 - 相频（拟合对比）
    ax = axes[0, 1]
    bode_plot(freq[valid_idx], G_est[valid_idx], ax_phase=ax,
              label='Welch估计', linewidth=2, color='blue', alpha=0.7)

    if fitting_success:
        bode_plot(freq_valid, G_fitted, ax_phase=ax,
                  label='拟合模型', linewidth=2, color='red', linestyle='--')

    ax.set_title('Bode图：相频特性（拟合对比）')
    ax.set_xlim([0.001, 0.1])

    # 时域验证：阶跃响应
    ax = axes[1, 0]

    if fitting_success:
        # 生成阶跃响应
        t_step = np.arange(0, 1000, dt)
        u_step = np.ones(len(t_step)) * 0.1  # 10%阶跃

        # 实际系统响应
        canal.set_state(h0, Q0)
        y_actual = []
        for k in range(len(t_step)):
            Q_out = gate.flow(canal.h[-1], 0.5 + u_step[k])
            canal.step(dt, Q_in=5.0, Q_out=Q_out)
            y_actual.append(canal.h[-10] - h0[-10])

        # 拟合模型响应（近似离散化）
        num = [K]
        den = [T, 1]
        sys_fitted = signal.TransferFunction(num, den)
        sys_discrete = sys_fitted.to_discrete(dt, method='zoh')

        _, y_model = signal.dlsim(sys_discrete, u_step, t_step)

        # 添加延迟效果
        delay_steps = int(tau / dt)
        y_model_delayed = np.concatenate([np.zeros(delay_steps), y_model[:-delay_steps].flatten()])

        ax.plot(t_step, y_actual, 'b-', linewidth=2, label='实际响应', alpha=0.7)
        ax.plot(t_step, y_model_delayed, 'r--', linewidth=2, label='拟合模型响应')
        ax.set_xlabel('时间 (s)')
        ax.set_ylabel('水位变化 (m)')
        ax.set_title('时域验证：阶跃响应')
        ax.legend()
        ax.grid(True, alpha=0.3)
    else:
        ax.text(0.5, 0.5, '拟合失败，无法显示时域验证',
                ha='center', va='center', transform=ax.transAxes, fontsize=14)
        ax.set_title('时域验证：阶跃响应')

    # 拟合误差分析
    ax = axes[1, 1]

    if fitting_success:
        mag_meas = np.abs(G_valid)
        mag_fit = np.abs(G_fitted)
        error_percent = 100 * np.abs(mag_meas - mag_fit) / (mag_meas + 1e-10)

        ax.semilogx(freq_valid, error_percent, 'go-', linewidth=2, markersize=5)
        ax.set_xlabel('频率 (Hz)')
        ax.set_ylabel('相对误差 (%)')
        ax.set_title(f'拟合误差（平均: {np.mean(error_percent):.2f}%）')
        ax.grid(True, which='both', alpha=0.3)
        ax.set_xlim([0.001, 0.1])
    else:
        ax.text(0.5, 0.5, '拟合失败，无法显示误差分析',
                ha='center', va='center', transform=ax.transAxes, fontsize=14)
        ax.set_title('拟合误差分析')

    plt.tight_layout()
    plt.savefig('part4_model_fitting.png', dpi=150, bbox_inches='tight')
    print("图表已保存: part4_model_fitting.png")
    plt.close()


def main():
    """主函数"""
    print("="*60)
    print("案例9：频域辨识方法")
    print("Frequency Domain Identification")
    print("="*60)

    # 运行所有部分
    part1_etfe_method()
    part2_welch_spectrum()
    part3_canal_frequency()
    part4_model_fitting()

    print("\n" + "="*60)
    print("案例9完成！所有图表已保存。")
    print("="*60)

    print("\n关键结论：")
    print("1. ETFE是最简单的频域辨识方法，但噪声敏感")
    print("2. Welch方法通过分段平均显著降低估计方差")
    print("3. 相干函数用于验证线性假设和确定有效频段")
    print("4. 渠道系统主要动态在低频段（0.001-0.05 Hz）")
    print("5. 参数化拟合得到简洁模型（一阶+延迟）")
    print("6. 频域方法提供直观的物理洞察（Bode图）")


if __name__ == "__main__":
    main()
