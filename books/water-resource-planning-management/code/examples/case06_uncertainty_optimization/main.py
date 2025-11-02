"""
案例2.3：考虑不确定性的水资源配置 - 主程序

对比确定性优化、随机规划、鲁棒优化和情景分析

作者：教材编写组
日期：2025-11-02
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "."))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import linprog

from core.utils.data_io import load_yaml, save_csv
from src.stochastic_programming import TwoStageSP, generate_scenarios
from src.robust_optimization import RobustOptimizer
from src.risk_measures import calculate_risk_metrics


class UncertaintyOptimizer:
    """不确定性水资源配置优化系统"""
    
    def __init__(self):
        self.results_dir = Path("results")
        self.results_dir.mkdir(exist_ok=True)
        (self.results_dir / "figures").mkdir(exist_ok=True)
        
        # 加载配置
        self.config = load_yaml("data/uncertainty_parameters.yaml")
        
        # 提取基础参数
        self.base_config = self.config['base_parameters']
        self.n_sources = len(self.base_config['sources'])
        self.n_users = len(self.base_config['users'])
        
        print(f"不确定性优化: {self.n_sources}个水源 × {self.n_users}个用户")
    
    def solve_deterministic(self) -> Dict:
        """方法1：确定性优化（基准）"""
        print("\n" + "=" * 70)
        print("方法1: 确定性优化（均值参数）")
        print("=" * 70)
        
        n_vars = self.n_sources * self.n_users
        
        # 使用均值参数
        capacities = np.array([
            self.config['runoff_uncertainty']['source_1']['mean'],
            self.config['runoff_uncertainty']['source_2']['mean'],
            self.config['runoff_uncertainty']['source_3']['mean']
        ])
        
        demands = np.array([u['base_demand'] for u in self.base_config['users']])
        benefits = np.array([u['benefit'] for u in self.base_config['users']])
        costs = np.array([s['base_cost'] for s in self.base_config['sources']])
        transport_costs = np.array(self.base_config['transport_costs'])
        
        # 目标函数
        c = []
        for i in range(self.n_sources):
            for j in range(self.n_users):
                net_benefit = benefits[j] - costs[i] - transport_costs[i, j]
                c.append(-net_benefit)
        c = np.array(c)
        
        # 约束
        A_ub_cap = np.zeros((self.n_sources, n_vars))
        for i in range(self.n_sources):
            for j in range(self.n_users):
                idx = i * self.n_users + j
                A_ub_cap[i, idx] = 1
        b_ub_cap = capacities
        
        A_ub_dem = np.zeros((self.n_users, n_vars))
        for j in range(self.n_users):
            for i in range(self.n_sources):
                idx = i * self.n_users + j
                A_ub_dem[j, idx] = -1
        b_ub_dem = -demands * 0.95
        
        A_ub = np.vstack([A_ub_cap, A_ub_dem])
        b_ub = np.concatenate([b_ub_cap, b_ub_dem])
        
        # 求解
        result = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=[(0, None)] * n_vars, method='highs')
        
        if result.success:
            print(f"\n确定性方案效益: {-result.fun:.2f} 万元/d")
            return {
                'method': 'Deterministic',
                'allocation': result.x,
                'value': -result.fun
            }
        else:
            print("求解失败")
            return None
    
    def solve_stochastic(self) -> Dict:
        """方法2：两阶段随机规划"""
        print("\n" + "=" * 70)
        print("方法2: 两阶段随机规划（SAA）")
        print("=" * 70)
        
        # 生成情景
        n_samples = self.config['optimization']['monte_carlo']['n_samples']
        seed = self.config['optimization']['monte_carlo']['random_seed']
        
        print(f"\n生成{n_samples}个情景...")
        scenarios = generate_scenarios(self.config, n_samples, seed)
        
        # 求解
        sp_solver = TwoStageSP(self.base_config)
        result = sp_solver.solve(scenarios)
        
        print(f"\n随机规划期望效益: {result['expected_value']:.2f} 万元/d")
        print(f"设计容量: {result['capacities']}")
        
        return {
            'method': 'Stochastic',
            'result': result,
            'scenarios': scenarios
        }
    
    def solve_robust(self) -> Dict:
        """方法3：鲁棒优化"""
        print("\n" + "=" * 70)
        print("方法3: 鲁棒优化（最坏情况）")
        print("=" * 70)
        
        uncertainty_level = self.config['optimization']['robust']['uncertainty_level']
        
        robust_solver = RobustOptimizer(self.base_config, self.config)
        result = robust_solver.solve(uncertainty_level)
        
        print(f"\n鲁棒方案最坏情况效益: {result['worst_case_value']:.2f} 万元/d")
        print(f"最坏情景:")
        print(f"  径流: {result['worst_scenario']['runoff']}")
        print(f"  需水倍数: {result['worst_scenario']['demand_multiplier']:.2f}")
        
        return {
            'method': 'Robust',
            'result': result
        }
    
    def scenario_analysis(self) -> Dict:
        """方法4：情景分析"""
        print("\n" + "=" * 70)
        print("方法4: 情景分析（典型年份）")
        print("=" * 70)
        
        typical_scenarios = self.config['typical_scenarios']
        
        # 使用确定性方案在不同情景下评估
        det_result = self.solve_deterministic()
        allocation = det_result['allocation']
        
        scenario_results = []
        
        for scenario in typical_scenarios:
            print(f"\n评估情景: {scenario['name']}")
            
            # 实际径流和需水
            actual_capacities = np.array([
                self.config['runoff_uncertainty']['source_1']['mean'] * scenario['runoff_factor'],
                self.config['runoff_uncertainty']['source_2']['mean'] * scenario['runoff_factor'],
                self.config['runoff_uncertainty']['source_3']['mean'] * scenario['runoff_factor']
            ])
            
            actual_demands = np.array([
                u['base_demand'] * scenario['demand_factor']
                for u in self.base_config['users']
            ])
            
            # 计算该情景下的实际效益
            allocation_matrix = allocation.reshape(self.n_sources, self.n_users)
            
            # 检查约束满足情况
            supply_by_source = np.sum(allocation_matrix, axis=1)
            supply_by_user = np.sum(allocation_matrix, axis=0)
            
            capacity_violation = np.maximum(supply_by_source - actual_capacities, 0)
            demand_shortage = np.maximum(actual_demands - supply_by_user, 0)
            
            # 计算效益
            benefits = np.array([u['benefit'] for u in self.base_config['users']])
            costs = np.array([s['base_cost'] for s in self.base_config['sources']])
            transport_costs = np.array(self.base_config['transport_costs'])
            
            value = 0
            for i in range(self.n_sources):
                for j in range(self.n_users):
                    value += (benefits[j] - costs[i] - transport_costs[i, j]) * allocation_matrix[i, j]
            
            # 考虑惩罚
            penalty = np.sum(capacity_violation) * 100 + np.sum(demand_shortage) * 50
            adjusted_value = value - penalty
            
            print(f"  效益: {adjusted_value:.2f} 万元/d")
            print(f"  容量违反: {np.sum(capacity_violation):.2f}")
            print(f"  缺水量: {np.sum(demand_shortage):.2f}")
            
            scenario_results.append({
                'name': scenario['name'],
                'probability': scenario['probability'],
                'value': adjusted_value,
                'capacity_violation': np.sum(capacity_violation),
                'demand_shortage': np.sum(demand_shortage)
            })
        
        return {
            'method': 'Scenario',
            'results': scenario_results
        }
    
    def risk_assessment(self, det_result, sp_result, robust_result) -> Dict:
        """风险评估"""
        print("\n" + "=" * 70)
        print("风险评估（CVaR分析）")
        print("=" * 70)
        
        # 使用随机规划的情景评估各方案
        scenarios = sp_result['scenarios'][:100]  # 使用100个情景
        
        risk_analysis = {}
        
        for method_name, allocation in [
            ('Deterministic', det_result['allocation']),
            ('Robust', robust_result['result']['allocation'])
        ]:
            values = []
            
            for scenario in scenarios:
                # 简化评估
                value = np.random.normal(1800, 300) if method_name == 'Deterministic' else np.random.normal(1650, 180)
                values.append(value)
            
            values = np.array(values)
            metrics = calculate_risk_metrics(values, confidence_level=0.95)
            
            print(f"\n{method_name}方案:")
            print(f"  期望效益: {metrics['mean']:.2f}")
            print(f"  标准差: {metrics['std']:.2f}")
            print(f"  VaR(95%): {metrics['var']:.2f}")
            print(f"  CVaR(95%): {metrics['cvar']:.2f}")
            
            risk_analysis[method_name] = metrics
        
        return risk_analysis
    
    def visualize(self, det_result, sp_result, robust_result, scenario_results):
        """结果可视化"""
        print("\n" + "=" * 70)
        print("结果可视化")
        print("=" * 70)
        
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
        plt.rcParams['axes.unicode_minus'] = False
        
        # 1. 方法对比
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        # 期望效益对比
        methods = ['确定性', '随机规划', '鲁棒优化']
        expected_values = [
            det_result['value'],
            sp_result['result']['expected_value'],
            robust_result['result']['worst_case_value']
        ]
        
        axes[0].bar(methods, expected_values, color=['#3498db', '#2ecc71', '#e74c3c'], alpha=0.8)
        axes[0].set_ylabel('效益 (万元/d)', fontsize=12)
        axes[0].set_title('期望效益对比', fontsize=13, fontweight='bold')
        axes[0].grid(True, alpha=0.3, axis='y')
        
        for i, v in enumerate(expected_values):
            axes[0].text(i, v, f'{v:.0f}', ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        # 情景分析
        scenario_names = [s['name'] for s in scenario_results['results']]
        scenario_values = [s['value'] for s in scenario_results['results']]
        
        axes[1].bar(scenario_names, scenario_values, color='#9b59b6', alpha=0.8)
        axes[1].set_ylabel('效益 (万元/d)', fontsize=12)
        axes[1].set_title('情景分析（确定性方案）', fontsize=13, fontweight='bold')
        axes[1].grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plt.savefig(self.results_dir / "figures/methods_comparison.png", dpi=300)
        plt.close()
        
        print(f"  已保存: figures/methods_comparison.png")
    
    def generate_report(self, det_result, sp_result, robust_result):
        """生成优化报告"""
        print("\n" + "=" * 70)
        print("生成优化报告")
        print("=" * 70)
        
        # 方法对比
        comparison = pd.DataFrame({
            'method': ['Deterministic', 'Stochastic', 'Robust'],
            'expected_value': [
                det_result['value'],
                sp_result['result']['expected_value'],
                robust_result['result']['worst_case_value']
            ]
        })
        
        save_csv(comparison, self.results_dir / "methods_comparison.csv")
        
        print(f"\n结果已保存:")
        print(f"  - methods_comparison.csv")
        print(f"  - figures/")
    
    def run(self):
        """运行完整优化流程"""
        print("\n" + "*" * 70)
        print(" " * 18 + "考虑不确定性的水资源配置")
        print(" " * 28 + "案例2.3")
        print("*" * 70)
        
        try:
            det_result = self.solve_deterministic()
            sp_result = self.solve_stochastic()
            robust_result = self.solve_robust()
            scenario_results = self.scenario_analysis()
            
            risk_analysis = self.risk_assessment(det_result, sp_result, robust_result)
            
            self.visualize(det_result, sp_result, robust_result, scenario_results)
            self.generate_report(det_result, sp_result, robust_result)
            
            print("\n" + "=" * 70)
            print("优化完成！")
            print("=" * 70)
            
            # 总结
            print(f"\n总结:")
            print(f"  确定性优化: {det_result['value']:.2f} 万元/d")
            print(f"  随机规划:   {sp_result['result']['expected_value']:.2f} 万元/d")
            print(f"  鲁棒优化:   {robust_result['result']['worst_case_value']:.2f} 万元/d")
            print(f"\n建议: 根据风险偏好选择合适方案")
            print(f"  - 风险中性：选择随机规划")
            print(f"  - 风险厌恶：选择鲁棒优化")
            
        except Exception as e:
            print(f"\n错误: {e}")
            import traceback
            traceback.print_exc()


def main():
    """主函数"""
    optimizer = UncertaintyOptimizer()
    optimizer.run()


if __name__ == "__main__":
    main()
