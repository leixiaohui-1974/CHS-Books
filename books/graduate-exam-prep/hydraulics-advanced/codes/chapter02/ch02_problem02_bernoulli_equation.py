#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第02章 流体动力学基础 - 题目2：伯努利方程应用

题目描述：
水平放置的文丘里管，直径从d1=0.2m渐变到d2=0.1m。
断面1处：压强p1=150kPa（表压），流速v1=2m/s。
忽略水头损失。求：
(1) 断面2处的流速v2
(2) 断面2处的压强p2
(3) 两断面的压强差Δp

知识点：
- 连续性方程
- 伯努利方程（能量守恒）
- 流速与压强的关系

作者：CHS-Books Team
日期：2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class BernoulliEquation:
    """伯努利方程计算类"""
    
    def __init__(self, d1: float, d2: float, p1: float, v1: float,
                 z1: float = 0, z2: float = 0, rho: float = 1000.0, g: float = 9.81):
        """
        初始化参数
        
        Parameters:
        -----------
        d1 : float
            断面1直径 (m)
        d2 : float
            断面2直径 (m)
        p1 : float
            断面1压强 (Pa)，表压
        v1 : float
            断面1流速 (m/s)
        z1 : float
            断面1高程 (m)，默认0
        z2 : float
            断面2高程 (m)，默认0
        rho : float
            密度 (kg/m³)
        g : float
            重力加速度 (m/s²)
        """
        self.d1 = d1
        self.d2 = d2
        self.p1 = p1
        self.v1 = v1
        self.z1 = z1
        self.z2 = z2
        self.rho = rho
        self.g = g
        
        # 计算断面面积
        self.A1 = np.pi * d1**2 / 4
        self.A2 = np.pi * d2**2 / 4
        
    def velocity_at_section2(self) -> float:
        """
        计算断面2流速（连续性方程）
        
        Returns:
        --------
        float : 断面2流速 (m/s)
        """
        return self.v1 * (self.d1 / self.d2)**2
    
    def pressure_at_section2(self) -> float:
        """
        计算断面2压强（伯努利方程）
        
        伯努利方程：
        z1 + p1/(ρg) + v1²/(2g) = z2 + p2/(ρg) + v2²/(2g)
        
        水平管道（z1=z2）：
        p2 = p1 + ρ/2(v1² - v2²)
        
        Returns:
        --------
        float : 断面2压强 (Pa)
        """
        v2 = self.velocity_at_section2()
        p2 = self.p1 + self.rho / 2 * (self.v1**2 - v2**2)
        return p2
    
    def pressure_difference(self) -> float:
        """
        计算压强差
        
        Returns:
        --------
        float : 压强差 Δp = p1 - p2 (Pa)
        """
        p2 = self.pressure_at_section2()
        return self.p1 - p2
    
    def total_head(self, section: int) -> float:
        """
        计算总水头
        
        Parameters:
        -----------
        section : int
            断面号（1或2）
            
        Returns:
        --------
        float : 总水头 H (m)
        """
        if section == 1:
            return self.z1 + self.p1/(self.rho*self.g) + self.v1**2/(2*self.g)
        elif section == 2:
            v2 = self.velocity_at_section2()
            p2 = self.pressure_at_section2()
            return self.z2 + p2/(self.rho*self.g) + v2**2/(2*self.g)
    
    def pressure_head(self, section: int) -> float:
        """
        计算测压管水头
        
        Parameters:
        -----------
        section : int
            断面号（1或2）
            
        Returns:
        --------
        float : 测压管水头 (m)
        """
        if section == 1:
            return self.z1 + self.p1/(self.rho*self.g)
        elif section == 2:
            p2 = self.pressure_at_section2()
            return self.z2 + p2/(self.rho*self.g)
    
    def velocity_head(self, section: int) -> float:
        """
        计算流速水头
        
        Parameters:
        -----------
        section : int
            断面号（1或2）
            
        Returns:
        --------
        float : 流速水头 (m)
        """
        if section == 1:
            return self.v1**2 / (2*self.g)
        elif section == 2:
            v2 = self.velocity_at_section2()
            return v2**2 / (2*self.g)
    
    def plot_venturi_diagram(self):
        """绘制文丘里管示意图和能量线"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # 图1：文丘里管结构示意图
        ax1 = axes[0, 0]
        
        # 绘制管道
        x = np.linspace(0, 10, 100)
        y_top = self.d1/2 - (self.d1 - self.d2)/2 * np.minimum(x/3, 1)
        y_bottom = -self.d1/2 + (self.d1 - self.d2)/2 * np.minimum(x/3, 1)
        
        ax1.fill_between(x, y_bottom, y_top, color='lightgray', alpha=0.7, label='文丘里管')
        ax1.plot(x, y_top, 'k-', linewidth=2)
        ax1.plot(x, y_bottom, 'k-', linewidth=2)
        
        # 断面标注
        ax1.plot([0, 0], [-self.d1/2, self.d1/2], 'b-', linewidth=3, label='断面1')
        ax1.plot([3, 3], [-self.d2/2, self.d2/2], 'r-', linewidth=3, label='断面2')
        
        # 流速箭头
        v2 = self.velocity_at_section2()
        ax1.arrow(-0.5, 0, 0.3, 0, head_width=0.02, head_length=0.1,
                 fc='blue', ec='blue', linewidth=2)
        ax1.text(-0.7, 0.05, f'v₁={self.v1}m/s', fontsize=10, color='blue', fontweight='bold')
        
        ax1.arrow(3.2, 0, 0.3, 0, head_width=0.02, head_length=0.1,
                 fc='red', ec='red', linewidth=2)
        ax1.text(3.5, 0.05, f'v₂={v2:.1f}m/s', fontsize=10, color='red', fontweight='bold')
        
        # 压强标注
        p2 = self.pressure_at_section2()
        ax1.text(0, -0.15, f'p₁={self.p1/1000:.0f}kPa', ha='center', fontsize=10, 
                color='blue', fontweight='bold')
        ax1.text(3, -0.15, f'p₂={p2/1000:.0f}kPa', ha='center', fontsize=10,
                color='red', fontweight='bold')
        
        ax1.set_xlim(-1, 10)
        ax1.set_ylim(-0.2, 0.2)
        ax1.set_xlabel('管道长度 (m)', fontsize=11, fontweight='bold')
        ax1.set_ylabel('半径 (m)', fontsize=11, fontweight='bold')
        ax1.set_title('文丘里管结构示意图', fontsize=13, fontweight='bold')
        ax1.legend(fontsize=9)
        ax1.grid(True, alpha=0.3)
        ax1.set_aspect('equal')
        
        # 图2：水头组成柱状图
        ax2 = axes[0, 1]
        
        # 计算各水头
        z_heads = [self.z1, self.z2]
        p_heads = [self.p1/(self.rho*self.g), p2/(self.rho*self.g)]
        v_heads = [self.v1**2/(2*self.g), v2**2/(2*self.g)]
        
        categories = ['断面1', '断面2']
        x_pos = np.arange(len(categories))
        width = 0.6
        
        # 堆叠柱状图
        bars1 = ax2.bar(x_pos, z_heads, width, label='位置水头', color='brown', alpha=0.7)
        bars2 = ax2.bar(x_pos, p_heads, width, bottom=z_heads, 
                       label='压强水头', color='blue', alpha=0.7)
        bars3 = ax2.bar(x_pos, v_heads, width, 
                       bottom=np.array(z_heads)+np.array(p_heads),
                       label='流速水头', color='red', alpha=0.7)
        
        # 标注总水头
        H1 = self.total_head(1)
        H2 = self.total_head(2)
        ax2.plot([-0.5, 1.5], [H1, H1], 'g--', linewidth=2, label='总水头（能量线）')
        ax2.text(-0.3, H1 + 0.3, f'H={H1:.2f}m', fontsize=10, 
                fontweight='bold', color='green')
        
        # 标注数值
        for i, (z, p, v) in enumerate(zip(z_heads, p_heads, v_heads)):
            if z > 0.1:
                ax2.text(i, z/2, f'{z:.2f}m', ha='center', fontsize=9, fontweight='bold')
            ax2.text(i, z + p/2, f'{p:.2f}m', ha='center', fontsize=9, fontweight='bold')
            ax2.text(i, z + p + v/2, f'{v:.2f}m', ha='center', fontsize=9, fontweight='bold')
        
        ax2.set_ylabel('水头 (m)', fontsize=11, fontweight='bold')
        ax2.set_title('水头组成对比', fontsize=13, fontweight='bold')
        ax2.set_xticks(x_pos)
        ax2.set_xticklabels(categories, fontsize=10)
        ax2.legend(fontsize=9)
        ax2.grid(True, alpha=0.3, axis='y')
        
        # 图3：压强与流速关系
        ax3 = axes[1, 0]
        
        positions = ['断面1', '断面2']
        pressures = [self.p1/1000, p2/1000]
        velocities = [self.v1, v2]
        
        x_pos = np.arange(len(positions))
        width = 0.35
        
        bars1 = ax3.bar(x_pos - width/2, pressures, width, label='压强 (kPa)',
                       color='lightblue', edgecolor='blue', linewidth=2)
        ax3_twin = ax3.twinx()
        bars2 = ax3_twin.bar(x_pos + width/2, velocities, width, label='流速 (m/s)',
                            color='lightcoral', edgecolor='red', linewidth=2)
        
        # 标注数值
        for bar, val in zip(bars1, pressures):
            ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                    f'{val:.0f}kPa', ha='center', fontsize=10, fontweight='bold')
        
        for bar, val in zip(bars2, velocities):
            ax3_twin.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                         f'{val:.1f}m/s', ha='center', fontsize=10, fontweight='bold')
        
        ax3.set_xlabel('断面', fontsize=11, fontweight='bold')
        ax3.set_ylabel('压强 (kPa)', fontsize=11, fontweight='bold', color='blue')
        ax3_twin.set_ylabel('流速 (m/s)', fontsize=11, fontweight='bold', color='red')
        ax3.set_title('压强与流速关系', fontsize=13, fontweight='bold')
        ax3.set_xticks(x_pos)
        ax3.set_xticklabels(positions, fontsize=10)
        ax3.tick_params(axis='y', labelcolor='blue')
        ax3_twin.tick_params(axis='y', labelcolor='red')
        ax3.grid(True, alpha=0.3, axis='y')
        
        # 标注关系
        ax3.text(0.5, max(pressures) * 0.7,
                '流速↑ → 压强↓\n（伯努利效应）',
                ha='center', fontsize=11, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        # 图4：能量线和测压管水头线
        ax4 = axes[1, 1]
        
        # x坐标
        x_positions = [0, 3]
        
        # 总水头线（能量线）- 水平线
        H_line = [H1, H2]
        ax4.plot(x_positions, H_line, 'g-', linewidth=3, marker='o', 
                markersize=10, label='总水头线（能量线）')
        
        # 测压管水头线
        Hp1 = self.pressure_head(1)
        Hp2 = self.pressure_head(2)
        Hp_line = [Hp1, Hp2]
        ax4.plot(x_positions, Hp_line, 'b-', linewidth=3, marker='s',
                markersize=10, label='测压管水头线')
        
        # 管道中心线
        z_line = [self.z1, self.z2]
        ax4.plot(x_positions, z_line, 'k-', linewidth=2, label='管道中心线')
        
        # 标注数值
        for i, (x, H, Hp, z) in enumerate(zip(x_positions, H_line, Hp_line, z_line)):
            ax4.text(x + 0.2, H, f'H={H:.2f}m', fontsize=9, color='green', fontweight='bold')
            ax4.text(x + 0.2, Hp, f'Hp={Hp:.2f}m', fontsize=9, color='blue', fontweight='bold')
        
        # 标注流速水头
        hv1 = self.velocity_head(1)
        hv2 = self.velocity_head(2)
        ax4.annotate('', xy=(0, H1), xytext=(0, Hp1),
                    arrowprops=dict(arrowstyle='<->', color='red', lw=2))
        ax4.text(-0.3, (H1+Hp1)/2, f'hv₁={hv1:.2f}m', fontsize=9, color='red', fontweight='bold')
        
        ax4.annotate('', xy=(3, H2), xytext=(3, Hp2),
                    arrowprops=dict(arrowstyle='<->', color='red', lw=2))
        ax4.text(3.3, (H2+Hp2)/2, f'hv₂={hv2:.2f}m', fontsize=9, color='red', fontweight='bold')
        
        ax4.set_xlabel('沿程位置 (m)', fontsize=11, fontweight='bold')
        ax4.set_ylabel('水头 (m)', fontsize=11, fontweight='bold')
        ax4.set_title('能量线和测压管水头线', fontsize=13, fontweight='bold')
        ax4.legend(fontsize=9, loc='upper right')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    def print_results(self):
        """打印计算结果"""
        print("=" * 70)
        print("伯努利方程应用 - 文丘里管")
        print("=" * 70)
        
        print(f"\n输入参数：")
        print(f"  断面1：d1={self.d1}m, p1={self.p1/1000:.0f}kPa, v1={self.v1}m/s, z1={self.z1}m")
        print(f"  断面2：d2={self.d2}m, z2={self.z2}m")
        print(f"  水密度：ρ={self.rho}kg/m³")
        
        v2 = self.velocity_at_section2()
        print(f"\n(1) 断面2流速：")
        print(f"  连续性方程：A1·v1 = A2·v2")
        print(f"  v2 = v1 × (d1/d2)² = {self.v1} × ({self.d1}/{self.d2})²")
        print(f"     = {self.v1} × {(self.d1/self.d2)**2:.2f} = {v2:.2f} m/s")
        
        p2 = self.pressure_at_section2()
        print(f"\n(2) 断面2压强：")
        print(f"  伯努利方程（水平管，z1=z2）：")
        print(f"  p1/(ρg) + v1²/(2g) = p2/(ρg) + v2²/(2g)")
        print(f"  p2 = p1 + ρ/2 × (v1² - v2²)")
        print(f"     = {self.p1:.0f} + {self.rho}/2 × ({self.v1}² - {v2:.2f}²)")
        print(f"     = {self.p1:.0f} + {self.rho/2:.0f} × ({self.v1**2:.2f} - {v2**2:.2f})")
        print(f"     = {self.p1:.0f} + {self.rho/2:.0f} × {self.v1**2 - v2**2:.2f}")
        print(f"     = {self.p1:.0f} + {self.rho/2 * (self.v1**2 - v2**2):.0f}")
        print(f"     = {p2:.0f} Pa = {p2/1000:.0f} kPa")
        
        dp = self.pressure_difference()
        print(f"\n(3) 压强差：")
        print(f"  Δp = p1 - p2 = {self.p1/1000:.0f} - {p2/1000:.0f} = {dp/1000:.0f} kPa")
        print(f"  说明：流速增大4倍，压强降低{dp/1000:.0f}kPa")
        
        print(f"\n水头分析：")
        H1 = self.total_head(1)
        H2 = self.total_head(2)
        Hp1 = self.pressure_head(1)
        Hp2 = self.pressure_head(2)
        hv1 = self.velocity_head(1)
        hv2 = self.velocity_head(2)
        
        print(f"  断面1：")
        print(f"    位置水头 z1 = {self.z1:.2f} m")
        print(f"    压强水头 p1/(ρg) = {Hp1 - self.z1:.2f} m")
        print(f"    流速水头 v1²/(2g) = {hv1:.2f} m")
        print(f"    总水头 H1 = {H1:.2f} m")
        
        print(f"  断面2：")
        print(f"    位置水头 z2 = {self.z2:.2f} m")
        print(f"    压强水头 p2/(ρg) = {Hp2 - self.z2:.2f} m")
        print(f"    流速水头 v2²/(2g) = {hv2:.2f} m")
        print(f"    总水头 H2 = {H2:.2f} m")
        
        print(f"\n  验证：H1 = H2 = {H1:.2f} m ✓（理想流体，能量守恒）")
        
        print("\n" + "=" * 70)
        print("考试要点：")
        print("=" * 70)
        print("1. 伯努利方程：z + p/(ρg) + v²/(2g) = 常数（能量守恒）")
        print("2. 水平管道：p1/(ρg) + v1²/(2g) = p2/(ρg) + v2²/(2g)")
        print("3. 流速增大，压强降低（伯努利效应）")
        print("4. 总水头不变（理想流体），各项水头相互转换")
        print("5. 文丘里管原理：利用压差测流量")
        print("=" * 70)


def main():
    """主函数"""
    print("\n" + "💧" * 35)
    print("第02章 流体动力学基础 - 题目2：伯努利方程")
    print("💧" * 35 + "\n")
    
    # 题目参数
    d1 = 0.2      # 断面1直径0.2m
    d2 = 0.1      # 断面2直径0.1m
    p1 = 150000   # 断面1压强150kPa
    v1 = 2.0      # 断面1流速2m/s
    
    # 创建伯努利方程对象
    bernoulli = BernoulliEquation(d1=d1, d2=d2, p1=p1, v1=v1)
    
    # 打印结果
    bernoulli.print_results()
    
    # 绘图
    print("\n正在绘制文丘里管分析图...")
    bernoulli.plot_venturi_diagram()
    
    print("\n✅ 计算完成！")


if __name__ == "__main__":
    main()
