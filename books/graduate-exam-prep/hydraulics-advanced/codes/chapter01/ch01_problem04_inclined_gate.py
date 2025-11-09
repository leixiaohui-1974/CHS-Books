#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第01章 静水力学 - 题目4：倾斜闸门总压力

题目：矩形闸门b=2m, h=3m，倾角α=45°，
顶边距水面d=1m，求总压力。

知识点：倾斜闸门的形心深度计算

作者：CHS-Books Team
日期：2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class InclinedGate:
    def __init__(self, b, h, alpha_deg, d, rho=1000.0, g=9.81):
        self.b = b
        self.h = h
        self.alpha = np.deg2rad(alpha_deg)
        self.d = d
        self.rho = rho
        self.g = g
        self.A = b * h
        self.Ic = b * h**3 / 12
        # 形心深度（竖直深度）
        self.hc = d + h/2 * np.sin(self.alpha)
    
    def total_pressure(self):
        return self.rho * self.g * self.hc * self.A
    
    def pressure_center(self):
        # 沿闸门方向的形心位置
        yc_along = self.d / np.sin(self.alpha) + self.h / 2
        # 压力中心沿闸门方向
        yD_along = yc_along + self.Ic / (self.A * yc_along)
        # 压力中心竖直深度
        yD_vertical = self.d + yD_along * np.sin(self.alpha) - self.d/np.sin(self.alpha) * np.sin(self.alpha)
        return yD_vertical, yD_along
    
    def plot(self):
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # 闸门起点和终点坐标
        x_start = 0
        y_start = self.d
        x_end = self.h * np.cos(self.alpha)
        y_end = self.d + self.h * np.sin(self.alpha)
        
        # 绘制闸门
        ax.plot([x_start, x_end], [y_start, y_end], 'r-', linewidth=5, label=f'闸门 (α={np.rad2deg(self.alpha):.0f}°)')
        
        # 绘制水面
        ax.axhline(y=0, color='blue', linestyle='--', linewidth=2, label='水面')
        
        # 形心
        xc = self.h/2 * np.cos(self.alpha)
        yc = self.hc
        ax.plot(xc, yc, 'go', markersize=12, label=f'形心 hc={self.hc:.3f}m')
        
        # 压力中心
        yD_vert, yD_along = self.pressure_center()
        xD = yD_along * np.cos(self.alpha)
        ax.plot(xD, yD_vert, 'r*', markersize=15, label=f'压力中心 yD={yD_vert:.3f}m')
        
        ax.set_xlabel('水平距离 (m)', fontsize=12, fontweight='bold')
        ax.set_ylabel('深度 (m)', fontsize=12, fontweight='bold')
        ax.set_title('倾斜闸门受力示意图', fontsize=14, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.invert_yaxis()
        ax.set_aspect('equal')
        plt.tight_layout()
        plt.show()
    
    def print_results(self):
        print("=" * 70)
        print("倾斜闸门静水总压力计算")
        print("=" * 70)
        print(f"\n输入：b={self.b}m, h={self.h}m, α={np.rad2deg(self.alpha):.0f}°, d={self.d}m")
        print(f"面积 A = {self.A} m²")
        print(f"形心深度 hc = d + h/2·sinα = {self.d} + {self.h/2}×sin({np.rad2deg(self.alpha):.0f}°)")
        print(f"          = {self.hc:.4f} m")
        
        P = self.total_pressure()
        print(f"\n总压力 P = ρg·hc·A = {P:.2f} N = {P/1000:.2f} kN")
        
        yD_vert, yD_along = self.pressure_center()
        print(f"\n压力中心竖直深度 yD = {yD_vert:.4f} m")
        print(f"沿闸门方向距离 = {yD_along:.4f} m")
        print("=" * 70)


def main():
    print("\n🌊 第01章 题目4：倾斜闸门总压力 🌊\n")
    gate = InclinedGate(b=2.0, h=3.0, alpha_deg=45, d=1.0)
    gate.print_results()
    gate.plot()
    print("\n✅ 完成！")


if __name__ == "__main__":
    main()
