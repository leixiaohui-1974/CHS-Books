# -*- coding: utf-8 -*-
"""
第07章 地下水动力学 - 题6：无压水井流

问题描述：
    某无压含水层（潜水层），初始水位H0 = 20m
    抽水井半径：r0 = 0.2m
    井中水位：hw = 10m
    影响半径：R = 200m
    渗透系数：K = 0.002 m/s
    
    求：
    1. 井流量（稳定流）
    2. 任意点水位
    3. 水位曲线（抛物线）
    4. 渗流速度分布
    5. 与承压水的对比
    6. 渗透系数影响

核心公式：
    1. Dupuit公式（无压水）：Q = πK(H0²-hw²)/ln(R/r0)
    2. 任意点水位：h² = hw² + (H0²-hw²)ln(r/r0)/ln(R/r0)
    3. 渗流速度：v = Q/(2πrh)
    4. 水位曲线：抛物线（vs承压水对数曲线）

考试要点：
    - 无压水vs承压水Dupuit公式区别
    - 水位曲线：抛物线vs对数曲线
    - 渗流速度：v∝1/(r·h)
    - 无压水井流更复杂（厚度变化）

作者: CHS-Books Team
日期: 2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class UnconfinedWell:
    """无压水井流分析"""
    
    def __init__(self, H0: float, K: float, r0: float, hw: float, R: float):
        """
        初始化参数
        
        参数:
            H0: 初始水位（潜水面）[m]
            K: 渗透系数 [m/s]
            r0: 抽水井半径 [m]
            hw: 井中水位 [m]
            R: 影响半径 [m]
        """
        self.H0 = H0
        self.K = K
        self.r0 = r0
        self.hw = hw
        self.R = R
        
        # 降深
        self.s0 = H0 - hw
        
    def well_discharge(self) -> float:
        """
        井流量（Dupuit公式 - 无压水）
        
        Q = πK(H0²-hw²)/ln(R/r0)
        """
        Q = np.pi * self.K * (self.H0**2 - self.hw**2) / np.log(self.R / self.r0)
        return Q
    
    def water_level(self, r: float) -> float:
        """
        任意点水位
        
        h² = hw² + (H0²-hw²)ln(r/r0)/ln(R/r0)
        
        参数:
            r: 距井中心距离 [m]
        """
        if r <= self.r0:
            return self.hw
        elif r >= self.R:
            return self.H0
        else:
            h_squared = self.hw**2 + (self.H0**2 - self.hw**2) * np.log(r / self.r0) / np.log(self.R / self.r0)
            h = np.sqrt(h_squared)
            return h
    
    def drawdown(self, r: float) -> float:
        """
        任意点降深
        
        s = H0 - h
        
        参数:
            r: 距井中心距离 [m]
        """
        h = self.water_level(r)
        s = self.H0 - h
        return s
    
    def seepage_velocity(self, r: float) -> float:
        """
        渗流速度
        
        v = Q/(2πrh)
        
        参数:
            r: 距井中心距离 [m]
        """
        Q = self.well_discharge()
        h = self.water_level(r)
        v = Q / (2 * np.pi * r * h)
        return v
    
    def permeability_effect(self, K_range: tuple = (0.0001, 0.01)) -> Tuple[np.ndarray, np.ndarray]:
        """
        渗透系数影响
        
        参数:
            K_range: 渗透系数范围 [m/s]
        
        返回:
            K_array: 渗透系数数组
            Q_array: 流量数组
        """
        K_array = np.linspace(K_range[0], K_range[1], 50)
        Q_array = np.pi * K_array * (self.H0**2 - self.hw**2) / np.log(self.R / self.r0)
        
        return K_array, Q_array
    
    def drawdown_curve(self, n_points: int = 100) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        水位曲线（抛物线）
        
        返回:
            r_array: 距离数组
            h_array: 水位数组
            s_array: 降深数组
        """
        r_array = np.logspace(np.log10(self.r0), np.log10(self.R), n_points)
        
        h_array = np.array([self.water_level(r) for r in r_array])
        s_array = self.H0 - h_array
        
        return r_array, h_array, s_array
    
    def compare_with_confined(self, M: float) -> dict:
        """
        与承压水对比
        
        参数:
            M: 假设承压含水层厚度（取H0） [m]
        
        返回:
            对比字典
        """
        # 无压水流量
        Q_unconf = self.well_discharge()
        
        # 承压水流量（相同条件）
        Q_conf = 2 * np.pi * self.K * M * self.s0 / np.log(self.R / self.r0)
        
        # 对比
        comparison = {
            'Q_unconfined': Q_unconf,
            'Q_confined': Q_conf,
            'ratio': Q_unconf / Q_conf,
            'M': M,
        }
        
        return comparison
    
    def velocity_distribution(self, n_points: int = 50) -> Tuple[np.ndarray, np.ndarray]:
        """
        渗流速度分布
        
        返回:
            r_array: 距离数组
            v_array: 速度数组
        """
        r_array = np.logspace(np.log10(self.r0), np.log10(self.R), n_points)
        v_array = np.array([self.seepage_velocity(r) for r in r_array])
        
        return r_array, v_array
    
    def plot_analysis(self):
        """绘制完整分析图表（9个子图）"""
        fig = plt.figure(figsize=(16, 12))
        
        # 计算关键参数
        Q = self.well_discharge()
        
        # 1. 无压水井流示意图
        ax1 = plt.subplot(3, 3, 1)
        
        # 含水层底部
        ax1.fill_between([0, 4], [-2, -2], [0, 0], color='gray', alpha=0.5, label='隔水层')
        
        # 含水层
        r_arr, h_arr, _ = self.drawdown_curve()
        x_left = 2 - r_arr / (self.R / 2)
        x_right = 2 + r_arr / (self.R / 2)
        
        # 水位曲线（抛物线）
        ax1.fill_between(x_left, 0, h_arr, color='lightblue', alpha=0.3)
        ax1.fill_between(x_right, 0, h_arr, color='lightblue', alpha=0.3, label='含水层')
        ax1.plot(x_left, h_arr, 'b-', linewidth=2)
        ax1.plot(x_right, h_arr, 'b-', linewidth=2, label='水位曲线(抛物线)')
        
        # 抽水井
        ax1.plot([2, 2], [0, self.hw], 'k-', linewidth=5, label='抽水井')
        ax1.plot([2, 2], [self.hw, self.H0], 'b--', linewidth=2)
        
        # 初始水位线
        ax1.axhline(self.H0, color='blue', linestyle='--', linewidth=1, alpha=0.5)
        ax1.text(0.5, self.H0+0.5, f'H₀={self.H0}m', fontsize=10, color='blue')
        
        # 井中水位
        ax1.axhline(self.hw, color='red', linestyle=':', linewidth=1.5)
        ax1.text(2.3, self.hw, f'hw={self.hw}m', fontsize=10, color='red', fontweight='bold')
        
        # 降深标注
        ax1.annotate('', xy=(0.8, self.hw), xytext=(0.8, self.H0),
                    arrowprops=dict(arrowstyle='<->', color='red', lw=1.5))
        ax1.text(0.5, (self.H0+self.hw)/2, f's₀={self.s0}m', fontsize=10, color='red', fontweight='bold')
        
        ax1.set_xlim(0, 4)
        ax1.set_ylim(-3, self.H0+2)
        ax1.set_aspect('equal')
        ax1.axis('off')
        ax1.set_title('无压水井流示意图', fontsize=12, fontweight='bold')
        ax1.legend(fontsize=9, loc='upper left')
        
        # 2. Dupuit公式计算（无压水）
        ax2 = plt.subplot(3, 3, 2)
        ax2.axis('off')
        
        steps = [
            '【Dupuit公式（无压水）】',
            '',
            '无压水特点:',
            '• 自由水面（潜水面）',
            '• 厚度随抽水变化',
            '• h²而非h',
            '',
            '① 基本参数',
            f'初始水位: H₀ = {self.H0} m',
            f'井中水位: hw = {self.hw} m',
            f'井半径: r₀ = {self.r0} m',
            f'影响半径: R = {self.R} m',
            f'渗透系数: K = {self.K} m/s',
            '',
            '② 井流量公式',
            'Q = πK(H₀²-hw²)/ln(R/r₀)',
            '',
            f'  = π×{self.K}×({self.H0}²-{self.hw}²)',
            f'    /ln({self.R}/{self.r0})',
            '',
            f'  = {Q:.6f} m³/s',
            f'  = {Q*1000:.3f} L/s',
        ]
        
        y_pos = 0.98
        for line in steps:
            if '【' in line:
                ax2.text(0.5, y_pos, line, fontsize=11, fontweight='bold',
                        horizontalalignment='center', verticalalignment='top',
                        color='darkblue')
            elif line.startswith('①') or line.startswith('②'):
                ax2.text(0.05, y_pos, line, fontsize=10, fontweight='bold',
                        verticalalignment='top', color='darkred')
            elif line.startswith('•'):
                ax2.text(0.1, y_pos, line, fontsize=9, verticalalignment='top',
                        color='darkgreen')
            elif line == '':
                y_pos -= 0.01
                continue
            else:
                ax2.text(0.1, y_pos, line, fontsize=9, verticalalignment='top',
                        family='monospace')
            y_pos -= 0.032
        
        ax2.set_title('计算流程', fontsize=12, fontweight='bold')
        
        # 3. 水位曲线（抛物线）
        ax3 = plt.subplot(3, 3, 3)
        
        r_arr, h_arr, s_arr = self.drawdown_curve()
        
        ax3_twin = ax3.twinx()
        
        line1 = ax3.plot(r_arr, h_arr, 'b-', linewidth=2, label='水位h (抛物线)')
        ax3.axhline(self.H0, color='b', linestyle='--', alpha=0.5, label=f'H₀={self.H0}m')
        ax3.axhline(self.hw, color='r', linestyle=':', alpha=0.5, label=f'hw={self.hw}m')
        
        line2 = ax3_twin.plot(r_arr, s_arr, 'r-', linewidth=2, label='降深s')
        
        ax3.set_xlabel('距离 r (m)', fontsize=11)
        ax3.set_ylabel('水位 h (m)', fontsize=11, color='b')
        ax3_twin.set_ylabel('降深 s (m)', fontsize=11, color='r')
        ax3.set_title('水位曲线（抛物线）', fontsize=12, fontweight='bold')
        ax3.set_xscale('log')
        ax3.tick_params(axis='y', labelcolor='b')
        ax3_twin.tick_params(axis='y', labelcolor='r')
        ax3.grid(True, alpha=0.3, which='both')
        
        lines = line1 + line2
        labels = [l.get_label() for l in lines[:2]] + [line2[0].get_label()]
        ax3.legend(lines[:2], labels[:2], fontsize=9, loc='upper left')
        ax3_twin.legend([line2[0]], [labels[2]], fontsize=9, loc='upper right')
        
        # 4. 渗流速度分布
        ax4 = plt.subplot(3, 3, 4)
        
        r_arr2, v_arr = self.velocity_distribution()
        
        ax4.plot(r_arr2, v_arr*1000, 'g-', linewidth=2, label='渗流速度v')
        
        # 理论趋势
        ax4.set_xlabel('距离 r (m)', fontsize=11)
        ax4.set_ylabel('渗流速度 v (mm/s)', fontsize=11)
        ax4.set_title('渗流速度分布 v∝1/(r·h)', fontsize=12, fontweight='bold')
        ax4.set_xscale('log')
        ax4.set_yscale('log')
        ax4.legend(fontsize=9)
        ax4.grid(True, alpha=0.3, which='both')
        
        # 5. 与承压水对比
        ax5 = plt.subplot(3, 3, 5)
        
        # 计算承压水（M=H0）
        comp = self.compare_with_confined(self.H0)
        
        # 流量对比
        cases = ['无压水\n(潜水)', '承压水\n(假设M=H₀)']
        flows = [comp['Q_unconfined']*1000, comp['Q_confined']*1000]
        colors = ['lightblue', 'lightcoral']
        
        bars = ax5.bar(cases, flows, color=colors, alpha=0.7, edgecolor='black')
        ax5.set_ylabel('流量 (L/s)', fontsize=11)
        ax5.set_title('无压水 vs 承压水流量对比', fontsize=12, fontweight='bold')
        ax5.grid(True, alpha=0.3, axis='y')
        
        for bar, val in zip(bars, flows):
            height = bar.get_height()
            ax5.text(bar.get_x() + bar.get_width()/2, height,
                    f'{val:.3f}', ha='center', va='bottom',
                    fontsize=10, fontweight='bold')
        
        # 标注比值
        ratio = comp['ratio']
        ax5.text(0.5, max(flows)*0.5, f'Q无压/Q承压={ratio:.2f}',
                ha='center', fontsize=10, color='darkgreen', fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))
        
        # 6. 水位曲线形状对比
        ax6 = plt.subplot(3, 3, 6)
        
        # 无压水曲线
        r_plot = np.logspace(np.log10(self.r0), np.log10(self.R), 100)
        h_unconf = np.array([self.water_level(r) for r in r_plot])
        
        # 假设承压水曲线（对数）
        h_conf = self.hw + (self.H0 - self.hw) * np.log(r_plot / self.r0) / np.log(self.R / self.r0)
        
        ax6.plot(r_plot, h_unconf, 'b-', linewidth=2, label='无压水(抛物线)')
        ax6.plot(r_plot, h_conf, 'r--', linewidth=2, label='承压水(对数)')
        
        ax6.axhline(self.H0, color='gray', linestyle=':', alpha=0.5)
        ax6.axhline(self.hw, color='gray', linestyle=':', alpha=0.5)
        
        ax6.set_xlabel('距离 r (m)', fontsize=11)
        ax6.set_ylabel('水位 h (m)', fontsize=11)
        ax6.set_title('水位曲线形状对比', fontsize=12, fontweight='bold')
        ax6.set_xscale('log')
        ax6.legend(fontsize=9)
        ax6.grid(True, alpha=0.3, which='both')
        
        # 7. 渗透系数K的影响
        ax7 = plt.subplot(3, 3, 7)
        
        K_arr, Q_arr = self.permeability_effect()
        
        ax7.plot(K_arr*1000, Q_arr*1000, 'b-', linewidth=2, label='流量Q')
        
        # 当前点
        ax7.plot(self.K*1000, Q*1000, 'ro', markersize=12, label=f'当前K={self.K}m/s')
        
        ax7.set_xlabel('渗透系数 K (mm/s)', fontsize=11)
        ax7.set_ylabel('流量 Q (L/s)', fontsize=11)
        ax7.set_title('渗透系数K的影响', fontsize=12, fontweight='bold')
        ax7.legend(fontsize=9)
        ax7.grid(True, alpha=0.3)
        
        # 8. 关键公式对比
        ax8 = plt.subplot(3, 3, 8)
        ax8.axis('off')
        
        formulas = [
            '【无压水 vs 承压水】',
            '',
            '无压水（潜水）:',
            '• Q = πK(H₀²-hw²)/ln(R/r₀)',
            '• h² = hw²+(H₀²-hw²)ln(r/r₀)/ln(R/r₀)',
            '• 水位: 抛物线分布',
            '• 厚度: h变化',
            '• v = Q/(2πrh)',
            '',
            '承压水:',
            '• Q = 2πKM(H₀-hw)/ln(R/r₀)',
            '• h = hw+(H₀-hw)ln(r/r₀)/ln(R/r₀)',
            '• 水位: 对数分布',
            '• 厚度: M不变',
            '• v = Q/(2πrM)',
            '',
            '关键区别:',
            '• 无压水: H²项，厚度变化',
            '• 承压水: H项，厚度不变',
            '• 无压水更复杂',
        ]
        
        y_pos = 0.98
        for line in formulas:
            if '【' in line:
                ax8.text(0.5, y_pos, line, fontsize=11, fontweight='bold',
                        horizontalalignment='center', verticalalignment='top',
                        color='darkblue')
            elif line.startswith('无压水') or line.startswith('承压水') or line.startswith('关键区别'):
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
            y_pos -= 0.038
        
        ax8.set_title('公式对比', fontsize=12, fontweight='bold')
        
        # 9. 结果汇总
        ax9 = plt.subplot(3, 3, 9)
        ax9.axis('off')
        
        summary = [
            '═══ 无压水井流结果 ═══',
            '',
            '【基本参数】',
            f'初始水位: H₀ = {self.H0} m',
            f'井中水位: hw = {self.hw} m',
            f'降深: s₀ = {self.s0} m',
            f'井半径: r₀ = {self.r0} m',
            f'影响半径: R = {self.R} m',
            f'渗透系数: K = {self.K} m/s',
            '',
            '【计算结果】',
            f'井流量: Q = {Q:.6f} m³/s',
            f'        = {Q*1000:.3f} L/s',
            f'        = {Q*86400:.2f} m³/d',
            '',
            '【水位曲线】',
            '类型: 抛物线',
            f'h²=hw²+(H₀²-hw²)ln(r/r₀)/ln(R/r₀)',
            '',
            '【与承压水对比】',
            f'Q无压/Q承压 = {comp["ratio"]:.2f}',
            '(假设M=H₀)',
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
            y_pos -= 0.036
        
        ax9.set_title('结果汇总', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('/tmp/ch07_problem06_unconfined_well.png', dpi=150, bbox_inches='tight')
        print(f"图表已保存: /tmp/ch07_problem06_unconfined_well.png")
        plt.show()
    
    def print_results(self):
        """打印计算结果"""
        print("\n" + "="*70)
        print("第07章 地下水动力学 - 题6：无压水井流")
        print("="*70)
        
        # 基本参数
        print(f"\n【已知条件】")
        print(f"初始水位: H₀ = {self.H0} m（潜水面）")
        print(f"井中水位: hw = {self.hw} m")
        print(f"降深: s₀ = H₀ - hw = {self.s0} m")
        print(f"井半径: r₀ = {self.r0} m")
        print(f"影响半径: R = {self.R} m")
        print(f"渗透系数: K = {self.K} m/s = {self.K*86400} m/d")
        
        # (1) 井流量
        print(f"\n【问题1】井流量（稳定流）")
        
        Q = self.well_discharge()
        
        print(f"\nDupuit公式（无压水）:")
        print(f"Q = πK(H₀²-hw²)/ln(R/r₀)")
        
        print(f"\n注意：无压水用H²而非H")
        print(f"• 原因：厚度h随位置变化")
        print(f"• 承压水厚度M不变，用H")
        
        print(f"\n代入数值:")
        print(f"Q = π × {self.K} × ({self.H0}² - {self.hw}²) / ln({self.R} / {self.r0})")
        print(f"  = π × {self.K} × ({self.H0**2} - {self.hw**2}) / ln({self.R / self.r0:.2f})")
        print(f"  = π × {self.K} × {self.H0**2 - self.hw**2} / {np.log(self.R / self.r0):.4f}")
        print(f"  = {Q:.6f} m³/s")
        print(f"  = {Q*1000:.3f} L/s")
        print(f"  = {Q*86400:.2f} m³/d")
        
        print(f"\n✓ 井流量: Q = {Q:.6f} m³/s = {Q*1000:.3f} L/s")
        
        # (2) 任意点水位
        print(f"\n【问题2】任意点水位")
        
        print(f"\n水位公式（抛物线）:")
        print(f"h² = hw² + (H₀² - hw²) × ln(r/r₀) / ln(R/r₀)")
        
        print(f"\n特点:")
        print(f"• 抛物线分布（vs 承压水对数分布）")
        print(f"• h²呈线性变化")
        print(f"• 近井梯度大，远井梯度小")
        
        # 几个典型位置
        positions = [1, 5, 10, 50, 100]
        
        print(f"\n典型位置水位:")
        print(f"{'距离(m)':<10} {'水位h(m)':<12} {'降深s(m)':<12} {'厚度h(m)':<12}")
        print(f"{'-'*50}")
        
        for r in positions:
            if self.r0 <= r <= self.R:
                h = self.water_level(r)
                s = self.drawdown(r)
                print(f"{r:<10} {h:<12.2f} {s:<12.2f} {h:<12.2f}")
        
        # (3) 水位曲线
        print(f"\n【问题3】水位曲线（抛物线）")
        
        print(f"\n曲线特征:")
        print(f"• 抛物线：h² = hw² + (H₀²-hw²)ln(r/r₀)/ln(R/r₀)")
        print(f"• 不同于承压水的对数曲线")
        print(f"• 降深更大（因为厚度减小）")
        
        # (4) 渗流速度分布
        print(f"\n【问题4】渗流速度分布")
        
        print(f"\n速度公式:")
        print(f"v = Q/(2πrh)")
        
        print(f"\n特征:")
        print(f"• v ∝ 1/(r·h)")
        print(f"• 不仅反比于r，还反比于h")
        print(f"• 近井处h小，v更大")
        print(f"• 比承压水复杂")
        
        print(f"\n典型位置速度:")
        print(f"{'距离(m)':<10} {'水位h(m)':<12} {'速度v(mm/s)':<15}")
        print(f"{'-'*40}")
        
        for r in positions:
            if self.r0 <= r <= self.R:
                h = self.water_level(r)
                v = self.seepage_velocity(r)
                print(f"{r:<10} {h:<12.2f} {v*1000:<15.4f}")
        
        # (5) 与承压水对比
        print(f"\n【问题5】与承压水的对比")
        
        comp = self.compare_with_confined(self.H0)
        
        print(f"\n流量对比（假设承压水M=H₀={self.H0}m）:")
        print(f"无压水: Q = πK(H₀²-hw²)/ln(R/r₀) = {comp['Q_unconfined']*1000:.3f} L/s")
        print(f"承压水: Q = 2πKM(H₀-hw)/ln(R/r₀) = {comp['Q_confined']*1000:.3f} L/s")
        print(f"比值: Q无压/Q承压 = {comp['ratio']:.3f}")
        
        print(f"\n分析:")
        print(f"• 2(H₀-hw) = 2×{self.s0} = {2*self.s0}")
        print(f"• (H₀²-hw²) = ({self.H0}+{self.hw})×({self.H0}-{self.hw}) = {self.H0+self.hw}×{self.s0} = {(self.H0+self.hw)*self.s0}")
        print(f"• Q无压/Q承压 = (H₀+hw)/(2H₀) = {(self.H0+self.hw)/(2*self.H0):.3f}")
        
        if comp['ratio'] < 1:
            print(f"\n结论: 无压水流量小于承压水（相同条件）")
            print(f"原因: 降深导致厚度减小，过流能力降低")
        else:
            print(f"\n结论: 无压水流量大于承压水（相同条件）")
        
        print(f"\n公式对比:")
        print(f"{'类型':<10} {'公式':<40} {'特点':<20}")
        print(f"{'-'*70}")
        print(f"{'无压水':<10} {'Q = πK(H₀²-hw²)/ln(R/r₀)':<40} {'H²，厚度变化':<20}")
        print(f"{'承压水':<10} {'Q = 2πKM(H₀-hw)/ln(R/r₀)':<40} {'H，厚度不变':<20}")
        
        print(f"\n水位曲线对比:")
        print(f"{'类型':<10} {'形状':<15} {'分布公式':<45}")
        print(f"{'-'*70}")
        print(f"{'无压水':<10} {'抛物线':<15} {'h² ∝ ln(r/r₀)':<45}")
        print(f"{'承压水':<10} {'对数线':<15} {'h ∝ ln(r/r₀)':<45}")
        
        # (6) 渗透系数影响
        print(f"\n【问题6】渗透系数影响")
        
        print(f"\n影响规律:")
        print(f"• Q = πK(H₀²-hw²)/ln(R/r₀)")
        print(f"• Q ∝ K（线性关系）")
        
        K_test = [0.0005, 0.001, 0.002, 0.005, 0.01]
        print(f"\n不同K值的流量:")
        print(f"{'K(m/s)':<12} {'K(m/d)':<12} {'Q(L/s)':<12}")
        print(f"{'-'*40}")
        
        for K_val in K_test:
            Q_val = np.pi * K_val * (self.H0**2 - self.hw**2) / np.log(self.R / self.r0)
            marker = ' ◀' if K_val == self.K else ''
            print(f"{K_val:<12} {K_val*86400:<12.2f} {Q_val*1000:<12.3f}{marker}")
        
        # 考试要点
        print(f"\n【考试要点】")
        print(f"1. 无压水Dupuit: Q = πK(H₀²-hw²)/ln(R/r₀)")
        print(f"2. 承压水Dupuit: Q = 2πKM(H₀-hw)/ln(R/r₀)")
        print(f"3. 关键区别: H²项 vs H项")
        print(f"4. 水位曲线: 抛物线 vs 对数线")
        print(f"5. 厚度: h变化 vs M不变")
        print(f"6. 速度: v=Q/(2πrh) vs v=Q/(2πrM)")
        print(f"7. 无压水更复杂（厚度变化）")
        print(f"8. 降深大→厚度减小→流量减小")
        
        print(f"\n{'='*70}\n")


def main():
    """主函数"""
    
    print("无压水井流分析")
    print("-" * 70)
    
    # 系统参数
    H0 = 20  # 初始水位 [m]
    K = 0.002  # 渗透系数 [m/s]
    r0 = 0.2  # 井半径 [m]
    hw = 10  # 井中水位 [m]
    R = 200  # 影响半径 [m]
    
    # 创建分析实例
    well = UnconfinedWell(H0, K, r0, hw, R)
    
    # 打印结果
    well.print_results()
    
    # 绘制分析图
    well.plot_analysis()


if __name__ == "__main__":
    main()
