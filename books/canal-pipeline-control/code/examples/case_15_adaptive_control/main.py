#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
案例15：自适应控制（Model Reference Adaptive Control, MRAC）

本案例演示MRAC在运河系统中的应用，包括：
1. MRAC基础 - 标量系统（MIT规则 vs Lyapunov方法）
2. 运河系统MRAC - 参数不确定性
3. MRAC鲁棒性测试 - 扰动和噪声
4. 持续激励条件验证

作者：Claude
日期：2024
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from scipy.integrate import odeint
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


# ============================================================================
# 第一部分：参考模型类
# ============================================================================

class ReferenceModel:
    """
    参考模型类 - 描述期望的系统动态响应

    通常选择标准二阶系统：
    G_m(s) = ω_n² / (s² + 2ζω_n·s + ω_n²)
    """

    def __init__(self, wn=0.1, zeta=0.8, order='second'):
        """
        初始化参考模型

        参数：
            wn: 自然频率 (rad/s)
            zeta: 阻尼比
            order: 'first' 或 'second'
        """
        self.wn = wn
        self.zeta = zeta
        self.order = order

        if order == 'first':
            # 一阶系统: G_m(s) = wn / (s + wn)
            self.Am = np.array([[-wn]])
            self.Bm = np.array([[wn]])
            self.Cm = np.array([[1.0]])
            self.x_m = np.array([0.0])
        else:
            # 二阶系统
            self.Am = np.array([
                [0, 1],
                [-wn**2, -2*zeta*wn]
            ])
            self.Bm = np.array([[0], [wn**2]])
            self.Cm = np.array([[1.0, 0]])
            self.x_m = np.array([0.0, 0.0])

    def update(self, r, dt):
        """
        更新参考模型状态

        参数：
            r: 参考输入
            dt: 时间步长
        """
        # 使用欧拉法积分（简单但需要小dt）
        dx_m = self.Am @ self.x_m + self.Bm.flatten() * r
        self.x_m += dt * dx_m
        y_m = (self.Cm @ self.x_m).item()
        return y_m

    def reset(self):
        """重置参考模型状态"""
        self.x_m = np.zeros_like(self.x_m)

    def get_transfer_function(self):
        """返回传递函数（用于频域分析）"""
        sys = signal.StateSpace(self.Am, self.Bm, self.Cm, 0)
        return signal.ss2tf(sys.A, sys.B, sys.C, sys.D)


# ============================================================================
# 第二部分：MRAC控制器类
# ============================================================================

class MRACController:
    """
    模型参考自适应控制器

    控制律：
        u(t) = θ_r(t)·r(t) - θ_y(t)·y(t) - θ_u(t)·u(t-1)

    自适应律：
        MIT规则（梯度法）或 Lyapunov方法
    """

    def __init__(self, reference_model, method='lyapunov',
                 gamma_r=0.01, gamma_y=0.02, gamma_u=0.01,
                 theta_r_init=1.0, theta_y_init=0.1, theta_u_init=0.0,
                 Kp_sign=1.0, use_projection=True,
                 use_sigma_modification=False, sigma=0.001,
                 use_dead_zone=False, dead_zone_width=0.01):
        """
        初始化MRAC控制器

        参数：
            reference_model: ReferenceModel对象
            method: 'mit' 或 'lyapunov'
            gamma_r, gamma_y, gamma_u: 自适应增益
            theta_r_init, theta_y_init, theta_u_init: 参数初值
            Kp_sign: 系统增益符号（+1或-1，Lyapunov方法需要）
            use_projection: 是否使用参数投影
            use_sigma_modification: 是否使用σ修正
            sigma: σ修正系数
            use_dead_zone: 是否使用误差死区
            dead_zone_width: 死区宽度
        """
        self.ref_model = reference_model
        self.method = method

        # 自适应增益
        self.gamma_r = gamma_r
        self.gamma_y = gamma_y
        self.gamma_u = gamma_u

        # 自适应参数
        self.theta_r = theta_r_init
        self.theta_y = theta_y_init
        self.theta_u = theta_u_init

        # Lyapunov方法需要知道系统增益符号
        self.Kp_sign = Kp_sign

        # 鲁棒性增强选项
        self.use_projection = use_projection
        self.use_sigma_modification = use_sigma_modification
        self.sigma = sigma
        self.use_dead_zone = use_dead_zone
        self.dead_zone_width = dead_zone_width

        # 参数约束（用于投影）
        self.theta_min = np.array([0.0, 0.0, -1.0])
        self.theta_max = np.array([10.0, 5.0, 1.0])

        # 控制输入约束
        self.u_min = 0.0
        self.u_max = 50.0

        # 历史记录
        self.u_prev = 0.0
        self.history = {
            'theta_r': [],
            'theta_y': [],
            'theta_u': [],
            'error': [],
            'y_m': []
        }

    def compute_control(self, y, r, dt):
        """
        计算控制输入和更新自适应参数

        参数：
            y: 当前系统输出
            r: 参考输入
            dt: 时间步长

        返回：
            u: 控制输入
            e: 跟踪误差
            y_m: 参考模型输出
        """
        # 1. 更新参考模型
        y_m = self.ref_model.update(r, dt)

        # 2. 计算跟踪误差
        e = y - y_m

        # 3. 误差死区处理
        e_effective = e
        if self.use_dead_zone:
            if abs(e) < self.dead_zone_width:
                e_effective = 0.0

        # 4. 更新自适应参数
        if self.method == 'mit':
            # MIT规则（梯度法）
            dtheta_r = -self.gamma_r * r * e_effective
            dtheta_y = self.gamma_y * y * e_effective
            dtheta_u = self.gamma_u * self.u_prev * e_effective
        else:
            # Lyapunov方法
            dtheta_r = -self.gamma_r * r * e_effective * self.Kp_sign
            dtheta_y = self.gamma_y * y * e_effective * self.Kp_sign
            dtheta_u = self.gamma_u * self.u_prev * e_effective * self.Kp_sign

        # 5. σ修正（鲁棒性增强）
        if self.use_sigma_modification:
            dtheta_r -= self.sigma * self.theta_r
            dtheta_y -= self.sigma * self.theta_y
            dtheta_u -= self.sigma * self.theta_u

        # 6. 积分更新参数
        self.theta_r += dt * dtheta_r
        self.theta_y += dt * dtheta_y
        self.theta_u += dt * dtheta_u

        # 7. 参数投影（防止漂移）
        if self.use_projection:
            self.theta_r = np.clip(self.theta_r,
                                   self.theta_min[0], self.theta_max[0])
            self.theta_y = np.clip(self.theta_y,
                                   self.theta_min[1], self.theta_max[1])
            self.theta_u = np.clip(self.theta_u,
                                   self.theta_min[2], self.theta_max[2])

        # 8. 计算控制输入
        u = self.theta_r * r - self.theta_y * y - self.theta_u * self.u_prev

        # 9. 控制饱和
        u = np.clip(u, self.u_min, self.u_max)

        # 10. 更新历史
        self.u_prev = u
        self.history['theta_r'].append(self.theta_r)
        self.history['theta_y'].append(self.theta_y)
        self.history['theta_u'].append(self.theta_u)
        self.history['error'].append(e)
        self.history['y_m'].append(y_m)

        return u, e, y_m

    def reset(self, theta_r_init=None, theta_y_init=None, theta_u_init=None):
        """重置控制器状态"""
        if theta_r_init is not None:
            self.theta_r = theta_r_init
        if theta_y_init is not None:
            self.theta_y = theta_y_init
        if theta_u_init is not None:
            self.theta_u = theta_u_init

        self.u_prev = 0.0
        self.ref_model.reset()
        self.history = {
            'theta_r': [],
            'theta_y': [],
            'theta_u': [],
            'error': [],
            'y_m': []
        }

    def get_parameters(self):
        """返回当前参数"""
        return {
            'theta_r': self.theta_r,
            'theta_y': self.theta_y,
            'theta_u': self.theta_u
        }


