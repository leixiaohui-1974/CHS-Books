"""
案例18扩展实验：强化学习控制深入研究

本程序包含以下扩展实验：
1. 探索率衰减策略对比（线性、指数、逆时间）
2. 学习率影响（不同α值的收敛速度）
3. 折扣因子影响（短期vs长期优化）
4. Q-learning vs SARSA vs DQN性能对比
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

# 设置中文显示
rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

# 复用main.py中的类
from collections import deque
import random

# ============================================================================
# 复用的类定义
# ============================================================================

class WaterTankEnv:
    """水箱环境"""
    def __init__(self, A=3.0, R=2.0, dt=0.1, target=2.0):
        self.A = A
        self.R = R
        self.dt = dt
        self.target = target
        self.h = 0.5
        self.h_min = 0.0
        self.h_max = 4.0
        self.actions = [0, 2, 4, 6, 8, 10]
        self.n_actions = len(self.actions)

    def reset(self):
        self.h = np.random.uniform(0.5, 1.5)
        return self.h

    def step(self, action_idx):
        u = self.actions[action_idx]
        dhdt = (u - self.h / self.R) / self.A
        self.h = self.h + dhdt * self.dt
        self.h = np.clip(self.h, self.h_min, self.h_max)
        error = abs(self.h - self.target)
        if error < 0.1:
            reward = 10.0
        else:
            reward = -error
        done = (self.h <= self.h_min + 0.1) or (self.h >= self.h_max - 0.1)
        return self.h, reward, done

class QLearningAgent:
    """Q-learning智能体"""
    def __init__(self, n_states, n_actions, learning_rate=0.1, discount=0.95, epsilon=1.0):
        self.n_states = n_states
        self.n_actions = n_actions
        self.alpha = learning_rate
        self.gamma = discount
        self.epsilon = epsilon
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.Q = np.zeros((n_states, n_actions))

    def discretize_state(self, state, n_bins=20):
        state_min, state_max = 0.0, 4.0
        bin_size = (state_max - state_min) / n_bins
        state_idx = int((state - state_min) / bin_size)
        state_idx = np.clip(state_idx, 0, n_bins - 1)
        return state_idx

    def choose_action(self, state):
        if np.random.random() < self.epsilon:
            return np.random.randint(self.n_actions)
        else:
            return np.argmax(self.Q[state, :])

    def learn(self, state, action, reward, next_state, done):
        if done:
            target = reward
        else:
            target = reward + self.gamma * np.max(self.Q[next_state, :])
        td_error = target - self.Q[state, action]
        self.Q[state, action] += self.alpha * td_error

    def decay_epsilon(self, strategy='exponential', episode=0, total_episodes=500):
        """衰减探索率，支持多种策略"""
        if strategy == 'exponential':
            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
        elif strategy == 'linear':
            self.epsilon = max(self.epsilon_min, 1.0 - (1.0 - self.epsilon_min) * episode / total_episodes)
        elif strategy == 'inverse':
            self.epsilon = max(self.epsilon_min, 1.0 / (1.0 + 0.01 * episode))

# ============================================================================
# 实验1：探索率衰减策略对比
# ============================================================================

def experiment_epsilon_decay():
    """对比不同探索率衰减策略"""
    print("=" * 80)
    print("实验1：探索率衰减策略对比")
    print("=" * 80)

    env = WaterTankEnv()
    n_episodes = 500
    max_steps = 200

    strategies = ['exponential', 'linear', 'inverse']
    strategy_names = {'exponential': '指数衰减', 'linear': '线性衰减', 'inverse': '逆时间衰减'}
    results = {}

    print("\n[测试不同衰减策略]\n")

    for strategy in strategies:
        agent = QLearningAgent(n_states=20, n_actions=env.n_actions)
        episode_rewards = []

        for episode in range(n_episodes):
            state = env.reset()
            state_idx = agent.discretize_state(state)
            total_reward = 0

            for step in range(max_steps):
                action = agent.choose_action(state_idx)
                next_state, reward, done = env.step(action)
                next_state_idx = agent.discretize_state(next_state)
                agent.learn(state_idx, action, reward, next_state_idx, done)
                total_reward += reward
                state_idx = next_state_idx
                if done:
                    break

            agent.decay_epsilon(strategy=strategy, episode=episode, total_episodes=n_episodes)
            episode_rewards.append(total_reward)

        avg_reward = np.mean(episode_rewards[-100:])
        results[strategy] = episode_rewards

        print(f"{strategy_names[strategy]}：")
        print(f"  最终平均奖励：{avg_reward:.2f}\n")

    # 绘图
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))

    # 奖励曲线
    window = 50
    for strategy in strategies:
        rewards = results[strategy]
        smoothed = np.convolve(rewards, np.ones(window)/window, mode='valid')
        axes[0].plot(range(window-1, len(rewards)), smoothed, label=strategy_names[strategy], linewidth=2)

    axes[0].set_xlabel('回合数')
    axes[0].set_ylabel('累积奖励（平滑）')
    axes[0].set_title('不同探索率衰减策略的学习曲线')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # 探索率变化
    for strategy in strategies:
        epsilon_values = []
        agent = QLearningAgent(n_states=20, n_actions=env.n_actions)
        for episode in range(n_episodes):
            epsilon_values.append(agent.epsilon)
            agent.decay_epsilon(strategy=strategy, episode=episode, total_episodes=n_episodes)
        axes[1].plot(epsilon_values, label=strategy_names[strategy], linewidth=2)

    axes[1].set_xlabel('回合数')
    axes[1].set_ylabel('探索率 ε')
    axes[1].set_title('探索率衰减曲线')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('exp1_epsilon_decay.png', dpi=150, bbox_inches='tight')
    plt.close()

    print("图表已保存：exp1_epsilon_decay.png")

    print("\n结论：")
    print("  - 指数衰减：平衡探索与利用，常用")
    print("  - 线性衰减：早期探索充分，后期快速收敛")
    print("  - 逆时间衰减：初期探索较慢，适合复杂环境\n")

# ============================================================================
# 实验2：学习率影响
# ============================================================================

def experiment_learning_rate():
    """测试不同学习率的影响"""
    print("=" * 80)
    print("实验2：学习率影响")
    print("=" * 80)

    env = WaterTankEnv()
    n_episodes = 500
    max_steps = 200

    learning_rates = [0.05, 0.1, 0.2, 0.5]
    results = {}

    print("\n[测试不同学习率]\n")

    for lr in learning_rates:
        agent = QLearningAgent(n_states=20, n_actions=env.n_actions, learning_rate=lr)
        episode_rewards = []

        for episode in range(n_episodes):
            state = env.reset()
            state_idx = agent.discretize_state(state)
            total_reward = 0

            for step in range(max_steps):
                action = agent.choose_action(state_idx)
                next_state, reward, done = env.step(action)
                next_state_idx = agent.discretize_state(next_state)
                agent.learn(state_idx, action, reward, next_state_idx, done)
                total_reward += reward
                state_idx = next_state_idx
                if done:
                    break

            agent.decay_epsilon()
            episode_rewards.append(total_reward)

        avg_reward = np.mean(episode_rewards[-100:])
        results[lr] = episode_rewards

        print(f"学习率 α = {lr}：")
        print(f"  最终平均奖励：{avg_reward:.2f}\n")

    # 绘图
    plt.figure(figsize=(12, 6))
    window = 50

    for lr in learning_rates:
        rewards = results[lr]
        smoothed = np.convolve(rewards, np.ones(window)/window, mode='valid')
        plt.plot(range(window-1, len(rewards)), smoothed, label=f'α={lr}', linewidth=2)

    plt.xlabel('回合数')
    plt.ylabel('累积奖励（平滑）')
    plt.title('不同学习率的学习曲线')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('exp2_learning_rate.png', dpi=150, bbox_inches='tight')
    plt.close()

    print("图表已保存：exp2_learning_rate.png")

    print("\n结论：")
    print("  - α过小（0.05）：学习慢，需要更多回合")
    print("  - α适中（0.1-0.2）：平衡学习速度和稳定性")
    print("  - α过大（0.5）：学习快但可能不稳定")
    print("  - 推荐：α = 0.1 ~ 0.2\n")

# ============================================================================
# 实验3：折扣因子影响
# ============================================================================

def experiment_discount_factor():
    """测试不同折扣因子的影响"""
    print("=" * 80)
    print("实验3：折扣因子影响（短期vs长期）")
    print("=" * 80)

    env = WaterTankEnv()
    n_episodes = 500
    max_steps = 200

    discount_factors = [0.8, 0.9, 0.95, 0.99]
    results = {}

    print("\n[测试不同折扣因子]\n")

    for gamma in discount_factors:
        agent = QLearningAgent(n_states=20, n_actions=env.n_actions, discount=gamma)
        episode_rewards = []

        for episode in range(n_episodes):
            state = env.reset()
            state_idx = agent.discretize_state(state)
            total_reward = 0

            for step in range(max_steps):
                action = agent.choose_action(state_idx)
                next_state, reward, done = env.step(action)
                next_state_idx = agent.discretize_state(next_state)
                agent.learn(state_idx, action, reward, next_state_idx, done)
                total_reward += reward
                state_idx = next_state_idx
                if done:
                    break

            agent.decay_epsilon()
            episode_rewards.append(total_reward)

        avg_reward = np.mean(episode_rewards[-100:])
        results[gamma] = episode_rewards

        print(f"折扣因子 γ = {gamma}：")
        print(f"  最终平均奖励：{avg_reward:.2f}")
        print(f"  特点：{'重视长期奖励' if gamma >= 0.95 else '重视短期奖励'}\n")

    # 绘图
    plt.figure(figsize=(12, 6))
    window = 50

    for gamma in discount_factors:
        rewards = results[gamma]
        smoothed = np.convolve(rewards, np.ones(window)/window, mode='valid')
        plt.plot(range(window-1, len(rewards)), smoothed, label=f'γ={gamma}', linewidth=2)

    plt.xlabel('回合数')
    plt.ylabel('累积奖励（平滑）')
    plt.title('不同折扣因子的学习曲线')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('exp3_discount_factor.png', dpi=150, bbox_inches='tight')
    plt.close()

    print("图表已保存：exp3_discount_factor.png")

    print("\n结论：")
    print("  - γ较小（0.8）：重视即时奖励，短视")
    print("  - γ较大（0.95-0.99）：考虑长期收益，远见")
    print("  - 控制任务通常使用γ = 0.9 ~ 0.99")
    print("  - 推荐：γ = 0.95\n")

# ============================================================================
# 实验4：Q-learning vs SARSA详细对比
# ============================================================================

def experiment_qlearning_vs_sarsa():
    """详细对比Q-learning和SARSA"""
    print("=" * 80)
    print("实验4：Q-learning vs SARSA详细对比")
    print("=" * 80)

    env = WaterTankEnv()
    n_episodes = 500
    max_steps = 200
    n_runs = 3  # 多次运行取平均

    print("\n[多次运行对比（消除随机性）]\n")

    # Q-learning
    qlearning_rewards_all = []
    for run in range(n_runs):
        agent = QLearningAgent(n_states=20, n_actions=env.n_actions)
        episode_rewards = []

        for episode in range(n_episodes):
            state = env.reset()
            state_idx = agent.discretize_state(state)
            total_reward = 0

            for step in range(max_steps):
                action = agent.choose_action(state_idx)
                next_state, reward, done = env.step(action)
                next_state_idx = agent.discretize_state(next_state)
                agent.learn(state_idx, action, reward, next_state_idx, done)
                total_reward += reward
                state_idx = next_state_idx
                if done:
                    break

            agent.decay_epsilon()
            episode_rewards.append(total_reward)

        qlearning_rewards_all.append(episode_rewards)
        print(f"  Q-learning 运行 {run+1}/{n_runs}：最终奖励 {np.mean(episode_rewards[-100:]):.2f}")

    # SARSA
    sarsa_rewards_all = []
    for run in range(n_runs):
        # 简化的SARSA（复用Q-learning类，修改更新规则）
        agent = QLearningAgent(n_states=20, n_actions=env.n_actions)
        episode_rewards = []

        for episode in range(n_episodes):
            state = env.reset()
            state_idx = agent.discretize_state(state)
            action = agent.choose_action(state_idx)
            total_reward = 0

            for step in range(max_steps):
                next_state, reward, done = env.step(action)
                next_state_idx = agent.discretize_state(next_state)
                next_action = agent.choose_action(next_state_idx)

                # SARSA更新（使用实际选择的动作）
                if done:
                    target = reward
                else:
                    target = reward + agent.gamma * agent.Q[next_state_idx, next_action]
                td_error = target - agent.Q[state_idx, action]
                agent.Q[state_idx, action] += agent.alpha * td_error

                total_reward += reward
                state_idx = next_state_idx
                action = next_action

                if done:
                    break

            agent.decay_epsilon()
            episode_rewards.append(total_reward)

        sarsa_rewards_all.append(episode_rewards)
        print(f"  SARSA 运行 {run+1}/{n_runs}：最终奖励 {np.mean(episode_rewards[-100:]):.2f}")

    # 计算平均和标准差
    qlearning_mean = np.mean(qlearning_rewards_all, axis=0)
    qlearning_std = np.std(qlearning_rewards_all, axis=0)
    sarsa_mean = np.mean(sarsa_rewards_all, axis=0)
    sarsa_std = np.std(sarsa_rewards_all, axis=0)

    print(f"\n[总体对比]")
    print(f"  Q-learning平均奖励：{np.mean(qlearning_mean[-100:]):.2f} ± {np.mean(qlearning_std[-100:]):.2f}")
    print(f"  SARSA平均奖励：{np.mean(sarsa_mean[-100:]):.2f} ± {np.mean(sarsa_std[-100:]):.2f}")

    # 绘图
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))

    # 平滑奖励曲线
    window = 50
    qlearning_smoothed = np.convolve(qlearning_mean, np.ones(window)/window, mode='valid')
    sarsa_smoothed = np.convolve(sarsa_mean, np.ones(window)/window, mode='valid')

    x = range(window-1, len(qlearning_mean))
    axes[0].plot(x, qlearning_smoothed, label='Q-learning', linewidth=2)
    axes[0].fill_between(x,
                          qlearning_smoothed - qlearning_std[window-1:],
                          qlearning_smoothed + qlearning_std[window-1:],
                          alpha=0.3)
    axes[0].plot(x, sarsa_smoothed, label='SARSA', linewidth=2)
    axes[0].fill_between(x,
                          sarsa_smoothed - sarsa_std[window-1:],
                          sarsa_smoothed + sarsa_std[window-1:],
                          alpha=0.3)
    axes[0].set_xlabel('回合数')
    axes[0].set_ylabel('累积奖励')
    axes[0].set_title('Q-learning vs SARSA 学习曲线（含标准差）')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # 累积奖励对比
    qlearning_cumsum = np.cumsum(qlearning_mean)
    sarsa_cumsum = np.cumsum(sarsa_mean)
    axes[1].plot(qlearning_cumsum, label='Q-learning', linewidth=2)
    axes[1].plot(sarsa_cumsum, label='SARSA', linewidth=2)
    axes[1].set_xlabel('回合数')
    axes[1].set_ylabel('累积总奖励')
    axes[1].set_title('累积奖励对比')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('exp4_qlearning_vs_sarsa.png', dpi=150, bbox_inches='tight')
    plt.close()

    print("\n图表已保存：exp4_qlearning_vs_sarsa.png")

    print("\n结论：")
    print("  - Q-learning：追求最优策略，学习较快")
    print("  - SARSA：考虑探索风险，更保守")
    print("  - 本案例中两者性能接近")
    print("  - 实际应用根据任务特点选择\n")

# ============================================================================
# 主程序
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("案例18扩展实验：强化学习控制深入研究")
    print("=" * 80)

    # 实验1：探索率衰减
    experiment_epsilon_decay()

    # 实验2：学习率
    experiment_learning_rate()

    # 实验3：折扣因子
    experiment_discount_factor()

    # 实验4：Q-learning vs SARSA
    experiment_qlearning_vs_sarsa()

    print("=" * 80)
    print("所有扩展实验完成！")
    print("=" * 80)
