# -*- coding: utf-8 -*-
"""
第07章 地下水动力学 - 题12：群井干扰

问题描述：
    某承压含水层，厚度M = 10m，渗透系数K = 0.001 m/s
    有3口抽水井：
    - 井1：位置(0, 0)，流量Q1 = 0.05 m³/s
    - 井2：位置(100, 0)，流量Q2 = 0.04 m³/s
    - 井3：位置(50, 86.6)，流量Q3 = 0.03 m³/s
    
    影响半径：R = 300m
    各井半径：r0 = 0.2m
    
    求：
    1. 各井单独作用时的水位降深
    2. 叠加原理应用
    3. 指定点总降深
    4. 井间相互影响
    5. 最大降深点位置

核心公式：
    1. 叠加原理：s总 = s1 + s2 + s3 + ...
    2. 单井降深：si = Qi·ln(R/ri)/(2πKM)
    3. ri = √[(x-xi)²+(y-yi)²]

考试要点：
    - 叠加原理（线性叠加）
    - 群井干扰增大降深
    - 井距影响
    - 最优井位布置

作者: CHS-Books Team
日期: 2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, List

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class WellInterference:
    """群井干扰分析"""
    
    def __init__(self, M: float, K: float, R: float, r0: float):
        """
        初始化参数
        
        参数:
            M: 含水层厚度 [m]
            K: 渗透系数 [m/s]
            R: 影响半径 [m]
            r0: 井半径 [m]
        """
        self.M = M
        self.K = K
        self.R = R
        self.r0 = r0
        
        # 井列表：[x, y, Q]
        self.wells = []
        
    def add_well(self, x: float, y: float, Q: float):
        """添加抽水井"""
        self.wells.append({'x': x, 'y': y, 'Q': Q})
    
    def distance(self, x1: float, y1: float, x2: float, y2: float) -> float:
        """计算两点距离"""
        return np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    
    def single_well_drawdown(self, Q: float, r: float) -> float:
        """
        单井降深
        
        s = Q·ln(R/r)/(2πKM)
        
        参数:
            Q: 流量 [m³/s]
            r: 距井距离 [m]
        """
        if r < self.r0:
            r = self.r0  # 井壁处
        
        s = Q * np.log(self.R / r) / (2 * np.pi * self.K * self.M)
        return s
    
    def total_drawdown(self, x: float, y: float) -> Tuple[float, List[float]]:
        """
        指定点总降深（叠加原理）
        
        s_total = Σ si
        
        参数:
            x, y: 计算点坐标 [m]
        
        返回:
            s_total: 总降深
            s_individual: 各井单独作用降深列表
        """
        s_individual = []
        
        for well in self.wells:
            r = self.distance(x, y, well['x'], well['y'])
            s = self.single_well_drawdown(well['Q'], r)
            s_individual.append(s)
        
        s_total = sum(s_individual)
        
        return s_total, s_individual
    
    def drawdown_at_well(self, well_idx: int) -> Tuple[float, float, List[float]]:
        """
        某井井壁处的降深
        
        参数:
            well_idx: 井编号（从0开始）
        
        返回:
            s_own: 自身降深
            s_total: 总降深
            s_others: 其他井影响列表
        """
        well = self.wells[well_idx]
        
        # 自身降深（井壁处r=r0）
        s_own = self.single_well_drawdown(well['Q'], self.r0)
        
        # 其他井影响
        s_others = []
        for i, other_well in enumerate(self.wells):
            if i != well_idx:
                r = self.distance(well['x'], well['y'], other_well['x'], other_well['y'])
                s = self.single_well_drawdown(other_well['Q'], r)
                s_others.append(s)
        
        s_total = s_own + sum(s_others)
        
        return s_own, s_total, s_others
    
    def drawdown_field(self, x_range: tuple, y_range: tuple, n_points: int = 50) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        降深场分布
        
        参数:
            x_range: x范围 [m]
            y_range: y范围 [m]
            n_points: 网格点数
        
        返回:
            X, Y, S: 网格坐标和降深
        """
        x = np.linspace(x_range[0], x_range[1], n_points)
        y = np.linspace(y_range[0], y_range[1], n_points)
        X, Y = np.meshgrid(x, y)
        
        S = np.zeros_like(X)
        
        for i in range(n_points):
            for j in range(n_points):
                S[i, j], _ = self.total_drawdown(X[i, j], Y[i, j])
        
        return X, Y, S
    
    def find_max_drawdown_point(self, x_range: tuple, y_range: tuple, n_search: int = 100) -> Tuple[float, float, float]:
        """
        寻找最大降深点
        
        参数:
            x_range: x搜索范围
            y_range: y搜索范围
            n_search: 搜索网格数
        
        返回:
            x_max, y_max, s_max: 最大降深点坐标和降深值
        """
        x = np.linspace(x_range[0], x_range[1], n_search)
        y = np.linspace(y_range[0], y_range[1], n_search)
        
        s_max = 0
        x_max, y_max = 0, 0
        
        for xi in x:
            for yi in y:
                s, _ = self.total_drawdown(xi, yi)
                if s > s_max:
                    s_max = s
                    x_max, y_max = xi, yi
        
        return x_max, y_max, s_max
    
    def plot_analysis(self):
        """绘制完整分析图表（9个子图）"""
        fig = plt.figure(figsize=(16, 12))
        
        # 1. 井位布置图
        ax1 = plt.subplot(3, 3, 1)
        
        for i, well in enumerate(self.wells):
            ax1.plot(well['x'], well['y'], 'ro', markersize=15)
            ax1.text(well['x'], well['y']+10, f'井{i+1}\nQ={well["Q"]*1000:.0f}L/s',
                    ha='center', va='bottom', fontsize=9, fontweight='bold',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))
            
            # 影响范围
            circle = plt.Circle((well['x'], well['y']), self.R, fill=False,
                              edgecolor='blue', linestyle='--', alpha=0.3)
            ax1.add_patch(circle)
        
        ax1.set_xlabel('x (m)', fontsize=11)
        ax1.set_ylabel('y (m)', fontsize=11)
        ax1.set_title('井位布置图', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.set_aspect('equal')
        ax1.set_xlim(-50, 150)
        ax1.set_ylim(-50, 150)
        
        # 2. 各井单独作用降深
        ax2 = plt.subplot(3, 3, 2)
        
        well_names = [f'井{i+1}' for i in range(len(self.wells))]
        Q_values = [well['Q']*1000 for well in self.wells]
        
        # 各井井壁处自身降深
        s_own_values = []
        for i, well in enumerate(self.wells):
            s_own = self.single_well_drawdown(well['Q'], self.r0)
            s_own_values.append(s_own)
        
        bars = ax2.bar(well_names, s_own_values, color='lightblue', alpha=0.7, edgecolor='black')
        ax2.set_ylabel('降深 (m)', fontsize=11)
        ax2.set_title('各井单独作用时井壁降深', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='y')
        
        for bar, s, Q in zip(bars, s_own_values, Q_values):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2, height,
                    f'{s:.2f}m', ha='center', va='bottom',
                    fontsize=9, fontweight='bold')
            ax2.text(bar.get_x() + bar.get_width()/2, height/2,
                    f'Q={Q:.0f}L/s', ha='center', va='center',
                    fontsize=8, color='darkblue')
        
        # 3. 各井相互影响
        ax3 = plt.subplot(3, 3, 3)
        ax3.axis('off')
        
        influence_text = ['【各井相互影响】', '']
        
        for i, well in enumerate(self.wells):
            s_own, s_total, s_others = self.drawdown_at_well(i)
            
            influence_text.append(f'井{i+1}井壁处:')
            influence_text.append(f'  自身降深: {s_own:.3f} m')
            
            for j, s_other in enumerate(s_others):
                other_idx = j if j < i else j + 1
                influence_text.append(f'  井{other_idx+1}影响: {s_other:.3f} m')
            
            influence_text.append(f'  总降深: {s_total:.3f} m')
            influence_text.append(f'  干扰增幅: {(s_total/s_own-1)*100:+.1f}%')
            influence_text.append('')
        
        y_pos = 0.98
        for line in influence_text:
            if '【' in line:
                ax3.text(0.5, y_pos, line, fontsize=11, fontweight='bold',
                        horizontalalignment='center', verticalalignment='top',
                        color='darkblue')
            elif line.startswith('井') and '井壁处' in line:
                ax3.text(0.05, y_pos, line, fontsize=10, fontweight='bold',
                        verticalalignment='top', color='darkred')
            elif line == '':
                y_pos -= 0.01
                continue
            elif '干扰增幅' in line:
                ax3.text(0.1, y_pos, line, fontsize=9, verticalalignment='top',
                        family='monospace', color='darkgreen', fontweight='bold')
            else:
                ax3.text(0.1, y_pos, line, fontsize=9, verticalalignment='top',
                        family='monospace')
            y_pos -= 0.032
        
        ax3.set_title('相互影响分析', fontsize=12, fontweight='bold')
        
        # 4. 降深场等值线图
        ax4 = plt.subplot(3, 3, 4)
        
        X, Y, S = self.drawdown_field((-50, 150), (-50, 150), 50)
        
        contour = ax4.contourf(X, Y, S, levels=15, cmap='YlOrRd', alpha=0.7)
        contour_lines = ax4.contour(X, Y, S, levels=10, colors='black', linewidths=0.5, alpha=0.5)
        ax4.clabel(contour_lines, inline=True, fontsize=8, fmt='%.1f')
        
        # 井位置
        for i, well in enumerate(self.wells):
            ax4.plot(well['x'], well['y'], 'ko', markersize=10)
            ax4.text(well['x'], well['y']+5, f'{i+1}', ha='center', va='bottom',
                    fontsize=9, fontweight='bold', color='white',
                    bbox=dict(boxstyle='circle', facecolor='black', alpha=0.7))
        
        plt.colorbar(contour, ax=ax4, label='降深 (m)')
        ax4.set_xlabel('x (m)', fontsize=11)
        ax4.set_ylabel('y (m)', fontsize=11)
        ax4.set_title('降深场等值线图', fontsize=12, fontweight='bold')
        ax4.set_aspect('equal')
        
        # 5. 沿x轴降深分布
        ax5 = plt.subplot(3, 3, 5)
        
        x_line = np.linspace(-50, 150, 100)
        y_line = 0
        
        s_total_line = []
        s_individual_lines = [[] for _ in range(len(self.wells))]
        
        for x in x_line:
            s_tot, s_ind = self.total_drawdown(x, y_line)
            s_total_line.append(s_tot)
            for i, s in enumerate(s_ind):
                s_individual_lines[i].append(s)
        
        # 各井单独作用
        for i in range(len(self.wells)):
            ax5.plot(x_line, s_individual_lines[i], '--', alpha=0.5, linewidth=1,
                    label=f'井{i+1}单独')
        
        # 总降深
        ax5.plot(x_line, s_total_line, 'k-', linewidth=2, label='总降深')
        
        # 井位置标注
        for well in self.wells:
            ax5.axvline(well['x'], color='gray', linestyle=':', alpha=0.3)
        
        ax5.set_xlabel('x (m)', fontsize=11)
        ax5.set_ylabel('降深 (m)', fontsize=11)
        ax5.set_title('沿x轴降深分布(y=0)', fontsize=12, fontweight='bold')
        ax5.legend(fontsize=8)
        ax5.grid(True, alpha=0.3)
        
        # 6. 井间距影响
        ax6 = plt.subplot(3, 3, 6)
        
        # 以井1和井2为例，分析井间距影响
        d12_current = self.distance(self.wells[0]['x'], self.wells[0]['y'],
                                   self.wells[1]['x'], self.wells[1]['y'])
        
        distances = np.linspace(20, 200, 50)
        interference_ratios = []
        
        for d in distances:
            s_own = self.single_well_drawdown(self.wells[0]['Q'], self.r0)
            s_other = self.single_well_drawdown(self.wells[1]['Q'], d)
            ratio = s_other / s_own
            interference_ratios.append(ratio)
        
        ax6.plot(distances, np.array(interference_ratios)*100, 'b-', linewidth=2)
        
        # 当前井距
        idx_current = np.argmin(np.abs(distances - d12_current))
        ax6.plot(d12_current, interference_ratios[idx_current]*100, 'ro', markersize=12,
                label=f'当前井距{d12_current:.0f}m')
        
        ax6.set_xlabel('井间距 d (m)', fontsize=11)
        ax6.set_ylabel('干扰比例 (%)', fontsize=11)
        ax6.set_title('井间距对干扰的影响', fontsize=12, fontweight='bold')
        ax6.legend(fontsize=9)
        ax6.grid(True, alpha=0.3)
        
        # 7. 各井井壁总降深对比
        ax7 = plt.subplot(3, 3, 7)
        
        s_own_list = []
        s_total_list = []
        interference_percent = []
        
        for i in range(len(self.wells)):
            s_own, s_total, _ = self.drawdown_at_well(i)
            s_own_list.append(s_own)
            s_total_list.append(s_total)
            interference_percent.append((s_total/s_own - 1) * 100)
        
        x = np.arange(len(self.wells))
        width = 0.35
        
        bars1 = ax7.bar(x - width/2, s_own_list, width, label='自身降深',
                       color='lightblue', alpha=0.7, edgecolor='black')
        bars2 = ax7.bar(x + width/2, s_total_list, width, label='总降深',
                       color='lightcoral', alpha=0.7, edgecolor='black')
        
        ax7.set_ylabel('降深 (m)', fontsize=11)
        ax7.set_xlabel('井号', fontsize=11)
        ax7.set_title('各井井壁降深对比', fontsize=12, fontweight='bold')
        ax7.set_xticks(x)
        ax7.set_xticklabels([f'井{i+1}' for i in range(len(self.wells))])
        ax7.legend(fontsize=9)
        ax7.grid(True, alpha=0.3, axis='y')
        
        # 添加数值标注
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax7.text(bar.get_x() + bar.get_width()/2, height,
                        f'{height:.2f}', ha='center', va='bottom', fontsize=8)
        
        # 标注增幅
        for i, pct in enumerate(interference_percent):
            ax7.text(i, max(s_own_list[i], s_total_list[i])*0.7,
                    f'+{pct:.0f}%', ha='center', fontsize=9,
                    color='darkgreen', fontweight='bold')
        
        # 8. 叠加原理说明
        ax8 = plt.subplot(3, 3, 8)
        ax8.axis('off')
        
        principle = [
            '【叠加原理】',
            '',
            '基本原理:',
            '• 群井总降深 = 各井单独降深之和',
            '• s_总 = s₁ + s₂ + s₃ + ...',
            '• 线性叠加（达西定律线性）',
            '',
            '单井降深公式:',
            'si = Qi·ln(R/ri)/(2πKM)',
            '其中 ri = √[(x-xi)²+(y-yi)²]',
            '',
            '适用条件:',
            '• 承压水或无压水',
            '• 稳定流',
            '• 达西定律成立',
            '• 均质各向同性',
            '',
            '工程意义:',
            '• 预测群井降深',
            '• 优化井位布置',
            '• 避免过度干扰',
            '• 保护周边水井',
        ]
        
        y_pos = 0.98
        for line in principle:
            if '【' in line:
                ax8.text(0.5, y_pos, line, fontsize=11, fontweight='bold',
                        horizontalalignment='center', verticalalignment='top',
                        color='darkblue')
            elif line.endswith(':'):
                ax8.text(0.05, y_pos, line, fontsize=10, fontweight='bold',
                        verticalalignment='top', color='darkred')
            elif line.startswith('•') or line.startswith('si') or line.startswith('其中'):
                ax8.text(0.1, y_pos, line, fontsize=9, verticalalignment='top',
                        family='monospace')
            elif line == '':
                y_pos -= 0.01
                continue
            else:
                ax8.text(0.1, y_pos, line, fontsize=9, verticalalignment='top',
                        family='monospace')
            y_pos -= 0.036
        
        ax8.set_title('叠加原理', fontsize=12, fontweight='bold')
        
        # 9. 结果汇总
        ax9 = plt.subplot(3, 3, 9)
        ax9.axis('off')
        
        summary = [
            '═══ 群井干扰结果 ═══',
            '',
            '【系统参数】',
            f'含水层厚度: M = {self.M} m',
            f'渗透系数: K = {self.K} m/s',
            f'井数: {len(self.wells)}口',
            '',
            '【各井流量】',
        ]
        
        for i, well in enumerate(self.wells):
            summary.append(f'井{i+1}: Q = {well["Q"]*1000:.0f} L/s')
            summary.append(f'   位置({well["x"]:.0f}, {well["y"]:.0f})')
        
        summary.append('')
        summary.append('【井壁总降深】')
        
        for i in range(len(self.wells)):
            s_own, s_total, _ = self.drawdown_at_well(i)
            interference = (s_total/s_own - 1) * 100
            summary.append(f'井{i+1}: {s_total:.3f} m')
            summary.append(f'   (干扰+{interference:.0f}%)')
        
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
            elif line.startswith('井') and ':' in line:
                ax9.text(0.1, y_pos, line, fontsize=9, verticalalignment='top',
                        family='monospace', fontweight='bold')
            else:
                ax9.text(0.15, y_pos, line, fontsize=9, verticalalignment='top',
                        family='monospace')
            y_pos -= 0.032
        
        ax9.set_title('结果汇总', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('/tmp/ch07_problem12_well_interference.png', dpi=150, bbox_inches='tight')
        print(f"图表已保存: /tmp/ch07_problem12_well_interference.png")
        plt.show()
    
    def print_results(self):
        """打印计算结果"""
        print("\n" + "="*70)
        print("第07章 地下水动力学 - 题12：群井干扰")
        print("="*70)
        
        # 基本参数
        print(f"\n【系统参数】")
        print(f"含水层厚度: M = {self.M} m")
        print(f"渗透系数: K = {self.K} m/s = {self.K*86400} m/d")
        print(f"影响半径: R = {self.R} m")
        print(f"井半径: r₀ = {self.r0} m")
        print(f"井数: {len(self.wells)}口")
        
        print(f"\n【各井参数】")
        for i, well in enumerate(self.wells):
            print(f"井{i+1}:")
            print(f"  位置: ({well['x']}, {well['y']})")
            print(f"  流量: Q = {well['Q']} m³/s = {well['Q']*1000} L/s")
        
        # (1) 各井单独作用降深
        print(f"\n【问题1】各井单独作用时的水位降深")
        
        print(f"\n单井降深公式:")
        print(f"s = Q·ln(R/r)/(2πKM)")
        
        print(f"\n各井井壁处（r=r₀）降深:")
        for i, well in enumerate(self.wells):
            s = self.single_well_drawdown(well['Q'], self.r0)
            print(f"\n井{i+1}:")
            print(f"s = {well['Q']}×ln({self.R}/{self.r0})/(2π×{self.K}×{self.M})")
            print(f"  = {well['Q']}×{np.log(self.R/self.r0):.4f}/{2*np.pi*self.K*self.M:.6f}")
            print(f"  = {s:.4f} m")
        
        # (2) 叠加原理
        print(f"\n【问题2】叠加原理应用")
        
        print(f"\n叠加原理:")
        print(f"• 群井总降深 = 各井单独作用降深之和")
        print(f"• s_总 = s₁ + s₂ + s₃ + ...")
        print(f"• 适用于线性系统（达西定律）")
        
        print(f"\n计算步骤:")
        print(f"1. 计算指定点到各井距离 ri")
        print(f"2. 计算各井在该点的降深 si")
        print(f"3. 叠加得总降深 s_总 = Σsi")
        
        # (3) 指定点总降深示例
        print(f"\n【问题3】指定点总降深")
        
        # 几个典型位置
        test_points = [
            (50, 50, "区域中心"),
            (0, 0, "井1井壁"),
            (100, 0, "井2井壁"),
        ]
        
        for x, y, desc in test_points:
            s_total, s_individual = self.total_drawdown(x, y)
            
            print(f"\n位置({x}, {y}) - {desc}:")
            for i, s in enumerate(s_individual):
                print(f"  井{i+1}影响: {s:.4f} m")
            print(f"  总降深: {s_total:.4f} m")
        
        # (4) 井间相互影响
        print(f"\n【问题4】井间相互影响")
        
        for i in range(len(self.wells)):
            print(f"\n井{i+1}井壁处分析:")
            
            s_own, s_total, s_others = self.drawdown_at_well(i)
            
            print(f"自身降深: {s_own:.4f} m")
            
            for j, s_other in enumerate(s_others):
                other_idx = j if j < i else j + 1
                other_well = self.wells[other_idx]
                d = self.distance(self.wells[i]['x'], self.wells[i]['y'],
                                other_well['x'], other_well['y'])
                print(f"井{other_idx+1}影响: {s_other:.4f} m (距离{d:.1f}m)")
            
            interference = sum(s_others)
            print(f"干扰总和: {interference:.4f} m")
            print(f"总降深: {s_total:.4f} m")
            print(f"干扰增幅: {(s_total/s_own-1)*100:+.1f}%")
        
        # 井间距影响分析
        print(f"\n井间距影响:")
        print(f"{'井距(m)':<15} {'干扰/自身(%)':<20} {'说明':<20}")
        print(f"{'-'*60}")
        
        for d in [20, 50, 100, 200, 300]:
            # 以井1为例
            s_own = self.single_well_drawdown(self.wells[0]['Q'], self.r0)
            # 假设另一井流量与井2相同
            s_other = self.single_well_drawdown(self.wells[1]['Q'], d)
            ratio = s_other / s_own * 100
            
            if ratio > 50:
                desc = "干扰很大"
            elif ratio > 20:
                desc = "干扰明显"
            elif ratio > 10:
                desc = "有干扰"
            else:
                desc = "干扰较小"
            
            print(f"{d:<15} {ratio:<20.1f} {desc:<20}")
        
        # (5) 最大降深点
        print(f"\n【问题5】最大降深点位置")
        
        print(f"\n说明:")
        print(f"• 最大降深一般不在井壁")
        print(f"• 出现在多井影响叠加最强处")
        print(f"• 通常在井群中心附近")
        
        # 简单搜索（粗略估计）
        x_max, y_max, s_max = self.find_max_drawdown_point((-50, 150), (-50, 150), 50)
        
        print(f"\n搜索结果（粗略）:")
        print(f"最大降深点: ({x_max:.1f}, {y_max:.1f})")
        print(f"最大降深: {s_max:.4f} m")
        
        # 对比各井井壁降深
        print(f"\n与各井井壁降深对比:")
        for i in range(len(self.wells)):
            _, s_well, _ = self.drawdown_at_well(i)
            print(f"井{i+1}井壁: {s_well:.4f} m")
        
        print(f"最大降深: {s_max:.4f} m")
        
        # 考试要点
        print(f"\n【考试要点】")
        print(f"1. 叠加原理: s_总 = Σsi")
        print(f"2. 单井降深: si = Qi·ln(R/ri)/(2πKM)")
        print(f"3. 距离: ri = √[(x-xi)²+(y-yi)²]")
        print(f"4. 群井干扰增大降深")
        print(f"5. 井距越小，干扰越大")
        print(f"6. 优化井位：适当井距")
        print(f"7. 线性叠加（达西定律线性）")
        print(f"8. 最大降深在井群中心附近")
        
        print(f"\n{'='*70}\n")


def main():
    """主函数"""
    
    print("群井干扰分析")
    print("-" * 70)
    
    # 系统参数
    M = 10  # 含水层厚度 [m]
    K = 0.001  # 渗透系数 [m/s]
    R = 300  # 影响半径 [m]
    r0 = 0.2  # 井半径 [m]
    
    # 创建分析实例
    wi = WellInterference(M, K, R, r0)
    
    # 添加3口井（三角形布置）
    wi.add_well(0, 0, 0.05)  # 井1
    wi.add_well(100, 0, 0.04)  # 井2
    wi.add_well(50, 86.6, 0.03)  # 井3（近似等边三角形）
    
    # 打印结果
    wi.print_results()
    
    # 绘制分析图
    wi.plot_analysis()


if __name__ == "__main__":
    main()
