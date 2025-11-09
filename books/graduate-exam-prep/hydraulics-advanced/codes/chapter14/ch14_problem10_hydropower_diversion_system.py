# -*- coding: utf-8 -*-
"""
第14章 压轴大题专项训练 - 题10：水电站引水系统设计

问题描述：
    某水电站装机N = 200MW，设计水头H = 80m
    引水系统方案：
    - 进水口高程 Z_in = 250m
    - 压力隧洞：L1 = 3000m, D1 = 5m, n = 0.025
    - 压力钢管：L2 = 500m, D2 = 4m, λ = 0.025
    - 蜗壳：Z_volute = 165m
    
    水力参数：
    - 设计流量Q = 300 m³/s
    - 沿程损失系数λ = 0.025
    - 局部损失系数Σξ = 5.0
    
    求：
    1. 水力计算（沿程、局部损失）
    2. 净水头与出力计算
    3. 管径优化选择（经济流速法）
    4. 水击计算与防护
    5. 洞室稳定性分析
    6. 综合技术经济评价

核心公式：
    1. hf = λ·L/D·v²/(2g)
    2. hj = Σξ·v²/(2g)
    3. N = 9.81·η·Q·H_净/1000
    4. Δp = ρ·c·Δv（水击压力）

考试要点：
    - 引水系统水力计算
    - 管径优化设计
    - 水击分析
    - 技术经济评价

作者: CHS-Books Team
日期: 2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, Dict, List

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class HydropowerDiversionSystem:
    """水电站引水系统设计"""
    
    def __init__(self, N_installed: float, H_design: float, Q_design: float,
                 Z_in: float, Z_volute: float, L1: float, D1: float,
                 L2: float, D2: float):
        self.N_installed = N_installed  # 装机容量 MW
        self.H_design = H_design  # 设计水头 m
        self.Q_design = Q_design  # 设计流量 m³/s
        self.Z_in = Z_in  # 进水口高程 m
        self.Z_volute = Z_volute  # 蜗壳高程 m
        self.L1 = L1  # 隧洞长度 m
        self.D1 = D1  # 隧洞直径 m
        self.L2 = L2  # 钢管长度 m
        self.D2 = D2  # 钢管直径 m
        
        # 水力参数
        self.lambda_tunnel = 0.025  # 隧洞沿程损失系数
        self.lambda_pipe = 0.025  # 钢管沿程损失系数
        self.sum_xi = 5.0  # 局部损失系数和
        
    def hydraulic_calculation(self) -> Dict:
        """水力计算"""
        # 隧洞段
        A1 = np.pi * self.D1**2 / 4
        v1 = self.Q_design / A1
        hf1 = self.lambda_tunnel * self.L1 / self.D1 * v1**2 / (2 * 9.81)
        
        # 钢管段
        A2 = np.pi * self.D2**2 / 4
        v2 = self.Q_design / A2
        hf2 = self.lambda_pipe * self.L2 / self.D2 * v2**2 / (2 * 9.81)
        
        # 总沿程损失
        hf_total = hf1 + hf2
        
        # 局部损失（取较大流速）
        v_max = max(v1, v2)
        hj_total = self.sum_xi * v_max**2 / (2 * 9.81)
        
        # 总水头损失
        h_loss = hf_total + hj_total
        
        # 毛水头
        H_gross = self.Z_in - self.Z_volute
        
        # 净水头
        H_net = H_gross - h_loss
        
        return {
            'v1': v1,
            'v2': v2,
            'hf1': hf1,
            'hf2': hf2,
            'hf_total': hf_total,
            'hj_total': hj_total,
            'h_loss': h_loss,
            'H_gross': H_gross,
            'H_net': H_net
        }
    
    def power_output(self, H_net: float, eta: float = 0.90) -> Dict:
        """出力计算"""
        # 额定出力
        N_rated = 9.81 * eta * self.Q_design * H_net / 1000  # MW
        
        # 与装机对比
        utilization_rate = N_rated / self.N_installed
        
        # 年发电量（假设年利用小时数7000）
        hours = 7000
        E_annual = N_rated * hours / 1e4  # 亿kW·h
        
        return {
            'N_rated': N_rated,
            'utilization_rate': utilization_rate,
            'E_annual': E_annual
        }
    
    def diameter_optimization(self) -> List[Dict]:
        """管径优化"""
        # 经济流速法：v_经济 = √(K·c/λ)
        # 简化：v = 3-6 m/s
        
        options = []
        
        # 隧洞直径优化
        D1_options = [4.5, 5.0, 5.5]  # m
        for D1 in D1_options:
            A1 = np.pi * D1**2 / 4
            v1 = self.Q_design / A1
            hf1 = self.lambda_tunnel * self.L1 / D1 * v1**2 / (2 * 9.81)
            
            # 工程量
            volume1 = A1 * self.L1
            
            # 投资（简化，元/m³）
            unit_price_tunnel = 5000
            cost1 = volume1 * unit_price_tunnel / 1e6  # 百万元
            
            options.append({
                'D1': D1,
                'v1': v1,
                'hf1': hf1,
                'volume1': volume1,
                'cost1': cost1
            })
        
        return options
    
    def water_hammer_analysis(self) -> Dict:
        """水击计算"""
        # 水击波速
        # c = √(K/ρ)，简化取c = 1000 m/s
        c = 1000  # m/s
        
        # 钢管段流速
        A2 = np.pi * self.D2**2 / 4
        v2 = self.Q_design / A2
        
        # 关闭时间（取5秒）
        T_close = 5.0  # s
        
        # 临界关闭时间
        T_critical = 2 * (self.L1 + self.L2) / c
        
        # 判断水击类型
        if T_close < T_critical:
            hammer_type = "直接水击"
            # 最大水击压力（Joukowsky公式）
            delta_p = 1000 * c * v2 / 1e6  # MPa
        else:
            hammer_type = "间接水击"
            # 简化计算
            delta_p = 1000 * c * v2 / T_close * T_critical / 1e6  # MPa
        
        # 最大压力
        p_normal = 1000 * 9.81 * self.H_design / 1e6  # MPa
        p_max = p_normal + delta_p
        
        return {
            'c': c,
            'v2': v2,
            'T_close': T_close,
            'T_critical': T_critical,
            'hammer_type': hammer_type,
            'delta_p': delta_p,
            'p_normal': p_normal,
            'p_max': p_max
        }
    
    def stability_analysis(self) -> Dict:
        """洞室稳定性分析"""
        # 围岩类别判断（简化）
        # 假设III类围岩
        rock_class = "III"
        
        # 内水压力
        p_internal = 1000 * 9.81 * self.H_design / 1e6  # MPa
        
        # 围岩承载力（III类围岩，简化取5-10MPa）
        p_allowable = 7.0  # MPa
        
        # 安全系数
        K_safety = p_allowable / p_internal
        
        # 衬砌设计
        if K_safety < 2.0:
            lining_type = "钢筋混凝土衬砌"
            thickness = 0.8  # m
        elif K_safety < 3.0:
            lining_type = "混凝土衬砌"
            thickness = 0.5  # m
        else:
            lining_type = "喷锚支护"
            thickness = 0.3  # m
        
        return {
            'rock_class': rock_class,
            'p_internal': p_internal,
            'p_allowable': p_allowable,
            'K_safety': K_safety,
            'lining_type': lining_type,
            'thickness': thickness
        }
    
    def techno_economic_evaluation(self, hydraulic: Dict, power: Dict,
                                    stability: Dict) -> Dict:
        """技术经济评价"""
        # 投资估算
        # 隧洞工程
        V_tunnel = np.pi * self.D1**2 / 4 * self.L1
        cost_tunnel = V_tunnel * 5000 / 1e6  # 百万元
        
        # 钢管工程
        V_pipe = np.pi * self.D2**2 / 4 * self.L2
        cost_pipe = V_pipe * 20000 / 1e6  # 百万元
        
        # 厂房工程（简化）
        cost_powerhouse = 50  # 百万元
        
        # 总投资
        total_investment = cost_tunnel + cost_pipe + cost_powerhouse
        
        # 单位千瓦投资
        unit_investment = total_investment * 1e6 / (self.N_installed * 1e3)  # 元/kW
        
        # 经济效益
        electricity_price = 0.4  # 元/kW·h
        annual_revenue = power['E_annual'] * 1e8 * electricity_price / 1e6  # 百万元
        
        # 投资回收期（简化，不考虑折现）
        payback_period = total_investment / annual_revenue
        
        # NPV（20年，折现率8%）
        discount_rate = 0.08
        years = 20
        NPV = sum([annual_revenue / (1 + discount_rate)**t 
                   for t in range(1, years+1)]) - total_investment
        
        return {
            'cost_tunnel': cost_tunnel,
            'cost_pipe': cost_pipe,
            'cost_powerhouse': cost_powerhouse,
            'total_investment': total_investment,
            'unit_investment': unit_investment,
            'annual_revenue': annual_revenue,
            'payback_period': payback_period,
            'NPV': NPV
        }
    
    def plot_analysis(self):
        """绘制分析图表"""
        fig = plt.figure(figsize=(16, 12))
        
        hydraulic = self.hydraulic_calculation()
        power = self.power_output(hydraulic['H_net'])
        options = self.diameter_optimization()
        hammer = self.water_hammer_analysis()
        stability = self.stability_analysis()
        economic = self.techno_economic_evaluation(hydraulic, power, stability)
        
        # 1. 引水系统剖面图
        ax1 = plt.subplot(3, 3, 1)
        
        # 纵断面
        x_points = [0, self.L1, self.L1 + self.L2]
        z_points = [self.Z_in, self.Z_in - 10, self.Z_volute]
        
        ax1.plot(x_points, z_points, 'b-', linewidth=3, label='引水系统')
        ax1.plot([0], [self.Z_in], 'go', markersize=12, label='进水口')
        ax1.plot([self.L1 + self.L2], [self.Z_volute], 'ro', markersize=12, label='蜗壳')
        
        # 标注
        ax1.text(self.L1/2, self.Z_in-5, f'隧洞\nL={self.L1}m\nD={self.D1}m',
                ha='center', fontsize=9, bbox=dict(boxstyle='round', facecolor='lightblue'))
        ax1.text(self.L1+self.L2/2, (self.Z_in-10+self.Z_volute)/2,
                f'钢管\nL={self.L2}m\nD={self.D2}m',
                ha='center', fontsize=9, bbox=dict(boxstyle='round', facecolor='pink'))
        
        ax1.set_xlabel('水平距离 (m)', fontsize=10)
        ax1.set_ylabel('高程 (m)', fontsize=10)
        ax1.set_title('引水系统纵断面', fontsize=12, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. 水头损失分配
        ax2 = plt.subplot(3, 3, 2)
        
        loss_items = ['隧洞沿程', '钢管沿程', '局部损失']
        loss_values = [hydraulic['hf1'], hydraulic['hf2'], hydraulic['hj_total']]
        colors_loss = ['blue', 'green', 'orange']
        
        wedges, texts, autotexts = ax2.pie(loss_values, labels=loss_items,
                                           autopct='%1.1f%%', colors=colors_loss,
                                           startangle=90)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(9)
            autotext.set_fontweight('bold')
        
        ax2.set_title(f'水头损失分配\n(总损失{hydraulic["h_loss"]:.2f}m)',
                     fontsize=12, fontweight='bold')
        
        # 3. 水头计算示意图
        ax3 = plt.subplot(3, 3, 3)
        
        water_heads = ['毛水头', '净水头', '设计水头']
        values = [hydraulic['H_gross'], hydraulic['H_net'], self.H_design]
        colors_head = ['blue', 'green', 'red']
        
        bars = ax3.bar(water_heads, values, color=colors_head, 
                      alpha=0.7, edgecolor='black')
        
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2, height,
                    f'{val:.1f}m', ha='center', va='bottom',
                    fontsize=10, fontweight='bold')
        
        # 标注损失
        ax3.text(1, hydraulic['H_gross'] - hydraulic['h_loss']/2,
                f'损失\n{hydraulic["h_loss"]:.2f}m',
                ha='center', fontsize=9, color='red',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
        
        ax3.set_ylabel('水头 (m)', fontsize=10)
        ax3.set_title('水头计算', fontsize=12, fontweight='bold')
        ax3.grid(True, alpha=0.3, axis='y')
        
        # 4. 管径优化对比
        ax4 = plt.subplot(3, 3, 4)
        
        D1_values = [opt['D1'] for opt in options]
        hf1_values = [opt['hf1'] for opt in options]
        cost1_values = [opt['cost1'] for opt in options]
        
        ax4_twin = ax4.twinx()
        
        line1 = ax4.plot(D1_values, hf1_values, 'b-o', linewidth=2, label='水头损失')
        line2 = ax4_twin.plot(D1_values, cost1_values, 'r-s', linewidth=2, label='工程投资')
        
        ax4.set_xlabel('隧洞直径 D1 (m)', fontsize=10)
        ax4.set_ylabel('水头损失 (m)', fontsize=10, color='blue')
        ax4_twin.set_ylabel('投资 (百万元)', fontsize=10, color='red')
        ax4.tick_params(axis='y', labelcolor='blue')
        ax4_twin.tick_params(axis='y', labelcolor='red')
        
        # 合并图例
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax4.legend(lines, labels, loc='upper left')
        
        ax4.set_title('管径优化分析', fontsize=12, fontweight='bold')
        ax4.grid(True, alpha=0.3)
        
        # 5. 水击压力分析
        ax5 = plt.subplot(3, 3, 5)
        
        pressure_items = ['正常压力', '水击升压', '最大压力']
        pressure_values = [hammer['p_normal'], hammer['delta_p'], hammer['p_max']]
        colors_pressure = ['blue', 'orange', 'red']
        
        bars = ax5.bar(pressure_items, pressure_values, color=colors_pressure,
                      alpha=0.7, edgecolor='black')
        
        for bar, val in zip(bars, pressure_values):
            height = bar.get_height()
            ax5.text(bar.get_x() + bar.get_width()/2, height,
                    f'{val:.2f}', ha='center', va='bottom',
                    fontsize=9, fontweight='bold')
        
        ax5.set_ylabel('压力 (MPa)', fontsize=10)
        ax5.set_title(f'水击压力分析\n({hammer["hammer_type"]})',
                     fontsize=12, fontweight='bold')
        ax5.grid(True, alpha=0.3, axis='y')
        
        # 6. 出力与装机对比
        ax6 = plt.subplot(3, 3, 6)
        
        power_items = ['装机容量', '额定出力']
        power_values = [self.N_installed, power['N_rated']]
        colors_power = ['blue', 'green']
        
        bars = ax6.bar(power_items, power_values, color=colors_power,
                      alpha=0.7, edgecolor='black')
        
        for bar, val in zip(bars, power_values):
            height = bar.get_height()
            ax6.text(bar.get_x() + bar.get_width()/2, height,
                    f'{val:.1f}MW', ha='center', va='bottom',
                    fontsize=10, fontweight='bold')
        
        ax6.set_ylabel('出力 (MW)', fontsize=10)
        ax6.set_title(f'出力分析\n(利用率{power["utilization_rate"]:.1%})',
                     fontsize=12, fontweight='bold')
        ax6.grid(True, alpha=0.3, axis='y')
        
        # 7. 投资构成
        ax7 = plt.subplot(3, 3, 7)
        
        cost_items = ['隧洞', '钢管', '厂房']
        cost_values = [economic['cost_tunnel'], economic['cost_pipe'],
                      economic['cost_powerhouse']]
        colors_cost = ['#8B4513', '#87CEEB', '#FFD700']
        
        wedges, texts, autotexts = ax7.pie(cost_values, labels=cost_items,
                                           autopct='%1.1f%%', colors=colors_cost,
                                           startangle=90)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(9)
            autotext.set_fontweight('bold')
        
        ax7.set_title(f'投资构成\n(总投资{economic["total_investment"]:.0f}百万元)',
                     fontsize=12, fontweight='bold')
        
        # 8. 稳定性与衬砌
        ax8 = plt.subplot(3, 3, 8)
        ax8.axis('off')
        
        ax8.text(0.5, 0.95, '洞室稳定性分析', fontsize=11, ha='center', fontweight='bold')
        ax8.text(0.1, 0.80, f'围岩类别: {stability["rock_class"]}', fontsize=10)
        ax8.text(0.1, 0.70, f'内水压力: {stability["p_internal"]:.2f} MPa', fontsize=10)
        ax8.text(0.1, 0.60, f'容许压力: {stability["p_allowable"]:.2f} MPa', fontsize=10)
        ax8.text(0.1, 0.50, f'安全系数: K = {stability["K_safety"]:.2f}', fontsize=10)
        
        if stability['K_safety'] > 2.0:
            color = 'green'
            status = '✓ 稳定'
        else:
            color = 'red'
            status = '△ 需加固'
        
        ax8.text(0.1, 0.35, f'稳定状态: {status}', fontsize=11, color=color, fontweight='bold')
        ax8.text(0.1, 0.22, f'衬砌类型: {stability["lining_type"]}', fontsize=10)
        ax8.text(0.1, 0.12, f'衬砌厚度: {stability["thickness"]:.1f} m', fontsize=10)
        
        ax8.set_title('稳定性评价', fontsize=12, fontweight='bold')
        
        # 9. 综合评价表
        ax9 = plt.subplot(3, 3, 9)
        ax9.axis('off')
        
        table_data = [
            ['项目', '数值', '单位'],
            ['设计流量', f'{self.Q_design}', 'm³/s'],
            ['净水头', f'{hydraulic["H_net"]:.1f}', 'm'],
            ['额定出力', f'{power["N_rated"]:.1f}', 'MW'],
            ['年发电量', f'{power["E_annual"]:.2f}', '亿kW·h'],
            ['总投资', f'{economic["total_investment"]:.0f}', '百万元'],
            ['单位千瓦', f'{economic["unit_investment"]:.0f}', '元/kW'],
            ['回收期', f'{economic["payback_period"]:.1f}', '年'],
            ['NPV', f'{economic["NPV"]:.0f}', '百万元']
        ]
        
        table = ax9.table(cellText=table_data, cellLoc='center', loc='center',
                         colWidths=[0.40, 0.30, 0.25])
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1, 2.0)
        
        for i in range(3):
            table[(0, i)].set_facecolor('#4472C4')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        # 高亮关键指标
        for i in [3, 5, 7]:
            for j in range(3):
                table[(i, j)].set_facecolor('#FFF9E6')
        
        ax9.set_title('综合评价汇总', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('/tmp/ch14_problem10_hydropower_diversion_system.png', dpi=150, bbox_inches='tight')
        print(f"图表已保存: /tmp/ch14_problem10_hydropower_diversion_system.png")
        plt.show()
    
    def print_results(self):
        """打印结果"""
        print("\n" + "="*70)
        print("第14章 压轴大题 - 题10：水电站引水系统设计")
        print("="*70)
        
        hydraulic = self.hydraulic_calculation()
        power = self.power_output(hydraulic['H_net'])
        hammer = self.water_hammer_analysis()
        stability = self.stability_analysis()
        economic = self.techno_economic_evaluation(hydraulic, power, stability)
        
        print(f"\n【1. 水力计算】")
        print(f"隧洞段: L1={self.L1}m, D1={self.D1}m")
        print(f"  流速: v1 = {hydraulic['v1']:.3f} m/s")
        print(f"  沿程损失: hf1 = {hydraulic['hf1']:.3f} m")
        print(f"钢管段: L2={self.L2}m, D2={self.D2}m")
        print(f"  流速: v2 = {hydraulic['v2']:.3f} m/s")
        print(f"  沿程损失: hf2 = {hydraulic['hf2']:.3f} m")
        print(f"局部损失: hj = {hydraulic['hj_total']:.3f} m")
        print(f"总损失: h_损 = {hydraulic['h_loss']:.3f} m")
        
        print(f"\n【2. 水头与出力】")
        print(f"毛水头: H_毛 = {hydraulic['H_gross']} m")
        print(f"净水头: H_净 = {hydraulic['H_net']:.2f} m")
        print(f"装机容量: N_装 = {self.N_installed} MW")
        print(f"额定出力: N_额 = {power['N_rated']:.2f} MW")
        print(f"装机利用率: {power['utilization_rate']:.1%}")
        print(f"年发电量: E = {power['E_annual']:.2f} 亿kW·h")
        
        print(f"\n【3. 水击分析】")
        print(f"波速: c = {hammer['c']} m/s")
        print(f"关闭时间: T = {hammer['T_close']} s")
        print(f"临界时间: Tc = {hammer['T_critical']:.3f} s")
        print(f"水击类型: {hammer['hammer_type']}")
        print(f"正常压力: p = {hammer['p_normal']:.3f} MPa")
        print(f"水击升压: Δp = {hammer['delta_p']:.3f} MPa")
        print(f"最大压力: p_max = {hammer['p_max']:.3f} MPa")
        
        print(f"\n【4. 稳定性分析】")
        print(f"围岩类别: {stability['rock_class']}")
        print(f"内水压力: {stability['p_internal']:.3f} MPa")
        print(f"容许压力: {stability['p_allowable']:.3f} MPa")
        print(f"安全系数: K = {stability['K_safety']:.2f}")
        print(f"衬砌类型: {stability['lining_type']}")
        print(f"衬砌厚度: {stability['thickness']} m")
        
        print(f"\n【5. 技术经济评价】")
        print(f"隧洞投资: {economic['cost_tunnel']:.1f} 百万元")
        print(f"钢管投资: {economic['cost_pipe']:.1f} 百万元")
        print(f"厂房投资: {economic['cost_powerhouse']:.1f} 百万元")
        print(f"总投资: {economic['total_investment']:.1f} 百万元")
        print(f"单位千瓦投资: {economic['unit_investment']:.0f} 元/kW")
        print(f"年发电收入: {economic['annual_revenue']:.1f} 百万元")
        print(f"投资回收期: {economic['payback_period']:.1f} 年")
        print(f"NPV(20年): {economic['NPV']:.0f} 百万元")
        
        if economic['payback_period'] < 15 and economic['NPV'] > 0:
            print(f"✓ 工程经济可行")
        else:
            print(f"△ 需进一步优化")
        
        print(f"\n✓ 水电站引水系统设计完成")
        print(f"\n{'='*70}\n")


def main():
    N_installed = 200  # MW
    H_design = 80  # m
    Q_design = 300  # m³/s
    Z_in = 250  # m
    Z_volute = 165  # m
    L1 = 3000  # m
    D1 = 5  # m
    L2 = 500  # m
    D2 = 4  # m
    
    diversion = HydropowerDiversionSystem(N_installed, H_design, Q_design,
                                          Z_in, Z_volute, L1, D1, L2, D2)
    diversion.print_results()
    diversion.plot_analysis()


if __name__ == "__main__":
    main()
