#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第01章 静水力学 - 题目7：液压千斤顶（帕斯卡原理）

题目描述：
液压千斤顶，小活塞直径d1=20mm，大活塞直径d2=100mm，
在小活塞上施加力F1=500N，求大活塞能举起的重物重量。

知识点：
- 帕斯卡原理（静压传递）
- 压强相等原理
- 力的放大作用

作者：CHS-Books Team
日期：2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class HydraulicJack:
    """液压千斤顶计算类"""
    
    def __init__(self, d1: float, d2: float, F1: float):
        """
        初始化参数
        
        Parameters:
        -----------
        d1 : float
            小活塞直径 (m)
        d2 : float
            大活塞直径 (m)
        F1 : float
            小活塞施加力 (N)
        """
        self.d1 = d1
        self.d2 = d2
        self.F1 = F1
        
        # 计算面积
        self.A1 = np.pi * d1**2 / 4
        self.A2 = np.pi * d2**2 / 4
        
        # 面积比
        self.area_ratio = self.A2 / self.A1
        
    def pressure_on_small_piston(self) -> float:
        """
        计算小活塞产生的压强
        
        Returns:
        --------
        float : 压强 (Pa)
        
        公式：p1 = F1/A1
        """
        return self.F1 / self.A1
    
    def force_on_large_piston(self) -> float:
        """
        计算大活塞能举起的力
        
        Returns:
        --------
        float : 力 (N)
        
        帕斯卡原理：p1 = p2
        F2/A2 = F1/A1
        F2 = F1 × (A2/A1)
        """
        return self.F1 * self.area_ratio
    
    def mechanical_advantage(self) -> float:
        """
        计算机械增益（力的放大倍数）
        
        Returns:
        --------
        float : 增益倍数
        """
        return self.area_ratio
    
    def efficiency_analysis(self, eta: float = 0.85) -> float:
        """
        考虑效率的实际举重能力
        
        Parameters:
        -----------
        eta : float
            机械效率（默认85%）
            
        Returns:
        --------
        float : 实际举重能力 (N)
        """
        F2_ideal = self.force_on_large_piston()
        F2_actual = F2_ideal * eta
        return F2_actual
    
    def plot_hydraulic_jack(self):
        """绘制液压千斤顶示意图"""
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        # 左图：结构示意图
        ax1 = axes[0]
        
        # 小活塞
        x1 = 2
        y1_bottom = 2
        h1 = 3
        small_piston = patches.Rectangle((x1 - self.d1/2, y1_bottom), 
                                         self.d1, h1,
                                         linewidth=2, edgecolor='blue', 
                                         facecolor='lightblue', alpha=0.7)
        ax1.add_patch(small_piston)
        
        # 大活塞
        x2 = 6
        y2_bottom = 1
        h2 = 2
        large_piston = patches.Rectangle((x2 - self.d2/2, y2_bottom), 
                                          self.d2, h2,
                                          linewidth=2, edgecolor='red', 
                                          facecolor='lightcoral', alpha=0.7)
        ax1.add_patch(large_piston)
        
        # 连接管道（液体）
        pipe_y = y1_bottom
        ax1.fill_between([x1 - self.d1/2, x1 + self.d1/2], 
                         [0, 0], [pipe_y, pipe_y],
                         color='cyan', alpha=0.5)
        ax1.fill_between([x2 - self.d2/2, x2 + self.d2/2], 
                         [0, 0], [pipe_y, pipe_y],
                         color='cyan', alpha=0.5)
        ax1.fill_between([x1 + self.d1/2, x2 - self.d2/2], 
                         [0, 0], [pipe_y, pipe_y],
                         color='cyan', alpha=0.5, label='液体')
        
        # 施加力F1（向下箭头）
        ax1.arrow(x1, y1_bottom + h1 + 0.5, 0, -0.3, 
                 head_width=0.2, head_length=0.1, 
                 fc='green', ec='green', linewidth=3)
        ax1.text(x1 + 0.3, y1_bottom + h1 + 0.5, 
                f'F₁={self.F1}N', fontsize=12, fontweight='bold', color='green')
        
        # 举起力F2（向上箭头）
        F2 = self.force_on_large_piston()
        ax1.arrow(x2, y2_bottom + h2 - 0.5, 0, 0.3, 
                 head_width=0.2, head_length=0.1, 
                 fc='red', ec='red', linewidth=3)
        ax1.text(x2 + 0.3, y2_bottom + h2 - 0.3, 
                f'F₂={F2/1000:.2f}kN', fontsize=12, fontweight='bold', color='red')
        
        # 标注直径
        ax1.plot([x1 - self.d1/2, x1 + self.d1/2], 
                [y1_bottom - 0.3, y1_bottom - 0.3], 'b-', linewidth=2)
        ax1.text(x1, y1_bottom - 0.5, f'd₁={self.d1*1000:.0f}mm', 
                fontsize=10, ha='center', color='blue', fontweight='bold')
        
        ax1.plot([x2 - self.d2/2, x2 + self.d2/2], 
                [y2_bottom - 0.3, y2_bottom - 0.3], 'r-', linewidth=2)
        ax1.text(x2, y2_bottom - 0.5, f'd₂={self.d2*1000:.0f}mm', 
                fontsize=10, ha='center', color='red', fontweight='bold')
        
        # 标注压强相等
        p1 = self.pressure_on_small_piston()
        ax1.text(4, 0.5, f'p₁ = p₂ = {p1/1000:.2f} kPa\n（帕斯卡原理）', 
                fontsize=11, ha='center', 
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
        
        ax1.set_xlim(0, 8)
        ax1.set_ylim(-1, 6)
        ax1.set_xlabel('位置 (m)', fontsize=12, fontweight='bold')
        ax1.set_ylabel('高度 (m)', fontsize=12, fontweight='bold')
        ax1.set_title('液压千斤顶结构示意图', fontsize=14, fontweight='bold')
        ax1.legend(fontsize=10)
        ax1.grid(True, alpha=0.3)
        ax1.set_aspect('equal')
        
        # 右图：力和面积的关系
        ax2 = axes[1]
        
        categories = ['小活塞', '大活塞']
        areas = [self.A1 * 1e6, self.A2 * 1e6]  # 转换为mm²
        forces = [self.F1 / 1000, F2 / 1000]  # 转换为kN
        
        x = np.arange(len(categories))
        width = 0.35
        
        bars1 = ax2.bar(x - width/2, areas, width, label='面积 (mm²)', 
                       color='lightblue', edgecolor='blue', linewidth=2)
        ax2_twin = ax2.twinx()
        bars2 = ax2_twin.bar(x + width/2, forces, width, label='力 (kN)', 
                            color='lightcoral', edgecolor='red', linewidth=2)
        
        # 标注数值
        for i, (bar, val) in enumerate(zip(bars1, areas)):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50, 
                    f'{val:.1f}mm²', ha='center', fontsize=10, fontweight='bold')
        
        for i, (bar, val) in enumerate(zip(bars2, forces)):
            ax2_twin.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                         f'{val:.2f}kN', ha='center', fontsize=10, fontweight='bold')
        
        ax2.set_xlabel('活塞', fontsize=12, fontweight='bold')
        ax2.set_ylabel('面积 (mm²)', fontsize=12, fontweight='bold', color='blue')
        ax2_twin.set_ylabel('力 (kN)', fontsize=12, fontweight='bold', color='red')
        ax2.set_title('面积与力的关系', fontsize=14, fontweight='bold')
        ax2.set_xticks(x)
        ax2.set_xticklabels(categories, fontsize=11)
        ax2.tick_params(axis='y', labelcolor='blue')
        ax2_twin.tick_params(axis='y', labelcolor='red')
        ax2.grid(True, alpha=0.3, axis='y')
        
        # 标注增益倍数
        ax2.text(0.5, max(areas) * 0.8, 
                f'力放大倍数 = {self.mechanical_advantage():.2f}×', 
                fontsize=12, fontweight='bold', ha='center',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        plt.tight_layout()
        plt.show()
    
    def print_results(self):
        """打印计算结果"""
        print("=" * 70)
        print("液压千斤顶计算（帕斯卡原理）")
        print("=" * 70)
        
        print(f"\n输入参数：")
        print(f"  小活塞直径 d1 = {self.d1*1000:.0f} mm = {self.d1} m")
        print(f"  大活塞直径 d2 = {self.d2*1000:.0f} mm = {self.d2} m")
        print(f"  小活塞施加力 F1 = {self.F1} N = {self.F1/1000:.2f} kN")
        
        print(f"\n面积计算：")
        print(f"  小活塞面积 A1 = πd1²/4 = π×{self.d1}²/4")
        print(f"               = {self.A1:.6f} m² = {self.A1*1e6:.2f} mm²")
        print(f"  大活塞面积 A2 = πd2²/4 = π×{self.d2}²/4")
        print(f"               = {self.A2:.6f} m² = {self.A2*1e6:.2f} mm²")
        print(f"  面积比 A2/A1 = {self.area_ratio:.2f}")
        
        p1 = self.pressure_on_small_piston()
        print(f"\n压强计算：")
        print(f"  小活塞压强 p1 = F1/A1 = {self.F1}/{self.A1:.6f}")
        print(f"                = {p1:.2f} Pa = {p1/1000:.2f} kPa")
        
        F2 = self.force_on_large_piston()
        print(f"\n帕斯卡原理应用：")
        print(f"  根据帕斯卡原理：p1 = p2")
        print(f"  即：F1/A1 = F2/A2")
        print(f"  解得：F2 = F1 × (A2/A1) = {self.F1} × {self.area_ratio:.2f}")
        print(f"       = {F2:.2f} N = {F2/1000:.2f} kN")
        
        print(f"\n机械增益：")
        ma = self.mechanical_advantage()
        print(f"  力放大倍数 = A2/A1 = {ma:.2f}×")
        print(f"  说明：在小活塞施加1N的力，大活塞可产生{ma:.2f}N的力")
        
        print(f"\n实际效率分析：")
        for eta in [0.80, 0.85, 0.90]:
            F2_actual = self.efficiency_analysis(eta)
            print(f"  效率η={eta:.0%}时，实际举重能力 = {F2_actual:.2f} N = {F2_actual/1000:.2f} kN")
        
        print("\n" + "=" * 70)
        print("考试要点：")
        print("=" * 70)
        print("1. 帕斯卡原理：密闭液体中，压强处处相等且垂直作用于容器壁")
        print("2. F2/A2 = F1/A1，力的放大倍数 = 面积比")
        print("3. 直径比d2/d1 = 5，则面积比A2/A1 = 25，力放大25倍")
        print("4. 实际应用需考虑摩擦、液体压缩性等损失，效率约80-90%")
        print("=" * 70)


def main():
    """主函数"""
    print("\n" + "🔧" * 35)
    print("第01章 静水力学 - 题目7：液压千斤顶")
    print("🔧" * 35 + "\n")
    
    # 题目参数
    d1 = 0.020  # 20mm = 0.02m
    d2 = 0.100  # 100mm = 0.1m
    F1 = 500    # 500N
    
    # 创建液压千斤顶对象
    jack = HydraulicJack(d1=d1, d2=d2, F1=F1)
    
    # 打印结果
    jack.print_results()
    
    # 绘图
    print("\n正在绘制液压千斤顶示意图...")
    jack.plot_hydraulic_jack()
    
    print("\n✅ 计算完成！")


if __name__ == "__main__":
    main()
