#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第01章 静水力学 - 题目14：船闸工程设计

题目描述：
设计一座船闸：
- 闸室长L=150m，宽B=20m
- 上游水位H1=20m，下游水位H2=10m
- 闸室初始水位与下游齐平

求：
(1) 将闸室水位提升到与上游齐平需要注入多少水？
(2) 阀门注水时间（A=2m²，μ=0.6，平均水头差5m）
(3) 船闸设计关键技术问题

知识点：
- 体积计算
- 孔口流量公式
- 工程设计

作者：CHS-Books Team
日期：2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class ShipLockDesign:
    """船闸工程设计计算类"""
    
    def __init__(self, L: float, B: float, H1: float, H2: float,
                 A_valve: float = 2.0, mu: float = 0.6, H_avg: float = 5.0,
                 rho: float = 1000.0, g: float = 9.81):
        """
        初始化参数
        
        Parameters:
        -----------
        L : float
            闸室长度 (m)
        B : float
            闸室宽度 (m)
        H1 : float
            上游水位 (m)
        H2 : float
            下游水位 (m)
        A_valve : float
            阀门面积 (m²)
        mu : float
            流量系数
        H_avg : float
            平均水头差 (m)
        rho : float
            水密度 (kg/m³)
        g : float
            重力加速度 (m/s²)
        """
        self.L = L
        self.B = B
        self.H1 = H1
        self.H2 = H2
        self.A_valve = A_valve
        self.mu = mu
        self.H_avg = H_avg
        self.rho = rho
        self.g = g
    
    def water_volume_required(self) -> tuple:
        """
        计算所需注水量
        
        Returns:
        --------
        tuple : (V, delta_H)
            V : 注水体积 (m³)
            delta_H : 水位差 (m)
        """
        delta_H = self.H1 - self.H2
        V = self.L * self.B * delta_H
        return V, delta_H
    
    def orifice_discharge(self) -> float:
        """
        计算阀门流量（孔口流量公式）
        
        Q = μA√(2gH)
        
        Returns:
        --------
        float : 流量 (m³/s)
        """
        Q = self.mu * self.A_valve * np.sqrt(2 * self.g * self.H_avg)
        return Q
    
    def filling_time(self) -> tuple:
        """
        计算注水时间
        
        Returns:
        --------
        tuple : (t_seconds, t_minutes)
            t_seconds : 时间 (秒)
            t_minutes : 时间 (分钟)
        """
        V, _ = self.water_volume_required()
        Q = self.orifice_discharge()
        
        t_seconds = V / Q
        t_minutes = t_seconds / 60
        
        return t_seconds, t_minutes
    
    def valve_area_optimization(self, A_range: tuple = (1, 5), 
                                n_points: int = 20) -> tuple:
        """
        阀门面积优化分析
        
        Parameters:
        -----------
        A_range : tuple
            阀门面积范围 (m²)
        n_points : int
            计算点数
            
        Returns:
        --------
        tuple : (A_array, t_array)
        """
        A_array = np.linspace(A_range[0], A_range[1], n_points)
        t_array = []
        
        original_A = self.A_valve
        
        for A in A_array:
            self.A_valve = A
            _, t_min = self.filling_time()
            t_array.append(t_min)
        
        self.A_valve = original_A
        
        return A_array, np.array(t_array)
    
    def water_head_analysis(self, t_array: np.ndarray = None) -> tuple:
        """
        注水过程中水头变化分析
        
        Parameters:
        -----------
        t_array : np.ndarray
            时间数组 (分钟)
            
        Returns:
        --------
        tuple : (t, H_lock, H_diff, Q_inst)
        """
        if t_array is None:
            _, t_total = self.filling_time()
            t_array = np.linspace(0, t_total, 50)
        
        V_total, _ = self.water_volume_required()
        Q_avg = self.orifice_discharge()
        
        H_lock = []
        H_diff = []
        Q_inst = []
        
        for t in t_array:
            # 闸室当前水位
            V_current = Q_avg * t * 60  # 转换为秒
            if V_current > V_total:
                V_current = V_total
            
            h_current = self.H2 + V_current / (self.L * self.B)
            H_lock.append(h_current)
            
            # 水头差
            h_diff = self.H1 - h_current
            if h_diff < 0:
                h_diff = 0
            H_diff.append(h_diff)
            
            # 瞬时流量
            Q = self.mu * self.A_valve * np.sqrt(2 * self.g * h_diff) if h_diff > 0 else 0
            Q_inst.append(Q)
        
        return t_array, np.array(H_lock), np.array(H_diff), np.array(Q_inst)
    
    def plot_ship_lock_analysis(self):
        """绘制船闸设计分析图"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # 图1：船闸结构示意图
        ax1 = axes[0, 0]
        
        # 上游水库
        ax1.fill_between([0, 30], [0, 0], [self.H1, self.H1],
                        color='lightblue', alpha=0.7, label=f'上游水位{self.H1}m')
        ax1.plot([0, 30], [self.H1, self.H1], 'b-', linewidth=2)
        ax1.text(15, self.H1 + 1, f'H₁={self.H1}m', ha='center', 
                fontsize=11, fontweight='bold')
        
        # 上游闸门
        ax1.add_patch(plt.Rectangle((28, 0), 2, self.H1,
                                    facecolor='gray', edgecolor='black', linewidth=2))
        ax1.text(29, self.H1/2, '上游闸门', ha='center', rotation=90,
                fontsize=9, fontweight='bold', color='white')
        
        # 闸室
        _, t_minutes = self.filling_time()
        h_mid = (self.H1 + self.H2) / 2
        
        ax1.add_patch(plt.Rectangle((30, 0), self.L/5, self.H1 * 1.1,
                                    facecolor='white', edgecolor='black',
                                    linewidth=3, fill=False))
        
        # 初始水位（下游）
        ax1.fill_between([30, 30 + self.L/5], [0, 0], [self.H2, self.H2],
                        color='lightcyan', alpha=0.5, linestyle='--')
        ax1.plot([30, 30 + self.L/5], [self.H2, self.H2], 'c--', linewidth=2,
                label=f'初始水位{self.H2}m')
        
        # 目标水位（上游）
        ax1.fill_between([30, 30 + self.L/5], [self.H2, self.H2], [self.H1, self.H1],
                        color='lightblue', alpha=0.3)
        ax1.plot([30, 30 + self.L/5], [self.H1, self.H1], 'b-', linewidth=2,
                label=f'目标水位{self.H1}m')
        
        # 阀门
        valve_x = 29
        valve_y = self.H1 - 5
        ax1.plot([valve_x, valve_x + 1], [valve_y, valve_y], 'r-', linewidth=4,
                label=f'阀门(A={self.A_valve}m²)')
        ax1.text(valve_x + 1.5, valve_y, f'Q={self.orifice_discharge():.1f}m³/s',
                fontsize=9, color='red', fontweight='bold')
        
        # 下游闸门
        ax1.add_patch(plt.Rectangle((30 + self.L/5, 0), 2, self.H2,
                                    facecolor='gray', edgecolor='black', linewidth=2))
        ax1.text(31 + self.L/5, self.H2/2, '下游闸门', ha='center', rotation=90,
                fontsize=9, fontweight='bold', color='white')
        
        # 下游水库
        ax1.fill_between([32 + self.L/5, 62 + self.L/5], [0, 0], [self.H2, self.H2],
                        color='lightcyan', alpha=0.7, label=f'下游水位{self.H2}m')
        ax1.plot([32 + self.L/5, 62 + self.L/5], [self.H2, self.H2], 'c-', linewidth=2)
        ax1.text(47 + self.L/5, self.H2 + 1, f'H₂={self.H2}m', ha='center',
                fontsize=11, fontweight='bold')
        
        # 标注闸室尺寸
        ax1.text(30 + self.L/10, -3, f'L={self.L}m, B={self.B}m',
                ha='center', fontsize=10, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        ax1.set_xlim(-2, 64 + self.L/5)
        ax1.set_ylim(-5, self.H1 + 3)
        ax1.set_xlabel('水平距离 (m)', fontsize=11, fontweight='bold')
        ax1.set_ylabel('高程 (m)', fontsize=11, fontweight='bold')
        ax1.set_title('船闸结构示意图', fontsize=13, fontweight='bold')
        ax1.legend(fontsize=8, loc='upper right')
        ax1.grid(True, alpha=0.3)
        
        # 图2：注水过程参数
        ax2 = axes[0, 1]
        
        V, delta_H = self.water_volume_required()
        Q = self.orifice_discharge()
        _, t_min = self.filling_time()
        
        items = ['水位提升\nΔH(m)', '注水量\nV(×1000m³)', '流量\nQ(m³/s)', '时间\nt(min)']
        values = [delta_H, V/1000, Q, t_min]
        colors = ['lightblue', 'lightgreen', 'lightcoral', 'lightyellow']
        
        bars = ax2.bar(items, values, color=colors, edgecolor='black',
                      linewidth=2, alpha=0.8)
        
        # 标注数值
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2, height + max(values)*0.03,
                    f'{val:.1f}', ha='center', fontsize=11, fontweight='bold')
        
        ax2.set_ylabel('数值', fontsize=11, fontweight='bold')
        ax2.set_title('注水过程参数', fontsize=13, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='y')
        
        # 图3：注水过程动态分析
        ax3 = axes[1, 0]
        
        t, H_lock, H_diff, Q_inst = self.water_head_analysis()
        
        ax3.plot(t, H_lock, 'b-', linewidth=2.5, label='闸室水位')
        ax3.plot(t, [self.H1]*len(t), 'g--', linewidth=2, label=f'上游水位{self.H1}m')
        ax3.plot(t, [self.H2]*len(t), 'c--', linewidth=2, label=f'下游水位{self.H2}m')
        ax3.fill_between(t, self.H2, H_lock, color='lightblue', alpha=0.3)
        
        ax3.set_xlabel('时间 (分钟)', fontsize=11, fontweight='bold')
        ax3.set_ylabel('水位 (m)', fontsize=11, fontweight='bold')
        ax3.set_title('闸室水位变化过程', fontsize=13, fontweight='bold')
        ax3.legend(fontsize=10)
        ax3.grid(True, alpha=0.3)
        
        # 标注关键点
        ax3.plot([t_min], [self.H1], 'ro', markersize=10)
        ax3.text(t_min, self.H1 + 0.5, f't={t_min:.0f}min', ha='center',
                fontsize=9, fontweight='bold')
        
        # 图4：阀门面积优化
        ax4 = axes[1, 1]
        
        A_array, t_array = self.valve_area_optimization()
        
        ax4.plot(A_array, t_array, 'b-', linewidth=2.5, label='注水时间')
        ax4.plot([self.A_valve], [t_min], 'ro', markersize=12,
                label=f'当前设计: A={self.A_valve}m²')
        
        # 推荐值（时间约30分钟）
        target_time = 30
        idx_optimal = np.argmin(np.abs(t_array - target_time))
        A_optimal = A_array[idx_optimal]
        ax4.plot([A_optimal], [t_array[idx_optimal]], 'g^', markersize=12,
                label=f'推荐设计: A={A_optimal:.1f}m²')
        
        ax4.axhline(y=target_time, color='orange', linestyle='--', linewidth=2,
                   label=f'目标时间{target_time}min')
        
        ax4.set_xlabel('阀门面积 (m²)', fontsize=11, fontweight='bold')
        ax4.set_ylabel('注水时间 (分钟)', fontsize=11, fontweight='bold')
        ax4.set_title('阀门面积优化分析', fontsize=13, fontweight='bold')
        ax4.legend(fontsize=9)
        ax4.grid(True, alpha=0.3)
        
        # 标注优化效果
        if A_optimal != self.A_valve:
            time_saving = t_min - t_array[idx_optimal]
            ax4.text(3, max(t_array) * 0.7,
                    f'优化建议：\n增大阀门至{A_optimal:.1f}m²\n可节省{time_saving:.0f}分钟',
                    ha='center', fontsize=9, fontweight='bold',
                    bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        plt.tight_layout()
        plt.show()
    
    def print_results(self):
        """打印计算结果"""
        print("=" * 70)
        print("船闸工程设计")
        print("=" * 70)
        
        print(f"\n输入参数：")
        print(f"  闸室尺寸：L={self.L}m，B={self.B}m")
        print(f"  上游水位：H₁={self.H1}m")
        print(f"  下游水位：H₂={self.H2}m")
        print(f"  阀门面积：A={self.A_valve}m²")
        print(f"  流量系数：μ={self.mu}")
        print(f"  平均水头差：H_avg={self.H_avg}m")
        
        # (1) 注水量
        V, delta_H = self.water_volume_required()
        
        print(f"\n(1) 所需注水量：")
        print(f"  水位提升：ΔH = H₁ - H₂ = {self.H1} - {self.H2} = {delta_H} m")
        print(f"  注水体积：V = L×B×ΔH")
        print(f"          = {self.L}×{self.B}×{delta_H}")
        print(f"          = {V:.0f} m³")
        print(f"          = {V/1000:.1f} × 10³ m³")
        
        # (2) 注水时间
        Q = self.orifice_discharge()
        t_seconds, t_minutes = self.filling_time()
        
        print(f"\n(2) 注水时间：")
        print(f"\n  孔口流量公式：Q = μA√(2gH)")
        print(f"  Q = {self.mu}×{self.A_valve}×√(2×{self.g}×{self.H_avg})")
        print(f"    = {self.mu}×{self.A_valve}×√{2*self.g*self.H_avg:.1f}")
        print(f"    = {self.mu}×{self.A_valve}×{np.sqrt(2*self.g*self.H_avg):.3f}")
        print(f"    = {Q:.3f} m³/s")
        
        print(f"\n  注水时间：t = V/Q")
        print(f"          = {V:.0f}/{Q:.3f}")
        print(f"          = {t_seconds:.0f} s")
        print(f"          = {t_minutes:.1f} min")
        print(f"          ≈ {int(t_minutes)} 分钟")
        
        # (3) 设计关键技术
        print(f"\n(3) 船闸设计关键技术问题：")
        
        print(f"\n  【1. 水力学问题】")
        print(f"    ✓ 注水/排水系统设计")
        print(f"      - 阀门位置与数量优化")
        print(f"      - 防止水流紊乱（影响船舶安全）")
        print(f"      - 注排水时间优化（运行效率）")
        print(f"    ✓ 当前设计：t={t_minutes:.0f}min，效率适中")
        
        print(f"\n  【2. 结构设计】")
        print(f"    ✓ 闸门设计")
        print(f"      - 上游闸门：承受{self.H1}m水压")
        print(f"      - 总压力：P≈{self.rho*self.g*self.H1/2*self.B*self.H1/1e6:.1f}MN")
        print(f"    ✓ 闸墙设计")
        print(f"      - 抗倾覆稳定性")
        print(f"      - 抗滑移稳定性")
        print(f"      - 基础承载力")
        
        print(f"\n  【3. 运行管理】")
        print(f"    ✓ 通航效率")
        print(f"      - 每次过闸{t_minutes:.0f}分钟")
        print(f"      - 日通过能力：约{1440/t_minutes:.0f}次")
        print(f"    ✓ 节水措施")
        print(f"      - 每次耗水：{V:.0f}m³")
        print(f"      - 考虑省水船闸（多级闸室）")
        print(f"    ✓ 安全保障")
        print(f"      - 船舶定位系统")
        print(f"      - 自动化控制")
        
        print(f"\n  【4. 优化方案】")
        A_array, t_array = self.valve_area_optimization()
        idx_30min = np.argmin(np.abs(t_array - 30))
        A_30min = A_array[idx_30min]
        
        print(f"    ✓ 缩短时间方案")
        print(f"      - 增大阀门至{A_30min:.1f}m²")
        print(f"      - 可缩短至约30分钟")
        print(f"    ✓ 多级船闸")
        print(f"      - 水位差{delta_H}m可分{int(delta_H/5)}级")
        print(f"      - 每级约5m，降低能耗")
        print(f"    ✓ 智能控制")
        print(f"      - 自动调节阀门开度")
        print(f"      - 优化注排水过程")
        
        print(f"\n  【工程实例：三峡船闸】")
        print(f"    • 双线五级船闸")
        print(f"    • 总水头差：113m")
        print(f"    • 每级水头差：约22.5m")
        print(f"    • 过闸时间：约3小时")
        print(f"    • 世界级工程！")
        
        print("\n" + "=" * 70)
        print("考试要点：")
        print("=" * 70)
        print("1. 体积计算：V = L×B×ΔH")
        print("2. 孔口流量：Q = μA√(2gH)")
        print("3. 时间计算：t = V/Q")
        print("4. 工程优化：阀门面积、多级船闸、自动控制")
        print("5. 综合考虑：水力学+结构+运行+经济")
        print("=" * 70)


def main():
    """主函数"""
    print("\n" + "💧" * 35)
    print("第01章 静水力学 - 题目14：船闸工程设计")
    print("💧" * 35 + "\n")
    
    # 题目参数
    L = 150.0       # 闸室长度150m
    B = 20.0        # 闸室宽度20m
    H1 = 20.0       # 上游水位20m
    H2 = 10.0       # 下游水位10m
    A_valve = 2.0   # 阀门面积2m²
    mu = 0.6        # 流量系数
    H_avg = 5.0     # 平均水头差5m
    
    # 创建船闸设计对象
    ship_lock = ShipLockDesign(L=L, B=B, H1=H1, H2=H2, 
                               A_valve=A_valve, mu=mu, H_avg=H_avg)
    
    # 打印结果
    ship_lock.print_results()
    
    # 绘图
    print("\n正在绘制船闸设计分析图...")
    ship_lock.plot_design_analysis()
    
    print("\n✅ 计算完成！")


if __name__ == "__main__":
    main()
