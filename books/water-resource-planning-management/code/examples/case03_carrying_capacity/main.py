"""
案例1.3：水资源承载能力评价 - 主程序

综合运用AHP、熵权法、TOPSIS等多准则决策方法

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

from core.utils.data_io import load_csv, load_yaml, save_csv
from core.decision import AHP, TOPSIS, EntropyWeight, FuzzyEvaluation


class CarryingCapacityEvaluator:
    """水资源承载能力评价系统"""
    
    def __init__(self, data_dir: str = "data", results_dir: str = "results"):
        self.data_dir = Path(data_dir)
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True)
        (self.results_dir / "figures").mkdir(exist_ok=True)
        
        self.data = None
        self.params = None
        self.weights = {}
    
    def load_data(self):
        """加载数据"""
        print("=" * 70)
        print("步骤1: 加载数据")
        print("=" * 70)
        
        self.data = load_csv(self.data_dir / "indicators_data.csv")
        self.params = load_yaml(self.data_dir / "evaluation_parameters.yaml")
        
        print(f"\n已加载{len(self.data)}个指标数据")
        print(f"评价维度: {len(self.params['dimensions'])}个")
        
        # 显示数据摘要
        print(f"\n指标分布:")
        for dim in self.data['dimension'].unique():
            count = len(self.data[self.data['dimension'] == dim])
            print(f"  {dim}: {count}个指标")
    
    def method1_ahp(self):
        """方法1：AHP确定权重"""
        print("\n" + "=" * 70)
        print("步骤2: AHP层次分析法")
        print("=" * 70)
        
        # 维度层权重
        matrix = np.array(self.params['dimension_judgment_matrix'])
        
        ahp = AHP()
        weights, CR = ahp.calculate_weights(matrix)
        
        print(f"\n维度权重:")
        for i, dim in enumerate(self.params['dimensions']):
            print(f"  {dim['name']}: {weights[i]:.4f}")
        
        print(f"\n一致性检验:")
        print(f"  CR = {CR:.4f}", end="")
        if CR < 0.10:
            print(" (通过)")
        else:
            print(" (未通过，需调整判断矩阵)")
        
        self.weights['ahp'] = weights
        self.weights['CR'] = CR
    
    def method2_entropy(self):
        """方法2：熵权法"""
        print("\n" + "=" * 70)
        print("步骤3: 熵权法客观赋权")
        print("=" * 70)
        
        # 准备数据矩阵（按维度分组）
        dimensions = self.data['dimension'].unique()
        dim_weights = []
        
        for dim in dimensions:
            dim_data = self.data[self.data['dimension'] == dim]['value'].values
            # 简化：用指标值的变异系数作为权重依据
            cv = np.std(dim_data) / (np.mean(dim_data) + 1e-10)
            dim_weights.append(cv)
        
        # 归一化
        dim_weights = np.array(dim_weights)
        dim_weights = dim_weights / np.sum(dim_weights)
        
        print(f"\n熵权法权重:")
        for i, dim in enumerate(dimensions):
            print(f"  {dim}: {dim_weights[i]:.4f}")
        
        self.weights['entropy'] = dim_weights
    
    def method3_combination(self):
        """方法3：组合赋权"""
        print("\n" + "=" * 70)
        print("步骤4: 组合赋权")
        print("=" * 70)
        
        alpha = self.params['combination_weight_alpha']
        
        w_combined = alpha * self.weights['ahp'] + (1 - alpha) * self.weights['entropy']
        
        print(f"\n组合权重 (α={alpha}):")
        dimensions = self.data['dimension'].unique()
        for i, dim in enumerate(dimensions):
            print(f"  {dim}: {w_combined[i]:.4f}")
            print(f"    - AHP: {self.weights['ahp'][i]:.4f}")
            print(f"    - 熵权: {self.weights['entropy'][i]:.4f}")
        
        self.weights['combined'] = w_combined
    
    def method4_topsis(self):
        """方法4: TOPSIS综合评价"""
        print("\n" + "=" * 70)
        print("步骤5: TOPSIS综合评价")
        print("=" * 70)
        
        # 构造决策矩阵（维度层面）
        dimensions = self.data['dimension'].unique()
        dim_scores = []
        
        for dim in dimensions:
            dim_data = self.data[self.data['dimension'] == dim]
            # 计算该维度的平均得分（简化）
            avg_score = dim_data['value'].mean()
            dim_scores.append(avg_score)
        
        # 归一化到0-100
        dim_scores = np.array(dim_scores)
        dim_scores = (dim_scores - dim_scores.min()) / (dim_scores.max() - dim_scores.min()) * 100
        
        # 构造单行矩阵（一个评价对象）
        matrix = dim_scores.reshape(1, -1)
        
        # TOPSIS评价
        topsis = TOPSIS()
        scores = topsis.calculate(matrix, self.weights['combined'])
        
        print(f"\nTOPSIS综合得分: {scores[0]:.4f}")
        
        # 判定承载状态
        score = scores[0]
        for grade_key, grade_info in self.params['carrying_capacity_grades'].items():
            if grade_info['range'][0] <= score <= grade_info['range'][1]:
                print(f"承载状态: {grade_info['label']} ({grade_info['description']})")
                break
        
        self.weights['topsis_score'] = scores[0]
        self.weights['dimension_scores'] = dim_scores
    
    def analyze_results(self):
        """结果分析"""
        print("\n" + "=" * 70)
        print("步骤6: 结果分析")
        print("=" * 70)
        
        print(f"\n维度贡献度分析:")
        dimensions = self.data['dimension'].unique()
        contributions = self.weights['combined'] * self.weights['dimension_scores'] / 100
        
        for i, dim in enumerate(dimensions):
            print(f"  {dim}: {contributions[i]:.4f} (权重{self.weights['combined'][i]:.3f} × 得分{self.weights['dimension_scores'][i]:.1f})")
        
        # 识别薄弱环节
        weakest_idx = np.argmin(self.weights['dimension_scores'])
        print(f"\n薄弱环节: {dimensions[weakest_idx]} (得分: {self.weights['dimension_scores'][weakest_idx]:.1f})")
        
        # 找出该维度的具体问题指标
        weak_dim_data = self.data[self.data['dimension'] == dimensions[weakest_idx]]
        print(f"\n该维度的指标情况:")
        for _, row in weak_dim_data.iterrows():
            print(f"  - {row['indicator']}: {row['value']}")
    
    def visualize(self):
        """结果可视化"""
        print("\n" + "=" * 70)
        print("步骤7: 结果可视化")
        print("=" * 70)
        
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
        
        dimensions = self.data['dimension'].unique()
        
        # 1. 权重对比图
        print("\n绘制权重对比图...")
        fig, ax = plt.subplots(figsize=(12, 6))
        x = np.arange(len(dimensions))
        width = 0.25
        
        ax.bar(x - width, self.weights['ahp'], width, label='AHP权重')
        ax.bar(x, self.weights['entropy'], width, label='熵权法')
        ax.bar(x + width, self.weights['combined'], width, label='组合权重')
        
        ax.set_xlabel('评价维度', fontsize=12)
        ax.set_ylabel('权重', fontsize=12)
        ax.set_title('权重对比分析', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(dimensions, rotation=15, ha='right')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plt.savefig(self.results_dir / "figures/weights_comparison.png", dpi=300)
        plt.close()
        
        # 2. 维度得分雷达图
        print("绘制雷达图...")
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
        
        angles = np.linspace(0, 2 * np.pi, len(dimensions), endpoint=False)
        scores = self.weights['dimension_scores']
        
        # 闭合图形
        angles = np.concatenate((angles, [angles[0]]))
        scores = np.concatenate((scores, [scores[0]]))
        
        ax.plot(angles, scores, 'o-', linewidth=2, label='当前状态')
        ax.fill(angles, scores, alpha=0.25)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(dimensions)
        ax.set_ylim(0, 100)
        ax.set_title('水资源承载能力雷达图', fontsize=14, fontweight='bold', pad=20)
        ax.legend(loc='upper right')
        ax.grid(True)
        
        plt.tight_layout()
        plt.savefig(self.results_dir / "figures/radar_chart.png", dpi=300)
        plt.close()
        
        print(f"  已保存: {self.results_dir}/figures/")
    
    def generate_report(self):
        """生成评价报告"""
        print("\n" + "=" * 70)
        print("步骤8: 生成评价报告")
        print("=" * 70)
        
        # 保存权重对比
        dimensions = self.data['dimension'].unique()
        weights_df = pd.DataFrame({
            'dimension': dimensions,
            'ahp_weight': self.weights['ahp'],
            'entropy_weight': self.weights['entropy'],
            'combined_weight': self.weights['combined'],
            'dimension_score': self.weights['dimension_scores']
        })
        save_csv(weights_df, self.results_dir / "weights_comparison.csv")
        
        print(f"\n评价结果已保存:")
        print(f"  - weights_comparison.csv: 权重对比")
        print(f"  - figures/: 可视化图表")
    
    def run(self):
        """运行完整评价流程"""
        print("\n" + "*" * 70)
        print(" " * 18 + "水资源承载能力评价系统")
        print(" " * 25 + "案例1.3")
        print("*" * 70)
        
        try:
            self.load_data()
            self.method1_ahp()
            self.method2_entropy()
            self.method3_combination()
            self.method4_topsis()
            self.analyze_results()
            self.visualize()
            self.generate_report()
            
            print("\n" + "=" * 70)
            print("评价完成！")
            print("=" * 70)
            
        except Exception as e:
            print(f"\n错误: {e}")
            import traceback
            traceback.print_exc()


def main():
    """主函数"""
    evaluator = CarryingCapacityEvaluator(
        data_dir="data",
        results_dir="results"
    )
    evaluator.run()


if __name__ == "__main__":
    main()
