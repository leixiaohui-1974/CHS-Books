#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第01章 静水力学 - 题目1：静水压强分布

题目描述：
某水池水深h=5m，水面以上有气压p0=1.2atm作用。
(1) 绘制压强分布图（从水面到池底）
(2) 计算池底压强（绝对压强、相对压强）
(3) 计算水深3m处的压强
(4) 分析气压p0对压强分布的影响

知识点：
- 静水压强基本公式：p = p0 + ρgh
- 绝对压强与相对压强
- 压强分布可视化

作者：CHS-Books Team
日期：2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class PressureDistribution:
    """静水压强分布计算与可视化类"""
    
    def __init__(self, h: float, p0: float = 101325.0, rho: float = 1000.0, g: float = 9.81):
        """
        初始化参数
        
        Parameters:
        -----------
        h : float
            水深 (m)
        p0 : float
            水面气压 (Pa)，默认1个标准大气压
        rho : float
            水的密度 (kg/m³)，默认1000
        g : float
            重力加速度 (m/s²)，默认9.81
        """
        self.h = h
        self.p0 = p0
        self.rho = rho
        self.g = g
        
    def absolute_pressure(self, z: float) -> float:
        """
        计算深度z处的绝对压强
        
        Parameters:
        -----------
        z : float
            从水面向下的深度 (m)
            
        Returns:
        --------
        float : 绝对压强 (Pa)
        
        公式：p_abs = p0 + ρgh
        """
        return self.p0 + self.rho * self.g * z
    
    def gauge_pressure(self, z: float) -> float:
        """
        计算深度z处的相对压强（表压）
        
        Parameters:
        -----------
        z : float
            从水面向下的深度 (m)
            
        Returns:
        --------
        float : 相对压强 (Pa)
        
        公式：p_gauge = ρgh
        """
        return self.rho * self.g * z
    
    def pressure_head(self, z: float) -> float:
        """
        计算深度z处的测压管水头
        
        Parameters:
        -----------
        z : float
            从水面向下的深度 (m)
            
        Returns:
        --------
        float : 测压管水头 (m)
        
        公式：h_p = p/ρg = h + p0/(ρg)
        """
        return z + self.p0 / (self.rho * self.g)
    
    def calculate_all(self) -> dict:
        """计算关键位置的压强"""
        results = {
            '水面(z=0)': {
                '深度(m)': 0,
                '绝对压强(Pa)': self.absolute_pressure(0),
                '相对压强(Pa)': self.gauge_pressure(0),
                '压强水头(m)': self.pressure_head(0)
            },
            '中层(z=h/2)': {
                '深度(m)': self.h / 2,
                '绝对压强(Pa)': self.absolute_pressure(self.h / 2),
                '相对压强(Pa)': self.gauge_pressure(self.h / 2),
                '压强水头(m)': self.pressure_head(self.h / 2)
            },
            '池底(z=h)': {
                '深度(m)': self.h,
                '绝对压强(Pa)': self.absolute_pressure(self.h),
                '相对压强(Pa)': self.gauge_pressure(self.h),
                '压强水头(m)': self.pressure_head(self.h)
            }
        }
        return results
    
    def plot_pressure_distribution(self, save_path: str = None):
        """
        绘制压强分布图
        
        Parameters:
        -----------
        save_path : str, optional
            图片保存路径
        """
        # 创建深度数组
        z = np.linspace(0, self.h, 100)
        
        # 计算压强
        p_abs = self.absolute_pressure(z)
        p_gauge = self.gauge_pressure(z)
        
        # 转换为kPa
        p_abs_kpa = p_abs / 1000
        p_gauge_kpa = p_gauge / 1000
        
        # 创建图形
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        # 绘制绝对压强分布
        ax1 = axes[0]
        ax1.plot(p_abs_kpa, z, 'b-', linewidth=2.5, label='绝对压强')
        ax1.axhline(y=0, color='cyan', linestyle='--', linewidth=1.5, label='水面')
        ax1.axhline(y=self.h, color='brown', linestyle='--', linewidth=1.5, label='池底')
        ax1.fill_betweenx(z, 0, p_abs_kpa, alpha=0.3, color='blue')
        ax1.set_xlabel('绝对压强 (kPa)', fontsize=12, fontweight='bold')
        ax1.set_ylabel('水深 z (m)', fontsize=12, fontweight='bold')
        ax1.set_title('静水压强分布 - 绝对压强', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.legend(fontsize=10)
        ax1.invert_yaxis()  # 反转y轴，使水面在上
        
        # 标注关键点
        for z_val in [0, self.h/2, self.h]:
            p_val = self.absolute_pressure(z_val) / 1000
            ax1.plot(p_val, z_val, 'ro', markersize=8)
            ax1.text(p_val + 5, z_val, f'z={z_val:.1f}m\np={p_val:.1f}kPa', 
                    fontsize=9, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        # 绘制相对压强（表压）分布
        ax2 = axes[1]
        ax2.plot(p_gauge_kpa, z, 'r-', linewidth=2.5, label='相对压强（表压）')
        ax2.axhline(y=0, color='cyan', linestyle='--', linewidth=1.5, label='水面')
        ax2.axhline(y=self.h, color='brown', linestyle='--', linewidth=1.5, label='池底')
        ax2.fill_betweenx(z, 0, p_gauge_kpa, alpha=0.3, color='red')
        ax2.set_xlabel('相对压强 (kPa)', fontsize=12, fontweight='bold')
        ax2.set_ylabel('水深 z (m)', fontsize=12, fontweight='bold')
        ax2.set_title('静水压强分布 - 相对压强', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.legend(fontsize=10)
        ax2.invert_yaxis()
        
        # 标注关键点
        for z_val in [0, self.h/2, self.h]:
            p_val = self.gauge_pressure(z_val) / 1000
            ax2.plot(p_val, z_val, 'ro', markersize=8)
            if z_val > 0:  # 水面处表压为0，不标注
                ax2.text(p_val + 2, z_val, f'z={z_val:.1f}m\np={p_val:.1f}kPa', 
                        fontsize=9, bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"图片已保存至: {save_path}")
        
        plt.show()
    
    def sensitivity_analysis(self):
        """分析气压p0对压强分布的影响"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # 不同气压值
        p0_values = [0.8 * 101325, 1.0 * 101325, 1.2 * 101325, 1.5 * 101325]
        p0_labels = ['0.8 atm', '1.0 atm', '1.2 atm', '1.5 atm']
        colors = ['blue', 'green', 'red', 'purple']
        
        z = np.linspace(0, self.h, 100)
        
        for p0, label, color in zip(p0_values, p0_labels, colors):
            p_abs = p0 + self.rho * self.g * z
            p_abs_kpa = p_abs / 1000
            ax.plot(p_abs_kpa, z, linewidth=2, label=label, color=color)
        
        ax.axhline(y=0, color='cyan', linestyle='--', linewidth=1.5, label='水面')
        ax.axhline(y=self.h, color='brown', linestyle='--', linewidth=1.5, label='池底')
        ax.set_xlabel('绝对压强 (kPa)', fontsize=12, fontweight='bold')
        ax.set_ylabel('水深 z (m)', fontsize=12, fontweight='bold')
        ax.set_title('气压p0对静水压强分布的影响', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=11)
        ax.invert_yaxis()
        
        plt.tight_layout()
        plt.show()
    
    def print_results(self):
        """打印计算结果"""
        print("=" * 70)
        print("静水压强分布计算")
        print("=" * 70)
        print(f"\n输入参数：")
        print(f"  水深 h = {self.h} m")
        print(f"  水面气压 p0 = {self.p0/101325:.2f} atm = {self.p0:.0f} Pa")
        print(f"  水的密度 ρ = {self.rho} kg/m³")
        print(f"  重力加速度 g = {self.g} m/s²")
        
        print(f"\n基本公式：")
        print(f"  绝对压强：p_abs = p0 + ρgh")
        print(f"  相对压强：p_gauge = ρgh")
        print(f"  压强水头：h_p = p/(ρg)")
        
        results = self.calculate_all()
        
        print(f"\n计算结果：")
        print("-" * 70)
        for position, values in results.items():
            print(f"\n{position}:")
            for key, value in values.items():
                if 'Pa' in key:
                    print(f"  {key}: {value:.2f} = {value/1000:.2f} kPa = {value/101325:.4f} atm")
                else:
                    print(f"  {key}: {value:.2f}")
        
        print("\n" + "=" * 70)
        print("考试要点：")
        print("=" * 70)
        print("1. 绝对压强 = 大气压 + 相对压强")
        print("2. 相对压强（表压）= ρgh，只与水深有关")
        print("3. 压强分布呈线性关系，深度每增加1m，压强增加约9.81 kPa")
        print("4. 水面气压p0会整体抬升压强曲线，但不改变压强梯度")
        print("=" * 70)


def main():
    """主函数：演示压强分布计算"""
    
    print("\n" + "🌊" * 35)
    print("第01章 静水力学 - 题目1：静水压强分布")
    print("🌊" * 35 + "\n")
    
    # 题目条件
    h = 5.0  # 水深5m
    p0 = 1.2 * 101325  # 水面气压1.2atm
    
    # 创建压强分布对象
    pressure = PressureDistribution(h=h, p0=p0)
    
    # 打印计算结果
    pressure.print_results()
    
    # 绘制压强分布图
    print("\n正在绘制压强分布图...")
    pressure.plot_pressure_distribution()
    
    # 敏感性分析
    print("\n正在分析气压p0的影响...")
    pressure.sensitivity_analysis()
    
    # 额外分析：不同水深的对比
    print("\n\n" + "=" * 70)
    print("附加分析：不同水深对比")
    print("=" * 70)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    depths = [3, 5, 8, 10]  # 不同水深
    colors = ['blue', 'green', 'red', 'purple']
    
    for depth, color in zip(depths, colors):
        p_temp = PressureDistribution(h=depth, p0=101325)
        z = np.linspace(0, depth, 100)
        p_gauge = p_temp.gauge_pressure(z) / 1000
        ax.plot(p_gauge, z, linewidth=2, label=f'h={depth}m', color=color)
    
    ax.set_xlabel('相对压强 (kPa)', fontsize=12, fontweight='bold')
    ax.set_ylabel('水深 z (m)', fontsize=12, fontweight='bold')
    ax.set_title('不同水深的压强分布对比', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=11)
    ax.invert_yaxis()
    
    plt.tight_layout()
    plt.show()
    
    print("\n✅ 计算完成！")


if __name__ == "__main__":
    main()
