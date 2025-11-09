# -*- coding: utf-8 -*-
"""
第07章 地下水动力学 - 题1：达西定律与渗流分析

问题描述：
    某砂土层，渗透系数K = 0.02 m/s
    土层厚度：M = 5m
    测压管间距：L = 100m
    上游水位：H1 = 10m
    下游水位：H2 = 6m
    
    求：
    1. 水力坡度
    2. 渗流速度
    3. 实际流速
    4. 单宽流量
    5. 渗透系数影响分析
    6. 水力坡度影响分析

核心公式：
    1. 达西定律：v = K·I
    2. 水力坡度：I = (H1 - H2) / L
    3. 单宽流量：q = K·I·M
    4. 实际流速：u = v/n（n为孔隙率）

考试要点：
    - 达西定律适用范围（层流）
    - 水力坡度与测压管水头
    - 渗透系数物理意义
    - 渗流速度vs实际流速

作者: CHS-Books Team
日期: 2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class DarcyLaw:
    """达西定律与渗流分析"""
    
    def __init__(self, K: float, M: float, L: float, H1: float, H2: float, n: float = 0.3):
        """
        初始化参数
        
        参数:
            K: 渗透系数 [m/s]
            M: 土层厚度 [m]
            L: 测压管间距 [m]
            H1: 上游水位 [m]
            H2: 下游水位 [m]
            n: 孔隙率（默认0.3）
        """
        self.K = K
        self.M = M
        self.L = L
        self.H1 = H1
        self.H2 = H2
        self.n = n
        
        self.rho = 1000  # 水密度 [kg/m³]
        self.g = 9.8  # 重力加速度 [m/s²]
        
    def hydraulic_gradient(self) -> float:
        """
        水力坡度
        
        I = (H1 - H2) / L
        """
        I = (self.H1 - self.H2) / self.L
        return I
    
    def seepage_velocity(self, I: float = None) -> float:
        """
        渗流速度（达西速度）
        
        v = K·I
        """
        if I is None:
            I = self.hydraulic_gradient()
        
        v = self.K * I
        return v
    
    def actual_velocity(self, v: float = None) -> float:
        """
        实际流速
        
        u = v/n
        """
        if v is None:
            v = self.seepage_velocity()
        
        u = v / self.n
        return u
    
    def unit_discharge(self, I: float = None) -> float:
        """
        单宽流量
        
        q = K·I·M
        """
        if I is None:
            I = self.hydraulic_gradient()
        
        q = self.K * I * self.M
        return q
    
    def total_discharge(self, B: float) -> float:
        """
        总流量
        
        Q = q·B
        
        参数:
            B: 宽度 [m]
        """
        q = self.unit_discharge()
        Q = q * B
        return Q
    
    def reynolds_number(self, v: float = None, d: float = 0.001) -> float:
        """
        雷诺数（判断流态）
        
        Re = v·d/ν
        
        参数:
            v: 渗流速度 [m/s]
            d: 特征粒径 [m]（默认1mm）
        """
        if v is None:
            v = self.seepage_velocity()
        
        nu = 1e-6  # 运动粘度 [m²/s]（20°C水）
        Re = v * d / nu
        return Re
    
    def permeability_effect(self, K_range: tuple = (0.001, 0.1)) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        渗透系数影响分析
        
        参数:
            K_range: 渗透系数范围 [m/s]
        
        返回:
            K_array: 渗透系数数组
            v_array: 渗流速度数组
            q_array: 单宽流量数组
        """
        K_array = np.linspace(K_range[0], K_range[1], 50)
        
        I = self.hydraulic_gradient()
        v_array = K_array * I
        q_array = K_array * I * self.M
        
        return K_array, v_array, q_array
    
    def gradient_effect(self, H1_range: tuple = (8, 15)) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        水力坡度影响分析
        
        参数:
            H1_range: 上游水位范围 [m]
        
        返回:
            H1_array: 上游水位数组
            I_array: 水力坡度数组
            v_array: 渗流速度数组
            q_array: 单宽流量数组
        """
        H1_array = np.linspace(H1_range[0], H1_range[1], 50)
        
        I_array = (H1_array - self.H2) / self.L
        v_array = self.K * I_array
        q_array = self.K * I_array * self.M
        
        return H1_array, I_array, v_array, q_array
    
    def water_head_profile(self, n_points: int = 50) -> Tuple[np.ndarray, np.ndarray]:
        """
        测压管水头线
        
        返回:
            x_array: 距离数组
            H_array: 水头数组
        """
        x_array = np.linspace(0, self.L, n_points)
        
        I = self.hydraulic_gradient()
        H_array = self.H1 - I * x_array
        
        return x_array, H_array
    
    def plot_analysis(self):
        """绘制完整分析图表（9个子图）"""
        fig = plt.figure(figsize=(16, 12))
        
        # 计算关键参数
        I = self.hydraulic_gradient()
        v = self.seepage_velocity()
        u = self.actual_velocity()
        q = self.unit_discharge()
        Re = self.reynolds_number()
        
        # 1. 渗流示意图
        ax1 = plt.subplot(3, 3, 1)
        ax1.axis('off')
        
        # 土层
        ax1.fill_between([0, 4], [0, 0], [self.M, self.M], color='wheat', alpha=0.5, label='土层')
        
        # 测压管
        # 上游
        ax1.plot([0.5, 0.5], [0, self.H1], 'b-', linewidth=3)
        ax1.plot([0.5, 0.5], [self.M, self.H1], 'b--', linewidth=2)
        ax1.fill_between([0.3, 0.7], [self.M, self.M], [self.H1, self.H1], color='lightblue', alpha=0.5)
        ax1.text(0.5, self.H1+0.3, f'H₁={self.H1}m', ha='center', fontsize=10, fontweight='bold')
        
        # 下游
        ax1.plot([3.5, 3.5], [0, self.H2], 'b-', linewidth=3)
        ax1.plot([3.5, 3.5], [self.M, self.H2], 'b--', linewidth=2)
        ax1.fill_between([3.3, 3.7], [self.M, self.M], [self.H2, self.H2], color='lightblue', alpha=0.5)
        ax1.text(3.5, self.H2+0.3, f'H₂={self.H2}m', ha='center', fontsize=10, fontweight='bold')
        
        # 水头线
        ax1.plot([0.5, 3.5], [self.H1, self.H2], 'r--', linewidth=2, label='水头线')
        
        # 渗流方向
        for i in range(1, 4):
            x = i
            y = self.M / 2
            ax1.arrow(x-0.2, y, 0.3, 0, head_width=0.3, head_length=0.1, fc='red', ec='red')
        
        # 尺寸标注
        ax1.plot([0, 4], [-0.5, -0.5], 'k-', linewidth=1)
        ax1.plot([0, 0], [-0.3, -0.7], 'k-', linewidth=1)
        ax1.plot([4, 4], [-0.3, -0.7], 'k-', linewidth=1)
        ax1.text(2, -1, f'L={self.L}m', ha='center', fontsize=10)
        
        ax1.plot([-0.3, -0.3], [0, self.M], 'k-', linewidth=1)
        ax1.plot([-0.1, -0.5], [0, 0], 'k-', linewidth=1)
        ax1.plot([-0.1, -0.5], [self.M, self.M], 'k-', linewidth=1)
        ax1.text(-0.8, self.M/2, f'M={self.M}m', ha='center', fontsize=10, rotation=90)
        
        ax1.set_xlim(-1.5, 5)
        ax1.set_ylim(-2, 12)
        ax1.set_aspect('equal')
        ax1.set_title('渗流示意图', fontsize=12, fontweight='bold')
        ax1.legend(fontsize=9, loc='upper right')
        
        # 2. 达西定律计算流程
        ax2 = plt.subplot(3, 3, 2)
        ax2.axis('off')
        
        steps = [
            '【达西定律计算流程】',
            '',
            '① 水力坡度',
            f'I = (H₁-H₂)/L',
            f'  = ({self.H1}-{self.H2})/{self.L}',
            f'  = {I:.6f}',
            '',
            '② 渗流速度（达西速度）',
            f'v = K·I',
            f'  = {self.K}×{I:.6f}',
            f'  = {v:.6f} m/s',
            f'  = {v*86400:.2f} m/d',
            '',
            '③ 实际流速',
            f'u = v/n',
            f'  = {v:.6f}/{self.n}',
            f'  = {u:.6f} m/s',
            '',
            '④ 单宽流量',
            f'q = K·I·M',
            f'  = {self.K}×{I:.6f}×{self.M}',
            f'  = {q:.6f} m²/s',
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
            elif line == '':
                y_pos -= 0.01
                continue
            else:
                ax2.text(0.1, y_pos, line, fontsize=9, verticalalignment='top',
                        family='monospace')
            y_pos -= 0.038
        
        ax2.set_title('计算流程', fontsize=12, fontweight='bold')
        
        # 3. 测压管水头线
        ax3 = plt.subplot(3, 3, 3)
        
        x_arr, H_arr = self.water_head_profile()
        
        ax3.plot(x_arr, H_arr, 'r-', linewidth=2, label='测压管水头线')
        ax3.plot([0, self.L], [self.H1, self.H1], 'b--', alpha=0.5, label=f'上游H₁={self.H1}m')
        ax3.plot([0, self.L], [self.H2, self.H2], 'g--', alpha=0.5, label=f'下游H₂={self.H2}m')
        
        # 标注水头降
        ax3.annotate('', xy=(self.L, self.H2), xytext=(self.L, self.H1),
                    arrowprops=dict(arrowstyle='<->', color='red', lw=2))
        ax3.text(self.L+5, (self.H1+self.H2)/2, f'ΔH={self.H1-self.H2}m',
                fontsize=10, color='red', fontweight='bold')
        
        ax3.set_xlabel('距离 x (m)', fontsize=11)
        ax3.set_ylabel('测压管水头 H (m)', fontsize=11)
        ax3.set_title('测压管水头线', fontsize=12, fontweight='bold')
        ax3.legend(fontsize=9)
        ax3.grid(True, alpha=0.3)
        
        # 4. 参数对比柱状图
        ax4 = plt.subplot(3, 3, 4)
        
        params = ['水力坡度\nI', '渗流速度\nv (×10⁴m/s)', '实际流速\nu (×10⁴m/s)', '单宽流量\nq (×10⁴m²/s)']
        values = [I*100, v*1e4, u*1e4, q*1e4]  # 归一化显示
        colors = ['lightcoral', 'lightblue', 'lightgreen', 'lightyellow']
        
        bars = ax4.bar(params, values, color=colors, alpha=0.7, edgecolor='black')
        ax4.set_ylabel('数值', fontsize=11)
        ax4.set_title('关键参数对比', fontsize=12, fontweight='bold')
        ax4.grid(True, alpha=0.3, axis='y')
        
        for bar, val, param in zip(bars, values, params):
            height = bar.get_height()
            if 'I' in param:
                text = f'{I:.6f}'
            elif 'v' in param and 'u' not in param:
                text = f'{v:.6f}m/s'
            elif 'u' in param:
                text = f'{u:.6f}m/s'
            else:
                text = f'{q:.6f}m²/s'
            ax4.text(bar.get_x() + bar.get_width()/2, height,
                    text, ha='center', va='bottom', fontsize=8, fontweight='bold')
        
        # 5. 渗透系数影响
        ax5 = plt.subplot(3, 3, 5)
        
        K_arr, v_arr, q_arr = self.permeability_effect()
        
        ax5_twin = ax5.twinx()
        
        line1 = ax5.plot(K_arr*1000, v_arr*1000, 'b-', linewidth=2, label='渗流速度v')
        line2 = ax5_twin.plot(K_arr*1000, q_arr*1000, 'r-', linewidth=2, label='单宽流量q')
        
        # 当前点
        ax5.plot(self.K*1000, v*1000, 'bo', markersize=10, label='当前工况')
        ax5_twin.plot(self.K*1000, q*1000, 'ro', markersize=10)
        
        ax5.set_xlabel('渗透系数 K (mm/s)', fontsize=11)
        ax5.set_ylabel('渗流速度 v (mm/s)', fontsize=11, color='b')
        ax5_twin.set_ylabel('单宽流量 q (mm²/s)', fontsize=11, color='r')
        ax5.set_title('渗透系数影响', fontsize=12, fontweight='bold')
        ax5.tick_params(axis='y', labelcolor='b')
        ax5_twin.tick_params(axis='y', labelcolor='r')
        ax5.grid(True, alpha=0.3)
        
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax5.legend(lines, labels, fontsize=9, loc='upper left')
        
        # 6. 水力坡度影响
        ax6 = plt.subplot(3, 3, 6)
        
        H1_arr, I_arr, v_arr2, q_arr2 = self.gradient_effect()
        
        ax6_twin = ax6.twinx()
        
        line1 = ax6.plot(H1_arr, I_arr, 'g-', linewidth=2, label='水力坡度I')
        line2 = ax6_twin.plot(H1_arr, q_arr2*1000, 'r-', linewidth=2, label='单宽流量q')
        
        # 当前点
        ax6.plot(self.H1, I, 'go', markersize=10)
        ax6_twin.plot(self.H1, q*1000, 'ro', markersize=10, label='当前工况')
        
        ax6.set_xlabel('上游水位 H₁ (m)', fontsize=11)
        ax6.set_ylabel('水力坡度 I', fontsize=11, color='g')
        ax6_twin.set_ylabel('单宽流量 q (mm²/s)', fontsize=11, color='r')
        ax6.set_title('水力坡度影响', fontsize=12, fontweight='bold')
        ax6.tick_params(axis='y', labelcolor='g')
        ax6_twin.tick_params(axis='y', labelcolor='r')
        ax6.grid(True, alpha=0.3)
        
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax6.legend(lines, labels, fontsize=9, loc='upper left')
        
        # 7. 流态判别（雷诺数）
        ax7 = plt.subplot(3, 3, 7)
        
        # 不同粒径的雷诺数
        d_array = np.array([0.0001, 0.0005, 0.001, 0.002, 0.005, 0.01])  # m
        Re_array = np.array([self.reynolds_number(d=d) for d in d_array])
        
        bars = ax7.bar(range(len(d_array)), Re_array, color='lightblue', alpha=0.7, edgecolor='black')
        
        # 临界雷诺数线
        ax7.axhline(1, color='r', linestyle='--', linewidth=2, label='Re=1 (层流临界)')
        ax7.axhline(10, color='orange', linestyle='--', linewidth=2, label='Re=10 (过渡流)')
        
        ax7.set_xticks(range(len(d_array)))
        ax7.set_xticklabels([f'{d*1000:.1f}' for d in d_array])
        ax7.set_xlabel('特征粒径 d (mm)', fontsize=11)
        ax7.set_ylabel('雷诺数 Re', fontsize=11)
        ax7.set_title('流态判别（达西定律适用范围）', fontsize=12, fontweight='bold')
        ax7.legend(fontsize=9)
        ax7.grid(True, alpha=0.3, axis='y')
        ax7.set_yscale('log')
        
        for bar, val in zip(bars, Re_array):
            height = bar.get_height()
            ax7.text(bar.get_x() + bar.get_width()/2, height,
                    f'{val:.2f}', ha='center', va='bottom', fontsize=8)
        
        # 8. 速度对比
        ax8 = plt.subplot(3, 3, 8)
        
        velocities = ['渗流速度\nv', '实际流速\nu']
        v_values = [v*1000, u*1000]  # mm/s
        v_colors = ['lightblue', 'lightgreen']
        
        bars = ax8.bar(velocities, v_values, color=v_colors, alpha=0.7, edgecolor='black')
        ax8.set_ylabel('速度 (mm/s)', fontsize=11)
        ax8.set_title('渗流速度 vs 实际流速', fontsize=12, fontweight='bold')
        ax8.grid(True, alpha=0.3, axis='y')
        
        for bar, val in zip(bars, v_values):
            height = bar.get_height()
            ax8.text(bar.get_x() + bar.get_width()/2, height,
                    f'{val:.4f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        # 标注关系
        ax8.text(0.5, max(v_values)*0.5, f'u = v/n\n= v/{self.n}\n= {u/v:.2f}v',
                ha='center', fontsize=10, color='red', fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))
        
        # 9. 结果汇总
        ax9 = plt.subplot(3, 3, 9)
        ax9.axis('off')
        
        summary = [
            '═══ 达西定律计算结果 ═══',
            '',
            '【基本参数】',
            f'渗透系数: K = {self.K} m/s',
            f'           = {self.K*86400:.2f} m/d',
            f'土层厚度: M = {self.M} m',
            f'测压管间距: L = {self.L} m',
            f'上游水位: H₁ = {self.H1} m',
            f'下游水位: H₂ = {self.H2} m',
            f'孔隙率: n = {self.n}',
            '',
            '【计算结果】',
            f'水力坡度: I = {I:.6f}',
            f'渗流速度: v = {v:.6f} m/s',
            f'           = {v*1000:.4f} mm/s',
            f'           = {v*86400:.2f} m/d',
            f'实际流速: u = {u:.6f} m/s',
            f'           = {u*1000:.4f} mm/s',
            f'单宽流量: q = {q:.6f} m²/s',
            '',
            '【流态判别】',
            f'雷诺数: Re = {Re:.2f} (d=1mm)',
            f'流态: {"层流" if Re < 1 else "过渡流" if Re < 10 else "紊流"}',
            f'达西定律: {"适用" if Re < 1 else "近似适用" if Re < 10 else "不适用"}',
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
        plt.savefig('/tmp/ch07_problem01_darcy_law.png', dpi=150, bbox_inches='tight')
        print(f"图表已保存: /tmp/ch07_problem01_darcy_law.png")
        plt.show()
    
    def print_results(self):
        """打印计算结果"""
        print("\n" + "="*70)
        print("第07章 地下水动力学 - 题1：达西定律与渗流分析")
        print("="*70)
        
        # 基本参数
        print(f"\n【已知条件】")
        print(f"渗透系数: K = {self.K} m/s = {self.K*86400:.2f} m/d")
        print(f"土层厚度: M = {self.M} m")
        print(f"测压管间距: L = {self.L} m")
        print(f"上游水位: H₁ = {self.H1} m")
        print(f"下游水位: H₂ = {self.H2} m")
        print(f"孔隙率: n = {self.n}")
        
        # (1) 水力坡度
        print(f"\n【问题1】水力坡度")
        
        I = self.hydraulic_gradient()
        
        print(f"\n水力坡度定义:")
        print(f"I = (H₁ - H₂) / L")
        print(f"  = ({self.H1} - {self.H2}) / {self.L}")
        print(f"  = {self.H1 - self.H2} / {self.L}")
        print(f"  = {I:.6f}")
        
        print(f"\n物理意义:")
        print(f"• 单位长度上的水头损失")
        print(f"• 驱动渗流的动力")
        print(f"• I = {I:.6f} 表示每米长度水头损失{I:.6f}m")
        
        print(f"\n✓ 水力坡度: I = {I:.6f}")
        
        # (2) 渗流速度
        print(f"\n【问题2】渗流速度（达西速度）")
        
        v = self.seepage_velocity()
        
        print(f"\n达西定律:")
        print(f"v = K·I")
        print(f"  = {self.K} × {I:.6f}")
        print(f"  = {v:.6f} m/s")
        print(f"  = {v*1000:.4f} mm/s")
        print(f"  = {v*86400:.2f} m/d")
        
        print(f"\n物理意义:")
        print(f"• 渗流速度（达西速度）")
        print(f"• 是假想速度，假设水充满整个截面")
        print(f"• 实际水只通过孔隙流动")
        
        print(f"\n✓ 渗流速度: v = {v:.6f} m/s = {v*86400:.2f} m/d")
        
        # (3) 实际流速
        print(f"\n【问题3】实际流速")
        
        u = self.actual_velocity()
        
        print(f"\n实际流速公式:")
        print(f"u = v / n")
        print(f"  = {v:.6f} / {self.n}")
        print(f"  = {u:.6f} m/s")
        print(f"  = {u*1000:.4f} mm/s")
        
        print(f"\n渗流速度与实际流速关系:")
        print(f"u = v/n = {u/v:.2f}v")
        print(f"实际流速是渗流速度的{u/v:.2f}倍")
        
        print(f"\n✓ 实际流速: u = {u:.6f} m/s")
        
        # (4) 单宽流量
        print(f"\n【问题4】单宽流量")
        
        q = self.unit_discharge()
        
        print(f"\n单宽流量公式:")
        print(f"q = K·I·M")
        print(f"  = {self.K} × {I:.6f} × {self.M}")
        print(f"  = {q:.6f} m²/s")
        print(f"  = {q*1000:.4f} mm²/s")
        
        print(f"\n物理意义:")
        print(f"• 单位宽度上的流量")
        print(f"• 如果宽度B={self.L}m，总流量Q={q*self.L:.4f}m³/s")
        
        print(f"\n✓ 单宽流量: q = {q:.6f} m²/s")
        
        # (5) 渗透系数影响
        print(f"\n【问题5】渗透系数影响分析")
        
        print(f"\n渗透系数K的影响:")
        print(f"• v = K·I，渗流速度与K成正比")
        print(f"• q = K·I·M，单宽流量与K成正比")
        print(f"• K越大，渗流能力越强")
        
        # 典型土壤渗透系数
        print(f"\n典型土壤渗透系数:")
        soils = [
            ('粘土', 1e-9, 1e-7),
            ('粉土', 1e-7, 1e-5),
            ('细砂', 1e-5, 1e-3),
            ('中砂', 1e-4, 1e-2),
            ('粗砂', 1e-3, 1e-1),
            ('砾石', 1e-2, 1),
        ]
        
        for soil, K_min, K_max in soils:
            print(f"{soil}: {K_min} ~ {K_max} m/s")
        
        print(f"\n当前土壤K={self.K}m/s，属于中砂级别")
        
        # (6) 水力坡度影响
        print(f"\n【问题6】水力坡度影响分析")
        
        print(f"\n水力坡度I的影响:")
        print(f"• I = (H₁ - H₂) / L")
        print(f"• I越大，驱动力越大")
        print(f"• 渗流速度和流量与I成正比")
        
        print(f"\n改变水力坡度的方法:")
        print(f"1. 增大上游水位H₁")
        print(f"2. 降低下游水位H₂")
        print(f"3. 减小距离L")
        
        # 流态判别
        print(f"\n【流态判别】")
        
        Re = self.reynolds_number()
        
        print(f"\n雷诺数（d=1mm）:")
        print(f"Re = v·d/ν")
        print(f"   = {v:.6f} × 0.001 / 1e-6")
        print(f"   = {Re:.2f}")
        
        print(f"\n流态判别标准:")
        print(f"• Re < 1：层流（达西定律适用）")
        print(f"• 1 < Re < 10：过渡流（达西定律近似适用）")
        print(f"• Re > 10：紊流（达西定律不适用）")
        
        if Re < 1:
            print(f"\n✓ Re={Re:.2f} < 1，层流，达西定律适用")
        elif Re < 10:
            print(f"\n△ Re={Re:.2f}，过渡流，达西定律近似适用")
        else:
            print(f"\n✗ Re={Re:.2f} > 10，紊流，达西定律不适用")
        
        # 考试要点
        print(f"\n【考试要点】")
        print(f"1. 达西定律: v = K·I")
        print(f"2. 水力坡度: I = (H₁ - H₂) / L")
        print(f"3. 单宽流量: q = K·I·M")
        print(f"4. 实际流速: u = v/n")
        print(f"5. 渗流速度vs实际流速: u = v/n > v")
        print(f"6. 达西定律适用范围: Re < 1~10（层流）")
        print(f"7. 渗透系数K的物理意义: I=1时的渗流速度")
        
        print(f"\n{'='*70}\n")


def main():
    """主函数"""
    
    print("达西定律与渗流分析")
    print("-" * 70)
    
    # 系统参数
    K = 0.02  # 渗透系数 [m/s]
    M = 5  # 土层厚度 [m]
    L = 100  # 测压管间距 [m]
    H1 = 10  # 上游水位 [m]
    H2 = 6  # 下游水位 [m]
    n = 0.3  # 孔隙率
    
    # 创建分析实例
    darcy = DarcyLaw(K, M, L, H1, H2, n)
    
    # 打印结果
    darcy.print_results()
    
    # 绘制分析图
    darcy.plot_analysis()


if __name__ == "__main__":
    main()
