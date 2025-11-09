# -*- coding: utf-8 -*-
"""
第10章 堰闸水力计算 - 题4：薄壁堰流量计算

问题描述：
    薄壁矩形堰，堰宽b = 2m，堰高P = 1.5m
    上游水头H = 0.8m，流量系数m = 0.42
    
    求：
    1. 堰流流量Q
    2. 与宽顶堰对比
    3. 不同堰型（矩形、三角形、梯形）对比
    4. 侧收缩影响
    5. 堰高P影响

核心公式：
    1. 矩形薄壁堰：Q = (2/3)m·b·√(2g)·H^(3/2)
    2. 三角形薄壁堰：Q = (8/15)m·tanθ·√(2g)·H^(5/2)
    3. 侧收缩：b_有效 = b - 0.1nH（n为收缩个数）
    4. 行近流速修正：H = H0 + v0²/(2g)

考试要点：
    - 薄壁堰与宽顶堰区别
    - 不同堰型流量公式
    - 侧收缩影响
    - 堰高修正

作者: CHS-Books Team
日期: 2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class SharpCrestedWeir:
    """薄壁堰流量计算"""
    
    def __init__(self, b: float, H: float, P: float, m: float = 0.42):
        self.b = b  # 堰宽
        self.H = H  # 水头
        self.P = P  # 堰高
        self.m = m  # 流量系数
        self.g = 9.8
        
    def discharge_rectangular(self) -> float:
        """矩形薄壁堰流量"""
        Q = (2/3) * self.m * self.b * np.sqrt(2*self.g) * (self.H ** 1.5)
        return Q
    
    def discharge_triangular(self, theta: float = 90) -> float:
        """
        三角形薄壁堰流量
        theta: 缺口角度（度）
        """
        theta_rad = np.deg2rad(theta)
        Q = (8/15) * self.m * np.tan(theta_rad/2) * np.sqrt(2*self.g) * (self.H ** 2.5)
        return Q
    
    def discharge_trapezoidal(self, b1: float, m_side: float) -> float:
        """
        梯形薄壁堰流量
        b1: 底宽
        m_side: 边坡系数
        """
        # 梯形 = 矩形 + 三角形
        Q_rect = (2/3) * self.m * b1 * np.sqrt(2*self.g) * (self.H ** 1.5)
        Q_tri = (8/15) * self.m * m_side * np.sqrt(2*self.g) * (self.H ** 2.5)
        return Q_rect + Q_tri
    
    def side_contraction(self, n: int = 2) -> float:
        """
        侧收缩影响
        n: 收缩个数（通常为2，两侧）
        """
        b_eff = self.b - 0.1 * n * self.H
        return b_eff
    
    def discharge_with_contraction(self, n: int = 2) -> float:
        """考虑侧收缩的流量"""
        b_eff = self.side_contraction(n)
        Q = (2/3) * self.m * b_eff * np.sqrt(2*self.g) * (self.H ** 1.5)
        return Q
    
    def approach_velocity_correction(self, A0: float) -> Tuple[float, float]:
        """
        行近流速修正
        A0: 上游渠道断面积
        """
        # 迭代求解
        H_corrected = self.H
        for _ in range(5):
            Q = self.discharge_rectangular()
            v0 = Q / A0
            H_corrected = self.H + v0**2 / (2*self.g)
        
        return H_corrected, v0
    
    def plot_analysis(self):
        """绘制分析图表"""
        fig = plt.figure(figsize=(16, 12))
        
        Q_rect = self.discharge_rectangular()
        
        # 1. 薄壁堰示意图
        ax1 = plt.subplot(3, 3, 1)
        
        # 堰体
        x_weir = np.array([2, 2, 2, 2+self.b, 2+self.b, 2+self.b])
        y_weir = np.array([0, self.P, self.P+0.05, self.P+0.05, self.P, 0])
        ax1.fill(x_weir, y_weir, color='gray', alpha=0.6, label='堰体（薄壁）')
        ax1.plot(x_weir, y_weir, 'k-', linewidth=2)
        
        # 水面
        x_water = np.array([0, 2, 2, 2+self.b, 2+self.b+1])
        y_water = np.array([self.P+self.H, self.P+self.H, self.P+self.H, self.P, 0.5*self.P])
        ax1.fill_between(x_water, 0, y_water, color='lightblue', alpha=0.5, label='水体')
        ax1.plot(x_water, y_water, 'b-', linewidth=2, label='水面线')
        
        # 标注
        ax1.arrow(1.5, self.P, 0, self.H, head_width=0.15, head_length=0.08, fc='red', ec='red')
        ax1.text(1.2, self.P+self.H/2, f'H={self.H}m', fontsize=10, color='red', fontweight='bold')
        ax1.text(2+self.b/2, self.P-0.2, f'b={self.b}m', fontsize=10, ha='center', color='blue')
        ax1.text(1.7, self.P/2, f'P={self.P}m', fontsize=10, color='black')
        
        ax1.set_xlim(-0.5, 5.5)
        ax1.set_ylim(-0.5, self.P+self.H+0.5)
        ax1.set_xlabel('距离 (m)', fontsize=10)
        ax1.set_ylabel('高程 (m)', fontsize=10)
        ax1.set_title('薄壁堰示意图', fontsize=12, fontweight='bold')
        ax1.legend(fontsize=8)
        ax1.grid(True, alpha=0.3)
        
        # 2. 计算参数
        ax2 = plt.subplot(3, 3, 2)
        ax2.axis('off')
        
        ax2.text(0.5, 0.9, '薄壁堰参数', fontsize=11, ha='center', fontweight='bold')
        ax2.text(0.1, 0.75, f'堰宽: b = {self.b} m', fontsize=10)
        ax2.text(0.1, 0.65, f'水头: H = {self.H} m', fontsize=10)
        ax2.text(0.1, 0.55, f'堰高: P = {self.P} m', fontsize=10)
        ax2.text(0.1, 0.45, f'流量系数: m = {self.m}', fontsize=10, color='blue')
        ax2.text(0.1, 0.30, f'流量: Q = {Q_rect:.3f} m³/s', fontsize=11, color='red', fontweight='bold')
        ax2.text(0.1, 0.15, f'公式: Q = (2/3)mb√(2g)H^(3/2)', fontsize=9, color='purple')
        ax2.text(0.1, 0.05, f'薄壁堰: 堰顶厚度<0.67H', fontsize=9, color='gray')
        
        ax2.set_title('基本参数', fontsize=12, fontweight='bold')
        
        # 3. H-Q关系
        ax3 = plt.subplot(3, 3, 3)
        
        H_range = np.linspace(0.1, 2, 100)
        Q_range = [(2/3)*self.m*self.b*np.sqrt(2*self.g)*(H**1.5) for H in H_range]
        
        ax3.plot(H_range, Q_range, 'b-', linewidth=2, label='矩形薄壁堰')
        ax3.plot(self.H, Q_rect, 'ro', markersize=10, label=f'当前点(H={self.H})')
        
        ax3.set_xlabel('水头 H (m)', fontsize=10)
        ax3.set_ylabel('流量 Q (m³/s)', fontsize=10)
        ax3.set_title('水头-流量关系', fontsize=12, fontweight='bold')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. 不同堰型对比
        ax4 = plt.subplot(3, 3, 4)
        
        Q_tri_90 = self.discharge_triangular(90)
        Q_tri_60 = self.discharge_triangular(60)
        Q_trap = self.discharge_trapezoidal(self.b*0.8, 0.5)
        
        weir_types = ['矩形', '三角90°', '三角60°', '梯形']
        discharges = [Q_rect, Q_tri_90, Q_tri_60, Q_trap]
        colors = ['skyblue', 'lightgreen', 'lightcoral', 'gold']
        
        bars = ax4.bar(weir_types, discharges, color=colors, alpha=0.7, edgecolor='black')
        ax4.set_ylabel('流量 Q (m³/s)', fontsize=10)
        ax4.set_title('不同堰型流量对比', fontsize=12, fontweight='bold')
        ax4.grid(True, alpha=0.3, axis='y')
        
        for bar, Q in zip(bars, discharges):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height,
                    f'{Q:.2f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        # 5. 侧收缩影响
        ax5 = plt.subplot(3, 3, 5)
        
        n_contractions = [0, 1, 2, 3]
        Q_contractions = []
        
        for n in n_contractions:
            if n == 0:
                Q_contractions.append(Q_rect)
            else:
                Q_contractions.append(self.discharge_with_contraction(n))
        
        bars = ax5.bar(n_contractions, Q_contractions, color='orange', alpha=0.7, edgecolor='black')
        ax5.set_xlabel('侧收缩数 n', fontsize=10)
        ax5.set_ylabel('流量 Q (m³/s)', fontsize=10)
        ax5.set_title('侧收缩影响', fontsize=12, fontweight='bold')
        ax5.set_xticks(n_contractions)
        ax5.grid(True, alpha=0.3, axis='y')
        
        for bar, Q in zip(bars, Q_contractions):
            height = bar.get_height()
            ax5.text(bar.get_x() + bar.get_width()/2., height,
                    f'{Q:.2f}', ha='center', va='bottom', fontsize=9)
        
        # 6. 堰高P影响
        ax6 = plt.subplot(3, 3, 6)
        
        P_range = np.linspace(0.5, 3, 50)
        # 简化：假设m随P/H变化（实际更复杂）
        Q_P = [(2/3)*self.m*self.b*np.sqrt(2*self.g)*(self.H**1.5) for P in P_range]
        
        ax6.plot(P_range, Q_P, 'b-', linewidth=2)
        ax6.plot(self.P, Q_rect, 'ro', markersize=10, label=f'P={self.P}m')
        
        ax6.set_xlabel('堰高 P (m)', fontsize=10)
        ax6.set_ylabel('流量 Q (m³/s)', fontsize=10)
        ax6.set_title('堰高影响（简化）', fontsize=12, fontweight='bold')
        ax6.legend()
        ax6.grid(True, alpha=0.3)
        ax6.text(1.5, Q_rect+0.2, '注：实际m=f(P/H)', fontsize=9, color='red')
        
        # 7. 流量系数m对比
        ax7 = plt.subplot(3, 3, 7)
        
        m_range = np.linspace(0.35, 0.5, 50)
        Q_m_range = [(2/3)*m*self.b*np.sqrt(2*self.g)*(self.H**1.5) for m in m_range]
        
        ax7.plot(m_range, Q_m_range, 'b-', linewidth=2)
        ax7.plot(self.m, Q_rect, 'ro', markersize=10, label=f'm={self.m}')
        ax7.axvline(0.42, color='green', linestyle='--', linewidth=1, alpha=0.7, label='标准m=0.42')
        
        ax7.set_xlabel('流量系数 m', fontsize=10)
        ax7.set_ylabel('流量 Q (m³/s)', fontsize=10)
        ax7.set_title('流量系数影响', fontsize=12, fontweight='bold')
        ax7.legend()
        ax7.grid(True, alpha=0.3)
        
        # 8. 薄壁堰 vs 宽顶堰
        ax8 = plt.subplot(3, 3, 8)
        ax8.axis('off')
        
        Q_broad = 0.385 * self.b * (self.H**1.5) * np.sqrt(2*self.g)  # 宽顶堰（m=0.385）
        
        ax8.text(0.5, 0.95, '薄壁堰 vs 宽顶堰', fontsize=11, ha='center', fontweight='bold')
        
        ax8.text(0.1, 0.80, '薄壁堰特点:', fontsize=10, color='blue', fontweight='bold')
        ax8.text(0.15, 0.70, '• 堰顶厚度 < 0.67H', fontsize=9)
        ax8.text(0.15, 0.62, '• 侧收缩明显', fontsize=9)
        ax8.text(0.15, 0.54, f'• m ≈ 0.42, Q = {Q_rect:.2f} m³/s', fontsize=9, color='red')
        
        ax8.text(0.1, 0.40, '宽顶堰特点:', fontsize=10, color='green', fontweight='bold')
        ax8.text(0.15, 0.30, '• 堰顶宽度 > 2H', fontsize=9)
        ax8.text(0.15, 0.22, '• 无侧收缩影响', fontsize=9)
        ax8.text(0.15, 0.14, f'• m ≈ 0.385, Q = {Q_broad:.2f} m³/s', fontsize=9, color='red')
        
        ax8.text(0.1, 0.02, f'流量差: {abs(Q_rect-Q_broad):.2f} m³/s ({abs(Q_rect-Q_broad)/Q_broad*100:.1f}%)', 
                fontsize=10, color='purple', fontweight='bold')
        
        ax8.set_title('堰型对比', fontsize=12, fontweight='bold')
        
        # 9. 结果汇总表
        ax9 = plt.subplot(3, 3, 9)
        ax9.axis('off')
        
        table_data = [
            ['参数', '数值', '单位'],
            ['堰宽 b', f'{self.b:.2f}', 'm'],
            ['水头 H', f'{self.H:.2f}', 'm'],
            ['堰高 P', f'{self.P:.2f}', 'm'],
            ['流量系数 m', f'{self.m:.2f}', '-'],
            ['矩形堰流量', f'{Q_rect:.3f}', 'm³/s'],
            ['三角堰(90°)', f'{Q_tri_90:.3f}', 'm³/s'],
            ['梯形堰', f'{Q_trap:.3f}', 'm³/s'],
            ['侧收缩修正(n=2)', f'{self.discharge_with_contraction(2):.3f}', 'm³/s']
        ]
        
        table = ax9.table(cellText=table_data, cellLoc='center', loc='center',
                         colWidths=[0.45, 0.3, 0.2])
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2.2)
        
        for i in range(3):
            table[(0, i)].set_facecolor('#4472C4')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        table[(5, 1)].set_facecolor('#90EE90')
        table[(5, 1)].set_text_props(weight='bold')
        
        ax9.set_title('计算结果汇总', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('/tmp/ch10_problem04_sharp_crested_weir.png', dpi=150, bbox_inches='tight')
        print(f"图表已保存: /tmp/ch10_problem04_sharp_crested_weir.png")
        plt.show()
    
    def print_results(self):
        """打印结果"""
        print("\n" + "="*70)
        print("第10章 堰闸水力计算 - 题4：薄壁堰流量计算")
        print("="*70)
        
        Q_rect = self.discharge_rectangular()
        Q_tri_90 = self.discharge_triangular(90)
        Q_tri_60 = self.discharge_triangular(60)
        
        print(f"\n【堰体参数】")
        print(f"堰宽: b = {self.b} m")
        print(f"堰高: P = {self.P} m")
        print(f"水头: H = {self.H} m")
        print(f"流量系数: m = {self.m}")
        
        print(f"\n【矩形薄壁堰】")
        print(f"Q = (2/3)·m·b·√(2g)·H^(3/2)")
        print(f"  = (2/3)×{self.m}×{self.b}×√(2×{self.g})×{self.H}^(3/2)")
        print(f"  = {Q_rect:.3f} m³/s")
        
        print(f"\n【三角形薄壁堰】")
        print(f"90°三角堰: Q = {Q_tri_90:.3f} m³/s")
        print(f"60°三角堰: Q = {Q_tri_60:.3f} m³/s")
        
        print(f"\n【侧收缩影响】")
        Q_no_contract = Q_rect
        Q_with_contract = self.discharge_with_contraction(2)
        print(f"无侧收缩: Q = {Q_no_contract:.3f} m³/s")
        print(f"双侧收缩: Q = {Q_with_contract:.3f} m³/s")
        print(f"流量减小: {(Q_no_contract-Q_with_contract)/Q_no_contract*100:.1f}%")
        
        print(f"\n✓ 薄壁堰流量计算完成")
        print(f"\n{'='*70}\n")


def main():
    b = 2
    H = 0.8
    P = 1.5
    m = 0.42
    
    weir = SharpCrestedWeir(b, H, P, m)
    weir.print_results()
    weir.plot_analysis()


if __name__ == "__main__":
    main()
