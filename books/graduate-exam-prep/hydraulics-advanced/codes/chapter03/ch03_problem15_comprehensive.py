#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第03章 管流与明渠流 - 题目15：综合应用（管渠联合输水系统）

题目描述：
某城市供水系统由管道和明渠组成：

**管道部分**：
- 从水库（水位H₀=50m）通过管道（直径d=0.5m，长度L=500m）输水
- 管道粗糙系数n=0.013
- 管道出口连接明渠

**明渠部分**：
- 矩形明渠（宽度b=2m，坡度i=0.002）
- 明渠粗糙系数n=0.020
- 明渠出口水位H₁=20m

求：
(1) 系统流量Q
(2) 管道出口压力
(3) 明渠正常水深
(4) 判断明渠流态
(5) 系统优化建议

知识点：
- 管渠联合计算
- 能量方程
- 明渠均匀流
- 系统优化

作者：CHS-Books Team
日期：2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class PipeChannelSystem:
    """管渠联合输水系统类"""
    
    def __init__(self, H0: float, H1: float, d: float, L: float, b: float,
                 i: float, n_pipe: float = 0.013, n_channel: float = 0.020,
                 rho: float = 1000.0, g: float = 9.81):
        """
        初始化参数
        
        Parameters:
        -----------
        H0 : float
            上游水库水位 (m)
        H1 : float
            下游出口水位 (m)
        d : float
            管道直径 (m)
        L : float
            管道长度 (m)
        b : float
            明渠宽度 (m)
        i : float
            明渠底坡
        n_pipe : float
            管道粗糙系数
        n_channel : float
            明渠粗糙系数
        rho : float
            水密度 (kg/m³)
        g : float
            重力加速度 (m/s²)
        """
        self.H0 = H0
        self.H1 = H1
        self.d = d
        self.L = L
        self.b = b
        self.i = i
        self.n_pipe = n_pipe
        self.n_channel = n_channel
        self.rho = rho
        self.g = g
    
    def pipe_friction_factor(self, Q: float) -> float:
        """
        计算管道沿程阻力系数
        
        使用曼宁公式推导：λ = 8gn²/R^(1/3)
        
        Parameters:
        -----------
        Q : float
            流量 (m³/s)
            
        Returns:
        --------
        float : 沿程阻力系数
        """
        R = self.d / 4
        return 8 * self.g * self.n_pipe**2 / R**(1/3)
    
    def pipe_head_loss(self, Q: float) -> float:
        """
        计算管道水头损失
        
        Parameters:
        -----------
        Q : float
            流量 (m³/s)
            
        Returns:
        --------
        float : 水头损失 (m)
        """
        A = np.pi * self.d**2 / 4
        v = Q / A
        lambda_f = self.pipe_friction_factor(Q)
        
        # 达西公式
        h_f = lambda_f * (self.L / self.d) * (v**2 / (2 * self.g))
        
        return h_f
    
    def channel_normal_depth(self, Q: float) -> float:
        """
        计算明渠正常水深
        
        使用曼宁公式求解
        
        Parameters:
        -----------
        Q : float
            流量 (m³/s)
            
        Returns:
        --------
        float : 正常水深 (m)
        """
        def equation(h):
            if h <= 0:
                return 1e10
            A = self.b * h
            chi = self.b + 2 * h
            R = A / chi
            v = (1 / self.n_channel) * R**(2/3) * self.i**0.5
            return Q - A * v
        
        # 初始猜测
        h_guess = (Q / (self.b * (1/self.n_channel) * self.i**0.5))**(3/5)
        
        try:
            h_n = fsolve(equation, h_guess)[0]
            return max(h_n, 0.01)
        except:
            return h_guess
    
    def channel_velocity(self, Q: float, h: float) -> float:
        """
        计算明渠流速
        
        Parameters:
        -----------
        Q : float
            流量 (m³/s)
        h : float
            水深 (m)
            
        Returns:
        --------
        float : 流速 (m/s)
        """
        A = self.b * h
        return Q / A
    
    def channel_froude_number(self, Q: float, h: float) -> float:
        """
        计算明渠佛汝德数
        
        Parameters:
        -----------
        Q : float
            流量 (m³/s)
        h : float
            水深 (m)
            
        Returns:
        --------
        float : 佛汝德数
        """
        v = self.channel_velocity(Q, h)
        return v / np.sqrt(self.g * h)
    
    def system_flow_rate(self) -> float:
        """
        计算系统流量
        
        能量方程：H0 = H1 + h_pipe + h_channel
        
        Returns:
        --------
        float : 流量 (m³/s)
        """
        def energy_equation(Q):
            if Q <= 0:
                return 1e10
            
            # 管道损失
            h_pipe = self.pipe_head_loss(Q)
            
            # 明渠正常水深
            h_n = self.channel_normal_depth(Q)
            
            # 明渠出口比能
            v_channel = self.channel_velocity(Q, h_n)
            E_channel = h_n + v_channel**2 / (2 * self.g)
            
            # 能量方程（相对于明渠出口）
            # H0 = (H1 + E_channel) + h_pipe
            return self.H0 - (self.H1 + E_channel) - h_pipe
        
        # 初始猜测（忽略损失的理想流量）
        Q_guess = np.pi * self.d**2 / 4 * np.sqrt(2 * self.g * (self.H0 - self.H1))
        
        try:
            Q = fsolve(energy_equation, Q_guess)[0]
            return max(Q, 0.001)
        except:
            return Q_guess * 0.5
    
    def pipe_outlet_pressure(self, Q: float) -> float:
        """
        计算管道出口压力
        
        Parameters:
        -----------
        Q : float
            流量 (m³/s)
            
        Returns:
        --------
        float : 出口压力 (Pa)
        """
        # 管道损失
        h_pipe = self.pipe_head_loss(Q)
        
        # 管道出口流速
        A = np.pi * self.d**2 / 4
        v_out = Q / A
        
        # 明渠正常水深
        h_n = self.channel_normal_depth(Q)
        
        # 假设管道出口位于明渠入口，出口高程 = H1 + h_n
        z_out = self.H1 + h_n
        
        # 伯努利方程（从水库到管道出口）
        # H0 = z_out + v_out²/(2g) + p_out/(ρg) + h_pipe
        p_out = self.rho * self.g * (self.H0 - z_out - v_out**2/(2*self.g) - h_pipe)
        
        return p_out
    
    def system_efficiency(self, Q: float) -> float:
        """
        计算系统效率
        
        η = 有效水头 / 总水头
        
        Parameters:
        -----------
        Q : float
            流量 (m³/s)
            
        Returns:
        --------
        float : 效率
        """
        h_pipe = self.pipe_head_loss(Q)
        h_total = self.H0 - self.H1
        
        # 有效水头（用于输水）
        h_effective = h_total - h_pipe
        
        return h_effective / h_total if h_total > 0 else 0
    
    def diameter_optimization(self, d_range: tuple = (0.3, 0.8),
                             n_points: int = 50) -> tuple:
        """
        管道直径优化分析
        
        Parameters:
        -----------
        d_range : tuple
            直径范围 (m)
        n_points : int
            计算点数
            
        Returns:
        --------
        tuple : (d_array, Q_array, h_loss_array, efficiency_array)
        """
        d_array = np.linspace(d_range[0], d_range[1], n_points)
        Q_array = np.zeros(n_points)
        h_loss_array = np.zeros(n_points)
        efficiency_array = np.zeros(n_points)
        
        d_original = self.d
        
        for i, d_val in enumerate(d_array):
            self.d = d_val
            Q = self.system_flow_rate()
            Q_array[i] = Q
            h_loss_array[i] = self.pipe_head_loss(Q)
            efficiency_array[i] = self.system_efficiency(Q)
        
        self.d = d_original
        
        return d_array, Q_array, h_loss_array, efficiency_array
    
    def plot_analysis(self):
        """绘制系统分析图"""
        fig = plt.figure(figsize=(16, 12))
        
        # 计算系统参数
        Q = self.system_flow_rate()
        h_pipe = self.pipe_head_loss(Q)
        h_n = self.channel_normal_depth(Q)
        v_channel = self.channel_velocity(Q, h_n)
        Fr = self.channel_froude_number(Q, h_n)
        p_out = self.pipe_outlet_pressure(Q)
        efficiency = self.system_efficiency(Q)
        
        # 图1：系统示意图
        ax1 = plt.subplot(3, 3, 1)
        
        # 绘制水库
        ax1.fill_between([0, 2], [0, 0], [self.H0, self.H0],
                        color='lightblue', alpha=0.5, label='上游水库')
        ax1.plot([0, 2], [self.H0, self.H0], 'b-', linewidth=2)
        ax1.text(1, self.H0 + 2, f'水库\nH₀={self.H0}m', ha='center',
                fontsize=10, fontweight='bold')
        
        # 管道
        z_pipe_out = self.H1 + h_n
        ax1.plot([2, 5], [self.H0 - 5, z_pipe_out], 'k-', linewidth=4,
                label=f'管道\nL={self.L}m, d={self.d}m')
        
        # 明渠
        L_channel = 5
        x_channel = np.linspace(5, 5 + L_channel, 50)
        z_bottom = z_pipe_out - self.i * (x_channel - 5)
        z_water = z_bottom + h_n
        
        ax1.fill_between(x_channel, z_bottom, z_water,
                        color='lightblue', alpha=0.5, label='明渠水流')
        ax1.plot(x_channel, z_water, 'b-', linewidth=2)
        ax1.plot(x_channel, z_bottom, 'k-', linewidth=2)
        
        # 下游水位
        ax1.axhline(y=self.H1, xmin=0.6, xmax=1, color='blue',
                   linestyle='--', linewidth=2, label=f'下游水位\nH₁={self.H1}m')
        
        ax1.set_xlim(0, 11)
        ax1.set_ylim(0, self.H0 + 5)
        ax1.set_xlabel('水平距离 (m)', fontsize=10, fontweight='bold')
        ax1.set_ylabel('高程 (m)', fontsize=10, fontweight='bold')
        ax1.set_title('管渠联合输水系统示意图', fontsize=13, fontweight='bold')
        ax1.legend(fontsize=8, loc='upper right')
        ax1.grid(True, alpha=0.3)
        
        # 图2：能量线
        ax2 = plt.subplot(3, 3, 2)
        
        # 水库水面
        x_energy = [0, 2]
        E_energy = [self.H0, self.H0]
        
        # 管道段
        x_energy.extend([2, 5])
        E_energy.extend([self.H0, self.H0 - h_pipe])
        
        # 明渠段
        x_channel_e = np.linspace(5, 10, 20)
        E_channel = (self.H0 - h_pipe) - (x_channel_e - 5) * 0.5  # 简化处理
        x_energy.extend(x_channel_e.tolist())
        E_energy.extend(E_channel.tolist())
        
        ax2.plot(x_energy, E_energy, 'r-', linewidth=2.5, label='能量线')
        
        # 水面线
        x_water = [0, 2, 5]
        z_water_line = [self.H0, self.H0, z_pipe_out]
        x_water.extend(x_channel.tolist())
        z_water_line.extend(z_water.tolist())
        
        ax2.plot(x_water, z_water_line, 'b-', linewidth=2, label='水面线')
        
        # 标注损失
        ax2.annotate('', xy=(3.5, self.H0 - h_pipe), xytext=(3.5, self.H0),
                    arrowprops=dict(arrowstyle='<->', color='red', lw=2))
        ax2.text(4, self.H0 - h_pipe/2, f'管道损失\n{h_pipe:.2f}m',
                fontsize=9, fontweight='bold', color='red')
        
        ax2.set_xlabel('水平距离 (m)', fontsize=10, fontweight='bold')
        ax2.set_ylabel('高程/能量 (m)', fontsize=10, fontweight='bold')
        ax2.set_title('系统能量线与水面线', fontsize=13, fontweight='bold')
        ax2.legend(fontsize=9)
        ax2.grid(True, alpha=0.3)
        
        # 图3：流量与损失
        ax3 = plt.subplot(3, 3, 3)
        
        Q_test = np.linspace(0.1, Q * 1.5, 50)
        h_loss_test = np.array([self.pipe_head_loss(q) for q in Q_test])
        
        ax3.plot(Q_test, h_loss_test, 'b-', linewidth=2.5, label='管道损失')
        ax3.plot([Q], [h_pipe], 'ro', markersize=12, label='当前工况')
        
        ax3.set_xlabel('流量 Q (m³/s)', fontsize=11, fontweight='bold')
        ax3.set_ylabel('水头损失 h_f (m)', fontsize=11, fontweight='bold')
        ax3.set_title('流量与管道损失关系', fontsize=13, fontweight='bold')
        ax3.legend(fontsize=10)
        ax3.grid(True, alpha=0.3)
        
        # 标注关系
        ax3.text(Q * 0.8, max(h_loss_test) * 0.7,
                'h_f ∝ Q²\n（平方关系）',
                fontsize=10, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        # 图4：明渠断面
        ax4 = plt.subplot(3, 3, 4)
        
        # 绘制断面
        x_section = np.array([0, 0, self.b, self.b, 0])
        y_section = np.array([0, h_n, h_n, 0, 0])
        
        ax4.plot(x_section, y_section, 'b-', linewidth=3)
        ax4.fill(x_section, y_section, color='lightblue', alpha=0.5)
        
        # 标注
        ax4.annotate('', xy=(self.b, -0.1), xytext=(0, -0.1),
                    arrowprops=dict(arrowstyle='<->', color='red', lw=2))
        ax4.text(self.b/2, -0.2, f'b = {self.b}m', ha='center',
                fontsize=10, fontweight='bold', color='red')
        
        ax4.annotate('', xy=(-0.1, h_n), xytext=(-0.1, 0),
                    arrowprops=dict(arrowstyle='<->', color='red', lw=2))
        ax4.text(-0.3, h_n/2, f'h = {h_n:.2f}m', va='center',
                fontsize=10, fontweight='bold', color='red', rotation=90)
        
        # 流速矢量
        ax4.arrow(self.b/2, h_n/2, 0.3, 0, head_width=0.1, head_length=0.1,
                 fc='red', ec='red')
        ax4.text(self.b/2 + 0.5, h_n/2, f'v={v_channel:.2f}m/s',
                fontsize=10, fontweight='bold', color='red')
        
        # 佛汝德数
        flow_type = '缓流' if Fr < 1 else ('急流' if Fr > 1 else '临界流')
        ax4.text(self.b/2, h_n + 0.2, f'Fr={Fr:.2f}\n{flow_type}',
                ha='center', fontsize=10, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        ax4.set_xlim(-0.5, self.b + 0.8)
        ax4.set_ylim(-0.3, h_n + 0.5)
        ax4.set_aspect('equal')
        ax4.set_xlabel('宽度 (m)', fontsize=10, fontweight='bold')
        ax4.set_ylabel('高度 (m)', fontsize=10, fontweight='bold')
        ax4.set_title('明渠断面与流态', fontsize=13, fontweight='bold')
        ax4.grid(True, alpha=0.3)
        
        # 图5：管径优化
        ax5 = plt.subplot(3, 3, 5)
        
        d_array, Q_d, h_loss_d, eff_d = self.diameter_optimization()
        
        ax5_twin = ax5.twinx()
        
        line1 = ax5.plot(d_array * 1000, Q_d, 'b-', linewidth=2.5,
                        label='流量Q', marker='o', markersize=4, markevery=5)
        line2 = ax5_twin.plot(d_array * 1000, eff_d * 100, 'r-', linewidth=2.5,
                             label='效率η', marker='s', markersize=4, markevery=5)
        
        # 当前直径
        ax5.plot([self.d * 1000], [Q], 'go', markersize=12, label='当前直径')
        
        ax5.set_xlabel('管径 d (mm)', fontsize=11, fontweight='bold')
        ax5.set_ylabel('流量 Q (m³/s)', fontsize=11, fontweight='bold', color='b')
        ax5_twin.set_ylabel('效率 η (%)', fontsize=11, fontweight='bold', color='r')
        ax5.set_title('管径优化分析', fontsize=13, fontweight='bold')
        
        ax5.tick_params(axis='y', labelcolor='b')
        ax5_twin.tick_params(axis='y', labelcolor='r')
        
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax5.legend(lines, labels, fontsize=9)
        ax5.grid(True, alpha=0.3)
        
        # 图6：系统参数汇总
        ax6 = plt.subplot(3, 3, 6)
        
        params_text = f"""
系统运行参数

【流量】
Q = {Q:.3f} m³/s = {Q*1000:.1f} L/s

【管道】
水头损失：{h_pipe:.2f} m
出口压力：{p_out/1000:.1f} kPa
流速：{Q/(np.pi*self.d**2/4):.2f} m/s

【明渠】
正常水深：{h_n:.3f} m
流速：{v_channel:.2f} m/s
佛汝德数：{Fr:.2f}（{flow_type}）

【系统效率】
η = {efficiency*100:.1f}%

【总水头】
ΔH = {self.H0 - self.H1:.1f} m
"""
        
        ax6.text(0.1, 0.5, params_text, fontsize=11, fontfamily='monospace',
                verticalalignment='center',
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
        ax6.axis('off')
        ax6.set_title('系统参数汇总', fontsize=13, fontweight='bold')
        
        # 图7：压力分布
        ax7 = plt.subplot(3, 3, 7)
        
        # 管道沿程压力
        x_pipe = np.linspace(0, self.L, 50)
        # 简化：线性压降
        p_inlet = self.rho * self.g * (self.H0 - 5)  # 假设管道入口高程
        p_pipe = p_inlet - (p_inlet - p_out) * x_pipe / self.L
        
        ax7.plot(x_pipe, p_pipe / 1000, 'b-', linewidth=2.5, label='管道压力')
        ax7.plot([self.L], [p_out / 1000], 'ro', markersize=12,
                label='出口压力')
        
        ax7.set_xlabel('管道长度 x (m)', fontsize=11, fontweight='bold')
        ax7.set_ylabel('压力 p (kPa)', fontsize=11, fontweight='bold')
        ax7.set_title('管道沿程压力分布', fontsize=13, fontweight='bold')
        ax7.legend(fontsize=10)
        ax7.grid(True, alpha=0.3)
        
        # 图8：能量分配
        ax8 = plt.subplot(3, 3, 8)
        
        energy_types = ['有效水头', '管道损失', '明渠势能']
        h_total = self.H0 - self.H1
        energy_values = [
            h_total - h_pipe,
            h_pipe,
            h_n
        ]
        colors_energy = ['green', 'red', 'blue']
        
        wedges, texts, autotexts = ax8.pie(energy_values, labels=energy_types,
                                           colors=colors_energy, autopct='%1.1f%%',
                                           startangle=90)
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(11)
            autotext.set_fontweight('bold')
        
        ax8.set_title('能量分配', fontsize=13, fontweight='bold')
        
        # 图9：优化建议
        ax9 = plt.subplot(3, 3, 9)
        
        # 计算优化潜力
        d_opt_idx = np.argmax(eff_d)
        d_opt = d_array[d_opt_idx]
        Q_opt = Q_d[d_opt_idx]
        eff_opt = eff_d[d_opt_idx]
        
        optimization_text = f"""
优化建议

【当前状态】
• 流量：{Q:.3f} m³/s
• 效率：{efficiency*100:.1f}%
• 管道损失：{h_pipe:.2f} m

【优化方案】
1. 管径优化
   推荐直径：{d_opt*1000:.0f} mm
   预期流量：{Q_opt:.3f} m³/s
   预期效率：{eff_opt*100:.1f}%
   
2. 明渠优化
   {'✓ 流态正常（缓流）' if Fr < 0.8 else '⚠ 考虑加大断面'}
   
3. 系统建议
   {'✓ 系统运行良好' if efficiency > 0.7 else '⚠ 效率偏低，建议优化'}
"""
        
        ax9.text(0.1, 0.5, optimization_text, fontsize=10, fontfamily='monospace',
                verticalalignment='center',
                bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
        ax9.axis('off')
        ax9.set_title('优化建议', fontsize=13, fontweight='bold')
        
        plt.tight_layout()
        plt.show()
    
    def print_results(self):
        """打印计算结果"""
        print("=" * 80)
        print("管渠联合输水系统综合计算")
        print("=" * 80)
        
        print(f"\n系统参数：")
        print(f"  【管道部分】")
        print(f"    上游水库水位：H₀ = {self.H0}m")
        print(f"    管道直径：d = {self.d}m = {self.d*1000}mm")
        print(f"    管道长度：L = {self.L}m")
        print(f"    粗糙系数：n = {self.n_pipe}")
        
        print(f"\n  【明渠部分】")
        print(f"    渠底宽度：b = {self.b}m")
        print(f"    渠底坡度：i = {self.i} = 1/{1/self.i:.0f}")
        print(f"    粗糙系数：n = {self.n_channel}")
        print(f"    下游水位：H₁ = {self.H1}m")
        
        # (1) 系统流量
        Q = self.system_flow_rate()
        
        print(f"\n(1) 系统流量：")
        print(f"  通过能量方程迭代求解：")
        print(f"  H₀ = H₁ + h_管道 + E_明渠")
        print(f"\n  计算结果：")
        print(f"    Q = {Q:.4f} m³/s")
        print(f"      = {Q*1000:.2f} L/s")
        print(f"      = {Q*3600:.1f} m³/h")
        print(f"      = {Q*86400:.0f} m³/d")
        
        # (2) 管道出口压力
        p_out = self.pipe_outlet_pressure(Q)
        h_pipe = self.pipe_head_loss(Q)
        
        print(f"\n(2) 管道出口压力：")
        print(f"  管道水头损失：h_f = {h_pipe:.3f} m")
        
        A_pipe = np.pi * self.d**2 / 4
        v_pipe = Q / A_pipe
        print(f"  管道流速：v = {v_pipe:.3f} m/s")
        
        print(f"\n  出口压力：")
        print(f"    p_出口 = {p_out:.0f} Pa")
        print(f"          = {p_out/1000:.2f} kPa")
        print(f"          = {p_out/100000:.3f} bar")
        print(f"          ≈ {p_out/101325:.2f} atm")
        
        if p_out < 0:
            print(f"    ⚠ 警告：出口压力为负，系统设计不合理！")
        elif p_out < 20000:
            print(f"    ⚠ 注意：出口压力较低")
        else:
            print(f"    ✓ 出口压力正常")
        
        # (3) 明渠正常水深
        h_n = self.channel_normal_depth(Q)
        
        print(f"\n(3) 明渠正常水深：")
        print(f"  使用曼宁公式：")
        print(f"    v = (1/n) × R^(2/3) × i^(1/2)")
        print(f"    Q = A × v")
        
        A_channel = self.b * h_n
        chi_channel = self.b + 2 * h_n
        R_channel = A_channel / chi_channel
        v_channel = self.channel_velocity(Q, h_n)
        
        print(f"\n  计算结果：")
        print(f"    正常水深：h_n = {h_n:.4f} m")
        print(f"    过水面积：A = {A_channel:.4f} m²")
        print(f"    湿周：χ = {chi_channel:.4f} m")
        print(f"    水力半径：R = {R_channel:.4f} m")
        print(f"    流速：v = {v_channel:.3f} m/s")
        
        # (4) 明渠流态
        Fr = self.channel_froude_number(Q, h_n)
        
        print(f"\n(4) 明渠流态判别：")
        print(f"  佛汝德数：")
        print(f"    Fr = v / √(gh)")
        print(f"       = {v_channel:.3f} / √({self.g}×{h_n:.4f})")
        print(f"       = {Fr:.4f}")
        
        if Fr < 1:
            flow_type = "缓流"
            print(f"\n  ✓ {flow_type}（Fr < 1）")
            print(f"    特点：水深大、流速小、水流平稳")
        elif Fr > 1:
            flow_type = "急流"
            print(f"\n  ✓ {flow_type}（Fr > 1）")
            print(f"    特点：水深小、流速大、易产生波动")
        else:
            flow_type = "临界流"
            print(f"\n  ⚠ {flow_type}（Fr = 1）")
            print(f"    特点：不稳定状态，应避免")
        
        # 临界水深
        h_c = (Q**2 / (self.g * self.b**2))**(1/3)
        print(f"\n  临界水深：h_c = {h_c:.4f} m")
        print(f"  正常水深：h_n = {h_n:.4f} m")
        print(f"  比值：h_n/h_c = {h_n/h_c:.2f}")
        
        if h_n > h_c * 1.2:
            print(f"  → 明显缓流，渠道坡度较缓")
        elif h_n < h_c * 0.8:
            print(f"  → 明显急流，渠道坡度较陡")
        
        # (5) 系统优化建议
        efficiency = self.system_efficiency(Q)
        
        print(f"\n(5) 系统优化建议：")
        print(f"\n  【系统效率】")
        print(f"    总水头：ΔH = {self.H0 - self.H1:.2f} m")
        print(f"    管道损失：h_管 = {h_pipe:.2f} m（占{h_pipe/(self.H0-self.H1)*100:.1f}%）")
        print(f"    有效水头：h_有效 = {(self.H0-self.H1-h_pipe):.2f} m")
        print(f"    系统效率：η = {efficiency*100:.2f}%")
        
        if efficiency > 0.8:
            print(f"    ✓ 效率优良")
        elif efficiency > 0.6:
            print(f"    ○ 效率良好")
        else:
            print(f"    ⚠ 效率偏低，建议优化")
        
        print(f"\n  【管道优化】")
        if h_pipe / (self.H0 - self.H1) > 0.3:
            print(f"    ⚠ 管道损失过大，建议：")
            print(f"      • 增大管径（建议≥{self.d*1.2*1000:.0f}mm）")
            print(f"      • 减小管长（如可能）")
            print(f"      • 使用更光滑的管材")
        else:
            print(f"    ✓ 管道损失合理")
        
        # 雷诺数
        nu = 1.0e-6
        Re = v_pipe * self.d / nu
        print(f"\n    管道雷诺数：Re = {Re:.0f}")
        if Re > 4000:
            print(f"    → 紊流（Re > 4000）")
        
        print(f"\n  【明渠优化】")
        if Fr > 0.8:
            print(f"    ⚠ 佛汝德数较大，建议：")
            print(f"      • 增大渠宽（建议≥{self.b*1.2:.1f}m）")
            print(f"      • 减小渠底坡度")
            print(f"      以降低流速，提高稳定性")
        else:
            print(f"    ✓ 明渠流态良好")
        
        # 水力最优断面
        h_opt = self.b / 2
        if abs(h_n - h_opt) / h_opt > 0.2:
            print(f"\n    水力最优断面（矩形）：h_最优 = b/2 = {h_opt:.2f}m")
            print(f"    当前水深：h_n = {h_n:.2f}m")
            print(f"    建议调整断面尺寸以接近最优")
        
        print(f"\n  【运行建议】")
        print(f"    1. 定期检查管道磨损情况")
        print(f"    2. 监测明渠水深变化")
        print(f"    3. 防止明渠淤积")
        print(f"    4. 保持系统清洁，减少局部损失")
        
        print("\n" + "=" * 80)
        print("考试要点：")
        print("=" * 80)
        print("1. 管渠联合：能量方程H₀ = H₁ + h_管 + E_渠")
        print("2. 管道损失：达西公式h_f = λ(L/d)(v²/2g)")
        print("3. 明渠均匀流：曼宁公式v = (1/n)R^(2/3)i^(1/2)")
        print("4. 流态判别：Fr = v/√(gh)")
        print("5. 系统优化：效率、管径、流态分析")
        print("=" * 80)


def main():
    """主函数"""
    print("\n" + "💧" * 40)
    print("第03章 管流与明渠流 - 题目15：综合应用（管渠联合输水系统）")
    print("💧" * 40 + "\n")
    
    # 系统参数
    H0 = 50.0           # 上游水库水位50m
    H1 = 20.0           # 下游水位20m
    d = 0.5             # 管道直径0.5m
    L = 500.0           # 管道长度500m
    b = 2.0             # 明渠宽度2m
    i = 0.002           # 明渠坡度0.002
    n_pipe = 0.013      # 管道粗糙系数
    n_channel = 0.020   # 明渠粗糙系数
    
    # 创建系统对象
    system = PipeChannelSystem(H0=H0, H1=H1, d=d, L=L, b=b, i=i,
                              n_pipe=n_pipe, n_channel=n_channel)
    
    # 打印结果
    system.print_results()
    
    # 绘图
    print("\n正在绘制系统分析图...")
    system.plot_analysis()
    
    print("\n✅ 计算完成！")


if __name__ == "__main__":
    main()
