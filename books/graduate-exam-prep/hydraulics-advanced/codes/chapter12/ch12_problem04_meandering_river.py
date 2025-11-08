# -*- coding: utf-8 -*-
"""
第12章 河流动力学 - 题4：弯曲河道水流分析

问题描述：
    某弯曲河道，弯曲半径R = 500m，河道宽度B = 100m
    流量Q = 500 m³/s，平均水深h = 5m
    弯道中心角θ = 90°，河床坡度i = 0.0001
    
    求：
    1. 弯道环流分析
    2. 横向水面比降
    3. 弯道冲淤规律
    4. 弯曲度影响
    5. 河道演变趋势

核心公式：
    1. 横向水面比降：J_s = v²/(g·R)
    2. 环流强度：Γ = K·v²/R
    3. 弯曲度：P = L_c/L_v
    4. 冲刷深度：h_max = h·(1+α·P)

考试要点：
    - 弯道环流
    - 横向水面比降
    - 弯道冲淤
    - 河道演变

作者: CHS-Books Team
日期: 2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, Dict

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class MeanderingRiver:
    """弯曲河道水流分析"""
    
    def __init__(self, R: float, B: float, Q: float, h: float, 
                 theta: float, i: float):
        self.R = R  # 弯曲半径
        self.B = B  # 河道宽度
        self.Q = Q  # 流量
        self.h = h  # 平均水深
        self.theta = theta  # 弯道中心角（度）
        self.i = i  # 河床坡度
        self.g = 9.8
        
    def flow_velocity(self) -> float:
        """平均流速"""
        v = self.Q / (self.B * self.h)
        return v
    
    def transverse_slope(self) -> float:
        """
        横向水面比降
        J_s = v²/(g·R)
        """
        v = self.flow_velocity()
        J_s = (v ** 2) / (self.g * self.R)
        return J_s
    
    def water_surface_difference(self) -> float:
        """
        横向水位差
        Δh = J_s·B
        """
        J_s = self.transverse_slope()
        delta_h = J_s * self.B
        return delta_h
    
    def circulation_intensity(self) -> float:
        """
        环流强度
        Γ = K·v²/R（K≈0.2-0.3）
        """
        v = self.flow_velocity()
        K = 0.25
        Gamma = K * (v ** 2) / self.R
        return Gamma
    
    def bend_length(self) -> float:
        """弯道长度"""
        theta_rad = np.deg2rad(self.theta)
        L_bend = self.R * theta_rad
        return L_bend
    
    def sinuosity(self) -> float:
        """
        弯曲度
        P = L_c/L_v
        L_c为河道中心线长度，L_v为谷线长度
        """
        theta_rad = np.deg2rad(self.theta)
        L_c = self.R * theta_rad
        L_v = self.R * np.sin(theta_rad)  # 简化
        
        if L_v > 0:
            P = L_c / L_v
        else:
            P = 1.0
        
        return P
    
    def scour_depth(self) -> Tuple[float, float]:
        """
        弯道冲刷深度
        凹岸：h_max = h·(1+α·P)
        凸岸：h_min = h·(1-β·P)
        α≈0.5, β≈0.3
        """
        P = self.sinuosity()
        alpha = 0.5
        beta = 0.3
        
        h_max = self.h * (1 + alpha * (P - 1))  # 凹岸
        h_min = self.h * (1 - beta * (P - 1))  # 凸岸
        
        return h_max, h_min
    
    def centrifugal_force(self) -> float:
        """
        离心力系数
        F_c = m·v²/R
        单位质量水体：F_c/m = v²/R
        """
        v = self.flow_velocity()
        Fc_per_mass = (v ** 2) / self.R
        return Fc_per_mass
    
    def plot_analysis(self):
        """绘制分析图表"""
        fig = plt.figure(figsize=(16, 12))
        
        v = self.flow_velocity()
        J_s = self.transverse_slope()
        delta_h = self.water_surface_difference()
        Gamma = self.circulation_intensity()
        L_bend = self.bend_length()
        P = self.sinuosity()
        h_max, h_min = self.scour_depth()
        Fc = self.centrifugal_force()
        
        # 1. 弯道平面示意图
        ax1 = plt.subplot(3, 3, 1)
        
        # 弯道中心线
        theta_range = np.linspace(0, np.deg2rad(self.theta), 100)
        x_center = self.R * np.sin(theta_range)
        y_center = self.R * (1 - np.cos(theta_range))
        
        # 内外边界
        x_inner = (self.R - self.B/2) * np.sin(theta_range)
        y_inner = (self.R - self.B/2) * (1 - np.cos(theta_range))
        x_outer = (self.R + self.B/2) * np.sin(theta_range)
        y_outer = (self.R + self.B/2) * (1 - np.cos(theta_range))
        
        ax1.plot(x_center, y_center, 'b-', linewidth=3, label='中心线')
        ax1.plot(x_inner, y_inner, 'k-', linewidth=2, label='凸岸（淤积）')
        ax1.plot(x_outer, y_outer, 'r-', linewidth=2, label='凹岸（冲刷）')
        ax1.fill_betweenx(y_center, x_inner, x_outer, alpha=0.3, color='lightblue')
        
        # 标注
        mid_idx = len(theta_range) // 2
        ax1.arrow(x_center[mid_idx], y_center[mid_idx], 20, 0, 
                 head_width=10, head_length=5, fc='blue', ec='blue')
        ax1.text(x_center[mid_idx]+30, y_center[mid_idx], 'v', fontsize=12, color='blue', fontweight='bold')
        
        ax1.set_xlabel('x (m)', fontsize=10)
        ax1.set_ylabel('y (m)', fontsize=10)
        ax1.set_title('弯道平面布置', fontsize=12, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.axis('equal')
        
        # 2. 基本参数
        ax2 = plt.subplot(3, 3, 2)
        ax2.axis('off')
        
        ax2.text(0.5, 0.95, '弯道参数', fontsize=11, ha='center', fontweight='bold')
        ax2.text(0.1, 0.82, f'弯曲半径: R = {self.R} m', fontsize=10, color='blue')
        ax2.text(0.1, 0.72, f'河道宽度: B = {self.B} m', fontsize=10)
        ax2.text(0.1, 0.62, f'弯道中心角: θ = {self.theta}°', fontsize=10)
        ax2.text(0.1, 0.52, f'弯道长度: L = {L_bend:.1f} m', fontsize=10)
        ax2.text(0.1, 0.42, f'弯曲度: P = {P:.3f}', fontsize=10, color='purple')
        ax2.text(0.1, 0.32, f'流量: Q = {self.Q} m³/s', fontsize=10)
        ax2.text(0.1, 0.22, f'水深: h = {self.h} m', fontsize=10)
        ax2.text(0.1, 0.12, f'流速: v = {v:.2f} m/s', fontsize=10, color='red')
        ax2.text(0.1, 0.02, f'佛汝德数: Fr = {v/np.sqrt(self.g*self.h):.3f}', fontsize=10)
        
        ax2.set_title('基本参数', fontsize=12, fontweight='bold')
        
        # 3. 横断面示意图
        ax3 = plt.subplot(3, 3, 3)
        
        # 横向坐标
        y_cross = np.linspace(0, self.B, 100)
        
        # 水面线（倾斜）
        z_surface = -J_s * y_cross + delta_h
        
        # 河床（假设平底）
        z_bed = np.zeros_like(y_cross) - self.h
        
        ax3.plot(y_cross, z_surface, 'b-', linewidth=3, label='水面线')
        ax3.plot(y_cross, z_bed, 'k-', linewidth=2, label='河床')
        ax3.fill_between(y_cross, z_bed, z_surface, alpha=0.3, color='lightblue')
        
        # 标注
        ax3.text(0, delta_h+0.05, f'凸岸\n+{delta_h*100:.2f}cm', ha='center', fontsize=9, color='blue')
        ax3.text(self.B, -0.05, '凹岸', ha='center', fontsize=9, color='red')
        
        ax3.set_xlabel('横向距离 (m)', fontsize=10)
        ax3.set_ylabel('高程 (m)', fontsize=10)
        ax3.set_title('横断面水面线', fontsize=12, fontweight='bold')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. 横向水面比降
        ax4 = plt.subplot(3, 3, 4)
        ax4.axis('off')
        
        ax4.text(0.5, 0.95, '横向水面比降', fontsize=11, ha='center', fontweight='bold')
        ax4.text(0.1, 0.75, f'J_s = v²/(g·R)', fontsize=10, color='gray')
        ax4.text(0.1, 0.65, f'   = {v:.2f}²/({self.g}×{self.R})', fontsize=9, color='gray')
        ax4.text(0.1, 0.50, f'J_s = {J_s:.6f}', fontsize=11, color='blue', fontweight='bold')
        ax4.text(0.1, 0.35, f'横向水位差:', fontsize=10)
        ax4.text(0.1, 0.25, f'Δh = J_s·B = {delta_h:.4f} m', fontsize=10, color='green')
        ax4.text(0.1, 0.15, f'   = {delta_h*100:.2f} cm', fontsize=10, color='green', fontweight='bold')
        ax4.text(0.1, 0.02, f'凹岸水位高于凸岸', fontsize=9, color='red')
        
        ax4.set_title('水面比降计算', fontsize=12, fontweight='bold')
        
        # 5. 环流强度
        ax5 = plt.subplot(3, 3, 5)
        
        # 环流示意（螺旋流）
        theta_circ = np.linspace(0, 2*np.pi, 100)
        x_circ = 0.3 * np.cos(theta_circ)
        y_circ = 0.5 * np.sin(theta_circ)
        
        ax5.plot(x_circ, y_circ, 'b-', linewidth=2)
        ax5.arrow(0, 0, 0.3, 0, head_width=0.1, head_length=0.05, fc='red', ec='red', linewidth=2)
        ax5.text(0.4, 0, '主流', fontsize=10, color='red', fontweight='bold')
        ax5.arrow(0.2, 0.4, -0.1, -0.2, head_width=0.08, head_length=0.04, fc='blue', ec='blue')
        ax5.text(-0.3, 0.5, '环流', fontsize=10, color='blue', fontweight='bold')
        
        ax5.text(0, -0.8, f'环流强度: Γ = {Gamma:.4f} m/s²', ha='center', fontsize=10, 
                bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
        
        ax5.set_xlim(-0.6, 0.6)
        ax5.set_ylim(-1, 0.8)
        ax5.set_aspect('equal')
        ax5.axis('off')
        ax5.set_title('弯道环流', fontsize=12, fontweight='bold')
        
        # 6. 冲淤分布
        ax6 = plt.subplot(3, 3, 6)
        
        # 横向冲淤深度分布
        y_scour = np.linspace(0, self.B, 100)
        # 凸岸（y=0）淤积，凹岸（y=B）冲刷
        depth_variation = self.h + (h_max - self.h) * (y_scour / self.B)
        
        ax6.plot(y_scour, -depth_variation, 'b-', linewidth=3)
        ax6.fill_between(y_scour, 0, -depth_variation, alpha=0.3, color='brown')
        ax6.axhline(-self.h, color='k', linestyle='--', linewidth=1, label=f'平均深度{self.h}m')
        
        # 标注
        ax6.text(0, -h_min-0.3, f'凸岸（淤积）\nh={h_min:.2f}m', ha='center', fontsize=9, 
                color='blue', bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
        ax6.text(self.B, -h_max-0.3, f'凹岸（冲刷）\nh={h_max:.2f}m', ha='center', fontsize=9,
                color='red', bbox=dict(boxstyle='round', facecolor='pink', alpha=0.8))
        
        ax6.set_xlabel('横向距离 (m)', fontsize=10)
        ax6.set_ylabel('河床高程 (m)', fontsize=10)
        ax6.set_title('横向冲淤分布', fontsize=12, fontweight='bold')
        ax6.legend()
        ax6.grid(True, alpha=0.3)
        
        # 7. 弯曲度影响
        ax7 = plt.subplot(3, 3, 7)
        
        # 不同弯曲半径的影响
        R_range = np.linspace(200, 1000, 50)
        J_s_range = []
        delta_h_range = []
        
        for R_val in R_range:
            river_temp = MeanderingRiver(R_val, self.B, self.Q, self.h, self.theta, self.i)
            J_s_range.append(river_temp.transverse_slope())
            delta_h_range.append(river_temp.water_surface_difference())
        
        ax7_twin = ax7.twinx()
        
        line1 = ax7.plot(R_range, np.array(J_s_range)*1000, 'b-', linewidth=2, label='比降J_s')
        line2 = ax7_twin.plot(R_range, np.array(delta_h_range)*100, 'r-', linewidth=2, label='水位差Δh')
        ax7.plot(self.R, J_s*1000, 'bo', markersize=10)
        ax7_twin.plot(self.R, delta_h*100, 'ro', markersize=10)
        
        ax7.set_xlabel('弯曲半径 R (m)', fontsize=10)
        ax7.set_ylabel('横向比降 J_s (‰)', fontsize=10, color='blue')
        ax7_twin.set_ylabel('水位差 Δh (cm)', fontsize=10, color='red')
        ax7.set_title('弯曲半径影响', fontsize=12, fontweight='bold')
        ax7.grid(True, alpha=0.3)
        
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax7.legend(lines, labels, loc='upper right')
        
        # 8. 离心力分析
        ax8 = plt.subplot(3, 3, 8)
        
        # 流速影响
        v_range = np.linspace(0.5, 3.0, 50)
        Fc_range = (v_range ** 2) / self.R
        
        ax8.plot(v_range, Fc_range, 'b-', linewidth=2)
        ax8.plot(v, Fc, 'ro', markersize=12, label=f'v={v:.2f}m/s')
        
        ax8.set_xlabel('流速 v (m/s)', fontsize=10)
        ax8.set_ylabel('离心力系数 F_c/m (m/s²)', fontsize=10)
        ax8.set_title('流速-离心力关系', fontsize=12, fontweight='bold')
        ax8.legend()
        ax8.grid(True, alpha=0.3)
        
        # 9. 结果汇总表
        ax9 = plt.subplot(3, 3, 9)
        ax9.axis('off')
        
        table_data = [
            ['项目', '数值', '单位'],
            ['弯曲半径', f'{self.R}', 'm'],
            ['河道宽度', f'{self.B}', 'm'],
            ['流速', f'{v:.2f}', 'm/s'],
            ['横向比降', f'{J_s*1000:.3f}', '‰'],
            ['水位差', f'{delta_h*100:.2f}', 'cm'],
            ['弯曲度', f'{P:.3f}', '-'],
            ['凹岸冲刷深', f'{h_max:.2f}', 'm'],
            ['凸岸淤积深', f'{h_min:.2f}', 'm']
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
        for i in [5, 6, 7, 8]:
            for j in range(3):
                table[(i, j)].set_facecolor('#FFF9E6')
        
        ax9.set_title('计算结果汇总', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('/tmp/ch12_problem04_meandering_river.png', dpi=150, bbox_inches='tight')
        print(f"图表已保存: /tmp/ch12_problem04_meandering_river.png")
        plt.show()
    
    def print_results(self):
        """打印结果"""
        print("\n" + "="*70)
        print("第12章 河流动力学 - 题4：弯曲河道水流分析")
        print("="*70)
        
        v = self.flow_velocity()
        J_s = self.transverse_slope()
        delta_h = self.water_surface_difference()
        Gamma = self.circulation_intensity()
        L_bend = self.bend_length()
        P = self.sinuosity()
        h_max, h_min = self.scour_depth()
        Fc = self.centrifugal_force()
        
        print(f"\n【弯道几何】")
        print(f"弯曲半径: R = {self.R} m")
        print(f"河道宽度: B = {self.B} m")
        print(f"弯道中心角: θ = {self.theta}°")
        print(f"弯道长度: L = R·θ = {self.R}×{np.deg2rad(self.theta):.4f} = {L_bend:.2f} m")
        print(f"弯曲度: P = {P:.4f}")
        
        print(f"\n【水流参数】")
        print(f"流量: Q = {self.Q} m³/s")
        print(f"平均水深: h = {self.h} m")
        print(f"平均流速: v = Q/(B·h) = {self.Q}/({self.B}×{self.h}) = {v:.3f} m/s")
        print(f"佛汝德数: Fr = v/√(g·h) = {v/np.sqrt(self.g*self.h):.3f}")
        
        print(f"\n【横向水面比降】")
        print(f"横向比降: J_s = v²/(g·R)")
        print(f"         = {v:.3f}²/({self.g}×{self.R})")
        print(f"         = {J_s:.6f}")
        print(f"         = {J_s*1000:.3f} ‰")
        print(f"横向水位差: Δh = J_s·B = {J_s:.6f}×{self.B} = {delta_h:.4f} m")
        print(f"           = {delta_h*100:.2f} cm")
        print(f"凹岸水位高于凸岸 {delta_h*100:.2f} cm")
        
        print(f"\n【弯道环流】")
        print(f"环流强度: Γ = K·v²/R（K=0.25）")
        print(f"         = 0.25×{v:.3f}²/{self.R}")
        print(f"         = {Gamma:.6f} m/s²")
        print(f"环流特征: 表层水流指向凹岸，底层水流指向凸岸")
        
        print(f"\n【弯道冲淤】")
        print(f"平均水深: h = {self.h} m")
        print(f"凹岸冲刷深度: h_max = h·(1+α·(P-1)) = {h_max:.3f} m")
        print(f"凸岸淤积深度: h_min = h·(1-β·(P-1)) = {h_min:.3f} m")
        print(f"冲刷幅度: Δh_冲 = {h_max - self.h:.3f} m")
        print(f"淤积幅度: Δh_淤 = {self.h - h_min:.3f} m")
        
        print(f"\n【离心力分析】")
        print(f"离心力系数: F_c/m = v²/R = {Fc:.4f} m/s²")
        print(f"与重力加速度比: F_c/(m·g) = {Fc/self.g:.4f}")
        
        print(f"\n【演变趋势】")
        if P > 1.5:
            print(f"弯曲度P = {P:.3f} > 1.5，属于蜿蜒型河道")
            print(f"→ 凹岸冲刷强烈，弯道继续发展")
            print(f"→ 凸岸淤积形成边滩")
            print(f"→ 可能发生河道裁弯取直")
        else:
            print(f"弯曲度P = {P:.3f} ≤ 1.5，属于微弯型河道")
            print(f"→ 冲淤相对缓和")
            print(f"→ 河道相对稳定")
        
        print(f"\n✓ 弯曲河道水流分析完成")
        print(f"\n{'='*70}\n")


def main():
    R = 500
    B = 100
    Q = 500
    h = 5
    theta = 90
    i = 0.0001
    
    river = MeanderingRiver(R, B, Q, h, theta, i)
    river.print_results()
    river.plot_analysis()


if __name__ == "__main__":
    main()
