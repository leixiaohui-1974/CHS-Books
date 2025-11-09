# -*- coding: utf-8 -*-
"""
第09章 渠系水力计算 - 题1：渠道均匀流

问题描述：
    某矩形渠道，宽度b = 3m，水深h = 2m
    底坡i = 0.001
    糙率n = 0.025（混凝土衬砌）
    
    求：
    1. 过水断面面积A
    2. 湿周χ
    3. 水力半径R
    4. 流速v（Manning公式）
    5. 流量Q
    6. Froude数Fr（流态判别）
    7. 底坡影响分析

核心公式：
    1. Manning公式：v = (1/n)R^(2/3)·i^(1/2)
    2. Chézy公式：v = C·√(R·i)
    3. 流量：Q = A·v
    4. Froude数：Fr = v/√(g·hm)
    5. 水力半径：R = A/χ

考试要点：
    - Manning公式适用范围（均匀流）
    - 水力半径R的计算
    - Froude数判别流态
    - 底坡i对流速的影响
    - 糙率n的物理意义

作者: CHS-Books Team
日期: 2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class UniformFlow:
    """渠道均匀流分析"""
    
    def __init__(self, b: float, h: float, i: float, n: float):
        """
        初始化参数
        
        参数:
            b: 渠道宽度 [m]
            h: 水深 [m]
            i: 底坡（坡降）
            n: 糙率（Manning系数）
        """
        self.b = b
        self.h = h
        self.i = i
        self.n = n
        
        self.g = 9.8  # 重力加速度 [m/s²]
        
    def cross_section_area(self) -> float:
        """
        过水断面面积（矩形渠道）
        
        A = b·h
        """
        A = self.b * self.h
        return A
    
    def wetted_perimeter(self) -> float:
        """
        湿周（矩形渠道）
        
        χ = b + 2h
        """
        chi = self.b + 2 * self.h
        return chi
    
    def hydraulic_radius(self) -> float:
        """
        水力半径
        
        R = A/χ
        """
        A = self.cross_section_area()
        chi = self.wetted_perimeter()
        R = A / chi
        return R
    
    def velocity_manning(self, R: float = None, i: float = None, n: float = None) -> float:
        """
        流速（Manning公式）
        
        v = (1/n)·R^(2/3)·i^(1/2)
        
        参数:
            R: 水力半径 [m]（可选）
            i: 底坡（可选）
            n: 糙率（可选）
        """
        if R is None:
            R = self.hydraulic_radius()
        if i is None:
            i = self.i
        if n is None:
            n = self.n
        
        v = (1 / n) * (R ** (2/3)) * (i ** 0.5)
        return v
    
    def discharge(self) -> float:
        """
        流量
        
        Q = A·v
        """
        A = self.cross_section_area()
        v = self.velocity_manning()
        Q = A * v
        return Q
    
    def froude_number(self) -> float:
        """
        Froude数
        
        Fr = v/√(g·hm)
        
        hm = A/B（平均水深，矩形渠道hm=h）
        """
        v = self.velocity_manning()
        Fr = v / np.sqrt(self.g * self.h)
        return Fr
    
    def flow_regime(self) -> str:
        """
        流态判别
        
        Fr < 1: 缓流（subcritical）
        Fr = 1: 临界流（critical）
        Fr > 1: 急流（supercritical）
        """
        Fr = self.froude_number()
        
        if Fr < 1:
            return "缓流"
        elif Fr > 1:
            return "急流"
        else:
            return "临界流"
    
    def chezy_coefficient(self, R: float = None, i: float = None) -> float:
        """
        Chézy系数
        
        C = v/√(R·i) = (1/n)·R^(1/6)
        """
        if R is None:
            R = self.hydraulic_radius()
        if i is None:
            i = self.i
        
        C = (1 / self.n) * (R ** (1/6))
        return C
    
    def slope_effect(self, i_range: tuple = (0.0001, 0.01)) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        底坡影响分析
        
        参数:
            i_range: 底坡范围
        
        返回:
            i_array: 底坡数组
            v_array: 流速数组
            Q_array: 流量数组
        """
        i_array = np.linspace(i_range[0], i_range[1], 50)
        
        R = self.hydraulic_radius()
        v_array = np.array([self.velocity_manning(R, i) for i in i_array])
        
        A = self.cross_section_area()
        Q_array = A * v_array
        
        return i_array, v_array, Q_array
    
    def roughness_effect(self, n_range: tuple = (0.01, 0.05)) -> Tuple[np.ndarray, np.ndarray]:
        """
        糙率影响分析
        
        参数:
            n_range: 糙率范围
        
        返回:
            n_array: 糙率数组
            v_array: 流速数组
        """
        n_array = np.linspace(n_range[0], n_range[1], 50)
        
        R = self.hydraulic_radius()
        v_array = np.array([self.velocity_manning(R, self.i, n) for n in n_array])
        
        return n_array, v_array
    
    def plot_analysis(self):
        """绘制完整分析图表（9个子图）"""
        fig = plt.figure(figsize=(16, 12))
        
        # 计算关键参数
        A = self.cross_section_area()
        chi = self.wetted_perimeter()
        R = self.hydraulic_radius()
        v = self.velocity_manning()
        Q = self.discharge()
        Fr = self.froude_number()
        regime = self.flow_regime()
        C = self.chezy_coefficient()
        
        # 1. 渠道断面示意图
        ax1 = plt.subplot(3, 3, 1)
        
        # 渠道底部和侧壁
        x_bottom = [-0.5, self.b+0.5]
        y_bottom = [0, 0]
        ax1.plot(x_bottom, y_bottom, 'k-', linewidth=3)
        
        # 侧壁
        ax1.plot([0, 0], [0, self.h], 'k-', linewidth=3)
        ax1.plot([self.b, self.b], [0, self.h], 'k-', linewidth=3)
        
        # 水面
        ax1.fill_between([0, self.b], [0, 0], [self.h, self.h], 
                        color='lightblue', alpha=0.5, label='水体')
        ax1.plot([0, self.b], [self.h, self.h], 'b-', linewidth=2, label='水面')
        
        # 尺寸标注
        ax1.annotate('', xy=(self.b, -0.2), xytext=(0, -0.2),
                    arrowprops=dict(arrowstyle='<->', color='red', lw=1.5))
        ax1.text(self.b/2, -0.4, f'b={self.b}m', ha='center', fontsize=10,
                color='red', fontweight='bold')
        
        ax1.annotate('', xy=(self.b+0.3, self.h), xytext=(self.b+0.3, 0),
                    arrowprops=dict(arrowstyle='<->', color='red', lw=1.5))
        ax1.text(self.b+0.6, self.h/2, f'h={self.h}m', ha='left', fontsize=10,
                color='red', fontweight='bold', rotation=90, va='center')
        
        ax1.set_xlim(-0.8, self.b+1)
        ax1.set_ylim(-0.6, self.h+0.5)
        ax1.set_aspect('equal')
        ax1.set_title('渠道断面示意图', fontsize=12, fontweight='bold')
        ax1.legend(fontsize=9)
        ax1.axis('off')
        
        # 2. Manning公式计算流程
        ax2 = plt.subplot(3, 3, 2)
        ax2.axis('off')
        
        steps = [
            '【Manning公式计算】',
            '',
            '① 断面几何',
            f'面积: A = b·h = {self.b}×{self.h} = {A:.2f} m²',
            f'湿周: χ = b+2h = {self.b}+2×{self.h} = {chi:.2f} m',
            f'水力半径: R = A/χ = {A:.2f}/{chi:.2f} = {R:.3f} m',
            '',
            '② Manning公式',
            'v = (1/n)·R^(2/3)·i^(1/2)',
            f'  = (1/{self.n})×{R:.3f}^(2/3)×{self.i}^(1/2)',
            f'  = {v:.4f} m/s',
            '',
            '③ 流量',
            'Q = A·v',
            f'  = {A:.2f}×{v:.4f}',
            f'  = {Q:.4f} m³/s',
            '',
            '④ Froude数',
            'Fr = v/√(g·h)',
            f'   = {v:.4f}/√({self.g}×{self.h})',
            f'   = {Fr:.3f}',
            f'流态: {regime}',
        ]
        
        y_pos = 0.98
        for line in steps:
            if '【' in line:
                ax2.text(0.5, y_pos, line, fontsize=11, fontweight='bold',
                        horizontalalignment='center', verticalalignment='top',
                        color='darkblue')
            elif line.startswith('①') or line.startswith('②') or line.startswith('③') or line.startswith('④'):
                ax2.text(0.05, y_pos, line, fontsize=10, fontweight='bold',
                        verticalalignment='top', color='darkred')
            elif '流态' in line:
                ax2.text(0.05, y_pos, line, fontsize=10, fontweight='bold',
                        verticalalignment='top', color='darkgreen')
            elif line == '':
                y_pos -= 0.01
                continue
            else:
                ax2.text(0.1, y_pos, line, fontsize=9, verticalalignment='top',
                        family='monospace')
            y_pos -= 0.028
        
        ax2.set_title('计算流程', fontsize=12, fontweight='bold')
        
        # 3. 参数对比
        ax3 = plt.subplot(3, 3, 3)
        
        params = ['A\n(m²)', 'χ\n(m)', 'R\n(m)', 'v\n(m/s)', 'Q\n(m³/s)']
        values = [A, chi, R, v, Q]
        colors = ['lightblue', 'lightgreen', 'lightyellow', 'lightcoral', 'plum']
        
        bars = ax3.bar(params, values, color=colors, alpha=0.7, edgecolor='black')
        ax3.set_ylabel('数值', fontsize=11)
        ax3.set_title('关键参数对比', fontsize=12, fontweight='bold')
        ax3.grid(True, alpha=0.3, axis='y')
        
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2, height,
                    f'{val:.3f}', ha='center', va='bottom',
                    fontsize=9, fontweight='bold')
        
        # 4. 底坡影响
        ax4 = plt.subplot(3, 3, 4)
        
        i_arr, v_arr, Q_arr = self.slope_effect()
        
        ax4_twin = ax4.twinx()
        
        line1 = ax4.plot(i_arr*1000, v_arr, 'b-', linewidth=2, label='流速v')
        line2 = ax4_twin.plot(i_arr*1000, Q_arr, 'r-', linewidth=2, label='流量Q')
        
        # 当前点
        ax4.plot(self.i*1000, v, 'bo', markersize=10)
        ax4_twin.plot(self.i*1000, Q, 'ro', markersize=10, label='当前工况')
        
        ax4.set_xlabel('底坡 i (‰)', fontsize=11)
        ax4.set_ylabel('流速 v (m/s)', fontsize=11, color='b')
        ax4_twin.set_ylabel('流量 Q (m³/s)', fontsize=11, color='r')
        ax4.set_title('底坡i的影响 (v∝√i)', fontsize=12, fontweight='bold')
        ax4.tick_params(axis='y', labelcolor='b')
        ax4_twin.tick_params(axis='y', labelcolor='r')
        ax4.grid(True, alpha=0.3)
        
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax4.legend(lines, labels, fontsize=9, loc='upper left')
        
        # 5. 糙率影响
        ax5 = plt.subplot(3, 3, 5)
        
        n_arr, v_n = self.roughness_effect()
        
        ax5.plot(n_arr*1000, v_n, 'g-', linewidth=2, label='流速v')
        
        # 当前点
        ax5.plot(self.n*1000, v, 'ro', markersize=12, label=f'当前n={self.n}')
        
        ax5.set_xlabel('糙率 n (×10⁻³)', fontsize=11)
        ax5.set_ylabel('流速 v (m/s)', fontsize=11)
        ax5.set_title('糙率n的影响 (v∝1/n)', fontsize=12, fontweight='bold')
        ax5.legend(fontsize=9)
        ax5.grid(True, alpha=0.3)
        
        # 6. Froude数与流态
        ax6 = plt.subplot(3, 3, 6)
        
        # 不同流速的Fr
        v_range = np.linspace(0.5, 3, 50)
        Fr_range = v_range / np.sqrt(self.g * self.h)
        
        ax6.plot(v_range, Fr_range, 'b-', linewidth=2)
        
        # 当前点
        ax6.plot(v, Fr, 'ro', markersize=12, label=f'当前Fr={Fr:.2f}')
        
        # 临界线
        ax6.axhline(1, color='r', linestyle='--', linewidth=2, label='Fr=1（临界）')
        
        # 流态区域
        ax6.fill_between(v_range, 0, 1, where=(Fr_range < 1), alpha=0.2, color='blue', label='缓流区')
        ax6.fill_between(v_range, 1, 2, where=(Fr_range > 1), alpha=0.2, color='red', label='急流区')
        
        ax6.set_xlabel('流速 v (m/s)', fontsize=11)
        ax6.set_ylabel('Froude数 Fr', fontsize=11)
        ax6.set_title('Froude数与流态', fontsize=12, fontweight='bold')
        ax6.legend(fontsize=9)
        ax6.grid(True, alpha=0.3)
        
        # 7. 不同糙率材料对比
        ax7 = plt.subplot(3, 3, 7)
        
        materials = ['光滑混凝土\n0.012', '一般混凝土\n0.014', '粗糙混凝土\n0.017',
                    '衬砌渠道\n0.025', '土质渠道\n0.030', '草皮渠道\n0.040']
        n_values = [0.012, 0.014, 0.017, 0.025, 0.030, 0.040]
        v_materials = [self.velocity_manning(R, self.i, n) for n in n_values]
        
        colors_mat = ['lightgreen', 'lightblue', 'lightyellow', 'lightcoral', 'plum', 'wheat']
        bars = ax7.barh(materials, v_materials, color=colors_mat, alpha=0.7, edgecolor='black')
        
        # 标注当前
        current_idx = np.argmin(np.abs(np.array(n_values) - self.n))
        bars[current_idx].set_edgecolor('red')
        bars[current_idx].set_linewidth(3)
        
        ax7.set_xlabel('流速 v (m/s)', fontsize=11)
        ax7.set_title('不同糙率材料对比', fontsize=12, fontweight='bold')
        ax7.grid(True, alpha=0.3, axis='x')
        
        for bar, v_val in zip(bars, v_materials):
            width = bar.get_width()
            ax7.text(width, bar.get_y() + bar.get_height()/2,
                    f'{v_val:.3f}', va='center', ha='left',
                    fontsize=8, fontweight='bold')
        
        # 8. Manning vs Chézy
        ax8 = plt.subplot(3, 3, 8)
        ax8.axis('off')
        
        comparison = [
            '【Manning vs Chézy】',
            '',
            'Manning公式:',
            'v = (1/n)·R^(2/3)·i^(1/2)',
            f'n = {self.n}（糙率）',
            f'v = {v:.4f} m/s',
            '',
            'Chézy公式:',
            'v = C·√(R·i)',
            f'C = (1/n)·R^(1/6) = {C:.2f}',
            f'v = {C:.2f}×√({R:.3f}×{self.i})',
            f'v = {v:.4f} m/s',
            '',
            '关系:',
            'C = (1/n)·R^(1/6)',
            'Manning更常用（n易查）',
            'Chézy理论性强',
            '',
            '适用条件:',
            '• 均匀流',
            '• 恒定流',
            '• 阻力平方区',
        ]
        
        y_pos = 0.98
        for line in comparison:
            if '【' in line:
                ax8.text(0.5, y_pos, line, fontsize=11, fontweight='bold',
                        horizontalalignment='center', verticalalignment='top',
                        color='darkblue')
            elif line.endswith('公式:') or line.endswith('系:') or line.endswith('条件:'):
                ax8.text(0.05, y_pos, line, fontsize=10, fontweight='bold',
                        verticalalignment='top', color='darkred')
            elif line.startswith('•'):
                ax8.text(0.1, y_pos, line, fontsize=9, verticalalignment='top')
            elif line == '':
                y_pos -= 0.01
                continue
            else:
                ax8.text(0.1, y_pos, line, fontsize=9, verticalalignment='top',
                        family='monospace')
            y_pos -= 0.032
        
        ax8.set_title('公式对比', fontsize=12, fontweight='bold')
        
        # 9. 结果汇总
        ax9 = plt.subplot(3, 3, 9)
        ax9.axis('off')
        
        summary = [
            '═══ 均匀流计算结果 ═══',
            '',
            '【渠道参数】',
            f'宽度: b = {self.b} m',
            f'水深: h = {self.h} m',
            f'底坡: i = {self.i} = {self.i*1000}‰',
            f'糙率: n = {self.n}',
            '',
            '【计算结果】',
            f'面积: A = {A:.3f} m²',
            f'湿周: χ = {chi:.3f} m',
            f'水力半径: R = {R:.3f} m',
            f'流速: v = {v:.4f} m/s',
            f'流量: Q = {Q:.4f} m³/s',
            '',
            '【流态判别】',
            f'Froude数: Fr = {Fr:.3f}',
            f'流态: {regime}',
            f'(Fr<1缓流, Fr>1急流)',
            '',
            '【Chézy系数】',
            f'C = {C:.2f}',
        ]
        
        y_pos = 0.98
        for line in summary:
            if '═══' in line:
                ax9.text(0.5, y_pos, line, fontsize=11, fontweight='bold',
                        horizontalalignment='center', verticalalignment='top',
                        color='darkblue')
            elif '【' in line:
                ax9.text(0.05, y_pos, line, fontsize=10, fontweight='bold',
                        verticalalignment='top', color='darkred')
            elif line == '':
                y_pos -= 0.01
                continue
            else:
                ax9.text(0.1, y_pos, line, fontsize=9, verticalalignment='top',
                        family='monospace')
            y_pos -= 0.032
        
        ax9.set_title('结果汇总', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('/tmp/ch09_problem01_uniform_flow.png', dpi=150, bbox_inches='tight')
        print(f"图表已保存: /tmp/ch09_problem01_uniform_flow.png")
        plt.show()
    
    def print_results(self):
        """打印计算结果"""
        print("\n" + "="*70)
        print("第09章 渠系水力计算 - 题1：渠道均匀流")
        print("="*70)
        
        # 基本参数
        print(f"\n【已知条件】")
        print(f"渠道类型: 矩形渠道")
        print(f"渠底宽度: b = {self.b} m")
        print(f"水深: h = {self.h} m")
        print(f"底坡: i = {self.i} = {self.i*1000}‰")
        print(f"糙率: n = {self.n}")
        
        # (1) 断面几何参数
        print(f"\n【问题1】过水断面面积")
        
        A = self.cross_section_area()
        
        print(f"\n矩形断面面积:")
        print(f"A = b·h")
        print(f"  = {self.b} × {self.h}")
        print(f"  = {A} m²")
        
        print(f"\n✓ 过水断面面积: A = {A} m²")
        
        # (2) 湿周
        print(f"\n【问题2】湿周")
        
        chi = self.wetted_perimeter()
        
        print(f"\n矩形断面湿周:")
        print(f"χ = b + 2h")
        print(f"  = {self.b} + 2×{self.h}")
        print(f"  = {chi} m")
        
        print(f"\n物理意义:")
        print(f"• 水流与固体边界接触的周长")
        print(f"• 产生阻力的边界长度")
        
        print(f"\n✓ 湿周: χ = {chi} m")
        
        # (3) 水力半径
        print(f"\n【问题3】水力半径")
        
        R = self.hydraulic_radius()
        
        print(f"\n水力半径定义:")
        print(f"R = A/χ")
        print(f"  = {A}/{chi}")
        print(f"  = {R:.4f} m")
        
        print(f"\n物理意义:")
        print(f"• 单位湿周的过水面积")
        print(f"• 水力效率的度量")
        print(f"• R越大，阻力越小")
        
        print(f"\n✓ 水力半径: R = {R:.4f} m")
        
        # (4) 流速
        print(f"\n【问题4】流速（Manning公式）")
        
        v = self.velocity_manning()
        
        print(f"\nManning公式:")
        print(f"v = (1/n)·R^(2/3)·i^(1/2)")
        
        print(f"\n代入数值:")
        print(f"v = (1/{self.n}) × {R:.4f}^(2/3) × {self.i}^(1/2)")
        print(f"  = {1/self.n:.2f} × {R**(2/3):.4f} × {self.i**0.5:.4f}")
        print(f"  = {v:.4f} m/s")
        
        print(f"\n公式特点:")
        print(f"• v ∝ R^(2/3)：R增大，v增大")
        print(f"• v ∝ √i：i增大，v增大")
        print(f"• v ∝ 1/n：n增大，v减小")
        
        print(f"\n✓ 流速: v = {v:.4f} m/s")
        
        # (5) 流量
        print(f"\n【问题5】流量")
        
        Q = self.discharge()
        
        print(f"\n流量公式:")
        print(f"Q = A·v")
        print(f"  = {A} × {v:.4f}")
        print(f"  = {Q:.4f} m³/s")
        
        print(f"\n单位换算:")
        print(f"Q = {Q:.4f} m³/s")
        print(f"  = {Q*1000:.2f} L/s")
        print(f"  = {Q*3600:.1f} m³/h")
        
        print(f"\n✓ 流量: Q = {Q:.4f} m³/s = {Q*1000:.2f} L/s")
        
        # (6) Froude数
        print(f"\n【问题6】Froude数与流态判别")
        
        Fr = self.froude_number()
        regime = self.flow_regime()
        
        print(f"\nFroude数定义:")
        print(f"Fr = v/√(g·h)")
        print(f"   = {v:.4f}/√({self.g}×{self.h})")
        print(f"   = {v:.4f}/{np.sqrt(self.g*self.h):.4f}")
        print(f"   = {Fr:.4f}")
        
        print(f"\n流态判别标准:")
        print(f"• Fr < 1：缓流（subcritical flow）")
        print(f"  - 重力作用占优")
        print(f"  - 扰动可向上游传播")
        print(f"  - 水面平稳")
        print(f"• Fr = 1：临界流（critical flow）")
        print(f"  - 临界状态")
        print(f"  - 能量最小")
        print(f"• Fr > 1：急流（supercritical flow）")
        print(f"  - 惯性力占优")
        print(f"  - 扰动不能上传")
        print(f"  - 水面波动")
        
        print(f"\n计算结果:")
        print(f"Fr = {Fr:.4f} {'<' if Fr < 1 else ('>' if Fr > 1 else '=')} 1")
        print(f"流态: {regime}")
        
        print(f"\n✓ Froude数: Fr = {Fr:.4f}, 流态: {regime}")
        
        # (7) 底坡影响
        print(f"\n【问题7】底坡影响分析")
        
        print(f"\n影响规律:")
        print(f"• v = (1/n)·R^(2/3)·i^(1/2)")
        print(f"• v ∝ √i")
        print(f"• i增大，v增大，但不是线性关系")
        
        i_test = [0.0001, 0.0005, 0.001, 0.005, 0.01]
        print(f"\n不同底坡下的流速:")
        print(f"{'底坡i':<12} {'i(‰)':<10} {'流速v(m/s)':<15} {'流量Q(m³/s)':<15}")
        print(f"{'-'*55}")
        
        for i_val in i_test:
            v_val = self.velocity_manning(R, i_val)
            Q_val = A * v_val
            marker = ' ◀' if i_val == self.i else ''
            print(f"{i_val:<12} {i_val*1000:<10.2f} {v_val:<15.4f} {Q_val:<15.4f}{marker}")
        
        print(f"\n分析:")
        print(f"• 底坡从0.1‰增到10‰")
        print(f"• 流速从{self.velocity_manning(R, 0.0001):.4f}增到{self.velocity_manning(R, 0.01):.4f}m/s")
        print(f"• 增大约{(self.velocity_manning(R, 0.01)/self.velocity_manning(R, 0.0001)):.1f}倍")
        
        # Chézy公式
        print(f"\n【Chézy公式】")
        
        C = self.chezy_coefficient()
        
        print(f"\nChézy系数:")
        print(f"C = (1/n)·R^(1/6)")
        print(f"  = (1/{self.n}) × {R:.4f}^(1/6)")
        print(f"  = {C:.2f}")
        
        print(f"\nChézy公式:")
        print(f"v = C·√(R·i)")
        print(f"  = {C:.2f}×√({R:.4f}×{self.i})")
        print(f"  = {v:.4f} m/s")
        
        print(f"\n与Manning一致 ✓")
        
        # 考试要点
        print(f"\n【考试要点】")
        print(f"1. Manning公式: v = (1/n)·R^(2/3)·i^(1/2)")
        print(f"2. 水力半径: R = A/χ")
        print(f"3. 流量: Q = A·v")
        print(f"4. Froude数: Fr = v/√(g·h)")
        print(f"5. 流态: Fr<1缓流, Fr>1急流")
        print(f"6. v ∝ √i, v ∝ R^(2/3), v ∝ 1/n")
        print(f"7. 均匀流条件: 底坡=水面坡=能坡")
        print(f"8. 糙率n: 反映边界粗糙程度")
        
        print(f"\n{'='*70}\n")


def main():
    """主函数"""
    
    print("渠道均匀流分析")
    print("-" * 70)
    
    # 系统参数
    b = 3  # 渠道宽度 [m]
    h = 2  # 水深 [m]
    i = 0.001  # 底坡
    n = 0.025  # 糙率（混凝土衬砌）
    
    # 创建分析实例
    uf = UniformFlow(b, h, i, n)
    
    # 打印结果
    uf.print_results()
    
    # 绘制分析图
    uf.plot_analysis()


if __name__ == "__main__":
    main()
