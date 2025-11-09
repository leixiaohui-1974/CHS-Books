#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第03章 管流与明渠流 - 题目6：明渠均匀流计算

题目描述：
矩形断面明渠均匀流，已知：
- 渠底宽度b=3m
- 水深h=1.2m
- 渠底坡度i=0.001
- 粗糙系数n=0.025（混凝土）

求：
(1) 过水断面面积A与湿周χ
(2) 水力半径R
(3) 流速v（曼宁公式）
(4) 流量Q
(5) 最优断面设计

知识点：
- 明渠均匀流
- 曼宁公式
- 水力半径
- 水力最优断面

作者：CHS-Books Team
日期：2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class OpenChannelUniformFlow:
    """明渠均匀流计算类"""
    
    def __init__(self, b: float, h: float, i: float, n: float = 0.025,
                 g: float = 9.81):
        """
        初始化参数
        
        Parameters:
        -----------
        b : float
            渠底宽度 (m)
        h : float
            水深 (m)
        i : float
            渠底坡度
        n : float
            曼宁粗糙系数
        g : float
            重力加速度 (m/s²)
        """
        self.b = b
        self.h = h
        self.i = i
        self.n = n
        self.g = g
    
    def cross_section_area(self) -> float:
        """
        计算过水断面面积
        
        A = b × h
        
        Returns:
        --------
        float : 断面面积 (m²)
        """
        return self.b * self.h
    
    def wetted_perimeter(self) -> float:
        """
        计算湿周
        
        χ = b + 2h
        
        Returns:
        --------
        float : 湿周 (m)
        """
        return self.b + 2 * self.h
    
    def hydraulic_radius(self) -> float:
        """
        计算水力半径
        
        R = A / χ
        
        Returns:
        --------
        float : 水力半径 (m)
        """
        A = self.cross_section_area()
        chi = self.wetted_perimeter()
        return A / chi
    
    def velocity_manning(self) -> float:
        """
        用曼宁公式计算流速
        
        v = (1/n) × R^(2/3) × i^(1/2)
        
        Returns:
        --------
        float : 流速 (m/s)
        """
        R = self.hydraulic_radius()
        return (1 / self.n) * R**(2/3) * self.i**0.5
    
    def velocity_chezy(self) -> float:
        """
        用谢才公式计算流速
        
        v = C × √(R×i)
        C = R^(1/6) / n（曼宁-谢才关系）
        
        Returns:
        --------
        float : 流速 (m/s)
        """
        R = self.hydraulic_radius()
        C = R**(1/6) / self.n
        return C * np.sqrt(R * self.i)
    
    def discharge(self) -> float:
        """
        计算流量
        
        Q = A × v
        
        Returns:
        --------
        float : 流量 (m³/s)
        """
        A = self.cross_section_area()
        v = self.velocity_manning()
        return A * v
    
    def froude_number(self) -> float:
        """
        计算佛汝德数
        
        Fr = v / √(gD)
        D = A/B = h (矩形断面)
        
        Returns:
        --------
        float : 佛汝德数
        """
        v = self.velocity_manning()
        return v / np.sqrt(self.g * self.h)
    
    def optimal_depth(self) -> float:
        """
        计算水力最优断面的水深
        
        矩形断面最优条件：h = b/2
        
        Returns:
        --------
        float : 最优水深 (m)
        """
        return self.b / 2
    
    def optimal_section_analysis(self) -> tuple:
        """
        水力最优断面分析
        
        Returns:
        --------
        tuple : (h_opt, A_opt, chi_opt, R_opt, v_opt, Q_opt)
        """
        h_opt = self.optimal_depth()
        
        # 最优断面参数
        A_opt = self.b * h_opt
        chi_opt = self.b + 2 * h_opt
        R_opt = A_opt / chi_opt
        v_opt = (1 / self.n) * R_opt**(2/3) * self.i**0.5
        Q_opt = A_opt * v_opt
        
        return h_opt, A_opt, chi_opt, R_opt, v_opt, Q_opt
    
    def depth_analysis(self, h_range: tuple = None, n_points: int = 100) -> tuple:
        """
        不同水深下的水力特性分析
        
        Parameters:
        -----------
        h_range : tuple
            水深范围 (m)
        n_points : int
            计算点数
            
        Returns:
        --------
        tuple : (h_array, A_array, R_array, v_array, Q_array)
        """
        if h_range is None:
            h_range = (0.1, 2.5)
        
        h_array = np.linspace(h_range[0], h_range[1], n_points)
        
        A_array = self.b * h_array
        chi_array = self.b + 2 * h_array
        R_array = A_array / chi_array
        v_array = (1 / self.n) * R_array**(2/3) * self.i**0.5
        Q_array = A_array * v_array
        
        return h_array, A_array, R_array, v_array, Q_array
    
    def slope_analysis(self, i_range: tuple = (0.0001, 0.01), 
                      n_points: int = 50) -> tuple:
        """
        不同坡度下的流速和流量分析
        
        Parameters:
        -----------
        i_range : tuple
            坡度范围
        n_points : int
            计算点数
            
        Returns:
        --------
        tuple : (i_array, v_array, Q_array, Fr_array)
        """
        i_array = np.linspace(i_range[0], i_range[1], n_points)
        
        R = self.hydraulic_radius()
        A = self.cross_section_area()
        
        v_array = (1 / self.n) * R**(2/3) * i_array**0.5
        Q_array = A * v_array
        Fr_array = v_array / np.sqrt(self.g * self.h)
        
        return i_array, v_array, Q_array, Fr_array
    
    def roughness_analysis(self, n_range: tuple = (0.010, 0.040),
                          n_points: int = 50) -> tuple:
        """
        不同粗糙度的影响分析
        
        Parameters:
        -----------
        n_range : tuple
            粗糙系数范围
        n_points : int
            计算点数
            
        Returns:
        --------
        tuple : (n_array, v_array, Q_array)
        """
        n_array = np.linspace(n_range[0], n_range[1], n_points)
        
        R = self.hydraulic_radius()
        A = self.cross_section_area()
        
        v_array = (1 / n_array) * R**(2/3) * self.i**0.5
        Q_array = A * v_array
        
        return n_array, v_array, Q_array
    
    def plot_analysis(self):
        """绘制明渠均匀流分析图"""
        fig = plt.figure(figsize=(15, 12))
        
        # 图1：断面示意图
        ax1 = plt.subplot(3, 3, 1)
        
        # 绘制断面
        x_section = np.array([0, 0, self.b, self.b, 0])
        y_section = np.array([0, self.h, self.h, 0, 0])
        
        ax1.plot(x_section, y_section, 'b-', linewidth=3)
        ax1.fill(x_section, y_section, color='lightblue', alpha=0.5)
        
        # 标注尺寸
        ax1.annotate('', xy=(self.b, -0.1), xytext=(0, -0.1),
                    arrowprops=dict(arrowstyle='<->', color='red', lw=2))
        ax1.text(self.b/2, -0.25, f'b = {self.b}m', ha='center',
                fontsize=11, fontweight='bold', color='red')
        
        ax1.annotate('', xy=(-0.2, self.h), xytext=(-0.2, 0),
                    arrowprops=dict(arrowstyle='<->', color='red', lw=2))
        ax1.text(-0.5, self.h/2, f'h = {self.h}m', va='center',
                fontsize=11, fontweight='bold', color='red', rotation=90)
        
        # 标注水面
        ax1.text(self.b/2, self.h + 0.1, '水面', ha='center',
                fontsize=11, fontweight='bold', color='blue')
        
        # 标注渠底
        ax1.text(self.b/2, -0.5, f'渠底坡度 i = {self.i}', ha='center',
                fontsize=10, fontweight='bold')
        
        ax1.set_xlim(-0.8, self.b + 0.5)
        ax1.set_ylim(-0.6, self.h + 0.4)
        ax1.set_aspect('equal')
        ax1.set_xlabel('宽度 (m)', fontsize=10, fontweight='bold')
        ax1.set_ylabel('高度 (m)', fontsize=10, fontweight='bold')
        ax1.set_title('矩形明渠断面', fontsize=13, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        
        # 图2：水深对水力半径的影响
        ax2 = plt.subplot(3, 3, 2)
        
        h_array, A_array, R_array, v_array, Q_array = self.depth_analysis()
        
        ax2.plot(h_array, R_array, 'b-', linewidth=2.5, label='R(h)')
        ax2.plot([self.h], [self.hydraulic_radius()], 'ro', markersize=12,
                label='当前状态')
        
        # 标注最优水深
        h_opt = self.optimal_depth()
        _, _, _, R_opt, _, _ = self.optimal_section_analysis()
        ax2.plot([h_opt], [R_opt], 'g^', markersize=12, label='最优断面')
        ax2.axvline(x=h_opt, color='g', linestyle='--', linewidth=1.5, alpha=0.7)
        
        ax2.set_xlabel('水深 h (m)', fontsize=11, fontweight='bold')
        ax2.set_ylabel('水力半径 R (m)', fontsize=11, fontweight='bold')
        ax2.set_title('水深对水力半径的影响', fontsize=13, fontweight='bold')
        ax2.legend(fontsize=9)
        ax2.grid(True, alpha=0.3)
        
        # 图3：水深对流速的影响
        ax3 = plt.subplot(3, 3, 3)
        
        ax3.plot(h_array, v_array, 'r-', linewidth=2.5, label='v(h)')
        ax3.plot([self.h], [self.velocity_manning()], 'bo', markersize=12,
                label='当前状态')
        
        # 最优断面
        _, _, _, _, v_opt, _ = self.optimal_section_analysis()
        ax3.plot([h_opt], [v_opt], 'g^', markersize=12, label='最优断面')
        
        ax3.set_xlabel('水深 h (m)', fontsize=11, fontweight='bold')
        ax3.set_ylabel('流速 v (m/s)', fontsize=11, fontweight='bold')
        ax3.set_title('水深对流速的影响', fontsize=13, fontweight='bold')
        ax3.legend(fontsize=9)
        ax3.grid(True, alpha=0.3)
        
        # 图4：水深对流量的影响
        ax4 = plt.subplot(3, 3, 4)
        
        ax4.plot(h_array, Q_array, 'g-', linewidth=2.5, label='Q(h)')
        ax4.plot([self.h], [self.discharge()], 'ro', markersize=12,
                label='当前状态')
        
        # 最优断面
        _, _, _, _, _, Q_opt = self.optimal_section_analysis()
        ax4.plot([h_opt], [Q_opt], 'g^', markersize=12, label='最优断面')
        
        ax4.set_xlabel('水深 h (m)', fontsize=11, fontweight='bold')
        ax4.set_ylabel('流量 Q (m³/s)', fontsize=11, fontweight='bold')
        ax4.set_title('水深对流量的影响', fontsize=13, fontweight='bold')
        ax4.legend(fontsize=9)
        ax4.grid(True, alpha=0.3)
        
        # 图5：坡度对流速的影响
        ax5 = plt.subplot(3, 3, 5)
        
        i_array, v_i, Q_i, Fr_i = self.slope_analysis()
        
        ax5.plot(i_array*1000, v_i, 'b-', linewidth=2.5, label='流速v')
        ax5.plot([self.i*1000], [self.velocity_manning()], 'ro',
                markersize=12, label='当前状态')
        
        ax5.set_xlabel('坡度 i (‰)', fontsize=11, fontweight='bold')
        ax5.set_ylabel('流速 v (m/s)', fontsize=11, fontweight='bold')
        ax5.set_title('坡度对流速的影响', fontsize=13, fontweight='bold')
        ax5.legend(fontsize=9)
        ax5.grid(True, alpha=0.3)
        
        # 标注关系
        ax5.text(5, max(v_i)*0.7,
                'v ∝ √i\n（平方根关系）',
                fontsize=10, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        # 图6：坡度对佛汝德数的影响
        ax6 = plt.subplot(3, 3, 6)
        
        ax6.plot(i_array*1000, Fr_i, 'r-', linewidth=2.5, label='Fr(i)')
        ax6.axhline(y=1.0, color='g', linestyle='--', linewidth=2,
                   label='Fr=1（临界流）')
        
        # 标注流态区域
        ax6.fill_between(i_array*1000, 0, 1, color='lightblue',
                        alpha=0.3, label='缓流(Fr<1)')
        ax6.fill_between(i_array*1000, 1, max(Fr_i), color='lightcoral',
                        alpha=0.3, label='急流(Fr>1)')
        
        # 当前状态
        Fr = self.froude_number()
        ax6.plot([self.i*1000], [Fr], 'ko', markersize=12, label='当前状态')
        
        ax6.set_xlabel('坡度 i (‰)', fontsize=11, fontweight='bold')
        ax6.set_ylabel('佛汝德数 Fr', fontsize=11, fontweight='bold')
        ax6.set_title('坡度对佛汝德数的影响', fontsize=13, fontweight='bold')
        ax6.legend(fontsize=8)
        ax6.grid(True, alpha=0.3)
        
        # 图7：粗糙度影响
        ax7 = plt.subplot(3, 3, 7)
        
        n_array, v_n, Q_n = self.roughness_analysis()
        
        ax7_twin = ax7.twinx()
        
        line1 = ax7.plot(n_array*1000, v_n, 'b-', linewidth=2.5,
                        label='流速v', marker='o', markersize=4, markevery=5)
        line2 = ax7_twin.plot(n_array*1000, Q_n, 'r-', linewidth=2.5,
                             label='流量Q', marker='s', markersize=4, markevery=5)
        
        # 当前状态
        ax7.plot([self.n*1000], [self.velocity_manning()], 'go',
                markersize=12, label='当前状态')
        
        ax7.set_xlabel('粗糙系数 n (×10⁻³)', fontsize=11, fontweight='bold')
        ax7.set_ylabel('流速 v (m/s)', fontsize=11, fontweight='bold', color='b')
        ax7_twin.set_ylabel('流量 Q (m³/s)', fontsize=11, fontweight='bold', color='r')
        ax7.set_title('粗糙度的影响', fontsize=13, fontweight='bold')
        
        ax7.tick_params(axis='y', labelcolor='b')
        ax7_twin.tick_params(axis='y', labelcolor='r')
        
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax7.legend(lines, labels, fontsize=9)
        ax7.grid(True, alpha=0.3)
        
        # 图8：最优断面对比
        ax8 = plt.subplot(3, 3, 8)
        
        # 当前断面与最优断面对比
        sections = ['当前断面', '最优断面']
        A_values = [self.cross_section_area(), A_opt]
        chi_values = [self.wetted_perimeter(), chi_opt]
        R_values = [self.hydraulic_radius(), R_opt]
        
        x_pos = np.arange(len(sections))
        width = 0.25
        
        ax8.bar(x_pos - width, A_values, width, label='面积A (m²)', color='b')
        ax8.bar(x_pos, chi_values, width, label='湿周χ (m)', color='r')
        ax8.bar(x_pos + width, R_values, width, label='水力半径R (m)', color='g')
        
        ax8.set_ylabel('数值', fontsize=11, fontweight='bold')
        ax8.set_title('当前断面与最优断面对比', fontsize=13, fontweight='bold')
        ax8.set_xticks(x_pos)
        ax8.set_xticklabels(sections, fontsize=10, fontweight='bold')
        ax8.legend(fontsize=9)
        ax8.grid(True, alpha=0.3, axis='y')
        
        # 图9：输水效率分析
        ax9 = plt.subplot(3, 3, 9)
        
        # 计算不同水深下的输水效率（Q/χ）
        efficiency = Q_array / (self.b + 2*h_array)
        
        ax9.plot(h_array, efficiency, 'purple', linewidth=2.5, 
                label='输水效率Q/χ')
        ax9.plot([self.h], [self.discharge()/self.wetted_perimeter()],
                'ro', markersize=12, label='当前状态')
        
        # 最优点
        eff_opt = Q_opt / chi_opt
        ax9.plot([h_opt], [eff_opt], 'g^', markersize=12, label='最优断面')
        ax9.axvline(x=h_opt, color='g', linestyle='--', linewidth=1.5, alpha=0.7)
        
        ax9.set_xlabel('水深 h (m)', fontsize=11, fontweight='bold')
        ax9.set_ylabel('输水效率 Q/χ (m²/s)', fontsize=11, fontweight='bold')
        ax9.set_title('输水效率分析', fontsize=13, fontweight='bold')
        ax9.legend(fontsize=9)
        ax9.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    def print_results(self):
        """打印计算结果"""
        print("=" * 70)
        print("明渠均匀流计算")
        print("=" * 70)
        
        print(f"\n输入参数：")
        print(f"  渠底宽度：b = {self.b}m")
        print(f"  水深：h = {self.h}m")
        print(f"  渠底坡度：i = {self.i} = 1/{1/self.i:.0f}")
        print(f"  粗糙系数：n = {self.n}（混凝土）")
        
        # (1) 过水断面面积与湿周
        A = self.cross_section_area()
        chi = self.wetted_perimeter()
        
        print(f"\n(1) 过水断面面积与湿周：")
        print(f"  过水断面面积：")
        print(f"    A = b × h")
        print(f"      = {self.b} × {self.h}")
        print(f"      = {A:.3f} m²")
        
        print(f"\n  湿周：")
        print(f"    χ = b + 2h")
        print(f"      = {self.b} + 2×{self.h}")
        print(f"      = {chi:.3f} m")
        
        # (2) 水力半径
        R = self.hydraulic_radius()
        
        print(f"\n(2) 水力半径：")
        print(f"  R = A / χ")
        print(f"    = {A:.3f} / {chi:.3f}")
        print(f"    = {R:.4f} m")
        
        # (3) 流速
        v = self.velocity_manning()
        v_chezy = self.velocity_chezy()
        
        print(f"\n(3) 流速：")
        print(f"  曼宁公式：")
        print(f"    v = (1/n) × R^(2/3) × i^(1/2)")
        print(f"      = (1/{self.n}) × {R:.4f}^(2/3) × {self.i}^(1/2)")
        print(f"      = {1/self.n:.2f} × {R**(2/3):.4f} × {self.i**0.5:.4f}")
        print(f"      = {v:.3f} m/s")
        
        print(f"\n  谢才公式验证：")
        C = R**(1/6) / self.n
        print(f"    C = R^(1/6)/n = {R**(1/6):.3f}/{self.n} = {C:.2f}")
        print(f"    v = C√(Ri) = {C:.2f} × √({R:.4f}×{self.i})")
        print(f"      = {v_chezy:.3f} m/s")
        print(f"    （与曼宁公式结果一致）")
        
        # (4) 流量
        Q = self.discharge()
        
        print(f"\n(4) 流量：")
        print(f"  Q = A × v")
        print(f"    = {A:.3f} × {v:.3f}")
        print(f"    = {Q:.3f} m³/s")
        print(f"    = {Q*3600:.1f} m³/h")
        print(f"    = {Q*86400:.1f} m³/d")
        
        # 佛汝德数
        Fr = self.froude_number()
        
        print(f"\n  佛汝德数：")
        print(f"    Fr = v/√(gh)")
        print(f"       = {v:.3f}/√({self.g}×{self.h})")
        print(f"       = {Fr:.3f}")
        
        if Fr < 1:
            print(f"    ✓ 缓流（Fr < 1）")
        elif Fr > 1:
            print(f"    ✓ 急流（Fr > 1）")
        else:
            print(f"    ✓ 临界流（Fr = 1）")
        
        # (5) 最优断面设计
        h_opt, A_opt, chi_opt, R_opt, v_opt, Q_opt = self.optimal_section_analysis()
        
        print(f"\n(5) 水力最优断面设计：")
        print(f"  矩形断面最优条件：h = b/2")
        print(f"\n  最优水深：")
        print(f"    h_opt = b/2 = {self.b}/2 = {h_opt:.2f} m")
        
        print(f"\n  最优断面参数：")
        print(f"    面积：A_opt = {A_opt:.3f} m²")
        print(f"    湿周：χ_opt = {chi_opt:.3f} m")
        print(f"    水力半径：R_opt = {R_opt:.4f} m")
        print(f"    流速：v_opt = {v_opt:.3f} m/s")
        print(f"    流量：Q_opt = {Q_opt:.3f} m³/s")
        
        print(f"\n  对比分析：")
        print(f"    {'参数':<15} {'当前值':<15} {'最优值':<15} {'变化率':<15}")
        print(f"    {'-'*60}")
        
        params = [
            ('水深h (m)', self.h, h_opt),
            ('面积A (m²)', A, A_opt),
            ('湿周χ (m)', chi, chi_opt),
            ('水力半径R (m)', R, R_opt),
            ('流速v (m/s)', v, v_opt),
            ('流量Q (m³/s)', Q, Q_opt)
        ]
        
        for name, current, optimal in params:
            change = (optimal - current) / current * 100
            print(f"    {name:<15} {current:<15.4f} {optimal:<15.4f} "
                  f"{change:+.2f}%")
        
        print(f"\n  物理意义：")
        print(f"    • 最优断面使得在相同面积下湿周最小")
        print(f"    • 或在相同流量下水力半径最大")
        print(f"    • 减少摩擦损失，提高输水效率")
        
        if abs(self.h - h_opt) / h_opt < 0.1:
            print(f"    ✓ 当前断面接近最优断面")
        else:
            print(f"    ⚠ 建议调整水深至{h_opt:.2f}m以达到最优")
        
        print("\n" + "=" * 70)
        print("考试要点：")
        print("=" * 70)
        print("1. 几何参数：A=bh, χ=b+2h, R=A/χ")
        print("2. 曼宁公式：v = (1/n)R^(2/3)i^(1/2)")
        print("3. 连续方程：Q = Av")
        print("4. 佛汝德数：Fr = v/√(gh)")
        print("5. 矩形最优：h = b/2")
        print("=" * 70)


def main():
    """主函数"""
    print("\n" + "💧" * 35)
    print("第03章 管流与明渠流 - 题目6：明渠均匀流计算")
    print("💧" * 35 + "\n")
    
    # 题目参数
    b = 3.0         # 渠底宽度3m
    h = 1.2         # 水深1.2m
    i = 0.001       # 渠底坡度0.001
    n = 0.025       # 粗糙系数0.025（混凝土）
    
    # 创建明渠均匀流对象
    channel = OpenChannelUniformFlow(b=b, h=h, i=i, n=n)
    
    # 打印结果
    channel.print_results()
    
    # 绘图
    print("\n正在绘制明渠均匀流分析图...")
    channel.plot_analysis()
    
    print("\n✅ 计算完成！")


if __name__ == "__main__":
    main()
