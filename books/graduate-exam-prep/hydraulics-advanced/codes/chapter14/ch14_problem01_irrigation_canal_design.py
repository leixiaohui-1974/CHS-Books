# -*- coding: utf-8 -*-
"""
第14章 压轴大题专项训练 - 题1：灌区渠系综合设计

问题描述：
    某灌区需设计三级渠系：干渠、支渠、斗渠
    灌溉面积A = 5000亩（1亩=666.7m²）
    灌溉定额m = 400 m³/亩
    灌溉周期T = 10天
    综合利用系数η = 0.6
    
    地形数据：
    干渠：起点z0=100m，末端z1=85m，长度L1=8km
    支渠：平均坡降J2=0.0004，长度L2=3km
    斗渠：平均坡降J3=0.0005，平均长度L3=500m
    
    求：
    1. 灌区设计流量Q_设
    2. 干渠断面设计（梯形，b:h=2:1，m=1.5，n=0.025）
    3. 正常水深h0和临界坡度Jc
    4. 流态判断和水面线类型
    5. 支渠和斗渠断面参数
    6. 工程总投资估算
    7. 经济分析（成本效益，投资回收期）

核心公式：
    1. Q_设 = W/(T×86400×η)
    2. A = (b + mh)h，P = b + 2h√(1+m²)
    3. Q = A×R^(2/3)×J^(1/2)/n（曼宁公式）
    4. hc = (q²/g)^(1/3)（临界水深）
    5. Jc = n²q²/(R^(4/3))（临界坡度）

考试要点：
    - 灌溉流量计算
    - 明渠水力设计
    - 渠系工程布置
    - 经济分析评价

作者: CHS-Books Team
日期: 2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, Dict, List
from scipy.optimize import fsolve

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class IrrigationCanalDesign:
    """灌区渠系综合设计"""
    
    def __init__(self, A_acre: float, m_quota: float, T_days: float,
                 eta: float, z0: float, z1: float, L1: float):
        self.A_acre = A_acre  # 灌溉面积 亩
        self.m_quota = m_quota  # 灌溉定额 m³/亩
        self.T_days = T_days  # 灌溉周期 天
        self.eta = eta  # 综合利用系数
        self.z0 = z0  # 干渠起点高程 m
        self.z1 = z1  # 干渠末端高程 m
        self.L1 = L1  # 干渠长度 km
        
    def design_flow(self) -> Dict:
        """计算设计流量"""
        # 总灌溉水量（m³）
        W = self.A_acre * self.m_quota
        
        # 净灌溉流量（m³/s）
        Q_net = W / (self.T_days * 86400)
        
        # 设计流量（考虑损失）
        Q_design = Q_net / self.eta
        
        # 取整到0.5
        Q_design_rounded = np.ceil(Q_design * 2) / 2
        
        return {
            'W': W,
            'Q_net': Q_net,
            'Q_design': Q_design,
            'Q_design_rounded': Q_design_rounded
        }
    
    def main_canal_section(self, Q: float, m_slope: float = 1.5, 
                           n: float = 0.025, bh_ratio: float = 2.0) -> Dict:
        """干渠断面设计"""
        # 地形坡度
        J = (self.z0 - self.z1) / (self.L1 * 1000)
        
        # 假设水深，通过迭代求解
        def equations(h):
            b = bh_ratio * h
            A = (b + m_slope * h) * h
            P = b + 2 * h * np.sqrt(1 + m_slope**2)
            R = A / P if P > 0 else 0
            Q_calc = A * R**(2/3) * J**(1/2) / n
            return Q_calc - Q
        
        # 初始猜测
        h0_guess = 1.0
        h0 = fsolve(equations, h0_guess)[0]
        
        b0 = bh_ratio * h0
        A0 = (b0 + m_slope * h0) * h0
        P0 = b0 + 2 * h0 * np.sqrt(1 + m_slope**2)
        R0 = A0 / P0
        v0 = Q / A0
        
        return {
            'J': J,
            'h0': h0,
            'b0': b0,
            'A0': A0,
            'P0': P0,
            'R0': R0,
            'v0': v0
        }
    
    def critical_parameters(self, Q: float, b: float, m_slope: float = 1.5) -> Dict:
        """临界参数计算"""
        # 单宽流量
        q = Q / b if b > 0 else Q
        
        # 临界水深（简化计算）
        hc = (q**2 / 9.81)**(1/3)
        
        # 临界流速
        vc = np.sqrt(9.81 * hc)
        
        # 临界坡度（曼宁公式）
        Ac = (b + m_slope * hc) * hc
        Pc = b + 2 * hc * np.sqrt(1 + m_slope**2)
        Rc = Ac / Pc if Pc > 0 else 0
        
        n = 0.025
        Jc = n**2 * Q**2 / (Ac**2 * Rc**(4/3)) if Rc > 0 else 0
        
        return {
            'q': q,
            'hc': hc,
            'vc': vc,
            'Ac': Ac,
            'Rc': Rc,
            'Jc': Jc
        }
    
    def flow_regime_analysis(self, h0: float, hc: float, J: float, Jc: float) -> Dict:
        """流态分析"""
        # 判断流态
        if J > Jc:
            regime = "急流"
            slope_type = "陡坡"
            profile_type = "S型水面线"
        elif J < Jc:
            regime = "缓流"
            slope_type = "缓坡"
            profile_type = "M型水面线"
        else:
            regime = "临界流"
            slope_type = "临界坡"
            profile_type = "临界流"
        
        # Fr数
        v = self.main_canal_section(self.design_flow()['Q_design_rounded'])['v0']
        Fr = v / np.sqrt(9.81 * h0) if h0 > 0 else 0
        
        return {
            'regime': regime,
            'slope_type': slope_type,
            'profile_type': profile_type,
            'Fr': Fr
        }
    
    def branch_canal_design(self, Q_main: float, n_branches: int = 3) -> List[Dict]:
        """支渠设计"""
        branches = []
        
        Q_branch = Q_main / n_branches
        J2 = 0.0004
        L2 = 3000  # m
        
        for i in range(n_branches):
            # 支渠断面（缩小）
            m_slope = 1.5
            n = 0.025
            bh_ratio = 2.0
            
            def equations(h):
                b = bh_ratio * h
                A = (b + m_slope * h) * h
                P = b + 2 * h * np.sqrt(1 + m_slope**2)
                R = A / P if P > 0 else 0
                Q_calc = A * R**(2/3) * J2**(1/2) / n
                return Q_calc - Q_branch
            
            h_branch = fsolve(equations, 0.5)[0]
            b_branch = bh_ratio * h_branch
            A_branch = (b_branch + m_slope * h_branch) * h_branch
            v_branch = Q_branch / A_branch if A_branch > 0 else 0
            
            branches.append({
                'id': i + 1,
                'Q': Q_branch,
                'h': h_branch,
                'b': b_branch,
                'A': A_branch,
                'v': v_branch,
                'L': L2
            })
        
        return branches
    
    def lateral_canal_design(self, Q_branch: float, n_laterals: int = 5) -> List[Dict]:
        """斗渠设计"""
        laterals = []
        
        Q_lateral = Q_branch / n_laterals
        J3 = 0.0005
        L3 = 500  # m
        
        for i in range(n_laterals):
            # 斗渠断面（更小）
            m_slope = 1.0
            n = 0.020
            bh_ratio = 1.5
            
            def equations(h):
                b = bh_ratio * h
                A = (b + m_slope * h) * h
                P = b + 2 * h * np.sqrt(1 + m_slope**2)
                R = A / P if P > 0 else 0
                Q_calc = A * R**(2/3) * J3**(1/2) / n
                return Q_calc - Q_lateral
            
            h_lateral = fsolve(equations, 0.3)[0]
            b_lateral = bh_ratio * h_lateral
            A_lateral = (b_lateral + m_slope * h_lateral) * h_lateral
            v_lateral = Q_lateral / A_lateral if A_lateral > 0 else 0
            
            laterals.append({
                'id': i + 1,
                'Q': Q_lateral,
                'h': h_lateral,
                'b': b_lateral,
                'A': A_lateral,
                'v': v_lateral,
                'L': L3
            })
        
        return laterals
    
    def cost_estimation(self, main_section: Dict, branches: List[Dict], 
                       laterals: List[Dict]) -> Dict:
        """工程投资估算"""
        # 干渠工程量
        main_excavation = main_section['A0'] * self.L1 * 1000  # m³
        main_lining_area = (main_section['b0'] + 2 * main_section['h0'] * 
                           np.sqrt(1 + 1.5**2)) * self.L1 * 1000  # m²
        
        # 支渠工程量
        branch_excavation = sum([b['A'] * b['L'] for b in branches])
        branch_lining_area = sum([(b['b'] + 2 * b['h'] * np.sqrt(1 + 1.5**2)) * 
                                  b['L'] for b in branches])
        
        # 斗渠工程量
        lateral_excavation = sum([l['A'] * l['L'] for l in laterals]) * len(branches)
        lateral_lining_area = sum([(l['b'] + 2 * l['h'] * np.sqrt(1 + 1.0**2)) * 
                                   l['L'] for l in laterals]) * len(branches)
        
        # 单价（元）
        excavation_price = 15  # 元/m³
        lining_price = 80  # 元/m²
        structure_price = 500000  # 元/座（建筑物）
        
        # 总造价
        excavation_cost = (main_excavation + branch_excavation + 
                          lateral_excavation) * excavation_price
        lining_cost = (main_lining_area + branch_lining_area + 
                      lateral_lining_area) * lining_price
        structure_cost = structure_price * (1 + len(branches) + 
                                           len(branches) * len(laterals))
        
        total_cost = excavation_cost + lining_cost + structure_cost
        
        return {
            'excavation': {
                'main': main_excavation,
                'branch': branch_excavation,
                'lateral': lateral_excavation,
                'total': main_excavation + branch_excavation + lateral_excavation
            },
            'lining': {
                'main': main_lining_area,
                'branch': branch_lining_area,
                'lateral': lateral_lining_area,
                'total': main_lining_area + branch_lining_area + lateral_lining_area
            },
            'cost': {
                'excavation': excavation_cost,
                'lining': lining_cost,
                'structure': structure_cost,
                'total': total_cost
            }
        }
    
    def economic_analysis(self, total_cost: float) -> Dict:
        """经济分析"""
        # 效益估算
        area_m2 = self.A_acre * 666.7
        area_hectare = area_m2 / 10000
        
        # 年增产效益（元/年）
        yield_increase = 300  # kg/亩
        price = 2.5  # 元/kg
        annual_benefit = self.A_acre * yield_increase * price
        
        # 年运行成本（总投资的3%）
        annual_cost = total_cost * 0.03
        
        # 年净效益
        net_benefit = annual_benefit - annual_cost
        
        # 投资回收期
        payback_period = total_cost / net_benefit if net_benefit > 0 else np.inf
        
        # NPV（20年，折现率8%）
        discount_rate = 0.08
        years = 20
        NPV = sum([net_benefit / (1 + discount_rate)**t for t in range(1, years+1)]) - total_cost
        
        # IRR（内部收益率，简化估算）
        IRR = net_benefit / total_cost * 100
        
        # B/C比
        BC_ratio = annual_benefit / (annual_cost + total_cost / years) if annual_cost > 0 else 0
        
        return {
            'annual_benefit': annual_benefit,
            'annual_cost': annual_cost,
            'net_benefit': net_benefit,
            'payback_period': payback_period,
            'NPV': NPV,
            'IRR': IRR,
            'BC_ratio': BC_ratio
        }
    
    def plot_analysis(self):
        """绘制分析图表"""
        fig = plt.figure(figsize=(16, 12))
        
        flow = self.design_flow()
        Q_design = flow['Q_design_rounded']
        main_section = self.main_canal_section(Q_design)
        critical = self.critical_parameters(Q_design, main_section['b0'])
        regime = self.flow_regime_analysis(main_section['h0'], critical['hc'],
                                          main_section['J'], critical['Jc'])
        branches = self.branch_canal_design(Q_design)
        laterals = self.lateral_canal_design(branches[0]['Q'])
        cost = self.cost_estimation(main_section, branches, laterals)
        economic = self.economic_analysis(cost['cost']['total'])
        
        # 1. 渠系布置示意图
        ax1 = plt.subplot(3, 3, 1)
        ax1.axis('off')
        
        ax1.text(0.5, 0.95, '渠系布置示意图', fontsize=11, ha='center', fontweight='bold')
        
        # 干渠
        ax1.plot([0.1, 0.9], [0.7, 0.7], 'b-', linewidth=4, label='干渠')
        ax1.text(0.5, 0.75, f'Q={Q_design:.1f}m³/s', ha='center', fontsize=9)
        
        # 支渠
        y_branches = [0.6, 0.5, 0.4]
        for i, yb in enumerate(y_branches):
            ax1.plot([0.5, 0.5], [0.7, yb], 'g--', linewidth=2)
            ax1.plot([0.5, 0.8], [yb, yb], 'g-', linewidth=3)
            ax1.text(0.65, yb+0.02, f'支{i+1}', ha='center', fontsize=8)
        
        # 斗渠（示意）
        for yb in y_branches[:2]:
            for i in range(3):
                xl = 0.8 + i * 0.02
                ax1.plot([0.8, xl], [yb, yb-0.05], 'orange', linewidth=1)
        
        ax1.text(0.5, 0.15, f'灌溉面积: {self.A_acre}亩', ha='center', fontsize=9)
        ax1.legend(loc='lower left')
        ax1.set_title('渠系总体布置', fontsize=12, fontweight='bold')
        
        # 2. 设计流量计算
        ax2 = plt.subplot(3, 3, 2)
        ax2.axis('off')
        
        ax2.text(0.5, 0.95, '设计流量计算', fontsize=11, ha='center', fontweight='bold')
        ax2.text(0.1, 0.82, f'灌溉面积: {self.A_acre} 亩', fontsize=10)
        ax2.text(0.1, 0.74, f'灌溉定额: {self.m_quota} m³/亩', fontsize=10)
        ax2.text(0.1, 0.66, f'灌溉周期: {self.T_days} 天', fontsize=10)
        ax2.text(0.1, 0.58, f'利用系数: {self.eta}', fontsize=10)
        
        ax2.text(0.1, 0.45, f'总水量: W = {flow["W"]/1e6:.2f} 万m³', fontsize=10, color='blue')
        ax2.text(0.1, 0.35, f'净流量: Q_净 = {flow["Q_net"]:.3f} m³/s', fontsize=10)
        ax2.text(0.1, 0.25, f'设计流量: Q_设 = {Q_design:.2f} m³/s', 
                fontsize=11, color='red', fontweight='bold')
        
        ax2.text(0.1, 0.10, '公式: Q = W/(T×86400×η)', fontsize=9, style='italic')
        ax2.set_title('流量设计', fontsize=12, fontweight='bold')
        
        # 3. 干渠断面参数
        ax3 = plt.subplot(3, 3, 3)
        
        # 绘制梯形断面
        h = main_section['h0']
        b = main_section['b0']
        m = 1.5
        
        x = np.array([0, b, b+m*h, m*h, 0])
        y = np.array([0, 0, h, h, 0])
        
        ax3.fill(x, y, alpha=0.3, color='blue', label='过水断面')
        ax3.plot(x, y, 'b-', linewidth=2)
        
        # 标注
        ax3.plot([0, b], [h, h], 'r--', linewidth=1)
        ax3.text(b/2, h+0.1, f'b={b:.2f}m', ha='center', fontsize=9)
        ax3.plot([b, b], [0, h], 'r--', linewidth=1)
        ax3.text(b+0.2, h/2, f'h={h:.2f}m', fontsize=9)
        ax3.text(b+m*h/2, h/2, f'm=1:{m}', fontsize=9, style='italic')
        
        ax3.set_xlabel('宽度 (m)', fontsize=10)
        ax3.set_ylabel('水深 (m)', fontsize=10)
        ax3.set_title(f'干渠断面设计\nA={main_section["A0"]:.2f}m²', 
                     fontsize=12, fontweight='bold')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        ax3.set_aspect('equal')
        
        # 4. 水力参数对比
        ax4 = plt.subplot(3, 3, 4)
        
        params = ['水深\n(m)', '流速\n(m/s)', 'Fr数']
        normal = [main_section['h0'], main_section['v0'], regime['Fr']]
        critical_vals = [critical['hc'], critical['vc'], 1.0]
        
        x = np.arange(len(params))
        width = 0.35
        
        bars1 = ax4.bar(x - width/2, normal, width, label='正常', 
                       color='blue', alpha=0.7, edgecolor='black')
        bars2 = ax4.bar(x + width/2, critical_vals, width, label='临界',
                       color='red', alpha=0.7, edgecolor='black')
        
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax4.text(bar.get_x() + bar.get_width()/2, height,
                        f'{height:.3f}', ha='center', va='bottom', fontsize=8)
        
        ax4.set_ylabel('数值', fontsize=10)
        ax4.set_title('水力参数对比', fontsize=12, fontweight='bold')
        ax4.set_xticks(x)
        ax4.set_xticklabels(params)
        ax4.legend()
        ax4.grid(True, alpha=0.3, axis='y')
        
        # 5. 流态判断
        ax5 = plt.subplot(3, 3, 5)
        ax5.axis('off')
        
        ax5.text(0.5, 0.95, '流态分析', fontsize=11, ha='center', fontweight='bold')
        
        ax5.text(0.1, 0.80, f'实际坡度: J = {main_section["J"]:.6f}', fontsize=10)
        ax5.text(0.1, 0.70, f'临界坡度: Jc = {critical["Jc"]:.6f}', fontsize=10)
        
        color = 'blue' if regime['regime'] == '缓流' else 'red'
        ax5.text(0.1, 0.55, f'流态: {regime["regime"]}', fontsize=12,
                color=color, fontweight='bold')
        ax5.text(0.1, 0.45, f'坡度类型: {regime["slope_type"]}', fontsize=10)
        ax5.text(0.1, 0.35, f'水面线: {regime["profile_type"]}', fontsize=10)
        ax5.text(0.1, 0.25, f'Fr = {regime["Fr"]:.3f}', fontsize=10)
        
        if regime['Fr'] < 1:
            ax5.text(0.1, 0.12, '✓ 缓流，水面线为M型', fontsize=9, color='green')
        else:
            ax5.text(0.1, 0.12, '! 急流，需要消能', fontsize=9, color='red')
        
        ax5.set_title('流态判别', fontsize=12, fontweight='bold')
        
        # 6. 各级渠道流量分配
        ax6 = plt.subplot(3, 3, 6)
        
        canal_types = ['干渠', '支渠', '斗渠']
        flows = [Q_design, branches[0]['Q'], laterals[0]['Q']]
        colors_flow = ['blue', 'green', 'orange']
        
        bars = ax6.bar(canal_types, flows, color=colors_flow, 
                      alpha=0.7, edgecolor='black')
        
        for bar, val in zip(bars, flows):
            height = bar.get_height()
            ax6.text(bar.get_x() + bar.get_width()/2, height,
                    f'{val:.3f}', ha='center', va='bottom',
                    fontsize=9, fontweight='bold')
        
        ax6.set_ylabel('流量 (m³/s)', fontsize=10)
        ax6.set_title('各级渠道流量分配', fontsize=12, fontweight='bold')
        ax6.grid(True, alpha=0.3, axis='y')
        ax6.set_yscale('log')
        
        # 7. 工程投资结构
        ax7 = plt.subplot(3, 3, 7)
        
        cost_types = ['土方开挖', '渠道衬砌', '建筑物']
        cost_values = [cost['cost']['excavation'], cost['cost']['lining'],
                      cost['cost']['structure']]
        colors_cost = ['#8B4513', '#87CEEB', '#FFD700']
        
        wedges, texts, autotexts = ax7.pie(cost_values, labels=cost_types,
                                           autopct='%1.1f%%', colors=colors_cost,
                                           startangle=90)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(9)
            autotext.set_fontweight('bold')
        
        ax7.set_title(f'投资结构\n(总投资{cost["cost"]["total"]/1e6:.2f}百万元)',
                     fontsize=12, fontweight='bold')
        
        # 8. 经济效益分析
        ax8 = plt.subplot(3, 3, 8)
        
        benefit_items = ['年收益', '年成本', '净效益']
        benefit_values = [economic['annual_benefit']/1e6,
                         economic['annual_cost']/1e6,
                         economic['net_benefit']/1e6]
        colors_benefit = ['green', 'red', 'blue']
        
        bars = ax8.barh(benefit_items, benefit_values, color=colors_benefit,
                       alpha=0.7, edgecolor='black')
        ax8.axvline(0, color='k', linewidth=1)
        
        for bar, val in zip(bars, benefit_values):
            width = bar.get_width()
            ax8.text(width, bar.get_y() + bar.get_height()/2,
                    f'{val:.2f}', ha='left' if width>0 else 'right',
                    va='center', fontsize=9, fontweight='bold')
        
        ax8.set_xlabel('金额 (百万元)', fontsize=10)
        ax8.set_title(f'经济效益分析\n(回收期{economic["payback_period"]:.1f}年)',
                     fontsize=12, fontweight='bold')
        ax8.grid(True, alpha=0.3, axis='x')
        
        # 9. 综合评价表
        ax9 = plt.subplot(3, 3, 9)
        ax9.axis('off')
        
        table_data = [
            ['项目', '数值', '单位'],
            ['设计流量', f'{Q_design:.2f}', 'm³/s'],
            ['干渠水深', f'{main_section["h0"]:.2f}', 'm'],
            ['干渠底宽', f'{main_section["b0"]:.2f}', 'm'],
            ['流态', regime['regime'], '-'],
            ['总投资', f'{cost["cost"]["total"]/1e6:.2f}', '百万元'],
            ['年净效益', f'{economic["net_benefit"]/1e6:.2f}', '百万元'],
            ['投资回收期', f'{economic["payback_period"]:.1f}', '年'],
            ['B/C比', f'{economic["BC_ratio"]:.2f}', '-'],
            ['NPV', f'{economic["NPV"]/1e6:.2f}', '百万元']
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
        for i in [1, 6, 8]:
            for j in range(3):
                table[(i, j)].set_facecolor('#FFF9E6')
        
        ax9.set_title('综合评价汇总', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('/tmp/ch14_problem01_irrigation_canal_design.png', dpi=150, bbox_inches='tight')
        print(f"图表已保存: /tmp/ch14_problem01_irrigation_canal_design.png")
        plt.show()
    
    def print_results(self):
        """打印结果"""
        print("\n" + "="*70)
        print("第14章 压轴大题 - 题1：灌区渠系综合设计")
        print("="*70)
        
        flow = self.design_flow()
        Q_design = flow['Q_design_rounded']
        main_section = self.main_canal_section(Q_design)
        critical = self.critical_parameters(Q_design, main_section['b0'])
        regime = self.flow_regime_analysis(main_section['h0'], critical['hc'],
                                          main_section['J'], critical['Jc'])
        branches = self.branch_canal_design(Q_design)
        laterals = self.lateral_canal_design(branches[0]['Q'])
        cost = self.cost_estimation(main_section, branches, laterals)
        economic = self.economic_analysis(cost['cost']['total'])
        
        print(f"\n【1. 设计流量计算】")
        print(f"灌溉面积: A = {self.A_acre} 亩")
        print(f"灌溉定额: m = {self.m_quota} m³/亩")
        print(f"灌溉周期: T = {self.T_days} 天")
        print(f"利用系数: η = {self.eta}")
        print(f"")
        print(f"总灌溉水量: W = {flow['W']/1e6:.3f} 万m³")
        print(f"净灌溉流量: Q_净 = {flow['Q_net']:.4f} m³/s")
        print(f"设计流量: Q_设 = {Q_design:.2f} m³/s ✓")
        
        print(f"\n【2. 干渠断面设计】")
        print(f"地形坡度: J = {main_section['J']:.6f}")
        print(f"梯形断面: b:h = 2:1, m = 1.5")
        print(f"糙率: n = 0.025")
        print(f"")
        print(f"正常水深: h₀ = {main_section['h0']:.3f} m")
        print(f"底宽: b = {main_section['b0']:.3f} m")
        print(f"过水断面积: A = {main_section['A0']:.3f} m²")
        print(f"湿周: P = {main_section['P0']:.3f} m")
        print(f"水力半径: R = {main_section['R0']:.3f} m")
        print(f"平均流速: v = {main_section['v0']:.3f} m/s")
        
        print(f"\n【3. 临界参数】")
        print(f"单宽流量: q = {critical['q']:.3f} m²/s")
        print(f"临界水深: hc = {critical['hc']:.3f} m")
        print(f"临界流速: vc = {critical['vc']:.3f} m/s")
        print(f"临界坡度: Jc = {critical['Jc']:.6f}")
        
        print(f"\n【4. 流态判断】")
        print(f"实际坡度 J = {main_section['J']:.6f}")
        print(f"临界坡度 Jc = {critical['Jc']:.6f}")
        print(f"Fr数 = {regime['Fr']:.3f}")
        print(f"")
        print(f"流态: {regime['regime']}")
        print(f"坡度类型: {regime['slope_type']}")
        print(f"水面线类型: {regime['profile_type']}")
        
        print(f"\n【5. 支渠和斗渠设计】")
        print(f"支渠数量: {len(branches)} 条")
        print(f"单条支渠流量: {branches[0]['Q']:.3f} m³/s")
        print(f"支渠水深: {branches[0]['h']:.3f} m")
        print(f"支渠底宽: {branches[0]['b']:.3f} m")
        print(f"")
        print(f"每条支渠斗渠数: {len(laterals)} 条")
        print(f"单条斗渠流量: {laterals[0]['Q']:.4f} m³/s")
        print(f"斗渠水深: {laterals[0]['h']:.3f} m")
        print(f"斗渠底宽: {laterals[0]['b']:.3f} m")
        
        print(f"\n【6. 工程投资估算】")
        print(f"土方开挖: {cost['excavation']['total']:.0f} m³ → {cost['cost']['excavation']/1e6:.2f} 百万元")
        print(f"渠道衬砌: {cost['lining']['total']:.0f} m² → {cost['cost']['lining']/1e6:.2f} 百万元")
        print(f"建筑物: {cost['cost']['structure']/1e6:.2f} 百万元")
        print(f"总投资: {cost['cost']['total']/1e6:.2f} 百万元")
        
        print(f"\n【7. 经济分析】")
        print(f"年收益: {economic['annual_benefit']/1e6:.2f} 百万元")
        print(f"年成本: {economic['annual_cost']/1e6:.2f} 百万元")
        print(f"年净效益: {economic['net_benefit']/1e6:.2f} 百万元")
        print(f"投资回收期: {economic['payback_period']:.1f} 年")
        print(f"NPV(20年): {economic['NPV']/1e6:.2f} 百万元")
        print(f"B/C比: {economic['BC_ratio']:.2f}")
        
        if economic['BC_ratio'] > 1.0 and economic['payback_period'] < 15:
            print(f"✓ 项目经济可行")
        else:
            print(f"△ 需进一步优化")
        
        print(f"\n✓ 灌区渠系综合设计完成")
        print(f"\n{'='*70}\n")


def main():
    A_acre = 5000  # 亩
    m_quota = 400  # m³/亩
    T_days = 10
    eta = 0.6
    z0 = 100  # m
    z1 = 85   # m
    L1 = 8    # km
    
    irrigation = IrrigationCanalDesign(A_acre, m_quota, T_days, eta, z0, z1, L1)
    irrigation.print_results()
    irrigation.plot_analysis()


if __name__ == "__main__":
    main()
