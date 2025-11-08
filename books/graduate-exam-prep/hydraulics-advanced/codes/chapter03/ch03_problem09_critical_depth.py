#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第03章 管流与明渠流 - 题目9：临界水深计算

题目描述：
矩形明渠，已知：
- 渠底宽度b=2m
- 流量Q=4m³/s

求：
(1) 临界水深h_c
(2) 临界流速v_c
(3) 临界比能E_c
(4) 不同流量下的临界水深
(5) 水深-比能曲线分析

知识点：
- 临界水深
- 佛汝德数
- 比能曲线
- 缓流与急流

作者：CHS-Books Team
日期：2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class CriticalDepthAnalysis:
    """临界水深分析类"""
    
    def __init__(self, b: float, Q: float, g: float = 9.81):
        """
        初始化参数
        
        Parameters:
        -----------
        b : float
            渠底宽度 (m)
        Q : float
            流量 (m³/s)
        g : float
            重力加速度 (m/s²)
        """
        self.b = b
        self.Q = Q
        self.g = g
    
    def critical_depth(self) -> float:
        """
        计算临界水深
        
        矩形断面临界水深公式：
        h_c = (Q²/(gb²))^(1/3)
        
        Returns:
        --------
        float : 临界水深 (m)
        """
        return (self.Q**2 / (self.g * self.b**2))**(1/3)
    
    def critical_velocity(self) -> float:
        """
        计算临界流速
        
        v_c = Q / (b × h_c)
        
        Returns:
        --------
        float : 临界流速 (m/s)
        """
        h_c = self.critical_depth()
        return self.Q / (self.b * h_c)
    
    def critical_specific_energy(self) -> float:
        """
        计算临界比能
        
        E_c = h_c + v_c²/(2g) = (3/2) × h_c
        
        Returns:
        --------
        float : 临界比能 (m)
        """
        h_c = self.critical_depth()
        return 1.5 * h_c
    
    def specific_energy(self, h: float) -> float:
        """
        计算给定水深的比能
        
        E = h + v²/(2g) = h + Q²/(2gb²h²)
        
        Parameters:
        -----------
        h : float
            水深 (m)
            
        Returns:
        --------
        float : 比能 (m)
        """
        v = self.Q / (self.b * h)
        return h + v**2 / (2 * self.g)
    
    def froude_number(self, h: float) -> float:
        """
        计算佛汝德数
        
        Fr = v / √(gh)
        
        Parameters:
        -----------
        h : float
            水深 (m)
            
        Returns:
        --------
        float : 佛汝德数
        """
        v = self.Q / (self.b * h)
        return v / np.sqrt(self.g * h)
    
    def depth_for_energy(self, E: float) -> tuple:
        """
        给定比能，计算可能的水深（共轭水深）
        
        Parameters:
        -----------
        E : float
            比能 (m)
            
        Returns:
        --------
        tuple : (h1, h2)
            h1 : 急流水深（较小）
            h2 : 缓流水深（较大）
        """
        # 定义方程：E = h + Q²/(2gb²h²)
        def equation(h):
            return h + self.Q**2 / (2 * self.g * self.b**2 * h**2) - E
        
        # 临界水深
        h_c = self.critical_depth()
        
        # 如果比能小于临界比能，无解
        E_c = self.critical_specific_energy()
        if E < E_c * 0.999:  # 留一点余量
            return None, None
        
        # 急流水深（小于临界水深）
        try:
            h1 = fsolve(equation, h_c * 0.5)[0]
            if h1 < 0.001 or h1 > h_c:
                h1 = None
        except:
            h1 = None
        
        # 缓流水深（大于临界水深）
        try:
            h2 = fsolve(equation, h_c * 2.0)[0]
            if h2 < h_c or h2 > 100:
                h2 = None
        except:
            h2 = None
        
        return h1, h2
    
    def discharge_analysis(self, Q_range: tuple = (1, 10), 
                          n_points: int = 50) -> tuple:
        """
        不同流量下的临界水深分析
        
        Parameters:
        -----------
        Q_range : tuple
            流量范围 (m³/s)
        n_points : int
            计算点数
            
        Returns:
        --------
        tuple : (Q_array, hc_array, vc_array, Ec_array)
        """
        Q_array = np.linspace(Q_range[0], Q_range[1], n_points)
        
        hc_array = (Q_array**2 / (self.g * self.b**2))**(1/3)
        vc_array = Q_array / (self.b * hc_array)
        Ec_array = 1.5 * hc_array
        
        return Q_array, hc_array, vc_array, Ec_array
    
    def width_analysis(self, b_range: tuple = (0.5, 5.0),
                      n_points: int = 50) -> tuple:
        """
        不同渠宽下的临界水深分析
        
        Parameters:
        -----------
        b_range : tuple
            渠宽范围 (m)
        n_points : int
            计算点数
            
        Returns:
        --------
        tuple : (b_array, hc_array, vc_array)
        """
        b_array = np.linspace(b_range[0], b_range[1], n_points)
        
        hc_array = (self.Q**2 / (self.g * b_array**2))**(1/3)
        vc_array = self.Q / (b_array * hc_array)
        
        return b_array, hc_array, vc_array
    
    def specific_energy_curve(self, E_range: tuple = None,
                             h_range: tuple = (0.1, 5.0),
                             n_points: int = 200) -> tuple:
        """
        绘制比能曲线
        
        Parameters:
        -----------
        E_range : tuple
            比能范围 (m)
        h_range : tuple
            水深范围 (m)
        n_points : int
            计算点数
            
        Returns:
        --------
        tuple : (h_array, E_array)
        """
        h_array = np.linspace(h_range[0], h_range[1], n_points)
        E_array = np.zeros(n_points)
        
        for i, h in enumerate(h_array):
            E_array[i] = self.specific_energy(h)
        
        return h_array, E_array
    
    def plot_analysis(self):
        """绘制临界水深分析图"""
        fig = plt.figure(figsize=(15, 12))
        
        h_c = self.critical_depth()
        v_c = self.critical_velocity()
        E_c = self.critical_specific_energy()
        
        # 图1：比能曲线
        ax1 = plt.subplot(3, 3, 1)
        
        h_array, E_array = self.specific_energy_curve()
        
        ax1.plot(E_array, h_array, 'b-', linewidth=2.5, label='比能曲线')
        
        # 临界点
        ax1.plot([E_c], [h_c], 'ro', markersize=12, label='临界状态')
        
        # 临界线
        ax1.axhline(y=h_c, color='r', linestyle='--', linewidth=1.5,
                   alpha=0.7, label=f'h_c={h_c:.3f}m')
        ax1.axvline(x=E_c, color='r', linestyle='--', linewidth=1.5,
                   alpha=0.7, label=f'E_c={E_c:.3f}m')
        
        # 填充区域
        # 急流区（h < h_c）
        idx_c = np.argmin(np.abs(h_array - h_c))
        ax1.fill_betweenx(h_array[:idx_c], E_c, E_array[:idx_c],
                         color='lightcoral', alpha=0.3, label='急流区(Fr>1)')
        
        # 缓流区（h > h_c）
        ax1.fill_betweenx(h_array[idx_c:], E_c, E_array[idx_c:],
                         color='lightblue', alpha=0.3, label='缓流区(Fr<1)')
        
        # 标注
        ax1.text(E_c + 0.5, h_c - 0.3, '临界状态\nFr=1',
                fontsize=10, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        ax1.set_xlabel('比能 E (m)', fontsize=11, fontweight='bold')
        ax1.set_ylabel('水深 h (m)', fontsize=11, fontweight='bold')
        ax1.set_title('水深-比能曲线', fontsize=13, fontweight='bold')
        ax1.legend(fontsize=8, loc='upper left')
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim(E_c * 0.9, max(E_array) * 0.6)
        ax1.set_ylim(0, 4)
        
        # 图2：佛汝德数随水深的变化
        ax2 = plt.subplot(3, 3, 2)
        
        h_Fr = np.linspace(0.1, 4, 100)
        Fr_array = np.array([self.froude_number(h) for h in h_Fr])
        
        ax2.plot(h_Fr, Fr_array, 'b-', linewidth=2.5, label='Fr(h)')
        ax2.axhline(y=1.0, color='r', linestyle='--', linewidth=2,
                   label='Fr=1（临界）')
        ax2.axvline(x=h_c, color='r', linestyle='--', linewidth=1.5,
                   alpha=0.7)
        
        # 填充区域
        ax2.fill_between(h_Fr, 0, Fr_array, where=(Fr_array > 1),
                        color='lightcoral', alpha=0.3, label='急流(Fr>1)')
        ax2.fill_between(h_Fr, 0, Fr_array, where=(Fr_array <= 1),
                        color='lightblue', alpha=0.3, label='缓流(Fr<1)')
        
        # 当前临界点
        ax2.plot([h_c], [1.0], 'ro', markersize=12, label='临界点')
        
        ax2.set_xlabel('水深 h (m)', fontsize=11, fontweight='bold')
        ax2.set_ylabel('佛汝德数 Fr', fontsize=11, fontweight='bold')
        ax2.set_title('佛汝德数随水深的变化', fontsize=13, fontweight='bold')
        ax2.legend(fontsize=8)
        ax2.grid(True, alpha=0.3)
        ax2.set_ylim(0, 4)
        
        # 图3：流量对临界水深的影响
        ax3 = plt.subplot(3, 3, 3)
        
        Q_array, hc_array, vc_array, Ec_array = self.discharge_analysis()
        
        ax3.plot(Q_array, hc_array, 'b-', linewidth=2.5, label='h_c(Q)')
        ax3.plot([self.Q], [h_c], 'ro', markersize=12, label='当前流量')
        
        ax3.set_xlabel('流量 Q (m³/s)', fontsize=11, fontweight='bold')
        ax3.set_ylabel('临界水深 h_c (m)', fontsize=11, fontweight='bold')
        ax3.set_title('流量对临界水深的影响', fontsize=13, fontweight='bold')
        ax3.legend(fontsize=10)
        ax3.grid(True, alpha=0.3)
        
        # 标注关系
        ax3.text(6, 1.5,
                'h_c ∝ Q^(2/3)\n（2/3次方关系）',
                fontsize=10, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        # 图4：流量对临界流速的影响
        ax4 = plt.subplot(3, 3, 4)
        
        ax4.plot(Q_array, vc_array, 'r-', linewidth=2.5, label='v_c(Q)')
        ax4.plot([self.Q], [v_c], 'go', markersize=12, label='当前流量')
        
        ax4.set_xlabel('流量 Q (m³/s)', fontsize=11, fontweight='bold')
        ax4.set_ylabel('临界流速 v_c (m/s)', fontsize=11, fontweight='bold')
        ax4.set_title('流量对临界流速的影响', fontsize=13, fontweight='bold')
        ax4.legend(fontsize=10)
        ax4.grid(True, alpha=0.3)
        
        # 标注关系
        ax4.text(6, max(vc_array)*0.7,
                'v_c ∝ Q^(1/3)\n（1/3次方关系）',
                fontsize=10, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        # 图5：渠宽对临界水深的影响
        ax5 = plt.subplot(3, 3, 5)
        
        b_array, hc_b, vc_b = self.width_analysis()
        
        ax5.plot(b_array, hc_b, 'b-', linewidth=2.5, label='h_c(b)')
        ax5.plot([self.b], [h_c], 'ro', markersize=12, label='当前渠宽')
        
        ax5.set_xlabel('渠底宽度 b (m)', fontsize=11, fontweight='bold')
        ax5.set_ylabel('临界水深 h_c (m)', fontsize=11, fontweight='bold')
        ax5.set_title('渠宽对临界水深的影响', fontsize=13, fontweight='bold')
        ax5.legend(fontsize=10)
        ax5.grid(True, alpha=0.3)
        
        # 标注关系
        ax5.text(3, max(hc_b)*0.6,
                'h_c ∝ b^(-2/3)\n（反比关系）',
                fontsize=10, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        # 图6：共轭水深分析
        ax6 = plt.subplot(3, 3, 6)
        
        # 选择几个比能值
        E_values = [E_c * 1.2, E_c * 1.5, E_c * 2.0]
        colors = ['red', 'blue', 'green']
        
        for E_val, color in zip(E_values, colors):
            h1, h2 = self.depth_for_energy(E_val)
            if h1 is not None and h2 is not None:
                ax6.plot([E_val, E_val], [h1, h2], 'o-', color=color,
                        linewidth=2, markersize=8,
                        label=f'E={E_val:.2f}m: h1={h1:.2f}, h2={h2:.2f}')
        
        # 绘制比能曲线作为参考
        ax6.plot(E_array, h_array, 'k--', linewidth=1, alpha=0.5,
                label='比能曲线')
        
        # 临界点
        ax6.plot([E_c], [h_c], 'ro', markersize=12, label='临界点')
        
        ax6.set_xlabel('比能 E (m)', fontsize=11, fontweight='bold')
        ax6.set_ylabel('水深 h (m)', fontsize=11, fontweight='bold')
        ax6.set_title('共轭水深分析', fontsize=13, fontweight='bold')
        ax6.legend(fontsize=8)
        ax6.grid(True, alpha=0.3)
        ax6.set_xlim(E_c * 0.9, max(E_values) * 1.1)
        ax6.set_ylim(0, 4)
        
        # 图7：临界状态参数对比
        ax7 = plt.subplot(3, 3, 7)
        
        params = ['h_c\n(m)', 'v_c\n(m/s)', 'E_c\n(m)', 'Fr']
        values = [h_c, v_c, E_c, 1.0]
        colors_bar = ['blue', 'red', 'green', 'purple']
        
        bars = ax7.bar(params, values, color=colors_bar, alpha=0.7)
        
        # 标注数值
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax7.text(bar.get_x() + bar.get_width()/2., height,
                    f'{val:.3f}',
                    ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        ax7.set_ylabel('数值', fontsize=11, fontweight='bold')
        ax7.set_title('临界状态参数', fontsize=13, fontweight='bold')
        ax7.grid(True, alpha=0.3, axis='y')
        
        # 图8：流速与水深关系
        ax8 = plt.subplot(3, 3, 8)
        
        h_v = np.linspace(0.2, 4, 100)
        v_h = self.Q / (self.b * h_v)
        
        ax8.plot(h_v, v_h, 'b-', linewidth=2.5, label='v(h)')
        
        # 临界点
        ax8.plot([h_c], [v_c], 'ro', markersize=12, label='临界点')
        
        # 临界线
        ax8.axhline(y=v_c, color='r', linestyle='--', linewidth=1.5,
                   alpha=0.7, label=f'v_c={v_c:.3f}m/s')
        ax8.axvline(x=h_c, color='r', linestyle='--', linewidth=1.5,
                   alpha=0.7, label=f'h_c={h_c:.3f}m')
        
        ax8.set_xlabel('水深 h (m)', fontsize=11, fontweight='bold')
        ax8.set_ylabel('流速 v (m/s)', fontsize=11, fontweight='bold')
        ax8.set_title('流速与水深关系', fontsize=13, fontweight='bold')
        ax8.legend(fontsize=9)
        ax8.grid(True, alpha=0.3)
        
        # 标注关系
        ax8.text(2.5, 2,
                'v = Q/(bh)\n（反比关系）',
                fontsize=10, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        # 图9：临界状态示意图
        ax9 = plt.subplot(3, 3, 9)
        
        # 绘制三种流态
        flow_types = ['急流\n(h<h_c)\nFr>1', '临界流\n(h=h_c)\nFr=1', '缓流\n(h>h_c)\nFr<1']
        y_positions = [0.7, 0.4, 0.1]
        colors_flow = ['lightcoral', 'yellow', 'lightblue']
        
        for i, (flow_type, y_pos, color) in enumerate(zip(flow_types, y_positions, colors_flow)):
            ax9.add_patch(plt.Rectangle((0.1, y_pos), 0.8, 0.2,
                                       facecolor=color, edgecolor='black', linewidth=2))
            ax9.text(0.5, y_pos + 0.1, flow_type, ha='center', va='center',
                    fontsize=11, fontweight='bold')
        
        ax9.set_xlim(0, 1)
        ax9.set_ylim(0, 1)
        ax9.axis('off')
        ax9.set_title('流态分类', fontsize=13, fontweight='bold')
        
        plt.tight_layout()
        plt.show()
    
    def print_results(self):
        """打印计算结果"""
        print("=" * 70)
        print("临界水深计算")
        print("=" * 70)
        
        print(f"\n输入参数：")
        print(f"  渠底宽度：b = {self.b}m")
        print(f"  流量：Q = {self.Q}m³/s")
        
        # (1) 临界水深
        h_c = self.critical_depth()
        
        print(f"\n(1) 临界水深：")
        print(f"  矩形断面临界水深公式：")
        print(f"    h_c = (Q²/(gb²))^(1/3)")
        print(f"        = ({self.Q}² / ({self.g}×{self.b}²))^(1/3)")
        print(f"        = ({self.Q**2} / {self.g * self.b**2:.2f})^(1/3)")
        print(f"        = {(self.Q**2 / (self.g * self.b**2)):.4f}^(1/3)")
        print(f"        = {h_c:.4f} m")
        
        # (2) 临界流速
        v_c = self.critical_velocity()
        
        print(f"\n(2) 临界流速：")
        print(f"  v_c = Q / (b × h_c)")
        print(f"      = {self.Q} / ({self.b} × {h_c:.4f})")
        print(f"      = {v_c:.4f} m/s")
        
        # 验证Fr=1
        Fr_c = self.froude_number(h_c)
        print(f"\n  验证佛汝德数：")
        print(f"    Fr_c = v_c / √(g×h_c)")
        print(f"         = {v_c:.4f} / √({self.g}×{h_c:.4f})")
        print(f"         = {Fr_c:.6f}")
        print(f"    ✓ Fr = 1（临界流）")
        
        # 临界流速与水深关系
        vc_gh = v_c / np.sqrt(self.g * h_c)
        print(f"\n  临界条件：v_c² = g×h_c")
        print(f"    v_c² = {v_c**2:.4f} m²/s²")
        print(f"    g×h_c = {self.g * h_c:.4f} m²/s²")
        print(f"    v_c = √(g×h_c) = {np.sqrt(self.g * h_c):.4f} m/s")
        
        # (3) 临界比能
        E_c = self.critical_specific_energy()
        
        print(f"\n(3) 临界比能：")
        print(f"  方法1：E_c = h_c + v_c²/(2g)")
        print(f"        = {h_c:.4f} + {v_c**2/(2*self.g):.4f}")
        print(f"        = {E_c:.4f} m")
        
        print(f"\n  方法2：E_c = (3/2) × h_c")
        print(f"        = 1.5 × {h_c:.4f}")
        print(f"        = {1.5*h_c:.4f} m")
        print(f"    （两种方法结果一致）")
        
        # 比能组成
        print(f"\n  比能组成：")
        print(f"    位置水头：h_c = {h_c:.4f} m（占{h_c/E_c*100:.1f}%）")
        print(f"    流速水头：v_c²/(2g) = {v_c**2/(2*self.g):.4f} m（占{v_c**2/(2*self.g)/E_c*100:.1f}%）")
        print(f"    总比能：E_c = {E_c:.4f} m")
        
        # (4) 不同流量
        print(f"\n(4) 不同流量下的临界水深：")
        print(f"\n  {'流量Q(m³/s)':<15} {'临界水深h_c(m)':<20} {'临界流速v_c(m/s)':<20} {'临界比能E_c(m)':<15}")
        print(f"  {'-'*70}")
        
        Q_test = [1, 2, 3, 4, 5, 6, 8, 10]
        for Q_val in Q_test:
            hc_val = (Q_val**2 / (self.g * self.b**2))**(1/3)
            vc_val = Q_val / (self.b * hc_val)
            Ec_val = 1.5 * hc_val
            
            marker = " ✓" if abs(Q_val - self.Q) < 0.01 else ""
            print(f"  {Q_val:<15.1f} {hc_val:<20.4f} {vc_val:<20.4f} {Ec_val:<15.4f}{marker}")
        
        print(f"\n  规律：h_c ∝ Q^(2/3)")
        print(f"        流量增加1倍 → 临界水深增加2^(2/3) = {2**(2/3):.3f}倍")
        
        # (5) 共轭水深
        print(f"\n(5) 共轭水深分析：")
        print(f"  给定比能，存在两个可能的水深（共轭水深）：")
        print(f"\n  {'比能E(m)':<15} {'急流水深h1(m)':<20} {'缓流水深h2(m)':<20} {'佛汝德数Fr1/Fr2':<20}")
        print(f"  {'-'*75}")
        
        E_test = [E_c * 1.1, E_c * 1.5, E_c * 2.0, E_c * 3.0]
        for E_val in E_test:
            h1, h2 = self.depth_for_energy(E_val)
            if h1 is not None and h2 is not None:
                Fr1 = self.froude_number(h1)
                Fr2 = self.froude_number(h2)
                print(f"  {E_val:<15.4f} {h1:<20.4f} {h2:<20.4f} {Fr1:.2f} / {Fr2:.2f}")
            else:
                print(f"  {E_val:<15.4f} {'无解':<20} {'无解':<20} {'---':<20}")
        
        print(f"\n  注：")
        print(f"    • 当E < E_c时，无实际水深（水流无法通过）")
        print(f"    • 当E = E_c时，唯一水深h = h_c（临界流）")
        print(f"    • 当E > E_c时，存在两个共轭水深")
        print(f"      - 较小水深h1：急流（Fr > 1）")
        print(f"      - 较大水深h2：缓流（Fr < 1）")
        
        print("\n" + "=" * 70)
        print("考试要点：")
        print("=" * 70)
        print("1. 临界水深公式（矩形）：h_c = (Q²/(gb²))^(1/3)")
        print("2. 临界条件：Fr = 1，v² = gh")
        print("3. 临界比能：E_c = (3/2)h_c（最小比能）")
        print("4. 流态判别：h<h_c急流，h=h_c临界流，h>h_c缓流")
        print("5. 共轭水深：相同比能、不同流态的两个水深")
        print("=" * 70)


def main():
    """主函数"""
    print("\n" + "💧" * 35)
    print("第03章 管流与明渠流 - 题目9：临界水深计算")
    print("💧" * 35 + "\n")
    
    # 题目参数
    b = 2.0         # 渠底宽度2m
    Q = 4.0         # 流量4m³/s
    
    # 创建临界水深分析对象
    critical = CriticalDepthAnalysis(b=b, Q=Q)
    
    # 打印结果
    critical.print_results()
    
    # 绘图
    print("\n正在绘制临界水深分析图...")
    critical.plot_analysis()
    
    print("\n✅ 计算完成！")


if __name__ == "__main__":
    main()
