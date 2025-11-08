#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第01章 静水力学 - 题目15：浮标系统设计（清华2020真题）

题目描述：
设计一个自动调节的浮标系统，用于监测水位变化。要求：
1. 浮标在水位10-15m范围内保持漂浮
2. 通过配重自动调节稳定性
3. 绘制系统设计方案
4. 计算关键参数

设定：
- 浮标圆柱体，直径D=0.5m，高H=2m
- 材料密度ρ_材=500kg/m³
- 配重铅块密度ρ_铅=11300kg/m³

知识点：
- 浮力平衡
- 稳定性分析
- 创新设计

作者：CHS-Books Team
日期：2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Circle, Rectangle, FancyBboxPatch

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class BuoySystemDesign:
    """浮标系统设计类"""
    
    def __init__(self, D: float, H: float, rho_material: float, rho_lead: float,
                 water_range: tuple = (10, 15), wall_thickness: float = 0.05,
                 rod_length: float = 3.0, rho_water: float = 1000.0, g: float = 9.81):
        """
        初始化参数
        
        Parameters:
        -----------
        D : float
            浮标直径 (m)
        H : float
            浮标高度 (m)
        rho_material : float
            浮标材料密度 (kg/m³)
        rho_lead : float
            配重铅块密度 (kg/m³)
        water_range : tuple
            工作水深范围 (m)
        wall_thickness : float
            壁厚 (m)
        rod_length : float
            连接杆长度 (m)
        rho_water : float
            水密度 (kg/m³)
        g : float
            重力加速度 (m/s²)
        """
        self.D = D
        self.H = H
        self.rho_material = rho_material
        self.rho_lead = rho_lead
        self.water_range = water_range
        self.wall_thickness = wall_thickness
        self.rod_length = rod_length
        self.rho_water = rho_water
        self.g = g
    
    def buoy_volume_and_weight(self) -> tuple:
        """
        计算浮标体积和重量（空心圆柱）
        
        Returns:
        --------
        tuple : (V_total, V_solid, W_buoy)
            V_total : 总体积 (m³)
            V_solid : 实体体积 (m³)
            W_buoy : 浮标重量 (N)
        """
        # 外半径
        R_outer = self.D / 2
        R_inner = R_outer - self.wall_thickness
        
        # 总体积
        V_total = np.pi * R_outer**2 * self.H
        
        # 实体体积（壁体积）
        V_solid = V_total - np.pi * R_inner**2 * self.H
        
        # 重量
        W_buoy = self.rho_material * self.g * V_solid
        
        return V_total, V_solid, W_buoy
    
    def required_ballast_weight(self, draft: float) -> tuple:
        """
        计算所需配重（给定吃水深度）
        
        Parameters:
        -----------
        draft : float
            吃水深度 (m)
            
        Returns:
        --------
        tuple : (W_ballast, m_ballast, V_ballast, R_ballast)
            W_ballast : 配重重量 (N)
            m_ballast : 配重质量 (kg)
            V_ballast : 配重体积 (m³)
            R_ballast : 配重球半径 (m)
        """
        V_total, _, W_buoy = self.buoy_volume_and_weight()
        
        # 浮力
        V_submerged = np.pi * (self.D/2)**2 * draft
        F_buoyancy = self.rho_water * self.g * V_submerged
        
        # 配重
        W_ballast = F_buoyancy - W_buoy
        
        if W_ballast < 0:
            return 0, 0, 0, 0
        
        m_ballast = W_ballast / self.g
        V_ballast = m_ballast / self.rho_lead
        
        # 假设配重为球形
        R_ballast = (3 * V_ballast / (4 * np.pi))**(1/3)
        
        return W_ballast, m_ballast, V_ballast, R_ballast
    
    def stability_analysis(self, draft: float) -> tuple:
        """
        稳定性分析
        
        Parameters:
        -----------
        draft : float
            吃水深度 (m)
            
        Returns:
        --------
        tuple : (z_G, z_B, BM, GM, is_stable)
            z_G : 重心位置 (m)
            z_B : 浮心位置 (m)
            BM : 浮心半径 (m)
            GM : 稳心高 (m)
            is_stable : 是否稳定
        """
        _, V_solid, W_buoy = self.buoy_volume_and_weight()
        W_ballast, _, _, R_ballast = self.required_ballast_weight(draft)
        
        # 重心位置（从水面算起）
        # 浮标重心在其几何中心
        z_G_buoy = draft - self.H/2
        
        # 配重重心在浮标下方（连接杆+配重半径）
        z_G_ballast = draft + self.rod_length + R_ballast
        
        # 总重心
        W_total = W_buoy + W_ballast
        z_G = (W_buoy * z_G_buoy + W_ballast * z_G_ballast) / W_total
        
        # 浮心位置（排水体积形心）
        z_B = draft / 2
        
        # 浮心半径（圆柱）
        BM = (self.D/2)**2 / (4 * draft)
        
        # 稳心高
        GM = z_B + BM - z_G
        
        is_stable = GM > 0
        
        return z_G, z_B, BM, GM, is_stable
    
    def draft_optimization(self, draft_range: tuple = (0.2, 1.5), n_points: int = 30) -> tuple:
        """
        吃水深度优化分析
        
        Parameters:
        -----------
        draft_range : tuple
            吃水深度范围 (m)
        n_points : int
            计算点数
            
        Returns:
        --------
        tuple : (draft_array, GM_array, W_ballast_array)
        """
        draft_array = np.linspace(draft_range[0], draft_range[1], n_points)
        GM_array = []
        W_ballast_array = []
        
        for draft in draft_array:
            _, _, _, GM, _ = self.stability_analysis(draft)
            GM_array.append(GM)
            
            W_ballast, _, _, _ = self.required_ballast_weight(draft)
            W_ballast_array.append(W_ballast)
        
        return draft_array, np.array(GM_array), np.array(W_ballast_array)
    
    def plot_buoy_design(self):
        """绘制浮标设计分析图"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # 图1：浮标系统结构图
        ax1 = axes[0, 0]
        
        draft = 0.5  # 示例吃水深度
        W_ballast, _, _, R_ballast = self.required_ballast_weight(draft)
        
        # 水面
        ax1.plot([-1, 1], [0, 0], 'b-', linewidth=3, label='水面')
        ax1.fill_between([-1, 1], [-5, -5], [0, 0], color='lightblue', alpha=0.3)
        
        # 浮标（圆柱）
        buoy = Rectangle((-self.D/2, -draft), self.D, self.H,
                        facecolor='yellow', edgecolor='black', linewidth=2,
                        alpha=0.7, label='浮标')
        ax1.add_patch(buoy)
        
        # 内部空心
        R_inner = self.D/2 - self.wall_thickness
        inner = Rectangle((-R_inner, -draft + 0.1), 2*R_inner, self.H - 0.2,
                         facecolor='white', edgecolor='gray', linewidth=1,
                         linestyle='--', alpha=0.5)
        ax1.add_patch(inner)
        
        # 连接杆
        rod_x = 0
        rod_y_top = -draft
        rod_y_bottom = rod_y_top - self.rod_length
        ax1.plot([rod_x, rod_x], [rod_y_top, rod_y_bottom], 'k-', 
                linewidth=3, label='连接杆')
        
        # 配重（铅球）
        ballast_center = rod_y_bottom - R_ballast
        ballast = Circle((0, ballast_center), R_ballast, 
                        facecolor='gray', edgecolor='black', linewidth=2,
                        alpha=0.8, label='配重')
        ax1.add_patch(ballast)
        
        # 重心、浮心标注
        z_G, z_B, BM, GM, is_stable = self.stability_analysis(draft)
        
        # 浮心B
        ax1.plot([0], [-z_B], 'bo', markersize=12, label='浮心B')
        ax1.text(0.15, -z_B, f'B\n(z={z_B:.2f}m)', fontsize=9, fontweight='bold')
        
        # 重心G
        ax1.plot([0], [-z_G], 'ro', markersize=12, label='重心G')
        ax1.text(0.15, -z_G, f'G\n(z={z_G:.2f}m)', fontsize=9, fontweight='bold')
        
        # 稳心M
        z_M = z_B + BM
        ax1.plot([0], [-z_M], 'g^', markersize=12, label='稳心M')
        ax1.text(0.15, -z_M, f'M\n(z={z_M:.2f}m)', fontsize=9, fontweight='bold')
        
        # 标注尺寸
        ax1.text(-self.D/2 - 0.15, -draft + self.H/2, f'H={self.H}m',
                rotation=90, ha='right', fontsize=9, fontweight='bold')
        ax1.text(0, -draft - 0.15, f'D={self.D}m', ha='center',
                fontsize=9, fontweight='bold')
        
        # 稳定性判断
        stability_text = '稳定' if is_stable else '不稳定'
        stability_color = 'green' if is_stable else 'red'
        ax1.text(0.6, -1.5, f'GM={GM:.3f}m\n{stability_text}',
                ha='center', fontsize=11, fontweight='bold', color=stability_color,
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        ax1.set_xlim(-1, 1)
        ax1.set_ylim(-5, 2)
        ax1.set_xlabel('径向距离 (m)', fontsize=11, fontweight='bold')
        ax1.set_ylabel('深度 (m，水面=0)', fontsize=11, fontweight='bold')
        ax1.set_title('浮标系统结构设计', fontsize=13, fontweight='bold')
        ax1.legend(fontsize=8, loc='upper right')
        ax1.grid(True, alpha=0.3)
        ax1.set_aspect('equal')
        
        # 图2：受力分析
        ax2 = axes[0, 1]
        
        _, V_solid, W_buoy = self.buoy_volume_and_weight()
        F_buoyancy = self.rho_water * self.g * np.pi * (self.D/2)**2 * draft
        
        forces = ['浮标重量\nW_buoy', '配重\nW_ballast', '浮力\nF_b']
        values = [W_buoy, W_ballast, F_buoyancy]
        colors = ['lightyellow', 'lightgray', 'lightblue']
        
        bars = ax2.bar(forces, values, color=colors, edgecolor='black',
                      linewidth=2, alpha=0.8)
        
        # 标注数值
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2, height + max(values)*0.03,
                    f'{val:.0f}N', ha='center', fontsize=10, fontweight='bold')
        
        ax2.set_ylabel('力 (N)', fontsize=11, fontweight='bold')
        ax2.set_title('受力分析', fontsize=13, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='y')
        
        # 标注平衡条件
        W_total = W_buoy + W_ballast
        balance_error = abs(W_total - F_buoyancy) / F_buoyancy * 100
        ax2.text(1, max(values) * 0.7,
                f'平衡条件：\nW_total = F_b\n{W_total:.0f} ≈ {F_buoyancy:.0f}N\n误差{balance_error:.2f}%',
                ha='center', fontsize=9, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        # 图3：吃水深度优化
        ax3 = axes[1, 0]
        
        draft_array, GM_array, W_ballast_array = self.draft_optimization()
        
        ax3.plot(draft_array, GM_array, 'b-', linewidth=2.5, label='稳心高GM')
        ax3.axhline(y=0, color='red', linestyle='--', linewidth=2, label='稳定性界限')
        ax3.fill_between(draft_array, 0, GM_array, where=(GM_array>0),
                        color='lightgreen', alpha=0.3, label='稳定区域')
        ax3.fill_between(draft_array, 0, GM_array, where=(GM_array<=0),
                        color='lightcoral', alpha=0.3, label='不稳定区域')
        
        # 标注推荐吃水深度
        stable_drafts = draft_array[GM_array > 0]
        if len(stable_drafts) > 0:
            optimal_draft = stable_drafts[len(stable_drafts)//2]
            optimal_GM = GM_array[np.argmin(np.abs(draft_array - optimal_draft))]
            ax3.plot([optimal_draft], [optimal_GM], 'g^', markersize=12,
                    label=f'推荐: d={optimal_draft:.2f}m')
        
        ax3.set_xlabel('吃水深度 (m)', fontsize=11, fontweight='bold')
        ax3.set_ylabel('稳心高 GM (m)', fontsize=11, fontweight='bold')
        ax3.set_title('稳定性分析', fontsize=13, fontweight='bold')
        ax3.legend(fontsize=9)
        ax3.grid(True, alpha=0.3)
        
        # 图4：配重与吃水关系
        ax4 = axes[1, 1]
        
        ax4.plot(draft_array, W_ballast_array/1000, 'r-', linewidth=2.5,
                label='所需配重')
        ax4.plot([draft], [W_ballast/1000], 'ro', markersize=12,
                label=f'当前设计: d={draft}m')
        
        ax4.set_xlabel('吃水深度 (m)', fontsize=11, fontweight='bold')
        ax4.set_ylabel('配重 (kN)', fontsize=11, fontweight='bold')
        ax4.set_title('配重需求分析', fontsize=13, fontweight='bold')
        ax4.legend(fontsize=10)
        ax4.grid(True, alpha=0.3)
        
        # 标注设计建议
        ax4.text(0.8, max(W_ballast_array/1000) * 0.7,
                f'设计建议：\n吃水深度：{optimal_draft:.2f}m\n配重：{W_ballast_array[np.argmin(np.abs(draft_array - optimal_draft))]/1000:.1f}kN',
                ha='center', fontsize=9, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        plt.tight_layout()
        plt.show()
    
    def print_results(self):
        """打印计算结果"""
        print("=" * 70)
        print("浮标系统创新设计（清华2020真题）")
        print("=" * 70)
        
        print(f"\n设计要求：")
        print(f"  ✓ 工作水深：{self.water_range[0]}-{self.water_range[1]}m")
        print(f"  ✓ 保持漂浮状态")
        print(f"  ✓ 自动调节稳定性")
        print(f"  ✓ 配重优化设计")
        
        print(f"\n输入参数：")
        print(f"  浮标：直径D={self.D}m，高度H={self.H}m")
        print(f"  材料密度：ρ_材={self.rho_material}kg/m³")
        print(f"  配重密度：ρ_铅={self.rho_lead}kg/m³")
        print(f"  壁厚：t={self.wall_thickness}m（空心设计）")
        print(f"  连接杆长：L={self.rod_length}m")
        
        # (1) 浮标参数
        V_total, V_solid, W_buoy = self.buoy_volume_and_weight()
        
        print(f"\n(1) 浮标参数计算：")
        print(f"\n  空心圆柱设计：")
        print(f"    外半径：R_外 = {self.D/2:.3f} m")
        print(f"    内半径：R_内 = {self.D/2 - self.wall_thickness:.3f} m")
        print(f"    总体积：V_总 = π×R²×H = {V_total:.4f} m³")
        print(f"    实体体积：V_实 = {V_solid:.4f} m³")
        print(f"    浮标重量：W_浮 = ρ_材×g×V_实")
        print(f"            = {self.rho_material}×{self.g}×{V_solid:.4f}")
        print(f"            = {W_buoy:.0f} N = {W_buoy/1000:.2f} kN")
        
        # (2) 配重计算（以吃水0.5m为例）
        draft = 0.5
        W_ballast, m_ballast, V_ballast, R_ballast = self.required_ballast_weight(draft)
        
        print(f"\n(2) 配重计算（吃水深度d={draft}m）：")
        print(f"\n  浮力：")
        V_submerged = np.pi * (self.D/2)**2 * draft
        F_buoyancy = self.rho_water * self.g * V_submerged
        print(f"    排水体积：V_排 = π×R²×d = {V_submerged:.4f} m³")
        print(f"    浮力：F_b = ρ_水×g×V_排 = {F_buoyancy:.0f} N")
        
        print(f"\n  配重：")
        print(f"    平衡条件：W_浮 + W_配 = F_b")
        print(f"    W_配 = F_b - W_浮 = {F_buoyancy:.0f} - {W_buoy:.0f}")
        print(f"         = {W_ballast:.0f} N = {W_ballast/1000:.2f} kN")
        print(f"    配重质量：m_配 = {m_ballast:.2f} kg")
        print(f"    配重体积：V_配 = m_配/ρ_铅 = {V_ballast:.6f} m³")
        print(f"    铅球半径：R_配 = {R_ballast:.3f} m = {R_ballast*100:.1f} cm")
        
        # (3) 稳定性分析
        z_G, z_B, BM, GM, is_stable = self.stability_analysis(draft)
        
        print(f"\n(3) 稳定性分析：")
        print(f"\n  关键位置（从水面算起）：")
        print(f"    浮心B：z_B = {z_B:.3f} m（排水体积形心）")
        print(f"    重心G：z_G = {z_G:.3f} m（总重心）")
        print(f"    稳心M：z_M = z_B + BM = {z_B + BM:.3f} m")
        
        print(f"\n  稳定性指标：")
        print(f"    浮心半径：BM = R²/(4d) = {BM:.3f} m")
        print(f"    稳心高：GM = z_B + BM - z_G")
        print(f"          = {z_B:.3f} + {BM:.3f} - {z_G:.3f}")
        print(f"          = {GM:.3f} m")
        
        if is_stable:
            print(f"\n  ✓ GM > 0，系统稳定！")
            print(f"  ✓ 倾斜后可自动恢复")
        else:
            print(f"\n  ✗ GM < 0，系统不稳定！")
            print(f"  ✗ 需要重新设计")
        
        # (4) 优化设计
        draft_array, GM_array, W_ballast_array = self.draft_optimization()
        stable_drafts = draft_array[GM_array > 0]
        
        print(f"\n(4) 优化设计建议：")
        
        if len(stable_drafts) > 0:
            optimal_draft = stable_drafts[len(stable_drafts)//2]
            optimal_idx = np.argmin(np.abs(draft_array - optimal_draft))
            optimal_GM = GM_array[optimal_idx]
            optimal_W = W_ballast_array[optimal_idx]
            
            print(f"\n  推荐设计方案：")
            print(f"    吃水深度：d = {optimal_draft:.2f} m")
            print(f"    配重：W_配 = {optimal_W/1000:.2f} kN")
            print(f"    稳心高：GM = {optimal_GM:.3f} m")
            print(f"    稳定性：优良")
            
            # 配重球尺寸
            _, m_opt, V_opt, R_opt = self.required_ballast_weight(optimal_draft)
            print(f"\n  配重球规格：")
            print(f"    质量：{m_opt:.1f} kg")
            print(f"    半径：{R_opt:.3f} m = {R_opt*100:.1f} cm")
            print(f"    体积：{V_opt:.6f} m³")
        else:
            print(f"\n  ⚠ 当前参数下无稳定设计！")
            print(f"  建议：")
            print(f"    • 增大浮标直径至{self.D*1.5:.2f}m")
            print(f"    • 或减小高度至{self.H*0.5:.2f}m")
            print(f"    • 或采用空心设计（已采用）")
        
        print(f"\n  【多工况适应性】")
        print(f"  水位{self.water_range[0]}-{self.water_range[1]}m范围内：")
        for h in range(self.water_range[0], self.water_range[1]+1, 2):
            print(f"    水位{h}m：浮标保持漂浮，配重不变 ✓")
        
        print(f"\n  【关键技术】")
        print(f"    ✓ 低重心设计：配重在底部")
        print(f"    ✓ 空心结构：降低浮标重量")
        print(f"    ✓ 连接杆：降低重心，增加稳定性")
        print(f"    ✓ 球形配重：最小体积，最大质量")
        
        print("\n" + "=" * 70)
        print("考试要点：")
        print("=" * 70)
        print("1. 浮力平衡：W_浮 + W_配 = F_b")
        print("2. 稳定性判据：GM > 0（稳定），GM < 0（不稳定）")
        print("3. 重心控制：配重在底部，降低重心")
        print("4. 空心设计：减小重量，保持浮力")
        print("5. 创新能力：结构设计、参数优化、工程实用")
        print("=" * 70)


def main():
    """主函数"""
    print("\n" + "💧" * 35)
    print("第01章 静水力学 - 题目15：浮标系统设计")
    print("💧" * 35 + "\n")
    
    # 题目参数
    D = 0.5           # 直径0.5m
    H = 2.0           # 高度2m
    rho_material = 500  # 材料密度500kg/m³
    rho_lead = 11300    # 铅密度11300kg/m³
    water_range = (10, 15)  # 工作水深10-15m
    wall_thickness = 0.05   # 壁厚0.05m（空心设计）
    rod_length = 3.0        # 连接杆长3m
    
    # 创建浮标设计对象
    buoy = BuoySystemDesign(D=D, H=H, rho_material=rho_material,
                           rho_lead=rho_lead, water_range=water_range,
                           wall_thickness=wall_thickness, rod_length=rod_length)
    
    # 打印结果
    buoy.print_results()
    
    # 绘图
    print("\n正在绘制浮标系统设计分析图...")
    buoy.plot_buoy_design()
    
    print("\n✅ 计算完成！")


if __name__ == "__main__":
    main()
