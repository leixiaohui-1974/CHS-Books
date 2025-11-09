# -*- coding: utf-8 -*-
"""
第06章 水泵与水泵站 - 题13：泵站综合设计

问题描述：
    某泵站需要从河道取水，设计流量Q = 1.2 m³/s
    最低水位: 20m
    最高水位: 22m
    输水高程: 45m
    管路总长: L = 2000m
    管径: d = 0.5m
    沿程阻力系数: λ = 0.03
    局部阻力系数和: Σζ = 20
    
    待选水泵:
    A型: Q = 0.4 m³/s, H = 30m, η = 0.75, N = 160 kW
    B型: Q = 0.6 m³/s, H = 28m, η = 0.78, N = 220 kW
    
    求：
    1. 管路特性曲线
    2. 水泵选型
    3. 运行工况分析
    4. 能耗与经济性
    5. 年运行费用
    6. 最优方案

核心公式：
    1. 管路特性: H = Hst + rQ²
    2. 阻力系数: r = (λL/d + Σζ)/(2gA²)
    3. 轴功率: N = ρgQH/η
    4. 年能耗: E = NTη_m/1000 [kWh]
    5. 年运行费用: C = E×电价

考试要点：
    - 静扬程随水位变化
    - 管路阻力系数计算
    - 多方案对比选型
    - 经济运行分析
    - 年运行费用估算

作者: CHS-Books Team
日期: 2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, Dict, List

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class PumpStationDesign:
    """泵站综合设计"""
    
    def __init__(self, Q_design: float, Z_low: float, Z_high: float, Z_out: float,
                 L: float, d: float, lambd: float, zeta: float):
        """
        初始化参数
        
        参数:
            Q_design: 设计流量 [m³/s]
            Z_low: 最低水位 [m]
            Z_high: 最高水位 [m]
            Z_out: 输水高程 [m]
            L: 管路总长 [m]
            d: 管径 [m]
            lambd: 沿程阻力系数
            zeta: 局部阻力系数和
        """
        self.Q_design = Q_design
        self.Z_low = Z_low
        self.Z_high = Z_high
        self.Z_out = Z_out
        self.L = L
        self.d = d
        self.lambd = lambd
        self.zeta = zeta
        
        self.rho = 1000  # 水密度 [kg/m³]
        self.g = 9.8  # 重力加速度 [m/s²]
        
        # 可选水泵（按型号存储）
        self.pumps = {}
        
    def add_pump(self, name: str, Q: float, H: float, eta: float, N: float):
        """添加水泵选项"""
        self.pumps[name] = {
            'Q': Q,
            'H': H,
            'eta': eta,
            'N': N
        }
    
    def static_head(self, Z_water: float = None) -> float:
        """
        静扬程
        
        参数:
            Z_water: 水位 [m]，默认为最低水位
        """
        if Z_water is None:
            Z_water = self.Z_low
        
        Hst = self.Z_out - Z_water
        return Hst
    
    def resistance_coefficient(self) -> float:
        """
        管路阻力系数
        
        r = (λL/d + Σζ)/(2gA²)
        """
        A = np.pi * (self.d ** 2) / 4
        r = (self.lambd * self.L / self.d + self.zeta) / (2 * self.g * A ** 2)
        return r
    
    def pipe_characteristic(self, Q: np.ndarray, Z_water: float = None) -> np.ndarray:
        """
        管路特性曲线
        
        H = Hst + rQ²
        """
        Hst = self.static_head(Z_water)
        r = self.resistance_coefficient()
        H = Hst + r * (Q ** 2)
        return H
    
    def pump_selection(self) -> Dict:
        """
        水泵选型分析
        
        返回各方案的详细信息
        """
        schemes = {}
        
        for name, pump in self.pumps.items():
            Q_single = pump['Q']
            H_single = pump['H']
            
            # 计算需要的台数
            n_pumps = int(np.ceil(self.Q_design / Q_single))
            
            # 并联运行流量
            Q_total = Q_single * n_pumps
            
            # 管路所需扬程（最低水位）
            H_required_low = self.pipe_characteristic(np.array([self.Q_design]), self.Z_low)[0]
            
            # 管路所需扬程（最高水位）
            H_required_high = self.pipe_characteristic(np.array([self.Q_design]), self.Z_high)[0]
            
            # 判断是否满足要求（最不利工况）
            is_adequate = H_single >= H_required_low
            
            # 总装机功率
            N_total = pump['N'] * n_pumps
            
            # 实际工况点（简化：假设各泵平均分配流量）
            Q_actual = self.Q_design
            H_actual_low = H_required_low
            H_actual_high = H_required_high
            
            # 实际轴功率（最低水位，最不利）
            N_actual_low = self.rho * self.g * Q_actual * H_actual_low / (pump['eta'] * 1000)
            N_actual_high = self.rho * self.g * Q_actual * H_actual_high / (pump['eta'] * 1000)
            
            schemes[name] = {
                'n_pumps': n_pumps,
                'Q_single': Q_single,
                'H_single': H_single,
                'Q_total': Q_total,
                'H_required_low': H_required_low,
                'H_required_high': H_required_high,
                'is_adequate': is_adequate,
                'N_rated': pump['N'],
                'N_total': N_total,
                'N_actual_low': N_actual_low,
                'N_actual_high': N_actual_high,
                'eta': pump['eta'],
                'margin_low': H_single - H_required_low,
                'margin_high': H_single - H_required_high,
            }
        
        return schemes
    
    def annual_cost(self, scheme: Dict, T_annual: float = 4000, 
                   price: float = 0.6, load_factor: float = 0.8) -> Dict:
        """
        年运行费用估算
        
        参数:
            scheme: 方案字典
            T_annual: 年运行时间 [h]
            price: 电价 [元/kWh]
            load_factor: 负荷系数（考虑不同水位）
        
        返回:
            成本字典
        """
        # 平均功率（考虑高低水位）
        N_avg = (scheme['N_actual_low'] + scheme['N_actual_high']) / 2 * load_factor
        
        # 年能耗
        E_annual = N_avg * T_annual  # kWh
        
        # 年电费
        C_annual = E_annual * price  # 元
        
        # 单位流量能耗
        E_unit = E_annual / (self.Q_design * 3600 * T_annual)  # kWh/m³
        
        # 单位流量成本
        C_unit = C_annual / (self.Q_design * 3600 * T_annual)  # 元/m³
        
        return {
            'N_avg': N_avg,
            'E_annual': E_annual,
            'C_annual': C_annual,
            'E_unit': E_unit,
            'C_unit': C_unit,
        }
    
    def plot_analysis(self):
        """绘制完整分析图表（9个子图）"""
        fig = plt.figure(figsize=(16, 12))
        
        # 获取选型方案
        schemes = self.pump_selection()
        
        # 流量范围
        Q_range = np.linspace(0, 1.5, 200)
        
        # 1. 管路特性曲线（不同水位）
        ax1 = plt.subplot(3, 3, 1)
        
        H_pipe_low = self.pipe_characteristic(Q_range, self.Z_low)
        H_pipe_high = self.pipe_characteristic(Q_range, self.Z_high)
        
        ax1.plot(Q_range*1000, H_pipe_low, 'r-', linewidth=2, 
                label=f'最低水位({self.Z_low}m)')
        ax1.plot(Q_range*1000, H_pipe_high, 'b-', linewidth=2, 
                label=f'最高水位({self.Z_high}m)')
        
        # 设计点
        H_design_low = self.pipe_characteristic(np.array([self.Q_design]), self.Z_low)[0]
        H_design_high = self.pipe_characteristic(np.array([self.Q_design]), self.Z_high)[0]
        
        ax1.plot(self.Q_design*1000, H_design_low, 'ro', markersize=12, 
                label=f'设计点(低水位)')
        ax1.plot(self.Q_design*1000, H_design_high, 'bo', markersize=12,
                label=f'设计点(高水位)')
        
        # 静扬程
        Hst_low = self.static_head(self.Z_low)
        Hst_high = self.static_head(self.Z_high)
        ax1.axhline(Hst_low, color='red', linestyle='--', alpha=0.3)
        ax1.axhline(Hst_high, color='blue', linestyle='--', alpha=0.3)
        
        ax1.set_xlabel('流量 Q (L/s)', fontsize=11)
        ax1.set_ylabel('扬程 H (m)', fontsize=11)
        ax1.set_title('管路特性曲线', fontsize=12, fontweight='bold')
        ax1.legend(fontsize=9)
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim(0, 1500)
        
        # 2. 水泵特性与管路特性匹配
        ax2 = plt.subplot(3, 3, 2)
        
        # 绘制管路特性
        ax2.plot(Q_range*1000, H_pipe_low, 'k-', linewidth=2, label='管路特性(低水位)')
        
        # 绘制各型号水泵特性
        colors = ['blue', 'green', 'orange']
        for i, (name, pump) in enumerate(self.pumps.items()):
            Q_pump = pump['Q']
            H_pump = pump['H']
            
            # 单泵特性（简化为水平线）
            ax2.axhline(H_pump, color=colors[i], linestyle='--', 
                       linewidth=1.5, alpha=0.5, label=f'{name}型单泵')
            
            # 并联特性（n台）
            scheme = schemes[name]
            n = scheme['n_pumps']
            if n > 1:
                # 简化并联特性线（实际应考虑并联效率损失）
                ax2.axhline(H_pump, color=colors[i], linestyle='-', 
                           linewidth=2, label=f'{name}型{n}台并联')
        
        # 设计点
        ax2.plot(self.Q_design*1000, H_design_low, 'ro', markersize=12, 
                label='设计工况')
        
        ax2.set_xlabel('流量 Q (L/s)', fontsize=11)
        ax2.set_ylabel('扬程 H (m)', fontsize=11)
        ax2.set_title('水泵选型匹配', fontsize=12, fontweight='bold')
        ax2.legend(fontsize=8, ncol=2)
        ax2.grid(True, alpha=0.3)
        ax2.set_xlim(0, 1500)
        ax2.set_ylim(0, 40)
        
        # 3. 各方案台数与流量
        ax3 = plt.subplot(3, 3, 3)
        
        names = list(schemes.keys())
        n_pumps_list = [schemes[n]['n_pumps'] for n in names]
        Q_singles = [schemes[n]['Q_single']*1000 for n in names]
        
        x = np.arange(len(names))
        width = 0.35
        
        bars1 = ax3.bar(x - width/2, n_pumps_list, width, label='台数',
                       color='lightblue', alpha=0.7, edgecolor='black')
        ax3_twin = ax3.twinx()
        bars2 = ax3_twin.bar(x + width/2, Q_singles, width, label='单泵流量',
                            color='lightgreen', alpha=0.7, edgecolor='black')
        
        ax3.set_ylabel('台数', fontsize=11, color='blue')
        ax3_twin.set_ylabel('单泵流量 (L/s)', fontsize=11, color='green')
        ax3.set_xlabel('方案', fontsize=11)
        ax3.set_title('各方案配置', fontsize=12, fontweight='bold')
        ax3.set_xticks(x)
        ax3.set_xticklabels(names)
        ax3.tick_params(axis='y', labelcolor='blue')
        ax3_twin.tick_params(axis='y', labelcolor='green')
        ax3.grid(True, alpha=0.3, axis='y')
        
        # 添加数值标注
        for bar in bars1:
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2, height,
                    f'{int(height)}台', ha='center', va='bottom', fontsize=9)
        
        for bar in bars2:
            height = bar.get_height()
            ax3_twin.text(bar.get_x() + bar.get_width()/2, height,
                         f'{height:.0f}', ha='center', va='bottom', fontsize=9)
        
        # 4. 扬程裕度对比
        ax4 = plt.subplot(3, 3, 4)
        
        margins_low = [schemes[n]['margin_low'] for n in names]
        margins_high = [schemes[n]['margin_high'] for n in names]
        is_adequate = [schemes[n]['is_adequate'] for n in names]
        
        x = np.arange(len(names))
        width = 0.35
        
        bars1 = ax4.bar(x - width/2, margins_low, width, label='低水位裕度',
                       color=['green' if a else 'red' for a in is_adequate],
                       alpha=0.7, edgecolor='black')
        bars2 = ax4.bar(x + width/2, margins_high, width, label='高水位裕度',
                       color='lightblue', alpha=0.7, edgecolor='black')
        
        ax4.axhline(0, color='red', linestyle='--', linewidth=2, alpha=0.5)
        ax4.set_ylabel('扬程裕度 (m)', fontsize=11)
        ax4.set_xlabel('方案', fontsize=11)
        ax4.set_title('扬程裕度分析', fontsize=12, fontweight='bold')
        ax4.set_xticks(x)
        ax4.set_xticklabels(names)
        ax4.legend(fontsize=9)
        ax4.grid(True, alpha=0.3, axis='y')
        
        # 添加数值标注
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                if height >= 0:
                    ax4.text(bar.get_x() + bar.get_width()/2, height,
                            f'{height:.1f}', ha='center', va='bottom', fontsize=9)
                else:
                    ax4.text(bar.get_x() + bar.get_width()/2, height,
                            f'{height:.1f}', ha='center', va='top', fontsize=9)
        
        # 5. 装机功率对比
        ax5 = plt.subplot(3, 3, 5)
        
        N_totals = [schemes[n]['N_total'] for n in names]
        N_actual_lows = [schemes[n]['N_actual_low'] for n in names]
        
        x = np.arange(len(names))
        width = 0.35
        
        bars1 = ax5.bar(x - width/2, N_totals, width, label='装机功率',
                       color='lightcoral', alpha=0.7, edgecolor='black')
        bars2 = ax5.bar(x + width/2, N_actual_lows, width, label='实际功率(低水位)',
                       color='lightgreen', alpha=0.7, edgecolor='black')
        
        ax5.set_ylabel('功率 (kW)', fontsize=11)
        ax5.set_xlabel('方案', fontsize=11)
        ax5.set_title('功率对比', fontsize=12, fontweight='bold')
        ax5.set_xticks(x)
        ax5.set_xticklabels(names)
        ax5.legend(fontsize=9)
        ax5.grid(True, alpha=0.3, axis='y')
        
        # 添加数值标注
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax5.text(bar.get_x() + bar.get_width()/2, height,
                        f'{height:.0f}', ha='center', va='bottom', fontsize=9)
        
        # 6. 年运行费用对比
        ax6 = plt.subplot(3, 3, 6)
        
        costs = {}
        for name in names:
            costs[name] = self.annual_cost(schemes[name])
        
        C_annuals = [costs[n]['C_annual']/10000 for n in names]  # 万元
        
        bars = ax6.bar(names, C_annuals, 
                      color=['lightgreen' if schemes[n]['is_adequate'] else 'lightcoral' 
                            for n in names],
                      alpha=0.7, edgecolor='black')
        
        ax6.set_ylabel('年运行费用 (万元)', fontsize=11)
        ax6.set_xlabel('方案', fontsize=11)
        ax6.set_title('年运行费用对比', fontsize=12, fontweight='bold')
        ax6.grid(True, alpha=0.3, axis='y')
        
        for bar, name in zip(bars, names):
            height = bar.get_height()
            ax6.text(bar.get_x() + bar.get_width()/2, height,
                    f'{height:.1f}万', ha='center', va='bottom',
                    fontsize=10, fontweight='bold')
            # 标注单位成本
            C_unit = costs[name]['C_unit']
            ax6.text(bar.get_x() + bar.get_width()/2, height/2,
                    f'{C_unit:.4f}元/m³', ha='center', va='center',
                    fontsize=8, color='darkred', fontweight='bold')
        
        # 7. 综合评分雷达图
        ax7 = plt.subplot(3, 3, 7, projection='polar')
        
        # 评价指标（标准化到0-1）
        categories = ['扬程\n裕度', '装机\n经济', '运行\n费用', '效率', '可靠性']
        N = len(categories)
        angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
        angles += angles[:1]
        
        for i, name in enumerate(names):
            if not schemes[name]['is_adequate']:
                continue  # 跳过不满足要求的方案
            
            # 标准化评分（0-1，越大越好）
            margin_score = min(schemes[name]['margin_low'] / 10, 1)  # 裕度越大越好
            cost_score = 1 - (schemes[name]['N_total'] - min([s['N_total'] for s in schemes.values()])) / max([s['N_total'] for s in schemes.values()])
            annual_score = 1 - (costs[name]['C_annual'] - min([costs[n]['C_annual'] for n in names])) / max([costs[n]['C_annual'] for n in names])
            eta_score = schemes[name]['eta'] / max([s['eta'] for s in schemes.values()])
            reliability_score = min(schemes[name]['n_pumps'] / 4, 1)  # 台数适中为佳
            
            values = [margin_score, cost_score, annual_score, eta_score, reliability_score]
            values += values[:1]
            
            ax7.plot(angles, values, 'o-', linewidth=2, label=name)
            ax7.fill(angles, values, alpha=0.15)
        
        ax7.set_xticks(angles[:-1])
        ax7.set_xticklabels(categories, fontsize=9)
        ax7.set_ylim(0, 1)
        ax7.set_title('综合评价雷达图', fontsize=12, fontweight='bold', pad=20)
        ax7.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0), fontsize=9)
        ax7.grid(True)
        
        # 8. 方案对比表
        ax8 = plt.subplot(3, 3, 8)
        ax8.axis('off')
        
        data = [['项目'] + names]
        data.append(['台数'] + [f"{schemes[n]['n_pumps']}" for n in names])
        data.append(['单泵Q(L/s)'] + [f"{schemes[n]['Q_single']*1000:.0f}" for n in names])
        data.append(['单泵H(m)'] + [f"{schemes[n]['H_single']:.1f}" for n in names])
        data.append(['裕度(m)'] + [f"{schemes[n]['margin_low']:.1f}" for n in names])
        data.append(['装机(kW)'] + [f"{schemes[n]['N_total']:.0f}" for n in names])
        data.append(['年费(万)'] + [f"{costs[n]['C_annual']/10000:.1f}" for n in names])
        data.append(['满足要求'] + ['✓' if schemes[n]['is_adequate'] else '✗' for n in names])
        
        table = ax8.table(cellText=data, loc='center', cellLoc='center',
                         colWidths=[0.3] + [0.35/(len(names))] * len(names))
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2.2)
        
        # 设置表头样式
        for i in range(len(names) + 1):
            table[(0, i)].set_facecolor('#4CAF50')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        # 设置满足要求行颜色
        for i in range(len(names)):
            cell = table[(len(data)-1, i+1)]
            if schemes[names[i]]['is_adequate']:
                cell.set_facecolor('#90EE90')
            else:
                cell.set_facecolor('#FFB6C1')
        
        ax8.set_title('方案对比表', fontsize=12, fontweight='bold', pad=20)
        
        # 9. 结果汇总与推荐
        ax9 = plt.subplot(3, 3, 9)
        ax9.axis('off')
        
        # 找出最优方案（满足要求且年费最低）
        valid_schemes = {n: costs[n]['C_annual'] for n in names if schemes[n]['is_adequate']}
        if valid_schemes:
            best_scheme = min(valid_schemes, key=valid_schemes.get)
        else:
            best_scheme = None
        
        Hst_low = self.static_head(self.Z_low)
        Hst_high = self.static_head(self.Z_high)
        r = self.resistance_coefficient()
        
        summary = [
            '═══ 泵站设计结果 ═══',
            '',
            '【设计条件】',
            f'设计流量: {self.Q_design} m³/s',
            f'= {self.Q_design*1000:.0f} L/s',
            f'水位: {self.Z_low}~{self.Z_high} m',
            f'输水高程: {self.Z_out} m',
            '',
            '【管路特性】',
            f'静扬程: {Hst_low:.1f}~{Hst_high:.1f} m',
            f'阻力系数: r = {r:.2f}',
            f'所需扬程(低): {H_design_low:.1f} m',
            f'所需扬程(高): {H_design_high:.1f} m',
            '',
        ]
        
        if best_scheme:
            bs = schemes[best_scheme]
            bc = costs[best_scheme]
            summary.extend([
                '【推荐方案】',
                f'型号: {best_scheme}型',
                f'台数: {bs["n_pumps"]}台',
                f'单泵: Q={bs["Q_single"]*1000:.0f}L/s, H={bs["H_single"]:.1f}m',
                f'裕度: {bs["margin_low"]:.1f} m',
                f'装机: {bs["N_total"]:.0f} kW',
                f'年费: {bc["C_annual"]/10000:.1f}万元',
                f'单位成本: {bc["C_unit"]:.4f}元/m³',
            ])
        else:
            summary.extend([
                '【结论】',
                '所有方案均不满足要求！',
                '建议: 选用更大扬程水泵',
            ])
        
        y_pos = 0.98
        for line in summary:
            if '═══' in line:
                ax9.text(0.5, y_pos, line, fontsize=11, fontweight='bold',
                        horizontalalignment='center', verticalalignment='top',
                        color='darkblue')
            elif '【' in line:
                ax9.text(0.05, y_pos, line, fontsize=10, fontweight='bold',
                        verticalalignment='top', color='darkred')
            elif line == '':
                y_pos -= 0.01
                continue
            else:
                ax9.text(0.1, y_pos, line, fontsize=9, verticalalignment='top',
                        family='monospace')
            y_pos -= 0.042
        
        ax9.set_title('设计结果汇总', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('/tmp/ch06_problem13_pump_station.png', dpi=150, bbox_inches='tight')
        print(f"图表已保存: /tmp/ch06_problem13_pump_station.png")
        plt.show()
    
    def print_results(self):
        """打印计算结果"""
        print("\n" + "="*70)
        print("第06章 水泵与水泵站 - 题13：泵站综合设计")
        print("="*70)
        
        # 设计条件
        print(f"\n【设计条件】")
        print(f"设计流量: Q = {self.Q_design} m³/s = {self.Q_design*1000} L/s")
        print(f"最低水位: {self.Z_low} m")
        print(f"最高水位: {self.Z_high} m")
        print(f"输水高程: {self.Z_out} m")
        print(f"管路总长: L = {self.L} m")
        print(f"管径: d = {self.d} m = {self.d*1000} mm")
        print(f"沿程阻力系数: λ = {self.lambd}")
        print(f"局部阻力系数和: Σζ = {self.zeta}")
        
        print(f"\n可选水泵:")
        for name, pump in self.pumps.items():
            print(f"{name}型: Q = {pump['Q']} m³/s, H = {pump['H']} m, "
                  f"η = {pump['eta']}, N = {pump['N']} kW")
        
        # (1) 管路特性曲线
        print(f"\n【问题1】管路特性曲线")
        
        Hst_low = self.static_head(self.Z_low)
        Hst_high = self.static_head(self.Z_high)
        
        print(f"\n静扬程:")
        print(f"最低水位: Hst = {self.Z_out} - {self.Z_low} = {Hst_low} m")
        print(f"最高水位: Hst = {self.Z_out} - {self.Z_high} = {Hst_high} m")
        
        A = np.pi * (self.d ** 2) / 4
        r = self.resistance_coefficient()
        
        print(f"\n管道面积:")
        print(f"A = πd²/4 = π×{self.d}²/4 = {A:.4f} m²")
        
        print(f"\n阻力系数:")
        print(f"r = (λL/d + Σζ)/(2gA²)")
        print(f"  = ({self.lambd}×{self.L}/{self.d} + {self.zeta})/(2×{self.g}×{A:.4f}²)")
        print(f"  = {r:.4f}")
        
        print(f"\n管路特性方程:")
        print(f"最低水位: H = {Hst_low} + {r:.4f}Q²")
        print(f"最高水位: H = {Hst_high} + {r:.4f}Q²")
        
        # 设计流量下的扬程
        H_design_low = self.pipe_characteristic(np.array([self.Q_design]), self.Z_low)[0]
        H_design_high = self.pipe_characteristic(np.array([self.Q_design]), self.Z_high)[0]
        
        print(f"\n设计流量所需扬程:")
        print(f"最低水位: H = {Hst_low} + {r:.4f}×{self.Q_design}² = {H_design_low:.2f} m")
        print(f"最高水位: H = {Hst_high} + {r:.4f}×{self.Q_design}² = {H_design_high:.2f} m")
        
        print(f"\n✓ 管路特性: H = Hst + {r:.4f}Q²")
        print(f"✓ 最不利工况(低水位): H = {H_design_low:.2f} m")
        
        # (2) 水泵选型
        print(f"\n【问题2】水泵选型")
        
        schemes = self.pump_selection()
        
        for name, scheme in schemes.items():
            print(f"\n方案{name}:")
            print(f"单泵: Q = {scheme['Q_single']} m³/s, H = {scheme['H_single']} m")
            print(f"所需台数: n = ⌈{self.Q_design}/{scheme['Q_single']}⌉ = {scheme['n_pumps']}台")
            print(f"总流量: Q = {scheme['Q_total']} m³/s")
            print(f"扬程裕度(低水位): ΔH = {scheme['H_single']} - {scheme['H_required_low']:.2f} "
                  f"= {scheme['margin_low']:.2f} m")
            print(f"扬程裕度(高水位): ΔH = {scheme['H_single']} - {scheme['H_required_high']:.2f} "
                  f"= {scheme['margin_high']:.2f} m")
            print(f"是否满足: {'✓ 满足' if scheme['is_adequate'] else '✗ 不满足'}")
        
        # (3) 运行工况分析
        print(f"\n【问题3】运行工况分析")
        
        for name, scheme in schemes.items():
            if not scheme['is_adequate']:
                continue
            
            print(f"\n方案{name}:")
            print(f"配置: {scheme['n_pumps']}台×{name}型")
            print(f"装机功率: {scheme['N_total']} kW")
            
            print(f"\n最低水位工况:")
            print(f"  所需扬程: {scheme['H_required_low']:.2f} m")
            print(f"  实际扬程: {scheme['H_single']} m")
            print(f"  实际功率: {scheme['N_actual_low']:.2f} kW")
            
            print(f"\n最高水位工况:")
            print(f"  所需扬程: {scheme['H_required_high']:.2f} m")
            print(f"  实际扬程: {scheme['H_single']} m")
            print(f"  实际功率: {scheme['N_actual_high']:.2f} kW")
        
        # (4) 能耗与经济性
        print(f"\n【问题4】能耗与经济性")
        
        print(f"\n假设条件:")
        T_annual = 4000
        price = 0.6
        print(f"年运行时间: {T_annual} h")
        print(f"电价: {price} 元/kWh")
        
        for name, scheme in schemes.items():
            if not scheme['is_adequate']:
                continue
            
            cost = self.annual_cost(scheme, T_annual, price)
            
            print(f"\n方案{name}:")
            print(f"平均功率: {cost['N_avg']:.2f} kW")
            print(f"年能耗: {cost['E_annual']:.0f} kWh = {cost['E_annual']/10000:.2f}万kWh")
            print(f"年电费: {cost['C_annual']:.0f} 元 = {cost['C_annual']/10000:.2f}万元")
            print(f"单位能耗: {cost['E_unit']:.6f} kWh/m³")
            print(f"单位成本: {cost['C_unit']:.6f} 元/m³")
        
        # (5) 年运行费用
        print(f"\n【问题5】年运行费用对比")
        
        costs = {}
        for name in schemes.keys():
            if schemes[name]['is_adequate']:
                costs[name] = self.annual_cost(schemes[name], T_annual, price)
        
        print(f"\n{'方案':<8} {'年能耗(万kWh)':<15} {'年电费(万元)':<15} {'单位成本(元/m³)':<18}")
        print(f"{'-'*60}")
        for name in costs.keys():
            print(f"{name:<8} {costs[name]['E_annual']/10000:<15.2f} "
                  f"{costs[name]['C_annual']/10000:<15.2f} "
                  f"{costs[name]['C_unit']:<18.6f}")
        
        # (6) 最优方案
        print(f"\n【问题6】最优方案推荐")
        
        if costs:
            best_scheme = min(costs, key=lambda x: costs[x]['C_annual'])
            bs = schemes[best_scheme]
            bc = costs[best_scheme]
            
            print(f"\n推荐方案: {best_scheme}型")
            print(f"\n理由:")
            print(f"1. 满足流量扬程要求")
            print(f"   • 设计流量: {self.Q_design*1000} L/s ≤ {bs['n_pumps']}×{bs['Q_single']*1000} = {bs['Q_total']*1000} L/s")
            print(f"   • 所需扬程: {bs['H_required_low']:.2f} m ≤ {bs['H_single']} m")
            print(f"   • 扬程裕度: {bs['margin_low']:.2f} m")
            
            print(f"\n2. 年运行费用最低")
            print(f"   • 年电费: {bc['C_annual']/10000:.2f}万元")
            print(f"   • 单位成本: {bc['C_unit']:.6f}元/m³")
            
            print(f"\n3. 配置合理")
            print(f"   • 台数: {bs['n_pumps']}台（便于调度）")
            print(f"   • 效率: {bs['eta']*100}%")
            print(f"   • 装机功率: {bs['N_total']} kW")
            
            print(f"\n方案参数:")
            print(f"型号: {best_scheme}型")
            print(f"台数: {bs['n_pumps']}台")
            print(f"单泵流量: {bs['Q_single']} m³/s = {bs['Q_single']*1000} L/s")
            print(f"单泵扬程: {bs['H_single']} m")
            print(f"单泵功率: {bs['N_rated']} kW")
            print(f"总装机功率: {bs['N_total']} kW")
        else:
            print(f"\n所有方案均不满足要求！")
            print(f"建议:")
            print(f"1. 选用更大扬程的水泵")
            print(f"2. 增大管径，减小管路损失")
            print(f"3. 缩短管路长度")
            print(f"4. 降低输水高程")
        
        # 考试要点
        print(f"\n【考试要点】")
        print(f"1. 管路特性: H = Hst + rQ²")
        print(f"2. 阻力系数: r = (λL/d + Σζ)/(2gA²)")
        print(f"3. 水泵选型: 扬程满足最不利工况")
        print(f"4. 台数选择: Q总 ≥ Q设计")
        print(f"5. 轴功率: N = ρgQH/η")
        print(f"6. 年能耗: E = N×T×负荷系数")
        print(f"7. 年运行费: C = E×电价")
        print(f"8. 综合比较: 技术+经济")
        
        print(f"\n{'='*70}\n")


def main():
    """主函数"""
    
    print("泵站综合设计")
    print("-" * 70)
    
    # 设计条件
    Q_design = 1.2  # 设计流量 [m³/s]
    Z_low = 20  # 最低水位 [m]
    Z_high = 22  # 最高水位 [m]
    Z_out = 45  # 输水高程 [m]
    L = 2000  # 管路总长 [m]
    d = 0.5  # 管径 [m]
    lambd = 0.03  # 沿程阻力系数
    zeta = 20  # 局部阻力系数和
    
    # 创建设计实例
    design = PumpStationDesign(Q_design, Z_low, Z_high, Z_out, L, d, lambd, zeta)
    
    # 添加可选水泵
    design.add_pump('A', Q=0.4, H=30, eta=0.75, N=160)
    design.add_pump('B', Q=0.6, H=28, eta=0.78, N=220)
    
    # 打印结果
    design.print_results()
    
    # 绘制分析图
    design.plot_analysis()


if __name__ == "__main__":
    main()
