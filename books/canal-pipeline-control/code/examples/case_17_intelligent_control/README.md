# 案例17：智能控制（Neural Networks & Reinforcement Learning）

## 1. 案例简介

本案例演示**智能控制**技术在运河系统中的应用。智能控制是一类基于机器学习和人工智能的控制方法，能够通过数据学习系统动态、优化控制策略，并在复杂非线性系统中表现出色。

本案例重点介绍两类智能控制方法：
1. **神经网络控制**：利用神经网络的非线性逼近能力
2. **强化学习控制**：通过试错学习最优控制策略

### 应用场景

在运河-管道系统中，智能控制适用于以下场景：

1. **复杂非线性**：Saint-Venant方程的非线性特性
2. **难以建模**：水力学参数难以精确测量
3. **多工况适应**：不同流量、水位下的统一控制策略
4. **在线优化**：根据实时数据持续改进控制性能
5. **大规模系统**：多渠段协同控制

### 关键优势

- ✅ **免建模/弱建模**：无需精确数学模型，数据驱动
- ✅ **非线性处理**：天然适合处理强非线性系统
- ✅ **自主学习**：从经验中学习，持续优化
- ✅ **端到端优化**：直接从传感器到执行器的映射

---

## 2. 神经网络控制理论

### 2.1 神经网络基础

#### 前馈神经网络（FNN）

```
输入层 → 隐藏层 → 输出层

y = f(W₂·σ(W₁·x + b₁) + b₂)

其中：
    x: 输入向量
    W₁, W₂: 权重矩阵
    b₁, b₂: 偏置向量
    σ: 激活函数（如ReLU, tanh）
    f: 输出激活函数
```

**通用逼近定理**：
单隐藏层神经网络可以逼近任意连续函数（在紧集上）。

#### 常用激活函数

```python
# ReLU（整流线性单元）
σ(x) = max(0, x)
# 优点：计算快，缓解梯度消失
# 缺点：死神经元问题

# Tanh（双曲正切）
σ(x) = tanh(x) = (e^x - e^(-x))/(e^x + e^(-x))
# 优点：输出范围[-1, 1]，零中心
# 缺点：饱和区梯度小

# Sigmoid（逻辑函数）
σ(x) = 1/(1 + e^(-x))
# 优点：输出范围[0, 1]，概率解释
# 缺点：非零中心，梯度消失
```

### 2.2 神经网络控制架构

#### (1) 直接逆控制

```
神经网络学习系统逆模型：
    u = NN(y_desired, x)

训练数据：
    给定 (x, u) → y
    学习 (y_desired, x) → u
```

#### (2) 内模控制

```
并联结构：
    NN学习系统正向模型： ŷ = NN(x, u)
    控制器基于模型预测： u = Controller(ŷ, y_desired)

优点：
    - 模型辨识独立于控制
    - 可以使用任何控制算法
```

#### (3) 自适应神经网络控制

```
在线学习结构：
    u = NN(x, θ)
    θ̇ = -η·∇_θ L(y, y_desired)

其中：
    θ: 神经网络参数
    η: 学习率
    L: 损失函数（如跟踪误差）

结合Lyapunov稳定性理论保证收敛
```

### 2.3 神经网络训练

#### 反向传播算法（Backpropagation）

```python
# 前向传播
z1 = W1 @ x + b1
a1 = σ(z1)
z2 = W2 @ a1 + b2
y_pred = f(z2)

# 计算损失
L = 0.5 * (y_pred - y_true)**2

# 反向传播
δ2 = (y_pred - y_true) * f'(z2)
δ1 = (W2.T @ δ2) * σ'(z1)

# 参数更新
W2 -= η * (δ2 @ a1.T)
b2 -= η * δ2
W1 -= η * (δ1 @ x.T)
b1 -= η * δ1
```

#### 优化算法

```python
# SGD（随机梯度下降）
θ -= η * ∇_θ L

# Adam（自适应矩估计）
m = β1*m + (1-β1)*∇_θ L
v = β2*v + (1-β2)*(∇_θ L)^2
θ -= η * m / (sqrt(v) + ε)

# 推荐Adam，收敛快且稳定
```

---

## 3. 强化学习控制理论

### 3.1 强化学习基础

#### 马尔可夫决策过程（MDP）

```
定义：(S, A, P, R, γ)

    S: 状态空间
    A: 动作空间
    P: 转移概率 P(s'|s,a)
    R: 奖励函数 R(s,a,s')
    γ: 折扣因子 (0 ≤ γ < 1)

策略：π(a|s) - 给定状态选择动作的概率

目标：最大化累积奖励
    J = E[Σ_{t=0}^∞ γ^t R_t | π]
```

