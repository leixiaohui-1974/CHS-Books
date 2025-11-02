"""
案例5.1：水库数字孪生系统 - 主程序

对比无滤波、卡尔曼滤波和虚拟传感器

作者：教材编写组
日期：2025-11-02
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../"))

import numpy as np
import matplotlib.pyplot as plt

from src import PhysicalReservoir, DigitalTwinReservoir


class DigitalTwinSystem:
    """数字孪生系统"""
    
    def __init__(self):
        self.results_dir = Path("results")
        self.results_dir.mkdir(exist_ok=True)
        (self.results_dir / "figures").mkdir(exist_ok=True)
        
        # 创建物理水库
        self.physical = PhysicalReservoir(
            min_storage=50,
            max_storage=500,
            min_level=180,
            max_level=200,
            dt=1.0
        )
        
        # 创建数字孪生
        self.digital_twin = DigitalTwinReservoir(
            min_storage=50,
            max_storage=500,
            min_level=180,
            max_level=200,
            dt=1.0
        )
        
        print(f"数字孪生系统初始化完成")
    
    def run_simulation(self, n_steps=100):
        """运行仿真"""
        print("\n" + "=" * 70)
        print("运行数字孪生仿真")
        print("=" * 70)
        
        # 历史记录
        history_raw = {'storage': [], 'level': []}
        history_twin = {'storage': [], 'level': [], 'std': []}
        history_true = {'storage': [], 'level': []}
        
        # 入流模式（含变化）
        base_inflow = 200
        inflow_pattern = [base_inflow + 50 * np.sin(2 * np.pi * t / 24) for t in range(n_steps)]
        outflow = 200  # 恒定出流
        
        for step in range(n_steps):
            # 物理水库演进
            inflow = inflow_pattern[step]
            storage_true, level_true = self.physical.step(inflow, outflow)
            
            # 获取带噪声的测量值
            measurements = self.physical.get_measurements(
                level_noise_std=0.1,
                flow_noise_std=10.0
            )
            
            # 方法1：直接使用测量值（无滤波）
            # 将水位测量转换为库容估计
            ratio = (measurements['level'] - 180) / (200 - 180)
            storage_raw = 50 + 450 * (ratio ** 1.25)
            
            history_raw['storage'].append(storage_raw)
            history_raw['level'].append(measurements['level'])
            
            # 方法2：数字孪生（卡尔曼滤波）
            control = {'outflow': outflow}
            twin_state = self.digital_twin.update(measurements, control)
            
            history_twin['storage'].append(twin_state['storage_est'])
            history_twin['level'].append(twin_state['level_est'])
            history_twin['std'].append(twin_state['storage_std'])
            
            # 真实值
            history_true['storage'].append(storage_true)
            history_true['level'].append(level_true)
            
            if (step + 1) % 20 == 0:
                print(f"  步数{step+1}: 真实库容={storage_true:.1f}, "
                      f"估计库容={twin_state['storage_est']:.1f}, "
                      f"误差={abs(storage_true - twin_state['storage_est']):.2f}")
        
        # 计算性能指标
        storage_true_arr = np.array(history_true['storage'])
        storage_raw_arr = np.array(history_raw['storage'])
        storage_twin_arr = np.array(history_twin['storage'])
        
        rmse_raw = np.sqrt(np.mean((storage_true_arr - storage_raw_arr) ** 2))
        rmse_twin = np.sqrt(np.mean((storage_true_arr - storage_twin_arr) ** 2))
        
        print(f"\n性能指标:")
        print(f"  无滤波 RMSE: {rmse_raw:.2f} 万m³")
        print(f"  数字孪生 RMSE: {rmse_twin:.2f} 万m³")
        print(f"  精度提升: {(1 - rmse_twin/rmse_raw)*100:.1f}%")
        
        return {
            'raw': history_raw,
            'twin': history_twin,
            'true': history_true,
            'rmse_raw': rmse_raw,
            'rmse_twin': rmse_twin
        }
    
    def visualize(self, results):
        """结果可视化"""
        print("\n" + "=" * 70)
        print("结果可视化")
        print("=" * 70)
        
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
        plt.rcParams['axes.unicode_minus'] = False
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        time = np.arange(len(results['true']['storage']))
        
        # 1. 库容对比
        axes[0, 0].plot(time, results['true']['storage'], 'k-', 
                       label='真实值', linewidth=2, alpha=0.8)
        axes[0, 0].plot(time, results['raw']['storage'], 
                       label='无滤波（测量值）', linewidth=1, alpha=0.6)
        axes[0, 0].plot(time, results['twin']['storage'], 
                       label='数字孪生（滤波后）', linewidth=2, alpha=0.8)
        
        axes[0, 0].set_xlabel('时间 (h)', fontsize=11)
        axes[0, 0].set_ylabel('库容 (万m³)', fontsize=11)
        axes[0, 0].set_title('库容估计对比', fontsize=12, fontweight='bold')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. 水位对比
        axes[0, 1].plot(time, results['true']['level'], 'k-', 
                       label='真实值', linewidth=2, alpha=0.8)
        axes[0, 1].plot(time, results['raw']['level'], 
                       label='测量值', linewidth=1, alpha=0.6)
        axes[0, 1].plot(time, results['twin']['level'], 
                       label='估计值', linewidth=2, alpha=0.8)
        
        axes[0, 1].set_xlabel('时间 (h)', fontsize=11)
        axes[0, 1].set_ylabel('水位 (m)', fontsize=11)
        axes[0, 1].set_title('水位估计对比', fontsize=12, fontweight='bold')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
        
        # 3. 估计误差
        error_raw = np.array(results['true']['storage']) - np.array(results['raw']['storage'])
        error_twin = np.array(results['true']['storage']) - np.array(results['twin']['storage'])
        
        axes[1, 0].plot(time, error_raw, label='无滤波误差', alpha=0.7)
        axes[1, 0].plot(time, error_twin, label='数字孪生误差', alpha=0.7)
        axes[1, 0].axhline(y=0, color='k', linestyle='--', linewidth=0.8)
        
        axes[1, 0].set_xlabel('时间 (h)', fontsize=11)
        axes[1, 0].set_ylabel('误差 (万m³)', fontsize=11)
        axes[1, 0].set_title('库容估计误差', fontsize=12, fontweight='bold')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # 4. 不确定性（标准差）
        std = np.array(results['twin']['std'])
        storage_twin = np.array(results['twin']['storage'])
        
        axes[1, 1].plot(time, storage_twin, 'b-', label='估计值', linewidth=2)
        axes[1, 1].fill_between(time, 
                                storage_twin - 2*std, 
                                storage_twin + 2*std,
                                alpha=0.3, label='95%置信区间')
        axes[1, 1].plot(time, results['true']['storage'], 'k--', 
                       label='真实值', alpha=0.6)
        
        axes[1, 1].set_xlabel('时间 (h)', fontsize=11)
        axes[1, 1].set_ylabel('库容 (万m³)', fontsize=11)
        axes[1, 1].set_title('不确定性分析', fontsize=12, fontweight='bold')
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.results_dir / "figures/digital_twin_results.png", 
                   dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"  已保存: figures/digital_twin_results.png")
    
    def run(self):
        """运行完整系统"""
        print("\n" + "*" * 70)
        print(" " * 20 + "水库数字孪生系统")
        print(" " * 28 + "案例5.1")
        print("*" * 70)
        
        try:
            results = self.run_simulation(n_steps=100)
            self.visualize(results)
            
            print("\n" + "=" * 70)
            print("数字孪生系统运行完成！")
            print("=" * 70)
            
            print(f"\n最终性能总结:")
            print(f"  无滤波方法:")
            print(f"    RMSE: {results['rmse_raw']:.2f} 万m³")
            
            print(f"\n  数字孪生方法:")
            print(f"    RMSE: {results['rmse_twin']:.2f} 万m³")
            print(f"    精度提升: {(1 - results['rmse_twin']/results['rmse_raw'])*100:.1f}%")
            
        except Exception as e:
            print(f"\n错误: {e}")
            import traceback
            traceback.print_exc()


def main():
    """主函数"""
    system = DigitalTwinSystem()
    system.run()


if __name__ == "__main__":
    main()
