# -*- coding: utf-8 -*-
"""
第12章 河流动力学 - 题7：河相关系分析

问题描述：
    某河段统计数据：多年平均流量Q = 800 m³/s
    河道宽度B = 150m，平均水深h = 6m
    河床坡度i = 0.0003，河床泥沙d₅₀ = 0.3mm
    
    求：
    1. 河相系数计算
    2. 河宽-流量关系
    3. 水深-流量关系
    4. 河相关系验证
    5. 河道稳定性评价

核心公式：
    1. 河宽关系：B = K_B·Q^b
    2. 水深关系：h = K_h·Q^f
    3. 流速关系：v = K_v·Q^m
    4. 约束条件：b + f + m = 1

考试要点：
    - 河相关系
    - 幂函数拟合
    - 河道稳定
    - 参数估算

作者: CHS-Books Team
日期: 2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, Dict, List
from scipy.optimize import curve_fit

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class RiverRegime:
    """河相关系分析"""
    
    def __init__(self, Q: float, B: float, h: float, i: float, d50: float):
        self.Q = Q  # 多年平均流量
        self.B = B  # 河道宽度
        self.h = h  # 平均水深
        self.i = i  # 河床坡度
        self.d50 = d50  # 中值粒径 mm
        self.g = 9.8
        
    def regime_coefficients(self) -> Dict:
        """
        河相系数（经验值）
        冲积平原河流：
        B = 4.7·Q^0.5
        h = 0.56·Q^0.36
        v = 0.38·Q^0.14
        """
        K_B = 4.7
        b = 0.5
        
        K_h = 0.56
        f = 0.36
        
        K_v = 0.38
        m = 0.14
        
        # 验证：b + f + m = 1
        check = b + f + m
        
        return {
            'K_B': K_B,
            'b': b,
            'K_h': K_h,
            'f': f,
            'K_v': K_v,
            'm': m,
            'sum': check
        }
    
    def calculate_width(self, Q: float) -> float:
        """
        根据流量计算河宽
        B = K_B·Q^b
        """
        coeffs = self.regime_coefficients()
        B_calc = coeffs['K_B'] * (Q ** coeffs['b'])
        return B_calc
    
    def calculate_depth(self, Q: float) -> float:
        """
        根据流量计算水深
        h = K_h·Q^f
        """
        coeffs = self.regime_coefficients()
        h_calc = coeffs['K_h'] * (Q ** coeffs['f'])
        return h_calc
    
    def calculate_velocity(self, Q: float) -> float:
        """
        根据流量计算流速
        v = K_v·Q^m
        """
        coeffs = self.regime_coefficients()
        v_calc = coeffs['K_v'] * (Q ** coeffs['m'])
        return v_calc
    
    def actual_velocity(self) -> float:
        """实际流速"""
        return self.Q / (self.B * self.h)
    
    def regime_validation(self) -> Dict:
        """河相关系验证"""
        B_calc = self.calculate_width(self.Q)
        h_calc = self.calculate_depth(self.Q)
        v_calc = self.calculate_velocity(self.Q)
        v_actual = self.actual_velocity()
        
        # 相对误差
        error_B = abs(B_calc - self.B) / self.B * 100
        error_h = abs(h_calc - self.h) / self.h * 100
        error_v = abs(v_calc - v_actual) / v_actual * 100
        
        return {
            'B_calc': B_calc,
            'error_B': error_B,
            'h_calc': h_calc,
            'error_h': error_h,
            'v_calc': v_calc,
            'v_actual': v_actual,
            'error_v': error_v
        }
    
    def stability_index(self) -> Tuple[float, str]:
        """
        河道稳定性指标
        SI = (B·h)/(Q·√i)
        SI > 1: 稳定
        """
        SI = (self.B * self.h) / (self.Q * np.sqrt(self.i))
        
        if SI > 1.5:
            status = "稳定"
        elif SI > 1.0:
            status = "基本稳定"
        else:
            status = "不稳定"
        
        return SI, status
    
    def hydraulic_geometry(self, Q_range: np.ndarray) -> Dict:
        """
        水力几何形态关系
        """
        B_range = [self.calculate_width(Q) for Q in Q_range]
        h_range = [self.calculate_depth(Q) for Q in Q_range]
        v_range = [self.calculate_velocity(Q) for Q in Q_range]
        
        return {
            'Q': Q_range,
            'B': np.array(B_range),
            'h': np.array(h_range),
            'v': np.array(v_range)
        }
    
    def plot_analysis(self):
        """绘制分析图表"""
        fig = plt.figure(figsize=(16, 12))
        
        coeffs = self.regime_coefficients()
        validation = self.regime_validation()
        SI, status = self.stability_index()
        v_actual = self.actual_velocity()
        
        # 流量范围
        Q_range = np.linspace(200, 2000, 100)
        geom = self.hydraulic_geometry(Q_range)
        
        # 1. 河道断面示意图
        ax1 = plt.subplot(3, 3, 1)
        
        y_section = np.linspace(0, self.B, 100)
        z_bed = np.zeros_like(y_section) - self.h
        z_surface = np.zeros_like(y_section)
        
        ax1.fill_between(y_section, z_bed, z_surface, alpha=0.5, color='lightblue')
        ax1.plot(y_section, z_surface, 'b-', linewidth=2, label='水面')
        ax1.plot(y_section, z_bed, 'k-', linewidth=2, label='河床')
        
        # 标注
        ax1.text(self.B/2, -self.h/2, f'Q={self.Q}m³/s\nB={self.B}m\nh={self.h}m\nv={v_actual:.2f}m/s', 
                ha='center', va='center', fontsize=9,
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        ax1.set_xlabel('宽度 (m)', fontsize=10)
        ax1.set_ylabel('高程 (m)', fontsize=10)
        ax1.set_title('河道断面', fontsize=12, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. 河相系数
        ax2 = plt.subplot(3, 3, 2)
        ax2.axis('off')
        
        ax2.text(0.5, 0.95, '河相系数', fontsize=11, ha='center', fontweight='bold')
        ax2.text(0.1, 0.80, '河宽关系: B = K_B·Q^b', fontsize=10, color='blue')
        ax2.text(0.15, 0.70, f'K_B = {coeffs["K_B"]}, b = {coeffs["b"]}', fontsize=9)
        ax2.text(0.1, 0.58, '水深关系: h = K_h·Q^f', fontsize=10, color='green')
        ax2.text(0.15, 0.48, f'K_h = {coeffs["K_h"]}, f = {coeffs["f"]}', fontsize=9)
        ax2.text(0.1, 0.36, '流速关系: v = K_v·Q^m', fontsize=10, color='red')
        ax2.text(0.15, 0.26, f'K_v = {coeffs["K_v"]}, m = {coeffs["m"]}', fontsize=9)
        ax2.text(0.1, 0.12, f'验证: b+f+m = {coeffs["sum"]:.2f}', fontsize=10,
                color='purple', fontweight='bold')
        ax2.text(0.1, 0.02, '✓ 满足连续性方程', fontsize=9, color='green')
        
        ax2.set_title('经验系数', fontsize=12, fontweight='bold')
        
        # 3. B-Q关系
        ax3 = plt.subplot(3, 3, 3)
        
        ax3.plot(Q_range, geom['B'], 'b-', linewidth=2, label='经验公式')
        ax3.plot(self.Q, self.B, 'ro', markersize=12, label=f'实测值')
        ax3.plot(self.Q, validation['B_calc'], 'g^', markersize=10, label=f'计算值')
        
        ax3.set_xlabel('流量 Q (m³/s)', fontsize=10)
        ax3.set_ylabel('河宽 B (m)', fontsize=10)
        ax3.set_title(f'河宽-流量关系 (误差{validation["error_B"]:.1f}%)', fontsize=12, fontweight='bold')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. h-Q关系
        ax4 = plt.subplot(3, 3, 4)
        
        ax4.plot(Q_range, geom['h'], 'g-', linewidth=2, label='经验公式')
        ax4.plot(self.Q, self.h, 'ro', markersize=12, label=f'实测值')
        ax4.plot(self.Q, validation['h_calc'], 'b^', markersize=10, label=f'计算值')
        
        ax4.set_xlabel('流量 Q (m³/s)', fontsize=10)
        ax4.set_ylabel('水深 h (m)', fontsize=10)
        ax4.set_title(f'水深-流量关系 (误差{validation["error_h"]:.1f}%)', fontsize=12, fontweight='bold')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        # 5. v-Q关系
        ax5 = plt.subplot(3, 3, 5)
        
        ax5.plot(Q_range, geom['v'], 'r-', linewidth=2, label='经验公式')
        ax5.plot(self.Q, v_actual, 'go', markersize=12, label=f'实测值')
        ax5.plot(self.Q, validation['v_calc'], 'b^', markersize=10, label=f'计算值')
        
        ax5.set_xlabel('流量 Q (m³/s)', fontsize=10)
        ax5.set_ylabel('流速 v (m/s)', fontsize=10)
        ax5.set_title(f'流速-流量关系 (误差{validation["error_v"]:.1f}%)', fontsize=12, fontweight='bold')
        ax5.legend()
        ax5.grid(True, alpha=0.3)
        
        # 6. 对数坐标B-Q
        ax6 = plt.subplot(3, 3, 6)
        
        ax6.loglog(Q_range, geom['B'], 'b-', linewidth=2, label='B=4.7·Q^0.5')
        ax6.loglog(self.Q, self.B, 'ro', markersize=12, label='实测')
        
        ax6.set_xlabel('lg(Q) (m³/s)', fontsize=10)
        ax6.set_ylabel('lg(B) (m)', fontsize=10)
        ax6.set_title('对数坐标B-Q关系', fontsize=12, fontweight='bold')
        ax6.legend()
        ax6.grid(True, alpha=0.3, which='both')
        
        # 7. 稳定性分析
        ax7 = plt.subplot(3, 3, 7)
        ax7.axis('off')
        
        ax7.text(0.5, 0.95, '河道稳定性', fontsize=11, ha='center', fontweight='bold')
        ax7.text(0.1, 0.78, f'稳定性指标:', fontsize=10)
        ax7.text(0.15, 0.68, f'SI = (B·h)/(Q·√i)', fontsize=9, color='gray')
        ax7.text(0.15, 0.58, f'   = ({self.B}×{self.h})/({self.Q}×√{self.i})', fontsize=9, color='gray')
        ax7.text(0.1, 0.45, f'SI = {SI:.3f}', fontsize=12, 
                color='green' if SI>1 else 'red', fontweight='bold')
        ax7.text(0.1, 0.30, f'评价: {status}', fontsize=11,
                color='green' if SI>1 else 'red', fontweight='bold')
        
        ax7.text(0.1, 0.15, '判别标准:', fontsize=9)
        ax7.text(0.15, 0.08, 'SI>1.5: 稳定', fontsize=8)
        ax7.text(0.15, 0.02, 'SI>1.0: 基本稳定', fontsize=8)
        
        ax7.set_title('稳定评价', fontsize=12, fontweight='bold')
        
        # 8. 横断面形态
        ax8 = plt.subplot(3, 3, 8)
        
        # 不同流量下的断面
        Q_levels = [400, 800, 1200, 1600]
        colors_levels = ['lightblue', 'blue', 'darkblue', 'navy']
        
        for Q_val, color in zip(Q_levels, colors_levels):
            B_val = self.calculate_width(Q_val)
            h_val = self.calculate_depth(Q_val)
            
            y = np.linspace(0, B_val, 50)
            z_top = np.zeros_like(y)
            z_bottom = np.zeros_like(y) - h_val
            
            ax8.fill_between(y, z_bottom, z_top, alpha=0.3, color=color, label=f'Q={Q_val}m³/s')
        
        ax8.set_xlabel('宽度 (m)', fontsize=10)
        ax8.set_ylabel('深度 (m)', fontsize=10)
        ax8.set_title('不同流量下的断面形态', fontsize=12, fontweight='bold')
        ax8.legend(fontsize=8)
        ax8.grid(True, alpha=0.3)
        
        # 9. 结果汇总表
        ax9 = plt.subplot(3, 3, 9)
        ax9.axis('off')
        
        table_data = [
            ['项目', '实测', '计算', '误差(%)'],
            ['河宽(m)', f'{self.B:.1f}', f'{validation["B_calc"]:.1f}', f'{validation["error_B"]:.1f}'],
            ['水深(m)', f'{self.h:.2f}', f'{validation["h_calc"]:.2f}', f'{validation["error_h"]:.1f}'],
            ['流速(m/s)', f'{v_actual:.2f}', f'{validation["v_calc"]:.2f}', f'{validation["error_v"]:.1f}'],
            ['稳定指标', f'{SI:.3f}', status, '-']
        ]
        
        table = ax9.table(cellText=table_data, cellLoc='center', loc='center',
                         colWidths=[0.3, 0.25, 0.25, 0.18])
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2.2)
        
        for i in range(4):
            table[(0, i)].set_facecolor('#4472C4')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        # 高亮稳定性
        table[(5, 0)].set_facecolor('#FFF9E6')
        table[(5, 1)].set_facecolor('#FFF9E6')
        table[(5, 2)].set_facecolor('#90EE90' if SI>1 else '#FFB6C1')
        
        ax9.set_title('验证结果汇总', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('/tmp/ch12_problem07_river_regime.png', dpi=150, bbox_inches='tight')
        print(f"图表已保存: /tmp/ch12_problem07_river_regime.png")
        plt.show()
    
    def print_results(self):
        """打印结果"""
        print("\n" + "="*70)
        print("第12章 河流动力学 - 题7：河相关系分析")
        print("="*70)
        
        coeffs = self.regime_coefficients()
        validation = self.regime_validation()
        SI, status = self.stability_index()
        v_actual = self.actual_velocity()
        
        print(f"\n【河道参数】")
        print(f"多年平均流量: Q = {self.Q} m³/s")
        print(f"河道宽度: B = {self.B} m")
        print(f"平均水深: h = {self.h} m")
        print(f"实际流速: v = Q/(B·h) = {v_actual:.3f} m/s")
        print(f"河床坡度: i = {self.i}")
        
        print(f"\n【河相系数（冲积平原河流）】")
        print(f"河宽关系: B = K_B·Q^b")
        print(f"  K_B = {coeffs['K_B']}, b = {coeffs['b']}")
        print(f"水深关系: h = K_h·Q^f")
        print(f"  K_h = {coeffs['K_h']}, f = {coeffs['f']}")
        print(f"流速关系: v = K_v·Q^m")
        print(f"  K_v = {coeffs['K_v']}, m = {coeffs['m']}")
        print(f"验证连续性: b + f + m = {coeffs['sum']:.2f} ✓")
        
        print(f"\n【河相关系验证】")
        print(f"河宽计算值: B = {coeffs['K_B']}×{self.Q}^{coeffs['b']} = {validation['B_calc']:.2f} m")
        print(f"  实测值: {self.B} m")
        print(f"  相对误差: {validation['error_B']:.2f}%")
        
        print(f"\n水深计算值: h = {coeffs['K_h']}×{self.Q}^{coeffs['f']} = {validation['h_calc']:.3f} m")
        print(f"  实测值: {self.h} m")
        print(f"  相对误差: {validation['error_h']:.2f}%")
        
        print(f"\n流速计算值: v = {coeffs['K_v']}×{self.Q}^{coeffs['m']} = {validation['v_calc']:.3f} m/s")
        print(f"  实测值: {v_actual:.3f} m/s")
        print(f"  相对误差: {validation['error_v']:.2f}%")
        
        print(f"\n【河道稳定性】")
        print(f"稳定性指标: SI = (B·h)/(Q·√i)")
        print(f"           = ({self.B}×{self.h})/({self.Q}×√{self.i})")
        print(f"           = {SI:.4f}")
        
        if SI > 1.5:
            print(f"✓ SI = {SI:.3f} > 1.5，河道稳定")
        elif SI > 1.0:
            print(f"✓ SI = {SI:.3f} > 1.0，河道基本稳定")
        else:
            print(f"✗ SI = {SI:.3f} < 1.0，河道不稳定")
        
        print(f"稳定性评价: {status}")
        
        print(f"\n✓ 河相关系分析完成")
        print(f"\n{'='*70}\n")


def main():
    Q = 800
    B = 150
    h = 6
    i = 0.0003
    d50 = 0.3
    
    river = RiverRegime(Q, B, h, i, d50)
    river.print_results()
    river.plot_analysis()


if __name__ == "__main__":
    main()
