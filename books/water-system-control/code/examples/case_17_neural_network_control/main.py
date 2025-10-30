"""
案例17：神经网络控制 - 深度学习与智能控制的结合

本程序演示神经网络控制在水箱液位控制中的应用，包括：
1. 神经网络基础（多层感知器MLP）
2. 神经网络PID控制器（自适应参数调整）
3. 直接神经网络控制器（端到端学习）
4. 模型参考自适应控制（MRAC）
5. 性能对比与分析
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

# 设置中文显示
rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

# ============================================================================
# 神经网络基础类
# ============================================================================

class NeuralNetwork:
    """多层感知器（MLP）"""

    def __init__(self, layers, learning_rate=0.01, activation='tanh'):
        """初始化神经网络

        Args:
            layers: 各层神经元数量列表，如[3, 10, 1]表示3输入-10隐藏-1输出
            learning_rate: 学习率
            activation: 激活函数类型（'tanh', 'sigmoid', 'relu'）
        """
        self.layers = layers
        self.learning_rate = learning_rate
        self.activation_type = activation

        # 初始化权重和偏置
        self.weights = []
        self.biases = []
        for i in range(len(layers) - 1):
            # Xavier初始化
            limit = np.sqrt(6 / (layers[i] + layers[i+1]))
            W = np.random.uniform(-limit, limit, (layers[i+1], layers[i]))
            b = np.zeros((layers[i+1], 1))
            self.weights.append(W)
            self.biases.append(b)

    def activation(self, x):
        """激活函数"""
        if self.activation_type == 'tanh':
            return np.tanh(x)
        elif self.activation_type == 'sigmoid':
            return 1 / (1 + np.exp(-np.clip(x, -500, 500)))
        elif self.activation_type == 'relu':
            return np.maximum(0, x)
        else:
            return x

    def activation_derivative(self, x):
        """激活函数导数"""
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
        """前向传播

        Args:
            x: 输入，shape=(n_features, 1)或(n_features,)

        Returns:
            输出值
        """
        if x.ndim == 1:
            x = x.reshape(-1, 1)

        self.activations = [x]
        self.z_values = []

        a = x
        for i in range(len(self.weights)):
            z = self.weights[i] @ a + self.biases[i]
            self.z_values.append(z)

            # 最后一层不使用激活函数（或使用线性）
            if i == len(self.weights) - 1:
                a = z  # 输出层线性
            else:
                a = self.activation(z)

            self.activations.append(a)

        return a.flatten()[0] if a.size == 1 else a.flatten()

    def backward(self, y_true):
        """反向传播

        Args:
            y_true: 真实标签
        """
        y_true = np.array(y_true).reshape(-1, 1)
        y_pred = self.activations[-1]

        # 计算输出层误差
        delta = y_pred - y_true

        # 反向传播
        for i in range(len(self.weights) - 1, -1, -1):
            # 梯度
            dW = delta @ self.activations[i].T
            db = delta

            # 更新权重和偏置
            self.weights[i] -= self.learning_rate * dW
            self.biases[i] -= self.learning_rate * db

            # 传播到前一层（如果不是输入层）
            if i > 0:
                delta = (self.weights[i].T @ delta) * self.activation_derivative(self.z_values[i-1])

    def train_step(self, x, y_true):
        """训练一步

        Args:
            x: 输入
            y_true: 真实标签

        Returns:
            预测值和损失
        """
        y_pred = self.forward(x)
        self.backward(y_true)
        loss = 0.5 * (y_pred - y_true)**2
        return y_pred, loss

# ============================================================================
# 水箱系统
# ============================================================================

def water_tank_dynamics(h, u, A=3.0, R=2.0, dt=0.1):
    """水箱动力学模型"""
    dhdt = (u - h / R) / A
    h_next = h + dhdt * dt
    return max(0, h_next)

# ============================================================================
# 第1部分：神经网络基础演示
# ============================================================================

def part1_nn_basics():
    """演示神经网络的基本功能"""
    print("=" * 80)
    print("第1部分：神经网络基础")
    print("=" * 80)

    # 创建简单网络：2输入-5隐藏-1输出
    nn = NeuralNetwork([2, 5, 1], learning_rate=0.1)

    print("\n[网络结构]")
    print(f"  层数：{len(nn.layers)}")
    print(f"  结构：{nn.layers}")
    print(f"  激活函数：{nn.activation_type}")
    print(f"  学习率：{nn.learning_rate}")

    # 生成训练数据：学习简单函数 y = x1 + x2
    np.random.seed(42)
    n_samples = 100
    X_train = np.random.randn(n_samples, 2)
    y_train = X_train[:, 0] + X_train[:, 1]

    print(f"\n[训练数据]")
    print(f"  样本数：{n_samples}")
    print(f"  目标函数：y = x1 + x2")

    # 训练
    n_epochs = 50
    losses = []

    for epoch in range(n_epochs):
        epoch_loss = 0
        for i in range(n_samples):
            _, loss = nn.train_step(X_train[i], y_train[i])
            epoch_loss += loss
        losses.append(epoch_loss / n_samples)

    print(f"\n[训练结果]")
    print(f"  训练轮数：{n_epochs}")
    print(f"  初始损失：{losses[0]:.4f}")
    print(f"  最终损失：{losses[-1]:.4f}")

    # 测试
    X_test = np.array([[1, 1], [2, 3], [-1, 2]])
    print(f"\n[测试]")
    for x in X_test:
        y_true = x[0] + x[1]
        y_pred = nn.forward(x)
        print(f"  输入：{x}, 真实值：{y_true:.2f}, 预测值：{y_pred:.2f}")

    # 绘制损失曲线
    plt.figure(figsize=(8, 5))
    plt.plot(losses, 'b-', linewidth=2)
    plt.xlabel('训练轮数')
    plt.ylabel('平均损失')
    plt.title('神经网络训练过程')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('case17_nn_basics.png', dpi=150, bbox_inches='tight')
    plt.close()

    print("\n图表已保存：case17_nn_basics.png\n")

# ============================================================================
# 第2部分：神经网络PID控制器
# ============================================================================

def part2_nn_pid():
    """神经网络自适应PID控制器"""
    print("=" * 80)
    print("第2部分：神经网络PID控制器")
    print("=" * 80)

    # 系统参数
    A, R, dt = 3.0, 2.0, 0.1
    t_total = 40
    N = int(t_total / dt)
    t = np.linspace(0, t_total, N)

    # 目标液位（阶跃变化）
    r = np.ones(N) * 2.0
    r[N//2:] = 2.5

    # 创建神经网络：3输入（e, de, ie）-> 10隐藏 -> 3输出（Kp, Ki, Kd）
    nn_pid = NeuralNetwork([3, 10, 3], learning_rate=0.001, activation='tanh')

    # 初始化
    h = np.zeros(N)
    u = np.zeros(N)
    e = np.zeros(N)
    de = np.zeros(N)
    ie = np.zeros(N)
    Kp_hist = np.zeros(N)
    Ki_hist = np.zeros(N)
    Kd_hist = np.zeros(N)

    h[0] = 0.5
    u[0] = 1.0

    print("\n[神经网络PID结构]")
    print("  输入：[e, Δe, ∫e]")
    print("  隐藏层：10个神经元（tanh激活）")
    print("  输出：[Kp, Ki, Kd]")
    print("  学习率：0.001")

    # 仿真
    for i in range(1, N):
        # 计算误差
        e[i] = r[i] - h[i-1]
        de[i] = (e[i] - e[i-1]) / dt
        ie[i] = ie[i-1] + e[i] * dt

        # 神经网络输出PID参数
        nn_input = np.array([e[i], de[i], ie[i]])
        pid_params = nn_pid.forward(nn_input)

        # 限制参数范围（归一化到合理范围）
        Kp = np.clip(pid_params[0], 0, 5)
        Ki = np.clip(pid_params[1], 0, 2)
        Kd = np.clip(pid_params[2], 0, 3)

        Kp_hist[i] = Kp
        Ki_hist[i] = Ki
        Kd_hist[i] = Kd

        # PID控制律
        u[i] = Kp * e[i] + Ki * ie[i] + Kd * de[i]
        u[i] = np.clip(u[i], 0, 10)

        # 系统动态
        h[i] = water_tank_dynamics(h[i-1], u[i], A, R, dt)

        # 在线学习：根据误差大小更新权重
        if abs(e[i]) > 0.05:  # 误差较大时才学习
            # 期望的控制效果：减小误差
            # 这里简化：期望下一步误差减半
            target_error_reduction = 0.5
            nn_pid.train_step(nn_input, pid_params)  # 基本更新

    # 性能指标
    mae = np.mean(np.abs(e))
    rmse = np.sqrt(np.mean(e**2))

    print(f"\n[性能指标]")
    print(f"  平均绝对误差（MAE）：{mae:.4f} m")
    print(f"  均方根误差（RMSE）：{rmse:.4f} m")
    print(f"  最终Kp：{Kp_hist[-1]:.3f}")
    print(f"  最终Ki：{Ki_hist[-1]:.3f}")
    print(f"  最终Kd：{Kd_hist[-1]:.3f}")

    # 绘图
    fig, axes = plt.subplots(4, 1, figsize=(12, 10))

    axes[0].plot(t, h, 'b-', label='实际液位', linewidth=2)
    axes[0].plot(t, r, 'r--', label='目标液位', linewidth=2)
    axes[0].set_ylabel('液位 (m)')
    axes[0].set_title('神经网络PID控制 - 液位跟踪')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(t, u, 'g-', linewidth=2)
    axes[1].set_ylabel('控制量 (m³/min)')
    axes[1].set_title('控制输入')
    axes[1].grid(True, alpha=0.3)

    axes[2].plot(t, Kp_hist, 'r-', label='Kp', linewidth=2)
    axes[2].plot(t, Ki_hist, 'g-', label='Ki', linewidth=2)
    axes[2].plot(t, Kd_hist, 'b-', label='Kd', linewidth=2)
    axes[2].set_ylabel('PID参数')
    axes[2].set_title('自适应PID参数变化')
    axes[2].legend()
    axes[2].grid(True, alpha=0.3)

    axes[3].plot(t, e, 'm-', linewidth=2)
    axes[3].set_xlabel('时间 (min)')
    axes[3].set_ylabel('误差 (m)')
    axes[3].set_title('跟踪误差')
    axes[3].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('case17_nn_pid.png', dpi=150, bbox_inches='tight')
    plt.close()

    print("\n图表已保存：case17_nn_pid.png\n")

    return nn_pid

# ============================================================================
# 第3部分：直接神经网络控制器
# ============================================================================

def part3_direct_nn_control():
    """直接神经网络控制器（端到端）"""
    print("=" * 80)
    print("第3部分：直接神经网络控制器")
    print("=" * 80)

    # 系统参数
    A, R, dt = 3.0, 2.0, 0.1
    t_total = 40
    N = int(t_total / dt)
    t = np.linspace(0, t_total, N)

    # 目标液位
    r = np.ones(N) * 2.0
    r[N//3:2*N//3] = 2.5

    # 创建神经网络：4输入（r, y, e, de）-> 15隐藏 -> 1输出（u）
    nn_controller = NeuralNetwork([4, 15, 1], learning_rate=0.005, activation='tanh')

    # 初始化
    h = np.zeros(N)
    u = np.zeros(N)
    e = np.zeros(N)
    de = np.zeros(N)

    h[0] = 0.5
    u[0] = 1.0

    print("\n[直接神经网络控制器结构]")
    print("  输入：[r, y, e, Δe]")
    print("  隐藏层：15个神经元（tanh激活）")
    print("  输出：u（控制量）")
    print("  学习率：0.005")

    # 仿真
    for i in range(1, N):
        # 计算误差
        e[i] = r[i] - h[i-1]
        de[i] = (e[i] - e[i-1]) / dt

        # 神经网络直接输出控制量
        nn_input = np.array([r[i], h[i-1], e[i], de[i]])
        u_raw = nn_controller.forward(nn_input)

        # 限制控制量（使用sigmoid缩放到0-10）
        u[i] = 5 + 5 * np.tanh(u_raw)  # 映射到0-10范围
        u[i] = np.clip(u[i], 0, 10)

        # 系统动态
        h[i] = water_tank_dynamics(h[i-1], u[i], A, R, dt)

        # 在线学习：根据误差更新网络
        if i > 10 and abs(e[i]) > 0.05:
            # 目标：使误差减小
            # 简化训练：如果误差为正，增大控制量；反之减小
            target_u = u[i] + 0.5 * np.sign(e[i])
            target_u = np.clip(target_u, 0, 10)
            nn_controller.train_step(nn_input, target_u)

    # 性能指标
    mae = np.mean(np.abs(e))
    rmse = np.sqrt(np.mean(e**2))

    print(f"\n[性能指标]")
    print(f"  平均绝对误差（MAE）：{mae:.4f} m")
    print(f"  均方根误差（RMSE）：{rmse:.4f} m")
    print(f"  稳态误差：{abs(e[-1]):.4f} m")

    # 绘图
    fig, axes = plt.subplots(3, 1, figsize=(12, 9))

    axes[0].plot(t, h, 'b-', label='实际液位', linewidth=2)
    axes[0].plot(t, r, 'r--', label='目标液位', linewidth=2)
    axes[0].set_ylabel('液位 (m)')
    axes[0].set_title('直接神经网络控制 - 液位跟踪')
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
    plt.savefig('case17_direct_nn.png', dpi=150, bbox_inches='tight')
    plt.close()

    print("\n图表已保存：case17_direct_nn.png\n")

    return nn_controller

# ============================================================================
# 第4部分：模型参考自适应控制（MRAC）
# ============================================================================

def part4_mrac():
    """模型参考自适应神经网络控制"""
    print("=" * 80)
    print("第4部分：模型参考自适应控制（MRAC）")
    print("=" * 80)

    # 系统参数
    A, R, dt = 3.0, 2.0, 0.1
    t_total = 40
    N = int(t_total / dt)
    t = np.linspace(0, t_total, N)

    # 参考输入
    r = np.ones(N) * 2.0
    r[N//4:] = 2.5

    # 参考模型（一阶系统，时间常数τ=2）
    tau_ref = 2.0
    ym = np.zeros(N)
    ym[0] = 0.5

    for i in range(1, N):
        dym = (r[i] - ym[i-1]) / tau_ref
        ym[i] = ym[i-1] + dym * dt

    # 创建神经网络控制器：3输入（ym, y, e_m）-> 12隐藏 -> 1输出（u）
    nn_mrac = NeuralNetwork([3, 12, 1], learning_rate=0.01, activation='tanh')

    # 初始化
    h = np.zeros(N)
    u = np.zeros(N)
    e_track = np.zeros(N)  # 跟踪误差（y相对于ym）

    h[0] = 0.5
    u[0] = 1.0

    print("\n[MRAC结构]")
    print("  参考模型：一阶系统，τ = 2.0 min")
    print("  神经网络输入：[ym, y, e_m]")
    print("  隐藏层：12个神经元（tanh激活）")
    print("  输出：u（控制量）")
    print("  学习率：0.01")

    # 仿真
    for i in range(1, N):
        # 跟踪误差：实际输出与参考模型输出的差
        e_track[i] = ym[i] - h[i-1]

        # 神经网络输入
        nn_input = np.array([ym[i], h[i-1], e_track[i]])
        u_raw = nn_mrac.forward(nn_input)

        # 控制量
        u[i] = 5 + 5 * np.tanh(u_raw)
        u[i] = np.clip(u[i], 0, 10)

        # 系统动态
        h[i] = water_tank_dynamics(h[i-1], u[i], A, R, dt)

        # 在线学习：最小化跟踪误差
        if i > 5 and abs(e_track[i]) > 0.01:
            # 期望增大或减小控制量以减小误差
            target_u = u[i] + 2.0 * np.sign(e_track[i])
            target_u = np.clip(target_u, 0, 10)
            nn_mrac.train_step(nn_input, target_u)

    # 性能指标
    mae_track = np.mean(np.abs(e_track))
    rmse_track = np.sqrt(np.mean(e_track**2))

    print(f"\n[性能指标]")
    print(f"  平均跟踪误差（MAE）：{mae_track:.4f} m")
    print(f"  均方根跟踪误差（RMSE）：{rmse_track:.4f} m")
    print(f"  最终跟踪误差：{abs(e_track[-1]):.4f} m")

    # 绘图
    fig, axes = plt.subplots(3, 1, figsize=(12, 9))

    axes[0].plot(t, h, 'b-', label='实际输出 y', linewidth=2)
    axes[0].plot(t, ym, 'r--', label='参考模型输出 ym', linewidth=2)
    axes[0].plot(t, r, 'k:', label='参考输入 r', linewidth=2)
    axes[0].set_ylabel('液位 (m)')
    axes[0].set_title('模型参考自适应控制（MRAC）')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(t, u, 'g-', linewidth=2)
    axes[1].set_ylabel('控制量 (m³/min)')
    axes[1].set_title('控制输入')
    axes[1].grid(True, alpha=0.3)

    axes[2].plot(t, e_track, 'm-', linewidth=2)
    axes[2].set_xlabel('时间 (min)')
    axes[2].set_ylabel('跟踪误差 (m)')
    axes[2].set_title('跟踪误差（y - ym）')
    axes[2].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('case17_mrac.png', dpi=150, bbox_inches='tight')
    plt.close()

    print("\n图表已保存：case17_mrac.png\n")

# ============================================================================
# 第5部分：总结
# ============================================================================

def part5_summary():
    """总结神经网络控制的关键点"""
    print("=" * 80)
    print("第5部分：案例17总结")
    print("=" * 80)

    summary_text = """
