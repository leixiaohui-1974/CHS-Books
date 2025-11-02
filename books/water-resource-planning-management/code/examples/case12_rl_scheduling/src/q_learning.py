"""
Q-Learning智能体

实现表格式Q-Learning算法
"""

import numpy as np
from typing import List, Tuple


class QLearningAgent:
    """
    Q-Learning智能体
    
    使用表格存储Q值
    """
    
    def __init__(
        self,
        n_states: int,
        n_actions: int,
        learning_rate: float = 0.1,
        discount_factor: float = 0.95,
        epsilon: float = 0.1,
        epsilon_decay: float = 0.995,
        epsilon_min: float = 0.01
    ):
        """
        初始化Q-Learning智能体
        
        Parameters
        ----------
        n_states : int
            状态数量（离散化后）
        n_actions : int
            动作数量
        learning_rate : float
            学习率α
        discount_factor : float
            折扣因子γ
        epsilon : float
            初始探索率ε
        epsilon_decay : float
            探索率衰减
        epsilon_min : float
            最小探索率
        """
        self.n_states = n_states
        self.n_actions = n_actions
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        
        # Q表初始化（乐观初始值）
        self.q_table = np.ones((n_states, n_actions)) * 10
        
        # 历史记录
        self.episode_rewards = []
    
    def discretize_state(self, state: np.ndarray, n_bins: int = 10) -> int:
        """
        离散化连续状态
        
        Parameters
        ----------
        state : np.ndarray
            连续状态 [storage, inflow, period]
        n_bins : int
            每个维度的离散化数量
        
        Returns
        -------
        int
            离散状态索引
        """
        # 将每个状态维度离散化到[0, n_bins-1]
        discrete = np.floor(state * n_bins).astype(int)
        discrete = np.clip(discrete, 0, n_bins - 1)
        
        # 转换为一维索引
        state_idx = discrete[0] * (n_bins ** 2) + discrete[1] * n_bins + discrete[2]
        state_idx = min(state_idx, self.n_states - 1)
        
        return state_idx
    
    def choose_action(self, state_idx: int, training: bool = True) -> int:
        """
        选择动作（ε-贪心策略）
        
        Parameters
        ----------
        state_idx : int
            状态索引
        training : bool
            是否训练模式
        
        Returns
        -------
        int
            动作索引
        """
        if training and np.random.rand() < self.epsilon:
            # 探索：随机动作
            action = np.random.randint(self.n_actions)
        else:
            # 利用：最优动作
            action = np.argmax(self.q_table[state_idx])
        
        return action
    
    def update(
        self,
        state_idx: int,
        action: int,
        reward: float,
        next_state_idx: int,
        done: bool
    ):
        """
        更新Q值
        
        Q(s,a) ← Q(s,a) + α[r + γ·max Q(s',a') - Q(s,a)]
        
        Parameters
        ----------
        state_idx : int
            当前状态
        action : int
            执行动作
        reward : float
            获得奖励
        next_state_idx : int
            下一状态
        done : bool
            是否结束
        """
        current_q = self.q_table[state_idx, action]
        
        if done:
            target_q = reward
        else:
            max_next_q = np.max(self.q_table[next_state_idx])
            target_q = reward + self.discount_factor * max_next_q
        
        # Q值更新
        self.q_table[state_idx, action] += self.learning_rate * (target_q - current_q)
    
    def decay_epsilon(self):
        """衰减探索率"""
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
    
    def train(
        self,
        env,
        n_episodes: int = 1000,
        verbose: bool = True
    ) -> List[float]:
        """
        训练智能体
        
        Parameters
        ----------
        env : ReservoirEnv
            环境
        n_episodes : int
            训练轮数
        verbose : bool
            是否打印信息
        
        Returns
        -------
        List[float]
            每轮累积奖励
        """
        episode_rewards = []
        
        for episode in range(n_episodes):
            state = env.reset()
            state_idx = self.discretize_state(state)
            
            episode_reward = 0
            done = False
            
            while not done:
                # 选择动作
                action = self.choose_action(state_idx, training=True)
                
                # 执行动作
                next_state, reward, done, info = env.step(action)
                next_state_idx = self.discretize_state(next_state)
                
                # 更新Q值
                self.update(state_idx, action, reward, next_state_idx, done)
                
                # 更新状态
                state_idx = next_state_idx
                episode_reward += reward
            
            # 衰减探索率
            self.decay_epsilon()
            
            # 记录
            episode_rewards.append(episode_reward)
            
            # 打印
            if verbose and (episode + 1) % 100 == 0:
                avg_reward = np.mean(episode_rewards[-100:])
                print(f"Episode {episode+1}/{n_episodes}, "
                      f"Avg Reward (last 100): {avg_reward:.2f}, "
                      f"ε: {self.epsilon:.3f}")
        
        self.episode_rewards = episode_rewards
        return episode_rewards
    
    def evaluate(self, env, n_episodes: int = 10) -> Tuple[float, List]:
        """
        评估智能体
        
        Parameters
        ----------
        env : ReservoirEnv
            环境
        n_episodes : int
            评估轮数
        
        Returns
        -------
        Tuple[float, List]
            (平均奖励, 详细结果列表)
        """
        total_rewards = []
        results = []
        
        for _ in range(n_episodes):
            state = env.reset()
            state_idx = self.discretize_state(state)
            
            episode_reward = 0
            done = False
            
            while not done:
                # 贪心策略（不探索）
                action = self.choose_action(state_idx, training=False)
                
                # 执行
                next_state, reward, done, info = env.step(action)
                next_state_idx = self.discretize_state(next_state)
                
                # 更新
                state_idx = next_state_idx
                episode_reward += reward
            
            total_rewards.append(episode_reward)
            results.append({
                'reward': episode_reward,
                'power': np.sum(env.episode_power),
                'storage': env.episode_storage
            })
        
        avg_reward = np.mean(total_rewards)
        
        return avg_reward, results
