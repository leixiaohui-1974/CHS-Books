"""
案例2.1：区域水资源多目标优化配置 - 主程序

运用线性规划、GA、PSO、NSGA-II求解多目标优化问题

作者：教材编写组
日期：2025-11-02
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../"))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from core.utils.data_io import load_yaml, save_csv
from core.optimization import LinearProgramming, GeneticAlgorithm, PSO, NSGAII


class WaterAllocationOptimizer:
    """水资源多目标优化配置系统"""
    
    def __init__(self, config_file: str = "data/problem_config.yaml"):
        self.config = load_yaml(config_file)
        self.results_dir = Path("results")
        self.results_dir.mkdir(exist_ok=True)
        (self.results_dir / "figures").mkdir(exist_ok=True)
        
        # 提取问题参数
        self.n_sources = len(self.config['sources'])
        self.n_users = len(self.config['users'])
        self.n_vars = self.n_sources * self.n_users
        
        self.capacities = np.array([s['capacity'] for s in self.config['sources']])
        self.demands = np.array([u['demand'] for u in self.config['users']])
        self.benefits = np.array([u['benefit'] for u in self.config['users']])
        self.guarantee_rates = np.array([u['guarantee_rate'] for u in self.config['users']])
        self.transport_costs = np.array(self.config['transport_costs'])
        
        # 变量边界
        self.bounds = []
        for i in range(self.n_sources):
            for j in range(self.n_users):
                self.bounds.append((0, self.capacities[i]))
        
        print(f"问题规模: {self.n_sources}个水源 × {self.n_users}个用户 = {self.n_vars}个变量")
    
    def decode_solution(self, x: np.ndarray) -> np.ndarray:
        """将一维解向量转换为配置矩阵"""
        return x.reshape(self.n_sources, self.n_users)
    
    def objective_benefit(self, x: np.ndarray) -> float:
        """目标1：经济效益（最大化）"""
        allocation = self.decode_solution(x)
        
        # 效益 = Σ(效益系数 - 输水成本) × 配水量
        benefit = 0
        for i in range(self.n_sources):
            for j in range(self.n_users):
                net_benefit = self.benefits[j] - self.transport_costs[i, j]
                benefit += net_benefit * allocation[i, j]
        
        return benefit
    
    def objective_shortage(self, x: np.ndarray) -> float:
        """目标2：缺水量（最小化）"""
        allocation = self.decode_solution(x)
        
        # 各用户实际供水量
        supply = np.sum(allocation, axis=0)
        
        # 缺水量
        shortage = np.sum(np.maximum(self.demands - supply, 0))
        
        return shortage
    
    def check_constraints(self, x: np.ndarray) -> Tuple[float, Dict]:
        """检查约束违反情况"""
        allocation = self.decode_solution(x)
        violations = {}
        total_penalty = 0
        
        # 1. 水源供水能力约束
        supply_by_source = np.sum(allocation, axis=1)
        capacity_violation = np.maximum(supply_by_source - self.capacities, 0)
        violations['capacity'] = capacity_violation
        total_penalty += np.sum(capacity_violation) * self.config['penalty']['capacity_violation']
        
        # 2. 需水保障约束
        supply_by_user = np.sum(allocation, axis=0)
        required_supply = self.demands * self.guarantee_rates
        demand_violation = np.maximum(required_supply - supply_by_user, 0)
        violations['demand'] = demand_violation
        total_penalty += np.sum(demand_violation) * self.config['penalty']['demand_violation']
        
        return total_penalty, violations
    
    def method1_linear_programming(self):
        """方法1：线性规划求解"""
        print("\n" + "=" * 70)
        print("方法1: 线性规划（加权法）")
        print("=" * 70)
        
        results = []
        
        for w1, w2 in self.config['optimization']['lp']['weights']:
            print(f"\n权重组合: 效益={w1:.1f}, 缺水={w2:.1f}")
            
            # 构造目标函数：min -w1·效益 + w2·缺水
            c = []
            for i in range(self.n_sources):
                for j in range(self.n_users):
                    net_benefit = self.benefits[j] - self.transport_costs[i, j]
                    c_ij = -w1 * net_benefit + w2
                    c.append(c_ij)
            c = np.array(c)
            
            # 约束1: 水源能力
            A_ub_cap = np.zeros((self.n_sources, self.n_vars))
            for i in range(self.n_sources):
                for j in range(self.n_users):
                    idx = i * self.n_users + j
                    A_ub_cap[i, idx] = 1
            b_ub_cap = self.capacities
            
            # 约束2: 需水保障
            A_ub_dem = np.zeros((self.n_users, self.n_vars))
            for j in range(self.n_users):
                for i in range(self.n_sources):
                    idx = i * self.n_users + j
                    A_ub_dem[j, idx] = -1
            b_ub_dem = -self.demands * self.guarantee_rates
            
            A_ub = np.vstack([A_ub_cap, A_ub_dem])
            b_ub = np.concatenate([b_ub_cap, b_ub_dem])
            
            # 求解
            lp = LinearProgramming()
            result = lp.solve(c, A_ub, b_ub, bounds=[(0, None)] * self.n_vars)
            
            if result['success']:
                x = result['x']
                benefit = self.objective_benefit(x)
                shortage = self.objective_shortage(x)
                
                print(f"  经济效益: {benefit:.2f} 万元/d")
                print(f"  缺水量: {shortage:.2f} 万m³/d")
                
                results.append({
                    'method': 'LP',
                    'weight_benefit': w1,
                    'weight_shortage': w2,
                    'benefit': benefit,
                    'shortage': shortage,
                    'solution': x
                })
        
        # 保存结果
        df = pd.DataFrame([{
            'method': r['method'],
            'weight_benefit': r['weight_benefit'],
            'weight_shortage': r['weight_shortage'],
            'benefit': r['benefit'],
            'shortage': r['shortage']
        } for r in results])
        save_csv(df, self.results_dir / "lp_results.csv")
        
        return results
    
    def method2_genetic_algorithm(self):
        """方法2：遗传算法"""
        print("\n" + "=" * 70)
        print("方法2: 遗传算法（单目标加权）")
        print("=" * 70)
        
        # 加权目标函数（最大化）
        def fitness_func(x):
            benefit = self.objective_benefit(x)
            shortage = self.objective_shortage(x)
            penalty, _ = self.check_constraints(x)
            
            # 归一化后加权
            return 0.7 * benefit / 2000 - 0.3 * shortage / 100 - penalty
        
        ga = GeneticAlgorithm(
            pop_size=self.config['optimization']['ga']['pop_size'],
            n_genes=self.n_vars,
            bounds=self.bounds,
            crossover_rate=self.config['optimization']['ga']['crossover_rate'],
            mutation_rate=self.config['optimization']['ga']['mutation_rate']
        )
        
        best_x, best_f = ga.optimize(fitness_func, n_generations=self.config['optimization']['ga']['n_generations'])
        
        benefit = self.objective_benefit(best_x)
        shortage = self.objective_shortage(best_x)
        
        print(f"\n最优解:")
        print(f"  经济效益: {benefit:.2f} 万元/d")
        print(f"  缺水量: {shortage:.2f} 万m³/d")
        print(f"  适应度: {best_f:.4f}")
        
        return {'method': 'GA', 'benefit': benefit, 'shortage': shortage, 'solution': best_x}
    
    def method3_pso(self):
        """方法3：粒子群算法"""
        print("\n" + "=" * 70)
        print("方法3: 粒子群算法（PSO）")
        print("=" * 70)
        
        # 目标函数（最小化）
        def objective_func(x):
            benefit = self.objective_benefit(x)
            shortage = self.objective_shortage(x)
            penalty, _ = self.check_constraints(x)
            
            # 多目标加权（最小化）
            return -0.7 * benefit / 2000 + 0.3 * shortage / 100 + penalty
        
        pso = PSO(
            n_particles=self.config['optimization']['pso']['n_particles'],
            n_dims=self.n_vars,
            bounds=self.bounds,
            w=self.config['optimization']['pso']['w'],
            c1=self.config['optimization']['pso']['c1'],
            c2=self.config['optimization']['pso']['c2']
        )
        
        best_x, best_f = pso.optimize(objective_func, n_iterations=self.config['optimization']['pso']['n_iterations'], minimize=True)
        
        benefit = self.objective_benefit(best_x)
        shortage = self.objective_shortage(best_x)
        
        print(f"\n最优解:")
        print(f"  经济效益: {benefit:.2f} 万元/d")
        print(f"  缺水量: {shortage:.2f} 万m³/d")
        
        return {'method': 'PSO', 'benefit': benefit, 'shortage': shortage, 'solution': best_x}
    
    def method4_nsga2(self):
        """方法4：NSGA-II多目标优化"""
        print("\n" + "=" * 70)
        print("方法4: NSGA-II多目标优化")
        print("=" * 70)
        
        # 多目标函数（最小化）
        def objectives(x):
            benefit = self.objective_benefit(x)
            shortage = self.objective_shortage(x)
            penalty, _ = self.check_constraints(x)
            
            # 目标1: 负效益（转为最小化）
            obj1 = -benefit + penalty * 1000
            # 目标2: 缺水量
            obj2 = shortage + penalty * 1000
            
            return [obj1, obj2]
        
        nsga2 = NSGAII(
            pop_size=self.config['optimization']['nsga2']['pop_size'],
            n_vars=self.n_vars,
            n_objs=2,
            bounds=self.bounds,
            crossover_rate=self.config['optimization']['nsga2']['crossover_rate'],
            mutation_rate=self.config['optimization']['nsga2']['mutation_rate']
        )
        
        result = nsga2.optimize(objectives, n_generations=self.config['optimization']['nsga2']['n_generations'])
        
        # Pareto前沿
        pareto_solutions = result['pareto_solutions']
        pareto_objectives = result['pareto_objectives']
        
        print(f"\nPareto前沿包含 {len(pareto_solutions)} 个非支配解")
        
        # 转换回原目标（效益、缺水）
        pareto_data = []
        for i, (sol, obj) in enumerate(zip(pareto_solutions, pareto_objectives)):
            benefit = self.objective_benefit(sol)
            shortage = self.objective_shortage(sol)
            pareto_data.append({
                'solution_id': i,
                'benefit': benefit,
                'shortage': shortage
            })
        
        df = pd.DataFrame(pareto_data)
        save_csv(df, self.results_dir / "pareto_front.csv")
        
        return {'method': 'NSGA-II', 'pareto_front': pareto_data, 'pareto_solutions': pareto_solutions}
    
    def visualize(self, lp_results, ga_result, pso_result, nsga2_result):
        """结果可视化"""
        print("\n" + "=" * 70)
        print("结果可视化")
        print("=" * 70)
        
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
        plt.rcParams['axes.unicode_minus'] = False
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # LP结果
        lp_benefits = [r['benefit'] for r in lp_results]
        lp_shortages = [r['shortage'] for r in lp_results]
        ax.plot(lp_benefits, lp_shortages, 'o-', label='LP (加权法)', markersize=8)
        
        # GA结果
        ax.plot(ga_result['benefit'], ga_result['shortage'], 'r*', label='GA', markersize=15)
        
        # PSO结果
        ax.plot(pso_result['benefit'], pso_result['shortage'], 'g^', label='PSO', markersize=12)
        
        # NSGA-II Pareto前沿
        pareto = nsga2_result['pareto_front']
        pareto_b = [p['benefit'] for p in pareto]
        pareto_s = [p['shortage'] for p in pareto]
        ax.scatter(pareto_b, pareto_s, c='blue', alpha=0.6, s=50, label='NSGA-II Pareto前沿')
        
        ax.set_xlabel('经济效益 (万元/d)', fontsize=12)
        ax.set_ylabel('缺水量 (万m³/d)', fontsize=12)
        ax.set_title('多目标优化结果对比', fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.results_dir / "figures/pareto_comparison.png", dpi=300)
        plt.close()
        
        print(f"  已保存: figures/pareto_comparison.png")
    
    def run(self):
        """运行完整优化流程"""
        print("\n" + "*" * 70)
        print(" " * 20 + "区域水资源多目标优化配置")
        print(" " * 28 + "案例2.1")
        print("*" * 70)
        
        try:
            lp_results = self.method1_linear_programming()
            ga_result = self.method2_genetic_algorithm()
            pso_result = self.method3_pso()
            nsga2_result = self.method4_nsga2()
            
            self.visualize(lp_results, ga_result, pso_result, nsga2_result)
            
            print("\n" + "=" * 70)
            print("优化完成！")
            print("=" * 70)
            
        except Exception as e:
            print(f"\n错误: {e}")
            import traceback
            traceback.print_exc()


def main():
    """主函数"""
    optimizer = WaterAllocationOptimizer("data/problem_config.yaml")
    optimizer.run()


if __name__ == "__main__":
    main()
