"""
案例16：模糊控制 - 智能控制的经典方法

本程序演示模糊控制在水箱液位控制中的应用，包括：
1. 模糊逻辑基础（隶属函数、模糊推理）
2. 模糊PD控制器设计
3. 模糊PID控制器
4. 与传统PID的性能对比
5. 控制曲面可视化
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import numpy as np
import matplotlib
matplotlib.use('Agg')  # 必须在import pyplot之前设置
import matplotlib.pyplot as plt
from matplotlib import rcParams

# 设置中文显示
rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

# ============================================================================
# 隶属函数定义
# ============================================================================

def trimf(x, params):
    """三角形隶属函数

    Args:
        x: 输入值（可以是标量或数组）
        params: [a, b, c]，其中 a < b < c

    Returns:
        隶属度值
    """
    a, b, c = params
    if isinstance(x, np.ndarray):
        y = np.zeros_like(x, dtype=float)
        # 左侧上升
        mask1 = (x >= a) & (x <= b)
        y[mask1] = (x[mask1] - a) / (b - a) if b != a else 0
        # 右侧下降
        mask2 = (x > b) & (x <= c)
        y[mask2] = (c - x[mask2]) / (c - b) if c != b else 0
        # 峰值
        y[x == b] = 1.0
        return y
    else:
        if x <= a or x >= c:
            return 0.0
        elif a < x <= b:
            return (x - a) / (b - a) if b != a else 0.0
        elif b < x < c:
            return (c - x) / (c - b) if c != b else 0.0
        else:
            return 1.0

def trapmf(x, params):
    """梯形隶属函数

    Args:
        x: 输入值
        params: [a, b, c, d]，其中 a < b < c < d

    Returns:
        隶属度值
    """
    a, b, c, d = params
    if isinstance(x, np.ndarray):
        y = np.zeros_like(x, dtype=float)
        # 左侧上升
        mask1 = (x >= a) & (x < b)
        y[mask1] = (x[mask1] - a) / (b - a) if b != a else 0
        # 平顶
        mask2 = (x >= b) & (x <= c)
        y[mask2] = 1.0
        # 右侧下降
        mask3 = (x > c) & (x <= d)
        y[mask3] = (d - x[mask3]) / (d - c) if d != c else 0
        return y
    else:
        if x <= a or x >= d:
            return 0.0
        elif a < x < b:
            return (x - a) / (b - a) if b != a else 0.0
        elif b <= x <= c:
            return 1.0
        elif c < x < d:
            return (d - x) / (d - c) if d != c else 0.0

# ============================================================================
# 模糊控制器类
# ============================================================================

class FuzzyController:
    """模糊控制器基类"""

    def __init__(self, e_range=(-2, 2), de_range=(-1, 1), du_range=(-5, 5)):
        """初始化模糊控制器

        Args:
            e_range: 误差论域范围
            de_range: 误差变化率论域范围
            du_range: 控制增量论域范围
        """
        self.e_range = e_range
        self.de_range = de_range
        self.du_range = du_range

        # 定义模糊集合的标签
        self.labels = ['NB', 'NM', 'NS', 'ZE', 'PS', 'PM', 'PB']

        # 初始化隶属函数
        self._init_membership_functions()

        # 初始化规则库
        self._init_rule_base()

    def _init_membership_functions(self):
        """初始化隶属函数参数"""
        # 误差e的隶属函数（7个三角形）
        e_min, e_max = self.e_range
        e_range_val = e_max - e_min
        self.e_mf = {
            'NB': [e_min, e_min, e_min + e_range_val/6],
            'NM': [e_min, e_min + e_range_val/6, e_min + 2*e_range_val/6],
            'NS': [e_min + e_range_val/6, e_min + 2*e_range_val/6, e_min + 3*e_range_val/6],
            'ZE': [e_min + 2*e_range_val/6, e_min + 3*e_range_val/6, e_min + 4*e_range_val/6],
            'PS': [e_min + 3*e_range_val/6, e_min + 4*e_range_val/6, e_min + 5*e_range_val/6],
            'PM': [e_min + 4*e_range_val/6, e_min + 5*e_range_val/6, e_max],
            'PB': [e_min + 5*e_range_val/6, e_max, e_max]
        }

        # 误差变化率Δe的隶属函数
        de_min, de_max = self.de_range
        de_range_val = de_max - de_min
        self.de_mf = {
            'NB': [de_min, de_min, de_min + de_range_val/6],
            'NM': [de_min, de_min + de_range_val/6, de_min + 2*de_range_val/6],
            'NS': [de_min + de_range_val/6, de_min + 2*de_range_val/6, de_min + 3*de_range_val/6],
            'ZE': [de_min + 2*de_range_val/6, de_min + 3*de_range_val/6, de_min + 4*de_range_val/6],
            'PS': [de_min + 3*de_range_val/6, de_min + 4*de_range_val/6, de_min + 5*de_range_val/6],
            'PM': [de_min + 4*de_range_val/6, de_min + 5*de_range_val/6, de_max],
            'PB': [de_min + 5*de_range_val/6, de_max, de_max]
        }

        # 控制增量Δu的隶属函数
        du_min, du_max = self.du_range
        du_range_val = du_max - du_min
        self.du_mf = {
            'NB': [du_min, du_min, du_min + du_range_val/6],
            'NM': [du_min, du_min + du_range_val/6, du_min + 2*du_range_val/6],
            'NS': [du_min + du_range_val/6, du_min + 2*du_range_val/6, du_min + 3*du_range_val/6],
            'ZE': [du_min + 2*du_range_val/6, du_min + 3*du_range_val/6, du_min + 4*du_range_val/6],
            'PS': [du_min + 3*du_range_val/6, du_min + 4*du_range_val/6, du_min + 5*du_range_val/6],
            'PM': [du_min + 4*du_range_val/6, du_min + 5*du_range_val/6, du_max],
            'PB': [du_min + 5*du_range_val/6, du_max, du_max]
        }

    def _init_rule_base(self):
        """初始化模糊规则库（7×7）

        规则格式：IF e is X AND de is Y THEN du is Z
        """
        # 规则表：行为e，列为de
        # 修正后的规则：e>0时(actual<target)应增大控制，e<0时(actual>target)应减小控制
        self.rule_base = [
            # de: NB    NM    NS    ZE    PS    PM    PB
            ['NB', 'NB', 'NM', 'NM', 'NS', 'ZE', 'ZE'],  # e = NB (actual > target, 应减小u)
            ['NB', 'NM', 'NM', 'NS', 'NS', 'ZE', 'PS'],  # e = NM
            ['NM', 'NM', 'NS', 'NS', 'ZE', 'PS', 'PM'],  # e = NS
            ['NM', 'NS', 'NS', 'ZE', 'PS', 'PS', 'PM'],  # e = ZE
            ['NS', 'NS', 'ZE', 'PS', 'PS', 'PM', 'PM'],  # e = PS
            ['NS', 'ZE', 'PS', 'PM', 'PM', 'PM', 'PB'],  # e = PM
            ['ZE', 'ZE', 'PM', 'PM', 'PM', 'PB', 'PB']   # e = PB (actual < target, 应增大u)
        ]

    def fuzzify(self, value, mf_dict):
        """模糊化：计算输入值在各模糊集的隶属度

        Args:
            value: 输入值
            mf_dict: 隶属函数字典

        Returns:
            字典，键为标签，值为隶属度
        """
        memberships = {}
        for label in self.labels:
            memberships[label] = trimf(value, mf_dict[label])
        return memberships

    def inference(self, e_memberships, de_memberships):
        """模糊推理：根据规则库计算输出模糊集

        Args:
            e_memberships: 误差的隶属度
            de_memberships: 误差变化率的隶属度

        Returns:
            输出的隶属度字典
        """
        # 初始化输出隶属度
        du_memberships = {label: 0.0 for label in self.labels}

        # 遍历所有规则
        for i, e_label in enumerate(self.labels):
            for j, de_label in enumerate(self.labels):
                # 规则激活度（使用最小值运算）
                activation = min(e_memberships[e_label], de_memberships[de_label])

                # 输出标签
                du_label = self.rule_base[i][j]

                # 聚合（使用最大值运算）
                du_memberships[du_label] = max(du_memberships[du_label], activation)

        return du_memberships

    def defuzzify(self, memberships, mf_dict):
        """去模糊化：使用重心法计算精确输出值

        Args:
            memberships: 隶属度字典
            mf_dict: 隶属函数字典

        Returns:
            精确输出值
        """
        # 定义论域的采样点
        du_min, du_max = self.du_range
        u_points = np.linspace(du_min, du_max, 201)

        # 计算每个点的总隶属度
        mu_total = np.zeros_like(u_points)
        for label in self.labels:
            mu = trimf(u_points, mf_dict[label])
            mu_total = np.maximum(mu_total, memberships[label] * mu)

        # 重心法
        if np.sum(mu_total) == 0:
            return 0.0
        else:
            return np.sum(u_points * mu_total) / np.sum(mu_total)

    def compute(self, e, de):
        """计算模糊控制器输出

        Args:
            e: 误差
            de: 误差变化率

        Returns:
            控制增量
        """
        # 限制输入范围
        e = np.clip(e, self.e_range[0], self.e_range[1])
        de = np.clip(de, self.de_range[0], self.de_range[1])

        # 模糊化
        e_memberships = self.fuzzify(e, self.e_mf)
        de_memberships = self.fuzzify(de, self.de_mf)

        # 推理
        du_memberships = self.inference(e_memberships, de_memberships)

        # 去模糊化
        du = self.defuzzify(du_memberships, self.du_mf)

        return du

# ============================================================================
# 水箱系统仿真
# ============================================================================

def water_tank_dynamics(h, u, A=3.0, R=2.0, dt=0.1):
    """水箱动力学模型

    Args:
        h: 当前液位
        u: 输入流量
        A: 水箱横截面积
        R: 出口阻力
        dt: 时间步长

    Returns:
        下一时刻液位
    """
    # dh/dt = (u - h/R) / A
    dhdt = (u - h / R) / A
    h_next = h + dhdt * dt
    return max(0, h_next)  # 液位不能为负

def traditional_pid(e, e_prev, e_integral, Kp, Ki, Kd, dt):
    """传统PID控制器

    Args:
        e: 当前误差
        e_prev: 前一时刻误差
        e_integral: 误差积分
        Kp, Ki, Kd: PID参数
        dt: 时间步长

    Returns:
        控制量, 新的误差积分
    """
    # 比例项
    P = Kp * e

    # 积分项
    e_integral += e * dt
    I = Ki * e_integral

    # 微分项
    D = Kd * (e - e_prev) / dt

    # 总控制量
    u = P + I + D

    return u, e_integral

# ============================================================================
# 第1部分：模糊逻辑基础演示
# ============================================================================

def part1_fuzzy_basics():
    """演示隶属函数和模糊化过程"""
    print("=" * 80)
    print("第1部分：模糊逻辑基础")
    print("=" * 80)

    # 创建模糊控制器
    fuzzy = FuzzyController()

    # 绘制隶属函数
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))

    # 误差e的隶属函数
    e_vals = np.linspace(fuzzy.e_range[0], fuzzy.e_range[1], 300)
    for label in fuzzy.labels:
        mu = trimf(e_vals, fuzzy.e_mf[label])
        axes[0].plot(e_vals, mu, label=label, linewidth=2)
    axes[0].set_xlabel('误差 e (m)')
    axes[0].set_ylabel('隶属度 μ')
    axes[0].set_title('误差e的隶属函数')
    axes[0].legend(ncol=7, loc='upper right')
    axes[0].grid(True, alpha=0.3)

    # 误差变化率Δe的隶属函数
    de_vals = np.linspace(fuzzy.de_range[0], fuzzy.de_range[1], 300)
    for label in fuzzy.labels:
        mu = trimf(de_vals, fuzzy.de_mf[label])
        axes[1].plot(de_vals, mu, label=label, linewidth=2)
    axes[1].set_xlabel('误差变化率 Δe (m/min)')
    axes[1].set_ylabel('隶属度 μ')
    axes[1].set_title('误差变化率Δe的隶属函数')
    axes[1].legend(ncol=7, loc='upper right')
    axes[1].grid(True, alpha=0.3)

    # 控制增量Δu的隶属函数
    du_vals = np.linspace(fuzzy.du_range[0], fuzzy.du_range[1], 300)
    for label in fuzzy.labels:
        mu = trimf(du_vals, fuzzy.du_mf[label])
        axes[2].plot(du_vals, mu, label=label, linewidth=2)
    axes[2].set_xlabel('控制增量 Δu (m³/min)')
    axes[2].set_ylabel('隶属度 μ')
    axes[2].set_title('控制增量Δu的隶属函数')
    axes[2].legend(ncol=7, loc='upper right')
    axes[2].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('case16_membership_functions.png', dpi=150, bbox_inches='tight')
    plt.close()

    # 模糊化示例
    print("\n[模糊化示例]")
    e_test = 0.3
    de_test = -0.2
    e_memberships = fuzzy.fuzzify(e_test, fuzzy.e_mf)
    de_memberships = fuzzy.fuzzify(de_test, fuzzy.de_mf)

    print(f"  输入：e = {e_test}, Δe = {de_test}")
    print(f"\n  e的隶属度：")
    for label, mu in e_memberships.items():
        if mu > 0.01:
            print(f"    {label}: {mu:.3f}")
    print(f"\n  Δe的隶属度：")
    for label, mu in de_memberships.items():
        if mu > 0.01:
            print(f"    {label}: {mu:.3f}")

    # 推理示例
    du_memberships = fuzzy.inference(e_memberships, de_memberships)
    print(f"\n  推理后Δu的隶属度：")
    for label, mu in du_memberships.items():
        if mu > 0.01:
            print(f"    {label}: {mu:.3f}")

    # 去模糊化
    du = fuzzy.defuzzify(du_memberships, fuzzy.du_mf)
    print(f"\n  去模糊化后的输出：Δu = {du:.3f} m³/min")

    print("\n图表已保存：case16_membership_functions.png\n")

# ============================================================================
# 第2部分：模糊PD控制器
# ============================================================================

def part2_fuzzy_pd():
    """演示模糊PD控制器"""
    print("=" * 80)
    print("第2部分：模糊PD控制器")
    print("=" * 80)

    # 系统参数
    A = 3.0  # 水箱横截面积
    R = 2.0  # 出口阻力
    dt = 0.1  # 时间步长
    t_total = 30  # 总仿真时间

    # 创建模糊控制器
    fuzzy = FuzzyController(e_range=(-2, 2), de_range=(-1, 1), du_range=(-5, 5))

    # 初始化
    N = int(t_total / dt)
    t = np.linspace(0, t_total, N)
    r = 2.0 * np.ones(N)  # 目标液位
    h = np.zeros(N)
    u = np.zeros(N)
    e = np.zeros(N)
    de = np.zeros(N)

    h[0] = 0.5  # 初始液位
    u[0] = 1.0  # 初始控制量

    # 模糊PD控制仿真
    for i in range(1, N):
        # 计算误差
        e[i] = r[i] - h[i-1]
        de[i] = (e[i] - e[i-1]) / dt if i > 0 else 0

        # 模糊控制器
        du = fuzzy.compute(e[i], de[i])

        # 更新控制量
        u[i] = u[i-1] + du
        u[i] = np.clip(u[i], 0, 10)  # 限幅

        # 系统动态
        h[i] = water_tank_dynamics(h[i-1], u[i], A, R, dt)

    # 性能指标
    settling_time_idx = np.where(np.abs(e) < 0.05)[0]
    if len(settling_time_idx) > 0:
        settling_time = t[settling_time_idx[0]]
    else:
        settling_time = t_total

    overshoot = np.max(h - r) if np.max(h) > r[0] else 0
    steady_error = np.abs(h[-1] - r[-1])

    print(f"\n[模糊PD控制性能]")
    print(f"  调节时间：{settling_time:.2f} min")
    print(f"  超调量：{overshoot:.4f} m")
    print(f"  稳态误差：{steady_error:.4f} m")

    # 绘图
    fig, axes = plt.subplots(3, 1, figsize=(12, 9))

    axes[0].plot(t, h, 'b-', label='实际液位', linewidth=2)
    axes[0].plot(t, r, 'r--', label='目标液位', linewidth=2)
    axes[0].set_ylabel('液位 (m)')
    axes[0].set_title('模糊PD控制 - 液位跟踪')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(t, u, 'g-', linewidth=2)
    axes[1].set_ylabel('控制量 (m³/min)')
    axes[1].set_title('控制输入')
    axes[1].grid(True, alpha=0.3)

    axes[2].plot(t, e, 'm-', linewidth=2)
    axes[2].set_xlabel('时间 (min)')
    axes[2].set_ylabel('误差 (m)')
    axes[2].set_title('跟踪误差')
    axes[2].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('case16_fuzzy_pd.png', dpi=150, bbox_inches='tight')
    plt.close()

    print("\n图表已保存：case16_fuzzy_pd.png\n")

    return fuzzy

# ============================================================================
# 第3部分：控制曲面可视化
# ============================================================================

def part3_control_surface(fuzzy):
    """可视化模糊控制器的控制曲面"""
    print("=" * 80)
    print("第3部分：控制曲面可视化")
    print("=" * 80)

    # 创建网格
    e_vals = np.linspace(fuzzy.e_range[0], fuzzy.e_range[1], 50)
    de_vals = np.linspace(fuzzy.de_range[0], fuzzy.de_range[1], 50)
    E, DE = np.meshgrid(e_vals, de_vals)

    # 计算控制曲面
    DU = np.zeros_like(E)
    for i in range(E.shape[0]):
        for j in range(E.shape[1]):
            DU[i, j] = fuzzy.compute(E[i, j], DE[i, j])

    # 绘制3D曲面
    fig = plt.figure(figsize=(14, 6))

    # 3D曲面图
    ax1 = fig.add_subplot(121, projection='3d')
    surf = ax1.plot_surface(E, DE, DU, cmap='viridis', alpha=0.9)
    ax1.set_xlabel('误差 e (m)')
    ax1.set_ylabel('误差变化率 Δe (m/min)')
    ax1.set_zlabel('控制增量 Δu (m³/min)')
    # 标题已移除，保持图表简洁
    fig.colorbar(surf, ax=ax1, shrink=0.5)

    # 2D等高线图
    ax2 = fig.add_subplot(122)
    contour = ax2.contourf(E, DE, DU, levels=20, cmap='viridis')
    ax2.set_xlabel('误差 e (m)')
    ax2.set_ylabel('误差变化率 Δe (m/min)')
    # 标题已移除，保持图表简洁
    fig.colorbar(contour, ax=ax2)

    plt.tight_layout()
    plt.savefig('case16_control_surface.png', dpi=150, bbox_inches='tight')
    plt.close()

    print("\n[控制曲面特性]")
    print("  - 误差大且增大时：控制增量大（快速响应）")
    print("  - 误差小且减小时：控制增量小（精细调节）")
    print("  - 曲面平滑：避免控制抖动")
    print("  - 非线性特性：优于线性PID")

    print("\n图表已保存：case16_control_surface.png\n")

# ============================================================================
# 第4部分：模糊控制 vs 传统PID
# ============================================================================

def part4_fuzzy_vs_pid():
    """对比模糊控制和传统PID"""
    print("=" * 80)
    print("第4部分：模糊控制 vs 传统PID")
    print("=" * 80)

    # 系统参数
    A = 3.0
    R = 2.0
    dt = 0.1
    t_total = 30
    N = int(t_total / dt)
    t = np.linspace(0, t_total, N)

    # 目标液位（阶跃+扰动）
    r = np.ones(N) * 2.0
    r[N//3:2*N//3] = 2.5  # 中间时段目标变化

    # ---- 模糊控制 ----
    fuzzy = FuzzyController(e_range=(-2, 2), de_range=(-1, 1), du_range=(-5, 5))
    h_fuzzy = np.zeros(N)
    u_fuzzy = np.zeros(N)
    e_fuzzy = np.zeros(N)
    de_fuzzy = np.zeros(N)
    h_fuzzy[0] = 0.5
    u_fuzzy[0] = 1.0

    for i in range(1, N):
        e_fuzzy[i] = r[i] - h_fuzzy[i-1]
        de_fuzzy[i] = (e_fuzzy[i] - e_fuzzy[i-1]) / dt
        du = fuzzy.compute(e_fuzzy[i], de_fuzzy[i])
        u_fuzzy[i] = np.clip(u_fuzzy[i-1] + du, 0, 10)
        h_fuzzy[i] = water_tank_dynamics(h_fuzzy[i-1], u_fuzzy[i], A, R, dt)

    # ---- 传统PID ----
    Kp, Ki, Kd = 3.0, 0.5, 1.0
    h_pid = np.zeros(N)
    u_pid = np.zeros(N)
    e_pid = np.zeros(N)
    e_integral_pid = 0
    e_prev_pid = 0
    h_pid[0] = 0.5

    for i in range(1, N):
        e_pid[i] = r[i] - h_pid[i-1]
        u_pid[i], e_integral_pid = traditional_pid(e_pid[i], e_prev_pid, e_integral_pid, Kp, Ki, Kd, dt)
        u_pid[i] = np.clip(u_pid[i], 0, 10)
        h_pid[i] = water_tank_dynamics(h_pid[i-1], u_pid[i], A, R, dt)
        e_prev_pid = e_pid[i]

    # 性能指标
    mae_fuzzy = np.mean(np.abs(e_fuzzy))
    mae_pid = np.mean(np.abs(e_pid))
    rmse_fuzzy = np.sqrt(np.mean(e_fuzzy**2))
    rmse_pid = np.sqrt(np.mean(e_pid**2))

    print(f"\n[性能对比]")
    print(f"  模糊控制：")
    print(f"    平均绝对误差（MAE）: {mae_fuzzy:.4f} m")
    print(f"    均方根误差（RMSE）: {rmse_fuzzy:.4f} m")
    print(f"\n  传统PID：")
    print(f"    平均绝对误差（MAE）: {mae_pid:.4f} m")
    print(f"    均方根误差（RMSE）: {rmse_pid:.4f} m")
    print(f"\n  改进：")
    print(f"    MAE改进: {(mae_pid - mae_fuzzy) / mae_pid * 100:.1f}%")
    print(f"    RMSE改进: {(rmse_pid - rmse_fuzzy) / rmse_pid * 100:.1f}%")

    # 绘图
    fig, axes = plt.subplots(3, 1, figsize=(14, 10))

    axes[0].plot(t, h_fuzzy, 'b-', label='模糊控制', linewidth=2)
    axes[0].plot(t, h_pid, 'r--', label='传统PID', linewidth=2)
    axes[0].plot(t, r, 'k:', label='目标液位', linewidth=2)
    axes[0].set_ylabel('液位 (m)')
    axes[0].set_title('模糊控制 vs 传统PID - 液位跟踪')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(t, u_fuzzy, 'b-', label='模糊控制', linewidth=2)
    axes[1].plot(t, u_pid, 'r--', label='传统PID', linewidth=2)
    axes[1].set_ylabel('控制量 (m³/min)')
    axes[1].set_title('控制输入对比')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    axes[2].plot(t, e_fuzzy, 'b-', label='模糊控制', linewidth=2)
    axes[2].plot(t, e_pid, 'r--', label='传统PID', linewidth=2)
    axes[2].set_xlabel('时间 (min)')
    axes[2].set_ylabel('误差 (m)')
    axes[2].set_title('跟踪误差对比')
    axes[2].legend()
    axes[2].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('case16_fuzzy_vs_pid.png', dpi=150, bbox_inches='tight')
    plt.close()

    print("\n图表已保存：case16_fuzzy_vs_pid.png\n")

# ============================================================================
# 第5部分：总结
# ============================================================================

def part5_summary():
    """总结模糊控制的关键点"""
    print("=" * 80)
    print("第5部分：案例16总结")
    print("=" * 80)

    summary_text = """
