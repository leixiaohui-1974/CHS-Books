"""
案例18：强化学习控制 - 智能体学习最优策略

本程序演示强化学习在水箱液位控制中的应用，包括：
1. Q-learning算法（离散状态空间）
2. SARSA算法（on-policy学习）
3. Deep Q-Network (DQN)（连续状态空间）
4. 性能对比与分析
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from collections import deque
import random

# 设置中文显示
rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

# ============================================================================
# 水箱环境类
# ============================================================================

class WaterTankEnv:
    """水箱环境"""

    def __init__(self, A=3.0, R=2.0, dt=0.1, target=2.0):
        """初始化环境

        Args:
            A: 水箱横截面积
            R: 出口阻力
            dt: 时间步长
            target: 目标液位
        """
        self.A = A
        self.R = R
        self.dt = dt
        self.target = target

        # 状态：液位
        self.h = 0.5
        self.h_min = 0.0
        self.h_max = 4.0

        # 动作空间：离散控制量
        self.actions = [0, 2, 4, 6, 8, 10]  # m³/min
        self.n_actions = len(self.actions)

    def reset(self):
        """重置环境"""
        self.h = np.random.uniform(0.5, 1.5)
        return self._get_state()

    def _get_state(self):
        """获取当前状态"""
        return self.h

    def step(self, action_idx):
        """执行动作，返回新状态、奖励、是否结束

        Args:
            action_idx: 动作索引

        Returns:
            state, reward, done
        """
        # 获取控制量
        u = self.actions[action_idx]

        # 动力学更新
        dhdt = (u - self.h / self.R) / self.A
        self.h = self.h + dhdt * self.dt
        self.h = np.clip(self.h, self.h_min, self.h_max)

        # 计算奖励
        error = abs(self.h - self.target)

        # 奖励函数：误差越小，奖励越高
        if error < 0.1:
            reward = 10.0  # 达到目标，大奖励
        else:
            reward = -error  # 误差越大，惩罚越大

        # 判断是否结束（液位超出范围）
        done = (self.h <= self.h_min + 0.1) or (self.h >= self.h_max - 0.1)

        return self._get_state(), reward, done

# ============================================================================
# Q-learning算法
# ============================================================================

class QLearningAgent:
    """Q-learning智能体"""

    def __init__(self, n_states, n_actions, learning_rate=0.1, discount=0.95, epsilon=1.0):
        """初始化Q-learning智能体

        Args:
            n_states: 状态数量
            n_actions: 动作数量
            learning_rate: 学习率α
            discount: 折扣因子γ
            epsilon: 探索率ε
        """
        self.n_states = n_states
        self.n_actions = n_actions
        self.alpha = learning_rate
        self.gamma = discount
        self.epsilon = epsilon
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995

        # 初始化Q表
        self.Q = np.zeros((n_states, n_actions))

    def discretize_state(self, state, n_bins=20):
        """将连续状态离散化

        Args:
            state: 连续状态值（液位）
            n_bins: 离散化的区间数

        Returns:
            离散状态索引
        """
        state_min, state_max = 0.0, 4.0
        bin_size = (state_max - state_min) / n_bins
        state_idx = int((state - state_min) / bin_size)
        state_idx = np.clip(state_idx, 0, n_bins - 1)
        return state_idx

    def choose_action(self, state):
        """选择动作（ε-greedy策略）

        Args:
            state: 状态索引

        Returns:
            动作索引
        """
        if np.random.random() < self.epsilon:
            # 探索：随机选择
            return np.random.randint(self.n_actions)
        else:
            # 利用：选择最优动作
            return np.argmax(self.Q[state, :])

    def learn(self, state, action, reward, next_state, done):
        """更新Q值

        Args:
            state: 当前状态
            action: 执行的动作
            reward: 获得的奖励
            next_state: 下一状态
            done: 是否结束
        """
        # Q-learning更新规则
        if done:
            target = reward
        else:
            target = reward + self.gamma * np.max(self.Q[next_state, :])

        # TD误差
        td_error = target - self.Q[state, action]

        # 更新Q值
        self.Q[state, action] += self.alpha * td_error

    def decay_epsilon(self):
        """衰减探索率"""
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

# ============================================================================
# SARSA算法
# ============================================================================

class SARSAAgent:
    """SARSA智能体（on-policy）"""

    def __init__(self, n_states, n_actions, learning_rate=0.1, discount=0.95, epsilon=1.0):
        self.n_states = n_states
        self.n_actions = n_actions
        self.alpha = learning_rate
        self.gamma = discount
        self.epsilon = epsilon
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995

        # 初始化Q表
        self.Q = np.zeros((n_states, n_actions))

    def discretize_state(self, state, n_bins=20):
        """状态离散化"""
        state_min, state_max = 0.0, 4.0
        bin_size = (state_max - state_min) / n_bins
        state_idx = int((state - state_min) / bin_size)
        state_idx = np.clip(state_idx, 0, n_bins - 1)
        return state_idx

    def choose_action(self, state):
        """ε-greedy策略"""
        if np.random.random() < self.epsilon:
            return np.random.randint(self.n_actions)
        else:
            return np.argmax(self.Q[state, :])

    def learn(self, state, action, reward, next_state, next_action, done):
        """SARSA更新（使用实际选择的下一个动作）

        Args:
            state: 当前状态
            action: 当前动作
            reward: 获得的奖励
            next_state: 下一状态
            next_action: 下一个实际选择的动作
            done: 是否结束
        """
        if done:
            target = reward
        else:
            # 关键区别：使用实际选择的next_action
            target = reward + self.gamma * self.Q[next_state, next_action]

        td_error = target - self.Q[state, action]
        self.Q[state, action] += self.alpha * td_error

    def decay_epsilon(self):
        """衰减探索率"""
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

# ============================================================================
# 简化的DQN（使用小型神经网络）
# ============================================================================

class SimpleDQN:
    """简化的Deep Q-Network"""

    def __init__(self, state_dim, n_actions, learning_rate=0.001):
        """初始化DQN

        Args:
            state_dim: 状态维度
            n_actions: 动作数量
            learning_rate: 学习率
        """
        self.state_dim = state_dim
        self.n_actions = n_actions
        self.lr = learning_rate

        # 简单的神经网络：输入层 -> 隐藏层 -> 输出层
        self.W1 = np.random.randn(state_dim, 16) * 0.1
        self.b1 = np.zeros(16)
        self.W2 = np.random.randn(16, n_actions) * 0.1
        self.b2 = np.zeros(n_actions)

        # 经验回放
        self.memory = deque(maxlen=2000)
        self.batch_size = 32

        # 探索参数
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.gamma = 0.95

    def forward(self, state):
        """前向传播

        Args:
            state: 输入状态

        Returns:
            Q值向量
        """
        # 确保state是1D数组
        if isinstance(state, (int, float)):
            state = np.array([state])

        # 隐藏层（ReLU激活）
        h = np.maximum(0, np.dot(state, self.W1) + self.b1)

        # 输出层（Q值）
        q_values = np.dot(h, self.W2) + self.b2

        return q_values, h

    def choose_action(self, state):
        """ε-greedy选择动作"""
        if np.random.random() < self.epsilon:
            return np.random.randint(self.n_actions)
        else:
            q_values, _ = self.forward(state)
            return np.argmax(q_values)

    def remember(self, state, action, reward, next_state, done):
        """存储经验"""
        self.memory.append((state, action, reward, next_state, done))

    def replay(self):
        """经验回放训练"""
        if len(self.memory) < self.batch_size:
            return

        # 随机采样
        batch = random.sample(self.memory, self.batch_size)

        for state, action, reward, next_state, done in batch:
            # 确保state格式正确
            if isinstance(state, (int, float)):
                state = np.array([state])
            if isinstance(next_state, (int, float)):
                next_state = np.array([next_state])

            # 计算目标Q值
            if done:
                target_q = reward
            else:
                next_q_values, _ = self.forward(next_state)
                target_q = reward + self.gamma * np.max(next_q_values)

            # 前向传播
            q_values, h = self.forward(state)

            # 计算TD误差
            td_error = target_q - q_values[action]

            # 反向传播（简化版梯度下降）
            # 输出层梯度
            dq = np.zeros(self.n_actions)
            dq[action] = -td_error

            dW2 = np.outer(h, dq)
            db2 = dq

            # 隐藏层梯度
            dh = np.dot(dq, self.W2.T)
            dh[h <= 0] = 0  # ReLU梯度

            dW1 = np.outer(state, dh)
            db1 = dh

            # 更新权重
            self.W2 -= self.lr * dW2
            self.b2 -= self.lr * db2
            self.W1 -= self.lr * dW1
            self.b1 -= self.lr * db1

    def decay_epsilon(self):
        """衰减探索率"""
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

# ============================================================================
# 第1部分：Q-learning训练
# ============================================================================

def part1_qlearning():
    """演示Q-learning算法"""
    print("=" * 80)
    print("第1部分：Q-learning算法")
    print("=" * 80)

    # 创建环境和智能体
    env = WaterTankEnv()
    agent = QLearningAgent(n_states=20, n_actions=env.n_actions)

    # 训练参数
    n_episodes = 500
    max_steps = 200

    # 记录训练过程
    episode_rewards = []
    episode_lengths = []

    print("\n[开始Q-learning训练]")
    print(f"  训练回合数：{n_episodes}")
    print(f"  每回合最大步数：{max_steps}")

    # 训练循环
    for episode in range(n_episodes):
        state = env.reset()
        state_idx = agent.discretize_state(state)

        total_reward = 0
        step = 0

        for step in range(max_steps):
            # 选择动作
            action = agent.choose_action(state_idx)

            # 执行动作
            next_state, reward, done = env.step(action)
            next_state_idx = agent.discretize_state(next_state)

            # 学习
            agent.learn(state_idx, action, reward, next_state_idx, done)

            total_reward += reward
            state_idx = next_state_idx

            if done:
                break

        # 衰减探索率
        agent.decay_epsilon()

        episode_rewards.append(total_reward)
        episode_lengths.append(step + 1)

        if (episode + 1) % 100 == 0:
            avg_reward = np.mean(episode_rewards[-100:])
            print(f"  回合 {episode + 1}: 平均奖励 = {avg_reward:.2f}, ε = {agent.epsilon:.3f}")

    print(f"\n[训练完成]")
    print(f"  最终平均奖励：{np.mean(episode_rewards[-100:]):.2f}")
    print(f"  最终探索率：{agent.epsilon:.3f}")

    # 绘制学习曲线
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))

    # 平滑奖励曲线
    window = 50
    smoothed_rewards = np.convolve(episode_rewards, np.ones(window)/window, mode='valid')

    axes[0].plot(episode_rewards, alpha=0.3, label='原始奖励')
    axes[0].plot(range(window-1, len(episode_rewards)), smoothed_rewards, label=f'{window}回合平均', linewidth=2)
    axes[0].set_xlabel('回合数')
    axes[0].set_ylabel('累积奖励')
    axes[0].set_title('Q-learning学习曲线')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(episode_lengths, alpha=0.5)
    axes[1].set_xlabel('回合数')
    axes[1].set_ylabel('回合长度（步数）')
    axes[1].set_title('每回合步数')
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('case18_qlearning.png', dpi=150, bbox_inches='tight')
    plt.close()

    print("图表已保存：case18_qlearning.png\n")

    return agent

# ============================================================================
# 第2部分：SARSA训练
# ============================================================================

def part2_sarsa():
    """演示SARSA算法"""
    print("=" * 80)
    print("第2部分：SARSA算法")
    print("=" * 80)

    env = WaterTankEnv()
    agent = SARSAAgent(n_states=20, n_actions=env.n_actions)

    n_episodes = 500
    max_steps = 200

    episode_rewards = []

    print("\n[开始SARSA训练]")

    for episode in range(n_episodes):
        state = env.reset()
        state_idx = agent.discretize_state(state)
        action = agent.choose_action(state_idx)

        total_reward = 0

        for step in range(max_steps):
            # 执行动作
            next_state, reward, done = env.step(action)
            next_state_idx = agent.discretize_state(next_state)

            # 选择下一个动作（关键：SARSA需要实际选择）
            next_action = agent.choose_action(next_state_idx)

            # 学习（使用实际选择的next_action）
            agent.learn(state_idx, action, reward, next_state_idx, next_action, done)

            total_reward += reward
            state_idx = next_state_idx
            action = next_action

            if done:
                break

        agent.decay_epsilon()
        episode_rewards.append(total_reward)

        if (episode + 1) % 100 == 0:
            avg_reward = np.mean(episode_rewards[-100:])
            print(f"  回合 {episode + 1}: 平均奖励 = {avg_reward:.2f}, ε = {agent.epsilon:.3f}")

    print(f"\n[训练完成]")
    print(f"  最终平均奖励：{np.mean(episode_rewards[-100:]):.2f}")

    # 绘图
    plt.figure(figsize=(12, 5))
    window = 50
    smoothed_rewards = np.convolve(episode_rewards, np.ones(window)/window, mode='valid')

    plt.plot(episode_rewards, alpha=0.3, label='原始奖励')
    plt.plot(range(window-1, len(episode_rewards)), smoothed_rewards, label=f'{window}回合平均', linewidth=2)
    plt.xlabel('回合数')
    plt.ylabel('累积奖励')
    plt.title('SARSA学习曲线')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('case18_sarsa.png', dpi=150, bbox_inches='tight')
    plt.close()

    print("图表已保存：case18_sarsa.png\n")

    return agent

# ============================================================================
# 第3部分：DQN训练
# ============================================================================

def part3_dqn():
    """演示Deep Q-Network"""
    print("=" * 80)
    print("第3部分：Deep Q-Network (DQN)")
    print("=" * 80)

    env = WaterTankEnv()
    agent = SimpleDQN(state_dim=1, n_actions=env.n_actions)

    n_episodes = 500
    max_steps = 200

    episode_rewards = []

    print("\n[开始DQN训练]")
    print("  使用经验回放和神经网络Q函数逼近")

    for episode in range(n_episodes):
        state = env.reset()
        total_reward = 0

        for step in range(max_steps):
            # 选择动作
            action = agent.choose_action(state)

            # 执行动作
            next_state, reward, done = env.step(action)

            # 存储经验
            agent.remember(state, action, reward, next_state, done)

            # 经验回放学习
            agent.replay()

            total_reward += reward
            state = next_state

            if done:
                break

        agent.decay_epsilon()
        episode_rewards.append(total_reward)

        if (episode + 1) % 100 == 0:
            avg_reward = np.mean(episode_rewards[-100:])
            print(f"  回合 {episode + 1}: 平均奖励 = {avg_reward:.2f}, ε = {agent.epsilon:.3f}")

    print(f"\n[训练完成]")
    print(f"  最终平均奖励：{np.mean(episode_rewards[-100:]):.2f}")

    # 绘图
    plt.figure(figsize=(12, 5))
    window = 50
    smoothed_rewards = np.convolve(episode_rewards, np.ones(window)/window, mode='valid')

    plt.plot(episode_rewards, alpha=0.3, label='原始奖励')
    plt.plot(range(window-1, len(episode_rewards)), smoothed_rewards, label=f'{window}回合平均', linewidth=2)
    plt.xlabel('回合数')
    plt.ylabel('累积奖励')
    plt.title('DQN学习曲线')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('case18_dqn.png', dpi=150, bbox_inches='tight')
    plt.close()

    print("图表已保存：case18_dqn.png\n")

    return agent

# ============================================================================
# 第4部分：性能对比
# ============================================================================

def part4_comparison():
    """对比三种算法的性能"""
    print("=" * 80)
    print("第4部分：算法性能对比")
    print("=" * 80)

    # 这里简化对比，实际中应该保存训练好的智能体
    print("\n[三种算法特点对比]")
    print("\nQ-learning:")
    print("  - Off-policy学习")
    print("  - 使用max Q(s',a')更新")
    print("  - 收敛到最优策略")
    print("  - 适合确定性环境")

    print("\nSARSA:")
    print("  - On-policy学习")
    print("  - 使用实际选择的Q(s',a')更新")
    print("  - 考虑探索的影响")
    print("  - 更保守，适合风险敏感任务")

    print("\nDQN:")
    print("  - 使用神经网络逼近Q函数")
    print("  - 经验回放提高样本效率")
    print("  - 处理连续状态空间")
    print("  - 适合大规模问题")

    print("\n[应用建议]")
    print("  - 小规模、离散问题 → Q-learning")
    print("  - 风险敏感任务 → SARSA")
    print("  - 连续状态、大规模 → DQN")

# ============================================================================
# 第5部分：总结
# ============================================================================

def part5_summary():
    """总结强化学习控制"""
    print("=" * 80)
    print("第5部分：案例18总结")
    print("=" * 80)

    summary_text = """
