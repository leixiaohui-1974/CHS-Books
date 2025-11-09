#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第02章 流体动力学基础 - 题目6：动量方程应用

题目描述：
水平放置的渐缩管道，d1=0.3m突变为d2=0.15m。
上游断面1：流速v1=2m/s，压强p1=200kPa（表压）
下游断面2：流速v2，压强p2
求：
(1) 断面2的流速v2
(2) 断面2的压强p2
(3) 水流对管道的作用力F

知识点：
- 动量方程（牛顿第二定律）
- 连续性方程
- 力的平衡分析

作者：CHS-Books Team
日期：2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyArrowPatch

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class MomentumEquation:
    """动量方程计算类"""
    
    def __init__(self, d1: float, d2: float, v1: float, p1: float,
                 rho: float = 1000.0, g: float = 9.81):
        """
        初始化参数
        
        Parameters:
        -----------
        d1 : float
            上游断面直径 (m)
        d2 : float
            下游断面直径 (m)
        v1 : float
            上游流速 (m/s)
        p1 : float
            上游压强 (Pa)，表压
        rho : float
            密度 (kg/m³)
        g : float
            重力加速度 (m/s²)
        """
        self.d1 = d1
        self.d2 = d2
        self.v1 = v1
        self.p1 = p1
        self.rho = rho
        self.g = g
        
        # 计算断面面积
        self.A1 = np.pi * d1**2 / 4
        self.A2 = np.pi * d2**2 / 4
    
    def velocity_at_section2(self) -> float:
        """
        计算下游流速（连续性方程）
        
        Returns:
        --------
        float : 下游流速 (m/s)
        """
        return self.v1 * (self.d1 / self.d2)**2
    
    def discharge(self) -> float:
        """
        计算流量
        
        Returns:
        --------
        float : 流量 (m³/s)
        """
        return self.A1 * self.v1
    
    def pressure_at_section2(self) -> float:
        """
        计算下游压强（伯努利方程）
        
        Returns:
        --------
        float : 下游压强 (Pa)
        """
        v2 = self.velocity_at_section2()
        p2 = self.p1 + self.rho / 2 * (self.v1**2 - v2**2)
        return p2
    
    def force_on_pipe(self) -> tuple:
        """
        计算水流对管道的作用力（动量方程）
        
        动量方程：
        ΣF = ρQ(v2 - v1)
        
        对于渐缩管，力的组成：
        F_pipe = p1·A1 - p2·A2 - ρQ(v2 - v1)
        
        Returns:
        --------
        tuple : (F_pipe, F_pressure, F_momentum)
            F_pipe : 管道对水流的作用力 (N)
            F_pressure : 压强力 (N)
            F_momentum : 动量变化力 (N)
        """
        v2 = self.velocity_at_section2()
        p2 = self.pressure_at_section2()
        Q = self.discharge()
        
        # 压强力
        F_pressure = self.p1 * self.A1 - p2 * self.A2
        
        # 动量变化力
        F_momentum = self.rho * Q * (v2 - self.v1)
        
        # 管道对水流的作用力
        F_pipe = F_pressure - F_momentum
        
        return F_pipe, F_pressure, F_momentum
    
    def plot_momentum_analysis(self):
        """绘制动量方程分析图"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # 图1：管道结构和受力示意图
        ax1 = axes[0, 0]
        
        # 绘制管道
        x_pipe = [0, 3, 5, 8]
        y_top = [self.d1/2, self.d1/2, self.d2/2, self.d2/2]
        y_bottom = [-self.d1/2, -self.d1/2, -self.d2/2, -self.d2/2]
        
        ax1.fill_between(x_pipe, y_bottom, y_top, color='lightgray', alpha=0.7, label='管道')
        ax1.plot(x_pipe, y_top, 'k-', linewidth=2)
        ax1.plot(x_pipe, y_bottom, 'k-', linewidth=2)
        
        # 断面标注
        ax1.plot([0, 0], [-self.d1/2, self.d1/2], 'b-', linewidth=3, label='断面1')
        ax1.plot([8, 8], [-self.d2/2, self.d2/2], 'r-', linewidth=3, label='断面2')
        
        # 流速箭头
        v2 = self.velocity_at_section2()
        ax1.arrow(-0.5, 0, 0.3, 0, head_width=0.03, head_length=0.15,
                 fc='blue', ec='blue', linewidth=2)
        ax1.text(-1, 0.05, f'v₁={self.v1}m/s', fontsize=10, color='blue', fontweight='bold')
        
        ax1.arrow(8.2, 0, 0.3, 0, head_width=0.02, head_length=0.15,
                 fc='red', ec='red', linewidth=2)
        ax1.text(8.5, 0.05, f'v₂={v2:.1f}m/s', fontsize=10, color='red', fontweight='bold')
        
        # 压强力箭头
        p2 = self.pressure_at_section2()
        ax1.arrow(0.2, 0, 0.8, 0, head_width=0.025, head_length=0.15,
                 fc='green', ec='green', linewidth=2.5, linestyle='--')
        ax1.text(0.6, -0.12, f'p₁A₁', fontsize=10, color='green', fontweight='bold')
        
        ax1.arrow(7.8, 0, -0.6, 0, head_width=0.02, head_length=0.12,
                 fc='orange', ec='orange', linewidth=2.5, linestyle='--')
        ax1.text(7, -0.1, f'p₂A₂', fontsize=10, color='orange', fontweight='bold')
        
        # 管道作用力
        F_pipe, _, _ = self.force_on_pipe()
        if F_pipe > 0:
            ax1.arrow(4, 0.2, 0.6, 0, head_width=0.025, head_length=0.15,
                     fc='purple', ec='purple', linewidth=3)
            ax1.text(4.7, 0.25, f'F_pipe={F_pipe/1000:.1f}kN', fontsize=10, 
                    color='purple', fontweight='bold')
        else:
            ax1.arrow(4, 0.2, -0.6, 0, head_width=0.025, head_length=0.15,
                     fc='purple', ec='purple', linewidth=3)
            ax1.text(2.5, 0.25, f'F_pipe={abs(F_pipe)/1000:.1f}kN', fontsize=10,
                    color='purple', fontweight='bold')
        
        ax1.set_xlim(-1.5, 9)
        ax1.set_ylim(-0.3, 0.35)
        ax1.set_xlabel('x方向 (m)', fontsize=11, fontweight='bold')
        ax1.set_ylabel('y方向 (m)', fontsize=11, fontweight='bold')
        ax1.set_title('管道受力分析示意图', fontsize=13, fontweight='bold')
        ax1.legend(fontsize=9, loc='upper right')
        ax1.grid(True, alpha=0.3)
        ax1.set_aspect('equal')
        
        # 图2：力的组成柱状图
        ax2 = axes[0, 1]
        
        F_pipe, F_pressure, F_momentum = self.force_on_pipe()
        
        forces = ['压强力\nF_p', '动量力\nF_m', '管道力\nF_pipe']
        values = [F_pressure/1000, F_momentum/1000, F_pipe/1000]
        colors = ['lightblue', 'lightcoral', 'lightgreen']
        
        bars = ax2.bar(forces, values, color=colors, edgecolor='black', linewidth=2, alpha=0.8)
        
        # 标注数值
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2, height + max(values)*0.05,
                    f'{val:.1f}kN', ha='center', fontsize=11, fontweight='bold')
        
        ax2.set_ylabel('力 (kN)', fontsize=11, fontweight='bold')
        ax2.set_title('力的组成', fontsize=13, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='y')
        
        # 标注动量方程
        ax2.text(0.5, max(values) * 0.6,
                f'F_pipe = F_p - F_m\n= {F_pressure/1000:.1f} - {F_momentum/1000:.1f}\n= {F_pipe/1000:.1f} kN',
                ha='center', fontsize=10, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        # 图3：流速与动量变化
        ax3 = axes[1, 0]
        
        sections = ['断面1', '断面2']
        velocities = [self.v1, v2]
        Q = self.discharge()
        momentums = [self.rho * Q * self.v1 / 1000, self.rho * Q * v2 / 1000]
        
        x_pos = np.arange(len(sections))
        width = 0.35
        
        bars1 = ax3.bar(x_pos - width/2, velocities, width, label='流速 (m/s)',
                       color='lightblue', edgecolor='blue', linewidth=2)
        ax3_twin = ax3.twinx()
        bars2 = ax3_twin.bar(x_pos + width/2, momentums, width, label='动量流率 (kN)',
                            color='lightcoral', edgecolor='red', linewidth=2)
        
        # 标注数值
        for bar, val in zip(bars1, velocities):
            ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                    f'{val:.1f}m/s', ha='center', fontsize=10, fontweight='bold')
        
        for bar, val in zip(bars2, momentums):
            ax3_twin.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(momentums)*0.05,
                         f'{val:.1f}kN', ha='center', fontsize=10, fontweight='bold')
        
        ax3.set_xlabel('断面', fontsize=11, fontweight='bold')
        ax3.set_ylabel('流速 (m/s)', fontsize=11, fontweight='bold', color='blue')
        ax3_twin.set_ylabel('动量流率 (kN)', fontsize=11, fontweight='bold', color='red')
        ax3.set_title('流速与动量变化', fontsize=13, fontweight='bold')
        ax3.set_xticks(x_pos)
        ax3.set_xticklabels(sections, fontsize=10)
        ax3.tick_params(axis='y', labelcolor='blue')
        ax3_twin.tick_params(axis='y', labelcolor='red')
        ax3.grid(True, alpha=0.3, axis='y')
        
        # 标注动量变化
        delta_momentum = momentums[1] - momentums[0]
        ax3.text(0.5, max(velocities) * 0.6,
                f'Δ(ρQv) = {delta_momentum:.1f}kN',
                ha='center', fontsize=11, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        # 图4：压强分布
        ax4 = axes[1, 1]
        
        sections = ['断面1', '断面2']
        pressures = [self.p1/1000, p2/1000]
        areas = [self.A1, self.A2]
        pressure_forces = [self.p1*self.A1/1000, p2*self.A2/1000]
        
        x_pos = np.arange(len(sections))
        
        # 压强
        bars1 = ax4.bar(x_pos - width/2, pressures, width, label='压强 (kPa)',
                       color='lightblue', edgecolor='blue', linewidth=2)
        
        # 压强力
        ax4_twin = ax4.twinx()
        bars2 = ax4_twin.bar(x_pos + width/2, pressure_forces, width, label='压强力 (kN)',
                            color='lightgreen', edgecolor='green', linewidth=2)
        
        # 标注数值
        for bar, val in zip(bars1, pressures):
            ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10,
                    f'{val:.0f}kPa', ha='center', fontsize=10, fontweight='bold')
        
        for bar, val in zip(bars2, pressure_forces):
            ax4_twin.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(pressure_forces)*0.05,
                         f'{val:.1f}kN', ha='center', fontsize=10, fontweight='bold')
        
        ax4.set_xlabel('断面', fontsize=11, fontweight='bold')
        ax4.set_ylabel('压强 (kPa)', fontsize=11, fontweight='bold', color='blue')
        ax4_twin.set_ylabel('压强力 (kN)', fontsize=11, fontweight='bold', color='green')
        ax4.set_title('压强分布', fontsize=13, fontweight='bold')
        ax4.set_xticks(x_pos)
        ax4.set_xticklabels(sections, fontsize=10)
        ax4.tick_params(axis='y', labelcolor='blue')
        ax4_twin.tick_params(axis='y', labelcolor='green')
        ax4.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plt.show()
    
    def print_results(self):
        """打印计算结果"""
        print("=" * 70)
        print("动量方程应用 - 渐缩管道")
        print("=" * 70)
        
        print(f"\n输入参数：")
        print(f"  上游断面1：d1={self.d1}m, v1={self.v1}m/s, p1={self.p1/1000:.0f}kPa")
        print(f"  下游断面2：d2={self.d2}m")
        print(f"  水密度：ρ={self.rho}kg/m³")
        
        # (1) 流速v2
        v2 = self.velocity_at_section2()
        print(f"\n(1) 断面2流速：")
        print(f"  连续性方程：A1·v1 = A2·v2")
        print(f"  v2 = v1 × (d1/d2)² = {self.v1} × ({self.d1}/{self.d2})²")
        print(f"     = {self.v1} × {(self.d1/self.d2)**2:.2f} = {v2:.2f} m/s")
        
        # (2) 压强p2
        p2 = self.pressure_at_section2()
        print(f"\n(2) 断面2压强：")
        print(f"  伯努利方程：p1 + ρv1²/2 = p2 + ρv2²/2")
        print(f"  p2 = p1 + ρ/2 × (v1² - v2²)")
        print(f"     = {self.p1:.0f} + {self.rho/2:.0f} × ({self.v1}² - {v2:.2f}²)")
        print(f"     = {self.p1:.0f} + {self.rho/2:.0f} × ({self.v1**2:.2f} - {v2**2:.2f})")
        print(f"     = {self.p1:.0f} + {self.rho/2 * (self.v1**2 - v2**2):.0f}")
        print(f"     = {p2:.0f} Pa = {p2/1000:.0f} kPa")
        
        # (3) 作用力F
        F_pipe, F_pressure, F_momentum = self.force_on_pipe()
        Q = self.discharge()
        
        print(f"\n(3) 水流对管道的作用力：")
        print(f"\n  流量：Q = A1·v1 = {self.A1:.4f} × {self.v1} = {Q:.4f} m³/s")
        
        print(f"\n  压强力：")
        print(f"    F_p = p1·A1 - p2·A2")
        print(f"        = {self.p1:.0f} × {self.A1:.4f} - {p2:.0f} × {self.A2:.4f}")
        print(f"        = {self.p1*self.A1:.0f} - {p2*self.A2:.0f}")
        print(f"        = {F_pressure:.0f} N = {F_pressure/1000:.1f} kN")
        
        print(f"\n  动量变化力：")
        print(f"    F_m = ρQ(v2 - v1)")
        print(f"        = {self.rho} × {Q:.4f} × ({v2:.2f} - {self.v1})")
        print(f"        = {self.rho} × {Q:.4f} × {v2 - self.v1:.2f}")
        print(f"        = {F_momentum:.0f} N = {F_momentum/1000:.1f} kN")
        
        print(f"\n  动量方程：")
        print(f"    F_pipe = F_p - F_m")
        print(f"           = {F_pressure:.0f} - {F_momentum:.0f}")
        print(f"           = {F_pipe:.0f} N = {F_pipe/1000:.1f} kN")
        
        if F_pipe > 0:
            print(f"\n  说明：F_pipe>0，管道对水流施加正向力（阻力），")
            print(f"       根据牛顿第三定律，水流对管道施加反向力（推力）")
            print(f"       水流对管道的作用力 = -{F_pipe/1000:.1f} kN（向左）")
        else:
            print(f"\n  说明：F_pipe<0，管道对水流施加负向力（拉力），")
            print(f"       根据牛顿第三定律，水流对管道施加正向力（推力）")
            print(f"       水流对管道的作用力 = {abs(F_pipe)/1000:.1f} kN（向右）")
        
        print("\n" + "=" * 70)
        print("考试要点：")
        print("=" * 70)
        print("1. 动量方程：ΣF = ρQ(v2 - v1)")
        print("2. 力的组成：压强力、动量变化力、管道力")
        print("3. 渐缩管道：流速增大，压强降低，管道受推力")
        print("4. 注意符号：力的方向与坐标系方向一致")
        print("5. 牛顿第三定律：水流对管道的力 = -管道对水流的力")
        print("=" * 70)


def main():
    """主函数"""
    print("\n" + "💧" * 35)
    print("第02章 流体动力学基础 - 题目6：动量方程")
    print("💧" * 35 + "\n")
    
    # 题目参数
    d1 = 0.3      # 上游直径0.3m
    d2 = 0.15     # 下游直径0.15m
    v1 = 2.0      # 上游流速2m/s
    p1 = 200000   # 上游压强200kPa
    
    # 创建动量方程对象
    momentum = MomentumEquation(d1=d1, d2=d2, v1=v1, p1=p1)
    
    # 打印结果
    momentum.print_results()
    
    # 绘图
    print("\n正在绘制动量方程分析图...")
    momentum.plot_momentum_analysis()
    
    print("\n✅ 计算完成！")


if __name__ == "__main__":
    main()
