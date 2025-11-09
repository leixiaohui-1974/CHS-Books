# -*- coding: utf-8 -*-
"""
第14章 压轴大题专项训练 - 题13：防洪工程综合设计

问题描述：
    某河段需设计防洪工程，保护面积A = 50 km²
    河道参数：
    - 河道长度L = 15km，底宽B = 80m，边坡m = 2.0
    - 河床坡度i = 0.0005，糙率n = 0.030
    - 百年一遇设计洪峰Q100 = 2000 m³/s
    - 二十年一遇校核洪峰Q20 = 1500 m³/s
    
    防洪标准：城区100年一遇，农田20年一遇
    工程措施：堤防+分洪道+蓄滞洪区
    
    求：
    1. 设计洪水位计算（天然+工程）
    2. 堤防断面设计与加高
    3. 分洪道布置与流量分配
    4. 蓄滞洪区容量与调度
    5. 防洪工程投资估算
    6. 综合效益评价（减灾效益）

核心公式：
    1. Q = A·R^(2/3)·i^(1/2)/n (曼宁)
    2. 分洪流量: Q_分 = Q_总 - Q_河
    3. 减灾效益: B = Σ(损失_无工程 - 损失_有工程)

考试要点：
    - 洪水计算
    - 堤防设计
    - 分洪工程
    - 减灾效益

作者: CHS-Books Team
日期: 2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, Dict, List
from scipy.optimize import fsolve

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class FloodControlDesign:
    """防洪工程综合设计"""
    
    def __init__(self, A_protect: float, L: float, B: float, m: float,
                 i: float, n: float, Q100: float, Q20: float):
        self.A_protect = A_protect  # 保护面积 km²
        self.L = L  # 河道长度 km
        self.B = B  # 河道底宽 m
        self.m = m  # 边坡系数
        self.i = i  # 河床坡度
        self.n = n  # 糙率
        self.Q100 = Q100  # 百年洪峰 m³/s
        self.Q20 = Q20  # 二十年洪峰 m³/s
        
    def natural_water_level(self, Q: float) -> Dict:
        """天然河道水位计算"""
        # 根据流量反推水深
        def equations(h):
            A = (self.B + self.m * h) * h
            P = self.B + 2 * h * np.sqrt(1 + self.m**2)
            R = A / P if P > 0 else 0
            Q_calc = A * R**(2/3) * self.i**(1/2) / self.n
            return Q_calc - Q
        
        h_natural = fsolve(equations, 5.0)[0]
        
        # 水面宽度
        B_water = self.B + 2 * self.m * h_natural
        
        # 过水断面积
        A_section = (self.B + self.m * h_natural) * h_natural
        
        # 流速
        v = Q / A_section if A_section > 0 else 0
        
        return {
            'h': h_natural,
            'B_water': B_water,
            'A_section': A_section,
            'v': v
        }
    
    def levee_design(self, h_design: float) -> Dict:
        """堤防设计"""
        # 设计堤顶高程
        # H_堤 = h_设计 + 超高 + 安全加高
        
        # 超高（根据流速和风浪）
        v = self.natural_water_level(self.Q100)['v']
        
        # 风浪爬高（简化）
        h_wave = 0.5 + 0.1 * v  # m
        
        # 安全加高
        h_safety = 0.5  # m
        
        # 堤顶高程
        H_levee = h_design + h_wave + h_safety
        
        # 堤身断面
        # 堤顶宽度
        B_top = 3.0  # m
        
        # 边坡（临水1:3，背水1:2.5）
        m_water = 3.0
        m_land = 2.5
        
        # 堤底宽度
        B_bottom = B_top + (m_water + m_land) * H_levee
        
        # 断面积
        A_levee = (B_top + B_bottom) * H_levee / 2
        
        return {
            'h_wave': h_wave,
            'h_safety': h_safety,
            'H_levee': H_levee,
            'B_top': B_top,
            'B_bottom': B_bottom,
            'A_levee': A_levee,
            'm_water': m_water,
            'm_land': m_land
        }
    
    def diversion_channel_design(self, Q_total: float, Q_river_capacity: float) -> Dict:
        """分洪道设计"""
        # 分洪流量
        Q_diversion = max(0, Q_total - Q_river_capacity)
        
        # 分洪道断面（简化为梯形）
        B_diversion = 50  # m
        m_diversion = 2.0
        i_diversion = 0.001
        n_diversion = 0.025
        
        # 根据分洪流量计算水深
        if Q_diversion > 0:
            def equations(h):
                A = (B_diversion + m_diversion * h) * h
                P = B_diversion + 2 * h * np.sqrt(1 + m_diversion**2)
                R = A / P if P > 0 else 0
                Q_calc = A * R**(2/3) * i_diversion**(1/2) / n_diversion
                return Q_calc - Q_diversion
            
            h_diversion = fsolve(equations, 3.0)[0]
        else:
            h_diversion = 0
        
        # 分洪道长度（取河道长度的70%）
        L_diversion = self.L * 0.7
        
        return {
            'Q_diversion': Q_diversion,
            'Q_river': Q_river_capacity,
            'B_diversion': B_diversion,
            'h_diversion': h_diversion,
            'L_diversion': L_diversion,
            'diversion_ratio': Q_diversion / Q_total if Q_total > 0 else 0
        }
    
    def detention_basin(self, Q_peak: float) -> Dict:
        """蓄滞洪区设计"""
        # 削峰量（简化计算）
        Q_reduction = Q_peak * 0.15  # 削减15%
        
        # 洪峰持续时间（简化取6小时）
        T_duration = 6 * 3600  # s
        
        # 所需容积
        V_basin = Q_reduction * T_duration / 1e6  # 百万m³
        
        # 蓄滞洪区面积（假设平均蓄水深度3m）
        h_average = 3.0  # m
        A_basin = V_basin * 1e6 / h_average / 1e6  # km²
        
        # 进退水时间
        T_fill = T_duration
        T_drain = T_duration * 2
        
        return {
            'Q_reduction': Q_reduction,
            'V_basin': V_basin,
            'A_basin': A_basin,
            'h_average': h_average,
            'T_fill': T_fill / 3600,  # hours
            'T_drain': T_drain / 3600
        }
    
    def cost_estimation(self, levee: Dict, diversion: Dict, basin: Dict) -> Dict:
        """投资估算"""
        # 堤防工程
        V_levee = levee['A_levee'] * self.L * 1000  # m³
        cost_levee = V_levee * 50 / 1e6  # 百万元（50元/m³）
        
        # 分洪道工程
        if diversion['Q_diversion'] > 0:
            # 土方开挖
            A_diversion = (diversion['B_diversion'] + self.m * diversion['h_diversion']) * diversion['h_diversion']
            V_diversion = A_diversion * diversion['L_diversion'] * 1000
            cost_diversion = V_diversion * 30 / 1e6  # 百万元
            
            # 控制建筑物
            cost_control = 50  # 百万元
            cost_diversion += cost_control
        else:
            cost_diversion = 0
        
        # 蓄滞洪区工程
        # 围堤工程
        cost_basin_levee = basin['A_basin'] * 0.5  # 百万元/km²
        # 进退水建筑物
        cost_basin_structures = 30  # 百万元
        cost_basin = cost_basin_levee + cost_basin_structures
        
        # 总投资
        total_cost = cost_levee + cost_diversion + cost_basin
        
        return {
            'cost_levee': cost_levee,
            'cost_diversion': cost_diversion,
            'cost_basin': cost_basin,
            'total_cost': total_cost
        }
    
    def flood_damage_assessment(self) -> Dict:
        """洪灾损失评估"""
        # 无工程情况损失（假设）
        # 百年一遇洪水
        damage_100_without = self.A_protect * 20  # 百万元/km²
        
        # 二十年一遇洪水
        damage_20_without = self.A_protect * 8
        
        # 有工程情况损失（大幅降低）
        damage_100_with = self.A_protect * 2  # 降低90%
        damage_20_with = self.A_protect * 0.5  # 降低94%
        
        # 减灾效益
        benefit_100 = damage_100_without - damage_100_with
        benefit_20 = damage_20_without - damage_20_with
        
        # 年均减灾效益（考虑频率）
        p_100 = 0.01  # 百年一遇概率
        p_20 = 0.05   # 二十年一遇概率
        
        annual_benefit = benefit_100 * p_100 + benefit_20 * p_20
        
        return {
            'damage_100_without': damage_100_without,
            'damage_100_with': damage_100_with,
            'benefit_100': benefit_100,
            'damage_20_without': damage_20_without,
            'damage_20_with': damage_20_with,
            'benefit_20': benefit_20,
            'annual_benefit': annual_benefit
        }
    
    def economic_evaluation(self, cost: Dict, damage: Dict) -> Dict:
        """经济评价"""
        total_investment = cost['total_cost']
        annual_benefit = damage['annual_benefit']
        
        # 年运行维护费（投资的2%）
        annual_maintenance = total_investment * 0.02
        
        # 年净效益
        net_benefit = annual_benefit - annual_maintenance
        
        # 投资回收期
        payback_period = total_investment / net_benefit if net_benefit > 0 else np.inf
        
        # 效益成本比
        BC_ratio = annual_benefit / (total_investment / 20 + annual_maintenance)
        
        # NPV（30年，折现率6%）
        discount_rate = 0.06
        years = 30
        NPV = sum([net_benefit / (1 + discount_rate)**t 
                   for t in range(1, years+1)]) - total_investment
        
        return {
            'total_investment': total_investment,
            'annual_benefit': annual_benefit,
            'annual_maintenance': annual_maintenance,
            'net_benefit': net_benefit,
            'payback_period': payback_period,
            'BC_ratio': BC_ratio,
            'NPV': NPV
        }
    
    def plot_analysis(self):
        """绘制分析图表"""
        fig = plt.figure(figsize=(16, 12))
        
        natural_100 = self.natural_water_level(self.Q100)
        natural_20 = self.natural_water_level(self.Q20)
        levee = self.levee_design(natural_100['h'])
        diversion = self.diversion_channel_design(self.Q100, self.Q20)
        basin = self.detention_basin(self.Q100)
        cost = self.cost_estimation(levee, diversion, basin)
        damage = self.flood_damage_assessment()
        economic = self.economic_evaluation(cost, damage)
        
        # 1. 河道断面与堤防
        ax1 = plt.subplot(3, 3, 1)
        
        # 河道断面
        h_levee = levee['H_levee']
        x_left = -self.B/2 - self.m * h_levee - levee['m_water'] * h_levee
        x_right = self.B/2 + self.m * h_levee + levee['m_land'] * h_levee
        
        # 河道
        x_river = np.array([
            -self.B/2 - self.m * h_levee,
            -self.B/2,
            self.B/2,
            self.B/2 + self.m * h_levee
        ])
        y_river = np.array([h_levee, 0, 0, h_levee])
        
        ax1.fill(x_river, y_river, alpha=0.3, color='lightblue', label='河道')
        ax1.plot(x_river, y_river, 'b-', linewidth=2)
        
        # 设计水位
        ax1.axhline(natural_100['h'], color='r', linestyle='--', linewidth=2,
                   label=f'百年洪水位{natural_100["h"]:.1f}m')
        ax1.axhline(natural_20['h'], color='orange', linestyle='--', linewidth=2,
                   label=f'20年洪水位{natural_20["h"]:.1f}m')
        
        # 左堤
        x_left_levee = [x_left, -self.B/2 - self.m * h_levee, 
                       -self.B/2 - self.m * h_levee - levee['B_top']]
        y_left_levee = [0, h_levee, h_levee]
        ax1.fill(x_left_levee, y_left_levee, alpha=0.5, color='brown', label='堤防')
        ax1.plot(x_left_levee, y_left_levee, 'k-', linewidth=2)
        
        # 右堤
        x_right_levee = [x_right, self.B/2 + self.m * h_levee,
                        self.B/2 + self.m * h_levee + levee['B_top']]
        y_right_levee = [0, h_levee, h_levee]
        ax1.fill(x_right_levee, y_right_levee, alpha=0.5, color='brown')
        ax1.plot(x_right_levee, y_right_levee, 'k-', linewidth=2)
        
        ax1.set_xlabel('宽度 (m)', fontsize=10)
        ax1.set_ylabel('高程 (m)', fontsize=10)
        ax1.set_title('河道断面与堤防设计', fontsize=12, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_aspect('equal')
        
        # 2. 基本参数
        ax2 = plt.subplot(3, 3, 2)
        ax2.axis('off')
        
        ax2.text(0.5, 0.95, '工程参数', fontsize=11, ha='center', fontweight='bold')
        ax2.text(0.1, 0.82, f'保护面积: {self.A_protect} km²', fontsize=10)
        ax2.text(0.1, 0.74, f'河道长度: {self.L} km', fontsize=10)
        ax2.text(0.1, 0.66, f'百年洪峰: {self.Q100} m³/s', fontsize=10)
        ax2.text(0.1, 0.58, f'20年洪峰: {self.Q20} m³/s', fontsize=10)
        
        ax2.text(0.1, 0.45, f'堤防高度: {levee["H_levee"]:.2f} m', fontsize=10, color='brown')
        ax2.text(0.1, 0.37, f'分洪流量: {diversion["Q_diversion"]:.0f} m³/s', fontsize=10, color='blue')
        ax2.text(0.1, 0.29, f'蓄滞容积: {basin["V_basin"]:.1f} 百万m³', fontsize=10, color='green')
        
        ax2.text(0.1, 0.16, f'总投资: {cost["total_cost"]:.1f} 百万元', fontsize=10, color='red')
        ax2.text(0.1, 0.08, f'年均效益: {damage["annual_benefit"]:.1f} 百万元', 
                fontsize=10, color='green', fontweight='bold')
        
        ax2.set_title('参数汇总', fontsize=12, fontweight='bold')
        
        # 3. 洪水位对比
        ax3 = plt.subplot(3, 3, 3)
        
        scenarios = ['百年一遇', '20年一遇']
        heights = [natural_100['h'], natural_20['h']]
        colors_flood = ['red', 'orange']
        
        bars = ax3.bar(scenarios, heights, color=colors_flood, 
                      alpha=0.7, edgecolor='black')
        ax3.axhline(levee['H_levee'], color='brown', linestyle='--', linewidth=2,
                   label=f'堤顶高程{levee["H_levee"]:.1f}m')
        
        for bar, val in zip(bars, heights):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2, height,
                    f'{val:.2f}m', ha='center', va='bottom',
                    fontsize=10, fontweight='bold')
        
        ax3.set_ylabel('水位 (m)', fontsize=10)
        ax3.set_title('设计洪水位', fontsize=12, fontweight='bold')
        ax3.legend()
        ax3.grid(True, alpha=0.3, axis='y')
        
        # 4. 流量分配
        ax4 = plt.subplot(3, 3, 4)
        
        flow_items = ['河道', '分洪道']
        flow_values = [diversion['Q_river'], diversion['Q_diversion']]
        colors_flow = ['blue', 'green']
        
        wedges, texts, autotexts = ax4.pie(flow_values, labels=flow_items,
                                           autopct='%1.1f%%', colors=colors_flow,
                                           startangle=90)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(10)
            autotext.set_fontweight('bold')
        
        ax4.set_title(f'百年洪峰流量分配\n(总流量{self.Q100}m³/s)',
                     fontsize=12, fontweight='bold')
        
        # 5. 投资构成
        ax5 = plt.subplot(3, 3, 5)
        
        cost_items = ['堤防', '分洪道', '蓄滞洪区']
        cost_values = [cost['cost_levee'], cost['cost_diversion'], cost['cost_basin']]
        colors_cost = ['brown', 'blue', 'green']
        
        bars = ax5.bar(cost_items, cost_values, color=colors_cost,
                      alpha=0.7, edgecolor='black')
        
        for bar, val in zip(bars, cost_values):
            height = bar.get_height()
            ax5.text(bar.get_x() + bar.get_width()/2, height,
                    f'{val:.1f}', ha='center', va='bottom',
                    fontsize=9, fontweight='bold')
        
        ax5.set_ylabel('投资 (百万元)', fontsize=10)
        ax5.set_title(f'投资构成\n(总投资{cost["total_cost"]:.1f}百万元)',
                     fontsize=12, fontweight='bold')
        ax5.grid(True, alpha=0.3, axis='y')
        
        # 6. 减灾效益对比
        ax6 = plt.subplot(3, 3, 6)
        
        scenarios_damage = ['百年一遇', '20年一遇']
        damage_without = [damage['damage_100_without'], damage['damage_20_without']]
        damage_with = [damage['damage_100_with'], damage['damage_20_with']]
        
        x = np.arange(len(scenarios_damage))
        width = 0.35
        
        bars1 = ax6.bar(x - width/2, damage_without, width, label='无工程',
                       color='red', alpha=0.7, edgecolor='black')
        bars2 = ax6.bar(x + width/2, damage_with, width, label='有工程',
                       color='green', alpha=0.7, edgecolor='black')
        
        ax6.set_xlabel('情景', fontsize=10)
        ax6.set_ylabel('损失 (百万元)', fontsize=10)
        ax6.set_title('洪灾损失对比', fontsize=12, fontweight='bold')
        ax6.set_xticks(x)
        ax6.set_xticklabels(scenarios_damage)
        ax6.legend()
        ax6.grid(True, alpha=0.3, axis='y')
        
        # 7. 蓄滞洪区调度
        ax7 = plt.subplot(3, 3, 7)
        
        # 简化的蓄泄过程
        time = np.array([0, 3, 6, 9, 12, 18, 24])  # hours
        storage = np.array([0, 50, 100, 80, 50, 20, 5])  # % of V_basin
        
        ax7.plot(time, storage, 'b-o', linewidth=2, markersize=6)
        ax7.fill_between(time, 0, storage, alpha=0.3, color='lightblue')
        ax7.axhline(100, color='r', linestyle='--', linewidth=1, label='设计容量')
        
        ax7.set_xlabel('时间 (小时)', fontsize=10)
        ax7.set_ylabel('蓄水率 (%)', fontsize=10)
        ax7.set_title(f'蓄滞洪区调度\n(容积{basin["V_basin"]:.1f}百万m³)',
                     fontsize=12, fontweight='bold')
        ax7.legend()
        ax7.grid(True, alpha=0.3)
        
        # 8. 经济效益分析
        ax8 = plt.subplot(3, 3, 8)
        
        benefit_items = ['年均效益', '年维护费', '年净效益']
        benefit_values = [economic['annual_benefit'],
                         -economic['annual_maintenance'],
                         economic['net_benefit']]
        colors_benefit = ['green', 'red', 'blue']
        
        bars = ax8.barh(benefit_items, benefit_values, color=colors_benefit,
                       alpha=0.7, edgecolor='black')
        ax8.axvline(0, color='k', linewidth=1)
        
        for bar, val in zip(bars, benefit_values):
            width = bar.get_width()
            ax8.text(width, bar.get_y() + bar.get_height()/2,
                    f'{val:.1f}', ha='left' if width>0 else 'right',
                    va='center', fontsize=9, fontweight='bold')
        
        ax8.set_xlabel('金额 (百万元)', fontsize=10)
        ax8.set_title(f'经济效益分析\n(B/C={economic["BC_ratio"]:.2f})',
                     fontsize=12, fontweight='bold')
        ax8.grid(True, alpha=0.3, axis='x')
        
        # 9. 综合评价表
        ax9 = plt.subplot(3, 3, 9)
        ax9.axis('off')
        
        table_data = [
            ['项目', '数值', '单位'],
            ['百年洪水位', f'{natural_100["h"]:.2f}', 'm'],
            ['堤防高度', f'{levee["H_levee"]:.2f}', 'm'],
            ['分洪流量', f'{diversion["Q_diversion"]:.0f}', 'm³/s'],
            ['蓄滞容积', f'{basin["V_basin"]:.1f}', '百万m³'],
            ['总投资', f'{cost["total_cost"]:.1f}', '百万元'],
            ['年均效益', f'{damage["annual_benefit"]:.1f}', '百万元'],
            ['投资回收期', f'{economic["payback_period"]:.1f}', '年'],
            ['NPV', f'{economic["NPV"]:.0f}', '百万元'],
            ['B/C比', f'{economic["BC_ratio"]:.2f}', '-']
        ]
        
        table = ax9.table(cellText=table_data, cellLoc='center', loc='center',
                         colWidths=[0.40, 0.30, 0.25])
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1, 1.9)
        
        for i in range(3):
            table[(0, i)].set_facecolor('#4472C4')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        # 高亮关键指标
        for i in [6, 8, 9]:
            for j in range(3):
                table[(i, j)].set_facecolor('#FFF9E6')
        
        ax9.set_title('综合评价汇总', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('/tmp/ch14_problem13_flood_control_design.png', dpi=150, bbox_inches='tight')
        print(f"图表已保存: /tmp/ch14_problem13_flood_control_design.png")
        plt.show()
    
    def print_results(self):
        """打印结果"""
        print("\n" + "="*70)
        print("第14章 压轴大题 - 题13：防洪工程综合设计")
        print("="*70)
        
        natural_100 = self.natural_water_level(self.Q100)
        natural_20 = self.natural_water_level(self.Q20)
        levee = self.levee_design(natural_100['h'])
        diversion = self.diversion_channel_design(self.Q100, self.Q20)
        basin = self.detention_basin(self.Q100)
        cost = self.cost_estimation(levee, diversion, basin)
        damage = self.flood_damage_assessment()
        economic = self.economic_evaluation(cost, damage)
        
        print(f"\n【1. 设计洪水位】")
        print(f"百年一遇 (Q={self.Q100} m³/s):")
        print(f"  水深: h = {natural_100['h']:.3f} m")
        print(f"  水面宽: B = {natural_100['B_water']:.2f} m")
        print(f"  流速: v = {natural_100['v']:.3f} m/s")
        print(f"20年一遇 (Q={self.Q20} m³/s):")
        print(f"  水深: h = {natural_20['h']:.3f} m")
        print(f"  流速: v = {natural_20['v']:.3f} m/s")
        
        print(f"\n【2. 堤防设计】")
        print(f"设计水位: {natural_100['h']:.2f} m")
        print(f"波浪爬高: {levee['h_wave']:.2f} m")
        print(f"安全加高: {levee['h_safety']:.2f} m")
        print(f"堤顶高程: {levee['H_levee']:.2f} m")
        print(f"堤顶宽度: {levee['B_top']:.1f} m")
        print(f"堤底宽度: {levee['B_bottom']:.1f} m")
        print(f"边坡(临水): 1:{levee['m_water']}")
        print(f"边坡(背水): 1:{levee['m_land']}")
        
        print(f"\n【3. 分洪道布置】")
        print(f"百年洪峰: Q_总 = {self.Q100} m³/s")
        print(f"河道流量: Q_河 = {diversion['Q_river']:.0f} m³/s")
        print(f"分洪流量: Q_分 = {diversion['Q_diversion']:.0f} m³/s")
        print(f"分洪比例: {diversion['diversion_ratio']:.1%}")
        print(f"分洪道长度: {diversion['L_diversion']:.1f} km")
        
        print(f"\n【4. 蓄滞洪区】")
        print(f"削峰流量: {basin['Q_reduction']:.0f} m³/s")
        print(f"蓄滞容积: {basin['V_basin']:.2f} 百万m³")
        print(f"淹没面积: {basin['A_basin']:.2f} km²")
        print(f"平均水深: {basin['h_average']:.1f} m")
        print(f"进水时间: {basin['T_fill']:.1f} 小时")
        print(f"退水时间: {basin['T_drain']:.1f} 小时")
        
        print(f"\n【5. 投资估算】")
        print(f"堤防工程: {cost['cost_levee']:.1f} 百万元")
        print(f"分洪道工程: {cost['cost_diversion']:.1f} 百万元")
        print(f"蓄滞洪区: {cost['cost_basin']:.1f} 百万元")
        print(f"总投资: {cost['total_cost']:.1f} 百万元")
        
        print(f"\n【6. 综合效益】")
        print(f"百年一遇减灾: {damage['benefit_100']:.1f} 百万元")
        print(f"20年一遇减灾: {damage['benefit_20']:.1f} 百万元")
        print(f"年均效益: {damage['annual_benefit']:.1f} 百万元")
        print(f"年维护费: {economic['annual_maintenance']:.1f} 百万元")
        print(f"年净效益: {economic['net_benefit']:.1f} 百万元")
        print(f"投资回收期: {economic['payback_period']:.1f} 年")
        print(f"效益成本比: B/C = {economic['BC_ratio']:.2f}")
        print(f"NPV(30年): {economic['NPV']:.0f} 百万元")
        
        if economic['BC_ratio'] > 1.0 and economic['NPV'] > 0:
            print(f"✓ 工程经济合理")
        else:
            print(f"△ 需优化方案")
        
        print(f"\n✓ 防洪工程综合设计完成")
        print(f"\n{'='*70}\n")


def main():
    A_protect = 50  # km²
    L = 15  # km
    B = 80  # m
    m = 2.0
    i = 0.0005
    n = 0.030
    Q100 = 2000  # m³/s
    Q20 = 1500  # m³/s
    
    flood_control = FloodControlDesign(A_protect, L, B, m, i, n, Q100, Q20)
    flood_control.print_results()
    flood_control.plot_analysis()


if __name__ == "__main__":
    main()
