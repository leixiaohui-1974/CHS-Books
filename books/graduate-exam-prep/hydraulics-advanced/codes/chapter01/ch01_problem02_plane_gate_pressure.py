#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第01章 静水力学 - 题目2：平面闸门总压力计算

题目描述：
矩形平面闸门，宽度b=3m，高度h=4m，水深H=5m，
闸门顶部距水面1m。求：
(1) 作用在闸门上的静水总压力
(2) 压力中心位置
(3) 绘制受力示意图

知识点：
- 平面静水总压力公式
- 压力中心计算
- 惯性矩应用

作者：CHS-Books Team
日期：2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class PlaneGatePressure:
    """平面闸门静水总压力计算类"""
    
    def __init__(self, b: float, h: float, d: float, H: float, 
                 rho: float = 1000.0, g: float = 9.81):
        """
        初始化参数
        
        Parameters:
        -----------
        b : float
            闸门宽度 (m)
        h : float
            闸门高度 (m)
        d : float
            闸门顶部距水面深度 (m)
        H : float
            水深 (m)
        rho : float
            水密度 (kg/m³)
        g : float
            重力加速度 (m/s²)
        """
        self.b = b
        self.h = h
        self.d = d
        self.H = H
        self.rho = rho
        self.g = g
        
        # 计算形心深度
        self.hc = d + h / 2
        
        # 计算面积
        self.A = b * h
        
        # 计算惯性矩（矩形，对通过形心的水平轴）
        self.Ic = b * h**3 / 12
        
    def total_pressure(self) -> float:
        """
        计算静水总压力
        
        公式：P = ρg·hc·A
        
        Returns:
        --------
        float : 总压力 (N)
        """
        P = self.rho * self.g * self.hc * self.A
        return P
    
    def pressure_center(self) -> tuple:
        """
        计算压力中心位置
        
        公式：yD = yc + Ic/(A·yc)
        
        Returns:
        --------
        tuple : (yD, zD) 压力中心坐标 (m)
                yD: 距水面深度
                zD: 距闸门顶部距离
        """
        # 压力中心距水面深度
        yD = self.hc + self.Ic / (self.A * self.hc)
        
        # 压力中心距闸门顶部距离
        zD = yD - self.d
        
        return yD, zD
    
    def pressure_distribution(self) -> np.ndarray:
        """计算沿闸门的压强分布"""
        z = np.linspace(0, self.h, 100)  # 沿闸门高度
        depth = self.d + z  # 对应水深
        p = self.rho * self.g * depth  # 压强
        return z, p
    
    def plot_gate_diagram(self, save_path: str = None):
        """绘制闸门受力示意图"""
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        # 左图：闸门位置示意图
        ax1 = axes[0]
        
        # 绘制水池
        water_width = 6
        ax1.fill_between([0, water_width], [0, 0], [self.H, self.H], 
                         color='lightblue', alpha=0.5, label='水体')
        ax1.plot([0, water_width], [0, 0], 'b-', linewidth=2, label='水面')
        ax1.plot([0, water_width], [self.H, self.H], 'brown', linewidth=2, label='池底')
        
        # 绘制闸门（位于x=2处）
        gate_x = 2
        gate_rect = patches.Rectangle((gate_x - 0.1, self.d), 0.2, self.h,
                                     linewidth=3, edgecolor='red', facecolor='gray',
                                     alpha=0.7, label='闸门')
        ax1.add_patch(gate_rect)
        
        # 标注尺寸
        ax1.annotate('', xy=(gate_x + 0.5, 0), xytext=(gate_x + 0.5, self.d),
                    arrowprops=dict(arrowstyle='<->', color='black', lw=1.5))
        ax1.text(gate_x + 0.8, self.d/2, f'd={self.d}m', fontsize=11, fontweight='bold')
        
        ax1.annotate('', xy=(gate_x + 0.5, self.d), xytext=(gate_x + 0.5, self.d + self.h),
                    arrowprops=dict(arrowstyle='<->', color='red', lw=1.5))
        ax1.text(gate_x + 0.8, self.d + self.h/2, f'h={self.h}m', fontsize=11, 
                fontweight='bold', color='red')
        
        ax1.annotate('', xy=(0.5, 0), xytext=(0.5, self.H),
                    arrowprops=dict(arrowstyle='<->', color='blue', lw=1.5))
        ax1.text(0.1, self.H/2, f'H={self.H}m', fontsize=11, fontweight='bold', color='blue')
        
        # 标注形心
        yc_line = self.hc
        ax1.plot([gate_x - 0.5, gate_x + 0.5], [yc_line, yc_line], 'g--', linewidth=2)
        ax1.plot(gate_x, yc_line, 'go', markersize=10, label='形心C')
        ax1.text(gate_x - 0.7, yc_line, f'形心\nhc={self.hc}m', fontsize=10, 
                bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))
        
        # 标注压力中心
        yD, zD = self.pressure_center()
        ax1.plot([gate_x - 0.5, gate_x + 0.5], [yD, yD], 'r--', linewidth=2)
        ax1.plot(gate_x, yD, 'r*', markersize=15, label='压力中心D')
        ax1.text(gate_x + 0.3, yD + 0.2, f'压力中心\nyD={yD:.3f}m', fontsize=10,
                bbox=dict(boxstyle='round', facecolor='pink', alpha=0.7))
        
        ax1.set_xlabel('横向位置 (m)', fontsize=12, fontweight='bold')
        ax1.set_ylabel('深度 z (m)', fontsize=12, fontweight='bold')
        ax1.set_title('闸门位置示意图', fontsize=14, fontweight='bold')
        ax1.legend(loc='lower right', fontsize=10)
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim(-0.5, water_width + 0.5)
        ax1.set_ylim(-0.5, self.H + 0.5)
        ax1.invert_yaxis()
        
        # 右图：压强分布图
        ax2 = axes[1]
        
        z, p = self.pressure_distribution()
        p_kpa = p / 1000
        
        # 绘制压强分布
        ax2.fill_betweenx(z, 0, p_kpa, alpha=0.3, color='blue')
        ax2.plot(p_kpa, z, 'b-', linewidth=2.5, label='压强分布')
        
        # 标注形心处压强
        pc = self.rho * self.g * self.hc / 1000
        zc = self.h / 2
        ax2.plot(pc, zc, 'go', markersize=10, label='形心C')
        ax2.text(pc + 2, zc, f'pc={pc:.2f}kPa', fontsize=10,
                bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))
        
        # 标注压力中心
        yD, zD = self.pressure_center()
        pD = self.rho * self.g * yD / 1000
        ax2.plot(pD, zD, 'r*', markersize=15, label='压力中心D')
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
        ax2.set_ylim(self.h, 0)  # 反转y轴
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def print_results(self):
        """打印计算结果"""
        print("=" * 70)
        print("平面闸门静水总压力计算")
        print("=" * 70)
        
        print(f"\n输入参数：")
        print(f"  闸门宽度 b = {self.b} m")
        print(f"  闸门高度 h = {self.h} m")
        print(f"  顶部距水面 d = {self.d} m")
        print(f"  水深 H = {self.H} m")
        print(f"  水密度 ρ = {self.rho} kg/m³")
        print(f"  重力加速度 g = {self.g} m/s²")
        
        print(f"\n几何参数：")
        print(f"  闸门面积 A = b × h = {self.b} × {self.h} = {self.A} m²")
        print(f"  形心深度 hc = d + h/2 = {self.d} + {self.h/2} = {self.hc} m")
        print(f"  惯性矩 Ic = bh³/12 = {self.b}×{self.h}³/12 = {self.Ic:.4f} m⁴")
        
        print(f"\n压力计算：")
        P = self.total_pressure()
        pc = self.rho * self.g * self.hc
        print(f"  形心处压强 pc = ρg·hc = {self.rho}×{self.g}×{self.hc}")
        print(f"                    = {pc:.2f} Pa = {pc/1000:.2f} kPa")
        print(f"  总压力 P = pc × A = {pc:.2f} × {self.A}")
        print(f"           = {P:.2f} N = {P/1000:.2f} kN")
        
        print(f"\n压力中心：")
        yD, zD = self.pressure_center()
        print(f"  公式：yD = yc + Ic/(A·yc)")
        print(f"  yD = {self.hc} + {self.Ic}/({self.A}×{self.hc})")
        print(f"     = {self.hc} + {self.Ic/(self.A*self.hc):.4f}")
        print(f"     = {yD:.4f} m （距水面深度）")
        print(f"  zD = yD - d = {yD:.4f} - {self.d} = {zD:.4f} m （距闸门顶部）")
        print(f"  位置：在形心下方 {zD - self.h/2:.4f} m")
        
        print("\n" + "=" * 70)
        print("考试要点：")
        print("=" * 70)
        print("1. 总压力 P = ρg·hc·A，形心深度hc是关键")
        print("2. 压力中心在形心下方，偏移量 = Ic/(A·yc)")
        print("3. 矩形闸门：Ic = bh³/12")
        print("4. 压力中心不是压强最大点，而是合力作用点")
        print("=" * 70)


def main():
    """主函数"""
    print("\n" + "🌊" * 35)
    print("第01章 静水力学 - 题目2：平面闸门总压力")
    print("🌊" * 35 + "\n")
    
    # 题目参数
    b = 3.0  # 宽度3m
    h = 4.0  # 高度4m
    d = 1.0  # 顶部距水面1m
    H = 5.0  # 水深5m
    
    # 创建计算对象
    gate = PlaneGatePressure(b=b, h=h, d=d, H=H)
    
    # 打印结果
    gate.print_results()
    
    # 绘图
    print("\n正在绘制闸门受力示意图...")
    gate.plot_gate_diagram()
    
    print("\n✅ 计算完成！")


if __name__ == "__main__":
    main()
