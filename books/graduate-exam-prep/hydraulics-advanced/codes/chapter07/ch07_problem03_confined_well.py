# -*- coding: utf-8 -*-
"""
第07章 地下水动力学 - 题3：承压水井流

问题描述：
    某承压含水层，厚度M = 10m，渗透系数K = 0.001 m/s
    抽水井半径：r0 = 0.2m
    井中水位降深：s0 = 5m
    影响半径：R = 200m
    
    求：
    1. 井流量（稳定流）
    2. 任意点水位降深
    3. 水位降深曲线
    4. 渗流速度分布
    5. 影响半径对流量的影响
    6. 井半径对流量的影响

核心公式：
    1. Dupuit公式（承压水）：Q = 2πKM(H0-hw)/ln(R/r0)
    2. 任意点水位：h = hw + (H0-hw)ln(r/r0)/ln(R/r0)
    3. 水位降深：s = s0[1 - ln(r/r0)/ln(R/r0)]
    4. 渗流速度：v = Q/(2πrM)

考试要点：
    - Dupuit公式适用条件（承压水、稳定流）
    - 水位降深呈对数分布
    - 渗流速度反比于半径
    - 影响半径R的确定

作者: CHS-Books Team
日期: 2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple
from scipy.optimize import fsolve

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class ConfinedWell:
    """承压水井流分析"""
    
    def __init__(self, M: float, K: float, r0: float, s0: float, R: float):
        """
        初始化参数
        
        参数:
            M: 含水层厚度 [m]
            K: 渗透系数 [m/s]
            r0: 抽水井半径 [m]
            s0: 井中水位降深 [m]
            R: 影响半径 [m]
        """
        self.M = M
        self.K = K
        self0 = r0
        self.s0 = s0
        self.R = R
        
        # 初始水位（含水层顶面）
        self.H0 = M  # 承压水初始水头等于含水层厚度
        # 井中水位
        self.hw = self.H0 - s0
        
    def well_discharge(self) -> float:
        """
        井流量（Dupuit公式）
        
        Q = 2πKM(H0-hw)/ln(R/r0)
        """
        Q = 2 * np.pi * self.K * self.M * (self.H0 - self.hw) / np.log(self.R / self.r0)
        return Q
    
    def water_head(self, r: float) -> float:
        """
        任意点水位
        
        h = hw + (H0-hw)ln(r/r0)/ln(R/r0)
        
        参数:
            r: 距井中心距离 [m]
        """
        if r <= self.r0:
            return self.hw
        elif r >= self.R:
            return self.H0
        else:
            h = self.hw + (self.H0 - self.hw) * np.log(r / self.r0) / np.log(self.R / self.r0)
            return h
    
    def drawdown(self, r: float) -> float:
        """
        任意点水位降深
        
        s = s0[1 - ln(r/r0)/ln(R/r0)]
        
        参数:
            r: 距井中心距离 [m]
        """
        if r <= self.r0:
            return self.s0
        elif r >= self.R:
            return 0
        else:
            s = self.s0 * (1 - np.log(r / self.r0) / np.log(self.R / self.r0))
            return s
    
    def seepage_velocity(self, r: float) -> float:
        """
        渗流速度
        
        v = Q/(2πrM)
        
        参数:
            r: 距井中心距离 [m]
        """
        Q = self.well_discharge()
        v = Q / (2 * np.pi * r * self.M)
        return v
    
    def influence_radius_effect(self, R_range: tuple = (50, 500)) -> Tuple[np.ndarray, np.ndarray]:
        """
        影响半径对流量的影响
        
        参数:
            R_range: 影响半径范围 [m]
        
        返回:
            R_array: 影响半径数组
            Q_array: 流量数组
        """
        R_array = np.linspace(R_range[0], R_range[1], 50)
        Q_array = 2 * np.pi * self.K * self.M * (self.H0 - self.hw) / np.log(R_array / self.r0)
        
        return R_array, Q_array
    
    def well_radius_effect(self, r0_range: tuple = (0.05, 0.5)) -> Tuple[np.ndarray, np.ndarray]:
        """
        井半径对流量的影响
        
        参数:
            r0_range: 井半径范围 [m]
        
        返回:
            r0_array: 井半径数组
            Q_array: 流量数组
        """
        r0_array = np.linspace(r0_range[0], r0_range[1], 50)
        Q_array = 2 * np.pi * self.K * self.M * (self.H0 - self.hw) / np.log(self.R / r0_array)
        
        return r0_array, Q_array
    
    def drawdown_curve(self, n_points: int = 100) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        水位降深曲线
        
        返回:
            r_array: 距离数组
            h_array: 水位数组
            s_array: 降深数组
        """
        # 对数分布采样点
        r_array = np.logspace(np.log10(self.r0), np.log10(self.R), n_points)
        
        h_array = np.array([self.water_head(r) for r in r_array])
        s_array = np.array([self.drawdown(r) for r in r_array])
        
        return r_array, h_array, s_array
    
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
        
        # 1. 承压水井流示意图
        ax1 = plt.subplot(3, 3, 1)
        
        # 含水层
        ax1.fill_between([0, 4], [-5, -5], [self.M-5, self.M-5], color='lightblue', alpha=0.3, label='含水层')
        
        # 隔水层
        ax1.fill_between([0, 4], [-5.5, -5.5], [-5, -5], color='gray', alpha=0.5, label='隔水层(底)')
        ax1.fill_between([0, 4], [self.M-5, self.M-5], [self.M-4.5, self.M-4.5], color='gray', alpha=0.5, label='隔水层(顶)')
        
        # 抽水井
        ax1.plot([2, 2], [-5, self.hw-5], 'k-', linewidth=5, label='抽水井')
        ax1.plot([2, 2], [self.hw-5, self.M-5], 'b--', linewidth=2)
        
        # 水位线
        r_arr, h_arr, _ = self.drawdown_curve()
        x_left = 2 - r_arr / (self.R / 2)
        x_right = 2 + r_arr / (self.R / 2)
        ax1.plot(x_left, h_arr-5, 'r-', linewidth=2)
        ax1.plot(x_right, h_arr-5, 'r-', linewidth=2, label='水位曲线')
        
        # 初始水位线
        ax1.axhline(self.H0-5, color='blue', linestyle='--', linewidth=1, alpha=0.5)
        ax1.text(0.5, self.H0-4.7, 'H₀', fontsize=10, color='blue')
        
        # 井中水位
        ax1.axhline(self.hw-5, color='red', linestyle=':', linewidth=1.5)
        ax1.text(2.3, self.hw-5, 'hw', fontsize=10, color='red', fontweight='bold')
        
        # 降深标注
        ax1.annotate('', xy=(0.8, self.hw-5), xytext=(0.8, self.H0-5),
                    arrowprops=dict(arrowstyle='<->', color='red', lw=1.5))
        ax1.text(0.5, (self.H0+self.hw)/2-5, f's₀={self.s0}m', fontsize=10, color='red', fontweight='bold')
        
        # 影响半径
        ax1.plot([2, 2+2*self.R/(self.R+50)], [self.M-4, self.M-4], 'g-', linewidth=2)
        ax1.plot([2+2*self.R/(self.R+50), 2+2*self.R/(self.R+50)], [self.M-4.2, self.M-3.8], 'g-', linewidth=2)
        ax1.text(2+self.R/(self.R+50), self.M-3.5, f'R={self.R}m', fontsize=9, color='green', ha='center')
        
        ax1.set_xlim(0, 4)
        ax1.set_ylim(-6, self.M-3)
        ax1.set_aspect('equal')
        ax1.axis('off')
        ax1.set_title('承压水井流示意图', fontsize=12, fontweight='bold')
        ax1.legend(fontsize=9, loc='upper left')
        
        # 2. Dupuit公式计算流程
        ax2 = plt.subplot(3, 3, 2)
        ax2.axis('off')
        
        steps = [
            '【Dupuit公式计算】',
            '',
            '① 基本参数',
            f'含水层厚度: M = {self.M} m',
            f'渗透系数: K = {self.K} m/s',
            f'初始水头: H₀ = {self.H0} m',
            f'井中水位: hw = H₀-s₀ = {self.hw} m',
            f'井半径: r₀ = {self.r0} m',
            f'影响半径: R = {self.R} m',
            '',
            '② 井流量公式',
            'Q = 2πKM(H₀-hw)/ln(R/r₀)',
            '',
            f'  = 2π×{self.K}×{self.M}',
            f'    ×({self.H0}-{self.hw})',
            f'    /ln({self.R}/{self.r0})',
            '',
            f'  = {Q:.6f} m³/s',
            f'  = {Q*1000:.3f} L/s',
            f'  = {Q*86400:.2f} m³/d',
            '',
            '✓ 稳定井流流量',
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
            elif line == '':
                y_pos -= 0.01
                continue
            elif '✓' in line:
                ax2.text(0.5, y_pos, line, fontsize=10, fontweight='bold',
                        horizontalalignment='center', verticalalignment='top',
                        color='green')
            else:
                ax2.text(0.1, y_pos, line, fontsize=9, verticalalignment='top',
                        family='monospace')
            y_pos -= 0.035
        
        ax2.set_title('计算流程', fontsize=12, fontweight='bold')
        
        # 3. 水位降深曲线
        ax3 = plt.subplot(3, 3, 3)
        
        r_arr, h_arr, s_arr = self.drawdown_curve()
        
        ax3_twin = ax3.twinx()
        
        line1 = ax3.plot(r_arr, h_arr, 'b-', linewidth=2, label='水位h')
        ax3.axhline(self.H0, color='b', linestyle='--', alpha=0.5, label=f'H₀={self.H0}m')
        ax3.axhline(self.hw, color='r', linestyle=':', alpha=0.5, label=f'hw={self.hw}m')
        
        line2 = ax3_twin.plot(r_arr, s_arr, 'r-', linewidth=2, label='降深s')
        
        ax3.set_xlabel('距离 r (m)', fontsize=11)
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
        
        # 4. 渗流速度分布
        ax4 = plt.subplot(3, 3, 4)
        
        r_arr2, v_arr = self.velocity_distribution()
        
        ax4.plot(r_arr2, v_arr*1000, 'g-', linewidth=2, label='渗流速度v')
        
        # 理论曲线 v∝1/r
        v_theory = (v_arr[0]*1000 * r_arr2[0]) / r_arr2
        ax4.plot(r_arr2, v_theory, 'r--', linewidth=1.5, alpha=0.5, label='v∝1/r')
        
        ax4.set_xlabel('距离 r (m)', fontsize=11)
        ax4.set_ylabel('渗流速度 v (mm/s)', fontsize=11)
        ax4.set_title('渗流速度分布', fontsize=12, fontweight='bold')
        ax4.set_xscale('log')
        ax4.set_yscale('log')
        ax4.legend(fontsize=9)
        ax4.grid(True, alpha=0.3, which='both')
        
        # 5. 影响半径R的影响
        ax5 = plt.subplot(3, 3, 5)
        
        R_arr, Q_R = self.influence_radius_effect()
        
        ax5.plot(R_arr, Q_R*1000, 'b-', linewidth=2, label='流量Q')
        
        # 当前点
        ax5.plot(self.R, Q*1000, 'ro', markersize=12, label=f'当前R={self.R}m')
        
        ax5.set_xlabel('影响半径 R (m)', fontsize=11)
        ax5.set_ylabel('流量 Q (L/s)', fontsize=11)
        ax5.set_title('影响半径R对流量的影响', fontsize=12, fontweight='bold')
        ax5.legend(fontsize=9)
        ax5.grid(True, alpha=0.3)
        
        # 6. 井半径r0的影响
        ax6 = plt.subplot(3, 3, 6)
        
        r0_arr, Q_r0 = self.well_radius_effect()
        
        ax6.plot(r0_arr*100, Q_r0*1000, 'g-', linewidth=2, label='流量Q')
        
        # 当前点
        ax6.plot(self.r0*100, Q*1000, 'ro', markersize=12, label=f'当前r₀={self.r0}m')
        
        ax6.set_xlabel('井半径 r₀ (cm)', fontsize=11)
        ax6.set_ylabel('流量 Q (L/s)', fontsize=11)
        ax6.set_title('井半径r₀对流量的影响', fontsize=12, fontweight='bold')
        ax6.legend(fontsize=9)
        ax6.grid(True, alpha=0.3)
        
        # 7. 不同位置水位对比
        ax7 = plt.subplot(3, 3, 7)
        
        # 选择几个特征位置
        r_positions = [self.r0, 1, 5, 10, 50, 100, self.R]
        h_positions = [self.water_head(r) for r in r_positions]
        s_positions = [self.drawdown(r) for r in r_positions]
        
        x = np.arange(len(r_positions))
        width = 0.35
        
        bars1 = ax7.bar(x - width/2, h_positions, width, label='水位h',
                       color='lightblue', alpha=0.7, edgecolor='black')
        bars2 = ax7.bar(x + width/2, s_positions, width, label='降深s',
                       color='lightcoral', alpha=0.7, edgecolor='black')
        
        ax7.set_ylabel('高度 (m)', fontsize=11)
        ax7.set_xlabel('位置', fontsize=11)
        ax7.set_title('不同位置水位对比', fontsize=12, fontweight='bold')
        ax7.set_xticks(x)
        ax7.set_xticklabels([f'{r:.1f}m' for r in r_positions], rotation=45)
        ax7.legend(fontsize=9)
        ax7.grid(True, alpha=0.3, axis='y')
        
        # 添加数值标注
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax7.text(bar.get_x() + bar.get_width()/2, height,
                        f'{height:.1f}', ha='center', va='bottom', fontsize=8)
        
        # 8. 参数敏感性分析
        ax8 = plt.subplot(3, 3, 8)
        
        # 归一化敏感性
        params = ['K\n(渗透系数)', 'M\n(厚度)', 's₀\n(降深)', 'R\n(影响半径)', 'r₀\n(井半径)']
        
        # 各参数变化10%对流量的影响（近似）
        # Q ∝ K*M*s0/ln(R/r0)
        # ∂Q/∂K / Q = 1
        # ∂Q/∂M / Q = 1
        # ∂Q/∂s0 / Q = 1
        # ∂Q/∂R / Q ≈ -1/(R*ln(R/r0))
        # ∂Q/∂r0 / Q ≈ 1/(r0*ln(R/r0))
        
        sensitivity = [1.0, 1.0, 1.0, -1/(self.R*np.log(self.R/self.r0))*self.R*0.1, 
                      1/(self.r0*np.log(self.R/self.r0))*self.r0*0.1]
        sensitivity = [abs(s)*100 for s in sensitivity]  # 转换为百分比
        
        colors = ['lightblue', 'lightgreen', 'lightyellow', 'lightcoral', 'plum']
        bars = ax8.bar(params, sensitivity, color=colors, alpha=0.7, edgecolor='black')
        
        ax8.set_ylabel('敏感度 (%)', fontsize=11)
        ax8.set_title('参数敏感性分析（变化10%对Q的影响）', fontsize=12, fontweight='bold')
        ax8.grid(True, alpha=0.3, axis='y')
        
        for bar, val in zip(bars, sensitivity):
            height = bar.get_height()
            ax8.text(bar.get_x() + bar.get_width()/2, height,
                    f'{val:.2f}%', ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        # 9. 结果汇总
        ax9 = plt.subplot(3, 3, 9)
        ax9.axis('off')
        
        summary = [
            '═══ 承压水井流计算结果 ═══',
            '',
            '【基本参数】',
            f'含水层厚度: M = {self.M} m',
            f'渗透系数: K = {self.K} m/s',
            f'井半径: r₀ = {self.r0} m',
            f'井中降深: s₀ = {self.s0} m',
            f'影响半径: R = {self.R} m',
            '',
            '【计算结果】',
            f'初始水头: H₀ = {self.H0} m',
            f'井中水位: hw = {self.hw} m',
            f'井流量: Q = {Q:.6f} m³/s',
            f'        = {Q*1000:.3f} L/s',
            f'        = {Q*86400:.2f} m³/d',
            '',
            '【特征位置】',
            f'r=1m: h={self.water_head(1):.2f}m, s={self.drawdown(1):.2f}m',
            f'r=10m: h={self.water_head(10):.2f}m, s={self.drawdown(10):.2f}m',
            f'r=100m: h={self.water_head(100):.2f}m, s={self.drawdown(100):.2f}m',
            '',
            '【公式】',
            'Dupuit: Q=2πKM(H₀-hw)/ln(R/r₀)',
            'h=hw+(H₀-hw)ln(r/r₀)/ln(R/r₀)',
            's=s₀[1-ln(r/r₀)/ln(R/r₀)]',
            'v=Q/(2πrM)∝1/r',
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
        plt.savefig('/tmp/ch07_problem03_confined_well.png', dpi=150, bbox_inches='tight')
        print(f"图表已保存: /tmp/ch07_problem03_confined_well.png")
        plt.show()
    
    def print_results(self):
        """打印计算结果"""
        print("\n" + "="*70)
        print("第07章 地下水动力学 - 题3：承压水井流")
        print("="*70)
        
        # 基本参数
        print(f"\n【已知条件】")
        print(f"含水层厚度: M = {self.M} m")
        print(f"渗透系数: K = {self.K} m/s = {self.K*86400} m/d")
        print(f"井半径: r₀ = {self.r0} m = {self.r0*100} cm")
        print(f"井中降深: s₀ = {self.s0} m")
        print(f"影响半径: R = {self.R} m")
        
        print(f"\n推导参数:")
        print(f"初始水头: H₀ = {self.H0} m（承压水顶面）")
        print(f"井中水位: hw = H₀ - s₀ = {self.H0} - {self.s0} = {self.hw} m")
        
        # (1) 井流量
        print(f"\n【问题1】井流量（稳定流）")
        
        Q = self.well_discharge()
        
        print(f"\nDupuit公式（承压水）:")
        print(f"Q = 2πKM(H₀-hw)/ln(R/r₀)")
        
        print(f"\n代入数值:")
        print(f"Q = 2π × {self.K} × {self.M} × ({self.H0} - {self.hw}) / ln({self.R} / {self.r0})")
        print(f"  = 2π × {self.K} × {self.M} × {self.H0 - self.hw} / ln({self.R / self.r0:.2f})")
        print(f"  = {Q:.6f} m³/s")
        print(f"  = {Q*1000:.3f} L/s")
        print(f"  = {Q*86400:.2f} m³/d")
        
        print(f"\n✓ 井流量: Q = {Q:.6f} m³/s = {Q*1000:.3f} L/s = {Q*86400:.2f} m³/d")
        
        # (2) 任意点水位降深
        print(f"\n【问题2】任意点水位降深")
        
        print(f"\n水位公式:")
        print(f"h = hw + (H₀-hw) × ln(r/r₀) / ln(R/r₀)")
        
        print(f"\n降深公式:")
        print(f"s = s₀ × [1 - ln(r/r₀) / ln(R/r₀)]")
        
        # 几个典型位置
        positions = [1, 5, 10, 50, 100]
        
        print(f"\n典型位置水位降深:")
        print(f"{'距离(m)':<10} {'水位h(m)':<12} {'降深s(m)':<12} {'s/s₀':<10}")
        print(f"{'-'*50}")
        
        for r in positions:
            if r <= self.R:
                h = self.water_head(r)
                s = self.drawdown(r)
                ratio = s / self.s0
                print(f"{r:<10} {h:<12.2f} {s:<12.2f} {ratio:<10.3f}")
        
        print(f"\n观察:")
        print(f"• r = r₀ = {self.r0}m: s = s₀ = {self.s0}m（井壁最大降深）")
        print(f"• r增大，s减小")
        print(f"• r = R = {self.R}m: s = 0m（影响半径边界）")
        print(f"• 降深呈对数分布")
        
        # (3) 水位降深曲线
        print(f"\n【问题3】水位降深曲线")
        
        print(f"\n曲线特征:")
        print(f"• 对数曲线：h = hw + (H₀-hw) × ln(r/r₀) / ln(R/r₀)")
        print(f"• 近井处梯度大，远井处梯度小")
        print(f"• 井壁(r=r₀): h = hw = {self.hw}m")
        print(f"• 影响半径(r=R): h = H₀ = {self.H0}m")
        
        # (4) 渗流速度分布
        print(f"\n【问题4】渗流速度分布")
        
        print(f"\n渗流速度公式:")
        print(f"v = Q/(2πrM)")
        
        print(f"\n特征:")
        print(f"• v ∝ 1/r（反比于半径）")
        print(f"• 近井处速度大，远井处速度小")
        
        print(f"\n典型位置渗流速度:")
        print(f"{'距离(m)':<10} {'速度v(mm/s)':<15} {'速度v(m/d)':<15}")
        print(f"{'-'*45}")
        
        for r in positions:
            if self.r0 <= r <= self.R:
                v = self.seepage_velocity(r)
                print(f"{r:<10} {v*1000:<15.4f} {v*86400:<15.2f}")
        
        # (5) 影响半径R的影响
        print(f"\n【问题5】影响半径对流量的影响")
        
        print(f"\n影响规律:")
        print(f"• Q = 2πKM(H₀-hw)/ln(R/r₀)")
        print(f"• R增大，ln(R/r₀)增大，Q减小")
        print(f"• 但影响较小（对数关系）")
        
        R_test = [50, 100, 200, 300, 500]
        print(f"\n不同R值的流量:")
        print(f"{'R(m)':<10} {'Q(L/s)':<12} {'相对变化':<15}")
        print(f"{'-'*40}")
        
        Q_base = Q
        for R_val in R_test:
            Q_val = 2 * np.pi * self.K * self.M * (self.H0 - self.hw) / np.log(R_val / self.r0)
            change = (Q_val - Q_base) / Q_base * 100
            marker = ' (当前)' if R_val == self.R else ''
            print(f"{R_val:<10} {Q_val*1000:<12.3f} {change:+.2f}%{marker}")
        
        print(f"\n结论:")
        print(f"• R从50m增到500m，Q仅减少{(Q_test[-1]/Q_test[0]-1)*100:.1f}%")
        print(f"• R对Q影响较小")
        print(f"• 实际中R常由经验确定")
        
        # (6) 井半径r0的影响
        print(f"\n【问题6】井半径对流量的影响")
        
        print(f"\n影响规律:")
        print(f"• Q = 2πKM(H₀-hw)/ln(R/r₀)")
        print(f"• r₀增大，ln(R/r₀)减小，Q增大")
        print(f"• 但影响很小（对数关系）")
        
        r0_test = [0.1, 0.15, 0.2, 0.3, 0.5]
        print(f"\n不同r₀值的流量:")
        print(f"{'r₀(m)':<10} {'Q(L/s)':<12} {'相对变化':<15}")
        print(f"{'-'*40}")
        
        for r0_val in r0_test:
            Q_val = 2 * np.pi * self.K * self.M * (self.H0 - self.hw) / np.log(self.R / r0_val)
            change = (Q_val - Q_base) / Q_base * 100
            marker = ' (当前)' if r0_val == self.r0 else ''
            print(f"{r0_val:<10} {Q_val*1000:<12.3f} {change:+.2f}%{marker}")
        
        print(f"\n结论:")
        print(f"• r₀从0.1m增到0.5m，Q仅增加{(1/np.log(self.R/0.1)/np.log(self.R/0.5)-1)*100:.1f}%")
        print(f"• r₀对Q影响很小")
        print(f"• 增大井径不能显著增加出水量")
        
        # 考试要点
        print(f"\n【考试要点】")
        print(f"1. Dupuit公式（承压水）: Q = 2πKM(H₀-hw)/ln(R/r₀)")
        print(f"2. 任意点水位: h = hw + (H₀-hw)ln(r/r₀)/ln(R/r₀)")
        print(f"3. 水位降深: s = s₀[1 - ln(r/r₀)/ln(R/r₀)]")
        print(f"4. 渗流速度: v = Q/(2πrM) ∝ 1/r")
        print(f"5. R、r₀对Q影响小（对数关系）")
        print(f"6. 水位降深呈对数分布")
        print(f"7. 近井处梯度大、速度大")
        print(f"8. 承压水：M不变，H变化")
        
        print(f"\n{'='*70}\n")


def main():
    """主函数"""
    
    print("承压水井流分析")
    print("-" * 70)
    
    # 系统参数
    M = 10  # 含水层厚度 [m]
    K = 0.001  # 渗透系数 [m/s]
    r0 = 0.2  # 井半径 [m]
    s0 = 5  # 井中降深 [m]
    R = 200  # 影响半径 [m]
    
    # 创建分析实例
    well = ConfinedWell(M, K, r0, s0, R)
    
    # 打印结果
    well.print_results()
    
    # 绘制分析图
    well.plot_analysis()


if __name__ == "__main__":
    main()
