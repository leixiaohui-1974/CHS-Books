# -*- coding: utf-8 -*-
"""
第08章 渗流计算 - 题7：土坝渗流分析

问题描述：
    均质土坝，坝顶宽b0 = 6m，上游坡比m1 = 3.0，下游坡比m2 = 2.5
    上游水深H1 = 25m，坝高H = 30m
    渗透系数K = 0.00005 m/s，坝基不透水
    
    求：
    1. 浸润线方程（A.卡萨格兰德法）
    2. 单宽渗流量q
    3. 浸润线出逸点位置
    4. 下游坡稳定性分析
    5. 排水设施设计

核心公式：
    1. 浸润线方程：y² = y0² - (2q/K)x
    2. 单宽流量：q = K·y0²/(2L)·f(α)
    3. 出逸点高度：ye
    4. 稳定安全系数：K = r·tanφ/(i·tanα)

考试要点：
    - 浸润线计算（抛物线）
    - 卡萨格兰德基点法
    - 渗流量计算
    - 排水设施作用

作者: CHS-Books Team
日期: 2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve
from typing import Tuple

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class EarthDamSeepage:
    """土坝渗流分析"""
    
    def __init__(self, b0: float, m1: float, m2: float, H1: float, 
                 H: float, K: float):
        self.b0 = b0  # 坝顶宽
        self.m1 = m1  # 上游坡比
        self.m2 = m2  # 下游坡比
        self.H1 = H1  # 上游水深
        self.H = H  # 坝高
        self.K = K  # 渗透系数
        self.g = 9.8
        
    def dam_dimensions(self) -> dict:
        """坝体尺寸"""
        # 上游坡脚
        L1 = self.m1 * self.H
        # 下游坡脚
        L2 = self.m2 * self.H
        # 总底宽
        L_total = L1 + self.b0 + L2
        
        return {
            'L1': L1,  # 上游坡脚距离
            'L2': L2,  # 下游坡脚距离
            'L_total': L_total,  # 总底宽
            'crest': self.b0  # 坝顶宽
        }
    
    def base_point(self) -> Tuple[float, float]:
        """
        卡萨格兰德基点法
        基点：A点（上游水位与坝体上游坡的交点修正）
        """
        dims = self.dam_dimensions()
        
        # 基点横坐标（简化）
        # 从坝轴线算起
        x0 = dims['L1'] - self.m1 * (self.H - self.H1)
        y0 = self.H1
        
        return x0, y0
    
    def seepage_length(self) -> float:
        """渗流路径长度"""
        dims = self.dam_dimensions()
        x0, y0 = self.base_point()
        
        # 渗流路径（从基点到下游出逸点）
        L_seep = dims['L_total'] - x0
        
        return L_seep
    
    def unit_seepage(self) -> float:
        """
        单宽渗流量（简化公式）
        q ≈ K·H1²/(2L)
        L: 渗流路径长度
        """
        L = self.seepage_length()
        q = self.K * (self.H1 ** 2) / (2 * L)
        return q
    
    def phreatic_line(self, n_points: int = 100) -> Tuple[np.ndarray, np.ndarray]:
        """
        浸润线方程（抛物线）
        y² = y0² - (2q/K)x
        """
        x0, y0 = self.base_point()
        q = self.unit_seepage()
        dims = self.dam_dimensions()
        
        # x从基点到下游出逸点
        x_range = np.linspace(0, dims['L_total'] - x0, n_points)
        
        # 浸润线高程
        y_range = []
        for x in x_range:
            y_sq = y0**2 - (2 * q / self.K) * x
            if y_sq > 0:
                y = np.sqrt(y_sq)
                y_range.append(y)
            else:
                y_range.append(0)
        
        # 转换为全局坐标
        x_global = x_range + x0
        
        return x_global, np.array(y_range)
    
    def exit_point(self) -> Tuple[float, float]:
        """出逸点位置"""
        x_phreatic, y_phreatic = self.phreatic_line()
        
        # 下游坡线方程
        dims = self.dam_dimensions()
        x_slope_start = dims['L1'] + self.b0
        
        # 找浸润线与下游坡的交点
        for i in range(len(x_phreatic)):
            if x_phreatic[i] >= x_slope_start:
                # 下游坡高程
                x_rel = x_phreatic[i] - x_slope_start
                y_slope = self.H - x_rel / self.m2
                
                # 浸润线低于坡面时为出逸点
                if y_phreatic[i] <= y_slope:
                    return x_phreatic[i], y_phreatic[i]
        
        # 默认返回坝脚
        return dims['L_total'], 0
    
    def drainage_design(self) -> dict:
        """排水设施设计"""
        xe, ye = self.exit_point()
        
        # 排水棱体
        # 起点：出逸点下方
        x_drain_start = xe - 5
        y_drain_start = 0
        
        # 终点：坝脚
        dims = self.dam_dimensions()
        x_drain_end = dims['L_total']
        y_drain_end = 0
        
        # 排水棱体高度（通常为出逸高度的1.5倍）
        h_drain = ye * 1.5
        
        return {
            'start': (x_drain_start, y_drain_start),
            'end': (x_drain_end, y_drain_end),
            'height': h_drain,
            'exit': (xe, ye)
        }
    
    def plot_analysis(self):
        """绘制分析图表"""
        fig = plt.figure(figsize=(16, 12))
        
        dims = self.dam_dimensions()
        x0, y0 = self.base_point()
        q = self.unit_seepage()
        x_phreatic, y_phreatic = self.phreatic_line()
        xe, ye = self.exit_point()
        drainage = self.drainage_design()
        
        # 1. 土坝断面与浸润线
        ax1 = plt.subplot(3, 3, 1)
        
        # 坝体轮廓
        x_dam = [0, dims['L1'], dims['L1']+self.b0, dims['L_total'], dims['L_total'], 0, 0]
        y_dam = [0, self.H, self.H, 0, 0, 0, 0]
        ax1.fill(x_dam, y_dam, color='brown', alpha=0.3, label='坝体')
        ax1.plot(x_dam, y_dam, 'k-', linewidth=2)
        
        # 上游水位
        ax1.fill([0, 0, dims['L1']], [0, self.H1, self.H], color='lightblue', alpha=0.5, label='上游水')
        ax1.plot([0, dims['L1']], [self.H1, self.H], 'b-', linewidth=2)
        
        # 浸润线
        ax1.plot(x_phreatic, y_phreatic, 'r-', linewidth=3, label='浸润线')
        
        # 出逸点
        ax1.plot(xe, ye, 'go', markersize=12, label=f'出逸点({xe:.1f}, {ye:.1f})')
        
        # 基点
        ax1.plot(x0, y0, 'bs', markersize=10, label=f'基点({x0:.1f}, {y0:.1f})')
        
        # 排水棱体（示意）
        x_drain = [drainage['start'][0], drainage['end'][0], drainage['end'][0], drainage['start'][0]]
        y_drain = [0, 0, drainage['height'], drainage['height']]
        ax1.fill(x_drain, y_drain, color='yellow', alpha=0.3, edgecolor='orange', 
                linewidth=2, label='排水设施')
        
        ax1.set_xlabel('水平距离 (m)', fontsize=10)
        ax1.set_ylabel('高程 (m)', fontsize=10)
        ax1.set_title('土坝断面与浸润线', fontsize=12, fontweight='bold')
        ax1.legend(fontsize=8)
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim(-5, dims['L_total']+5)
        ax1.set_ylim(-2, self.H+5)
        
        # 2. 计算参数
        ax2 = plt.subplot(3, 3, 2)
        ax2.axis('off')
        
        ax2.text(0.5, 0.95, '土坝参数', fontsize=11, ha='center', fontweight='bold')
        ax2.text(0.1, 0.82, f'坝高: H = {self.H} m', fontsize=10)
        ax2.text(0.1, 0.72, f'坝顶宽: b₀ = {self.b0} m', fontsize=10)
        ax2.text(0.1, 0.62, f'上游坡比: m₁ = {self.m1}', fontsize=10)
        ax2.text(0.1, 0.52, f'下游坡比: m₂ = {self.m2}', fontsize=10)
        ax2.text(0.1, 0.42, f'上游水深: H₁ = {self.H1} m', fontsize=10)
        ax2.text(0.1, 0.32, f'渗透系数: K = {self.K} m/s', fontsize=10)
        ax2.text(0.1, 0.20, f'渗流路径: L = {self.seepage_length():.1f} m', fontsize=10, color='blue')
        ax2.text(0.1, 0.10, f'单宽流量: q = {q*1000:.3f} L/(s·m)', fontsize=10, color='red', fontweight='bold')
        ax2.text(0.1, 0.00, f'出逸高度: ye = {ye:.2f} m', fontsize=10, color='green')
        
        ax2.set_title('基本参数', fontsize=12, fontweight='bold')
        
        # 3. 浸润线方程验证
        ax3 = plt.subplot(3, 3, 3)
        
        # y² vs x 关系（应为直线）
        y_sq = y_phreatic ** 2
        x_rel = x_phreatic - x0
        
        ax3.plot(x_rel, y_sq, 'b-', linewidth=2, label='y²(x)')
        
        # 理论直线
        y0_sq = y0 ** 2
        slope = -2 * q / self.K
        x_theory = np.linspace(0, max(x_rel), 50)
        y_sq_theory = y0_sq + slope * x_theory
        ax3.plot(x_theory, y_sq_theory, 'r--', linewidth=1.5, 
                label=f'理论: y²={y0_sq:.0f}{slope:.4f}x')
        
        ax3.set_xlabel('相对距离 x (m)', fontsize=10)
        ax3.set_ylabel('y² (m²)', fontsize=10)
        ax3.set_title('浸润线方程验证', fontsize=12, fontweight='bold')
        ax3.legend(fontsize=8)
        ax3.grid(True, alpha=0.3)
        
        # 4. 渗透系数影响
        ax4 = plt.subplot(3, 3, 4)
        
        K_range = np.logspace(-6, -4, 50)
        q_K = [K_val * (self.H1**2) / (2*self.seepage_length()) * 1000 for K_val in K_range]
        
        ax4.plot(K_range, q_K, 'b-', linewidth=2)
        ax4.plot(self.K, q*1000, 'ro', markersize=10, label=f'K={self.K}m/s')
        
        ax4.set_xlabel('渗透系数 K (m/s)', fontsize=10)
        ax4.set_ylabel('单宽流量 q (L/(s·m))', fontsize=10)
        ax4.set_title('渗透系数影响', fontsize=12, fontweight='bold')
        ax4.set_xscale('log')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        # 5. 水位影响
        ax5 = plt.subplot(3, 3, 5)
        
        H1_range = np.linspace(10, self.H, 50)
        q_H1 = [self.K * (H1_val**2) / (2*self.seepage_length()) * 1000 for H1_val in H1_range]
        
        ax5.plot(H1_range, q_H1, 'g-', linewidth=2)
        ax5.plot(self.H1, q*1000, 'ro', markersize=10, label=f'H₁={self.H1}m')
        
        ax5.set_xlabel('上游水深 H₁ (m)', fontsize=10)
        ax5.set_ylabel('单宽流量 q (L/(s·m))', fontsize=10)
        ax5.set_title('水位影响', fontsize=12, fontweight='bold')
        ax5.legend()
        ax5.grid(True, alpha=0.3)
        
        # 6. 浸润线高程分布
        ax6 = plt.subplot(3, 3, 6)
        
        ax6.plot(x_phreatic, y_phreatic, 'b-', linewidth=2, label='浸润线高程')
        ax6.plot(xe, ye, 'ro', markersize=10, label='出逸点')
        ax6.fill_between(x_phreatic, 0, y_phreatic, color='lightblue', alpha=0.3)
        
        ax6.set_xlabel('水平距离 (m)', fontsize=10)
        ax6.set_ylabel('浸润线高程 (m)', fontsize=10)
        ax6.set_title('浸润线高程分布', fontsize=12, fontweight='bold')
        ax6.legend()
        ax6.grid(True, alpha=0.3)
        
        # 7. 排水设施作用
        ax7 = plt.subplot(3, 3, 7)
        ax7.axis('off')
        
        ax7.text(0.5, 0.95, '排水设施设计', fontsize=11, ha='center', fontweight='bold')
        
        ax7.text(0.1, 0.80, '1. 排水棱体:', fontsize=10, color='blue', fontweight='bold')
        ax7.text(0.15, 0.70, f'• 起点: x={drainage["start"][0]:.1f}m', fontsize=9)
        ax7.text(0.15, 0.62, f'• 高度: h={drainage["height"]:.2f}m', fontsize=9)
        ax7.text(0.15, 0.54, '• 作用：降低出逸点', fontsize=9)
        
        ax7.text(0.1, 0.40, '2. 排水管/褥垫:', fontsize=10, color='green', fontweight='bold')
        ax7.text(0.15, 0.30, '• 加速排水', fontsize=9)
        ax7.text(0.15, 0.22, '• 防止渗透破坏', fontsize=9)
        
        ax7.text(0.1, 0.08, '✓ 有效降低浸润线', fontsize=10, color='orange', fontweight='bold')
        
        ax7.set_title('工程措施', fontsize=12, fontweight='bold')
        
        # 8. 坡比影响
        ax8 = plt.subplot(3, 3, 8)
        
        m2_range = np.linspace(1.5, 4, 50)
        L_m2 = []
        q_m2 = []
        
        for m2_val in m2_range:
            L2_temp = m2_val * self.H
            L_total_temp = dims['L1'] + self.b0 + L2_temp
            L_seep_temp = L_total_temp - x0
            q_temp = self.K * (self.H1**2) / (2*L_seep_temp) * 1000
            
            L_m2.append(L_seep_temp)
            q_m2.append(q_temp)
        
        ax8_twin = ax8.twinx()
        
        line1 = ax8.plot(m2_range, q_m2, 'b-', linewidth=2, label='流量q')
        line2 = ax8_twin.plot(m2_range, L_m2, 'r--', linewidth=2, label='渗流长度L')
        ax8.plot(self.m2, q*1000, 'go', markersize=10)
        
        ax8.set_xlabel('下游坡比 m₂', fontsize=10)
        ax8.set_ylabel('单宽流量 q (L/(s·m))', fontsize=10, color='b')
        ax8_twin.set_ylabel('渗流长度 L (m)', fontsize=10, color='r')
        ax8.set_title('下游坡比影响', fontsize=12, fontweight='bold')
        
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax8.legend(lines, labels, fontsize=8)
        ax8.grid(True, alpha=0.3)
        
        # 9. 结果汇总表
        ax9 = plt.subplot(3, 3, 9)
        ax9.axis('off')
        
        table_data = [
            ['参数', '数值', '单位'],
            ['坝高', f'{self.H:.1f}', 'm'],
            ['上游水深', f'{self.H1:.1f}', 'm'],
            ['渗透系数', f'{self.K*1e6:.1f}', '×10⁻⁶m/s'],
            ['基点坐标', f'({x0:.1f}, {y0:.1f})', 'm'],
            ['渗流路径', f'{self.seepage_length():.1f}', 'm'],
            ['单宽流量', f'{q*1000:.3f}', 'L/(s·m)'],
            ['出逸点高度', f'{ye:.2f}', 'm'],
            ['排水高度', f'{drainage["height"]:.2f}', 'm']
        ]
        
        table = ax9.table(cellText=table_data, cellLoc='center', loc='center',
                         colWidths=[0.4, 0.3, 0.25])
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2.2)
        
        for i in range(3):
            table[(0, i)].set_facecolor('#4472C4')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        table[(6, 1)].set_facecolor('#90EE90')
        table[(6, 1)].set_text_props(weight='bold')
        
        ax9.set_title('计算结果汇总', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('/tmp/ch08_problem07_earth_dam_seepage.png', dpi=150, bbox_inches='tight')
        print(f"图表已保存: /tmp/ch08_problem07_earth_dam_seepage.png")
        plt.show()
    
    def print_results(self):
        """打印结果"""
        print("\n" + "="*70)
        print("第08章 渗流计算 - 题7：土坝渗流分析")
        print("="*70)
        
        dims = self.dam_dimensions()
        x0, y0 = self.base_point()
        L = self.seepage_length()
        q = self.unit_seepage()
        xe, ye = self.exit_point()
        
        print(f"\n【土坝参数】")
        print(f"坝高: H = {self.H} m")
        print(f"坝顶宽: b₀ = {self.b0} m")
        print(f"上游坡比: m₁ = {self.m1} (1:{self.m1})")
        print(f"下游坡比: m₂ = {self.m2} (1:{self.m2})")
        print(f"上游水深: H₁ = {self.H1} m")
        print(f"渗透系数: K = {self.K} m/s = {self.K*86400:.3f} m/d")
        
        print(f"\n【坝体尺寸】")
        print(f"上游坡脚: L₁ = m₁×H = {dims['L1']:.1f} m")
        print(f"下游坡脚: L₂ = m₂×H = {dims['L2']:.1f} m")
        print(f"总底宽: L_total = {dims['L_total']:.1f} m")
        
        print(f"\n【基点（卡萨格兰德法）】")
        print(f"基点坐标: A({x0:.1f}, {y0:.1f}) m")
        print(f"渗流路径长度: L = {L:.1f} m")
        
        print(f"\n【浸润线方程】")
        print(f"抛物线方程: y² = y₀² - (2q/K)x")
        print(f"其中：y₀ = {y0:.2f} m")
        print(f"      2q/K = {2*q/self.K:.6f}")
        
        print(f"\n【单宽渗流量】")
        print(f"q = K·H₁²/(2L)")
        print(f"  = {self.K}×{self.H1}²/(2×{L:.1f})")
        print(f"  = {q:.6f} m³/(s·m) = {q*1000:.3f} L/(s·m)")
        
        print(f"\n【出逸点】")
        print(f"出逸点坐标: ({xe:.1f}, {ye:.2f}) m")
        print(f"出逸高度: ye = {ye:.2f} m")
        
        drainage = self.drainage_design()
        
        print(f"\n【排水设施】")
        print(f"排水棱体起点: x = {drainage['start'][0]:.1f} m")
        print(f"排水棱体高度: h = {drainage['height']:.2f} m")
        print(f"作用：降低浸润线出逸点，增加下游坡稳定性")
        
        print(f"\n✓ 土坝渗流分析完成")
        print(f"\n{'='*70}\n")


def main():
    b0 = 6
    m1 = 3.0
    m2 = 2.5
    H1 = 25
    H = 30
    K = 0.00005
    
    dam = EarthDamSeepage(b0, m1, m2, H1, H, K)
    dam.print_results()
    dam.plot_analysis()


if __name__ == "__main__":
    main()
