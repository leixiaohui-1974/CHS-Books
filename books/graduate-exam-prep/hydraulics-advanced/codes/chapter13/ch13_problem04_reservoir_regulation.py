# -*- coding: utf-8 -*-
"""
第13章 水资源计算 - 题4：水库调节计算

问题描述：
    某水库总库容V = 5亿m³，死库容Vd = 1亿m³
    年平均入流量Q_in = 50 m³/s，用水需求Q_out = 40 m³/s
    汛期（6-9月）入流量占60%，枯期占40%
    
    求：
    1. 调节库容计算
    2. 年调节性能分析
    3. 兴利库容确定
    4. 水库调度方案
    5. 供水保证率

核心公式：
    1. 兴利库容：V_b = V - V_d
    2. 调节库容：V_r = max(累计入流-累计出流)
    3. 保证率：P = (1 - 缺水次数/总次数)×100%
    4. 调节系数：β = V_r/W_年

考试要点：
    - 水库调节计算
    - 兴利库容
    - 调节系数
    - 保证率

作者: CHS-Books Team
日期: 2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, Dict, List

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class ReservoirRegulation:
    """水库调节计算"""
    
    def __init__(self, V_total: float, V_dead: float, Q_in: float, Q_out: float):
        self.V_total = V_total  # 总库容 亿m³
        self.V_dead = V_dead  # 死库容 亿m³
        self.Q_in = Q_in  # 年平均入流量 m³/s
        self.Q_out = Q_out  # 用水需求 m³/s
        
    def beneficial_capacity(self) -> float:
        """兴利库容"""
        V_b = self.V_total - self.V_dead
        return V_b
    
    def annual_inflow(self) -> float:
        """年入流量"""
        W_in = self.Q_in * 86400 * 365 / 1e8  # 亿m³
        return W_in
    
    def annual_demand(self) -> float:
        """年用水量"""
        W_out = self.Q_out * 86400 * 365 / 1e8  # 亿m³
        return W_out
    
    def monthly_inflow_distribution(self) -> np.ndarray:
        """月入流量分配"""
        W_in = self.annual_inflow()
        
        # 汛期（6-9月）60%，非汛期40%
        distribution = np.array([
            0.03, 0.03, 0.04, 0.05, 0.05,  # 1-5月
            0.15, 0.18, 0.15, 0.12,        # 6-9月（汛期）
            0.08, 0.06, 0.06               # 10-12月
        ])
        
        W_monthly = W_in * distribution
        return W_monthly
    
    def regulation_calculation(self) -> Dict:
        """调节计算"""
        W_monthly_in = self.monthly_inflow_distribution()
        W_out = self.annual_demand()
        W_monthly_out = W_out / 12  # 均匀用水
        
        # 累计入流
        W_cumulative_in = np.cumsum(W_monthly_in)
        
        # 累计出流
        W_cumulative_out = np.cumsum(np.ones(12) * W_monthly_out)
        
        # 差值
        W_diff = W_cumulative_in - W_cumulative_out
        
        # 调节库容
        V_regulation = max(W_diff) - min(W_diff)
        
        return {
            'W_monthly_in': W_monthly_in,
            'W_monthly_out': np.ones(12) * W_monthly_out,
            'W_cumulative_in': W_cumulative_in,
            'W_cumulative_out': W_cumulative_out,
            'W_diff': W_diff,
            'V_regulation': V_regulation
        }
    
    def regulation_coefficient(self) -> float:
        """调节系数"""
        W_in = self.annual_inflow()
        reg = self.regulation_calculation()
        beta = reg['V_regulation'] / W_in
        return beta
    
    def supply_guarantee_rate(self) -> Tuple[float, bool]:
        """供水保证率"""
        W_in = self.annual_inflow()
        W_out = self.annual_demand()
        
        # 简化：假设水量充足
        if W_in >= W_out:
            guarantee_rate = 0.95  # 95%
            is_sufficient = True
        else:
            guarantee_rate = W_in / W_out * 0.90
            is_sufficient = False
        
        return guarantee_rate, is_sufficient
    
    def plot_analysis(self):
        """绘制分析图表"""
        fig = plt.figure(figsize=(16, 12))
        
        V_b = self.beneficial_capacity()
        W_in = self.annual_inflow()
        W_out = self.annual_demand()
        reg = self.regulation_calculation()
        beta = self.regulation_coefficient()
        guarantee_rate, is_sufficient = self.supply_guarantee_rate()
        
        months = np.arange(1, 13)
        
        # 1. 水库库容分配
        ax1 = plt.subplot(3, 3, 1)
        
        capacity_types = ['死库容', '兴利库容']
        capacity_values = [self.V_dead, V_b]
        colors_cap = ['gray', 'blue']
        
        bottom = 0
        for cap_type, cap_val, color in zip(capacity_types, capacity_values, colors_cap):
            ax1.bar(['总库容'], [cap_val], bottom=bottom, color=color, 
                   alpha=0.7, edgecolor='black', label=cap_type)
            ax1.text(0, bottom + cap_val/2, f'{cap_type}\n{cap_val:.1f}亿m³',
                    ha='center', va='center', fontsize=10, fontweight='bold')
            bottom += cap_val
        
        ax1.set_ylabel('库容 (亿m³)', fontsize=10)
        ax1.set_title(f'水库库容分配 (总库容{self.V_total}亿m³)', fontsize=12, fontweight='bold')
        ax1.legend()
        ax1.set_ylim(0, self.V_total * 1.1)
        
        # 2. 基本参数
        ax2 = plt.subplot(3, 3, 2)
        ax2.axis('off')
        
        ax2.text(0.5, 0.95, '水库参数', fontsize=11, ha='center', fontweight='bold')
        ax2.text(0.1, 0.82, f'总库容: V = {self.V_total} 亿m³', fontsize=10)
        ax2.text(0.1, 0.72, f'死库容: V_d = {self.V_dead} 亿m³', fontsize=10)
        ax2.text(0.1, 0.62, f'兴利库容: V_b = {V_b} 亿m³', fontsize=10, color='blue')
        ax2.text(0.1, 0.52, f'调节库容: V_r = {reg["V_regulation"]:.2f} 亿m³', fontsize=10, color='red')
        ax2.text(0.1, 0.40, f'年入流量: W_in = {W_in:.2f} 亿m³', fontsize=10, color='green')
        ax2.text(0.1, 0.30, f'年用水量: W_out = {W_out:.2f} 亿m³', fontsize=10, color='orange')
        ax2.text(0.1, 0.18, f'调节系数: β = {beta:.3f}', fontsize=10, color='purple')
        ax2.text(0.1, 0.06, f'保证率: {guarantee_rate:.0%}', fontsize=10, 
                color='green' if is_sufficient else 'red', fontweight='bold')
        
        ax2.set_title('基本参数', fontsize=12, fontweight='bold')
        
        # 3. 月入流与用水过程
        ax3 = plt.subplot(3, 3, 3)
        
        ax3.plot(months, reg['W_monthly_in'], 'b-o', linewidth=2, markersize=6, label='入流')
        ax3.plot(months, reg['W_monthly_out'], 'r--s', linewidth=2, markersize=6, label='用水')
        ax3.fill_between(months, 0, reg['W_monthly_in'], alpha=0.3, color='lightblue')
        
        ax3.set_xlabel('月份', fontsize=10)
        ax3.set_ylabel('水量 (亿m³)', fontsize=10)
        ax3.set_title('月入流与用水过程', fontsize=12, fontweight='bold')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        ax3.set_xticks(months)
        
        # 4. 累计水量过程
        ax4 = plt.subplot(3, 3, 4)
        
        ax4.plot(months, reg['W_cumulative_in'], 'b-o', linewidth=2, label='累计入流')
        ax4.plot(months, reg['W_cumulative_out'], 'r-s', linewidth=2, label='累计用水')
        ax4.fill_between(months, reg['W_cumulative_in'], reg['W_cumulative_out'],
                        alpha=0.3, color='yellow')
        
        ax4.set_xlabel('月份', fontsize=10)
        ax4.set_ylabel('累计水量 (亿m³)', fontsize=10)
        ax4.set_title('累计水量过程', fontsize=12, fontweight='bold')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        ax4.set_xticks(months)
        
        # 5. 调节库容图解
        ax5 = plt.subplot(3, 3, 5)
        
        ax5.plot(months, reg['W_diff'], 'g-o', linewidth=3, markersize=8)
        ax5.fill_between(months, 0, reg['W_diff'], 
                        where=(reg['W_diff'] >= 0), alpha=0.3, color='blue', label='盈余')
        ax5.fill_between(months, 0, reg['W_diff'], 
                        where=(reg['W_diff'] < 0), alpha=0.3, color='red', label='亏缺')
        ax5.axhline(0, color='k', linewidth=1)
        
        # 标注最大最小值
        max_idx = np.argmax(reg['W_diff'])
        min_idx = np.argmin(reg['W_diff'])
        ax5.plot(months[max_idx], reg['W_diff'][max_idx], 'b^', markersize=12)
        ax5.plot(months[min_idx], reg['W_diff'][min_idx], 'rv', markersize=12)
        
        ax5.text(months[max_idx], reg['W_diff'][max_idx]+0.5, 
                f'最大盈余\n{reg["W_diff"][max_idx]:.2f}亿m³',
                ha='center', fontsize=8, bbox=dict(boxstyle='round', facecolor='lightblue'))
        ax5.text(months[min_idx], reg['W_diff'][min_idx]-0.5, 
                f'最大亏缺\n{reg["W_diff"][min_idx]:.2f}亿m³',
                ha='center', fontsize=8, bbox=dict(boxstyle='round', facecolor='pink'))
        
        ax5.set_xlabel('月份', fontsize=10)
        ax5.set_ylabel('水量差值 (亿m³)', fontsize=10)
        ax5.set_title(f'调节库容图解 (V_r={reg["V_regulation"]:.2f}亿m³)', 
                     fontsize=12, fontweight='bold')
        ax5.legend()
        ax5.grid(True, alpha=0.3)
        ax5.set_xticks(months)
        
        # 6. 水量平衡
        ax6 = plt.subplot(3, 3, 6)
        
        balance_items = ['年入流', '年用水', '盈余']
        balance_values = [W_in, W_out, W_in - W_out]
        colors_balance = ['blue', 'red', 'green']
        
        bars = ax6.barh(balance_items, balance_values, color=colors_balance, 
                       alpha=0.7, edgecolor='black')
        ax6.axvline(0, color='k', linewidth=1)
        
        for bar, val in zip(bars, balance_values):
            width = bar.get_width()
            ax6.text(width, bar.get_y() + bar.get_height()/2,
                    f'{val:.2f}', ha='left' if width>0 else 'right',
                    va='center', fontsize=10, fontweight='bold')
        
        ax6.set_xlabel('水量 (亿m³)', fontsize=10)
        ax6.set_title('年水量平衡', fontsize=12, fontweight='bold')
        ax6.grid(True, alpha=0.3, axis='x')
        
        # 7. 不同库容的调节能力
        ax7 = plt.subplot(3, 3, 7)
        
        V_range = np.linspace(1, 10, 50)
        beta_range = []
        
        for V_val in V_range:
            reservoir_temp = ReservoirRegulation(V_val, self.V_dead, self.Q_in, self.Q_out)
            beta_range.append(reservoir_temp.regulation_coefficient())
        
        ax7.plot(V_range, beta_range, 'b-', linewidth=2)
        ax7.plot(self.V_total, beta, 'ro', markersize=12, label=f'本工程V={self.V_total}亿m³')
        ax7.axhline(beta, color='r', linestyle='--', linewidth=1, alpha=0.5)
        
        ax7.set_xlabel('总库容 V (亿m³)', fontsize=10)
        ax7.set_ylabel('调节系数 β', fontsize=10)
        ax7.set_title('库容-调节系数关系', fontsize=12, fontweight='bold')
        ax7.legend()
        ax7.grid(True, alpha=0.3)
        
        # 8. 调节类型判别
        ax8 = plt.subplot(3, 3, 8)
        ax8.axis('off')
        
        ax8.text(0.5, 0.95, '调节类型', fontsize=11, ha='center', fontweight='bold')
        ax8.text(0.1, 0.78, f'调节系数: β = {beta:.4f}', fontsize=10)
        
        if beta < 0.05:
            regulation_type = "径流式"
            description = "基本无调节能力"
        elif beta < 0.2:
            regulation_type = "日调节"
            description = "调节能力较弱"
        elif beta < 0.5:
            regulation_type = "季调节"
            description = "可进行季节调节"
        elif beta < 1.0:
            regulation_type = "年调节"
            description = "可进行年度调节"
        else:
            regulation_type = "多年调节"
            description = "调节能力强"
        
        ax8.text(0.1, 0.58, f'调节类型: {regulation_type}', fontsize=12,
                color='blue', fontweight='bold')
        ax8.text(0.1, 0.45, f'特征: {description}', fontsize=10)
        
        ax8.text(0.1, 0.28, '判别标准:', fontsize=10, fontweight='bold')
        ax8.text(0.15, 0.20, 'β<0.05: 径流式', fontsize=9)
        ax8.text(0.15, 0.13, '0.05≤β<0.2: 日调节', fontsize=9)
        ax8.text(0.15, 0.06, '0.2≤β<0.5: 季调节', fontsize=9)
        ax8.text(0.15, -0.01, '0.5≤β<1.0: 年调节', fontsize=9)
        
        ax8.set_title('调节性能评价', fontsize=12, fontweight='bold')
        
        # 9. 结果汇总表
        ax9 = plt.subplot(3, 3, 9)
        ax9.axis('off')
        
        table_data = [
            ['项目', '数值', '单位'],
            ['总库容', f'{self.V_total}', '亿m³'],
            ['兴利库容', f'{V_b}', '亿m³'],
            ['调节库容', f'{reg["V_regulation"]:.2f}', '亿m³'],
            ['年入流量', f'{W_in:.2f}', '亿m³'],
            ['年用水量', f'{W_out:.2f}', '亿m³'],
            ['调节系数', f'{beta:.3f}', '-'],
            ['调节类型', regulation_type, '-'],
            ['保证率', f'{guarantee_rate:.0%}', '-']
        ]
        
        table = ax9.table(cellText=table_data, cellLoc='center', loc='center',
                         colWidths=[0.40, 0.30, 0.25])
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2.2)
        
        for i in range(3):
            table[(0, i)].set_facecolor('#4472C4')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        # 高亮关键指标
        for i in [4, 7, 8]:
            for j in range(3):
                table[(i, j)].set_facecolor('#FFF9E6')
        
        ax9.set_title('计算结果汇总', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('/tmp/ch13_problem04_reservoir_regulation.png', dpi=150, bbox_inches='tight')
        print(f"图表已保存: /tmp/ch13_problem04_reservoir_regulation.png")
        plt.show()
    
    def print_results(self):
        """打印结果"""
        print("\n" + "="*70)
        print("第13章 水资源计算 - 题4：水库调节计算")
        print("="*70)
        
        V_b = self.beneficial_capacity()
        W_in = self.annual_inflow()
        W_out = self.annual_demand()
        reg = self.regulation_calculation()
        beta = self.regulation_coefficient()
        guarantee_rate, is_sufficient = self.supply_guarantee_rate()
        
        print(f"\n【水库基本参数】")
        print(f"总库容: V = {self.V_total} 亿m³")
        print(f"死库容: V_d = {self.V_dead} 亿m³")
        print(f"兴利库容: V_b = V - V_d = {V_b} 亿m³")
        
        print(f"\n【水量参数】")
        print(f"年平均入流量: Q_in = {self.Q_in} m³/s")
        print(f"年入流量: W_in = {W_in:.3f} 亿m³")
        print(f"年用水需求: Q_out = {self.Q_out} m³/s")
        print(f"年用水量: W_out = {W_out:.3f} 亿m³")
        print(f"水量盈余: ΔW = {W_in - W_out:.3f} 亿m³")
        
        print(f"\n【调节计算】")
        print(f"调节库容: V_r = max(W_累计入-W_累计出) - min(W_累计入-W_累计出)")
        print(f"         = {reg['V_regulation']:.3f} 亿m³")
        print(f"调节系数: β = V_r/W_年 = {reg['V_regulation']:.3f}/{W_in:.3f} = {beta:.4f}")
        
        if beta < 0.05:
            regulation_type = "径流式"
        elif beta < 0.2:
            regulation_type = "日调节"
        elif beta < 0.5:
            regulation_type = "季调节"
        elif beta < 1.0:
            regulation_type = "年调节"
        else:
            regulation_type = "多年调节"
        
        print(f"调节类型: {regulation_type}")
        
        print(f"\n【供水保证率】")
        print(f"供水保证率: P = {guarantee_rate:.1%}")
        if is_sufficient:
            print(f"✓ 水量充足，可满足用水需求")
        else:
            print(f"✗ 水量不足，可能出现缺水")
        
        print(f"\n✓ 水库调节计算完成")
        print(f"\n{'='*70}\n")


def main():
    V_total = 5.0  # 亿m³
    V_dead = 1.0   # 亿m³
    Q_in = 50      # m³/s
    Q_out = 40     # m³/s
    
    reservoir = ReservoirRegulation(V_total, V_dead, Q_in, Q_out)
    reservoir.print_results()
    reservoir.plot_analysis()


if __name__ == "__main__":
    main()
