# -*- coding: utf-8 -*-
"""
第11章 水工建筑物 - 题1：重力坝稳定分析

问题描述：
    混凝土重力坝，坝高H = 50m，坝顶宽b = 6m
    上游坡比m1 = 0.1，下游坡比m2 = 0.8
    上游水深h1 = 45m，下游水深h2 = 5m
    混凝土重度γc = 24 kN/m³，扬压力折减系数α = 0.3
    
    求：
    1. 坝体自重与作用点
    2. 水压力与扬压力
    3. 抗滑稳定安全系数
    4. 抗倾覆稳定安全系数
    5. 坝底应力分布

核心公式：
    1. 抗滑稳定：Kc = f·ΣV/ΣH
    2. 抗倾覆：K0 = ΣM稳/ΣM倾
    3. 坝底应力：σ = ΣV/B ± 6ΣM/B²
    4. 扬压力：U = (1/2)γw·(h1+αh1)·B

考试要点：
    - 重力坝荷载计算
    - 抗滑与抗倾覆
    - 坝底应力分析
    - 安全系数判别

作者: CHS-Books Team
日期: 2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, Dict

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class GravityDamStability:
    """重力坝稳定分析"""
    
    def __init__(self, H: float, b: float, m1: float, m2: float,
                 h1: float, h2: float, gamma_c: float, alpha: float = 0.3):
        self.H = H  # 坝高
        self.b = b  # 坝顶宽
        self.m1 = m1  # 上游坡比
        self.m2 = m2  # 下游坡比
        self.h1 = h1  # 上游水深
        self.h2 = h2  # 下游水深
        self.gamma_c = gamma_c  # 混凝土重度
        self.alpha = alpha  # 扬压力折减系数
        self.gamma_w = 10.0  # 水的重度
        self.f = 0.75  # 摩擦系数
        self.g = 9.8
        
    def dam_dimensions(self) -> Dict:
        """坝体尺寸"""
        # 上游坡脚宽度
        B1 = self.m1 * self.H
        # 下游坡脚宽度
        B2 = self.m2 * self.H
        # 坝底总宽
        B = B1 + self.b + B2
        
        return {
            'B1': B1,
            'B2': B2,
            'B': B,
            'b': self.b,
            'H': self.H
        }
    
    def dam_weight(self) -> Tuple[float, float]:
        """
        坝体自重与作用点
        将坝体分解为矩形+两个三角形
        """
        dims = self.dam_dimensions()
        
        # 矩形部分（坝顶宽度）
        W_rect = self.gamma_c * self.b * self.H
        x_rect = dims['B1'] + self.b / 2
        
        # 上游三角形
        W_tri1 = 0.5 * self.gamma_c * dims['B1'] * self.H
        x_tri1 = dims['B1'] / 3
        
        # 下游三角形
        W_tri2 = 0.5 * self.gamma_c * dims['B2'] * self.H
        x_tri2 = dims['B1'] + self.b + 2 * dims['B2'] / 3
        
        # 总重
        W_total = W_rect + W_tri1 + W_tri2
        
        # 合力作用点（对坝踵取矩）
        x_total = (W_rect * x_rect + W_tri1 * x_tri1 + W_tri2 * x_tri2) / W_total
        
        return W_total, x_total
    
    def water_pressure(self) -> Tuple[Dict, Dict]:
        """上下游水压力"""
        # 上游水压力
        P1 = 0.5 * self.gamma_w * self.h1 ** 2
        y1 = self.h1 / 3  # 作用点高度（从坝底）
        
        # 下游水压力
        P2 = 0.5 * self.gamma_w * self.h2 ** 2
        y2 = self.h2 / 3
        
        upstream = {'P': P1, 'y': y1}
        downstream = {'P': P2, 'y': y2}
        
        return upstream, downstream
    
    def uplift_pressure(self) -> Tuple[float, float]:
        """
        扬压力与作用点
        U = (1/2)γw·(h1 + α·h1)·B
        """
        dims = self.dam_dimensions()
        B = dims['B']
        
        # 扬压力（梯形分布简化）
        # 上游端：h1，下游端：α·h1
        U = 0.5 * self.gamma_w * (self.h1 + self.alpha * self.h1) * B
        
        # 作用点（梯形形心）
        # x距坝踵的距离
        x_U = B * (2 * self.h1 + self.alpha * self.h1) / (3 * (self.h1 + self.alpha * self.h1))
        
        return U, x_U
    
    def sliding_stability(self) -> Tuple[float, bool]:
        """
        抗滑稳定
        Kc = f·ΣV/ΣH ≥ 1.05（正常）或 1.0（特殊）
        """
        W, _ = self.dam_weight()
        U, _ = self.uplift_pressure()
        P_up, P_down = self.water_pressure()
        
        # 竖向力
        sum_V = W - U
        
        # 水平力
        sum_H = P_up['P'] - P_down['P']
        
        # 安全系数
        Kc = self.f * sum_V / sum_H
        is_safe = Kc >= 1.05
        
        return Kc, is_safe
    
    def overturning_stability(self) -> Tuple[float, bool]:
        """
        抗倾覆稳定（对坝趾取矩）
        K0 = ΣM稳/ΣM倾 ≥ 1.5
        """
        dims = self.dam_dimensions()
        B = dims['B']
        
        W, x_W = self.dam_weight()
        U, x_U = self.uplift_pressure()
        P_up, P_down = self.water_pressure()
        
        # 稳定力矩（对坝趾，逆时针为正）
        M_stab = W * (B - x_W) - U * (B - x_U)
        
        # 倾覆力矩（对坝趾，顺时针为正）
        M_over = P_up['P'] * P_up['y'] - P_down['P'] * P_down['y']
        
        # 安全系数
        K0 = M_stab / M_over
        is_safe = K0 >= 1.5
        
        return K0, is_safe
    
    def base_stress(self) -> Tuple[float, float, float]:
        """
        坝底应力分布
        σ = ΣV/B ± 6ΣM/B²
        """
        dims = self.dam_dimensions()
        B = dims['B']
        
        W, x_W = self.dam_weight()
        U, x_U = self.uplift_pressure()
        P_up, P_down = self.water_pressure()
        
        # 竖向力
        sum_V = W - U
        
        # 对坝底中心的力矩
        M_center = (W * (x_W - B/2) - U * (x_U - B/2) - 
                   P_up['P'] * P_up['y'] + P_down['P'] * P_down['y'])
        
        # 坝踵应力
        sigma_heel = sum_V / B - 6 * M_center / (B ** 2)
        
        # 坝趾应力
        sigma_toe = sum_V / B + 6 * M_center / (B ** 2)
        
        # 平均应力
        sigma_avg = sum_V / B
        
        return sigma_heel, sigma_toe, sigma_avg
    
    def plot_analysis(self):
        """绘制分析图表"""
        fig = plt.figure(figsize=(16, 12))
        
        dims = self.dam_dimensions()
        W, x_W = self.dam_weight()
        P_up, P_down = self.water_pressure()
        U, x_U = self.uplift_pressure()
        Kc, safe_sliding = self.sliding_stability()
        K0, safe_overturning = self.overturning_stability()
        sigma_heel, sigma_toe, sigma_avg = self.base_stress()
        
        # 1. 重力坝断面与荷载
        ax1 = plt.subplot(3, 3, 1)
        
        # 坝体轮廓
        x_dam = [0, dims['B1'], dims['B1'], dims['B1']+self.b, dims['B'], dims['B'], 0]
        y_dam = [0, self.H, self.H, self.H, 0, 0, 0]
        ax1.fill(x_dam, y_dam, color='gray', alpha=0.4, label='坝体')
        ax1.plot(x_dam, y_dam, 'k-', linewidth=2)
        
        # 上游水体
        ax1.fill([0, 0, dims['B1']], [0, self.h1, self.H], 
                color='lightblue', alpha=0.5, label='上游水')
        
        # 下游水体
        ax1.fill([dims['B'], dims['B'], dims['B']], [0, self.h2, 0], 
                color='lightgreen', alpha=0.5, label='下游水')
        
        # 自重（向下箭头）
        ax1.arrow(x_W, self.H+5, 0, -8, head_width=2, head_length=1, 
                 fc='red', ec='red', linewidth=2)
        ax1.text(x_W, self.H+7, f'W={W:.0f}kN', ha='center', fontsize=9, color='red', fontweight='bold')
        
        # 水压力（水平箭头）
        ax1.arrow(dims['B1']+5, P_up['y'], -8, 0, head_width=1, head_length=1, 
                 fc='blue', ec='blue', linewidth=2)
        ax1.text(dims['B1']+8, P_up['y'], f'P₁={P_up["P"]:.0f}kN', fontsize=9, color='blue', fontweight='bold')
        
        # 标注尺寸
        ax1.text(dims['B']/2, -3, f'B={dims["B"]:.1f}m', ha='center', fontsize=10, color='black', fontweight='bold')
        ax1.text(dims['B1']/2, self.H+2, f'b={self.b}m', ha='center', fontsize=9)
        
        ax1.set_xlabel('水平距离 (m)', fontsize=10)
        ax1.set_ylabel('高程 (m)', fontsize=10)
        ax1.set_title('重力坝断面与荷载', fontsize=12, fontweight='bold')
        ax1.legend(fontsize=8)
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim(-5, dims['B']+5)
        ax1.set_ylim(-5, self.H+10)
        
        # 2. 计算参数
        ax2 = plt.subplot(3, 3, 2)
        ax2.axis('off')
        
        ax2.text(0.5, 0.95, '坝体参数', fontsize=11, ha='center', fontweight='bold')
        ax2.text(0.1, 0.82, f'坝高: H = {self.H} m', fontsize=10)
        ax2.text(0.1, 0.72, f'坝顶宽: b = {self.b} m', fontsize=10)
        ax2.text(0.1, 0.62, f'坝底宽: B = {dims["B"]:.1f} m', fontsize=10)
        ax2.text(0.1, 0.52, f'上游水深: h₁ = {self.h1} m', fontsize=10)
        ax2.text(0.1, 0.42, f'下游水深: h₂ = {self.h2} m', fontsize=10)
        ax2.text(0.1, 0.32, f'混凝土重度: γc = {self.gamma_c} kN/m³', fontsize=10)
        ax2.text(0.1, 0.20, f'坝体自重: W = {W:.0f} kN', fontsize=10, color='red')
        ax2.text(0.1, 0.10, f'上游水压: P₁ = {P_up["P"]:.0f} kN', fontsize=10, color='blue')
        ax2.text(0.1, 0.00, f'扬压力: U = {U:.0f} kN', fontsize=10, color='green')
        
        ax2.set_title('基本参数', fontsize=12, fontweight='bold')
        
        # 3. 荷载汇总
        ax3 = plt.subplot(3, 3, 3)
        
        loads = ['自重W', '上游P₁', '下游P₂', '扬压力U']
        values = [W, P_up['P'], -P_down['P'], -U]
        colors = ['red', 'blue', 'green', 'orange']
        
        bars = ax3.barh(loads, values, color=colors, alpha=0.7, edgecolor='black')
        ax3.axvline(0, color='k', linewidth=1)
        ax3.set_xlabel('荷载 (kN)', fontsize=10)
        ax3.set_title('荷载汇总', fontsize=12, fontweight='bold')
        ax3.grid(True, alpha=0.3, axis='x')
        
        for bar, val in zip(bars, values):
            width = bar.get_width()
            ax3.text(width, bar.get_y() + bar.get_height()/2,
                    f'{abs(val):.0f}', ha='left' if width>0 else 'right', 
                    va='center', fontsize=9, fontweight='bold')
        
        # 4. 抗滑稳定
        ax4 = plt.subplot(3, 3, 4)
        ax4.axis('off')
        
        sum_V = W - U
        sum_H = P_up['P'] - P_down['P']
        
        ax4.text(0.5, 0.95, '抗滑稳定', fontsize=11, ha='center', fontweight='bold')
        ax4.text(0.1, 0.80, f'摩擦系数: f = {self.f}', fontsize=10)
        ax4.text(0.1, 0.68, f'竖向力: ΣV = {sum_V:.0f} kN', fontsize=10)
        ax4.text(0.1, 0.58, f'水平力: ΣH = {sum_H:.0f} kN', fontsize=10)
        ax4.text(0.1, 0.45, f'Kc = f·ΣV/ΣH', fontsize=10, color='gray')
        ax4.text(0.1, 0.35, f'   = {self.f}×{sum_V:.0f}/{sum_H:.0f}', fontsize=9, color='gray')
        ax4.text(0.1, 0.20, f'Kc = {Kc:.2f}', fontsize=12, 
                color='green' if safe_sliding else 'red', fontweight='bold')
        
        if safe_sliding:
            ax4.text(0.1, 0.05, '✓ 满足要求（Kc≥1.05）', fontsize=10, color='green', fontweight='bold')
        else:
            ax4.text(0.1, 0.05, '✗ 不满足要求！', fontsize=10, color='red', fontweight='bold')
        
        ax4.set_title('抗滑验算', fontsize=12, fontweight='bold')
        
        # 5. 抗倾覆稳定
        ax5 = plt.subplot(3, 3, 5)
        ax5.axis('off')
        
        M_stab = W * (dims['B'] - x_W) - U * (dims['B'] - x_U)
        M_over = P_up['P'] * P_up['y'] - P_down['P'] * P_down['y']
        
        ax5.text(0.5, 0.95, '抗倾覆稳定', fontsize=11, ha='center', fontweight='bold')
        ax5.text(0.1, 0.78, f'稳定力矩: M_稳 = {M_stab:.0f} kN·m', fontsize=10, color='green')
        ax5.text(0.1, 0.68, f'倾覆力矩: M_倾 = {M_over:.0f} kN·m', fontsize=10, color='red')
        ax5.text(0.1, 0.53, f'K₀ = M_稳/M_倾', fontsize=10, color='gray')
        ax5.text(0.1, 0.43, f'   = {M_stab:.0f}/{M_over:.0f}', fontsize=9, color='gray')
        ax5.text(0.1, 0.28, f'K₀ = {K0:.2f}', fontsize=12,
                color='green' if safe_overturning else 'red', fontweight='bold')
        
        if safe_overturning:
            ax5.text(0.1, 0.10, '✓ 满足要求（K₀≥1.5）', fontsize=10, color='green', fontweight='bold')
        else:
            ax5.text(0.1, 0.10, '✗ 不满足要求！', fontsize=10, color='red', fontweight='bold')
        
        ax5.set_title('抗倾验算', fontsize=12, fontweight='bold')
        
        # 6. 安全系数对比
        ax6 = plt.subplot(3, 3, 6)
        
        categories = ['抗滑Kc', '抗倾K₀']
        K_values = [Kc, K0]
        K_limits = [1.05, 1.5]
        colors_bar = ['green' if K > lim else 'red' for K, lim in zip(K_values, K_limits)]
        
        bars = ax6.bar(categories, K_values, color=colors_bar, alpha=0.7, edgecolor='black')
        ax6.axhline(1.05, color='orange', linestyle='--', linewidth=2, label='Kc≥1.05')
        ax6.axhline(1.5, color='red', linestyle='--', linewidth=2, label='K₀≥1.5')
        
        ax6.set_ylabel('安全系数', fontsize=10)
        ax6.set_title('安全系数对比', fontsize=12, fontweight='bold')
        ax6.legend(fontsize=8)
        ax6.grid(True, alpha=0.3, axis='y')
        
        for bar, K in zip(bars, K_values):
            height = bar.get_height()
            ax6.text(bar.get_x() + bar.get_width()/2., height,
                    f'{K:.2f}', ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        # 7. 坝底应力分布
        ax7 = plt.subplot(3, 3, 7)
        
        x_base = np.array([0, dims['B']])
        sigma_base = np.array([sigma_heel, sigma_toe])
        
        ax7.plot(x_base, sigma_base, 'b-', linewidth=3, marker='o', markersize=8)
        ax7.fill_between(x_base, 0, sigma_base, alpha=0.3, color='blue')
        ax7.axhline(0, color='k', linewidth=1)
        ax7.axhline(sigma_avg, color='r', linestyle='--', linewidth=1.5, label=f'平均σ={sigma_avg:.0f}kPa')
        
        # 标注
        ax7.text(0, sigma_heel, f'坝踵\n{sigma_heel:.0f}kPa', 
                ha='center', va='bottom', fontsize=9, fontweight='bold', color='blue')
        ax7.text(dims['B'], sigma_toe, f'坝趾\n{sigma_toe:.0f}kPa', 
                ha='center', va='bottom', fontsize=9, fontweight='bold', color='blue')
        
        ax7.set_xlabel('坝底位置 (m)', fontsize=10)
        ax7.set_ylabel('应力 σ (kPa)', fontsize=10)
        ax7.set_title('坝底应力分布', fontsize=12, fontweight='bold')
        ax7.legend()
        ax7.grid(True, alpha=0.3)
        
        # 检查拉应力
        if sigma_heel < 0:
            ax7.text(0, sigma_heel-50, '⚠ 出现拉应力！', ha='center', fontsize=9, color='red', fontweight='bold')
        
        # 8. 坝高影响
        ax8 = plt.subplot(3, 3, 8)
        
        H_range = np.linspace(30, 80, 50)
        Kc_range = []
        K0_range = []
        
        for H_val in H_range:
            dam_temp = GravityDamStability(H_val, self.b, self.m1, self.m2,
                                          H_val-5, 5, self.gamma_c, self.alpha)
            Kc_temp, _ = dam_temp.sliding_stability()
            K0_temp, _ = dam_temp.overturning_stability()
            Kc_range.append(Kc_temp)
            K0_range.append(K0_temp)
        
        ax8.plot(H_range, Kc_range, 'b-', linewidth=2, label='抗滑Kc')
        ax8.plot(H_range, K0_range, 'g-', linewidth=2, label='抗倾K₀')
        ax8.axhline(1.05, color='orange', linestyle='--', linewidth=1, alpha=0.7)
        ax8.axhline(1.5, color='red', linestyle='--', linewidth=1, alpha=0.7)
        ax8.plot(self.H, Kc, 'ro', markersize=10, label=f'H={self.H}m')
        
        ax8.set_xlabel('坝高 H (m)', fontsize=10)
        ax8.set_ylabel('安全系数', fontsize=10)
        ax8.set_title('坝高影响', fontsize=12, fontweight='bold')
        ax8.legend(fontsize=8)
        ax8.grid(True, alpha=0.3)
        
        # 9. 结果汇总表
        ax9 = plt.subplot(3, 3, 9)
        ax9.axis('off')
        
        table_data = [
            ['项目', '数值', '标准', '判别'],
            ['坝高(m)', f'{self.H:.1f}', '-', '-'],
            ['坝底宽(m)', f'{dims["B"]:.1f}', '-', '-'],
            ['自重(kN)', f'{W:.0f}', '-', '-'],
            ['抗滑Kc', f'{Kc:.2f}', '≥1.05', '✓' if safe_sliding else '✗'],
            ['抗倾K₀', f'{K0:.2f}', '≥1.5', '✓' if safe_overturning else '✗'],
            ['坝踵应力(kPa)', f'{sigma_heel:.0f}', '>0', '✓' if sigma_heel>0 else '✗'],
            ['坝趾应力(kPa)', f'{sigma_toe:.0f}', '-', '-']
        ]
        
        table = ax9.table(cellText=table_data, cellLoc='center', loc='center',
                         colWidths=[0.35, 0.25, 0.2, 0.15])
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2.2)
        
        for i in range(4):
            table[(0, i)].set_facecolor('#4472C4')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        # 高亮判别结果
        for i in [4, 5, 6]:
            cell = table_data[i][3]
            if cell == '✓':
                table[(i, 3)].set_facecolor('#90EE90')
            elif cell == '✗':
                table[(i, 3)].set_facecolor('#FFB6C1')
        
        ax9.set_title('计算结果汇总', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('/tmp/ch11_problem01_gravity_dam_stability.png', dpi=150, bbox_inches='tight')
        print(f"图表已保存: /tmp/ch11_problem01_gravity_dam_stability.png")
        plt.show()
    
    def print_results(self):
        """打印结果"""
        print("\n" + "="*70)
        print("第11章 水工建筑物 - 题1：重力坝稳定分析")
        print("="*70)
        
        dims = self.dam_dimensions()
        W, x_W = self.dam_weight()
        P_up, P_down = self.water_pressure()
        U, x_U = self.uplift_pressure()
        Kc, safe_sliding = self.sliding_stability()
        K0, safe_overturning = self.overturning_stability()
        sigma_heel, sigma_toe, sigma_avg = self.base_stress()
        
        print(f"\n【坝体参数】")
        print(f"坝高: H = {self.H} m")
        print(f"坝顶宽: b = {self.b} m")
        print(f"上游坡比: m₁ = {self.m1}")
        print(f"下游坡比: m₂ = {self.m2}")
        print(f"坝底宽: B = {dims['B']:.2f} m")
        print(f"混凝土重度: γc = {self.gamma_c} kN/m³")
        
        print(f"\n【荷载计算】")
        print(f"坝体自重: W = {W:.2f} kN (作用点距坝踵{x_W:.2f}m)")
        print(f"上游水压力: P₁ = {P_up['P']:.2f} kN (作用点高{P_up['y']:.2f}m)")
        print(f"下游水压力: P₂ = {P_down['P']:.2f} kN (作用点高{P_down['y']:.2f}m)")
        print(f"扬压力: U = {U:.2f} kN (作用点距坝踵{x_U:.2f}m)")
        
        print(f"\n【抗滑稳定】")
        sum_V = W - U
        sum_H = P_up['P'] - P_down['P']
        print(f"竖向力: ΣV = {sum_V:.2f} kN")
        print(f"水平力: ΣH = {sum_H:.2f} kN")
        print(f"摩擦系数: f = {self.f}")
        print(f"Kc = f·ΣV/ΣH = {self.f}×{sum_V:.2f}/{sum_H:.2f} = {Kc:.3f}")
        if safe_sliding:
            print(f"✓ Kc = {Kc:.3f} ≥ 1.05，满足抗滑要求")
        else:
            print(f"✗ Kc = {Kc:.3f} < 1.05，不满足抗滑要求！")
        
        print(f"\n【抗倾覆稳定】")
        M_stab = W * (dims['B'] - x_W) - U * (dims['B'] - x_U)
        M_over = P_up['P'] * P_up['y'] - P_down['P'] * P_down['y']
        print(f"稳定力矩: M_稳 = {M_stab:.2f} kN·m")
        print(f"倾覆力矩: M_倾 = {M_over:.2f} kN·m")
        print(f"K₀ = M_稳/M_倾 = {M_stab:.2f}/{M_over:.2f} = {K0:.3f}")
        if safe_overturning:
            print(f"✓ K₀ = {K0:.3f} ≥ 1.5，满足抗倾覆要求")
        else:
            print(f"✗ K₀ = {K0:.3f} < 1.5，不满足抗倾覆要求！")
        
        print(f"\n【坝底应力】")
        print(f"坝踵应力: σ_踵 = {sigma_heel:.2f} kPa")
        print(f"坝趾应力: σ_趾 = {sigma_toe:.2f} kPa")
        print(f"平均应力: σ_平 = {sigma_avg:.2f} kPa")
        if sigma_heel < 0:
            print(f"⚠ 坝踵出现拉应力（{sigma_heel:.2f} kPa），需要处理！")
        else:
            print(f"✓ 坝底无拉应力")
        
        print(f"\n✓ 重力坝稳定分析完成")
        print(f"\n{'='*70}\n")


def main():
    H = 50
    b = 6
    m1 = 0.1
    m2 = 0.8
    h1 = 45
    h2 = 5
    gamma_c = 24
    alpha = 0.3
    
    dam = GravityDamStability(H, b, m1, m2, h1, h2, gamma_c, alpha)
    dam.print_results()
    dam.plot_analysis()


if __name__ == "__main__":
    main()