#### 值函数

```python
# 状态值函数（V函数）
V^π(s) = E[Σ_{t=0}^∞ γ^t R_t | s_0=s, π]
# 表示：从状态s出发，遵循策略π的期望回报

# 状态-动作值函数（Q函数）
Q^π(s,a) = E[Σ_{t=0}^∞ γ^t R_t | s_0=s, a_0=a, π]
# 表示：在状态s采取动作a，然后遵循策略π的期望回报

# Bellman方程
Q^π(s,a) = E[R(s,a) + γ·V^π(s')]
V^π(s) = Σ_a π(a|s)·Q^π(s,a)
```

### 3.2 Q-Learning（值迭代）

#### 算法原理

Q-learning是**无模型**的强化学习算法，直接学习Q函数：

```python
# Q-learning更新规则
Q(s,a) ← Q(s,a) + α·[r + γ·max_a' Q(s',a') - Q(s,a)]

其中：
    α: 学习率
    r: 即时奖励
    γ: 折扣因子
    max_a' Q(s',a'): 下一状态的最大Q值（贪婪策略）

# 伪代码
初始化 Q(s,a) = 0
for episode in episodes:
    s = initial_state
    while not done:
        # ε-greedy策略选择动作
        if random() < ε:
            a = random_action()
        else:
            a = argmax_a Q(s,a)

        # 执行动作
        s', r = step(s, a)

        # 更新Q函数
        Q(s,a) += α·[r + γ·max_a' Q(s',a') - Q(s,a)]

        s = s'
```

#### 探索-利用权衡

```python
# ε-greedy策略
ε = ε_start
for episode in episodes:
    ...
    ε = max(ε_end, ε * decay_rate)

# 典型参数
ε_start = 1.0   # 初期完全探索
ε_end = 0.01    # 最终保留1%探索
decay_rate = 0.995
```

### 3.3 Deep Q-Network (DQN)

当状态空间连续或非常大时，用神经网络近似Q函数：

```python
Q(s,a; θ) ≈ Q*(s,a)

其中 θ 是神经网络参数

# 损失函数
L(θ) = E[(y - Q(s,a;θ))^2]
其中 y = r + γ·max_a' Q(s',a';θ⁻)

# 关键技术
1. 经验回放（Experience Replay）
   - 存储转移 (s,a,r,s') 到回放缓冲区
   - 随机采样小批量进行训练
   - 打破样本相关性，提高稳定性

2. 目标网络（Target Network）
   - 使用独立的目标网络 Q(s,a;θ⁻)
   - 每隔N步更新 θ⁻ ← θ
   - 稳定训练过程
```

### 3.4 Actor-Critic算法

Actor-Critic结合策略梯度和值函数：

```
Actor（策略网络）：
    π(a|s; θ_π) - 选择动作

Critic（价值网络）：
    V(s; θ_v) 或 Q(s,a; θ_q) - 评估价值

# 更新规则
Critic: 最小化 TD误差
    δ = r + γ·V(s') - V(s)
    θ_v ← θ_v - α_v·δ·∇_θ_v V(s)

Actor: 策略梯度
    θ_π ← θ_π + α_π·δ·∇_θ_π log π(a|s)
```

### 3.5 DDPG（连续控制）

Deep Deterministic Policy Gradient适用于连续动作空间：

```python
# 确定性策略
a = μ(s; θ_μ)

# Critic网络（Q函数）
Q(s,a; θ_Q)

# Actor更新（策略梯度）
∇_θ_μ J ≈ E[∇_a Q(s,a)|_{a=μ(s)} · ∇_θ_μ μ(s)]

# Critic更新（TD学习）
L = E[(r + γ·Q'(s', μ'(s')) - Q(s,a))^2]

# 软更新目标网络
θ' ← τ·θ + (1-τ)·θ'   (τ << 1, 如0.001)
```

---

## 4. 运河系统的智能控制设计

### 4.1 状态和动作空间设计

#### 状态空间（观测）

```python
# 完整状态
s = [h₁, h₂, ..., h_n,        # 各渠段水位
     Q₁, Q₂, ..., Q_n,        # 各渠段流量
     h_ref₁, h_ref₂, ...,     # 参考水位
     Δh₁, Δh₂, ...,           # 水位误差
     t_normalized]            # 时间信息（可选）

# 归一化（重要！）
s_norm = (s - s_min) / (s_max - s_min)
```

#### 动作空间

