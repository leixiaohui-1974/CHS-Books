# -*- coding: utf-8 -*-
"""
第06章 水泵与水泵站 - 题1：水泵基本性能参数计算

问题描述：
    某离心泵，叶轮外径D₂ = 300 mm，叶轮内径D₁ = 150 mm，
    叶片出口角β₂ = 30°，转速n = 1450 r/min。
    设计工况下：流量Q = 200 L/s，水泵进出口压力差Δp = 400 kPa，
    水泵轴功率N = 100 kW。
    
    求：
    1. 叶轮外缘圆周速度u₂和径向速度vr₂
    2. 理论扬程Ht（假设无预旋，cu₁ = 0）
    3. 有效功率Ne和效率η
    4. 如果转速提高到n' = 2900 r/min，流量、扬程、功率如何变化？

核心公式：
    1. 欧拉方程：Ht = (u₂·cu₂ - u₁·cu₁)/g
    2. 圆周速度：u = π·D·n/60
    3. 有效功率：Ne = ρgQH
    4. 效率：η = Ne/N
    5. 相似定律：Q'/Q = n'/n, H'/H = (n'/n)², N'/N = (n'/n)³

考试要点：
    - 欧拉方程是水泵理论基础（必考）
    - 相似定律用于变转速调节
    - 效率是水泵重要性能指标
    - 速度三角形是理解水泵工作原理的关键

作者: CHS-Books Team
日期: 2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class PumpPerformance:
    """水泵基本性能参数计算"""
    
    def __init__(self, D2: float, D1: float, beta2: float, n: float,
                 Q: float, delta_p: float, N: float, b2: float = 0.02):
        """
        初始化水泵参数
        
        参数:
            D2: 叶轮外径 [m]
            D1: 叶轮内径 [m]
            beta2: 叶片出口角 [度]
            n: 转速 [r/min]
            Q: 流量 [m³/s]
            delta_p: 进出口压力差 [Pa]
            N: 轴功率 [W]
            b2: 叶片出口宽度 [m]（假设值）
        """
        self.D2 = D2
        self.D1 = D1
        self.beta2 = np.radians(beta2)  # 转换为弧度
        self.beta2_deg = beta2
        self.n = n
        self.Q = Q
        self.delta_p = delta_p
        self.N = N
        self.b2 = b2
        
        # 物性参数
        self.rho = 1000  # 水密度 [kg/m³]
        self.g = 9.8  # 重力加速度 [m/s²]
        
    def circumferential_velocity(self, D: float = None, n: float = None) -> float:
        """
        计算圆周速度
        
        参数:
            D: 直径 [m]（默认为D2）
            n: 转速 [r/min]（默认为self.n）
        
        返回:
            u: 圆周速度 [m/s]
        
        公式:
            u = π·D·n/60
        """
        if D is None:
            D = self.D2
        if n is None:
            n = self.n
        u = np.pi * D * n / 60
        return u
    
    def radial_velocity(self) -> float:
        """
        计算径向速度（从连续性方程）
        
        返回:
            vr2: 径向速度 [m/s]
        
        公式:
            Q = π·D2·b2·vr2
            vr2 = Q/(π·D2·b2)
        """
        vr2 = self.Q / (np.pi * self.D2 * self.b2)
        return vr2
    
    def tangential_velocity_component(self, u2: float, vr2: float) -> float:
        """
        从速度三角形计算绝对速度的圆周分量
        
        参数:
            u2: 叶轮外缘圆周速度 [m/s]
            vr2: 径向速度 [m/s]
        
        返回:
            cu2: 绝对速度的圆周分量 [m/s]
        
        公式:
            cu2 = u2 - vr2/tan(β2)
        """
        cu2 = u2 - vr2 / np.tan(self.beta2)
        return cu2
    
    def theoretical_head(self, u2: float, cu2: float) -> float:
        """
        欧拉方程计算理论扬程
        
        参数:
            u2: 叶轮外缘圆周速度 [m/s]
            cu2: 绝对速度的圆周分量 [m/s]
        
        返回:
            Ht: 理论扬程 [m]
        
        公式:
            Ht = (u2·cu2 - u1·cu1)/g
            假设无预旋：cu1 = 0
            Ht = u2·cu2/g
        """
        Ht = u2 * cu2 / self.g
        return Ht
    
    def actual_head(self) -> float:
        """
        从压力差计算实际扬程
        
        返回:
            H: 实际扬程 [m]
        
        公式:
            H = Δp/(ρ·g)
        """
        H = self.delta_p / (self.rho * self.g)
        return H
    
    def effective_power(self, H: float) -> float:
        """
        计算有效功率
        
        参数:
            H: 扬程 [m]
        
        返回:
            Ne: 有效功率 [W]
        
        公式:
            Ne = ρ·g·Q·H
        """
        Ne = self.rho * self.g * self.Q * H
        return Ne
    
    def efficiency(self, Ne: float) -> float:
        """
        计算效率
        
        参数:
            Ne: 有效功率 [W]
        
        返回:
            eta: 效率 [无量纲]
        
        公式:
            η = Ne/N
        """
        eta = Ne / self.N
        return eta
    
    def similarity_law_speed_change(self, n_new: float) -> Tuple[float, float, float]:
        """
        相似定律：转速变化
        
        参数:
            n_new: 新转速 [r/min]
        
        返回:
            Q_new: 新流量 [m³/s]
            H_new: 新扬程 [m]
            N_new: 新功率 [W]
        
        公式:
            Q'/Q = n'/n
            H'/H = (n'/n)²
            N'/N = (n'/n)³
        """
        ratio = n_new / self.n
        Q_new = self.Q * ratio
        H = self.actual_head()
        H_new = H * (ratio ** 2)
        N_new = self.N * (ratio ** 3)
        return Q_new, H_new, N_new
    
    def specific_speed(self, H: float = None) -> float:
        """
        计算比转速
        
        参数:
            H: 扬程 [m]（默认为实际扬程）
        
        返回:
            ns: 比转速
        
        公式:
            ns = n·Q^0.5/H^0.75
            Q单位: m³/s, H单位: m
        """
        if H is None:
            H = self.actual_head()
        ns = self.n * (self.Q ** 0.5) / (H ** 0.75)
        return ns
    
    def plot_analysis(self):
        """绘制完整分析图表（9个子图）"""
        fig = plt.figure(figsize=(16, 12))
        
        # 计算基本参数
        u2 = self.circumferential_velocity()
        u1 = self.circumferential_velocity(D=self.D1)
        vr2 = self.radial_velocity()
        cu2 = self.tangential_velocity_component(u2, vr2)
        Ht = self.theoretical_head(u2, cu2)
        H = self.actual_head()
        Ne = self.effective_power(H)
        eta = self.efficiency(Ne)
        ns = self.specific_speed()
        
        # 1. 速度三角形（出口）
        ax1 = plt.subplot(3, 3, 1)
        
        # 绘制速度三角形
        # u2: 圆周速度（水平向右）
        ax1.arrow(0, 0, u2, 0, head_width=0.8, head_length=1, fc='blue', ec='blue', linewidth=2)
        ax1.text(u2/2, -1.5, f'u₂={u2:.1f}m/s', ha='center', fontsize=10, color='blue')
        
        # vr2: 径向速度（垂直向上）
        ax1.arrow(u2, 0, 0, vr2, head_width=0.8, head_length=0.5, fc='green', ec='green', linewidth=2)
        ax1.text(u2+1.5, vr2/2, f'vr₂={vr2:.1f}m/s', ha='left', fontsize=10, color='green')
        
        # w2: 相对速度
        w2 = np.sqrt((u2 - cu2)**2 + vr2**2)
        ax1.plot([0, u2-cu2], [0, vr2], 'r--', linewidth=2, label=f'w₂={w2:.1f}m/s')
        
        # c2: 绝对速度
        c2 = np.sqrt(cu2**2 + vr2**2)
        ax1.arrow(0, 0, cu2, vr2, head_width=0.8, head_length=0.5, fc='purple', ec='purple', linewidth=2)
        ax1.text(cu2/2-2, vr2+1, f'c₂={c2:.1f}m/s', ha='center', fontsize=10, color='purple')
        
        # 角度标注
        ax1.text(u2-4, 1, f'β₂={self.beta2_deg}°', fontsize=10, color='red')
        
        ax1.set_xlim(-2, u2+5)
        ax1.set_ylim(-3, vr2+3)
        ax1.set_aspect('equal')
        ax1.grid(True, alpha=0.3)
        ax1.set_xlabel('圆周方向 (m/s)', fontsize=10)
        ax1.set_ylabel('径向 (m/s)', fontsize=10)
        ax1.set_title('叶轮出口速度三角形', fontsize=12, fontweight='bold')
        ax1.legend(loc='upper left', fontsize=9)
        
        # 2. 基本参数柱状图
        ax2 = plt.subplot(3, 3, 2)
        params = ['u₂\n(m/s)', 'vr₂\n(m/s)', 'cu₂\n(m/s)', 'Ht\n(m)', 'H\n(m)']
        values = [u2, vr2, cu2, Ht, H]
        colors = ['skyblue', 'lightgreen', 'lightcoral', 'orange', 'pink']
        
        bars = ax2.bar(params, values, color=colors, alpha=0.7, edgecolor='black')
        ax2.set_ylabel('数值', fontsize=11)
        ax2.set_title('速度与扬程参数', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='y')
        
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2, height,
                    f'{val:.1f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        # 3. 功率与效率
        ax3 = plt.subplot(3, 3, 3)
        power_params = ['轴功率N\n(kW)', '有效功率Ne\n(kW)', '损失功率\n(kW)']
        power_values = [self.N/1000, Ne/1000, (self.N-Ne)/1000]
        power_colors = ['red', 'green', 'gray']
        
        bars = ax3.bar(power_params, power_values, color=power_colors, alpha=0.7, edgecolor='black')
        ax3.set_ylabel('功率 (kW)', fontsize=11)
        ax3.set_title(f'功率分析（效率η={eta*100:.1f}%）', fontsize=12, fontweight='bold')
        ax3.grid(True, alpha=0.3, axis='y')
        
        for bar, val in zip(bars, power_values):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2, height,
                    f'{val:.1f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        # 4. 欧拉方程计算流程
        ax4 = plt.subplot(3, 3, 4)
        ax4.axis('off')
        
        steps = [
            '【欧拉方程计算流程】',
            '',
            f'步骤1：计算圆周速度',
            f'u₂ = π·D₂·n/60',
            f'u₂ = π×{self.D2}×{self.n}/60 = {u2:.2f} m/s',
            '',
            f'步骤2：计算径向速度',
            f'vr₂ = Q/(π·D₂·b₂)',
            f'vr₂ = {self.Q}/(π×{self.D2}×{self.b2}) = {vr2:.2f} m/s',
            '',
            f'步骤3：速度三角形',
            f'cu₂ = u₂ - vr₂/tan(β₂)',
            f'cu₂ = {u2:.1f} - {vr2:.1f}/tan({self.beta2_deg}°) = {cu2:.2f} m/s',
            '',
            f'步骤4：理论扬程',
            f'Ht = u₂·cu₂/g = {u2:.1f}×{cu2:.1f}/{self.g} = {Ht:.2f} m',
        ]
        
        y_pos = 0.95
        for step in steps:
            if '【' in step:
                ax4.text(0.5, y_pos, step, fontsize=11, fontweight='bold',
                        horizontalalignment='center', verticalalignment='top', color='darkred')
            elif step == '':
                y_pos -= 0.01
                continue
            elif '步骤' in step:
                ax4.text(0.05, y_pos, step, fontsize=10, fontweight='bold',
                        verticalalignment='top', color='darkblue')
            else:
                ax4.text(0.1, y_pos, step, fontsize=9, verticalalignment='top',
                        family='monospace')
            y_pos -= 0.055
        
        ax4.set_title('欧拉方程计算', fontsize=12, fontweight='bold')
        
        # 5. 相似定律（转速变化）
        ax5 = plt.subplot(3, 3, 5)
        n_range = np.linspace(500, 3000, 50)
        Q_range = self.Q * (n_range / self.n)
        H_range = H * ((n_range / self.n) ** 2)
        N_range = self.N / 1000 * ((n_range / self.n) ** 3)
        
        ax5_Q = ax5.twinx()
        ax5_N = ax5.twinx()
        ax5_N.spines['right'].set_position(('outward', 60))
        
        line1 = ax5.plot(n_range, H_range, 'b-', linewidth=2, label='扬程H')
        line2 = ax5_Q.plot(n_range, Q_range*1000, 'g-', linewidth=2, label='流量Q')
        line3 = ax5_N.plot(n_range, N_range, 'r-', linewidth=2, label='功率N')
        
        ax5.plot(self.n, H, 'bo', markersize=10)
        ax5_Q.plot(self.n, self.Q*1000, 'go', markersize=10)
        ax5_N.plot(self.n, self.N/1000, 'ro', markersize=10)
        
        ax5.set_xlabel('转速 n (r/min)', fontsize=11)
        ax5.set_ylabel('扬程 H (m)', fontsize=11, color='b')
        ax5_Q.set_ylabel('流量 Q (L/s)', fontsize=11, color='g')
        ax5_N.set_ylabel('功率 N (kW)', fontsize=11, color='r')
        
        ax5.tick_params(axis='y', labelcolor='b')
        ax5_Q.tick_params(axis='y', labelcolor='g')
        ax5_N.tick_params(axis='y', labelcolor='r')
        
        ax5.set_title('相似定律（转速影响）', fontsize=12, fontweight='bold')
        ax5.grid(True, alpha=0.3)
        
        # 6. 转速变化对比
        ax6 = plt.subplot(3, 3, 6)
        n_new = 2900
        Q_new, H_new, N_new = self.similarity_law_speed_change(n_new)
        
        x = np.arange(3)
        width = 0.35
        
        original = [self.Q*1000, H, self.N/1000]
        new = [Q_new*1000, H_new, N_new/1000]
        
        bars1 = ax6.bar(x - width/2, original, width, label=f'n={self.n}rpm', 
                       color='skyblue', alpha=0.7, edgecolor='black')
        bars2 = ax6.bar(x + width/2, new, width, label=f'n={n_new}rpm',
                       color='lightcoral', alpha=0.7, edgecolor='black')
        
        ax6.set_ylabel('参数值', fontsize=11)
        ax6.set_title('转速变化对比（n加倍）', fontsize=12, fontweight='bold')
        ax6.set_xticks(x)
        ax6.set_xticklabels(['Q(L/s)', 'H(m)', 'N(kW)'])
        ax6.legend()
        ax6.grid(True, alpha=0.3, axis='y')
        
        # 添加倍数标注
        for i, (bar1, bar2, val1, val2) in enumerate(zip(bars1, bars2, original, new)):
            ratio = val2 / val1
            ax6.text(bar2.get_x() + bar2.get_width()/2, bar2.get_height(),
                    f'×{ratio:.1f}', ha='center', va='bottom', fontsize=10,
                    fontweight='bold', color='red')
        
        # 7. 效率分解
        ax7 = plt.subplot(3, 3, 7)
        
        # 假设典型效率分解
        eta_h = 0.90  # 水力效率
        eta_v = 0.96  # 容积效率
        eta_m = 0.97  # 机械效率
        eta_total = eta_h * eta_v * eta_m
        
        efficiencies = ['水力\n效率ηh', '容积\n效率ηv', '机械\n效率ηm', '总\n效率η']
        eff_values = [eta_h*100, eta_v*100, eta_m*100, eta*100]
        eff_colors = ['lightblue', 'lightgreen', 'lightyellow', 'lightcoral']
        
        bars = ax7.bar(efficiencies, eff_values, color=eff_colors, alpha=0.7, edgecolor='black')
        ax7.set_ylabel('效率 (%)', fontsize=11)
        ax7.set_title('效率分解（η=ηh·ηv·ηm）', fontsize=12, fontweight='bold')
        ax7.axhline(100, color='r', linestyle='--', linewidth=1, alpha=0.5)
        ax7.grid(True, alpha=0.3, axis='y')
        ax7.set_ylim(0, 105)
        
        for bar, val in zip(bars, eff_values):
            height = bar.get_height()
            ax7.text(bar.get_x() + bar.get_width()/2, height,
                    f'{val:.1f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        # 8. 比转速分析
        ax8 = plt.subplot(3, 3, 8)
        ax8.axis('off')
        
        ns_info = [
            '【比转速分析】',
            '',
            f'比转速公式：',
            f'ns = n·Q^0.5/H^0.75',
            '',
            f'本泵参数：',
            f'n = {self.n} r/min',
            f'Q = {self.Q} m³/s = {self.Q*1000} L/s',
            f'H = {H:.1f} m',
            '',
            f'计算：',
            f'ns = {self.n}×{self.Q}^0.5/{H:.1f}^0.75',
            f'ns = {ns:.1f}',
            '',
            f'水泵类型判断：',
        ]
        
        # 判断水泵类型
        if ns < 80:
            pump_type = '低比转速泵（离心泵）'
            characteristics = '扬程高，流量小'
        elif ns < 150:
            pump_type = '中比转速泵（混流泵）'
            characteristics = '扬程、流量适中'
        else:
            pump_type = '高比转速泵（轴流泵）'
            characteristics = '扬程低，流量大'
        
        ns_info.append(f'类型：{pump_type}')
        ns_info.append(f'特点：{characteristics}')
        
        y_pos = 0.95
        for line in ns_info:
            if '【' in line:
                ax8.text(0.5, y_pos, line, fontsize=11, fontweight='bold',
                        horizontalalignment='center', verticalalignment='top', color='darkred')
            elif line == '':
                y_pos -= 0.015
                continue
            elif '类型' in line or '特点' in line:
                ax8.text(0.1, y_pos, line, fontsize=10, verticalalignment='top',
                        color='darkgreen', fontweight='bold')
            else:
                ax8.text(0.1, y_pos, line, fontsize=9, verticalalignment='top',
                        family='monospace')
            y_pos -= 0.055
        
        ax8.set_title('比转速与水泵类型', fontsize=12, fontweight='bold')
        
        # 9. 结果汇总
        ax9 = plt.subplot(3, 3, 9)
        ax9.axis('off')
        
        summary = [
            '═══ 计算结果汇总 ═══',
            '',
            '【速度参数】',
            f'叶轮外缘圆周速度: u₂ = {u2:.2f} m/s',
            f'叶轮内缘圆周速度: u₁ = {u1:.2f} m/s',
            f'径向速度: vr₂ = {vr2:.2f} m/s',
            f'圆周分量: cu₂ = {cu2:.2f} m/s',
            '',
            '【扬程参数】',
            f'理论扬程: Ht = {Ht:.2f} m',
            f'实际扬程: H = {H:.2f} m',
            f'水力效率: ηh ≈ {H/Ht*100:.1f}%',
            '',
            '【功率效率】',
            f'轴功率: N = {self.N/1000:.1f} kW',
            f'有效功率: Ne = {Ne/1000:.1f} kW',
            f'总效率: η = {eta*100:.1f}%',
            '',
            '【比转速】',
            f'ns = {ns:.1f}（{pump_type}）',
            '',
            '【相似定律（n×2）】',
            f'流量: Q = {Q_new*1000:.0f} L/s（×2）',
            f'扬程: H = {H_new:.1f} m（×4）',
            f'功率: N = {N_new/1000:.0f} kW（×8）',
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
                y_pos -= 0.008
                continue
            else:
                ax9.text(0.1, y_pos, line, fontsize=9, verticalalignment='top',
                        family='monospace')
            y_pos -= 0.04
        
        ax9.set_title('计算结果', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('/tmp/ch06_problem01_pump_performance.png', dpi=150, bbox_inches='tight')
        print(f"图表已保存: /tmp/ch06_problem01_pump_performance.png")
        plt.show()
    
    def print_results(self):
        """打印计算结果"""
        print("\n" + "="*70)
        print("第06章 水泵与水泵站 - 题1：水泵基本性能参数计算")
        print("="*70)
        
        # 基本参数
        print(f"\n【水泵基本参数】")
        print(f"叶轮外径: D₂ = {self.D2*1000} mm")
        print(f"叶轮内径: D₁ = {self.D1*1000} mm")
        print(f"叶片出口角: β₂ = {self.beta2_deg}°")
        print(f"转速: n = {self.n} r/min")
        print(f"流量: Q = {self.Q} m³/s = {self.Q*1000} L/s")
        print(f"压力差: Δp = {self.delta_p/1000} kPa")
        print(f"轴功率: N = {self.N/1000} kW")
        print(f"叶片出口宽度: b₂ = {self.b2*1000} mm（假设）")
        
        # (1) 圆周速度和径向速度
        print(f"\n【问题1】圆周速度和径向速度")
        
        u2 = self.circumferential_velocity()
        u1 = self.circumferential_velocity(D=self.D1)
        print(f"\n叶轮外缘圆周速度:")
        print(f"u₂ = π·D₂·n/60")
        print(f"u₂ = π×{self.D2}×{self.n}/60")
        print(f"u₂ = {u2:.3f} m/s")
        print(f"✓ u₂ = {u2:.2f} m/s")
        
        print(f"\n叶轮内缘圆周速度:")
        print(f"u₁ = π·D₁·n/60 = π×{self.D1}×{self.n}/60 = {u1:.2f} m/s")
        
        vr2 = self.radial_velocity()
        print(f"\n径向速度（从连续性方程）:")
        print(f"Q = π·D₂·b₂·vr₂")
        print(f"vr₂ = Q/(π·D₂·b₂)")
        print(f"vr₂ = {self.Q}/(π×{self.D2}×{self.b2})")
        print(f"vr₂ = {vr2:.3f} m/s")
        print(f"✓ vr₂ = {vr2:.2f} m/s")
        
        # (2) 理论扬程
        print(f"\n【问题2】理论扬程（欧拉方程）")
        
        cu2 = self.tangential_velocity_component(u2, vr2)
        print(f"\n从速度三角形求圆周分量:")
        print(f"cu₂ = u₂ - vr₂/tan(β₂)")
        print(f"cu₂ = {u2:.2f} - {vr2:.2f}/tan({self.beta2_deg}°)")
        print(f"cu₂ = {u2:.2f} - {vr2:.2f}/{np.tan(self.beta2):.3f}")
        print(f"cu₂ = {cu2:.3f} m/s")
        
        Ht = self.theoretical_head(u2, cu2)
        print(f"\n欧拉方程（无预旋，cu₁=0）:")
        print(f"Ht = u₂·cu₂/g")
        print(f"Ht = {u2:.2f}×{cu2:.2f}/{self.g}")
        print(f"Ht = {Ht:.3f} m")
        print(f"✓ 理论扬程: Ht = {Ht:.2f} m")
        
        H = self.actual_head()
        print(f"\n实际扬程（从压力差）:")
        print(f"H = Δp/(ρ·g) = {self.delta_p/1000}×10³/({self.rho}×{self.g})")
        print(f"H = {H:.2f} m")
        
        eta_h = H / Ht
        print(f"\n水力效率:")
        print(f"ηh = H/Ht = {H:.1f}/{Ht:.1f} = {eta_h:.3f} = {eta_h*100:.1f}%")
        
        # (3) 有效功率和效率
        print(f"\n【问题3】有效功率和效率")
        
        Ne = self.effective_power(H)
        print(f"\n有效功率:")
        print(f"Ne = ρ·g·Q·H")
        print(f"Ne = {self.rho}×{self.g}×{self.Q}×{H:.1f}")
        print(f"Ne = {Ne:.0f} W = {Ne/1000:.1f} kW")
        print(f"✓ Ne = {Ne/1000:.1f} kW")
        
        eta = self.efficiency(Ne)
        print(f"\n总效率:")
        print(f"η = Ne/N = {Ne/1000:.1f}/{self.N/1000:.1f}")
        print(f"η = {eta:.4f} = {eta*100:.1f}%")
        print(f"✓ η = {eta*100:.1f}%")
        
        print(f"\n效率分解:")
        print(f"η = ηh·ηv·ηm")
        print(f"假设典型值: ηh≈90%, ηv≈96%, ηm≈97%")
        print(f"η理论 = 0.90×0.96×0.97 = 0.837 ≈ 84%")
        print(f"与实际{eta*100:.0f}%接近✓")
        
        # (4) 转速变化（相似定律）
        print(f"\n【问题4】转速变化（相似定律）")
        
        n_new = 2900
        Q_new, H_new, N_new = self.similarity_law_speed_change(n_new)
        
        print(f"\n转速提高到 n' = {n_new} r/min")
        print(f"转速比: n'/n = {n_new}/{self.n} = {n_new/self.n}")
        
        print(f"\n相似定律:")
        print(f"(1) 流量比: Q'/Q = n'/n")
        print(f"    Q' = Q × n'/n = {self.Q*1000} × {n_new/self.n}")
        print(f"    Q' = {Q_new*1000:.0f} L/s")
        print(f"    ✓ 流量变为{Q_new*1000/self.Q/1000:.0f}倍")
        
        print(f"\n(2) 扬程比: H'/H = (n'/n)²")
        print(f"    H' = H × (n'/n)² = {H:.1f} × {(n_new/self.n)**2}")
        print(f"    H' = {H_new:.1f} m")
        print(f"    ✓ 扬程变为{H_new/H:.0f}倍")
        
        print(f"\n(3) 功率比: N'/N = (n'/n)³")
        print(f"    N' = N × (n'/n)³ = {self.N/1000:.0f} × {(n_new/self.n)**3}")
        print(f"    N' = {N_new/1000:.0f} kW")
        print(f"    ✓ 功率变为{N_new/self.N:.0f}倍")
        
        print(f"\n对比总结:")
        print(f"{'参数':<10} {'原值':>15} {'新值':>15} {'倍数':>10}")
        print(f"{'-'*55}")
        print(f"{'转速(rpm)':<10} {self.n:>15.0f} {n_new:>15.0f} {n_new/self.n:>10.0f}x")
        print(f"{'流量(L/s)':<10} {self.Q*1000:>15.0f} {Q_new*1000:>15.0f} {Q_new/self.Q:>10.0f}x")
        print(f"{'扬程(m)':<10} {H:>15.1f} {H_new:>15.1f} {H_new/H:>10.0f}x")
        print(f"{'功率(kW)':<10} {self.N/1000:>15.0f} {N_new/1000:>15.0f} {N_new/self.N:>10.0f}x")
        
        print(f"\n工程意义:")
        print(f"- 转速加倍，流量加倍（线性关系）")
        print(f"- 扬程增大4倍（平方关系）")
        print(f"- 功率增大8倍（立方关系）")
        print(f"- ⚠ 能耗剧增，需谨慎调节！")
        
        # 比转速
        ns = self.specific_speed()
        print(f"\n【比转速】")
        print(f"ns = n·Q^0.5/H^0.75")
        print(f"ns = {self.n}×{self.Q}^0.5/{H:.1f}^0.75")
        print(f"ns = {ns:.1f}")
        
        if ns < 80:
            pump_type = "低比转速泵（离心泵）"
        elif ns < 150:
            pump_type = "中比转速泵（混流泵）"
        else:
            pump_type = "高比转速泵（轴流泵）"
        print(f"水泵类型: {pump_type}")
        
        # 考试要点
        print(f"\n【考试要点】")
        print(f"1. 欧拉方程: Ht = u₂·cu₂/g（必须记住！）")
        print(f"2. 圆周速度: u = π·D·n/60")
        print(f"3. 速度三角形: cu₂ = u₂ - vr₂/tan(β₂)")
        print(f"4. 有效功率: Ne = ρ·g·Q·H = 9.8QH (kW)")
        print(f"5. 效率: η = Ne/N = ηh·ηv·ηm")
        print(f"6. 相似定律: Q∝n, H∝n², N∝n³")
        print(f"7. 比转速: ns = n·Q^0.5/H^0.75")
        
        print(f"\n{'='*70}\n")


def main():
    """主函数"""
    
    print("水泵基本性能参数计算")
    print("-" * 70)
    
    # 水泵参数
    D2 = 0.3  # 叶轮外径 [m]
    D1 = 0.15  # 叶轮内径 [m]
    beta2 = 30  # 叶片出口角 [度]
    n = 1450  # 转速 [r/min]
    Q = 0.2  # 流量 [m³/s]
    delta_p = 400e3  # 压力差 [Pa]
    N = 100e3  # 轴功率 [W]
    b2 = 0.02  # 叶片出口宽度 [m]（假设）
    
    # 创建水泵实例
    pump = PumpPerformance(D2, D1, beta2, n, Q, delta_p, N, b2)
    
    # 打印结果
    pump.print_results()
    
    # 绘制分析图
    pump.plot_analysis()


if __name__ == "__main__":
    main()
