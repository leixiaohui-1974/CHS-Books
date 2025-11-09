# -*- coding: utf-8 -*-
"""
第06章 水泵与水泵站 - 题3：水泵工况点分析

问题描述：
    某离心泵特性曲线为：H = 50 - 0.001Q²（Q单位L/s，H单位m）
    管路特性曲线为：H = 20 + 0.0005Q²（静扬程20 m）
    
    求：
    1. 确定水泵工况点（流量Q和扬程H）
    2. 如果管路阻力增大（系数变为0.001），工况点如何变化？
    3. 如果将两台相同水泵并联运行，工况点如何变化？
    4. 绘制水泵特性曲线、管路特性曲线及工况点示意图

核心公式：
    1. 工况点条件：H泵 = H管
    2. 水泵特性：H = H0 - kQ²
    3. 管路特性：H = Hst + rQ²
    4. 并联：Q并 = Q1 + Q2（相同扬程）
    5. 串联：H串 = H1 + H2（相同流量）

考试要点：
    - 工况点是水泵与管路共同作用的平衡点
    - 管路阻力增大导致流量减小、扬程增大
    - 并联增加流量，但不是简单的2倍
    - 工况点图解法是重要分析方法

作者: CHS-Books Team
日期: 2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve
from typing import Tuple

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class OperatingPoint:
    """水泵工况点分析"""
    
    def __init__(self, H0: float, k_pump: float, Hst: float, r_pipe: float):
        """
        初始化水泵和管路特性
        
        参数:
            H0: 水泵零流量扬程 [m]
            k_pump: 水泵特性系数
            Hst: 静扬程 [m]
            r_pipe: 管路阻力系数
        """
        self.H0 = H0
        self.k_pump = k_pump
        self.Hst = Hst
        self.r_pipe = r_pipe
        
    def pump_curve(self, Q: np.ndarray) -> np.ndarray:
        """
        水泵特性曲线
        
        参数:
            Q: 流量 [L/s]
        
        返回:
            H: 扬程 [m]
        
        公式:
            H = H0 - k·Q²
        """
        H = self.H0 - self.k_pump * (Q ** 2)
        return H
    
    def pipe_curve(self, Q: np.ndarray, r: float = None) -> np.ndarray:
        """
        管路特性曲线
        
        参数:
            Q: 流量 [L/s]
            r: 管路阻力系数（可选，默认使用self.r_pipe）
        
        返回:
            H: 扬程 [m]
        
        公式:
            H = Hst + r·Q²
        """
        if r is None:
            r = self.r_pipe
        H = self.Hst + r * (Q ** 2)
        return H
    
    def find_operating_point(self, r: float = None) -> Tuple[float, float]:
        """
        求解工况点（解析法）
        
        参数:
            r: 管路阻力系数（可选）
        
        返回:
            Q: 工况点流量 [L/s]
            H: 工况点扬程 [m]
        
        工况点条件:
            H泵 = H管
            H0 - k·Q² = Hst + r·Q²
            Q² = (H0 - Hst)/(k + r)
        """
        if r is None:
            r = self.r_pipe
        
        # 解析解
        Q_squared = (self.H0 - self.Hst) / (self.k_pump + r)
        Q = np.sqrt(Q_squared)
        H = self.pump_curve(Q)
        
        return Q, H
    
    def parallel_pump_curve(self, Q: np.ndarray, n_pumps: int = 2) -> np.ndarray:
        """
        并联水泵特性曲线
        
        参数:
            Q: 总流量 [L/s]
            n_pumps: 并联台数
        
        返回:
            H: 扬程 [m]
        
        并联特性:
            相同扬程下，流量相加
            Q总 = n·Q单
            H = H0 - k·(Q总/n)²
        """
        Q_single = Q / n_pumps
        H = self.pump_curve(Q_single)
        return H
    
    def find_parallel_operating_point(self, n_pumps: int = 2) -> Tuple[float, float, float]:
        """
        求解并联工况点
        
        参数:
            n_pumps: 并联台数
        
        返回:
            Q_total: 总流量 [L/s]
            H: 扬程 [m]
            Q_single: 单泵流量 [L/s]
        """
        # 并联特性方程：H0 - k·(Q/n)² = Hst + r·Q²
        # 整理：(H0 - Hst) = k·Q²/n² + r·Q²
        # Q² = (H0 - Hst)/(k/n² + r)
        
        Q_squared = (self.H0 - self.Hst) / (self.k_pump / (n_pumps ** 2) + self.r_pipe)
        Q_total = np.sqrt(Q_squared)
        H = self.pipe_curve(Q_total)
        Q_single = Q_total / n_pumps
        
        return Q_total, H, Q_single
    
    def series_pump_curve(self, Q: np.ndarray, n_pumps: int = 2) -> np.ndarray:
        """
        串联水泵特性曲线
        
        参数:
            Q: 流量 [L/s]
            n_pumps: 串联台数
        
        返回:
            H: 总扬程 [m]
        
        串联特性:
            相同流量下，扬程相加
            H总 = n·H单
            H = n·(H0 - k·Q²)
        """
        H_single = self.pump_curve(Q)
        H_total = n_pumps * H_single
        return H_total
    
    def find_series_operating_point(self, n_pumps: int = 2) -> Tuple[float, float]:
        """
        求解串联工况点
        
        参数:
            n_pumps: 串联台数
        
        返回:
            Q: 流量 [L/s]
            H: 总扬程 [m]
        """
        # 串联特性方程：n·(H0 - k·Q²) = Hst + r·Q²
        # 整理：n·H0 - Hst = n·k·Q² + r·Q²
        # Q² = (n·H0 - Hst)/(n·k + r)
        
        Q_squared = (n_pumps * self.H0 - self.Hst) / (n_pumps * self.k_pump + self.r_pipe)
        Q = np.sqrt(Q_squared)
        H = self.pipe_curve(Q)
        
        return Q, H
    
    def plot_analysis(self):
        """绘制完整分析图表（9个子图）"""
        fig = plt.figure(figsize=(16, 12))
        
        # 计算工况点
        Q_op, H_op = self.find_operating_point()
        Q_op2, H_op2 = self.find_operating_point(r=0.001)
        Q_par, H_par, Q_single = self.find_parallel_operating_point()
        
        # 流量范围
        Q_range = np.linspace(0, 250, 200)
        
        # 1. 基本工况点图
        ax1 = plt.subplot(3, 3, 1)
        
        H_pump = self.pump_curve(Q_range)
        H_pipe = self.pipe_curve(Q_range)
        
        ax1.plot(Q_range, H_pump, 'b-', linewidth=2, label='水泵特性')
        ax1.plot(Q_range, H_pipe, 'r-', linewidth=2, label='管路特性')
        ax1.plot(Q_op, H_op, 'go', markersize=12, label=f'工况点A\n({Q_op:.1f}L/s, {H_op:.1f}m)')
        
        ax1.axhline(self.Hst, color='gray', linestyle='--', alpha=0.5, label=f'静扬程{self.Hst}m')
        ax1.axhline(self.H0, color='gray', linestyle='--', alpha=0.5, label=f'零流量{self.H0}m')
        
        ax1.set_xlabel('流量 Q (L/s)', fontsize=11)
        ax1.set_ylabel('扬程 H (m)', fontsize=11)
        ax1.set_title('水泵工况点确定', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.legend(fontsize=9)
        ax1.set_xlim(0, 250)
        ax1.set_ylim(0, 60)
        
        # 2. 阻力变化影响
        ax2 = plt.subplot(3, 3, 2)
        
        H_pipe2 = self.pipe_curve(Q_range, r=0.001)
        
        ax2.plot(Q_range, H_pump, 'b-', linewidth=2, label='水泵特性')
        ax2.plot(Q_range, H_pipe, 'r-', linewidth=2, label='原管路')
        ax2.plot(Q_range, H_pipe2, 'r--', linewidth=2, label='新管路(阻力↑)')
        ax2.plot(Q_op, H_op, 'go', markersize=12, label=f'原工况点A')
        ax2.plot(Q_op2, H_op2, 'ro', markersize=12, label=f'新工况点B')
        
        # 标注变化
        ax2.annotate('', xy=(Q_op2, H_op2), xytext=(Q_op, H_op),
                    arrowprops=dict(arrowstyle='->', color='purple', lw=2))
        ax2.text((Q_op+Q_op2)/2, (H_op+H_op2)/2+3, 'Q↓\nH↑', 
                fontsize=10, color='purple', fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
        
        ax2.set_xlabel('流量 Q (L/s)', fontsize=11)
        ax2.set_ylabel('扬程 H (m)', fontsize=11)
        ax2.set_title('管路阻力增大的影响', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.legend(fontsize=9)
        ax2.set_xlim(0, 250)
        ax2.set_ylim(0, 60)
        
        # 3. 并联运行工况点
        ax3 = plt.subplot(3, 3, 3)
        
        H_parallel = self.parallel_pump_curve(Q_range, n_pumps=2)
        
        ax3.plot(Q_range, H_pump, 'b-', linewidth=2, label='单泵特性')
        ax3.plot(Q_range, H_parallel, 'b--', linewidth=2, label='并联特性')
        ax3.plot(Q_range, H_pipe, 'r-', linewidth=2, label='管路特性')
        ax3.plot(Q_op, H_op, 'go', markersize=12, label=f'单泵工况A')
        ax3.plot(Q_par, H_par, 'mo', markersize=12, label=f'并联工况C')
        
        # 标注单泵分担流量
        ax3.axvline(Q_single, color='purple', linestyle=':', alpha=0.5)
        ax3.text(Q_single, 5, f'单泵分担\n{Q_single:.0f}L/s', 
                ha='center', fontsize=9, color='purple',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))
        
        ax3.set_xlabel('流量 Q (L/s)', fontsize=11)
        ax3.set_ylabel('扬程 H (m)', fontsize=11)
        ax3.set_title('并联运行工况点', fontsize=12, fontweight='bold')
        ax3.grid(True, alpha=0.3)
        ax3.legend(fontsize=9)
        ax3.set_xlim(0, 250)
        ax3.set_ylim(0, 60)
        
        # 4. 工况点对比表
        ax4 = plt.subplot(3, 3, 4)
        ax4.axis('off')
        
        data = [
            ['工况', '流量Q(L/s)', '扬程H(m)', '说明'],
            ['单泵A', f'{Q_op:.1f}', f'{H_op:.1f}', '原工况'],
            ['阻力增B', f'{Q_op2:.1f}', f'{H_op2:.1f}', f'Q↓{(1-Q_op2/Q_op)*100:.1f}%'],
            ['并联C', f'{Q_par:.1f}', f'{H_par:.1f}', f'Q↑{(Q_par/Q_op-1)*100:.1f}%'],
            ['单泵分担', f'{Q_single:.1f}', f'{H_par:.1f}', f'每台{Q_single:.0f}L/s'],
        ]
        
        table = ax4.table(cellText=data, loc='center', cellLoc='center',
                         colWidths=[0.2, 0.25, 0.25, 0.3])
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2)
        
        # 设置表头样式
        for i in range(4):
            table[(0, i)].set_facecolor('#4CAF50')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        # 设置数据行颜色
        for i in range(1, 5):
            for j in range(4):
                if i % 2 == 0:
                    table[(i, j)].set_facecolor('#E8F5E9')
        
        ax4.set_title('工况点对比表', fontsize=12, fontweight='bold', pad=20)
        
        # 5. 流量变化柱状图
        ax5 = plt.subplot(3, 3, 5)
        
        cases = ['单泵A', '阻力增B', '并联C']
        flows = [Q_op, Q_op2, Q_par]
        colors_bar = ['green', 'red', 'blue']
        
        bars = ax5.bar(cases, flows, color=colors_bar, alpha=0.7, edgecolor='black')
        ax5.set_ylabel('流量 (L/s)', fontsize=11)
        ax5.set_title('不同工况流量对比', fontsize=12, fontweight='bold')
        ax5.grid(True, alpha=0.3, axis='y')
        
        for bar, val in zip(bars, flows):
            height = bar.get_height()
            ax5.text(bar.get_x() + bar.get_width()/2, height,
                    f'{val:.1f}', ha='center', va='bottom', 
                    fontsize=10, fontweight='bold')
        
        # 6. 扬程变化柱状图
        ax6 = plt.subplot(3, 3, 6)
        
        heads = [H_op, H_op2, H_par]
        bars = ax6.bar(cases, heads, color=colors_bar, alpha=0.7, edgecolor='black')
        ax6.set_ylabel('扬程 (m)', fontsize=11)
        ax6.set_title('不同工况扬程对比', fontsize=12, fontweight='bold')
        ax6.grid(True, alpha=0.3, axis='y')
        
        for bar, val in zip(bars, heads):
            height = bar.get_height()
            ax6.text(bar.get_x() + bar.get_width()/2, height,
                    f'{val:.1f}', ha='center', va='bottom',
                    fontsize=10, fontweight='bold')
        
        # 7. 并联效果分析
        ax7 = plt.subplot(3, 3, 7)
        
        n_pumps_range = np.arange(1, 6)
        Q_parallel_range = []
        H_parallel_range = []
        Q_single_range = []
        
        for n in n_pumps_range:
            Q_p, H_p, Q_s = self.find_parallel_operating_point(n_pumps=n)
            Q_parallel_range.append(Q_p)
            H_parallel_range.append(H_p)
            Q_single_range.append(Q_s)
        
        ax7_twin = ax7.twinx()
        line1 = ax7.plot(n_pumps_range, Q_parallel_range, 'b-o', linewidth=2, 
                        markersize=8, label='总流量')
        line2 = ax7_twin.plot(n_pumps_range, H_parallel_range, 'r-s', linewidth=2,
                             markersize=8, label='扬程')
        
        ax7.set_xlabel('并联台数', fontsize=11)
        ax7.set_ylabel('流量 (L/s)', fontsize=11, color='b')
        ax7_twin.set_ylabel('扬程 (m)', fontsize=11, color='r')
        ax7.tick_params(axis='y', labelcolor='b')
        ax7_twin.tick_params(axis='y', labelcolor='r')
        ax7.set_title('并联台数影响分析', fontsize=12, fontweight='bold')
        ax7.grid(True, alpha=0.3)
        
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax7.legend(lines, labels, loc='upper left')
        
        # 8. 工况点求解过程
        ax8 = plt.subplot(3, 3, 8)
        ax8.axis('off')
        
        steps = [
            '【工况点求解步骤】',
            '',
            '单泵工况点A：',
            f'H泵 = H管',
            f'{self.H0} - {self.k_pump}Q² = {self.Hst} + {self.r_pipe}Q²',
            f'Q² = ({self.H0}-{self.Hst})/({self.k_pump}+{self.r_pipe})',
            f'Q² = {(self.H0-self.Hst)/(self.k_pump+self.r_pipe):.0f}',
            f'Q = {Q_op:.1f} L/s',
            f'H = {H_op:.1f} m',
            '',
            '阻力增大工况点B(r=0.001)：',
            f'Q² = {(self.H0-self.Hst)/(self.k_pump+0.001):.0f}',
            f'Q = {Q_op2:.1f} L/s (↓{(1-Q_op2/Q_op)*100:.1f}%)',
            f'H = {H_op2:.1f} m (↑{(H_op2/H_op-1)*100:.1f}%)',
            '',
            '并联工况点C(n=2)：',
            f'Q² = {(self.H0-self.Hst)/(self.k_pump/4+self.r_pipe):.0f}',
            f'Q = {Q_par:.1f} L/s (↑{(Q_par/Q_op-1)*100:.1f}%)',
            f'单泵分担: {Q_single:.1f} L/s',
        ]
        
        y_pos = 0.95
        for step in steps:
            if '【' in step:
                ax8.text(0.5, y_pos, step, fontsize=11, fontweight='bold',
                        horizontalalignment='center', verticalalignment='top',
                        color='darkred')
            elif step == '':
                y_pos -= 0.015
                continue
            elif '工况点' in step:
                ax8.text(0.05, y_pos, step, fontsize=10, fontweight='bold',
                        verticalalignment='top', color='darkblue')
            else:
                ax8.text(0.1, y_pos, step, fontsize=9, verticalalignment='top',
                        family='monospace')
            y_pos -= 0.048
        
        ax8.set_title('工况点计算过程', fontsize=12, fontweight='bold')
        
        # 9. 结果汇总
        ax9 = plt.subplot(3, 3, 9)
        ax9.axis('off')
        
        summary = [
            '═══ 分析结果汇总 ═══',
            '',
            '【单泵工况点A】',
            f'流量: Q = {Q_op:.1f} L/s',
            f'扬程: H = {H_op:.1f} m',
            '',
            '【阻力增大工况点B】',
            f'流量: Q = {Q_op2:.1f} L/s',
            f'变化: ↓{(1-Q_op2/Q_op)*100:.1f}%',
            f'扬程: H = {H_op2:.1f} m',
            f'变化: ↑{(H_op2/H_op-1)*100:.1f}%',
            '',
            '【并联工况点C】',
            f'总流量: Q = {Q_par:.1f} L/s',
            f'增幅: ↑{(Q_par/Q_op-1)*100:.1f}% (非2倍!)',
            f'扬程: H = {H_par:.1f} m',
            f'单泵分担: {Q_single:.1f} L/s',
            '',
            '【结论】',
            '• 阻力↑→Q↓H↑（工况点左移）',
            '• 并联→Q↑但<2倍（因H也↑）',
            '• 并联适合增大流量',
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
            y_pos -= 0.042
        
        ax9.set_title('结果汇总', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('/tmp/ch06_problem03_operating_point.png', dpi=150, bbox_inches='tight')
        print(f"图表已保存: /tmp/ch06_problem03_operating_point.png")
        plt.show()
    
    def print_results(self):
        """打印计算结果"""
        print("\n" + "="*70)
        print("第06章 水泵与水泵站 - 题3：水泵工况点分析")
        print("="*70)
        
        # 基本参数
        print(f"\n【系统参数】")
        print(f"水泵特性: H = {self.H0} - {self.k_pump}Q²")
        print(f"管路特性: H = {self.Hst} + {self.r_pipe}Q²")
        print(f"静扬程: Hst = {self.Hst} m")
        
        # (1) 单泵工况点
        print(f"\n【问题1】单泵工况点")
        Q_op, H_op = self.find_operating_point()
        
        print(f"\n工况点条件：H泵 = H管")
        print(f"{self.H0} - {self.k_pump}Q² = {self.Hst} + {self.r_pipe}Q²")
        print(f"{self.H0} - {self.Hst} = {self.k_pump}Q² + {self.r_pipe}Q²")
        print(f"{self.H0 - self.Hst} = {self.k_pump + self.r_pipe}Q²")
        print(f"Q² = {(self.H0 - self.Hst)/(self.k_pump + self.r_pipe):.0f}")
        print(f"Q = {Q_op:.3f} L/s")
        
        print(f"\n扬程验证:")
        print(f"H泵 = {self.H0} - {self.k_pump}×{Q_op:.1f}² = {H_op:.2f} m")
        print(f"H管 = {self.Hst} + {self.r_pipe}×{Q_op:.1f}² = {self.pipe_curve(Q_op):.2f} m")
        print(f"✓ 一致")
        
        print(f"\n✓ 工况点A: Q = {Q_op:.1f} L/s, H = {H_op:.1f} m")
        
        # (2) 阻力增大
        print(f"\n【问题2】管路阻力增大（r = 0.001）")
        Q_op2, H_op2 = self.find_operating_point(r=0.001)
        
        print(f"\n新管路特性: H = {self.Hst} + 0.001Q²")
        print(f"新工况点方程:")
        print(f"{self.H0} - {self.k_pump}Q² = {self.Hst} + 0.001Q²")
        print(f"Q² = {(self.H0 - self.Hst)/(self.k_pump + 0.001):.0f}")
        print(f"Q = {Q_op2:.1f} L/s")
        print(f"H = {H_op2:.1f} m")
        
        print(f"\n✓ 新工况点B: Q = {Q_op2:.1f} L/s, H = {H_op2:.1f} m")
        
        print(f"\n对比分析:")
        print(f"流量变化: {Q_op:.1f} → {Q_op2:.1f} L/s (↓{(1-Q_op2/Q_op)*100:.1f}%)")
        print(f"扬程变化: {H_op:.1f} → {H_op2:.1f} m (↑{(H_op2/H_op-1)*100:.1f}%)")
        print(f"结论: 阻力增大 → 流量减小，扬程增大")
        
        # (3) 并联运行
        print(f"\n【问题3】两台泵并联运行")
        Q_par, H_par, Q_single = self.find_parallel_operating_point()
        
        print(f"\n并联特性:")
        print(f"相同扬程下，流量相加: Q总 = 2Q单")
        print(f"H = {self.H0} - {self.k_pump}(Q/2)²")
        print(f"H = {self.H0} - {self.k_pump/4}Q²")
        
        print(f"\n并联工况点:")
        print(f"{self.H0} - {self.k_pump/4}Q² = {self.Hst} + {self.r_pipe}Q²")
        print(f"Q² = {(self.H0 - self.Hst)/(self.k_pump/4 + self.r_pipe):.0f}")
        print(f"Q = {Q_par:.1f} L/s")
        print(f"H = {H_par:.1f} m")
        
        print(f"\n✓ 并联工况点C: Q = {Q_par:.1f} L/s, H = {H_par:.1f} m")
        print(f"✓ 单泵分担流量: {Q_single:.1f} L/s")
        
        print(f"\n对比分析:")
        print(f"总流量: {Q_op:.1f} → {Q_par:.1f} L/s (增幅{(Q_par/Q_op-1)*100:.1f}%)")
        print(f"扬程: {H_op:.1f} → {H_par:.1f} m (增幅{(H_par/H_op-1)*100:.1f}%)")
        print(f"单泵流量: {Q_op:.1f} → {Q_single:.1f} L/s (↓{(1-Q_single/Q_op)*100:.1f}%)")
        
        print(f"\n重要结论:")
        print(f"• 并联后总流量增大{(Q_par/Q_op-1)*100:.0f}%，不是2倍（{Q_par/Q_op:.2f}倍）")
        print(f"• 原因：扬程增大（{H_op:.1f}→{H_par:.1f}m），每台泵流量减小")
        print(f"• 并联适用：需要增大流量的场合")
        
        # 对比表
        print(f"\n【工况点对比表】")
        print(f"{'工况':^12} {'流量Q(L/s)':^15} {'扬程H(m)':^12} {'备注':^20}")
        print(f"{'-'*65}")
        print(f"{'单泵A':^12} {Q_op:^15.1f} {H_op:^12.1f} {'原工况':^20}")
        print(f"{'阻力增B':^12} {Q_op2:^15.1f} {H_op2:^12.1f} {f'Q↓{(1-Q_op2/Q_op)*100:.1f}%':^20}")
        print(f"{'并联C':^12} {Q_par:^15.1f} {H_par:^12.1f} {f'Q↑{(Q_par/Q_op-1)*100:.1f}%':^20}")
        print(f"{'单泵分担':^12} {Q_single:^15.1f} {H_par:^12.1f} {f'每台{Q_single:.0f}L/s':^20}")
        
        # 考试要点
        print(f"\n【考试要点】")
        print(f"1. 工况点：H泵 = H管（特性曲线交点）")
        print(f"2. 解析法：{self.H0-self.Hst} = (k+r)Q²，求Q")
        print(f"3. 阻力增大：流量↓，扬程↑（工况点左移）")
        print(f"4. 并联运行：Q并 = Q1 + Q2（相同H）")
        print(f"5. 并联效果：流量增大，但不是台数倍")
        print(f"6. 图解法：画出两条曲线，找交点")
        
        print(f"\n{'='*70}\n")


def main():
    """主函数"""
    
    print("水泵工况点分析")
    print("-" * 70)
    
    # 水泵和管路参数
    H0 = 50  # 水泵零流量扬程 [m]
    k_pump = 0.001  # 水泵特性系数
    Hst = 20  # 静扬程 [m]
    r_pipe = 0.0005  # 管路阻力系数
    
    # 创建工况点分析实例
    op = OperatingPoint(H0, k_pump, Hst, r_pipe)
    
    # 打印结果
    op.print_results()
    
    # 绘制分析图
    op.plot_analysis()


if __name__ == "__main__":
    main()
