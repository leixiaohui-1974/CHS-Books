"""
案例6.2：供水安全风险分析 - 主程序

使用情景分析和蒙特卡洛评估供水可靠性

作者：教材编写组
日期：2025-11-02
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../"))

import numpy as np
import matplotlib.pyplot as plt

from core.risk import (
    ScenarioGenerator,
    ScenarioAnalyzer,
    MonteCarloSimulator,
    VaRCalculator,
    CVaRCalculator
)


class WaterSecurityAnalysis:
    """供水安全风险分析系统"""
    
    def __init__(self):
        self.results_dir = Path("results")
        self.results_dir.mkdir(exist_ok=True)
        (self.results_dir / "figures").mkdir(exist_ok=True)
        
        # 系统参数
        self.reservoir_capacity = 5000  # 水库容量（万m³）
        self.plant_capacity = 50  # 水厂能力（万m³/月）
        self.normal_demand = 40  # 正常需水（万m³/月）
        self.normal_inflow = 45  # 正常来水（万m³/月）
        
        print(f"供水安全风险分析系统")
        print(f"水库容量: {self.reservoir_capacity}万m³")
        print(f"水厂能力: {self.plant_capacity}万m³/月")
        print(f"正常需水: {self.normal_demand}万m³/月")
    
    def simulate_water_balance(self, inflow_factor, demand_factor, plant_factor, months=12):
        """
        模拟水量平衡
        
        Parameters
        ----------
        inflow_factor : float
            来水系数（1.0为正常）
        demand_factor : float
            需水系数
        plant_factor : float
            水厂能力系数
        months : int
            模拟月数
        
        Returns
        -------
        dict
            模拟结果
        """
        # 初始状态
        storage = self.reservoir_capacity * 0.7  # 初始70%蓄水
        
        shortages = []
        storages = [storage]
        supplies = []
        
        for month in range(months):
            # 入流（含季节变化）
            seasonal_factor = 1.0 + 0.3 * np.sin(2 * np.pi * month / 12)
            inflow = self.normal_inflow * inflow_factor * seasonal_factor
            
            # 需水
            demand = self.normal_demand * demand_factor
            
            # 可供水能力
            available_from_plant = self.plant_capacity * plant_factor
            available_from_storage = storage
            available = min(available_from_plant, available_from_storage, demand)
            
            # 实际供水
            supply = available
            
            # 缺水
            shortage = max(0, demand - supply)
            
            # 更新水库
            storage = storage + inflow - supply
            storage = np.clip(storage, 0, self.reservoir_capacity)
            
            # 记录
            shortages.append(shortage)
            storages.append(storage)
            supplies.append(supply)
        
        # 计算指标
        total_shortage = sum(shortages)
        shortage_months = sum(1 for s in shortages if s > 0)
        reliability = (months - shortage_months) / months * 100
        
        return {
            'shortages': shortages,
            'storages': storages,
            'supplies': supplies,
            'total_shortage': total_shortage,
            'shortage_months': shortage_months,
            'reliability': reliability
        }
    
    def scenario_analysis(self):
        """情景分析"""
        print("\n" + "=" * 70)
        print("情景分析")
        print("=" * 70)
        
        # 定义情景
        scenarios = {
            '正常': {
                'inflow': 1.0,
                'demand': 1.0,
                'plant': 1.0,
                'probability': 0.60
            },
            '干旱': {
                'inflow': 0.7,
                'demand': 1.1,
                'plant': 1.0,
                'probability': 0.25
            },
            '故障': {
                'inflow': 1.0,
                'demand': 1.0,
                'plant': 0.5,
                'probability': 0.10
            },
            '复合': {
                'inflow': 0.7,
                'demand': 1.1,
                'plant': 0.5,
                'probability': 0.05
            }
        }
        
        results = {}
        
        for name, params in scenarios.items():
            print(f"\n{name}情景:")
            print(f"  来水系数: {params['inflow']:.2f}")
            print(f"  需水系数: {params['demand']:.2f}")
            print(f"  水厂系数: {params['plant']:.2f}")
            print(f"  发生概率: {params['probability']*100:.0f}%")
            
            result = self.simulate_water_balance(
                params['inflow'],
                params['demand'],
                params['plant']
            )
            
            print(f"  年缺水量: {result['total_shortage']:.1f}万m³")
            print(f"  缺水月数: {result['shortage_months']}月")
            print(f"  供水保证率: {result['reliability']:.1f}%")
            
            results[name] = {
                **result,
                'probability': params['probability']
            }
        
        # 计算加权期望
        expected_shortage = sum(
            results[s]['total_shortage'] * results[s]['probability']
            for s in scenarios.keys()
        )
        
        print(f"\n加权期望年缺水量: {expected_shortage:.1f}万m³")
        
        return results, scenarios
    
    def monte_carlo_analysis(self, n_simulations=1000):
        """蒙特卡洛分析"""
        print("\n" + "=" * 70)
        print("蒙特卡洛风险分析")
        print("=" * 70)
        
        shortages_all = []
        
        for i in range(n_simulations):
            # 随机生成参数
            rand = np.random.rand()
            
            if rand < 0.60:  # 正常
                inflow_factor = 1.0 + np.random.randn() * 0.1
                demand_factor = 1.0 + np.random.randn() * 0.05
                plant_factor = 1.0
            elif rand < 0.85:  # 干旱
                inflow_factor = 0.7 + np.random.randn() * 0.1
                demand_factor = 1.1 + np.random.randn() * 0.05
                plant_factor = 1.0
            elif rand < 0.95:  # 故障
                inflow_factor = 1.0 + np.random.randn() * 0.1
                demand_factor = 1.0 + np.random.randn() * 0.05
                plant_factor = 0.5 + np.random.rand() * 0.3  # 故障程度随机
            else:  # 复合
                inflow_factor = 0.7 + np.random.randn() * 0.1
                demand_factor = 1.1 + np.random.randn() * 0.05
                plant_factor = 0.5 + np.random.rand() * 0.3
            
            result = self.simulate_water_balance(inflow_factor, demand_factor, plant_factor)
            shortages_all.append(result['total_shortage'])
        
        shortages_arr = np.array(shortages_all)
        
        # 计算风险指标
        expected_shortage = np.mean(shortages_arr)
        std_shortage = np.std(shortages_arr)
        
        # VaR和CVaR
        var_calc = VaRCalculator(confidence_level=0.95)
        cvar_calc = CVaRCalculator(confidence_level=0.95)
        
        # 转换为负收益
        returns = -shortages_arr
        var = var_calc.calculate_historical(returns)
        var_val, cvar_val = cvar_calc.calculate(returns)
        
        # 缺水概率
        shortage_prob = sum(1 for s in shortages_arr if s > 0) / len(shortages_arr) * 100
        
        print(f"\n蒙特卡洛模拟结果 (N={n_simulations}):")
        print(f"  期望年缺水量: {expected_shortage:.1f}万m³")
        print(f"  标准差: {std_shortage:.1f}万m³")
        print(f"  缺水概率: {shortage_prob:.1f}%")
        print(f"  VaR(95%): {var:.1f}万m³")
        print(f"  CVaR(95%): {cvar_val:.1f}万m³")
        print(f"  最大缺水: {shortages_arr.max():.1f}万m³")
        
        return {
            'shortages': shortages_arr,
            'expected': expected_shortage,
            'std': std_shortage,
            'prob': shortage_prob,
            'var': var,
            'cvar': cvar_val
        }
    
    def visualize(self, scenario_results, mc_results):
        """结果可视化"""
        print("\n" + "=" * 70)
        print("结果可视化")
        print("=" * 70)
        
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
        plt.rcParams['axes.unicode_minus'] = False
        
        fig, axes = plt.subplots(2, 3, figsize=(16, 10))
        
        # 1. 情景缺水量对比
        scenarios = list(scenario_results.keys())
        shortages = [scenario_results[s]['total_shortage'] for s in scenarios]
        probs = [scenario_results[s]['probability'] * 100 for s in scenarios]
        
        colors = ['#4ECDC4', '#FFD93D', '#FF6B6B', '#C44569']
        bars = axes[0, 0].bar(scenarios, shortages, color=colors, alpha=0.7)
        
        # 标注概率
        for i, (bar, prob) in enumerate(zip(bars, probs)):
            height = bar.get_height()
            axes[0, 0].text(bar.get_x() + bar.get_width()/2., height,
                          f'{prob:.0f}%',
                          ha='center', va='bottom', fontsize=9)
        
        axes[0, 0].set_ylabel('年缺水量 (万m³)', fontsize=11)
        axes[0, 0].set_title('情景分析：年缺水量', fontsize=12, fontweight='bold')
        axes[0, 0].grid(True, alpha=0.3, axis='y')
        
        # 2. 供水保证率
        reliabilities = [scenario_results[s]['reliability'] for s in scenarios]
        
        axes[0, 1].bar(scenarios, reliabilities, color=colors, alpha=0.7)
        axes[0, 1].axhline(y=95, color='r', linestyle='--', linewidth=2, label='95%标准')
        axes[0, 1].set_ylabel('供水保证率 (%)', fontsize=11)
        axes[0, 1].set_title('情景分析：供水保证率', fontsize=12, fontweight='bold')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3, axis='y')
        
        # 3. 缺水分布（蒙特卡洛）
        axes[0, 2].hist(mc_results['shortages'], bins=50, color='#95E1D3', 
                       alpha=0.7, edgecolor='black')
        axes[0, 2].axvline(mc_results['expected'], color='r', linestyle='--', 
                          linewidth=2, label='期望值')
        axes[0, 2].axvline(mc_results['var'], color='orange', linestyle='--', 
                          linewidth=2, label='VaR(95%)')
        axes[0, 2].set_xlabel('年缺水量 (万m³)', fontsize=11)
        axes[0, 2].set_ylabel('频数', fontsize=11)
        axes[0, 2].set_title('蒙特卡洛：缺水分布', fontsize=12, fontweight='bold')
        axes[0, 2].legend()
        axes[0, 2].grid(True, alpha=0.3, axis='y')
        
        # 4. 正常情景水库调节
        normal_storages = scenario_results['正常']['storages']
        months = range(len(normal_storages))
        
        axes[1, 0].plot(months, normal_storages, 'b-', linewidth=2, label='水库蓄水')
        axes[1, 0].axhline(y=self.reservoir_capacity, color='r', linestyle='--', 
                          label='水库容量')
        axes[1, 0].axhline(y=self.reservoir_capacity * 0.3, color='orange', 
                          linestyle='--', label='死水位')
        axes[1, 0].fill_between(months, 0, normal_storages, alpha=0.3)
        axes[1, 0].set_xlabel('月份', fontsize=11)
        axes[1, 0].set_ylabel('蓄水量 (万m³)', fontsize=11)
        axes[1, 0].set_title('正常情景：水库调节', fontsize=12, fontweight='bold')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # 5. 干旱情景缺水过程
        drought_shortages = scenario_results['干旱']['shortages']
        
        axes[1, 1].bar(range(len(drought_shortages)), drought_shortages, 
                      color='#FF6B6B', alpha=0.7)
        axes[1, 1].set_xlabel('月份', fontsize=11)
        axes[1, 1].set_ylabel('月缺水量 (万m³)', fontsize=11)
        axes[1, 1].set_title('干旱情景：月缺水过程', fontsize=12, fontweight='bold')
        axes[1, 1].grid(True, alpha=0.3, axis='y')
        
        # 6. 综合风险指标
        risk_metrics = {
            '期望\n缺水': mc_results['expected'],
            'VaR\n(95%)': mc_results['var'],
            'CVaR\n(95%)': mc_results['cvar']
        }
        
        axes[1, 2].bar(risk_metrics.keys(), risk_metrics.values(), 
                      color=['#4ECDC4', '#FFD93D', '#FF6B6B'], alpha=0.7)
        axes[1, 2].set_ylabel('缺水量 (万m³)', fontsize=11)
        axes[1, 2].set_title('综合风险指标', fontsize=12, fontweight='bold')
        axes[1, 2].grid(True, alpha=0.3, axis='y')
        
        for i, (label, val) in enumerate(risk_metrics.items()):
            axes[1, 2].text(i, val, f'{val:.1f}', 
                          ha='center', va='bottom', fontsize=10)
        
        plt.tight_layout()
        plt.savefig(self.results_dir / "figures/water_security_analysis.png", 
                   dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"  已保存: figures/water_security_analysis.png")
    
    def run(self):
        """运行风险分析"""
        print("\n" + "*" * 70)
        print(" " * 20 + "供水安全风险分析")
        print(" " * 28 + "案例6.2")
        print("*" * 70)
        
        try:
            # 情景分析
            scenario_results, scenarios = self.scenario_analysis()
            
            # 蒙特卡洛分析
            mc_results = self.monte_carlo_analysis(n_simulations=2000)
            
            # 可视化
            self.visualize(scenario_results, mc_results)
            
            print("\n" + "=" * 70)
            print("供水安全风险分析完成！")
            print("=" * 70)
            
        except Exception as e:
            print(f"\n错误: {e}")
            import traceback
            traceback.print_exc()


def main():
    """主函数"""
    analysis = WaterSecurityAnalysis()
    analysis.run()


if __name__ == "__main__":
    main()
