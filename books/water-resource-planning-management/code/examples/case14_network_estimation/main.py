"""
案例5.2：供水管网状态估计 - 主程序

使用EKF估计全网状态

作者：教材编写组
日期：2025-11-02
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../"))

import numpy as np
import matplotlib.pyplot as plt

from core.digital_twin import ExtendedKalmanFilter, VirtualSensor


class NetworkStateEstimator:
    """管网状态估计系统"""
    
    def __init__(self):
        self.results_dir = Path("results")
        self.results_dir.mkdir(exist_ok=True)
        (self.results_dir / "figures").mkdir(exist_ok=True)
        
        # 管网参数（简化：5个节点，4条管道）
        self.n_nodes = 5
        self.n_pipes = 4
        
        # 传感器布置（只在2个节点有压力传感器）
        self.sensor_nodes = [0, 2]  # 节点0和2有传感器
        
        print(f"管网状态估计系统: {self.n_nodes}个节点, {self.sensor_nodes}个传感器")
    
    def simulate_network(self, n_steps=50):
        """模拟管网运行"""
        
        # 真实压力（模拟）
        true_pressures = []
        measured_pressures = []
        estimated_pressures = []
        
        # 简化管网模型
        base_pressures = np.array([40, 35, 30, 28, 25])  # 各节点基准压力
        
        # EKF初始化
        ekf = ExtendedKalmanFilter(dim_x=self.n_nodes, dim_z=len(self.sensor_nodes))
        
        # 状态转移函数（简化：压力缓慢变化）
        def f(x, u, dt):
            # 简单动态：压力随需水量波动
            return x + np.random.randn(self.n_nodes) * 0.1
        
        # 观测函数（选择有传感器的节点）
        def h(x):
            return x[self.sensor_nodes]
        
        ekf.f = f
        ekf.h = h
        
        # 噪声协方差
        ekf.Q = np.eye(self.n_nodes) * 0.1
        ekf.R = np.eye(len(self.sensor_nodes)) * 0.5
        
        # 初始状态
        ekf.x = base_pressures.copy()
        ekf.P = np.eye(self.n_nodes) * 1.0
        
        print("\n开始模拟...")
        
        for step in range(n_steps):
            # 真实压力（随时间波动）
            true_p = base_pressures + 2 * np.sin(2 * np.pi * step / 20) + np.random.randn(self.n_nodes) * 0.2
            
            # 测量值（只有部分节点，且有噪声）
            measured_p = true_p[self.sensor_nodes] + np.random.randn(len(self.sensor_nodes)) * 0.5
            
            # EKF估计
            ekf.predict(u=None, dt=1.0)
            ekf.update(measured_p)
            
            estimated_p = ekf.get_state()
            
            # 记录
            true_pressures.append(true_p.copy())
            measured_pressures.append(measured_p.copy())
            estimated_pressures.append(estimated_p.copy())
            
            if (step + 1) % 10 == 0:
                rmse = np.sqrt(np.mean((true_p - estimated_p) ** 2))
                print(f"  步数{step+1}: RMSE={rmse:.3f} m")
        
        # 计算性能
        true_arr = np.array(true_pressures)
        est_arr = np.array(estimated_pressures)
        
        rmse_all = np.sqrt(np.mean((true_arr - est_arr) ** 2))
        
        # 只比较有传感器的节点
        rmse_sensor = np.sqrt(np.mean((true_arr[:, self.sensor_nodes] - 
                                       np.array(measured_pressures)) ** 2))
        
        print(f"\n性能指标:")
        print(f"  传感器节点测量RMSE: {rmse_sensor:.3f} m")
        print(f"  全网估计RMSE: {rmse_all:.3f} m")
        print(f"  精度提升: {(1 - rmse_all/rmse_sensor)*100:.1f}%")
        
        return {
            'true': true_arr,
            'measured': np.array(measured_pressures),
            'estimated': est_arr,
            'rmse_all': rmse_all,
            'rmse_sensor': rmse_sensor
        }
    
    def visualize(self, results):
        """结果可视化"""
        print("\n" + "=" * 70)
        print("结果可视化")
        print("=" * 70)
        
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
        plt.rcParams['axes.unicode_minus'] = False
        
        fig, axes = plt.subplots(2, 3, figsize=(16, 10))
        
        time = np.arange(len(results['true']))
        
        # 绘制各节点压力估计
        for i in range(min(5, self.n_nodes)):
            row = i // 3
            col = i % 3
            
            if i < self.n_nodes:
                axes[row, col].plot(time, results['true'][:, i], 
                                   'k-', label='真实值', linewidth=2, alpha=0.7)
                axes[row, col].plot(time, results['estimated'][:, i], 
                                   'b-', label='估计值', linewidth=1.5, alpha=0.8)
                
                # 标记是否有传感器
                if i in self.sensor_nodes:
                    axes[row, col].plot(time, results['measured'][:, self.sensor_nodes.index(i)],
                                       'r.', label='测量值', markersize=3, alpha=0.5)
                    title = f'节点{i+1}（有传感器）'
                else:
                    title = f'节点{i+1}（虚拟传感器）'
                
                axes[row, col].set_xlabel('时间 (h)', fontsize=10)
                axes[row, col].set_ylabel('压力 (m)', fontsize=10)
                axes[row, col].set_title(title, fontsize=11, fontweight='bold')
                axes[row, col].legend(fontsize=9)
                axes[row, col].grid(True, alpha=0.3)
        
        # 最后一个子图：整体RMSE
        axes[1, 2].bar(['传感器节点\n测量误差', '全网\n估计误差'],
                      [results['rmse_sensor'], results['rmse_all']],
                      color=['#FF6B6B', '#4ECDC4'], alpha=0.7)
        axes[1, 2].set_ylabel('RMSE (m)', fontsize=11)
        axes[1, 2].set_title('估计精度对比', fontsize=12, fontweight='bold')
        axes[1, 2].grid(True, alpha=0.3, axis='y')
        
        for i, (val, label) in enumerate([(results['rmse_sensor'], '测量'), 
                                          (results['rmse_all'], '估计')]):
            axes[1, 2].text(i, val, f'{val:.3f}m', 
                          ha='center', va='bottom', fontsize=10)
        
        plt.tight_layout()
        plt.savefig(self.results_dir / "figures/network_estimation.png", 
                   dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"  已保存: figures/network_estimation.png")
    
    def run(self):
        """运行状态估计"""
        print("\n" + "*" * 70)
        print(" " * 20 + "供水管网状态估计")
        print(" " * 28 + "案例5.2")
        print("*" * 70)
        
        try:
            results = self.simulate_network(n_steps=50)
            self.visualize(results)
            
            print("\n" + "=" * 70)
            print("管网状态估计完成！")
            print("=" * 70)
            
        except Exception as e:
            print(f"\n错误: {e}")
            import traceback
            traceback.print_exc()


def main():
    """主函数"""
    estimator = NetworkStateEstimator()
    estimator.run()


if __name__ == "__main__":
    main()
