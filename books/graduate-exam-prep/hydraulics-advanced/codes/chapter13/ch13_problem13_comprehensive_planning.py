# -*- coding: utf-8 -*-
"""
第13章 水资源计算 - 题13：水资源综合规划

问题描述：
    某流域规划区面积A = 5000 km²
    多年平均降水量P = 800 mm，径流系数α = 0.40
    现状人口200万人，规划人口300万人
    现状GDP 600亿元，规划GDP 1200亿元
    规划期20年
    
    求：
    1. 水资源总量评价
    2. 供需平衡分析
    3. 调控方案设计
    4. 工程措施建议
    5. 综合效益评估

核心公式：
    1. 水资源总量：W = P × A × α
    2. 需水预测：W_需 = W_生活 + W_生产 + W_生态
    3. 供需平衡：W_供 = W_地表 + W_地下 + W_外调
    4. 效益指标：B/C比率

考试要点：
    - 水资源规划
    - 供需平衡
    - 工程措施
    - 综合效益

作者: CHS-Books Team
日期: 2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, Dict, List

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class ComprehensivePlanning:
    """水资源综合规划"""
    
    def __init__(self, A: float, P: float, alpha: float,
                 P_current: float, P_plan: float,
                 GDP_current: float, GDP_plan: float, years: int = 20):
        self.A = A  # 流域面积 km²
        self.P = P  # 年降水量 mm
        self.alpha = alpha  # 径流系数
        self.P_current = P_current  # 现状人口 万人
        self.P_plan = P_plan  # 规划人口 万人
        self.GDP_current = GDP_current  # 现状GDP 亿元
        self.GDP_plan = GDP_plan  # 规划GDP 亿元
        self.years = years  # 规划年限 年
        
    def water_resources_evaluation(self) -> Dict:
        """水资源总量评价"""
        # 多年平均径流量（亿m³）
        W_total = self.A * self.P * self.alpha / 1000  # km²·mm → 亿m³
        
        # 可开发利用量（取60%）
        W_available = W_total * 0.60
        
        # 生态用水（取15%）
        W_ecological = W_total * 0.15
        
        # 可供水量
        W_supply = W_available - W_ecological
        
        return {
            'W_total': W_total,
            'W_available': W_available,
            'W_ecological': W_ecological,
            'W_supply': W_supply
        }
    
    def water_demand_forecast(self) -> Dict:
        """需水预测"""
        # 现状需水
        q_p_current = 150  # L/(人·d)
        W_domestic_current = self.P_current * 1e4 * q_p_current * 365 / 1e12
        
        q_GDP_current = 100  # m³/万元
        W_production_current = self.GDP_current * 1e4 * q_GDP_current / 1e8
        
        W_demand_current = W_domestic_current + W_production_current
        
        # 规划需水（考虑节水）
        q_p_plan = 130  # L/(人·d) - 节水20L
        W_domestic_plan = self.P_plan * 1e4 * q_p_plan * 365 / 1e12
        
        q_GDP_plan = 60  # m³/万元 - 节水40%
        W_production_plan = self.GDP_plan * 1e4 * q_GDP_plan / 1e8
        
        W_demand_plan = W_domestic_plan + W_production_plan
        
        return {
            'current': {
                'W_domestic': W_domestic_current,
                'W_production': W_production_current,
                'W_total': W_demand_current
            },
            'plan': {
                'W_domestic': W_domestic_plan,
                'W_production': W_production_plan,
                'W_total': W_demand_plan
            }
        }
    
    def supply_demand_balance(self) -> Dict:
        """供需平衡分析"""
        resources = self.water_resources_evaluation()
        demand = self.water_demand_forecast()
        
        # 现状平衡
        deficit_current = max(0, demand['current']['W_total'] - resources['W_supply'])
        surplus_current = max(0, resources['W_supply'] - demand['current']['W_total'])
        
        # 规划平衡
        deficit_plan = max(0, demand['plan']['W_total'] - resources['W_supply'])
        surplus_plan = max(0, resources['W_supply'] - demand['plan']['W_total'])
        
        return {
            'current': {
                'deficit': deficit_current,
                'surplus': surplus_current,
                'balance': resources['W_supply'] - demand['current']['W_total']
            },
            'plan': {
                'deficit': deficit_plan,
                'surplus': surplus_plan,
                'balance': resources['W_supply'] - demand['plan']['W_total']
            }
        }
    
    def regulation_scheme(self) -> Dict:
        """调控方案设计"""
        balance = self.supply_demand_balance()
        
        schemes = []
        
        # 方案1：节水工程
        water_saving = {
            'name': '节水工程',
            'capacity': 0.5,  # 亿m³
            'investment': 2.0,  # 亿元
            'description': '农业节水灌溉、工业节水改造、城市管网改造'
        }
        schemes.append(water_saving)
        
        # 方案2：水库工程
        if balance['plan']['deficit'] > 0:
            reservoir = {
                'name': '水库调蓄',
                'capacity': min(1.0, balance['plan']['deficit'] * 0.6),  # 亿m³
                'investment': 5.0,  # 亿元
                'description': '新建中型水库，调节径流'
            }
            schemes.append(reservoir)
        
        # 方案3：外调水工程
        if balance['plan']['deficit'] > 1.0:
            diversion = {
                'name': '外调水',
                'capacity': balance['plan']['deficit'] * 0.4,  # 亿m³
                'investment': 10.0,  # 亿元
                'description': '跨流域调水工程'
            }
            schemes.append(diversion)
        
        # 总调控能力
        total_capacity = sum(s['capacity'] for s in schemes)
        total_investment = sum(s['investment'] for s in schemes)
        
        return {
            'schemes': schemes,
            'total_capacity': total_capacity,
            'total_investment': total_investment
        }
    
    def engineering_measures(self) -> List[Dict]:
        """工程措施建议"""
        measures = [
            {
                'type': '水源工程',
                'items': ['新建中型水库1座', '扩建现有水库2座', '地下水开采井20眼'],
                'investment': 8.0,
                'supply_capacity': 1.2
            },
            {
                'type': '输配水工程',
                'items': ['输水管道100km', '配水管网200km', '泵站5座'],
                'investment': 5.0,
                'supply_capacity': 0.8
            },
            {
                'type': '节水工程',
                'items': ['节水灌溉5万亩', '工业节水改造50家', '城市管网改造'],
                'investment': 3.0,
                'saving_capacity': 0.5
            },
            {
                'type': '水质保护',
                'items': ['污水处理厂3座', '河道整治50km', '水源地保护'],
                'investment': 4.0,
                'quality_improvement': '达到III类'
            }
        ]
        
        return measures
    
    def comprehensive_benefit(self) -> Dict:
        """综合效益评估"""
        regulation = self.regulation_scheme()
        measures = self.engineering_measures()
        
        # 总投资
        total_investment = regulation['total_investment']
        total_investment += sum(m['investment'] for m in measures)
        
        # 经济效益（年均）
        # 保障GDP增长的经济效益
        GDP_increase = self.GDP_plan - self.GDP_current
        economic_benefit_annual = GDP_increase * 0.02  # 2%归功于水资源保障
        
        # 生态效益（年均）
        ecological_benefit = 0.5  # 亿元/年
        
        # 社会效益（年均）
        social_benefit = 0.3  # 亿元/年
        
        # 总效益（20年）
        total_benefit = (economic_benefit_annual + ecological_benefit + 
                        social_benefit) * self.years
        
        # 效益成本比
        BC_ratio = total_benefit / total_investment if total_investment > 0 else 0
        
        # 投资回收期
        payback_period = total_investment / (economic_benefit_annual + ecological_benefit + 
                                            social_benefit) if (economic_benefit_annual + 
                                            ecological_benefit + social_benefit) > 0 else 0
        
        return {
            'total_investment': total_investment,
            'economic_benefit': economic_benefit_annual * self.years,
            'ecological_benefit': ecological_benefit * self.years,
            'social_benefit': social_benefit * self.years,
            'total_benefit': total_benefit,
            'BC_ratio': BC_ratio,
            'payback_period': payback_period
        }
    
    def plot_analysis(self):
        """绘制分析图表"""
        fig = plt.figure(figsize=(16, 12))
        
        resources = self.water_resources_evaluation()
        demand = self.water_demand_forecast()
        balance = self.supply_demand_balance()
        regulation = self.regulation_scheme()
        measures = self.engineering_measures()
        benefit = self.comprehensive_benefit()
        
        # 1. 水资源评价
        ax1 = plt.subplot(3, 3, 1)
        
        resource_types = ['总量', '可开发', '生态', '可供']
        resource_values = [resources['W_total'], resources['W_available'],
                          resources['W_ecological'], resources['W_supply']]
        colors_res = ['blue', 'cyan', 'green', 'orange']
        
        bars = ax1.bar(resource_types, resource_values, color=colors_res,
                      alpha=0.7, edgecolor='black')
        
        for bar, val in zip(bars, resource_values):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2, height,
                    f'{val:.2f}', ha='center', va='bottom',
                    fontsize=9, fontweight='bold')
        
        ax1.set_ylabel('水量 (亿m³)', fontsize=10)
        ax1.set_title(f'水资源评价 (面积{self.A}km², 降水{self.P}mm)',
                     fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3, axis='y')
        
        # 2. 基本参数
        ax2 = plt.subplot(3, 3, 2)
        ax2.axis('off')
        
        ax2.text(0.5, 0.95, '规划参数', fontsize=11, ha='center', fontweight='bold')
        ax2.text(0.1, 0.80, f'流域面积: {self.A} km²', fontsize=10)
        ax2.text(0.1, 0.72, f'年降水量: {self.P} mm', fontsize=10)
        ax2.text(0.1, 0.64, f'径流系数: {self.alpha}', fontsize=10)
        ax2.text(0.1, 0.56, f'规划年限: {self.years} 年', fontsize=10)
        
        ax2.text(0.1, 0.42, '人口发展:', fontsize=10, fontweight='bold')
        ax2.text(0.15, 0.35, f'现状: {self.P_current}万人', fontsize=9)
        ax2.text(0.15, 0.28, f'规划: {self.P_plan}万人', fontsize=9)
        ax2.text(0.15, 0.21, f'增长: {self.P_plan - self.P_current}万人', fontsize=9)
        
        ax2.text(0.1, 0.10, '经济发展:', fontsize=10, fontweight='bold')
        ax2.text(0.15, 0.03, f'现状: {self.GDP_current}亿元', fontsize=9)
        ax2.text(0.15, -0.04, f'规划: {self.GDP_plan}亿元', fontsize=9)
        
        ax2.set_title('参数汇总', fontsize=12, fontweight='bold')
        
        # 3. 供需对比（现状vs规划）
        ax3 = plt.subplot(3, 3, 3)
        
        periods = ['现状', '规划']
        supply_values = [resources['W_supply'], resources['W_supply']]
        demand_values = [demand['current']['W_total'], demand['plan']['W_total']]
        
        x = np.arange(len(periods))
        width = 0.35
        
        bars1 = ax3.bar(x - width/2, supply_values, width, label='可供水量',
                       color='blue', alpha=0.7, edgecolor='black')
        bars2 = ax3.bar(x + width/2, demand_values, width, label='需水量',
                       color='red', alpha=0.7, edgecolor='black')
        
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax3.text(bar.get_x() + bar.get_width()/2, height,
                        f'{height:.2f}', ha='center', va='bottom', fontsize=9)
        
        ax3.set_ylabel('水量 (亿m³)', fontsize=10)
        ax3.set_title('供需对比分析', fontsize=12, fontweight='bold')
        ax3.set_xticks(x)
        ax3.set_xticklabels(periods)
        ax3.legend()
        ax3.grid(True, alpha=0.3, axis='y')
        
        # 4. 需水预测
        ax4 = plt.subplot(3, 3, 4)
        
        need_types = ['生活', '生产']
        need_current = [demand['current']['W_domestic'], demand['current']['W_production']]
        need_plan = [demand['plan']['W_domestic'], demand['plan']['W_production']]
        
        x = np.arange(len(need_types))
        width = 0.35
        
        bars1 = ax4.bar(x - width/2, need_current, width, label='现状',
                       color='orange', alpha=0.7, edgecolor='black')
        bars2 = ax4.bar(x + width/2, need_plan, width, label='规划',
                       color='purple', alpha=0.7, edgecolor='black')
        
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax4.text(bar.get_x() + bar.get_width()/2, height,
                        f'{height:.2f}', ha='center', va='bottom', fontsize=8)
        
        ax4.set_ylabel('需水量 (亿m³)', fontsize=10)
        ax4.set_title('各类需水预测', fontsize=12, fontweight='bold')
        ax4.set_xticks(x)
        ax4.set_xticklabels(need_types)
        ax4.legend()
        ax4.grid(True, alpha=0.3, axis='y')
        
        # 5. 调控方案
        ax5 = plt.subplot(3, 3, 5)
        
        if regulation['schemes']:
            scheme_names = [s['name'] for s in regulation['schemes']]
            scheme_capacities = [s['capacity'] for s in regulation['schemes']]
            
            bars = ax5.barh(scheme_names, scheme_capacities, 
                           color=['#FF6B6B', '#4ECDC4', '#45B7D1'][:len(scheme_names)],
                           alpha=0.7, edgecolor='black')
            
            for bar, val in zip(bars, scheme_capacities):
                width = bar.get_width()
                ax5.text(width, bar.get_y() + bar.get_height()/2,
                        f'{val:.2f}', ha='left', va='center',
                        fontsize=9, fontweight='bold')
            
            ax5.set_xlabel('调控能力 (亿m³)', fontsize=10)
            ax5.set_title(f'调控方案 (总投资{regulation["total_investment"]:.1f}亿元)',
                         fontsize=12, fontweight='bold')
            ax5.grid(True, alpha=0.3, axis='x')
        else:
            ax5.text(0.5, 0.5, '无需调控\n供需平衡', ha='center', va='center',
                    fontsize=14, fontweight='bold',
                    bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))
            ax5.set_title('调控方案', fontsize=12, fontweight='bold')
            ax5.axis('off')
        
        # 6. 工程措施投资
        ax6 = plt.subplot(3, 3, 6)
        
        measure_types = [m['type'] for m in measures]
        measure_investments = [m['investment'] for m in measures]
        colors_meas = ['#FFB6C1', '#87CEEB', '#98FB98', '#FFD700']
        
        wedges, texts, autotexts = ax6.pie(measure_investments, labels=measure_types,
                                           autopct='%1.1f%%', colors=colors_meas,
                                           startangle=90)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(9)
            autotext.set_fontweight('bold')
        
        ax6.set_title(f'工程措施投资分配\n(总投资{sum(measure_investments)}亿元)',
                     fontsize=12, fontweight='bold')
        
        # 7. 规划时序（年度发展）
        ax7 = plt.subplot(3, 3, 7)
        
        years_array = np.linspace(0, self.years, self.years+1)
        pop_growth = self.P_current + (self.P_plan - self.P_current) * years_array / self.years
        gdp_growth = self.GDP_current + (self.GDP_plan - self.GDP_current) * years_array / self.years
        
        ax7_twin = ax7.twinx()
        
        line1 = ax7.plot(years_array, pop_growth, 'b-o', linewidth=2, 
                        markersize=4, label='人口')
        line2 = ax7_twin.plot(years_array, gdp_growth, 'r-s', linewidth=2,
                             markersize=4, label='GDP')
        
        ax7.set_xlabel('年份', fontsize=10)
        ax7.set_ylabel('人口 (万人)', fontsize=10, color='blue')
        ax7_twin.set_ylabel('GDP (亿元)', fontsize=10, color='red')
        ax7.tick_params(axis='y', labelcolor='blue')
        ax7_twin.tick_params(axis='y', labelcolor='red')
        
        # 合并图例
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax7.legend(lines, labels, loc='upper left')
        
        ax7.set_title('规划时序分析', fontsize=12, fontweight='bold')
        ax7.grid(True, alpha=0.3)
        
        # 8. 综合效益
        ax8 = plt.subplot(3, 3, 8)
        
        benefit_types = ['经济效益', '生态效益', '社会效益']
        benefit_values = [benefit['economic_benefit']/1e1,
                         benefit['ecological_benefit']/1e1,
                         benefit['social_benefit']/1e1]
        colors_ben = ['gold', 'green', 'blue']
        
        bars = ax8.bar(benefit_types, benefit_values, color=colors_ben,
                      alpha=0.7, edgecolor='black')
        
        for bar, val in zip(bars, benefit_values):
            height = bar.get_height()
            ax8.text(bar.get_x() + bar.get_width()/2, height,
                    f'{val:.1f}', ha='center', va='bottom',
                    fontsize=9, fontweight='bold')
        
        ax8.set_ylabel('效益 (十亿元)', fontsize=10)
        ax8.set_title(f'综合效益评估\n(B/C={benefit["BC_ratio"]:.2f})',
                     fontsize=12, fontweight='bold')
        ax8.grid(True, alpha=0.3, axis='y')
        
        # 9. 结果汇总表
        ax9 = plt.subplot(3, 3, 9)
        ax9.axis('off')
        
        table_data = [
            ['项目', '数值', '单位'],
            ['水资源总量', f'{resources["W_total"]:.2f}', '亿m³'],
            ['可供水量', f'{resources["W_supply"]:.2f}', '亿m³'],
            ['现状需水', f'{demand["current"]["W_total"]:.2f}', '亿m³'],
            ['规划需水', f'{demand["plan"]["W_total"]:.2f}', '亿m³'],
            ['缺水量', f'{balance["plan"]["deficit"]:.2f}', '亿m³'],
            ['调控能力', f'{regulation["total_capacity"]:.2f}', '亿m³'],
            ['总投资', f'{benefit["total_investment"]:.1f}', '亿元'],
            ['总效益', f'{benefit["total_benefit"]:.1f}', '亿元'],
            ['B/C比', f'{benefit["BC_ratio"]:.2f}', '-'],
            ['回收期', f'{benefit["payback_period"]:.1f}', '年']
        ]
        
        table = ax9.table(cellText=table_data, cellLoc='center', loc='center',
                         colWidths=[0.40, 0.30, 0.25])
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1, 1.8)
        
        for i in range(3):
            table[(0, i)].set_facecolor('#4472C4')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        # 高亮关键指标
        for i in [6, 8, 9]:
            for j in range(3):
                table[(i, j)].set_facecolor('#FFF9E6')
        
        ax9.set_title('规划结果汇总', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('/tmp/ch13_problem13_comprehensive_planning.png', dpi=150, bbox_inches='tight')
        print(f"图表已保存: /tmp/ch13_problem13_comprehensive_planning.png")
        plt.show()
    
    def print_results(self):
        """打印结果"""
        print("\n" + "="*70)
        print("第13章 水资源计算 - 题13：水资源综合规划")
        print("="*70)
        
        resources = self.water_resources_evaluation()
        demand = self.water_demand_forecast()
        balance = self.supply_demand_balance()
        regulation = self.regulation_scheme()
        measures = self.engineering_measures()
        benefit = self.comprehensive_benefit()
        
        print(f"\n【水资源评价】")
        print(f"水资源总量: W = P×A×α = {self.P}×{self.A}×{self.alpha}")
        print(f"             = {resources['W_total']:.3f} 亿m³")
        print(f"可开发利用量: {resources['W_available']:.3f} 亿m³ (60%)")
        print(f"生态用水量: {resources['W_ecological']:.3f} 亿m³ (15%)")
        print(f"可供水量: {resources['W_supply']:.3f} 亿m³")
        
        print(f"\n【需水预测】")
        print(f"现状需水: {demand['current']['W_total']:.3f} 亿m³")
        print(f"  - 生活用水: {demand['current']['W_domestic']:.3f} 亿m³")
        print(f"  - 生产用水: {demand['current']['W_production']:.3f} 亿m³")
        print(f"规划需水: {demand['plan']['W_total']:.3f} 亿m³")
        print(f"  - 生活用水: {demand['plan']['W_domestic']:.3f} 亿m³")
        print(f"  - 生产用水: {demand['plan']['W_production']:.3f} 亿m³")
        
        print(f"\n【供需平衡】")
        print(f"现状平衡: {balance['current']['balance']:+.3f} 亿m³")
        if balance['current']['deficit'] > 0:
            print(f"  ✗ 缺水 {balance['current']['deficit']:.3f} 亿m³")
        else:
            print(f"  ✓ 富余 {balance['current']['surplus']:.3f} 亿m³")
        
        print(f"规划平衡: {balance['plan']['balance']:+.3f} 亿m³")
        if balance['plan']['deficit'] > 0:
            print(f"  ✗ 缺水 {balance['plan']['deficit']:.3f} 亿m³")
        else:
            print(f"  ✓ 富余 {balance['plan']['surplus']:.3f} 亿m³")
        
        print(f"\n【调控方案】")
        for i, scheme in enumerate(regulation['schemes'], 1):
            print(f"{i}. {scheme['name']}")
            print(f"   调控能力: {scheme['capacity']:.3f} 亿m³")
            print(f"   投资: {scheme['investment']:.1f} 亿元")
            print(f"   措施: {scheme['description']}")
        print(f"总调控能力: {regulation['total_capacity']:.3f} 亿m³")
        print(f"总投资: {regulation['total_investment']:.1f} 亿元")
        
        print(f"\n【工程措施】")
        for i, measure in enumerate(measures, 1):
            print(f"{i}. {measure['type']} (投资{measure['investment']}亿元)")
            for item in measure['items']:
                print(f"   - {item}")
        
        print(f"\n【综合效益】")
        print(f"总投资: {benefit['total_investment']:.2f} 亿元")
        print(f"经济效益: {benefit['economic_benefit']:.2f} 亿元 ({self.years}年)")
        print(f"生态效益: {benefit['ecological_benefit']:.2f} 亿元 ({self.years}年)")
        print(f"社会效益: {benefit['social_benefit']:.2f} 亿元 ({self.years}年)")
        print(f"总效益: {benefit['total_benefit']:.2f} 亿元")
        print(f"效益成本比: B/C = {benefit['BC_ratio']:.2f}")
        print(f"投资回收期: {benefit['payback_period']:.1f} 年")
        
        if benefit['BC_ratio'] > 1.0:
            print(f"✓ 项目经济可行")
        else:
            print(f"✗ 项目经济效益不佳")
        
        print(f"\n✓ 水资源综合规划完成")
        print(f"\n{'='*70}\n")


def main():
    A = 5000  # km²
    P = 800   # mm
    alpha = 0.40
    P_current = 200  # 万人
    P_plan = 300
    GDP_current = 600  # 亿元
    GDP_plan = 1200
    
    planning = ComprehensivePlanning(A, P, alpha, P_current, P_plan,
                                     GDP_current, GDP_plan, years=20)
    planning.print_results()
    planning.plot_analysis()


if __name__ == "__main__":
    main()
