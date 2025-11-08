#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第04章 地下水与渗流 - 题目6：渗流场流网分析

题目描述：
某坝基下有一渗流场，已知：
- 上游水位H₁=10m
- 下游水位H₂=2m
- 坝基水平长度L=20m
- 渗透系数k=5×10⁻⁴cm/s
- 坝基厚度T=5m

求：
(1) 绘制渗流场流网（4条流线、5条等势线）
(2) 计算单宽流量q
(3) 计算坝基中点（x=10m）处的水头和流速
(4) 分析坝基出口处的渗透稳定性

知识点：
- 渗流网理论
- 流网法计算流量
- 达西定律
- 渗透稳定性

作者：CHS-Books Team
日期：2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch
import matplotlib.patches as mpatches

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class SeepageNetwork:
    """渗流网络分析类"""
    
    def __init__(self, H1: float, H2: float, L: float, T: float, k: float,
                 n_flow_lines: int = 4, n_equipotential_lines: int = 5):
        """
        初始化参数
        
        Parameters:
        -----------
        H1 : float
            上游水位 (m)
        H2 : float
            下游水位 (m)
        L : float
            坝基水平长度 (m)
        T : float
            坝基厚度 (m)
        k : float
            渗透系数 (m/s 或 m/d)
        n_flow_lines : int
            流线数量
        n_equipotential_lines : int
            等势线数量
        """
        self.H1 = H1
        self.H2 = H2
        self.L = L
        self.T = T
        self.k = k  # 假设已转换为m/d
        self.n_flow = n_flow_lines
        self.n_equi = n_equipotential_lines
        
        # 计算流道数和势降数
        self.m = n_flow_lines - 1  # 流道数
        self.n = n_equipotential_lines - 1  # 势降数
        self.delta_H = H1 - H2  # 总水头差
    
    def equipotential_heads(self) -> np.ndarray:
        """
        计算各等势线的水头值
        
        Returns:
        --------
        np.ndarray : 等势线水头数组
        """
        return np.linspace(self.H1, self.H2, self.n_equi)
    
    def unit_width_discharge_flownet(self) -> float:
        """
        流网法计算单宽流量
        
        q = k * ΔH * (m/n)
        
        Returns:
        --------
        float : 单宽流量 (m²/d)
        """
        return self.k * self.delta_H * (self.m / self.n)
    
    def unit_width_discharge_darcy(self) -> float:
        """
        达西定律计算单宽流量（简化）
        
        q = k * i * T = k * (ΔH/L) * T
        
        Returns:
        --------
        float : 单宽流量 (m²/d)
        """
        i = self.delta_H / self.L
        return self.k * i * self.T
    
    def head_at_position(self, x: float) -> float:
        """
        计算x位置处的水头（线性插值）
        
        Parameters:
        -----------
        x : float
            距上游的距离 (m)
            
        Returns:
        --------
        float : 水头 (m)
        """
        return self.H1 - (x / self.L) * self.delta_H
    
    def velocity_darcy(self) -> float:
        """
        计算达西流速（渗透流速）
        
        v = k * i = k * (ΔH/L)
        
        Returns:
        --------
        float : 渗透流速 (m/d)
        """
        i = self.delta_H / self.L
        return self.k * i
    
    def exit_gradient(self) -> float:
        """
        计算出口坡降
        
        i_exit = Δh / Δl
        
        Returns:
        --------
        float : 出口坡降
        """
        # 最后一个势降
        delta_h = self.delta_H / self.n
        # 最后一格长度（近似）
        delta_l = self.L / self.n
        return delta_h / delta_l
    
    def critical_gradient(self, gamma_s: float = 26.0, gamma_w: float = 10.0) -> float:
        """
        计算临界坡降
        
        i_cr = (γ_s - γ_w) / γ_w
        
        Parameters:
        -----------
        gamma_s : float
            土的饱和重度 (kN/m³)
        gamma_w : float
            水的重度 (kN/m³)
            
        Returns:
        --------
        float : 临界坡降
        """
        return (gamma_s - gamma_w) / gamma_w
    
    def safety_factor(self, gamma_s: float = 26.0, gamma_w: float = 10.0) -> float:
        """
        计算渗透稳定安全系数
        
        K = i_cr / i_exit
        
        Parameters:
        -----------
        gamma_s : float
            土的饱和重度 (kN/m³)
        gamma_w : float
            水的重度 (kN/m³)
            
        Returns:
        --------
        float : 安全系数
        """
        i_cr = self.critical_gradient(gamma_s, gamma_w)
        i_exit = self.exit_gradient()
        return i_cr / i_exit
    
    def permeability_analysis(self, k_range: tuple = (0.1, 1.0), 
                             n_points: int = 50) -> tuple:
        """
        渗透系数影响分析
        
        Parameters:
        -----------
        k_range : tuple
            渗透系数范围 (m/d)
        n_points : int
            计算点数
            
        Returns:
        --------
        tuple : (k_array, q_array, v_array)
        """
        k_array = np.linspace(k_range[0], k_range[1], n_points)
        q_array = k_array * self.delta_H * (self.m / self.n)
        v_array = k_array * (self.delta_H / self.L)
        
        return k_array, q_array, v_array
    
    def head_drop_analysis(self, dH_range: tuple = (2, 20), 
                          n_points: int = 50) -> tuple:
        """
        水头差影响分析
        
        Parameters:
        -----------
        dH_range : tuple
            水头差范围 (m)
        n_points : int
            计算点数
            
        Returns:
        --------
        tuple : (dH_array, q_array, i_exit_array, K_array)
        """
        dH_array = np.linspace(dH_range[0], dH_range[1], n_points)
        q_array = self.k * dH_array * (self.m / self.n)
        i_exit_array = (dH_array / self.n) / (self.L / self.n)
        
        i_cr = self.critical_gradient()
        K_array = i_cr / i_exit_array
        
        return dH_array, q_array, i_exit_array, K_array
    
    def plot_flow_net(self, ax):
        """绘制渗流网"""
        # 坝基轮廓
        dam_base = Rectangle((0, -self.T), self.L, self.T, 
                            linewidth=2, edgecolor='black', facecolor='lightgray', alpha=0.3)
        ax.add_patch(dam_base)
        
        # 上下游水位
        ax.plot([0, 0], [0, self.H1], 'b-', linewidth=3, label='上游水位')
        ax.plot([self.L, self.L], [0, self.H2], 'b-', linewidth=3, label='下游水位')
        
        # 等势线（竖直线，从上游到下游）
        x_equi = np.linspace(0, self.L, self.n_equi)
        heads = self.equipotential_heads()
        
        for i, (x, h) in enumerate(zip(x_equi, heads)):
            # 等势线
            ax.plot([x, x], [-self.T, 0], 'r--', linewidth=1.5, alpha=0.7)
            # 标注水头
            ax.text(x, 0.5, f'h={h:.1f}m', fontsize=8, ha='center',
                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        # 流线（水平，均匀分布）
        y_flow = np.linspace(-self.T, 0, self.n_flow)
        
        for i, y in enumerate(y_flow):
            # 基本流线（直线）
            x_line = np.linspace(0, self.L, 50)
            y_line = np.ones_like(x_line) * y
            ax.plot(x_line, y_line, 'b-', linewidth=1.5, alpha=0.6)
            
            # 在流线上添加箭头
            arrow_x = [self.L/4, self.L/2, 3*self.L/4]
            for ax_x in arrow_x:
                arrow = FancyArrowPatch((ax_x-0.5, y), (ax_x+0.5, y),
                                      arrowstyle='->', mutation_scale=15,
                                      linewidth=1.5, color='blue', alpha=0.6)
                ax.add_patch(arrow)
        
        # 标注
        ax.text(-1, self.H1/2, f'H₁={self.H1}m', fontsize=11, fontweight='bold',
               rotation=90, va='center')
        ax.text(self.L+1, self.H2/2, f'H₂={self.H2}m', fontsize=11, fontweight='bold',
               rotation=90, va='center')
        ax.text(self.L/2, -self.T-1, f'L={self.L}m', fontsize=11, fontweight='bold',
               ha='center')
        
        ax.set_xlim(-2, self.L+2)
        ax.set_ylim(-self.T-2, self.H1+1)
        ax.set_aspect('equal')
        ax.set_xlabel('水平距离 x (m)', fontsize=11, fontweight='bold')
        ax.set_ylabel('高程 (m)', fontsize=11, fontweight='bold')
        ax.set_title('渗流场流网图', fontsize=13, fontweight='bold')
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)
    
    def plot_analysis(self):
        """绘制渗流网络分析图"""
        fig = plt.figure(figsize=(16, 12))
        
        # 图1：渗流网
        ax1 = plt.subplot(3, 3, 1)
        self.plot_flow_net(ax1)
        
        # 图2：水头分布
        ax2 = plt.subplot(3, 3, 2)
        
        x_array = np.linspace(0, self.L, 100)
        h_array = np.array([self.head_at_position(x) for x in x_array])
        
        ax2.plot(x_array, h_array, 'b-', linewidth=2.5, label='水头线')
        ax2.axhline(y=self.H1, color='r', linestyle='--', linewidth=1.5, 
                   label=f'上游水位={self.H1}m')
        ax2.axhline(y=self.H2, color='g', linestyle='--', linewidth=1.5,
                   label=f'下游水位={self.H2}m')
        
        # 标注中点
        x_mid = self.L / 2
        h_mid = self.head_at_position(x_mid)
        ax2.plot([x_mid], [h_mid], 'ro', markersize=12,
                label=f'中点: x={x_mid}m, h={h_mid}m')
        
        ax2.set_xlabel('距离 x (m)', fontsize=11, fontweight='bold')
        ax2.set_ylabel('水头 h (m)', fontsize=11, fontweight='bold')
        ax2.set_title('水头沿程分布', fontsize=13, fontweight='bold')
        ax2.legend(fontsize=9)
        ax2.grid(True, alpha=0.3)
        
        # 图3：流速分布
        ax3 = plt.subplot(3, 3, 3)
        
        v_darcy = self.velocity_darcy()
        
        ax3.barh(['达西流速'], [v_darcy], color='skyblue', edgecolor='black', linewidth=2)
        ax3.set_xlabel('流速 (m/d)', fontsize=11, fontweight='bold')
        ax3.set_title(f'渗透流速（v={v_darcy:.4f} m/d）', fontsize=13, fontweight='bold')
        ax3.grid(True, alpha=0.3, axis='x')
        
        # 单位转换显示
        v_ms = v_darcy / 86400  # m/s
        v_um_s = v_ms * 1e6  # μm/s
        ax3.text(v_darcy/2, 0, f'{v_ms:.2e} m/s\n{v_um_s:.2f} μm/s',
                fontsize=10, ha='center', va='center', fontweight='bold')
        
        # 图4：单宽流量对比
        ax4 = plt.subplot(3, 3, 4)
        
        q_flownet = self.unit_width_discharge_flownet()
        q_darcy = self.unit_width_discharge_darcy()
        
        methods = ['流网法', '达西定律']
        q_values = [q_flownet, q_darcy]
        colors = ['steelblue', 'coral']
        
        bars = ax4.bar(methods, q_values, color=colors, edgecolor='black', linewidth=2)
        
        # 标注数值
        for bar, q in zip(bars, q_values):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height,
                    f'{q:.3f}', ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        ax4.set_ylabel('单宽流量 (m²/d)', fontsize=11, fontweight='bold')
        ax4.set_title('单宽流量计算对比', fontsize=13, fontweight='bold')
        ax4.grid(True, alpha=0.3, axis='y')
        
        # 图5：渗透稳定性
        ax5 = plt.subplot(3, 3, 5)
        
        i_exit = self.exit_gradient()
        i_cr = self.critical_gradient()
        K_safety = self.safety_factor()
        
        categories = ['出口坡降\ni_exit', '临界坡降\ni_cr']
        values = [i_exit, i_cr]
        colors_grad = ['orange', 'green']
        
        bars = ax5.bar(categories, values, color=colors_grad, edgecolor='black', linewidth=2)
        
        # 标注
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax5.text(bar.get_x() + bar.get_width()/2., height,
                    f'{val:.2f}', ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        # 安全系数标注
        ax5.text(0.5, max(values)*0.9, f'安全系数 K = {K_safety:.2f}',
                fontsize=12, ha='center', fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='lightgreen' if K_safety > 2 else 'yellow'))
        
        # 安全判定
        stability = '稳定 ✓' if K_safety >= 2.0 else '不稳定 ✗'
        color_text = 'green' if K_safety >= 2.0 else 'red'
        ax5.text(0.5, max(values)*0.75, stability,
                fontsize=14, ha='center', fontweight='bold', color=color_text)
        
        ax5.set_ylabel('坡降', fontsize=11, fontweight='bold')
        ax5.set_title('渗透稳定性分析', fontsize=13, fontweight='bold')
        ax5.grid(True, alpha=0.3, axis='y')
        
        # 图6：渗透系数影响
        ax6 = plt.subplot(3, 3, 6)
        
        k_array, q_array, v_array = self.permeability_analysis()
        
        ax6_twin = ax6.twinx()
        
        line1 = ax6.plot(k_array, q_array, 'b-', linewidth=2.5, label='单宽流量q')
        line2 = ax6_twin.plot(k_array, v_array, 'r--', linewidth=2.5, label='流速v')
        
        # 标注当前值
        ax6.plot([self.k], [q_flownet], 'bo', markersize=10)
        ax6_twin.plot([self.k], [v_darcy], 'ro', markersize=10)
        
        ax6.set_xlabel('渗透系数 k (m/d)', fontsize=11, fontweight='bold')
        ax6.set_ylabel('单宽流量 q (m²/d)', fontsize=11, fontweight='bold', color='b')
        ax6_twin.set_ylabel('流速 v (m/d)', fontsize=11, fontweight='bold', color='r')
        ax6.set_title('渗透系数的影响', fontsize=13, fontweight='bold')
        
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax6.legend(lines, labels, fontsize=9)
        ax6.grid(True, alpha=0.3)
        
        # 图7：水头差影响
        ax7 = plt.subplot(3, 3, 7)
        
        dH_array, q_array_dH, i_exit_array, K_array = self.head_drop_analysis()
        
        ax7_twin = ax7.twinx()
        
        line1 = ax7.plot(dH_array, q_array_dH, 'b-', linewidth=2.5, label='单宽流量q')
        line2 = ax7_twin.plot(dH_array, K_array, 'g--', linewidth=2.5, label='安全系数K')
        
        # 安全线
        ax7_twin.axhline(y=2.0, color='r', linestyle=':', linewidth=2, label='K=2.0(安全线)')
        
        ax7.set_xlabel('水头差 ΔH (m)', fontsize=11, fontweight='bold')
        ax7.set_ylabel('单宽流量 q (m²/d)', fontsize=11, fontweight='bold', color='b')
        ax7_twin.set_ylabel('安全系数 K', fontsize=11, fontweight='bold', color='g')
        ax7.set_title('水头差的影响', fontsize=13, fontweight='bold')
        
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax7.legend(lines, labels, fontsize=9)
        ax7.grid(True, alpha=0.3)
        
        # 图8：参数汇总
        ax8 = plt.subplot(3, 3, 8)
        
        x_mid = self.L / 2
        h_mid = self.head_at_position(x_mid)
        
        params_text = f"""
渗流场分析结果

【边界条件】
上游水位：H₁ = {self.H1} m
下游水位：H₂ = {self.H2} m
水头差：ΔH = {self.delta_H} m

【几何参数】
坝基长度：L = {self.L} m
坝基厚度：T = {self.T} m
渗透系数：k = {self.k} m/d

【流网参数】
流线数：{self.n_flow}
等势线数：{self.n_equi}
流道数：m = {self.m}
势降数：n = {self.n}

【计算结果】
单宽流量（流网法）：q = {q_flownet:.4f} m²/d
单宽流量（达西法）：q = {q_darcy:.4f} m²/d
中点水头：h = {h_mid:.2f} m
达西流速：v = {v_darcy:.4f} m/d

【渗透稳定性】
出口坡降：i_exit = {i_exit:.3f}
临界坡降：i_cr = {i_cr:.3f}
安全系数：K = {K_safety:.2f}
判定：{'稳定' if K_safety >= 2.0 else '不稳定'}
"""
        
        ax8.text(0.1, 0.5, params_text, fontsize=9, fontfamily='monospace',
                verticalalignment='center',
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
        ax8.axis('off')
        ax8.set_title('计算结果汇总', fontsize=13, fontweight='bold')
        
        # 图9：公式总结
        ax9 = plt.subplot(3, 3, 9)
        
        formula_text = """
渗流网理论

【流网法】
q = k·ΔH·(m/n)
m = 流道数（流线数-1）
n = 势降数（等势线数-1）

【达西定律】
q = k·i·T = k·(ΔH/L)·T
v = k·i = k·(ΔH/L)

【水头分布】
h(x) = H₁ - (x/L)·ΔH

【渗透稳定性】
i_cr = (γ_s - γ_w)/γ_w
K = i_cr / i_exit ≥ 2.0

【出口坡降】
i_exit = Δh / Δl
"""
        
        ax9.text(0.1, 0.5, formula_text, fontsize=9, fontfamily='monospace',
                verticalalignment='center',
                bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
        ax9.axis('off')
        ax9.set_title('公式总结', fontsize=13, fontweight='bold')
        
        plt.tight_layout()
        plt.show()
    
    def print_results(self):
        """打印计算结果"""
        print("=" * 70)
        print("渗流场流网分析")
        print("=" * 70)
        
        print(f"\n输入参数：")
        print(f"  上游水位：H₁ = {self.H1} m")
        print(f"  下游水位：H₂ = {self.H2} m")
        print(f"  水头差：ΔH = {self.delta_H} m")
        print(f"  坝基长度：L = {self.L} m")
        print(f"  坝基厚度：T = {self.T} m")
        print(f"  渗透系数：k = {self.k} m/d = {self.k/86400:.2e} m/s")
        
        print(f"\n(1) 渗流场流网：")
        print(f"  流线数量：{self.n_flow} 条")
        print(f"  等势线数量：{self.n_equi} 条")
        print(f"  流道数：m = {self.n_flow} - 1 = {self.m}")
        print(f"  势降数：n = {self.n_equi} - 1 = {self.n}")
        
        print(f"\n  等势线水头分布：")
        heads = self.equipotential_heads()
        for i, h in enumerate(heads):
            print(f"    等势线{i+1}：h = {h:.2f} m")
        
        print(f"\n(2) 单宽流量计算：")
        
        q_flownet = self.unit_width_discharge_flownet()
        print(f"\n  【流网法】：")
        print(f"    q = k·ΔH·(m/n)")
        print(f"      = {self.k} × {self.delta_H} × ({self.m}/{self.n})")
        print(f"      = {q_flownet:.4f} m²/d")
        
        q_darcy = self.unit_width_discharge_darcy()
        print(f"\n  【达西定律】（简化）：")
        print(f"    q = k·i·T = k·(ΔH/L)·T")
        print(f"      = {self.k} × ({self.delta_H}/{self.L}) × {self.T}")
        print(f"      = {self.k} × {self.delta_H/self.L:.3f} × {self.T}")
        print(f"      = {q_darcy:.4f} m²/d")
        
        print(f"\n  对比：")
        print(f"    流网法更精确（考虑了流线弯曲）")
        print(f"    差值：{abs(q_flownet - q_darcy):.4f} m²/d")
        print(f"    相对误差：{abs(q_flownet - q_darcy)/q_flownet*100:.1f}%")
        
        print(f"\n(3) 坝基中点分析：")
        x_mid = self.L / 2
        h_mid = self.head_at_position(x_mid)
        v_darcy = self.velocity_darcy()
        
        print(f"  中点位置：x = {x_mid} m")
        
        print(f"\n  【水头】（线性插值）：")
        print(f"    h(x) = H₁ - (x/L)·ΔH")
        print(f"         = {self.H1} - ({x_mid}/{self.L}) × {self.delta_H}")
        print(f"         = {self.H1} - {x_mid/self.L} × {self.delta_H}")
        print(f"         = {h_mid:.2f} m")
        
        print(f"\n  【流速】（达西流速）：")
        print(f"    v = k·i = k·(ΔH/L)")
        print(f"      = {self.k} × ({self.delta_H}/{self.L})")
        print(f"      = {v_darcy:.4f} m/d")
        
        v_ms = v_darcy / 86400
        v_um_s = v_ms * 1e6
        print(f"\n  单位换算：")
        print(f"    v = {v_ms:.2e} m/s")
        print(f"    v = {v_um_s:.2f} μm/s")
        
        print(f"\n(4) 出口渗透稳定性分析：")
        
        i_exit = self.exit_gradient()
        print(f"\n  【出口坡降】：")
        print(f"    最后一格流网：")
        delta_h = self.delta_H / self.n
        delta_l = self.L / self.n
        print(f"      Δh = ΔH/n = {self.delta_H}/{self.n} = {delta_h:.2f} m")
        print(f"      Δl = L/n = {self.L}/{self.n} = {delta_l:.2f} m")
        print(f"    i_exit = Δh/Δl = {delta_h:.2f}/{delta_l:.2f} = {i_exit:.3f}")
        
        i_cr = self.critical_gradient()
        print(f"\n  【临界坡降】（砂土）：")
        print(f"    i_cr = (γ_s - γ_w) / γ_w")
        print(f"         = (26 - 10) / 10")
        print(f"         = {i_cr:.3f}")
        
        K_safety = self.safety_factor()
        print(f"\n  【安全系数】：")
        print(f"    K = i_cr / i_exit")
        print(f"      = {i_cr:.3f} / {i_exit:.3f}")
        print(f"      = {K_safety:.2f}")
        
        print(f"\n  【稳定判定】：")
        if K_safety >= 2.0:
            print(f"    ✓ 渗透稳定（K = {K_safety:.2f} ≥ 2.0）")
            print(f"    安全系数充足，无需额外工程措施")
        else:
            print(f"    ✗ 渗透不稳定（K = {K_safety:.2f} < 2.0）")
            print(f"    需要采取工程措施：")
            print(f"      - 延长渗径（下游设反滤层）")
            print(f"      - 设置排水沟")
            print(f"      - 加设截水墙")
        
        print("\n" + "=" * 70)
        print("考试要点：")
        print("=" * 70)
        print("1. 流网绘制：流线与等势线正交，网格近似正方形")
        print("2. 流网法：q = k·ΔH·(m/n)")
        print("3. 达西定律：q = k·i·T")
        print("4. 渗透稳定：K = i_cr/i_exit ≥ 2.0")
        print("5. 工程措施：反滤层、排水沟、截水墙")
        print("=" * 70)


def main():
    """主函数"""
    print("\n" + "💧" * 35)
    print("第04章 地下水与渗流 - 题目6：渗流场流网分析")
    print("💧" * 35 + "\n")
    
    # 题目参数
    H1 = 10.0         # 上游水位10m
    H2 = 2.0          # 下游水位2m
    L = 20.0          # 坝基长度20m
    T = 5.0           # 坝基厚度5m
    k_cm_s = 5e-4     # 渗透系数5×10⁻⁴cm/s
    
    # 单位转换：cm/s → m/d
    k = k_cm_s * 0.01 * 86400  # m/d
    
    print(f"单位转换：k = {k_cm_s} cm/s = {k:.3f} m/d\n")
    
    # 创建渗流网络对象
    seepage = SeepageNetwork(H1=H1, H2=H2, L=L, T=T, k=k,
                            n_flow_lines=4, n_equipotential_lines=5)
    
    # 打印结果
    seepage.print_results()
    
    # 绘图
    print("\n正在绘制渗流场分析图...")
    seepage.plot_analysis()
    
    print("\n✅ 计算完成！")


if __name__ == "__main__":
    main()
