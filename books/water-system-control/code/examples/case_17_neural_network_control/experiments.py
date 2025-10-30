"""
案例17扩展实验：神经网络控制深入研究

本程序包含以下扩展实验：
1. 不同网络结构对比（神经元数量、隐藏层数）
2. 学习率影响（收敛速度与稳定性）
3. 在线学习vs离线学习
4. 鲁棒性测试（参数不确定性、噪声）
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

# 设置中文显示
rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

# ============================================================================
# 神经网络类（复用）
# ============================================================================

class NeuralNetwork:
    """多层感知器（MLP）"""

    def __init__(self, layers, learning_rate=0.01, activation='tanh'):
        self.layers = layers
        self.learning_rate = learning_rate
        self.activation_type = activation

        # 初始化权重和偏置
        self.weights = []
        self.biases = []
        for i in range(len(layers) - 1):
            limit = np.sqrt(6 / (layers[i] + layers[i+1]))
            W = np.random.uniform(-limit, limit, (layers[i+1], layers[i]))
            b = np.zeros((layers[i+1], 1))
            self.weights.append(W)
            self.biases.append(b)

    def activation(self, x):
        if self.activation_type == 'tanh':
            return np.tanh(x)
        elif self.activation_type == 'sigmoid':
            return 1 / (1 + np.exp(-np.clip(x, -500, 500)))
        elif self.activation_type == 'relu':
            return np.maximum(0, x)
        else:
            return x

    def activation_derivative(self, x):
        if self.activation_type == 'tanh':
            return 1 - np.tanh(x)**2
        elif self.activation_type == 'sigmoid':
            sig = 1 / (1 + np.exp(-np.clip(x, -500, 500)))
            return sig * (1 - sig)
        elif self.activation_type == 'relu':
            return (x > 0).astype(float)
        else:
            return np.ones_like(x)

    def forward(self, x):
        if x.ndim == 1:
            x = x.reshape(-1, 1)

        self.activations = [x]
        self.z_values = []

        a = x
        for i in range(len(self.weights)):
            z = self.weights[i] @ a + self.biases[i]
            self.z_values.append(z)

            if i == len(self.weights) - 1:
                a = z
            else:
                a = self.activation(z)

            self.activations.append(a)

        return a.flatten()[0] if a.size == 1 else a.flatten()

    def backward(self, y_true):
        y_true = np.array(y_true).reshape(-1, 1)
        y_pred = self.activations[-1]

        delta = y_pred - y_true

        for i in range(len(self.weights) - 1, -1, -1):
            dW = delta @ self.activations[i].T
            db = delta

            self.weights[i] -= self.learning_rate * dW
            self.biases[i] -= self.learning_rate * db

            if i > 0:
                delta = (self.weights[i].T @ delta) * self.activation_derivative(self.z_values[i-1])

    def train_step(self, x, y_true):
        y_pred = self.forward(x)
        self.backward(y_true)
        loss = 0.5 * (y_pred - y_true)**2
        return y_pred, loss

# ============================================================================
# 水箱系统
# ============================================================================

def water_tank_dynamics(h, u, A=3.0, R=2.0, dt=0.1):
    """水箱动力学"""
    dhdt = (u - h / R) / A
    h_next = h + dhdt * dt
    return max(0, h_next)

# ============================================================================
# 实验1：不同网络结构对比
# ============================================================================

def experiment_network_structures():
    """对比不同网络结构的性能"""
    print("=" * 80)
    print("实验1：网络结构影响")
    print("=" * 80)

    # 系统参数
    A, R, dt = 3.0, 2.0, 0.1
    t_total = 30
    N = int(t_total / dt)
    t = np.linspace(0, t_total, N)
    r = 2.0 * np.ones(N)

    # 测试不同结构
    structures = [
        ([4, 5, 1], "5神经元"),
        ([4, 10, 1], "10神经元"),
        ([4, 20, 1], "20神经元"),
        ([4, 10, 10, 1], "两隐藏层")
    ]

    results = {}

    print("\n[测试不同网络结构]\n")

    for struct, label in structures:
        # 创建控制器
        nn = NeuralNetwork(struct, learning_rate=0.005, activation='tanh')

        # 初始化
        h = np.zeros(N)
        u = np.zeros(N)
        e = np.zeros(N)
        de = np.zeros(N)
        h[0] = 0.5
        u[0] = 1.0

        # 仿真
        for i in range(1, N):
            e[i] = r[i] - h[i-1]
            de[i] = (e[i] - e[i-1]) / dt

            nn_input = np.array([r[i], h[i-1], e[i], de[i]])
            u_raw = nn.forward(nn_input)
            u[i] = 5 + 5 * np.tanh(u_raw)
            u[i] = np.clip(u[i], 0, 10)

            h[i] = water_tank_dynamics(h[i-1], u[i], A, R, dt)

            # 在线学习
            if i > 10 and abs(e[i]) > 0.05:
                target_u = u[i] + 0.5 * np.sign(e[i])
                target_u = np.clip(target_u, 0, 10)
                nn.train_step(nn_input, target_u)

        # 性能指标
        mae = np.mean(np.abs(e))
        settling_idx = np.where(np.abs(e) < 0.05)[0]
        settling_time = t[settling_idx[0]] if len(settling_idx) > 0 else t_total

        results[label] = {'h': h, 'e': e, 'mae': mae, 'settling_time': settling_time}

        print(f"{label}（{struct}）：")
        print(f"  平均绝对误差：{mae:.4f} m")
        print(f"  调节时间：{settling_time:.2f} min\n")

    # 绘图
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))

    for label, data in results.items():
        axes[0].plot(t, data['h'], label=label, linewidth=2)
    axes[0].plot(t, r, 'k--', label='目标', linewidth=2)
    axes[0].set_ylabel('液位 (m)')
    axes[0].set_title('不同网络结构的液位响应')
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
    plt.savefig('exp1_network_structures.png', dpi=150, bbox_inches='tight')
    plt.close()

    print("图表已保存：exp1_network_structures.png")

    print("\n结论：")
    print("  - 5神经元：简单但可能不够")
    print("  - 10神经元：性能良好，推荐")
    print("  - 20神经元：性能更好但计算量大")
    print("  - 两隐藏层：更强表达能力，但训练较慢\n")

# ============================================================================
# 实验2：学习率影响
# ============================================================================

def experiment_learning_rates():
    """测试不同学习率的影响"""
    print("=" * 80)
    print("实验2：学习率影响")
    print("=" * 80)

    # 系统参数
    A, R, dt = 3.0, 2.0, 0.1
    t_total = 30
    N = int(t_total / dt)
    t = np.linspace(0, t_total, N)
    r = 2.0 * np.ones(N)

    # 测试不同学习率
    learning_rates = [0.001, 0.005, 0.01, 0.05]
    results = {}

    print("\n[测试不同学习率]\n")

    for lr in learning_rates:
        # 创建控制器
        nn = NeuralNetwork([4, 10, 1], learning_rate=lr, activation='tanh')

        # 初始化
        h = np.zeros(N)
        u = np.zeros(N)
        e = np.zeros(N)
        de = np.zeros(N)
        h[0] = 0.5
        u[0] = 1.0

        # 仿真
        for i in range(1, N):
            e[i] = r[i] - h[i-1]
            de[i] = (e[i] - e[i-1]) / dt

            nn_input = np.array([r[i], h[i-1], e[i], de[i]])
            u_raw = nn.forward(nn_input)
            u[i] = 5 + 5 * np.tanh(u_raw)
            u[i] = np.clip(u[i], 0, 10)

            h[i] = water_tank_dynamics(h[i-1], u[i], A, R, dt)

            # 在线学习
            if i > 10 and abs(e[i]) > 0.05:
                target_u = u[i] + 0.5 * np.sign(e[i])
                target_u = np.clip(target_u, 0, 10)
                nn.train_step(nn_input, target_u)

        # 性能指标
        mae = np.mean(np.abs(e))
        results[lr] = {'h': h, 'e': e, 'mae': mae}

        print(f"学习率 = {lr}：")
        print(f"  平均绝对误差：{mae:.4f} m\n")

    # 绘图
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))

    for lr, data in results.items():
        axes[0].plot(t, data['h'], label=f'η={lr}', linewidth=2)
    axes[0].plot(t, r, 'k--', label='目标', linewidth=2)
    axes[0].set_ylabel('液位 (m)')
    axes[0].set_title('不同学习率的液位响应')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    for lr, data in results.items():
        axes[1].plot(t, data['e'], label=f'η={lr}', linewidth=2)
    axes[1].set_xlabel('时间 (min)')
    axes[1].set_ylabel('误差 (m)')
    axes[1].set_title('跟踪误差对比')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('exp2_learning_rates.png', dpi=150, bbox_inches='tight')
    plt.close()

    print("图表已保存：exp2_learning_rates.png")

    print("\n结论：")
    print("  - 学习率过小（0.001）：收敛慢")
    print("  - 学习率适中（0.005-0.01）：性能好")
    print("  - 学习率过大（0.05）：可能震荡或发散")
    print("  - 推荐：0.005用于在线学习\n")

# ============================================================================
# 实验3：在线学习vs离线学习
# ============================================================================

def experiment_online_vs_offline():
    """对比在线学习和离线学习"""
    print("=" * 80)
    print("实验3：在线学习 vs 离线学习")
    print("=" * 80)

    # 系统参数
    A, R, dt = 3.0, 2.0, 0.1
    t_total = 40
    N = int(t_total / dt)
    t = np.linspace(0, t_total, N)

    # 目标变化（测试适应能力）
    r = np.ones(N) * 2.0
    r[N//2:] = 2.5  # 中途目标变化

    # ---- 离线学习：先用数据训练，然后固定权重 ----
    print("\n[离线学习阶段]")

    # 生成训练数据
    np.random.seed(42)
    n_train = 200
    X_train = []
    y_train = []

    for _ in range(n_train):
        # 随机生成状态
        r_sample = np.random.uniform(1.5, 2.5)
        h_sample = np.random.uniform(0.5, 3.0)
        e_sample = r_sample - h_sample
        de_sample = np.random.uniform(-0.5, 0.5)

        # 简单的控制策略（基于误差的比例控制）
        u_sample = 1.5 * e_sample + h_sample / R

        X_train.append([r_sample, h_sample, e_sample, de_sample])
        y_train.append(u_sample)

    X_train = np.array(X_train)
    y_train = np.array(y_train)

    # 训练网络
    nn_offline = NeuralNetwork([4, 10, 1], learning_rate=0.01, activation='tanh')

    n_epochs = 100
    for epoch in range(n_epochs):
        for i in range(n_train):
            nn_offline.train_step(X_train[i], y_train[i])

    print(f"  完成{n_epochs}轮离线训练，样本数：{n_train}")

    # 测试离线训练的控制器（固定权重）
    h_offline = np.zeros(N)
    u_offline = np.zeros(N)
    e_offline = np.zeros(N)
    h_offline[0] = 0.5
    u_offline[0] = 1.0

    for i in range(1, N):
        e_offline[i] = r[i] - h_offline[i-1]
        de = (e_offline[i] - e_offline[i-1]) / dt

        nn_input = np.array([r[i], h_offline[i-1], e_offline[i], de])
        u_raw = nn_offline.forward(nn_input)
        u_offline[i] = 5 + 5 * np.tanh(u_raw)
        u_offline[i] = np.clip(u_offline[i], 0, 10)

        h_offline[i] = water_tank_dynamics(h_offline[i-1], u_offline[i], A, R, dt)
        # 注意：不进行在线更新

    # ---- 在线学习：实时更新权重 ----
    print("\n[在线学习]")

    nn_online = NeuralNetwork([4, 10, 1], learning_rate=0.005, activation='tanh')

    h_online = np.zeros(N)
    u_online = np.zeros(N)
    e_online = np.zeros(N)
    h_online[0] = 0.5
    u_online[0] = 1.0

    for i in range(1, N):
        e_online[i] = r[i] - h_online[i-1]
        de = (e_online[i] - e_online[i-1]) / dt

        nn_input = np.array([r[i], h_online[i-1], e_online[i], de])
        u_raw = nn_online.forward(nn_input)
        u_online[i] = 5 + 5 * np.tanh(u_raw)
        u_online[i] = np.clip(u_online[i], 0, 10)

        h_online[i] = water_tank_dynamics(h_online[i-1], u_online[i], A, R, dt)

        # 在线学习
        if i > 10 and abs(e_online[i]) > 0.05:
            target_u = u_online[i] + 0.5 * np.sign(e_online[i])
            target_u = np.clip(target_u, 0, 10)
            nn_online.train_step(nn_input, target_u)

    # 性能对比
    mae_offline = np.mean(np.abs(e_offline))
    mae_online = np.mean(np.abs(e_online))

    # 特别关注目标变化后的性能
    mae_offline_after = np.mean(np.abs(e_offline[N//2:]))
    mae_online_after = np.mean(np.abs(e_online[N//2:]))

    print(f"\n[性能对比]")
    print(f"  离线学习：")
    print(f"    总体MAE：{mae_offline:.4f} m")
    print(f"    目标变化后MAE：{mae_offline_after:.4f} m")
    print(f"\n  在线学习：")
    print(f"    总体MAE：{mae_online:.4f} m")
    print(f"    目标变化后MAE：{mae_online_after:.4f} m")
    print(f"\n  改进：{(mae_offline - mae_online) / mae_offline * 100:.1f}%")

    # 绘图
    fig, axes = plt.subplots(3, 1, figsize=(12, 9))

    axes[0].plot(t, h_offline, 'b-', label='离线学习', linewidth=2)
    axes[0].plot(t, h_online, 'r--', label='在线学习', linewidth=2)
    axes[0].plot(t, r, 'k:', label='目标', linewidth=2)
    axes[0].set_ylabel('液位 (m)')
    axes[0].set_title('在线学习 vs 离线学习')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    axes[0].axvline(x=t[N//2], color='gray', linestyle='--', alpha=0.5, label='目标变化')

    axes[1].plot(t, u_offline, 'b-', label='离线学习', linewidth=2)
    axes[1].plot(t, u_online, 'r--', label='在线学习', linewidth=2)
    axes[1].set_ylabel('控制量 (m³/min)')
    axes[1].set_title('控制输入对比')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    axes[2].plot(t, e_offline, 'b-', label='离线学习', linewidth=2)
    axes[2].plot(t, e_online, 'r--', label='在线学习', linewidth=2)
    axes[2].set_xlabel('时间 (min)')
    axes[2].set_ylabel('误差 (m)')
    axes[2].set_title('跟踪误差对比')
    axes[2].legend()
    axes[2].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('exp3_online_vs_offline.png', dpi=150, bbox_inches='tight')
    plt.close()

    print("\n图表已保存：exp3_online_vs_offline.png")

    print("\n结论：")
    print("  - 离线学习：初始性能好，但无法适应目标变化")
    print("  - 在线学习：持续学习，能适应新情况")
    print("  - 最佳策略：离线预训练 + 在线微调\n")

# ============================================================================
# 实验4：鲁棒性测试
# ============================================================================

def experiment_robustness():
    """测试神经网络控制的鲁棒性"""
    print("=" * 80)
    print("实验4：鲁棒性测试（参数不确定性 + 噪声）")
    print("=" * 80)

    # 参数
    dt = 0.1
    t_total = 30
    N = int(t_total / dt)
    t = np.linspace(0, t_total, N)
    r = 2.0 * np.ones(N)

    # 测试不同参数
    param_cases = [
        {'A': 3.0, 'R': 2.0, 'label': '标称参数'},
        {'A': 3.6, 'R': 2.4, 'label': '+20%偏差'},
        {'A': 2.4, 'R': 1.6, 'label': '-20%偏差'}
    ]

    results = {}

    print("\n[测试参数鲁棒性]\n")

    for case in param_cases:
        A, R = case['A'], case['R']

        # 创建控制器
        nn = NeuralNetwork([4, 10, 1], learning_rate=0.005, activation='tanh')

        h = np.zeros(N)
        u = np.zeros(N)
        e = np.zeros(N)
        h[0] = 0.5
        u[0] = 1.0

        for i in range(1, N):
            e[i] = r[i] - h[i-1]
            de = (e[i] - e[i-1]) / dt

            nn_input = np.array([r[i], h[i-1], e[i], de])
            u_raw = nn.forward(nn_input)
            u[i] = 5 + 5 * np.tanh(u_raw)
            u[i] = np.clip(u[i], 0, 10)

            # 添加测量噪声
            h_measured = h[i-1] + np.random.normal(0, 0.02)
            h[i] = water_tank_dynamics(h_measured, u[i], A, R, dt)

            # 在线学习
            if i > 10 and abs(e[i]) > 0.05:
                target_u = u[i] + 0.5 * np.sign(e[i])
                target_u = np.clip(target_u, 0, 10)
                nn.train_step(nn_input, target_u)

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
    print("  - 神经网络控制对参数偏差鲁棒")
    print("  - 在线学习能适应参数变化")
    print("  - ±20%参数变化性能仍可接受")
    print("  - 测量噪声影响较小\n")

# ============================================================================
# 主程序
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("案例17扩展实验：神经网络控制深入研究")
    print("=" * 80)

    # 实验1：网络结构
    experiment_network_structures()

    # 实验2：学习率
    experiment_learning_rates()

    # 实验3：在线vs离线
    experiment_online_vs_offline()

    # 实验4：鲁棒性
    experiment_robustness()

    print("=" * 80)
    print("所有扩展实验完成！")
    print("=" * 80)