[关键知识点]
  1. 模糊逻辑基础：
     • 隶属函数：描述"属于某集合的程度"
     • 三角形/梯形/高斯函数
     • 论域与模糊集划分

  2. 模糊控制器结构：
     • 模糊化：精确值 → 隶属度
     • 推理：规则匹配与激活
     • 去模糊化：隶属度 → 精确值

  3. 规则库设计：
     • IF-THEN规则表达专家经验
     • 7×7规则常用且有效
     • 误差大 → 控制强，误差小 → 控制弱

  4. 模糊vs传统PID：
     • 模糊：非线性、鲁棒、无需精确模型
     • PID：线性、简单、需要调参
     • 模糊适合复杂非线性系统

[工程应用]
  • 家电：洗衣机、空调、电饭煲
  • 汽车：自动变速箱、ABS
  • 工业：窑炉、锅炉控制
  • 适用于难以建模的系统

[实用建议]
  • 从简单规则库（5×5）开始
  • 观察控制曲面是否合理
  • 调整隶属函数覆盖范围
  • 结合仿真逐步优化

[扩展方向]
  • 自适应模糊控制
  • 神经模糊系统（ANFIS）
  • 类型二模糊系统
  • 与其他智能方法结合

[下一步学习]
  → 案例17：神经网络控制
  → 案例18：强化学习控制
"""
    print(summary_text)

    print("=" * 80)
    print("案例16演示完成！")
    print("=" * 80)

# ============================================================================
# 主程序
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("案例16：模糊控制 - 智能控制的经典方法")
    print("=" * 80)

    # 第1部分：模糊逻辑基础
    part1_fuzzy_basics()

    # 第2部分：模糊PD控制
    fuzzy = part2_fuzzy_pd()

    # 第3部分：控制曲面
    part3_control_surface(fuzzy)

    # 第4部分：模糊 vs PID
    part4_fuzzy_vs_pid()

    # 第5部分：总结
    part5_summary()