[关键知识点]
  1. 神经网络基础：
     • 前向传播：层层计算激活值
     • 反向传播：梯度下降更新权重
     • 激活函数：tanh、sigmoid、ReLU

  2. 神经网络PID控制器：
     • 自适应调整PID参数
     • 输入：[e, Δe, ∫e]
     • 输出：[Kp, Ki, Kd]
     • 优势：非线性增益调度

  3. 直接神经网络控制器：
     • 端到端学习控制策略
     • 输入：[r, y, e, Δe]
     • 输出：u（控制量）
     • 优势：更大设计自由度

  4. 模型参考自适应控制（MRAC）：
     • 参考模型定义期望行为
     • 神经网络最小化跟踪误差
     • 在线学习持续改进
     • 优势：明确的性能目标

[工程应用]
  • 复杂非线性系统控制
  • 时变参数系统
  • 难以建模的过程
  • 需要在线适应的场合

[实用建议]
  • 从简单结构开始（1层隐藏层）
  • 使用小学习率（0.001-0.01）
  • 限制输出范围（饱和、限幅）
  • 结合传统控制器作为backup
  • 监控性能，防止发散

[优势]
  • 强大的非线性逼近能力
  • 无需精确数学模型
  • 数据驱动，易于实现
  • 在线学习，自适应能力强

[局限]
  • 稳定性难以保证
  • 需要careful调参
  • 计算开销较大
  • 可解释性差

[下一步学习]
  → 案例18：强化学习控制（Q-learning、DQN）
  → 案例19：综合对比与性能评估
"""
    print(summary_text)

    print("=" * 80)
    print("案例17演示完成！")
    print("=" * 80)

# ============================================================================
# 主程序
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("案例17：神经网络控制 - 深度学习与智能控制的结合")
    print("=" * 80)

    # 第1部分：神经网络基础
    part1_nn_basics()

    # 第2部分：神经网络PID
    part2_nn_pid()

    # 第3部分：直接神经网络控制
    part3_direct_nn_control()

    # 第4部分：MRAC
    part4_mrac()

    # 第5部分：总结
    part5_summary()