```python
# 离散动作（Q-learning/DQN）
A = {增大流量, 保持, 减小流量}
或
A = {0, 1, 2, ..., 10}  # 10个离散流量等级

# 连续动作（DDPG/SAC）
a ∈ [u_min, u_max]  # 连续入流量
a_norm ∈ [-1, 1]    # 归一化后
```

### 4.2 奖励函数设计

奖励函数设计是强化学习的**关键**，直接影响学习效果：

```python
# 基本奖励：跟踪误差
r_tracking = -|h - h_ref|

# 多目标奖励
r = w1 * r_tracking + w2 * r_control + w3 * r_smooth

其中：
    r_tracking = -|h - h_ref|²        # 跟踪精度
    r_control = -u²                   # 控制能量
    r_smooth = -|u - u_prev|²         # 平滑性

    w1, w2, w3: 权重系数

# 加入约束惩罚
if h < h_min or h > h_max:
    r += penalty  # 大负值（如-100）

# 稀疏奖励（可选）
if |h - h_ref| < tolerance:
    r += bonus  # 达到目标给予额外奖励
```

### 4.3 神经网络架构选择

#### 控制器网络（Actor）

```python
# 简单前馈网络（适合运河系统）
class ControllerNetwork(nn.Module):
    def __init__(self, state_dim, action_dim):
        super().__init__()
        self.fc1 = nn.Linear(state_dim, 64)
        self.fc2 = nn.Linear(64, 64)
        self.fc3 = nn.Linear(64, action_dim)

    def forward(self, state):
        x = torch.relu(self.fc1(state))
        x = torch.relu(self.fc2(x))
        action = torch.tanh(self.fc3(x))  # 输出[-1, 1]
        return action

# 层数：2-3层足够（运河系统不太复杂）
# 神经元：32-128个/层
# 激活函数：ReLU（隐藏层），tanh（输出层）
```

#### Q网络（Critic）

```python
class QNetwork(nn.Module):
    def __init__(self, state_dim, action_dim):
        super().__init__()
        self.fc1 = nn.Linear(state_dim + action_dim, 64)
        self.fc2 = nn.Linear(64, 64)
        self.fc3 = nn.Linear(64, 1)

    def forward(self, state, action):
        x = torch.cat([state, action], dim=-1)
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        q_value = self.fc3(x)
        return q_value
```

### 4.4 训练策略

#### 课程学习（Curriculum Learning）

```python
# 从简单到复杂
Phase 1: 固定参考水位（阶跃响应）
Phase 2: 正弦参考轨迹
Phase 3: 随机扰动
Phase 4: 复杂工况（多扰动 + 参数不确定性）
```

#### 预训练（可选）

```python
# 使用专家数据（如PID控制器）预训练
dataset = collect_data_from_PID_controller()
pretrain_actor(dataset)

# 优点：
- 加速学习
- 减少探索风险
- 提供性能下界
```

#### 安全探索

```python
# 限制动作范围
a_safe = clip(a, a_min, a_max)

# 回退机制
if safety_violation(state):
    a = fallback_controller(state)  # 切换到安全控制器

# 使用模拟器训练
在真实系统部署前，在仿真环境中充分训练
```

---

## 5. 工程实现要点

### 5.1 神经网络控制实现

```python
import torch
import torch.nn as nn

class NeuralController:
    def __init__(self, state_dim, action_dim, hidden_dim=64):
        self.network = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, action_dim),
            nn.Tanh()  # 输出[-1, 1]
        )

        self.optimizer = torch.optim.Adam(
            self.network.parameters(), lr=1e-3
        )

    def compute_control(self, state):
        """计算控制输入"""
        state_tensor = torch.FloatTensor(state).unsqueeze(0)
        with torch.no_grad():
            action = self.network(state_tensor)
        return action.squeeze(0).numpy()

    def train_step(self, state, target_action):
        """训练步骤（监督学习）"""
        state_tensor = torch.FloatTensor(state)
        target_tensor = torch.FloatTensor(target_action)

        # 前向传播
        predicted_action = self.network(state_tensor)

        # 计算损失
        loss = nn.MSELoss()(predicted_action, target_tensor)

        # 反向传播
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        return loss.item()
```

### 5.2 DQN实现

