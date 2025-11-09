# -*- coding: utf-8 -*-
"""
第09章 渠系水力计算 - 题3：优化断面设计

问题描述：
    设计流量Q = 10 m³/s，底坡i = 0.0005，糙率n = 0.025
    求梯形断面优化设计（水力最优断面）
    
    约束条件：
    - 边坡系数m = 1.5（1:1.5）
    - 底宽b与水深h的关系待定
    
    求：
    1. 水力最优断面条件
    2. 最优底宽与水深
    3. 与矩形、三角形断面对比
    4. 土方量分析
    5. 经济性比较

核心公式：
    1. 梯形断面：A = (b+mh)h，χ = b+2h√(1+m²)
    2. 水力最优条件：R最大 → χ最小（A固定）
    3. 最优条件：b = 2h(√(1+m²)-m)
    4. Manning: v = (1/n)R^(2/3)i^(1/2)

考试要点：
    - 水力最优断面定义
    - 梯形断面最优条件
    - 与其他断面对比
    - 工程经济性

作者: CHS-Books Team
日期: 2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple
from scipy.optimize import fsolve

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class OptimalSection:
    """优化断面设计"""
    
    def __init__(self, Q: float, i: float, n: float, m: float = 1.5):
        self.Q = Q
        self.i = i
        self.n = n
        self.m = m  # 边坡系数
        self.g = 9.8
        
    def trapezoid_area(self, b: float, h: float) -> float:
        """梯形断面面积"""
        return (b + self.m * h) * h
    
    def trapezoid_perimeter(self, b: float, h: float) -> float:
        """梯形断面湿周"""
        return b + 2 * h * np.sqrt(1 + self.m**2)
    
    def hydraulic_radius(self, b: float, h: float) -> float:
        """水力半径"""
        A = self.trapezoid_area(b, h)
        chi = self.trapezoid_perimeter(b, h)
        return A / chi
    
    def velocity(self, R: float) -> float:
        """流速（Manning）"""
        return (1 / self.n) * (R ** (2/3)) * (self.i ** 0.5)
    
    def optimal_condition(self) -> Tuple[float, float]:
        """
        水力最优断面条件
        b_opt = 2h(√(1+m²)-m)
        """
        def equations(vars):
            h = vars[0]
            b = 2 * h * (np.sqrt(1 + self.m**2) - self.m)
            R = self.hydraulic_radius(b, h)
            v = self.velocity(R)
            A = self.trapezoid_area(b, h)
            return [A * v - self.Q]
        
        h_init = 2.0
        h_opt = fsolve(equations, h_init)[0]
        b_opt = 2 * h_opt * (np.sqrt(1 + self.m**2) - self.m)
        
        return b_opt, h_opt
    
    def compare_sections(self) -> dict:
        """对比不同断面"""
        # 最优梯形
        b_opt, h_opt = self.optimal_condition()
        A_opt = self.trapezoid_area(b_opt, h_opt)
        chi_opt = self.trapezoid_perimeter(b_opt, h_opt)
        
        # 矩形（b=2h最优）
        def rect_eq(h):
            b = 2 * h
            A = b * h
            chi = b + 2 * h
            R = A / chi
            v = self.velocity(R)
            return A * v - self.Q
        
        h_rect = fsolve(rect_eq, 2.0)[0]
        b_rect = 2 * h_rect
        A_rect = b_rect * h_rect
        chi_rect = b_rect + 2 * h_rect
        
        return {
            'optimal_trap': {'b': b_opt, 'h': h_opt, 'A': A_opt, 'chi': chi_opt},
            'rectangle': {'b': b_rect, 'h': h_rect, 'A': A_rect, 'chi': chi_rect}
        }
    
    def plot_analysis(self):
        """绘制分析图表"""
        fig = plt.figure(figsize=(16, 12))
        
        b_opt, h_opt = self.optimal_condition()
        R_opt = self.hydraulic_radius(b_opt, h_opt)
        v_opt = self.velocity(R_opt)
        A_opt = self.trapezoid_area(b_opt, h_opt)
        
        # 1. 优化断面示意图
        ax1 = plt.subplot(3, 3, 1)
        
        # 绘制梯形
        x_trap = np.array([0, b_opt, b_opt+self.m*h_opt, -self.m*h_opt, 0])
        y_trap = np.array([0, 0, h_opt, h_opt, 0])
        
        ax1.fill(x_trap, y_trap, color='lightblue', alpha=0.5, label='水体')
        ax1.plot(x_trap, y_trap, 'k-', linewidth=2)
        
        # 标注尺寸
        ax1.text(b_opt/2, -0.3, f'b={b_opt:.2f}m', ha='center', fontsize=10, color='red', fontweight='bold')
        ax1.text(b_opt+0.5, h_opt/2, f'h={h_opt:.2f}m', fontsize=10, color='red', fontweight='bold')
        ax1.text(-0.5, h_opt/2, f'm={self.m}', fontsize=10, color='blue')
        
        ax1.set_aspect('equal')
        ax1.set_title('优化梯形断面', fontsize=12, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. 优化条件推导
        ax2 = plt.subplot(3, 3, 2)
        ax2.axis('off')
        ax2.text(0.5, 0.9, '水力最优条件推导', fontsize=11, ha='center', fontweight='bold')
        ax2.text(0.1, 0.75, '目标：A固定，χ最小 → R最大', fontsize=10)
        ax2.text(0.1, 0.60, f'A = (b+mh)h = {A_opt:.2f} m²', fontsize=10)
        ax2.text(0.1, 0.50, f'χ = b+2h√(1+m²)', fontsize=10)
        ax2.text(0.1, 0.35, f'最优条件：dχ/db = 0', fontsize=10, color='red')
        ax2.text(0.1, 0.20, f'b_opt = 2h(√(1+m²)-m)', fontsize=10, color='red', fontweight='bold')
        ax2.text(0.1, 0.05, f'得：b={b_opt:.2f}m, h={h_opt:.2f}m', fontsize=10, color='blue', fontweight='bold')
        ax2.set_title('优化条件', fontsize=12, fontweight='bold')
        
        # 3. b-h关系
        ax3 = plt.subplot(3, 3, 3)
        h_range = np.linspace(0.5, 4, 100)
        b_range = 2 * h_range * (np.sqrt(1 + self.m**2) - self.m)
        
        ax3.plot(h_range, b_range, 'b-', linewidth=2, label='b=2h(√(1+m²)-m)')
        ax3.plot(h_opt, b_opt, 'ro', markersize=10, label=f'最优点({h_opt:.2f}, {b_opt:.2f})')
        ax3.set_xlabel('水深 h (m)', fontsize=10)
        ax3.set_ylabel('底宽 b (m)', fontsize=10)
        ax3.set_title('b-h最优关系', fontsize=12, fontweight='bold')
        ax3.grid(True, alpha=0.3)
        ax3.legend()
        
        # 4. 断面对比（梯形、矩形、三角形）
        ax4 = plt.subplot(3, 3, 4)
        
        # 矩形
        h_rect = fsolve(lambda h: 2*h*h * self.velocity(2*h*h/(2*h+2*h)) - self.Q, 2.0)[0]
        b_rect = 2 * h_rect
        x_rect = np.array([0, b_rect, b_rect, 0, 0])
        y_rect = np.array([0, 0, h_rect, h_rect, 0])
        ax4.plot(x_rect, y_rect, 'g--', linewidth=2, label=f'矩形 b={b_rect:.2f}m')
        
        # 优化梯形
        ax4.fill(x_trap, y_trap, color='lightblue', alpha=0.3)
        ax4.plot(x_trap, y_trap, 'b-', linewidth=2, label=f'梯形 b={b_opt:.2f}m')
        
        ax4.set_aspect('equal')
        ax4.set_xlabel('宽度 (m)', fontsize=10)
        ax4.set_ylabel('高度 (m)', fontsize=10)
        ax4.set_title('断面形式对比', fontsize=12, fontweight='bold')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        # 5. 参数对比柱状图
        ax5 = plt.subplot(3, 3, 5)
        
        A_rect = b_rect * h_rect
        chi_rect = b_rect + 2 * h_rect
        R_rect = A_rect / chi_rect
        
        categories = ['面积\n(m²)', '湿周\n(m)', '水力半径\n(m)']
        trap_vals = [A_opt, self.trapezoid_perimeter(b_opt, h_opt), R_opt]
        rect_vals = [A_rect, chi_rect, R_rect]
        
        x = np.arange(len(categories))
        width = 0.35
        
        bars1 = ax5.bar(x - width/2, trap_vals, width, label='梯形', color='skyblue')
        bars2 = ax5.bar(x + width/2, rect_vals, width, label='矩形', color='lightgreen')
        
        ax5.set_xticks(x)
        ax5.set_xticklabels(categories, fontsize=9)
        ax5.set_title('参数对比', fontsize=12, fontweight='bold')
        ax5.legend()
        ax5.grid(True, alpha=0.3, axis='y')
        
        # 添加数值标签
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax5.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.2f}', ha='center', va='bottom', fontsize=8)
        
        # 6. 湿周随b变化（h固定）
        ax6 = plt.subplot(3, 3, 6)
        b_test = np.linspace(0.5, 10, 100)
        chi_test = b_test + 2 * h_opt * np.sqrt(1 + self.m**2)
        
        ax6.plot(b_test, chi_test, 'b-', linewidth=2)
        ax6.plot(b_opt, self.trapezoid_perimeter(b_opt, h_opt), 'ro', markersize=10, label='最优点')
        ax6.set_xlabel('底宽 b (m)', fontsize=10)
        ax6.set_ylabel('湿周 χ (m)', fontsize=10)
        ax6.set_title('湿周随b变化（h固定）', fontsize=12, fontweight='bold')
        ax6.grid(True, alpha=0.3)
        ax6.legend()
        
        # 7. 水力半径随b变化
        ax7 = plt.subplot(3, 3, 7)
        R_test = []
        for b in b_test:
            A = self.trapezoid_area(b, h_opt)
            chi = self.trapezoid_perimeter(b, h_opt)
            R_test.append(A / chi)
        
        ax7.plot(b_test, R_test, 'b-', linewidth=2)
        ax7.plot(b_opt, R_opt, 'ro', markersize=10, label='最优点')
        ax7.set_xlabel('底宽 b (m)', fontsize=10)
        ax7.set_ylabel('水力半径 R (m)', fontsize=10)
        ax7.set_title('水力半径随b变化', fontsize=12, fontweight='bold')
        ax7.grid(True, alpha=0.3)
        ax7.legend()
        
        # 8. 土方量对比
        ax8 = plt.subplot(3, 3, 8)
        
        # 假设开挖深度
        H_dig = h_opt + 0.5  # 加保护层
        
        # 梯形土方量
        V_trap = ((b_opt + (b_opt + 2*self.m*H_dig)) / 2) * H_dig  # 单位长度
        # 矩形土方量
        V_rect = b_rect * (h_rect + 0.5)
        
        sections = ['梯形优化', '矩形']
        volumes = [V_trap, V_rect]
        colors = ['skyblue', 'lightgreen']
        
        bars = ax8.bar(sections, volumes, color=colors, alpha=0.7, edgecolor='black')
        ax8.set_ylabel('单位长度土方 (m³/m)', fontsize=10)
        ax8.set_title('土方量对比', fontsize=12, fontweight='bold')
        ax8.grid(True, alpha=0.3, axis='y')
        
        for bar, vol in zip(bars, volumes):
            height = bar.get_height()
            ax8.text(bar.get_x() + bar.get_width()/2., height,
                    f'{vol:.2f}\nm³/m', ha='center', va='bottom', fontsize=9)
        
        # 9. 综合结果表
        ax9 = plt.subplot(3, 3, 9)
        ax9.axis('off')
        
        table_data = [
            ['参数', '梯形优化', '矩形'],
            ['底宽(m)', f'{b_opt:.2f}', f'{b_rect:.2f}'],
            ['水深(m)', f'{h_opt:.2f}', f'{h_rect:.2f}'],
            ['面积(m²)', f'{A_opt:.2f}', f'{A_rect:.2f}'],
            ['湿周(m)', f'{self.trapezoid_perimeter(b_opt, h_opt):.2f}', f'{chi_rect:.2f}'],
            ['水力半径(m)', f'{R_opt:.3f}', f'{R_rect:.3f}'],
            ['流速(m/s)', f'{v_opt:.3f}', f'{self.velocity(R_rect):.3f}'],
            ['土方(m³/m)', f'{V_trap:.2f}', f'{V_rect:.2f}']
        ]
        
        table = ax9.table(cellText=table_data, cellLoc='center', loc='center',
                         colWidths=[0.3, 0.35, 0.35])
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2)
        
        # 设置表头样式
        for i in range(3):
            table[(0, i)].set_facecolor('#4472C4')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        ax9.set_title('优化结果汇总', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('/tmp/ch09_problem03_optimal_section.png', dpi=150, bbox_inches='tight')
        print(f"图表已保存: /tmp/ch09_problem03_optimal_section.png")
        plt.show()
    
    def print_results(self):
        """打印结果"""
        print("\n" + "="*70)
        print("第09章 渠系水力计算 - 题3：优化断面设计")
        print("="*70)
        
        b_opt, h_opt = self.optimal_condition()
        A_opt = self.trapezoid_area(b_opt, h_opt)
        chi_opt = self.trapezoid_perimeter(b_opt, h_opt)
        R_opt = self.hydraulic_radius(b_opt, h_opt)
        v_opt = self.velocity(R_opt)
        
        print(f"\n【设计条件】")
        print(f"设计流量: Q = {self.Q} m³/s")
        print(f"底坡: i = {self.i}")
        print(f"糙率: n = {self.n}")
        print(f"边坡系数: m = {self.m}")
        
        print(f"\n【优化断面】")
        print(f"底宽: b = {b_opt:.3f} m")
        print(f"水深: h = {h_opt:.3f} m")
        print(f"面积: A = {A_opt:.3f} m²")
        print(f"湿周: χ = {chi_opt:.3f} m")
        print(f"水力半径: R = {R_opt:.3f} m")
        print(f"流速: v = {v_opt:.3f} m/s")
        
        print(f"\n【优化条件】")
        print(f"b = 2h(√(1+m²)-m)")
        print(f"  = 2×{h_opt:.3f}×(√(1+{self.m}²)-{self.m})")
        print(f"  = {b_opt:.3f} m")
        
        print(f"\n✓ 水力最优断面设计完成")
        print(f"\n{'='*70}\n")


def main():
    Q = 10
    i = 0.0005
    n = 0.025
    m = 1.5
    
    opt = OptimalSection(Q, i, n, m)
    opt.print_results()
    opt.plot_analysis()


if __name__ == "__main__":
    main()
