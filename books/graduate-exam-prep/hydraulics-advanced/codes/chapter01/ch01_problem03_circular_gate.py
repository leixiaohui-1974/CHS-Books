#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第01章 静水力学 - 题目3：圆形闸门总压力

题目：直径D=2m的圆形闸门，圆心距水面深度hc=3m，
求总压力和压力中心位置。

知识点：圆形平面总压力、惯性矩Ic=πD⁴/64

作者：CHS-Books Team  
日期：2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class CircularGate:
    def __init__(self, D: float, hc: float, rho=1000.0, g=9.81):
        self.D = D
        self.hc = hc
        self.rho = rho
        self.g = g
        self.A = np.pi * D**2 / 4
        self.Ic = np.pi * D**4 / 64
    
    def total_pressure(self):
        return self.rho * self.g * self.hc * self.A
    
    def pressure_center(self):
        yD = self.hc + self.Ic / (self.A * self.hc)
        return yD
    
    def plot(self):
        fig, ax = plt.subplots(figsize=(8, 6))
        circle = plt.Circle((0, self.hc), self.D/2, color='gray', alpha=0.5, label='圆形闸门')
        ax.add_patch(circle)
        ax.plot(0, self.hc, 'go', markersize=12, label=f'形心 hc={self.hc}m')
        
        yD = self.pressure_center()
        ax.plot(0, yD, 'r*', markersize=15, label=f'压力中心 yD={yD:.3f}m')
        
        ax.axhline(y=0, color='blue', linestyle='--', linewidth=2, label='水面')
        ax.set_xlim(-2, 2)
        ax.set_ylim(-0.5, self.hc + self.D/2 + 1)
        ax.set_xlabel('横向 (m)', fontsize=12, fontweight='bold')
        ax.set_ylabel('深度 (m)', fontsize=12, fontweight='bold')
        ax.set_title('圆形闸门受力示意图', fontsize=14, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.invert_yaxis()
        plt.tight_layout()
        plt.show()
    
    def print_results(self):
        print("=" * 60)
        print("圆形闸门静水总压力计算")
        print("=" * 60)
        print(f"\n输入：D={self.D}m, hc={self.hc}m")
        print(f"面积 A = πD²/4 = {self.A:.4f} m²")
        print(f"惯性矩 Ic = πD⁴/64 = {self.Ic:.6f} m⁴")
        
        P = self.total_pressure()
        print(f"\n总压力 P = ρg·hc·A = {P:.2f} N = {P/1000:.2f} kN")
        
        yD = self.pressure_center()
        print(f"压力中心 yD = hc + Ic/(A·hc) = {yD:.4f} m")
        print(f"偏移量 = {yD - self.hc:.4f} m （在形心下方）")
        print("=" * 60)


def main():
    print("\n🌊 第01章 题目3：圆形闸门总压力 🌊\n")
    gate = CircularGate(D=2.0, hc=3.0)
    gate.print_results()
    gate.plot()
    print("\n✅ 完成！")


if __name__ == "__main__":
    main()
