#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第04章 地下水与渗流 - 题目3：承压完整井计算

题目描述：
某承压含水层，已知：
- 厚度M=10m
- 渗透系数k=8m/d
- 初始水头H₀=50m
- 井半径r₀=0.2m
- 影响半径R=200m
- 抽水稳定后井中水头hw=40m

求：
(1) 井的出水量Q
(2) 距井轴r=30m和r=100m处的水头
(3) 绘制水头分布曲线
(4) 两井叠加计算

知识点：
- 承压完整井公式
- 水头分布
- 叠加原理
- 群井干扰

作者：CHS-Books Team
日期：2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class ConfinedWellFlow:
    """承压完整井流动分析类"""
    
    def __init__(self, M: float, k: float, H0: float, r0: float, R: float, hw: float):
        """
        初始化参数
        
        Parameters:
        -----------
        M : float
            承压含水层厚度 (m)
        k : float
            渗透系数 (m/d)
        H0 : float
            初始水头 (m)
        r0 : float
            井半径 (m)
        R : float
            影响半径 (m)
        hw : float
            井中水头 (m)
        """
        self.M = M
        self.k = k
        self.H0 = H0
        self.r0 = r0
        self.R = R
        self.hw = hw
    
    def discharge(self) -> float:
        """
        计算井的出水量
        
        Q = 2πkM(H₀-hw)/ln(R/r₀)
        
        Returns:
        --------
        float : 出水量 (m³/d)
        """
        return 2 * np.pi * self.k * self.M * (self.H0 - self.hw) / np.log(self.R / self.r0)
    
    def head_at_radius(self, r: float) -> float:
        """
        计算距井轴r处的水头
        
        h(r) = H₀ - Q/(2πkM) * ln(R/r)
        
        Parameters:
        -----------
        r : float
            距井轴距离 (m)
            
        Returns:
        --------
        float : 水头 (m)
        """
        Q = self.discharge()
        if r <= 0 or r > self.R:
            return self.H0
        return self.H0 - Q / (2 * np.pi * self.k * self.M) * np.log(self.R / r)
    
    def drawdown_at_radius(self, r: float) -> float:
        """
        计算距井轴r处的降深
        
        s(r) = H₀ - h(r)
        
        Parameters:
        -----------
        r : float
            距井轴距离 (m)
            
        Returns:
        --------
        float : 降深 (m)
        """
        return self.H0 - self.head_at_radius(r)
    
    def head_distribution(self, r_range: tuple = None, n_points: int = 100) -> tuple:
        """
        计算水头分布
        
        Parameters:
        -----------
        r_range : tuple
            半径范围 (m)
        n_points : int
            计算点数
            
        Returns:
        --------
        tuple : (r_array, h_array, s_array)
        """
        if r_range is None:
            r_range = (self.r0, self.R)
        
        r_array = np.logspace(np.log10(r_range[0]), np.log10(r_range[1]), n_points)
        h_array = np.array([self.head_at_radius(r) for r in r_array])
        s_array = self.H0 - h_array
        
        return r_array, h_array, s_array
    
    def two_wells_interference(self, d: float) -> tuple:
        """
        计算两井干扰（叠加原理）
        
        Parameters:
        -----------
        d : float
            两井距离 (m)
            
        Returns:
        --------
        tuple : (s1_at_well2, s2_at_well1, total_drawdown)
        """
        # 井1在井2处引起的降深
        s1_at_well2 = self.drawdown_at_radius(d)
        
        # 井2在井1处引起的降深（对称）
        s2_at_well1 = s1_at_well2
        
        # 每口井的总降深（自身 + 对方影响）
        s_well1 = self.H0 - self.hw  # 单井时的降深
        total_drawdown_well1 = s_well1 + s2_at_well1
        
        # 井中新水头
        new_hw = self.H0 - total_drawdown_well1
        
        return s1_at_well2, s2_at_well1, total_drawdown_well1, new_hw
    
    def permeability_analysis(self, k_range: tuple = (5, 15), n_points: int = 50) -> tuple:
        """
        渗透系数影响分析
        
        Parameters:
        -----------
        k_range : tuple
            渗透系数范围 (m/d)
        n_points : int
            计算点数
            
        Returns:
        --------
        tuple : (k_array, Q_array)
        """
        k_array = np.linspace(k_range[0], k_range[1], n_points)
        Q_array = 2 * np.pi * k_array * self.M * (self.H0 - self.hw) / np.log(self.R / self.r0)
        
        return k_array, Q_array
    
    def radius_analysis(self, R_range: tuple = (100, 500), n_points: int = 50) -> tuple:
        """
        影响半径影响分析
        
        Parameters:
        -----------
        R_range : tuple
            影响半径范围 (m)
        n_points : int
            计算点数
            
        Returns:
        --------
        tuple : (R_array, Q_array)
        """
        R_array = np.linspace(R_range[0], R_range[1], n_points)
        Q_array = 2 * np.pi * self.k * self.M * (self.H0 - self.hw) / np.log(R_array / self.r0)
        
        return R_array, Q_array
    
    def plot_analysis(self):
        """绘制井流分析图"""
        fig = plt.figure(figsize=(16, 12))
        
        Q = self.discharge()
        
        # 图1：承压井示意图
        ax1 = plt.subplot(3, 3, 1)
        
        # 绘制含水层
        x_max = min(self.R * 1.2, 250)
        ax1.fill_between([-x_max, x_max], [0, 0], [-self.M, -self.M],
                        color='lightblue', alpha=0.3, label='承压含水层')
        ax1.plot([-x_max, x_max], [0, 0], 'k-', linewidth=2, label='隔水顶板')
        ax1.plot([-x_max, x_max], [-self.M, -self.M], 'k-', linewidth=2, label='隔水底板')
        
        # 初始水头线
        ax1.plot([-x_max, x_max], [self.H0 - self.M, self.H0 - self.M], 
                'b--', linewidth=1.5, alpha=0.7, label=f'初始水头H₀={self.H0}m')
        
        # 抽水后水头线（简化）
        r_plot = np.logspace(np.log10(self.r0), np.log10(x_max), 50)
        h_plot = np.array([self.head_at_radius(r) for r in r_plot])
        ax1.plot(r_plot, h_plot - self.M, 'r-', linewidth=2, label='抽水后水头')
        ax1.plot(-r_plot, h_plot - self.M, 'r-', linewidth=2)
        
        # 井
        well = Circle((0, -self.M/2), self.r0 * 50, color='brown', alpha=0.5)
        ax1.add_patch(well)
        ax1.plot([0, 0], [self.hw - self.M, 0], 'b-', linewidth=4, label='井筒')
        
        # 标注
        ax1.text(0, self.hw - self.M - 2, f'井中水头\nhw={self.hw}m',
                ha='center', fontsize=9, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        ax1.set_xlim(-x_max, x_max)
        ax1.set_ylim(-self.M - 5, self.H0 - self.M + 5)
        ax1.set_xlabel('水平距离 (m)', fontsize=10, fontweight='bold')
        ax1.set_ylabel('高程 (m)', fontsize=10, fontweight='bold')
        ax1.set_title('承压完整井示意图', fontsize=13, fontweight='bold')
        ax1.legend(fontsize=8, loc='upper right')
        ax1.grid(True, alpha=0.3)
        ax1.axhline(y=0, color='k', linewidth=0.5)
        ax1.axvline(x=0, color='k', linewidth=0.5)
        
        # 图2：水头分布（对数坐标）
        ax2 = plt.subplot(3, 3, 2)
        
        r_array, h_array, s_array = self.head_distribution()
        
        ax2.semilogx(r_array, h_array, 'b-', linewidth=2.5, label='水头h(r)')
        ax2.axhline(y=self.H0, color='g', linestyle='--', linewidth=1.5,
                   alpha=0.7, label=f'初始水头H₀={self.H0}m')
        
        # 标注特殊点
        r_special = [self.r0, 30, 100, self.R]
        for r in r_special:
            h = self.head_at_radius(r)
            ax2.plot([r], [h], 'ro', markersize=8)
            if r == self.r0:
                ax2.text(r, h - 2, f'井\nr={r}m\nh={h:.1f}m',
                        ha='center', fontsize=8)
            elif r < self.R:
                ax2.text(r, h + 1, f'r={r}m\nh={h:.2f}m',
                        ha='center', fontsize=8)
        
        ax2.set_xlabel('距井轴距离 r (m)', fontsize=11, fontweight='bold')
        ax2.set_ylabel('水头 h (m)', fontsize=11, fontweight='bold')
        ax2.set_title('水头分布曲线（对数坐标）', fontsize=13, fontweight='bold')
        ax2.legend(fontsize=9)
        ax2.grid(True, alpha=0.3, which='both')
        
        # 图3：降深分布
        ax3 = plt.subplot(3, 3, 3)
        
        ax3.semilogx(r_array, s_array, 'r-', linewidth=2.5, label='降深s(r)')
        
        # 标注特殊点
        for r in r_special:
            s = self.drawdown_at_radius(r)
            ax3.plot([r], [s], 'bo', markersize=8)
            if r == self.r0:
                ax3.text(r * 2, s, f'井\ns={s:.1f}m',
                        fontsize=8, fontweight='bold')
        
        ax3.set_xlabel('距井轴距离 r (m)', fontsize=11, fontweight='bold')
        ax3.set_ylabel('降深 s (m)', fontsize=11, fontweight='bold')
        ax3.set_title('降深分布曲线（对数坐标）', fontsize=13, fontweight='bold')
        ax3.legend(fontsize=9)
        ax3.grid(True, alpha=0.3, which='both')
        
        ax3.text(5, max(s_array) * 0.5,
                '降深特点：\n• 井附近最大\n• 对数衰减\n• 边界处为0',
                fontsize=9, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        # 图4：流线与等水头线
        ax4 = plt.subplot(3, 3, 4)
        
        # 等水头线（圆形）
        h_levels = [42, 44, 46, 48, 49, 49.5]
        for h_level in h_levels:
            # 求对应的r
            if h_level > self.hw and h_level < self.H0:
                # h = H0 - Q/(2πkM) * ln(R/r)
                # ln(R/r) = (H0 - h) * 2πkM / Q
                # r = R * exp(-(H0-h)*2πkM/Q)
                ln_term = (self.H0 - h_level) * 2 * np.pi * self.k * self.M / Q
                r_level = self.R * np.exp(-ln_term)
                
                circle = Circle((0, 0), r_level, fill=False, 
                              edgecolor='blue', linewidth=1.5, alpha=0.6)
                ax4.add_patch(circle)
                ax4.text(r_level, 0, f'{h_level}m', fontsize=8)
        
        # 流线（径向）
        angles = np.linspace(0, 2*np.pi, 12, endpoint=False)
        for angle in angles:
            x_line = [self.r0 * np.cos(angle), self.R * 0.8 * np.cos(angle)]
            y_line = [self.r0 * np.sin(angle), self.R * 0.8 * np.sin(angle)]
            ax4.plot(x_line, y_line, 'r-', linewidth=0.8, alpha=0.5)
            # 箭头
            mid_x = (x_line[0] + x_line[1]) / 2
            mid_y = (y_line[0] + y_line[1]) / 2
            ax4.arrow(mid_x * 0.8, mid_y * 0.8, 
                     (mid_x - mid_x * 0.8) * 0.3, (mid_y - mid_y * 0.8) * 0.3,
                     head_width=5, head_length=3, fc='red', ec='red', alpha=0.5)
        
        # 井
        well_circle = Circle((0, 0), self.r0, color='brown', alpha=0.7)
        ax4.add_patch(well_circle)
        
        # 影响半径
        influence_circle = Circle((0, 0), self.R, fill=False,
                                 edgecolor='green', linewidth=2, linestyle='--')
        ax4.add_patch(influence_circle)
        ax4.text(self.R * 0.7, self.R * 0.7, f'影响半径R={self.R}m',
                fontsize=9, fontweight='bold', color='green')
        
        ax4.set_xlim(-self.R * 1.1, self.R * 1.1)
        ax4.set_ylim(-self.R * 1.1, self.R * 1.1)
        ax4.set_aspect('equal')
        ax4.set_xlabel('X (m)', fontsize=10, fontweight='bold')
        ax4.set_ylabel('Y (m)', fontsize=10, fontweight='bold')
        ax4.set_title('流线与等水头线（平面图）', fontsize=13, fontweight='bold')
        ax4.grid(True, alpha=0.3)
        
        # 图5：渗透系数影响
        ax5 = plt.subplot(3, 3, 5)
        
        k_array, Q_k = self.permeability_analysis()
        
        ax5.plot(k_array, Q_k, 'b-', linewidth=2.5, label='出水量Q(k)')
        ax5.plot([self.k], [Q], 'ro', markersize=12, label='当前状态')
        
        ax5.set_xlabel('渗透系数 k (m/d)', fontsize=11, fontweight='bold')
        ax5.set_ylabel('出水量 Q (m³/d)', fontsize=11, fontweight='bold')
        ax5.set_title('渗透系数的影响', fontsize=13, fontweight='bold')
        ax5.legend(fontsize=10)
        ax5.grid(True, alpha=0.3)
        
        ax5.text(10, max(Q_k) * 0.6,
                'Q ∝ k\n（线性关系）',
                fontsize=10, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        # 图6：影响半径影响
        ax6 = plt.subplot(3, 3, 6)
        
        R_array, Q_R = self.radius_analysis()
        
        ax6.plot(R_array, Q_R, 'g-', linewidth=2.5, label='出水量Q(R)')
        ax6.plot([self.R], [Q], 'ro', markersize=12, label='当前状态')
        
        ax6.set_xlabel('影响半径 R (m)', fontsize=11, fontweight='bold')
        ax6.set_ylabel('出水量 Q (m³/d)', fontsize=11, fontweight='bold')
        ax6.set_title('影响半径的影响', fontsize=13, fontweight='bold')
        ax6.legend(fontsize=10)
        ax6.grid(True, alpha=0.3)
        
        ax6.text(300, max(Q_R) * 0.7,
                'Q随R增大而减小\n（对数关系）',
                fontsize=10, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        # 图7：两井干扰示意图
        ax7 = plt.subplot(3, 3, 7)
        
        d = 100  # 两井距离
        s1_at_2, s2_at_1, total_s, new_hw = self.two_wells_interference(d)
        
        # 单井降深曲线
        r_single = np.logspace(np.log10(self.r0), np.log10(self.R), 100)
        s_single = np.array([self.drawdown_at_radius(r) for r in r_single])
        
        ax7.semilogx(r_single, s_single, 'b--', linewidth=1.5, 
                    alpha=0.7, label='单井降深')
        
        # 两井时的总降深（简化示意）
        ax7.semilogx(r_single, s_single * 1.2, 'r-', linewidth=2.5,
                    label='两井总降深（示意）')
        
        # 标注
        ax7.axhline(y=self.H0 - self.hw, color='blue', linestyle=':',
                   linewidth=1.5, alpha=0.7, label=f'单井降深={self.H0-self.hw}m')
        ax7.axhline(y=total_s, color='red', linestyle=':',
                   linewidth=1.5, label=f'两井总降深={total_s:.2f}m')
        
        ax7.set_xlabel('距井轴距离 r (m)', fontsize=11, fontweight='bold')
        ax7.set_ylabel('降深 s (m)', fontsize=11, fontweight='bold')
        ax7.set_title('两井干扰（叠加原理）', fontsize=13, fontweight='bold')
        ax7.legend(fontsize=8)
        ax7.grid(True, alpha=0.3, which='both')
        
        # 图8：参数汇总
        ax8 = plt.subplot(3, 3, 8)
        
        params_text = f"""
承压井计算结果

【基本参数】
厚度 M = {self.M} m
渗透系数 k = {self.k} m/d
初始水头 H₀ = {self.H0} m
井半径 r₀ = {self.r0} m
影响半径 R = {self.R} m
井中水头 hw = {self.hw} m

【计算结果】
出水量 Q = {Q:.2f} m³/d
         = {Q/24:.2f} m³/h
         = {Q/86400*1000:.2f} L/s

降深 sw = {self.H0 - self.hw} m

【特定点水头】
r = 30m:  h = {self.head_at_radius(30):.2f} m
r = 100m: h = {self.head_at_radius(100):.2f} m

【两井干扰】
井间距 d = {d} m
叠加降深 = {total_s:.2f} m
新井中水头 = {new_hw:.2f} m
"""
        
        ax8.text(0.1, 0.5, params_text, fontsize=9, fontfamily='monospace',
                verticalalignment='center',
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
        ax8.axis('off')
        ax8.set_title('计算结果汇总', fontsize=13, fontweight='bold')
        
        # 图9：公式总结
        ax9 = plt.subplot(3, 3, 9)
        
        formula_text = """
承压完整井公式

【出水量】
Q = 2πkM(H₀-hw)/ln(R/r₀)

【水头分布】
h(r) = H₀ - Q/(2πkM)·ln(R/r)

【降深】
s(r) = H₀ - h(r)
     = Q/(2πkM)·ln(R/r)

【叠加原理】
多井同时抽水：
s_总 = Σ s_i

特点：
• 线性叠加
• 各井独立
• 代数求和
"""
        
        ax9.text(0.1, 0.5, formula_text, fontsize=10, fontfamily='monospace',
                verticalalignment='center',
                bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
        ax9.axis('off')
        ax9.set_title('公式总结', fontsize=13, fontweight='bold')
        
        plt.tight_layout()
        plt.show()
    
    def print_results(self):
        """打印计算结果"""
        print("=" * 70)
        print("承压完整井计算")
        print("=" * 70)
        
        print(f"\n输入参数：")
        print(f"  承压含水层厚度：M = {self.M} m")
        print(f"  渗透系数：k = {self.k} m/d")
        print(f"  初始水头：H₀ = {self.H0} m（从含水层底板算起）")
        print(f"  井半径：r₀ = {self.r0} m")
        print(f"  影响半径：R = {self.R} m")
        print(f"  井中水头：hw = {self.hw} m")
        
        # (1) 出水量
        Q = self.discharge()
        
        print(f"\n(1) 井的出水量：")
        print(f"  承压完整井公式：")
        print(f"    Q = 2πkM(H₀-hw)/ln(R/r₀)")
        print(f"      = 2π × {self.k} × {self.M} × ({self.H0}-{self.hw}) / ln({self.R}/{self.r0})")
        print(f"      = 2π × {self.k} × {self.M} × {self.H0-self.hw} / ln({self.R/self.r0:.1f})")
        print(f"      = {2*np.pi*self.k*self.M*(self.H0-self.hw):.2f} / {np.log(self.R/self.r0):.3f}")
        print(f"      = {Q:.2f} m³/d")
        
        print(f"\n  单位换算：")
        print(f"    Q = {Q:.2f} m³/d")
        print(f"      = {Q/24:.2f} m³/h")
        print(f"      = {Q/86400:.6f} m³/s")
        print(f"      = {Q/86400*1000:.2f} L/s")
        
        print(f"\n  降深：")
        print(f"    sw = H₀ - hw = {self.H0} - {self.hw} = {self.H0-self.hw} m")
        
        # (2) 特定半径处水头
        r_values = [30, 100]
        
        print(f"\n(2) 距井轴不同距离处的水头：")
        print(f"  公式：h(r) = H₀ - Q/(2πkM) × ln(R/r)")
        
        for r in r_values:
            h = self.head_at_radius(r)
            s = self.drawdown_at_radius(r)
            
            print(f"\n  r = {r} m：")
            print(f"    h_{r} = {self.H0} - {Q:.2f}/(2π×{self.k}×{self.M}) × ln({self.R}/{r})")
            coef = Q / (2 * np.pi * self.k * self.M)
            print(f"        = {self.H0} - {coef:.3f} × {np.log(self.R/r):.3f}")
            print(f"        = {self.H0} - {coef * np.log(self.R/r):.2f}")
            print(f"        = {h:.2f} m")
            print(f"    降深：s_{r} = H₀ - h_{r} = {self.H0} - {h:.2f} = {s:.2f} m")
        
        # (3) 水头分布曲线
        print(f"\n(3) 水头分布曲线：")
        print(f"\n  {'r(m)':<10} {'ln(R/r)':<12} {'h(m)':<12} {'s(m)':<12}")
        print(f"  {'-'*46}")
        
        r_table = [self.r0, 1, 5, 10, 30, 50, 100, self.R]
        for r in r_table:
            if r <= 0:
                continue
            ln_term = np.log(self.R / r) if r < self.R else 0
            h = self.head_at_radius(r)
            s = self.H0 - h
            marker = " (井)" if abs(r - self.r0) < 0.01 else (" (R)" if abs(r - self.R) < 0.01 else "")
            print(f"  {r:<10.2f} {ln_term:<12.3f} {h:<12.2f} {s:<12.2f}{marker}")
        
        print(f"\n  曲线特点：")
        print(f"    • 对数曲线")
        print(f"    • 井附近降深大")
        print(f"    • 远离井降深小")
        print(f"    • 影响半径处降深为0")
        
        # (4) 两井叠加
        d = 100  # 两井距离
        s1_at_2, s2_at_1, total_s, new_hw = self.two_wells_interference(d)
        
        print(f"\n(4) 两井干扰计算（叠加原理）：")
        print(f"  假设在r = {d}m处再钻一口相同的井")
        
        print(f"\n  井1在井2处引起的降深：")
        print(f"    s₁(r={d}) = {s1_at_2:.2f} m")
        
        print(f"\n  井2在井1处引起的降深：")
        print(f"    s₂(r={d}) = {s2_at_1:.2f} m（对称）")
        
        print(f"\n  叠加原理：")
        print(f"    两井同时抽水时，某点的总降深 = 各井单独作用时降深之和")
        
        print(f"\n  井1中的总降深：")
        print(f"    s_总1 = s_自身 + s_井2影响")
        print(f"          = {self.H0 - self.hw} + {s2_at_1:.2f}")
        print(f"          = {total_s:.2f} m")
        
        print(f"\n  井1中的新水头：")
        print(f"    hw_新 = H₀ - s_总1")
        print(f"          = {self.H0} - {total_s:.2f}")
        print(f"          = {new_hw:.2f} m")
        
        print(f"\n  对比：")
        print(f"    单井时：hw = {self.hw} m，降深 = {self.H0-self.hw} m")
        print(f"    两井时：hw = {new_hw:.2f} m，降深 = {total_s:.2f} m")
        print(f"    增加降深：Δs = {total_s - (self.H0-self.hw):.2f} m")
        
        print(f"\n  结论：")
        print(f"    • 两井干扰使降深增大")
        print(f"    • 距离越近，干扰越大")
        print(f"    • 需要合理布置井距")
        
        print("\n" + "=" * 70)
        print("考试要点：")
        print("=" * 70)
        print("1. 承压井公式：Q = 2πkM(H₀-hw)/ln(R/r₀)")
        print("2. 水头分布：h(r) = H₀ - Q/(2πkM)·ln(R/r)")
        print("3. 叠加原理：s_总 = Σs_i")
        print("4. 影响半径：R = 10s√(kM) (Kussakin公式)")
        print("5. 对数曲线特征")
        print("=" * 70)


def main():
    """主函数"""
    print("\n" + "💧" * 35)
    print("第04章 地下水与渗流 - 题目3：承压完整井计算")
    print("💧" * 35 + "\n")
    
    # 题目参数
    M = 10.0          # 含水层厚度10m
    k = 8.0           # 渗透系数8m/d
    H0 = 50.0         # 初始水头50m
    r0 = 0.2          # 井半径0.2m
    R = 200.0         # 影响半径200m
    hw = 40.0         # 井中水头40m
    
    # 创建承压井流动对象
    well = ConfinedWellFlow(M=M, k=k, H0=H0, r0=r0, R=R, hw=hw)
    
    # 打印结果
    well.print_results()
    
    # 绘图
    print("\n正在绘制井流分析图...")
    well.plot_analysis()
    
    print("\n✅ 计算完成！")


if __name__ == "__main__":
    main()
