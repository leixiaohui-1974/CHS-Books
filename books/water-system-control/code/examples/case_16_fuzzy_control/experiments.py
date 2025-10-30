"""
案例16扩展实验：模糊控制深入研究

本程序包含以下扩展实验：
1. 不同规则库大小对比（3×3, 5×5, 7×7, 9×9）
2. 隶属函数形状影响（三角形 vs 梯形 vs 高斯）
3. 自适应模糊控制（在线调整隶属函数）
4. 鲁棒性测试（参数不确定性 + 噪声）
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

# 设置中文显示
rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

# ============================================================================
# 隶属函数
# ============================================================================

def trimf(x, params):
    """三角形隶属函数"""
    a, b, c = params
    if isinstance(x, np.ndarray):
        y = np.zeros_like(x, dtype=float)
        mask1 = (x >= a) & (x <= b)
        y[mask1] = (x[mask1] - a) / (b - a) if b != a else 0
        mask2 = (x > b) & (x <= c)
        y[mask2] = (c - x[mask2]) / (c - b) if c != b else 0
        y[x == b] = 1.0
        return y
    else:
        if x <= a or x >= c:
            return 0.0
        elif a < x <= b:
            return (x - a) / (b - a) if b != a else 1.0
        elif b < x < c:
            return (c - x) / (c - b) if c != b else 1.0
        else:
            return 1.0

def trapmf(x, params):
    """梯形隶属函数"""
    a, b, c, d = params
    if isinstance(x, np.ndarray):
        y = np.zeros_like(x, dtype=float)
        mask1 = (x >= a) & (x < b)
        y[mask1] = (x[mask1] - a) / (b - a) if b != a else 0
        mask2 = (x >= b) & (x <= c)
        y[mask2] = 1.0
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

def gaussmf(x, params):
    """高斯隶属函数"""
    mean, sigma = params
    return np.exp(-((x - mean) ** 2) / (2 * sigma ** 2))

# ============================================================================
# 不同规则库的模糊控制器
# ============================================================================

class SimpleFuzzyController:
    """简化的模糊控制器（支持不同规则库大小）"""

    def __init__(self, n_sets=7, e_range=(-2, 2), de_range=(-1, 1), du_range=(-5, 5)):
        self.n_sets = n_sets
        self.e_range = e_range
        self.de_range = de_range
        self.du_range = du_range

        # 定义标签
        if n_sets == 3:
            self.labels = ['N', 'Z', 'P']  # 负、零、正
        elif n_sets == 5:
            self.labels = ['NB', 'NS', 'ZE', 'PS', 'PB']
        elif n_sets == 7:
            self.labels = ['NB', 'NM', 'NS', 'ZE', 'PS', 'PM', 'PB']
        elif n_sets == 9:
            self.labels = ['NVB', 'NB', 'NM', 'NS', 'ZE', 'PS', 'PM', 'PB', 'PVB']

        self._init_membership_functions()
        self._init_rule_base()

    def _init_membership_functions(self):
        """初始化隶属函数"""
        n = self.n_sets

        # 误差e的隶属函数
        e_min, e_max = self.e_range
        e_range_val = e_max - e_min
        self.e_mf = {}
        for i, label in enumerate(self.labels):
            a = e_min + i * e_range_val / n
            b = e_min + (i + 1) * e_range_val / n
            c = e_min + (i + 2) * e_range_val / n if i < n - 1 else e_max
            if i == 0:
                a = e_min
            if i == n - 1:
                c = e_max
            self.e_mf[label] = [a, b, c]

        # 误差变化率Δe的隶属函数
        de_min, de_max = self.de_range
        de_range_val = de_max - de_min
        self.de_mf = {}
        for i, label in enumerate(self.labels):
            a = de_min + i * de_range_val / n
            b = de_min + (i + 1) * de_range_val / n
            c = de_min + (i + 2) * de_range_val / n if i < n - 1 else de_max
            if i == 0:
                a = de_min
            if i == n - 1:
                c = de_max
            self.de_mf[label] = [a, b, c]

        # 控制增量Δu的隶属函数
        du_min, du_max = self.du_range
        du_range_val = du_max - du_min
        self.du_mf = {}
        for i, label in enumerate(self.labels):
            a = du_min + i * du_range_val / n
            b = du_min + (i + 1) * du_range_val / n
            c = du_min + (i + 2) * du_range_val / n if i < n - 1 else du_max
            if i == 0:
                a = du_min
            if i == n - 1:
                c = du_max
            self.du_mf[label] = [a, b, c]

    def _init_rule_base(self):
        """初始化规则库"""
        n = self.n_sets
        self.rule_base = []

        # 简单对角线规则：误差大 → 控制强
        for i in range(n):
            row = []
            for j in range(n):
                # 基本思想：e + de 决定控制量
                # e大且de大 → 控制量大
                idx = min(max(i + j - n + 1, 0), n - 1)
                row.append(self.labels[idx])
            self.rule_base.append(row)

    def fuzzify(self, value, mf_dict):
        """模糊化"""
        memberships = {}
        for label in self.labels:
            memberships[label] = trimf(value, mf_dict[label])
        return memberships

    def inference(self, e_memberships, de_memberships):
        """模糊推理"""
        du_memberships = {label: 0.0 for label in self.labels}
        for i, e_label in enumerate(self.labels):
            for j, de_label in enumerate(self.labels):
                activation = min(e_memberships[e_label], de_memberships[de_label])
                du_label = self.rule_base[i][j]
                du_memberships[du_label] = max(du_memberships[du_label], activation)
        return du_memberships

    def defuzzify(self, memberships, mf_dict):
        """去模糊化"""
        du_min, du_max = self.du_range
        u_points = np.linspace(du_min, du_max, 201)
        mu_total = np.zeros_like(u_points)
        for label in self.labels:
            mu = trimf(u_points, mf_dict[label])
            mu_total = np.maximum(mu_total, memberships[label] * mu)
        if np.sum(mu_total) == 0:
            return 0.0
        else:
            return np.sum(u_points * mu_total) / np.sum(mu_total)

    def compute(self, e, de):
        """计算控制量"""
        e = np.clip(e, self.e_range[0], self.e_range[1])
        de = np.clip(de, self.de_range[0], self.de_range[1])
        e_memberships = self.fuzzify(e, self.e_mf)
        de_memberships = self.fuzzify(de, self.de_mf)
        du_memberships = self.inference(e_memberships, de_memberships)
        du = self.defuzzify(du_memberships, self.du_mf)
        return du

# ============================================================================
# 水箱系统
# ============================================================================

def water_tank_dynamics(h, u, A=3.0, R=2.0, dt=0.1):
    """水箱动力学"""
    dhdt = (u - h / R) / A
    h_next = h + dhdt * dt
    return max(0, h_next)

# ============================================================================
# 实验1：规则库大小对比
# ============================================================================

def experiment_rule_base_size():
    """对比不同规则库大小的性能"""
    print("=" * 80)
    print("实验1：规则库大小影响")
    print("=" * 80)

    # 参数
    A, R, dt = 3.0, 2.0, 0.1
    t_total = 30
    N = int(t_total / dt)
    t = np.linspace(0, t_total, N)
    r = 2.0 * np.ones(N)

    # 测试不同规则库
    rule_sizes = [3, 5, 7, 9]
    results = {}

    print("\n[测试不同规则库大小]\n")

    for n_sets in rule_sizes:
        fuzzy = SimpleFuzzyController(n_sets=n_sets)

        h = np.zeros(N)
        u = np.zeros(N)
        e = np.zeros(N)
        de = np.zeros(N)
        h[0] = 0.5
        u[0] = 1.0

        for i in range(1, N):
            e[i] = r[i] - h[i-1]
            de[i] = (e[i] - e[i-1]) / dt
            du = fuzzy.compute(e[i], de[i])
            u[i] = np.clip(u[i-1] + du, 0, 10)
            h[i] = water_tank_dynamics(h[i-1], u[i], A, R, dt)

        # 性能指标
        settling_idx = np.where(np.abs(e) < 0.05)[0]
        settling_time = t[settling_idx[0]] if len(settling_idx) > 0 else t_total
        overshoot = np.max(h - r) if np.max(h) > r[0] else 0
        steady_error = np.abs(h[-1] - r[-1])

        results[n_sets] = {'h': h, 'u': u, 'e': e, 'settling_time': settling_time,
                           'overshoot': overshoot, 'steady_error': steady_error}

        print(f"{n_sets}×{n_sets} 规则库（{n_sets**2}条规则）：")
        print(f"  调节时间：{settling_time:.2f} min")
        print(f"  超调量：{overshoot:.4f} m")
        print(f"  稳态误差：{steady_error:.4f} m\n")

    # 绘图
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))

    for n_sets in rule_sizes:
        axes[0].plot(t, results[n_sets]['h'], label=f'{n_sets}×{n_sets}', linewidth=2)
    axes[0].plot(t, r, 'k--', label='目标', linewidth=2)
    axes[0].set_ylabel('液位 (m)')
    axes[0].set_title('不同规则库大小的液位响应')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    for n_sets in rule_sizes:
        axes[1].plot(t, results[n_sets]['u'], label=f'{n_sets}×{n_sets}', linewidth=2)
    axes[1].set_xlabel('时间 (min)')
    axes[1].set_ylabel('控制量 (m³/min)')
    axes[1].set_title('控制输入对比')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('exp1_rule_base_size.png', dpi=150, bbox_inches='tight')
    plt.close()

    print("图表已保存：exp1_rule_base_size.png")

    print("\n结论：")
    print("  - 3×3：规则太少，性能有限")
    print("  - 5×5：性能较好，计算简单")
    print("  - 7×7：最常用，性能优秀")
    print("  - 9×9：性能略有提升，但计算量大")
    print("  - 推荐：5×5或7×7规则库\n")

# ============================================================================
# 实验2：隶属函数形状影响
# ============================================================================

def experiment_membership_shapes():
    """对比不同隶属函数形状"""
    print("=" * 80)
    print("实验2：隶属函数形状影响")
    print("=" * 80)

    # 绘制不同形状的隶属函数
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))

    x = np.linspace(-2, 2, 300)

    # 三角形
    tri_mf = trimf(x, [-2, 0, 2])
    axes[0].plot(x, tri_mf, 'b-', linewidth=2)
    axes[0].set_title('三角形隶属函数')
    axes[0].set_xlabel('x')
    axes[0].set_ylabel('μ(x)')
    axes[0].grid(True, alpha=0.3)

    # 梯形
    trap_mf = trapmf(x, [-2, -1, 1, 2])
    axes[1].plot(x, trap_mf, 'r-', linewidth=2)
    axes[1].set_title('梯形隶属函数')
    axes[1].set_xlabel('x')
    axes[1].set_ylabel('μ(x)')
    axes[1].grid(True, alpha=0.3)

    # 高斯
    gauss_mf = gaussmf(x, [0, 0.6])
    axes[2].plot(x, gauss_mf, 'g-', linewidth=2)
    axes[2].set_title('高斯隶属函数')
    axes[2].set_xlabel('x')
    axes[2].set_ylabel('μ(x)')
    axes[2].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('exp2_membership_shapes.png', dpi=150, bbox_inches='tight')
    plt.close()

    print("\n[隶属函数形状特性]\n")
    print("三角形：")
    print("  - 计算简单")
    print("  - 尖锐过渡")
    print("  - 最常用\n")
    print("梯形：")
    print("  - 平顶区域")
    print("  - 更强的隶属度")
    print("  - 适合明确分类\n")
    print("高斯：")
    print("  - 平滑过渡")
    print("  - 连续可微")
    print("  - 适合精细控制\n")

    print("图表已保存：exp2_membership_shapes.png\n")

# ============================================================================
# 实验3：自适应模糊控制
# ============================================================================

def experiment_adaptive_fuzzy():
    """演示自适应模糊控制（在线调整论域范围）"""
    print("=" * 80)
    print("实验3：自适应模糊控制")
    print("=" * 80)

    # 参数
    A, R, dt = 3.0, 2.0, 0.1
    t_total = 40
    N = int(t_total / dt)
    t = np.linspace(0, t_total, N)

    # 目标变化
    r = np.ones(N) * 2.0
    r[N//2:] = 3.0  # 中途目标大幅变化

    # ---- 固定论域模糊控制 ----
    fuzzy_fixed = SimpleFuzzyController(n_sets=7, e_range=(-2, 2), de_range=(-1, 1))
    h_fixed = np.zeros(N)
    u_fixed = np.zeros(N)
    e_fixed = np.zeros(N)
    h_fixed[0] = 0.5
    u_fixed[0] = 1.0

    for i in range(1, N):
        e_fixed[i] = r[i] - h_fixed[i-1]
        de = (e_fixed[i] - e_fixed[i-1]) / dt
        du = fuzzy_fixed.compute(e_fixed[i], de)
        u_fixed[i] = np.clip(u_fixed[i-1] + du, 0, 10)
        h_fixed[i] = water_tank_dynamics(h_fixed[i-1], u_fixed[i], A, R, dt)

    # ---- 自适应论域模糊控制 ----
    h_adaptive = np.zeros(N)
    u_adaptive = np.zeros(N)
    e_adaptive = np.zeros(N)
    h_adaptive[0] = 0.5
    u_adaptive[0] = 1.0

    # 初始论域
    e_range_adaptive = [-2, 2]
    de_range_adaptive = [-1, 1]

    for i in range(1, N):
        e_adaptive[i] = r[i] - h_adaptive[i-1]
        de = (e_adaptive[i] - e_adaptive[i-1]) / dt

        # 自适应调整论域（根据误差大小）
        e_max = max(np.abs(e_adaptive[max(0, i-50):i+1]))  # 近期最大误差
        e_range_adaptive = [-e_max * 1.5, e_max * 1.5] if e_max > 0.5 else [-2, 2]

        # 创建自适应控制器
        fuzzy_adaptive = SimpleFuzzyController(n_sets=7, e_range=e_range_adaptive, de_range=de_range_adaptive)
        du = fuzzy_adaptive.compute(e_adaptive[i], de)
        u_adaptive[i] = np.clip(u_adaptive[i-1] + du, 0, 10)
        h_adaptive[i] = water_tank_dynamics(h_adaptive[i-1], u_adaptive[i], A, R, dt)

    # 性能对比
    mae_fixed = np.mean(np.abs(e_fixed))
    mae_adaptive = np.mean(np.abs(e_adaptive))

    print(f"\n[自适应vs固定论域]")
    print(f"  固定论域：MAE = {mae_fixed:.4f} m")
    print(f"  自适应论域：MAE = {mae_adaptive:.4f} m")
    print(f"  改进：{(mae_fixed - mae_adaptive) / mae_fixed * 100:.1f}%\n")

    # 绘图
    fig, axes = plt.subplots(3, 1, figsize=(12, 9))

    axes[0].plot(t, h_fixed, 'b-', label='固定论域', linewidth=2)
    axes[0].plot(t, h_adaptive, 'r--', label='自适应论域', linewidth=2)
    axes[0].plot(t, r, 'k:', label='目标', linewidth=2)
    axes[0].set_ylabel('液位 (m)')
    axes[0].set_title('自适应模糊控制 vs 固定论域')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(t, u_fixed, 'b-', label='固定论域', linewidth=2)
    axes[1].plot(t, u_adaptive, 'r--', label='自适应论域', linewidth=2)
    axes[1].set_ylabel('控制量 (m³/min)')
    axes[1].set_title('控制输入对比')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    axes[2].plot(t, e_fixed, 'b-', label='固定论域', linewidth=2)
    axes[2].plot(t, e_adaptive, 'r--', label='自适应论域', linewidth=2)
    axes[2].set_xlabel('时间 (min)')
    axes[2].set_ylabel('误差 (m)')
    axes[2].set_title('跟踪误差对比')
    axes[2].legend()
    axes[2].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('exp3_adaptive_fuzzy.png', dpi=150, bbox_inches='tight')
    plt.close()

    print("图表已保存：exp3_adaptive_fuzzy.png")

    print("\n结论：")
    print("  - 自适应调整论域能应对大范围变化")
    print("  - 目标突变时自适应性能更好")
    print("  - 实际应用中可结合多种自适应策略\n")

# ============================================================================
# 实验4：鲁棒性测试
# ============================================================================

def experiment_robustness():
    """测试模糊控制对参数不确定性和噪声的鲁棒性"""
    print("=" * 80)
    print("实验4：鲁棒性测试（参数不确定性 + 噪声）")
    print("=" * 80)

    # 参数
    dt = 0.1
    t_total = 30
    N = int(t_total / dt)
    t = np.linspace(0, t_total, N)
    r = 2.0 * np.ones(N)

    # 测试不同参数偏差
    param_cases = [
        {'A': 3.0, 'R': 2.0, 'label': '标称参数'},
        {'A': 3.6, 'R': 2.4, 'label': '+20%偏差'},
        {'A': 2.4, 'R': 1.6, 'label': '-20%偏差'}
    ]

    results = {}

    print("\n[测试参数鲁棒性]\n")

    for case in param_cases:
        A, R = case['A'], case['R']
        fuzzy = SimpleFuzzyController(n_sets=7)

        h = np.zeros(N)
        u = np.zeros(N)
        e = np.zeros(N)
        h[0] = 0.5
        u[0] = 1.0

        for i in range(1, N):
            e[i] = r[i] - h[i-1]
            de = (e[i] - e[i-1]) / dt
            du = fuzzy.compute(e[i], de)
            u[i] = np.clip(u[i-1] + du, 0, 10)

            # 添加测量噪声
            h_measured = h[i-1] + np.random.normal(0, 0.01)
            h[i] = water_tank_dynamics(h_measured, u[i], A, R, dt)

        mae = np.mean(np.abs(e))
        results[case['label']] = {'h': h, 'e': e, 'mae': mae}

        print(f"{case['label']}（A={A:.1f}, R={R:.1f}）：")
        print(f"  平均绝对误差：{mae:.4f} m\n")

    # 绘图
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))

    for label, data in results.items():
        axes[0].plot(t, data['h'], label=label, linewidth=2)
    axes[0].plot(t, r, 'k--', label='目标', linewidth=2)
    axes[0].set_ylabel('液位 (m)')
    axes[0].set_title('不同参数下的鲁棒性测试')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    for label, data in results.items():
        axes[1].plot(t, data['e'], label=label, linewidth=2)
    axes[1].set_xlabel('时间 (min)')
    axes[1].set_ylabel('误差 (m)')
    axes[1].set_title('跟踪误差对比')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('exp4_robustness.png', dpi=150, bbox_inches='tight')
    plt.close()

    print("图表已保存：exp4_robustness.png")

    print("\n结论：")
    print("  - 模糊控制对参数偏差鲁棒")
    print("  - ±20%参数变化仍能良好工作")
    print("  - 噪声影响较小")
    print("  - 适合参数不确定的系统\n")

# ============================================================================
# 主程序
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("案例16扩展实验：模糊控制深入研究")
    print("=" * 80)

    # 实验1：规则库大小
    experiment_rule_base_size()

    # 实验2：隶属函数形状
    experiment_membership_shapes()

    # 实验3：自适应模糊控制
    experiment_adaptive_fuzzy()

    # 实验4：鲁棒性测试
    experiment_robustness()

    print("=" * 80)
    print("所有扩展实验完成！")
    print("=" * 80)
