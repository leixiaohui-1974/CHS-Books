#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第01章 静水力学 - 题目8：梯形闸门总压力

题目描述：
梯形闸门，上底b1=2m，下底b2=4m，高度h=3m，
闸门顶边距水面d=1m。求静水总压力和压力中心位置。

知识点：
- 梯形图形的形心位置
- 梯形惯性矩计算
- 压力中心位置

作者：CHS-Books Team
日期：2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class TrapezoidalGate:
    """梯形闸门静水总压力计算类"""
    
    def __init__(self, b1: float, b2: float, h: float, d: float, 
                 rho: float = 1000.0, g: float = 9.81):
        """
        初始化参数
        
        Parameters:
        -----------
        b1 : float
            梯形上底（顶边）宽度 (m)
        b2 : float
            梯形下底（底边）宽度 (m)
        h : float
            梯形高度 (m)
        d : float
            顶边距水面深度 (m)
        rho : float
            水密度 (kg/m³)
        g : float
            重力加速度 (m/s²)
        """
        self.b1 = b1
        self.b2 = b2
        self.h = h
        self.d = d
        self.rho = rho
        self.g = g
        
        # 计算梯形面积
        self.A = (b1 + b2) * h / 2
        
        # 梯形形心距顶边的距离
        self.yc_from_top = h * (2*b2 + b1) / (3 * (b1 + b2))
        
        # 形心距水面深度
        self.hc = d + self.yc_from_top
        
        # 梯形对通过底边的平行轴的惯性矩
        self.I0 = h**3 * (b1**2 + 4*b1*b2 + b2**2) / (36 * (b1 + b2))
        
        # 梯形对通过形心的水平轴的惯性矩
        self.Ic = self.I0 - self.A * self.yc_from_top**2
        
    def total_pressure(self) -> float:
        """
        计算静水总压力
        
        Returns:
        --------
        float : 总压力 (N)
        
        公式：P = ρg·hc·A
        """
        return self.rho * self.g * self.hc * self.A
    
    def pressure_center(self) -> tuple:
        """
        计算压力中心位置
        
        Returns:
        --------
        tuple : (yD, zD)
                yD: 压力中心距水面深度 (m)
                zD: 压力中心距闸门顶边距离 (m)
        
        公式：yD = hc + Ic/(A·hc)
        """
        yD = self.hc + self.Ic / (self.A * self.hc)
        zD = yD - self.d
        return yD, zD
    
    def pressure_at_depth(self, z: float) -> float:
        """
        计算沿闸门某位置的压强
        
        Parameters:
        -----------
        z : float
            距闸门顶边的距离 (m)
            
        Returns:
        --------
        float : 压强 (Pa)
        """
        depth = self.d + z
        return self.rho * self.g * depth
    
    def width_at_position(self, z: float) -> float:
        """
        计算梯形在某高度的宽度
        
        Parameters:
        -----------
        z : float
            距顶边的距离 (m)
            
        Returns:
        --------
        float : 宽度 (m)
        """
        return self.b1 + (self.b2 - self.b1) * z / self.h
    
    def plot_gate_diagram(self):
        """绘制梯形闸门示意图"""
        fig, axes = plt.subplots(1, 2, figsize=(14, 7))
        
        # 左图：闸门位置示意图
        ax1 = axes[0]
        
        # 绘制水体
        water_width = 6
        ax1.fill_between([0, water_width], [0, 0], [self.d + self.h + 1, self.d + self.h + 1],
                        color='lightblue', alpha=0.5, label='水体')
        ax1.plot([0, water_width], [0, 0], 'b-', linewidth=2, label='水面')
        
        # 绘制梯形闸门（位于x=3处）
        gate_x = 3
        # 梯形顶点坐标
        trap_x = [gate_x - self.b1/2, gate_x + self.b1/2, 
                  gate_x + self.b2/2, gate_x - self.b2/2]
        trap_y = [self.d, self.d, self.d + self.h, self.d + self.h]
        
        trap = patches.Polygon(list(zip(trap_x, trap_y)), 
                              closed=True, edgecolor='red', facecolor='gray',
                              alpha=0.7, linewidth=3, label='梯形闸门')
        ax1.add_patch(trap)
        
        # 标注尺寸
        # 上底
        ax1.plot([gate_x - self.b1/2, gate_x + self.b1/2], 
                [self.d - 0.2, self.d - 0.2], 'r-', linewidth=2)
        ax1.text(gate_x, self.d - 0.4, f'b₁={self.b1}m', 
                fontsize=11, ha='center', color='red', fontweight='bold')
        
        # 下底
        ax1.plot([gate_x - self.b2/2, gate_x + self.b2/2], 
                [self.d + self.h + 0.2, self.d + self.h + 0.2], 'r-', linewidth=2)
        ax1.text(gate_x, self.d + self.h + 0.4, f'b₂={self.b2}m', 
                fontsize=11, ha='center', color='red', fontweight='bold')
        
        # 高度
        ax1.annotate('', xy=(gate_x + self.b2/2 + 0.5, self.d), 
                    xytext=(gate_x + self.b2/2 + 0.5, self.d + self.h),
                    arrowprops=dict(arrowstyle='<->', color='black', lw=2))
        ax1.text(gate_x + self.b2/2 + 0.8, self.d + self.h/2, f'h={self.h}m', 
                fontsize=11, fontweight='bold')
        
        # 顶边距水面
        ax1.annotate('', xy=(0.5, 0), xytext=(0.5, self.d),
                    arrowprops=dict(arrowstyle='<->', color='blue', lw=2))
        ax1.text(0.1, self.d/2, f'd={self.d}m', fontsize=11, 
                fontweight='bold', color='blue')
        
        # 标注形心
        xc = gate_x
        yc = self.d + self.yc_from_top
        ax1.plot(xc, yc, 'go', markersize=12, label='形心C', zorder=5)
        ax1.text(xc - 0.8, yc, f'形心\nhc={self.hc:.3f}m', fontsize=10,
                bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
        
        # 标注压力中心
        yD, zD = self.pressure_center()
        ax1.plot(xc, yD, 'r*', markersize=15, label='压力中心D', zorder=5)
        ax1.text(xc + 0.6, yD, f'压力中心\nyD={yD:.3f}m', fontsize=10,
                bbox=dict(boxstyle='round', facecolor='pink', alpha=0.8))
        
        ax1.set_xlabel('横向位置 (m)', fontsize=12, fontweight='bold')
        ax1.set_ylabel('深度 (m)', fontsize=12, fontweight='bold')
        ax1.set_title('梯形闸门位置示意图', fontsize=14, fontweight='bold')
        ax1.legend(loc='upper right', fontsize=10)
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim(-0.5, water_width + 0.5)
        ax1.set_ylim(-1, self.d + self.h + 1.5)
        ax1.invert_yaxis()
        
        # 右图：压强分布
        ax2 = axes[1]
        
        z = np.linspace(0, self.h, 100)
        p = np.array([self.pressure_at_depth(zi) for zi in z])
        p_kpa = p / 1000
        
        # 绘制压强分布
        ax2.fill_betweenx(z, 0, p_kpa, alpha=0.3, color='blue')
        ax2.plot(p_kpa, z, 'b-', linewidth=2.5, label='压强分布')
        
        # 标注形心压强
        pc = self.rho * self.g * self.hc / 1000
        zc = self.yc_from_top
        ax2.plot(pc, zc, 'go', markersize=10, label='形心')
        ax2.text(pc + 2, zc, f'pc={pc:.2f}kPa', fontsize=10,
                bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))
        
        # 标注压力中心
        yD, zD = self.pressure_center()
        pD = self.rho * self.g * yD / 1000
        ax2.plot(pD, zD, 'r*', markersize=15, label='压力中心')
        ax2.text(pD + 2, zD, f'pD={pD:.2f}kPa', fontsize=10,
                bbox=dict(boxstyle='round', facecolor='pink', alpha=0.7))
        
        # 绘制总压力作用线
        P = self.total_pressure()
        P_kn = P / 1000
        arrow_start = pD - 5
        ax2.annotate('', xy=(arrow_start, zD), xytext=(0, zD),
                    arrowprops=dict(arrowstyle='->', color='red', lw=3))
        ax2.text(arrow_start/2, zD - 0.3, f'P={P_kn:.1f}kN', fontsize=11,
                fontweight='bold', color='red',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
        
        ax2.set_xlabel('压强 (kPa)', fontsize=12, fontweight='bold')
        ax2.set_ylabel('沿闸门高度 z (m)', fontsize=12, fontweight='bold')
        ax2.set_title('压强分布与总压力', fontsize=14, fontweight='bold')
        ax2.legend(loc='lower right', fontsize=10)
        ax2.grid(True, alpha=0.3)
        ax2.set_ylim(self.h, 0)
        
        plt.tight_layout()
        plt.show()
    
    def print_results(self):
        """打印计算结果"""
        print("=" * 70)
        print("梯形闸门静水总压力计算")
        print("=" * 70)
        
        print(f"\n输入参数：")
        print(f"  上底 b1 = {self.b1} m")
        print(f"  下底 b2 = {self.b2} m")
        print(f"  高度 h = {self.h} m")
        print(f"  顶边距水面 d = {self.d} m")
        
        print(f"\n几何参数：")
        print(f"  面积 A = (b1+b2)×h/2 = ({self.b1}+{self.b2})×{self.h}/2")
        print(f"         = {self.A} m²")
        print(f"  形心距顶边 yc = h(2b2+b1)/(3(b1+b2))")
        print(f"               = {self.h}×(2×{self.b2}+{self.b1})/(3×({self.b1}+{self.b2}))")
        print(f"               = {self.yc_from_top:.4f} m")
        print(f"  形心深度 hc = d + yc = {self.d} + {self.yc_from_top:.4f}")
        print(f"             = {self.hc:.4f} m")
        
        print(f"\n惯性矩：")
        print(f"  对底边的惯性矩 I0 = h³(b1²+4b1b2+b2²)/(36(b1+b2))")
        print(f"                    = {self.I0:.6f} m⁴")
        print(f"  对形心轴的惯性矩 Ic = I0 - A·yc²")
        print(f"                     = {self.I0:.6f} - {self.A}×{self.yc_from_top:.4f}²")
        print(f"                     = {self.Ic:.6f} m⁴")
        
        P = self.total_pressure()
        pc = self.rho * self.g * self.hc
        print(f"\n压力计算：")
        print(f"  形心处压强 pc = ρg·hc = {self.rho}×{self.g}×{self.hc:.4f}")
        print(f"                = {pc:.2f} Pa = {pc/1000:.2f} kPa")
        print(f"  总压力 P = pc × A = {pc:.2f} × {self.A}")
        print(f"           = {P:.2f} N = {P/1000:.2f} kN")
        
        yD, zD = self.pressure_center()
        print(f"\n压力中心：")
        print(f"  公式：yD = hc + Ic/(A·hc)")
        print(f"  yD = {self.hc:.4f} + {self.Ic:.6f}/({self.A}×{self.hc:.4f})")
        print(f"     = {self.hc:.4f} + {self.Ic/(self.A*self.hc):.4f}")
        print(f"     = {yD:.4f} m （距水面深度）")
        print(f"  zD = yD - d = {yD:.4f} - {self.d} = {zD:.4f} m （距顶边）")
        print(f"  在形心下方 {zD - self.yc_from_top:.4f} m")
        
        print("\n" + "=" * 70)
        print("考试要点：")
        print("=" * 70)
        print("1. 梯形面积 A = (b1+b2)×h/2")
        print("2. 梯形形心距顶边 yc = h(2b2+b1)/(3(b1+b2))")
        print("3. 梯形惯性矩 Ic需要先计算I0，再用平行轴定理")
        print("4. 压力中心必在形心下方")
        print("=" * 70)


def main():
    """主函数"""
    print("\n" + "🔺" * 35)
    print("第01章 静水力学 - 题目8：梯形闸门总压力")
    print("🔺" * 35 + "\n")
    
    # 题目参数
    b1 = 2.0  # 上底2m
    b2 = 4.0  # 下底4m
    h = 3.0   # 高度3m
    d = 1.0   # 顶边距水面1m
    
    # 创建梯形闸门对象
    gate = TrapezoidalGate(b1=b1, b2=b2, h=h, d=d)
    
    # 打印结果
    gate.print_results()
    
    # 绘图
    print("\n正在绘制梯形闸门示意图...")
    gate.plot_gate_diagram()
    
    print("\n✅ 计算完成！")


if __name__ == "__main__":
    main()
