#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第01章 静水力学 - 题目12：潜水艇沉浮控制

题目描述：
潜水艇总体积V=1000m³，空载质量m0=800吨，
通过调节水舱进出水来控制沉浮。求：
(1) 悬浮时水舱需要的水量
(2) 下潜100m时受到的压强
(3) 上浮所需排出的水量

知识点：
- 浮力与重力平衡
- 可变浮力控制
- 深水压强计算

作者：CHS-Books Team
日期：2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class Submarine:
    """潜水艇沉浮控制计算类"""
    
    def __init__(self, V: float, m0: float, rho_water: float = 1025.0, g: float = 9.81):
        """
        初始化参数
        
        Parameters:
        -----------
        V : float
            潜艇总体积 (m³)
        m0 : float
            空载质量 (kg)
        rho_water : float
            海水密度 (kg/m³)，默认1025
        g : float
            重力加速度 (m/s²)
        """
        self.V = V
        self.m0 = m0
        self.rho_water = rho_water
        self.g = g
        
    def buoyancy_force(self) -> float:
        """
        计算最大浮力（全部排水时）
        
        Returns:
        --------
        float : 浮力 (N)
        """
        return self.rho_water * self.g * self.V
    
    def weight_empty(self) -> float:
        """
        计算空载重力
        
        Returns:
        --------
        float : 重力 (N)
        """
        return self.m0 * self.g
    
    def water_for_neutral_buoyancy(self) -> tuple:
        """
        计算悬浮所需水舱水量
        
        Returns:
        --------
        tuple : (m_water, V_water)
                m_water: 水质量 (kg)
                V_water: 水体积 (m³)
        """
        # 悬浮条件：浮力 = 总重力
        # ρ_water × g × V = (m0 + m_water) × g
        m_water = self.rho_water * self.V - self.m0
        V_water = m_water / self.rho_water
        return m_water, V_water
    
    def pressure_at_depth(self, h: float, p0: float = 101325.0) -> tuple:
        """
        计算某深度的压强
        
        Parameters:
        -----------
        h : float
            水深 (m)
        p0 : float
            水面气压 (Pa)
            
        Returns:
        --------
        tuple : (p_abs, p_gauge)
                p_abs: 绝对压强 (Pa)
                p_gauge: 表压 (Pa)
        """
        p_gauge = self.rho_water * self.g * h
        p_abs = p0 + p_gauge
        return p_abs, p_gauge
    
    def water_to_surface(self, current_depth: float) -> tuple:
        """
        计算从当前深度上浮所需排出的水量
        
        Parameters:
        -----------
        current_depth : float
            当前深度 (m)
            
        Returns:
        --------
        tuple : (m_eject, V_eject)
                m_eject: 需排出的水质量 (kg)
                V_eject: 需排出的水体积 (m³)
        """
        # 悬浮时的水量
        m_water_neutral, _ = self.water_for_neutral_buoyancy()
        
        # 上浮需要浮力 > 重力，设排出水量为m_eject
        # 保守估计：排出10%的水舱水即可产生足够浮力
        m_eject = m_water_neutral * 0.1
        V_eject = m_eject / self.rho_water
        
        return m_eject, V_eject
    
    def plot_submarine_states(self):
        """绘制潜艇不同状态示意图"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        states = [
            {'title': '状态1: 水面漂浮', 'depth': 0, 'water_ratio': 0.2},
            {'title': '状态2: 中性悬浮', 'depth': 50, 'water_ratio': 0.5},
            {'title': '状态3: 下潜100m', 'depth': 100, 'water_ratio': 0.7},
            {'title': '状态4: 上浮准备', 'depth': 100, 'water_ratio': 0.3}
        ]
        
        for idx, (ax, state) in enumerate(zip(axes.flat, states)):
            # 绘制海水
            ax.fill_between([0, 10], [0, 0], [-150, -150], 
                           color='lightblue', alpha=0.5, label='海水')
            ax.plot([0, 10], [0, 0], 'b-', linewidth=2, label='海面')
            
            # 绘制潜艇（椭圆形）
            sub_y = -state['depth']
            sub_width = 3
            sub_height = 1
            
            ellipse = patches.Ellipse((5, sub_y), sub_width, sub_height,
                                     linewidth=3, edgecolor='black',
                                     facecolor='gray', alpha=0.8)
            ax.add_patch(ellipse)
            
            # 绘制水舱（内部蓝色部分表示水量）
            water_width = sub_width * 0.6 * state['water_ratio']
            water_rect = patches.Rectangle((5 - water_width/2, sub_y - sub_height/3),
                                          water_width, sub_height/2,
                                          linewidth=1, edgecolor='blue',
                                          facecolor='cyan', alpha=0.7)
            ax.add_patch(water_rect)
            
            # 标注深度
            if state['depth'] > 0:
                ax.plot([1, 1], [0, sub_y], 'r--', linewidth=2)
                ax.text(0.5, sub_y/2, f'{state["depth"]}m', 
                       fontsize=11, fontweight='bold', color='red')
            
            # 标注水舱水量百分比
            ax.text(5, sub_y, f'{state["water_ratio"]*100:.0f}%满', 
                   ha='center', va='center', fontsize=10, fontweight='bold',
                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
            
            # 标注状态
            ax.text(5, 20, state['title'], ha='center', fontsize=12, fontweight='bold',
                   bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
            
            # 绘制力的方向
            if state['water_ratio'] < 0.5:
                # 浮力 > 重力，向上箭头
                ax.arrow(5, sub_y - sub_height/2 - 5, 0, -3,
                        head_width=0.5, head_length=1, fc='green', ec='green', lw=3)
                ax.text(6, sub_y - sub_height/2 - 7, '上浮', fontsize=11, 
                       fontweight='bold', color='green')
            elif state['water_ratio'] > 0.5:
                # 浮力 < 重力，向下箭头
                ax.arrow(5, sub_y + sub_height/2 + 5, 0, 3,
                        head_width=0.5, head_length=1, fc='red', ec='red', lw=3)
                ax.text(6, sub_y + sub_height/2 + 7, '下潜', fontsize=11, 
                       fontweight='bold', color='red')
            else:
                # 悬浮
                ax.text(6, sub_y, '悬浮', fontsize=11, fontweight='bold', color='blue')
            
            ax.set_xlim(0, 10)
            ax.set_ylim(-150, 25)
            ax.set_xlabel('水平位置 (m)', fontsize=11)
            ax.set_ylabel('深度 (m)', fontsize=11)
            ax.grid(True, alpha=0.3)
            ax.set_aspect('equal')
        
        plt.tight_layout()
        plt.show()
    
    def plot_pressure_vs_depth(self):
        """绘制压强随深度变化曲线"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        depths = np.linspace(0, 200, 100)
        pressures_abs = []
        pressures_gauge = []
        
        for h in depths:
            p_abs, p_gauge = self.pressure_at_depth(h)
            pressures_abs.append(p_abs / 1e6)  # 转换为MPa
            pressures_gauge.append(p_gauge / 1e6)
        
        ax.plot(pressures_abs, depths, 'b-', linewidth=2.5, label='绝对压强')
        ax.plot(pressures_gauge, depths, 'r--', linewidth=2.5, label='表压')
        
        # 标注关键深度
        key_depths = [0, 50, 100, 150, 200]
        for h in key_depths:
            p_abs, p_gauge = self.pressure_at_depth(h)
            ax.plot(p_abs/1e6, h, 'bo', markersize=8)
            ax.text(p_abs/1e6 + 0.1, h, f'{h}m\n{p_abs/1e6:.2f}MPa', 
                   fontsize=9, bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))
        
        ax.set_xlabel('压强 (MPa)', fontsize=12, fontweight='bold')
        ax.set_ylabel('深度 (m)', fontsize=12, fontweight='bold')
        ax.set_title('海水压强随深度变化', fontsize=14, fontweight='bold')
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)
        ax.invert_yaxis()
        
        plt.tight_layout()
        plt.show()
    
    def print_results(self):
        """打印计算结果"""
        print("=" * 70)
        print("潜水艇沉浮控制计算")
        print("=" * 70)
        
        print(f"\n输入参数：")
        print(f"  潜艇总体积 V = {self.V} m³")
        print(f"  空载质量 m0 = {self.m0/1000:.0f} 吨 = {self.m0} kg")
        print(f"  海水密度 ρ = {self.rho_water} kg/m³")
        
        Fb = self.buoyancy_force()
        W0 = self.weight_empty()
        print(f"\n最大浮力：")
        print(f"  Fb = ρ×g×V = {self.rho_water}×{self.g}×{self.V}")
        print(f"     = {Fb:.2f} N = {Fb/1000:.2f} kN")
        
        print(f"\n空载重力：")
        print(f"  W0 = m0×g = {self.m0}×{self.g}")
        print(f"     = {W0:.2f} N = {W0/1000:.2f} kN")
        
        print(f"\n浮力储备：")
        print(f"  Fb - W0 = {(Fb-W0)/1000:.2f} kN = {(Fb-W0)/(W0)*100:.2f}%")
        
        m_water, V_water = self.water_for_neutral_buoyancy()
        print(f"\n悬浮条件（中性浮力）：")
        print(f"  需要水舱进水：")
        print(f"    质量 m_water = ρ×V - m0 = {self.rho_water}×{self.V} - {self.m0}")
        print(f"             = {m_water:.2f} kg = {m_water/1000:.2f} 吨")
        print(f"    体积 V_water = m_water/ρ = {m_water}/{self.rho_water}")
        print(f"             = {V_water:.4f} m³")
        print(f"    占总体积 {V_water/self.V*100:.2f}%")
        
        print(f"\n下潜100m深度：")
        p_abs_100, p_gauge_100 = self.pressure_at_depth(100)
        print(f"  绝对压强 p = {p_abs_100:.2f} Pa = {p_abs_100/1e6:.2f} MPa")
        print(f"  表压 = {p_gauge_100:.2f} Pa = {p_gauge_100/1e6:.2f} MPa")
        print(f"  相当于大气压的 {p_abs_100/101325:.2f} 倍")
        
        m_eject, V_eject = self.water_to_surface(100)
        print(f"\n上浮所需排水量：")
        print(f"  排出水量 ≈ {m_eject:.2f} kg = {m_eject/1000:.2f} 吨")
        print(f"  排出体积 ≈ {V_eject:.4f} m³")
        print(f"  占水舱水量的 {m_eject/m_water*100:.2f}%")
        
        print("\n" + "=" * 70)
        print("考试要点：")
        print("=" * 70)
        print("1. 悬浮条件：浮力 = 总重力，ρ_water×g×V = (m0+m_water)×g")
        print("2. 下潜：注水增重，使浮力 < 总重力")
        print("3. 上浮：排水减重，使浮力 > 总重力")
        print("4. 深水压强：p = p0 + ρ×g×h，每下潜10m压强增加约0.1MPa")
        print("=" * 70)


def main():
    """主函数"""
    print("\n" + "🚢" * 35)
    print("第01章 静水力学 - 题目12：潜水艇沉浮控制")
    print("🚢" * 35 + "\n")
    
    # 题目参数
    V = 1000      # 总体积1000m³
    m0 = 800000   # 空载质量800吨 = 800000kg
    
    # 创建潜水艇对象
    sub = Submarine(V=V, m0=m0)
    
    # 打印结果
    sub.print_results()
    
    # 绘图
    print("\n正在绘制潜艇不同状态示意图...")
    sub.plot_submarine_states()
    
    print("\n正在绘制压强-深度关系图...")
    sub.plot_pressure_vs_depth()
    
    print("\n✅ 计算完成！")


if __name__ == "__main__":
    main()
