# -*- coding: utf-8 -*-
"""
第12章 河流动力学 - 题13：河流综合治理方案

问题描述：
    某河段治理工程，河道长度L = 5km
    多年平均流量Q = 1000 m³/s，设计洪峰Qp = 3000 m³/s
    河道宽度B = 150m，河床坡度i = 0.0003
    泥沙d₅₀ = 0.25mm，含沙量S = 4 kg/m³
    
    求：
    1. 河道整治方案设计
    2. 防洪能力评估
    3. 生态护岸设计
    4. 泥沙综合治理
    5. 综合效益分析

核心内容：
    1. 河道断面设计
    2. 防洪标准
    3. 生态护岸
    4. 泥沙调控
    5. 综合评价

考试要点：
    - 河道整治
    - 防洪能力
    - 生态设计
    - 综合治理

作者: CHS-Books Team
日期: 2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, Dict, List

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class ComprehensiveRiverManagement:
    """河流综合治理"""
    
    def __init__(self, L: float, Q: float, Qp: float, B: float,
                 i: float, d50: float, S: float):
        self.L = L * 1000  # 转为m
        self.Q = Q  # 多年平均流量
        self.Qp = Qp  # 设计洪峰
        self.B = B  # 河道宽度
        self.i = i  # 河床坡度
        self.d50 = d50  # 中值粒径
        self.S = S  # 含沙量
        self.n = 0.025  # 糙率
        self.g = 9.8
        
    def design_discharge(self) -> Dict:
        """设计流量"""
        Q_normal = self.Q
        Q_flood = self.Qp
        
        # 设计标准（百年一遇）
        return_period = 100
        
        return {
            'Q_normal': Q_normal,
            'Q_flood': Q_flood,
            'return_period': return_period
        }
    
    def channel_design(self) -> Dict:
        """
        河道断面设计（梯形断面）
        采用统一河相关系估算
        """
        # 平均流量下的设计
        Q = self.Q
        
        # 河宽（按河相关系）
        B_design = 4.7 * (Q ** 0.5)
        
        # 水深（曼宁公式反算）
        h_design = (Q * self.n / (B_design * np.sqrt(self.i))) ** (3/5)
        
        # 边坡系数（生态护岸，缓坡）
        m = 3.0  # 1:3边坡
        
        # 超高（防洪加高）
        freeboard = 1.5  # m
        
        # 设计洪水位
        h_flood = (self.Qp * self.n / (B_design * np.sqrt(self.i))) ** (3/5)
        
        # 堤顶高程
        H_dike = h_flood + freeboard
        
        return {
            'B': B_design,
            'h': h_design,
            'm': m,
            'freeboard': freeboard,
            'h_flood': h_flood,
            'H_dike': H_dike
        }
    
    def flood_capacity(self) -> Dict:
        """防洪能力评估"""
        design = self.channel_design()
        
        # 过流能力（曼宁公式）
        A = design['B'] * design['h_flood'] + design['m'] * (design['h_flood'] ** 2)
        P = design['B'] + 2 * design['h_flood'] * np.sqrt(1 + design['m'] ** 2)
        R = A / P
        
        Q_capacity = (1/self.n) * A * (R ** (2/3)) * np.sqrt(self.i)
        
        # 安全系数
        safety_factor = Q_capacity / self.Qp
        
        return {
            'Q_capacity': Q_capacity,
            'safety_factor': safety_factor,
            'is_safe': safety_factor >= 1.2
        }
    
    def ecological_revetment(self) -> Dict:
        """生态护岸设计"""
        design = self.channel_design()
        
        # 护岸类型
        revetment_types = {
            '主河道': '混凝土预制块+植草',
            '边滩': '植被护坡',
            '堤脚': '石笼+水生植物'
        }
        
        # 护岸工程量
        # 边坡长度
        slope_length = design['H_dike'] * np.sqrt(1 + design['m'] ** 2)
        
        # 护岸面积（两岸）
        area_revetment = 2 * slope_length * self.L
        
        # 植被覆盖率目标
        vegetation_coverage = 0.7  # 70%
        
        return {
            'types': revetment_types,
            'slope_length': slope_length,
            'area_revetment': area_revetment,
            'vegetation_coverage': vegetation_coverage
        }
    
    def sediment_management(self) -> Dict:
        """泥沙综合治理"""
        # 年输沙量
        Q_sediment_year = self.S * self.Q * 86400 * 365 / 1e6  # 万t/年
        
        # 治理措施
        measures = {
            '上游': '水土保持、植树造林',
            '中游': '淤地坝、梯田',
            '下游': '疏浚清淤、调水调沙'
        }
        
        # 治理目标（减少30%泥沙）
        reduction_target = 0.3
        Q_sediment_target = Q_sediment_year * (1 - reduction_target)
        
        return {
            'Q_sediment_year': Q_sediment_year,
            'measures': measures,
            'reduction_target': reduction_target,
            'Q_sediment_target': Q_sediment_target
        }
    
    def comprehensive_benefits(self) -> Dict:
        """综合效益评估"""
        # 防洪效益（减少洪灾损失）
        benefit_flood = 5000  # 万元/年
        
        # 生态效益（改善环境）
        benefit_ecology = 3000  # 万元/年
        
        # 航运效益（改善通航）
        benefit_navigation = 2000  # 万元/年
        
        # 景观效益（滨水空间）
        benefit_landscape = 1500  # 万元/年
        
        # 总效益
        benefit_total = benefit_flood + benefit_ecology + benefit_navigation + benefit_landscape
        
        # 工程投资（估算）
        design = self.channel_design()
        revetment = self.ecological_revetment()
        
        # 清淤疏浚
        cost_dredging = self.L * self.B * 2 * 100 / 10000  # 万元
        
        # 护岸工程
        cost_revetment = revetment['area_revetment'] * 200 / 10000  # 万元
        
        # 植被绿化
        cost_vegetation = revetment['area_revetment'] * 50 / 10000  # 万元
        
        # 总投资
        cost_total = cost_dredging + cost_revetment + cost_vegetation
        
        # 效益费用比
        bcr = benefit_total / cost_total if cost_total > 0 else 0
        
        return {
            'benefit_flood': benefit_flood,
            'benefit_ecology': benefit_ecology,
            'benefit_navigation': benefit_navigation,
            'benefit_landscape': benefit_landscape,
            'benefit_total': benefit_total,
            'cost_dredging': cost_dredging,
            'cost_revetment': cost_revetment,
            'cost_vegetation': cost_vegetation,
            'cost_total': cost_total,
            'bcr': bcr
        }
    
    def plot_analysis(self):
        """绘制分析图表"""
        fig = plt.figure(figsize=(16, 12))
        
        discharge_design = self.design_discharge()
        channel = self.channel_design()
        flood = self.flood_capacity()
        revetment = self.ecological_revetment()
        sediment = self.sediment_management()
        benefits = self.comprehensive_benefits()
        
        # 1. 河道断面设计
        ax1 = plt.subplot(3, 3, 1)
        
        # 断面坐标
        y_section = np.array([
            -channel['m']*channel['H_dike'],  # 左堤脚
            0, 0, channel['B'], channel['B'],  # 河底
            channel['B'] + channel['m']*channel['H_dike']  # 右堤脚
        ])
        z_section = np.array([
            channel['H_dike'],  # 左堤顶
            channel['H_dike'], 0, 0, channel['H_dike'],  # 河底到右堤顶
            channel['H_dike']  # 右堤顶
        ])
        
        ax1.fill(y_section, z_section, color='brown', alpha=0.3, edgecolor='black', linewidth=2, label='河道断面')
        
        # 水位线
        y_water = np.array([0, channel['B']])
        z_normal = np.array([channel['h'], channel['h']])
        z_flood = np.array([channel['h_flood'], channel['h_flood']])
        
        ax1.fill_between(y_water, 0, z_normal, color='lightblue', alpha=0.5, label='正常水位')
        ax1.fill_between(y_water, z_normal, z_flood, color='lightcoral', alpha=0.3, label='洪水位')
        ax1.plot(y_water, z_normal, 'b-', linewidth=2)
        ax1.plot(y_water, z_flood, 'r--', linewidth=2)
        
        # 标注
        ax1.text(channel['B']/2, channel['h']/2, f'正常水深\n{channel["h"]:.2f}m', 
                ha='center', fontsize=9, bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        ax1.set_xlabel('宽度 (m)', fontsize=10)
        ax1.set_ylabel('高程 (m)', fontsize=10)
        ax1.set_title('河道断面设计', fontsize=12, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim(y_section[0]-5, y_section[-1]+5)
        
        # 2. 设计参数
        ax2 = plt.subplot(3, 3, 2)
        ax2.axis('off')
        
        ax2.text(0.5, 0.95, '设计参数', fontsize=11, ha='center', fontweight='bold')
        ax2.text(0.1, 0.82, f'河段长度: L = {self.L/1000} km', fontsize=10)
        ax2.text(0.1, 0.72, f'设计河宽: B = {channel["B"]:.1f} m', fontsize=10, color='blue')
        ax2.text(0.1, 0.62, f'正常水深: h = {channel["h"]:.2f} m', fontsize=10)
        ax2.text(0.1, 0.52, f'洪水水深: h_flood = {channel["h_flood"]:.2f} m', fontsize=10, color='red')
        ax2.text(0.1, 0.42, f'边坡系数: m = {channel["m"]}', fontsize=10)
        ax2.text(0.1, 0.32, f'超高: {channel["freeboard"]} m', fontsize=10)
        ax2.text(0.1, 0.22, f'设计流量: Q = {self.Q} m³/s', fontsize=10)
        ax2.text(0.1, 0.12, f'洪峰流量: Qp = {self.Qp} m³/s', fontsize=10)
        ax2.text(0.1, 0.02, f'防洪标准: {discharge_design["return_period"]}年一遇', fontsize=10, color='green')
        
        ax2.set_title('基本参数', fontsize=12, fontweight='bold')
        
        # 3. 防洪能力
        ax3 = plt.subplot(3, 3, 3)
        
        items = ['设计洪峰', '过流能力']
        values = [self.Qp, flood['Q_capacity']]
        colors_flood = ['red', 'green']
        
        bars = ax3.barh(items, values, color=colors_flood, alpha=0.7, edgecolor='black')
        
        ax3.set_xlabel('流量 (m³/s)', fontsize=10)
        ax3.set_title(f'防洪能力 (安全系数{flood["safety_factor"]:.2f})', fontsize=12, fontweight='bold')
        ax3.grid(True, alpha=0.3, axis='x')
        
        for bar, val in zip(bars, values):
            width = bar.get_width()
            ax3.text(width, bar.get_y() + bar.get_height()/2,
                    f'{val:.0f}', ha='left', va='center', fontsize=10, fontweight='bold')
        
        # 4. 生态护岸布置
        ax4 = plt.subplot(3, 3, 4)
        
        # 平面示意（简化）
        x_river = np.linspace(0, self.L/1000, 100)
        y_left = np.ones_like(x_river) * (-channel['B']/2)
        y_right = np.ones_like(x_river) * (channel['B']/2)
        
        ax4.fill_between(x_river, y_left, y_right, color='lightblue', alpha=0.5, label='河道')
        ax4.plot(x_river, y_left, 'g-', linewidth=3, label='生态护岸')
        ax4.plot(x_river, y_right, 'g-', linewidth=3)
        
        # 标注护岸类型
        for i, (name, desc) in enumerate(revetment['types'].items()):
            ax4.text(self.L/1000/4*(i+0.5), 0, name, ha='center', fontsize=8,
                    bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.6))
        
        ax4.set_xlabel('长度 (km)', fontsize=10)
        ax4.set_ylabel('宽度方向 (m)', fontsize=10)
        ax4.set_title('生态护岸布置', fontsize=12, fontweight='bold')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        ax4.set_xlim(0, self.L/1000)
        
        # 5. 综合效益
        ax5 = plt.subplot(3, 3, 5)
        
        benefit_labels = ['防洪', '生态', '航运', '景观']
        benefit_values = [benefits['benefit_flood'], benefits['benefit_ecology'],
                         benefits['benefit_navigation'], benefits['benefit_landscape']]
        colors_benefit = ['red', 'green', 'blue', 'orange']
        
        wedges, texts, autotexts = ax5.pie(benefit_values, labels=benefit_labels,
                                           autopct='%1.1f%%', colors=colors_benefit,
                                           startangle=90)
        
        for text in texts:
            text.set_fontsize(10)
            text.set_fontweight('bold')
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(9)
            autotext.set_fontweight('bold')
        
        ax5.set_title(f'综合效益 (总计{benefits["benefit_total"]}万元/年)', 
                     fontsize=12, fontweight='bold')
        
        # 6. 投资构成
        ax6 = plt.subplot(3, 3, 6)
        
        cost_labels = ['清淤疏浚', '护岸工程', '植被绿化']
        cost_values = [benefits['cost_dredging'], benefits['cost_revetment'],
                      benefits['cost_vegetation']]
        colors_cost = ['brown', 'gray', 'lightgreen']
        
        bars = ax6.bar(cost_labels, cost_values, color=colors_cost, alpha=0.7, edgecolor='black')
        
        ax6.set_ylabel('投资 (万元)', fontsize=10)
        ax6.set_title(f'投资构成 (总计{benefits["cost_total"]:.0f}万元)', 
                     fontsize=12, fontweight='bold')
        ax6.grid(True, alpha=0.3, axis='y')
        
        for bar, val in zip(bars, cost_values):
            height = bar.get_height()
            ax6.text(bar.get_x() + bar.get_width()/2., height,
                    f'{val:.0f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        # 7. 泥沙治理
        ax7 = plt.subplot(3, 3, 7)
        ax7.axis('off')
        
        ax7.text(0.5, 0.95, '泥沙治理', fontsize=11, ha='center', fontweight='bold')
        ax7.text(0.1, 0.80, f'年输沙量: {sediment["Q_sediment_year"]:.0f} 万t/年', fontsize=10, color='red')
        ax7.text(0.1, 0.68, f'治理目标: 减少{sediment["reduction_target"]:.0%}', fontsize=10)
        ax7.text(0.1, 0.58, f'目标输沙量: {sediment["Q_sediment_target"]:.0f} 万t/年', fontsize=10, color='green')
        
        ax7.text(0.1, 0.45, '治理措施:', fontsize=10, fontweight='bold')
        y_pos = 0.35
        for region, measure in sediment['measures'].items():
            ax7.text(0.15, y_pos, f'{region}: {measure}', fontsize=9)
            y_pos -= 0.10
        
        ax7.set_title('泥沙综合治理', fontsize=12, fontweight='bold')
        
        # 8. 效益-费用分析
        ax8 = plt.subplot(3, 3, 8)
        
        items_bc = ['年效益', '总投资', '20年总效益']
        values_bc = [benefits['benefit_total'], benefits['cost_total'], 
                    benefits['benefit_total']*20]
        colors_bc = ['green', 'red', 'blue']
        
        bars = ax8.barh(items_bc, values_bc, color=colors_bc, alpha=0.7, edgecolor='black')
        
        ax8.set_xlabel('金额 (万元)', fontsize=10)
        ax8.set_title(f'效益-费用分析 (B/C={benefits["bcr"]:.2f})', 
                     fontsize=12, fontweight='bold')
        ax8.grid(True, alpha=0.3, axis='x')
        
        for bar, val in zip(bars, values_bc):
            width = bar.get_width()
            ax8.text(width, bar.get_y() + bar.get_height()/2,
                    f'{val:.0f}', ha='left', va='center', fontsize=9, fontweight='bold')
        
        # 9. 结果汇总表
        ax9 = plt.subplot(3, 3, 9)
        ax9.axis('off')
        
        table_data = [
            ['项目', '数值', '单位/评价'],
            ['设计河宽', f'{channel["B"]:.1f}', 'm'],
            ['防洪标准', f'{discharge_design["return_period"]}', '年'],
            ['安全系数', f'{flood["safety_factor"]:.2f}', flood['is_safe'] and '✓满足' or '✗不足'],
            ['年效益', f'{benefits["benefit_total"]}', '万元'],
            ['总投资', f'{benefits["cost_total"]:.0f}', '万元'],
            ['效益费用比', f'{benefits["bcr"]:.2f}', benefits["bcr"]>1 and '✓可行' or '✗不可行'],
            ['植被覆盖率', f'{revetment["vegetation_coverage"]:.0%}', '生态良好']
        ]
        
        table = ax9.table(cellText=table_data, cellLoc='center', loc='center',
                         colWidths=[0.40, 0.30, 0.28])
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
        
        ax9.set_title('综合评价', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('/tmp/ch12_problem13_comprehensive.png', dpi=150, bbox_inches='tight')
        print(f"图表已保存: /tmp/ch12_problem13_comprehensive.png")
        plt.show()
    
    def print_results(self):
        """打印结果"""
        print("\n" + "="*70)
        print("第12章 河流动力学 - 题13：河流综合治理方案")
        print("="*70)
        
        discharge_design = self.design_discharge()
        channel = self.channel_design()
        flood = self.flood_capacity()
        revetment = self.ecological_revetment()
        sediment = self.sediment_management()
        benefits = self.comprehensive_benefits()
        
        print(f"\n【工程概况】")
        print(f"河段长度: L = {self.L/1000} km")
        print(f"多年平均流量: Q = {self.Q} m³/s")
        print(f"设计洪峰流量: Qp = {self.Qp} m³/s")
        print(f"防洪标准: {discharge_design['return_period']}年一遇")
        
        print(f"\n【河道断面设计】")
        print(f"设计河宽: B = {channel['B']:.2f} m")
        print(f"正常水深: h = {channel['h']:.2f} m")
        print(f"洪水水深: h_flood = {channel['h_flood']:.2f} m")
        print(f"边坡系数: m = {channel['m']} (1:{channel['m']})")
        print(f"超高: {channel['freeboard']} m")
        print(f"堤顶高程: H = {channel['H_dike']:.2f} m")
        
        print(f"\n【防洪能力】")
        print(f"过流能力: Q_capacity = {flood['Q_capacity']:.2f} m³/s")
        print(f"设计洪峰: Qp = {self.Qp} m³/s")
        print(f"安全系数: K = Q_capacity/Qp = {flood['safety_factor']:.3f}")
        if flood['is_safe']:
            print(f"✓ K = {flood['safety_factor']:.3f} ≥ 1.2，满足防洪要求")
        else:
            print(f"✗ K = {flood['safety_factor']:.3f} < 1.2，不满足防洪要求")
        
        print(f"\n【生态护岸】")
        print(f"护岸类型:")
        for region, rtype in revetment['types'].items():
            print(f"  {region}: {rtype}")
        print(f"边坡长度: {revetment['slope_length']:.2f} m")
        print(f"护岸面积: {revetment['area_revetment']/10000:.2f} 万m²")
        print(f"植被覆盖率目标: {revetment['vegetation_coverage']:.0%}")
        
        print(f"\n【泥沙治理】")
        print(f"现状年输沙量: {sediment['Q_sediment_year']:.2f} 万t/年")
        print(f"治理目标: 减少{sediment['reduction_target']:.0%}")
        print(f"目标年输沙量: {sediment['Q_sediment_target']:.2f} 万t/年")
        print(f"治理措施:")
        for region, measure in sediment['measures'].items():
            print(f"  {region}: {measure}")
        
        print(f"\n【综合效益】（年效益，万元/年）")
        print(f"防洪效益: {benefits['benefit_flood']} 万元/年")
        print(f"生态效益: {benefits['benefit_ecology']} 万元/年")
        print(f"航运效益: {benefits['benefit_navigation']} 万元/年")
        print(f"景观效益: {benefits['benefit_landscape']} 万元/年")
        print(f"总效益: {benefits['benefit_total']} 万元/年")
        
        print(f"\n【工程投资】（万元）")
        print(f"清淤疏浚: {benefits['cost_dredging']:.2f} 万元")
        print(f"护岸工程: {benefits['cost_revetment']:.2f} 万元")
        print(f"植被绿化: {benefits['cost_vegetation']:.2f} 万元")
        print(f"总投资: {benefits['cost_total']:.2f} 万元")
        
        print(f"\n【经济评价】")
        print(f"效益费用比: B/C = {benefits['bcr']:.3f}")
        if benefits['bcr'] > 1.0:
            print(f"✓ B/C = {benefits['bcr']:.3f} > 1.0，工程经济可行")
        else:
            print(f"✗ B/C = {benefits['bcr']:.3f} < 1.0，工程经济不可行")
        
        payback_period = benefits['cost_total'] / benefits['benefit_total']
        print(f"静态投资回收期: {payback_period:.2f} 年")
        
        print(f"\n✓ 河流综合治理方案设计完成")
        print(f"\n{'='*70}\n")


def main():
    L = 5  # km
    Q = 1000
    Qp = 3000
    B = 150
    i = 0.0003
    d50 = 0.25
    S = 4
    
    river = ComprehensiveRiverManagement(L, Q, Qp, B, i, d50, S)
    river.print_results()
    river.plot_analysis()


if __name__ == "__main__":
    main()