[关键知识点]
  1. 强化学习基础：
     • 智能体通过与环境交互学习
     • 状态、动作、奖励、策略
     • 目标：最大化累积奖励

  2. Q-learning算法：
     • Off-policy学习
     • Bellman方程和Q值更新
     • ε-greedy探索策略
     • 收敛到最优策略

  3. SARSA算法：
     • On-policy学习
     • 使用实际选择的动作更新
     • 考虑探索的风险
     • 更保守的策略

  4. Deep Q-Network：
     • 神经网络逼近Q函数
     • 经验回放打破数据相关性
     • 目标网络稳定训练
     • 处理连续状态空间

[工程应用]
  • 自动驾驶、机器人控制
  • 游戏AI、资源管理
  • 推荐系统、对话系统
  • 任何需要序列决策的问题

[实用建议]
  • 仔细设计奖励函数
  • 充分探索状态空间
  • 监控学习曲线
  • 调整超参数（α, γ, ε）
  • 在仿真中充分训练

[优势与挑战]
  优势：
    • 无需精确模型
    • 自动发现最优策略
    • 适应环境变化

  挑战：
    • 需要大量样本
    • 训练时间长
    • 超参数敏感
    • 安全性难保证

[下一步学习]
  → 案例19：综合对比与性能评估
  → 高级RL算法：DDPG、TD3、SAC、PPO
"""
    print(summary_text)

    print("=" * 80)
    print("案例18演示完成！")
    print("=" * 80)

# ============================================================================
# 主程序
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("案例18：强化学习控制 - 智能体学习最优策略")
    print("=" * 80)

    # 第1部分：Q-learning
    part1_qlearning()

    # 第2部分：SARSA
    part2_sarsa()

    # 第3部分：DQN
    part3_dqn()

    # 第4部分：对比
    part4_comparison()

    # 第5部分：总结
    part5_summary()
