#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第01章 静水力学 - 题目5：浮力计算

题目：圆柱体直径D=1m，高度H=2m，密度ρ_body=800kg/m³，
漂浮在水面上，求吃水深度h。

知识点：浮力公式、浮体平衡

作者：CHS-Books Team
日期：2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class BuoyancyCalculation:
    def __init__(self, D, H, rho_body, rho_water=1000.0, g=9.81):
        self.D = D
        self.H = H
        self.rho_body = rho_body
        self.rho_water = rho_water
        self.g = g
        self.V_total = np.pi * D**2 / 4 * H
    
    def draft_depth(self):
        """计算吃水深度"""
        # 浮力 = 重力
        # ρ_water * g * V_submerged = ρ_body * g * V_total
        # ρ_water * (πD²/4 * h) = ρ_body * (πD²/4 * H)
        h = self.rho_body / self.rho_water * self.H
        return h
    
    def forces(self):
        """计算重力和浮力"""
        W = self.rho_body * self.g * self.V_total
        h = self.draft_depth()
        V_sub = np.pi * self.D**2 / 4 * h
        Fb = self.rho_water * self.g * V_sub
        return W, Fb
    
    def plot(self):
        fig, ax = plt.subplots(figsize=(8, 8))
        
        # 绘制水面
        water_width = 3
        ax.fill_between([-water_width/2, water_width/2], [0, 0], [-5, -5],
                       color='lightblue', alpha=0.5, label='水体')
        ax.axhline(y=0, color='blue', linestyle='--', linewidth=2, label='水面')
        
        # 计算吃水深度
        h = self.draft_depth()
        
        # 绘制圆柱体
        x_center = 0
        y_bottom = -h
        y_top = y_bottom + self.H
        
        # 水下部分
        rect_sub = patches.Rectangle((x_center - self.D/2, y_bottom), self.D, h,
                                     linewidth=2, edgecolor='black', facecolor='lightcoral',
                                     alpha=0.7, label='水下部分')
        ax.add_patch(rect_sub)
        
        # 水上部分
        if self.H > h:
            rect_above = patches.Rectangle((x_center - self.D/2, 0), self.D, self.H - h,
                                          linewidth=2, edgecolor='black', facecolor='coral',
                                          alpha=0.7, label='水上部分')
            ax.add_patch(rect_above)
        
        # 标注尺寸
        ax.annotate('', xy=(self.D/2 + 0.3, y_bottom), xytext=(self.D/2 + 0.3, 0),
                   arrowprops=dict(arrowstyle='<->', color='red', lw=2))
        ax.text(self.D/2 + 0.5, -h/2, f'h={h:.3f}m', fontsize=12, fontweight='bold', color='red')
        
        ax.annotate('', xy=(self.D/2 + 0.3, y_bottom), xytext=(self.D/2 + 0.3, y_top),
                   arrowprops=dict(arrowstyle='<->', color='black', lw=2))
        ax.text(self.D/2 + 0.6, (y_bottom + y_top)/2, f'H={self.H}m', fontsize=12, fontweight='bold')
        
        # 标注力
        W, Fb = self.forces()
        # 重力（向下）
        ax.arrow(0, y_top + 0.2, 0, -0.5, head_width=0.15, head_length=0.1, 
                fc='green', ec='green', linewidth=3)
        ax.text(0.3, y_top + 0.3, f'W={W/1000:.2f}kN', fontsize=11, fontweight='bold', color='green')
        
        # 浮力（向上）
        ax.arrow(0, y_bottom - 0.2, 0, 0.5, head_width=0.15, head_length=0.1,
                fc='purple', ec='purple', linewidth=3)
        ax.text(0.3, y_bottom - 0.3, f'Fb={Fb/1000:.2f}kN', fontsize=11, fontweight='bold', color='purple')
        
        ax.set_xlabel('横向位置 (m)', fontsize=12, fontweight='bold')
        ax.set_ylabel('高程 (m)', fontsize=12, fontweight='bold')
        ax.set_title('圆柱体浮力平衡示意图', fontsize=14, fontweight='bold')
        ax.legend(fontsize=10, loc='lower right')
        ax.grid(True, alpha=0.3)
        ax.set_xlim(-water_width/2 - 0.5, water_width/2 + 1.5)
        ax.set_ylim(-5, self.H + 1)
        ax.set_aspect('equal')
        plt.tight_layout()
        plt.show()
    
    def print_results(self):
        print("=" * 70)
        print("浮力计算")
        print("=" * 70)
        print(f"\n输入：D={self.D}m, H={self.H}m, ρ_body={self.rho_body}kg/m³")
        print(f"总体积 V = πD²H/4 = {self.V_total:.4f} m³")
        
        W, Fb = self.forces()
        print(f"\n重力 W = ρ_body × g × V = {W:.2f} N = {W/1000:.2f} kN")
        
        h = self.draft_depth()
        print(f"\n浮力平衡：Fb = W")
        print(f"ρ_water × g × V_sub = ρ_body × g × V_total")
        print(f"ρ_water × (πD²/4 × h) = ρ_body × (πD²/4 × H)")
        print(f"h = (ρ_body/ρ_water) × H = ({self.rho_body}/{self.rho_water}) × {self.H}")
        print(f"  = {h:.4f} m")
        
        print(f"\n验证浮力 Fb = ρ_water × g × V_sub = {Fb:.2f} N = {Fb/1000:.2f} kN")
        print(f"误差 = |Fb - W| = {abs(Fb - W):.6f} N ≈ 0 ✓")
        
        print(f"\n吃水深度比 h/H = {h/self.H:.2%}")
        print("=" * 70)


def main():
    print("\n🌊 第01章 题目5：浮力计算 🌊\n")
    buoy = BuoyancyCalculation(D=1.0, H=2.0, rho_body=800)
    buoy.print_results()
    buoy.plot()
    print("\n✅ 完成！")


if __name__ == "__main__":
    main()
