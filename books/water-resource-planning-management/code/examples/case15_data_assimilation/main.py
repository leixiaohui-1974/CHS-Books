"""
案例5.3：实时数据同化与预测 - 主程序

对比仅模型、仅观测和数据同化方法

作者：教材编写组
日期：2025-11-02
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../"))

import numpy as np
import matplotlib.pyplot as plt

from core.digital_twin import KalmanFilter


class DataAssimilationSystem:
    """数据同化系统"""
    
    def __init__(self):
        self.results_dir = Path("results")
        self.results_dir.mkdir(exist_ok=True)
        (self.results_dir / "figures").mkdir(exist_ok=True)
        
        print(f"数据同化系统初始化完成")
    
    def generate_true_state(self, n_steps=100):
        """生成真实状态（模拟）"""
        # 模拟水位变化（含趋势和周期）
        t = np.arange(n_steps)
        
        # 基础水位 + 趋势 + 周期 + 噪声
        base = 190
        trend = 0.05 * t
        seasonal = 3 * np.sin(2 * np.pi * t / 24)
        noise = np.random.randn(n_steps) * 0.5
        
        true_state = base + trend + seasonal + noise
        
        return true_state
    
    def method1_model_only(self, true_state):
        """方法1：仅模型预测"""
        print("\n" + "=" * 70)
        print("方法1: 仅物理模型预测（无数据同化）")
        print("=" * 70)
        
        n_steps = len(true_state)
        predictions = []
        
        # 初始状态
        x = true_state[0]
        
        for t in range(n_steps):
            # 简单模型：持续上一时刻状态 + 小扰动
            x = x + 0.05 + np.random.randn() * 0.3
            predictions.append(x)
        
        predictions = np.array(predictions)
        rmse = np.sqrt(np.mean((true_state - predictions) ** 2))
        
        print(f"\n预测RMSE: {rmse:.3f} m")
        
        return {
            'method': '仅模型',
            'predictions': predictions,
            'rmse': rmse
        }
    
    def method2_observation_only(self, true_state, obs_frequency=5):
        """方法2：仅观测外推"""
        print("\n" + "=" * 70)
        print(f"方法2: 仅观测外推（每{obs_frequency}步观测一次）")
        print("=" * 70)
        
        n_steps = len(true_state)
        predictions = []
        
        last_obs = true_state[0]
        last_obs_time = 0
        
        for t in range(n_steps):
            # 每obs_frequency步观测一次
            if t % obs_frequency == 0:
                last_obs = true_state[t] + np.random.randn() * 0.5  # 加测量噪声
                last_obs_time = t
            
            # 线性外推
            if t > last_obs_time:
                # 简单持续
                pred = last_obs
            else:
                pred = last_obs
            
            predictions.append(pred)
        
        predictions = np.array(predictions)
        rmse = np.sqrt(np.mean((true_state - predictions) ** 2))
        
        print(f"\n预测RMSE: {rmse:.3f} m")
        
        return {
            'method': '仅观测',
            'predictions': predictions,
            'rmse': rmse
        }
    
    def method3_data_assimilation(self, true_state, obs_frequency=5):
        """方法3：数据同化"""
        print("\n" + "=" * 70)
        print(f"方法3: 数据同化（卡尔曼滤波）")
        print("=" * 70)
        
        n_steps = len(true_state)
        
        # 创建卡尔曼滤波器
        kf = KalmanFilter(dim_x=1, dim_z=1)
        
        # 状态转移（简单持续模型）
        kf.F = np.array([[1.0]])
        kf.H = np.array([[1.0]])
        
        # 误差协方差
        kf.Q = np.array([[0.3 ** 2]])  # 模型误差
        kf.R = np.array([[0.5 ** 2]])  # 观测误差
        
        # 初始化
        kf.x = np.array([[true_state[0]]])
        kf.P = np.array([[1.0]])
        
        predictions = []
        
        for t in range(n_steps):
            # 预测（模型）
            kf.predict()
            
            # 同化（观测）
            if t % obs_frequency == 0:
                # 获取观测
                obs = true_state[t] + np.random.randn() * 0.5
                kf.update(np.array([obs]))
            
            # 记录预测
            predictions.append(kf.x[0, 0])
        
        predictions = np.array(predictions)
        rmse = np.sqrt(np.mean((true_state - predictions) ** 2))
        
        print(f"\n预测RMSE: {rmse:.3f} m")
        
        return {
            'method': '数据同化',
            'predictions': predictions,
            'rmse': rmse
        }
    
    def visualize(self, true_state, results_list):
        """结果可视化"""
        print("\n" + "=" * 70)
        print("结果可视化")
        print("=" * 70)
        
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
        plt.rcParams['axes.unicode_minus'] = False
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        time = np.arange(len(true_state))
        colors = ['#FF6B6B', '#FFD93D', '#4ECDC4']
        
        # 1. 预测曲线对比
        axes[0, 0].plot(time, true_state, 'k-', label='真实值', 
                       linewidth=2.5, alpha=0.8)
        
        for i, result in enumerate(results_list):
            axes[0, 0].plot(time, result['predictions'], 
                          label=result['method'], linewidth=1.5, 
                          alpha=0.7, color=colors[i])
        
        axes[0, 0].set_xlabel('时间 (h)', fontsize=11)
        axes[0, 0].set_ylabel('水位 (m)', fontsize=11)
        axes[0, 0].set_title('预测曲线对比', fontsize=12, fontweight='bold')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. RMSE对比
        methods = [r['method'] for r in results_list]
        rmses = [r['rmse'] for r in results_list]
        
        bars = axes[0, 1].bar(methods, rmses, color=colors, alpha=0.7)
        axes[0, 1].set_ylabel('RMSE (m)', fontsize=11)
        axes[0, 1].set_title('预测精度对比', fontsize=12, fontweight='bold')
        axes[0, 1].grid(True, alpha=0.3, axis='y')
        
        for bar, rmse in zip(bars, rmses):
            height = bar.get_height()
            axes[0, 1].text(bar.get_x() + bar.get_width()/2., height,
                          f'{rmse:.3f}',
                          ha='center', va='bottom', fontsize=10)
        
        # 3. 误差时间序列
        for i, result in enumerate(results_list):
            error = true_state - result['predictions']
            axes[1, 0].plot(time, error, label=result['method'], 
                          alpha=0.7, color=colors[i])
        
        axes[1, 0].axhline(y=0, color='k', linestyle='--', linewidth=0.8)
        axes[1, 0].set_xlabel('时间 (h)', fontsize=11)
        axes[1, 0].set_ylabel('误差 (m)', fontsize=11)
        axes[1, 0].set_title('预测误差时间序列', fontsize=12, fontweight='bold')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # 4. 精度提升
        baseline_rmse = results_list[0]['rmse']
        improvements = [(baseline_rmse - r['rmse']) / baseline_rmse * 100 
                       for r in results_list]
        
        bars = axes[1, 1].bar(methods, improvements, color=colors, alpha=0.7)
        axes[1, 1].set_ylabel('精度提升 (%)', fontsize=11)
        axes[1, 1].set_title('相对仅模型的精度提升', fontsize=12, fontweight='bold')
        axes[1, 1].axhline(y=0, color='k', linestyle='-', linewidth=0.8)
        axes[1, 1].grid(True, alpha=0.3, axis='y')
        
        for bar, imp in zip(bars, improvements):
            height = bar.get_height()
            axes[1, 1].text(bar.get_x() + bar.get_width()/2., height,
                          f'{imp:+.1f}%',
                          ha='center', va='bottom' if imp > 0 else 'top', 
                          fontsize=10)
        
        plt.tight_layout()
        plt.savefig(self.results_dir / "figures/data_assimilation.png", 
                   dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"  已保存: figures/data_assimilation.png")
    
    def run(self):
        """运行数据同化系统"""
        print("\n" + "*" * 70)
        print(" " * 18 + "实时数据同化与预测")
        print(" " * 28 + "案例5.3")
        print("*" * 70)
        
        try:
            # 生成真实状态
            true_state = self.generate_true_state(n_steps=100)
            
            # 三种方法
            model_result = self.method1_model_only(true_state)
            obs_result = self.method2_observation_only(true_state, obs_frequency=5)
            da_result = self.method3_data_assimilation(true_state, obs_frequency=5)
            
            results_list = [model_result, obs_result, da_result]
            
            self.visualize(true_state, results_list)
            
            print("\n" + "=" * 70)
            print("数据同化完成！")
            print("=" * 70)
            
            # 性能总结
            print(f"\n性能总结:")
            for result in results_list:
                print(f"  {result['method']}: RMSE={result['rmse']:.3f} m")
            
            improvement = (model_result['rmse'] - da_result['rmse']) / model_result['rmse'] * 100
            print(f"\n数据同化相对仅模型精度提升: {improvement:.1f}%")
            
        except Exception as e:
            print(f"\n错误: {e}")
            import traceback
            traceback.print_exc()


def main():
    """主函数"""
    system = DataAssimilationSystem()
    system.run()


if __name__ == "__main__":
    main()
