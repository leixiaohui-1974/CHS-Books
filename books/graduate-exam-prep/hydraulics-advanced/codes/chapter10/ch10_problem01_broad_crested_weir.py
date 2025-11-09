# -*- coding: utf-8 -*-
"""
第10章 堰闸水力计算 - 题1：宽顶堰流量计算

问题描述：
    宽顶堰，堰顶宽度b = 3m，上游水头H = 1.5m
    堰顶高度P = 2.0m，流量系数m = 0.385
    
    求：
    1. 堰流流量Q
    2. 堰顶水深h0
    3. 淹没度影响
    4. 不同水头下的流量关系
    5. 流量系数敏感性

核心公式：
    1. 自由出流：Q = m·b·H^(3/2)·√(2g)
    2. 堰顶水深：h0 = (2/3)H
    3. 淹没出流：Q' = σ·Q（σ为淹没系数）
    4. 淹没度：s = h_下/H

考试要点：
    - 宽顶堰流量公式
    - 流量系数m的含义与取值
    - 淹没度判别（s临界≈0.7-0.8）
    - 与薄壁堰对比

作者: CHS-Books Team
日期: 2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class BroadCrestedWeir:
    """宽顶堰流量计算"""
    
    def __init__(self, b: float, H: float, P: float, m: float = 0.385):
        self.b = b  # 堰宽
        self.H = H  # 上游水头（相对堰顶）
        self.P = P  # 堰顶高度
        self.m = m  # 流量系数
        self.g = 9.8
        
    def discharge_free(self) -> float:
        """自由出流流量"""
        Q = self.m * self.b * (self.H ** 1.5) * np.sqrt(2 * self.g)
        return Q
    
    def crest_depth(self) -> float:
        """堰顶临界水深"""
        h0 = (2/3) * self.H
        return h0
    
    def crest_velocity(self) -> float:
        """堰顶流速"""
        h0 = self.crest_depth()
        v0 = np.sqrt(2 * self.g * (self.H - h0))
        return v0
    
    def submergence_coefficient(self, h_tail: float) -> float:
        """
        淹没系数
        s = h_tail/H（淹没度）
        s < 0.7: 自由出流（σ=1）
        s > 0.7: 淹没出流（σ<1）
        """
        s = h_tail / self.H
        if s <= 0.7:
            sigma = 1.0
        else:
            # 经验公式：σ = 1 - 0.2(s-0.7)^2
            sigma = 1 - 0.2 * ((s - 0.7) ** 2)
        return sigma
    
    def discharge_submerged(self, h_tail: float) -> float:
        """淹没出流流量"""
        Q_free = self.discharge_free()
        sigma = self.submergence_coefficient(h_tail)
        return sigma * Q_free
    
    def H_Q_relation(self, H_range: tuple = (0.2, 3)) -> Tuple[np.ndarray, np.ndarray]:
        """水头-流量关系"""
        H_arr = np.linspace(H_range[0], H_range[1], 100)
        Q_arr = []
        
        for H_val in H_arr:
            weir_temp = BroadCrestedWeir(self.b, H_val, self.P, self.m)
            Q_arr.append(weir_temp.discharge_free())
        
        return H_arr, np.array(Q_arr)
    
    def plot_analysis(self):
        """绘制分析图表"""
        fig = plt.figure(figsize=(16, 12))
        
        Q = self.discharge_free()
        h0 = self.crest_depth()
        v0 = self.crest_velocity()
        
        # 1. 宽顶堰示意图
        ax1 = plt.subplot(3, 3, 1)
        
        # 绘制堰体
        x_weir = np.array([0, 0, 3, 3, 5, 5, 6])
        y_weir = np.array([0, self.P, self.P, self.P, self.P, 0, 0])
        ax1.fill_between(x_weir, 0, y_weir, color='gray', alpha=0.5, label='堰体')
        ax1.plot(x_weir, y_weir, 'k-', linewidth=2)
        
        # 水面线
        x_water_up = np.array([-1, 0, 0, 3])
        y_water_up = np.array([self.P+self.H, self.P+self.H, self.P+self.H, self.P+h0])
        ax1.fill_between(x_water_up, self.P, y_water_up, color='lightblue', alpha=0.5, label='水体')
        ax1.plot(x_water_up, y_water_up, 'b-', linewidth=2, label='水面线')
        
        # 标注
        ax1.arrow(-0.5, self.P, 0, self.H, head_width=0.2, head_length=0.1, fc='red', ec='red')
        ax1.text(-0.8, self.P+self.H/2, f'H={self.H}m', fontsize=10, color='red', fontweight='bold')
        ax1.text(1.5, self.P-0.3, f'b={self.b}m', fontsize=10, ha='center', color='blue')
        ax1.text(6.2, self.P/2, f'P={self.P}m', fontsize=10, color='black')
        ax1.text(1.5, self.P+h0+0.1, f'h₀={h0:.2f}m', fontsize=9, color='green', ha='center')
        
        ax1.set_xlim(-2, 7)
        ax1.set_ylim(-0.5, self.P+self.H+0.5)
        ax1.set_xlabel('距离 (m)', fontsize=10)
        ax1.set_ylabel('高程 (m)', fontsize=10)
        ax1.set_title('宽顶堰示意图', fontsize=12, fontweight='bold')
        ax1.legend(fontsize=8)
        ax1.grid(True, alpha=0.3)
        
        # 2. 计算参数
        ax2 = plt.subplot(3, 3, 2)
        ax2.axis('off')
        
        ax2.text(0.5, 0.9, '计算参数', fontsize=11, ha='center', fontweight='bold')
        ax2.text(0.1, 0.75, f'堰宽: b = {self.b} m', fontsize=10)
        ax2.text(0.1, 0.65, f'水头: H = {self.H} m', fontsize=10)
        ax2.text(0.1, 0.55, f'堰高: P = {self.P} m', fontsize=10)
        ax2.text(0.1, 0.45, f'流量系数: m = {self.m}', fontsize=10, color='blue')
        ax2.text(0.1, 0.30, f'流量: Q = {Q:.3f} m³/s', fontsize=11, color='red', fontweight='bold')
        ax2.text(0.1, 0.20, f'堰顶水深: h₀ = {h0:.3f} m', fontsize=10, color='green')
        ax2.text(0.1, 0.10, f'堰顶流速: v₀ = {v0:.3f} m/s', fontsize=10, color='green')
        ax2.text(0.1, 0.00, f'Q = m·b·H^(3/2)·√(2g)', fontsize=9, color='purple')
        
        ax2.set_title('基本参数', fontsize=12, fontweight='bold')
        
        # 3. H-Q关系曲线
        ax3 = plt.subplot(3, 3, 3)
        
        H_arr, Q_arr = self.H_Q_relation()
        
        ax3.plot(H_arr, Q_arr, 'b-', linewidth=2, label='Q(H)')
        ax3.plot(self.H, Q, 'ro', markersize=10, label=f'当前点(H={self.H}, Q={Q:.2f})')
        
        ax3.set_xlabel('水头 H (m)', fontsize=10)
        ax3.set_ylabel('流量 Q (m³/s)', fontsize=10)
        ax3.set_title('水头-流量关系', fontsize=12, fontweight='bold')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. Q vs H^(3/2)验证
        ax4 = plt.subplot(3, 3, 4)
        
        H_32 = H_arr ** 1.5
        
        ax4.plot(H_32, Q_arr, 'g-', linewidth=2, label='Q vs H^(3/2)')
        ax4.scatter(self.H**1.5, Q, c='red', s=100, zorder=5, label='当前点')
        
        # 拟合直线
        slope = self.m * self.b * np.sqrt(2*self.g)
        ax4.plot(H_32, slope * H_32, 'r--', linewidth=1.5, alpha=0.7, 
                label=f'理论: Q={slope:.2f}·H^(3/2)')
        
        ax4.set_xlabel('H^(3/2) (m^(3/2))', fontsize=10)
        ax4.set_ylabel('流量 Q (m³/s)', fontsize=10)
        ax4.set_title('Q ∝ H^(3/2) 验证', fontsize=12, fontweight='bold')
        ax4.legend(fontsize=8)
        ax4.grid(True, alpha=0.3)
        
        # 5. 流量系数m影响
        ax5 = plt.subplot(3, 3, 5)
        
        m_range = np.linspace(0.3, 0.5, 50)
        Q_m = []
        
        for m_val in m_range:
            Q_m.append(m_val * self.b * (self.H**1.5) * np.sqrt(2*self.g))
        
        ax5.plot(m_range, Q_m, 'b-', linewidth=2)
        ax5.plot(self.m, Q, 'ro', markersize=10, label=f'm={self.m}')
        ax5.axvline(0.385, color='green', linestyle='--', linewidth=1, 
                   alpha=0.7, label='标准值m=0.385')
        
        ax5.set_xlabel('流量系数 m', fontsize=10)
        ax5.set_ylabel('流量 Q (m³/s)', fontsize=10)
        ax5.set_title('流量系数影响', fontsize=12, fontweight='bold')
        ax5.legend()
        ax5.grid(True, alpha=0.3)
        
        # 6. 淹没度影响
        ax6 = plt.subplot(3, 3, 6)
        
        s_range = np.linspace(0, 1, 100)  # 淹没度
        sigma_range = []
        
        for s in s_range:
            if s <= 0.7:
                sigma_range.append(1.0)
            else:
                sigma_range.append(1 - 0.2*((s-0.7)**2))
        
        ax6.plot(s_range, sigma_range, 'b-', linewidth=2)
        ax6.axhline(1.0, color='green', linestyle='--', linewidth=1, alpha=0.5, label='σ=1')
        ax6.axvline(0.7, color='red', linestyle='--', linewidth=1.5, 
                   alpha=0.7, label='临界淹没度s=0.7')
        ax6.fill_between(s_range, 0, sigma_range, where=np.array(s_range)<=0.7, 
                        alpha=0.2, color='green', label='自由出流')
        ax6.fill_between(s_range, 0, sigma_range, where=np.array(s_range)>0.7, 
                        alpha=0.2, color='orange', label='淹没出流')
        
        ax6.set_xlabel('淹没度 s = h_下/H', fontsize=10)
        ax6.set_ylabel('淹没系数 σ', fontsize=10)
        ax6.set_title('淹没度影响', fontsize=12, fontweight='bold')
        ax6.legend(fontsize=8)
        ax6.grid(True, alpha=0.3)
        ax6.set_xlim(0, 1)
        ax6.set_ylim(0, 1.1)
        
        # 7. 不同下游水深的流量
        ax7 = plt.subplot(3, 3, 7)
        
        h_tail_range = np.linspace(0, self.H*0.95, 50)
        Q_submerged = []
        
        for h_tail in h_tail_range:
            Q_submerged.append(self.discharge_submerged(h_tail))
        
        ax7.plot(h_tail_range, Q_submerged, 'b-', linewidth=2, label='淹没流量')
        ax7.axhline(Q, color='green', linestyle='--', linewidth=1.5, label=f'自由流量Q={Q:.2f}')
        ax7.axvline(0.7*self.H, color='red', linestyle='--', linewidth=1.5, 
                   alpha=0.7, label=f'临界h_下=0.7H={0.7*self.H:.2f}m')
        
        ax7.set_xlabel('下游水深 h_下 (m)', fontsize=10)
        ax7.set_ylabel('流量 Q (m³/s)', fontsize=10)
        ax7.set_title('淹没流量变化', fontsize=12, fontweight='bold')
        ax7.legend(fontsize=8)
        ax7.grid(True, alpha=0.3)
        
        # 8. 堰顶水深分布（假设）
        ax8 = plt.subplot(3, 3, 8)
        
        x_crest = np.linspace(0, 3, 50)
        # 简化：线性降低
        h_crest = self.H - (self.H - h0) * (x_crest / 3)
        
        ax8.fill_between(x_crest, self.P, self.P + h_crest, color='lightblue', alpha=0.5)
        ax8.plot(x_crest, self.P + h_crest, 'b-', linewidth=2, label='水面线')
        ax8.plot([0, 3], [self.P, self.P], 'k-', linewidth=2, label='堰顶')
        
        ax8.axhline(self.P+self.H, color='red', linestyle='--', linewidth=1, 
                   alpha=0.5, label=f'上游水位={self.P+self.H:.2f}m')
        ax8.axhline(self.P+h0, color='green', linestyle='--', linewidth=1, 
                   alpha=0.5, label=f'临界水深={self.P+h0:.2f}m')
        
        ax8.set_xlabel('沿堰顶距离 (m)', fontsize=10)
        ax8.set_ylabel('高程 (m)', fontsize=10)
        ax8.set_title('堰顶水深分布', fontsize=12, fontweight='bold')
        ax8.legend(fontsize=8)
        ax8.grid(True, alpha=0.3)
        
        # 9. 结果汇总表
        ax9 = plt.subplot(3, 3, 9)
        ax9.axis('off')
        
        table_data = [
            ['参数', '数值', '单位'],
            ['堰宽 b', f'{self.b:.2f}', 'm'],
            ['水头 H', f'{self.H:.2f}', 'm'],
            ['堰高 P', f'{self.P:.2f}', 'm'],
            ['流量系数 m', f'{self.m:.3f}', '-'],
            ['流量 Q', f'{Q:.3f}', 'm³/s'],
            ['堰顶水深 h₀', f'{h0:.3f}', 'm'],
            ['堰顶流速 v₀', f'{v0:.3f}', 'm/s'],
            ['临界淹没度', '0.70', '-']
        ]
        
        table = ax9.table(cellText=table_data, cellLoc='center', loc='center',
                         colWidths=[0.4, 0.3, 0.2])
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2.2)
        
        for i in range(3):
            table[(0, i)].set_facecolor('#4472C4')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        # 高亮流量
        table[(5, 1)].set_facecolor('#90EE90')
        table[(5, 1)].set_text_props(weight='bold')
        
        ax9.set_title('计算结果汇总', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('/tmp/ch10_problem01_broad_crested_weir.png', dpi=150, bbox_inches='tight')
        print(f"图表已保存: /tmp/ch10_problem01_broad_crested_weir.png")
        plt.show()
    
    def print_results(self):
        """打印结果"""
        print("\n" + "="*70)
        print("第10章 堰闸水力计算 - 题1：宽顶堰流量计算")
        print("="*70)
        
        Q = self.discharge_free()
        h0 = self.crest_depth()
        v0 = self.crest_velocity()
        
        print(f"\n【堰体参数】")
        print(f"堰宽: b = {self.b} m")
        print(f"堰高: P = {self.P} m")
        print(f"上游水头: H = {self.H} m")
        print(f"流量系数: m = {self.m}")
        
        print(f"\n【流量计算】")
        print(f"Q = m·b·H^(3/2)·√(2g)")
        print(f"  = {self.m}×{self.b}×{self.H}^(3/2)×√(2×{self.g})")
        print(f"  = {Q:.3f} m³/s")
        
        print(f"\n【堰顶参数】")
        print(f"临界水深: h₀ = (2/3)H = {h0:.3f} m")
        print(f"堰顶流速: v₀ = √(2g(H-h₀)) = {v0:.3f} m/s")
        
        print(f"\n【淹没判别】")
        print(f"临界淹没度: s_c = 0.7")
        print(f"自由出流: h_下 < 0.7H = {0.7*self.H:.3f} m")
        print(f"淹没出流: h_下 > 0.7H")
        
        print(f"\n✓ 宽顶堰流量计算完成")
        print(f"\n{'='*70}\n")


def main():
    b = 3
    H = 1.5
    P = 2.0
    m = 0.385
    
    weir = BroadCrestedWeir(b, H, P, m)
    weir.print_results()
    weir.plot_analysis()


if __name__ == "__main__":
    main()
