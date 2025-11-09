# -*- coding: utf-8 -*-
"""
第08章 渗流计算 - 题13：渗流稳定性分析

问题描述：
    土坝下游坡稳定性分析
    坝高H = 25m，下游坡比m = 2.5，土层内摩擦角φ = 25°
    天然重度γ = 19 kN/m³，饱和重度γsat = 20 kN/m³
    出逸点高度ye = 3m，渗透坡降i = 0.8
    
    求：
    1. 渗透力计算
    2. 边坡稳定安全系数
    3. 管涌稳定性验算
    4. 流土稳定性验算
    5. 渗透破坏判别与防治

核心公式：
    1. 渗透力：j = i·γw
    2. 边坡安全系数：K = Σ(c·l + N·tanφ)/ΣT
    3. 管涌临界坡降：[i] = (γs-γw)/γw
    4. 流土临界坡降：ic = (γs-γw)/(γw·n)

考试要点：
    - 渗透力方向与大小
    - 边坡稳定圆弧法
    - 管涌与流土区别
    - 渗透破坏判别标准

作者: CHS-Books Team
日期: 2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, Dict

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class SeepageStability:
    """渗流稳定性分析"""
    
    def __init__(self, H: float, m: float, ye: float, i: float,
                 phi: float, gamma: float, gamma_sat: float):
        self.H = H  # 坝高
        self.m = m  # 下游坡比
        self.ye = ye  # 出逸点高度
        self.i = i  # 渗透坡降
        self.phi = phi  # 内摩擦角（度）
        self.gamma = gamma  # 天然重度（kN/m³）
        self.gamma_sat = gamma_sat  # 饱和重度（kN/m³）
        self.g = 9.8
        self.gamma_w = 10.0  # 水的重度（kN/m³）
        
    def seepage_force(self) -> float:
        """
        渗透力（单位体积）
        j = i·γw (kN/m³)
        """
        j = self.i * self.gamma_w
        return j
    
    def critical_gradient_piping(self) -> float:
        """
        管涌临界坡降
        [i] = (γs-γw)/γw
        假设土粒重度γs ≈ 26 kN/m³
        """
        gamma_s = 26.0
        i_cr = (gamma_s - self.gamma_w) / self.gamma_w
        return i_cr
    
    def piping_safety_factor(self) -> Tuple[float, bool]:
        """管涌安全系数"""
        i_cr = self.critical_gradient_piping()
        K = i_cr / self.i
        is_safe = K > 1.5
        return K, is_safe
    
    def critical_gradient_quicksand(self, n: float = 0.4) -> float:
        """
        流土临界坡降
        ic = (γs-γw)/(γw·n)
        n: 孔隙率
        """
        gamma_s = 26.0
        ic = (gamma_s - self.gamma_w) / (self.gamma_w * n)
        return ic
    
    def quicksand_safety_factor(self, n: float = 0.4) -> Tuple[float, bool]:
        """流土安全系数"""
        ic = self.critical_gradient_quicksand(n)
        K = ic / self.i
        is_safe = K > 1.5
        return K, is_safe
    
    def slope_stability(self) -> Dict:
        """
        边坡稳定性（简化）
        采用圆弧法简化计算
        """
        # 简化：计算出逸点处的稳定性
        phi_rad = np.deg2rad(self.phi)
        alpha_rad = np.atan(1 / self.m)  # 坡角
        
        # 考虑渗透力的有效应力
        gamma_eff = self.gamma_sat - self.gamma_w
        j = self.seepage_force()
        
        # 简化安全系数（仅考虑内摩擦角）
        # K = tanφ / (tanα + j/(γeff·cosα))
        K_slope = np.tan(phi_rad) / (np.tan(alpha_rad) + j/(gamma_eff*np.cos(alpha_rad)))
        
        is_stable = K_slope > 1.3
        
        return {
            'K': K_slope,
            'is_stable': is_stable,
            'phi': self.phi,
            'alpha': np.rad2deg(alpha_rad),
            'j': j
        }
    
    def prevention_measures(self) -> Dict:
        """渗透破坏防治措施"""
        K_piping, _ = self.piping_safety_factor()
        K_quicksand, _ = self.quicksand_safety_factor()
        slope = self.slope_stability()
        
        measures = {
            'drainage': False,
            'filter': False,
            'weight': False,
            'slope_protection': False
        }
        
        # 根据安全系数判断
        if K_piping < 1.5:
            measures['filter'] = True
        
        if K_quicksand < 1.5:
            measures['weight'] = True
            measures['drainage'] = True
        
        if slope['K'] < 1.3:
            measures['slope_protection'] = True
            measures['drainage'] = True
        
        return measures
    
    def plot_analysis(self):
        """绘制分析图表"""
        fig = plt.figure(figsize=(16, 12))
        
        j = self.seepage_force()
        i_cr_piping = self.critical_gradient_piping()
        K_piping, safe_piping = self.piping_safety_factor()
        i_cr_quicksand = self.critical_gradient_quicksand()
        K_quicksand, safe_quicksand = self.quicksand_safety_factor()
        slope_result = self.slope_stability()
        measures = self.prevention_measures()
        
        # 1. 渗流稳定性示意图
        ax1 = plt.subplot(3, 3, 1)
        
        # 下游坡
        L_slope = self.m * self.H
        x_slope = [0, L_slope]
        y_slope = [self.H, 0]
        ax1.plot(x_slope, y_slope, 'k-', linewidth=3, label='下游坡')
        ax1.fill([0, L_slope, L_slope], [self.H, 0, self.H], color='brown', alpha=0.2)
        
        # 出逸点
        x_exit = L_slope - self.m * (self.H - self.ye)
        ax1.plot(x_exit, self.ye, 'ro', markersize=12, label=f'出逸点(ye={self.ye}m)')
        
        # 渗透力方向（箭头）
        arrow_length = 5
        ax1.arrow(x_exit, self.ye+2, arrow_length*np.cos(np.atan(1/self.m)), 
                 -arrow_length*np.sin(np.atan(1/self.m)),
                 head_width=1, head_length=0.5, fc='red', ec='red', linewidth=2)
        ax1.text(x_exit+3, self.ye+3, '渗透力j', fontsize=10, color='red', fontweight='bold')
        
        # 浸润线（简化）
        x_phreatic = np.linspace(0, x_exit, 50)
        y_phreatic = self.H - (self.H - self.ye) * (x_phreatic / x_exit) ** 0.5
        ax1.plot(x_phreatic, y_phreatic, 'b--', linewidth=2, label='浸润线')
        
        ax1.set_xlabel('水平距离 (m)', fontsize=10)
        ax1.set_ylabel('高程 (m)', fontsize=10)
        ax1.set_title('渗流稳定性示意', fontsize=12, fontweight='bold')
        ax1.legend(fontsize=8)
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim(-2, L_slope+5)
        ax1.set_ylim(-2, self.H+5)
        
        # 2. 计算参数
        ax2 = plt.subplot(3, 3, 2)
        ax2.axis('off')
        
        ax2.text(0.5, 0.95, '稳定性参数', fontsize=11, ha='center', fontweight='bold')
        ax2.text(0.1, 0.82, f'坝高: H = {self.H} m', fontsize=10)
        ax2.text(0.1, 0.72, f'坡比: m = {self.m}', fontsize=10)
        ax2.text(0.1, 0.62, f'坡角: α = {slope_result["alpha"]:.1f}°', fontsize=10)
        ax2.text(0.1, 0.52, f'内摩擦角: φ = {self.phi}°', fontsize=10)
        ax2.text(0.1, 0.42, f'天然重度: γ = {self.gamma} kN/m³', fontsize=10)
        ax2.text(0.1, 0.32, f'饱和重度: γsat = {self.gamma_sat} kN/m³', fontsize=10)
        ax2.text(0.1, 0.20, f'渗透坡降: i = {self.i}', fontsize=10, color='red')
        ax2.text(0.1, 0.10, f'渗透力: j = {j:.2f} kN/m³', fontsize=10, color='red', fontweight='bold')
        ax2.text(0.1, 0.00, 'j = i·γw', fontsize=9, color='gray')
        
        ax2.set_title('基本参数', fontsize=12, fontweight='bold')
        
        # 3. 管涌稳定性
        ax3 = plt.subplot(3, 3, 3)
        ax3.axis('off')
        
        ax3.text(0.5, 0.95, '管涌稳定性', fontsize=11, ha='center', fontweight='bold')
        ax3.text(0.1, 0.80, f'实际坡降: i = {self.i}', fontsize=10)
        ax3.text(0.1, 0.70, f'临界坡降: [i] = {i_cr_piping:.2f}', fontsize=10, color='blue')
        ax3.text(0.1, 0.60, '[i] = (γs-γw)/γw', fontsize=9, color='gray')
        ax3.text(0.1, 0.45, f'安全系数: K = {K_piping:.2f}', fontsize=11, 
                color='green' if safe_piping else 'red', fontweight='bold')
        
        if safe_piping:
            ax3.text(0.1, 0.30, '✓ 满足要求（K>1.5）', fontsize=10, color='green', fontweight='bold')
            ax3.text(0.1, 0.18, '不会发生管涌', fontsize=9)
        else:
            ax3.text(0.1, 0.30, '✗ 不满足要求（K<1.5）', fontsize=10, color='red', fontweight='bold')
            ax3.text(0.1, 0.18, '⚠ 可能发生管涌！', fontsize=9, color='red')
            ax3.text(0.1, 0.08, '建议：设置反滤层', fontsize=9, color='orange')
        
        ax3.set_title('管涌验算', fontsize=12, fontweight='bold')
        
        # 4. 流土稳定性
        ax4 = plt.subplot(3, 3, 4)
        ax4.axis('off')
        
        ax4.text(0.5, 0.95, '流土稳定性', fontsize=11, ha='center', fontweight='bold')
        ax4.text(0.1, 0.80, f'实际坡降: i = {self.i}', fontsize=10)
        ax4.text(0.1, 0.70, f'临界坡降: ic = {i_cr_quicksand:.2f}', fontsize=10, color='blue')
        ax4.text(0.1, 0.60, 'ic = (γs-γw)/(γw·n)', fontsize=9, color='gray')
        ax4.text(0.1, 0.45, f'安全系数: K = {K_quicksand:.2f}', fontsize=11,
                color='green' if safe_quicksand else 'red', fontweight='bold')
        
        if safe_quicksand:
            ax4.text(0.1, 0.30, '✓ 满足要求（K>1.5）', fontsize=10, color='green', fontweight='bold')
            ax4.text(0.1, 0.18, '不会发生流土', fontsize=9)
        else:
            ax4.text(0.1, 0.30, '✗ 不满足要求（K<1.5）', fontsize=10, color='red', fontweight='bold')
            ax4.text(0.1, 0.18, '⚠ 可能发生流土！', fontsize=9, color='red')
            ax4.text(0.1, 0.08, '建议：增加覆盖层', fontsize=9, color='orange')
        
        ax4.set_title('流土验算', fontsize=12, fontweight='bold')
        
        # 5. 边坡稳定性
        ax5 = plt.subplot(3, 3, 5)
        ax5.axis('off')
        
        ax5.text(0.5, 0.95, '边坡稳定性', fontsize=11, ha='center', fontweight='bold')
        ax5.text(0.1, 0.80, f'坡角: α = {slope_result["alpha"]:.1f}°', fontsize=10)
        ax5.text(0.1, 0.70, f'内摩擦角: φ = {slope_result["phi"]:.1f}°', fontsize=10)
        ax5.text(0.1, 0.60, f'渗透力: j = {slope_result["j"]:.2f} kN/m³', fontsize=10)
        ax5.text(0.1, 0.45, f'安全系数: K = {slope_result["K"]:.2f}', fontsize=11,
                color='green' if slope_result['is_stable'] else 'red', fontweight='bold')
        
        if slope_result['is_stable']:
            ax5.text(0.1, 0.30, '✓ 稳定（K>1.3）', fontsize=10, color='green', fontweight='bold')
        else:
            ax5.text(0.1, 0.30, '✗ 不稳定（K<1.3）', fontsize=10, color='red', fontweight='bold')
            ax5.text(0.1, 0.18, '⚠ 边坡可能滑动！', fontsize=9, color='red')
            ax5.text(0.1, 0.08, '建议：削坡或加固', fontsize=9, color='orange')
        
        ax5.set_title('边坡验算', fontsize=12, fontweight='bold')
        
        # 6. 安全系数对比
        ax6 = plt.subplot(3, 3, 6)
        
        categories = ['管涌', '流土', '边坡']
        K_values = [K_piping, K_quicksand, slope_result['K']]
        K_limits = [1.5, 1.5, 1.3]
        colors = ['green' if K > lim else 'red' for K, lim in zip(K_values, K_limits)]
        
        bars = ax6.bar(categories, K_values, color=colors, alpha=0.7, edgecolor='black')
        ax6.axhline(1.5, color='orange', linestyle='--', linewidth=2, label='K≥1.5')
        ax6.axhline(1.3, color='red', linestyle=':', linewidth=2, label='K≥1.3')
        
        ax6.set_ylabel('安全系数 K', fontsize=10)
        ax6.set_title('安全系数对比', fontsize=12, fontweight='bold')
        ax6.legend(fontsize=8)
        ax6.grid(True, alpha=0.3, axis='y')
        
        for bar, K in zip(bars, K_values):
            height = bar.get_height()
            ax6.text(bar.get_x() + bar.get_width()/2., height,
                    f'{K:.2f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        # 7. 渗透坡降影响
        ax7 = plt.subplot(3, 3, 7)
        
        i_range = np.linspace(0.1, 2, 50)
        K_piping_range = [i_cr_piping / i_val for i_val in i_range]
        K_quicksand_range = [i_cr_quicksand / i_val for i_val in i_range]
        
        ax7.plot(i_range, K_piping_range, 'b-', linewidth=2, label='管涌K')
        ax7.plot(i_range, K_quicksand_range, 'g-', linewidth=2, label='流土K')
        ax7.axhline(1.5, color='r', linestyle='--', linewidth=2, label='最小K=1.5')
        ax7.plot(self.i, K_piping, 'ro', markersize=10, label=f'i={self.i}')
        
        ax7.set_xlabel('渗透坡降 i', fontsize=10)
        ax7.set_ylabel('安全系数 K', fontsize=10)
        ax7.set_title('渗透坡降影响', fontsize=12, fontweight='bold')
        ax7.legend(fontsize=8)
        ax7.grid(True, alpha=0.3)
        ax7.set_ylim(0, 5)
        
        # 8. 防治措施
        ax8 = plt.subplot(3, 3, 8)
        ax8.axis('off')
        
        ax8.text(0.5, 0.95, '防治措施', fontsize=11, ha='center', fontweight='bold')
        
        y_pos = 0.80
        if measures['filter']:
            ax8.text(0.1, y_pos, '• 设置反滤层（防管涌）', fontsize=10, color='blue')
            y_pos -= 0.12
        
        if measures['weight']:
            ax8.text(0.1, y_pos, '• 增加覆盖层（防流土）', fontsize=10, color='green')
            y_pos -= 0.12
        
        if measures['drainage']:
            ax8.text(0.1, y_pos, '• 设置排水设施', fontsize=10, color='orange')
            y_pos -= 0.12
        
        if measures['slope_protection']:
            ax8.text(0.1, y_pos, '• 削坡或加固边坡', fontsize=10, color='red')
            y_pos -= 0.12
        
        if not any(measures.values()):
            ax8.text(0.1, 0.50, '✓ 无需特殊措施', fontsize=11, color='green', fontweight='bold')
        
        # 反滤层示意
        ax8.text(0.1, 0.30, '反滤层设计:', fontsize=10, fontweight='bold')
        ax8.text(0.15, 0.20, 'D15(粗)/d85(细) < 5', fontsize=9)
        ax8.text(0.15, 0.12, 'D15(粗)/d15(细) > 5', fontsize=9)
        ax8.text(0.15, 0.04, '分层过渡，3~5层', fontsize=9)
        
        ax8.set_title('工程措施', fontsize=12, fontweight='bold')
        
        # 9. 结果汇总表
        ax9 = plt.subplot(3, 3, 9)
        ax9.axis('off')
        
        table_data = [
            ['项目', '实际值', '标准值', '判别'],
            ['渗透坡降', f'{self.i:.2f}', '-', '-'],
            ['管涌K', f'{K_piping:.2f}', '≥1.5', '✓' if safe_piping else '✗'],
            ['流土K', f'{K_quicksand:.2f}', '≥1.5', '✓' if safe_quicksand else '✗'],
            ['边坡K', f'{slope_result["K"]:.2f}', '≥1.3', '✓' if slope_result['is_stable'] else '✗'],
            ['渗透力', f'{j:.2f}', 'kN/m³', '-'],
            ['临界坡降(管涌)', f'{i_cr_piping:.2f}', '-', '-'],
            ['临界坡降(流土)', f'{i_cr_quicksand:.2f}', '-', '-']
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
        for i in [2, 3, 4]:
            cell = table_data[i][3]
            if cell == '✓':
                table[(i, 3)].set_facecolor('#90EE90')
            elif cell == '✗':
                table[(i, 3)].set_facecolor('#FFB6C1')
        
        ax9.set_title('稳定性汇总', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('/tmp/ch08_problem13_seepage_stability.png', dpi=150, bbox_inches='tight')
        print(f"图表已保存: /tmp/ch08_problem13_seepage_stability.png")
        plt.show()
    
    def print_results(self):
        """打印结果"""
        print("\n" + "="*70)
        print("第08章 渗流计算 - 题13：渗流稳定性分析")
        print("="*70)
        
        j = self.seepage_force()
        i_cr_piping = self.critical_gradient_piping()
        K_piping, safe_piping = self.piping_safety_factor()
        i_cr_quicksand = self.critical_gradient_quicksand()
        K_quicksand, safe_quicksand = self.quicksand_safety_factor()
        slope_result = self.slope_stability()
        
        print(f"\n【土体参数】")
        print(f"坝高: H = {self.H} m")
        print(f"下游坡比: m = {self.m} (1:{self.m})")
        print(f"内摩擦角: φ = {self.phi}°")
        print(f"天然重度: γ = {self.gamma} kN/m³")
        print(f"饱和重度: γsat = {self.gamma_sat} kN/m³")
        print(f"渗透坡降: i = {self.i}")
        
        print(f"\n【渗透力】")
        print(f"j = i·γw = {self.i}×{self.gamma_w} = {j:.2f} kN/m³")
        
        print(f"\n【管涌稳定性】")
        print(f"临界坡降: [i] = (γs-γw)/γw = {i_cr_piping:.2f}")
        print(f"安全系数: K = [i]/i = {K_piping:.2f}")
        if safe_piping:
            print(f"✓ K = {K_piping:.2f} > 1.5，满足要求，不会发生管涌")
        else:
            print(f"✗ K = {K_piping:.2f} < 1.5，不满足要求，可能发生管涌！")
            print(f"⚠ 建议：设置反滤层")
        
        print(f"\n【流土稳定性】")
        print(f"临界坡降: ic = (γs-γw)/(γw·n) = {i_cr_quicksand:.2f}")
        print(f"安全系数: K = ic/i = {K_quicksand:.2f}")
        if safe_quicksand:
            print(f"✓ K = {K_quicksand:.2f} > 1.5，满足要求，不会发生流土")
        else:
            print(f"✗ K = {K_quicksand:.2f} < 1.5，不满足要求，可能发生流土！")
            print(f"⚠ 建议：增加覆盖层、设置排水设施")
        
        print(f"\n【边坡稳定性】")
        print(f"坡角: α = {slope_result['alpha']:.1f}°")
        print(f"安全系数: K = {slope_result['K']:.2f}")
        if slope_result['is_stable']:
            print(f"✓ K = {slope_result['K']:.2f} > 1.3，边坡稳定")
        else:
            print(f"✗ K = {slope_result['K']:.2f} < 1.3，边坡不稳定！")
            print(f"⚠ 建议：削坡、加固、设置排水")
        
        print(f"\n✓ 渗流稳定性分析完成")
        print(f"\n{'='*70}\n")


def main():
    H = 25
    m = 2.5
    ye = 3
    i = 0.8
    phi = 25
    gamma = 19
    gamma_sat = 20
    
    stab = SeepageStability(H, m, ye, i, phi, gamma, gamma_sat)
    stab.print_results()
    stab.plot_analysis()


if __name__ == "__main__":
    main()
