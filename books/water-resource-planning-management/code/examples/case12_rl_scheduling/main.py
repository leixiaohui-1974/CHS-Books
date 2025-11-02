"""
案例4.3：强化学习水库优化调度 - 主程序

对比贪心策略和Q-Learning

作者：教材编写组
日期：2025-11-02
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../"))

import numpy as np
import matplotlib.pyplot as plt
import time

from src import ReservoirEnv, QLearningAgent


class RLSchedulingSystem:
    """强化学习调度系统"""
    
    def __init__(self):
        self.results_dir = Path("results")
        self.results_dir.mkdir(exist_ok=True)
        (self.results_dir / "figures").mkdir(exist_ok=True)
        
        # 创建环境
        self.env = ReservoirEnv(
            min_storage=50,
            max_storage=500,
            normal_storage=400,
            min_discharge=50,
            max_discharge=500,
            n_actions=10,
            n_periods=12,
            inflow_mean=200,
            inflow_std=50
        )
        
        print(f"强化学习调度系统初始化完成")
        print(f"  状态空间: [库容, 入流, 时段]")
        print(f"  动作空间: {self.env.n_actions}个离散动作")
        print(f"  调度时段: {self.env.n_periods}个")
    
    def method1_greedy(self, n_episodes=10):
        """方法1：贪心策略（基准）"""
        print("\n" + "=" * 70)
        print("方法1: 贪心策略（当前最优）")
        print("=" * 70)
        
        episode_rewards = []
        episode_powers = []
        
        for episode in range(n_episodes):
            state = self.env.reset()
            episode_reward = 0
            done = False
            
            while not done:
                # 贪心策略：选择能产生最大即时奖励的动作
                best_action = 0
                best_reward = -np.inf
                
                for action_idx in range(self.env.n_actions):
                    # 模拟执行
                    test_env = ReservoirEnv(
                        min_storage=self.env.min_storage,
                        max_storage=self.env.max_storage,
                        normal_storage=self.env.normal_storage,
                        min_discharge=self.env.min_discharge,
                        max_discharge=self.env.max_discharge,
                        n_actions=self.env.n_actions,
                        n_periods=self.env.n_periods
                    )
                    test_env.current_storage = self.env.current_storage
                    test_env.current_inflow = self.env.current_inflow
                    test_env.current_period = self.env.current_period
                    
                    _, reward, _, _ = test_env.step(action_idx)
                    
                    if reward > best_reward:
                        best_reward = reward
                        best_action = action_idx
                
                # 执行最优动作
                next_state, reward, done, info = self.env.step(best_action)
                episode_reward += reward
            
            episode_rewards.append(episode_reward)
            episode_powers.append(np.sum(self.env.episode_power))
        
        avg_reward = np.mean(episode_rewards)
        avg_power = np.mean(episode_powers)
        
        print(f"\n平均累积奖励: {avg_reward:.2f}")
        print(f"平均总发电量: {avg_power:.2f} MW·h")
        
        return {
            'method': '贪心策略',
            'rewards': episode_rewards,
            'powers': episode_powers,
            'avg_reward': avg_reward,
            'avg_power': avg_power
        }
    
    def method2_q_learning(self, n_episodes=1000):
        """方法2：Q-Learning"""
        print("\n" + "=" * 70)
        print("方法2: Q-Learning强化学习")
        print("=" * 70)
        
        start_time = time.time()
        
        # 创建Q-Learning智能体
        n_bins = 10  # 每个状态维度的离散化数量
        n_states = n_bins ** 3  # 3维状态空间
        
        agent = QLearningAgent(
            n_states=n_states,
            n_actions=self.env.n_actions,
            learning_rate=0.1,
            discount_factor=0.95,
            epsilon=1.0,  # 初始探索率
            epsilon_decay=0.995,
            epsilon_min=0.01
        )
        
        print(f"\n开始训练... ({n_episodes}轮)")
        
        # 训练
        training_rewards = agent.train(self.env, n_episodes=n_episodes, verbose=True)
        
        training_time = time.time() - start_time
        
        print(f"\n训练完成！耗时: {training_time:.2f} 秒")
        
        # 评估
        print("\n评估学习到的策略...")
        avg_reward, results = agent.evaluate(self.env, n_episodes=10)
        
        episode_rewards = [r['reward'] for r in results]
        episode_powers = [r['power'] for r in results]
        
        avg_power = np.mean(episode_powers)
        
        print(f"\n平均累积奖励: {avg_reward:.2f}")
        print(f"平均总发电量: {avg_power:.2f} MW·h")
        
        return {
            'method': 'Q-Learning',
            'training_rewards': training_rewards,
            'rewards': episode_rewards,
            'powers': episode_powers,
            'avg_reward': avg_reward,
            'avg_power': avg_power,
            'time': training_time
        }
    
    def visualize(self, greedy_result, ql_result):
        """结果可视化"""
        print("\n" + "=" * 70)
        print("结果可视化")
        print("=" * 70)
        
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
        plt.rcParams['axes.unicode_minus'] = False
        
        fig = plt.figure(figsize=(16, 10))
        
        # 创建网格布局
        gs = fig.add_gridspec(2, 3, hspace=0.3, wspace=0.3)
        
        # 1. Q-Learning学习曲线
        ax1 = fig.add_subplot(gs[0, :2])
        training_rewards = ql_result['training_rewards']
        
        # 滑动平均
        window = 50
        moving_avg = np.convolve(training_rewards, np.ones(window)/window, mode='valid')
        
        ax1.plot(training_rewards, alpha=0.3, color='#4ECDC4', label='原始奖励')
        ax1.plot(range(window-1, len(training_rewards)), moving_avg,
                color='#45B7D1', linewidth=2, label=f'{window}轮平均')
        ax1.axhline(y=greedy_result['avg_reward'], color='#FF6B6B',
                   linestyle='--', linewidth=2, label='贪心策略基准')
        
        ax1.set_xlabel('训练轮数', fontsize=11)
        ax1.set_ylabel('累积奖励', fontsize=11)
        ax1.set_title('Q-Learning学习曲线', fontsize=13, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. 平均奖励对比
        ax2 = fig.add_subplot(gs[0, 2])
        methods = ['贪心策略', 'Q-Learning']
        rewards = [greedy_result['avg_reward'], ql_result['avg_reward']]
        colors = ['#FF6B6B', '#4ECDC4']
        
        bars = ax2.bar(methods, rewards, color=colors, alpha=0.7)
        ax2.set_ylabel('平均累积奖励', fontsize=11)
        ax2.set_title('累积奖励对比', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='y')
        
        for bar, reward in zip(bars, rewards):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{reward:.1f}',
                    ha='center', va='bottom', fontsize=10)
        
        # 3. 发电量对比
        ax3 = fig.add_subplot(gs[1, 0])
        powers = [greedy_result['avg_power'], ql_result['avg_power']]
        
        bars = ax3.bar(methods, powers, color=colors, alpha=0.7)
        ax3.set_ylabel('平均总发电量 (MW·h)', fontsize=11)
        ax3.set_title('发电量对比', fontsize=12, fontweight='bold')
        ax3.grid(True, alpha=0.3, axis='y')
        
        for bar, power in zip(bars, powers):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height,
                    f'{power:.0f}',
                    ha='center', va='bottom', fontsize=10)
        
        # 4. 奖励分布箱线图
        ax4 = fig.add_subplot(gs[1, 1])
        data = [greedy_result['rewards'], ql_result['rewards']]
        
        bp = ax4.boxplot(data, labels=methods, patch_artist=True)
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        
        ax4.set_ylabel('累积奖励', fontsize=11)
        ax4.set_title('奖励分布', fontsize=12, fontweight='bold')
        ax4.grid(True, alpha=0.3, axis='y')
        
        # 5. 性能提升
        ax5 = fig.add_subplot(gs[1, 2])
        improvement = (ql_result['avg_reward'] - greedy_result['avg_reward']) / abs(greedy_result['avg_reward']) * 100
        power_improvement = (ql_result['avg_power'] - greedy_result['avg_power']) / greedy_result['avg_power'] * 100
        
        metrics = ['奖励提升', '发电量提升']
        improvements = [improvement, power_improvement]
        
        bars = ax5.bar(metrics, improvements, color=['#45B7D1', '#95E1D3'], alpha=0.7)
        ax5.set_ylabel('提升百分比 (%)', fontsize=11)
        ax5.set_title('Q-Learning相对贪心策略的提升', fontsize=12, fontweight='bold')
        ax5.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
        ax5.grid(True, alpha=0.3, axis='y')
        
        for bar, imp in zip(bars, improvements):
            height = bar.get_height()
            ax5.text(bar.get_x() + bar.get_width()/2., height,
                    f'{imp:+.1f}%',
                    ha='center', va='bottom' if imp > 0 else 'top', fontsize=10)
        
        plt.savefig(self.results_dir / "figures/rl_comparison.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"  已保存: figures/rl_comparison.png")
    
    def run(self):
        """运行完整强化学习调度"""
        print("\n" + "*" * 70)
        print(" " * 18 + "强化学习水库优化调度")
        print(" " * 28 + "案例4.3")
        print("*" * 70)
        
        try:
            greedy_result = self.method1_greedy(n_episodes=10)
            ql_result = self.method2_q_learning(n_episodes=1000)
            
            self.visualize(greedy_result, ql_result)
            
            print("\n" + "=" * 70)
            print("强化学习调度完成！")
            print("=" * 70)
            
            # 性能总结
            print(f"\n性能总结:")
            print(f"\n  贪心策略:")
            print(f"    平均累积奖励: {greedy_result['avg_reward']:.2f}")
            print(f"    平均总发电量: {greedy_result['avg_power']:.2f} MW·h")
            
            print(f"\n  Q-Learning:")
            print(f"    平均累积奖励: {ql_result['avg_reward']:.2f}")
            print(f"    平均总发电量: {ql_result['avg_power']:.2f} MW·h")
            print(f"    训练时间: {ql_result['time']:.2f} 秒")
            
            improvement = (ql_result['avg_reward'] - greedy_result['avg_reward']) / abs(greedy_result['avg_reward']) * 100
            print(f"\n  Q-Learning相对贪心策略提升: {improvement:+.1f}%")
            
        except Exception as e:
            print(f"\n错误: {e}")
            import traceback
            traceback.print_exc()


def main():
    """主函数"""
    system = RLSchedulingSystem()
    system.run()


if __name__ == "__main__":
    main()
