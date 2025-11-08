# -*- coding: utf-8 -*-
"""
第13章 水资源计算 - 题7：水资源配置

问题描述：
    某区域总水资源量W = 10亿m³/年
    生活用水需求：0.8亿m³/年，优先级最高
    工业用水需求：3.5亿m³/年，优先级次之
    农业用水需求：6.0亿m³/年，优先级最低
    生态用水需求：0.5亿m³/年，刚性需求
    
    求：
    1. 水资源平衡分析
    2. 配置方案优化
    3. 各部门分配比例
    4. 缺水风险评估
    5. 综合效益分析

核心公式：
    1. 水资源平衡：W_供 = W_需 + W_损失
    2. 缺水率：η = (W_需 - W_供)/W_需
    3. 综合效益：B = Σ(w_i × b_i)

考试要点：
    - 水资源配置
    - 供需平衡
    - 优先级排序
    - 效益分析

作者: CHS-Books Team
日期: 2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, Dict, List

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class WaterAllocation:
    """水资源配置"""
    
    def __init__(self, W_total: float, W_domestic: float, W_industrial: float,
                 W_agricultural: float, W_ecological: float):
        self.W_total = W_total  # 总水资源量 亿m³
        self.W_domestic = W_domestic  # 生活用水 亿m³
        self.W_industrial = W_industrial  # 工业用水 亿m³
        self.W_agricultural = W_agricultural  # 农业用水 亿m³
        self.W_ecological = W_ecological  # 生态用水 亿m³
        
    def total_demand(self) -> float:
        """总需求"""
        W_demand = (self.W_domestic + self.W_industrial + 
                   self.W_agricultural + self.W_ecological)
        return W_demand
    
    def water_balance(self) -> Dict:
        """水资源平衡分析"""
        W_demand = self.total_demand()
        W_deficit = max(0, W_demand - self.W_total)
        W_surplus = max(0, self.W_total - W_demand)
        deficit_rate = W_deficit / W_demand if W_demand > 0 else 0
        
        return {
            'W_supply': self.W_total,
            'W_demand': W_demand,
            'W_deficit': W_deficit,
            'W_surplus': W_surplus,
            'deficit_rate': deficit_rate
        }
    
    def allocation_scheme(self) -> Dict:
        """配置方案（按优先级）"""
        W_available = self.W_total
        
        # 优先级排序：生活 > 生态 > 工业 > 农业
        allocations = {}
        
        # 1. 生活用水（最高优先级）
        W_domestic_alloc = min(self.W_domestic, W_available)
        allocations['domestic'] = W_domestic_alloc
        W_available -= W_domestic_alloc
        
        # 2. 生态用水（刚性需求）
        W_ecological_alloc = min(self.W_ecological, W_available)
        allocations['ecological'] = W_ecological_alloc
        W_available -= W_ecological_alloc
        
        # 3. 工业用水
        W_industrial_alloc = min(self.W_industrial, W_available)
        allocations['industrial'] = W_industrial_alloc
        W_available -= W_industrial_alloc
        
        # 4. 农业用水
        W_agricultural_alloc = min(self.W_agricultural, W_available)
        allocations['agricultural'] = W_agricultural_alloc
        W_available -= W_agricultural_alloc
        
        return {
            'domestic': W_domestic_alloc,
            'ecological': W_ecological_alloc,
            'industrial': W_industrial_alloc,
            'agricultural': W_agricultural_alloc,
            'remaining': W_available
        }
    
    def allocation_ratio(self) -> Dict:
        """各部门分配比例"""
        alloc = self.allocation_scheme()
        
        return {
            'domestic': alloc['domestic'] / self.W_total,
            'ecological': alloc['ecological'] / self.W_total,
            'industrial': alloc['industrial'] / self.W_total,
            'agricultural': alloc['agricultural'] / self.W_total,
            'remaining': alloc['remaining'] / self.W_total
        }
    
    def shortage_assessment(self) -> Dict:
        """缺水风险评估"""
        alloc = self.allocation_scheme()
        
        shortage = {
            'domestic': self.W_domestic - alloc['domestic'],
            'ecological': self.W_ecological - alloc['ecological'],
            'industrial': self.W_industrial - alloc['industrial'],
            'agricultural': self.W_agricultural - alloc['agricultural']
        }
        
        shortage_rate = {
            'domestic': shortage['domestic'] / self.W_domestic if self.W_domestic > 0 else 0,
            'ecological': shortage['ecological'] / self.W_ecological if self.W_ecological > 0 else 0,
            'industrial': shortage['industrial'] / self.W_industrial if self.W_industrial > 0 else 0,
            'agricultural': shortage['agricultural'] / self.W_agricultural if self.W_agricultural > 0 else 0
        }
        
        return {
            'shortage': shortage,
            'shortage_rate': shortage_rate
        }
    
    def comprehensive_benefit(self) -> Dict:
        """综合效益分析"""
        alloc = self.allocation_scheme()
        
        # 单位用水效益（万元/万m³）
        benefit_per_unit = {
            'domestic': 200,  # 生活用水效益高
            'ecological': 50,  # 生态效益难以量化
            'industrial': 150,  # 工业用水效益较高
            'agricultural': 30  # 农业用水效益较低
        }
        
        # 计算各部门效益
        benefits = {
            'domestic': alloc['domestic'] * 10000 * benefit_per_unit['domestic'],
            'ecological': alloc['ecological'] * 10000 * benefit_per_unit['ecological'],
            'industrial': alloc['industrial'] * 10000 * benefit_per_unit['industrial'],
            'agricultural': alloc['agricultural'] * 10000 * benefit_per_unit['agricultural']
        }
        
        total_benefit = sum(benefits.values())
        
        return {
            'benefits': benefits,
            'total_benefit': total_benefit,
            'benefit_per_m3': total_benefit / (self.W_total * 1e8) if self.W_total > 0 else 0
        }
    
    def plot_analysis(self):
        """绘制分析图表"""
        fig = plt.figure(figsize=(16, 12))
        
        balance = self.water_balance()
        alloc = self.allocation_scheme()
        ratio = self.allocation_ratio()
        shortage = self.shortage_assessment()
        benefit = self.comprehensive_benefit()
        
        sectors = ['生活', '生态', '工业', '农业']
        demands = [self.W_domestic, self.W_ecological, 
                  self.W_industrial, self.W_agricultural]
        allocations = [alloc['domestic'], alloc['ecological'],
                      alloc['industrial'], alloc['agricultural']]
        
        # 1. 供需对比
        ax1 = plt.subplot(3, 3, 1)
        
        categories = ['总供水', '总需求']
        values = [self.W_total, balance['W_demand']]
        colors = ['blue', 'red']
        
        bars = ax1.bar(categories, values, color=colors, alpha=0.7, edgecolor='black')
        ax1.axhline(self.W_total, color='b', linestyle='--', linewidth=1, alpha=0.5)
        
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2, height,
                    f'{val:.2f}', ha='center', va='bottom',
                    fontsize=10, fontweight='bold')
        
        if balance['W_deficit'] > 0:
            ax1.text(0.5, max(values)*0.5, f'缺水量\n{balance["W_deficit"]:.2f}亿m³',
                    ha='center', fontsize=10, color='red',
                    bbox=dict(boxstyle='round', facecolor='pink', alpha=0.7))
        else:
            ax1.text(0.5, max(values)*0.5, f'富余量\n{balance["W_surplus"]:.2f}亿m³',
                    ha='center', fontsize=10, color='green',
                    bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))
        
        ax1.set_ylabel('水量 (亿m³)', fontsize=10)
        ax1.set_title('供需总量对比', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3, axis='y')
        
        # 2. 基本参数
        ax2 = plt.subplot(3, 3, 2)
        ax2.axis('off')
        
        ax2.text(0.5, 0.95, '基本参数', fontsize=11, ha='center', fontweight='bold')
        ax2.text(0.1, 0.82, f'总水资源量: {self.W_total} 亿m³', fontsize=10)
        ax2.text(0.1, 0.72, f'总需求量: {balance["W_demand"]:.2f} 亿m³', fontsize=10)
        ax2.text(0.1, 0.62, f'缺水量: {balance["W_deficit"]:.2f} 亿m³', 
                fontsize=10, color='red' if balance['W_deficit']>0 else 'green')
        ax2.text(0.1, 0.52, f'缺水率: {balance["deficit_rate"]:.1%}', fontsize=10)
        
        ax2.text(0.1, 0.38, '各部门需求:', fontsize=10, fontweight='bold')
        ax2.text(0.15, 0.30, f'生活: {self.W_domestic} 亿m³', fontsize=9)
        ax2.text(0.15, 0.23, f'生态: {self.W_ecological} 亿m³', fontsize=9)
        ax2.text(0.15, 0.16, f'工业: {self.W_industrial} 亿m³', fontsize=9)
        ax2.text(0.15, 0.09, f'农业: {self.W_agricultural} 亿m³', fontsize=9)
        
        ax2.set_title('参数汇总', fontsize=12, fontweight='bold')
        
        # 3. 需求与分配对比
        ax3 = plt.subplot(3, 3, 3)
        
        x = np.arange(len(sectors))
        width = 0.35
        
        bars1 = ax3.bar(x - width/2, demands, width, label='需求', 
                       color='red', alpha=0.7, edgecolor='black')
        bars2 = ax3.bar(x + width/2, allocations, width, label='分配',
                       color='blue', alpha=0.7, edgecolor='black')
        
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax3.text(bar.get_x() + bar.get_width()/2, height,
                        f'{height:.2f}', ha='center', va='bottom', fontsize=8)
        
        ax3.set_ylabel('水量 (亿m³)', fontsize=10)
        ax3.set_title('各部门需求与分配对比', fontsize=12, fontweight='bold')
        ax3.set_xticks(x)
        ax3.set_xticklabels(sectors)
        ax3.legend()
        ax3.grid(True, alpha=0.3, axis='y')
        
        # 4. 配置方案饼图
        ax4 = plt.subplot(3, 3, 4)
        
        pie_labels = sectors + ['富余']
        pie_values = allocations + [alloc['remaining']]
        pie_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8']
        
        wedges, texts, autotexts = ax4.pie(pie_values, labels=pie_labels, autopct='%1.1f%%',
                                           colors=pie_colors, startangle=90)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(9)
            autotext.set_fontweight('bold')
        
        ax4.set_title('水资源配置方案', fontsize=12, fontweight='bold')
        
        # 5. 分配比例
        ax5 = plt.subplot(3, 3, 5)
        
        ratio_values = [ratio['domestic'], ratio['ecological'],
                       ratio['industrial'], ratio['agricultural']]
        ratio_percent = [r * 100 for r in ratio_values]
        
        bars = ax5.barh(sectors, ratio_percent, color=pie_colors[:4], 
                       alpha=0.7, edgecolor='black')
        
        for bar, val in zip(bars, ratio_percent):
            width = bar.get_width()
            ax5.text(width, bar.get_y() + bar.get_height()/2,
                    f'{val:.1f}%', ha='left', va='center',
                    fontsize=9, fontweight='bold')
        
        ax5.set_xlabel('比例 (%)', fontsize=10)
        ax5.set_title('各部门分配比例', fontsize=12, fontweight='bold')
        ax5.grid(True, alpha=0.3, axis='x')
        
        # 6. 缺水风险评估
        ax6 = plt.subplot(3, 3, 6)
        
        shortage_values = [shortage['shortage']['domestic'],
                          shortage['shortage']['ecological'],
                          shortage['shortage']['industrial'],
                          shortage['shortage']['agricultural']]
        
        colors_shortage = ['green' if s == 0 else 'red' for s in shortage_values]
        
        bars = ax6.bar(sectors, shortage_values, color=colors_shortage,
                      alpha=0.7, edgecolor='black')
        ax6.axhline(0, color='k', linewidth=1)
        
        for bar, val in zip(bars, shortage_values):
            if val > 0:
                ax6.text(bar.get_x() + bar.get_width()/2, val,
                        f'{val:.2f}', ha='center', va='bottom',
                        fontsize=8, color='red', fontweight='bold')
        
        ax6.set_ylabel('缺水量 (亿m³)', fontsize=10)
        ax6.set_title('各部门缺水量', fontsize=12, fontweight='bold')
        ax6.grid(True, alpha=0.3, axis='y')
        
        # 7. 效益分析
        ax7 = plt.subplot(3, 3, 7)
        
        benefit_values = [benefit['benefits']['domestic']/1e8,
                         benefit['benefits']['ecological']/1e8,
                         benefit['benefits']['industrial']/1e8,
                         benefit['benefits']['agricultural']/1e8]
        
        bars = ax7.bar(sectors, benefit_values, color=pie_colors[:4],
                      alpha=0.7, edgecolor='black')
        
        for bar, val in zip(bars, benefit_values):
            height = bar.get_height()
            ax7.text(bar.get_x() + bar.get_width()/2, height,
                    f'{val:.1f}', ha='center', va='bottom', fontsize=8)
        
        ax7.set_ylabel('效益 (亿元)', fontsize=10)
        ax7.set_title('各部门经济效益', fontsize=12, fontweight='bold')
        ax7.grid(True, alpha=0.3, axis='y')
        
        # 8. 优先级排序
        ax8 = plt.subplot(3, 3, 8)
        ax8.axis('off')
        
        ax8.text(0.5, 0.95, '优先级排序', fontsize=11, ha='center', fontweight='bold')
        
        priorities = [
            ('生活用水', '1', '最高', 'red'),
            ('生态用水', '2', '刚性', 'green'),
            ('工业用水', '3', '次之', 'blue'),
            ('农业用水', '4', '最低', 'orange')
        ]
        
        y_pos = 0.78
        for name, level, desc, color in priorities:
            ax8.text(0.15, y_pos, f'{level}', fontsize=16, fontweight='bold',
                    color=color, ha='center')
            ax8.text(0.25, y_pos, f'{name}', fontsize=10, va='center')
            ax8.text(0.70, y_pos, f'({desc})', fontsize=9, va='center',
                    color=color, style='italic')
            y_pos -= 0.17
        
        ax8.text(0.5, 0.10, '配置原则：优先保障生活和生态用水\n工业和农业根据剩余水量分配',
                fontsize=9, ha='center', style='italic',
                bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.7))
        
        ax8.set_title('配置策略', fontsize=12, fontweight='bold')
        
        # 9. 结果汇总表
        ax9 = plt.subplot(3, 3, 9)
        ax9.axis('off')
        
        table_data = [
            ['部门', '需求\n(亿m³)', '分配\n(亿m³)', '比例', '缺水\n(亿m³)'],
            ['生活', f'{self.W_domestic:.2f}', f'{alloc["domestic"]:.2f}', 
             f'{ratio["domestic"]:.1%}', f'{shortage["shortage"]["domestic"]:.2f}'],
            ['生态', f'{self.W_ecological:.2f}', f'{alloc["ecological"]:.2f}',
             f'{ratio["ecological"]:.1%}', f'{shortage["shortage"]["ecological"]:.2f}'],
            ['工业', f'{self.W_industrial:.2f}', f'{alloc["industrial"]:.2f}',
             f'{ratio["industrial"]:.1%}', f'{shortage["shortage"]["industrial"]:.2f}'],
            ['农业', f'{self.W_agricultural:.2f}', f'{alloc["agricultural"]:.2f}',
             f'{ratio["agricultural"]:.1%}', f'{shortage["shortage"]["agricultural"]:.2f}'],
            ['合计', f'{balance["W_demand"]:.2f}', f'{self.W_total:.2f}',
             '100%', f'{balance["W_deficit"]:.2f}']
        ]
        
        table = ax9.table(cellText=table_data, cellLoc='center', loc='center',
                         colWidths=[0.20, 0.20, 0.20, 0.15, 0.20])
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1, 2.0)
        
        for i in range(5):
            table[(0, i)].set_facecolor('#4472C4')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        # 高亮合计行
        for j in range(5):
            table[(5, j)].set_facecolor('#FFF9E6')
            table[(5, j)].set_text_props(weight='bold')
        
        ax9.set_title('配置结果汇总', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('/tmp/ch13_problem07_water_allocation.png', dpi=150, bbox_inches='tight')
        print(f"图表已保存: /tmp/ch13_problem07_water_allocation.png")
        plt.show()
    
    def print_results(self):
        """打印结果"""
        print("\n" + "="*70)
        print("第13章 水资源计算 - 题7：水资源配置")
        print("="*70)
        
        balance = self.water_balance()
        alloc = self.allocation_scheme()
        ratio = self.allocation_ratio()
        shortage = self.shortage_assessment()
        benefit = self.comprehensive_benefit()
        
        print(f"\n【供需分析】")
        print(f"总水资源量: W_总 = {self.W_total} 亿m³")
        print(f"总需求量: W_需 = {balance['W_demand']:.3f} 亿m³")
        print(f"  - 生活用水: {self.W_domestic} 亿m³")
        print(f"  - 生态用水: {self.W_ecological} 亿m³")
        print(f"  - 工业用水: {self.W_industrial} 亿m³")
        print(f"  - 农业用水: {self.W_agricultural} 亿m³")
        
        if balance['W_deficit'] > 0:
            print(f"缺水量: ΔW = {balance['W_deficit']:.3f} 亿m³ ✗")
            print(f"缺水率: η = {balance['deficit_rate']:.2%}")
        else:
            print(f"富余量: ΔW = {balance['W_surplus']:.3f} 亿m³ ✓")
        
        print(f"\n【配置方案】（按优先级）")
        print(f"1. 生活用水: {alloc['domestic']:.3f} 亿m³ ({ratio['domestic']:.1%})")
        if alloc['domestic'] < self.W_domestic:
            print(f"   ✗ 缺水 {shortage['shortage']['domestic']:.3f} 亿m³")
        else:
            print(f"   ✓ 满足需求")
        
        print(f"2. 生态用水: {alloc['ecological']:.3f} 亿m³ ({ratio['ecological']:.1%})")
        if alloc['ecological'] < self.W_ecological:
            print(f"   ✗ 缺水 {shortage['shortage']['ecological']:.3f} 亿m³")
        else:
            print(f"   ✓ 满足需求")
        
        print(f"3. 工业用水: {alloc['industrial']:.3f} 亿m³ ({ratio['industrial']:.1%})")
        if alloc['industrial'] < self.W_industrial:
            print(f"   ✗ 缺水 {shortage['shortage']['industrial']:.3f} 亿m³")
        else:
            print(f"   ✓ 满足需求")
        
        print(f"4. 农业用水: {alloc['agricultural']:.3f} 亿m³ ({ratio['agricultural']:.1%})")
        if alloc['agricultural'] < self.W_agricultural:
            print(f"   ✗ 缺水 {shortage['shortage']['agricultural']:.3f} 亿m³")
        else:
            print(f"   ✓ 满足需求")
        
        print(f"剩余水量: {alloc['remaining']:.3f} 亿m³")
        
        print(f"\n【综合效益】")
        print(f"生活用水效益: {benefit['benefits']['domestic']/1e8:.2f} 亿元")
        print(f"生态用水效益: {benefit['benefits']['ecological']/1e8:.2f} 亿元")
        print(f"工业用水效益: {benefit['benefits']['industrial']/1e8:.2f} 亿元")
        print(f"农业用水效益: {benefit['benefits']['agricultural']/1e8:.2f} 亿元")
        print(f"总效益: {benefit['total_benefit']/1e8:.2f} 亿元")
        print(f"单位水量效益: {benefit['benefit_per_m3']:.2f} 元/m³")
        
        print(f"\n✓ 水资源配置完成")
        print(f"\n{'='*70}\n")


def main():
    W_total = 10.0  # 亿m³
    W_domestic = 0.8
    W_industrial = 3.5
    W_agricultural = 6.0
    W_ecological = 0.5
    
    allocation = WaterAllocation(W_total, W_domestic, W_industrial, 
                                 W_agricultural, W_ecological)
    allocation.print_results()
    allocation.plot_analysis()


if __name__ == "__main__":
    main()