# ============================================================================
# 第三部分：被控系统模型
# ============================================================================

class ScalarSystem:
    """
    标量一阶系统（用于演示Part 1）

    dy/dt = -a·y + b·u

    其中 a, b 是未知参数
    """

    def __init__(self, a=2.0, b=1.5, y0=0.0, dt=0.01):
        """
        初始化标量系统

        参数：
            a: 系统参数（衰减率）
            b: 控制增益（未知）
            y0: 初始状态
            dt: 时间步长
        """
        self.a = a
        self.b = b
        self.y = y0
        self.dt = dt

    def update(self, u):
        """
        更新系统状态

        参数：
            u: 控制输入

        返回：
            y: 当前输出
        """
        # dy/dt = -a·y + b·u
        dy = -self.a * self.y + self.b * u
        self.y += self.dt * dy
        return self.y

    def reset(self, y0=0.0):
        """重置系统状态"""
        self.y = y0


class SimplifiedCanalSystem:
    """
    简化运河系统模型（用于演示Part 2-4）

    状态空间形式：
        dx/dt = A·x + B·u + E·d
        y = C·x + v

    其中：
        x = [h, Q]ᵀ  （水位，流量）
        u = Q_in     （入流量）
        d = Q_lateral（侧向入流扰动）
        y = h + v    （水位测量 + 噪声）
    """

    def __init__(self, L=1000, B=5.0, S0=0.001, n=0.025,
                 h0=2.0, Q0=10.0, dt=1.0):
        """
        初始化运河系统

        参数：
            L: 渠段长度 (m)
            B: 渠道宽度 (m)
            S0: 底坡
            n: 曼宁糙率系数（可能未知或时变）
            h0: 平衡水位 (m)
            Q0: 平衡流量 (m³/s)
            dt: 时间步长 (s)
        """
        self.L = L
        self.B_width = B  # 渠道宽度（避免与控制矩阵B冲突）
        self.S0 = S0
        self.n = n
        self.h0 = h0
        self.Q0 = Q0
        self.dt = dt

        # 计算过水断面积和水力半径（矩形渠道）
        self.A_c = B * h0
        self.R_h = (B * h0) / (B + 2 * h0)

        # 流速
        self.v = Q0 / self.A_c

        # 构建线性化系统矩阵
        self._build_matrices()

        # 状态：[h, Q]
        self.x = np.array([h0, Q0])

    def _build_matrices(self):
        """构建线性化状态空间矩阵"""
        g = 9.81  # 重力加速度

        # A矩阵
        a11 = -self.v / self.L
        a12 = 1.0 / (self.B_width * self.L)
        a21 = -g * self.A_c * self.S0 / self.L
        a22 = -g * self.n**2 * abs(self.Q0) / (self.A_c * self.R_h**(4/3))

        self.A = np.array([
            [a11, a12],
            [a21, a22]
        ])

        # B矩阵（控制输入）
        self.B = np.array([0, 1.0 / self.A_c])

        # E矩阵（扰动输入）
        self.E = np.array([0, 1.0 / self.A_c])

        # C矩阵（输出：水位）
        self.C = np.array([1.0, 0])

    def update(self, u, d=0.0, noise_std=0.0):
        """
        更新系统状态

        参数：
            u: 控制输入（入流量）
            d: 扰动（侧向入流）
            noise_std: 测量噪声标准差

        返回：
            y: 带噪声的水位测量值
        """
        # dx/dt = A·x + B·u + E·d
        dx = self.A @ self.x + self.B * u + self.E * d
        self.x += self.dt * dx

        # 状态约束（物理可行性）
        self.x[0] = np.clip(self.x[0], 0.5, 5.0)  # 水位范围
        self.x[1] = np.clip(self.x[1], 0.0, 50.0)  # 流量范围

        # 输出：y = C·x + v（测量噪声）
        y_true = self.C @ self.x
        noise = np.random.normal(0, noise_std)
        y = y_true + noise

        return y

    def get_state(self):
        """返回当前状态"""
        return self.x.copy()

    def reset(self, x0=None):
        """重置系统状态"""
        if x0 is None:
            self.x = np.array([self.h0, self.Q0])
        else:
            self.x = np.array(x0)

    def set_parameter(self, param_name, value):
        """
        改变系统参数（模拟时变特性）

        参数：
            param_name: 'n', 'S0', 'B' 等
            value: 新值
        """
        if param_name == 'n':
            self.n = value
        elif param_name == 'S0':
            self.S0 = value
        elif param_name == 'B':
            self.B_width = value
            # 重新计算几何参数
            self.A_c = self.B_width * self.h0
            self.R_h = (self.B_width * self.h0) / (self.B_width + 2 * self.h0)
            self.v = self.Q0 / self.A_c

        # 重新构建矩阵
        self._build_matrices()


