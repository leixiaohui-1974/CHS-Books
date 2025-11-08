# -*- coding: utf-8 -*-
"""
第07章 地下水动力学 - 题9：集水廊道

问题描述：
    某承压含水层，厚度M = 12m，渗透系数K = 0.0015 m/s
    集水廊道（渗渠）半宽：a = 1m
    廊道中水位降深：s0 = 6m
    影响半径：R = 150m
    廊道长度：L = 100m（单位长度分析）
    
    求：
    1. 单位长度廊道流量
    2. 任意点水位分布
    3. 与井流的对比
    4. 廊道半宽影响
    5. 总流量（给定长度）

核心公式：
    1. 单位长度流量：q = 2KM(H0-hw)/ln(R/a)
    2. 任意点水位：h = hw + (H0-hw)ln(x/a)/ln(R/a)
    3. 总流量：Q = q·L
    4. 与井流对比：廊道是线状，井是点状

考试要点：
    - 集水廊道是线状集水建筑物
    - 单位长度流量q [m²/s]
    - 公式类似井流（半宽a代替半径r0）
    - 廊道比井更经济（单位长度）

作者: CHS-Books Team
日期: 2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class Gallery:
    """集水廊道分析"""
    
    def __init__(self, M: float, K: float, a: float, s0: float, R: float, L: float = 100):
        """
        初始化参数
        
        参数:
            M: 含水层厚度 [m]
            K: 渗透系数 [m/s]
            a: 廊道半宽 [m]
            s0: 廊道中水位降深 [m]
            R: 影响半径 [m]
            L: 廊道长度 [m]（用于总流量计算）
        """
        self.M = M
        self.K = K
        self.a = a
        self.s0 = s0
        self.R = R
        self.L = L
        
        # 初始水位
        self.H0 = M
        # 廊道中水位
        self.hw = self.H0 - s0
        
    def unit_discharge(self) -> float:
        """
        单位长度流量
        
        q = 2KM(H0-hw)/ln(R/a)
        
        单位：m²/s（每米长度的流量）
        """
        q = 2 * self.K * self.M * (self.H0 - self.hw) / np.log(self.R / self.a)
        return q
    
    def total_discharge(self, L: float = None) -> float:
        """
        总流量
        
        Q = q·L
        
        参数:
            L: 廊道长度 [m]
        """
        if L is None:
            L = self.L
        
        q = self.unit_discharge()
        Q = q * L
        return Q
    
    def water_head(self, x: float) -> float:
        """
        任意点水位（垂直于廊道方向）
        
        h = hw + (H0-hw)ln(x/a)/ln(R/a)
        
        参数:
            x: 距廊道中心距离 [m]
        """
        if x <= self.a:
            return self.hw
        elif x >= self.R:
            return self.H0
        else:
            h = self.hw + (self.H0 - self.hw) * np.log(x / self.a) / np.log(self.R / self.a)
            return h
    
    def drawdown(self, x: float) -> float:
        """
        任意点降深
        
        s = s0[1 - ln(x/a)/ln(R/a)]
        
        参数:
            x: 距廊道中心距离 [m]
        """
        if x <= self.a:
            return self.s0
        elif x >= self.R:
            return 0
        else:
            s = self.s0 * (1 - np.log(x / self.a) / np.log(self.R / self.a))
            return s
    
    def seepage_velocity(self, x: float) -> float:
        """
        渗流速度
        
        v = q/M（单位长度）
        或 v = q/(M·1)
        
        参数:
            x: 距廊道中心距离 [m]
        """
        q = self.unit_discharge()
        v = q / self.M  # 简化：假设均匀分布
        return v
    
    def compare_with_well(self, r0: float) -> dict:
        """
        与井流对比
        
        参数:
            r0: 假设井半径 [m]
        
        返回:
            对比字典
        """
        # 廊道单位长度流量
        q_gallery = self.unit_discharge()
        
        # 井流量（相同条件）
        Q_well = 2 * np.pi * self.K * self.M * self.s0 / np.log(self.R / r0)
        
        # 等效：廊道多长相当于一口井
        L_equiv = Q_well / q_gallery
        
        comparison = {
            'q_gallery': q_gallery,
            'Q_well': Q_well,
            'L_equiv': L_equiv,
            'r0': r0,
        }
        
        return comparison
    
    def width_effect(self, a_range: tuple = (0.5, 3)) -> Tuple[np.ndarray, np.ndarray]:
        """
        廊道半宽影响
        
        参数:
            a_range: 半宽范围 [m]
        
        返回:
            a_array: 半宽数组
            q_array: 单位流量数组
        """
        a_array = np.linspace(a_range[0], a_range[1], 50)
        q_array = 2 * self.K * self.M * (self.H0 - self.hw) / np.log(self.R / a_array)
        
        return a_array, q_array
    
    def drawdown_curve(self, n_points: int = 100) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        水位降深曲线
        
        返回:
            x_array: 距离数组
            h_array: 水位数组
            s_array: 降深数组
        """
        x_array = np.logspace(np.log10(self.a), np.log10(self.R), n_points)
        
        h_array = np.array([self.water_head(x) for x in x_array])
        s_array = np.array([self.drawdown(x) for x in x_array])
        
        return x_array, h_array, s_array
    
    def plot_analysis(self):
        """绘制完整分析图表（9个子图）"""
        fig = plt.figure(figsize=(16, 12))
        
        # 计算关键参数
        q = self.unit_discharge()
        Q = self.total_discharge()
        
        # 1. 集水廊道示意图（俯视图+剖面图）
        ax1 = plt.subplot(3, 3, 1)
        ax1.axis('off')
        
        # 俯视图（上半部分）
        ax1.text(0.5, 0.95, '俯视图', ha='center', fontsize=10, fontweight='bold', transform=ax1.transAxes)
        
        # 廊道
        ax1.fill_between([0.2, 0.8], [0.75, 0.75], [0.8, 0.8], color='gray', alpha=0.7, transform=ax1.transAxes)
        ax1.text(0.5, 0.775, f'集水廊道\n(宽2a={2*self.a}m)', ha='center', va='center',
                fontsize=8, transform=ax1.transAxes, color='white', fontweight='bold')
        
        # 影响范围
        for y in [0.65, 0.9]:
            ax1.plot([0.2, 0.8], [y, y], 'b--', alpha=0.3, transform=ax1.transAxes)
        ax1.text(0.1, 0.775, f'R={self.R}m', fontsize=8, transform=ax1.transAxes, rotation=90, va='center')
        
        # 长度标注
        ax1.annotate('', xy=(0.8, 0.7), xytext=(0.2, 0.7),
                    arrowprops=dict(arrowstyle='<->', color='red', lw=1.5), transform=ax1.transAxes)
        ax1.text(0.5, 0.68, f'L={self.L}m', ha='center', fontsize=9, color='red',
                fontweight='bold', transform=ax1.transAxes)
        
        # 剖面图（下半部分）
        ax1.text(0.5, 0.55, '剖面图（AA\'）', ha='center', fontsize=10, fontweight='bold', transform=ax1.transAxes)
        
        # 含水层
        ax1.fill_between([0.1, 0.9], [0.05, 0.05], [0.35, 0.35], color='lightblue', alpha=0.3, transform=ax1.transAxes)
        
        # 隔水层
        ax1.fill_between([0.1, 0.9], [0.02, 0.02], [0.05, 0.05], color='gray', alpha=0.5, transform=ax1.transAxes)
        ax1.fill_between([0.1, 0.9], [0.35, 0.35], [0.38, 0.38], color='gray', alpha=0.5, transform=ax1.transAxes)
        
        # 廊道
        廊道_x = [0.48, 0.48, 0.52, 0.52]
        廊道_y = [0.05, 0.25, 0.25, 0.05]
        ax1.fill(廊道_x, 廊道_y, color='gray', alpha=0.7, transform=ax1.transAxes)
        ax1.text(0.5, 0.15, '廊道', ha='center', va='center', fontsize=8, color='white',
                fontweight='bold', transform=ax1.transAxes)
        
        # 水位线
        x_water = np.array([0.1, 0.3, 0.48, 0.52, 0.7, 0.9])
        y_water = np.array([0.35, 0.32, 0.25, 0.25, 0.32, 0.35])
        ax1.plot(x_water, y_water, 'b-', linewidth=2, transform=ax1.transAxes)
        
        # 初始水位
        ax1.plot([0.1, 0.9], [0.35, 0.35], 'b--', linewidth=1, alpha=0.5, transform=ax1.transAxes)
        ax1.text(0.92, 0.35, 'H₀', fontsize=9, color='blue', transform=ax1.transAxes)
        
        # 廊道水位
        ax1.plot([0.48, 0.52], [0.25, 0.25], 'r-', linewidth=2, transform=ax1.transAxes)
        ax1.text(0.54, 0.25, 'hw', fontsize=9, color='red', fontweight='bold', transform=ax1.transAxes)
        
        ax1.set_title('集水廊道示意图', fontsize=12, fontweight='bold')
        
        # 2. 计算流程
        ax2 = plt.subplot(3, 3, 2)
        ax2.axis('off')
        
        steps = [
            '【集水廊道计算】',
            '',
            '① 基本参数',
            f'含水层厚度: M = {self.M} m',
            f'渗透系数: K = {self.K} m/s',
            f'廊道半宽: a = {self.a} m',
            f'降深: s₀ = {self.s0} m',
            f'影响半径: R = {self.R} m',
            f'廊道长度: L = {self.L} m',
            '',
            '② 单位长度流量',
            'q = 2KM(H₀-hw)/ln(R/a)',
            f'  = 2×{self.K}×{self.M}×{self.s0}',
            f'    /ln({self.R}/{self.a})',
            f'  = {q:.6f} m²/s',
            f'  = {q*1000:.3f} L/(s·m)',
            '',
            '③ 总流量',
            'Q = q×L',
            f'  = {q:.6f}×{self.L}',
            f'  = {Q:.6f} m³/s',
            f'  = {Q*1000:.2f} L/s',
        ]
        
        y_pos = 0.98
        for line in steps:
            if '【' in line:
                ax2.text(0.5, y_pos, line, fontsize=11, fontweight='bold',
                        horizontalalignment='center', verticalalignment='top',
                        color='darkblue')
            elif line.startswith('①') or line.startswith('②') or line.startswith('③'):
                ax2.text(0.05, y_pos, line, fontsize=10, fontweight='bold',
                        verticalalignment='top', color='darkred')
            elif line == '':
                y_pos -= 0.01
                continue
            else:
                ax2.text(0.1, y_pos, line, fontsize=9, verticalalignment='top',
                        family='monospace')
            y_pos -= 0.032
        
        ax2.set_title('计算流程', fontsize=12, fontweight='bold')
        
        # 3. 水位降深曲线
        ax3 = plt.subplot(3, 3, 3)
        
        x_arr, h_arr, s_arr = self.drawdown_curve()
        
        ax3_twin = ax3.twinx()
        
        line1 = ax3.plot(x_arr, h_arr, 'b-', linewidth=2, label='水位h')
        ax3.axhline(self.H0, color='b', linestyle='--', alpha=0.5, label=f'H₀={self.H0}m')
        ax3.axhline(self.hw, color='r', linestyle=':', alpha=0.5, label=f'hw={self.hw}m')
        
        line2 = ax3_twin.plot(x_arr, s_arr, 'r-', linewidth=2, label='降深s')
        
        ax3.set_xlabel('距廊道中心距离 x (m)', fontsize=11)
        ax3.set_ylabel('水位 h (m)', fontsize=11, color='b')
        ax3_twin.set_ylabel('降深 s (m)', fontsize=11, color='r')
        ax3.set_title('水位降深曲线', fontsize=12, fontweight='bold')
        ax3.set_xscale('log')
        ax3.tick_params(axis='y', labelcolor='b')
        ax3_twin.tick_params(axis='y', labelcolor='r')
        ax3.grid(True, alpha=0.3, which='both')
        
        lines = line1 + line2
        labels = [l.get_label() for l in lines[:2]] + [line2[0].get_label()]
        ax3.legend(lines[:2], labels[:2], fontsize=9, loc='upper left')
        ax3_twin.legend([line2[0]], [labels[2]], fontsize=9, loc='upper right')
        
        # 4. 与井流对比
        ax4 = plt.subplot(3, 3, 4)
        
        # 对比（假设井半径r0=0.2m）
        comp = self.compare_with_well(r0=0.2)
        
        items = ['廊道\n(单位长度)', f'井\n(r₀={comp["r0"]}m)', f'廊道×{self.L}m']
        values = [comp['q_gallery']*1000, comp['Q_well']*1000, Q*1000]
        colors = ['lightblue', 'lightcoral', 'lightgreen']
        
        bars = ax4.bar(items, values, color=colors, alpha=0.7, edgecolor='black')
        ax4.set_ylabel('流量 (L/s)', fontsize=11)
        ax4.set_title('廊道 vs 井流对比', fontsize=12, fontweight='bold')
        ax4.grid(True, alpha=0.3, axis='y')
        
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2, height,
                    f'{val:.2f}', ha='center', va='bottom',
                    fontsize=10, fontweight='bold')
        
        # 标注等效长度
        ax4.text(0.5, max(values)*0.6, 
                f'1口井 ≈ {comp["L_equiv"]:.1f}m廊道',
                ha='center', fontsize=10, color='darkgreen', fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7),
                transform=ax4.transAxes)
        
        # 5. 廊道半宽影响
        ax5 = plt.subplot(3, 3, 5)
        
        a_arr, q_arr = self.width_effect()
        
        ax5.plot(a_arr, q_arr*1000, 'b-', linewidth=2, label='单位流量q')
        
        # 当前点
        ax5.plot(self.a, q*1000, 'ro', markersize=12, label=f'当前a={self.a}m')
        
        ax5.set_xlabel('廊道半宽 a (m)', fontsize=11)
        ax5.set_ylabel('单位流量 q (L/(s·m))', fontsize=11)
        ax5.set_title('廊道半宽a的影响', fontsize=12, fontweight='bold')
        ax5.legend(fontsize=9)
        ax5.grid(True, alpha=0.3)
        
        # 6. 廊道长度影响
        ax6 = plt.subplot(3, 3, 6)
        
        L_array = np.linspace(50, 200, 50)
        Q_array = q * L_array
        
        ax6.plot(L_array, Q_array*1000, 'g-', linewidth=2, label='总流量Q')
        
        # 当前点
        ax6.plot(self.L, Q*1000, 'ro', markersize=12, label=f'当前L={self.L}m')
        
        ax6.set_xlabel('廊道长度 L (m)', fontsize=11)
        ax6.set_ylabel('总流量 Q (L/s)', fontsize=11)
        ax6.set_title('廊道长度L的影响', fontsize=12, fontweight='bold')
        ax6.legend(fontsize=9)
        ax6.grid(True, alpha=0.3)
        
        # 7. 不同位置水位对比
        ax7 = plt.subplot(3, 3, 7)
        
        x_positions = [self.a, 5, 10, 30, 50, 100]
        h_positions = [self.water_head(x) for x in x_positions]
        s_positions = [self.drawdown(x) for x in x_positions]
        
        x_idx = np.arange(len(x_positions))
        width = 0.35
        
        bars1 = ax7.bar(x_idx - width/2, h_positions, width, label='水位h',
                       color='lightblue', alpha=0.7, edgecolor='black')
        bars2 = ax7.bar(x_idx + width/2, s_positions, width, label='降深s',
                       color='lightcoral', alpha=0.7, edgecolor='black')
        
        ax7.set_ylabel('高度 (m)', fontsize=11)
        ax7.set_xlabel('位置', fontsize=11)
        ax7.set_title('不同位置水位对比', fontsize=12, fontweight='bold')
        ax7.set_xticks(x_idx)
        ax7.set_xticklabels([f'{x:.0f}m' for x in x_positions])
        ax7.legend(fontsize=9)
        ax7.grid(True, alpha=0.3, axis='y')
        
        # 添加数值标注
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                if height > 0.5:  # 只标注较大的值
                    ax7.text(bar.get_x() + bar.get_width()/2, height,
                            f'{height:.1f}', ha='center', va='bottom', fontsize=8)
        
        # 8. 集水效率分析
        ax8 = plt.subplot(3, 3, 8)
        ax8.axis('off')
        
        efficiency = [
            '【集水效率分析】',
            '',
            '廊道优势:',
            f'• 单位长度: q={q*1000:.3f} L/(s·m)',
            f'• 总流量: Q={Q*1000:.2f} L/s',
            f'• 等效井数: {Q/comp["Q_well"]:.1f}口',
            '',
            '与井对比:',
            f'• 1口井: {comp["Q_well"]*1000:.2f} L/s',
            f'• 等效长度: {comp["L_equiv"]:.1f}m廊道',
            f'• 廊道/井: {comp["q_gallery"]/comp["Q_well"]*self.L:.1f}倍',
            '',
            '经济性:',
            '• 廊道：连续取水',
            '• 井：点状取水',
            '• 廊道适合：长距离',
            '• 井适合：分散点',
            '',
            '工程应用:',
            '• 河道集水廊道',
            '• 堤防渗漏排水',
            '• 基坑降水（沟渠）',
        ]
        
        y_pos = 0.98
        for line in efficiency:
            if '【' in line:
                ax8.text(0.5, y_pos, line, fontsize=11, fontweight='bold',
                        horizontalalignment='center', verticalalignment='top',
                        color='darkblue')
            elif line.endswith(':'):
                ax8.text(0.05, y_pos, line, fontsize=10, fontweight='bold',
                        verticalalignment='top', color='darkred')
            elif line.startswith('•'):
                ax8.text(0.1, y_pos, line, fontsize=9, verticalalignment='top',
                        family='monospace')
            elif line == '':
                y_pos -= 0.01
                continue
            else:
                ax8.text(0.1, y_pos, line, fontsize=9, verticalalignment='top',
                        family='monospace')
            y_pos -= 0.035
        
        ax8.set_title('集水效率分析', fontsize=12, fontweight='bold')
        
        # 9. 结果汇总
        ax9 = plt.subplot(3, 3, 9)
        ax9.axis('off')
        
        summary = [
            '═══ 集水廊道计算结果 ═══',
            '',
            '【基本参数】',
            f'含水层厚度: M = {self.M} m',
            f'渗透系数: K = {self.K} m/s',
            f'廊道半宽: a = {self.a} m',
            f'降深: s₀ = {self.s0} m',
            f'影响半径: R = {self.R} m',
            '',
            '【计算结果】',
            f'单位流量: q = {q:.6f} m²/s',
            f'          = {q*1000:.3f} L/(s·m)',
            f'总流量(L={self.L}m):',
            f'  Q = {Q:.6f} m³/s',
            f'  = {Q*1000:.2f} L/s',
            '',
            '【公式】',
            'q = 2KM(H₀-hw)/ln(R/a)',
            'Q = q×L',
            'h = hw+(H₀-hw)ln(x/a)/ln(R/a)',
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
            y_pos -= 0.034
        
        ax9.set_title('结果汇总', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('/tmp/ch07_problem09_gallery.png', dpi=150, bbox_inches='tight')
        print(f"图表已保存: /tmp/ch07_problem09_gallery.png")
        plt.show()
    
    def print_results(self):
        """打印计算结果"""
        print("\n" + "="*70)
        print("第07章 地下水动力学 - 题9：集水廊道")
        print("="*70)
        
        # 基本参数
        print(f"\n【已知条件】")
        print(f"含水层厚度: M = {self.M} m")
        print(f"渗透系数: K = {self.K} m/s = {self.K*86400} m/d")
        print(f"廊道半宽: a = {self.a} m（宽度2a = {2*self.a} m）")
        print(f"降深: s₀ = {self.s0} m")
        print(f"影响半径: R = {self.R} m")
        print(f"廊道长度: L = {self.L} m")
        
        # (1) 单位长度流量
        print(f"\n【问题1】单位长度廊道流量")
        
        q = self.unit_discharge()
        
        print(f"\n集水廊道公式:")
        print(f"q = 2KM(H₀-hw)/ln(R/a)")
        
        print(f"\n特点:")
        print(f"• q是单位长度流量，单位：m²/s 或 L/(s·m)")
        print(f"• 类似井流公式，半宽a代替半径r₀")
        print(f"• 没有2π（井是圆形，廊道是线形）")
        
        print(f"\n代入数值:")
        print(f"q = 2 × {self.K} × {self.M} × {self.s0} / ln({self.R} / {self.a})")
        print(f"  = 2 × {self.K} × {self.M} × {self.s0} / ln({self.R / self.a:.2f})")
        print(f"  = 2 × {self.K} × {self.M} × {self.s0} / {np.log(self.R / self.a):.4f}")
        print(f"  = {q:.6f} m²/s")
        print(f"  = {q*1000:.3f} L/(s·m)")
        print(f"  = {q*86400:.2f} m²/d")
        
        print(f"\n物理意义:")
        print(f"• 每米长度廊道的流量")
        print(f"• 单位：m²/s = (m³/s)/m")
        
        print(f"\n✓ 单位长度流量: q = {q:.6f} m²/s = {q*1000:.3f} L/(s·m)")
        
        # (2) 总流量
        print(f"\n【问题2】总流量")
        
        Q = self.total_discharge()
        
        print(f"\n总流量公式:")
        print(f"Q = q × L")
        print(f"  = {q:.6f} × {self.L}")
        print(f"  = {Q:.6f} m³/s")
        print(f"  = {Q*1000:.2f} L/s")
        print(f"  = {Q*86400:.2f} m³/d")
        
        print(f"\n✓ 总流量: Q = {Q:.6f} m³/s = {Q*1000:.2f} L/s")
        
        # (3) 任意点水位
        print(f"\n【问题3】任意点水位分布")
        
        print(f"\n水位公式:")
        print(f"h = hw + (H₀-hw) × ln(x/a) / ln(R/a)")
        
        print(f"\n特征:")
        print(f"• 对数分布（类似承压水井流）")
        print(f"• x是距廊道中心的垂直距离")
        
        positions = [2, 5, 10, 30, 50, 100]
        
        print(f"\n典型位置水位:")
        print(f"{'距离(m)':<10} {'水位h(m)':<12} {'降深s(m)':<12}")
        print(f"{'-'*40}")
        
        for x in positions:
            if self.a <= x <= self.R:
                h = self.water_head(x)
                s = self.drawdown(x)
                print(f"{x:<10} {h:<12.2f} {s:<12.2f}")
        
        # (4) 与井流对比
        print(f"\n【问题4】与井流的对比")
        
        comp = self.compare_with_well(r0=0.2)
        
        print(f"\n假设井半径r₀ = {comp['r0']} m:")
        
        print(f"\n廊道（单位长度）:")
        print(f"q = 2KM(H₀-hw)/ln(R/a) = {comp['q_gallery']*1000:.3f} L/(s·m)")
        
        print(f"\n井流:")
        print(f"Q = 2πKM(H₀-hw)/ln(R/r₀) = {comp['Q_well']*1000:.2f} L/s")
        
        print(f"\n等效关系:")
        print(f"1口井 ≈ {comp['L_equiv']:.1f}m廊道")
        print(f"或：{self.L}m廊道 ≈ {Q/comp['Q_well']:.1f}口井")
        
        print(f"\n公式对比:")
        print(f"{'类型':<15} {'公式':<45} {'特点':<15}")
        print(f"{'-'*75}")
        print(f"{'廊道（单位长度）':<15} {'q = 2KM(H₀-hw)/ln(R/a)':<45} {'线状集水':<15}")
        print(f"{'井流':<15} {'Q = 2πKM(H₀-hw)/ln(R/r₀)':<45} {'点状集水':<15}")
        
        print(f"\n关键区别:")
        print(f"• 廊道：系数2，半宽a，单位长度")
        print(f"• 井：系数2π，半径r₀，总流量")
        print(f"• 廊道是线状，井是点状")
        
        # (5) 廊道半宽影响
        print(f"\n【问题5】廊道半宽影响")
        
        print(f"\n影响规律:")
        print(f"• q = 2KM(H₀-hw)/ln(R/a)")
        print(f"• a增大，ln(R/a)减小，q增大")
        print(f"• 但影响较小（对数关系）")
        
        a_test = [0.5, 1.0, 1.5, 2.0, 3.0]
        print(f"\n不同a值的单位流量:")
        print(f"{'a(m)':<10} {'宽度2a(m)':<12} {'q(L/(s·m))':<15}")
        print(f"{'-'*40}")
        
        for a_val in a_test:
            q_val = 2 * self.K * self.M * self.s0 / np.log(self.R / a_val)
            marker = ' ◀' if a_val == self.a else ''
            print(f"{a_val:<10} {2*a_val:<12} {q_val*1000:<15.3f}{marker}")
        
        # 考试要点
        print(f"\n【考试要点】")
        print(f"1. 单位流量: q = 2KM(H₀-hw)/ln(R/a)")
        print(f"2. 总流量: Q = q×L")
        print(f"3. 水位分布: h = hw+(H₀-hw)ln(x/a)/ln(R/a)")
        print(f"4. 廊道vs井: 线状vs点状")
        print(f"5. 等效关系: 1井 ≈ 若干米廊道")
        print(f"6. 廊道优势: 连续取水，长距离")
        print(f"7. 工程应用: 河道集水、基坑降水")
        
        print(f"\n{'='*70}\n")


def main():
    """主函数"""
    
    print("集水廊道分析")
    print("-" * 70)
    
    # 系统参数
    M = 12  # 含水层厚度 [m]
    K = 0.0015  # 渗透系数 [m/s]
    a = 1  # 廊道半宽 [m]
    s0 = 6  # 降深 [m]
    R = 150  # 影响半径 [m]
    L = 100  # 廊道长度 [m]
    
    # 创建分析实例
    gallery = Gallery(M, K, a, s0, R, L)
    
    # 打印结果
    gallery.print_results()
    
    # 绘制分析图
    gallery.plot_analysis()


if __name__ == "__main__":
    main()
