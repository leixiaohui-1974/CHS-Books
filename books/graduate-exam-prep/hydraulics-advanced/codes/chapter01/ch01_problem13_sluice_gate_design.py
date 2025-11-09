#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第01章 静水力学 - 题目13：水闸设计综合题

题目描述：
设计一座水闸：
- 闸门：矩形平板，宽b=10m，高h=5m
- 上游水深：h1=4m
- 下游水深：h2=1m
- 闸门可绕底部铰链转动

求：
(1) 上下游作用于闸门的总压力差
(2) 启闭力矩（绕铰链）
(3) 卷扬机拉力（作用点距铰链6m）
(4) 不同水位差对启闭力的影响

知识点：
- 静水压力计算
- 压力中心
- 力矩平衡
- 工程设计

作者：CHS-Books Team
日期：2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class SluiceGateDesign:
    """水闸设计综合计算类"""
    
    def __init__(self, b: float, h: float, h1: float, h2: float,
                 l_F: float = 6.0, rho: float = 1000.0, g: float = 9.81):
        """
        初始化参数
        
        Parameters:
        -----------
        b : float
            闸门宽度 (m)
        h : float
            闸门高度 (m)
        h1 : float
            上游水深 (m)
        h2 : float
            下游水深 (m)
        l_F : float
            卷扬机作用点距铰链距离 (m)
        rho : float
            水密度 (kg/m³)
        g : float
            重力加速度 (m/s²)
        """
        self.b = b
        self.h = h
        self.h1 = h1
        self.h2 = h2
        self.l_F = l_F
        self.rho = rho
        self.g = g
    
    def upstream_pressure(self) -> tuple:
        """
        计算上游总压力和压力中心
        
        Returns:
        --------
        tuple : (P1, l_P1)
            P1 : 上游总压力 (N)
            l_P1 : 压力中心距铰链距离 (m)
        """
        # 形心深度
        h_c1 = self.h1 / 2
        
        # 总压力
        A1 = self.b * self.h1
        P1 = self.rho * self.g * h_c1 * A1
        
        # 压力中心距水面距离
        y_c = h_c1
        I_c = self.b * self.h1**3 / 12
        y_D = y_c + I_c / (A1 * y_c)
        
        # 压力中心距铰链（底部）距离
        l_P1 = self.h1 - y_D
        
        return P1, l_P1
    
    def downstream_pressure(self) -> tuple:
        """
        计算下游总压力和压力中心
        
        Returns:
        --------
        tuple : (P2, l_P2)
            P2 : 下游总压力 (N)
            l_P2 : 压力中心距铰链距离 (m)
        """
        # 形心深度
        h_c2 = self.h2 / 2
        
        # 总压力
        A2 = self.b * self.h2
        P2 = self.rho * self.g * h_c2 * A2
        
        # 压力中心距水面距离
        y_c = h_c2
        I_c = self.b * self.h2**3 / 12
        y_D = y_c + I_c / (A2 * y_c)
        
        # 压力中心距铰链距离
        l_P2 = self.h2 - y_D
        
        return P2, l_P2
    
    def net_pressure(self) -> float:
        """
        计算净压力
        
        Returns:
        --------
        float : 净压力 ΔP (N)
        """
        P1, _ = self.upstream_pressure()
        P2, _ = self.downstream_pressure()
        return P1 - P2
    
    def opening_moment(self) -> float:
        """
        计算启闭力矩（绕铰链）
        
        Returns:
        --------
        float : 启闭力矩 M_O (N·m)
        """
        P1, l_P1 = self.upstream_pressure()
        P2, l_P2 = self.downstream_pressure()
        
        M_O = P1 * l_P1 - P2 * l_P2
        
        return M_O
    
    def winch_force(self) -> float:
        """
        计算卷扬机拉力
        
        Returns:
        --------
        float : 卷扬机拉力 F (N)
        """
        M_O = self.opening_moment()
        F = M_O / self.l_F
        return F
    
    def water_level_analysis(self, h1_range: tuple = (2, 6), h2_range: tuple = (0, 2),
                            n_points: int = 20) -> tuple:
        """
        分析不同水位差对启闭力的影响
        
        Parameters:
        -----------
        h1_range : tuple
            上游水位范围 (m)
        h2_range : tuple
            下游水位范围 (m)
        n_points : int
            计算点数
            
        Returns:
        --------
        tuple : (h1_array, h2_array, M_grid)
        """
        h1_array = np.linspace(h1_range[0], h1_range[1], n_points)
        h2_array = np.linspace(h2_range[0], h2_range[1], n_points)
        
        M_grid = np.zeros((len(h2_array), len(h1_array)))
        
        original_h1 = self.h1
        original_h2 = self.h2
        
        for i, h2 in enumerate(h2_array):
            for j, h1 in enumerate(h1_array):
                self.h1 = h1
                self.h2 = h2
                M_grid[i, j] = self.opening_moment() / 1000  # 转换为kN·m
        
        # 恢复原值
        self.h1 = original_h1
        self.h2 = original_h2
        
        return h1_array, h2_array, M_grid
    
    def plot_design_analysis(self):
        """绘制水闸设计分析图"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # 图1：水闸结构示意图
        ax1 = axes[0, 0]
        
        # 闸门
        gate_x = [0, 0]
        gate_y = [0, self.h]
        ax1.plot(gate_x, gate_y, 'k-', linewidth=5, label='闸门')
        
        # 铰链
        ax1.plot([0], [0], 'ro', markersize=15, label='铰链')
        
        # 上游水体
        ax1.fill_between([-3, 0], [0, 0], [self.h1, self.h1],
                        color='lightblue', alpha=0.6, label=f'上游水深{self.h1}m')
        ax1.plot([-3, 0], [self.h1, self.h1], 'b-', linewidth=2)
        
        # 下游水体
        ax1.fill_between([0, 3], [0, 0], [self.h2, self.h2],
                        color='lightcyan', alpha=0.6, label=f'下游水深{self.h2}m')
        ax1.plot([0, 3], [self.h2, self.h2], 'c-', linewidth=2)
        
        # 压力分布
        P1, l_P1 = self.upstream_pressure()
        P2, l_P2 = self.downstream_pressure()
        
        # 上游压力
        y_P1 = l_P1
        ax1.arrow(-0.5, y_P1, 0.3, 0, head_width=0.15, head_length=0.1,
                 fc='red', ec='red', linewidth=2)
        ax1.text(-0.8, y_P1, f'P₁={P1/1000:.0f}kN', fontsize=9, 
                color='red', fontweight='bold', ha='right')
        
        # 下游压力
        y_P2 = l_P2
        ax1.arrow(0.5, y_P2, -0.3, 0, head_width=0.1, head_length=0.1,
                 fc='orange', ec='orange', linewidth=2)
        ax1.text(0.8, y_P2, f'P₂={P2/1000:.0f}kN', fontsize=9,
                color='orange', fontweight='bold')
        
        # 卷扬机拉力
        F = self.winch_force()
        ax1.arrow(0, self.l_F, 0, 0.3, head_width=0.1, head_length=0.1,
                 fc='green', ec='green', linewidth=3)
        ax1.text(0.3, self.l_F, f'F={F/1000:.0f}kN', fontsize=10,
                color='green', fontweight='bold')
        ax1.plot([0], [self.l_F], 'g^', markersize=12)
        
        ax1.set_xlim(-4, 4)
        ax1.set_ylim(-0.5, 7)
        ax1.set_xlabel('水平距离 (m)', fontsize=11, fontweight='bold')
        ax1.set_ylabel('高程 (m)', fontsize=11, fontweight='bold')
        ax1.set_title('水闸结构示意图', fontsize=13, fontweight='bold')
        ax1.legend(fontsize=9, loc='upper right')
        ax1.grid(True, alpha=0.3)
        ax1.set_aspect('equal')
        
        # 图2：力和力矩对比
        ax2 = axes[0, 1]
        
        M_O = self.opening_moment()
        
        items = ['上游压力\nP₁', '下游压力\nP₂', '净压力\nΔP', '力矩\nM₀(÷1000)']
        values = [P1/1000, P2/1000, (P1-P2)/1000, M_O/1000]
        colors = ['lightblue', 'lightcoral', 'lightyellow', 'lightgreen']
        
        bars = ax2.bar(items, values, color=colors, edgecolor='black',
                      linewidth=2, alpha=0.8)
        
        # 标注数值
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2, height + max(values)*0.03,
                    f'{val:.0f}', ha='center', fontsize=11, fontweight='bold')
        
        ax2.set_ylabel('力 (kN) / 力矩 (kN·m)', fontsize=11, fontweight='bold')
        ax2.set_title('力和力矩分析', fontsize=13, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='y')
        
        # 图3：水位差影响
        ax3 = axes[1, 0]
        
        h1_array, h2_array, M_grid = self.water_level_analysis()
        
        # 等高线图
        contour = ax3.contourf(h1_array, h2_array, M_grid, levels=15, cmap='YlOrRd')
        contour_lines = ax3.contour(h1_array, h2_array, M_grid, levels=10,
                                    colors='black', linewidths=0.5)
        ax3.clabel(contour_lines, inline=True, fontsize=8)
        
        # 标注当前工况
        ax3.plot([self.h1], [self.h2], 'r*', markersize=20, label='当前工况')
        
        ax3.set_xlabel('上游水深 h₁ (m)', fontsize=11, fontweight='bold')
        ax3.set_ylabel('下游水深 h₂ (m)', fontsize=11, fontweight='bold')
        ax3.set_title('启闭力矩随水位变化（kN·m）', fontsize=13, fontweight='bold')
        ax3.legend(fontsize=10)
        
        cbar = plt.colorbar(contour, ax=ax3)
        cbar.set_label('力矩 (kN·m)', fontsize=10, fontweight='bold')
        
        # 图4：力臂影响分析
        ax4 = axes[1, 1]
        
        l_F_array = np.linspace(3, 10, 20)
        F_array = []
        
        original_l_F = self.l_F
        
        for l_F in l_F_array:
            self.l_F = l_F
            F_array.append(self.winch_force() / 1000)
        
        self.l_F = original_l_F
        
        ax4.plot(l_F_array, F_array, 'b-', linewidth=2.5, label='拉力-力臂关系')
        ax4.plot([self.l_F], [F/1000], 'ro', markersize=12, label=f'当前设计: {self.l_F}m')
        
        # 标注最优点
        min_idx = np.argmin(F_array)
        ax4.plot([l_F_array[min_idx]], [F_array[min_idx]], 'g^', 
                markersize=12, label=f'理论最优: {l_F_array[min_idx]:.1f}m')
        
        ax4.set_xlabel('力臂 (m)', fontsize=11, fontweight='bold')
        ax4.set_ylabel('卷扬机拉力 (kN)', fontsize=11, fontweight='bold')
        ax4.set_title('拉力与力臂关系', fontsize=13, fontweight='bold')
        ax4.legend(fontsize=10)
        ax4.grid(True, alpha=0.3)
        
        # 标注节省百分比
        F_current = F/1000
        F_optimal = F_array[min_idx]
        saving = (F_current - F_optimal) / F_current * 100
        
        ax4.text(7, max(F_array) * 0.7,
                f'优化建议：\n增大力臂至{l_F_array[min_idx]:.1f}m\n可降低拉力{saving:.1f}%',
                ha='center', fontsize=9, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        plt.tight_layout()
        plt.show()
    
    def print_results(self):
        """打印计算结果"""
        print("=" * 70)
        print("水闸设计综合计算")
        print("=" * 70)
        
        print(f"\n输入参数：")
        print(f"  闸门：宽度b={self.b}m，高度h={self.h}m")
        print(f"  上游水深：h₁={self.h1}m")
        print(f"  下游水深：h₂={self.h2}m")
        print(f"  卷扬机力臂：l_F={self.l_F}m")
        print(f"  水密度：ρ={self.rho}kg/m³")
        
        # (1) 上下游压力
        P1, l_P1 = self.upstream_pressure()
        P2, l_P2 = self.downstream_pressure()
        
        print(f"\n(1) 上下游压力计算：")
        print(f"\n  上游：")
        print(f"    形心深度：h_c1 = h₁/2 = {self.h1}/2 = {self.h1/2:.2f} m")
        print(f"    作用面积：A1 = b×h₁ = {self.b}×{self.h1} = {self.b*self.h1:.1f} m²")
        print(f"    总压力：P₁ = ρgh_c1·A1")
        print(f"          = {self.rho}×{self.g}×{self.h1/2:.2f}×{self.b*self.h1:.1f}")
        print(f"          = {P1:.0f} N = {P1/1000:.1f} kN")
        print(f"    压力中心距铰链：l_P1 = {l_P1:.3f} m")
        
        print(f"\n  下游：")
        print(f"    形心深度：h_c2 = h₂/2 = {self.h2}/2 = {self.h2/2:.2f} m")
        print(f"    作用面积：A2 = b×h₂ = {self.b}×{self.h2} = {self.b*self.h2:.1f} m²")
        print(f"    总压力：P₂ = ρgh_c2·A2")
        print(f"          = {self.rho}×{self.g}×{self.h2/2:.2f}×{self.b*self.h2:.1f}")
        print(f"          = {P2:.0f} N = {P2/1000:.2f} kN")
        print(f"    压力中心距铰链：l_P2 = {l_P2:.3f} m")
        
        delta_P = P1 - P2
        print(f"\n  净压力：ΔP = P₁ - P₂ = {P1/1000:.1f} - {P2/1000:.2f} = {delta_P/1000:.1f} kN")
        
        # (2) 启闭力矩
        M_O = self.opening_moment()
        
        print(f"\n(2) 启闭力矩（绕铰链）：")
        print(f"  M₀ = P₁·l_P1 - P₂·l_P2")
        print(f"     = {P1:.0f}×{l_P1:.3f} - {P2:.0f}×{l_P2:.3f}")
        print(f"     = {P1*l_P1:.0f} - {P2*l_P2:.0f}")
        print(f"     = {M_O:.0f} N·m = {M_O/1000:.1f} kN·m")
        
        # (3) 卷扬机拉力
        F = self.winch_force()
        
        print(f"\n(3) 卷扬机拉力：")
        print(f"  F = M₀/l_F = {M_O:.0f}/{self.l_F} = {F:.0f} N = {F/1000:.1f} kN")
        
        # 设备选型
        F_design = F * 1.2
        print(f"\n  设备选型（安全系数1.2）：")
        print(f"    F_设计 = 1.2×{F/1000:.1f} = {F_design/1000:.1f} kN")
        
        # (4) 水位差影响
        print(f"\n(4) 水位差影响分析：")
        print(f"\n  力矩与水位关系：")
        print(f"    M₀ ∝ (h₁³ - h₂³)")
        
        # 计算几种工况
        h1_cases = [2, 3, 4, 5, 6]
        print(f"\n  不同上游水位（下游{self.h2}m）：")
        print(f"  ┌────────┬───────────┬───────────┐")
        print(f"  │ h₁(m)  │ M₀(kN·m)  │  F(kN)    │")
        print(f"  ├────────┼───────────┼───────────┤")
        
        original_h1 = self.h1
        for h1 in h1_cases:
            self.h1 = h1
            M = self.opening_moment()
            F_temp = self.winch_force()
            print(f"  │  {h1:.1f}   │  {M/1000:7.1f}  │  {F_temp/1000:7.1f}  │")
        print(f"  └────────┴───────────┴───────────┘")
        
        self.h1 = original_h1
        
        print(f"\n  结论：")
        print(f"    ✓ 水位差越大，启闭力矩越大")
        print(f"    ✓ 上游水位影响显著（三次方关系）")
        print(f"    ✓ 设计应考虑最不利工况（最大水位差）")
        
        print("\n" + "=" * 70)
        print("设计要点：")
        print("=" * 70)
        print("1. 压力计算：P = ρgh_c·A")
        print("2. 压力中心：y_D = y_c + I_c/(A·y_c)")
        print("3. 力矩平衡：M₀ = P₁·l_P1 - P₂·l_P2")
        print("4. 启闭力：F = M₀/l_F（力臂越大，拉力越小）")
        print("5. 安全系数：设备容量 = 1.2~1.5倍计算值")
        print("=" * 70)


def main():
    """主函数"""
    print("\n" + "💧" * 35)
    print("第01章 静水力学 - 题目13：水闸设计")
    print("💧" * 35 + "\n")
    
    # 题目参数
    b = 10.0      # 闸门宽度10m
    h = 5.0       # 闸门高度5m
    h1 = 4.0      # 上游水深4m
    h2 = 1.0      # 下游水深1m
    l_F = 6.0     # 卷扬机力臂6m
    
    # 创建水闸设计对象
    sluice = SluiceGateDesign(b=b, h=h, h1=h1, h2=h2, l_F=l_F)
    
    # 打印结果
    sluice.print_results()
    
    # 绘图
    print("\n正在绘制水闸设计分析图...")
    sluice.plot_design_analysis()
    
    print("\n✅ 计算完成！")


if __name__ == "__main__":
    main()