```python
class ReplayBuffer:
    """经验回放缓冲区"""
    def __init__(self, capacity=10000):
        self.buffer = []
        self.capacity = capacity
        self.position = 0

    def push(self, state, action, reward, next_state, done):
        if len(self.buffer) < self.capacity:
            self.buffer.append(None)
        self.buffer[self.position] = (state, action, reward, next_state, done)
        self.position = (self.position + 1) % self.capacity

    def sample(self, batch_size):
        return random.sample(self.buffer, batch_size)

class DQNAgent:
    def __init__(self, state_dim, action_dim):
        self.q_network = QNetwork(state_dim, action_dim)
        self.target_network = QNetwork(state_dim, action_dim)
        self.target_network.load_state_dict(self.q_network.state_dict())

        self.optimizer = torch.optim.Adam(
            self.q_network.parameters(), lr=1e-3
        )
        self.replay_buffer = ReplayBuffer(capacity=10000)

        self.gamma = 0.99
        self.epsilon = 1.0
        self.epsilon_decay = 0.995
        self.epsilon_min = 0.01

    def select_action(self, state):
        """ε-greedy策略"""
        if np.random.rand() < self.epsilon:
            return np.random.randint(self.action_dim)
        else:
            state_tensor = torch.FloatTensor(state).unsqueeze(0)
            with torch.no_grad():
                q_values = self.q_network(state_tensor)
            return q_values.argmax().item()

    def train_step(self, batch_size=64):
        """训练步骤"""
        if len(self.replay_buffer) < batch_size:
            return 0

        # 采样
        batch = self.replay_buffer.sample(batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)

        states = torch.FloatTensor(states)
        actions = torch.LongTensor(actions)
        rewards = torch.FloatTensor(rewards)
        next_states = torch.FloatTensor(next_states)
        dones = torch.FloatTensor(dones)

        # 当前Q值
        current_q = self.q_network(states).gather(1, actions.unsqueeze(1))

        # 目标Q值
        with torch.no_grad():
            next_q = self.target_network(next_states).max(1)[0]
            target_q = rewards + (1 - dones) * self.gamma * next_q

        # 损失和更新
        loss = nn.MSELoss()(current_q.squeeze(), target_q)

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        return loss.item()

    def update_target_network(self):
        """更新目标网络"""
        self.target_network.load_state_dict(self.q_network.state_dict())
```

### 5.3 超参数选择指南

```python
# 学习率
learning_rate = 1e-3  # Adam优化器推荐值
# 太大：不稳定；太小：学习慢

# 折扣因子
gamma = 0.95 - 0.99
# 运河系统：0.95（不需要看太远）

# 探索率
epsilon_start = 1.0
epsilon_end = 0.01
epsilon_decay = 0.995
# 或使用线性衰减

# 经验回放
buffer_size = 10000 - 50000
batch_size = 64 - 256

# 目标网络更新频率
update_frequency = 100 - 1000 步

# 训练周期
num_episodes = 500 - 2000
```

---

## 6. 本案例演示内容

本案例包含4个演示部分：

### Part 1: 神经网络系统辨识
- 使用神经网络学习运河动态模型
- 数据收集和预处理
- 训练和验证
- 与线性模型对比

### Part 2: 神经网络自适应控制
- 神经网络控制器在线学习
- 基于监督学习的逆模型控制
- 参数自适应
- 跟踪性能评估

### Part 3: Q-Learning离散控制
- 离散化状态和动作空间
- Q表学习过程
- ε-greedy探索策略
- 学习曲线和性能

### Part 4: DDPG连续控制
- 连续动作空间控制
- Actor-Critic架构
- 经验回放和目标网络
- 与传统控制器对比

---

## 7. 与其他控制方法对比

| 控制方法 | 模型需求 | 非线性处理 | 学习能力 | 实时性 | 数据需求 | 可解释性 |
|---------|---------|-----------|---------|--------|---------|---------|
| PID | 无 | 弱 | 无 | 极高 | 无 | 强 |
| LQR | 精确模型 | 无 | 无 | 高 | 无 | 强 |
| MPC | 精确模型 | 中 | 无 | 中 | 无 | 强 |
| MRAC | 部分模型 | 弱 | 强 | 高 | 少 | 中 |
| **神经网络** | **弱模型** | **强** | **强** | 高 | 多 | 弱 |
| **强化学习** | **无需模型** | **强** | **极强** | 高（部署后） | 极多 | 弱 |

**智能控制的独特优势**：
- 数据驱动，无需精确建模
- 天然处理非线性
- 自主学习和持续优化
- 端到端优化

**主要挑战**：
- 训练数据需求大
- 训练时间长
- 稳定性和安全性保证困难
- 可解释性差（黑盒）

---

## 8. 工程应用建议

### 8.1 何时使用神经网络控制？

