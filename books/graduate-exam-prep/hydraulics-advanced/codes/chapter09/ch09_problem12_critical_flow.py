# -*- coding: utf-8 -*-
"""
第09章 渠系水力计算 - 题12：临界水深与临界坡度

问题描述：
    梯形断面渠道，b = 4m，m = 1.5，n = 0.025，Q = 12 m³/s
    
    求：
    1. 临界水深hc
    2. 临界坡度ic
    3. 临界流速vc
    4. 与正常水深比较（不同底坡）
    5. 坡度分类（缓坡、陡坡、临界坡）
    
核心公式：
    1. 临界流条件：Fr = 1
       Fr = v/√(g·hm) = 1
    2. 临界水深：A³/B = Q²/g
       其中B为水面宽度
    3. 临界坡度：ic对应hc时的底坡
       Q = A·(1/n)R^(2/3)ic^(1/2)

考试要点：
    - 临界水深计算方法
    - Fr数物理意义
    - 坡度分类依据
    - 流态转换判别

作者: CHS-Books Team
日期: 2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve
from typing import Tuple

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class CriticalFlow:
    """临界流计算"""
    
    def __init__(self, b: float, m: float, n: float, Q: float):
        self.b = b
        self.m = m
        self.n = n
        self.Q = Q
        self.g = 9.8
        
    def area(self, h: float) -> float:
        """断面面积"""
        return (self.b + self.m * h) * h
    
    def width(self, h: float) -> float:
        """水面宽度"""
        return self.b + 2 * self.m * h
    
    def wetted_perimeter(self, h: float) -> float:
        """湿周"""
        return self.b + 2 * h * np.sqrt(1 + self.m**2)
    
    def hydraulic_radius(self, h: float) -> float:
        """水力半径"""
        return self.area(h) / self.wetted_perimeter(h)
    
    def critical_depth(self) -> float:
        """
        临界水深：A³/B = Q²/g
        """
        def equation(h):
            A = self.area(h)
            B = self.width(h)
            return A**3 / B - self.Q**2 / self.g
        
        hc = fsolve(equation, 1.0)[0]
        return hc
    
    def critical_velocity(self) -> float:
        """临界流速"""
        hc = self.critical_depth()
        Ac = self.area(hc)
        vc = self.Q / Ac
        return vc
    
    def critical_slope(self) -> float:
        """
        临界坡度：正常水深 = 临界水深时的底坡
        Q = A·(1/n)R^(2/3)ic^(1/2)
        """
        hc = self.critical_depth()
        Ac = self.area(hc)
        Rc = self.hydraulic_radius(hc)
        vc = self.Q / Ac
        
        # ic = (n·v / R^(2/3))²
        ic = (self.n * vc / (Rc ** (2/3)))**2
        return ic
    
    def normal_depth(self, i: float) -> float:
        """正常水深（给定底坡）"""
        def equation(h):
            A = self.area(h)
            R = self.hydraulic_radius(h)
            v = (1 / self.n) * (R ** (2/3)) * (i ** 0.5)
            return A * v - self.Q
        
        h0 = fsolve(equation, 1.0)[0]
        return h0
    
    def froude_number(self, h: float) -> float:
        """Froude数"""
        A = self.area(h)
        v = self.Q / A
        hm = A / self.width(h)  # 平均水深
        Fr = v / np.sqrt(self.g * hm)
        return Fr
    
    def slope_classification(self, i: float) -> str:
        """坡度分类"""
        ic = self.critical_slope()
        h0 = self.normal_depth(i)
        hc = self.critical_depth()
        
        if i < ic:
            return f"缓坡 (i={i} < ic={ic:.6f}, h₀={h0:.3f} > hc={hc:.3f})"
        elif i > ic:
            return f"陡坡 (i={i} > ic={ic:.6f}, h₀={h0:.3f} < hc={hc:.3f})"
        else:
            return f"临界坡 (i={i} ≈ ic={ic:.6f}, h₀ ≈ hc={hc:.3f})"
    
    def plot_analysis(self):
        """绘制分析图表"""
        fig = plt.figure(figsize=(16, 12))
        
        hc = self.critical_depth()
        vc = self.critical_velocity()
        ic = self.critical_slope()
        
        # 1. 断面示意图
        ax1 = plt.subplot(3, 3, 1)
        
        x_trap = np.array([0, self.b, self.b+self.m*hc, -self.m*hc, 0])
        y_trap = np.array([0, 0, hc, hc, 0])
        
        ax1.fill(x_trap, y_trap, color='lightblue', alpha=0.5, label='临界水深')
        ax1.plot(x_trap, y_trap, 'k-', linewidth=2)
        
        ax1.text(self.b/2, -0.2, f'b={self.b}m', ha='center', fontsize=10, color='red', fontweight='bold')
        ax1.text(self.b+0.5, hc/2, f'hc={hc:.2f}m', fontsize=10, color='red', fontweight='bold')
        ax1.text(-0.5, hc/2, f'm={self.m}', fontsize=10, color='blue')
        
        ax1.set_xlim(-1, self.b+2)
        ax1.set_ylim(-0.5, hc+0.5)
        ax1.set_aspect('equal')
        ax1.set_title('临界流断面', fontsize=12, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. 临界流参数
        ax2 = plt.subplot(3, 3, 2)
        ax2.axis('off')
        
        Ac = self.area(hc)
        Bc = self.width(hc)
        Rc = self.hydraulic_radius(hc)
        Frc = self.froude_number(hc)
        
        ax2.text(0.5, 0.9, '临界流参数', fontsize=11, ha='center', fontweight='bold')
        ax2.text(0.1, 0.75, f'临界水深: hc = {hc:.3f} m', fontsize=10, color='red', fontweight='bold')
        ax2.text(0.1, 0.65, f'临界流速: vc = {vc:.3f} m/s', fontsize=10, color='red', fontweight='bold')
        ax2.text(0.1, 0.55, f'临界坡度: ic = {ic:.6f}', fontsize=10, color='red', fontweight='bold')
        ax2.text(0.1, 0.40, f'断面面积: Ac = {Ac:.3f} m²', fontsize=9)
        ax2.text(0.1, 0.30, f'水面宽度: Bc = {Bc:.3f} m', fontsize=9)
        ax2.text(0.1, 0.20, f'水力半径: Rc = {Rc:.3f} m', fontsize=9)
        ax2.text(0.1, 0.05, f'Froude数: Fr = {Frc:.3f} ≈ 1', fontsize=10, color='green', fontweight='bold')
        
        ax2.set_title('临界流特征', fontsize=12, fontweight='bold')
        
        # 3. Fr-h关系
        ax3 = plt.subplot(3, 3, 3)
        
        h_range = np.linspace(0.3, 3, 100)
        Fr_range = [self.froude_number(h) for h in h_range]
        
        ax3.plot(h_range, Fr_range, 'b-', linewidth=2, label='Fr(h)')
        ax3.axhline(1, color='red', linestyle='--', linewidth=2, label='Fr=1')
        ax3.axvline(hc, color='green', linestyle='--', linewidth=2, label=f'hc={hc:.2f}m')
        ax3.plot(hc, 1, 'ro', markersize=10, label='临界点')
        
        # 标注流态
        ax3.fill_between(h_range, 0, Fr_range, where=np.array(Fr_range)<1, 
                        alpha=0.2, color='blue', label='缓流区(Fr<1)')
        ax3.fill_between(h_range, 0, Fr_range, where=np.array(Fr_range)>=1, 
                        alpha=0.2, color='orange', label='急流区(Fr>1)')
        
        ax3.set_xlabel('水深 h (m)', fontsize=10)
        ax3.set_ylabel('Froude数 Fr', fontsize=10)
        ax3.set_title('Fr数与水深关系', fontsize=12, fontweight='bold')
        ax3.legend(fontsize=8)
        ax3.grid(True, alpha=0.3)
        ax3.set_xlim(h_range[0], h_range[-1])
        ax3.set_ylim(0, max(Fr_range)*1.1)
        
        # 4. 坡度分类
        ax4 = plt.subplot(3, 3, 4)
        
        i_range = np.logspace(-5, -2, 100)
        h0_range = [self.normal_depth(i) for i in i_range]
        
        ax4.plot(i_range, h0_range, 'b-', linewidth=2, label='正常水深h₀(i)')
        ax4.axhline(hc, color='red', linestyle='--', linewidth=2, label=f'临界水深hc={hc:.2f}m')
        ax4.axvline(ic, color='green', linestyle='--', linewidth=2, label=f'临界坡度ic={ic:.6f}')
        
        # 标注区域
        ax4.fill_betweenx([0, hc], i_range[0], ic, alpha=0.2, color='blue', label='缓坡区')
        ax4.fill_betweenx([0, hc], ic, i_range[-1], alpha=0.2, color='orange', label='陡坡区')
        
        ax4.set_xlabel('底坡 i', fontsize=10)
        ax4.set_ylabel('正常水深 h₀ (m)', fontsize=10)
        ax4.set_title('坡度分类图', fontsize=12, fontweight='bold')
        ax4.set_xscale('log')
        ax4.legend(fontsize=8)
        ax4.grid(True, alpha=0.3)
        
        # 5. 比能E-h曲线
        ax5 = plt.subplot(3, 3, 5)
        
        h_E = np.linspace(0.3, 3, 100)
        E_range = []
        for h in h_E:
            A = self.area(h)
            v = self.Q / A
            E = h + v**2 / (2 * self.g)
            E_range.append(E)
        
        ax5.plot(E_range, h_E, 'b-', linewidth=2)
        
        # 临界比能
        Ec = hc + vc**2 / (2 * self.g)
        ax5.plot(Ec, hc, 'ro', markersize=10, label=f'临界点(Ec={Ec:.2f}, hc={hc:.2f})')
        ax5.axhline(hc, color='red', linestyle='--', linewidth=1, alpha=0.5)
        ax5.axvline(Ec, color='red', linestyle='--', linewidth=1, alpha=0.5)
        
        ax5.set_xlabel('比能 E (m)', fontsize=10)
        ax5.set_ylabel('水深 h (m)', fontsize=10)
        ax5.set_title('比能曲线', fontsize=12, fontweight='bold')
        ax5.legend()
        ax5.grid(True, alpha=0.3)
        
        # 6. h₀与hc对比（多个坡度）
        ax6 = plt.subplot(3, 3, 6)
        
        i_test = [0.0001, 0.0005, ic, 0.001, 0.005]
        h0_test = [self.normal_depth(i) for i in i_test]
        labels = [f'i={i:.6f}' for i in i_test]
        
        colors = ['blue' if i < ic else 'orange' if i > ic else 'green' for i in i_test]
        
        bars = ax6.bar(range(len(i_test)), h0_test, color=colors, alpha=0.6, edgecolor='black')
        ax6.axhline(hc, color='red', linestyle='--', linewidth=2, label=f'hc={hc:.2f}m')
        
        ax6.set_xticks(range(len(i_test)))
        ax6.set_xticklabels([f'i{j+1}' for j in range(len(i_test))], fontsize=9)
        ax6.set_ylabel('水深 (m)', fontsize=10)
        ax6.set_title('不同坡度下h₀与hc对比', fontsize=12, fontweight='bold')
        ax6.legend()
        ax6.grid(True, alpha=0.3, axis='y')
        
        # 添加数值标签
        for bar, h0, lbl in zip(bars, h0_test, labels):
            height = bar.get_height()
            ax6.text(bar.get_x() + bar.get_width()/2., height,
                    f'{h0:.2f}m\n{lbl}', ha='center', va='bottom', fontsize=7)
        
        # 7. 流速-水深关系
        ax7 = plt.subplot(3, 3, 7)
        
        v_range = [self.Q / self.area(h) for h in h_range]
        
        ax7.plot(h_range, v_range, 'b-', linewidth=2, label='流速v(h)')
        ax7.axvline(hc, color='red', linestyle='--', linewidth=2, label=f'hc={hc:.2f}m')
        ax7.axhline(vc, color='green', linestyle='--', linewidth=2, label=f'vc={vc:.2f}m/s')
        ax7.plot(hc, vc, 'ro', markersize=10, label='临界点')
        
        ax7.set_xlabel('水深 h (m)', fontsize=10)
        ax7.set_ylabel('流速 v (m/s)', fontsize=10)
        ax7.set_title('流速-水深关系', fontsize=12, fontweight='bold')
        ax7.legend(fontsize=8)
        ax7.grid(True, alpha=0.3)
        
        # 8. 坡度分类表
        ax8 = plt.subplot(3, 3, 8)
        ax8.axis('off')
        
        ax8.text(0.5, 0.95, '坡度分类判别', fontsize=11, ha='center', fontweight='bold')
        
        ax8.text(0.1, 0.80, '缓坡 (Mild):', fontsize=10, color='blue', fontweight='bold')
        ax8.text(0.15, 0.70, 'i < ic, h₀ > hc, Fr < 1', fontsize=9)
        
        ax8.text(0.1, 0.55, '临界坡 (Critical):', fontsize=10, color='green', fontweight='bold')
        ax8.text(0.15, 0.45, 'i = ic, h₀ = hc, Fr = 1', fontsize=9)
        
        ax8.text(0.1, 0.30, '陡坡 (Steep):', fontsize=10, color='orange', fontweight='bold')
        ax8.text(0.15, 0.20, 'i > ic, h₀ < hc, Fr > 1', fontsize=9)
        
        ax8.text(0.1, 0.05, f'本例: ic = {ic:.6f}', fontsize=10, color='red', fontweight='bold')
        
        ax8.set_title('分类标准', fontsize=12, fontweight='bold')
        
        # 9. 结果汇总表
        ax9 = plt.subplot(3, 3, 9)
        ax9.axis('off')
        
        table_data = [
            ['参数', '数值', '单位'],
            ['临界水深', f'{hc:.3f}', 'm'],
            ['临界流速', f'{vc:.3f}', 'm/s'],
            ['临界坡度', f'{ic:.6f}', '-'],
            ['断面面积', f'{Ac:.3f}', 'm²'],
            ['水面宽度', f'{Bc:.3f}', 'm'],
            ['水力半径', f'{Rc:.3f}', 'm'],
            ['Froude数', f'{Frc:.3f}', '-'],
            ['临界比能', f'{Ec:.3f}', 'm']
        ]
        
        table = ax9.table(cellText=table_data, cellLoc='center', loc='center',
                         colWidths=[0.4, 0.3, 0.2])
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2.2)
        
        for i in range(3):
            table[(0, i)].set_facecolor('#4472C4')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        ax9.set_title('临界流参数汇总', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('/tmp/ch09_problem12_critical_flow.png', dpi=150, bbox_inches='tight')
        print(f"图表已保存: /tmp/ch09_problem12_critical_flow.png")
        plt.show()
    
    def print_results(self):
        """打印结果"""
        print("\n" + "="*70)
        print("第09章 渠系水力计算 - 题12：临界水深与临界坡度")
        print("="*70)
        
        hc = self.critical_depth()
        vc = self.critical_velocity()
        ic = self.critical_slope()
        
        print(f"\n【渠道参数】")
        print(f"底宽: b = {self.b} m")
        print(f"边坡系数: m = {self.m}")
        print(f"糙率: n = {self.n}")
        print(f"流量: Q = {self.Q} m³/s")
        
        print(f"\n【临界流参数】")
        print(f"临界水深: hc = {hc:.3f} m")
        print(f"临界流速: vc = {vc:.3f} m/s")
        print(f"临界坡度: ic = {ic:.6f}")
        
        Ac = self.area(hc)
        Bc = self.width(hc)
        Rc = self.hydraulic_radius(hc)
        Frc = self.froude_number(hc)
        
        print(f"\n【断面参数（临界流）】")
        print(f"面积: Ac = {Ac:.3f} m²")
        print(f"水面宽度: Bc = {Bc:.3f} m")
        print(f"水力半径: Rc = {Rc:.3f} m")
        print(f"Froude数: Fr = {Frc:.3f} ≈ 1.0 ✓")
        
        print(f"\n【坡度分类示例】")
        for i in [0.0001, 0.0005, ic, 0.001, 0.005]:
            print(f"\n  {self.slope_classification(i)}")
        
        print(f"\n✓ 临界流分析完成")
        print(f"\n{'='*70}\n")


def main():
    b = 4
    m = 1.5
    n = 0.025
    Q = 12
    
    cf = CriticalFlow(b, m, n, Q)
    cf.print_results()
    cf.plot_analysis()


if __name__ == "__main__":
    main()
