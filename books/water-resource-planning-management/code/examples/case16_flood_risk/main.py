"""
案例6.1：洪水风险评估 - 主程序

使用蒙特卡洛和VaR/CVaR进行风险分析

作者：教材编写组
日期：2025-11-02
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../"))

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import pearson3

from core.risk import (
    MonteCarloSimulator,
    VaRCalculator,
    CVaRCalculator,
    calculate_probability_of_failure
)


class FloodRiskAssessment:
    """洪水风险评估系统"""
    
    def __init__(self):
        self.results_dir = Path("results")
        self.results_dir.mkdir(exist_ok=True)
        (self.results_dir / "figures").mkdir(exist_ok=True)
        
        # 历史洪水数据（年最大洪峰，m³/s）
        self.historical_floods = np.array([
            5200, 6800, 4500, 7200, 5800, 6100, 4800, 8500, 5500, 6300,
            7000, 5100, 6500, 4900, 7800, 5600, 6700, 5300, 9200, 6000,
            5400, 7500, 6200, 5700, 8000, 5900, 6400, 5000, 7300, 6600
        ])
        
        print(f"洪水风险评估系统")
        print(f"历史洪水样本: {len(self.historical_floods)}年")
        print(f"最大洪峰: {self.historical_floods.max():.0f} m³/s")
        print(f"平均洪峰: {self.historical_floods.mean():.0f} m³/s")
    
    def frequency_analysis(self):
        """频率分析（Pearson-III分布）"""
        print("\n" + "=" * 70)
        print("洪水频率分析（Pearson-III分布）")
        print("=" * 70)
        
        # 计算统计参数
        mean = np.mean(self.historical_floods)
        std = np.std(self.historical_floods, ddof=1)
        skew = ((self.historical_floods - mean) ** 3).mean() / (std ** 3)
        
        print(f"\n统计参数:")
        print(f"  均值: {mean:.1f} m³/s")
        print(f"  标准差: {std:.1f} m³/s")
        print(f"  偏态系数: {skew:.3f}")
        
        # 设计洪水
        return_periods = [10, 20, 50, 100, 200]
        design_floods = {}
        
        print(f"\n设计洪水:")
        for T in return_periods:
            # 超越概率
            p = 1 / T
            
            # Pearson-III分布分位数
            # 使用scipy的pearson3（需要转换参数）
            q = pearson3.ppf(1 - p, skew, loc=mean, scale=std)
            
            design_floods[T] = q
            print(f"  {T}年一遇: {q:.0f} m³/s")
        
        return design_floods, {'mean': mean, 'std': std, 'skew': skew}
    
    def damage_function(self, flood_peak, design_capacity):
        """
        损失函数
        
        Parameters
        ----------
        flood_peak : float
            洪峰流量
        design_capacity : float
            设计防洪能力
        
        Returns
        -------
        float
            经济损失（万元）
        """
        if flood_peak <= design_capacity:
            return 0
        
        # 超标倍数
        excess_ratio = (flood_peak - design_capacity) / design_capacity
        
        # 分级损失模型
        if excess_ratio < 0.1:
            # 轻度超标：线性损失
            damage = 1000 * excess_ratio / 0.1
        elif excess_ratio < 0.3:
            # 中度超标：加速损失
            damage = 1000 + 3000 * (excess_ratio - 0.1) / 0.2
        else:
            # 严重超标：溃坝
            damage = 4000 + 6000 * min((excess_ratio - 0.3) / 0.2, 1.0)
        
        return damage
    
    def monte_carlo_risk(self, design_capacity, params, n_simulations=10000):
        """蒙特卡洛风险模拟"""
        
        # 生成随机洪水样本
        floods = pearson3.rvs(
            params['skew'],
            loc=params['mean'],
            scale=params['std'],
            size=n_simulations
        )
        
        # 计算损失
        damages = np.array([self.damage_function(q, design_capacity) for q in floods])
        
        # 风险指标
        failure_prob = calculate_probability_of_failure(floods, design_capacity)
        expected_damage = np.mean(damages)
        
        # VaR和CVaR
        var_calc = VaRCalculator(confidence_level=0.95)
        cvar_calc = CVaRCalculator(confidence_level=0.95)
        
        # 转换为负收益（损失）
        returns = -damages
        var = var_calc.calculate_historical(returns)
        var_val, cvar_val = cvar_calc.calculate(returns)
        
        return {
            'floods': floods,
            'damages': damages,
            'failure_prob': failure_prob,
            'expected_damage': expected_damage,
            'var_95': var,
            'cvar_95': cvar_val,
            'max_damage': damages.max()
        }
    
    def compare_standards(self, design_floods, params):
        """对比不同防洪标准"""
        print("\n" + "=" * 70)
        print("对比不同防洪标准")
        print("=" * 70)
        
        standards = [20, 50, 100, 200]
        results = {}
        
        for T in standards:
            design_capacity = design_floods[T]
            
            print(f"\n{T}年一遇标准 (Q={design_capacity:.0f} m³/s):")
            
            risk_result = self.monte_carlo_risk(design_capacity, params, n_simulations=10000)
            
            print(f"  失效概率: {risk_result['failure_prob']*100:.2f}%")
            print(f"  年期望损失: {risk_result['expected_damage']:.0f}万元")
            print(f"  VaR(95%): {risk_result['var_95']:.0f}万元")
            print(f"  CVaR(95%): {risk_result['cvar_95']:.0f}万元")
            print(f"  最大损失: {risk_result['max_damage']:.0f}万元")
            
            results[T] = risk_result
        
        return results
    
    def visualize(self, design_floods, params, comparison_results):
        """结果可视化"""
        print("\n" + "=" * 70)
        print("结果可视化")
        print("=" * 70)
        
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
        plt.rcParams['axes.unicode_minus'] = False
        
        fig = plt.figure(figsize=(16, 10))
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        # 1. 频率曲线
        ax1 = fig.add_subplot(gs[0, :2])
        
        return_periods = np.array([10, 20, 50, 100, 200, 500, 1000])
        design_values = []
        for T in return_periods:
            p = 1 / T
            q = pearson3.ppf(1 - p, params['skew'], loc=params['mean'], scale=params['std'])
            design_values.append(q)
        
        ax1.semilogx(return_periods, design_values, 'b-', linewidth=2, label='设计曲线')
        
        # 标记常用标准
        for T in [20, 50, 100, 200]:
            ax1.plot(T, design_floods[T], 'ro', markersize=8)
            ax1.text(T, design_floods[T], f' {T}年', fontsize=9)
        
        ax1.set_xlabel('重现期 (年)', fontsize=11)
        ax1.set_ylabel('设计洪峰 (m³/s)', fontsize=11)
        ax1.set_title('洪水频率曲线', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        # 2. 风险指标对比
        ax2 = fig.add_subplot(gs[0, 2])
        
        standards = list(comparison_results.keys())
        failure_probs = [comparison_results[T]['failure_prob'] * 100 for T in standards]
        
        ax2.bar(range(len(standards)), failure_probs, color='#FF6B6B', alpha=0.7)
        ax2.set_xticks(range(len(standards)))
        ax2.set_xticklabels([f'{T}年' for T in standards])
        ax2.set_ylabel('失效概率 (%)', fontsize=11)
        ax2.set_title('失效概率', fontsize=11, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='y')
        
        # 3. 期望损失
        ax3 = fig.add_subplot(gs[1, 0])
        
        expected_damages = [comparison_results[T]['expected_damage'] for T in standards]
        
        ax3.bar(range(len(standards)), expected_damages, color='#FFD93D', alpha=0.7)
        ax3.set_xticks(range(len(standards)))
        ax3.set_xticklabels([f'{T}年' for T in standards])
        ax3.set_ylabel('期望损失 (万元)', fontsize=11)
        ax3.set_title('年期望损失', fontsize=11, fontweight='bold')
        ax3.grid(True, alpha=0.3, axis='y')
        
        # 4. VaR vs CVaR
        ax4 = fig.add_subplot(gs[1, 1])
        
        var_values = [comparison_results[T]['var_95'] for T in standards]
        cvar_values = [comparison_results[T]['cvar_95'] for T in standards]
        
        x = np.arange(len(standards))
        width = 0.35
        
        ax4.bar(x - width/2, var_values, width, label='VaR(95%)', color='#4ECDC4', alpha=0.7)
        ax4.bar(x + width/2, cvar_values, width, label='CVaR(95%)', color='#45B7D1', alpha=0.7)
        
        ax4.set_xticks(x)
        ax4.set_xticklabels([f'{T}年' for T in standards])
        ax4.set_ylabel('风险值 (万元)', fontsize=11)
        ax4.set_title('VaR与CVaR对比', fontsize=11, fontweight='bold')
        ax4.legend()
        ax4.grid(True, alpha=0.3, axis='y')
        
        # 5. 损失分布（100年一遇）
        ax5 = fig.add_subplot(gs[1, 2])
        
        damages_100 = comparison_results[100]['damages']
        ax5.hist(damages_100[damages_100 > 0], bins=50, color='#95E1D3', alpha=0.7, edgecolor='black')
        ax5.axvline(comparison_results[100]['expected_damage'], color='r', 
                   linestyle='--', linewidth=2, label='期望损失')
        ax5.axvline(comparison_results[100]['var_95'], color='orange', 
                   linestyle='--', linewidth=2, label='VaR(95%)')
        
        ax5.set_xlabel('损失 (万元)', fontsize=11)
        ax5.set_ylabel('频数', fontsize=11)
        ax5.set_title('损失分布（100年标准）', fontsize=11, fontweight='bold')
        ax5.legend()
        ax5.grid(True, alpha=0.3, axis='y')
        
        # 6. 风险-成本权衡
        ax6 = fig.add_subplot(gs[2, :])
        
        # 假设建设成本（与标准成正比）
        construction_costs = np.array([design_floods[T] * 5 for T in standards])  # 简化
        
        # 总成本 = 建设成本 + 年期望损失现值（按50年计算）
        discount_rate = 0.05
        years = 50
        pv_factor = (1 - (1 + discount_rate) ** -years) / discount_rate
        
        total_costs = construction_costs + np.array(expected_damages) * pv_factor
        
        ax6_twin = ax6.twinx()
        
        line1 = ax6.plot(standards, construction_costs, 'b-o', linewidth=2, 
                        label='建设成本', markersize=8)
        line2 = ax6.plot(standards, np.array(expected_damages) * pv_factor, 
                        'r-s', linewidth=2, label='损失现值', markersize=8)
        line3 = ax6_twin.plot(standards, total_costs, 'g-^', linewidth=2.5, 
                             label='总成本', markersize=8)
        
        # 标记最优点
        optimal_idx = np.argmin(total_costs)
        optimal_standard = standards[optimal_idx]
        ax6_twin.plot(optimal_standard, total_costs[optimal_idx], 'r*', 
                     markersize=20, label='最优标准')
        
        ax6.set_xlabel('防洪标准 (年)', fontsize=12)
        ax6.set_ylabel('成本 (万元)', fontsize=12, color='b')
        ax6_twin.set_ylabel('总成本 (万元)', fontsize=12, color='g')
        ax6.set_title('风险-成本权衡分析', fontsize=13, fontweight='bold')
        
        # 合并图例
        lines = line1 + line2 + line3
        labels = [l.get_label() for l in lines]
        ax6.legend(lines, labels, loc='upper left', fontsize=10)
        
        ax6.grid(True, alpha=0.3)
        
        plt.savefig(self.results_dir / "figures/flood_risk_assessment.png", 
                   dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"  已保存: figures/flood_risk_assessment.png")
        
        # 输出最优标准
        print(f"\n经济最优标准: {optimal_standard}年一遇")
        print(f"  建设成本: {construction_costs[optimal_idx]:.0f}万元")
        print(f"  损失现值: {expected_damages[optimal_idx] * pv_factor:.0f}万元")
        print(f"  总成本: {total_costs[optimal_idx]:.0f}万元")
    
    def run(self):
        """运行风险评估"""
        print("\n" + "*" * 70)
        print(" " * 22 + "洪水风险评估")
        print(" " * 28 + "案例6.1")
        print("*" * 70)
        
        try:
            # 频率分析
            design_floods, params = self.frequency_analysis()
            
            # 对比不同标准
            comparison_results = self.compare_standards(design_floods, params)
            
            # 可视化
            self.visualize(design_floods, params, comparison_results)
            
            print("\n" + "=" * 70)
            print("洪水风险评估完成！")
            print("=" * 70)
            
        except Exception as e:
            print(f"\n错误: {e}")
            import traceback
            traceback.print_exc()


def main():
    """主函数"""
    assessment = FloodRiskAssessment()
    assessment.run()


if __name__ == "__main__":
    main()