✅ **适合场景**：
- 系统高度非线性，难以精确建模
- 有大量历史运行数据
- 对性能要求高，可以离线训练
- 专家经验丰富（可用于监督学习）

❌ **不适合场景**：
- 安全关键系统（除非有严格验证）
- 数据稀缺
- 需要强可解释性
- 计算资源极其受限

### 8.2 何时使用强化学习控制？

✅ **适合场景**：
- 无法获得精确模型
- 奖励函数明确
- 有仿真环境可供训练
- 长期优化目标（不只是瞬态性能）

❌ **不适合场景**：
- 无法承受试错成本（危险/昂贵）
- 奖励函数难以定义
- 状态/动作空间极其巨大
- 需要快速部署（训练时间长）

### 8.3 实际部署checklist

**神经网络控制器：**
- [ ] 收集充足训练数据（数千到数万样本）
- [ ] 数据归一化和预处理
- [ ] 划分训练/验证/测试集
- [ ] 选择合适的网络架构（不要过度复杂）
- [ ] 防止过拟合（dropout, early stopping）
- [ ] 仿真环境验证
- [ ] 逐步过渡（先辅助，后主控）
- [ ] 监控和异常检测

**强化学习控制器：**
- [ ] 设计合理的奖励函数（关键！）
- [ ] 建立高保真仿真环境
- [ ] 充分训练（数万到数十万episode）
- [ ] 评估鲁棒性（不同初始条件、扰动）
- [ ] 安全机制（动作限制、回退控制器）
- [ ] A/B测试（与基线控制器对比）
- [ ] 持续学习（在线微调）
- [ ] 版本管理和回滚机制

### 8.4 常见陷阱

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 过拟合 | 模型太复杂/数据太少 | 正则化、数据增强、简化网络 |
| 训练不收敛 | 学习率不当、奖励函数设计差 | 调整超参数、重新设计奖励 |
| 性能不稳定 | 探索不足、网络震荡 | 增加探索、使用目标网络 |
| 泛化能力差 | 训练数据不够多样 | 增加数据多样性、课程学习 |
| 安全性问题 | 探索导致危险状态 | 安全约束、离线训练 |

---

## 9. 扩展阅读

### 经典教材

1. **强化学习**：
   - Sutton, R. S., & Barto, A. G. (2018). *Reinforcement Learning: An Introduction* (2nd ed.). MIT Press.
   - Bertsekas, D. P. (2019). *Reinforcement Learning and Optimal Control*. Athena Scientific.

2. **深度学习**：
   - Goodfellow, I., Bengio, Y., & Courville, A. (2016). *Deep Learning*. MIT Press.
   - Bishop, C. M. (2006). *Pattern Recognition and Machine Learning*. Springer.

3. **智能控制**：
   - Lewis, F. L., & Liu, D. (2013). *Reinforcement Learning and Adaptive Dynamic Programming for Feedback Control*. Wiley.

### 前沿算法

- **SAC (Soft Actor-Critic)**：最大熵强化学习，更稳定
- **PPO (Proximal Policy Optimization)**：策略优化，实用性强
- **TD3 (Twin Delayed DDPG)**：改进的DDPG，减少过估计
- **Model-Based RL**：结合模型学习，样本效率高
- **Meta-RL**：元学习，快速适应新任务

### 工程框架

```python
# PyTorch: 神经网络框架
import torch
import torch.nn as nn

# Stable-Baselines3: 强化学习算法库
from stable_baselines3 import PPO, SAC, TD3

# Gym: 强化学习环境接口
import gym
```

---

## 10. 总结

### 核心要点

1. **神经网络控制**：利用非线性逼近能力，学习控制器或系统模型
2. **强化学习控制**：通过试错学习最优策略，无需系统模型
3. **数据驱动**：性能取决于数据质量和数量
4. **训练关键**：奖励函数设计、超参数调优、安全探索

### 学习目标

通过本案例，你将掌握：
- ✅ 神经网络的基本原理和训练方法
- ✅ 强化学习的核心概念（MDP、Q-learning、DQN、DDPG）
- ✅ 智能控制器的设计和实现
- ✅ 运河系统的状态/动作/奖励设计
- ✅ 智能控制与传统控制的对比分析

### 实际意义

在运河-管道系统中，智能控制能够：
- 🎯 处理复杂非线性和强耦合
- 🎯 免去繁琐的建模过程
- 🎯 从历史数据中学习最优策略
- 🎯 持续优化，适应环境变化
- 🎯 大规模系统的端到端控制

---

**下一步**：运行 `main.py` 查看智能控制的学习过程和性能！
