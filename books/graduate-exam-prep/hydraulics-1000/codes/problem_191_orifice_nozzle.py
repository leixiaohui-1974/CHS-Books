"""
《水力学考研1000题详解》配套代码
题目191：孔口管嘴出流

问题描述：
容器侧壁有一圆形薄壁孔口，直径d=0.05m，孔口中心距液面高度H=2.0m。
水的重度γ=9800N/m³，流量系数μ=0.62，收缩系数ε=0.64。
要求：
(1) 计算孔口自由出流的流量Q和流速v
(2) 计算孔口淹没出流时的流量（下游水位差ΔH=1.5m）
(3) 如果改为圆柱形外管嘴（L=3d），计算流量
(4) 如果改为圆锥形收缩管嘴，计算流量
(5) 比较四种出流方式的流量和效率

考点：
1. 孔口自由出流：Q = μ·A·√(2gH)
2. 孔口淹没出流：Q = μ·A·√(2g·ΔH)
3. 管嘴出流：Q = μ_管嘴·A·√(2gH)
4. 收缩系数ε：A_c = ε·A
5. 流速系数φ：v = φ·√(2gH)
6. 流量系数μ = ε·φ

作者: CHS-Books开发团队
日期: 2025-11-10
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Polygon, FancyArrowPatch, Wedge
from matplotlib.patches import FancyBboxPatch

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class OrificeNozzleFlow:
    """孔口管嘴出流分析类"""
    
    def __init__(self, d, H, mu_orifice=0.62, epsilon=0.64, g=9.8):
        """
        初始化
        
        参数:
            d: 孔口直径 (m)
            H: 孔口中心距液面高度 (m)
            mu_orifice: 孔口流量系数
            epsilon: 收缩系数
            g: 重力加速度 (m/s²)
        """
        self.d = d              # 直径 (m)
        self.H = H              # 作用水头 (m)
        self.mu = mu_orifice    # 流量系数
        self.epsilon = epsilon  # 收缩系数
        self.g = g              # 重力加速度 (m/s²)
        
        # 孔口面积
        self.A = np.pi * self.d**2 / 4
        
        # 计算各种出流
        self.calculate_free_orifice()
        self.calculate_submerged_orifice()
        self.calculate_cylindrical_nozzle()
        self.calculate_conical_nozzle()
    
    def calculate_free_orifice(self):
        """计算孔口自由出流"""
        # 理论流速（托里拆利公式）
        self.v_theory = np.sqrt(2 * self.g * self.H)
        
        # 流速系数
        self.phi = self.mu / self.epsilon
        
        # 实际流速
        self.v_orifice = self.phi * self.v_theory
        
        # 收缩断面面积
        self.A_contraction = self.epsilon * self.A
        
        # 流量
        self.Q_orifice = self.mu * self.A * self.v_theory
        
        # 能量损失系数
        self.zeta_orifice = 1 / self.mu**2 - 1
    
    def calculate_submerged_orifice(self, delta_H=1.5):
        """计算孔口淹没出流"""
        self.delta_H = delta_H
        
        # 淹没出流流量
        self.Q_submerged = self.mu * self.A * np.sqrt(2 * self.g * delta_H)
        
        # 与自由出流比较
        self.Q_ratio_submerged = self.Q_submerged / self.Q_orifice
    
    def calculate_cylindrical_nozzle(self, L_ratio=3):
        """计算圆柱形外管嘴出流"""
        # 管嘴长度
        self.L_nozzle = L_ratio * self.d
        
        # 圆柱形外管嘴流量系数（典型值0.82）
        self.mu_cylindrical = 0.82
        
        # 流量
        self.Q_cylindrical = self.mu_cylindrical * self.A * np.sqrt(2 * self.g * self.H)
        
        # 与孔口比较
        self.Q_ratio_cylindrical = self.Q_cylindrical / self.Q_orifice
        
        # 管嘴内部真空度
        # 在收缩断面处产生真空
        self.h_vacuum = self.H * (1 - self.epsilon**2)
    
    def calculate_conical_nozzle(self, alpha=13.5):
        """计算圆锥形收缩管嘴出流"""
        # 锥角（半角）
        self.alpha = alpha  # 度
        
        # 圆锥形收缩管嘴流量系数（典型值0.95-0.98）
        self.mu_conical = 0.97
        
        # 流量
        self.Q_conical = self.mu_conical * self.A * np.sqrt(2 * self.g * self.H)
        
        # 与孔口比较
        self.Q_ratio_conical = self.Q_conical / self.Q_orifice
    
    def print_results(self):
        """打印结果"""
        print("\n" + "="*80)
        print("题目191：孔口管嘴出流")
        print("="*80)
        
        print("\n【已知条件】")
        print(f"孔口直径: d = {self.d} m = {self.d*1000} mm")
        print(f"作用水头: H = {self.H} m")
        print(f"孔口流量系数: μ = {self.mu}")
        print(f"收缩系数: ε = {self.epsilon}")
        print(f"重力加速度: g = {self.g} m/s²")
        print(f"孔口面积: A = πd²/4 = {self.A:.6f} m²")
        
        print("\n【孔口管嘴出流基本概念】")
        print("1. 薄壁孔口自由出流:")
        print("   • 水流从孔口流出形成自由射流")
        print("   • 射流收缩，形成收缩断面")
        print("   • Q = μ·A·√(2gH)")
        print("   • μ = ε·φ（流量系数 = 收缩系数 × 流速系数）")
        
        print("\n2. 孔口淹没出流:")
        print("   • 下游有水淹没孔口")
        print("   • 水头差ΔH = H₁ - H₂")
        print("   • Q = μ·A·√(2g·ΔH)")
        
        print("\n3. 圆柱形外管嘴:")
        print("   • 长度L = (2.5~4)d")
        print("   • 管内形成真空，增大流量")
        print("   • μ ≈ 0.82（比孔口大）")
        
        print("\n4. 圆锥形收缩管嘴:")
        print("   • 锥角α = 13°~14°")
        print("   • 渐缩流道，减小损失")
        print("   • μ ≈ 0.95~0.98（最大）")
        
        print("\n【计算过程】")
        
        # (1) 孔口自由出流
        print("\n(1) 薄壁孔口自由出流")
        
        print("\n    理论流速（托里拆利公式）:")
        print(f"    v_理论 = √(2gH) = √(2×{self.g}×{self.H})")
        print(f"          = {self.v_theory:.3f} m/s")
        
        print(f"\n    流速系数:")
        print(f"    φ = μ/ε = {self.mu}/{self.epsilon} = {self.phi:.4f}")
        
        print(f"\n    实际流速:")
        print(f"    v = φ·√(2gH) = {self.phi:.4f} × {self.v_theory:.3f}")
        print(f"      = {self.v_orifice:.3f} m/s")
        
        print(f"\n    收缩断面面积:")
        print(f"    A_c = ε·A = {self.epsilon} × {self.A:.6f}")
        print(f"        = {self.A_contraction:.6f} m²")
        
        print(f"\n    流量:")
        print(f"    Q = μ·A·√(2gH)")
        print(f"      = {self.mu} × {self.A:.6f} × {self.v_theory:.3f}")
        print(f"      = {self.Q_orifice:.6f} m³/s")
        print(f"      = {self.Q_orifice*1000:.3f} L/s")
        
        print(f"\n    能量损失系数:")
        print(f"    ζ = 1/μ² - 1 = 1/{self.mu}² - 1")
        print(f"      = {self.zeta_orifice:.4f}")
        
        print(f"\n    水头损失:")
        h_loss = self.zeta_orifice * self.v_orifice**2 / (2*self.g)
        print(f"    h_f = ζ·v²/(2g) = {self.zeta_orifice:.4f} × {self.v_orifice:.3f}²/(2×{self.g})")
        print(f"        = {h_loss:.4f} m")
        
        # (2) 孔口淹没出流
        print("\n(2) 薄壁孔口淹没出流")
        print(f"    下游水位差: ΔH = {self.delta_H} m")
        
        print(f"\n    流量:")
        print(f"    Q = μ·A·√(2g·ΔH)")
        print(f"      = {self.mu} × {self.A:.6f} × √(2×{self.g}×{self.delta_H})")
        print(f"      = {self.Q_submerged:.6f} m³/s")
        print(f"      = {self.Q_submerged*1000:.3f} L/s")
        
        print(f"\n    与自由出流比较:")
        print(f"    Q_淹没/Q_自由 = {self.Q_ratio_submerged:.4f}")
        print(f"    流量减少: {(1-self.Q_ratio_submerged)*100:.1f}%")
        
        # (3) 圆柱形外管嘴
        print("\n(3) 圆柱形外管嘴出流")
        print(f"    管嘴长度: L = 3d = 3 × {self.d} = {self.L_nozzle:.3f} m")
        print(f"    流量系数: μ = {self.mu_cylindrical}")
        
        print(f"\n    流量:")
        print(f"    Q = μ·A·√(2gH)")
        print(f"      = {self.mu_cylindrical} × {self.A:.6f} × {self.v_theory:.3f}")
        print(f"      = {self.Q_cylindrical:.6f} m³/s")
        print(f"      = {self.Q_cylindrical*1000:.3f} L/s")
        
        print(f"\n    与孔口比较:")
        print(f"    Q_管嘴/Q_孔口 = {self.Q_ratio_cylindrical:.4f}")
        print(f"    流量增加: {(self.Q_ratio_cylindrical-1)*100:.1f}%")
        
        print(f"\n    管内真空度:")
        print(f"    h_真空 = H(1-ε²) = {self.H} × (1-{self.epsilon}²)")
        print(f"          = {self.h_vacuum:.3f} m水柱")
        print(f"          ≈ {self.h_vacuum*9.8:.1f} kPa")
        
        print("\n    工作原理:")
        print("    • 水流进入管嘴后收缩")
        print("    • 收缩断面与管壁间形成真空")
        print("    • 真空吸力增大流量")
        print("    • 流量系数μ从0.62提高到0.82")
        
        # (4) 圆锥形收缩管嘴
        print("\n(4) 圆锥形收缩管嘴出流")
        print(f"    锥角（半角）: α = {self.alpha}°")
        print(f"    流量系数: μ = {self.mu_conical}")
        
        print(f"\n    流量:")
        print(f"    Q = μ·A·√(2gH)")
        print(f"      = {self.mu_conical} × {self.A:.6f} × {self.v_theory:.3f}")
        print(f"      = {self.Q_conical:.6f} m³/s")
        print(f"      = {self.Q_conical*1000:.3f} L/s")
        
        print(f"\n    与孔口比较:")
        print(f"    Q_圆锥/Q_孔口 = {self.Q_ratio_conical:.4f}")
        print(f"    流量增加: {(self.Q_ratio_conical-1)*100:.1f}%")
        
        print("\n    优点:")
        print("    • 渐缩流道，流线光滑")
        print("    • 能量损失最小")
        print("    • 流量系数最大（0.95~0.98）")
        print("    • 广泛用于流量测量")
        
        # (5) 综合比较
        print("\n(5) 四种出流方式比较")
        print("┌" + "─"*78 + "┐")
        print("│ 出流方式       │ 流量系数μ │  流量(L/s)  │ 相对流量 │    特点    │")
        print("├" + "─"*78 + "┤")
        
        print(f"│ 孔口自由出流   │   {self.mu:.2f}    │  {self.Q_orifice*1000:10.3f} │   1.00   │   基准     │")
        print(f"│ 孔口淹没出流   │   {self.mu:.2f}    │  {self.Q_submerged*1000:10.3f} │  {self.Q_ratio_submerged:6.2f}  │  流量减小  │")
        print(f"│ 圆柱形管嘴     │   {self.mu_cylindrical:.2f}    │  {self.Q_cylindrical*1000:10.3f} │  {self.Q_ratio_cylindrical:6.2f}  │ 真空增流   │")
        print(f"│ 圆锥形管嘴     │   {self.mu_conical:.2f}    │  {self.Q_conical*1000:10.3f} │  {self.Q_ratio_conical:6.2f}  │  损失最小  │")
        
        print("└" + "─"*78 + "┘")
        
        print("\n【选用原则】")
        print("1. 孔口自由出流:")
        print("   • 结构简单，成本低")
        print("   • 流量较小")
        print("   • 适用于一般泄水")
        
        print("\n2. 孔口淹没出流:")
        print("   • 下游有水位")
        print("   • 流量取决于水位差")
        print("   • 适用于水位控制")
        
        print("\n3. 圆柱形外管嘴:")
        print("   • 流量比孔口大30%")
        print("   • 管内有真空")
        print("   • 适用于需要增大流量")
        print("   • 注意真空度限制")
        
        print("\n4. 圆锥形收缩管嘴:")
        print("   • 流量最大（比孔口大56%）")
        print("   • 能量损失最小")
        print("   • 适用于流量测量、精确控制")
        print("   • 成本较高")
    
    def visualize(self):
        """可视化"""
        fig = plt.figure(figsize=(14, 11))
        
        # 子图1：孔口自由出流
        ax1 = plt.subplot(2, 2, 1)
        self._plot_free_orifice(ax1)
        
        # 子图2：圆柱形管嘴
        ax2 = plt.subplot(2, 2, 2)
        self._plot_cylindrical_nozzle(ax2)
        
        # 子图3：圆锥形管嘴
        ax3 = plt.subplot(2, 2, 3)
        self._plot_conical_nozzle(ax3)
        
        # 子图4：流量对比
        ax4 = plt.subplot(2, 2, 4)
        self._plot_comparison(ax4)
        
        plt.tight_layout()
        return fig
    
    def _plot_free_orifice(self, ax):
        """绘制孔口自由出流示意图"""
        # 容器
        tank_width = 1.0
        tank_height = self.H + 0.5
        
        # 容器侧壁
        ax.plot([0, 0], [0, tank_height], 'k-', linewidth=3)
        ax.plot([tank_width, tank_width], [0, tank_height], 'k-', linewidth=3)
        ax.plot([0, tank_width], [tank_height, tank_height], 'k-', linewidth=3)
        
        # 水体
        water = Rectangle((0, 0), tank_width, tank_height, 
                         facecolor='lightblue', edgecolor='blue',
                         linewidth=2, alpha=0.5)
        ax.add_patch(water)
        
        # 孔口位置
        orifice_y = self.H
        orifice_size = 0.08
        
        # 孔口
        orifice = Rectangle((tank_width, orifice_y-orifice_size/2), 
                           0.05, orifice_size,
                           facecolor='white', edgecolor='black', linewidth=2)
        ax.add_patch(orifice)
        
        # 射流（收缩）
        jet_x = np.linspace(tank_width+0.05, tank_width+0.5, 50)
        
        # 上边界（抛物线）
        jet_top = orifice_y + orifice_size/2 - (jet_x - tank_width - 0.05) * 0.1
        # 下边界
        jet_bottom = orifice_y - orifice_size/2 + (jet_x - tank_width - 0.05) * 0.1
        
        # 收缩到收缩断面
        contraction_x = tank_width + 0.15
        contraction_width = orifice_size * self.epsilon
        
        # 修正射流边界
        for i, x in enumerate(jet_x):
            if x < contraction_x:
                ratio = (x - tank_width - 0.05) / (contraction_x - tank_width - 0.05)
                jet_top[i] = orifice_y + orifice_size/2 * (1 - ratio + ratio*self.epsilon)
                jet_bottom[i] = orifice_y - orifice_size/2 * (1 - ratio + ratio*self.epsilon)
            else:
                jet_top[i] = orifice_y + contraction_width/2
                jet_bottom[i] = orifice_y - contraction_width/2
        
        # 绘制射流
        ax.plot(jet_x, jet_top, 'b-', linewidth=2)
        ax.plot(jet_x, jet_bottom, 'b-', linewidth=2)
        ax.fill_between(jet_x, jet_bottom, jet_top, color='lightblue', alpha=0.6)
        
        # 收缩断面标注
        ax.plot([contraction_x, contraction_x], 
               [orifice_y-contraction_width/2, orifice_y+contraction_width/2],
               'r--', linewidth=2)
        ax.text(contraction_x, orifice_y+contraction_width/2+0.1, 
               '收缩断面', fontsize=9, ha='center', color='red')
        
        # H标注
        ax.annotate('', xy=(tank_width+0.7, tank_height), 
                   xytext=(tank_width+0.7, orifice_y),
                   arrowprops=dict(arrowstyle='<->', lw=2, color='green'))
        ax.text(tank_width+0.8, (tank_height+orifice_y)/2, 
               f'H={self.H}m', fontsize=11, rotation=90, 
               va='center', color='green', weight='bold')
        
        # 流量标注
        ax.text(tank_width+0.25, orifice_y-0.3, 
               f'Q={self.Q_orifice*1000:.2f}L/s\nμ={self.mu}',
               fontsize=10, ha='center',
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        # 收缩系数标注
        ax.text(contraction_x+0.05, orifice_y-contraction_width/2-0.15,
               f'ε={self.epsilon}', fontsize=9, color='red')
        
        ax.set_xlim(-0.1, tank_width+1.0)
        ax.set_ylim(-0.2, tank_height+0.3)
        ax.set_aspect('equal')
        ax.set_xlabel('x (m)', fontsize=12)
        ax.set_ylabel('y (m)', fontsize=12)
        ax.set_title('薄壁孔口自由出流', fontsize=13, weight='bold')
        ax.grid(True, alpha=0.3)
    
    def _plot_cylindrical_nozzle(self, ax):
        """绘制圆柱形管嘴示意图"""
        # 容器
        tank_width = 1.0
        tank_height = self.H + 0.5
        
        # 容器侧壁
        ax.plot([0, 0], [0, tank_height], 'k-', linewidth=3)
        ax.plot([tank_width, tank_width], [0, tank_height], 'k-', linewidth=3)
        ax.plot([0, tank_width], [tank_height, tank_height], 'k-', linewidth=3)
        
        # 水体
        water = Rectangle((0, 0), tank_width, tank_height, 
                         facecolor='lightblue', edgecolor='blue',
                         linewidth=2, alpha=0.5)
        ax.add_patch(water)
        
        # 管嘴位置
        nozzle_y = self.H
        nozzle_diameter = 0.08
        nozzle_length = 0.25
        
        # 管嘴
        nozzle_wall_thickness = 0.02
        # 上壁
        nozzle_top = Rectangle((tank_width, nozzle_y+nozzle_diameter/2),
                              nozzle_length, nozzle_wall_thickness,
                              facecolor='gray', edgecolor='black', linewidth=2)
        ax.add_patch(nozzle_top)
        
        # 下壁
        nozzle_bottom = Rectangle((tank_width, nozzle_y-nozzle_diameter/2-nozzle_wall_thickness),
                                 nozzle_length, nozzle_wall_thickness,
                                 facecolor='gray', edgecolor='black', linewidth=2)
        ax.add_patch(nozzle_bottom)
        
        # 管嘴内水流
        nozzle_water = Rectangle((tank_width, nozzle_y-nozzle_diameter/2),
                                nozzle_length, nozzle_diameter,
                                facecolor='lightgreen', edgecolor='green',
                                linewidth=1.5, alpha=0.6)
        ax.add_patch(nozzle_water)
        
        # 收缩断面（真空区）
        contraction_x = tank_width + 0.08
        contraction_width = nozzle_diameter * self.epsilon
        
        # 真空区（环形）
        vacuum_top = Polygon([
            [tank_width, nozzle_y+nozzle_diameter/2],
            [contraction_x, nozzle_y+contraction_width/2],
            [contraction_x, nozzle_y+nozzle_diameter/2],
            [tank_width, nozzle_y+nozzle_diameter/2]
        ], facecolor='lightyellow', edgecolor='orange', 
        linewidth=1.5, linestyle='--', alpha=0.7)
        ax.add_patch(vacuum_top)
        
        vacuum_bottom = Polygon([
            [tank_width, nozzle_y-nozzle_diameter/2],
            [contraction_x, nozzle_y-contraction_width/2],
            [contraction_x, nozzle_y-nozzle_diameter/2],
            [tank_width, nozzle_y-nozzle_diameter/2]
        ], facecolor='lightyellow', edgecolor='orange',
        linewidth=1.5, linestyle='--', alpha=0.7)
        ax.add_patch(vacuum_bottom)
        
        # 真空标注
        ax.text(tank_width+0.05, nozzle_y+nozzle_diameter/2+0.05,
               '真空', fontsize=9, color='orange', weight='bold')
        
        # 出口射流
        jet_x = np.linspace(tank_width+nozzle_length, tank_width+nozzle_length+0.3, 30)
        jet_top = np.ones_like(jet_x) * (nozzle_y + nozzle_diameter/2)
        jet_bottom = np.ones_like(jet_x) * (nozzle_y - nozzle_diameter/2)
        
        ax.plot(jet_x, jet_top, 'g-', linewidth=2)
        ax.plot(jet_x, jet_bottom, 'g-', linewidth=2)
        ax.fill_between(jet_x, jet_bottom, jet_top, color='lightgreen', alpha=0.5)
        
        # H标注
        ax.annotate('', xy=(tank_width+0.65, tank_height), 
                   xytext=(tank_width+0.65, nozzle_y),
                   arrowprops=dict(arrowstyle='<->', lw=2, color='green'))
        ax.text(tank_width+0.75, (tank_height+nozzle_y)/2, 
               f'H={self.H}m', fontsize=11, rotation=90, 
               va='center', color='green', weight='bold')
        
        # 管嘴长度标注
        ax.annotate('', xy=(tank_width, nozzle_y-nozzle_diameter/2-0.15), 
                   xytext=(tank_width+nozzle_length, nozzle_y-nozzle_diameter/2-0.15),
                   arrowprops=dict(arrowstyle='<->', lw=1.5, color='purple'))
        ax.text(tank_width+nozzle_length/2, nozzle_y-nozzle_diameter/2-0.25,
               f'L=3d', fontsize=9, ha='center', color='purple')
        
        # 流量标注
        ax.text(tank_width+nozzle_length+0.15, nozzle_y+0.3, 
               f'Q={self.Q_cylindrical*1000:.2f}L/s\nμ={self.mu_cylindrical}',
               fontsize=10, ha='center',
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        ax.set_xlim(-0.1, tank_width+1.0)
        ax.set_ylim(-0.3, tank_height+0.3)
        ax.set_aspect('equal')
        ax.set_xlabel('x (m)', fontsize=12)
        ax.set_ylabel('y (m)', fontsize=12)
        ax.set_title('圆柱形外管嘴出流', fontsize=13, weight='bold')
        ax.grid(True, alpha=0.3)
    
    def _plot_conical_nozzle(self, ax):
        """绘制圆锥形管嘴示意图"""
        # 容器
        tank_width = 1.0
        tank_height = self.H + 0.5
        
        # 容器侧壁
        ax.plot([0, 0], [0, tank_height], 'k-', linewidth=3)
        ax.plot([tank_width, tank_width], [0, tank_height], 'k-', linewidth=3)
        ax.plot([0, tank_width], [tank_height, tank_height], 'k-', linewidth=3)
        
        # 水体
        water = Rectangle((0, 0), tank_width, tank_height, 
                         facecolor='lightblue', edgecolor='blue',
                         linewidth=2, alpha=0.5)
        ax.add_patch(water)
        
        # 管嘴位置
        nozzle_y = self.H
        nozzle_inlet_d = 0.12
        nozzle_outlet_d = 0.08
        nozzle_length = 0.25
        
        # 圆锥形管嘴壁（梯形）
        # 上壁
        nozzle_top_points = [
            [tank_width, nozzle_y + nozzle_inlet_d/2],
            [tank_width + nozzle_length, nozzle_y + nozzle_outlet_d/2],
            [tank_width + nozzle_length, nozzle_y + nozzle_outlet_d/2 + 0.02],
            [tank_width, nozzle_y + nozzle_inlet_d/2 + 0.02]
        ]
        nozzle_top_wall = Polygon(nozzle_top_points, facecolor='gray',
                                 edgecolor='black', linewidth=2)
        ax.add_patch(nozzle_top_wall)
        
        # 下壁
        nozzle_bottom_points = [
            [tank_width, nozzle_y - nozzle_inlet_d/2],
            [tank_width + nozzle_length, nozzle_y - nozzle_outlet_d/2],
            [tank_width + nozzle_length, nozzle_y - nozzle_outlet_d/2 - 0.02],
            [tank_width, nozzle_y - nozzle_inlet_d/2 - 0.02]
        ]
        nozzle_bottom_wall = Polygon(nozzle_bottom_points, facecolor='gray',
                                    edgecolor='black', linewidth=2)
        ax.add_patch(nozzle_bottom_wall)
        
        # 管嘴内水流（梯形）
        nozzle_water_points = [
            [tank_width, nozzle_y + nozzle_inlet_d/2],
            [tank_width + nozzle_length, nozzle_y + nozzle_outlet_d/2],
            [tank_width + nozzle_length, nozzle_y - nozzle_outlet_d/2],
            [tank_width, nozzle_y - nozzle_inlet_d/2]
        ]
        nozzle_water = Polygon(nozzle_water_points, facecolor='lightcyan',
                              edgecolor='cyan', linewidth=1.5, alpha=0.7)
        ax.add_patch(nozzle_water)
        
        # 出口射流
        jet_x = np.linspace(tank_width+nozzle_length, tank_width+nozzle_length+0.3, 30)
        jet_top = np.ones_like(jet_x) * (nozzle_y + nozzle_outlet_d/2)
        jet_bottom = np.ones_like(jet_x) * (nozzle_y - nozzle_outlet_d/2)
        
        ax.plot(jet_x, jet_top, 'c-', linewidth=2)
        ax.plot(jet_x, jet_bottom, 'c-', linewidth=2)
        ax.fill_between(jet_x, jet_bottom, jet_top, color='lightcyan', alpha=0.5)
        
        # H标注
        ax.annotate('', xy=(tank_width+0.65, tank_height), 
                   xytext=(tank_width+0.65, nozzle_y),
                   arrowprops=dict(arrowstyle='<->', lw=2, color='green'))
        ax.text(tank_width+0.75, (tank_height+nozzle_y)/2, 
               f'H={self.H}m', fontsize=11, rotation=90, 
               va='center', color='green', weight='bold')
        
        # 锥角标注
        ax.text(tank_width+nozzle_length/2, nozzle_y+nozzle_outlet_d/2+0.1,
               f'α={self.alpha}°', fontsize=9, ha='center', color='red')
        
        # 流量标注
        ax.text(tank_width+nozzle_length+0.15, nozzle_y+0.3, 
               f'Q={self.Q_conical*1000:.2f}L/s\nμ={self.mu_conical}',
               fontsize=10, ha='center',
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        # 流线标注
        ax.text(tank_width+nozzle_length/2, nozzle_y,
               '流线光滑\n损失最小', fontsize=9, ha='center',
               bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))
        
        ax.set_xlim(-0.1, tank_width+1.0)
        ax.set_ylim(-0.3, tank_height+0.3)
        ax.set_aspect('equal')
        ax.set_xlabel('x (m)', fontsize=12)
        ax.set_ylabel('y (m)', fontsize=12)
        ax.set_title('圆锥形收缩管嘴出流', fontsize=13, weight='bold')
        ax.grid(True, alpha=0.3)
    
    def _plot_comparison(self, ax):
        """绘制流量对比图"""
        # 数据
        labels = ['孔口\n自由', '孔口\n淹没', '圆柱\n管嘴', '圆锥\n管嘴']
        Q_values = [
            self.Q_orifice * 1000,
            self.Q_submerged * 1000,
            self.Q_cylindrical * 1000,
            self.Q_conical * 1000
        ]
        mu_values = [self.mu, self.mu, self.mu_cylindrical, self.mu_conical]
        colors = ['#FF6B6B', '#FFA07A', '#4ECDC4', '#45B7D1']
        
        x = np.arange(len(labels))
        width = 0.4
        
        # 流量柱状图
        bars1 = ax.bar(x - width/2, Q_values, width, label='流量(L/s)',
                      color=colors, edgecolor='black', linewidth=2, alpha=0.8)
        
        # 流量系数柱状图（右Y轴）
        ax2 = ax.twinx()
        bars2 = ax2.bar(x + width/2, mu_values, width, label='流量系数μ',
                       color='lightgreen', edgecolor='green', linewidth=2, alpha=0.6)
        
        # 标注数值
        for bar, q in zip(bars1, Q_values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height + 0.05,
                   f'{q:.2f}',
                   ha='center', va='bottom', fontsize=10, weight='bold')
        
        for bar, mu in zip(bars2, mu_values):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2, height + 0.01,
                    f'{mu:.2f}',
                    ha='center', va='bottom', fontsize=9, color='green')
        
        # 相对值标注
        for i, q in enumerate(Q_values[1:], 1):
            ratio = (q / Q_values[0] - 1) * 100
            if ratio >= 0:
                text = f'+{ratio:.0f}%'
                color = 'green'
            else:
                text = f'{ratio:.0f}%'
                color = 'red'
            ax.text(i, q/2, text, ha='center', fontsize=11,
                   color=color, weight='bold')
        
        ax.set_ylabel('流量 Q (L/s)', fontsize=12)
        ax2.set_ylabel('流量系数 μ', fontsize=12, color='green')
        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=11)
        ax.set_title('四种出流方式对比', fontsize=13, weight='bold')
        ax.legend(loc='upper left', fontsize=10)
        ax2.legend(loc='upper right', fontsize=10)
        ax.grid(True, axis='y', alpha=0.3)
        
        # 结论文字
        ax.text(0.5, 0.02, 
               '圆锥形管嘴流量最大，圆柱形管嘴次之\n孔口淹没出流流量最小',
               transform=ax.transAxes, fontsize=10, ha='center',
               bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))


def test_problem_191():
    """测试题目191"""
    # 已知条件
    d = 0.05      # 孔口直径 (m)
    H = 2.0       # 作用水头 (m)
    mu = 0.62     # 流量系数
    epsilon = 0.64  # 收缩系数
    g = 9.8       # 重力加速度 (m/s²)
    
    # 创建分析对象
    orifice = OrificeNozzleFlow(d, H, mu, epsilon, g)
    
    # 打印结果
    orifice.print_results()
    
    print("\n【最终答案】")
    print("="*80)
    print(f"(1) 孔口自由出流:")
    print(f"    流量: Q = {orifice.Q_orifice*1000:.3f} L/s")
    print(f"    流速: v = {orifice.v_orifice:.3f} m/s")
    print(f"(2) 孔口淹没出流:")
    print(f"    流量: Q = {orifice.Q_submerged*1000:.3f} L/s（减少{(1-orifice.Q_ratio_submerged)*100:.1f}%）")
    print(f"(3) 圆柱形管嘴:")
    print(f"    流量: Q = {orifice.Q_cylindrical*1000:.3f} L/s（增加{(orifice.Q_ratio_cylindrical-1)*100:.1f}%）")
    print(f"(4) 圆锥形管嘴:")
    print(f"    流量: Q = {orifice.Q_conical*1000:.3f} L/s（增加{(orifice.Q_ratio_conical-1)*100:.1f}%）")
    print("(5) 综合评价:")
    print("    圆锥形管嘴流量最大（μ=0.97），损失最小")
    print("    圆柱形管嘴次之（μ=0.82），利用真空增流")
    print("    孔口结构简单（μ=0.62），成本最低")
    print("="*80)
    
    # 可视化
    print("\n生成可视化图表...")
    fig = orifice.visualize()
    plt.savefig('/workspace/books/graduate-exam-prep/hydraulics-1000/codes/problem_191_result.png',
                dpi=150, bbox_inches='tight')
    print("图片已保存: problem_191_result.png")
    
    # 验证
    assert orifice.Q_orifice > 0, "流量必须为正"
    assert orifice.Q_cylindrical > orifice.Q_orifice, "管嘴流量应大于孔口"
    assert orifice.Q_conical > orifice.Q_cylindrical, "圆锥管嘴流量应最大"
    
    print("\n✓ 所有测试通过！")
    print("\n【核心要点】")
    print("孔口管嘴出流是水动力学的重要应用！")
    print("• 孔口: Q = μ·A·√(2gH), μ≈0.62")
    print("• 圆柱管嘴: μ≈0.82（真空增流30%）")
    print("• 圆锥管嘴: μ≈0.97（损失最小，增流56%）")
    print("• 应用: 流量控制、测量、泄水设施")


if __name__ == "__main__":
    test_problem_191()