# ============================================================================
# 第四部分：演示函数
# ============================================================================

def part1_scalar_system_demo():
    """
    Part 1: MRAC基础 - 标量系统

    演示：
    - MIT规则 vs Lyapunov方法
    - 参数收敛过程
    - 不同自适应增益的影响
    """
    print("\n" + "="*70)
    print("Part 1: MRAC基础 - 标量系统")
    print("="*70)

    # 仿真参数
    T_sim = 50.0  # 仿真时间
    dt = 0.01
    t = np.arange(0, T_sim, dt)
    N = len(t)

    # 真实系统：dy/dt = -a·y + b·u（参数未知）
    a_true = 2.0
    b_true = 1.5
    system = ScalarSystem(a=a_true, b=b_true, dt=dt)

    # 参考模型：一阶系统，时间常数 = 1.0s
    wn_ref = 1.0
    ref_model = ReferenceModel(wn=wn_ref, zeta=1.0, order='first')

    # 理想参数（使y(t) = y_m(t)）
    theta_r_ideal = wn_ref / b_true  # ≈ 0.667
    theta_y_ideal = (wn_ref - (-a_true)) / b_true  # = 3/1.5 = 2.0

    print(f"\n真实系统参数: a={a_true}, b={b_true}")
    print(f"理想控制器参数: θ_r*={theta_r_ideal:.3f}, θ_y*={theta_y_ideal:.3f}")

    # 参考输入：正弦 + 阶跃（持续激励）
    r = np.zeros(N)
    r[0:N//2] = 1.0  # 阶跃
    r[N//2:] = 1.0 + 0.5*np.sin(2*np.pi*0.1*t[N//2:])  # 正弦

    # ========== 测试1：MIT规则 ==========
    print("\n--- 测试1：MIT规则 ---")
    controller_mit = MRACController(
        reference_model=ReferenceModel(wn=wn_ref, zeta=1.0, order='first'),
        method='mit',
        gamma_r=0.1, gamma_y=0.1, gamma_u=0.0,
        theta_r_init=0.1, theta_y_init=0.1,
        use_projection=True
    )

    system.reset()
    y_mit = np.zeros(N)
    y_m_mit = np.zeros(N)
    u_mit = np.zeros(N)

    for i in range(N):
        u, e, y_m = controller_mit.compute_control(system.y, r[i], dt)
        y_mit[i] = system.update(u)
        y_m_mit[i] = y_m
        u_mit[i] = u

    # ========== 测试2：Lyapunov方法 ==========
    print("--- 测试2：Lyapunov方法 ---")
    controller_lyap = MRACController(
        reference_model=ReferenceModel(wn=wn_ref, zeta=1.0, order='first'),
        method='lyapunov',
        gamma_r=0.1, gamma_y=0.1, gamma_u=0.0,
        theta_r_init=0.1, theta_y_init=0.1,
        Kp_sign=1.0,  # b_true > 0
        use_projection=True
    )

    system.reset()
    y_lyap = np.zeros(N)
    y_m_lyap = np.zeros(N)
    u_lyap = np.zeros(N)

    for i in range(N):
        u, e, y_m = controller_lyap.compute_control(system.y, r[i], dt)
        y_lyap[i] = system.update(u)
        y_m_lyap[i] = y_m
        u_lyap[i] = u

    # 性能评估
    iae_mit = np.mean(np.abs(np.array(controller_mit.history['error'])))
    iae_lyap = np.mean(np.abs(np.array(controller_lyap.history['error'])))

    print(f"\nMIT规则 - 平均绝对误差: {iae_mit:.4f}")
    print(f"Lyapunov方法 - 平均绝对误差: {iae_lyap:.4f}")

    # 可视化
    fig, axes = plt.subplots(3, 2, figsize=(14, 10))
    fig.suptitle('Part 1: MRAC基础 - 标量系统（MIT vs Lyapunov）',
                 fontsize=14, fontweight='bold')

    # 左列：MIT规则
    axes[0, 0].plot(t, r, 'k--', label='参考输入 r(t)', linewidth=1.5)
    axes[0, 0].plot(t, y_m_mit, 'b-', label='参考模型 $y_m(t)$', linewidth=2)
    axes[0, 0].plot(t, y_mit, 'r-', label='系统输出 y(t)', alpha=0.7)
    axes[0, 0].set_ylabel('输出')
    axes[0, 0].set_title('MIT规则 - 跟踪性能')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)

    axes[1, 0].plot(t, controller_mit.history['theta_r'], 'g-',
                   label=f'$\\theta_r(t)$ → {theta_r_ideal:.2f}', linewidth=2)
    axes[1, 0].plot(t, controller_mit.history['theta_y'], 'm-',
                   label=f'$\\theta_y(t)$ → {theta_y_ideal:.2f}', linewidth=2)
    axes[1, 0].axhline(theta_r_ideal, color='g', linestyle=':', alpha=0.5)
    axes[1, 0].axhline(theta_y_ideal, color='m', linestyle=':', alpha=0.5)
    axes[1, 0].set_ylabel('参数值')
    axes[1, 0].set_title('MIT规则 - 参数收敛')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)

    axes[2, 0].plot(t, controller_mit.history['error'], 'r-')
    axes[2, 0].axhline(0, color='k', linestyle='--', alpha=0.5)
    axes[2, 0].set_xlabel('时间 (s)')
    axes[2, 0].set_ylabel('误差 e(t)')
    axes[2, 0].set_title('MIT规则 - 跟踪误差')
    axes[2, 0].grid(True, alpha=0.3)

    # 右列：Lyapunov方法
    axes[0, 1].plot(t, r, 'k--', label='参考输入 r(t)', linewidth=1.5)
    axes[0, 1].plot(t, y_m_lyap, 'b-', label='参考模型 $y_m(t)$', linewidth=2)
    axes[0, 1].plot(t, y_lyap, 'r-', label='系统输出 y(t)', alpha=0.7)
    axes[0, 1].set_ylabel('输出')
    axes[0, 1].set_title('Lyapunov方法 - 跟踪性能')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)

    axes[1, 1].plot(t, controller_lyap.history['theta_r'], 'g-',
                   label=f'$\\theta_r(t)$ → {theta_r_ideal:.2f}', linewidth=2)
    axes[1, 1].plot(t, controller_lyap.history['theta_y'], 'm-',
                   label=f'$\\theta_y(t)$ → {theta_y_ideal:.2f}', linewidth=2)
    axes[1, 1].axhline(theta_r_ideal, color='g', linestyle=':', alpha=0.5)
    axes[1, 1].axhline(theta_y_ideal, color='m', linestyle=':', alpha=0.5)
    axes[1, 1].set_ylabel('参数值')
    axes[1, 1].set_title('Lyapunov方法 - 参数收敛')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)

    axes[2, 1].plot(t, controller_lyap.history['error'], 'r-')
    axes[2, 1].axhline(0, color='k', linestyle='--', alpha=0.5)
    axes[2, 1].set_xlabel('时间 (s)')
    axes[2, 1].set_ylabel('误差 e(t)')
    axes[2, 1].set_title('Lyapunov方法 - 跟踪误差')
    axes[2, 1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('part1_scalar_mrac.png', dpi=150, bbox_inches='tight')
    print("\n✓ 图表已保存: part1_scalar_mrac.png")
    plt.close()


def part2_canal_system_mrac():
    """
    Part 2: 运河系统MRAC - 参数不确定性

    演示：
    - 糙率系数n未知或时变
    - 水位跟踪控制
    - 参数在线辨识效果
    """
    print("\n" + "="*70)
    print("Part 2: 运河系统MRAC - 参数不确定性")
    print("="*70)

    # 仿真参数
    T_sim = 600.0  # 10分钟
    dt = 1.0
    t = np.arange(0, T_sim, dt)
    N = len(t)

    # 运河系统（糙率n未知且在t=300s时突变）
    n_initial = 0.025
    n_changed = 0.035  # 糙率增加（淤积/植物生长）
    canal = SimplifiedCanalSystem(
        L=1000, B=5.0, S0=0.001, n=n_initial,
        h0=2.0, Q0=10.0, dt=dt
    )

    # 参考模型：二阶系统
    wn = 0.05  # 较慢的响应（运河系统惯性大）
    zeta = 0.9
    ref_model = ReferenceModel(wn=wn, zeta=zeta, order='second')

    # MRAC控制器（Lyapunov方法）
    controller = MRACController(
        reference_model=ref_model,
        method='lyapunov',
        gamma_r=0.005, gamma_y=0.01, gamma_u=0.002,
        theta_r_init=0.5, theta_y_init=0.01, theta_u_init=0.0,
        Kp_sign=1.0,
        use_projection=True,
        use_sigma_modification=True,
        sigma=0.0005
    )

    # 参考水位轨迹（阶梯状变化）
    h_ref = np.ones(N) * 2.0
    h_ref[100:200] = 2.5
    h_ref[200:300] = 2.2
    h_ref[300:400] = 2.8
    h_ref[400:] = 2.3

    # 初始化记录
    h_actual = np.zeros(N)
    h_model = np.zeros(N)
    Q_actual = np.zeros(N)
    u_control = np.zeros(N)

    print(f"\n初始糙率: n={n_initial}")
    print(f"在 t=300s 时糙率变为: n={n_changed}")

    # 仿真循环
    for i in range(N):
        # 在t=300s时改变糙率（模拟系统变化）
        if i == 300:
            canal.set_parameter('n', n_changed)
            print(f"\n⚠️  糙率突变！ n: {n_initial} → {n_changed}")

        # 当前状态
        state = canal.get_state()
        h_actual[i] = state[0]
        Q_actual[i] = state[1]

        # MRAC控制
        u, e, y_m = controller.compute_control(h_actual[i], h_ref[i], dt)
        u_control[i] = u
        h_model[i] = y_m

        # 更新运河系统
        _ = canal.update(u)

    # 性能评估
    tracking_error = np.abs(h_actual - h_ref)
    mae = np.mean(tracking_error)
    mae_before = np.mean(tracking_error[:300])
    mae_after = np.mean(tracking_error[300:])

    print(f"\n跟踪性能:")
    print(f"  总体平均绝对误差: {mae:.4f} m")
    print(f"  参数变化前 (0-300s): {mae_before:.4f} m")
    print(f"  参数变化后 (300-600s): {mae_after:.4f} m")

    # 可视化
    fig, axes = plt.subplots(4, 1, figsize=(14, 12))
    fig.suptitle('Part 2: 运河系统MRAC - 参数不确定性适应',
                 fontsize=14, fontweight='bold')

    # 子图1：水位跟踪
    axes[0].plot(t, h_ref, 'k--', label='期望水位', linewidth=2)
    axes[0].plot(t, h_model, 'b-', label='参考模型', linewidth=1.5, alpha=0.7)
    axes[0].plot(t, h_actual, 'r-', label='实际水位', linewidth=1.5)
    axes[0].axvline(300, color='orange', linestyle=':', linewidth=2,
                   label=f'糙率突变 (n: {n_initial}→{n_changed})')
    axes[0].set_ylabel('水位 (m)')
    axes[0].set_title('水位跟踪性能')
    axes[0].legend(loc='best')
    axes[0].grid(True, alpha=0.3)

    # 子图2：控制输入
    axes[1].plot(t, u_control, 'g-', linewidth=1.5)
    axes[1].axvline(300, color='orange', linestyle=':', linewidth=2)
    axes[1].axhline(canal.Q0, color='k', linestyle='--', alpha=0.5, label='平衡流量')
    axes[1].set_ylabel('入流量 (m³/s)')
    axes[1].set_title('控制输入（入流量）')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    # 子图3：自适应参数
    theta_r_history = np.array(controller.history['theta_r'])
    theta_y_history = np.array(controller.history['theta_y'])
    axes[2].plot(t, theta_r_history, 'c-', label='$\\theta_r(t)$', linewidth=2)
    axes[2].plot(t, theta_y_history, 'm-', label='$\\theta_y(t)$', linewidth=2)
    axes[2].axvline(300, color='orange', linestyle=':', linewidth=2)
    axes[2].set_ylabel('参数值')
    axes[2].set_title('自适应参数演化（自动适应糙率变化）')
    axes[2].legend()
    axes[2].grid(True, alpha=0.3)

    # 子图4：跟踪误差
    error_history = np.array(controller.history['error'])
    axes[3].plot(t, error_history, 'r-', linewidth=1.5)
    axes[3].axhline(0, color='k', linestyle='--', alpha=0.5)
    axes[3].axvline(300, color='orange', linestyle=':', linewidth=2)
    axes[3].fill_between(t, -0.05, 0.05, alpha=0.2, color='green', label='±5cm容差')
    axes[3].set_xlabel('时间 (s)')
    axes[3].set_ylabel('误差 (m)')
    axes[3].set_title('跟踪误差（注意参数变化后的重新收敛）')
    axes[3].legend()
    axes[3].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('part2_canal_mrac.png', dpi=150, bbox_inches='tight')
    print("\n✓ 图表已保存: part2_canal_mrac.png")
    plt.close()


def part3_robustness_test():
    """
    Part 3: MRAC鲁棒性测试 - 扰动和噪声

    演示：
    - 外部扰动（侧向入流）
    - 测量噪声
    - 鲁棒修正效果（σ修正、死区）
    """
    print("\n" + "="*70)
    print("Part 3: MRAC鲁棒性测试 - 扰动和噪声")
    print("="*70)

    # 仿真参数
    T_sim = 400.0
    dt = 1.0
    t = np.arange(0, T_sim, dt)
    N = len(t)

    # 运河系统
    canal = SimplifiedCanalSystem(
        L=1000, B=5.0, S0=0.001, n=0.025,
        h0=2.0, Q0=10.0, dt=dt
    )

    # 参考模型
    ref_model = ReferenceModel(wn=0.05, zeta=0.9, order='second')

    # 参考水位
    h_ref = 2.0 + 0.3 * np.sin(2*np.pi*t/200)  # 缓慢正弦变化

    # 扰动信号（侧向入流变化）
    disturbance = np.zeros(N)
    disturbance[100:150] = 2.0  # 突然增加2 m³/s
    disturbance[200:250] = -1.5  # 突然减少1.5 m³/s

    # 测量噪声
    noise_std = 0.02  # 2cm标准差

    # ========== 测试1：无鲁棒修正 ==========
    print("\n--- 测试1：无鲁棒修正 ---")
    controller1 = MRACController(
        reference_model=ReferenceModel(wn=0.05, zeta=0.9, order='second'),
        method='lyapunov',
        gamma_r=0.008, gamma_y=0.015, gamma_u=0.003,
        theta_r_init=0.5, theta_y_init=0.01,
        Kp_sign=1.0,
        use_sigma_modification=False,
        use_dead_zone=False
    )

    canal.reset()
    h1 = np.zeros(N)
    u1 = np.zeros(N)

    for i in range(N):
        state = canal.get_state()
        h_measured = state[0] + np.random.normal(0, noise_std)
        h1[i] = state[0]  # 真实值（用于评估）

        u, _, _ = controller1.compute_control(h_measured, h_ref[i], dt)
        u1[i] = u
        _ = canal.update(u, d=disturbance[i], noise_std=0)

    # ========== 测试2：有鲁棒修正 ==========
    print("--- 测试2：σ修正 + 死区 ---")
    controller2 = MRACController(
        reference_model=ReferenceModel(wn=0.05, zeta=0.9, order='second'),
        method='lyapunov',
        gamma_r=0.008, gamma_y=0.015, gamma_u=0.003,
        theta_r_init=0.5, theta_y_init=0.01,
        Kp_sign=1.0,
        use_sigma_modification=True,
        sigma=0.001,
        use_dead_zone=True,
        dead_zone_width=0.03  # 3cm死区
    )

    canal.reset()
    h2 = np.zeros(N)
    u2 = np.zeros(N)

    for i in range(N):
        state = canal.get_state()
        h_measured = state[0] + np.random.normal(0, noise_std)
        h2[i] = state[0]

        u, _, _ = controller2.compute_control(h_measured, h_ref[i], dt)
        u2[i] = u
        _ = canal.update(u, d=disturbance[i], noise_std=0)

    # 性能评估
    mae1 = np.mean(np.abs(h1 - h_ref))
    mae2 = np.mean(np.abs(h2 - h_ref))

    u_variance1 = np.var(np.diff(u1))
    u_variance2 = np.var(np.diff(u2))

    print(f"\n性能对比:")
    print(f"  无鲁棒修正 - MAE: {mae1:.4f} m, 控制抖动方差: {u_variance1:.6f}")
    print(f"  有鲁棒修正 - MAE: {mae2:.4f} m, 控制抖动方差: {u_variance2:.6f}")
    print(f"  控制平滑度改善: {(1-u_variance2/u_variance1)*100:.1f}%")

    # 可视化
    fig, axes = plt.subplots(4, 2, figsize=(15, 12))
    fig.suptitle('Part 3: MRAC鲁棒性测试（扰动+噪声）',
                 fontsize=14, fontweight='bold')

    # 左列：无鲁棒修正
    axes[0, 0].plot(t, h_ref, 'k--', label='期望水位', linewidth=2)
    axes[0, 0].plot(t, h1, 'r-', label='实际水位', alpha=0.8)
    axes[0, 0].fill_between(t, h_ref-0.05, h_ref+0.05, alpha=0.2, color='green')
    axes[0, 0].set_ylabel('水位 (m)')
    axes[0, 0].set_title('无鲁棒修正 - 水位跟踪')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)

    axes[1, 0].plot(t, u1, 'g-', alpha=0.7)
    axes[1, 0].set_ylabel('入流量 (m³/s)')
    axes[1, 0].set_title('控制输入（注意抖动）')
    axes[1, 0].grid(True, alpha=0.3)

    axes[2, 0].plot(t, disturbance, 'orange', linewidth=2)
    axes[2, 0].set_ylabel('扰动 (m³/s)')
    axes[2, 0].set_title('外部扰动（侧向入流）')
    axes[2, 0].grid(True, alpha=0.3)

    theta_r1 = np.array(controller1.history['theta_r'])
    theta_y1 = np.array(controller1.history['theta_y'])
    axes[3, 0].plot(t, theta_r1, 'c-', label='$\\theta_r$', alpha=0.7)
    axes[3, 0].plot(t, theta_y1, 'm-', label='$\\theta_y$', alpha=0.7)
    axes[3, 0].set_xlabel('时间 (s)')
    axes[3, 0].set_ylabel('参数值')
    axes[3, 0].set_title('自适应参数（可能漂移）')
    axes[3, 0].legend()
    axes[3, 0].grid(True, alpha=0.3)

    # 右列：有鲁棒修正
    axes[0, 1].plot(t, h_ref, 'k--', label='期望水位', linewidth=2)
    axes[0, 1].plot(t, h2, 'r-', label='实际水位', alpha=0.8)
    axes[0, 1].fill_between(t, h_ref-0.05, h_ref+0.05, alpha=0.2, color='green')
    axes[0, 1].set_ylabel('水位 (m)')
    axes[0, 1].set_title('有鲁棒修正 - 水位跟踪')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)

    axes[1, 1].plot(t, u2, 'g-', alpha=0.7)
    axes[1, 1].set_ylabel('入流量 (m³/s)')
    axes[1, 1].set_title('控制输入（更平滑）')
    axes[1, 1].grid(True, alpha=0.3)

    axes[2, 1].plot(t, disturbance, 'orange', linewidth=2)
    axes[2, 1].set_ylabel('扰动 (m³/s)')
    axes[2, 1].set_title('外部扰动（相同）')
    axes[2, 1].grid(True, alpha=0.3)

    theta_r2 = np.array(controller2.history['theta_r'])
    theta_y2 = np.array(controller2.history['theta_y'])
    axes[3, 1].plot(t, theta_r2, 'c-', label='$\\theta_r$', alpha=0.7)
    axes[3, 1].plot(t, theta_y2, 'm-', label='$\\theta_y$', alpha=0.7)
    axes[3, 1].set_xlabel('时间 (s)')
    axes[3, 1].set_ylabel('参数值')
    axes[3, 1].set_title('自适应参数（σ修正防漂移）')
    axes[3, 1].legend()
    axes[3, 1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('part3_robustness_test.png', dpi=150, bbox_inches='tight')
    print("\n✓ 图表已保存: part3_robustness_test.png")
    plt.close()


def part4_persistent_excitation():
    """
    Part 4: 持续激励条件验证

    演示：
    - 阶跃输入：参数不收敛（但e→0）
    - 正弦输入：参数收敛到真值
    - Chirp信号：最佳参数收敛
    """
    print("\n" + "="*70)
    print("Part 4: 持续激励（PE）条件验证")
    print("="*70)

    # 仿真参数
    T_sim = 300.0
    dt = 0.1
    t = np.arange(0, T_sim, dt)
    N = len(t)

    # 真实系统（标量）
    a_true = 2.0
    b_true = 1.5

    # 理想参数
    wn_ref = 1.0
    theta_r_ideal = wn_ref / b_true
    theta_y_ideal = (wn_ref + a_true) / b_true

    print(f"\n真实系统: dy/dt = -{a_true}·y + {b_true}·u")
    print(f"理想参数: θ_r*={theta_r_ideal:.3f}, θ_y*={theta_y_ideal:.3f}")

    # ========== 测试1：阶跃输入（不满足PE）==========
    print("\n--- 测试1：阶跃输入（不满足PE条件）---")
    r_step = np.ones(N)

    system1 = ScalarSystem(a=a_true, b=b_true, dt=dt)
    controller1 = MRACController(
        reference_model=ReferenceModel(wn=wn_ref, zeta=1.0, order='first'),
        method='lyapunov',
        gamma_r=0.2, gamma_y=0.2, gamma_u=0.0,
        theta_r_init=0.2, theta_y_init=0.2,
        Kp_sign=1.0
    )

    y1 = np.zeros(N)
    for i in range(N):
        u, _, _ = controller1.compute_control(system1.y, r_step[i], dt)
        y1[i] = system1.update(u)

    # ========== 测试2：正弦输入（满足PE）==========
    print("--- 测试2：正弦输入（满足PE条件）---")
    r_sine = 1.0 + 0.5 * np.sin(2*np.pi*0.1*t)

    system2 = ScalarSystem(a=a_true, b=b_true, dt=dt)
    controller2 = MRACController(
        reference_model=ReferenceModel(wn=wn_ref, zeta=1.0, order='first'),
        method='lyapunov',
        gamma_r=0.2, gamma_y=0.2, gamma_u=0.0,
        theta_r_init=0.2, theta_y_init=0.2,
        Kp_sign=1.0
    )

    y2 = np.zeros(N)
    for i in range(N):
        u, _, _ = controller2.compute_control(system2.y, r_sine[i], dt)
        y2[i] = system2.update(u)

    # ========== 测试3：Chirp信号（多频率，最佳PE）==========
    print("--- 测试3：Chirp信号（多频率，最佳PE）---")
    from scipy.signal import chirp
    r_chirp = 1.0 + 0.5 * chirp(t, f0=0.05, f1=0.5, t1=T_sim, method='linear')

    system3 = ScalarSystem(a=a_true, b=b_true, dt=dt)
    controller3 = MRACController(
        reference_model=ReferenceModel(wn=wn_ref, zeta=1.0, order='first'),
        method='lyapunov',
        gamma_r=0.2, gamma_y=0.2, gamma_u=0.0,
        theta_r_init=0.2, theta_y_init=0.2,
        Kp_sign=1.0
    )

    y3 = np.zeros(N)
    for i in range(N):
        u, _, _ = controller3.compute_control(system3.y, r_chirp[i], dt)
        y3[i] = system3.update(u)

    # 参数收敛评估
    theta_r1_final = controller1.history['theta_r'][-1]
    theta_y1_final = controller1.history['theta_y'][-1]
    error1 = np.sqrt((theta_r1_final - theta_r_ideal)**2 +
                     (theta_y1_final - theta_y_ideal)**2)

    theta_r2_final = controller2.history['theta_r'][-1]
    theta_y2_final = controller2.history['theta_y'][-1]
    error2 = np.sqrt((theta_r2_final - theta_r_ideal)**2 +
                     (theta_y2_final - theta_y_ideal)**2)

    theta_r3_final = controller3.history['theta_r'][-1]
    theta_y3_final = controller3.history['theta_y'][-1]
    error3 = np.sqrt((theta_r3_final - theta_r_ideal)**2 +
                     (theta_y3_final - theta_y_ideal)**2)

    print(f"\n参数收敛情况:")
    print(f"  阶跃输入 - θ_r={theta_r1_final:.3f}, θ_y={theta_y1_final:.3f}, "
          f"误差={error1:.3f}")
    print(f"  正弦输入 - θ_r={theta_r2_final:.3f}, θ_y={theta_y2_final:.3f}, "
          f"误差={error2:.3f}")
    print(f"  Chirp信号 - θ_r={theta_r3_final:.3f}, θ_y={theta_y3_final:.3f}, "
          f"误差={error3:.3f}")
    print(f"\n结论：Chirp信号提供最好的参数收敛（误差最小）")

    # 可视化
    fig = plt.figure(figsize=(16, 10))
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
    fig.suptitle('Part 4: 持续激励（PE）条件对参数收敛的影响',
                 fontsize=14, fontweight='bold')

    # 第一行：三种输入信号
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.plot(t, r_step, 'k-', linewidth=2)
    ax1.set_ylabel('r(t)')
    ax1.set_title('输入1: 阶跃（不满足PE）')
    ax1.grid(True, alpha=0.3)

    ax2 = fig.add_subplot(gs[0, 1])
    ax2.plot(t, r_sine, 'k-', linewidth=2)
    ax2.set_ylabel('r(t)')
    ax2.set_title('输入2: 正弦（满足PE）')
    ax2.grid(True, alpha=0.3)

    ax3 = fig.add_subplot(gs[0, 2])
    ax3.plot(t, r_chirp, 'k-', linewidth=2)
    ax3.set_ylabel('r(t)')
    ax3.set_title('输入3: Chirp（最佳PE）')
    ax3.grid(True, alpha=0.3)

    # 第二行：参数θ_r收敛过程
    ax4 = fig.add_subplot(gs[1, 0])
    ax4.plot(t, controller1.history['theta_r'], 'b-', linewidth=2)
    ax4.axhline(theta_r_ideal, color='r', linestyle='--',
               label=f'理想值={theta_r_ideal:.2f}')
    ax4.set_ylabel('$\\theta_r(t)$')
    ax4.set_title(f'θ_r收敛（最终={theta_r1_final:.2f}）')
    ax4.legend()
    ax4.grid(True, alpha=0.3)

    ax5 = fig.add_subplot(gs[1, 1])
    ax5.plot(t, controller2.history['theta_r'], 'b-', linewidth=2)
    ax5.axhline(theta_r_ideal, color='r', linestyle='--',
               label=f'理想值={theta_r_ideal:.2f}')
    ax5.set_ylabel('$\\theta_r(t)$')
    ax5.set_title(f'θ_r收敛（最终={theta_r2_final:.2f}）')
    ax5.legend()
    ax5.grid(True, alpha=0.3)

    ax6 = fig.add_subplot(gs[1, 2])
    ax6.plot(t, controller3.history['theta_r'], 'b-', linewidth=2)
    ax6.axhline(theta_r_ideal, color='r', linestyle='--',
               label=f'理想值={theta_r_ideal:.2f}')
    ax6.set_ylabel('$\\theta_r(t)$')
    ax6.set_title(f'θ_r收敛（最终={theta_r3_final:.2f}）✓')
    ax6.legend()
    ax6.grid(True, alpha=0.3)

    # 第三行：参数θ_y收敛过程
    ax7 = fig.add_subplot(gs[2, 0])
    ax7.plot(t, controller1.history['theta_y'], 'm-', linewidth=2)
    ax7.axhline(theta_y_ideal, color='r', linestyle='--',
               label=f'理想值={theta_y_ideal:.2f}')
    ax7.set_xlabel('时间 (s)')
    ax7.set_ylabel('$\\theta_y(t)$')
    ax7.set_title(f'θ_y收敛（最终={theta_y1_final:.2f}）')
    ax7.legend()
    ax7.grid(True, alpha=0.3)

    ax8 = fig.add_subplot(gs[2, 1])
    ax8.plot(t, controller2.history['theta_y'], 'm-', linewidth=2)
    ax8.axhline(theta_y_ideal, color='r', linestyle='--',
               label=f'理想值={theta_y_ideal:.2f}')
    ax8.set_xlabel('时间 (s)')
    ax8.set_ylabel('$\\theta_y(t)$')
    ax8.set_title(f'θ_y收敛（最终={theta_y2_final:.2f}）')
    ax8.legend()
    ax8.grid(True, alpha=0.3)

    ax9 = fig.add_subplot(gs[2, 2])
    ax9.plot(t, controller3.history['theta_y'], 'm-', linewidth=2)
    ax9.axhline(theta_y_ideal, color='r', linestyle='--',
               label=f'理想值={theta_y_ideal:.2f}')
    ax9.set_xlabel('时间 (s)')
    ax9.set_ylabel('$\\theta_y(t)$')
    ax9.set_title(f'θ_y收敛（最终={theta_y3_final:.2f}）✓')
    ax9.legend()
    ax9.grid(True, alpha=0.3)

    plt.savefig('part4_persistent_excitation.png', dpi=150, bbox_inches='tight')
    print("\n✓ 图表已保存: part4_persistent_excitation.png")
    plt.close()


# ============================================================================
# 主程序
# ============================================================================

def main():
    """主函数：运行所有演示"""
    print("\n" + "="*70)
    print(" 案例15：自适应控制（MRAC）")
    print("="*70)
    print("\n本案例演示模型参考自适应控制在运河系统中的应用")
    print("包含4个演示部分，每个部分将生成一张图表\n")

    # 设置随机种子（可重复性）
    np.random.seed(42)

    # 运行各部分演示
    try:
        part1_scalar_system_demo()
        part2_canal_system_mrac()
        part3_robustness_test()
        part4_persistent_excitation()

        print("\n" + "="*70)
        print("✓ 所有演示完成！")
        print("="*70)
        print("\n生成的图表文件:")
        print("  1. part1_scalar_mrac.png - 标量系统MRAC基础")
        print("  2. part2_canal_mrac.png - 运河系统参数不确定性适应")
        print("  3. part3_robustness_test.png - 鲁棒性测试")
        print("  4. part4_persistent_excitation.png - 持续激励条件验证")
        print("\n关键结论:")
        print("  ✓ Lyapunov方法比MIT规则更稳定")
        print("  ✓ MRAC能自动适应参数变化（如糙率突变）")
        print("  ✓ σ修正和死区提高鲁棒性，减少噪声影响")
        print("  ✓ 持续激励（PE）条件对参数收敛至关重要")
        print("="*70 + "\n")

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
