# -*- coding: utf-8 -*-
"""
第11章 水工建筑物 - 题10：土石坝设计

问题描述：
    某土石坝最大坝高H = 60m，坝顶宽度b = 10m
    上游坡比m1 = 3.0，下游坡比m2 = 2.5
    正常蓄水位h1 = 55m，设计洪水位hd = 58m
    土料干密度ρd = 1.8 t/m³，饱和密度ρsat = 2.0 t/m³
    
    求：
    1. 坝体断面尺寸
    2. 坝体填筑方量
    3. 边坡稳定分析
    4. 渗流安全分析
    5. 经济指标估算

核心公式：
    1. 坝底宽度：B = b + m1·H + m2·H
    2. 边坡稳定：Fs = (c·L + W·cos(α)·tan(φ))/(W·sin(α))
    3. 浸润线：y² = h₁² - (h₁²/L)·x
    4. 单宽渗流量：q = k·h₁/L

考试要点：
    - 土石坝断面设计
    - 边坡稳定计算
    - 渗流分析
    - 工程量估算

作者: CHS-Books Team
日期: 2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, Dict, List

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class EarthDamDesign:
    """土石坝设计"""
    
    def __init__(self, H: float, b: float, m1: float, m2: float,
                 h1: float, hd: float, rho_d: float, rho_sat: float):
        self.H = H  # 最大坝高
        self.b = b  # 坝顶宽度
        self.m1 = m1  # 上游坡比
        self.m2 = m2  # 下游坡比
        self.h1 = h1  # 正常蓄水位
        self.hd = hd  # 设计洪水位
        self.rho_d = rho_d  # 干密度 t/m³
        self.rho_sat = rho_sat  # 饱和密度 t/m³
        self.g = 9.8  # m/s²
        self.k = 1e-5  # 渗透系数 m/s
        
    def dam_dimensions(self) -> Dict:
        """坝体尺寸"""
        # 上游坡脚宽度
        B1 = self.m1 * self.H
        # 下游坡脚宽度
        B2 = self.m2 * self.H
        # 坝底总宽
        B = self.b + B1 + B2
        
        return {
            'B': B,
            'B1': B1,
            'B2': B2,
            'b': self.b,
            'H': self.H
        }
    
    def cross_section_area(self) -> float:
        """坝体横断面面积"""
        dims = self.dam_dimensions()
        
        # 梯形面积
        A = (self.b + dims['B']) * self.H / 2
        return A
    
    def fill_volume(self, L: float = 1000) -> Dict:
        """
        坝体填筑方量（假设坝轴线长度L）
        """
        A = self.cross_section_area()
        
        # 总方量
        V_total = A * L
        
        # 实方（压实后）
        V_solid = V_total
        
        # 松方（施工方量，松方系数1.25）
        V_loose = V_total * 1.25
        
        return {
            'A': A,
            'L': L,
            'V_solid': V_solid,
            'V_loose': V_loose
        }
    
    def slope_stability(self, alpha: float = 20, c: float = 15, phi: float = 25) -> Tuple[float, bool]:
        """
        边坡稳定分析（简化Bishop法）
        Fs = (c·L + W·cos(α)·tan(φ))/(W·sin(α))
        
        参数：
        alpha - 滑弧角度（度）
        c - 粘聚力（kPa）
        phi - 内摩擦角（度）
        """
        # 转为弧度
        alpha_rad = np.deg2rad(alpha)
        phi_rad = np.deg2rad(phi)
        
        # 简化计算：假设滑动体为三角形
        # 滑动体重量（kN/m）
        h_slide = self.H * 0.6  # 滑动体高度
        L_slide = h_slide * self.m2  # 滑动体底边长
        A_slide = 0.5 * h_slide * L_slide  # 滑动体面积
        
        gamma = self.rho_d * self.g  # 重度
        W = gamma * A_slide  # 重量
        
        # 滑动面长度
        L_arc = L_slide / np.cos(alpha_rad)
        
        # 抗滑力
        F_resist = c * L_arc + W * np.cos(alpha_rad) * np.tan(phi_rad)
        
        # 滑动力
        F_slide = W * np.sin(alpha_rad)
        
        # 安全系数
        Fs = F_resist / F_slide
        is_safe = Fs >= 1.3
        
        return Fs, is_safe
    
    def phreatic_line(self, n_points: int = 100) -> Tuple[np.ndarray, np.ndarray]:
        """
        浸润线（抛物线）
        y² = h₁² - (h₁²/L)·x
        """
        dims = self.dam_dimensions()
        
        # 渗流长度（上游坡面+坝底部分）
        L = dims['B1'] + dims['B'] * 0.3
        
        x = np.linspace(0, L, n_points)
        y = np.sqrt(self.h1 ** 2 - (self.h1 ** 2 / L) * x)
        
        return x, y
    
    def seepage_discharge(self) -> float:
        """
        单宽渗流量
        q = k·h₁/L（简化Dupuit公式）
        """
        dims = self.dam_dimensions()
        L = dims['B1'] + dims['B'] * 0.3
        
        q = self.k * self.h1 / L
        return q
    
    def freeboard(self) -> Dict:
        """
        超高计算（风浪爬高）
        """
        # 风浪爬高（经验公式）
        # R = K·h_wave，K=1.5
        h_wave = 0.5  # 波高，假设0.5m
        R = 1.5 * h_wave
        
        # 安全加高
        a = 0.5  # 安全加高0.5m
        
        # 最小超高
        e = R + a
        
        # 实际超高
        e_actual = self.H - self.hd
        
        is_sufficient = e_actual >= e
        
        return {
            'R': R,
            'a': a,
            'e_required': e,
            'e_actual': e_actual,
            'is_sufficient': is_sufficient
        }
    
    def cost_estimate(self, L: float = 1000) -> Dict:
        """
        经济指标估算
        """
        volumes = self.fill_volume(L)
        
        # 单价（元/m³）
        unit_price_excavation = 15  # 开挖
        unit_price_fill = 25  # 填筑
        unit_price_compaction = 10  # 碾压
        
        # 各项费用
        cost_excavation = volumes['V_loose'] * unit_price_excavation
        cost_fill = volumes['V_solid'] * unit_price_fill
        cost_compaction = volumes['V_solid'] * unit_price_compaction
        
        # 总费用
        cost_total = cost_excavation + cost_fill + cost_compaction
        
        # 单位库容造价（元/m³库容）
        reservoir_capacity = L * self.h1 * 100  # 假设库容（简化）
        cost_per_capacity = cost_total / reservoir_capacity
        
        return {
            'cost_excavation': cost_excavation,
            'cost_fill': cost_fill,
            'cost_compaction': cost_compaction,
            'cost_total': cost_total,
            'reservoir_capacity': reservoir_capacity,
            'cost_per_capacity': cost_per_capacity
        }
    
    def plot_analysis(self):
        """绘制分析图表"""
        fig = plt.figure(figsize=(16, 12))
        
        dims = self.dam_dimensions()
        A = self.cross_section_area()
        volumes = self.fill_volume()
        Fs, is_safe = self.slope_stability()
        q = self.seepage_discharge()
        freeboard_info = self.freeboard()
        costs = self.cost_estimate()
        
        # 1. 坝体断面图
        ax1 = plt.subplot(3, 3, 1)
        
        # 坝体轮廓
        x_dam = [0, dims['B1'], dims['B1'], dims['B1']+self.b, dims['B'], dims['B'], 0]
        y_dam = [0, self.H, self.H, self.H, 0, 0, 0]
        ax1.fill(x_dam, y_dam, color='tan', alpha=0.5, label='坝体')
        ax1.plot(x_dam, y_dam, 'k-', linewidth=2)
        
        # 水位线
        ax1.plot([0, dims['B1']], [self.h1, self.H], 'b--', linewidth=2, label=f'正常水位{self.h1}m')
        ax1.plot([0, dims['B1']], [self.hd, self.H], 'r--', linewidth=2, label=f'设计水位{self.hd}m')
        
        # 上游水体
        ax1.fill([0, 0, dims['B1']], [0, self.h1, self.H], 
                color='lightblue', alpha=0.3)
        
        # 浸润线
        x_phreatic, y_phreatic = self.phreatic_line()
        ax1.plot(x_phreatic, y_phreatic, 'g-', linewidth=2, label='浸润线')
        
        # 标注尺寸
        ax1.text(dims['B']/2, -5, f"B={dims['B']:.1f}m", ha='center', fontsize=10, fontweight='bold')
        ax1.text(dims['B1']/2, self.H+2, f"b={self.b}m", ha='center', fontsize=9)
        ax1.text(dims['B1']-10, self.H/2, f"m₁={self.m1}", ha='center', fontsize=9, color='blue')
        ax1.text(dims['B1']+self.b+20, self.H/2, f"m₂={self.m2}", ha='center', fontsize=9, color='red')
        
        ax1.set_xlabel('水平距离 (m)', fontsize=10)
        ax1.set_ylabel('高程 (m)', fontsize=10)
        ax1.set_title('土石坝断面设计', fontsize=12, fontweight='bold')
        ax1.legend(fontsize=8)
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim(-10, dims['B']+10)
        ax1.set_ylim(-8, self.H+5)
        
        # 2. 设计参数
        ax2 = plt.subplot(3, 3, 2)
        ax2.axis('off')
        
        ax2.text(0.5, 0.95, '设计参数', fontsize=11, ha='center', fontweight='bold')
        ax2.text(0.1, 0.82, f'最大坝高: H = {self.H} m', fontsize=10, color='red')
        ax2.text(0.1, 0.72, f'坝顶宽度: b = {self.b} m', fontsize=10)
        ax2.text(0.1, 0.62, f'坝底宽度: B = {dims["B"]:.1f} m', fontsize=10)
        ax2.text(0.1, 0.52, f'上游坡比: m₁ = {self.m1}', fontsize=10)
        ax2.text(0.1, 0.42, f'下游坡比: m₂ = {self.m2}', fontsize=10)
        ax2.text(0.1, 0.32, f'正常水位: {self.h1} m', fontsize=10, color='blue')
        ax2.text(0.1, 0.22, f'设计水位: {self.hd} m', fontsize=10)
        ax2.text(0.1, 0.12, f'断面面积: A = {A:.0f} m²', fontsize=10, color='green')
        ax2.text(0.1, 0.02, f'干密度: ρd = {self.rho_d} t/m³', fontsize=10)
        
        ax2.set_title('基本参数', fontsize=12, fontweight='bold')
        
        # 3. 填筑方量
        ax3 = plt.subplot(3, 3, 3)
        
        volume_types = ['实方', '松方']
        volume_values = [volumes['V_solid']/10000, volumes['V_loose']/10000]  # 转为万m³
        colors_volume = ['green', 'orange']
        
        bars = ax3.bar(volume_types, volume_values, color=colors_volume, 
                      alpha=0.7, edgecolor='black')
        
        ax3.set_ylabel('方量 (万m³)', fontsize=10)
        ax3.set_title(f'填筑方量 (L={volumes["L"]}m)', fontsize=12, fontweight='bold')
        ax3.grid(True, alpha=0.3, axis='y')
        
        for bar, V in zip(bars, volume_values):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height,
                    f'{V:.2f}', ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        # 4. 边坡稳定
        ax4 = plt.subplot(3, 3, 4)
        ax4.axis('off')
        
        ax4.text(0.5, 0.95, '边坡稳定分析', fontsize=11, ha='center', fontweight='bold')
        ax4.text(0.1, 0.78, '简化Bishop法', fontsize=10, color='gray')
        ax4.text(0.1, 0.65, f'滑弧角度: α = 20°', fontsize=10)
        ax4.text(0.1, 0.55, f'粘聚力: c = 15 kPa', fontsize=10)
        ax4.text(0.1, 0.45, f'内摩擦角: φ = 25°', fontsize=10)
        ax4.text(0.1, 0.30, f'Fs = {Fs:.2f}', fontsize=12, 
                color='green' if is_safe else 'red', fontweight='bold')
        
        if is_safe:
            ax4.text(0.1, 0.15, '✓ 满足要求（Fs≥1.3）', fontsize=10, color='green', fontweight='bold')
        else:
            ax4.text(0.1, 0.15, '✗ 不满足要求！', fontsize=10, color='red', fontweight='bold')
        
        ax4.text(0.1, 0.02, f'稳定状态: {"稳定" if is_safe else "不稳定"}', fontsize=9)
        
        ax4.set_title('稳定计算', fontsize=12, fontweight='bold')
        
        # 5. 渗流分析
        ax5 = plt.subplot(3, 3, 5)
        
        x_ph, y_ph = self.phreatic_line()
        
        ax5.plot(x_ph, y_ph, 'b-', linewidth=3, label='浸润线')
        ax5.fill_between(x_ph, 0, y_ph, color='lightblue', alpha=0.3)
        
        # 上游水位
        ax5.axhline(self.h1, color='blue', linestyle='--', linewidth=2, label=f'蓄水位{self.h1}m')
        
        ax5.set_xlabel('距离 (m)', fontsize=10)
        ax5.set_ylabel('高程 (m)', fontsize=10)
        ax5.set_title('浸润线分析', fontsize=12, fontweight='bold')
        ax5.legend()
        ax5.grid(True, alpha=0.3)
        ax5.set_xlim(0, max(x_ph)+10)
        ax5.set_ylim(0, self.h1+5)
        
        # 6. 超高验算
        ax6 = plt.subplot(3, 3, 6)
        ax6.axis('off')
        
        fb = freeboard_info
        ax6.text(0.5, 0.95, '超高验算', fontsize=11, ha='center', fontweight='bold')
        ax6.text(0.1, 0.78, f'波浪爬高: R = {fb["R"]:.2f} m', fontsize=10)
        ax6.text(0.1, 0.68, f'安全加高: a = {fb["a"]:.2f} m', fontsize=10)
        ax6.text(0.1, 0.58, f'所需超高: e = {fb["e_required"]:.2f} m', fontsize=10, color='red')
        ax6.text(0.1, 0.48, f'实际超高: {fb["e_actual"]:.2f} m', fontsize=10, color='blue')
        
        if fb['is_sufficient']:
            ax6.text(0.1, 0.30, '✓ 超高满足要求', fontsize=10, color='green', fontweight='bold')
        else:
            ax6.text(0.1, 0.30, '✗ 超高不足！', fontsize=10, color='red', fontweight='bold')
        
        ax6.text(0.1, 0.15, f'最大坝高: {self.H} m', fontsize=9)
        ax6.text(0.1, 0.05, f'设计水位: {self.hd} m', fontsize=9)
        
        ax6.set_title('超高计算', fontsize=12, fontweight='bold')
        
        # 7. 造价分布
        ax7 = plt.subplot(3, 3, 7)
        
        cost_items = ['开挖', '填筑', '碾压']
        cost_values = [costs['cost_excavation']/10000, 
                      costs['cost_fill']/10000, 
                      costs['cost_compaction']/10000]  # 转为万元
        colors_cost = ['brown', 'green', 'orange']
        
        wedges, texts, autotexts = ax7.pie(cost_values, labels=cost_items, 
                                           autopct='%1.1f%%', colors=colors_cost,
                                           startangle=90)
        
        for text in texts:
            text.set_fontsize(10)
            text.set_fontweight('bold')
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(9)
            autotext.set_fontweight('bold')
        
        ax7.set_title(f'造价分布 (总计{costs["cost_total"]/10000:.0f}万元)', 
                     fontsize=12, fontweight='bold')
        
        # 8. 坝高影响
        ax8 = plt.subplot(3, 3, 8)
        
        H_range = np.linspace(30, 80, 50)
        V_range = []
        Cost_range = []
        
        for H_val in H_range:
            dam_temp = EarthDamDesign(H_val, self.b, self.m1, self.m2,
                                     H_val-5, H_val-2, self.rho_d, self.rho_sat)
            vol_temp = dam_temp.fill_volume()
            cost_temp = dam_temp.cost_estimate()
            V_range.append(vol_temp['V_solid']/10000)
            Cost_range.append(cost_temp['cost_total']/10000)
        
        ax8_twin = ax8.twinx()
        
        line1 = ax8.plot(H_range, V_range, 'b-', linewidth=2, label='方量')
        line2 = ax8_twin.plot(H_range, Cost_range, 'r-', linewidth=2, label='造价')
        ax8.plot(self.H, volumes['V_solid']/10000, 'bo', markersize=10)
        ax8_twin.plot(self.H, costs['cost_total']/10000, 'ro', markersize=10)
        
        ax8.set_xlabel('坝高 H (m)', fontsize=10)
        ax8.set_ylabel('方量 (万m³)', fontsize=10, color='blue')
        ax8_twin.set_ylabel('造价 (万元)', fontsize=10, color='red')
        ax8.set_title('坝高影响分析', fontsize=12, fontweight='bold')
        ax8.grid(True, alpha=0.3)
        
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax8.legend(lines, labels, loc='upper left')
        
        # 9. 结果汇总表
        ax9 = plt.subplot(3, 3, 9)
        ax9.axis('off')
        
        table_data = [
            ['项目', '数值', '单位'],
            ['坝高', f'{self.H}', 'm'],
            ['坝底宽', f'{dims["B"]:.1f}', 'm'],
            ['断面面积', f'{A:.0f}', 'm²'],
            ['填筑方量', f'{volumes["V_solid"]/10000:.2f}', '万m³'],
            ['边坡安全系数', f'{Fs:.2f}', '-'],
            ['渗流量', f'{q*86400:.2e}', 'm²/d'],
            ['工程总造价', f'{costs["cost_total"]/10000:.0f}', '万元']
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
        for i in [1, 5, 8]:
            for j in range(3):
                table[(i, j)].set_facecolor('#FFF9E6')
        
        ax9.set_title('设计结果汇总', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('/tmp/ch11_problem10_earth_dam_design.png', dpi=150, bbox_inches='tight')
        print(f"图表已保存: /tmp/ch11_problem10_earth_dam_design.png")
        plt.show()
    
    def print_results(self):
        """打印结果"""
        print("\n" + "="*70)
        print("第11章 水工建筑物 - 题10：土石坝设计")
        print("="*70)
        
        dims = self.dam_dimensions()
        A = self.cross_section_area()
        volumes = self.fill_volume()
        Fs, is_safe = self.slope_stability()
        q = self.seepage_discharge()
        freeboard_info = self.freeboard()
        costs = self.cost_estimate()
        
        print(f"\n【坝体尺寸】")
        print(f"最大坝高: H = {self.H} m")
        print(f"坝顶宽度: b = {self.b} m")
        print(f"上游坡比: m₁ = {self.m1}")
        print(f"下游坡比: m₂ = {self.m2}")
        print(f"上游坡脚宽: B₁ = m₁×H = {dims['B1']:.2f} m")
        print(f"下游坡脚宽: B₂ = m₂×H = {dims['B2']:.2f} m")
        print(f"坝底总宽: B = b + B₁ + B₂ = {dims['B']:.2f} m")
        print(f"横断面面积: A = {A:.2f} m²")
        
        print(f"\n【填筑方量】（坝轴线长L={volumes['L']}m）")
        print(f"实方（压实后）: V = {volumes['V_solid']:.2f} m³ = {volumes['V_solid']/10000:.2f} 万m³")
        print(f"松方（施工量）: V = {volumes['V_loose']:.2f} m³ = {volumes['V_loose']/10000:.2f} 万m³")
        
        print(f"\n【边坡稳定】")
        print(f"采用简化Bishop法")
        print(f"安全系数: Fs = {Fs:.3f}")
        if is_safe:
            print(f"✓ Fs = {Fs:.3f} ≥ 1.3，边坡稳定")
        else:
            print(f"✗ Fs = {Fs:.3f} < 1.3，边坡不稳定！")
        
        print(f"\n【渗流分析】")
        print(f"渗透系数: k = {self.k} m/s")
        print(f"单宽渗流量: q = {q:.2e} m²/s = {q*86400:.2e} m²/d")
        
        print(f"\n【超高验算】")
        print(f"设计洪水位: {self.hd} m")
        print(f"波浪爬高: R = {freeboard_info['R']:.2f} m")
        print(f"安全加高: a = {freeboard_info['a']:.2f} m")
        print(f"所需超高: e = R + a = {freeboard_info['e_required']:.2f} m")
        print(f"实际超高: {freeboard_info['e_actual']:.2f} m")
        if freeboard_info['is_sufficient']:
            print(f"✓ 超高满足要求")
        else:
            print(f"✗ 超高不足！")
        
        print(f"\n【经济指标】")
        print(f"开挖费用: {costs['cost_excavation']/10000:.2f} 万元")
        print(f"填筑费用: {costs['cost_fill']/10000:.2f} 万元")
        print(f"碾压费用: {costs['cost_compaction']/10000:.2f} 万元")
        print(f"工程总造价: {costs['cost_total']/10000:.2f} 万元")
        print(f"单位库容造价: {costs['cost_per_capacity']:.2f} 元/m³")
        
        print(f"\n✓ 土石坝设计完成")
        print(f"\n{'='*70}\n")


def main():
    H = 60
    b = 10
    m1 = 3.0
    m2 = 2.5
    h1 = 55
    hd = 58
    rho_d = 1.8
    rho_sat = 2.0
    
    dam = EarthDamDesign(H, b, m1, m2, h1, hd, rho_d, rho_sat)
    dam.print_results()
    dam.plot_analysis()


if __name__ == "__main__":
    main()
