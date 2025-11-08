#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第02章 流体动力学基础 - 题目1：连续性方程应用

题目描述：
圆形管道从直径d1=0.2m渐变到d2=0.1m，
断面1处流速v1=2m/s，水流不可压缩。求：
(1) 断面2处的流速v2
(2) 通过管道的流量Q
(3) 流量增加50%时断面2的流速

知识点：
- 连续性方程：A1v1 = A2v2
- 流量计算：Q = Av
- 流速与断面关系

作者：CHS-Books Team
日期：2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class ContinuityEquation:
    """连续性方程计算类"""
    
    def __init__(self, d1: float, d2: float, v1: float):
        """
        初始化参数
        
        Parameters:
        -----------
        d1 : float
            断面1直径 (m)
        d2 : float
            断面2直径 (m)
        v1 : float
            断面1流速 (m/s)
        """
        self.d1 = d1
        self.d2 = d2
        self.v1 = v1
        
        # 计算断面面积
        self.A1 = np.pi * d1**2 / 4
        self.A2 = np.pi * d2**2 / 4
        
    def velocity_at_section2(self) -> float:
        """
        计算断面2流速
        
        连续性方程：A1*v1 = A2*v2
        v2 = v1 * (A1/A2) = v1 * (d1/d2)²
        
        Returns:
        --------
        float : 断面2流速 (m/s)
        """
        return self.v1 * (self.d1 / self.d2)**2
    
    def discharge(self) -> float:
        """
        计算流量
        
        Q = A1*v1 = A2*v2
        
        Returns:
        --------
        float : 流量 (m³/s)
        """
        return self.A1 * self.v1
    
    def velocity_with_new_discharge(self, Q_ratio: float) -> tuple:
        """
        计算新流量下的流速
        
        Parameters:
        -----------
        Q_ratio : float
            流量变化比例（如1.5表示增加50%）
            
        Returns:
        --------
        tuple : (v1_new, v2_new) 新流速 (m/s)
        """
        Q_new = self.discharge() * Q_ratio
        v1_new = Q_new / self.A1
        v2_new = Q_new / self.A2
        return v1_new, v2_new
    
    def plot_pipe_diagram(self):
        """绘制管道渐变示意图"""
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        # 左图：管道示意图
        ax1 = axes[0]
        
        # 绘制渐变管道
        x = np.linspace(0, 10, 100)
        # 上边界
        y_top = self.d1/2 - (self.d1 - self.d2)/2 * x/10
        # 下边界
        y_bottom = -self.d1/2 + (self.d1 - self.d2)/2 * x/10
        
        ax1.fill_between(x, y_bottom, y_top, color='lightgray', alpha=0.7, label='管道')
        ax1.plot(x, y_top, 'k-', linewidth=2)
        ax1.plot(x, y_bottom, 'k-', linewidth=2)
        
        # 断面1
        ax1.plot([0, 0], [-self.d1/2, self.d1/2], 'b-', linewidth=3, label='断面1')
        ax1.text(0, self.d1/2 + 0.03, f'd₁={self.d1}m', ha='center', 
                fontsize=11, fontweight='bold', color='blue')
        
        # 断面2
        ax1.plot([10, 10], [-self.d2/2, self.d2/2], 'r-', linewidth=3, label='断面2')
        ax1.text(10, self.d2/2 + 0.03, f'd₂={self.d2}m', ha='center',
                fontsize=11, fontweight='bold', color='red')
        
        # 流速箭头
        v2 = self.velocity_at_section2()
        
        # 断面1流速
        ax1.arrow(-0.5, 0, 0.3, 0, head_width=0.02, head_length=0.1,
                 fc='blue', ec='blue', linewidth=2)
        ax1.text(-0.7, 0.05, f'v₁={self.v1}m/s', fontsize=10, 
                fontweight='bold', color='blue')
        
        # 断面2流速
        ax1.arrow(10.2, 0, 0.3, 0, head_width=0.02, head_length=0.1,
                 fc='red', ec='red', linewidth=2)
        ax1.text(10.5, 0.05, f'v₂={v2:.1f}m/s', fontsize=10,
                fontweight='bold', color='red')
        
        # 流量标注
        Q = self.discharge()
        ax1.text(5, -0.15, f'Q={Q:.4f}m³/s={Q*1000:.1f}L/s',
                ha='center', fontsize=11, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        ax1.set_xlim(-1, 11)
        ax1.set_ylim(-0.2, 0.2)
        ax1.set_xlabel('管道长度方向 (m)', fontsize=12, fontweight='bold')
        ax1.set_ylabel('管道半径 (m)', fontsize=12, fontweight='bold')
        ax1.set_title('管道渐变示意图', fontsize=14, fontweight='bold')
        ax1.legend(fontsize=10)
        ax1.grid(True, alpha=0.3)
        ax1.set_aspect('equal')
        
        # 右图：流速与断面积关系
        ax2 = axes[1]
        
        # 数据
        categories = ['断面1', '断面2']
        areas = [self.A1 * 1e4, self.A2 * 1e4]  # 转换为cm²
        velocities = [self.v1, v2]
        
        x_pos = np.arange(len(categories))
        width = 0.35
        
        # 绘制柱状图
        bars1 = ax2.bar(x_pos - width/2, areas, width, label='面积 (cm²)',
                       color='lightblue', edgecolor='blue', linewidth=2)
        ax2_twin = ax2.twinx()
        bars2 = ax2_twin.bar(x_pos + width/2, velocities, width, label='流速 (m/s)',
                            color='lightcoral', edgecolor='red', linewidth=2)
        
        # 标注数值
        for bar, val in zip(bars1, areas):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                    f'{val:.1f}cm²', ha='center', fontsize=10, fontweight='bold')
        
        for bar, val in zip(bars2, velocities):
            ax2_twin.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                         f'{val:.1f}m/s', ha='center', fontsize=10, fontweight='bold')
        
        ax2.set_xlabel('断面', fontsize=12, fontweight='bold')
        ax2.set_ylabel('面积 (cm²)', fontsize=12, fontweight='bold', color='blue')
        ax2_twin.set_ylabel('流速 (m/s)', fontsize=12, fontweight='bold', color='red')
        ax2.set_title('流速与断面积关系', fontsize=14, fontweight='bold')
        ax2.set_xticks(x_pos)
        ax2.set_xticklabels(categories, fontsize=11)
        ax2.tick_params(axis='y', labelcolor='blue')
        ax2_twin.tick_params(axis='y', labelcolor='red')
        ax2.grid(True, alpha=0.3, axis='y')
        
        # 标注关系
        ax2.text(0.5, max(areas) * 0.7, 
                f'面积比 A₁:A₂ = {self.A1/self.A2:.1f}:1\n'
                f'流速比 v₁:v₂ = 1:{v2/self.v1:.1f}',
                ha='center', fontsize=11, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        plt.tight_layout()
        plt.show()
    
    def plot_flow_change_analysis(self):
        """绘制流量变化分析图"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # 流量变化范围
        Q_ratios = np.linspace(0.5, 2.0, 50)
        v1_array = []
        v2_array = []
        
        for ratio in Q_ratios:
            v1_new, v2_new = self.velocity_with_new_discharge(ratio)
            v1_array.append(v1_new)
            v2_array.append(v2_new)
        
        # 绘制曲线
        ax.plot(Q_ratios * 100, v1_array, 'b-', linewidth=2.5, label='断面1流速')
        ax.plot(Q_ratios * 100, v2_array, 'r-', linewidth=2.5, label='断面2流速')
        
        # 标注原始点
        ax.plot(100, self.v1, 'bo', markersize=10, label='原始工况（断面1）')
        v2 = self.velocity_at_section2()
        ax.plot(100, v2, 'ro', markersize=10, label='原始工况（断面2）')
        
        # 标注流量增加50%的点
        v1_150, v2_150 = self.velocity_with_new_discharge(1.5)
        ax.plot(150, v1_150, 'b^', markersize=12)
        ax.plot(150, v2_150, 'r^', markersize=12)
        ax.text(155, v1_150, f'v₁={v1_150:.1f}m/s', fontsize=10, color='blue')
        ax.text(155, v2_150, f'v₂={v2_150:.1f}m/s', fontsize=10, color='red')
        
        ax.set_xlabel('流量比例 (%)', fontsize=12, fontweight='bold')
        ax.set_ylabel('流速 (m/s)', fontsize=12, fontweight='bold')
        ax.set_title('流量变化对流速的影响', fontsize=14, fontweight='bold')
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    def print_results(self):
        """打印计算结果"""
        print("=" * 70)
        print("连续性方程应用")
        print("=" * 70)
        
        print(f"\n输入参数：")
        print(f"  断面1直径 d1 = {self.d1} m = {self.d1*1000:.0f} mm")
        print(f"  断面2直径 d2 = {self.d2} m = {self.d2*1000:.0f} mm")
        print(f"  断面1流速 v1 = {self.v1} m/s")
        
        print(f"\n断面面积：")
        print(f"  A1 = πd1²/4 = π×{self.d1}²/4 = {self.A1:.6f} m²")
        print(f"                          = {self.A1*1e4:.2f} cm²")
        print(f"  A2 = πd2²/4 = π×{self.d2}²/4 = {self.A2:.6f} m²")
        print(f"                          = {self.A2*1e4:.2f} cm²")
        print(f"  面积比 A1/A2 = {self.A1/self.A2:.2f}")
        
        v2 = self.velocity_at_section2()
        print(f"\n(1) 断面2流速：")
        print(f"  连续性方程：A1·v1 = A2·v2")
        print(f"  v2 = v1 × (A1/A2) = v1 × (d1/d2)²")
        print(f"     = {self.v1} × ({self.d1}/{self.d2})²")
        print(f"     = {self.v1} × {(self.d1/self.d2)**2:.2f}")
        print(f"     = {v2:.2f} m/s")
        print(f"  说明：直径缩小到1/2，流速增大到4倍")
        
        Q = self.discharge()
        print(f"\n(2) 管道流量：")
        print(f"  Q = A1·v1 = {self.A1:.6f} × {self.v1}")
        print(f"    = {Q:.6f} m³/s")
        print(f"    = {Q*1000:.2f} L/s")
        print(f"  验证：Q = A2·v2 = {self.A2:.6f} × {v2:.2f}")
        print(f"       = {self.A2*v2:.6f} m³/s ✓")
        
        print(f"\n(3) 流量增加50%后：")
        Q_new = Q * 1.5
        v1_new, v2_new = self.velocity_with_new_discharge(1.5)
        print(f"  新流量 Q' = 1.5Q = {Q_new:.6f} m³/s = {Q_new*1000:.2f} L/s")
        print(f"  断面1流速 v1' = Q'/A1 = {v1_new:.2f} m/s （增加50%）")
        print(f"  断面2流速 v2' = Q'/A2 = {v2_new:.2f} m/s （增加50%）")
        print(f"  结论：流量变化n%，流速也变化n%（断面不变时）")
        
        print("\n" + "=" * 70)
        print("考试要点：")
        print("=" * 70)
        print("1. 连续性方程：A1v1 = A2v2（质量守恒）")
        print("2. 流速与断面积成反比：v2/v1 = A1/A2 = (d1/d2)²")
        print("3. 流量 Q = Av 在各断面处相等（不可压缩流体）")
        print("4. 断面缩小，流速增大；断面扩大，流速减小")
        print("=" * 70)


def main():
    """主函数"""
    print("\n" + "💧" * 35)
    print("第02章 流体动力学基础 - 题目1：连续性方程")
    print("💧" * 35 + "\n")
    
    # 题目参数
    d1 = 0.2  # 断面1直径0.2m
    d2 = 0.1  # 断面2直径0.1m
    v1 = 2.0  # 断面1流速2m/s
    
    # 创建连续性方程对象
    continuity = ContinuityEquation(d1=d1, d2=d2, v1=v1)
    
    # 打印结果
    continuity.print_results()
    
    # 绘图
    print("\n正在绘制管道示意图...")
    continuity.plot_pipe_diagram()
    
    print("\n正在绘制流量变化分析图...")
    continuity.plot_flow_change_analysis()
    
    print("\n✅ 计算完成！")


if __name__ == "__main__":
    main()
