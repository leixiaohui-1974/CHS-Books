#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第02章 流体动力学基础 - 题目9：能量损失计算

题目描述：
水平管道，直径d=0.2m，长度L=100m，粗糙度n=0.012。
断面1：流量Q=0.08m³/s，压强p1=250kPa（表压）
断面2：压强p2=180kPa（表压）
求：
(1) 平均流速v
(2) 沿程水头损失hf
(3) 局部水头损失hm（假设有一个阀门，ζ=5.0）
(4) 总水头损失h_loss

知识点：
- 达西-魏斯巴赫公式（沿程损失）
- 局部损失系数法
- 能量方程与水头损失

作者：CHS-Books Team
日期：2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class EnergyLoss:
    """能量损失计算类"""
    
    def __init__(self, d: float, L: float, Q: float, p1: float, p2: float,
                 n: float = 0.012, zeta: float = 5.0, rho: float = 1000.0, g: float = 9.81):
        """
        初始化参数
        
        Parameters:
        -----------
        d : float
            管道直径 (m)
        L : float
            管道长度 (m)
        Q : float
            流量 (m³/s)
        p1 : float
            断面1压强 (Pa)
        p2 : float
            断面2压强 (Pa)
        n : float
            粗糙度系数（曼宁系数）
        zeta : float
            局部损失系数
        rho : float
            密度 (kg/m³)
        g : float
            重力加速度 (m/s²)
        """
        self.d = d
        self.L = L
        self.Q = Q
        self.p1 = p1
        self.p2 = p2
        self.n = n
        self.zeta = zeta
        self.rho = rho
        self.g = g
        
        # 计算断面面积
        self.A = np.pi * d**2 / 4
    
    def velocity(self) -> float:
        """
        计算平均流速
        
        Returns:
        --------
        float : 平均流速 (m/s)
        """
        return self.Q / self.A
    
    def reynolds_number(self) -> float:
        """
        计算雷诺数
        
        Returns:
        --------
        float : 雷诺数
        """
        v = self.velocity()
        nu = 1e-6  # 水的运动粘度，20℃时约为1×10^-6 m²/s
        return v * self.d / nu
    
    def friction_factor_darcy(self) -> float:
        """
        计算达西摩擦系数（使用曼宁公式）
        
        曼宁公式：v = (1/n) × R^(2/3) × J^(1/2)
        达西公式：hf = λ × (L/d) × v²/(2g)
        
        转换关系：λ ≈ 8gn²/R^(1/3)
        
        Returns:
        --------
        float : 达西摩擦系数
        """
        R = self.d / 4  # 水力半径，圆管R=d/4
        lamb = 8 * self.g * self.n**2 / R**(1/3)
        return lamb
    
    def head_loss_friction(self) -> float:
        """
        计算沿程水头损失（达西-魏斯巴赫公式）
        
        hf = λ × (L/d) × v²/(2g)
        
        Returns:
        --------
        float : 沿程水头损失 (m)
        """
        v = self.velocity()
        lamb = self.friction_factor_darcy()
        hf = lamb * (self.L / self.d) * v**2 / (2 * self.g)
        return hf
    
    def head_loss_local(self) -> float:
        """
        计算局部水头损失
        
        hm = ζ × v²/(2g)
        
        Returns:
        --------
        float : 局部水头损失 (m)
        """
        v = self.velocity()
        hm = self.zeta * v**2 / (2 * self.g)
        return hm
    
    def total_head_loss(self) -> float:
        """
        计算总水头损失
        
        Returns:
        --------
        float : 总水头损失 (m)
        """
        hf = self.head_loss_friction()
        hm = self.head_loss_local()
        return hf + hm
    
    def verify_by_pressure_difference(self) -> tuple:
        """
        通过压强差验证水头损失
        
        对于水平管道：
        h_loss = (p1 - p2) / (ρg)
        
        Returns:
        --------
        tuple : (h_loss_calculated, h_loss_from_pressure, error)
        """
        h_loss_calc = self.total_head_loss()
        h_loss_press = (self.p1 - self.p2) / (self.rho * self.g)
        error = abs(h_loss_calc - h_loss_press) / h_loss_press * 100
        return h_loss_calc, h_loss_press, error
    
    def plot_energy_line(self):
        """绘制能量线和测压管水头线"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # 图1：管道示意图和能量线
        ax1 = axes[0, 0]
        
        # 管道
        x = [0, self.L]
        y_top = [self.d/2, self.d/2]
        y_bottom = [-self.d/2, -self.d/2]
        ax1.fill_between(x, y_bottom, y_top, color='lightgray', alpha=0.7, label='管道')
        ax1.plot(x, y_top, 'k-', linewidth=2)
        ax1.plot(x, y_bottom, 'k-', linewidth=2)
        
        # 管道中心线
        ax1.plot(x, [0, 0], 'k--', linewidth=1.5, label='管道中心线')
        
        # 断面标注
        ax1.plot([0, 0], y_bottom[0:1] + y_top[0:1], 'b-', linewidth=3, label='断面1')
        ax1.plot([self.L, self.L], y_bottom[-1:] + y_top[-1:], 'r-', linewidth=3, label='断面2')
        
        # 能量线
        v = self.velocity()
        H1 = self.p1/(self.rho*self.g) + v**2/(2*self.g)
        H2 = self.p2/(self.rho*self.g) + v**2/(2*self.g)
        
        # 沿程损失线性分布
        hf = self.head_loss_friction()
        hm = self.head_loss_local()
        
        # 假设阀门在中间
        x_valve = self.L / 2
        
        x_energy = [0, x_valve - 1, x_valve, self.L]
        H_energy = [H1, H1 - hf/2, H1 - hf/2 - hm, H2]
        
        # 绘制能量线
        ax1.plot(x_energy, H_energy, 'g-', linewidth=3, marker='o', 
                markersize=8, label='能量线（总水头线）')
        
        # 测压管水头线（去掉流速水头）
        Hp1 = self.p1/(self.rho*self.g)
        Hp2 = self.p2/(self.rho*self.g)
        
        x_pressure = [0, x_valve - 1, x_valve, self.L]
        H_pressure = [Hp1, Hp1 - hf/2, Hp1 - hf/2 - hm, Hp2]
        
        ax1.plot(x_pressure, H_pressure, 'b-', linewidth=3, marker='s',
                markersize=8, label='测压管水头线')
        
        # 标注水头损失
        ax1.annotate('', xy=(0, H1), xytext=(self.L, H2),
                    arrowprops=dict(arrowstyle='<->', color='red', lw=2))
        ax1.text(self.L/2, (H1+H2)/2 + 1, f'总损失={hf+hm:.2f}m',
                fontsize=11, color='red', fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        # 标注沿程损失和局部损失
        ax1.text(self.L/4, H1 - hf/4, f'沿程损失\nhf={hf:.2f}m',
                fontsize=9, color='blue', fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
        
        ax1.text(x_valve + 5, H1 - hf/2 - hm/2, f'局部损失\nhm={hm:.2f}m',
                fontsize=9, color='orange', fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
        
        ax1.set_xlim(-5, self.L + 10)
        ax1.set_ylim(-2, max(H1, Hp1) + 3)
        ax1.set_xlabel('沿程位置 (m)', fontsize=11, fontweight='bold')
        ax1.set_ylabel('水头 (m)', fontsize=11, fontweight='bold')
        ax1.set_title('能量线和测压管水头线', fontsize=13, fontweight='bold')
        ax1.legend(fontsize=9, loc='upper right')
        ax1.grid(True, alpha=0.3)
        
        # 图2：水头损失组成
        ax2 = axes[0, 1]
        
        losses = ['沿程损失\nhf', '局部损失\nhm', '总损失\nh_total']
        values = [hf, hm, hf + hm]
        colors = ['lightblue', 'lightcoral', 'lightgreen']
        
        bars = ax2.bar(losses, values, color=colors, edgecolor='black', 
                      linewidth=2, alpha=0.8)
        
        # 标注数值
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2, height + max(values)*0.03,
                    f'{val:.2f}m', ha='center', fontsize=11, fontweight='bold')
        
        ax2.set_ylabel('水头损失 (m)', fontsize=11, fontweight='bold')
        ax2.set_title('水头损失组成', fontsize=13, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='y')
        
        # 标注比例
        ax2.text(1, max(values) * 0.6,
                f'沿程：{hf/(hf+hm)*100:.1f}%\n局部：{hm/(hf+hm)*100:.1f}%',
                ha='center', fontsize=10, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        # 图3：沿程水头损失分布
        ax3 = axes[1, 0]
        
        x_dist = np.linspace(0, self.L, 100)
        hf_dist = hf * x_dist / self.L
        
        ax3.plot(x_dist, hf_dist, 'b-', linewidth=2.5, label='沿程水头损失累积')
        ax3.fill_between(x_dist, 0, hf_dist, color='lightblue', alpha=0.5)
        
        # 标注关键点
        points_x = [0, self.L/4, self.L/2, 3*self.L/4, self.L]
        points_y = [0, hf/4, hf/2, 3*hf/4, hf]
        ax3.plot(points_x, points_y, 'ro', markersize=8)
        
        for x, y in zip(points_x, points_y):
            ax3.text(x, y + hf*0.05, f'{y:.2f}m', ha='center', 
                    fontsize=9, fontweight='bold')
        
        ax3.set_xlabel('沿程位置 (m)', fontsize=11, fontweight='bold')
        ax3.set_ylabel('累积水头损失 (m)', fontsize=11, fontweight='bold')
        ax3.set_title('沿程水头损失分布', fontsize=13, fontweight='bold')
        ax3.legend(fontsize=10)
        ax3.grid(True, alpha=0.3)
        
        # 标注水力坡度
        J = hf / self.L
        ax3.text(self.L/2, hf * 0.7,
                f'水力坡度 J = hf/L\n= {hf:.2f}/{self.L}\n= {J:.6f}',
                ha='center', fontsize=10, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        # 图4：压强变化
        ax4 = axes[1, 1]
        
        sections = ['断面1', '断面2']
        pressures = [self.p1/1000, self.p2/1000]
        pressure_heads = [Hp1, Hp2]
        
        x_pos = np.arange(len(sections))
        width = 0.35
        
        bars1 = ax4.bar(x_pos - width/2, pressures, width, label='压强 (kPa)',
                       color='lightblue', edgecolor='blue', linewidth=2)
        ax4_twin = ax4.twinx()
        bars2 = ax4_twin.bar(x_pos + width/2, pressure_heads, width, 
                            label='压强水头 (m)',
                            color='lightgreen', edgecolor='green', linewidth=2)
        
        # 标注数值
        for bar, val in zip(bars1, pressures):
            ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10,
                    f'{val:.0f}kPa', ha='center', fontsize=10, fontweight='bold')
        
        for bar, val in zip(bars2, pressure_heads):
            ax4_twin.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(pressure_heads)*0.03,
                         f'{val:.2f}m', ha='center', fontsize=10, fontweight='bold')
        
        ax4.set_xlabel('断面', fontsize=11, fontweight='bold')
        ax4.set_ylabel('压强 (kPa)', fontsize=11, fontweight='bold', color='blue')
        ax4_twin.set_ylabel('压强水头 (m)', fontsize=11, fontweight='bold', color='green')
        ax4.set_title('压强变化', fontsize=13, fontweight='bold')
        ax4.set_xticks(x_pos)
        ax4.set_xticklabels(sections, fontsize=10)
        ax4.tick_params(axis='y', labelcolor='blue')
        ax4_twin.tick_params(axis='y', labelcolor='green')
        ax4.grid(True, alpha=0.3, axis='y')
        
        # 标注压强降
        delta_p = self.p1 - self.p2
        ax4.text(0.5, max(pressures) * 0.7,
                f'Δp = {delta_p/1000:.0f}kPa\nΔH = {Hp1-Hp2:.2f}m',
                ha='center', fontsize=10, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        plt.tight_layout()
        plt.show()
    
    def print_results(self):
        """打印计算结果"""
        print("=" * 70)
        print("能量损失计算 - 水平管道")
        print("=" * 70)
        
        print(f"\n输入参数：")
        print(f"  管道：d={self.d}m, L={self.L}m, n={self.n}")
        print(f"  流量：Q={self.Q}m³/s")
        print(f"  断面1：p1={self.p1/1000:.0f}kPa")
        print(f"  断面2：p2={self.p2/1000:.0f}kPa")
        print(f"  局部损失系数：ζ={self.zeta}")
        
        # (1) 流速
        v = self.velocity()
        print(f"\n(1) 平均流速：")
        print(f"  A = πd²/4 = π × {self.d}² / 4 = {self.A:.4f} m²")
        print(f"  v = Q/A = {self.Q} / {self.A:.4f} = {v:.2f} m/s")
        
        # 雷诺数
        Re = self.reynolds_number()
        print(f"\n  雷诺数：Re = vd/ν = {v:.2f} × {self.d} / 1e-6 = {Re:.0f}")
        if Re > 4000:
            print(f"  判断：Re > 4000，为紊流")
        elif Re < 2000:
            print(f"  判断：Re < 2000，为层流")
        else:
            print(f"  判断：2000 < Re < 4000，为过渡流")
        
        # (2) 沿程损失
        lamb = self.friction_factor_darcy()
        hf = self.head_loss_friction()
        print(f"\n(2) 沿程水头损失：")
        print(f"  摩擦系数：λ = 8gn²/R^(1/3)")
        R = self.d / 4
        print(f"            R = d/4 = {self.d}/4 = {R:.3f} m")
        print(f"            λ = 8 × {self.g} × {self.n}² / {R}^(1/3)")
        print(f"              = {lamb:.4f}")
        
        print(f"\n  达西-魏斯巴赫公式：hf = λ × (L/d) × v²/(2g)")
        print(f"                      = {lamb:.4f} × ({self.L}/{self.d}) × {v}²/(2×{self.g})")
        print(f"                      = {lamb:.4f} × {self.L/self.d:.0f} × {v**2/(2*self.g):.3f}")
        print(f"                      = {hf:.2f} m")
        
        # (3) 局部损失
        hm = self.head_loss_local()
        print(f"\n(3) 局部水头损失：")
        print(f"  hm = ζ × v²/(2g)")
        print(f"     = {self.zeta} × {v}²/(2×{self.g})")
        print(f"     = {self.zeta} × {v**2/(2*self.g):.3f}")
        print(f"     = {hm:.2f} m")
        
        # (4) 总损失
        h_total = self.total_head_loss()
        print(f"\n(4) 总水头损失：")
        print(f"  h_total = hf + hm = {hf:.2f} + {hm:.2f} = {h_total:.2f} m")
        
        # 验证
        h_calc, h_press, error = self.verify_by_pressure_difference()
        print(f"\n验证（通过压强差）：")
        print(f"  水平管道能量方程：p1/(ρg) = p2/(ρg) + h_loss")
        print(f"  h_loss = (p1 - p2)/(ρg)")
        print(f"         = ({self.p1:.0f} - {self.p2:.0f}) / ({self.rho} × {self.g})")
        print(f"         = {self.p1 - self.p2:.0f} / {self.rho*self.g:.0f}")
        print(f"         = {h_press:.2f} m")
        print(f"\n  对比：")
        print(f"    计算值：h_total = {h_calc:.2f} m")
        print(f"    压差值：h_loss  = {h_press:.2f} m")
        print(f"    误差：{error:.2f}%")
        
        if error < 5:
            print(f"  ✓ 误差小于5%，计算合理")
        else:
            print(f"  ⚠ 误差较大，需检查参数")
        
        print("\n" + "=" * 70)
        print("考试要点：")
        print("=" * 70)
        print("1. 沿程损失：hf = λ(L/d)v²/(2g)  （达西公式）")
        print("2. 局部损失：hm = ζv²/(2g)")
        print("3. 总损失：h_total = hf + hm")
        print("4. 水平管：h_loss = (p1-p2)/(ρg)")
        print("5. 摩擦系数：层流λ=64/Re，紊流用经验公式")
        print("=" * 70)


def main():
    """主函数"""
    print("\n" + "💧" * 35)
    print("第02章 流体动力学基础 - 题目9：能量损失")
    print("💧" * 35 + "\n")
    
    # 题目参数
    d = 0.2         # 直径0.2m
    L = 100.0       # 长度100m
    Q = 0.08        # 流量0.08m³/s
    p1 = 250000     # 断面1压强250kPa
    p2 = 180000     # 断面2压强180kPa
    n = 0.012       # 粗糙度
    zeta = 5.0      # 局部损失系数
    
    # 创建能量损失对象
    energy_loss = EnergyLoss(d=d, L=L, Q=Q, p1=p1, p2=p2, n=n, zeta=zeta)
    
    # 打印结果
    energy_loss.print_results()
    
    # 绘图
    print("\n正在绘制能量损失分析图...")
    energy_loss.plot_energy_line()
    
    print("\n✅ 计算完成！")


if __name__ == "__main__":
    main()
