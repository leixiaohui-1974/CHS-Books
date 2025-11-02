"""
案例19：智能决策支持系统 - 主程序

整合评价、优化、风险分析，提供综合决策支持

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

from core.decision import ahp, topsis
from core.optimization import solve_linear_programming
from core.risk import MonteCarloSimulator, VaRCalculator


class DecisionSupportSystem:
    """智能决策支持系统"""
    
    def __init__(self):
        self.results_dir = Path("results")
        self.results_dir.mkdir(exist_ok=True)
        (self.results_dir / "figures").mkdir(exist_ok=True)
        
        # 系统参数
        self.water_sources = ['水库', '地下水', '外调水']
        self.n_sources = len(self.water_sources)
        
        # 评价指标
        self.criteria = ['供水保证率', '总成本', '环境影响', '风险水平', '技术可行性']
        
        print(f"智能决策支持系统")
        print(f"水源数: {self.n_sources}")
        print(f"评价指标: {len(self.criteria)}个")
    
    def generate_scheme_deterministic(self):
        """
        方案A：确定性优化
        
        目标：最小化成本
        """
        print("\n" + "=" * 70)
        print("方案A：确定性优化")
        print("=" * 70)
        
        # 简化线性规划
        # min: 成本 = 2*x1 + 3*x2 + 4*x3
        # s.t.: x1 + x2 + x3 >= 100 (满足需水)
        #       x1 <= 50, x2 <= 40, x3 <= 30 (水源能力)
        
        c = np.array([2, 3, 4])  # 成本系数
        
        # 不等式约束 A_ub * x <= b_ub
        A_ub = np.array([
            [-1, -1, -1],  # 需水约束（转为<=）
            [1, 0, 0],     # 水库能力
            [0, 1, 0],     # 地下水能力
            [0, 0, 1]      # 外调水能力
        ])
        b_ub = np.array([-100, 50, 40, 30])
        
        result = solve_linear_programming(c, A_ub, b_ub)
        
        if result['success']:
            allocation = result['x']
            cost = result['fun']
            
            print(f"\n最优配置:")
            for i, source in enumerate(self.water_sources):
                print(f"  {source}: {allocation[i]:.1f}万m³")
            print(f"总成本: {cost:.0f}万元")
            
            # 评估指标
            reliability = 95  # 确定性假设
            env_score = 75  # 环境影响评分（0-100）
            risk = 0.15  # 风险水平
            feasibility = 90  # 技术可行性
            
            return {
                'name': '方案A（确定性）',
                'allocation': allocation,
                'indicators': {
                    '供水保证率': reliability,
                    '总成本': cost,
                    '环境影响': env_score,
                    '风险水平': risk * 100,
                    '技术可行性': feasibility
                }
            }
        else:
            print("优化失败！")
            return None
    
    def generate_scheme_robust(self):
        """
        方案B：鲁棒优化
        
        考虑需水不确定性
        """
        print("\n" + "=" * 70)
        print("方案B：鲁棒优化")
        print("=" * 70)
        
        # 考虑需水量不确定性（90-110万m³）
        def robust_objective(x):
            cost = 2*x[0] + 3*x[1] + 4*x[2]
            
            # 最坏情景：需水110万m³
            worst_shortage = max(0, 110 - sum(x))
            penalty = worst_shortage * 10  # 缺水惩罚
            
            return cost + penalty
        
        def constraints(x):
            return [
                x[0] + x[1] + x[2] - 95,  # 至少满足95万m³
                50 - x[0],  # 水库能力
                40 - x[1],  # 地下水能力
                30 - x[2],  # 外调水能力
                x[0], x[1], x[2]  # 非负
            ]
        
        x0 = np.array([40, 35, 25])
        bounds = [(0, 50), (0, 40), (0, 30)]
        
        cons = {'type': 'ineq', 'fun': constraints}
        
        result = minimize(robust_objective, x0, bounds=bounds, constraints=cons)
        
        if result.success:
            allocation = result.x
            cost = 2*allocation[0] + 3*allocation[1] + 4*allocation[2]
            
            print(f"\n鲁棒配置:")
            for i, source in enumerate(self.water_sources):
                print(f"  {source}: {allocation[i]:.1f}万m³")
            print(f"总成本: {cost:.0f}万元")
            
            # 评估指标（更保守）
            reliability = 93  # 稍低但更稳健
            env_score = 82  # 更好的环境表现
            risk = 0.08  # 更低风险
            feasibility = 92
            
            return {
                'name': '方案B（鲁棒）',
                'allocation': allocation,
                'indicators': {
                    '供水保证率': reliability,
                    '总成本': cost,
                    '环境影响': env_score,
                    '风险水平': risk * 100,
                    '技术可行性': feasibility
                }
            }
        else:
            print("优化失败！")
            return None
    
    def generate_scheme_multiobjective(self):
        """
        方案C：多目标优化
        
        平衡成本、环境和风险
        """
        print("\n" + "=" * 70)
        print("方案C：多目标优化")
        print("=" * 70)
        
        # 权重
        w_cost = 0.4
        w_env = 0.3
        w_risk = 0.3
        
        def multi_objective(x):
            # 成本
            cost = 2*x[0] + 3*x[1] + 4*x[2]
            cost_norm = cost / 300  # 归一化
            
            # 环境影响（地下水影响大）
            env_impact = 0.5*x[0] + 1.0*x[1] + 0.3*x[2]
            env_norm = env_impact / 100
            
            # 风险（外调水风险大）
            risk = 0.2*x[0] + 0.1*x[1] + 0.8*x[2]
            risk_norm = risk / 50
            
            return w_cost*cost_norm + w_env*env_norm + w_risk*risk_norm
        
        def constraints(x):
            return [
                x[0] + x[1] + x[2] - 100,
                50 - x[0],
                40 - x[1],
                30 - x[2],
                x[0], x[1], x[2]
            ]
        
        x0 = np.array([45, 35, 20])
        bounds = [(0, 50), (0, 40), (0, 30)]
        
        cons = {'type': 'ineq', 'fun': constraints}
        
        result = minimize(multi_objective, x0, bounds=bounds, constraints=cons)
        
        if result.success:
            allocation = result.x
            cost = 2*allocation[0] + 3*allocation[1] + 4*allocation[2]
            
            print(f"\n多目标配置:")
            for i, source in enumerate(self.water_sources):
                print(f"  {source}: {allocation[i]:.1f}万m³")
            print(f"总成本: {cost:.0f}万元")
            
            # 评估指标（平衡）
            reliability = 96
            env_score = 80
            risk = 0.10
            feasibility = 93
            
            return {
                'name': '方案C（多目标）',
                'allocation': allocation,
                'indicators': {
                    '供水保证率': reliability,
                    '总成本': cost,
                    '环境影响': env_score,
                    '风险水平': risk * 100,
                    '技术可行性': feasibility
                }
            }
        else:
            print("优化失败！")
            return None
    
    def evaluate_schemes(self, schemes):
        """
        多准则评估方案
        
        使用AHP-TOPSIS
        """
        print("\n" + "=" * 70)
        print("多准则评估")
        print("=" * 70)
        
        # 1. AHP确定权重
        print("\n1. AHP确定指标权重:")
        
        # 判断矩阵（简化）
        judgment_matrix = np.array([
            [1,   2,   3,   2,   1],  # 供水保证率
            [1/2, 1,   2,   1,   1/2],  # 总成本
            [1/3, 1/2, 1,   1/2, 1/3],  # 环境影响
            [1/2, 1,   2,   1,   1/2],  # 风险水平
            [1,   2,   3,   2,   1]   # 技术可行性
        ])
        
        weights, cr = ahp(judgment_matrix)
        
        print(f"\n指标权重:")
        for i, criterion in enumerate(self.criteria):
            print(f"  {criterion}: {weights[i]:.3f}")
        print(f"一致性比率CR: {cr:.4f}")
        
        # 2. 构造决策矩阵
        print("\n2. 构造决策矩阵:")
        
        decision_matrix = []
        for scheme in schemes:
            indicators = scheme['indicators']
            row = [
                indicators['供水保证率'],
                indicators['总成本'],
                indicators['环境影响'],
                indicators['风险水平'],
                indicators['技术可行性']
            ]
            decision_matrix.append(row)
        
        decision_matrix = np.array(decision_matrix)
        
        # 打印矩阵
        print(f"\n决策矩阵:")
        print(f"{'方案':<15}", end='')
        for criterion in self.criteria:
            print(f"{criterion:<12}", end='')
        print()
        
        for i, scheme in enumerate(schemes):
            print(f"{scheme['name']:<15}", end='')
            for val in decision_matrix[i]:
                print(f"{val:<12.1f}", end='')
            print()
        
        # 3. TOPSIS评估
        print("\n3. TOPSIS评估:")
        
        # 属性类型（成本型、效益型）
        criteria_types = ['benefit', 'cost', 'benefit', 'cost', 'benefit']
        
        scores, ranking = topsis(decision_matrix, weights, criteria_types)
        
        print(f"\nTOPSIS得分和排序:")
        results = []
        for i, scheme in enumerate(schemes):
            results.append((scheme['name'], scores[i], ranking[i]))
            print(f"  {scheme['name']}: 得分={scores[i]:.4f}, 排名={ranking[i]}")
        
        # 排序
        results.sort(key=lambda x: x[2])
        
        print(f"\n推荐方案: {results[0][0]}")
        
        return results
    
    def visualize(self, schemes, evaluation_results):
        """结果可视化"""
        print("\n" + "=" * 70)
        print("结果可视化")
        print("=" * 70)
        
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
        plt.rcParams['axes.unicode_minus'] = False
        
        fig, axes = plt.subplots(2, 3, figsize=(16, 10))
        
        # 1. 水源配置对比
        x = np.arange(len(self.water_sources))
        width = 0.25
        colors = ['#4ECDC4', '#FF6B6B', '#FFD93D']
        
        for i, scheme in enumerate(schemes):
            offset = (i - 1) * width
            axes[0, 0].bar(x + offset, scheme['allocation'], width, 
                          label=scheme['name'], color=colors[i], alpha=0.7)
        
        axes[0, 0].set_xticks(x)
        axes[0, 0].set_xticklabels(self.water_sources)
        axes[0, 0].set_ylabel('配水量 (万m³)', fontsize=11)
        axes[0, 0].set_title('水源配置对比', fontsize=12, fontweight='bold')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3, axis='y')
        
        # 2. 雷达图（指标对比）
        angles = np.linspace(0, 2 * np.pi, len(self.criteria), endpoint=False).tolist()
        angles += angles[:1]
        
        ax = plt.subplot(232, projection='polar')
        
        for i, scheme in enumerate(schemes):
            values = []
            for criterion in self.criteria:
                val = scheme['indicators'][criterion]
                # 归一化（0-100）
                if criterion == '总成本':
                    val = 100 - val / 15  # 成本越低越好
                elif criterion == '风险水平':
                    val = 100 - val
                values.append(val)
            
            values += values[:1]
            
            ax.plot(angles, values, 'o-', linewidth=2, label=scheme['name'], 
                   color=colors[i], alpha=0.7)
            ax.fill(angles, values, alpha=0.15, color=colors[i])
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(self.criteria, fontsize=9)
        ax.set_ylim(0, 100)
        ax.set_title('综合指标雷达图', fontsize=12, fontweight='bold', pad=20)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
        ax.grid(True)
        
        # 3. TOPSIS得分
        names = [r[0] for r in evaluation_results]
        scores = [r[1] for r in evaluation_results]
        
        bars = axes[0, 2].barh(names, scores, color=colors, alpha=0.7)
        axes[0, 2].set_xlabel('TOPSIS得分', fontsize=11)
        axes[0, 2].set_title('方案综合评分', fontsize=12, fontweight='bold')
        axes[0, 2].grid(True, alpha=0.3, axis='x')
        
        for bar, score in zip(bars, scores):
            width = bar.get_width()
            axes[0, 2].text(width, bar.get_y() + bar.get_height()/2,
                          f'{score:.4f}',
                          ha='left', va='center', fontsize=10)
        
        # 4. 成本对比
        costs = [s['indicators']['总成本'] for s in schemes]
        scheme_names = [s['name'] for s in schemes]
        
        axes[1, 0].bar(scheme_names, costs, color=colors, alpha=0.7)
        axes[1, 0].set_ylabel('总成本 (万元)', fontsize=11)
        axes[1, 0].set_title('成本对比', fontsize=12, fontweight='bold')
        axes[1, 0].grid(True, alpha=0.3, axis='y')
        
        # 5. 风险对比
        risks = [s['indicators']['风险水平'] for s in schemes]
        
        axes[1, 1].bar(scheme_names, risks, color=colors, alpha=0.7)
        axes[1, 1].set_ylabel('风险水平 (%)', fontsize=11)
        axes[1, 1].set_title('风险对比', fontsize=12, fontweight='bold')
        axes[1, 1].grid(True, alpha=0.3, axis='y')
        
        # 6. 综合排名
        rankings = [r[2] for r in evaluation_results]
        
        axes[1, 2].bar(names, rankings, color=colors, alpha=0.7)
        axes[1, 2].set_ylabel('排名', fontsize=11)
        axes[1, 2].set_title('综合排名（越小越好）', fontsize=12, fontweight='bold')
        axes[1, 2].set_ylim(0, len(schemes) + 0.5)
        axes[1, 2].invert_yaxis()
        axes[1, 2].grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plt.savefig(self.results_dir / "figures/decision_support.png", 
                   dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"  已保存: figures/decision_support.png")
    
    def run(self):
        """运行决策支持系统"""
        print("\n" + "*" * 70)
        print(" " * 18 + "智能决策支持系统")
        print(" " * 28 + "案例19")
        print("*" * 70)
        
        try:
            # 生成方案
            schemeA = self.generate_scheme_deterministic()
            schemeB = self.generate_scheme_robust()
            schemeC = self.generate_scheme_multiobjective()
            
            schemes = [schemeA, schemeB, schemeC]
            
            # 评估方案
            evaluation_results = self.evaluate_schemes(schemes)
            
            # 可视化
            self.visualize(schemes, evaluation_results)
            
            print("\n" + "=" * 70)
            print("决策分析完成！")
            print("=" * 70)
            
            print(f"\n决策建议:")
            print(f"  最优方案: {evaluation_results[0][0]}")
            print(f"  综合得分: {evaluation_results[0][1]:.4f}")
            
        except Exception as e:
            print(f"\n错误: {e}")
            import traceback
            traceback.print_exc()


def main():
    """主函数"""
    dss = DecisionSupportSystem()
    dss.run()


if __name__ == "__main__":
    main()
