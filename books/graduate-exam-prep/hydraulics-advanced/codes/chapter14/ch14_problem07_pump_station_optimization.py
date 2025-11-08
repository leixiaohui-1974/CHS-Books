# -*- coding: utf-8 -*-
"""
第14章 压轴大题专项训练 - 题7：泵站系统优化设计

问题描述：
    某泵站设计流量Q = 15 m³/s，扬程H = 12m
    可选泵型：
    - A型：Q=5m³/s, H=15m, η=82%, P=100kW, 价格50万元
    - B型：Q=7.5m³/s, H=13m, η=85%, P=135kW, 价格65万元
    - C型：Q=10m³/s, H=12m, η=88%, P=160kW, 价格75万元
    
    运行工况：
    - 全年运行8000小时
    - 电价：白天0.8元/kW·h（50%），夜间0.4元/kW·h（50%）
    - 维护成本：设备投资的3%/年
    
    求：
    1. 各种配置方案（单台、并联、混合）
    2. 运行特性分析（Q-H曲线，效率）
    3. 经济性比较（投资、运行成本、总成本）
    4. 优化方案选择（最小年费用法）
    5. 调节运行分析（变速、变角、变台）
    6. 综合评价与建议

核心公式：
    1. P = ρgQH/η
    2. 年费用 = (投资×折旧率) + 年运行费
    3. 并联：Q_总 = ΣQ_i, H = H_单台
    4. 串联：Q = Q_单台, H_总 = ΣH_i

考试要点：
    - 泵站配置方案
    - 运行特性分析
    - 经济优化设计
    - 综合比选

作者: CHS-Books Team
日期: 2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, Dict, List

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class PumpStationOptimization:
    """泵站系统优化设计"""
    
    def __init__(self, Q_design: float, H_design: float, hours_per_year: float):
        self.Q_design = Q_design  # 设计流量 m³/s
        self.H_design = H_design  # 设计扬程 m
        self.hours_per_year = hours_per_year  # 年运行小时
        
        # 泵型参数
        self.pump_types = {
            'A': {'Q': 5.0, 'H': 15.0, 'eta': 0.82, 'P': 100, 'price': 50},
            'B': {'Q': 7.5, 'H': 13.0, 'eta': 0.85, 'P': 135, 'price': 65},
            'C': {'Q': 10.0, 'H': 12.0, 'eta': 0.88, 'P': 160, 'price': 75}
        }
        
        # 电价
        self.price_day = 0.8  # 元/kW·h
        self.price_night = 0.4
        self.price_avg = (self.price_day + self.price_night) / 2
        
        # 维护率
        self.maintenance_rate = 0.03
        
    def configuration_schemes(self) -> List[Dict]:
        """配置方案"""
        schemes = []
        
        # 方案1: 3台A型并联
        schemes.append({
            'id': 1,
            'type': 'A',
            'num': 3,
            'mode': '并联',
            'Q_total': 3 * self.pump_types['A']['Q'],
            'H_total': self.pump_types['A']['H'],
            'P_total': 3 * self.pump_types['A']['P'],
            'eta_avg': self.pump_types['A']['eta'],
            'investment': 3 * self.pump_types['A']['price']
        })
        
        # 方案2: 2台B型并联
        schemes.append({
            'id': 2,
            'type': 'B',
            'num': 2,
            'mode': '并联',
            'Q_total': 2 * self.pump_types['B']['Q'],
            'H_total': self.pump_types['B']['H'],
            'P_total': 2 * self.pump_types['B']['P'],
            'eta_avg': self.pump_types['B']['eta'],
            'investment': 2 * self.pump_types['B']['price']
        })
        
        # 方案3: 1台C+1台A
        schemes.append({
            'id': 3,
            'type': 'C+A',
            'num': 2,
            'mode': '混合并联',
            'Q_total': self.pump_types['C']['Q'] + self.pump_types['A']['Q'],
            'H_total': min(self.pump_types['C']['H'], self.pump_types['A']['H']),
            'P_total': self.pump_types['C']['P'] + self.pump_types['A']['P'],
            'eta_avg': (self.pump_types['C']['eta'] + self.pump_types['A']['eta']) / 2,
            'investment': self.pump_types['C']['price'] + self.pump_types['A']['price']
        })
        
        # 方案4: 2台C并联
        schemes.append({
            'id': 4,
            'type': 'C',
            'num': 2,
            'mode': '并联',
            'Q_total': 2 * self.pump_types['C']['Q'],
            'H_total': self.pump_types['C']['H'],
            'P_total': 2 * self.pump_types['C']['P'],
            'eta_avg': self.pump_types['C']['eta'],
            'investment': 2 * self.pump_types['C']['price']
        })
        
        return schemes
    
    def operating_characteristics(self, scheme: Dict) -> Dict:
        """运行特性分析"""
        # Q-H特性曲线（简化为二次曲线）
        Q_rated = scheme['Q_total']
        H_rated = scheme['H_total']
        
        # H = H0 - a·Q²
        H0 = H_rated * 1.15
        a = (H0 - H_rated) / Q_rated**2
        
        Q_range = np.linspace(0, Q_rated * 1.3, 50)
        H_range = H0 - a * Q_range**2
        
        # 效率曲线（简化为抛物线）
        eta_max = scheme['eta_avg']
        Q_opt = Q_rated * 0.9
        
        eta_range = eta_max * (1 - ((Q_range - Q_opt) / Q_rated)**2)
        eta_range = np.maximum(eta_range, 0.3)
        
        # 功率曲线
        P_range = 9.81 * Q_range * H_range / (eta_range * 1000) * 1000  # kW
        
        return {
            'Q': Q_range,
            'H': H_range,
            'eta': eta_range,
            'P': P_range,
            'Q_design_idx': np.argmin(np.abs(Q_range - self.Q_design)),
            'H_design_idx': np.argmin(np.abs(H_range - self.H_design))
        }
    
    def economic_analysis(self, scheme: Dict) -> Dict:
        """经济分析"""
        # 投资
        investment = scheme['investment']
        
        # 年折旧（15年，残值5%）
        depreciation_years = 15
        salvage_rate = 0.05
        annual_depreciation = investment * (1 - salvage_rate) / depreciation_years
        
        # 年电费（实际功率）
        P_actual = 9.81 * self.Q_design * self.H_design / (scheme['eta_avg'] * 1000) * 1000  # kW
        annual_energy = P_actual * self.hours_per_year  # kW·h
        annual_electricity_cost = annual_energy * self.price_avg / 10000  # 万元
        
        # 年维护费
        annual_maintenance = investment * self.maintenance_rate
        
        # 年运行费
        annual_operating_cost = annual_electricity_cost + annual_maintenance
        
        # 年总费用
        annual_total_cost = annual_depreciation + annual_operating_cost
        
        # 单位水量成本
        annual_water_volume = self.Q_design * self.hours_per_year * 3600 / 1e4  # 万m³
        unit_cost = annual_total_cost / annual_water_volume  # 元/m³
        
        return {
            'investment': investment,
            'annual_depreciation': annual_depreciation,
            'annual_electricity': annual_electricity_cost,
            'annual_maintenance': annual_maintenance,
            'annual_operating': annual_operating_cost,
            'annual_total': annual_total_cost,
            'unit_cost': unit_cost
        }
    
    def optimization_selection(self, schemes: List[Dict]) -> Dict:
        """优化方案选择"""
        economics = []
        
        for scheme in schemes:
            econ = self.economic_analysis(scheme)
            economics.append({
                'scheme_id': scheme['id'],
                'annual_total': econ['annual_total'],
                'unit_cost': econ['unit_cost']
            })
        
        # 按年总费用排序
        economics_sorted = sorted(economics, key=lambda x: x['annual_total'])
        
        best_scheme_id = economics_sorted[0]['scheme_id']
        
        return {
            'economics': economics,
            'best_scheme_id': best_scheme_id
        }
    
    def regulation_analysis(self, scheme: Dict) -> Dict:
        """调节运行分析"""
        # 变速调节
        n_ratios = np.array([0.7, 0.8, 0.9, 1.0, 1.1])
        Q_variable_speed = scheme['Q_total'] * n_ratios
        H_variable_speed = scheme['H_total'] * n_ratios**2
        P_variable_speed = scheme['P_total'] * n_ratios**3 / 1000  # kW
        
        # 变台数调节（以方案1为例）
        if scheme['num'] >= 3:
            num_stages = np.array([1, 2, 3])
            Q_variable_num = scheme['Q_total'] / scheme['num'] * num_stages
            P_variable_num = scheme['P_total'] / scheme['num'] * num_stages / 1000
        else:
            num_stages = np.array([1, 2])
            Q_variable_num = scheme['Q_total'] / scheme['num'] * num_stages
            P_variable_num = scheme['P_total'] / scheme['num'] * num_stages / 1000
        
        return {
            'n_ratios': n_ratios,
            'Q_vs': Q_variable_speed,
            'H_vs': H_variable_speed,
            'P_vs': P_variable_speed,
            'num_stages': num_stages,
            'Q_vn': Q_variable_num,
            'P_vn': P_variable_num
        }
    
    def plot_analysis(self):
        """绘制分析图表"""
        fig = plt.figure(figsize=(16, 12))
        
        schemes = self.configuration_schemes()
        optimization = self.optimization_selection(schemes)
        best_scheme = schemes[optimization['best_scheme_id'] - 1]
        characteristics = self.operating_characteristics(best_scheme)
        regulation = self.regulation_analysis(best_scheme)
        
        # 1. 配置方案对比
        ax1 = plt.subplot(3, 3, 1)
        
        scheme_names = [f"方案{s['id']}\n{s['type']}" for s in schemes]
        Q_totals = [s['Q_total'] for s in schemes]
        
        bars = ax1.bar(scheme_names, Q_totals, alpha=0.7, edgecolor='black',
                      color=['blue', 'green', 'orange', 'red'])
        ax1.axhline(self.Q_design, color='r', linestyle='--', linewidth=2,
                   label=f'设计流量{self.Q_design}m³/s')
        
        for bar, val in zip(bars, Q_totals):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2, height,
                    f'{val:.1f}', ha='center', va='bottom',
                    fontsize=9, fontweight='bold')
        
        ax1.set_ylabel('总流量 (m³/s)', fontsize=10)
        ax1.set_title('各方案流量对比', fontsize=12, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3, axis='y')
        
        # 2. 泵型参数对比
        ax2 = plt.subplot(3, 3, 2)
        
        pump_names = list(self.pump_types.keys())
        Q_pumps = [self.pump_types[p]['Q'] for p in pump_names]
        H_pumps = [self.pump_types[p]['H'] for p in pump_names]
        eta_pumps = [self.pump_types[p]['eta'] * 100 for p in pump_names]
        
        x = np.arange(len(pump_names))
        width = 0.25
        
        ax2.bar(x - width, Q_pumps, width, label='流量(m³/s)', alpha=0.7, color='blue', edgecolor='black')
        ax2.bar(x, H_pumps, width, label='扬程(m)', alpha=0.7, color='green', edgecolor='black')
        ax2.bar(x + width, eta_pumps, width, label='效率(%)', alpha=0.7, color='orange', edgecolor='black')
        
        ax2.set_xlabel('泵型', fontsize=10)
        ax2.set_ylabel('数值', fontsize=10)
        ax2.set_title('泵型参数对比', fontsize=12, fontweight='bold')
        ax2.set_xticks(x)
        ax2.set_xticklabels(pump_names)
        ax2.legend()
        ax2.grid(True, alpha=0.3, axis='y')
        
        # 3. Q-H特性曲线（最优方案）
        ax3 = plt.subplot(3, 3, 3)
        
        ax3.plot(characteristics['Q'], characteristics['H'], 'b-', linewidth=2, label='H-Q曲线')
        ax3.plot(self.Q_design, self.H_design, 'ro', markersize=12, label='设计工况点')
        ax3.axhline(self.H_design, color='r', linestyle='--', linewidth=1, alpha=0.5)
        ax3.axvline(self.Q_design, color='r', linestyle='--', linewidth=1, alpha=0.5)
        
        ax3.set_xlabel('流量 Q (m³/s)', fontsize=10)
        ax3.set_ylabel('扬程 H (m)', fontsize=10)
        ax3.set_title(f'最优方案{best_scheme["id"]}特性曲线', fontsize=12, fontweight='bold')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. 效率曲线
        ax4 = plt.subplot(3, 3, 4)
        
        ax4.plot(characteristics['Q'], characteristics['eta'] * 100, 'g-', linewidth=2)
        ax4.plot(self.Q_design, best_scheme['eta_avg'] * 100, 'ro', markersize=12)
        ax4.axvline(self.Q_design, color='r', linestyle='--', linewidth=1, alpha=0.5)
        ax4.axhline(best_scheme['eta_avg'] * 100, color='g', linestyle='--', linewidth=1, alpha=0.5)
        
        ax4.set_xlabel('流量 Q (m³/s)', fontsize=10)
        ax4.set_ylabel('效率 η (%)', fontsize=10)
        ax4.set_title('泵站效率特性', fontsize=12, fontweight='bold')
        ax4.grid(True, alpha=0.3)
        
        # 5. 投资成本对比
        ax5 = plt.subplot(3, 3, 5)
        
        investments = [s['investment'] for s in schemes]
        
        bars = ax5.barh(scheme_names, investments, alpha=0.7, edgecolor='black',
                       color=['blue', 'green', 'orange', 'red'])
        
        for bar, val in zip(bars, investments):
            width = bar.get_width()
            ax5.text(width, bar.get_y() + bar.get_height()/2,
                    f'{val}万元', ha='left', va='center',
                    fontsize=9, fontweight='bold')
        
        ax5.set_xlabel('投资 (万元)', fontsize=10)
        ax5.set_title('初期投资对比', fontsize=12, fontweight='bold')
        ax5.grid(True, alpha=0.3, axis='x')
        
        # 6. 年费用对比
        ax6 = plt.subplot(3, 3, 6)
        
        annual_costs = []
        for s in schemes:
            econ = self.economic_analysis(s)
            annual_costs.append(econ['annual_total'])
        
        bars = ax6.bar(scheme_names, annual_costs, alpha=0.7, edgecolor='black',
                      color=['blue', 'green', 'orange', 'red'])
        
        # 标注最优
        min_idx = np.argmin(annual_costs)
        bars[min_idx].set_color('gold')
        bars[min_idx].set_edgecolor('red')
        bars[min_idx].set_linewidth(3)
        
        for bar, val in zip(bars, annual_costs):
            height = bar.get_height()
            ax6.text(bar.get_x() + bar.get_width()/2, height,
                    f'{val:.1f}', ha='center', va='bottom',
                    fontsize=9, fontweight='bold')
        
        ax6.set_ylabel('年费用 (万元)', fontsize=10)
        ax6.set_title('年费用对比（最优方案金色）', fontsize=12, fontweight='bold')
        ax6.grid(True, alpha=0.3, axis='y')
        
        # 7. 变速调节
        ax7 = plt.subplot(3, 3, 7)
        
        ax7.plot(regulation['Q_vs'], regulation['H_vs'], 'b-o', linewidth=2, label='H-Q')
        ax7.plot(self.Q_design, self.H_design, 'r*', markersize=15, label='设计点')
        
        ax7.set_xlabel('流量 Q (m³/s)', fontsize=10)
        ax7.set_ylabel('扬程 H (m)', fontsize=10)
        ax7.set_title('变速调节特性', fontsize=12, fontweight='bold')
        ax7.legend()
        ax7.grid(True, alpha=0.3)
        
        # 8. 单位成本对比
        ax8 = plt.subplot(3, 3, 8)
        
        unit_costs = []
        for s in schemes:
            econ = self.economic_analysis(s)
            unit_costs.append(econ['unit_cost'])
        
        bars = ax8.barh(scheme_names, unit_costs, alpha=0.7, edgecolor='black',
                       color=['blue', 'green', 'orange', 'red'])
        
        # 标注最优
        min_idx = np.argmin(unit_costs)
        bars[min_idx].set_color('gold')
        bars[min_idx].set_edgecolor('red')
        bars[min_idx].set_linewidth(3)
        
        for bar, val in zip(bars, unit_costs):
            width = bar.get_width()
            ax8.text(width, bar.get_y() + bar.get_height()/2,
                    f'{val:.3f}', ha='left', va='center',
                    fontsize=9, fontweight='bold')
        
        ax8.set_xlabel('单位成本 (元/m³)', fontsize=10)
        ax8.set_title('单位水量成本', fontsize=12, fontweight='bold')
        ax8.grid(True, alpha=0.3, axis='x')
        
        # 9. 综合评价表
        ax9 = plt.subplot(3, 3, 9)
        ax9.axis('off')
        
        best_econ = self.economic_analysis(best_scheme)
        
        table_data = [
            ['项目', '数值', '单位'],
            ['最优方案', f"{best_scheme['id']}({best_scheme['type']})", '-'],
            ['总流量', f"{best_scheme['Q_total']:.1f}", 'm³/s'],
            ['总扬程', f"{best_scheme['H_total']:.1f}", 'm'],
            ['平均效率', f"{best_scheme['eta_avg']*100:.1f}", '%'],
            ['初期投资', f"{best_scheme['investment']:.0f}", '万元'],
            ['年运行费', f"{best_econ['annual_operating']:.1f}", '万元'],
            ['年总费用', f"{best_econ['annual_total']:.1f}", '万元'],
            ['单位成本', f"{best_econ['unit_cost']:.3f}", '元/m³']
        ]
        
        table = ax9.table(cellText=table_data, cellLoc='center', loc='center',
                         colWidths=[0.40, 0.30, 0.25])
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1, 2.0)
        
        for i in range(3):
            table[(0, i)].set_facecolor('#4472C4')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        # 高亮最优方案
        for j in range(3):
            table[(1, j)].set_facecolor('#FFD700')
            table[(1, j)].set_text_props(weight='bold')
        
        ax9.set_title('最优方案汇总', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('/tmp/ch14_problem07_pump_station_optimization.png', dpi=150, bbox_inches='tight')
        print(f"图表已保存: /tmp/ch14_problem07_pump_station_optimization.png")
        plt.show()
    
    def print_results(self):
        """打印结果"""
        print("\n" + "="*70)
        print("第14章 压轴大题 - 题7：泵站系统优化设计")
        print("="*70)
        
        schemes = self.configuration_schemes()
        optimization = self.optimization_selection(schemes)
        best_scheme = schemes[optimization['best_scheme_id'] - 1]
        
        print(f"\n【1. 配置方案】")
        print(f"{'方案':<6} {'类型':<8} {'台数':<6} {'模式':<10} {'总流量':<10} {'投资':<10}")
        print(f"{'':6} {'':8} {'(台)':<6} {'':10} {'(m³/s)':<10} {'(万元)':<10}")
        print("-" * 70)
        
        for s in schemes:
            print(f"{s['id']:<6} {s['type']:<8} {s['num']:<6} {s['mode']:<10} "
                  f"{s['Q_total']:<10.1f} {s['investment']:<10.0f}")
        
        print(f"\n【2. 经济分析】")
        print(f"{'方案':<6} {'投资':<10} {'年运行费':<12} {'年总费用':<12} {'单位成本':<12}")
        print(f"{'':6} {'(万元)':<10} {'(万元)':<12} {'(万元)':<12} {'(元/m³)':<12}")
        print("-" * 70)
        
        for s in schemes:
            econ = self.economic_analysis(s)
            print(f"{s['id']:<6} {s['investment']:<10.0f} {econ['annual_operating']:<12.2f} "
                  f"{econ['annual_total']:<12.2f} {econ['unit_cost']:<12.4f}")
        
        print(f"\n【3. 优化方案选择】")
        print(f"最优方案: 方案{best_scheme['id']}（{best_scheme['type']}）")
        print(f"配置: {best_scheme['num']}台{best_scheme['mode']}")
        print(f"总流量: {best_scheme['Q_total']} m³/s")
        print(f"总扬程: {best_scheme['H_total']} m")
        print(f"平均效率: {best_scheme['eta_avg']*100:.1f}%")
        
        best_econ = self.economic_analysis(best_scheme)
        print(f"\n经济指标:")
        print(f"初期投资: {best_scheme['investment']} 万元")
        print(f"年运行费: {best_econ['annual_operating']:.2f} 万元")
        print(f"年总费用: {best_econ['annual_total']:.2f} 万元")
        print(f"单位成本: {best_econ['unit_cost']:.4f} 元/m³")
        
        print(f"\n✓ 泵站系统优化设计完成")
        print(f"\n{'='*70}\n")


def main():
    Q_design = 15.0  # m³/s
    H_design = 12.0  # m
    hours_per_year = 8000  # hours
    
    pump_station = PumpStationOptimization(Q_design, H_design, hours_per_year)
    pump_station.print_results()
    pump_station.plot_analysis()


if __name__ == "__main__":
    main()
