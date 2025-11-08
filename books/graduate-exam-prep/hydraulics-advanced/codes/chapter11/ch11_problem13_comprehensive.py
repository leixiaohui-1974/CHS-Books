# -*- coding: utf-8 -*-
"""
第11章 水工建筑物 - 题13：综合水利枢纽布置

问题描述：
    某综合水利枢纽工程，包含大坝、溢洪道、电站、船闸等建筑物
    水库总库容V = 5亿m³，正常蓄水位h_norm = 150m
    死水位h_dead = 130m，防洪限制水位h_flood = 145m
    装机容量P = 300MW，设计水头Hd = 50m
    
    求：
    1. 水库特征水位与库容
    2. 大坝枢纽总体布置
    3. 水电站出力计算
    4. 综合效益评价
    5. 枢纽运行调度

核心公式：
    1. 有效库容：V_eff = V_norm - V_dead
    2. 防洪库容：V_flood = V_design - V_flood_limit
    3. 水电出力：P = 9.81·Q·H·η
    4. 年发电量：E = P·T

考试要点：
    - 水利枢纽布置
    - 库容计算
    - 水电计算
    - 综合效益

作者: CHS-Books Team
日期: 2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, Dict, List

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class ComprehensiveProject:
    """综合水利枢纽"""
    
    def __init__(self, V_total: float, h_norm: float, h_dead: float, 
                 h_flood: float, P_installed: float, Hd: float):
        self.V_total = V_total  # 总库容（亿m³）
        self.h_norm = h_norm  # 正常蓄水位
        self.h_dead = h_dead  # 死水位
        self.h_flood = h_flood  # 防洪限制水位
        self.P_installed = P_installed  # 装机容量（MW）
        self.Hd = Hd  # 设计水头
        self.eta = 0.85  # 水电站效率
        self.g = 9.8
        
    def reservoir_capacity(self) -> Dict:
        """
        水库库容特征值
        假设库容曲线为：V = k·(h - h_base)^n
        """
        # 简化假设：线性关系
        h_base = self.h_dead - 20  # 基准高程
        
        # 死库容（30%总库容）
        V_dead = self.V_total * 0.3
        
        # 兴利库容（正常-死）
        V_benefit = self.V_total * 0.5
        
        # 防洪库容（设计-正常）
        V_flood = self.V_total * 0.2
        
        # 总库容验算
        V_calc = V_dead + V_benefit + V_flood
        
        return {
            'V_total': self.V_total,
            'V_dead': V_dead,
            'V_benefit': V_benefit,
            'V_flood': V_flood,
            'V_calc': V_calc
        }
    
    def characteristic_levels(self) -> Dict:
        """特征水位"""
        return {
            'h_dead': self.h_dead,
            'h_flood': self.h_flood,
            'h_norm': self.h_norm,
            'h_design': self.h_norm + 5  # 设计洪水位
        }
    
    def hydropower_output(self, Q: float = None, H: float = None) -> Dict:
        """
        水电站出力
        P = 9.81·Q·H·η（kW）
        
        参数：
        Q - 流量（m³/s），默认使用设计流量
        H - 水头（m），默认使用设计水头
        """
        if Q is None:
            # 设计流量（根据装机容量反算）
            Q = self.P_installed * 1000 / (9.81 * self.Hd * self.eta)
        
        if H is None:
            H = self.Hd
        
        # 出力（kW）
        P = 9.81 * Q * H * self.eta
        
        # 年发电量（假设利用小时数T=5000h）
        T = 5000  # 利用小时数
        E_year = P * T / 1e6  # GWh
        
        return {
            'Q': Q,
            'H': H,
            'P': P / 1000,  # MW
            'T': T,
            'E_year': E_year
        }
    
    def project_layout(self) -> Dict:
        """枢纽总体布置"""
        # 各建筑物长度（假设）
        L_dam = 500  # 大坝长度
        L_spillway = 120  # 溢洪道宽度
        L_powerhouse = 80  # 电站厂房长度
        L_lock = 100  # 船闸长度
        L_total = L_dam + L_spillway + L_powerhouse + L_lock
        
        return {
            'L_dam': L_dam,
            'L_spillway': L_spillway,
            'L_powerhouse': L_powerhouse,
            'L_lock': L_lock,
            'L_total': L_total,
            'layout': ['大坝', '溢洪道', '电站', '船闸']
        }
    
    def comprehensive_benefits(self) -> Dict:
        """
        综合效益评价
        """
        power_output = self.hydropower_output()
        
        # 发电效益（元/年）
        price_electricity = 0.4  # 电价（元/kWh）
        benefit_power = power_output['E_year'] * 1e6 * price_electricity
        
        # 防洪效益（元/年）
        capacity_info = self.reservoir_capacity()
        benefit_flood = capacity_info['V_flood'] * 1e8 * 0.05  # 简化估算
        
        # 灌溉效益（元/年）
        benefit_irrigation = capacity_info['V_benefit'] * 1e8 * 0.03
        
        # 航运效益（元/年）
        benefit_navigation = 5000 * 10000  # 固定值
        
        # 总效益
        benefit_total = benefit_power + benefit_flood + benefit_irrigation + benefit_navigation
        
        return {
            'benefit_power': benefit_power / 1e8,  # 转为亿元
            'benefit_flood': benefit_flood / 1e8,
            'benefit_irrigation': benefit_irrigation / 1e8,
            'benefit_navigation': benefit_navigation / 1e8,
            'benefit_total': benefit_total / 1e8
        }
    
    def operation_modes(self) -> List[Dict]:
        """
        运行调度模式
        """
        modes = []
        
        # 模式1：汛期防洪运行
        modes.append({
            'name': '汛期防洪',
            'period': '6-9月',
            'water_level': self.h_flood,
            'operation': '降低水位至防洪限制水位，预留防洪库容',
            'priority': '防洪'
        })
        
        # 模式2：枯期蓄水运行
        modes.append({
            'name': '枯期蓄水',
            'period': '10-次年5月',
            'water_level': self.h_norm,
            'operation': '蓄水至正常蓄水位，满足发电、灌溉需求',
            'priority': '兴利'
        })
        
        # 模式3：平水期综合运行
        modes.append({
            'name': '平水期综合',
            'period': '4-5月',
            'water_level': (self.h_flood + self.h_norm) / 2,
            'operation': '兼顾防洪与兴利，动态调节水位',
            'priority': '综合'
        })
        
        return modes
    
    def plot_analysis(self):
        """绘制分析图表"""
        fig = plt.figure(figsize=(16, 12))
        
        capacity_info = self.reservoir_capacity()
        levels = self.characteristic_levels()
        power_output = self.hydropower_output()
        layout_info = self.project_layout()
        benefits = self.comprehensive_benefits()
        modes = self.operation_modes()
        
        # 1. 枢纽平面布置
        ax1 = plt.subplot(3, 3, 1)
        
        # 简化平面布置图
        x_starts = [0, layout_info['L_dam'], 
                   layout_info['L_dam'] + layout_info['L_spillway'],
                   layout_info['L_dam'] + layout_info['L_spillway'] + layout_info['L_powerhouse']]
        widths = [layout_info['L_dam'], layout_info['L_spillway'], 
                 layout_info['L_powerhouse'], layout_info['L_lock']]
        colors_layout = ['gray', 'blue', 'green', 'orange']
        labels_layout = layout_info['layout']
        
        for x, w, c, l in zip(x_starts, widths, colors_layout, labels_layout):
            ax1.barh(1, w, left=x, height=0.5, color=c, alpha=0.7, 
                    edgecolor='black', linewidth=2, label=l)
            ax1.text(x + w/2, 1, l, ha='center', va='center', 
                    fontsize=10, fontweight='bold', color='white')
        
        # 上下游水体
        ax1.barh(1.5, layout_info['L_total'], height=0.3, color='lightblue', 
                alpha=0.5, label='上游库区')
        ax1.barh(0.5, layout_info['L_total'], height=0.3, color='lightgreen', 
                alpha=0.5, label='下游河道')
        
        ax1.set_xlabel('长度 (m)', fontsize=10)
        ax1.set_title('枢纽平面布置', fontsize=12, fontweight='bold')
        ax1.set_yticks([])
        ax1.set_xlim(0, layout_info['L_total'])
        ax1.set_ylim(0, 2)
        ax1.legend(loc='upper right', fontsize=8, ncol=2)
        
        # 2. 特征水位
        ax2 = plt.subplot(3, 3, 2)
        
        level_names = ['死水位', '防洪限制', '正常蓄水', '设计洪水']
        level_values = [levels['h_dead'], levels['h_flood'], 
                       levels['h_norm'], levels['h_design']]
        colors_level = ['brown', 'orange', 'blue', 'red']
        
        for i, (name, val, c) in enumerate(zip(level_names, level_values, colors_level)):
            ax2.barh(i, val, color=c, alpha=0.7, edgecolor='black')
            ax2.text(val/2, i, f'{name}\n{val}m', ha='center', va='center',
                    fontsize=9, fontweight='bold', color='white')
        
        ax2.set_xlabel('高程 (m)', fontsize=10)
        ax2.set_title('特征水位', fontsize=12, fontweight='bold')
        ax2.set_yticks([])
        ax2.set_xlim(0, levels['h_design']+10)
        
        # 3. 库容分布
        ax3 = plt.subplot(3, 3, 3)
        
        capacity_names = ['死库容', '兴利库容', '防洪库容']
        capacity_values = [capacity_info['V_dead'], 
                          capacity_info['V_benefit'],
                          capacity_info['V_flood']]
        colors_capacity = ['brown', 'green', 'blue']
        
        wedges, texts, autotexts = ax3.pie(capacity_values, labels=capacity_names,
                                           autopct='%1.1f%%', colors=colors_capacity,
                                           startangle=90)
        
        for text in texts:
            text.set_fontsize(10)
            text.set_fontweight('bold')
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(9)
            autotext.set_fontweight('bold')
        
        ax3.set_title(f'库容分布 (总计{self.V_total}亿m³)', 
                     fontsize=12, fontweight='bold')
        
        # 4. 水位-库容关系
        ax4 = plt.subplot(3, 3, 4)
        
        # 假设库容曲线
        h_range = np.linspace(self.h_dead-20, levels['h_design'], 100)
        h_base = self.h_dead - 20
        V_range = self.V_total * ((h_range - h_base) / (levels['h_design'] - h_base)) ** 1.5
        
        ax4.plot(V_range, h_range, 'b-', linewidth=2)
        
        # 标注特征水位
        for name, val, c in zip(level_names, level_values, colors_level):
            V_val = self.V_total * ((val - h_base) / (levels['h_design'] - h_base)) ** 1.5
            ax4.plot(V_val, val, 'o', color=c, markersize=10)
            ax4.text(V_val+0.2, val, name, fontsize=8, color=c, fontweight='bold')
        
        ax4.set_xlabel('库容 (亿m³)', fontsize=10)
        ax4.set_ylabel('水位 (m)', fontsize=10)
        ax4.set_title('水位-库容关系', fontsize=12, fontweight='bold')
        ax4.grid(True, alpha=0.3)
        
        # 5. 水电出力
        ax5 = plt.subplot(3, 3, 5)
        ax5.axis('off')
        
        ax5.text(0.5, 0.95, '水电站参数', fontsize=11, ha='center', fontweight='bold')
        ax5.text(0.1, 0.80, f'装机容量: {self.P_installed} MW', fontsize=10, color='red')
        ax5.text(0.1, 0.70, f'设计水头: {self.Hd} m', fontsize=10)
        ax5.text(0.1, 0.60, f'设计流量: {power_output["Q"]:.1f} m³/s', fontsize=10)
        ax5.text(0.1, 0.50, f'水轮机效率: {self.eta:.0%}', fontsize=10)
        ax5.text(0.1, 0.38, f'保证出力: {power_output["P"]:.1f} MW', fontsize=10, color='blue')
        ax5.text(0.1, 0.28, f'利用小时数: {power_output["T"]} h', fontsize=10)
        ax5.text(0.1, 0.15, f'年发电量: {power_output["E_year"]:.2f} GWh', fontsize=11,
                color='green', fontweight='bold')
        ax5.text(0.1, 0.02, f'           = {power_output["E_year"]*1e6:.2e} kWh', fontsize=9, color='gray')
        
        ax5.set_title('水电计算', fontsize=12, fontweight='bold')
        
        # 6. 综合效益
        ax6 = plt.subplot(3, 3, 6)
        
        benefit_names = ['发电', '防洪', '灌溉', '航运']
        benefit_values = [benefits['benefit_power'], benefits['benefit_flood'],
                         benefits['benefit_irrigation'], benefits['benefit_navigation']]
        colors_benefit = ['green', 'blue', 'orange', 'purple']
        
        bars = ax6.bar(benefit_names, benefit_values, color=colors_benefit,
                      alpha=0.7, edgecolor='black')
        
        ax6.set_ylabel('效益 (亿元/年)', fontsize=10)
        ax6.set_title(f'综合效益 (总计{benefits["benefit_total"]:.2f}亿元/年)', 
                     fontsize=12, fontweight='bold')
        ax6.grid(True, alpha=0.3, axis='y')
        
        for bar, val in zip(bars, benefit_values):
            height = bar.get_height()
            ax6.text(bar.get_x() + bar.get_width()/2., height,
                    f'{val:.2f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        # 7. 运行调度
        ax7 = plt.subplot(3, 3, 7)
        
        # 全年水位变化（示意）
        months = np.arange(1, 13)
        water_levels = []
        for m in months:
            if 6 <= m <= 9:  # 汛期
                wl = self.h_flood
            elif 10 <= m or m <= 3:  # 枯期
                wl = self.h_norm
            else:  # 平水期
                wl = (self.h_flood + self.h_norm) / 2
            water_levels.append(wl)
        
        ax7.plot(months, water_levels, 'b-o', linewidth=2, markersize=6)
        ax7.axhline(self.h_norm, color='blue', linestyle='--', linewidth=1, label='正常蓄水位')
        ax7.axhline(self.h_flood, color='orange', linestyle='--', linewidth=1, label='防洪限制水位')
        ax7.axhline(self.h_dead, color='red', linestyle='--', linewidth=1, label='死水位')
        
        # 标注运行期
        ax7.axvspan(6, 9, alpha=0.2, color='blue', label='汛期')
        ax7.axvspan(10, 12, alpha=0.2, color='green')
        ax7.axvspan(1, 3, alpha=0.2, color='green', label='枯期')
        ax7.axvspan(4, 5, alpha=0.2, color='yellow', label='平水期')
        
        ax7.set_xlabel('月份', fontsize=10)
        ax7.set_ylabel('水位 (m)', fontsize=10)
        ax7.set_title('全年运行调度', fontsize=12, fontweight='bold')
        ax7.legend(fontsize=7, loc='upper right')
        ax7.grid(True, alpha=0.3)
        ax7.set_xticks(months)
        ax7.set_xticklabels(['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'])
        
        # 8. 效益对比雷达图
        ax8 = plt.subplot(3, 3, 8, projection='polar')
        
        # 归一化效益（满分100）
        max_benefit = max(benefit_values)
        benefit_scores = [v / max_benefit * 100 for v in benefit_values]
        
        angles = np.linspace(0, 2*np.pi, len(benefit_names), endpoint=False).tolist()
        benefit_scores += benefit_scores[:1]
        angles += angles[:1]
        
        ax8.plot(angles, benefit_scores, 'o-', linewidth=2, color='blue')
        ax8.fill(angles, benefit_scores, alpha=0.25, color='blue')
        ax8.set_xticks(angles[:-1])
        ax8.set_xticklabels(benefit_names, fontsize=10)
        ax8.set_ylim(0, 100)
        ax8.set_title('效益雷达图', fontsize=12, fontweight='bold', pad=20)
        ax8.grid(True)
        
        # 9. 结果汇总表
        ax9 = plt.subplot(3, 3, 9)
        ax9.axis('off')
        
        table_data = [
            ['项目', '数值', '单位'],
            ['总库容', f'{self.V_total:.1f}', '亿m³'],
            ['正常蓄水位', f'{self.h_norm}', 'm'],
            ['装机容量', f'{self.P_installed}', 'MW'],
            ['年发电量', f'{power_output["E_year"]:.2f}', 'GWh'],
            ['年发电效益', f'{benefits["benefit_power"]:.2f}', '亿元'],
            ['年总效益', f'{benefits["benefit_total"]:.2f}', '亿元'],
            ['枢纽总长', f'{layout_info["L_total"]}', 'm']
        ]
        
        table = ax9.table(cellText=table_data, cellLoc='center', loc='center',
                         colWidths=[0.45, 0.3, 0.2])
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2.2)
        
        for i in range(3):
            table[(0, i)].set_facecolor('#4472C4')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        # 高亮关键指标
        for i in [1, 5, 7]:
            for j in range(3):
                table[(i, j)].set_facecolor('#FFF9E6')
        
        ax9.set_title('工程总结', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('/tmp/ch11_problem13_comprehensive.png', dpi=150, bbox_inches='tight')
        print(f"图表已保存: /tmp/ch11_problem13_comprehensive.png")
        plt.show()
    
    def print_results(self):
        """打印结果"""
        print("\n" + "="*70)
        print("第11章 水工建筑物 - 题13：综合水利枢纽布置")
        print("="*70)
        
        capacity_info = self.reservoir_capacity()
        levels = self.characteristic_levels()
        power_output = self.hydropower_output()
        layout_info = self.project_layout()
        benefits = self.comprehensive_benefits()
        modes = self.operation_modes()
        
        print(f"\n【水库特征】")
        print(f"总库容: {self.V_total} 亿m³")
        print(f"死库容: {capacity_info['V_dead']:.2f} 亿m³")
        print(f"兴利库容: {capacity_info['V_benefit']:.2f} 亿m³")
        print(f"防洪库容: {capacity_info['V_flood']:.2f} 亿m³")
        
        print(f"\n【特征水位】")
        print(f"死水位: {levels['h_dead']} m")
        print(f"防洪限制水位: {levels['h_flood']} m")
        print(f"正常蓄水位: {levels['h_norm']} m")
        print(f"设计洪水位: {levels['h_design']} m")
        
        print(f"\n【枢纽布置】")
        print(f"枢纽总长: {layout_info['L_total']} m")
        print(f"  - 大坝: {layout_info['L_dam']} m")
        print(f"  - 溢洪道: {layout_info['L_spillway']} m")
        print(f"  - 电站厂房: {layout_info['L_powerhouse']} m")
        print(f"  - 船闸: {layout_info['L_lock']} m")
        
        print(f"\n【水电站】")
        print(f"装机容量: {self.P_installed} MW")
        print(f"设计水头: {self.Hd} m")
        print(f"设计流量: {power_output['Q']:.2f} m³/s")
        print(f"水轮机效率: {self.eta:.0%}")
        print(f"保证出力: P = 9.81·Q·H·η = {power_output['P']:.2f} MW")
        print(f"年利用小时数: {power_output['T']} h")
        print(f"年发电量: E = {power_output['E_year']:.2f} GWh = {power_output['E_year']*1e6:.2e} kWh")
        
        print(f"\n【综合效益】（年效益）")
        print(f"发电效益: {benefits['benefit_power']:.2f} 亿元")
        print(f"防洪效益: {benefits['benefit_flood']:.2f} 亿元")
        print(f"灌溉效益: {benefits['benefit_irrigation']:.2f} 亿元")
        print(f"航运效益: {benefits['benefit_navigation']:.2f} 亿元")
        print(f"综合效益合计: {benefits['benefit_total']:.2f} 亿元/年")
        
        print(f"\n【运行调度】")
        for i, mode in enumerate(modes, 1):
            print(f"\n调度模式{i}：{mode['name']}")
            print(f"  时段: {mode['period']}")
            print(f"  运行水位: {mode['water_level']:.1f} m")
            print(f"  调度原则: {mode['operation']}")
            print(f"  优先任务: {mode['priority']}")
        
        print(f"\n✓ 综合水利枢纽规划完成")
        print(f"\n{'='*70}\n")


def main():
    V_total = 5.0  # 亿m³
    h_norm = 150
    h_dead = 130
    h_flood = 145
    P_installed = 300  # MW
    Hd = 50
    
    project = ComprehensiveProject(V_total, h_norm, h_dead, h_flood, P_installed, Hd)
    project.print_results()
    project.plot_analysis()


if __name__ == "__main__":
    main()
