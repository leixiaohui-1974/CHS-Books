# -*- coding: utf-8 -*-
"""
第13章 水资源计算 - 题10：水资源承载力评价

问题描述：
    某区域多年平均水资源量W = 15亿m³/年
    现状人口P = 200万人，人均用水量q_p = 150 L/(人·d)
    现状GDP = 500亿元，万元GDP用水量q_GDP = 80 m³/万元
    生态用水比例占15%
    
    求：
    1. 现状用水量计算
    2. 水资源承载人口
    3. 水资源承载经济规模
    4. 承载力综合评价
    5. 可持续发展建议

核心公式：
    1. 承载人口：P_max = (W_可用 - W_生态 - W_生产)/(q_p × 365)
    2. 承载GDP：GDP_max = (W_可用 - W_生态 - W_生活)/q_GDP
    3. 承载指数：CI = W_用/W_可用

考试要点：
    - 水资源承载力
    - 可持续利用
    - 人口承载力
    - 经济承载力

作者: CHS-Books Team
日期: 2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, Dict, List

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class WaterCarryingCapacity:
    """水资源承载力评价"""
    
    def __init__(self, W_total: float, P_current: float, q_p: float,
                 GDP_current: float, q_GDP: float, eco_ratio: float = 0.15):
        self.W_total = W_total  # 水资源量 亿m³/年
        self.P_current = P_current  # 现状人口 万人
        self.q_p = q_p  # 人均用水量 L/(人·d)
        self.GDP_current = GDP_current  # 现状GDP 亿元
        self.q_GDP = q_GDP  # 万元GDP用水量 m³/万元
        self.eco_ratio = eco_ratio  # 生态用水比例
        
    def current_water_use(self) -> Dict:
        """现状用水量"""
        # 生活用水
        W_domestic = self.P_current * 1e4 * self.q_p * 365 / 1e12  # 亿m³
        
        # 生产用水（工业+农业）
        W_production = self.GDP_current * 1e4 * self.q_GDP / 1e8  # 亿m³
        
        # 生态用水
        W_ecological = self.W_total * self.eco_ratio
        
        # 总用水量
        W_total_use = W_domestic + W_production + W_ecological
        
        return {
            'W_domestic': W_domestic,
            'W_production': W_production,
            'W_ecological': W_ecological,
            'W_total_use': W_total_use
        }
    
    def population_capacity(self) -> Tuple[float, float]:
        """人口承载力"""
        current_use = self.current_water_use()
        
        # 可用于人口的水量
        W_available_pop = (self.W_total * (1 - self.eco_ratio) - 
                          current_use['W_production'])
        
        # 承载人口（万人）
        P_max = W_available_pop * 1e12 / (self.q_p * 365 * 1e4)
        
        # 人口承载率
        pop_carrying_rate = self.P_current / P_max if P_max > 0 else 1.0
        
        return P_max, pop_carrying_rate
    
    def economic_capacity(self) -> Tuple[float, float]:
        """经济承载力"""
        current_use = self.current_water_use()
        
        # 可用于经济的水量
        W_available_econ = (self.W_total * (1 - self.eco_ratio) - 
                           current_use['W_domestic'])
        
        # 承载GDP（亿元）
        GDP_max = W_available_econ * 1e8 / (self.q_GDP * 1e4)
        
        # 经济承载率
        econ_carrying_rate = self.GDP_current / GDP_max if GDP_max > 0 else 1.0
        
        return GDP_max, econ_carrying_rate
    
    def carrying_index(self) -> Tuple[float, str]:
        """承载指数"""
        current_use = self.current_water_use()
        
        CI = current_use['W_total_use'] / self.W_total
        
        if CI < 0.4:
            status = "未开发"
            color = "green"
        elif CI < 0.6:
            status = "可开发"
            color = "blue"
        elif CI < 0.8:
            status = "重度开发"
            color = "orange"
        else:
            status = "超载"
            color = "red"
        
        return CI, status
    
    def comprehensive_evaluation(self) -> Dict:
        """综合评价"""
        P_max, pop_rate = self.population_capacity()
        GDP_max, econ_rate = self.economic_capacity()
        CI, status = self.carrying_index()
        
        # 综合承载指数
        comprehensive_index = (pop_rate + econ_rate) / 2
        
        # 评价等级
        if comprehensive_index < 0.5:
            grade = "优"
            suggestion = "水资源充足，可适度开发"
        elif comprehensive_index < 0.7:
            grade = "良"
            suggestion = "水资源较充足，注意节水"
        elif comprehensive_index < 0.9:
            grade = "中"
            suggestion = "水资源紧张，需加强节水"
        else:
            grade = "差"
            suggestion = "水资源超载，需调整产业结构"
        
        return {
            'comprehensive_index': comprehensive_index,
            'grade': grade,
            'suggestion': suggestion,
            'P_max': P_max,
            'GDP_max': GDP_max,
            'pop_rate': pop_rate,
            'econ_rate': econ_rate
        }
    
    def plot_analysis(self):
        """绘制分析图表"""
        fig = plt.figure(figsize=(16, 12))
        
        current_use = self.current_water_use()
        P_max, pop_rate = self.population_capacity()
        GDP_max, econ_rate = self.economic_capacity()
        CI, status = self.carrying_index()
        comp_eval = self.comprehensive_evaluation()
        
        # 1. 现状用水结构
        ax1 = plt.subplot(3, 3, 1)
        
        use_types = ['生活', '生产', '生态']
        use_values = [current_use['W_domestic'], current_use['W_production'],
                     current_use['W_ecological']]
        colors_use = ['#FF6B6B', '#4ECDC4', '#95E1D3']
        
        wedges, texts, autotexts = ax1.pie(use_values, labels=use_types, autopct='%1.1f%%',
                                           colors=colors_use, startangle=90)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(10)
            autotext.set_fontweight('bold')
        
        ax1.set_title(f'现状用水结构\n(总用水{current_use["W_total_use"]:.2f}亿m³)',
                     fontsize=12, fontweight='bold')
        
        # 2. 基本参数
        ax2 = plt.subplot(3, 3, 2)
        ax2.axis('off')
        
        ax2.text(0.5, 0.95, '基本参数', fontsize=11, ha='center', fontweight='bold')
        ax2.text(0.1, 0.80, f'水资源量: {self.W_total} 亿m³/年', fontsize=10)
        ax2.text(0.1, 0.70, f'现状人口: {self.P_current} 万人', fontsize=10)
        ax2.text(0.1, 0.60, f'人均用水: {self.q_p} L/(人·d)', fontsize=10)
        ax2.text(0.1, 0.50, f'现状GDP: {self.GDP_current} 亿元', fontsize=10)
        ax2.text(0.1, 0.40, f'万元GDP用水: {self.q_GDP} m³/万元', fontsize=10)
        ax2.text(0.1, 0.30, f'生态用水比: {self.eco_ratio:.0%}', fontsize=10)
        
        ax2.text(0.1, 0.15, '现状用水:', fontsize=10, fontweight='bold')
        ax2.text(0.15, 0.07, f'总用水: {current_use["W_total_use"]:.2f} 亿m³', fontsize=9)
        ax2.text(0.15, 0.00, f'利用率: {CI:.1%}', fontsize=9,
                color='green' if CI < 0.6 else 'red')
        
        ax2.set_title('参数汇总', fontsize=12, fontweight='bold')
        
        # 3. 供需平衡
        ax3 = plt.subplot(3, 3, 3)
        
        categories = ['水资源总量', '现状用水量']
        values = [self.W_total, current_use['W_total_use']]
        colors = ['blue', 'red']
        
        bars = ax3.bar(categories, values, color=colors, alpha=0.7, edgecolor='black')
        ax3.axhline(self.W_total * 0.8, color='orange', linestyle='--',
                   linewidth=2, label='警戒线(80%)')
        
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2, height,
                    f'{val:.2f}', ha='center', va='bottom',
                    fontsize=10, fontweight='bold')
        
        # 显示余量
        remaining = self.W_total - current_use['W_total_use']
        ax3.text(0.5, max(values)*0.5, f'剩余量\n{remaining:.2f}亿m³',
                ha='center', fontsize=10,
                bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))
        
        ax3.set_ylabel('水量 (亿m³)', fontsize=10)
        ax3.set_title('供需平衡分析', fontsize=12, fontweight='bold')
        ax3.legend()
        ax3.grid(True, alpha=0.3, axis='y')
        
        # 4. 人口承载力
        ax4 = plt.subplot(3, 3, 4)
        
        pop_categories = ['现状人口', '承载人口']
        pop_values = [self.P_current, P_max]
        colors_pop = ['orange' if pop_rate > 0.8 else 'green', 'blue']
        
        bars = ax4.bar(pop_categories, pop_values, color=colors_pop,
                      alpha=0.7, edgecolor='black')
        
        for bar, val in zip(bars, pop_values):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2, height,
                    f'{val:.1f}', ha='center', va='bottom',
                    fontsize=10, fontweight='bold')
        
        # 承载率
        ax4.text(0.5, max(pop_values)*0.5, f'人口承载率\n{pop_rate:.1%}',
                ha='center', fontsize=10, fontweight='bold',
                bbox=dict(boxstyle='round', 
                         facecolor='pink' if pop_rate > 0.8 else 'lightgreen',
                         alpha=0.7))
        
        ax4.set_ylabel('人口 (万人)', fontsize=10)
        ax4.set_title('人口承载力分析', fontsize=12, fontweight='bold')
        ax4.grid(True, alpha=0.3, axis='y')
        
        # 5. 经济承载力
        ax5 = plt.subplot(3, 3, 5)
        
        gdp_categories = ['现状GDP', '承载GDP']
        gdp_values = [self.GDP_current, GDP_max]
        colors_gdp = ['orange' if econ_rate > 0.8 else 'green', 'blue']
        
        bars = ax5.bar(gdp_categories, gdp_values, color=colors_gdp,
                      alpha=0.7, edgecolor='black')
        
        for bar, val in zip(bars, gdp_values):
            height = bar.get_height()
            ax5.text(bar.get_x() + bar.get_width()/2, height,
                    f'{val:.1f}', ha='center', va='bottom',
                    fontsize=10, fontweight='bold')
        
        # 承载率
        ax5.text(0.5, max(gdp_values)*0.5, f'经济承载率\n{econ_rate:.1%}',
                ha='center', fontsize=10, fontweight='bold',
                bbox=dict(boxstyle='round',
                         facecolor='pink' if econ_rate > 0.8 else 'lightgreen',
                         alpha=0.7))
        
        ax5.set_ylabel('GDP (亿元)', fontsize=10)
        ax5.set_title('经济承载力分析', fontsize=12, fontweight='bold')
        ax5.grid(True, alpha=0.3, axis='y')
        
        # 6. 承载指数雷达图
        ax6 = plt.subplot(3, 3, 6, projection='polar')
        
        categories_radar = ['水资源\n开发率', '人口\n承载率', '经济\n承载率', '综合\n承载指数']
        values_radar = [CI, pop_rate, econ_rate, comp_eval['comprehensive_index']]
        
        angles = np.linspace(0, 2*np.pi, len(categories_radar), endpoint=False).tolist()
        values_radar += values_radar[:1]
        angles += angles[:1]
        
        ax6.plot(angles, values_radar, 'o-', linewidth=2, color='blue')
        ax6.fill(angles, values_radar, alpha=0.25, color='blue')
        ax6.set_ylim(0, 1.2)
        ax6.set_xticks(angles[:-1])
        ax6.set_xticklabels(categories_radar, fontsize=9)
        ax6.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
        ax6.set_yticklabels(['20%', '40%', '60%', '80%', '100%'])
        ax6.grid(True)
        
        # 警戒线
        warning_line = [0.8] * len(angles)
        ax6.plot(angles, warning_line, 'r--', linewidth=1.5, label='警戒线')
        ax6.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
        
        ax6.set_title('承载力指数评价', fontsize=12, fontweight='bold', pad=20)
        
        # 7. 不同用水定额下的人口承载力
        ax7 = plt.subplot(3, 3, 7)
        
        q_p_range = np.linspace(100, 250, 50)
        P_max_range = []
        
        for q in q_p_range:
            capacity_temp = WaterCarryingCapacity(self.W_total, self.P_current, q,
                                                 self.GDP_current, self.q_GDP, self.eco_ratio)
            P_temp, _ = capacity_temp.population_capacity()
            P_max_range.append(P_temp)
        
        ax7.plot(q_p_range, P_max_range, 'b-', linewidth=2)
        ax7.plot(self.q_p, P_max, 'ro', markersize=12, label=f'现状q_p={self.q_p}L/(人·d)')
        ax7.axhline(P_max, color='r', linestyle='--', linewidth=1, alpha=0.5)
        ax7.axhline(self.P_current, color='orange', linestyle='--', linewidth=1,
                   alpha=0.5, label=f'现状人口{self.P_current}万人')
        
        ax7.set_xlabel('人均用水量 q_p [L/(人·d)]', fontsize=10)
        ax7.set_ylabel('承载人口 P_max (万人)', fontsize=10)
        ax7.set_title('人均用水定额-承载人口关系', fontsize=12, fontweight='bold')
        ax7.legend()
        ax7.grid(True, alpha=0.3)
        
        # 8. 综合评价
        ax8 = plt.subplot(3, 3, 8)
        ax8.axis('off')
        
        ax8.text(0.5, 0.95, '综合评价', fontsize=11, ha='center', fontweight='bold')
        
        ax8.text(0.1, 0.78, f'承载指数: {comp_eval["comprehensive_index"]:.2%}', fontsize=10)
        
        grade_color = {'优': 'green', '良': 'blue', '中': 'orange', '差': 'red'}
        ax8.text(0.1, 0.65, f'评价等级: {comp_eval["grade"]}', fontsize=12,
                color=grade_color[comp_eval['grade']], fontweight='bold')
        
        ax8.text(0.1, 0.52, '承载状况:', fontsize=10, fontweight='bold')
        ax8.text(0.15, 0.44, f'开发程度: {status} (CI={CI:.1%})', fontsize=9)
        ax8.text(0.15, 0.37, f'人口承载率: {pop_rate:.1%}', fontsize=9)
        ax8.text(0.15, 0.30, f'经济承载率: {econ_rate:.1%}', fontsize=9)
        
        ax8.text(0.1, 0.18, '发展建议:', fontsize=10, fontweight='bold')
        suggestion_lines = comp_eval['suggestion'].split('，')
        y_pos = 0.10
        for line in suggestion_lines:
            ax8.text(0.15, y_pos, f'• {line}', fontsize=9, wrap=True)
            y_pos -= 0.08
        
        ax8.set_title('评价结论', fontsize=12, fontweight='bold')
        
        # 9. 结果汇总表
        ax9 = plt.subplot(3, 3, 9)
        ax9.axis('off')
        
        table_data = [
            ['指标', '数值', '单位'],
            ['水资源总量', f'{self.W_total}', '亿m³'],
            ['现状用水量', f'{current_use["W_total_use"]:.2f}', '亿m³'],
            ['剩余水量', f'{self.W_total - current_use["W_total_use"]:.2f}', '亿m³'],
            ['承载指数CI', f'{CI:.1%}', '-'],
            ['现状人口', f'{self.P_current}', '万人'],
            ['承载人口', f'{P_max:.1f}', '万人'],
            ['现状GDP', f'{self.GDP_current}', '亿元'],
            ['承载GDP', f'{GDP_max:.1f}', '亿元'],
            ['评价等级', comp_eval['grade'], '-']
        ]
        
        table = ax9.table(cellText=table_data, cellLoc='center', loc='center',
                         colWidths=[0.40, 0.30, 0.25])
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2.0)
        
        for i in range(3):
            table[(0, i)].set_facecolor('#4472C4')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        # 高亮评价等级
        for j in range(3):
            table[(9, j)].set_facecolor('#FFF9E6')
            table[(9, j)].set_text_props(weight='bold')
        
        ax9.set_title('计算结果汇总', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('/tmp/ch13_problem10_carrying_capacity.png', dpi=150, bbox_inches='tight')
        print(f"图表已保存: /tmp/ch13_problem10_carrying_capacity.png")
        plt.show()
    
    def print_results(self):
        """打印结果"""
        print("\n" + "="*70)
        print("第13章 水资源计算 - 题10：水资源承载力评价")
        print("="*70)
        
        current_use = self.current_water_use()
        P_max, pop_rate = self.population_capacity()
        GDP_max, econ_rate = self.economic_capacity()
        CI, status = self.carrying_index()
        comp_eval = self.comprehensive_evaluation()
        
        print(f"\n【现状用水分析】")
        print(f"生活用水: W_生活 = {current_use['W_domestic']:.3f} 亿m³")
        print(f"生产用水: W_生产 = {current_use['W_production']:.3f} 亿m³")
        print(f"生态用水: W_生态 = {current_use['W_ecological']:.3f} 亿m³")
        print(f"总用水量: W_总 = {current_use['W_total_use']:.3f} 亿m³")
        print(f"水资源开发利用率: CI = {CI:.2%} ({status})")
        
        print(f"\n【人口承载力】")
        print(f"现状人口: P = {self.P_current} 万人")
        print(f"人均用水量: q_p = {self.q_p} L/(人·d)")
        print(f"承载人口: P_max = {P_max:.2f} 万人")
        print(f"人口承载率: {pop_rate:.2%}")
        if pop_rate > 1.0:
            print(f"✗ 人口超载")
        elif pop_rate > 0.8:
            print(f"△ 人口接近承载上限")
        else:
            print(f"✓ 人口在承载范围内")
        
        print(f"\n【经济承载力】")
        print(f"现状GDP: {self.GDP_current} 亿元")
        print(f"万元GDP用水量: {self.q_GDP} m³/万元")
        print(f"承载GDP: GDP_max = {GDP_max:.2f} 亿元")
        print(f"经济承载率: {econ_rate:.2%}")
        if econ_rate > 1.0:
            print(f"✗ 经济规模超载")
        elif econ_rate > 0.8:
            print(f"△ 经济规模接近承载上限")
        else:
            print(f"✓ 经济规模在承载范围内")
        
        print(f"\n【综合评价】")
        print(f"综合承载指数: {comp_eval['comprehensive_index']:.2%}")
        print(f"评价等级: {comp_eval['grade']}")
        print(f"发展建议: {comp_eval['suggestion']}")
        
        print(f"\n✓ 水资源承载力评价完成")
        print(f"\n{'='*70}\n")


def main():
    W_total = 15.0  # 亿m³/年
    P_current = 200  # 万人
    q_p = 150  # L/(人·d)
    GDP_current = 500  # 亿元
    q_GDP = 80  # m³/万元
    
    capacity = WaterCarryingCapacity(W_total, P_current, q_p, GDP_current, q_GDP)
    capacity.print_results()
    capacity.plot_analysis()


if __name__ == "__main__":
    main()
