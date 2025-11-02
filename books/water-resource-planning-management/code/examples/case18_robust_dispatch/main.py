"""
案例6.3：鲁棒优化调度 - 主程序

对比确定性、Min-Max、Min-Regret和加权鲁棒方法

作者：教材编写组
日期：2025-11-02
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../"))

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize

from core.risk import RobustOptimizer


class RobustDispatchSystem:
    """鲁棒优化调度系统"""
    
    def __init__(self):
        self.results_dir = Path("results")
        self.results_dir.mkdir(exist_ok=True)
        (self.results_dir / "figures").mkdir(exist_ok=True)
        
        # 水库参数
        self.min_storage = 50  # 万m³
        self.max_storage = 500
        self.installed_power = 100  # MW
        
        # 情景定义
        self.scenarios = [
            {'name': '丰水', 'inflow': 250, 'probability': 0.30},
            {'name': '平水', 'inflow': 200, 'probability': 0.50},
            {'name': '枯水', 'inflow': 150, 'probability': 0.20}
        ]
        
        print(f"鲁棒优化调度系统")
        print(f"水库: {self.min_storage}-{self.max_storage}万m³")
        print(f"装机: {self.installed_power}MW")
        print(f"情景数: {len(self.scenarios)}")
    
    def calculate_power(self, discharge, head):
        """
        计算发电量
        
        Parameters
        ----------
        discharge : float
            放水流量 (m³/s)
        head : float
            水头 (m)
        
        Returns
        -------
        float
            发电量 (万kWh/月)
        """
        # 简化公式：P = 9.81 * η * Q * H * t / 10000
        efficiency = 0.85
        hours_per_month = 720
        
        power = 9.81 * efficiency * discharge * head * hours_per_month / 10000
        
        # 限制装机容量
        max_power = self.installed_power * hours_per_month / 100
        power = min(power, max_power)
        
        return power
    
    def simulate_dispatch(self, discharge_plan, inflow):
        """
        模拟调度过程
        
        Parameters
        ----------
        discharge_plan : np.ndarray
            放水计划 (m³/s), 12个月
        inflow : float
            平均入流 (m³/s)
        
        Returns
        -------
        float
            总发电量 (万kWh)
        """
        n_months = len(discharge_plan)
        storage = (self.min_storage + self.max_storage) / 2  # 初始蓄水
        total_power = 0
        
        for month in range(n_months):
            # 月入流（含季节变化）
            seasonal_factor = 1.0 + 0.3 * np.sin(2 * np.pi * month / 12)
            monthly_inflow = inflow * seasonal_factor * 30 * 24 * 3600 / 10000  # 万m³
            
            # 放水
            discharge = discharge_plan[month]
            monthly_discharge = discharge * 30 * 24 * 3600 / 10000  # 万m³
            
            # 水量平衡
            new_storage = storage + monthly_inflow - monthly_discharge
            
            # 约束检查
            if new_storage < self.min_storage:
                # 放水过多，减少放水
                monthly_discharge = storage + monthly_inflow - self.min_storage
                discharge = monthly_discharge / (30 * 24 * 3600 / 10000)
                new_storage = self.min_storage
            
            elif new_storage > self.max_storage:
                # 蓄水过多，增加放水（弃水）
                monthly_discharge = storage + monthly_inflow - self.max_storage
                discharge = monthly_discharge / (30 * 24 * 3600 / 10000)
                new_storage = self.max_storage
            
            # 计算水头（简化）
            avg_storage = (storage + new_storage) / 2
            water_level = 180 + (avg_storage - self.min_storage) / (self.max_storage - self.min_storage) * 20
            downstream_level = 165
            head = water_level - downstream_level
            
            # 发电
            power = self.calculate_power(discharge, head)
            total_power += power
            
            # 更新蓄水
            storage = new_storage
        
        return -total_power  # 返回负值（最小化问题）
    
    def deterministic_optimization(self):
        """确定性优化（期望值）"""
        print("\n" + "=" * 70)
        print("方法1: 确定性优化（期望入流）")
        print("=" * 70)
        
        # 期望入流
        expected_inflow = sum(s['inflow'] * s['probability'] for s in self.scenarios)
        
        print(f"\n期望入流: {expected_inflow:.1f} m³/s")
        
        # 优化
        x0 = np.ones(12) * 200  # 初始放水计划
        bounds = [(50, 300)] * 12
        
        result = minimize(
            lambda x: self.simulate_dispatch(x, expected_inflow),
            x0,
            bounds=bounds,
            method='L-BFGS-B'
        )
        
        optimal_plan = result.x
        
        # 评估各情景
        print(f"\n各情景性能:")
        scenario_powers = []
        for scenario in self.scenarios:
            power = -self.simulate_dispatch(optimal_plan, scenario['inflow'])
            scenario_powers.append(power)
            print(f"  {scenario['name']}: {power:.0f}万kWh")
        
        expected_power = sum(p * s['probability'] for p, s in zip(scenario_powers, self.scenarios))
        worst_power = min(scenario_powers)
        
        print(f"\n期望发电: {expected_power:.0f}万kWh")
        print(f"最坏发电: {worst_power:.0f}万kWh")
        
        return {
            'plan': optimal_plan,
            'scenario_powers': scenario_powers,
            'expected': expected_power,
            'worst': worst_power,
            'method': '确定性'
        }
    
    def robust_minmax_optimization(self):
        """Min-Max鲁棒优化"""
        print("\n" + "=" * 70)
        print("方法2: Min-Max鲁棒优化")
        print("=" * 70)
        
        def worst_case_objective(x):
            powers = []
            for scenario in self.scenarios:
                power = self.simulate_dispatch(x, scenario['inflow'])
                powers.append(power)
            return max(powers)  # 最坏（最大负发电）
        
        x0 = np.ones(12) * 200
        bounds = [(50, 300)] * 12
        
        result = minimize(
            worst_case_objective,
            x0,
            bounds=bounds,
            method='L-BFGS-B',
            options={'maxiter': 100}
        )
        
        optimal_plan = result.x
        
        # 评估
        print(f"\n各情景性能:")
        scenario_powers = []
        for scenario in self.scenarios:
            power = -self.simulate_dispatch(optimal_plan, scenario['inflow'])
            scenario_powers.append(power)
            print(f"  {scenario['name']}: {power:.0f}万kWh")
        
        expected_power = sum(p * s['probability'] for p, s in zip(scenario_powers, self.scenarios))
        worst_power = min(scenario_powers)
        
        print(f"\n期望发电: {expected_power:.0f}万kWh")
        print(f"最坏发电: {worst_power:.0f}万kWh")
        
        return {
            'plan': optimal_plan,
            'scenario_powers': scenario_powers,
            'expected': expected_power,
            'worst': worst_power,
            'method': 'Min-Max'
        }
    
    def weighted_robust_optimization(self, alpha=0.3):
        """加权鲁棒优化"""
        print("\n" + "=" * 70)
        print(f"方法3: 加权鲁棒优化 (α={alpha})")
        print("=" * 70)
        
        def weighted_objective(x):
            powers = []
            for scenario in self.scenarios:
                power = self.simulate_dispatch(x, scenario['inflow'])
                powers.append((power, scenario['probability']))
            
            # 期望
            expected = sum(p * prob for p, prob in powers)
            
            # 最坏
            worst = max(p for p, _ in powers)
            
            # 加权
            return (1 - alpha) * expected + alpha * worst
        
        x0 = np.ones(12) * 200
        bounds = [(50, 300)] * 12
        
        result = minimize(
            weighted_objective,
            x0,
            bounds=bounds,
            method='L-BFGS-B',
            options={'maxiter': 100}
        )
        
        optimal_plan = result.x
        
        # 评估
        print(f"\n各情景性能:")
        scenario_powers = []
        for scenario in self.scenarios:
            power = -self.simulate_dispatch(optimal_plan, scenario['inflow'])
            scenario_powers.append(power)
            print(f"  {scenario['name']}: {power:.0f}万kWh")
        
        expected_power = sum(p * s['probability'] for p, s in zip(scenario_powers, self.scenarios))
        worst_power = min(scenario_powers)
        
        print(f"\n期望发电: {expected_power:.0f}万kWh")
        print(f"最坏发电: {worst_power:.0f}万kWh")
        
        return {
            'plan': optimal_plan,
            'scenario_powers': scenario_powers,
            'expected': expected_power,
            'worst': worst_power,
            'method': f'加权(α={alpha})'
        }
    
    def visualize(self, results_list):
        """结果可视化"""
        print("\n" + "=" * 70)
        print("结果可视化")
        print("=" * 70)
        
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
        plt.rcParams['axes.unicode_minus'] = False
        
        fig, axes = plt.subplots(2, 3, figsize=(16, 10))
        
        # 1. 期望发电对比
        methods = [r['method'] for r in results_list]
        expected_powers = [r['expected'] for r in results_list]
        
        axes[0, 0].bar(methods, expected_powers, color='#4ECDC4', alpha=0.7)
        axes[0, 0].set_ylabel('期望发电 (万kWh)', fontsize=11)
        axes[0, 0].set_title('期望发电对比', fontsize=12, fontweight='bold')
        axes[0, 0].grid(True, alpha=0.3, axis='y')
        
        # 2. 最坏发电对比
        worst_powers = [r['worst'] for r in results_list]
        
        axes[0, 1].bar(methods, worst_powers, color='#FF6B6B', alpha=0.7)
        axes[0, 1].set_ylabel('最坏发电 (万kWh)', fontsize=11)
        axes[0, 1].set_title('最坏发电对比（鲁棒性）', fontsize=12, fontweight='bold')
        axes[0, 1].grid(True, alpha=0.3, axis='y')
        
        # 3. 期望vs最坏散点图
        axes[0, 2].scatter(expected_powers, worst_powers, s=150, alpha=0.7, c=range(len(methods)))
        for i, method in enumerate(methods):
            axes[0, 2].annotate(method, (expected_powers[i], worst_powers[i]),
                              xytext=(5, 5), textcoords='offset points', fontsize=9)
        
        axes[0, 2].set_xlabel('期望发电 (万kWh)', fontsize=11)
        axes[0, 2].set_ylabel('最坏发电 (万kWh)', fontsize=11)
        axes[0, 2].set_title('期望-鲁棒权衡', fontsize=12, fontweight='bold')
        axes[0, 2].grid(True, alpha=0.3)
        
        # 4-6. 各方法调度计划
        months = np.arange(1, 13)
        colors_plan = ['#4ECDC4', '#FF6B6B', '#FFD93D']
        
        for i, result in enumerate(results_list[:3]):
            row = 1 + i // 3
            col = i % 3
            
            axes[row, col].plot(months, result['plan'], 'o-', 
                              linewidth=2, markersize=6, color=colors_plan[i])
            axes[row, col].fill_between(months, 0, result['plan'], alpha=0.3, color=colors_plan[i])
            axes[row, col].set_xlabel('月份', fontsize=11)
            axes[row, col].set_ylabel('放水 (m³/s)', fontsize=11)
            axes[row, col].set_title(f'{result["method"]}：调度计划', 
                                    fontsize=11, fontweight='bold')
            axes[row, col].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.results_dir / "figures/robust_optimization.png", 
                   dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"  已保存: figures/robust_optimization.png")
    
    def run(self):
        """运行鲁棒优化"""
        print("\n" + "*" * 70)
        print(" " * 22 + "鲁棒优化调度")
        print(" " * 28 + "案例6.3")
        print("*" * 70)
        
        try:
            # 三种方法
            det_result = self.deterministic_optimization()
            minmax_result = self.robust_minmax_optimization()
            weighted_result = self.weighted_robust_optimization(alpha=0.3)
            
            results_list = [det_result, minmax_result, weighted_result]
            
            # 可视化
            self.visualize(results_list)
            
            print("\n" + "=" * 70)
            print("鲁棒优化完成！")
            print("=" * 70)
            
            # 性能对比
            print(f"\n性能对比总结:")
            for result in results_list:
                print(f"\n{result['method']}:")
                print(f"  期望发电: {result['expected']:.0f}万kWh")
                print(f"  最坏发电: {result['worst']:.0f}万kWh")
                print(f"  差距: {result['expected'] - result['worst']:.0f}万kWh")
            
        except Exception as e:
            print(f"\n错误: {e}")
            import traceback
            traceback.print_exc()


def main():
    """主函数"""
    system = RobustDispatchSystem()
    system.run()


if __name__ == "__main__":
    main()
